-- asset.description = Daily Filecoin DeFi metrics from DefiLlama, dated by their snapshot date.

-- asset.depends = raw.defillama_filecoin_tvl
-- asset.depends = raw.defillama_filecoin_protocol_tvl
-- asset.depends = raw.defillama_ifil_yields
-- asset.depends = raw.defillama_usdfc_supply

-- asset.column = date | UTC date.
-- asset.column = defi_tvl_usd | DefiLlama Filecoin DeFi TVL, excluding liquid staking and double counted TVL, in USD.
-- asset.column = defi_protocol_tvl_usd_json | DefiLlama Filecoin TVL by protocol slug, in USD, including liquid staking.
-- asset.column = glif_tvl_fil | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in FIL.
-- asset.column = glif_tvl_usd | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in USD.
-- asset.column = ifil_base_apy | GLIF iFIL annualized base yield from DefiLlama, as a fraction.
-- asset.column = usdfc_supply | DefiLlama USDFC circulating supply, in tokens.

-- asset.not_null = date
-- asset.unique = date

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
)
select
    dates.date,
    tvl.tvl_usd as defi_tvl_usd,
    protocols.defi_protocol_tvl_usd_json,
    glif.glif_tvl_fil,
    glif.glif_tvl_usd,
    yields.base_apy as ifil_base_apy,
    usdfc.circulating_usdfc as usdfc_supply
from dates
left join raw.defillama_filecoin_tvl as tvl using (date)
left join protocols using (date)
left join glif using (date)
left join raw.defillama_ifil_yields as yields using (date)
left join raw.defillama_usdfc_supply as usdfc using (date)
order by date desc
