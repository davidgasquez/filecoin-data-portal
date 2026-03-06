import { DuckDBInstance } from "@duckdb/node-api"

const DAILY_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/filecoin_daily_metrics.parquet"

type DatasetValue = boolean | number | string | null
type DatasetRow = Record<string, DatasetValue>

const SQL = `
  SELECT
    * REPLACE (
      coalesce(onboarded_data_pibs_with_payments, 0) AS onboarded_data_pibs_with_payments
    ),
    coalesce(total_value_fil, 0) + coalesce(total_gas_used_millions, 0) AS total_value_flow_fil
  FROM read_parquet('${DAILY_METRICS_PARQUET_URL}')
  WHERE date IS NOT NULL
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
