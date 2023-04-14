import datetime
import os
from typing import Any, Dict, Union

import requests
import uvicorn
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from server.processer import (
    calc_limit_time,
    fetch_weights_from_json,
    write_tokens_to_json_server,
)
from utils.load_env import load_env

load_env()


class Code(BaseModel):
    code: str


CLIENT_ID = os.environ.get("CLIENT_ID")
CUSTOMER_SECRET = os.environ.get("CUSTOMER_SECRET")
STATE = os.environ.get("STATE")
ACCOUNT_URL = os.environ.get("ACCOUNT_URL")
WBSAPI_URL = os.environ.get("WPSAPI_URL")
CALLBACK_URI = os.environ.get("CALLBACK_URI")
JSON_SERVER_URL = os.environ.get("JSON_SERVER_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> RedirectResponse:
    payload = {
        "response_type": "code",  # imposed string by the api
        "client_id": CLIENT_ID,
        "state": STATE,
        "scope": "user.metrics",  # see docs for enhanced scope
        "redirect_uri": CALLBACK_URI,  # URL of this app
    }

    r_auth = requests.get(
        f"{ACCOUNT_URL}/oauth2_user/authorize2", params=payload
    )

    return RedirectResponse(r_auth.url)


@app.get("/get_token")
async def get_token(code: Union[str, None]) -> Any:
    """
    Callback route when the user has accepted to share his data.
    Once the auth has arrived Withings servers come back with
    an authentication code and the state code provided in the
    initial call
    """

    if code is None:
        return {"error": "code is not define"}

    payload = {
        "action": "requesttoken",
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CUSTOMER_SECRET,
        "code": code,
        "redirect_uri": CALLBACK_URI,
    }

    r_token = requests.post(f"{WBSAPI_URL}/v2/oauth2", data=payload).json()

    return r_token


@app.post("/get_token")
async def update_token(code: str) -> None:

    if code == "" or code is None:
        raise TypeError("code is not defined")

    if CALLBACK_URI is None:
        raise TypeError("CALLBACK_URI is not defined")

    payload = {
        "action": "requesttoken",
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CUSTOMER_SECRET,
        "code": code,
        "redirect_uri": CALLBACK_URI,
    }

    r_token = requests.post(f"{WBSAPI_URL}/v2/oauth2", data=payload).json()

    if r_token["status"] != 601:
        limit_time = calc_limit_time(r_token["body"]["expires_in"])
        # limitTimeをstrに置き換える。
        str_limit_time = limit_time.strftime("%Y-%m-%d %H:%M:%S")

        json_server_payload: Dict[str, str] = {
            "accessToken": r_token["body"]["access_token"],
            "refreshToken": r_token["body"]["refresh_token"],
            "limitTime": str_limit_time,
        }

        if type(JSON_SERVER_URL) == str:
            write_tokens_to_json_server(
                json_server_payload, f"{JSON_SERVER_URL}/tokens"
            )


@app.get("/refresh_token")
async def fetch_refresh_token(refresh_token: str) -> Any:

    if refresh_token is None:
        return {"error": "refresh_tokenがありません"}

    # GET Some info with this token
    headers = {"Authorization": "Bearer " + refresh_token}
    payload = {
        "action": "requesttoken",
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CUSTOMER_SECRET,
        "refresh_token": refresh_token,
    }

    # List devices of returned user
    r_token = requests.get(
        f"{WBSAPI_URL}/v2/oauth2", headers=headers, params=payload
    ).json()

    return r_token


@app.post("/refresh_token", response_model=None)
async def update_refresh_token(
    refresh_token: Union[str, None]
) -> Union[RedirectResponse, Dict[str, str]]:

    if refresh_token is None or refresh_token == "":
        raise TypeError("refresh_token is not defined")

    if CALLBACK_URI is None or CALLBACK_URI == "":
        raise TypeError("CALLBACK_URI is not defined")

    # GET Some info with this token
    headers = {"Authorization": "Bearer " + refresh_token}
    payload = {
        "action": "requesttoken",
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CUSTOMER_SECRET,
        "refresh_token": refresh_token,
    }

    # List devices of returned user
    r_token = requests.get(
        f"{WBSAPI_URL}/v2/oauth2", headers=headers, params=payload
    ).json()

    limit_time = calc_limit_time(r_token["body"]["expires_in"])
    # limitTimeをstrに置き換える。
    str_limit_time = limit_time.strftime("%Y-%m-%d %H:%M:%S")

    json_server_payload: Dict[str, str] = {
        "accessToken": r_token["body"]["access_token"],
        "refreshToken": r_token["body"]["refresh_token"],
        "limitTime": str_limit_time,
    }

    if type(JSON_SERVER_URL) == str:
        write_tokens_to_json_server(
            json_server_payload, f"{JSON_SERVER_URL}/tokens"
        )

    return RedirectResponse(CALLBACK_URI)


@app.get("/load_token_from_json_server")
async def load_token_from_json_server() -> Any:
    return requests.get(f"{JSON_SERVER_URL}/tokens").json()


@app.get("/load_measures")
async def load_measures(access_token: Union[str, None]) -> Any:
    if access_token is None:
        return {"error": "access_tokenがありません"}
    now_date = datetime.datetime.now()
    start_date = now_date - relativedelta(months=3)

    # GET Some info with this token
    headers = {"Authorization": "Bearer " + access_token}
    payload = {
        "aceess_token": access_token,
        "action": "getmeas",
        "meastype": "1",
        "category": "1",
        "startdate": str(int(start_date.timestamp())),
        "enddate": str(int(now_date.timestamp())),
    }

    # List devices of returned user
    r_metrics = requests.get(
        f"{WBSAPI_URL}/measure", headers=headers, params=payload
    ).json()

    measures = fetch_weights_from_json(r_metrics["body"]["measuregrps"])
    return measures


def main() -> None:
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
