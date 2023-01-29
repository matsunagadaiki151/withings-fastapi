import datetime
import os
from typing import Any, Union

import requests
import uvicorn
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

CLIENT_ID = os.environ.get("CLIENT_ID")
CUSTOMER_SECRET = os.environ.get("CUSTOMER_SECRET")
STATE = os.environ.get("STATE")
ACCOUNT_URL = os.environ.get("ACCOUNT_URL")
WBSAPI_URL = os.environ.get("WPSAPI_URL")
CALLBACK_URI = os.environ.get("CALLBACK_URI")

app = FastAPI()


@app.get("/")
async def root() -> RedirectResponse:
    payload = {
        "response_type": "code",  # imposed string by the api
        "client_id": CLIENT_ID,
        "state": STATE,
        "scope": "user.metrics",  # see docs for enhanced scope
        "redirect_uri": CALLBACK_URI,  # URL of this app
        "mode": "demo",  # Use demo mode, DELETE THIS FOR REAL APP
    }

    r_auth = requests.post(
        f"{ACCOUNT_URL}/oauth2_user/authorize2", params=payload
    )

    print(r_auth.url)

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

    access_token = r_token["body"]["access_token"]

    now_date = datetime.datetime.now()
    start_date = now_date - relativedelta(months=1)

    # GET Some info with this token
    headers = {"Authorization": "Bearer " + access_token}
    payload = {
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

    return r_metrics


def main() -> None:
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
