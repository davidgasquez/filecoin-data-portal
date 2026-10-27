-- asset.description = Gross settlements on admitted Filecoin Pay contracts since activation, with the ServiceOrchestrator binding covering each one.

-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = raw.solstice_deployments
-- asset.depends = model.foc_orchestrator_bindings

-- asset.column = contract | Filecoin Pay contract that emitted the settlement.
-- asset.column = block_number | Settlement epoch.
-- asset.column = transaction_index | Message position in the tipset.
-- asset.column = log_index | Settlement log index.
-- asset.column = rail_id | Rail identifier.
-- asset.column = payer | Rail payer, fixed at creation.
-- asset.column = operator | Rail operator, fixed at creation.
-- asset.column = token | Rail token (zero address for FIL).
-- asset.column = amount | Gross settled amount (RailSettled total, or one-time net + commission + fee), in token base units.
-- asset.column = orchestrator | ServiceOrchestrator whose binding span covers the settlement position; NULL if unbound.

-- asset.not_null = contract
-- asset.not_null = block_number
-- asset.not_null = log_index
-- asset.not_null = amount

with params as (
    select activation_epoch as a
    from raw.solstice_deployments
    where chain_id = 314
),
pay_contracts as (
    -- Every Pay contract ever admitted; quarter scope is applied downstream.
    select distinct lower(unnest(json_extract_string(args, '$.filecoinPayContracts[*]'))) as contract
    from raw.riba_eth_logs_decoded
    where contract_name = 'service_rewards_actor'
      and event_name = 'AdmittedListsUpdated'
),
rails as (
    -- Payer and operator are fixed at rail creation; rails are keyed per Pay contract.
    select
        lower(address) as contract,
        cast(json_extract_string(args, '$.railId') as hugeint) as rail_id,
        lower(json_extract_string(args, '$.payer')) as payer,
        lower(json_extract_string(args, '$.operator')) as operator,
        lower(json_extract_string(args, '$.token')) as token
    from raw.riba_eth_logs_decoded
    where event_name = 'RailCreated'
      and lower(address) in (select contract from pay_contracts)
),
settlements as (
    select
        lower(e.address) as contract,
        e.block_number,
        e.transaction_index,
        e.log_index,
        cast(json_extract_string(e.args, '$.railId') as hugeint) as rail_id,
        if(
            e.event_name = 'RailSettled',
            cast(json_extract_string(e.args, '$.totalSettledAmount') as hugeint),
            cast(json_extract_string(e.args, '$.netPayeeAmount') as hugeint)
            + cast(json_extract_string(e.args, '$.operatorCommission') as hugeint)
            + cast(json_extract_string(e.args, '$.networkFee') as hugeint)
        ) as amount
    from raw.riba_eth_logs_decoded as e
    cross join params as p
    where e.event_name in ('RailSettled', 'RailOneTimePaymentProcessed')
      and e.block_number >= p.a
      and lower(e.address) in (select contract from pay_contracts)
)
select
    s.contract,
    s.block_number,
    s.transaction_index,
    s.log_index,
    s.rail_id,
    r.payer,
    r.operator,
    r.token,
    s.amount,
    -- A settlement counts for the binding span covering its (block, log_index) position.
    b.orchestrator
from settlements as s
join rails as r
    on r.contract = s.contract and r.rail_id = s.rail_id
left join model.foc_orchestrator_bindings as b
    on b.payer = r.payer
    and b.operator = r.operator
    and (b.effective_from_block, b.effective_from_log_index) <= (s.block_number, s.log_index)
    and (
        b.effective_to_block is null
        or (s.block_number, s.log_index) < (b.effective_to_block, b.effective_to_log_index)
    )
order by s.block_number desc, s.log_index desc
