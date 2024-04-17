import datetime

import pandas as pd
import requests
from dagster import Output, MetadataValue, AssetExecutionContext, asset

from ..resources import MongoDBResource


@asset(compute_kind="python")
def raw_storage_providers_filrep_reputation() -> Output[pd.DataFrame]:
    """
    Storage Provider reputation data from Filrep (https://filrep.io).
    """

    url = "https://api.filrep.io/api/v1/miners"

    storage_providers = pd.DataFrame(requests.get(url).json()["miners"])
    storage_providers["name"] = storage_providers["tag"].apply(lambda x: x.get("name"))
    storage_providers = storage_providers.convert_dtypes()

    return Output(
        storage_providers.drop(
            columns=[
                "id",
                "price",
                "verifiedPrice",
                "minPieceSize",
                "maxPieceSize",
                "rawPower",
                "qualityAdjPower",
                "creditScore",
            ]
        ),
        metadata={
            "Sample": MetadataValue.md(storage_providers.sample(5).to_markdown())
        },
    )


@asset(compute_kind="python")
def raw_retrieval_bot_measures(reputation_db: MongoDBResource) -> Output[pd.DataFrame]:
    """
    Retrieval bot measures.
    """

    collection_names = [
        "retrievalbot_1",
        "retrievalbot_2",
        "retrievalbot_3",
        "retrievalbot_4",
        "retrievalbot_5",
        "retrievalbot_6",
        "glif_retrieval_bot",
    ]

    df = pd.DataFrame()

    for name in collection_names:
        c = reputation_db.get_collection("reputation", name)

        collection_df = pd.DataFrame.from_records(c.find())

        df = pd.concat([df, collection_df], ignore_index=True)

    df.drop(columns=["_id"], inplace=True)

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_spark_retrieval_success_rate(
    context: AssetExecutionContext,
) -> Output[pd.DataFrame]:
    """
    Spark retrieval success rate.
    """
    first_day = datetime.date(2024, 4, 1)
    today = datetime.date.today()

    df = pd.DataFrame()

    for day in pd.date_range(first_day, today, freq="d"):
        context.log.info(f"Fetching retrieval success rate data for {day}")
        date = day.strftime("%Y-%m-%d")
        url = "https://stats.filspark.com/miners/retrieval-success-rate/summary"
        url = f"{url}?from={date}&to={date}"

        date_df = pd.DataFrame(requests.get(url).json())
        date_df["date"] = day
        df = pd.concat([df, date_df], ignore_index=True)

    df.rename(columns={"miner_id": "provider_id"}, inplace=True)

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})
