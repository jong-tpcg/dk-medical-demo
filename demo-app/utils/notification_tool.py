import vertexai
from google.cloud import bigquery
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
)
import google.auth
from google.auth.transport.requests import Request
from datetime import datetime
        
def validate_date_format(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False
# BigQuery에서 데이터 가져오는 함수 정의
def get_noti_list(start_date, end_date):
    """
    Fetches notifications from BigQuery based on the specified date range.

    Args:
        start_date (str): Start date in ISO format (e.g., 2024-05-01T00:00:00).
        end_date (str): End date in ISO format (e.g., 2024-05-31T23:59:59).

    Returns:
        list[dict]: List of notifications with revision date, notification number, effective date, and summary.
    """
    if not validate_date_format(start_date) or not validate_date_format(end_date):
        raise ValueError("Invalid date format. Dates must be in ISO 8601 format (e.g., 2024-05-01).")

    print(f"Fetching notifications between {start_date} and {end_date}...")
    credentials, project = google.auth.default()
    credentials.refresh(Request())
    client = bigquery.Client(credentials=credentials , project="556320446019")
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
    
    try:
        query_job = client.query(query)
        results = query_job.result()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    
    # 결과 데이터 정리
    insurance_list = []
    for row in results:
        insurance_list.append({
            "revision_date": row["revision_date"].strftime('%Y-%m-%d %H:%M:%S') if row["revision_date"] else "",
            "effective_date": row["effective_date"].strftime('%Y-%m-%d %H:%M:%S') if row["effective_date"] else "",
            "notification_number": row["notification_number"],
            "summary": row["summary"]
        })
    print("결과" , insurance_list)
    print(f"Fetched {len(insurance_list)} notifications.")
    return insurance_list


# Function Declaration 정의
get_noti_list_func = FunctionDeclaration(
    name="get_noti_list",
    description=(
        "Fetches notification data from BigQuery for a given date range. "
        "The results include revision date, notification number, effective date, and a summary."
        ),
    parameters={
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date for fetching notifications in ISO format (e.g., 2024-05-01)."
            },
            "end_date": {
                "type": "string",
                "description": "End date for fetching notifications in ISO format (e.g., 2024-05-31)."
            },
        },
        "required": ["start_date", "end_date"],
    },
)

# Tool 정의
noti_tool = Tool(
    function_declarations=[get_noti_list_func],
)

get_noti_list("2024-09-01","2024-09-30")