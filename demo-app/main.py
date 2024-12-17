from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.auth
import uvicorn
from pydantic import BaseModel
import requests
import urllib.parse
import json
import vertexai
from vertexai.generative_models import (GenerativeModel, ToolConfig)
from utils.agent_builder_query_nfilter import DiscoveryEngineClient
from utils.rerank import rank_query, fact_parser
from utils.noti_tool import call_vertex_ai_gemini_model
import logging
import os
from utils.token import get_access_token
from google.auth.transport.requests import Request
import google.auth
from typing import Optional
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
PROJECT_NUMBER = '556320446019'
DATA_STORE_ID = 'demo-dk-qna-csv_1733369222458'
OCR_DATASTORE_ID = 'dk-demo-ocr-insurance_1727419968121'



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_qna(query):
    client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)
    result = client.search(query)
    qna_results = []
    if "results" in result:
        for item in result["results"][0:3]:
            document = item.get("document", {})
            struct_data = document.get("structData", None)
            if struct_data:
                qna_results.append(struct_data)
    return qna_results

def get_filter_text(reference_data, answer_text):
    print("=================Fact Parsing===================")
    fact_parsing = fact_parser(reference_data)
    client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)
    result_parse = client.check_grounding(
        project_id=PROJECT_NUMBER,
        answer_candidate= answer_text,
        facts=fact_parsing,
        citation_threshold=0.8,
        )
    source_list = None
    ## 참고 문서가 있을경우 답변에 문서 URL 삽입
    if "citedChunks" in result_parse:
        # 참고 문서 URL 추가
        for chunk in result_parse["citedChunks"]:
            source_index = int(chunk['source'])
            chunk["reference_index"] = source_index
            chunk["reference_url_page"] = reference_data[source_index].get('url_page', '#')
            chunk["reference_title"] = f"{reference_data[source_index].get('title', 'Unknown')}_page_{reference_data[source_index].get('pageIdentifier', 'Unknown')}"
            del chunk['source']
        with open ("result_parse.json", 'w', encoding='utf-8') as f:
            json.dump(result_parse, f, indent=4, ensure_ascii=False)
            
        source_list = result_parse["citedChunks"]
        for claim in result_parse["claims"]:
            if claim.get("citationIndices"):
                source_text = ""
                for index in claim["citationIndices"]:
                    source_index = int(index) + 1
                    source_url = source_list[int(index)]["reference_url_page"]
                    # URL 전체를 파싱
                    parsed_url = urllib.parse.urlparse(source_url)

                    # path와 query만 인코딩
                    encoded_path = urllib.parse.quote(parsed_url.path)  # 경로 인코딩
                    fragment = parsed_url.fragment

                    # 인코딩된 URL 재구성
                    encoded_url = urllib.parse.urlunparse((
                        parsed_url.scheme,    # http or https
                        parsed_url.netloc,    # example.com
                        encoded_path,         # /path/to/resource
                        parsed_url.params,    # URL params (if any)
                        parsed_url.query,     # 쿼리는 없으므로 그대로
                        fragment              # #page=3 그대로 유지
                    ))
                    url = f"[{source_index}]({encoded_url})"
                    source_text += url

                    
                print("==========claim", source_text)
                # 텍스트 위치 찾기
                claim_text = claim["claimText"]
                start_pos = answer_text.find(claim_text)
                if start_pos == -1:
                    print(f"Claim text not found in answer_text: {claim_text}")
                    continue
                end_pos = start_pos + len(claim_text)

                answer_text = answer_text[:end_pos] + source_text + answer_text[end_pos:]
    filter = {
        "filter_text": answer_text,
        "filter_references_data": source_list
    }
    return filter

