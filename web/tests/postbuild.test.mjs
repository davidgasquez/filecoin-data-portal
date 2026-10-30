import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, truncateSync, rmSync, existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'

function fixture(out, files) {
  const root = mkdtempSync(join(tmpdir(), 'fdp-postbuild-test-'))
  for (const path of ['scripts', 'src', 'public', `${out}/datasets`]) mkdirSync(join(root, path), { recursive: true })
  for (const file of ['scripts/postbuild.mjs', 'src/site.mjs', 'public/_headers']) writeFileSync(join(root, file), readFileSync(new URL(`../${file}`, import.meta.url)))
  for (const file of files) writeFileSync(join(root, out, file), 'fixture')
  const read = file => readFileSync(join(root, out, file), 'utf8')
  const build = (env) => spawnSync(process.execPath, [join(root, 'scripts/postbuild.mjs')], { encoding: 'utf8', env: { ...process.env, SITE_URL: '', FOC_URL: '', FDP_SITE: '', ...env } })
  return { root, read, build }
}

test('postbuild scopes Markdown MIME to real paths, regenerates indexing rules, and gates asset size', () => {
  const { root, read, build } = fixture('dist', ['SKILL.md', 'datasets.md', 'datasets/example.md', 'sitemap.xml'])
  try {
    const preview = build({ SITE_URL: 'https://preview.example' })
    assert.equal(preview.status, 0, preview.stderr)
    for (const path of ['/SKILL.md', '/datasets.md', '/datasets/example.md']) assert.ok(read('_headers').includes(path + '\n  Content-Type: text/markdown; charset=utf-8'))
    assert.ok(!read('_headers').includes('/*.md'))
    assert.match(read('_headers'), /X-Robots-Tag: noindex/)
    assert.doesNotMatch(read('robots.txt'), /Sitemap:/)
    const production = build({ SITE_URL: 'https://filecoindataportal.xyz' })
    assert.equal(production.status, 0, production.stderr)
    assert.doesNotMatch(read('_headers'), /noindex/)
    assert.match(read('robots.txt'), /Sitemap: https:\/\/filecoindataportal.xyz\/sitemap.xml/)
    const large = join(root, 'dist/large.bin')
    writeFileSync(large, '')
    truncateSync(large, 25 * 1024 ** 2 + 1)
    const rejected = build({ SITE_URL: 'https://preview.example' })
    assert.notEqual(rejected.status, 0)
    assert.match(rejected.stderr, /exceeds 25 MiB/)
  } finally { rmSync(root, { recursive: true, force: true }) }
})

test('the explorer target writes its own origin rules and drops the portal agent files', () => {
  const { root, read, build } = fixture('dist-foc', ['SKILL.md', 'llms.txt', 'sitemap.xml'])
  try {
    const production = build({ FDP_SITE: 'foc', SITE_URL: 'https://preview.example' })
    assert.equal(production.status, 0, production.stderr)
    assert.doesNotMatch(read('_headers'), /noindex|text\/markdown/)
    assert.equal(read('robots.txt'), 'User-agent: *\nAllow: /\n\nSitemap: https://foc.filecoindataportal.xyz/sitemap.xml\n')
    for (const file of ['SKILL.md', 'llms.txt']) assert.ok(!existsSync(join(root, 'dist-foc', file)), file)
    const preview = build({ FDP_SITE: 'foc', FOC_URL: 'https://foc-preview.example' })
    assert.equal(preview.status, 0, preview.stderr)
    assert.match(read('_headers'), /X-Robots-Tag: noindex/)
    assert.doesNotMatch(read('robots.txt'), /Sitemap:/)
    assert.notEqual(build({ FDP_SITE: 'other' }).status, 0, 'unknown targets are rejected')
  } finally { rmSync(root, { recursive: true, force: true }) }
})
