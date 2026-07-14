import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"
import { DuckDBInstance } from "@duckdb/node-api"

type DatasetValue = boolean | number | string | null
type DatasetRow = Record<string, DatasetValue>

const source = process.env.DAILY_NETWORK_METRICS_PARQUET_URL
  ?? "https://data.filecoindataportal.xyz/daily_network_metrics.parquet"
const output = path.resolve(process.cwd(), "src/data/generated/filecoin-daily-metrics.json")

const sql = `
  SELECT
    date,
    transactions,
    onboarded_pibs,
    terminated_pibs,
    raw_power_pibs,
    quality_adjusted_power_pibs,
    gas_used_millions,
    total_value_fil,
    total_value_flow_fil,
    total_gas_fee_fil,
    base_fee_burn_fil,
    base_fee_burn_usd,
    overestimation_burn_fil,
    overestimation_burn_usd,
    message_burn_fil,
    message_burn_usd,
    miner_tip_fil,
    miner_tip_usd,
    protocol_revenue_fil,
    protocol_revenue_usd,
    message_storage_provider_penalty_fil,
    message_storage_provider_penalty_usd,
    circulating_fil,
    locked_fil,
    burnt_fil,
    pledge_collateral_fil,
    locked_fil / nullif(circulating_fil, 0) AS locked_to_circulating_ratio,
    mining_yield,
    yearly_inflation_rate,
    block_rewards_fil,
    block_rewards_usd,
    reward_per_wincount_fil,
    coalesce(filecoin_pay_active_payers, 0) AS filecoin_pay_active_payers,
    coalesce(filecoin_pay_active_rails, 0) AS filecoin_pay_active_rails,
    coalesce(filecoin_pay_paid_usd, 0) AS filecoin_pay_paid_usd,
    coalesce(filecoin_pay_gross_payment_volume_run_rate_usd, 0) AS filecoin_pay_gross_payment_volume_run_rate_usd,
    coalesce(filecoin_pay_gross_payment_volume_run_rate_usdfc_usd, 0) AS filecoin_pay_gross_payment_volume_run_rate_usdfc_usd,
    coalesce(filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd, 0) AS filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd,
    coalesce(filecoin_pay_network_fee_arr_usd, 0) AS filecoin_pay_network_fee_arr_usd,
    revenue_coverage_ratio,
    0 AS high_profile_paying_clients,
    fil_token_price_avg_usd,
    fil_token_volume_usd,
    fil_token_market_cap_usd,
    annual_pgf_deployments_usd,
    annual_protocol_revenue_usd,
    annual_block_rewards_usd
  FROM read_parquet('${source}')
  WHERE date IS NOT NULL AND date <= current_date - INTERVAL 2 DAY
  ORDER BY date
`

function normalize(value: unknown): DatasetValue {
  if (value == null) return null

  if (typeof value === "boolean" || typeof value === "string") {
    return value
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error(`Invalid numeric value: ${value}`)
    return Number.isInteger(value) ? value : Math.round(value * 1_000_000) / 1_000_000
  }

  if (typeof value === "bigint") {
    const number = Number(value)
    if (!Number.isSafeInteger(number)) {
      throw new Error(`BigInt value is outside the safe integer range: ${value}`)
    }
    return number
  }

  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) throw new Error(`Invalid date value: ${value}`)
    const iso = value.toISOString()
    return iso.endsWith("T00:00:00.000Z") ? iso.slice(0, 10) : iso
  }

  throw new Error(`Unsupported dataset value: ${String(value)}`)
}

const instance = await DuckDBInstance.create(":memory:")
const connection = await instance.connect()
let rawRows: Record<string, unknown>[]

try {
  const result = await connection.run(sql)
  rawRows = await result.getRowObjectsJson() as Record<string, unknown>[]
} finally {
  connection.closeSync()
}

if (rawRows.length === 0) {
  throw new Error("No rows returned from daily metrics dataset query")
}

const rows: DatasetRow[] = rawRows.map((row) => Object.fromEntries(
  Object.entries(row).map(([column, value]) => [column, normalize(value)]),
))

await mkdir(path.dirname(output), { recursive: true })
await writeFile(output, JSON.stringify(rows))
console.log(`Generated ${rows.length.toLocaleString("en-US")} daily metric rows`)
