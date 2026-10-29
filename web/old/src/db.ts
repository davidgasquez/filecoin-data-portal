import { DuckDBInstance } from "@duckdb/node-api"

export type Row = Record<string, string | number | boolean | null>

// Build-time only. The archive is frozen: FDP_DB must point to the archived snapshot, never the live database.
export const dataUrl = "https://data.filecoindataportal.xyz"
const source = process.env.FDP_DB
if (!source) throw new Error("FDP_DB is required: point it to the archived fdp.duckdb snapshot (see README.md)")

const connection = await (await DuckDBInstance.create(":memory:")).connect()
await connection.run("SET TimeZone = 'UTC'")
await connection.run(`ATTACH '${source.replaceAll("'", "''")}' AS fdp (READ_ONLY); USE fdp`)

// JSON rows carry BIGINTs as strings; keep *_atto_* amounts exact, parse other integers.
export async function query(sql: string): Promise<Row[]> {
  const rows = (await connection.runAndReadAll(sql)).getRowObjectsJson()
  return rows.map((row) => Object.fromEntries(Object.entries(row).map(([column, value]) => {
    if (typeof value === "string" && /^-?\d+$/.test(value) && !column.includes("_atto_")) return [column, Number(value)]
    if (typeof value === "number" && !Number.isInteger(value)) return [column, Math.round(value * 1e6) / 1e6]
    return [column, value as Row[string]]
  })))
}
