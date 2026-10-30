// Explicit opt-in smoke test against a local Workers runtime or an already deployed candidate.
// FDP_SITE=foc checks the explorer; SITE_URL/FOC_URL name the build's origins.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { EXPLORER, PORTAL, explorer, origin } from '../src/site.mjs'

if (!process.env.BASE_URL) throw new Error('Set BASE_URL to the deployed site or local Workers runtime')
const base = new URL(process.env.BASE_URL).origin
const preview = origin !== (explorer ? EXPLORER : PORTAL)
const get = path => fetch(`${base}${path}`, { redirect: 'manual', signal: AbortSignal.timeout(30_000) })
const pages = explorer
  ? [['/', 'text/html'], ['/providers', 'text/html'], ['/datasets', 'text/html'], ['/rails', 'text/html'], ['/clients', 'text/html'], ['/operators', 'text/html'], ['/solstice', 'text/html'], ['/provider/1', 'text/html'],
      ['/robots.txt', 'text/plain'], ['/sitemap.xml', 'application/xml']]
  : [['/', 'text/html'], ['/numbers', 'text/html'],
      ['/datasets', 'text/html'], ['/datasets/daily_network_metrics', 'text/html'], ['/docs', 'text/html'], ['/about', 'text/html'],
      ['/SKILL.md', 'text/markdown'], ['/datasets.md', 'text/markdown'], ['/datasets/daily_network_metrics.md', 'text/markdown'],
      ['/llms.txt', 'text/plain'], ['/robots.txt', 'text/plain'], ['/sitemap.xml', 'application/xml'], ['/numbers-history.json', 'application/json']]
const missing = explorer
  ? ['/not-a-route', '/provider/99999999999999', '/foc', '/foc/providers', '/numbers', '/SKILL.md', '/llms.txt', '/datasets/daily_network_metrics']
  : ['/not-a-portal-route', '/foc', '/foc/providers', '/providers', '/numbers.json', '/assets/daily_network_metrics.md', '/datasets/no-such-table.md', '/missing.md', '/guide']

test('public HTML, machine-readable resources and static history have correct responses', async () => {
  for (const [path, mime] of pages) {
    const response = await get(path)
    assert.equal(response.status, 200, path)
    assert.ok(response.headers.get('content-type')?.startsWith(mime), `${path}: ${response.headers.get('content-type')}`)
    assert.equal(response.headers.get('access-control-allow-origin'), '*', path)
    assert.equal(response.headers.get('x-robots-tag')?.includes('noindex') ?? false, preview, path)
    const body = await response.text()
    assert.ok(body.length > 0, path)
    if (path === '/') {
      assert.ok(body.includes(`rel="canonical" href="${origin}/"`))
      if (!explorer) assert.ok(body.includes(`${origin}/SKILL.md`))
      const css = body.match(/href="(\/_astro\/[^"?]+\.css)"/)?.[1]
      assert.ok(css, 'self-hosted stylesheet')
      const asset = await get(css)
      assert.equal(asset.status, 200)
      assert.match(asset.headers.get('cache-control'), /max-age=31536000.*immutable/)
      await asset.arrayBuffer()
    }
  }
})

test('clean URL redirects preserve query state, and removed/unknown routes are real 404s', async () => {
  const page = explorer ? '/providers' : '/numbers', query = explorer ? '?sort=-provider' : '?range=all'
  for (const path of [`${page}/${query}`, `${page}/index.html${query}`]) {
    const response = await get(path)
    assert.ok([301, 302, 307, 308].includes(response.status), `${path}: ${response.status}`)
    const target = new URL(response.headers.get('location'), base)
    assert.equal(target.pathname, page)
    assert.equal(target.search, query)
    await response.arrayBuffer()
  }
  for (const path of missing) {
    const response = await get(path)
    assert.equal(response.status, 404, path)
    assert.ok(response.headers.get('content-type')?.startsWith('text/html'), path)
    assert.match(await response.text(), /<html/)
  }
})
