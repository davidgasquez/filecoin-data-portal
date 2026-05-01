import { DuckDBInstance } from "@duckdb/node-api";

const DAILY_NETWORK_METRICS_PARQUET_URL =
  "https://data.filecoindataportal.xyz/daily_network_metrics.parquet";

type DatasetValue = boolean | number | string | null;
type DatasetRow = Record<string, DatasetValue>;

const SQL = `
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
    protocol_revenue_fil,
    locked_fil / nullif(circulating_fil, 0) AS locked_to_circulating_ratio,
    block_rewards_fil,
    reward_per_wincount_fil,
    coalesce(filecoin_pay_active_payers, 0) AS filecoin_pay_active_payers,
    coalesce(filecoin_pay_active_rails, 0) AS filecoin_pay_active_rails,
    coalesce(usdfc_paid, 0) AS usdfc_paid,
    coalesce(arr_usdfc, 0) AS arr_usdfc,
    revenue_coverage_ratio,
    0 AS high_profile_paying_clients,
    fil_token_price_avg_usd,
    fil_token_volume_usd,
    fil_token_market_cap_usd,
    annual_pgf_deployments_usd,
    annual_protocol_revenue_usd,
    annual_block_rewards_usd
  FROM read_parquet('${DAILY_NETWORK_METRICS_PARQUET_URL}')
  WHERE date IS NOT NULL
  ORDER BY date
`;

function normalizeNumber(value: number): number {
  if (!Number.isFinite(value)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }

  if (Number.isInteger(value)) {
    return value;
  }

  return Math.round(value * 1_000_000) / 1_000_000;
}

function normalizeDate(value: Date): string {
  if (Number.isNaN(value.getTime())) {
    throw new Error(`Invalid date value: ${value}`);
  }

  const isoValue = value.toISOString();
  return isoValue.endsWith("T00:00:00.000Z") ? isoValue.slice(0, 10) : isoValue;
}

function normalizeValue(value: unknown): DatasetValue {
  if (value == null) {
    return null;
  }

  if (typeof value === "boolean" || typeof value === "string") {
    return value;
  }

  if (typeof value === "number") {
    return normalizeNumber(value);
  }

  if (typeof value === "bigint") {
    const numberValue = Number(value);

    if (!Number.isSafeInteger(numberValue)) {
      throw new Error(
        `BigInt value is outside the safe integer range: ${value}`,
      );
    }

    return numberValue;
  }

  if (value instanceof Date) {
    return normalizeDate(value);
  }

  throw new Error(`Unsupported dataset value type: ${String(value)}`);
}

function normalizeRow(row: Record<string, unknown>): DatasetRow {
  return Object.fromEntries(
    Object.entries(row).map(([column, value]) => [
      column,
      normalizeValue(value),
    ]),
  );
}

export default async function generateFilecoinDailyMetricsDataset(): Promise<
  DatasetRow[]
> {
  const instance = await DuckDBInstance.create(":memory:");
  const connection = await instance.connect();
  const result = await connection.run(SQL);
  const rawRows = (await result.getRowObjectsJson()) as Array<
    Record<string, unknown>
  >;

  if (rawRows.length === 0) {
    throw new Error("No rows returned from daily metrics dataset query");
  }

  connection.closeSync();

  return rawRows.map(normalizeRow);
}
