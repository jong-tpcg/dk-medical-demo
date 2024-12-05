from google.cloud import bigquery

def get_insurance_list(start_date, end_date):
    """
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
            "revision_date": row["revision_date"],
            "notification_number": row["notification_number"],
            "effective_date": row["effective_date"],
            "summary": row["summary"]
        })
    results = insurance_list
    for i in results:
        print(i)
    for item in results:
        item["revision_date"] = item["revision_date"].strftime('%Y-%m-%d %H:%M:%S')
        item["effective_date"] = item["effective_date"].strftime('%Y-%m-%d %H:%M:%S')
    return results[0]

# test
print(get_insurance_list('2024-05-01T00:00:00', '2024-05-31T00:00:00'))