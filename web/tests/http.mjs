// Explicit opt-in smoke test against a local Workers runtime or an already deployed candidate.
import { test } from 'node:test'
import assert from 'node:assert/strict'

if (!process.env.BASE_URL) throw new Error('Set BASE_URL to the deployed site or local Workers runtime')
const base = new URL(process.env.BASE_URL).origin
const site = new URL(process.env.SITE_URL ?? base).origin
const preview = site !== 'https://filecoindataportal.xyz'
const get = path => fetch(`${base}${path}`, { redirect: 'manual', signal: AbortSignal.timeout(30_000) })

test('public HTML, machine-readable resources and static history have correct responses', async () => {
  for (const [path, mime] of [
    ['/', 'text/html'], ['/numbers', 'text/html'], ['/foc', 'text/html'], ['/foc/providers', 'text/html'],
    ['/datasets', 'text/html'], ['/datasets/daily_network_metrics', 'text/html'], ['/docs', 'text/html'], ['/about', 'text/html'],
    ['/SKILL.md', 'text/markdown'], ['/datasets.md', 'text/markdown'], ['/datasets/daily_network_metrics.md', 'text/markdown'],
    ['/llms.txt', 'text/plain'], ['/robots.txt', 'text/plain'], ['/sitemap.xml', 'application/xml'], ['/numbers-history.json', 'application/json'],
  ]) {
    const response = await get(path)
    assert.equal(response.status, 200, path)
    assert.ok(response.headers.get('content-type')?.startsWith(mime), `${path}: ${response.headers.get('content-type')}`)
    assert.equal(response.headers.get('access-control-allow-origin'), '*', path)
    assert.equal(response.headers.get('x-robots-tag')?.includes('noindex') ?? false, preview, path)
    const body = await response.text()
    assert.ok(body.length > 0, path)
    if (path === '/') {
      assert.ok(body.includes(`rel="canonical" href="${site}/"`))
      assert.ok(body.includes(`${site}/SKILL.md`))
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
  for (const path of ['/numbers/?range=all', '/numbers/index.html?range=all']) {
    const response = await get(path)
    assert.ok([301, 302, 307, 308].includes(response.status), `${path}: ${response.status}`)
    const target = new URL(response.headers.get('location'), base)
    assert.equal(target.pathname, '/numbers')
    assert.equal(target.search, '?range=all')
    await response.arrayBuffer()
  }
  for (const path of ['/not-a-portal-route', '/foc/provider/99999999999999', '/numbers.json', '/assets/daily_network_metrics.md', '/datasets/no-such-table.md', '/missing.md', '/guide']) {
    const response = await get(path)
    assert.equal(response.status, 404, path)
    assert.ok(response.headers.get('content-type')?.startsWith('text/html'), path)
    assert.match(await response.text(), /<html/)
  }
})
