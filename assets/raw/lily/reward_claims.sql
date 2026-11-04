-- asset.description = Successful native reward Claim payouts per message and wallet.
-- asset.resource = bigquery.lily

-- asset.column = height | Message execution height.
-- asset.column = cid | Claim message CID.
-- asset.column = wallet_index | Wallet position in the Claim batch.
-- asset.column = stream_id | Reward stream ID.
-- asset.column = recipient | Wallet address as given in the Claim params.
-- asset.column = recipient_id | Wallet actor ID address, if resolvable.
-- asset.column = recipient_address | Wallet delegated (f410) address, if any.
-- asset.column = claimed_atto | Paid amount from the receipt, in attoFIL (decimal string).

-- asset.not_null = height
-- asset.not_null = cid
-- asset.not_null = wallet_index
-- asset.not_null = stream_id
-- asset.not_null = recipient
-- asset.not_null = claimed_atto
-- asset.assert = regexp_full_match(claimed_atto, '[0-9]+')

with claims as (
    -- f02 is the reward actor; receipts are recorded at the child tipset height.
    select m.height, m.cid, m.params, r.parsed_return
    from `parsed_messages` as m
    left join `receipts` as r
        on r.message = m.cid
        and r.height >= 6470280
    where m.height >= 6470280
      and m.height < div(unix_seconds(timestamp(current_date())) - 1598306400, 30)
      -- Messages in the latest loaded tipset may not have their receipt yet.
      and m.height < (select max(height) from `receipts` where height >= 6470280)
      and m.`to` = 'f02'
      and m.method = 'ClaimExported'
      -- Missing receipts are kept so the not-null checks fail.
      and coalesce(r.exit_code, 0) = 0
), payouts as (
    -- Zip wallets and amounts by position; missing or mismatched arrays yield nulls.
    select
        height,
        cid,
        wallet_index,
        cast(json_value(params, '$.ID') as int64) as stream_id,
        json_value_array(params, '$.Wallets')[safe_offset(wallet_index)] as recipient,
        cast(cast(json_value(
            json_query_array(parsed_return, '$.Amounts')[safe_offset(wallet_index)], '$.Int'
        ) as bignumeric) as string) as claimed_atto
    from claims,
        unnest(generate_array(0, greatest(
            coalesce(array_length(json_value_array(params, '$.Wallets')), 1),
            coalesce(array_length(json_query_array(parsed_return, '$.Amounts')), 1)
        ) - 1)) as wallet_index
), aliases as (
    select distinct id, address from `id_addresses`
), ids as (
    select address, if(count(*) = 1, any_value(id), null) as id
    from aliases
    group by 1
), delegated as (
    select id, if(count(*) = 1, any_value(address), null) as address
    from aliases
    where starts_with(address, 'f410f')
    group by 1
)
select
    c.height,
    c.cid,
    c.wallet_index,
    c.stream_id,
    c.recipient,
    if(starts_with(c.recipient, 'f0'), c.recipient, i.id) as recipient_id,
    d.address as recipient_address,
    c.claimed_atto
from payouts as c
left join ids as i
    on i.address = c.recipient
left join delegated as d
    on d.id = if(starts_with(c.recipient, 'f0'), c.recipient, i.id)
order by c.height desc, c.cid, c.wallet_index
