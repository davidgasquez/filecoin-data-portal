// Run after `npm run build`; checks actual HTML, not just the metric inventory.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { sections } from '../src/sections.ts'
import { numbersSections } from '../src/numbers-sections.ts'

const dist = resolve(process.env.SITE_DIST ?? 'dist')
const site = process.env.SITE_URL ?? 'https://filecoindataportal.xyz'
const archive = process.env.ARCHIVE_URL ?? 'https://old.filecoindataportal.xyz'
const page = await readFile(resolve(dist, 'numbers/index.html'), 'utf8')
const home = await readFile(resolve(dist, 'index.html'), 'utf8')
const primary = sections.flatMap((section) => section.groups.flatMap((group) => group.charts))
const columns = primary.flatMap((metric) => [metric.y, ...(metric.details ?? []).map((item) => item.y), ...(metric.series ?? []).filter((item) => item.y !== metric.y).map((item) => item.y)])

test('landing and Numbers are distinct routes with the portal identity', () => {
  assert.match(home, /filecoindataportal\.xyz/)
  assert.match(home, /href="\/numbers"/)
  assert.match(home, /SKILL\.md/)
  assert.doesNotMatch(home, /data-primary-metric=/)
})
test('homepage actions and dataset copy stay concise without counts or the diagram caption', () => {
  assert.match(home, /<a[^>]+class="button primary"[^>]+href="\/datasets"[^>]*>Datasets<\/a>/)
  assert.match(home, /<a[^>]+class="button"[^>]+href="\/numbers"[^>]*>Dashboard<\/a>/)
  assert.match(home, /href="\/datasets"[^>]*>more datasets<\/a>/)
  assert.match(home, /Public tables, each a Parquet file you can query directly\./)
  assert.doesNotMatch(home, /\d+ (?:public tables|more tables)|How the portal is built|flow-caption|Browse datasets|Read the numbers/)
  assert.match(home, /<figure[^>]+class="flow"[^>]+aria-label="[^"]+"/)
})
test('Get Answers offers one agent instruction and a formatted SQL alternative', () => {
  assert.match(home, /<h2[^>]+id="quickstart"[^>]*>Get Answers<\/h2>/)
  assert.match(home, /<h3[^>]+id="ask-agent"[^>]*>Paste this into your favorite agent<\/h3>/)
  assert.match(home, /<h3[^>]+id="sql"[^>]*><a[^>]+href="\/docs"[^>]*>Query it yourself<\/a><\/h3>/)
  assert.doesNotMatch(home, /Answer a question|Ask your agent|Query with SQL|Or query it yourself|ampcode\.com|chatgpt\.com|claude\.ai/)
  assert.match(home, /aria-label="Agent prompt"/)
  const sql = home.match(/<pre[^>]+aria-label="DuckDB query"[^>]*><code>([\s\S]*?)<\/code>/)?.[1]
  assert.ok(sql)
  assert.match(sql, /^select\s*\n +date,\s*\n +raw_power_pibs,\s*\n +onboarded_pibs\s*\nfrom/i)
  assert.match(sql, /daily_network_metrics\.parquet/)
  assert.match(sql, /order by date desc\s*\nlimit 7;/i)
})
test('helper prose is removed and the footer links the author, code license and llms.txt', () => {
  assert.doesNotMatch(home, /teach agents to find, query, and chart|Any Parquet reader works|covers caveats before citing|Latest observation per metric, UTC|Every chart and all network metrics|Follow providers and payments/)
  assert.ok(home.includes(`href="${new URL('/SKILL.md', site).href}"`))
  for (const html of [home, page]) {
    const footer = html.match(/<footer\b[\s\S]*?<\/footer>/)?.[0]
    assert.ok(footer)
    assert.match(footer, /Built by <a[^>]+href="https:\/\/davidgasquez\.com\/"[^>]*>David Gasquez<\/a>/)
    assert.match(footer, /href="https:\/\/github\.com\/davidgasquez\/filecoin-data-portal\/blob\/main\/LICENSE"[^>]*>MIT license<\/a>/)
    assert.match(footer, /href="\/llms\.txt"[^>]*>llms\.txt<\/a>/)
    assert.ok(footer.includes(`href="${archive}"`), 'Previous site points to this build’s archive')
    assert.match(footer, />Previous site<\/a>/)
    assert.doesNotMatch(footer, /Filecoin Data Portal|Datasets rebuild daily/)
  }
})
test('the sixth headline uses the billing-payer chart value and its observation date', () => {
  const facts = home.match(/<dl class="facts home-facts"[^>]*>([\s\S]*?)<\/dl>/)?.[1]
  assert.ok(facts)
  assert.equal([...facts.matchAll(/<dt\b/g)].length, 6)
  const payer = facts.match(/<dt><a href="\/numbers#warm_storage_billing_payers"[^>]*>Warm storage billing payers<\/a><\/dt><dd>([^<]+)<span class="meta">([^<]+)<\/span><\/dd>/)
  assert.ok(payer)
  const chart = page.match(/<figure[^>]+id="warm_storage_billing_payers"[\s\S]*?<\/figure>/)?.[0]
  assert.ok(chart)
  assert.equal(payer[1], chart.match(/class="chart-value"[^>]*>([^<]+)<\/span>/)?.[1])
  assert.match(payer[2], /^\d{4}-\d{2}-\d{2}$/)
  assert.ok(chart.includes(`Latest non-null observation: ${payer[2]}`))
})
test('the shared theme control is an SVG icon hidden until enhancement is available', () => {
  for (const html of [home, page]) {
    const toggle = html.match(/<button\b[^>]*data-theme-toggle[^>]*>[\s\S]*?<\/button>/)?.[0]
    assert.ok(toggle)
    assert.match(toggle, /\bhidden\b/)
    assert.match(toggle, /<svg\b[^>]*aria-hidden="true"/)
    assert.doesNotMatch(toggle, />\s*(?:Light|Dark)\s*</)
  }
})
test('Numbers represents the complete inventory, with the flow pair combined and the declared zero visible', () => {
  const rendered = [...page.matchAll(/data-metric="([^"]+)"/g)].map(match => match[1])
  const negative = [...page.matchAll(/data-negative-metric="([^"]+)"/g)].map(match => match[1])
  assert.deepEqual([...rendered, ...negative].sort(), [...columns].sort())
  assert.equal([...page.matchAll(/data-primary-metric=/g)].length, primary.length - 1)
  assert.deepEqual(negative, ['terminated_pibs'])
  const declared = page.match(/<figure[^>]+id="high_profile_paying_clients"[\s\S]*?<\/figure>/)?.[0]
  assert.ok(declared)
  assert.match(declared, /data-declared-value="0"/)
  assert.match(declared, /no dated history/)
  assert.match(declared, /<svg[^>]+role="img"[^>]+aria-label="[^"]*constant 0/)
  assert.match(declared, /<path[^>]+d="M3,140H637"/)
  assert.doesNotMatch(declared, /data-chart|data-range|data-start|data-values/)
  assert.doesNotMatch(page, /data-metric="annual_coverage_days"/)
  const ids = [...page.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1])
  assert.equal(ids.length, new Set(ids).size, 'Chart anchors must be unique')
})
test('hover payloads, integrated sources and full-number values are present', () => {
  assert.match(page, /data-chart/)
  assert.match(page, /chart-tooltip/)
  assert.match(page, /class="metric-info"/)
  const values = [...page.matchAll(/class="chart-value"[^>]*>(.*?)<\/span>/g)].map((match) => match[1])
  assert.ok(values.length >= primary.length - 1)
  assert.doesNotMatch(values.join('\n'), /\d(?:\.\d+)?[KMB](?=\s|$)/)
  assert.doesNotMatch(page, /Observed Oct 26, 2026/)
  assert.doesNotMatch(page, /class="chart-scale/)
})
test('PDP volume uses unique data as its headline without duplicate series anchors', () => {
  const unique = page.match(/<figure[^>]+id="pdp_unique_bytes"[\s\S]*?<\/figure>/)?.[0]
  assert.ok(unique)
  assert.match(unique, /PDP Data Volume/)
  assert.match(unique, /Headline: unique data/)
  assert.match(page, /Unique data on 2\+ providers/)
  assert.match(page, /Total registered data \(including copies\)/)
  assert.match(home, /Unique PDP data/)
  assert.match(home, /href="\/numbers#pdp_unique_bytes"/)
})
test('static history matches every rendered series, including the negative companion', async () => {
  const history = JSON.parse(await readFile(resolve(dist, 'numbers-history.json'), 'utf8'))
  assert.equal(history.high_profile_paying_clients, undefined)
  assert.equal(history.annual_coverage_days, undefined)
  assert.ok(Object.values(history).some(series => series.values.length > 366), 'All is not limited to one year')
  for (const [tag] of page.matchAll(/<div\b[^>]*\bdata-chart\s[^>]*>/g)) {
    const attr = name => tag.match(new RegExp(`${name}="([^"]*)"`))?.[1]
    const start = attr('data-start')
    for (const [keyName, valuesName] of [['data-key', 'data-values'], ['data-negative-key', 'data-negative-values']]) {
      const key = attr(keyName)
      if (!key) continue
      const source = history[key]
      assert.ok(source, `${key} has complete static history`)
      const offset = (Date.parse(start) - Date.parse(source.start)) / 86400000
      const values = JSON.parse(attr(valuesName))
      assert.deepEqual(values, values.map((_, i) => source.values[offset + i] ?? null), key)
    }
  }
})
test('history controls, compact navigation and pre-paint theme preference are present', () => {
  assert.match(page, /data-chart-range/)
  for (const value of ['6m', '1y', 'all']) assert.match(page, new RegExp(`name="numbers-range" value="${value}"`))
  assert.doesNotMatch(page, /Hover or focus a chart for daily values/)
  assert.match(page, /class="section-menu"/)
  assert.match(home, /data-theme-toggle/)
  assert.ok(home.indexOf('fdp-theme') < home.indexOf('<body>'), 'Saved theme applies before the body paints')
})
test('legacy chart slugs, column anchors and old table anchors all resolve to unique targets', () => {
  const ids = [...page.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1])
  const legacy = numbersSections.flatMap((section) => section.groups.flatMap((group) => group.charts.map((chart) => chart.id)))
  assert.ok(legacy.length > 50)
  for (const id of [...legacy, ...columns, 'terminated_pibs', 'provider-comparison', 'solstice-q1']) assert.ok(ids.includes(id), `#${id} resolves`)
  assert.equal(ids.length, new Set(ids).size, 'Anchors must be unique')
  assert.match(page, /<details class="audit" id="provider-comparison">/)
})
test('the combined flow chart answers to both legacy slugs and both columns without a duplicate chart', () => {
  const combined = page.match(/<div class="metric[^"]*" id="sector-onboarding"[\s\S]*?<\/figure>/)?.[0]
  assert.ok(combined)
  for (const id of ['sector-termination', 'terminated_pibs']) assert.match(combined, new RegExp(`<span class="anchor-alias" id="${id}"[^>]*></span>`))
  assert.match(combined, /<figure[^>]+id="onboarded_pibs"[^>]+data-negative-metric="terminated_pibs"/)
  assert.equal([...page.matchAll(/class="anchor-alias/g)].length, 2)
  assert.equal([...page.matchAll(/<figure[^>]+data-metric="terminated_pibs"/g)].length, 0)
})
test('every chart Info panel has a native link and a progressive copy button outside its summary', () => {
  const ids = new Set([...page.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]))
  const figures = [...page.matchAll(/<figure class="chart"[\s\S]*?<\/figure>/g)].map((match) => match[0])
  assert.equal(figures.length, [...page.matchAll(/data-metric="/g)].length)
  for (const figure of figures) {
    const link = figure.match(/<p class="meta chart-link"[^>]*>Link <a href="#([^"]+)"[^>]*>#\1<\/a> <button class="button" type="button" data-copy-link="\1" aria-label="Copy link to [^"]+" hidden[^>]*>Copy link<\/button><span role="status"[^>]*><\/span><\/p>/)
    assert.ok(link, figure.slice(0, 120))
    assert.ok(ids.has(link[1]), `#${link[1]} exists`)
    assert.doesNotMatch(figure.match(/<summary[^>]*>[\s\S]*?<\/summary>/)[0], /<a |<button/)
  }
  assert.match(page, /href="#raw-power"[^>]*>#raw-power</)
  assert.match(page, /href="#sector-onboarding"[^>]*>#sector-onboarding</)
  assert.match(page, /href="#high-profile-paying-clients"[^>]*>#high-profile-paying-clients</)
  assert.match(page, /href="#provider_storage_successes"[^>]*>#provider_storage_successes</)
})
