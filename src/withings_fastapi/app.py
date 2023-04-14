import datetime
import os

import plotly.express as px
import requests
import streamlit as st
from token_management import Token

from utils.load_env import load_env

st.title("今日の私の体重")

load_env()


url = os.environ.get("ENDPOINT")

headers = {"content-type": "application/json"}

tokens = requests.get(
    f"{url}/load_token_from_json_server",
    headers=headers,
).json()

token_management = Token(url, headers)

if "code" not in st.experimental_get_query_params() and (
    tokens is None
    or tokens["accessToken"] == ""
    or tokens["accessToken"] is None
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
elif (
    tokens is None
    or tokens["accessToken"] == ""
    or tokens["accessToken"] is None
):
    token_management.fetch_access_token(
        st.experimental_get_query_params()["code"][0]
    )

    st.write(
        """<p>
            Authentication completed.
            If you are not transitioned, please reload.
            </p>
        """,
        unsafe_allow_html=True,
    )

    st.experimental_rerun()
else:
    # Disable query params
    st.experimental_set_query_params()

    access_token = str(tokens["accessToken"])
    refresh_token = str(tokens["refreshToken"])
    str_limit_time = str(tokens["limitTime"])
    limit_time = datetime.datetime.strptime(
        str_limit_time, "%Y-%m-%d %H:%M:%S"
    )

    if datetime.datetime.now() > limit_time:
        token_management.fetch_refreshed_token(refresh_token)

        # Access Tokenを取得するために再起動する。
        st.experimental_rerun()

    token_params = {
        "access_token": access_token,
    }
    response_weights = requests.get(
        f"{url}/load_measures", headers=headers, params=token_params
    ).json()

    weights_dic = {k: v for k, v in response_weights.items()}

    date_weights_dic_keys = [
        datetime.datetime.strptime(k, "%Y/%m/%d") for k in weights_dic.keys()
    ]

    fig = px.line(x=date_weights_dic_keys, y=weights_dic.values())

    today_str = datetime.date.today().strftime("%Y/%m/%d")
    if today_str in weights_dic:
        st.write(f"今日の体重 : {weights_dic[today_str]}kg")
    else:
        st.write("今日の体重はまだ測られていません")

    st.plotly_chart(fig)
