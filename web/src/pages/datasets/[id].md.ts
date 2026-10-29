import type { APIRoute } from 'astro'
import { datasets, type Dataset } from '../../data'
import { datasetMarkdown } from '../../markdown'

export const getStaticPaths = () => datasets.map((dataset) => ({ params: { id: dataset.id }, props: { dataset } }))

export const GET: APIRoute = ({ props, site, url }) =>
  new Response(datasetMarkdown((props as { dataset: Dataset }).dataset, site ?? url.origin), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } })
