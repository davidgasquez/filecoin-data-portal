select
    date,
    method,
    gas_used_millions,
    transactions,
    gas_used_millions / transactions as average_gas_used_millions
from {{ source("raw_assets", "raw_filecoin_transactions") }}
where date > '2021-12-31'
