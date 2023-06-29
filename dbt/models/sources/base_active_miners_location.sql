with
    source as (select * from {{ source("state_market_deals", "active_miners") }}),
    renamed as (select * from source)
select *
from renamed
