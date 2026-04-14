import { DuckDBInstance } from "@duckdb/node-api"

const DAILY_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/filecoin_daily_metrics.parquet"
const BETA_FILECOIN_DAILY_CORE_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/beta_filecoin_daily_core_metrics.parquet"

type DatasetValue = boolean | number | string | null
type DatasetRow = Record<string, DatasetValue>

const SQL = `
  WITH core_metrics AS (
    SELECT
      date,
      total_arr_usdfc
    FROM read_parquet('${BETA_FILECOIN_DAILY_CORE_METRICS_PARQUET_URL}')
    WHERE date IS NOT NULL
  ),
  daily_metrics AS (
    SELECT
      dm.date,
      dm.sector_onboarding_raw_power_pibs,
      dm.clients_with_active_data_gt_1_tibs,
      dm.deal_storage_cost_fil,
      dm.total_value_fil,
      dm.total_gas_used_millions,
      dm.sector_terminated_raw_power_pibs,
      dm.raw_power_pibs,
      dm.quality_adjusted_power_pibs,
      dm.verified_data_power_pibs,
      dm.providers_with_power,
      dm.network_utilization_ratio,
      dm.active_sector_count,
      dm.active_address_count_daily,
      dm.transactions,
      dm.unit_base_fee,
      dm.data_on_active_deals_pibs,
      dm.clients_with_active_deals,
      dm.providers_with_active_deals,
      dm.unique_deal_making_clients,
      dm.unique_deal_making_providers,
      coalesce(dm.onboarded_data_pibs_with_payments, 0) AS onboarded_data_pibs_with_payments,
      dm.ddo_sector_onboarding_raw_power_tibs,
      dm.circulating_fil,
      dm.mined_fil,
      dm.vested_fil,
      dm.locked_fil,
      dm.storage_providers_collateral,
      dm.burnt_fil,
      dm.miner_tip_fil,
      dm.reward_per_wincount,
      dm.yearly_inflation_rate,
      dm.fil_token_price_avg_usd,
      dm.fil_token_volume_usd,
      dm.fil_token_market_cap_usd,
      dm.fil_plus_bytes_share,
      dm.fil_plus_rewards_share,
      coalesce(cm.total_arr_usdfc, 0) AS total_arr_usdfc
    FROM read_parquet('${DAILY_METRICS_PARQUET_URL}') AS dm
    LEFT JOIN core_metrics AS cm ON dm.date = cm.date
    WHERE dm.date IS NOT NULL
  )
  SELECT
    date,
    sector_onboarding_raw_power_pibs,
    clients_with_active_data_gt_1_tibs,
    deal_storage_cost_fil,
    total_arr_usdfc,
    total_value_fil,
    total_gas_used_millions,
    sector_terminated_raw_power_pibs,
    raw_power_pibs,
    quality_adjusted_power_pibs,
    verified_data_power_pibs,
    providers_with_power,
    network_utilization_ratio,
    active_sector_count,
    active_address_count_daily,
    transactions,
    unit_base_fee,
    data_on_active_deals_pibs,
    clients_with_active_deals,
    providers_with_active_deals,
    unique_deal_making_clients,
    unique_deal_making_providers,
    onboarded_data_pibs_with_payments,
    ddo_sector_onboarding_raw_power_tibs,
    circulating_fil,
    mined_fil,
    vested_fil,
    locked_fil,
    storage_providers_collateral,
    burnt_fil,
    miner_tip_fil,
    reward_per_wincount,
    yearly_inflation_rate,
    fil_token_price_avg_usd,
    fil_token_volume_usd,
    fil_token_market_cap_usd,
    fil_plus_bytes_share,
    fil_plus_rewards_share,
    coalesce(total_value_fil, 0) + coalesce(total_gas_used_millions, 0) AS total_value_flow_fil,
    coalesce(locked_fil / nullif(circulating_fil, 0), 0) AS locked_to_circulating_ratio,
    coalesce(
      ((mined_fil - lag(mined_fil) OVER (ORDER BY date)) / nullif(locked_fil, 0)) * 365,
      0
    ) AS mining_yield
  FROM daily_metrics
  ORDER BY date
`

function normalizeNumber(value: number): number {
  if (!Number.isFinite(value)) {
    throw new Error(`Invalid numeric value: ${value}`)
  }

  if (Number.isInteger(value)) {
    return value
  }

  return Math.round(value * 1_000_000) / 1_000_000
}

function normalizeDate(value: Date): string {
  if (Number.isNaN(value.getTime())) {
    throw new Error(`Invalid date value: ${value}`)
  }

  const isoValue = value.toISOString()
  return isoValue.endsWith("T00:00:00.000Z") ? isoValue.slice(0, 10) : isoValue
}

function normalizeValue(value: unknown): DatasetValue {
  if (value == null) {
    return null
  }

  if (typeof value === "boolean" || typeof value === "string") {
    return value
  }

  if (typeof value === "number") {
    return normalizeNumber(value)
  }

  if (typeof value === "bigint") {
    const numberValue = Number(value)

    if (!Number.isSafeInteger(numberValue)) {
      throw new Error(`BigInt value is outside the safe integer range: ${value}`)
    }

    return numberValue
  }

  if (value instanceof Date) {
    return normalizeDate(value)
  }

  throw new Error(`Unsupported dataset value type: ${String(value)}`)
}

function normalizeRow(row: Record<string, unknown>): DatasetRow {
  return Object.fromEntries(
    Object.entries(row).map(([column, value]) => [column, normalizeValue(value)]),
  )
}

export default async function generateFilecoinDailyMetricsDataset(): Promise<DatasetRow[]> {
  const instance = await DuckDBInstance.create(":memory:")
  const connection = await instance.connect()
  const result = await connection.run(SQL)
  const rawRows = (await result.getRowObjectsJson()) as Array<Record<string, unknown>>

  if (rawRows.length === 0) {
    throw new Error("No rows returned from daily metrics dataset query")
  }

  connection.closeSync()

  return rawRows.map(normalizeRow)
}
