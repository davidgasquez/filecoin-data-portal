# ruff: noqa: E501
# asset.description = Historically active Filecoin storage providers enriched with current miner info, current power, market deal activity, and verified claim activity.
# asset.materialization = dataframe

# asset.depends = raw.storage_provider_sector_lifecycle
# asset.depends = raw.storage_provider_verified_claims

# asset.column = provider_id | Filecoin storage provider miner actor id address.
# asset.column = owner_id | Current owner id address from the latest Lily miner info snapshot, if available.
# asset.column = worker_id | Current worker id address from the latest Lily miner info snapshot, if available.
# asset.column = peer_id | Current libp2p peer id from the latest Lily miner info snapshot, if available.
# asset.column = control_addresses | Current JSON array of control addresses from the latest Lily miner info snapshot, if available.
# asset.column = multi_addresses | Current JSON array of multiaddrs from the latest Lily miner info snapshot, if available.
# asset.column = sector_size | Current sector size in bytes from the latest Lily miner info snapshot, if available.
# asset.column = current_raw_power_pibs | Latest observed raw byte power for the provider, in pebibytes, if currently positive.
# asset.column = current_quality_adj_power_pibs | Latest observed quality adjusted power for the provider, in pebibytes, if currently positive.
# asset.column = has_current_power | Whether the provider currently has positive raw or quality adjusted power.
# asset.column = has_sector_activity | Whether the provider has at least one sector lifecycle event in the provider daily sector lifecycle table.
# asset.column = has_market_deals | Whether the provider appears in Lily market deal proposals.
# asset.column = has_verified_claims | Whether the provider has at least one successful verified claim.
# asset.column = first_sector_activity_date | First day with sector lifecycle activity for the provider, if available.
# asset.column = last_sector_activity_date | Most recent day with sector lifecycle activity for the provider, if available.
# asset.column = first_market_deal_start_date | First observed storage deal start date for the provider, if available.
# asset.column = last_market_deal_start_date | Most recent storage deal start date for the provider, if available.
# asset.column = first_verified_claim_date | First day with a successful verified claim for the provider, if available.
# asset.column = last_verified_claim_date | Most recent day with a successful verified claim for the provider, if available.
# asset.column = total_verified_claims | Total successful verified claims observed for the provider.
# asset.column = total_verified_data_onboarded_tibs | Total verified data successfully claimed by the provider, in tebibytes.
# asset.not_null = provider_id
# asset.not_null = has_current_power
# asset.not_null = has_sector_activity
# asset.not_null = has_market_deals
# asset.not_null = has_verified_claims
# asset.unique = provider_id

import polars as pl

from fdp.api import db_connection
from fdp.bigquery import query_arrow

LATEST_MINER_INFO_QUERY = """
select
    miner_id as provider_id,
    owner_id,
    worker_id,
    nullif(peer_id, '') as peer_id,
    nullif(control_addresses, '[]') as control_addresses,
    nullif(multi_addresses, '[]') as multi_addresses,
    cast(sector_size as int64) as sector_size
from `lily-data.lily.miner_infos`
where cast(sector_size as int64) > 0
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
order by provider_id
""".strip()

LATEST_POWER_QUERY = """
select
    miner_id as provider_id,
    cast(raw_byte_power as float64) / pow(1024, 5) as current_raw_power_pibs,
    cast(quality_adj_power as float64) / pow(1024, 5) as current_quality_adj_power_pibs,
    true as has_current_power
from `lily-data.lily.power_actor_claims`
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
and (
    cast(raw_byte_power as int64) > 0
    or cast(quality_adj_power as int64) > 0
)
order by provider_id
""".strip()

MARKET_DEAL_ACTIVITY_QUERY = """
select
    provider_id,
    min(date(timestamp_seconds((start_epoch * 30) + 1598306400))) as first_market_deal_start_date,
    max(date(timestamp_seconds((start_epoch * 30) + 1598306400))) as last_market_deal_start_date
from `lily-data.lily.market_deal_proposals`
group by 1
order by provider_id
""".strip()


def filecoin_storage_providers() -> pl.DataFrame:
    latest_miner_info = pl.DataFrame(query_arrow(LATEST_MINER_INFO_QUERY))
    latest_power = pl.DataFrame(query_arrow(LATEST_POWER_QUERY))
    market_deal_activity = pl.DataFrame(query_arrow(MARKET_DEAL_ACTIVITY_QUERY))

    with db_connection() as conn:
        conn.register("latest_miner_info", latest_miner_info)
        conn.register("latest_power", latest_power)
        conn.register("market_deal_activity", market_deal_activity)
        result = conn.execute(
            """
            with sector_activity as (
                select
                    provider_id,
                    min(date) as first_sector_activity_date,
                    max(date) as last_sector_activity_date,
                    true as has_sector_activity
                from raw.storage_provider_sector_lifecycle
                group by 1
            ),
            verified_claim_activity as (
                select
                    provider_id,
                    min(date) as first_verified_claim_date,
                    max(date) as last_verified_claim_date,
                    sum(verified_claims) as total_verified_claims,
                    sum(verified_data_onboarded_tibs) as total_verified_data_onboarded_tibs,
                    true as has_verified_claims
                from raw.storage_provider_verified_claims
                group by 1
            ),
            providers as (
                select provider_id from sector_activity
                union
                select provider_id from market_deal_activity
                union
                select provider_id from verified_claim_activity
                union
                select provider_id from latest_power
            )
            select
                p.provider_id,
                i.owner_id,
                i.worker_id,
                i.peer_id,
                i.control_addresses,
                i.multi_addresses,
                i.sector_size,
                pow.current_raw_power_pibs,
                pow.current_quality_adj_power_pibs,
                coalesce(pow.has_current_power, false) as has_current_power,
                coalesce(sa.has_sector_activity, false) as has_sector_activity,
                md.provider_id is not null as has_market_deals,
                coalesce(vc.has_verified_claims, false) as has_verified_claims,
                sa.first_sector_activity_date,
                sa.last_sector_activity_date,
                md.first_market_deal_start_date,
                md.last_market_deal_start_date,
                vc.first_verified_claim_date,
                vc.last_verified_claim_date,
                vc.total_verified_claims,
                vc.total_verified_data_onboarded_tibs
            from providers as p
            left join latest_miner_info as i using (provider_id)
            left join latest_power as pow using (provider_id)
            left join sector_activity as sa using (provider_id)
            left join market_deal_activity as md using (provider_id)
            left join verified_claim_activity as vc using (provider_id)
            order by p.provider_id
            """
        ).fetch_arrow_table()

    return pl.DataFrame(result)
