import type { APIRoute } from 'astro'
import { datasets } from '../data'

// Canonical portal HTML pages only: no JSON, Markdown, 404, archive or explorer paths (the explorer has its own).
const pages = [
  '/', '/numbers', '/datasets', '/docs', '/about',
  ...datasets.map(({ id }) => `/datasets/${encodeURIComponent(id)}`),
]
const xml = (value: string) => value.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`)

export const GET: APIRoute = ({ site, url }) => new Response(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...new Set(pages)].map((page) => `<url><loc>${xml(new URL(page, site ?? url.origin).href)}</loc></url>`).join('\n')}
</urlset>
`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } })
