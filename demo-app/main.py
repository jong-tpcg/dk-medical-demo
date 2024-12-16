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

def get_filter_text(reference_data, response):
    answer_text = response.text
    print("=================Fact Parsing===================")
    fact_parsing = fact_parser(reference_data)
    client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)
    result_parse = client.check_grounding(
        project_id=PROJECT_NUMBER,
        answer_candidate= answer_text,
        facts=fact_parsing,
        citation_threshold=0.8,
        )
    # with open ("result_parse.json", 'w', encoding='utf-8') as f:
    #     json.dump(result_parse, f, indent=4, ensure_ascii=False)
    
    if "citedChunks" in result_parse:
        for chunk in result_parse["citedChunks"]:
            source_index = int(chunk['source'])
            chunk["url_page"] = reference_data[source_index].get('url_page', '#')
            chunk["title"] = f"{reference_data[source_index].get('title', 'Unknown')}_page_{reference_data[source_index].get('pageIdentifier', 'Unknown')}"
        # 중복 url 제거
        existing_urls = set()
        for claim in result_parse["claims"]:
            if claim.get("citationIndices"):
                print("================claim")
                source_text = ""
                for index in claim["citationIndices"]:
                    source_url = result_parse["citedChunks"][int(index)].get('url_page', '#')
                    source_title = result_parse["citedChunks"][int(index)].get("title", "Unknown")
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
                    if encoded_url not in existing_urls:
                        url = f"[{source_title}]({encoded_url})"
                        source_text += url
                        existing_urls.add(encoded_url)  # URL 추가 

                claim_text = claim["claimText"]

                # 텍스트 위치 찾기
                start_pos = answer_text.find(claim_text)
                if start_pos == -1:
                    print(f"Claim text not found in answer_text: {claim_text}")
                    continue
                end_pos = start_pos + len(claim_text)

                answer_text = answer_text[:end_pos] + source_text + answer_text[end_pos:]
    return answer_text

def generate_prompt(model, reference_data,tool_data, query):
        
    tool_call_status = tool_data.get("tool_called", False)
    tool_data = tool_data.get("results", [])
    
    # print("SourceData(Reference):",reference_data)
    # print("Tool Call Status:",tool_call_status)
    # print("Tool Data:",tool_data)
        
    ## model prompt
    vertexai.init(project="dk-medical-solutions", location="us-central1")
    if model == "medlm":
        model = GenerativeModel("medlm-large-1.5@001")
    else:
        model = GenerativeModel("gemini-1.5-flash-002")
    
    prompt = f"""
    <role>
        당신은 D-Chat이라는 도메인 특화 대화형 어시스턴트입니다. 당신의 역할은 의료보험 심사 규정에 기반하여 정확하고 구조화된 응답을 제공하는 것입니다. 사용자가 질문하는 내용에 따라 명확하고 최신 정보를 제공하세요.
        주의:
        - 질문이 명확하지 않을 경우, 어시스턴트는 필요한 추가 정보를 요청할 수 있습니다.
        - 어시스턴트는 주어진 정보 외의 내용을 유추하거나 생성하지 않습니다.
    </role>
    <task>
    Step-by-step instructions:

    1. 사용자가 입력한 질문 {query}의 내용을 분석하여 질문의 의도를 명확히 파악합니다. 이후, 질문에 유형에 따라 정보를 선택하여 정보내에서 답변합니다.
    2.  답변은 질문의 유형에 따라 달라지며, 답변을 생성할때는 질문의 유형에 따라 {tool_data} 또는 {reference_data} 중 하나의 정보만을 참고하여 답변을 생성합니다.
    - {tool_call_status}가 True일 경우
        1. {tool_data}이  빈배열이 아닐경우:
            {tool_data}안에  모든 객체 정보를 표로 출력합니다. 각 객체는 다음과 같은 속성을 가집니다:
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
        2. {tool_data}가 빈배열일경우:
            다른 텍스트 없이 "기간내에 고시된 데이터가 없습니다."라는 메시지만 반환합니다.
    - **특정 내용에 대한 질문 (예: 기간없이 특정 고시 내용질문, 기준, 응급실 재방문시 수가 산정기준 등) 유형일 경우:  
       - 주어진 {reference_data}는 {query}에 맞는 정보 객체의 리스트로 구성되어 있습니다. **모든 객체의 `content` 필드를 순차적으로 분석하고**, 각 객체에서 질문에 대한 핵심 정보를 추출한 뒤 **모든 내용을 종합**하여 답변을 생성합니다.  
            각 객체는 다음과 같은 속성을 포함합니다:
            - id: 객체의 id, - 답변에는 사용하지 않습니다.
            - title :  content를 가지고 온 문서의 제목
            - content: 질문과 관련된 문서의 세부 내용.
            - 요구 사항:  
        - **각 객체의 `content`**를 개별적으로 분석하고, 내용을 요약하여 하나의 응답에 포함합니다.  
        - 기준에 대해 질문했을 경우 요약해서 답변하지 않고 세부 기준에 대해서 자세히 설명합니다.
        - 리스트 형태로 나열하며 **항상 다음 형식**을 유지합니다:  
        
            **굵은 글씨 헤더**  
            1. 첫 번째 객체의 요약된 내용  
            2. 두 번째 객체의 요약된 내용  
            3. 세 번째 객체의 요약된 내용  
        
        - 중복된 내용은 병합하고, 불필요한 문구는 제거합니다.  
        - `title`과 `id`는 응답에 포함하지 않습니다.  
        - {reference_data}이 비어 있는 경우:
            - "검색어에 대한 정보가 존재하지 않습니다."라는 메시지를 반환합니다.
    
    3. 각 문단이 끝난 후 한 개의 개행(빈 줄)을 추가하여 새로운 문단을 시작합니다. 
    4. 질문의 유형(기간 포함 여부, 특정 내용 요구 등)에 따라 답변 형식을 명확히 구분하고, 불필요한 표 또는 요약이 생성되지 않게 합니다. 모든 질문에 대한 답변은 {reference_data} 또는 {tool_data} 둘 중 하나의 정보만 참고하여 생성되어야 합니다.
    5. 표에 사용된 데이터가 {tool_data}가 아닌 경우, 표를 삭제하고 해당 기간내에 고시 정보가 없습니다 라는 텍스트를 반환합니다.
    </task>

    <format>
    응답의 맨 위에 헤더나 머리글을 넣지 않습니다.
    응답에 사용자의 질문은 포함하지 않습니다.
    질문의 유형에 따라 적절한 형식으로 구분하여 형식에 맞는 데이터를 사용하여 응답합니다.
    모든 텍스트는 <code></code> 태그로 감싸지 않습니다.
    최종응답에 json형식이 들어가지 않습니다.
    </format>
    <example>
    ### Example 1: Recent Notices Query

    질문: 최근 한달내 고시된 내용을 알려주세요.

    응답:  최근 한달 동안 공지된 고시 목록입니다.

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
    final = {
        "answer_text": response.text,
        "references_data": reference_data,
        "tools_data": tool_data
    }
    
    if(len(reference_data) != 0 and "|-" not in response.text and "|" not in response.text ):
        filter_text  = get_filter_text(reference_data, response)
        print(filter_text)
        if filter_text != "":
            final["filter_text"] = filter_text
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
        print(model)
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
                # with open("result.json", 'w', encoding='utf-8') as f:
                #     json.dump(prompt_data, f, indent=4, ensure_ascii=False)
                
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