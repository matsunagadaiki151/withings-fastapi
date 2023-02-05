import os

import requests
import streamlit as st
from load_env import load_env

# from processer import obtain_weights_from_json

st.title("今日の私の体重")

url = os.environ.get("ENDPOINT")

load_env()

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
    st.write(response_token["body"]["access_token"])
