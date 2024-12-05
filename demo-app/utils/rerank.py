from google.cloud import discoveryengine_v1 as discoveryengine

def remove_id_duplicate(rows, key="id"):
    seen = set()
    unique_dict_list = []
    
    for d in rows:
        if d[key] not in seen:
            unique_dict_list.append(d)
            seen.add(d[key])
    
    return unique_dict_list

def rank_query(query, project_id, rows, datastore_id):
    client = discoveryengine.RankServiceClient()
    resopnse = routing_parser(datastore_id, rows)
    remove_duplicate = remove_id_duplicate(resopnse)
    # The full resource name of the ranking config.
    # Format: projects/{project_id}/locations/{location}/rankingConfigs/default_ranking_config
    ranking_config = client.ranking_config_path(
        project=project_id,
        location="global",
        ranking_config="default_ranking_config",
    )
    request = discoveryengine.RankRequest(
        ranking_config=ranking_config,
        model="semantic-ranker-512@latest",
        top_n=10,
        query=query,
        records=[
            discoveryengine.RankingRecord(
                id=row["id"],
                title=row.get("title", "Not found"),
                content=row.get("content") or row.get("answer", "Not found")
            )
            for row in remove_duplicate
        ]
    )

    response = client.rank(request=request)

    # Handle the response
    print(response)
    return response

def ocr_search_parse(response):
    parsed_results = []
    for result in response['results']:
        document = result.get('document', {})
        parsed_results.append({
            "id": document.get("id", "No ID"),
            "title": document.get("derivedStructData", {}).get("title", "No Title"),
            "content": document.get("derivedStructData", {}).get("extractive_answers", [{"content": "No Content"}])[0].get("content", "No Content"),
            "page_number": document.get("derivedStructData", {}).get("extractive_answers", [{}])[0].get("pageNumber", "No Page Number"),
            "link": document.get("derivedStructData", {}).get("link", "No Link")
        })

    return parsed_results
    
def faq_search_parse(response):
        parsed_results = []
        for result in response['results']:
            print(result)
            document = result.get('document', {})
            struct_data = document.get('structData', {})
            parsed_results.append({
                "id": document.get("id", "No ID"),
                "title": struct_data.get("document_title", "No Title"),
                "question": struct_data.get("question", "No Question"),
                "answer": struct_data.get("answer", "No Answer"),
                "document_uri": struct_data.get("document_uri", "No URI")
            })
        return parsed_results

def routing_parser(datastore_id, response):
    if datastore_id == 'dk-demo-ocr-insurance_1727419968121':
        return ocr_search_parse(response)
    elif datastore_id == 'demo-dk-qna-csv_1733369222458':
        return faq_search_parse(response)
    else:
        return {"error": "Datastore ID not found."}
    
# Example usage
# print(rank_query("What is Google Gemini?", "dk-medical-solutions"))

# API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
# API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
PROJECT_NUMBER = '556320446019'
DATA_STORE_ID = 'demo-dk-qna-csv_1733369222458'
# DATA_STORE_ID = 'dk-demo-ocr-insurance_1727419968121'
# DATA_STORE_ID = 'dk-demo-ocr-search_1727419939769'
from agent_builder_query_nfilter import DiscoveryEngineClient

query = "응급의료수가 산정할 때 응급실 재방문 시 규정은 어떻게 되나요?"
client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)
rslt = client.search(query)
# print(ranking_parser(rslt))
# print(rslt)

rank_query(query, project_id=PROJECT_NUMBER, rows=rslt, datastore_id=DATA_STORE_ID)