import type { ChartConfig, DetailConfig, Period } from "./numbers"

export type NumbersMetric = ChartConfig & {
  id: string
  title: string
  description: string
  period: Period
  source?: string | null
  columns?: string[]
  details?: DetailConfig[]
}
type NumbersSection = { id: string; title: string; columns: 2 | 3 | 4; groups: { title?: string; charts: NumbersMetric[] }[] }

const quality = (
  id: string,
  title: string,
  description: string,
  rate: string,
  numerator: [string, string],
  denominator: [string, string],
  extra: DetailConfig[] = [],
): NumbersMetric => ({
  id,
  title,
  description,
  period: "pooled",
  source: "daily_provider_quality",
  columns: [numerator[0], denominator[0]],
  y: `provider_${rate}`,
  format: "percent",
  bounded: !rate.includes("fault"),
  details: [
    { title: numerator[1], description: `Sum of ${numerator[0]} across providers per day.`, y: `provider_${numerator[0]}`, format: "integer", kind: "bar" },
    { title: denominator[1], description: `Sum of ${denominator[0]} across providers per day.`, y: `provider_${denominator[0]}`, format: "integer", kind: "bar" },
    ...extra,
  ],
})

export const numbersSections: NumbersSection[] = [
  {
    id: "key-metrics",
    title: "Ecosystem KPIs",
    columns: 3,
    groups: [{
      charts: [
        {
          id: "filecoin-pay-gross-payment-volume-run-rate-usd",
          title: "Filecoin Pay GPV Run Rate",
          description: "Annualized gross stablecoin payment volume from active eligible recurring Filecoin Pay rails, including USDFC and USDC.axl, at day-end.",
          period: "runRate",
          y: "filecoin_pay_gross_payment_volume_run_rate_usd",
          format: "usd",
          series: [
            { label: "USDFC", y: "filecoin_pay_gross_payment_volume_run_rate_usdfc_usd" },
            { label: "USDC.axl", y: "filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd" },
          ],
        },
        {
          id: "burn-coverage-ratio",
          title: "Burn Coverage Ratio",
          description: "Trailing-365-day non-emission FIL burn divided by annual PGF deployments plus miner and service block rewards. Burn and rewards cover complete days only; PGF covers the full window.",
          period: "trailing",
          y: "burn_coverage_ratio",
          format: "percent",
          details: [
            { title: "Non-emission Burn", description: "FIL burned over complete days of the trailing 365 days, excluding emission burn, valued at average FIL/USD price.", y: "annual_non_emission_burn_usd", format: "usd" },
            { title: "PGF Deployments", description: "Public goods funding deployments disbursed over the trailing 365 days.", y: "annual_pgf_deployments_usd", format: "usd" },
            { title: "Distributed Rewards", description: "Miner and service block rewards over complete days of the trailing 365 days.", y: "annual_distributed_rewards_usd", format: "usd" },
            { title: "Complete Days", description: "Days in the trailing 365 days with known burn, rewards, and FIL price.", y: "annual_coverage_days", format: "integer" },
          ],
        },
        {
          id: "high-profile-paying-clients",
          title: "High-profile Paying Clients",
          description: "Count of recognized paying clients using Filecoin products.",
          source: null,
          columns: [],
          period: "eod",
          y: "high_profile_paying_clients",
          format: "number",
        },
      ],
    }],
  },
  {
    id: "filecoin-onchain-cloud",
    title: "Filecoin Onchain Cloud",
    columns: 3,
    groups: [
      {
        title: "Payments",
        charts: [
          { id: "foc-filecoin-pay-paid-usd", title: "Filecoin Pay Paid", description: "Gross stablecoin paid through Filecoin Pay rails per day, including USDFC and USDC.axl.", period: "day", y: "filecoin_pay_paid_usd", format: "usd", kind: "bar" },
          { id: "foc-filecoin-pay-network-fee-arr-usd", title: "Network Fee ARR", description: "Annualized Filecoin Pay network fee revenue from active eligible recurring stablecoin rails at day-end.", period: "runRate", y: "filecoin_pay_network_fee_arr_usd", format: "usd" },
          { id: "foc-active-rails", title: "Open Rails", description: "Unterminated Filecoin Pay rails at day-end, whether or not they are billing.", period: "eod", y: "filecoin_pay_active_rails", format: "integer", kind: "step" },
          { id: "foc-active-payers", title: "Payers with Open Rails", description: "Unique Filecoin Pay payer addresses with at least one unterminated rail at day-end, whether or not it is billing.", period: "eod", y: "filecoin_pay_active_payers", format: "integer", kind: "step" },
          { id: "foc-active-operators", title: "Operators with Open Rails", description: "Unique Filecoin Pay operator addresses with at least one unterminated rail at day-end.", period: "eod", y: "filecoin_pay_active_operators", format: "integer", kind: "step" },
        ],
      },
      {
        title: "Storage",
        charts: [
          { id: "foc-warm-storage-billing-payers", title: "Billing Payers", description: "Payers with at least one warm storage data set billing at a positive PDP rail rate at day-end.", period: "eod", y: "warm_storage_billing_payers", format: "integer", kind: "step" },
          { id: "foc-warm-storage-billing-data-sets", title: "Billing Data Sets", description: "Warm storage data sets billing at a positive PDP rail rate at day-end.", period: "eod", y: "warm_storage_billing_data_sets", format: "integer", kind: "step" },
          { id: "foc-warm-storage-data", title: "Warm Storage Data", description: "Raw piece data stored in Filecoin Warm Storage Service data sets at day-end, counting every stored copy, in TiB.", period: "eod", y: "warm_storage_stored_bytes", format: "number", scale: 2 ** 40, suffix: " TiB" },
        ],
      },
    ],
  },
  {
    id: "provider-quality",
    title: "Provider Quality",
    columns: 4,
    groups: [{
      charts: [
        quality(
          "provider-storage-success-rate",
          "Storage Probe Success",
          "Dealbot storage probes that created a deal over finished probes, pooled across providers. Synthetic probes, not client traffic. Days without probes are gaps.",
          "storage_success_rate",
          ["storage_successes", "Successes"],
          ["storage_checks", "Checks"],
        ),
        quality(
          "provider-retrieval-success-rate",
          "Dealbot Retrieval Success",
          "Successful IPFS retrievals of Dealbot's own deals over attempts, pooled across providers. Synthetic probes, not client traffic. Days without probes are gaps.",
          "retrieval_success_rate",
          ["retrieval_successes", "Successes"],
          ["retrieval_checks", "Checks"],
        ),
        quality(
          "provider-sampled-retrieval-success-rate",
          "Sampled Piece Retrieval Success",
          "Retrievals of sampled non-Dealbot pieces returning bytes matching the piece CID over attempts, pooled across providers. Skips (no candidate piece) are excluded and shown separately.",
          "sampled_retrieval_success_rate",
          ["sampled_retrieval_successes", "Successes"],
          ["sampled_retrieval_checks", "Attempts"],
          [{ title: "Skipped", description: "Sum of sampled_retrieval_skipped across providers per day. Not attempts.", y: "provider_sampled_retrieval_skipped", format: "integer", kind: "bar" }],
        ),
        quality(
          "provider-proving-fault-rate",
          "Proving Fault Rate",
          "Faulted proving periods over proving periods closed onchain on the date, pooled across providers. Missed periods count only once closed, so this is not current or overdue provider health.",
          "proving_fault_rate",
          ["proving_periods_faulted", "Faulted"],
          ["proving_periods_closed", "Closed"],
        ),
      ],
    }],
  },
  { id: "solstice", title: "Solstice", columns: 2, groups: [] },
  {
    id: "power",
    title: "Power",
    columns: 4,
    groups: [{
      charts: [
        { id: "sector-onboarding", title: "Onboarded Data", description: "Raw sector data onboarded to the network per day.", period: "day", y: "onboarded_pibs", format: "pib" },
        { id: "sector-termination", title: "Terminated Data", description: "Raw sector data terminated from the network per day.", period: "day", y: "terminated_pibs", format: "pib" },
        { id: "raw-power", title: "Raw Power", description: "End-of-day raw storage power committed to the network.", period: "eod", y: "raw_power_pibs", format: "pib" },
        { id: "quality-adjusted-power", title: "Quality Adjusted Power", description: "End-of-day quality-adjusted storage power committed to the network.", period: "eod", y: "quality_adjusted_power_pibs", format: "pib" },
      ],
    }],
  },
  {
    id: "activity",
    title: "Activity",
    columns: 3,
    groups: [{
      charts: [
        { id: "all-transactions", title: "Transactions", description: "On-chain transactions included per day.", period: "day", y: "transactions", format: "number", scale: 1_000_000, suffix: " M" },
        { id: "total-value-fil", title: "Value Transferred", description: "FIL transferred by top-level messages per day.", period: "day", y: "total_value_fil", format: "number", scale: 1_000_000, suffix: " M FIL" },
        { id: "total-gas-used", title: "Gas Used", description: "Gas consumed by on-chain messages per day.", period: "day", y: "gas_used_millions", format: "number", scale: 1_000_000, suffix: " T Gas" },
      ],
    }],
  },
  {
    id: "protocol",
    title: "Protocol",
    columns: 2,
    groups: [{
      charts: [
        { id: "fil-burned", title: "FIL Burned", description: "Total FIL burned per day, including gas, penalties, cron fees, contract burns, and emission burn.", period: "day", y: "total_burn_fil", format: "fil" },
        { id: "non-emission-burn-usd", title: "Non-emission Burn Value", description: "FIL burned per day excluding newly minted rewards burned by FIP-0118, valued at average FIL/USD price.", period: "day", y: "non_emission_burn_usd", format: "usd" },
        { id: "emission-burn", title: "Emission Burn", description: "Newly minted block rewards burned as the FIP-0118 residual per day.", period: "day", y: "emission_burn_fil", format: "fil" },
        { id: "storage-provider-cron-burn", title: "Storage Provider Cron Burn", description: "FIL burned during storage provider cron fees and penalties per day.", period: "day", y: "storage_provider_cron_burn_fil", format: "fil" },
        { id: "unattributed-burn", title: "Unattributed Burn", description: "Non-emission FIL burned outside gas, message penalties, and cron, such as contract burns and unclassified penalties.", period: "day", y: "unattributed_burn_fil", format: "fil" },
        { id: "locked-fil", title: "Locked FIL", description: "End-of-day FIL locked in the network.", period: "eod", y: "locked_fil", format: "mfil" },
        { id: "circulating-fil", title: "Circulating FIL", description: "End-of-day FIL circulating and tradeable in the economy.", period: "eod", y: "circulating_fil", format: "mfil" },
        { id: "yearly-inflation-rate", title: "Yearly Inflation Rate", description: "Year-over-year change in circulating FIL.", period: "yoy", y: "yearly_inflation_rate", format: "percent" },
        { id: "minted-rewards-fil", title: "Minted Block Rewards", description: "FIL block rewards minted per day across miner, service, and emission burn allocations.", period: "day", y: "minted_rewards_fil", format: "fil" },
        { id: "miner-rewards-fil", title: "Miner Block Rewards", description: "FIL block rewards allocated to block-winning storage providers per day.", period: "day", y: "miner_rewards_fil", format: "fil" },
        { id: "service-rewards-fil", title: "Service Rewards", description: "FIL block rewards accrued to the FIP-0118 service stream per day.", period: "day", y: "service_rewards_fil", format: "fil" },
        { id: "total-gas-fees", title: "Total Gas Fees", description: "FIL paid in gas fees per day.", period: "day", y: "total_gas_fee_fil", format: "fil" },
        { id: "base-fee-burn", title: "Base Fee Burn", description: "FIL burned by message base fees per day.", period: "day", y: "base_fee_burn_fil", format: "fil" },
        { id: "overestimation-burn", title: "Overestimation Burn", description: "FIL burned by gas overestimation per day.", period: "day", y: "overestimation_burn_fil", format: "fil" },
        { id: "miner-tips", title: "Miner Tips", description: "FIL paid to miners as message tips per day.", period: "day", y: "miner_tip_fil", format: "fil" },
        { id: "storage-provider-penalties", title: "Storage Provider Penalties", description: "FIL penalties incurred by storage providers during message execution per day.", period: "day", y: "message_storage_provider_penalty_fil", format: "fil" },
        { id: "pledge-collateral", title: "Pledge Collateral", description: "End-of-day FIL locked as storage provider pledge collateral.", period: "eod", y: "pledge_collateral_fil", format: "mfil" },
        { id: "locked-to-circulating-ratio", title: "Locked to Circulating Ratio", description: "Percentage of circulating FIL that is locked.", period: "eod", y: "locked_to_circulating_ratio", columns: ["locked_fil", "circulating_fil"], format: "percent" },
        { id: "miner-rewards-usd", title: "Miner Block Rewards Value", description: "Miner block rewards per day, valued at average FIL/USD price.", period: "day", y: "miner_rewards_usd", format: "usd" },
        { id: "mining-yield", title: "Mining Yield", description: "Annualized miner block rewards relative to locked FIL.", period: "annualized", y: "mining_yield", format: "percent" },
        { id: "reward-per-wincount", title: "Reward per Wincount", description: "Average miner block reward per winning proof per day.", period: "avg", y: "reward_per_wincount_fil", format: "fil" },
      ],
    }],
  },
  {
    id: "markets",
    title: "Markets",
    columns: 3,
    groups: [
      {
        charts: [
          { id: "fil-token-price", title: "FIL Token Price", description: "Average daily FIL token price in USD.", period: "avg", y: "fil_token_price_avg_usd", format: "usd" },
          { id: "fil-token-volume", title: "FIL Trading Volume", description: "Reported daily FIL trading volume in USD.", period: "day", y: "fil_token_volume_usd", format: "usd", scale: 1_000_000, suffix: "M" },
          { id: "fil-token-market-cap", title: "FIL Market Cap", description: "Daily FIL market capitalization in USD.", period: "snapshot", y: "fil_token_market_cap_usd", format: "usd", scale: 1_000_000_000, suffix: "B" },
        ],
      },
      {
        title: "DeFi",
        charts: [
          { id: "defi-tvl", title: "Filecoin DeFi TVL", description: "DefiLlama Filecoin chain TVL in USD, excluding liquid staking and double counted TVL. Dated by DefiLlama's snapshot.", period: "snapshot", y: "defi_tvl_usd", format: "usd", scale: 1_000_000, suffix: "M" },
          {
            id: "glif-tvl",
            title: "GLIF TVL",
            description: "DefiLlama GLIF TVL on Filecoin only, in FIL, including borrower collateral. Not comparable to or summed with chain DeFi TVL. Dated by DefiLlama's snapshot.",
            period: "snapshot",
            y: "glif_tvl_fil",
            format: "mfil",
            details: [{ title: "GLIF TVL (USD)", description: "Same DefiLlama snapshot valued in USD.", y: "glif_tvl_usd", format: "usd" }],
          },
          { id: "ifil-base-apy", title: "iFIL Base APY", description: "GLIF iFIL annualized base yield from DefiLlama, latest observation on the date.", period: "annualized", y: "ifil_base_apy", format: "percent" },
          { id: "usdfc-supply", title: "USDFC Supply", description: "DefiLlama USDFC circulating supply, in tokens (not USD value). Dated by DefiLlama's snapshot.", period: "snapshot", y: "usdfc_supply", format: "number", suffix: " USDFC" },
        ],
      },
    ],
  },
]
