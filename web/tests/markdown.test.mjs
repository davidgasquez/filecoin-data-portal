// Synthetic Dataset objects only; never opens DuckDB (markdown.ts imports data.ts as a type).
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { catalogMarkdown, datasetMarkdown, value } from '../src/markdown.ts'

const base = {
  id: 'daily_things', title: 'Daily things', description: 'Counts | of\nthings with `ticks` and *stars*.', rows: 1234567,
  url: 'https://data.example/daily_things.parquet', codeUrl: 'https://code.example/daily_things.sql',
  columns: [
    { name: 'date', type: 'DATE', description: 'Day, UTC.' },
    { name: 'burn_atto', type: 'HUGEINT', description: 'Burn in attoFIL | exact.' },
    { name: 'note', type: 'VARCHAR', description: '' },
  ],
  sample: [
    { date: '2026-10-28', burn_atto: '123456789012345678901234567890', note: 'a|b`c' },
    { date: '2026-10-27', burn_atto: '0', note: null },
    { date: '2026-10-26', burn_atto: null, note: 'line\nbreak' },
  ],
  key: ['date'], sources: ['raw.chain_things', 'raw.prices'], coverage: { start: '2026-01-01', end: '2026-10-28' },
}
const origin = 'https://preview.example.dev'
const lines = (markdown) => markdown.split('\n')
const cells = (row) => row.slice(1, -1).split(/(?<!\\)\|/).map((cell) => cell.trim())

test('cell values keep exact strings and distinguish null from zero', () => {
  assert.equal(value('123456789012345678901234567890'), '`123456789012345678901234567890`')
  assert.equal(value('0'), '`0`')
  assert.equal(value(0), '`0`')
  assert.equal(value(null), 'null')
  assert.equal(value(undefined), 'null')
  assert.equal(value(''), '`""`')
  assert.equal(value('  '), '`"  "`')
  assert.equal(value(' padded '), '`" padded "`')
  assert.equal(value('a\tb'), '`"a\\tb"`')
  assert.equal(value('a|b`c'), '``a\\|b`c``')
  assert.equal(value('line\nbreak'), '`"line\\nbreak"`')
  const withSlashAndPipe = 'a\\|b'
  assert.equal(value(withSlashAndPipe), '`' + JSON.stringify(withSlashAndPipe).replaceAll('|', '\\|') + '`')
  assert.equal(value(false), '`false`')
  assert.equal(value({ a: [1] }), '`{"a":[1]}`')
})

test('dataset Markdown has metadata, coverage, sources, query, columns and an exact sample', () => {
  const md = datasetMarkdown(base, origin)
  assert.match(md, /^# Daily things\n/)
  assert.match(md, /Counts \\\| of things with \\`ticks\\` and \\\*stars\\\*\./)
  assert.match(md, /- Parquet: https:\/\/data\.example\/daily_things\.parquet/)
  assert.match(md, /- Source SQL: https:\/\/code\.example\/daily_things\.sql/)
  assert.match(md, /- Page: https:\/\/preview\.example\.dev\/datasets\/daily_things\n/)
  assert.match(md, /- Catalog: https:\/\/preview\.example\.dev\/datasets\.md/)
  assert.match(md, /- Rows: ≈ 1,234,567 \(snapshot estimate\) · 3 columns/)
  assert.match(md, /- Key \(grain\): `date`/)
  assert.match(md, /- Coverage, UTC: `2026-01-01` to `2026-10-28` \(first and last day/)
  assert.match(md, /- Raw sources: `raw\.chain_things`, `raw\.prices`/)
  assert.match(md, /```sql\nselect \*\nfrom 'https:\/\/data\.example\/daily_things\.parquet'\norder by date desc\nlimit 10;\n```/)
  assert.doesNotMatch(md, /built|Built/)
  const all = lines(md)
  const head = all.indexOf('| `date` | `burn_atto` | `note` |')
  assert.ok(head > 0)
  const rows = all.slice(head + 2, head + 5)
  assert.deepEqual(rows.map(cells), [
    ['`2026-10-28`', '`123456789012345678901234567890`', '``a\\|b`c``'],
    ['`2026-10-27`', '`0`', 'null'],
    ['`2026-10-26`', 'null', '`"line\\nbreak"`'],
  ])
  assert.ok(all.includes('| `burn_atto` | `HUGEINT` | Burn in attoFIL \\| exact. |'))
  assert.ok(all.includes('| `note` | `VARCHAR` |  |'))
})

test('every table row keeps its column count', () => {
  const md = datasetMarkdown(base, origin)
  for (const row of lines(md).filter((line) => line.startsWith('|'))) {
    const n = cells(row).length
    assert.ok(n === 3, `${n} cells: ${row}`)
  }
})

test('undeclared key, undated coverage, no sources and empty sample stay explicit', () => {
  const md = datasetMarkdown({ ...base, description: '', key: [], sources: [], coverage: null, sample: [] }, origin)
  assert.match(md, /\n\nNo description\.\n/)
  assert.doesNotMatch(md, /Key \(grain\)/)
  assert.match(md, /- Coverage: not date-indexed/)
  assert.doesNotMatch(md, /order by date/)
  assert.match(md, /- Raw sources: none declared/)
  assert.doesNotMatch(md, /## Sample/)
  assert.match(datasetMarkdown({ ...base, coverage: { start: null, end: null } }, origin), /- Coverage: no dated rows before today/)
})

test('catalog lists ids, descriptions and links for the build origin', () => {
  const md = catalogMarkdown([base, { ...base, id: 'providers', description: '' }], origin)
  assert.match(md, /^# Filecoin Data Portal datasets\n\n2 public tables\./)
  assert.ok(lines(md).includes('- [`daily_things`](https://preview.example.dev/datasets/daily_things.md): Counts \\| of things with \\`ticks\\` and \\*stars\\*. [Page](https://preview.example.dev/datasets/daily_things) · [Parquet](https://data.example/daily_things.parquet)'))
  assert.match(md, /- \[`providers`\]\(https:\/\/preview\.example\.dev\/datasets\/providers\.md\): No description\./)
  assert.match(catalogMarkdown([base], new URL('https://filecoindataportal.xyz')), /\(https:\/\/filecoindataportal\.xyz\/datasets\/daily_things\.md\)/)
})
