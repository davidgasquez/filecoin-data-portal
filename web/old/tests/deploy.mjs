import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, delimiter } from 'node:path'
import { spawnSync } from 'node:child_process'

// Stub Wrangler; these tests never make network requests or deploy anything.
test('archive domain publication requires opt-in, correct origin, noindex, and no target overrides', () => {
  const preview = 'https://filecoindataportal-old.davidgasquez.workers.dev'
  const production = 'https://old.filecoindataportal.xyz'
  for (const [target, origin, approved, noindex, extra, allowed] of [
    ['preview', preview, '', true, [], true],
    ['production', production, '', true, [], false],
    ['production', production, 'true', true, [], true],
    ['production', preview, 'true', true, [], false],
    ['preview', production, '', true, [], false],
    ['preview', preview, '', false, [], false],
    ['preview', preview, '', true, ['--env', 'production'], false],
    ['preview', preview, '', true, ['--name', 'filecoindataportal'], false],
  ]) {
    const root = mkdtempSync(join(tmpdir(), 'fdp-archive-deploy-test-'))
    try {
      for (const dir of ['scripts', 'dist', 'bin']) mkdirSync(join(root, dir))
      writeFileSync(join(root, 'scripts/deploy.mjs'), readFileSync(new URL('../scripts/deploy.mjs', import.meta.url)))
      writeFileSync(join(root, 'dist/index.html'), `<link rel="canonical" href="${origin}/">`)
      writeFileSync(join(root, 'dist/_headers'), noindex ? '/*\n  X-Robots-Tag: noindex' : '/*')
      const log = join(root, 'called.json')
      writeFileSync(join(root, 'bin/wrangler'), '#!/usr/bin/env node\nrequire("node:fs").writeFileSync(process.env.CALL_LOG, JSON.stringify(process.argv.slice(2)))\n', { mode: 0o700 })
      const result = spawnSync(process.execPath, [join(root, 'scripts/deploy.mjs'), target, '--dry-run', ...extra], {
        encoding: 'utf8', env: { ...process.env, PATH: `${join(root, 'bin')}${delimiter}${process.env.PATH}`, CALL_LOG: log, FDP_PRODUCTION_DEPLOY: approved },
      })
      assert.equal(result.status, allowed ? 0 : 1, result.stderr)
      assert.equal(existsSync(log), allowed)
      if (allowed) assert.deepEqual(JSON.parse(readFileSync(log, 'utf8')), ['deploy', '--env', target === 'production' ? 'production' : '', '--dry-run'])
    } finally { rmSync(root, { recursive: true, force: true }) }
  }
})
