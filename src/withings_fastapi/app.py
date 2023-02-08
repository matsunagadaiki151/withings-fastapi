import datetime
import os
import pickle
from typing import Optional
from xmlrpc.client import DateTime

import plotly.express as px
import requests
import streamlit as st
from token_management import Token

from utils.load_env import load_env

st.title("今日の私の体重")

load_env()

url = os.environ.get("ENDPOINT")
access_token_path = "tokens/access_token.pkl"
refresh_token_path = "tokens/refresh_token.pkl"
limit_time_path = "tokens/limit_time.pkl"

headers = {"content-type": "application/json"}

token = Token(url, headers)


def save_limit_time(expiration_time: int, filename: str) -> None:
    limit_time = datetime.datetime.now() + datetime.timedelta(
        seconds=expiration_time
    )
    with open(filename, "wb") as f:
        pickle.dump(limit_time, f)


def load_limit_time(filename: str) -> Optional[DateTime]:
    with open(filename, "rb") as f:
        limit_time: Optional[DateTime] = pickle.load(f)
    return limit_time


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
    save_limit_time(response_token["body"]["expires_in"], limit_time_path)
    st.experimental_rerun()
else:
    # Disable query params
    st.experimental_set_query_params()

    limit_time = load_limit_time(limit_time_path)
    access_token = token.load_token(access_token_path)

    token_params = {
        "access_token": access_token,
    }
    response_weights = requests.get(
        f"{url}/load_measures", headers=headers, params=token_params
    ).json()

    weights_dic = {
        datetime.datetime.strptime(k, "%Y/%m/%d"): v
        for k, v in response_weights.items()
    }

    fig = px.line(x=weights_dic.keys(), y=weights_dic.values())

    st.plotly_chart(fig)