def generate_prompt(model, reference_data,tool_data, query):
        
    tool_call_status = tool_data.get("tool_called", False)
    tool_data = tool_data.get("results", [])
    
    # print("SourceData(Reference):",reference_data)
    print("Tool Call Status:",tool_call_status)
    print("Tool Data:",tool_data)
        
    ## model prompt
    vertexai.init(project="dk-medical-solutions", location="us-central1")
    if model == "medlm":
        model = GenerativeModel("medlm-large-1.5@001")
    else:
        model = GenerativeModel("gemini-1.5-flash-002")
    
    prompt = f"""
    <role>
    당신은 D-Chat이라는 도메인 특화 대화형 어시스턴트입니다. 당신의 역할은 의료보험 심사 규정에 기반하여 정확하고 구조화된 응답을 제공하는 것입니다. 사용자가 질문하는 내용에 따라 명확하고 최신 정보를 제공하세요.
    </role>
    <task>
    Step-by-step instructions:

    1. 사용자가 입력한 질문 {query}의 내용을 분석하여 질문의 의도를 명확히 파악합니다. 이후, 질문에 유형에 따라 정보를 선택하여 정보내에서 답변합니다.
    2.  답변은 질문의 유형에 따라 달라지며, 아래와 같이 제공됩니다:
    [공통]: 답변은 요약된 형태로 제공되어야 하며, 주요 내용은 명확하게 설명되어야 합니다.  답변을 생성할때는 질문의 유형에 따라 {tool_data} 또는 {reference_data} 중 하나의 정보만을 참고하여 답변을 생성합니다.
    - 사용자의 질문이 고시된 내용에 대해 알고 싶어하는 질문이면서 특정고시에 대해 물어보는게 아닌 기간을 포함해 여러개의 고시에 대해 알고 싶은 질문일 경우 {tool_data}를 사용해서 답변합니다. 검색 결과를 확인하여 다음 두 가지 경우에 따라 처리합니다:
        - {tool_data}이  빈배열이 아닐경우:
            {tool_data}에 results 리스트 안에  모든 객체 정보를 표로 출력합니다. 각 객체는 다음과 같은 속성을 가집니다:
            revision_date: 고시일 or ""
            notification_number: 고시번호
            effective_date: 시행일 or ""
            summary: 고시 내용 요약 (최대 100자)
            없는 속성이 있을경우 그 객체의 속성은 ""으로 표시합니다.
            - 결과를 Markdown 표 형식으로 정리합니다. 표의 열은 다음과 같습니다:
            - "고시일"
            - "고시번호"
            - "시행일"
            - "고시 내용 요약" (최대 100자)
                | 고시일         | 고시번호      | 시행일         | 고시 내용 요약          |
                |---------------|---------------|---------------|-------------------------|
                | 2024-11-01    | 2024-101      | 2024-11-10    | 요양급여 기준 변경     |
            -  markdown형태로 만들어진 표와 함께 어떤 데이터를 제공해주는지에 대한 소개 텍스트와 함께(ex. 요청하신 9월 고시목록입니다. / 가장 최근 고시목록 3개입니다.) 모두 텍스트로 반환됩니다.
        -  {tool_data}가 빈배열일경우:
            다른 텍스트 없이 "기간내에 고시된 데이터가 없습니다."라는 메시지만 반환합니다.
    -**특정 내용에 대한 질문 (예: 기간없이 특정 고시 내용질문, 기준, 응급실 재방문시 수가 산정기준 등) 유형일 경우:  
        질문에 관련된 정보를 {reference_data}에서 검색하여 응답합니다.  
        어떤 자료를 어떻게 참고해서 답변했는지에 대한 정보를 제공해야 합니다.
        - {reference_data}은 정보 객체의 리스트로 구성되며, 각 객체는 다음과 같은 속성을 포함합니다:
            - id: 사용하지 않습니다.
            - title :  content를 뽑아낸 문서의 제목
            - content: 질문과 관련된 문서의 세부 내용을 포함하며, 이미 질문과 관련된 텍스트만을 뽑아낸 상태입니다.
        - 각 객체의 content 필드의 모든 내용을 분석하여 질문의 주요 내용을 요약합니다.
        - 기준에 대해 질문했을 경우는 요약해서 답변하지 않고 세부 기준에 대해서 리스트 형태로 자세히 설명합니다.
        - 모든 객체의 content를 요약하여 헤더와 함께 정리된 리스트 형태로 제공하며, 하위 목록은 1., 2., 3. 형식으로 나열합니다.  
        - 표는 생성하지 않습니다.
        - 주요 변경 항목과 같이 리스트 형식은 1. 2. 3.과 같은 순서로 나열합니다.
        - 리스트의 헤더는 항상 굵은 글씨로 표시합니다. 
        - 요약 내용은 간결하고 명확하게 작성하며, 불필요한 반복이나 문구는 생략합니다.
        - title은 답변에는 사용하지 않습니다. 어떤 문서를 참고했는지는 제공하지 않습니다.
        - {reference_data}이 비어 있는 경우:
            - "검색어에 대한 정보가 존재하지 않습니다."라는 메시지를 반환합니다.
    4. 각 문단이 끝난 후 한 개의 개행(빈 줄)을 추가하여 새로운 문단을 시작합니다. 
    6. 질문의 유형(기간 포함 여부, 특정 내용 요구 등)에 따라 답변 형식을 명확히 구분하고, 불필요한 표 또는 요약이 생성되지 않게 합니다. 모든 질문에 대한 답변은 {reference_data} 또는 {tool_data} 둘 중 하나의 정보만 참고하여 생성되어야 합니다.
    7. {tool_data}를 사용했는데 {reference_data}도 사용했을 경우 처음 사용했던 {tool_data}만을 사용하여 답변을 생성합니다.
    8. 표에 사용된 데이터가 {tool_data}가 아닌 경우, 표를 삭제하고 해당 기간내에 고시 정보가 없습니다 라는 텍스트를 반환합니다.
    9. 표에 사용된 데이터가 정확한 정보인지 확인하고, 아닐 경우 표를 삭제하고 해당 기간내에 고시 정보가 없습니다. 라는 텍스트를 반환합니다.
    </task>

    <format>
    응답의 맨 위에 헤더나 머리글을 넣지 않습니다.
    응답에 사용자의 질문은 포함하지 않습니다.
    질문의 유형에 따라 적절한 형식으로 구분하여 형식에 맞는 데이터를 사용하여 응답합니다.
    모든 텍스트는 <code></code> 태그로 감싸지 않습니다.
    최종응답에 json형식이 들어가지 않습니다.
    표에 사용된 데이터가 {tool_data}가 아닌 경우, 표를 삭제하고 해당 기간내에 고시 정보가 없습니다 라는 텍스트를 반환합니다.
    </format>
    <example>
    ### Example 1: Recent Notices Query

    질문: 최근 한달내 고시된 내용을 알려주세요.

    응답:  최근 한달 동안 공지된 고시 목록입니다.

    | 고시일         | 고시번호                        | 시행일       | 고시내용요약                |
    |---------------|--------------------------------|------------|---------------------------|

    
    질문: 최근 고시목록 알려줘 

    응답: 가장 최근 고시된 상위 3개 목록입니다.

    | 고시일         | 고시번호                        | 시행일       | 고시내용요약                |
    |---------------|--------------------------------|------------|---------------------------|
    ---

    ### Example 2: Specific Notice Query

    질문: 오늘 고시된 제2024-181호 고시 내용을 자세히 알려주세요.

    응답: 제2024-181호 개정 고시 내용은 다음과 같습니다. 

    ● 주요 변경 항목:  
    ○ 제19장 응급의료수가 일반사항, 응급실 재방문 시 수가산정기준  
    - 시행규칙 개정으로 인한 응급실 경증환자 본인부담률 인상  

    ○ 제19장 응급의료수가 응3 중증응급환자 진료구역 관찰료 산정방법, 중증응급환자 진료구역 관찰료 산정기준  
    - 응급의료에 관한 법률 개정에 따른 문구 정비. ‘중앙응급의료센터’를 응급의료기관에서 제외.  

    ○ 제19장 응급의료수가 응4 응급환자 진료구역 관찰료 산정방법, 응급환자 진료구역 관찰료 산정기준  
    - 응급의료에 관한 법률 개정에 따른 문구 정비. ‘중앙응급의료센터’를 응급의료기관에서 제외.  
    ---

    ### Example 3: Specific Policy Query

    질문: 응급실 재방문시 수가 산정기준에 대해서 알려주세요.

    응답: 현재까지 반영된 최신 응급실 재방문시 수가 산정기준은 다음과 같습니다.

    응급실 내원환자가 동일 상병 또는 증상으로 당일 또는 퇴실 후 6시간 이내 응급실을 재방문하는 경우, 응급실 진료가 계속된 것과 동일하게 응급의료수가를 산정합니다.  

    1. 응1 응급의료관리료, 응3 중증응급환자 진료구역관찰료, 응4 응급환자 진료구역 관찰료, 응7 응급환자 중증도 분류 및 선별료, 응7-1 정신응급환자 초기 평가료, 응8 외상환자 관리료 등은 1회에 한하여 산정됩니다.  
    2. 응급실 방문 중 한 번이라도 입원환자 본인부담률 산정조건에 해당되면, 전체 응급실 요양급여비용은 입원환자 본인부담률에 따라 산정됩니다.  
    3. 위의 2번에 해당하지 않는 경우, 「국민건강보험법 시행규칙」 [별표 6] 제1호 사목 2)‧3)에 따라 본인부담률을 각각 적용합니다.  
    </example>
    
    """
    response = model.generate_content(
    prompt)
    
    
    print("=================MODEL RESPONSE===================")
    print(response.text)
    final = {
        "answer_text": response.text,
        "references_data": reference_data,
        "tools_data": tool_data
    }
    
    if(len(reference_data) != 0 and "|-" not in response.text and "|" not in response.text ):
        filter_text  = get_filter_text(reference_data, response.text)
        print(filter_text)
        if filter_text != "":
            final["filter_text"] = filter_text["filter_text"]
            final["filter_references_data"] = filter_text["filter_references_data"]
    return final

