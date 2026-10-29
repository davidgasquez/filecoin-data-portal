// Independent archive deployment. Domain publication requires explicit approval; default is workers.dev.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'

const [target = 'preview', ...args] = process.argv.slice(2)
const fail = message => { console.error(`archive deploy: ${message}`); process.exit(1) }
if (!['preview', 'production'].includes(target)) fail('choose preview or production')
if (args.some(arg => arg !== '--dry-run')) fail('only --dry-run may be passed through')
const production = target === 'production'
if (production && process.env.FDP_PRODUCTION_DEPLOY !== 'true') fail('domain publication requires explicit approval and FDP_PRODUCTION_DEPLOY=true')
const expected = production ? 'https://old.filecoindataportal.xyz' : 'https://filecoindataportal-old.davidgasquez.workers.dev'
const read = file => readFileSync(new URL(`../dist/${file}`, import.meta.url), 'utf8')
const canonical = read('index.html').match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"|<link[^>]*href="([^"]+)"[^>]*rel="canonical"/)
const href = canonical?.[1] ?? canonical?.[2]
if (!href || new URL(href).origin !== expected) fail(`rebuild with SITE_URL=${expected}`)
if (!/X-Robots-Tag: noindex/.test(read('_headers'))) fail('archive noindex headers are required')
const result = spawnSync('wrangler', ['deploy', '--env', production ? 'production' : '', ...args], { stdio: 'inherit' })
process.exit(result.status ?? 1)
