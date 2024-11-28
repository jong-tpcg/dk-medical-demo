from flask import Flask, render_template, request
import requests
import json
from google.auth.transport.requests import Request

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
                }
            }
            response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                data = response.json()
                parsed_data = parse_data(data)
                return render_template('index.html', query=query, results=parsed_data)
            else:
                error = "Error fetching data from API."
                return render_template('index.html', error=error)
    return render_template('index.html')

def parse_data(data):
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
        'answer': answer_text.replace('\n', ' ').strip(),
        'references': list(reference_map.values()),
        'related_questions': data.get('answer', {}).get('relatedQuestions', [])
    }
    return parsed_results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
