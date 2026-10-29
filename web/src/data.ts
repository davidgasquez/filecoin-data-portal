import { DuckDBInstance } from '@duckdb/node-api'
import { readFile, readdir } from 'node:fs/promises'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
import { number, pooledQuality } from './metrics.mjs'
import { missingMetricSources } from './schema'

export const repoUrl = 'https://github.com/davidgasquez/filecoin-data-portal'
export const dataUrl = 'https://data.filecoindataportal.xyz'
export const builtAt = new Date().toISOString().slice(0, 10)
export type Row = Record<string, string | number | boolean | null>
export type Column = { name: string; type: string; description: string }
export type Dataset = {
  id: string; title: string; description: string; rows: number; url: string; codeUrl: string
  columns: Column[]; sample: Row[]; key: string[]; sources: string[]
  coverage: { start: string | null; end: string | null } | null
}

// Local and read-only by default. No remote snapshot downloads or materialization.
const source = resolve(process.env.FDP_DB ?? '../fdp.duckdb')
const instance = await DuckDBInstance.create(source, { access_mode: 'READ_ONLY' })
const connection = await instance.connect()
await connection.run("SET TimeZone = 'UTC'")
const query = async (sql: string): Promise<Row[]> => (await connection.runAndReadAll(sql)).getRowObjectsJson() as Row[]
const literal = (value: string) => `'${value.replaceAll("'", "''")}'`
const identifier = (value: string) => `"${value.replaceAll('"', '""')}"`
const assetRoot = pathToFileURL(resolve('../assets') + '/')
const files = (await readdir(assetRoot, { recursive: true })).filter((path) => /\.(sql|py)$/.test(path) && !path.includes('.test.'))
const assets = new Map<string, string>(await Promise.all(files.map(async (path) => {
  const [schema, ...parts] = path.replace(/\.(sql|py)$/, '').split('/')
  return [`${schema}.${parts.join('_')}`, await readFile(new URL(path, assetRoot), 'utf8')] as const
})))
function sources(id: string, seen = new Set<string>()): string[] {
  if (seen.has(id)) return []
  seen.add(id)
  if (id.startsWith('raw.')) return [id]
  return [...new Set([...((assets.get(id) ?? '').matchAll(/asset\.depends\s*=\s*([\w.]+)/g))]
    .flatMap((match) => sources(match[1], seen)))].sort()
}

const tables = await query("SELECT table_name AS id, comment AS description, estimated_size AS rows FROM duckdb_tables() WHERE schema_name = 'main' AND NOT internal ORDER BY table_name")
export const datasets: Dataset[] = []
for (const table of tables) {
  const id = String(table.id)
  const columns = await query(`SELECT column_name AS name, data_type AS type, coalesce(comment, '') AS description FROM duckdb_columns() WHERE schema_name = 'main' AND table_name = ${literal(id)} ORDER BY column_index`) as unknown as Column[]
  const dated = columns.some((column) => column.name === 'date')
  const coverage = dated ? (await query(`SELECT min(date)::varchar AS start, max(date)::varchar AS "end" FROM main.${identifier(id)} WHERE date < current_date`))[0] : null
  datasets.push({
    id, title: id.replaceAll('_', ' ').replace(/^./, (letter) => letter.toUpperCase()), description: String(table.description ?? ''), rows: Number(table.rows),
    url: `${dataUrl}/${id}.parquet`, codeUrl: `${repoUrl}/blob/main/assets/main/${id}.sql`, columns,
    sample: await query(`SELECT * FROM main.${identifier(id)} ${dated ? 'WHERE date < current_date ORDER BY date DESC' : ''} LIMIT 5`),
    key: [...((assets.get(`main.${id}`) ?? '').matchAll(/asset\.unique\s*=\s*([^\n]+)/g))].flatMap((match) => match[1].trim().split(/\s*,\s*/)),
    sources: sources(`main.${id}`), coverage: coverage as Dataset['coverage'],
  })
}
// Previews may expose unavailable observations honestly; a production build must have every source column.
export const missingSources = missingMetricSources(datasets)
if (missingSources.length) {
  const message = `Snapshot lacks required metric sources: ${missingSources.join(', ')}`
  if (import.meta.env.PROD && new URL(process.env.SITE_URL || 'https://filecoindataportal.xyz').origin === 'https://filecoindataportal.xyz') {
    connection.closeSync()
    instance.closeSync()
    throw new Error(message)
  }
  console.warn(message)
}
export const network = datasets.find((dataset) => dataset.id === 'daily_network_metrics')!
const networkRows = await query('SELECT * REPLACE (date::varchar AS date) FROM main.daily_network_metrics WHERE date < current_date ORDER BY date')
if (!networkRows.length) throw new Error('No daily network observations. Set FDP_DB to a materialized FDP snapshot.')
export const quality = await query('SELECT * REPLACE (date::varchar AS date) FROM main.daily_provider_quality WHERE date < current_date ORDER BY date')
const byDate = new Map(networkRows.map((row) => [String(row.date), row]))
for (const row of pooledQuality(quality)) byDate.set(String(row.date), { ...byDate.get(String(row.date)), ...row })
export const daily: Row[] = [...byDate.values()].sort((a, b) => String(a.date).localeCompare(String(b.date))).map((row) => ({
  ...row,
  locked_to_circulating_ratio: number(row.locked_fil) != null && Number(row.circulating_fil) > 0 ? Number(row.locked_fil) / Number(row.circulating_fil) : null,
}))
export const providers = await query('SELECT provider_id, name FROM main.providers')
export const quarters = await query('SELECT * FROM main.service_quarters ORDER BY quarter DESC')
export const orchestrators = await query('SELECT * FROM main.orchestrator_quarters ORDER BY quarter DESC, orchestrator')
connection.closeSync()
instance.closeSync()
