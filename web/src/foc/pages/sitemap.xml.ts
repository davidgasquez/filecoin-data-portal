import type { APIRoute } from 'astro'
import { routes } from '../data.ts'
import { url } from '../ui.ts'

// Every pre-rendered explorer page, from the same route list that renders them.
const xml = (value: string) => value.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`)

export const GET: APIRoute = ({ site, url: request }) => new Response(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${routes.map(({ route }) => `<url><loc>${xml(new URL(url(route), site ?? request.origin).href)}</loc></url>`).join('\n')}
</urlset>
`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } })
