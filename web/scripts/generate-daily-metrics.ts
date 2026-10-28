import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"
import { DuckDBInstance } from "@duckdb/node-api"

type DatasetValue = boolean | number | string | null
type DatasetRow = Record<string, DatasetValue>

// One base for every dataset, so local exports and published parquets never mix.
const base = (process.env.FDP_DATA_URL ?? "https://data.filecoindataportal.xyz").replace(/\/$/, "")
const parquet = (name: string) => `read_parquet('${base}/${name}.parquet')`
const outputDir = path.resolve(process.cwd(), "src/data/generated")
const providerWindowDays = 30
const attoColumns = {
  service_quarters: ["bound_volume_atto_usd", "shares_total_atto_usd", "gate_threshold_atto_usd"],
  orchestrator_quarters: [
    "volume_atto_usd",
    "fil_pending_atto_fil",
    "reported_volume_atto_usd",
    "bound_volume_atto_usd",
  ],
}

// Pooled across providers: sum of numerators over sum of denominators, never averaged rates.
const pooled = (rate: string, numerator: string, denominator: string) => `
    sum(${numerator})::bigint AS provider_${numerator},
    sum(${denominator})::bigint AS provider_${denominator},
    sum(${numerator})::double / nullif(sum(${denominator}), 0) AS provider_${rate}`

const qualitySql = `
  SELECT
    date,${pooled("storage_success_rate", "storage_successes", "storage_checks")},${pooled("retrieval_success_rate", "retrieval_successes", "retrieval_checks")},${pooled("sampled_retrieval_success_rate", "sampled_retrieval_successes", "sampled_retrieval_checks")},
    sum(sampled_retrieval_skipped)::bigint AS provider_sampled_retrieval_skipped,${pooled("proving_fault_rate", "proving_periods_faulted", "proving_periods_closed")}
  FROM ${parquet("daily_provider_quality")}
  WHERE date < cast(timezone('UTC', now()) AS date)
  GROUP BY date
`

const dailySql = `
  WITH network AS (
    SELECT * FROM ${parquet("daily_network_metrics")}
    WHERE date IS NOT NULL AND date < cast(timezone('UTC', now()) AS date)
  ), quality AS (${qualitySql})
  SELECT
    date,
    transactions,
    onboarded_pibs,
    terminated_pibs,
    raw_power_pibs,
    quality_adjusted_power_pibs,
    gas_used_millions,
    total_value_fil,
    total_gas_fee_fil,
    base_fee_burn_fil,
    overestimation_burn_fil,
    miner_tip_fil,
    total_burn_fil,
    emission_burn_fil,
    non_emission_burn_usd,
    storage_provider_cron_burn_fil,
    unattributed_burn_fil,
    message_storage_provider_penalty_fil,
    circulating_fil,
    locked_fil,
    pledge_collateral_fil,
    locked_fil / nullif(circulating_fil, 0) AS locked_to_circulating_ratio,
    mining_yield,
    yearly_inflation_rate,
    minted_rewards_fil,
    miner_rewards_fil,
    miner_rewards_usd,
    service_rewards_fil,
    reward_per_wincount_fil,
    filecoin_pay_active_payers,
    filecoin_pay_active_rails,
    filecoin_pay_active_operators,
    filecoin_pay_paid_usd,
    warm_storage_billing_payers,
    warm_storage_billing_data_sets,
    warm_storage_stored_bytes,
    filecoin_pay_gross_payment_volume_run_rate_usd,
    filecoin_pay_gross_payment_volume_run_rate_usdfc_usd,
    filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd,
    filecoin_pay_network_fee_arr_usd,
    burn_coverage_ratio,
    0 AS high_profile_paying_clients,
    fil_token_price_avg_usd,
    fil_token_volume_usd,
    fil_token_market_cap_usd,
    defi_tvl_usd,
    glif_tvl_fil,
    glif_tvl_usd,
    ifil_base_apy,
    usdfc_supply,
    annual_pgf_deployments_usd,
    annual_non_emission_burn_usd,
    annual_distributed_rewards_usd,
    annual_coverage_days,
    quality.* EXCLUDE (date)
  FROM network
  FULL JOIN quality USING (date)
  ORDER BY date
`

// Check types come from different sources, so each window ends at that check's own last covered date.
const providerChecks = {
  storage: ["storage_successes", "storage_checks"],
  retrieval: ["retrieval_successes", "retrieval_checks"],
  sampled: ["sampled_retrieval_successes", "sampled_retrieval_checks", "sampled_retrieval_skipped"],
  proving: ["proving_periods_faulted", "proving_periods_closed"],
}
const providerCheckEnds = Object.entries(providerChecks)
  .map(([check, [, denominator]]) => `max(date) FILTER (WHERE ${denominator} IS NOT NULL) AS ${check}_end`)
  .join(",\n    ")
const providerCheckSums = Object.entries(providerChecks).flatMap(([check, columns]) => columns.map((column) =>
  `sum(${column}) FILTER (WHERE q.date > ends.${check}_end - INTERVAL ${providerWindowDays} DAY)::bigint AS ${column}`))
  .join(",\n    ")

const providersSql = `
  WITH quality AS (
    SELECT * FROM ${parquet("daily_provider_quality")}
    WHERE date < cast(timezone('UTC', now()) AS date)
  ), ends AS (
    SELECT
    ${providerCheckEnds}
    FROM quality
  )
  SELECT
    q.provider_id,
    any_value(p.name) AS name,
    ${providerCheckSums}
  FROM quality AS q
  LEFT JOIN ${parquet("providers")} AS p USING (provider_id)
  CROSS JOIN ends
  WHERE q.date > least(${Object.keys(providerChecks).map((check) => `ends.${check}_end`).join(", ")}) - INTERVAL ${providerWindowDays} DAY
  GROUP BY q.provider_id
  ORDER BY q.provider_id NULLS LAST
`

const providerWindowsSql = `
  SELECT ${providerCheckEnds}
  FROM ${parquet("daily_provider_quality")}
  WHERE date < cast(timezone('UTC', now()) AS date)
`

const quartersSql = `
  SELECT
    * REPLACE (
      ${attoColumns.service_quarters.map((column) => `${column}::varchar AS ${column}`).join(", ")},
      strftime(gate_checked_at, '%Y-%m-%dT%H:%M:%SZ') AS gate_checked_at,
      strftime(shares_submitted_at, '%Y-%m-%dT%H:%M:%SZ') AS shares_submitted_at
    )
  FROM ${parquet("service_quarters")}
  ORDER BY quarter DESC
`

const orchestratorQuartersSql = `
  SELECT
    quarter,
    orchestrator,
    volume_as_of_block,
    is_complete,
    is_removed_in_quarter,
    as_of_block,
    is_bound,
    corrections,
    ${attoColumns.orchestrator_quarters.map((column) => `${column}::varchar AS ${column}`).join(",\n    ")}
  FROM ${parquet("orchestrator_quarters")}
  ORDER BY quarter DESC, orchestrator
`

// JSON rows carry BIGINTs as strings; keep atto amounts as exact strings, parse the rest.
function normalize(column: string, value: unknown): DatasetValue {
  if (value == null) return null
  if (typeof value === "string" && /^-?\d+$/.test(value) && !column.includes("_atto_")) {
    const number = Number(value)
    if (!Number.isSafeInteger(number)) throw new Error(`${column} is outside the safe integer range: ${value}`)
    return number
  }
  if (typeof value === "boolean" || typeof value === "string") return value
  if (value instanceof Date) return value.toISOString()

  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error(`Invalid numeric value: ${value}`)
    return Number.isInteger(value) ? value : Math.round(value * 1_000_000) / 1_000_000
  }

  throw new Error(`Unsupported dataset value: ${String(value)}`)
}

const instance = await DuckDBInstance.create(":memory:")
const connection = await instance.connect()

async function query(sql: string): Promise<DatasetRow[]> {
  const result = await connection.run(sql)
  const rows = await result.getRowObjectsJson() as Record<string, unknown>[]
  return rows.map((row) => Object.fromEntries(
    Object.entries(row).map(([column, value]) => [column, normalize(column, value)]),
  ))
}

// Parquet stores HUGEINT as DOUBLE, which silently rounds atto amounts; main tables publish DECIMAL(38,0).
async function assertExact(table: keyof typeof attoColumns): Promise<void> {
  const types = await query(`DESCRIBE SELECT * FROM ${parquet(table)}`)
  for (const column of attoColumns[table]) {
    const type = String(types.find((row) => row.column_name === column)?.column_type)
    if (!/^(HUGEINT|BIGINT|VARCHAR|DECIMAL\(\d+,0\))$/.test(type)) {
      throw new Error(`${table}.${column} is ${type}; atto amounts need an exact integer type`)
    }
  }
}

try {
  await connection.run("SET TimeZone = 'UTC'")
  if (base.startsWith("http")) {
    await connection.run("INSTALL httpfs; LOAD httpfs;")
  }
  await assertExact("service_quarters")
  await assertExact("orchestrator_quarters")

  const daily = await query(dailySql)
  if (daily.length === 0) throw new Error("No rows returned from daily metrics dataset query")

  const snapshot = {
    source: base,
    generatedAt: new Date().toISOString(),
    providerWindowDays,
    providerWindowEnds: (await query(providerWindowsSql))[0],
    providers: await query(providersSql),
    quarters: await query(quartersSql),
    orchestratorQuarters: await query(orchestratorQuartersSql),
  }

  await mkdir(outputDir, { recursive: true })
  await writeFile(path.join(outputDir, "filecoin-daily-metrics.json"), JSON.stringify(daily))
  await writeFile(path.join(outputDir, "numbers-snapshot.json"), JSON.stringify(snapshot))
  console.log(
    `Generated ${daily.length.toLocaleString("en-US")} daily rows, ${snapshot.providers.length} providers, `
    + `${snapshot.quarters.length} quarters from ${base}`,
  )
} finally {
  connection.closeSync()
}
