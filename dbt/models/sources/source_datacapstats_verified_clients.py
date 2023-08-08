import os

import pandas as pd
import requests

url = "https://api.datacapstats.io/"
data_dir = os.getenv("DATA_DIR", "data")


def model(dbt, session):
    verified_clients = pd.DataFrame(
        requests.get(url + "api/getVerifiedClients").json()["data"]
    )

    verified_clients.drop(columns=["allowanceArray"]).to_csv(
        f"{data_dir}/verified_clients.csv", index=False
    )

    return verified_clients.drop(columns=["allowanceArray"])
