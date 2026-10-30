import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, delimiter } from 'node:path'
import { spawnSync } from 'node:child_process'

const PORTAL = { preview: 'https://filecoindataportal-preview.davidgasquez.workers.dev', production: 'https://filecoindataportal.xyz' }
const FOC = { preview: 'https://filecoindataportal-foc-preview.davidgasquez.workers.dev', production: 'https://foc.filecoindataportal.xyz' }

// Exercise the actual CLI gate with a harmless stub. No network or real Wrangler invocation.
// The explorer links the portal; the portal has no explorer link.
function run(args, { site = 'portal', origin = PORTAL.preview, other = null, noindex = true, approved = '', built = site } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'fdp-deploy-test-'))
  const out = built === 'foc' ? 'dist-foc' : 'dist'
  try {
    for (const dir of ['scripts', 'src', out, 'bin']) mkdirSync(join(root, dir))
    for (const file of ['scripts/deploy.mjs', 'src/site.mjs']) writeFileSync(join(root, file), readFileSync(new URL(`../${file}`, import.meta.url)))
    writeFileSync(join(root, out, 'index.html'), `<link rel="canonical" href="${origin}/">${other ? `<a href="${other}/">other</a>` : ''}`)
    writeFileSync(join(root, out, '_headers'), noindex ? '/*\n  X-Robots-Tag: noindex\n' : '/*\n')
    const log = join(root, 'invocation.json')
    writeFileSync(join(root, 'bin/wrangler'), '#!/usr/bin/env node\nrequire("node:fs").writeFileSync(process.env.CALL_LOG, JSON.stringify(process.argv.slice(2)))\n', { mode: 0o700 })
    const result = spawnSync(process.execPath, [join(root, 'scripts/deploy.mjs'), ...args], {
      encoding: 'utf8', env: { ...process.env, PATH: `${join(root, 'bin')}${delimiter}${process.env.PATH}`, CALL_LOG: log, FDP_PRODUCTION_DEPLOY: approved, FDP_SITE: site },
    })
    return { status: result.status, error: result.stderr, invocation: existsSync(log) ? JSON.parse(readFileSync(log, 'utf8')) : null }
  } finally { rmSync(root, { recursive: true, force: true }) }
}

test('CI deploys the explorer before updating the portal', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/website.yml', import.meta.url), 'utf8')
  for (const stage of ['preview', 'production']) {
    assert.ok(workflow.includes(`run: FDP_SITE=foc npm run deploy:${stage} && npm run deploy:${stage}`))
  }
})

test('default deploy and dry run select only the isolated preview', () => {
  assert.deepEqual(run([]).invocation, ['deploy', '--env', ''])
  assert.deepEqual(run(['preview', '--dry-run']).invocation, ['deploy', '--env', '', '--dry-run'])
  assert.equal(run(['preview'], { origin: PORTAL.production }).invocation, null)
  assert.equal(run(['preview'], { noindex: false }).invocation, null)
})

test('target, config, asset and route overrides cannot bypass the deployment gate', () => {
  for (const args of [['--env', 'production'], ['--name', 'filecoindataportal'], ['--config', 'other.json'], ['--assets', 'other'], ['--routes', 'filecoindataportal.xyz/*']]) {
    const result = run(['preview', ...args])
    assert.equal(result.status, 1)
    assert.equal(result.invocation, null)
    assert.match(result.error, /only --dry-run/)
  }
})

test('production requires explicit approval and an indexable production-origin build', () => {
  assert.equal(run(['production']).invocation, null)
  assert.equal(run(['production'], { approved: 'true' }).invocation, null)
  const production = { approved: 'true', origin: PORTAL.production, noindex: false }
  assert.deepEqual(run(['production', '--dry-run'], production).invocation, ['deploy', '--env', 'production', '--dry-run'])
  assert.equal(run(['production'], { ...production, noindex: true }).invocation, null)
  assert.equal(run(['production'], { ...production, approved: '' }).invocation, null)
})

test('the explorer deploys only its own output, origin and Worker environments', () => {
  const preview = { site: 'foc', origin: FOC.preview, other: PORTAL.preview }
  assert.deepEqual(run(['preview', '--dry-run'], preview).invocation, ['deploy', '--env', 'foc-preview', '--dry-run'])
  const production = { site: 'foc', origin: FOC.production, other: PORTAL.production, noindex: false, approved: 'true' }
  assert.deepEqual(run(['production', '--dry-run'], production).invocation, ['deploy', '--env', 'foc-production', '--dry-run'])
  assert.equal(run(['production'], { ...production, approved: '' }).invocation, null)
  // A portal build is not an explorer build, nor the reverse.
  assert.equal(run(['preview'], { ...preview, built: 'portal' }).invocation, null)
  assert.equal(run(['preview'], { ...preview, origin: PORTAL.preview, other: FOC.preview }).invocation, null)
  assert.equal(run(['preview'], { origin: FOC.preview, other: PORTAL.preview }).invocation, null)
})

test('the explorer must link the portal of the same stage', () => {
  const preview = { site: 'foc', origin: FOC.preview }
  assert.equal(run(['preview'], preview).invocation, null)
  assert.match(run(['preview'], preview).error, /does not link/)
  assert.equal(run(['preview'], { ...preview, other: PORTAL.production }).invocation, null)
  assert.equal(run(['production'], { site: 'foc', origin: FOC.production, other: PORTAL.preview, noindex: false, approved: 'true' }).invocation, null)
})
