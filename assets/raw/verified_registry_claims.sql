-- asset.description = Successful verified registry claims extracted from
-- parseable ClaimAllocations messages in Lily BigQuery.

-- asset.resource = bigquery.lily

-- asset.column = claim_epoch | Chain epoch when the verified claim was
-- executed.
-- asset.column = provider_id | Storage provider actor ID as an integer.
-- asset.column = sector_number | Sector number containing the claimed verified
-- data.
-- asset.column = sector_expiry | Sector expiration epoch recorded on the claim
-- message.
-- asset.column = client_id | Verified client actor ID as an integer.
-- asset.column = allocation_id | Verified allocation ID claimed by the
-- provider.
-- asset.column = piece_size_bytes | Verified piece size claimed in bytes.

-- asset.not_null = claim_epoch
-- asset.not_null = provider_id
-- asset.not_null = sector_number
-- asset.not_null = sector_expiry
-- asset.not_null = client_id
-- asset.not_null = allocation_id
-- asset.not_null = piece_size_bytes

with claim_messages as (
    select
        v.height as claim_epoch,
        cast(substr(v.`from`, 3) as int64) as provider_id,
        json_extract_array(v.params, '$.Sectors') as sectors
    from `vm_messages` as v
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and starts_with(v.`from`, 'f0')
),
claims_nested as (
    select
        claim_epoch,
        provider_id,
        cast(json_extract_scalar(sector, '$.Sector') as int64) as sector_number,
        cast(
            json_extract_scalar(sector, '$.SectorExpiry') as int64
        ) as sector_expiry,
        cast(json_extract_scalar(claim, '$.Client') as int64) as client_id,
        cast(
            json_extract_scalar(claim, '$.AllocationId') as int64
        ) as allocation_id,
        cast(json_extract_scalar(claim, '$.Size') as int64) as piece_size_bytes
    from claim_messages
    cross join unnest(coalesce(sectors, array<string>[])) as sector
    cross join unnest(
        coalesce(json_extract_array(sector, '$.Claims'), array<string>[])
    ) as claim
    where json_extract_scalar(sector, '$.Sector') is not null
      and json_extract_scalar(sector, '$.SectorExpiry') is not null
      and json_extract_scalar(claim, '$.Client') is not null
      and json_extract_scalar(claim, '$.AllocationId') is not null
      and json_extract_scalar(claim, '$.Size') is not null
),
claims_flat as (
    select
        claim_epoch,
        provider_id,
        cast(json_extract_scalar(sector, '$.Sector') as int64) as sector_number,
        cast(
            json_extract_scalar(sector, '$.SectorExpiry') as int64
        ) as sector_expiry,
        cast(json_extract_scalar(sector, '$.Client') as int64) as client_id,
        cast(
            json_extract_scalar(sector, '$.AllocationId') as int64
        ) as allocation_id,
        cast(json_extract_scalar(sector, '$.Size') as int64) as piece_size_bytes
    from claim_messages
    cross join unnest(coalesce(sectors, array<string>[])) as sector
    where json_extract_scalar(sector, '$.Sector') is not null
      and json_extract_scalar(sector, '$.SectorExpiry') is not null
      and json_extract_scalar(sector, '$.Client') is not null
      and json_extract_scalar(sector, '$.AllocationId') is not null
      and json_extract_scalar(sector, '$.Size') is not null
      and array_length(
          coalesce(json_extract_array(sector, '$.Claims'), array<string>[])
      ) = 0
)
select
    claim_epoch,
    provider_id,
    sector_number,
    sector_expiry,
    client_id,
    allocation_id,
    piece_size_bytes
from claims_nested

union all

select
    claim_epoch,
    provider_id,
    sector_number,
    sector_expiry,
    client_id,
    allocation_id,
    piece_size_bytes
from claims_flat
