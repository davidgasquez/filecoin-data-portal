import os
import requests

SPACESCOPE_TOKEN = os.environ.get("SPACESCOPE_TOKEN")
SPACESCOPE_API_ENDPOINT = "https://api.spacescope.io/v2/"


def call_method(method: str, params=None):
    endpoint = f"{SPACESCOPE_API_ENDPOINT}/{method}"
    headers = {"Authorization": f"Bearer {SPACESCOPE_TOKEN}"}

    r = requests.get(
        endpoint,
        headers=headers,
        params=params,
    )

    if r.status_code != 200:
        raise Exception(f"Error: {r.text}")

    return r.json()


def get_power_data(date=None, miner_id=None):
    response = call_method(
        "storage_provider/power", params={"state_date": date, "miner_id": miner_id}
    )

    return response
