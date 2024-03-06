import datetime

import pandas as pd
from dagster import AssetExecutionContext, Output, MetadataValue, asset
from dagster_duckdb import DuckDBResource
from duckdb import CatalogException

from .resources import SpacescopeResource, StarboardDatabricksResource


@asset(compute_kind="python")
def raw_datacapstats_verified_clients() -> Output[pd.DataFrame]:
    """
    Verified Clients information from Datacapstats API.
    """
    url = "https://api.datacapstats.io/api/getVerifiedClients"

    data = pd.read_json(url, typ="series")["data"]
    df = pd.json_normalize(data)
    df["allowanceArray"] = df["allowanceArray"]

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_storage_providers_location_provider_quest() -> Output[pd.DataFrame]:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).
    """
    url = "https://geoip.feeds.provider.quest/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])
    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="API")
def raw_storage_provider_daily_power(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> None:
    """
    Storage Providers daily power from Spacescope API.
    """

    FILECOIN_FIRST_DAY = datetime.date(2020, 10, 15)

    with duckdb.get_connection() as conn:
        try:
            from_day = (
                conn.execute(
                    "select max(stat_date) as max_date from main.raw_storage_provider_daily_power"
                )
                .df()["max_date"]
                .values[0]
            )
            if from_day:
                from_day = pd.to_datetime(from_day).date()
        except CatalogException:
            from_day = FILECOIN_FIRST_DAY
            conn.execute(
                """
                create table main.raw_storage_provider_daily_power(
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    raw_byte_power BIGINT,
                    quality_adj_power BIGINT
                );
                """
            )

        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=2)

        if from_day >= to_day:
            context.log.info(
                f"Storage provider power data is up to date. Last update was on {from_day}"
            )
            return

        context.log.info(
            f"Fetching storage provider power data from {from_day} to {to_day}"
        )

        df_power_data = pd.DataFrame()

        for day in pd.date_range(FILECOIN_FIRST_DAY, to_day, freq="d"):
            power_data = spacescope_api.get_storage_provider_power(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df_power_data = pd.concat(
                [df_power_data, pd.DataFrame(power_data)], ignore_index=True
            )

        conn.execute(
            """
            insert into main.raw_storage_provider_daily_power
            select * from df_power_data
            """
        )

        context.log.info(
            f"Persisted {df_power_data.shape[0]} rows of storage provider power data"
        )


# @asset(compute_kind="python")
# def raw_filecoin_state_market_deals(context) -> None:
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


@asset(compute_kind="python")
def raw_filecoin_state_market_deals(
    context: AssetExecutionContext,
    starboard_databricks: StarboardDatabricksResource,
    duckdb: DuckDBResource,
) -> None:
    """
    State Market Deals derived from Lily's market_deal_proposals and market_deal_states tables.
    """
    databricks_con = starboard_databricks.get_connection()
    duckdb.get_connection()

    cursor = databricks_con.cursor()
    batch_size = 5000000

    r = cursor.execute(
        """
        with market_deals as (
            select
                *
            from lily.market_deal_proposals
            qualify row_number() over (partition by deal_id order by height desc) = 1
        ),

        market_chain_activity as (
            select
                *
            from lily.market_deal_states
            qualify row_number() over (partition by deal_id order by height desc) = 1
        )

        select
            d.height,
            d.deal_id,
            d.state_root,
            d.piece_cid,
            d.padded_piece_size,
            d.unpadded_piece_size,
            d.is_verified,
            d.client_id,
            d.provider_id,
            d.start_epoch,
            d.end_epoch,
            d.slashed_epoch,
            d.storage_price_per_epoch,
            d.provider_collateral,
            d.client_collateral,
            d.label,
            a.sector_start_epoch,
            a.slash_epoch
        from market_deals as d
        left join market_chain_activity as a on d.deal_id = a.deal_id
        order by d.provider_id desc, d.client_id desc, d.height desc
    """
    )

    context.log.info("Fetched market deals and chain activity")

    with duckdb.get_connection() as duckdb_con:
        data = r.fetchmany_arrow(batch_size)
        duckdb_con.execute(
            """
            create or replace table raw_filecoin_state_market_deals as (
                select * from data
            )
            """
        )

        context.log.info(f"Persisted {data.num_rows} rows")

        while data.num_rows > 0:
            data = r.fetchmany_arrow(batch_size)
            duckdb_con.sql(
                """
                insert into raw_filecoin_state_market_deals
                select
                    *
                from data
                """
            )

            context.log.info(f"Persisted {data.num_rows} rows")
