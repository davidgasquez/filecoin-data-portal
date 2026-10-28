# Web Guidelines

- Fully static site served via Cloudflare Workers Static Assets.
- Use semantic HTML and keep things vanilla when possible. No react or other frameworks.
- Use modern CSS.
- Keep accesibility in mind.
- Only hydrate where needed (Astro islands).
- Keep things fast. Load only required data, render charts appropiately, ...
- Follow a neo-brutalist design. Minimal, monochrome, monospace fonts, high contrast, sharp rectangles, utilitarian layout.
- Workflow: `npm run dev`, `npm run build`, `npm run preview` (Cloudflare runtime), `npm run deploy`.
- Use `FDP_DB=../fdp.duckdb npm run dev` to preview local tables.
