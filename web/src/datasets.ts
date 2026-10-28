import { dataUrl, query } from "./db"

export type Column = { name: string; type: string; description: string }
export type Dataset = {
  id: string
  description: string
  rows: number
  url: string
  codeUrl: string
  columns: Column[]
  sample: Record<string, unknown>[]
}

const tables = await query(`
  SELECT table_name AS id, comment AS description, estimated_size AS rows
  FROM duckdb_tables() WHERE database_name = 'fdp' AND schema_name = 'main'
  ORDER BY table_name
`)

export const datasets: Dataset[] = await Promise.all(tables.map(async (table) => {
  const id = String(table.id)
  const columns = await query(`
    SELECT column_name AS name, data_type AS type, coalesce(comment, '') AS description
    FROM duckdb_columns() WHERE database_name = 'fdp' AND schema_name = 'main' AND table_name = '${id}'
    ORDER BY column_index
  `) as Column[]
  return {
    id,
    description: String(table.description ?? ""),
    rows: Number(table.rows),
    url: `${dataUrl}/${id}.parquet`,
    codeUrl: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/${id}.sql`,
    columns,
    sample: await query(`SELECT * FROM main."${id}" LIMIT 10`),
  }
}))

export const cell = (value: unknown) => value == null ? "null" : typeof value === "object" ? JSON.stringify(value) : String(value)
const escape = (value: string) => value.replaceAll("|", "\\|").replaceAll("\n", " ")

// Markdown for agents: /assets/<id>.md
export function datasetMarkdown(dataset: Dataset): string {
  const names = dataset.columns.map((column) => column.name)
  return [
    `# ${dataset.id}`,
    "",
    dataset.description,
    "",
    `- dataset url: \`${dataset.url}\``,
    `- asset code: \`${dataset.codeUrl}\``,
    `- rows: \`${dataset.rows}\``,
    "",
    "## Columns",
    "",
    "| column | type | description |",
    "|---|---|---|",
    ...dataset.columns.map((column) => `| \`${column.name}\` | \`${column.type}\` | ${escape(column.description)} |`),
    "",
    "## Sample",
    "",
    `| ${names.join(" | ")} |`,
    `|${names.map(() => "---|").join("")}`,
    ...dataset.sample.map((row) => `| ${names.map((name) => escape(cell(row[name]))).join(" | ")} |`),
    "",
  ].join("\n")
}
