import pandas as pd
import requests
from dagster import Output, MetadataValue, asset

from fdp.resources import DuneResource


@asset(compute_kind="python")
def raw_storage_providers_location_provider_quest() -> Output[pd.DataFrame]:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).
    """
    url = "https://geoip.feeds.provider.quest/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])
    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_storage_providers_reputation() -> Output[pd.DataFrame]:
    """
    Storage Provider reputation data from Filrep (https://filrep.io).
    """

    url = "https://api.filrep.io/api/v1/miners"

    storage_providers = pd.DataFrame(requests.get(url).json()["miners"])
    storage_providers["name"] = storage_providers["tag"].apply(lambda x: x.get("name"))
    storage_providers = storage_providers.convert_dtypes()

    return Output(
        storage_providers.drop(columns=["id"]),
        metadata={
            "Sample": MetadataValue.md(storage_providers.sample(5).to_markdown())
        },
    )


# @asset(compute_kind="python")
# def raw_filecoin_state_market_deals_snapshot(context) -> None:
#     """
#     State Market Deals snapshot from Gliff S3 JSON.
#     """
#     urllib.request.urlretrieve(
#         "https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst",
#         "/tmp/StateMarketDeals.json.zst",
#     )

#     context.log.info("Downloaded StateMarketDeals.json.zst")

#     dctx = zstandard.ZstdDecompressor()
#     input_path = "/tmp/StateMarketDeals.json.zst"
#     output_path = "/tmp/ParsedStateMarketDeals.json"

#     # jq --stream -c 'fromstream(1|truncate_stream(inputs))' /tmp/StateMarketDeals.json.zst > /tmp/ParsedStateMarketDeals.json
#     with open(input_path, "rb") as ifh, open(output_path, "wb") as ofh:
#         reader = dctx.stream_reader(ifh)
#         for k, v in ijson.kvitems(reader, ""):
#             v["DealID"] = k
#             ofh.write(json.dumps(v).encode("utf-8") + b"\n")

#     context.log.info("Decompressed and parsed StateMarketDeals.json.zst")

#     # Remove the input file
#     os.remove("/tmp/StateMarketDeals.json.zst")

#     # Compress the parsed file
#     os.system(
#         "zstd --rm -q -f -T0 /tmp/ParsedStateMarketDeals.json -o /tmp/ParsedStateMarketDeals.json.zst"
#     )


@asset(compute_kind="API")
def dune_metrics(dune: DuneResource, filecoin_daily_metrics: pd.DataFrame) -> None:
    """
    Uploads allo deployments to Dune.
    """
    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