def get_references(query):
    try:
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": {
                "text": query,
                "queryId": ""
            },
            "session": "",
            # Related Questions
            "relatedQuestionsSpec": {
                "enable": True
            },
            "answerGenerationSpec": {
                "ignoreAdversarialQuery": True,
                "ignoreNonAnswerSeekingQuery": True,
                "ignoreLowRelevantContent": True,
                "includeCitations": True,
                "modelSpec": {
                    "modelVersion": "gemini-1.5-flash-002/answer_gen/v1"
                }
            },
        }
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 401:
            logger.error("인증 실패: 유효하지 않은 크레덴셜 또는 토큰")
            credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            request = Request()
            credentials.refresh(request)
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": {
                    "text": query,
                    "queryId": ""
                },
                "session": "",
                # Related Questions
                "relatedQuestionsSpec": {
                    "enable": True
                },
                "answerGenerationSpec": {
                    "ignoreAdversarialQuery": True,
                    "ignoreNonAnswerSeekingQuery": True,
                    "ignoreLowRelevantContent": True,
                    "includeCitations": True,
                    "modelSpec": {
                        "modelVersion": "gemini-1.5-flash-002/answer_gen/v1"
                    }
                },
            }
            response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
            
        if response.status_code == 200:
            print("(get_references) API 요청 성공")
            response.encoding = 'utf-8'
            data = response.json()
            return data
        response.raise_for_status()  # HTTP 오류가 있으면 예외 발생
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"(get_references) HTTP 요청 오류 발생: {e}")
    except google.auth.exceptions.GoogleAuthError as e:
        logger.error(f"(get_references)Google 인증 오류 발생: {e}")
    except Exception as e:
        logger.error(f"(get_references) 예기치 않은 오류 발생: {e}")
    
