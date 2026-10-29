// Run after `npm run build`: Markdown endpoints, catalog anchors and sitemap in the actual output.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const dist = process.env.SITE_DIST ?? 'dist'
const origin = new URL(process.env.SITE_URL ?? 'https://filecoindataportal.xyz').origin
const read = (path) => readFileSync(join(dist, path), 'utf8')
const catalogHtml = read('datasets/index.html')
const ids = readdirSync(join(dist, 'datasets'), { withFileTypes: true }).filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort()

test('catalog and every dataset have Markdown at the build origin', () => {
  assert.ok(ids.length > 5)
  const catalog = read('datasets.md')
  assert.match(catalog, /^# Filecoin Data Portal datasets\n/)
  for (const id of ids) {
    assert.ok(catalog.includes(`- [\`${id}\`](${origin}/datasets/${id}.md): `), `catalog lists ${id}`)
    const md = read(`datasets/${id}.md`)
    assert.match(md, /^# .+\n/)
    assert.ok(md.includes(`- Parquet: https://data.filecoindataportal.xyz/${id}.parquet`), id)
    assert.ok(md.includes(`- Source SQL: https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/${id}.sql`), id)
    assert.ok(md.includes(`- Page: ${origin}/datasets/${id}\n`), id)
    assert.match(md, /- Coverage(?:, UTC: `\d{4}-\d{2}-\d{2}` to `\d{4}-\d{2}-\d{2}`|: not date-indexed|: no dated rows before today)/)
    assert.match(md, /```sql\nselect \*\nfrom '[^']+'\n(?:order by date desc\n)?limit 10;\n```/)
    assert.match(md, /## Columns\n\n\| Name \| Type \| Description \|/)
    for (const section of md.split(/\n## /).slice(1)) {
      const rows = section.split('\n').filter((line) => line.startsWith('|'))
      for (const row of rows) assert.equal(row.split(/(?<!\\)\|/).length, rows[0].split(/(?<!\\)\|/).length, `${id}: ${row.slice(0, 80)}`)
    }
  }
  assert.ok(!existsSync(join(dist, 'numbers.json')), 'no legacy numbers.json')
  assert.ok(!existsSync(join(dist, 'assets')), 'no legacy /assets/*.md')
})

test('catalog and detail pages link Markdown; catalog entries keep unique dataset anchors', () => {
  assert.match(catalogHtml, /href="\/datasets\.md"/)
  const pageIds = [...catalogHtml.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1])
  assert.equal(pageIds.length, new Set(pageIds).size, 'unique IDs')
  for (const id of ids) {
    assert.match(catalogHtml, new RegExp(`<li[^>]*\\bid="${id}"`), `anchor #${id}`)
    const page = read(`datasets/${id}/index.html`)
    assert.ok(page.includes(`href="/datasets/${id}.md"`), `${id} links Markdown`)
    assert.ok(page.includes(`href="/datasets#${id}"`), `${id} returns to its catalog entry`)
  }
})

test('sitemap lists canonical HTML routes once, at the build origin', () => {
  const xml = read('sitemap.xml')
  assert.match(xml, /^<\?xml version="1\.0" encoding="UTF-8"\?>\n<urlset xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9">/)
  const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1])
  assert.equal(locs.length, new Set(locs).size, 'no duplicates')
  for (const path of ['/', '/numbers', '/datasets', '/docs', '/about', '/foc', '/foc/providers']) assert.ok(locs.includes(new URL(path, origin).href), path)
  for (const id of ids) assert.ok(locs.includes(`${origin}/datasets/${id}`), id)
  for (const loc of locs) {
    const url = new URL(loc)
    assert.equal(url.origin, origin)
    assert.doesNotMatch(url.pathname, /\.(?:json|md|xml|txt)$|^\/(?:guide|404|assets)(?:\/|$)/)
    assert.ok(existsSync(join(dist, decodeURIComponent(url.pathname), 'index.html')), `built: ${url.pathname}`)
  }
})
