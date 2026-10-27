-- asset.description = Daily Filecoin DeFi metrics. DefiLlama values use their snapshot date; RPC values are end-of-day state.

-- asset.depends = raw.defillama_filecoin_tvl
-- asset.depends = raw.defillama_filecoin_protocol_tvl
-- asset.depends = raw.defillama_ifil_yields
-- asset.depends = raw.defillama_usdfc_supply
-- asset.depends = raw.rpc_daily_defi_state

-- asset.column = date | UTC date.
-- asset.column = defi_tvl_usd | DefiLlama Filecoin DeFi TVL, excluding liquid staking and double counted TVL, in USD.
-- asset.column = defi_protocol_tvl_usd_json | DefiLlama Filecoin TVL by protocol slug, in USD, including liquid staking.
-- asset.column = glif_tvl_fil | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in FIL.
-- asset.column = glif_tvl_usd | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in USD.
-- asset.column = glif_pool_assets_fil | End-of-day GLIF Infinity Pool total assets, in FIL.
-- asset.column = glif_borrowed_fil | End-of-day FIL borrowed from the GLIF Infinity Pool.
-- asset.column = glif_available_liquidity_fil | End-of-day FIL borrowable from the GLIF Infinity Pool.
-- asset.column = glif_utilization | End-of-day GLIF borrowed FIL divided by pool total assets.
-- asset.column = ifil_base_apy | GLIF iFIL annualized base yield from DefiLlama, as a fraction.
-- asset.column = usdfc_supply | DefiLlama USDFC circulating supply, in tokens.
-- asset.column = usdc_axl_supply | End-of-day axlUSDC total supply on Filecoin, in tokens.

-- asset.not_null = date
-- asset.unique = date
-- asset.assert = glif_utilization between 0 and 1

with protocols as (
    select date, json_group_object(protocol, tvl_usd) as defi_protocol_tvl_usd_json
    from (
        select date, protocol, tvl_usd
        from raw.defillama_filecoin_protocol_tvl
        where tvl_usd is not null
        order by date, tvl_usd desc, protocol
    )
    group by 1
), glif as (
    select date, tvl_fil as glif_tvl_fil, tvl_usd as glif_tvl_usd
    from raw.defillama_filecoin_protocol_tvl
    where protocol = 'glif'
), dates as (
    select date from raw.defillama_filecoin_tvl
    union
    select date from raw.defillama_filecoin_protocol_tvl
    union
    select date from raw.defillama_ifil_yields
    union
    select date from raw.defillama_usdfc_supply
    union
    select date from raw.rpc_daily_defi_state
)
select
    dates.date,
    tvl.tvl_usd as defi_tvl_usd,
    protocols.defi_protocol_tvl_usd_json,
    glif.glif_tvl_fil,
    glif.glif_tvl_usd,
    state.glif_pool_total_assets_fil as glif_pool_assets_fil,
    state.glif_pool_total_borrowed_fil as glif_borrowed_fil,
    state.glif_pool_borrowable_fil as glif_available_liquidity_fil,
    state.glif_pool_total_borrowed_fil
        / nullif(state.glif_pool_total_assets_fil, 0) as glif_utilization,
    yields.base_apy as ifil_base_apy,
    usdfc.circulating_usdfc as usdfc_supply,
    state.usdc_axl_total_supply as usdc_axl_supply
from dates
left join raw.defillama_filecoin_tvl as tvl using (date)
left join protocols using (date)
left join glif using (date)
left join raw.rpc_daily_defi_state as state using (date)
left join raw.defillama_ifil_yields as yields using (date)
left join raw.defillama_usdfc_supply as usdfc using (date)
order by date desc
