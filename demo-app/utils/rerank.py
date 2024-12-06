from google.cloud import discoveryengine_v1 as discoveryengine
from google.protobuf.json_format import MessageToDict, MessageToJson


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
    record_map = {r["id"]: r for r in remove_duplicate}
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

    rank_response = client.rank(request=request)

    # Handle the response
    # print(response)
    response = []
    for i in rank_response.records:
        response.append(
            {
            "id": i.id,
            "title": i.title,
            "content": i.content,
            "score": i.score
        }
        )
    reranked_records = []
    # `ranking_response_json` structure should be checked; 
    # assuming it has a top-level "records" array or similar.
    for rec in response:
        rec_id = rec["id"]
        original_record = record_map.get(rec_id, {})
        
        # Add fields from original record to the reranked record
        rec["uri"] = original_record.get("uri", "No URI")
        rec["pageIdentifier"] = original_record.get("pageIdentifier", "No Page Identifier")
        rec["relevanceScore"] = original_record.get("relevanceScore", "No Relevance Score")
        
        reranked_records.append(rec)
    
    # Return the enriched reranked records
    return {"records": reranked_records}
    # return response

# def ocr_search_parse(response):
#     parsed_results = []
#     for result in response['results']:
#         document = result.get('document', {})
#         parsed_results.append({
#             "id": document.get("id", "No ID"),
#             "title": document.get("derivedStructData", {}).get("title", "No Title"),
#             "content": document.get("derivedStructData", {}).get("extractive_answers", [{"content": "No Content"}])[0].get("content", "No Content"),
#             "page_number": document.get("derivedStructData", {}).get("extractive_answers", [{}])[0].get("pageNumber", "No Page Number"),
#             "link": document.get("derivedStructData", {}).get("link", "No Link")
#         })

#     return parsed_results

def ocr_search_parse(response):
    parsed_results = []
    references = response.get("answer", {}).get("references", [])
    
    for ref in references:
        chunk_info = ref.get("chunkInfo", {})
        content = chunk_info.get("content", "No Content")
        relevance_score = chunk_info.get("relevanceScore", "No Relevance Score")
        
        metadata = chunk_info.get("documentMetadata", {})
        doc_id = metadata.get("document", "No ID")
        title = metadata.get("title", "No Title")
        uri = metadata.get("uri", "No URI")
        page_identifier = metadata.get("pageIdentifier", "No Page Identifier")
        
        parsed_results.append({
            "id": doc_id + "_" + page_identifier,
            "title": title,
            "content": content,
            "uri": uri,
            "pageIdentifier": page_identifier,
            "relevanceScore": relevance_score
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


def fact_parser(response):
    parsed_facts = []
    for record in response.get("records", []):
        parsed_facts.append({
            "factText": record.get("content", "No Content"),
            "attributes": {
                "id": str(record.get("id", "No ID")),
                "title": str(record.get("title", "No Title")),
                "score": str(record.get("score", "No Score"))
            }
        })
    return parsed_facts




# # Example usage
# # print(rank_query("What is Google Gemini?", "dk-medical-solutions"))

# API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
# API_ENDPOINT = "https://discoveryengine.googleapis.com/v1alpha/projects/556320446019/locations/global/collections/default_collection/engines/dk-demo-ocr-search_1727419939769/servingConfigs/default_search:answer"
# PROJECT_NUMBER = '556320446019'
# # DATA_STORE_ID = 'demo-dk-qna-csv_1733369222458'
# DATA_STORE_ID = 'dk-demo-ocr-insurance_1727419968121'
# # DATA_STORE_ID = 'dk-demo-ocr-search_1727419939769'
# from agent_builder_query_nfilter import DiscoveryEngineClient

# query = "응급의료수가 산정할 때 응급실 재방문 시 규정은 어떻게 되나요?"
# client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)
# rslt = client.search(query)
# # print(ranking_parser(rslt))
# print(rslt)


# rslt = rank_query(query, project_id=PROJECT_NUMBER, rows=rslt, datastore_id=DATA_STORE_ID)
# print(rslt)
# print("=====================================================================")
# facts = fact_parser(rslt)
# print(facts)
# temp_answer = "응급실 재방문 시 응급의료수가 산정 기준은, 동일 상병 또는 증상으로 당일 또는 퇴실 후 6시간 이내에 응급실을 재방문하는 경우, 응급실 진료가 계속된 것과 동일하게 응급의료수가를 산정합니다. 즉, 재방문 시에도 수가가 추가로 산정되는 것이 아니라, 기존 진료의 연장으로 간주됩니다."
# print("=====================================================================")
# rslt = client.check_grounding(
#     project_id=PROJECT_NUMBER,
#     answer_candidate=temp_answer,
#     facts=facts,
#     citation_threshold=0.8,
#     )
# print(rslt)