import os

import requests
import streamlit as st
from dotenv import load_dotenv

# from processer import obtain_weights_from_json


def load_env() -> None:
    load_dotenv(verbose=True)
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)


def obtain_refreshed_token(refresh_token: str) -> str:
    """Re-get access token from refresh token.

    Returns
    -------
    str
        Reacquired access token
    """
    response_refresh = requests.get(
        f"{url}/refresh_token",
        headers=headers,
        params={"refresh_token": refresh_token},
    ).json()
    return str(response_refresh["body"]["access_token"])


load_env()

st.title("今日の私の体重")

url = os.environ.get("ENDPOINT")


if "code" not in st.experimental_get_query_params():
    st.write(
        f"""
        <a target="_self" href="
    {url}">
            <button>
                OAuth2で認可する。
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )
else:
    params = {
        "code": st.experimental_get_query_params()["code"][0],
    }
    headers = {"content-type": "application/json"}
    response_token = requests.get(
        f"{url}/get_token", params=params, headers=headers
    ).json()
