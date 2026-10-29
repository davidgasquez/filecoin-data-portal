// Run after the full static build. All entity pages must work on a cold request.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { routes, readFoc } from '../src/foc/data.ts'

const dist = resolve(process.env.SITE_DIST ?? 'dist', 'foc')
const html = (route = '') => readFileSync(join(dist, route, 'index.html'), 'utf8')
const overview = html()
const samples = ['providers', 'datasets', 'rails', 'clients', 'operators', 'solstice',
  ...['provider', 'dataset', 'rail', 'address'].map(kind => routes.find(entry => entry.kind === kind).route)]

test('every explorer entity has a real static route', () => {
  for (const { route } of routes) assert.ok(existsSync(join(dist, route ?? '', 'index.html')), `Missing /foc/${route ?? ''}`)
  for (const [kind, file] of [['provider', 'providers'], ['dataset', 'datasets'], ['rail', 'rails']]) {
    assert.equal(routes.filter(entry => entry.kind === kind).length, readFoc(`${file}.json`).length)
  }
})
test('FOC integrates the portal identity and renders essential evidence without JavaScript', () => {
  assert.match(overview, /filecoindataportal\.xyz/)
  assert.match(overview, /href="\/numbers"/)
  assert.match(overview, /<svg/)
  assert.match(overview, /<table/)
  for (const route of samples) {
    const page = html(route)
    assert.equal([...page.matchAll(/<h1\b/g)].length, 1, `${route}: one page heading`)
    if (!route.includes('/')) assert.match(page, /<tbody>[\s\S]*?<tr/)
    assert.doesNotMatch(page, /href="#(?:provider|dataset|rail|address)-/)
    const ids = [...page.matchAll(/\bid="([^"]+)"/g)].map(match => match[1])
    assert.equal(ids.length, new Set(ids).size, `${route}: unique IDs`)
  }
})
test('the overview chart ends at its own last observed day', () => {
  const s = readFoc('overview.json').series
  const expected = s.date[s.run_rate.findLastIndex(value => value != null)]
  const match = overview.match(/data-key="filecoin_pay_gross_payment_volume_run_rate_usd"[^>]*data-start="([^"]+)" data-values="([^"]+)"/)
  assert.ok(match)
  const end = new Date(Date.parse(match[1]) + (JSON.parse(match[2]).length - 1) * 86400000).toISOString().slice(0, 10)
  assert.equal(end, expected)
})

test('sample explorer relationships resolve to generated pages', () => {
  const valid = new Set(routes.map(entry => `/foc${entry.route ? `/${entry.route}` : ''}`))
  for (const route of ['', ...samples]) for (const match of html(route).matchAll(/href="(\/foc[^"?#]*)/g)) {
    const href = match[1].replace(/\/$/, '')
    // JSON downloads, if present, are data rather than page navigation.
    if (!href.endsWith('.json')) assert.ok(valid.has(href), `Broken relationship: ${route} → ${href}`)
  }
})
test('explorer totals, quotes, and snapshot provenance remain consistent', () => {
  assert.equal(readFoc('overview.json').counts[0].clients, readFoc('clients.json').length)
  const coverage = readFoc('coverage.json')
  for (const source of ['rails', 'data_sets']) assert.ok(coverage.find(row => row.source === source)?.observed_at)
  for (const entry of routes.filter(row => row.kind === 'provider')) {
    const { provider } = readFoc(entry.file)
    if (provider.payment_token === '0x0000000000000000000000000000000000000000') {
      assert.equal(provider.price_symbol, 'FIL')
      assert.ok(Number.isFinite(provider.price_tib_month))
    }
  }
  for (const entry of routes.filter(row => row.kind === 'address')) {
    const row = readFoc(entry.file)
    if (row.paid_in != null) assert.ok(Math.abs(row.paid_in - (row.daily_in.v ?? []).reduce((sum, value) => sum + value, 0)) < 1e-7)
  }
})

test('Solstice amounts remain exact atto strings and missing states stay null', () => {
  const data = readFoc('solstice.json')
  for (const row of [...data.quarters, ...data.orchestrator_quarters]) {
    for (const key of ['bound_volume', 'shares_total', 'gate_threshold', 'volume', 'stablecoin_volume', 'fil_volume', 'posted_volume', 'reported_volume', 'fil_pending_atto_fil']) {
      if (row[key] != null) assert.match(row[key], /^-?\d+$/, key)
    }
    if (!row.is_bound) assert.equal(row.bound_volume, null)
  }
})
