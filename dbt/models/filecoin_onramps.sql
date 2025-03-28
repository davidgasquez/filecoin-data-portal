with onramp_mappings as (
    select * from (
        values
            ('Storacha', 'f02759235'),
            ('Storacha', 'f03123037'),
            ('Lighthouse', 'f01945035'),
            ('Lighthouse', 'f03200311'),
            ('CID Gravity', 'f02824311'),
            ('Haluo', 'f03143604'),
            ('Triton One', 'f02144497'),
            ('Triton One', 'f03087718'),
            ('Ghostdrive', 'f02844684')
    ) as t (onramp_name, client_id)
),

client_data as (
    select
        *
    from {{ ref('filecoin_clients') }}
    where client_id in (select client_id from onramp_mappings)
)

select
    m.onramp_name,
    count(distinct c.client_id) as total_known_clients,
    array_agg(distinct c.client_id) as known_client_ids,
    sum(c.total_deals) as total_deals,
    sum(c.total_verified_deals) as total_verified_deals,
    sum(c.total_active_deals) as total_active_deals,
    sum(c.total_active_verified_deals) as total_active_verified_deals,
    sum(c.total_data_uploaded_tibs) as total_data_uploaded_tibs,
    sum(c.total_active_data_uploaded_tibs) as total_active_data_uploaded_tibs,
    min(c.first_deal_at) as first_deal_at,
    min(c.first_active_deal_at) as first_active_deal_at,
    max(c.last_deal_at) as last_deal_at,
    max(c.last_active_deal_at) as last_active_deal_at,
    sum(c.data_uploaded_tibs_30d) as data_uploaded_tibs_30d,
    sum(c.data_uploaded_tibs_6m) as data_uploaded_tibs_6m,
    sum(c.data_uploaded_tibs_1y) as data_uploaded_tibs_1y,
    sum(c.data_expired_tibs_30d) as data_expired_tibs_30d,
    sum(c.data_expired_tibs_6m) as data_expired_tibs_6m,
    sum(c.data_expired_tibs_1y) as data_expired_tibs_1y,
from client_data as c
inner join onramp_mappings as m
    on c.client_id = m.client_id
group by 1
order by 1
