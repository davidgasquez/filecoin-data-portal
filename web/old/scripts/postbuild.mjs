// Preserve the archive's plain-text Markdown MIME, without mislabelling HTML 404s.
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'

const dist = new URL('../dist/', import.meta.url)
let headers = readFileSync(new URL('../public/_headers', import.meta.url), 'utf8')
for (const path of readdirSync(dist, { recursive: true }).filter(path => path.endsWith('.md')).sort()) {
  headers += `\n/${path}\n  Content-Type: text/plain; charset=utf-8\n`
}
writeFileSync(new URL('_headers', dist), headers)
