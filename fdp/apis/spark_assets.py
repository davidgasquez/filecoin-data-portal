import datetime

import pandas as pd
import dagster as dg
from dagster_duckdb import DuckDBResource

from fdp.resources import HttpClientResource


@dg.asset(compute_kind="python")
def raw_spark_retrieval_success_rate(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
    httpx_filspark: HttpClientResource,
) -> dg.MaterializeResult:
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

        date_df = pd.DataFrame(httpx_filspark.get(url).json())
        date_df["date"] = day
        df = pd.concat([df, date_df], ignore_index=True)

    df.rename(columns={"miner_id": "provider_id"}, inplace=True)

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


# @dg.asset(compute_kind="python")
# def raw_spark_retrievals_onchain_data(
#     context: dg.AssetExecutionContext,
#     duckdb: DuckDBResource,
#     httpx_filspark: HttpClientResource,
# ) -> dg.MaterializeResult:
#     """
#     Spark retrievals onchain data.
#     """

#     first_day = datetime.date(2024, 4, 1)

#     with duckdb.get_connection() as con:
#         try:
#             latest_date = con.sql("""
#                 select max(date) as max_date
#                 from raw.raw_spark_retrieval_success_ratesss
#             """).fetchone()

#             start_date = latest_date[0] if latest_date else first_day

#         except Exception:
#             start_date = first_day

#     print(start_date)

#     # with duckdb.get_connection() as con:
#     #     con.sql(f"""
#     #         create table if not exists raw.{context.asset_key.to_user_string()} as
#     #         select * from df where 1=0;

#     #         insert into raw.{context.asset_key.to_user_string()}
#     #         select * from df;
#     #     """)

#     return dg.MaterializeResult()
