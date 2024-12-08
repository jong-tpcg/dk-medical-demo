from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport.requests import Request
import uvicorn
from pydantic import BaseModel
import google.auth
import requests
import json
import vertexai
from vertexai.generative_models import (GenerativeModel, ToolConfig)
import markdown
from utils.agent_builder_query_nfilter import DiscoveryEngineClient
from utils.rerank import rank_query, fact_parser
from utils.notification_tool import noti_tool
import logging
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
PROJECT_NUMBER = '556320446019'
DATA_STORE_ID = 'demo-dk-qna-csv_1733369222458'
OCR_DATASTORE_ID = 'dk-demo-ocr-insurance_1727419968121'

client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_access_token():
    credentials, project = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

AUTH_TOKEN = get_access_token()
    
def generate_prompt(parsed_results,query):
    # references = parsed_results.get('answer', {}).get('references', [])
    # reference_map = []
    # for idx, ref in enumerate(references):
    #     chunk_info = ref.get('chunkInfo', {})
    #     doc_meta = chunk_info.get('documentMetadata', {})
    #     uri = doc_meta.get('uri', '#')
    #     # Convert gs:// links to https://
    #     if uri.startswith('gs://'):
    #         uri = uri.replace('gs://', 'https://storage.googleapis.com/')
    #     reference_map.append({
    #         'title': doc_meta.get('title', 'No Title'),
    #         'uri': uri,
    #         'page': doc_meta.get('pageIdentifier', 'Unknown'),
    #         'relevance': chunk_info.get('relevanceScore', 'N/A'),
    #         'content': chunk_info.get('content', '')
    #     })

    reference_map = parsed_results.get('records', [])

    ## model prompt
    vertexai.init(project="dk-medical-solutions", location="us-central1")

    model = GenerativeModel("gemini-1.5-flash-002")
    current_time = datetime.now()
    current_date = current_time.date()
    prompt = f"""
    <role>
    당신은 D-Chat이라는 도메인 특화 대화형 어시스턴트입니다. 당신의 역할은 의료보험 심사 규정에 기반하여 정확하고 구조화된 응답을 제공하는 것입니다. 사용자가 질문하는 내용에 따라 명확하고 최신 정보를 제공하세요.
    </role>
    <task>
    Step-by-step instructions:

    1. 사용자가 입력한 질문 {query}의 내용을 분석하여 질문의 의도를 명확히 파악합니다.
    3.  답변은 질문의 유형에 따라 달라지며, 아래와 같이 제공됩니다:
    [공통]: 답변은 요약된 형태로 제공되어야 하며, 주요 내용은 명확하게 설명되어야 합니다.
    - **기간을 포함한 질문 (예: 최근 한 달 내 고시된 내용 등)** 또는 9월 내에 고시된 내용을 알려주세요.:  
        1. 사용자의 질문에서 명시된 기간 정보를 추출합니다.  
            - 예: "2024년 10월부터 2024년 11월까지" 또는 "최근 한 달 내" 또는 9월 내에.
            - 9월 내의 경우 9월 1일부터 9월 30일까지로 기간을 정의합니다.
        2. 현재 날짜는{current_date} 으로 기준날짜로 지정 후 사용자의 질문에 맞게 기간을 정의합니다:
            만약 최근 한달 내라고 했을경우
            - `start_date`: 현재 날짜로부터 30일 전 날짜 (예: 2024-11-08)
            - `end_date`: 현재 날짜 (예: 2024-12-08)
            만약 9월 내라고 했을경우
            - `start_date`:  2024-09-01
            - `end_date`: 2024-09-30
        2. (Function Calling get_noti_list)  에 start_date, end_date 사이에 포함된 데이터를 검색합니다. 함수 호출 시 다음 매개변수를 사용합니다:
                - `start_date`: 검색 시작 날짜 (예: 2024-11-08)
                - `end_date`: 검색 종료 날짜 (예: 2024-12-08)
        3. 검색 결과를 확인하여 다음 두 가지 경우에 따라 처리합니다:
        - **데이터가 존재할 경우**:
            데이터는 각 정보객체의 배열로 이루어져있고 각 객체는 다음과 같은 속성을 가집니다:
            revision_date: 고시일
            notification_number: 고시번호
            effective_date: 시행일
            summary: 고시 내용 요약 (최대 100자)
            - 결과를 Markdown 표 형식으로 정리합니다. 표의 열은 다음과 같습니다:
            - "고시일"
            - "고시번호"
            - "시행일"
            - "고시 내용 요약" (최대 100자)
                | 고시일         | 고시번호      | 시행일         | 고시 내용 요약          |
                |---------------|---------------|---------------|-------------------------|
                | 2024-11-01    | 2024-101      | 2024-11-10    | 요양급여 기준 변경     |
            - 최종적으로  start_date와 end_date 기간에 고시된 내용입니다. 라는 텍스트와 함께 markdown형태로 만들어진 표와 함께 모두 텍스트로 반환됩니다.
        -4. (Function Calling (Tool)) 결과의 데이터가 빈배열 일경우**:
            - "지정된 기간 내 고시된 내용이 없습니다."라는 메시지를 반환합니다. 표는 제공하지 않습니다.
    - **특정 내용에 대한 질문 (예: 특정 고시 내용, 기준, 응급실 수가 등)**:  
        질문에 관련된 정보가 담긴 {reference_map}에서 검색하여 답변합니다. {reference_map}안에 id값은 사용하지 않습니다. 
        질문의 주요 내용을 간결하고 명확하게 요약합니다.  
        - 해당 세부 정보를 헤더와 함께 정리된 리스트 형태로 제공하며, 하위 목록은 1., 2., 3. 형식으로 나열합니다.  
        - 표는 생성하지 않습니다.
        -  {reference_map}에서 정보가 없어서 답을 못할 경우에는 검색어에 대한 정보가 존재하지 않습니다.라고 응답합니다.
    4. 각 문단이 끝난 후 한 개의 개행(빈 줄)을 추가하여 새로운 문단을 시작합니다. 
    5.  질문의 유형(기간 포함 여부, 특정 내용 요구 등)에 따라 답변 형식을 명확히 구분하고, 불필요한 표가 생성되지 않도록 확인합니다.
    
    </task>

    <format>
    응답의 맨 위에 헤더나 머리글을 넣지 않습니다.
    주요 변경 항목과 같이 리스트 형식은 1. 2. 3.과 같은 순서로 나열합니다.
    리스트의 헤더는 항상 굵은 글씨로 표시합니다. 
    질문:은 포함하지 않습니다.
    질문의 유형에 따라 적절한 형식으로 구분하여 응답합니다.
    모든 텍스트는 <code></code> 태그로 감싸지 않습니다.
    최종답변은 항상 텍스트로 반환됩니다.
    </format>
    <example>
    ### Example 1: Recent Notices Query

    질문: 최근 한달내 고시된 내용을 알려주세요.

    응답: 아래는 “요양급여의 적용기준 및 방법에 관한 세부사항”에 대한 최근 한달 동안 공지된 고시 목록입니다.

    | 고시일         | 고시번호                        | 시행일       | 고시내용요약                |
    |---------------|--------------------------------|------------|---------------------------|
    | 2024-09-12    | 보건복지부 고시 제2024-181호   | 2024-09-13 | 응급의료                   |
    | 2024-08-29    | 보건복지부 고시 제2024-176호   | 2024-09-01 | 검사료 및 영상진단 및 방사선치료 |

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
    # response = model.generate_content(
    # prompt)
    ## Tool 사용
    response = model.generate_content(
        prompt,
        tools=[noti_tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
            )
        )
    )
    print("=================MODEL RESPONSE===================")
    print(response)  
    ## qna search
    result = client.search(query)
    qna_results = []
    if "results" in result:
        for item in result["results"]:
            document = item.get("document", {})
            struct_data = document.get("structData", None)
            if struct_data:
                qna_results.append(struct_data)
    
    
    final = {
        "answer_text": response.text,
        "references": reference_map,
        "related_questions": parsed_results.get('answer', {}).get('relatedQuestions', []),
        "qna_results": qna_results
    }
    fact_parsing = fact_parser(parsed_results)
    result_parse = client.check_grounding(
        project_id=PROJECT_NUMBER,
        answer_candidate=response.text,
        facts=fact_parsing,
        citation_threshold=0.8,
        )
    final["filter_answer"] = result_parse
    # print(final)
    # print("====================================")
    # print(result_parse)
    return final
    
class QueryRequest(BaseModel):
    query: str
    
@app.post("/")
def index(request: QueryRequest):
    try:
        query = request.query
        print("사용자 질문 : ",query)
        if query:
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
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
                response.encoding = 'utf-8'
                data = response.json()
            # print("=================API RESPONSE===================")
            # print(response.text)
            # client = DiscoveryEngineClient(PROJECT_NUMBER, OCR_DATASTORE_ID)
            # response = client.search(query)
            if response:
                ##### Rerank #####
                ocr_data = rank_query(
                    query=query,
                    project_id=PROJECT_NUMBER,
                    rows=data,
                    datastore_id=OCR_DATASTORE_ID
                    )
                print("=================RERANK===================")
                # print(ocr_data)
                prompt_data = generate_prompt(ocr_data,query)
                with open("result.json", 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, indent=4, ensure_ascii=False)
                if(prompt_data["references"] != []):
                    prompt_data["status"] = "success"
                    return JSONResponse(content=prompt_data, status_code=200)
                else:  
                    prompt_data["status"] = "error"
                    return JSONResponse(content=prompt_data, status_code=200)
            else:
                print(response.text)
                error = "Error fetching data from API."
                error = {
                        "error": "Error fetching data from API.",
                        "status_code": response.status_code,
                        "details": response.text
                }
                return JSONResponse(content=error, status_code=501)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)