import type { APIRoute } from 'astro'
import { datasets } from '../data'
import { routes } from '../foc/data'

// Canonical HTML pages only: no JSON, Markdown, 404, or archive paths. FOC comes from the same
// route list that pre-renders its pages, so every listed entity page exists in the build.
const pages = [
  '/', '/numbers', '/datasets', '/docs', '/about',
  ...datasets.map(({ id }) => `/datasets/${encodeURIComponent(id)}`),
  ...routes.map(({ route }) => route ? `/foc/${route}` : '/foc'),
]
const xml = (value: string) => value.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`)

export const GET: APIRoute = ({ site, url }) => new Response(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...new Set(pages)].map((page) => `<url><loc>${xml(new URL(page, site ?? url.origin).href)}</loc></url>`).join('\n')}
</urlset>
`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } })
