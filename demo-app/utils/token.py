import logging
import json
import requests
from google.auth.transport.requests import Request
import google.auth

# 로거 설정
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_access_token():
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        request = Request()
        credentials.refresh(request)
        if not credentials.valid or credentials.expired:
            credentials.refresh(request)
        return credentials.token
    except Exception as e:
        logger.error(f"토큰 발급 실패: {e}")
        raise e
