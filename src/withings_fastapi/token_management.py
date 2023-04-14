import datetime
import pickle
from typing import Dict, Optional
from xmlrpc.client import DateTime

import requests
from requests import Response


class Token:
    """Class about Token"""

    def __init__(self, url: str, headers: Dict[str, str]):
        self.url = url
        self.headers = headers

    def fetch_access_token(self, auth_code: str) -> Response:
        data = {"code": auth_code}

        response = requests.post(
            f"{self.url}/get_token", params=data, headers=self.headers
        )

        return response

    def fetch_refreshed_token(self, refresh_token: str) -> None:
        """Re-get access token from refresh token."""

        data = {"refresh_token": refresh_token}
        requests.post(
            f"{self.url}/refresh_token", headers=self.headers, params=data
        )

    def load_token(self, file_path: str) -> str:
        """load pickled token"""
        with open(file_path, "rb") as f:
            token: str = pickle.load(f)
        return token

    def save_limit_time(self, expiration_time: int, filename: str) -> None:
        limit_time = datetime.datetime.now() + datetime.timedelta(
            seconds=expiration_time
        )
        with open(filename, "wb") as f:
            pickle.dump(limit_time, f)

    def load_limit_time(self, filename: str) -> Optional[DateTime]:
        with open(filename, "rb") as f:
            limit_time: Optional[DateTime] = pickle.load(f)
        return limit_time
