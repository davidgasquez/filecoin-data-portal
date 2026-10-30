// Deploy an already-built target: FDP_SITE selects the portal (dist/, default) or the explorer (dist-foc/).
// `preview` (default) targets that site's isolated workers.dev Worker. `production` targets its custom domain
// and requires FDP_PRODUCTION_DEPLOY=true plus a production build.
// Only --dry-run may pass through: --env/--name/--config could bypass the selected target.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { EXPLORER, PORTAL, explorer, outDir } from '../src/site.mjs'
const PREVIEW = { portal: 'https://filecoindataportal-preview.davidgasquez.workers.dev', foc: 'https://filecoindataportal-foc-preview.davidgasquez.workers.dev' }

const argv = process.argv.slice(2)
const target = argv[0]?.startsWith('-') || !argv.length ? 'preview' : String(argv.shift())
const args = argv
/** @param {string} file */
const read = (file) => readFileSync(new URL(`../${outDir}/${file}`, import.meta.url), 'utf8')
/** @param {string} message @returns {never} */
const fail = (message) => { console.error(`deploy: ${message}`); process.exit(1) }

if (args.some(arg => arg !== '--dry-run')) fail('only --dry-run may be passed through; choose preview or production explicitly')
if (target !== 'preview' && target !== 'production') fail(`unknown target ${target}; use preview or production`)

// The built canonical identifies the target origin. The explorer must also link the portal
// of the same stage; the portal intentionally has no explorer link.
const home = read('index.html')
const canonical = home.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"|<link[^>]*href="([^"]+)"[^>]*rel="canonical"/)
const href = canonical?.[1] ?? canonical?.[2]
if (!href) fail(`${outDir}/index.html has no canonical link; run a build first`)
const origin = new URL(href).origin
const noindex = /X-Robots-Tag: noindex/.test(read('_headers'))
const [own, other] = target === 'production'
  ? (explorer ? [EXPLORER, PORTAL] : [PORTAL, EXPLORER])
  : (explorer ? [PREVIEW.foc, PREVIEW.portal] : [PREVIEW.portal, PREVIEW.foc])

if (target === 'production' && process.env.FDP_PRODUCTION_DEPLOY !== 'true') fail('production deploy requires FDP_PRODUCTION_DEPLOY=true')
if (origin !== own) fail(`${outDir} was built for ${origin}, not ${own}; rebuild ${target === 'preview' ? 'with npm run build:preview' : 'without SITE_URL/FOC_URL'}`)
if (noindex !== (target === 'preview')) fail(`${outDir} ${noindex ? 'is' : 'is not'} noindex; rebuild for ${target}`)
if (explorer && !home.includes(`href="${other}/`)) fail(`${outDir} does not link ${other}; rebuild with matching SITE_URL and FOC_URL`)
args.unshift('--env', explorer ? `foc-${target}` : target === 'production' ? 'production' : '')

console.log(`deploy: ${explorer ? 'explorer' : 'portal'} ${target} from ${origin}`)
const result = spawnSync('wrangler', ['deploy', ...args], { stdio: 'inherit' })
process.exit(result.status ?? 1)
