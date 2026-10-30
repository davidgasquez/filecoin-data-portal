// Run after `npm run build`; checks docs, about, agent files, and build-origin links.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile, access } from 'node:fs/promises'
import { resolve } from 'node:path'

const root = resolve(process.env.SITE_DIST ?? 'dist')
const dist = (path) => readFile(resolve(root, path), 'utf8')
const site = new URL(process.env.SITE_URL || 'https://filecoindataportal.xyz').origin
const archive = process.env.ARCHIVE_URL || 'https://old.filecoindataportal.xyz'
const [home, docs, about, skill, llms] = await Promise.all(['index.html', 'docs/index.html', 'about/index.html', 'SKILL.md', 'llms.txt'].map(dist))
const footer = (html) => html.match(/<footer\b[\s\S]*?<\/footer>/)?.[0] ?? ''
const escape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

test('/docs replaces /guide everywhere in the main site', async () => {
  await assert.rejects(access(resolve(root, 'guide/index.html')))
  for (const html of [home, docs, about]) {
    assert.doesNotMatch(html, /href="\/guide"/)
    assert.match(html, /<nav class="site-nav"[\s\S]*?<a href="\/docs"[^>]*>Docs<\/a>/)
  }
  assert.match(home, /<h3[^>]+id="sql"[^>]*><a[^>]+href="\/docs"[^>]*>Query it yourself<\/a><\/h3>/)
})

test('docs keep caveats and add Python, JavaScript, and whole-database examples', () => {
  assert.match(docs, /<h1>Docs<\/h1>/)
  for (const label of ['DuckDB example', 'Python example', 'JavaScript example', 'Whole database example', 'Agent prompt']) assert.match(docs, new RegExp(`aria-label="${label}"`))
  assert.match(docs, /pl\.read_parquet/)
  assert.match(docs, /daily_network_metrics\.json/)
  assert.match(docs, /attach &#39;https:\/\/data\.filecoindataportal\.xyz\/fdp\.duckdb&#39; as fdp \(read_only\)|attach 'https:\/\/data\.filecoindataportal\.xyz\/fdp\.duckdb' as fdp \(read_only\)/)
  assert.match(docs, /UTC yesterday/)
  assert.match(docs, /Null means unavailable or undefined, not zero/)
  assert.match(docs, /href="https:\/\/github\.com\/davidgasquez\/filecoin-data-portal\/blob\/main\/docs\/data-sources\.md"/)
})

test('about keeps maintainer, funding, scoped licenses, and the archive link', () => {
  assert.match(about, /<h1>About<\/h1>/)
  assert.match(about, /href="https:\/\/davidgasquez\.com\/"[^>]*>David Gasquez<\/a>/)
  assert.match(about, /Protocol Labs blue funds/)
  assert.match(about, /Filecoin Retroactive Public Goods Funding/)
  assert.match(about, /datasets[^<]*<a href="https:\/\/creativecommons\.org\/public-domain\/cc0\/"/)
  assert.match(about, /code[^<]*<a href="https:\/\/github\.com\/davidgasquez\/filecoin-data-portal\/blob\/main\/LICENSE"[^>]*>MIT license<\/a>/)
  assert.match(about, /without warranties/)
  assert.match(about, new RegExp(`<a href="${escape(archive)}"`))
  assert.match(about, /frozen archive/)
  assert.doesNotMatch(about, /local experiment/i)
})

test('footer credits the author and keeps secondary links without repeating Docs', () => {
  for (const html of [home, docs, about]) {
    const html_ = footer(html)
    assert.match(html_, /Built by <a[^>]+href="https:\/\/davidgasquez\.com\/"[^>]*>David Gasquez<\/a>/)
    assert.match(html_, /blob\/main\/LICENSE"[^>]*>MIT license<\/a>/)
    assert.doesNotMatch(html_, /href="\/docs"/)
    for (const [href, label] of [['/about', 'About'], ['/llms.txt', 'llms.txt'], [archive, 'Previous site']]) {
      assert.match(html_, new RegExp(`<a href="${escape(href)}"[^>]*>${escape(label)}</a>`))
    }
    assert.match(html_, /href="https:\/\/github\.com\/davidgasquez\/filecoin-data-portal\/issues"/)
    assert.doesNotMatch(html_, /https:\/\/filecoindataportal\.xyz\/llms\.txt/)
  }
})

test('canonical, og:url, prompt, and indexing follow the build origin', () => {
  for (const [html, path] of [[home, '/'], [docs, '/docs'], [about, '/about']]) {
    const url = new URL(path, site).href
    assert.match(html, new RegExp(`<link rel="canonical" href="${escape(url)}"`))
    assert.match(html, new RegExp(`<meta property="og:url" content="${escape(url)}"`))
    assert.equal(/<meta name="robots" content="noindex"/.test(html), site !== 'https://filecoindataportal.xyz')
  }
  const prompt = home.match(/aria-label="Agent prompt"[^>]*><code>([\s\S]*?)<\/code>/)?.[1]
  assert.ok(prompt)
  assert.match(prompt, new RegExp(`Read <a href="${escape(site)}/SKILL\\.md">${escape(site)}/SKILL\\.md</a> and tell me which providers onboarded more data last week`))
  assert.match(home, new RegExp(`data-copy="Read ${escape(site)}/SKILL\\.md and tell me which providers onboarded more data last week"`))
})

test('SKILL.md and llms.txt are authored discovery files linking the Markdown catalog', () => {
  assert.match(skill, /^---\nname: fdp\ndescription: .+\n---\n/)
  assert.doesNotMatch(skill, /\{\{|dataset_catalog/)
  for (const text of [skill, llms]) {
    assert.match(text, /\]\(\/datasets\.md\)/)
    assert.doesNotMatch(text, /\/assets\/[^)\s]+\.md|numbers\.json|\/guide\b/)
  }
  for (const pattern of [/data\.filecoindataportal\.xyz\/<dataset>\.parquet/, /UTC yesterday/, /Null means unknown/, /DECIMAL\(38,0\)/, /1e18/, /issues\/new/]) assert.match(skill, pattern)
  for (const link of ['/SKILL.md', '/datasets.md', '/docs', '/about']) assert.match(llms, new RegExp(`\\]\\(${escape(link)}\\)`))
})
