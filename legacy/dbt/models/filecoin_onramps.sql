with onramp_mappings as (
    select * from {{ source('raw_assets', 'raw_onramp_mappings') }}
),

all_client_data as (
    select
        *
    from {{ ref('filecoin_clients') }}
),

mapped_clients as (
    select
        m.onramp_name,
        c.*
    from all_client_data as c
    inner join onramp_mappings as m
        on c.client_id = m.client_id
),

unmapped_clients as (
    select
        'No Onramp' as onramp_name,
        c.*
    from all_client_data as c
    where c.client_id not in (select client_id from onramp_mappings)
),

combined_clients as (
    select * from mapped_clients
    union all
    select * from unmapped_clients
)

select
    onramp_name,
    count(distinct client_id) as total_known_clients,
    case
        when onramp_name = 'No Onramp' then null
        else array_agg(distinct client_id)
    end as known_client_ids,
    sum(total_deals) as total_deals,
    sum(total_verified_deals) as total_verified_deals,
    sum(total_active_deals) as total_active_deals,
    sum(total_active_verified_deals) as total_active_verified_deals,
    sum(total_data_uploaded_tibs) as total_data_uploaded_tibs,
    sum(total_active_data_uploaded_tibs) as total_active_data_uploaded_tibs,
    min(first_deal_at) as first_deal_at,
    min(first_active_deal_at) as first_active_deal_at,
    max(last_deal_at) as last_deal_at,
    max(last_active_deal_at) as last_active_deal_at,
    sum(data_uploaded_tibs_30d) as data_uploaded_tibs_30d,
    sum(data_uploaded_tibs_6m) as data_uploaded_tibs_6m,
    sum(data_uploaded_tibs_1y) as data_uploaded_tibs_1y,
    sum(data_expired_tibs_30d) as data_expired_tibs_30d,
    sum(data_expired_tibs_6m) as data_expired_tibs_6m,
    sum(data_expired_tibs_1y) as data_expired_tibs_1y
from combined_clients
group by 1
order by 1
