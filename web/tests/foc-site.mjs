// Run after both static builds (`npm run build`, `npm run build:foc`). All entity pages must work on a cold request.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { routes, readFoc } from '../src/foc/data.ts'

const dist = resolve('dist-foc'), portalDist = resolve(process.env.SITE_DIST ?? 'dist')
const portal = new URL(process.env.SITE_URL || 'https://filecoindataportal.xyz').origin
const site = new URL(process.env.FOC_URL || 'https://foc.filecoindataportal.xyz').origin
const read = path => readFileSync(join(dist, path), 'utf8')
const html = (route = '') => read(join(route, 'index.html'))
const escape = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const overview = html()
const samples = ['providers', 'datasets', 'rails', 'clients', 'operators', 'solstice',
  ...['provider', 'dataset', 'rail', 'address'].map(kind => routes.find(entry => entry.kind === kind).route)]

test('every explorer entity has a real static route', () => {
  for (const { route } of routes) assert.ok(existsSync(join(dist, route ?? '', 'index.html')), `Missing /${route ?? ''}`)
  for (const [kind, file] of [['provider', 'providers'], ['dataset', 'datasets'], ['rail', 'rails']]) {
    assert.equal(routes.filter(entry => entry.kind === kind).length, readFoc(`${file}.json`).length)
  }
})
test('FOC integrates the portal identity and renders essential evidence without JavaScript', () => {
  assert.match(overview, /filecoindataportal\.xyz/)
  assert.ok(overview.includes(`href="${portal}/numbers"`))
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
    assert.match(header, new RegExp(`<a class="brand" href="${escape(portal)}/"[\\s\\S]*?<span>filecoindataportal\\.xyz</span></a>`))
    assert.match(header, /<form class="foc-search" role="search" action="\/"[^>]*hidden>[\s\S]*?role="combobox"/)
    // The inline sections (wide screens) and the menu's copy (narrow screens) are the same links with the same state.
    const navs = [...header.matchAll(/<nav\b[^>]*aria-label="Filecoin Onchain Cloud"[^>]*>([\s\S]*?)<\/nav>/g)].map(match => match[1])
    assert.equal(navs.length, 2)
    assert.equal(navs[0], navs[1])
    const nav = navs[0]
    assert.deepEqual([...nav.matchAll(/<a\b[^>]*>([^<]+)<\/a>/g)].map(match => match[1]), labels)
    assert.match(nav, /href="\/datasets"[^>]*>Storage data sets<\/a>/)
    const entity = route.includes('/')
    const section = ({ provider: 'providers', dataset: 'datasets', rail: 'rails', address: 'clients' })[route.split('/')[0]] ?? route
    const current = nav.match(new RegExp(`<a[^>]+href="/${section}"[^>]*>([^<]+)`))
    assert.ok(current)
    assert.ok(current[0].includes(`aria-current="${entity ? 'true' : 'page'}"`))
    assert.equal([...nav.matchAll(/aria-current=/g)].length, 1)
    // The menu names the section (an entity's parent list) and leads out to the portal's origin.
    const menu = header.match(/<details class="foc-menu">([\s\S]*?)<\/details>/)?.[1]
    assert.ok(menu)
    assert.match(menu, new RegExp(`<summary><span>Filecoin Onchain Cloud</span><span class="foc-menu-current">${current[1]}</span><span aria-hidden="true">▾</span></summary>`))
    const exits = menu.match(/<nav\b[^>]*aria-label="Portal"[^>]*>([\s\S]*?)<\/nav>/)?.[1]
    assert.deepEqual([...exits.matchAll(/<a href="([^"]+)"/g)].map(match => match[1]), [`${portal}/`, `${portal}/numbers`, '/', `${portal}/datasets`, `${portal}/docs`])
    assert.ok(exits.includes(`<a href="/" aria-current="${route ? 'true' : 'page'}">Filecoin Onchain Cloud<`))
    assert.ok(exits.includes(`href="${portal}/datasets">Datasets<span class="meta">Public table catalog</span>`))
    assert.ok(exits.includes(`<a href="${portal}/">Filecoin Data Portal<span class="meta">filecoindataportal.xyz</span></a>`))
    assert.doesNotMatch(exits, /<p\b|>Home<|data-astro-prefetch/)
    const crumbs = page.match(/<nav\b[^>]*aria-label="Breadcrumb"[^>]*>([\s\S]*?)<\/nav>/)?.[1]
    assert.equal(!!crumbs, entity, route || 'overview')
    if (entity) assert.match(crumbs, /aria-current="page"/)
    if (route.startsWith('dataset/')) assert.match(crumbs, />Storage data sets<\/a>/)
  }
})
test('explorer pages opt into client swaps and prefetch only internal links; the portal does not', () => {
  for (const route of ['', ...samples]) {
    const page = html(route)
    assert.match(page, /name="astro-view-transitions-enabled"/)
    assert.match(page, /::view-transition-new\(\*\).*animation:none/)
    const prefetch = [...page.matchAll(/<a\b[^>]*data-astro-prefetch="([^"]*)"[^>]*>/g)]
    assert.ok(prefetch.length > 0)
    for (const [tag, strategy] of prefetch) {
      assert.equal(strategy, 'hover')
      assert.match(tag, /href="\/(?!\/)/)
    }
  }
  for (const file of ['index.html', 'numbers/index.html', 'datasets/index.html', 'docs/index.html']) {
    assert.doesNotMatch(readFileSync(resolve(portalDist, file), 'utf8'), /name="astro-view-transitions-enabled"/)
  }
})

test('pages preload only normal font faces and do not load a global prefetch entry', () => {
  for (const page of [overview, html('providers'), readFileSync(resolve(portalDist, 'numbers/index.html'), 'utf8')]) {
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
  const valid = new Set(routes.map(entry => `/${entry.route ?? ''}`))
  for (const route of ['', ...samples]) for (const match of html(route).matchAll(/href="(\/[^/"?#][^"?#]*|\/)["?#]/g)) {
    const href = match[1]
    // Built assets and JSON downloads are not page navigation.
    if (!/^\/(?:_astro\/|favicon\.svg$)|\.json$/.test(href)) assert.ok(valid.has(href), `Broken relationship: ${route} → ${href}`)
  }
})
test('source disclosures cite the portal catalog, never the explorer\'s storage data sets', () => {
  for (const route of ['', ...samples]) {
    const page = html(route)
    for (const [, href] of page.matchAll(/Sources?: (?:<a href="([^"]+)")/g)) assert.ok(href.startsWith(`${portal}/datasets/`), `${route}: ${href}`)
  }
  assert.ok(overview.includes(`href="${portal}/datasets/daily_network_metrics#filecoin_pay_gross_payment_volume_run_rate_usd"`))
  assert.ok(html('datasets').includes(`portal’s <a href="${portal}/datasets">published datasets</a>`))
  for (const [href, label] of [['/about', 'About'], ['/llms.txt', 'llms.txt']]) assert.ok(overview.includes(`<a href="${portal}${href}">${label}</a>`), label)
})
test('the explorer target has its own canonicals, indexing, sitemap, robots and real 404', () => {
  const preview = site !== 'https://foc.filecoindataportal.xyz'
  for (const route of ['', 'providers', samples.at(-1)]) {
    const page = html(route)
    const url = new URL(`/${route}`, site).href.replace(/\/$/, route ? '' : '/')
    assert.ok(page.includes(`<link rel="canonical" href="${url}">`), url)
    assert.equal(page.includes('<meta name="robots" content="noindex">'), preview)
  }
  const locs = [...read('sitemap.xml').matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1])
  assert.deepEqual(locs, routes.map(({ route }) => `${site}/${route ?? ''}`))
  assert.equal(read('robots.txt'), `User-agent: *\nAllow: /\n${preview ? '' : `\nSitemap: ${site}/sitemap.xml\n`}`)
  assert.equal(read('_headers').includes('X-Robots-Tag: noindex'), preview)
  assert.match(read('404.html'), /<h1>Not found<\/h1>[\s\S]*href="\/">Filecoin Onchain Cloud overview<\/a>/)
  // Portal-relative agent files belong to the portal only.
  for (const file of ['SKILL.md', 'llms.txt', 'datasets.md', 'numbers/index.html', 'foc/index.html']) assert.ok(!existsSync(join(dist, file)), file)
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

test('explorer pages omit source footers and observation windows', () => {
  for (const entry of routes) {
    const page = html(entry.route)
    assert.ok(!page.includes('foc-sources'))
    assert.ok(!page.includes('Observation windows'))
  }
})

test('orchestrator pages show payment activity by token and distinct clients', () => {
  for (const entry of routes.filter(r => r.kind === 'address')) {
    const data = readFoc(entry.file)
    const activity = data.orchestrator_activity
    const page = html(entry.route)
    if (!activity?.daily?.length) {
      if (data.orchestrator) assert.ok(page.includes('No attributed settlements.'))
      continue
    }
    assert.ok(page.includes('Paying clients'))
    assert.ok(activity.daily.every(d => Number.isInteger(d.payers) && d.payers >= 0))
    for (const token of activity.tokens) {
      for (const day of token.daily) assert.match(day.amount, /^\d+$/)
      if (token.decimals != null) assert.ok(page.includes(`Payment volume (${token.symbol})`))
    }
  }
})

test('orchestrator pages chart exact daily rewards as FIL flows', () => {
  const totals = readFoc('solstice.json').rewards
  for (const entry of routes.filter(r => r.kind === 'address')) {
    const data = readFoc(entry.file)
    if (!data.reward_daily?.length) continue
    const page = html(entry.route)
    for (const title of ['Earned rewards', 'Claimed rewards']) assert.ok(page.includes(title))
    for (const key of ['earned', 'claimed']) {
      for (const day of data.reward_daily) assert.match(day[key], /^\d+$/)
      const expected = totals.filter(r => r.orchestrator === data.address || (!r.orchestrator && r.wallet === data.address))
        .reduce((n, r) => n + BigInt(r[key]), 0n)
      assert.equal(data.reward_daily.reduce((n, r) => n + BigInt(r[key]), 0n), expected)
    }
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
  for (const row of data.rewards) {
    assert.match(row.earned, /^\d+$/)
    assert.match(row.claimed, /^\d+$/)
  }
  const rewards = html('solstice').match(/<section[^>]*id="rewards"[\s\S]*?<\/section>/)?.[0]
  assert.ok(rewards)
  for (const heading of ['Orchestrator ID', 'Earned', 'Claimed']) assert.ok(rewards.includes(`>${heading}</th>`))
  assert.equal(rewards.includes('>Wallet</th>'), data.rewards.some(r => r.wallet !== r.orchestrator))
  for (const row of data.rewards.filter(r => r.orchestrator)) assert.ok(rewards.includes(`>${row.orchestrator}</a>`))
})

test('entity daily states reconcile with network totals at the last FEVM checkpoint', () => {
  const end = readFoc('coverage.json').find(row => row.source === 'fevm').end
  const { series } = readFoc('overview.json'), i = series.date.indexOf(end)
  assert.ok(i >= 0)
  const latest = (s, key) => s?.d?.length && s.d[0] <= end ? Number(s[key].findLast((_, j) => s.d[j] <= end)) : 0
  const at = (s, key) => s?.d?.includes(end) ? Number(s[key][s.d.indexOf(end)]) : 0
  let stored = 0, billing = 0
  for (const entry of routes.filter(r => r.kind === 'provider')) stored += latest(readFoc(entry.file).storage, 'bytes')
  for (const entry of routes.filter(r => r.kind === 'address')) billing += at(readFoc(entry.file).billing_daily, 'v')
  assert.equal(stored, series.stored_bytes[i])
  assert.equal(billing, series.billing_data_sets[i])
})

test('entity series keep exact strings, tokens and observed coverage', () => {
  const end = readFoc('coverage.json').find(row => row.source === 'fevm').end
  const values = (page, key) => JSON.parse(page.match(new RegExp(`data-key="${key}"[^>]*data-start="([^"]+)" data-values="([^"]+)"`))[2].replaceAll('&quot;', '"'))
  for (const entry of routes.filter(r => r.kind === 'rail')) {
    const data = readFoc(entry.file)
    for (const v of data.rate?.v ?? []) assert.match(v, /^\d+$/)
    if (data.rate?.d) assert.ok(data.rate.d.at(-1) <= end)
  }
  // Native FIL rails share one token rule; unknown event amounts never read as zero.
  for (const entry of routes.filter(r => r.kind === 'rail')) {
    const data = readFoc(entry.file)
    if (data.rail.token === '0x0000000000000000000000000000000000000000') assert.equal(data.rail.token_symbol, 'FIL', entry.route)
    if (data.rate_token) assert.equal(data.rate_token.symbol, data.rail.token_symbol, entry.route)
    if (data.net_daily?.v?.length && !data.net_daily.v.some(v => v != null)) {
      const page = html(entry.route), net = page.match(/<h3>Net to payee<\/h3><span class="chart-value">([\s\S]*?)<\/span><\/div>/)
      assert.ok(net?.[1].includes('Not observed') && page.includes('no recorded amount'), entry.route)
      if (data.rail.token_symbol === 'FIL') assert.doesNotMatch(page, /unidentified token|unknown token/, entry.route)
    }
  }
  // A deleted data set reads zero after deletion, through the last checkpoint.
  const deleted = readFoc('ds/1293.json').storage
  assert.equal(deleted.bytes.at(-1), 0)
  const datasetPage = html('dataset/1293')
  const stored = values(datasetPage, 'stored_bytes')
  assert.equal(stored.at(-1), 0)
  // Daily states connect observations directly; flows retain their daily bar encoding.
  for (const key of ['stored_bytes', 'stored_pieces', 'rate_month_usd']) {
    assert.match(datasetPage, new RegExp(`data-key="${key}" data-kind="line"`))
  }
  assert.match(datasetPage, /data-kind="bar" data-label="Data added and removed"/)
  for (const entry of routes.filter(r => r.kind === 'address')) {
    for (const t of readFoc(entry.file).payer_rates ?? []) {
      for (const v of t.v) assert.match(v, /^\d+$/)
      assert.equal(new Set((readFoc(entry.file).payer_rates).map(x => x.token)).size, readFoc(entry.file).payer_rates.length)
    }
  }
})