class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = Field(default="gemini", description="Optional model name")

@app.post("/")
def index(request: QueryRequest):
    try:
        query = request.query
        model = request.model
        logger.info("사용자 질문: %s", query)
        print("모델",model,"사용자 질문",query)
        if query:
            reference_data = get_references(query)
            rerank_data = None
            if reference_data:
                print("=================DATA OK===================")
                #### Rerank #####
                rerank_data = rank_query(
                    query=query,
                    project_id=PROJECT_NUMBER,
                    rows=reference_data,
                    datastore_id=OCR_DATASTORE_ID
                    )
            if rerank_data:
                print("=================RERANK OK===================")  
                reference_data_r = rerank_data.get('records', [])
                for idx, ref in enumerate(reference_data_r):
                    uri = ref.get('uri', '#')
                    page = ref.get('pageIdentifier', 'Unknown')
                    if uri.startswith('gs://'):
                        uri = uri.replace('gs://', 'https://storage.googleapis.com/')
                    ref["uri"] = uri
                    ref["url_page"] = f"{uri}#page={page}"
                tool_data = call_vertex_ai_gemini_model(query)
                
                print("=================Source OK===================")
                related_questions = reference_data.get('answer', {}).get('relatedQuestions', [])
                qna_results = get_qna(query)
                
                
                prompt_data = generate_prompt(model,reference_data_r,tool_data ,query)
                prompt_data["related_qna_list"] = qna_results
                prompt_data["related_questions"] = related_questions
                #(테스트 용도) result 파일 저장
                with open("result.json", 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, indent=4, ensure_ascii=False)
                
                if(prompt_data["references_data"] != []):
                    prompt_data["status"] = "success"
                    return JSONResponse(content=prompt_data, status_code=200)
                else:  
                    prompt_data["status"] = "error"
                    return JSONResponse(content=prompt_data, status_code=200)
                
            else:
                raise HTTPException(status_code=500, detail="Rerank 실패")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)