from utils.agent_builder_query_nfilter import DiscoveryEngineClient
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
)


# Function Declaration 정의
get_noti_list_func = FunctionDeclaration(
    name="get_noti_list",
    description="Get the list Notification results from the datastore",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query for QnA data"},
        },
        "required": ["query"],
    },
)

# Tool 정의
qna_tool = Tool(
    function_declarations=[get_qna_list_func],
)

def get_qna_datastore(query):
    print("QNA TOOL Query: ", query)
    project_number = '556320446019'
    data_stroe_id = 'demo-dk-qna-csv_1733369222458'

    client = DiscoveryEngineClient(project_number, data_stroe_id)
    result = client.search(query)
    qna_results = []
    if "results" in result:
        for item in result["results"]:
            document = item.get("document", {})
            struct_data = document.get("structData", None)
            if struct_data:
                qna_results.append(struct_data)
    return qna_results

get_qna_list_func = FunctionDeclaration(
    name="get_qna_list",
    description="Get the list QnA results from the datastore",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query for QnA data"},
        },
        "required": ["query"],
    },
)
