from google.cloud import bigquery
# from langchain.llms import VertexAI
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
import json
from datetime import datetime


@tool
def get_insurance_list(start_date : str, end_date : str) -> list:
    """
    Bigquery에 등록된 보험심사 고시 데이터를 시작일과 종료일 사이에 맞춰 가져오는 함수
    Args : 
        start_date : Datetime
            ex : 2024-05-01T00:00:00
        end_date : Datetime
            ex : 2024-05-01T00:00:00
    """
    client = bigquery.Client()
    print(f"start_date: {start_date}, end_date : {end_date}")
    query = f"""
    SELECT 
        revision_date AS revision_date, 
        notification_number AS notification_number, 
        effective_date AS effective_date, 
        summary AS summary
    FROM `dk-medical-solutions.dk_demo.notification-list-ga`
    WHERE revision_date BETWEEN '{start_date}' AND '{end_date}'
        OR effective_date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY revision_date DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    insurance_list = []
    for row in results:
        insurance_list.append({
            "revision_date": row["revision_date"].strftime('%Y-%m-%d %H:%M:%S') if row["revision_date"] else "",
            "effective_date": row["effective_date"].strftime('%Y-%m-%d %H:%M:%S') if row["effective_date"] else "",
            "notification_number": row["notification_number"],
            "summary": row["summary"]
        })
    results = insurance_list
    return results

@tool
def get_insurance_recent_list() -> list:
    """
    Bigquery에 등록된 보험심사 고시 데이터를 가장 최근 고시 5개만 가져오는 함수
    """
    client = bigquery.Client()
    print(f"최근 고시 가져오기")
    query = f"""
    SELECT 
        revision_date AS revision_date, 
        notification_number AS notification_number, 
        effective_date AS effective_date, 
        summary AS summary
    FROM `dk-medical-solutions.dk_demo.notification-list-ga`
    ORDER BY revision_date DESC
    LIMIT 3;
    """
    query_job = client.query(query)
    results = query_job.result()
    insurance_list = []
    for row in results:
        insurance_list.append({
            "revision_date": row["revision_date"].strftime('%Y-%m-%d %H:%M:%S') if row["revision_date"] else "",
            "effective_date": row["effective_date"].strftime('%Y-%m-%d %H:%M:%S') if row["effective_date"] else "",
            "notification_number": row["notification_number"],
            "summary": row["summary"]
        })
    results = insurance_list
    return results



tool_list = [get_insurance_list,get_insurance_recent_list]
from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools=tool_list)
def call_vertex_ai_gemini_model(prompt_text):
    current_date = datetime.now().strftime('%Y-%m-%d')
    llm = ChatVertexAI(model_name="gemini-1.5-flash-002")
    llm = llm.bind_tools(tool_list)
    messages = [
        {
            "role": "system",
            "content": "당신은 사용자가 질문하는 내용에 의도에 따라 TOOL을 호출하세요.\n\n\
            1. 사용자의 질문이 특정 고시에 대한 정확한 정보를 포함하고 있는 경우, 예를 들어 \"오늘 고시된 제2024-181호 고시 내용을 자세히 알려주세요.\"와 같이 고시 내용을 알고 싶어하는 질문이라면 TOOL을 호출하지 않습니다.\n\n\
            2. 사용자의 질문이 고시에 대해서 물어보는 질문이 아닐경우 ex. 산정 기준 TOOL을 호출하지 않습니다.\n\n\
            3. 사용자의 질문이 고시된 내용에 대해 알고 싶어하면서 특정 기간을 포함한 경우, 예를 들어 \"9월에 고시된 내용을 알려주세요.\" ,\"최근 한달내 고시된 내용을 알려주세요.\"와 같이 기간 정보가 포함된 질문이라면 현재 날짜 또는 사용자 질문에 맞게 기간을 정의한 후 `get_insurance_list` Tool을 호출합니다. 이때, 사용자의 질문에서 기간 정보를 추출합니다. 예를 들어, \"9월에 고시된 내용을 알려주세요.\"는 9월 1일부터 9월 30일까지의 데이터를 가져옵니다.\n\n\
            4. 사용자의 질문이 기간을 명시 안하면서 최근에or 마지막 고시된 내용을 알고 싶어하는 경우,  `get_insurance_recent_list` Tool을 호출합니다."
        },
        {
            "role": "user",
            "content": prompt_text,
        },
        {
            "role": "system",
            "content": f"현재 날짜: {current_date}",
        },
    ]
    # response = llm.invoke(prompt_text)
    response = tool_node.invoke({"messages": [llm.invoke(messages)]})
    # ToolMessage에서 content만 반환
    tool_result = None  # Tool 결과를 추적
    tool_called = False  # Tool 호출 여부를 추적
    for message in response.get("messages", []): 
        if hasattr(message, "name") and message.name in ["get_insurance_list", "get_insurance_recent_list"]:
            tool_result = message.content  # Tool의 결과를 가져옴
            tool_called = True
            break
    result = {
        "tool_called": tool_called,
        "results": tool_result if tool_result else []
    }
    return result

# 테스트
# rslt = call_vertex_ai_gemini_model("이번달 고시된 내용을 알려주세요")
# print(rslt)