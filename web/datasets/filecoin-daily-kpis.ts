import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"

import { DuckDBInstance } from "@duckdb/node-api"

type RawRow = {
  date: string | Date
  sector_onboarding_raw_power_pibs: number | string
  clients_with_active_data_gt_1_tibs: number | string
  deal_storage_cost_fil: number | string
  total_value_flow_fil: number | string
}

type CompactKpiDataset = {
  s: string
  r: Array<[number, number, number, number, number]>
}

const DAILY_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/filecoin_daily_metrics.parquet"

const OUTPUT_PATH = path.resolve(
  process.cwd(),
  "src/data/generated/filecoin-daily-kpis.json",
)

const SQL = `
  SELECT
    date,
    sector_onboarding_raw_power_pibs,
    clients_with_active_data_gt_1_tibs,
    deal_storage_cost_fil,
    total_value_fil + total_gas_used_millions AS total_value_flow_fil
  FROM read_parquet('${DAILY_METRICS_PARQUET_URL}')
  WHERE date IS NOT NULL
  ORDER BY date
`

function toNumber(value: number | string): number {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    throw new Error(`Invalid numeric value: ${value}`)
  }

  return parsedValue
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

export default async function generateFilecoinDailyKpisDataset(): Promise<void> {
  const instance = await DuckDBInstance.create(":memory:")
  const connection = await instance.connect()
  const result = await connection.run(SQL)

  const rawRows = (await result.getRowObjectsJson()) as RawRow[]

  if (rawRows.length === 0) {
    throw new Error("No rows returned from KPI dataset query")
  }

  const rows = rawRows.map((row) => ({
    date: toIsoDate(row.date),
    sectorOnboardingMicroPibs: Math.round(
      toNumber(row.sector_onboarding_raw_power_pibs) * 1_000_000,
    ),
    clientsWithActiveDataGt1Tibs: Math.round(
      toNumber(row.clients_with_active_data_gt_1_tibs),
    ),
    dealStorageCostNanoFil: Math.round(toNumber(row.deal_storage_cost_fil) * 1_000_000_000),
    totalValueFlowMilliFil: Math.round(toNumber(row.total_value_flow_fil) * 1_000),
  }))

  const startDate = rows[0].date

  const compactDataset: CompactKpiDataset = {
    s: startDate,
    r: rows.map((row) => [
      toDayOffset(startDate, row.date),
      row.sectorOnboardingMicroPibs,
      row.clientsWithActiveDataGt1Tibs,
      row.dealStorageCostNanoFil,
      row.totalValueFlowMilliFil,
    ]),
  }

  await mkdir(path.dirname(OUTPUT_PATH), { recursive: true })
  await writeFile(OUTPUT_PATH, JSON.stringify(compactDataset))

  connection.closeSync()
}
