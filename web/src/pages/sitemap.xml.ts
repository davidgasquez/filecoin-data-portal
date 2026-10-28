import type { APIRoute } from "astro"

const pages = Object.keys(import.meta.glob("./*.astro"))
  .map((file) => file.slice(2, -6))
  .filter((page) => page !== "404")
  .map((page) => (page === "index" ? "" : page))
  .sort()

export const GET: APIRoute = ({ site }) => new Response(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map((page) => `  <url><loc>${new URL(page, site)}</loc></url>`).join("\n")}
</urlset>
`)
