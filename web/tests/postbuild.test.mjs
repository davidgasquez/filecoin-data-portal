import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, truncateSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'

test('postbuild scopes Markdown MIME to real paths, regenerates indexing rules, and gates asset size', () => {
  const root = mkdtempSync(join(tmpdir(), 'fdp-postbuild-test-'))
  try {
    for (const path of ['scripts', 'public', 'dist/datasets']) mkdirSync(join(root, path), { recursive: true })
    writeFileSync(join(root, 'scripts/postbuild.mjs'), readFileSync(new URL('../scripts/postbuild.mjs', import.meta.url)))
    writeFileSync(join(root, 'public/_headers'), readFileSync(new URL('../public/_headers', import.meta.url)))
    for (const file of ['SKILL.md', 'datasets.md', 'datasets/example.md', 'sitemap.xml']) writeFileSync(join(root, 'dist', file), 'fixture')
    const read = file => readFileSync(join(root, 'dist', file), 'utf8')
    const build = origin => spawnSync(process.execPath, [join(root, 'scripts/postbuild.mjs')], {
      encoding: 'utf8', env: { ...process.env, SITE_URL: origin },
    })
    const preview = build('https://preview.example')
    assert.equal(preview.status, 0, preview.stderr)
    for (const path of ['/SKILL.md', '/datasets.md', '/datasets/example.md']) assert.ok(read('_headers').includes(path + '\n  Content-Type: text/markdown; charset=utf-8'))
    assert.ok(!read('_headers').includes('/*.md'))
    assert.match(read('_headers'), /X-Robots-Tag: noindex/)
    assert.doesNotMatch(read('robots.txt'), /Sitemap:/)
    const production = build('https://filecoindataportal.xyz')
    assert.equal(production.status, 0, production.stderr)
    assert.doesNotMatch(read('_headers'), /noindex/)
    assert.match(read('robots.txt'), /Sitemap: https:\/\/filecoindataportal.xyz\/sitemap.xml/)
    const large = join(root, 'dist/large.bin')
    writeFileSync(large, '')
    truncateSync(large, 25 * 1024 ** 2 + 1)
    const rejected = build('https://preview.example')
    assert.notEqual(rejected.status, 0)
    assert.match(rejected.stderr, /exceeds 25 MiB/)
  } finally { rmSync(root, { recursive: true, force: true }) }
})
