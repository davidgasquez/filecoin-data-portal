with expected as (
    select cast(timezone('UTC', to_timestamp(1598306400 + block_number * 30)) as date) as date,
        orchestrator, payer, token, cast(sum(amount) as decimal(38, 0)) as amount
    from model.foc_orchestrator_settlements
    where orchestrator is not null
    group by 1, 2, 3, 4
),
differences as (
    (select * from expected where date < cast(timezone('UTC', current_timestamp) as date)
     except all select * from model.foc_daily_orchestrator_payments)
    union all
    (select * from model.foc_daily_orchestrator_payments
     except all select * from expected where date < cast(timezone('UTC', current_timestamp) as date))
)
select * from differences
