with token_map as (
  select *
  from (
    values
      ('0x80B98d3aa09ffff255c3ba4A241111Ff1262F045', 'USDFC', 'USD Filecoin', 18)
  ) as t(token, symbol, name, decimals)
)

select
  token,
  symbol,
  name,
  decimals
from token_map
order by token
