// Deploy the already-built dist/. `preview` (default) targets the isolated workers.dev Worker.
// `production` targets the apex and requires FDP_PRODUCTION_DEPLOY=true plus a production build.
// Only --dry-run may pass through: --env/--name/--config could bypass the selected target.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const PRODUCTION = 'https://filecoindataportal.xyz'
const PREVIEW = 'https://filecoindataportal-preview.davidgasquez.workers.dev'

const argv = process.argv.slice(2)
const target = argv[0]?.startsWith('-') || !argv.length ? 'preview' : String(argv.shift())
const args = argv
/** @param {string} file */
const read = (file) => readFileSync(new URL(`../dist/${file}`, import.meta.url), 'utf8')
/** @param {string} message @returns {never} */
const fail = (message) => { console.error(`deploy: ${message}`); process.exit(1) }

if (args.some(arg => arg !== '--dry-run')) fail('only --dry-run may be passed through; choose preview or production explicitly')

// The built canonical is the source of truth for which origin dist/ targets.
const canonical = read('index.html').match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"|<link[^>]*href="([^"]+)"[^>]*rel="canonical"/)
const href = canonical?.[1] ?? canonical?.[2]
if (!href) fail('dist/index.html has no canonical link; run a build first')
const origin = new URL(href).origin
const noindex = /X-Robots-Tag: noindex/.test(read('_headers'))

if (target === 'preview') {
  if (origin !== PREVIEW || !noindex) fail(`dist was built for ${origin}; rebuild with npm run build:preview`)
  args.unshift('--env', '')
} else if (target === 'production') {
  if (process.env.FDP_PRODUCTION_DEPLOY !== 'true') fail('production deploy requires FDP_PRODUCTION_DEPLOY=true')
  if (origin !== PRODUCTION || noindex) fail(`dist was built for ${origin}; rebuild without SITE_URL`)
  args.unshift('--env', 'production')
} else fail(`unknown target ${target}; use preview or production`)

console.log(`deploy: ${target} from ${origin}`)
const result = spawnSync('wrangler', ['deploy', ...args], { stdio: 'inherit' })
process.exit(result.status ?? 1)
