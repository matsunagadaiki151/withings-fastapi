import datetime
import pickle
from typing import Any, Dict, Optional
from xmlrpc.client import DateTime

import requests


class Token:
    """Class about Token"""

    def __init__(
        self,
        url: str,
        headers: Dict[str, str],
        access_token_path: str,
        refresh_token_path: str,
        limit_time_path: str,
    ):
        self.url = url
        self.headers = headers
        self.access_token_path = access_token_path
        self.refresh_token_path = refresh_token_path
        self.limit_time_path = limit_time_path

    def fetch_access_token(self, auth_code: str) -> None:
        params = {
            "code": auth_code,
        }

        response_token = requests.get(
            f"{self.url}/get_token", params=params, headers=self.headers
        ).json()

        self.save_tokens(response_token)

    def fetch_refreshed_token(self, refresh_token: str) -> None:
        """Re-get access token from refresh token."""
        response_refresh = requests.get(
            f"{self.url}/refresh_token",
            headers=self.headers,
            params={"refresh_token": refresh_token},
        ).json()

        self.save_tokens(response_refresh)

    def save_token(self, token: str, file_path: str) -> None:
        """save token to pickle"""
        with open(file_path, "wb") as f:
            pickle.dump(token, f)

    def save_tokens(self, response: Any) -> None:
        self.save_token(
            str(response["body"]["access_token"]), self.access_token_path
        )
        self.save_token(
            str(response["body"]["refresh_token"]),
            self.refresh_token_path,
        )
        self.save_limit_time(
            int(response["body"]["expires_in"]), self.limit_time_path
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
