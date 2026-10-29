import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, delimiter } from 'node:path'
import { spawnSync } from 'node:child_process'

// Exercise the actual CLI gate with a harmless stub. No network or real Wrangler invocation.
function run(args, { origin = 'https://filecoindataportal-preview.davidgasquez.workers.dev', noindex = true, approved = '' } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'fdp-deploy-test-'))
  try {
    for (const dir of ['scripts', 'dist', 'bin']) mkdirSync(join(root, dir))
    writeFileSync(join(root, 'scripts/deploy.mjs'), readFileSync(new URL('../scripts/deploy.mjs', import.meta.url)))
    writeFileSync(join(root, 'dist/index.html'), `<link rel="canonical" href="${origin}/">`)
    writeFileSync(join(root, 'dist/_headers'), noindex ? '/*\n  X-Robots-Tag: noindex\n' : '/*\n')
    const log = join(root, 'invocation.json')
    writeFileSync(join(root, 'bin/wrangler'), '#!/usr/bin/env node\nrequire("node:fs").writeFileSync(process.env.CALL_LOG, JSON.stringify(process.argv.slice(2)))\n', { mode: 0o700 })
    const result = spawnSync(process.execPath, [join(root, 'scripts/deploy.mjs'), ...args], {
      encoding: 'utf8', env: { ...process.env, PATH: `${join(root, 'bin')}${delimiter}${process.env.PATH}`, CALL_LOG: log, FDP_PRODUCTION_DEPLOY: approved },
    })
    return { status: result.status, error: result.stderr, invocation: existsSync(log) ? JSON.parse(readFileSync(log, 'utf8')) : null }
  } finally { rmSync(root, { recursive: true, force: true }) }
}

test('default deploy and dry run select only the isolated preview', () => {
  assert.deepEqual(run([]).invocation, ['deploy', '--env', ''])
  assert.deepEqual(run(['preview', '--dry-run']).invocation, ['deploy', '--env', '', '--dry-run'])
  assert.equal(run(['preview'], { origin: 'https://filecoindataportal.xyz' }).invocation, null)
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
  const production = { approved: 'true', origin: 'https://filecoindataportal.xyz', noindex: false }
  assert.deepEqual(run(['production', '--dry-run'], production).invocation, ['deploy', '--env', 'production', '--dry-run'])
  assert.equal(run(['production'], { ...production, noindex: true }).invocation, null)
  assert.equal(run(['production'], { ...production, approved: '' }).invocation, null)
})
