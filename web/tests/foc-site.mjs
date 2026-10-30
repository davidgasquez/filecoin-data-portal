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
test('one explorer header: sections, a portal menu and search; breadcrumbs only for entities', () => {
  const labels = ['Overview', 'Providers', 'Storage data sets', 'Rails', 'Clients', 'Operators', 'Solstice']
  for (const route of ['', ...samples]) {
    const page = html(route)
    assert.equal([...page.matchAll(/<header class="site-header/g)].length, 1, `${route}: one site header`)
    assert.doesNotMatch(page, /subbar|subnav|aria-label="Primary"/)
    const header = page.match(/<header class="site-header[\s\S]*?<\/header>/)[0]
    assert.match(header, /<a class="brand" href="\/"[\s\S]*?<span>filecoindataportal\.xyz<\/span><\/a>/)
    assert.match(header, /<form class="foc-search" role="search" action="\/foc"[^>]*hidden>[\s\S]*?role="combobox"/)
    // The inline sections (wide screens) and the menu's copy (narrow screens) are the same links with the same state.
    const navs = [...header.matchAll(/<nav\b[^>]*aria-label="Onchain Cloud"[^>]*>([\s\S]*?)<\/nav>/g)].map(match => match[1])
    assert.equal(navs.length, 2)
    assert.equal(navs[0], navs[1])
    const nav = navs[0]
    assert.deepEqual([...nav.matchAll(/<a\b[^>]*>([^<]+)<\/a>/g)].map(match => match[1]), labels)
    assert.match(nav, /href="\/foc\/datasets"[^>]*>Storage data sets<\/a>/)
    const entity = route.includes('/')
    const section = ({ provider: 'providers', dataset: 'datasets', rail: 'rails', address: 'clients' })[route.split('/')[0]] ?? route
    const current = nav.match(new RegExp(`<a[^>]+href="/foc${section ? `/${section}` : ''}"[^>]*>([^<]+)`))
    assert.ok(current)
    assert.ok(current[0].includes(`aria-current="${entity ? 'true' : 'page'}"`))
    assert.equal([...nav.matchAll(/aria-current=/g)].length, 1)
    // The menu names the section (an entity's parent list) and leads out to the rest of the portal.
    const menu = header.match(/<details class="foc-menu">([\s\S]*?)<\/details>/)?.[1]
    assert.ok(menu)
    assert.match(menu, new RegExp(`<summary><span>Onchain Cloud</span><span class="foc-menu-current">${current[1]}</span><span aria-hidden="true">▾</span></summary>`))
    const portal = menu.match(/<nav\b[^>]*aria-label="Portal"[^>]*>([\s\S]*?)<\/nav>/)?.[1]
    assert.deepEqual([...portal.matchAll(/<a href="([^"]+)"/g)].map(match => match[1]), ['/', '/numbers', '/foc', '/datasets', '/docs'])
    assert.ok(portal.includes(`<a href="/foc" aria-current="${route ? 'true' : 'page'}">Onchain Cloud<`))
    assert.match(portal, /href="\/datasets">Datasets<span class="meta">Public table catalog<\/span>/)
    assert.match(portal, /<a href="\/">Filecoin Data Portal<span class="meta">filecoindataportal\.xyz<\/span><\/a>/)
    assert.doesNotMatch(portal, /<p\b|>Home<|data-astro-prefetch/)
    const crumbs = page.match(/<nav\b[^>]*aria-label="Breadcrumb"[^>]*>([\s\S]*?)<\/nav>/)?.[1]
    assert.equal(!!crumbs, entity, route || 'overview')
    if (entity) assert.match(crumbs, /aria-current="page"/)
    if (route.startsWith('dataset/')) assert.match(crumbs, />Storage data sets<\/a>/)
  }
})
test('only explorer routes opt into client swaps and prefetch only internal links', () => {
  for (const route of ['', ...samples]) {
    const page = html(route)
    assert.match(page, /name="astro-view-transitions-enabled"/)
    assert.match(page, /::view-transition-new\(\*\).*animation:none/)
    const prefetch = [...page.matchAll(/<a\b[^>]*data-astro-prefetch="([^"]*)"[^>]*>/g)]
    assert.ok(prefetch.length > 0)
    for (const [tag, strategy] of prefetch) {
      assert.equal(strategy, 'hover')
      assert.match(tag, /href="\/foc(?:\/|"|#)/)
    }
  }
  for (const file of ['index.html', 'numbers/index.html', 'datasets/index.html', 'docs/index.html']) {
    assert.doesNotMatch(readFileSync(resolve(dist, '..', file), 'utf8'), /name="astro-view-transitions-enabled"/)
  }
})

test('pages preload only normal font faces and do not load a global prefetch entry', () => {
  for (const page of [overview, html('providers'), readFileSync(resolve(dist, '../numbers/index.html'), 'utf8')]) {
    const fonts = [...page.matchAll(/<link\b[^>]*rel="preload"[^>]*as="font"[^>]*>/g)]
    assert.equal(fonts.length, 4)
    assert.doesNotMatch(page, /font-style:italic/)
    assert.doesNotMatch(page, /src="\/_astro\/page\.[^"]+\.js"/)
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
