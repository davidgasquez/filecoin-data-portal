import pandas as pd
from dagster import Output, MetadataValue, asset


@asset(compute_kind="python")
def raw_storage_providers_location_provider_quest() -> Output[pd.DataFrame]:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).
    """
    url = "https://geoip.feeds.provider.quest/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])
    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


# @asset(compute_kind="python")
# def raw_deal_tags(duckdb: DuckDBResource) -> MaterializeResult:
#     """
#     Deal tags from CID checker.
#     """

#     STATEMARKETDEALS_POSTGRES_HOST = os.getenv("STATEMARKETDEALS_POSTGRES_HOST")
#     STATEMARKETDEALS_POSTGRES_PORT = os.getenv("STATEMARKETDEALS_POSTGRES_PORT")
#     STATEMARKETDEALS_POSTGRES_DATABASE = os.getenv("STATEMARKETDEALS_POSTGRES_DATABASE")
#     STATEMARKETDEALS_POSTGRES_USERNAME = os.getenv("STATEMARKETDEALS_POSTGRES_USERNAME")
#     STATEMARKETDEALS_POSTGRES_PASSWORD = os.getenv("STATEMARKETDEALS_POSTGRES_PASSWORD")

#     with duckdb.get_connection() as con:
#         con.execute(
#             f"""
#             INSTALL postgres_scanner;
#             LOAD postgres_scanner;
#             CALL postgres_attach('dbname={STATEMARKETDEALS_POSTGRES_DATABASE} user={STATEMARKETDEALS_POSTGRES_USERNAME} password={STATEMARKETDEALS_POSTGRES_PASSWORD} host={STATEMARKETDEALS_POSTGRES_HOST} port={STATEMARKETDEALS_POSTGRES_PORT}');
#             create or replace table raw_deal_tags as (select * from deal_tags);
#             """
#         )

#     return MaterializeResult(
#         metadata={"Sample": MetadataValue.md("select * from raw_deal_tags limit 5;")},
#     )


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
