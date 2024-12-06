import requests
import json
import google.auth
from google.auth.transport.requests import Request

class DiscoveryEngineClient:
    """
    A client for interacting with the Google Discovery Engine API.
    """

    API_BASE_URL = 'https://discoveryengine.googleapis.com/v1beta'

    def __init__(self, project_number, data_store_id):
        """
        Initializes the DiscoveryEngineClient.

        Parameters:
        - project_number (str): Your Google Cloud project number.
        - data_store_id (str): Your data store ID.
        """
        self.project_number = project_number
        self.data_store_id = data_store_id
        self.access_token = self.get_default_access_token()

    @staticmethod
    def get_default_access_token():
        """
        Obtains the default access token using Google application default credentials.

        Returns:
        - str: The access token.
        """
        # Obtain the default credentials
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        credentials, _ = google.auth.default(scopes=scopes)

        # Refresh the credentials to get an access token
        credentials.refresh(Request())

        # Get the access token
        access_token = credentials.token

        return access_token

    def search(self, query, filter_expression=None, natural_language_query=True):
        """
        Performs a search using the Discovery Engine API.

        Parameters:
        - query (str): The search query string.
        - filter_expression (str, optional): The filter expression.
        - natural_language_query (bool, optional): Whether to use natural language query understanding.

        Returns:
        - dict: The JSON response from the API.
        """
        # Prepare the authorization header
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Construct the API endpoint URL
        url = (
            f'{self.API_BASE_URL}/projects/{self.project_number}'
            f'/locations/global/collections/default_collection/dataStores/{self.data_store_id}'
            '/servingConfigs/default_search:search'
        )

        # Prepare the payload
        payload = {
            'query': query,
            'pageSize':10,
            }

        if filter_expression:
            payload['filter'] = filter_expression

        if natural_language_query:
            payload['naturalLanguageQueryUnderstandingSpec'] = {
                'filterExtractionCondition': 'ENABLED'
            }

        # Make the POST request
        response = requests.post(url, headers=headers, json=payload) 

        # Check for errors
        if response.status_code != 200:
            raise Exception(f'API request failed with status code {response.status_code}: {response.text}')
        
        response.encoding = 'utf-8'
        # Return the JSON response
        return response.json()
    
    def check_grounding(self, project_id, answer_candidate, facts, citation_threshold="0.6", enable_claim_level_score=True):
        """
        Calls the grounding check API.

        Parameters:
        - project_id (str): Your Google Cloud project ID.
        - answer_candidate (str): The answer candidate to check.
        - facts (list): A list of facts to check against.
        - citation_threshold (str, optional): The citation threshold.
        - enable_claim_level_score (bool, optional): Whether to enable claim level score.

        Returns:
        - dict: The JSON response from the API.
        """
        # Prepare the authorization header
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Construct the API endpoint URL
        url = (
            f'https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}'
            '/locations/global/groundingConfigs/default_grounding_config:check'
        )

        # Prepare the payload
        payload = {
            'answerCandidate': answer_candidate,
            'facts': facts,
            'groundingSpec': {
                'citationThreshold': citation_threshold,
                'enableClaimLevelScore': enable_claim_level_score,
            }
        }
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)

        # Check for errors
        if response.status_code != 200:
            raise Exception(f'API request failed with status code {response.status_code}: {response.text}')

        response.encoding = 'utf-8'
        # Return the JSON response
        return response.json()

    def save_response_to_file(self, response_data, filename='result.json'):
        """
        Saves the response data to a JSON file.

        Parameters:
        - response_data (dict): The response data to save.
        - filename (str, optional): The filename to save the data to.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)

# # Example usage
# if __name__ == '__main__':
#     # Your project number and data store ID
#     PROJECT_NUMBER = '661430115304'
#     DATA_STORE_ID = 'ds-naver-cards-search_1729048293144'

#     # Replace these with your actual query and filter
#     QUERY = '주말에 여행, 외식, 주유가 많은 생활인데 혜택이 가장 좋은 카드 추천해줘. 연회비는 1만원 미만으로 해외결제가 가능한 카드로 알려줘.'
#     # FILTER = 'category:ANY("여행", "외식", "주유") AND domestic_annual_fee:IN(0,10000i) AND all:ANY("해외결제")'
#     FILTER = None

#     try:
#         # Initialize the client
#         client = DiscoveryEngineClient(PROJECT_NUMBER, DATA_STORE_ID)

#         # Perform the search
#         result = client.search(QUERY, filter_expression=FILTER)

#         # Print the result
#         print(json.dumps(result, indent=2, ensure_ascii=False))

#         # Save the result to a file
#         client.save_response_to_file(result, filename='result.json')

#     except Exception as e:
#         print(f'Error: {e}')
