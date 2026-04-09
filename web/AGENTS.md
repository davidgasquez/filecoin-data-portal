# Web Guidelines

- Fully static site served via Cloudflare Workers.
- Use semantic HTML and keep things vanilla when possible. No react or other frameworks.
- Use modern CSS.
- Keep accesibility in mind.
- Only hydrate where needed (Astro islands).
- Keep things fast. Load only required data, render charts appropiately, ...
- Follow a neo-brutalist design. Minimal, monochrome, monospace fonts, high contrast, sharp rectangles, utilitarian layout.
- Consult [Astro docs](https://docs.astro.build/llms.txt) when needed.
- Verify after making changes! Run `npx astro check` and `npm run build`, if you made aesthetic changes, make screenshots and check them.
