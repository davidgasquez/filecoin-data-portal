import dagster as dg
from dagster_duckdb import DuckDBResource

from fdp.dune.resources import DuneResource


@dg.asset(compute_kind="API", deps=["filecoin_daily_metrics"])
def dune_metrics(dune: DuneResource, duckdb: DuckDBResource) -> None:
    """
    Uploads filecoin daily metrics to Dune.
    """

    with duckdb.get_connection() as conn:
        filecoin_daily_metrics = conn.execute("""
            select
                date,
                onboarded_data_pibs,
                unique_data_onboarded_data_pibs,
                unique_data_onboarded_ratio,
                data_on_active_deals_pibs,
                unique_data_on_active_deals_pibs,
                deals,
                unique_deal_making_clients,
                unique_deal_making_providers,
                active_deals,
                clients_with_active_deals,
                providers_with_active_deals,
                raw_power_pibs,
                quality_adjusted_power_pibs,
                verified_data_power_pibs,
                network_utilization_ratio,
                new_client_ids,
                new_provider_ids,
                ended_data_pibs,
                new_client_ids,
                new_provider_ids,
                new_piece_cids,
                mean_spark_retrieval_success_rate,
                providers_with_successful_retrieval,
            from filecoin_daily_metrics
            where date > '2021-01-01'
        """).df()

    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
