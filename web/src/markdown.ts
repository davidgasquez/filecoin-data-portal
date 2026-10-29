import type { Dataset } from './data'

// Plain Markdown for agents, from the same Dataset objects as the HTML pages.
// Cells keep exact stored values: atto/bigint strings untouched, null distinct from 0.

const text = (value: string) => value.replace(/\s*(?:\r\n|\r|\n)\s*/g, ' ').replace(/[\\|`*_<>[\]]/g, '\\$&')
const code = (value: string) => {
  const flat = value.replace(/\r?\n|\r/g, ' ')
  const fence = '`'.repeat(Math.max(0, ...(flat.match(/`+/g) ?? []).map((run) => run.length)) + 1)
  const pad = /^`|`$/.test(flat) || /^ .* $/.test(flat) ? ' ' : ''
  return `${fence}${pad}${flat}${pad}${fence}`
}
// Table cells: pipes must be escaped even inside code spans (GFM strips the backslash).
const cellCode = (value: string) => code(value).replaceAll('|', '\\|')
export const value = (raw: unknown) => {
  if (raw == null) return 'null'
  // Strings that would be ambiguous or break a row are shown as JSON literals.
  const exact = typeof raw === 'string' ? (raw === '' || raw.trim() !== raw || /[\\\r\n\t]/.test(raw) ? JSON.stringify(raw) : raw) : typeof raw === 'object' ? JSON.stringify(raw) : String(raw)
  return cellCode(exact)
}
const link = (origin: string | URL, path: string) => new URL(path, origin).href
const page = (id: string) => `/datasets/${encodeURIComponent(id)}`

export function catalogMarkdown(datasets: Dataset[], origin: string | URL) {
  return [
    '# Filecoin Data Portal datasets',
    '',
    `${datasets.length} public tables. Each is a Parquet file you can query directly, for example with DuckDB.`,
    '',
    ...datasets.map(({ id, description, url }) =>
      `- [${code(id)}](${link(origin, `${page(id)}.md`)}): ${description ? text(description) : 'No description.'} [Page](${link(origin, page(id))}) · [Parquet](${url})`),
    '',
  ].join('\n')
}

export function datasetMarkdown(dataset: Dataset, origin: string | URL) {
  const { id, title, description, rows, url, codeUrl, columns, sample, key, sources, coverage } = dataset
  const names = columns.map(({ name }) => name)
  return [
    `# ${text(title)}`,
    '',
    description ? text(description) : 'No description.',
    '',
    `- Table: ${code(id)}`,
    `- Parquet: ${url}`,
    `- Source SQL: ${codeUrl}`,
    `- Page: ${link(origin, page(id))}`,
    `- Catalog: ${link(origin, '/datasets.md')}`,
    `- Rows: ≈ ${rows.toLocaleString('en-US')} (snapshot estimate) · ${columns.length} columns`,
    ...(key.length ? [`- Key (grain): ${key.map(code).join(', ')}`] : []),
    coverage?.start
      ? `- Coverage, UTC: ${code(coverage.start)} to ${code(coverage.end ?? coverage.start)} (first and last day before today; days may be missing)`
      : coverage ? '- Coverage: no dated rows before today' : '- Coverage: not date-indexed',
    `- Raw sources: ${sources.length ? sources.map(code).join(', ') : 'none declared'}`,
    '',
    '## Query',
    '',
    '```sql',
    `select *\nfrom '${url.replaceAll("'", "''")}'${coverage ? '\norder by date desc' : ''}\nlimit 10;`,
    '```',
    '',
    '## Columns',
    '',
    '| Name | Type | Description |',
    '| --- | --- | --- |',
    ...columns.map(({ name, type, description }) => `| ${cellCode(name)} | ${cellCode(type)} | ${description ? text(description) : ''} |`),
    ...(sample.length ? [
      '',
      '## Sample',
      '',
      `${sample.length} rows exactly as stored${coverage ? ', latest first' : ''}. Values are code spans; strings with whitespace or backslashes use JSON literals. A bare null is missing, not zero.`,
      '',
      `| ${names.map(cellCode).join(' | ')} |`,
      `| ${names.map(() => '---').join(' | ')} |`,
      ...sample.map((row) => `| ${names.map((name) => value(row[name])).join(' | ')} |`),
    ] : []),
    '',
  ].join('\n')
}
