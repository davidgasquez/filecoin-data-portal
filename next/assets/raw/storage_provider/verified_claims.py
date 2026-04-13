# ruff: noqa: E501
# asset.description = Daily verified claim metrics by Filecoin storage provider, derived from verified registry ClaimAllocations execution traces in Lily BigQuery.
# asset.materialization = custom
# asset.column = date | UTC day when verified data was successfully claimed/onboarded.
# asset.column = provider_id | Filecoin storage provider miner actor id address.
# asset.column = verified_data_onboarded_tibs | Sum of verified piece sizes claimed by the provider on the day, in tebibytes.
# asset.column = verified_claims | Number of successful verified registry claims by the provider on the day.
# asset.column = unique_verified_clients | Distinct verified clients with at least one successful claim with the provider on the day.
# asset.not_null = date
# asset.not_null = provider_id
# asset.not_null = verified_data_onboarded_tibs
# asset.not_null = verified_claims
# asset.not_null = unique_verified_clients
# asset.assert = verified_data_onboarded_tibs >= 0
# asset.assert = verified_claims >= 0
# asset.assert = unique_verified_clients >= 0

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.storage_provider_verified_claims"
SCHEMA = "raw"
QUERY = """
with verified_registry_claims as (
    select
        date(timestamp_seconds((v.height * 30) + 1598306400)) as date,
        v.`from` as provider_id,
        concat('f0', json_extract_scalar(claim, '$.Client')) as client_id,
        cast(json_extract_scalar(claim, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    cross join unnest(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) as claim
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(claim, '$.Client') is not null

    union all

    select
        date(timestamp_seconds((v.height * 30) + 1598306400)) as date,
        v.`from` as provider_id,
        concat('f0', json_extract_scalar(sector, '$.Client')) as client_id,
        cast(json_extract_scalar(sector, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(sector, '$.Client') is not null
      and array_length(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) = 0
)
select
    date,
    provider_id,
    cast(sum(piece_size_bytes) as float64) / pow(1024, 4) as verified_data_onboarded_tibs,
    count(*) as verified_claims,
    count(distinct client_id) as unique_verified_clients
from verified_registry_claims
group by 1, 2
order by 1, 2
""".strip()


def verified_claims() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
