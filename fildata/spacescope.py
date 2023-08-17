import datetime
import os

import pandas as pd
import requests
from tqdm.auto import tqdm

SPACESCOPE_TOKEN = os.environ.get("SPACESCOPE_TOKEN")
SPACESCOPE_API_ENDPOINT = "https://api.spacescope.io/v2/"
FILECOIN_FIRST_DAY = datetime.date(2020, 10, 15)


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

    return response["data"]


def historical_power_data(miner_id=None, use_cache=True):
    if use_cache:
        df_power_data = pd.read_csv(
            "/tmp/storage_provider_power.csv", parse_dates=["stat_date"]
        )

    today = datetime.date.today()
    latest_day = today - datetime.timedelta(days=2)

    df_power_data = pd.DataFrame()

    for day in tqdm(pd.date_range(FILECOIN_FIRST_DAY, latest_day, freq="d")):
        power_data = get_power_data(date=day.strftime("%Y-%m-%d"), miner_id=miner_id)
        df_power_data = pd.concat(
            [df_power_data, pd.DataFrame(power_data)], ignore_index=True
        )

    return df_power_data
