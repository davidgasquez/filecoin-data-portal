// Static checks for the built archive. Run after `npm run build`: `npm test`.
import assert from "node:assert/strict"
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs"
import { join } from "node:path"
import { test } from "node:test"

const dist = new URL("../dist/", import.meta.url).pathname
const site = (process.env.SITE_URL ?? "https://old.filecoindataportal.xyz").replace(/\/$/, "")
const read = (path) => readFileSync(join(dist, path), "utf8")
const files = (dir = dist) => readdirSync(dir).flatMap((name) => statSync(join(dir, name)).isDirectory() ? files(join(dir, name)) : [join(dir, name).slice(dist.length)])
const pages = ["index", "about", "datasets", "docs", "numbers", "404"]

test("keeps the original routes", () => {
  for (const path of [...pages.map((page) => `${page}.html`), "numbers.json", "SKILL.md", "llms.txt", "sitemap.xml", "robots.txt", "_headers", "favicon.svg", "assets/daily_network_metrics.md", "assets/payments.md"]) {
    assert.ok(existsSync(join(dist, path)), path)
  }
  const datasets = files().filter((path) => /^assets\/.+\.md$/.test(path))
  assert.ok(datasets.length >= 10, `${datasets.length} dataset docs`)
  for (const path of datasets) assert.match(read("SKILL.md"), new RegExp(`\\(${path.replace(".", "\\.")}\\)`))
})

test("ships no database", () => {
  assert.deepEqual(files().filter((path) => /\.(duckdb|wal|parquet)$/.test(path)), [])
})

test("every page is noindex, canonical to the archive origin, and links to the current site", () => {
  for (const page of pages) {
    const html = read(`${page}.html`)
    assert.match(html, /<meta name="robots" content="noindex">/, page)
    const canonical = html.match(/<link rel="canonical" href="([^"]+)"/)[1]
    assert.ok(canonical.startsWith(`${site}/`), `${page}: ${canonical}`)
    assert.doesNotMatch(html, /archive-notice|aria-label="Archive notice"/, page)
    assert.match(html, /<footer[\s\S]*?<a href="https:\/\/filecoindataportal\.xyz">Current site<\/a>/, page)
  }
  assert.match(read("_headers"), /^\/\*\n(?:  .+\n)*  X-Robots-Tag: noindex$/m)
  assert.doesNotMatch(read("robots.txt"), /Sitemap: https:\/\/filecoindataportal\.xyz/)
})

test("archive date and observation date are distinct and honest", () => {
  const [, archived, observed] = read("SKILL.md").match(/frozen on ([\d-]+) with observations through ([\d-]+)/)
  const daily = JSON.parse(read("numbers.json"))
  assert.equal(daily.at(-1).date, observed)
  assert.ok(observed < archived, `${observed} < ${archived}`)
  for (const path of ["SKILL.md", "llms.txt"]) assert.match(read(path), new RegExp(`frozen on ${archived} with observations through ${observed}`), path)
})

test("agent resources point to the archive origin, data downloads stay on the data host", () => {
  for (const path of ["index.html", "numbers.html", "llms.txt", "sitemap.xml"]) {
    const text = read(path)
    assert.doesNotMatch(text, /https:\/\/filecoindataportal\.xyz\/(SKILL\.md|datasets|docs|about|numbers|assets|sitemap)/, path)
  }
  assert.ok(read("index.html").includes(`${site}/SKILL.md`))
  assert.match(read("datasets.html"), /https:\/\/data\.filecoindataportal\.xyz\/[a-z_]+\.parquet/)
  assert.match(read("assets/payments.md"), /dataset url: `https:\/\/data\.filecoindataportal\.xyz\/payments\.parquet`/)
})

test("numbers.json keeps exact atto amounts and UTC timestamps", () => {
  const daily = JSON.parse(read("numbers.json"))
  const atto = Object.keys(daily.at(-1)).filter((key) => key.includes("_atto_"))
  for (const key of atto) for (const row of daily) assert.ok(row[key] == null || typeof row[key] === "string", key)
  assert.doesNotMatch(read("datasets.html"), /\d{2}:\d{2}(:\d{2})?\+0[1-9]</)
})
