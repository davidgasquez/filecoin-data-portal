-- asset.description = Daily service stream rewards earned and claimed per ServiceOrchestrator and payout wallet.

-- asset.depends = raw.lily_reward_earnings
-- asset.depends = raw.lily_reward_claims
-- asset.depends = raw.riba_eth_logs_decoded

-- asset.column = date | UTC date of the executed tipset.
-- asset.column = orchestrator | ServiceOrchestrator identity address; NULL when the wallet's owner is unknown or ambiguous.
-- asset.column = wallet | Payout wallet (0x address, or actor address when it has none).
-- asset.column = earned_atto_fil | Rewards earned, in attoFIL.
-- asset.column = claimed_atto_fil | Rewards paid out by Claim, in attoFIL.

-- asset.not_null = date
-- asset.not_null = wallet
-- asset.not_null = earned_atto_fil
-- asset.not_null = claimed_atto_fil
-- asset.assert = earned_atto_fil >= 0
-- asset.assert = claimed_atto_fil >= 0

with sra as (
    select
        event_name,
        lower(coalesce(args ->> '$.orch', args ->> '$.oldOrch')) as orchestrator,
        lower(coalesce(args ->> '$.wallet', args ->> '$.newWallet')) as wallet,
        block_number,
        log_index
    from raw.riba_eth_logs_decoded
    where contract_name = 'service_rewards_actor'
      and event_name in ('OrchestratorAdmitted', 'OrchestratorWalletReplaced', 'OrchestratorRemoved')
),
spans as (
    -- Historical wallet spans, inclusive at both ends: awards in the event's
    -- tipset may land on either side of it, so same-height overlaps stay ambiguous.
    select orchestrator, wallet, from_block, to_block
    from (
        select
            *,
            block_number as from_block,
            lead(block_number) over (
                partition by orchestrator order by block_number, log_index
            ) as to_block
        from sra
    )
    where event_name != 'OrchestratorRemoved'
),
facts as (
    -- Service stream (ID 2).
    select
        height,
        recipient as recipient_id,
        recipient,
        recipient_address,
        earned_atto::hugeint as earned_atto,
        null::hugeint as claimed_atto
    from raw.lily_reward_earnings
    where stream_id = 2
    union all
    select
        height,
        recipient_id,
        recipient,
        recipient_address,
        null,
        claimed_atto::hugeint
    from raw.lily_reward_claims
    where stream_id = 2
),
wallets as (
    select
        *,
        coalesce(
            '0x' || lower(hex(unbin(left(list_aggregate(list_transform(
                split(substr(recipient_address, 6), ''),
                lambda c: lpad(bin(strpos('abcdefghijklmnopqrstuvwxyz234567', c) - 1), 5, '0')
            ), 'string_agg', ''), 160)))),
            recipient_id,
            recipient
        ) as wallet,
        -- SRA wallets may also be ID-masked 0xff... addresses.
        '0xff' || lpad(lower(hex(substr(recipient_id, 3)::ubigint)), 38, '0') as masked_wallet
    from facts
),
earned as (
    select
        w.height,
        w.recipient_id,
        w.wallet,
        w.earned_atto,
        if(count(distinct s.orchestrator) = 1, any_value(s.orchestrator), null) as orchestrator
    from wallets as w
    left join spans as s
        on s.wallet in (w.wallet, w.masked_wallet)
        and w.height >= s.from_block
        and (s.to_block is null or w.height <= s.to_block)
    where w.earned_atto is not null
    group by 1, 2, 3, 4
),
claimed as (
    -- A Claim drains the wallet: attribute it only when one orchestrator
    -- earned everything the wallet ever earned up to the Claim (reuse is NULL).
    select
        c.height,
        c.wallet,
        c.claimed_atto,
        if(
            count(distinct e.orchestrator) = 1 and bool_and(e.orchestrator is not null),
            any_value(e.orchestrator),
            null
        ) as orchestrator
    from (
        select *, row_number() over () as claim_row from wallets where claimed_atto is not null
    ) as c
    left join earned as e
        on e.recipient_id = c.recipient_id
        and e.height <= c.height
    group by c.claim_row, c.height, c.wallet, c.claimed_atto
)
select
    timezone('UTC', to_timestamp(height * 30 + 1598306400))::date as date,
    orchestrator,
    wallet,
    coalesce(sum(earned_atto), 0)::hugeint as earned_atto_fil,
    coalesce(sum(claimed_atto), 0)::hugeint as claimed_atto_fil
from (
    select height, orchestrator, wallet, earned_atto, null::hugeint as claimed_atto from earned
    union all
    select height, orchestrator, wallet, null, claimed_atto from claimed
)
group by all
order by date desc, orchestrator, wallet
