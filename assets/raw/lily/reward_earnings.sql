-- asset.description = Reward stream earnings per tipset height and recipient.
-- asset.resource = bigquery.lily

-- asset.column = height | Executed tipset height.
-- asset.column = stream_id | Reward stream ID.
-- asset.column = recipient | Recipient actor ID address.
-- asset.column = recipient_address | Recipient delegated (f410) address, if any.
-- asset.column = earned_atto | Earned amount summed across the tipset's blocks, in attoFIL (decimal string).

-- asset.not_null = height
-- asset.not_null = stream_id
-- asset.not_null = recipient
-- asset.not_null = earned_atto
-- asset.assert = regexp_full_match(earned_atto, '[0-9]+')

with distributions as (
    -- Heights with duplicate distributions are ambiguous (as in block rewards).
    select height, distribution
    from `chain_reward_distributions`
    where height >= 6470280
      and height < div(unix_seconds(timestamp(current_date())) - 1598306400, 30)
    qualify count(*) over (partition by height) = 1
), earnings as (
    select
        height,
        cast(json_value(stream, '$.ID') as int64) as stream_id,
        json_value(recipient, '$.Recipient') as recipient,
        sum(cast(json_value(recipient, '$.EarnedAmount') as bignumeric)) as earned_atto
    from distributions,
        unnest(json_query_array(distribution, '$.Blocks')) as block,
        unnest(json_query_array(block, '$.Streams')) as stream,
        unnest(json_query_array(stream, '$.Distribution.Recipients')) as recipient
    group by 1, 2, 3
), delegated as (
    select id, if(count(distinct address) = 1, any_value(address), null) as address
    from `id_addresses`
    where starts_with(address, 'f410f')
    group by 1
)
select
    e.height,
    e.stream_id,
    e.recipient,
    d.address as recipient_address,
    cast(e.earned_atto as string) as earned_atto
from earnings as e
left join delegated as d
    on d.id = e.recipient
order by e.height desc, e.stream_id, e.recipient
