import { DuckDBInstance } from "@duckdb/node-api"

const DAILY_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/filecoin_daily_metrics.parquet"

const METRIC_COLUMNS = [
  "sector_onboarding_raw_power_pibs",
  "clients_with_active_data_gt_1_tibs",
  "deal_storage_cost_fil",
  "total_value_flow_fil",
  "raw_power_pibs",
  "quality_adjusted_power_pibs",
  "verified_data_power_pibs",
  "providers_with_power",
  "network_utilization_ratio",
  "active_sector_count",
  "data_on_active_deals_pibs",
  "clients_with_active_deals",
  "providers_with_active_deals",
  "unique_deal_making_clients",
  "unique_deal_making_providers",
  "onboarded_data_tibs_with_payments",
  "ddo_sector_onboarding_raw_power_tibs",
] as const

type MetricColumn = (typeof METRIC_COLUMNS)[number]

type RawRow = {
  date: string | Date
} & Record<MetricColumn, number | string>

type CompactDailyMetricsDataset = {
  s: string
  c: MetricColumn[]
  r: Array<[number, ...number[]]>
}

const SQL = `
  SELECT
    date,
    sector_onboarding_raw_power_pibs,
    clients_with_active_data_gt_1_tibs,
    deal_storage_cost_fil,
    total_value_fil + total_gas_used_millions AS total_value_flow_fil,
    raw_power_pibs,
    quality_adjusted_power_pibs,
    verified_data_power_pibs,
    providers_with_power,
    network_utilization_ratio * 100 AS network_utilization_ratio,
    active_sector_count,
    data_on_active_deals_pibs,
    clients_with_active_deals,
    providers_with_active_deals,
    unique_deal_making_clients,
    unique_deal_making_providers,
    coalesce(onboarded_data_pibs_with_payments, 0) * 1024 AS onboarded_data_tibs_with_payments,
    ddo_sector_onboarding_raw_power_tibs
  FROM read_parquet('${DAILY_METRICS_PARQUET_URL}')
  WHERE date IS NOT NULL
  ORDER BY date
`

function toNumber(value: number | string): number {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    throw new Error(`Invalid numeric value: ${value}`)
  }

  return Math.round(parsedValue * 1_000_000) / 1_000_000
}

function toIsoDate(value: string | Date): string {
  const date = value instanceof Date ? value : new Date(value)

  if (Number.isNaN(date.getTime())) {
    throw new Error(`Invalid date value: ${value}`)
  }

  return date.toISOString().slice(0, 10)
}

function toDayOffset(startDate: string, currentDate: string): number {
  const startTimestamp = new Date(`${startDate}T00:00:00Z`).getTime()
  const currentTimestamp = new Date(`${currentDate}T00:00:00Z`).getTime()

  return Math.round((currentTimestamp - startTimestamp) / 86_400_000)
}

export default async function generateFilecoinDailyMetricsDataset(): Promise<CompactDailyMetricsDataset> {
  const instance = await DuckDBInstance.create(":memory:")
  const connection = await instance.connect()
  const result = await connection.run(SQL)

  const rawRows = (await result.getRowObjectsJson()) as RawRow[]

  if (rawRows.length === 0) {
    throw new Error("No rows returned from daily metrics dataset query")
  }

  const rows = rawRows.map((row) => ({
    date: toIsoDate(row.date),
    values: METRIC_COLUMNS.map((column) => toNumber(row[column])),
  }))

  const startDate = rows[0].date

  const compactDataset: CompactDailyMetricsDataset = {
    s: startDate,
    c: [...METRIC_COLUMNS],
    r: rows.map((row) => [toDayOffset(startDate, row.date), ...row.values]),
  }

  connection.closeSync()
  return compactDataset
}
