-- asset.description = Daily bound orchestrator gross payments in token base units.

-- asset.depends = model.foc_orchestrator_settlements

-- asset.not_null = date
-- asset.not_null = orchestrator
-- asset.not_null = payer
-- asset.not_null = token
-- asset.not_null = amount

with settlements as (
    select cast(timezone('UTC', to_timestamp(1598306400 + block_number * 30)) as date) as date,
        orchestrator, payer, token, cast(amount as decimal(38, 0)) as amount
    from model.foc_orchestrator_settlements
    where orchestrator is not null
)
select date, orchestrator, payer, token, cast(sum(amount) as decimal(38, 0)) as amount
from settlements
where date < cast(timezone('UTC', current_timestamp) as date)
group by 1, 2, 3, 4
order by date desc, orchestrator, token, payer
