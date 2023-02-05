import pickle
from typing import Dict

import requests


class Token:
    """Class about Token"""

    def __init__(self, url: str, headers: Dict[str, str]):
        self.url = url
        self.headers = headers

    def fetch_refreshed_token(self, refresh_token: str) -> str:
        """Re-get access token from refresh token.

        Returns
        -------
        str
            Reacquired access token
        """
        response_refresh = requests.get(
            f"{self.url}/refresh_token",
            headers=self.headers,
            params={"refresh_token": refresh_token},
        ).json()
        return str(response_refresh["body"]["access_token"])

    def save_token(self, token: str, file_path: str) -> None:
        """save token to pickle"""
        with open(file_path, "wb") as f:
            pickle.dump(token, f)

    def load_token(self, file_path: str) -> str:
        """load pickled token

        Parameters
        ----------
        file_path : str
            file_path

        Returns
        -------
        str
            loaded_token
        """
        with open(file_path, "rb") as f:
            token: str = pickle.load(f)
        return token
