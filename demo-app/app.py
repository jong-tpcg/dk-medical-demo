from flask import Flask, render_template, request
import requests
import json
from google.auth.transport.requests import Request
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part
import markdown
app = Flask(__name__)

# Replace with your actual API endpoint and authorization token
API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
import google.auth

def get_access_token():
    credentials, project = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

AUTH_TOKEN = get_access_token()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
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
                with open("data.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                prompt_data = generate_prompt(data,query)
                # parsed_data = parse_data(data,prompt_data)
                return 
            else:
                error = "Error fetching data from API."
                error = {
                        "error": "Error fetching data from API.",
                        "status_code": response.status_code,
                        "details": response.text
                }
                return render_template('index.html', error=error)
    return 

def generate_prompt(parsed_results,query):
    answer_text = parsed_results.get('answer', {}).get('answerText', '')
    references = parsed_results.get('answer', {}).get('references', [])
    citations = parsed_results.get('answer', {}).get('citations', [])
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
    2. 답변은 요약된 형태로 제공되어야 하며, 주요 내용은 명확하게 설명되어야 합니다. 어떤 자료를 어떻게 참고해서 답변했는지에 대한 정보를 제공해야 합니다.
    3.  답변 뒤에 질문의 의도에 따라 정보를 다르게 표현해서 보여줍니다:
    - 기간을 포함하여 모든 내용을 요청하는 경우 (예: 최근 한 달 내 고시된 내용 등):
    사용자가 질문에 명시한 기간안에 시행일 또는 고시일이 들어가 있는 경우 해당 고시들에 대해 정리하고 요약한 표에 넣습니다. 고시는 "~ 시행 한다 , ~발령한다"과 같이" 끝을 맺는 형식이며 다양한 형식으로 존재합니다. 
    고시일은 해당 고시가 만들어진 날짜이고, 고시 번호는 ~호 와 같이 표기되어 있는 형식입니다. 시행일은 고시가 시행된 날짜이며, 고시내용요약은 해당 고시의 주요 내용을 요약한 것입니다.  고시들에 대한 정보를 표를 통해 고시에 대한 "고시일", "고시번호", "시행일", "고시내용요약" 열이 포함된 테이블을 생성합니다. 테이블에 있는 내용은 모두 {reference_map}에서만 참조할 수 있습니다.
    만약 고시내용이 없는 경우 그 기간안에 고시된 내용이 없다는 메시지를 출력합니다.
    [고시내용] ([고시일]) 제 1 조 ( 시행일 ) 이 고시 는 [시행일]일 부터 시행 한다
    - 기타 특정 내용을 요청하는 경우 (예: 오늘 고시된 제2024-181호 고시 내용을 자세히 알려주세요, 기준을 알려주세요 등):
    주요 변경 항목같은 정리된 목록을 제공할 경우 헤더와 함께, 해당 세부 정보를 설명하는 리스트 형태로 명확한 답변을 제공합니다. 리스트의 하위목록은 1. 2. 3.같은 형식으로 나열합니다. 
    4. 각 문단이 끝난 후 한 개의 개행(빈 줄)을 추가하여 새로운 문단을 시작합니다.
    5. 표 안의 내용이 { reference_map }에서 참조할 수 있는 내용인지 다시 확인합니다.
    6. 만약 {reference_map}이 빈배열이면 "검색어에 대한 요약을 생성할 수 없습니다. 다음은 몇 가지 연관 검색어입니다."를 출력합니다.
    </task>

    <format>
    응답의 맨 위에 헤더나 머리글을 넣지 않습니다.
    주요 변경 항목과 같이 리스트 형식은 1. 2. 3.과 같은 순서로 나열합니다.
    질문:은 포함하지 않습니다.
    참조문서는 항상 응답의 맨 아래에 위치해야합니다.

    </format>
    <example>
    ### Example 1: Recent Notices Query

    질문: 최근 한달내 고시된 내용을 알려주세요.

    응답: 아래는 “요양급여의 적용기준 및 방법에 관한 세부사항”에 대한 최근 한달 동안 공지된 고시 목록입니다.

    | 고시일         | 고시번호                        | 시행일       | 고시내용요약                |
    |---------------|--------------------------------|------------|---------------------------|
    | 2024-09-12    | 보건복지부 고시 제2024-181호   | 2024-09-13 | 응급의료                   |
    | 2024-08-29    | 보건복지부 고시 제2024-176호   | 2024-09-01 | 검사료 및 영상진단 및 방사선치료 |

    참조 문서:  
    - [★(제2024-181호, 9.12.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3](https://example.com/link1)  
    - [★(제2024-176호, 8.29.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3](https://example.com/link2)  

    ---

    ### Example 2: Specific Notice Query

    질문: 오늘 고시된 제2024-181호 고시 내용을 자세히 알려주세요.

    응답: 제2024-181호 개정 고시 내용은 다음과 같습니다. 원본은 여기서 [링크](https://example.com/link1) 확인하세요.

    ● 주요 변경 항목:  
    ○ 제19장 응급의료수가 일반사항, 응급실 재방문 시 수가산정기준  
    - 시행규칙 개정으로 인한 응급실 경증환자 본인부담률 인상  

    ○ 제19장 응급의료수가 응3 중증응급환자 진료구역 관찰료 산정방법, 중증응급환자 진료구역 관찰료 산정기준  
    - 응급의료에 관한 법률 개정에 따른 문구 정비. ‘중앙응급의료센터’를 응급의료기관에서 제외.  

    ○ 제19장 응급의료수가 응4 응급환자 진료구역 관찰료 산정방법, 응급환자 진료구역 관찰료 산정기준  
    - 응급의료에 관한 법률 개정에 따른 문구 정비. ‘중앙응급의료센터’를 응급의료기관에서 제외.  

    참조 문서:  
    - [★(제2024-181호, 9.12.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3](https://example.com/link1)  

    ---

    ### Example 3: Specific Policy Query

    질문: 응급실 재방문시 수가 산정기준에 대해서 알려주세요.

    응답: 현재까지 반영된 최신 응급실 재방문시 수가 산정기준은 다음과 같습니다.

    응급실 내원환자가 동일 상병 또는 증상으로 당일 또는 퇴실 후 6시간 이내 응급실을 재방문하는 경우, 응급실 진료가 계속된 것과 동일하게 응급의료수가를 산정합니다.  

    1. 응1 응급의료관리료, 응3 중증응급환자 진료구역관찰료, 응4 응급환자 진료구역 관찰료, 응7 응급환자 중증도 분류 및 선별료, 응7-1 정신응급환자 초기 평가료, 응8 외상환자 관리료 등은 1회에 한하여 산정됩니다.  
    2. 응급실 방문 중 한 번이라도 입원환자 본인부담률 산정조건에 해당되면, 전체 응급실 요양급여비용은 입원환자 본인부담률에 따라 산정됩니다.  
    3. 위의 2번에 해당하지 않는 경우, 「국민건강보험법 시행규칙」 [별표 6] 제1호 사목 2)‧3)에 따라 본인부담률을 각각 적용합니다.  

    참조 문서:  
    - [★(제2024-181호, 9.12.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3 - Page 1](https://example.com/link1)  
    - [★(제2024-181호, 9.12.) 요양급여의 적용기준 및 방법에 관한 세부사항 일부개정안_v3 - Page 4](https://example.com/link2)  
    </example>
    
    """
    response = model.generate_content(
    prompt,
    # generation_config={
    #     "temperature": 1,
    #     "max_output_tokens": 2048,
    #     "top_p": 1.0,
    #     "top_k": 40,
    # }
    )
    output_data = {
    "query": query,
    "answer_text": answer_text,
    "references_map": reference_map,
    "response": response.text 
    }   
    with open("result.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        
    raw_markdown = response.text.replace('\n', '  \n').strip()
    html_content = markdown.markdown(
        raw_markdown,
        extensions=['markdown.extensions.tables']  # 테이블 변환을 위한 확장
    )
    
    
    parsed_results = {
        "answer_text": response.text,
        "answer_html": html_content,
        "references": reference_map,
    }
    return parsed_results
    
    
def parse_data(data,test):
    answer_text = data.get('answer', {}).get('answerText', '')
    citations = data.get('answer', {}).get('citations', [])
    references = data.get('answer', {}).get('references', [])

    # Create a mapping of referenceId to their corresponding metadata and URL
    reference_map = {}
    for idx, ref in enumerate(references):
        chunk_info = ref.get('chunkInfo', {})
        doc_meta = chunk_info.get('documentMetadata', {})
        uri = doc_meta.get('uri', '#')
        # Convert gs:// links to https://
        if uri.startswith('gs://'):
            uri = uri.replace('gs://', 'https://storage.googleapis.com/')
        reference_map[str(idx)] = {
            'title': doc_meta.get('title', 'No Title'),
            'uri': uri,
            'page': doc_meta.get('pageIdentifier', 'Unknown'),
            'relevance': chunk_info.get('relevanceScore', 'N/A'),
            'content': chunk_info.get('content', '')
        }
        print(reference_map)
        
    # Sort citations by endIndex in descending order to avoid insertion conflicts
    citations.sort(key=lambda x: int(x.get('endIndex', 0)), reverse=True)

    # Process the answer text to insert citations
    for citation in citations:
        end_index = int(citation.get('endIndex', 0))
        start_index = int(citation.get('startIndex', 0)) if 'startIndex' in citation else None
        sources = citation.get('sources', [])
        if sources:
            # Collect all reference URIs for the current citation
            links = []
            for source in sources:
                ref_id = source.get('referenceId', '')
                ref_meta = reference_map.get(ref_id, {})
                uri = ref_meta.get('uri', '#')
                links.append(f'<a href="{uri}" target="_blank">[{int(ref_id) + 1}]</a>')
            # Join multiple links if they exist
            citation_links = ' '.join(links)

            # Insert the citation links at the correct location
            if start_index is not None:
                # Handle cases with both startIndex and endIndex
                answer_text = (
                    answer_text[:start_index]
                    + f'{citation_links} '
                    + answer_text[start_index:end_index]
                    + answer_text[end_index:]
                )
            else:
                # Insert at endIndex only
                answer_text = (
                    answer_text[:end_index]
                    + f' {citation_links}'
                    + answer_text[end_index:]
                )

    # Final cleanup for consistent formatting
    parsed_results = {
        'answer': answer_text.replace('\n', ' ').strip() + "=========================Prompt적용=========================" + test,
        'references': list(reference_map.values()),
        'related_questions': data.get('answer', {}).get('relatedQuestions', [])
    }
    return parsed_results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
