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
from vertexai.generative_models import GenerativeModel
import markdown
from utils.agent_builder_query_nfilter import DiscoveryEngineClient


API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
PROJECT_NUMBER = '556320446019'
DATA_STORE_ID = 'demo-dk-qna-csv_1733369222458'

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
    references = parsed_results.get('answer', {}).get('references', [])
    reference_map = []
    for idx, ref in enumerate(references):
        chunk_info = ref.get('chunkInfo', {})
        doc_meta = chunk_info.get('documentMetadata', {})
        uri = doc_meta.get('uri', '#')
        # Convert gs:// links to https://
        if uri.startswith('gs://'):
            uri = uri.replace('gs://', 'https://storage.googleapis.com/')
        reference_map.append({
            'title': doc_meta.get('title', 'No Title'),
            'uri': uri,
            'page': doc_meta.get('pageIdentifier', 'Unknown'),
            'relevance': chunk_info.get('relevanceScore', 'N/A'),
            'content': chunk_info.get('content', '')
        })
        
    ## model prompt
    vertexai.init(project="dk-medical-solutions", location="us-central1")

    model = GenerativeModel("gemini-1.5-flash-002")
    
    prompt = f"""
    <role>
    You are D-Chat, a domain-specific conversational assistant designed for delivering precise and structured responses based on healthcare insurance review regulations.
    Your role is to assist users by providing accurate, up-to-date information in a structured manner. 
    </role>
    <task>
    Step-by-step instructions:

    1. 사용자가 입력한 질문 {query}의 내용을 분석하여 질문의 의도를 명확히 파악합니다. 이후, 질문에 관련된 정보가 담긴 {reference_map}에서 검색하여 답변합니다.
    3.  답변은 질문의 유형에 따라 달라지며, 아래와 같이 제공됩니다:
    [공통]: 답변은 요약된 형태로 제공되어야 하며, 주요 내용은 명확하게 설명되어야 합니다. 어떤 자료를 어떻게 참고해서 답변했는지에 대한 정보를 제공해야 합니다.
    - **기간을 포함한 질문 (예: 최근 한 달 내 고시된 내용 등)**:  
        사용자가 명시한 기간 내 시행일 또는 고시일이 들어 있는 고시 정보를 정리하여 표를 생성합니다.  
        - 표의 열은 "고시일", "고시번호", "시행일", "고시 내용 요약"을 포함합니다.  
        - 고시 내용 요약은 100자 이내로 제한되어야 하며, 긴 내용은 생략하여 요약해야 합니다.
        - 고시에 대한 정보는 반드시 {reference_map}에서 참조한 내용이어야 합니다.  
        - 만약 해당 기간 내 고시된 내용이 없다면, "지정된 기간 내 고시된 내용이 없습니다."라는 메시지를 출력합니다.  
    만약 고시내용이 없는 경우 그 기간안에 고시된 내용이 없다는 메시지를 출력합니다.
    - **특정 내용에 대한 질문 (예: 특정 고시 내용, 기준, 응급실 수가 등)**:  
        질문의 주요 내용을 간결하고 명확하게 요약합니다.  
        - 해당 세부 정보를 헤더와 함께 정리된 리스트 형태로 제공하며, 하위 목록은 1., 2., 3. 형식으로 나열합니다.  
        - 표는 생성하지 않습니다.
    4. 각 문단이 끝난 후 한 개의 개행(빈 줄)을 추가하여 새로운 문단을 시작합니다. 
    5. 표 안의 내용과 리스트 정보는 {reference_map}에서만 참조할 수 있으며, {reference_map}이 빈 배열일 경우 "검색어에 대한 요약을 생성할 수 없습니다."라는 메시지를 출력합니다.
    6.  질문의 유형(기간 포함 여부, 특정 내용 요구 등)에 따라 답변 형식을 명확히 구분하고, 불필요한 표가 생성되지 않도록 확인합니다.
    </task>

    <format>
    응답의 맨 위에 헤더나 머리글을 넣지 않습니다.
    주요 변경 항목과 같이 리스트 형식은 1. 2. 3.과 같은 순서로 나열합니다.
    리스트의 헤더는 항상 굵은 글씨로 표시합니다. 
    질문:은 포함하지 않습니다.
    참조문서는 제공하지 않습니다.
    참고로, 이 내용은 [문서 이름](문서 URL) 문서를 참고하여 작성되었습니다.
    {reference_map}에서 정보가 없어서 답을 못할 경우에는 <p>검색어에 대한 정보가 존재하지 않습니다.</p> 라고 응답합니다.
    
    모든 텍스트는 <code></code> 태그로 감싸지 않습니다.
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

    응답: 제2024-181호 개정 고시 내용은 다음과 같습니다. 원본은 여기서 [문서 title](문서 url) 확인하세요.

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

        
    raw_markdown = response.text.replace('\n', '  \n').strip()
    html_content = markdown.markdown(
        raw_markdown,
        extensions=['markdown.extensions.tables']  
    )
    ## qna search
    result = client.search(query)
    qna_results = []
    if "results" in result:
        for item in result["results"]:
            document = item.get("document", {})
            struct_data = document.get("structData", None)
            if struct_data:
                qna_results.append(struct_data)
    
    
    parsed_results = {
        "answer_text": response.text,
        "answer_html": html_content,
        "references": reference_map,
        "related_questions": parsed_results.get('answer', {}).get('relatedQuestions', []),
        "qna_results": qna_results
    }
    return parsed_results
    
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
                prompt_data = generate_prompt(data,query)
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





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)