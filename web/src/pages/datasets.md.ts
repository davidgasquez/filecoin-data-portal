import type { APIRoute } from 'astro'
import { datasets } from '../data'
import { catalogMarkdown } from '../markdown'

export const GET: APIRoute = ({ site, url }) =>
  new Response(catalogMarkdown(datasets, site ?? url.origin), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } })
