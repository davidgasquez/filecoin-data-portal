-- asset.description = Daily Filecoin network economics snapshots from Lily chain economics.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = circulating_fil | End-of-day VM circulating supply, in FIL.
-- asset.column = mined_fil | End-of-day cumulative mined FIL, in FIL.
-- asset.column = vested_fil | End-of-day cumulative vested FIL, in FIL.
-- asset.column = locked_fil | End-of-day VM locked FIL, in FIL.
-- asset.column = burnt_fil | End-of-day cumulative burnt FIL, in FIL.
-- asset.column = pledge_collateral_fil | End-of-day total pledge collateral locked by storage providers, in FIL.

-- asset.not_null = date
-- asset.not_null = circulating_fil
-- asset.not_null = mined_fil
-- asset.not_null = vested_fil
-- asset.not_null = locked_fil
-- asset.not_null = burnt_fil
-- asset.not_null = pledge_collateral_fil
-- asset.unique = date

with daily_economics as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        height,
        1 as version,
        cast(
            cast(circulating_fil as bignumeric) / 1000000000000000000 as float64
        ) as circulating_fil,
        cast(cast(mined_fil as bignumeric) / 1000000000000000000 as float64)
            as mined_fil,
        cast(cast(vested_fil as bignumeric) / 1000000000000000000 as float64)
            as vested_fil,
        cast(cast(locked_fil as bignumeric) / 1000000000000000000 as float64)
            as locked_fil,
        cast(cast(burnt_fil as bignumeric) / 1000000000000000000 as float64)
            as burnt_fil
    from `chain_economics`

    union all

    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        height,
        2 as version,
        cast(
            cast(circulating_fil_v2 as bignumeric) / 1000000000000000000
                as float64
        ) as circulating_fil,
        cast(cast(mined_fil as bignumeric) / 1000000000000000000 as float64)
            as mined_fil,
        cast(cast(vested_fil as bignumeric) / 1000000000000000000 as float64)
            as vested_fil,
        cast(cast(locked_fil_v2 as bignumeric) / 1000000000000000000 as float64)
            as locked_fil,
        cast(cast(burnt_fil as bignumeric) / 1000000000000000000 as float64)
            as burnt_fil
    from `chain_economics_v2`
), daily_economics_snapshots as (
    select * except (height, version)
    from daily_economics
    qualify row_number() over (
        partition by date
        order by version desc, height desc
    ) = 1
), daily_pledge_collateral as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        cast(
            cast(total_pledge_collateral as bignumeric) / 1000000000000000000
                as float64
        ) as pledge_collateral_fil
    from `chain_powers`
    qualify row_number() over (
        partition by date(timestamp_seconds((height * 30) + 1598306400))
        order by height desc
    ) = 1
)
select
    daily_economics_snapshots.date,
    daily_economics_snapshots.circulating_fil,
    daily_economics_snapshots.mined_fil,
    daily_economics_snapshots.vested_fil,
    daily_economics_snapshots.locked_fil,
    daily_economics_snapshots.burnt_fil,
    daily_pledge_collateral.pledge_collateral_fil
from daily_economics_snapshots
join daily_pledge_collateral
    using (date)
order by 1 desc
