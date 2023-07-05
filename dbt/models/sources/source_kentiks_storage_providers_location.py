from pymongo import MongoClient
import os
import pandas as pd

REPUTATION_MONGODB_URI = os.getenv("REPUTATION_MONGODB_URI")
data_dir = os.getenv("DATA_DIR", "data")


def model(dbt, session):
    client = MongoClient(REPUTATION_MONGODB_URI)
    reputation_db = client.get_database("reputation")

    df = pd.DataFrame.from_records(reputation_db["kentiks"].find())

    df.to_csv(f"{data_dir}/source_kentiks_storage_providers_location.csv", index=False)

    return df
