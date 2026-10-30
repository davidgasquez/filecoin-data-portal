// Derive origin-specific static files after `astro build` for the selected FDP_SITE target. Idempotent:
// always regenerated from public/. Non-production origins (previews) get X-Robots-Tag: noindex and no
// sitemap; production never inherits it.
import { existsSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { explorer, origin, outDir, production } from '../src/site.mjs'

const dist = new URL(`../${outDir}/`, import.meta.url)
// The portal's agent files use portal-relative links; the explorer does not publish them.
if (explorer) for (const file of ['SKILL.md', 'llms.txt']) rmSync(new URL(file, dist), { force: true })

let headers = readFileSync(new URL('../public/_headers', import.meta.url), 'utf8')
if (!production) headers = headers.replace(/^\/\*\n/m, '/*\n  X-Robots-Tag: noindex\n')
// Exact existing paths only: a missing .md URL must retain its HTML 404 content type.
for (const path of readdirSync(dist, { recursive: true }).filter(path => path.endsWith('.md')).sort()) {
  headers += `\n/${path}\n  Content-Type: text/markdown; charset=utf-8\n`
}
writeFileSync(new URL('_headers', dist), headers)

const sitemap = production && existsSync(new URL('sitemap.xml', dist)) ? `\nSitemap: ${origin}/sitemap.xml\n` : ''
writeFileSync(new URL('robots.txt', dist), `User-agent: *\nAllow: /\n${sitemap}`)
// Conservative Workers Free limits; review the account plan before raising the file cap.
const files = readdirSync(dist, { recursive: true, withFileTypes: true }).filter(file => file.isFile())
if (files.length > 20_000) throw new Error(`Static asset limit exceeded: ${files.length} files > 20,000`)
for (const file of files) {
  const path = join(file.parentPath, file.name)
  if (statSync(path).size > 25 * 1024 ** 2) throw new Error(`Static asset exceeds 25 MiB: ${path}`)
}
console.log(`postbuild: ${outDir} for ${origin} (${production ? 'production, indexable' : 'preview, noindex'}), ${files.length} assets within size/count limits`)
