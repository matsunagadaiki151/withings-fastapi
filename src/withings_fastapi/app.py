import os

import requests
import streamlit as st
from token_management import Token

from utils.load_env import load_env

st.title("今日の私の体重")

load_env()

url = os.environ.get("ENDPOINT")
access_token_path = "tokens/access_token.pkl"
refresh_token_path = "tokens/refresh_token.pkl"

headers = {"content-type": "application/json"}

token = Token(url, headers)

if (
    not os.path.exists(access_token_path)
    and "code" not in st.experimental_get_query_params()
):
    st.write(
        f"""
        <a target="_self" href="
    {url}">
            <button>
                Get Access Token
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )
elif not os.path.exists(access_token_path):
    params = {
        "code": st.experimental_get_query_params()["code"][0],
    }

    response_token = requests.get(
        f"{url}/get_token", params=params, headers=headers
    ).json()

    st.write(
        """<p>
            Authentication completed.
            If you are not transitioned, please reload.
            </p>
        """,
        unsafe_allow_html=True,
    )

    token.save_token(response_token["body"]["access_token"], access_token_path)
    token.save_token(
        response_token["body"]["refresh_token"], refresh_token_path
    )
    st.experimental_rerun()
else:
    # Disable query params
    st.experimental_set_query_params()

    access_token = token.load_token(access_token_path)
    token_params = {
        "access_token": access_token,
    }
    response_weights = requests.get(
        f"{url}/load_measure", headers=headers, params=token_params
    ).json()
    st.write(response_weights)
