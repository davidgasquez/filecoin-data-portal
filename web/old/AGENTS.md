# Archive Guidelines

- Frozen copy of the previous filecoindataportal.xyz site (source as deployed at `d952d88`), served from `old.filecoindataportal.xyz`.
- Independent static Astro app: own `package.json`, lockfile, and config. Never import from `../src` or rely on `../node_modules`.
- Not part of the daily workflow. Rebuild and deploy manually, only from the archived snapshot recorded in `README.md`.
- Keep the original code, routes (`/numbers.json`, `/assets/<dataset>.md`, ...), and design. Only archive notice, noindex, and origin fixes are allowed.
- Always noindex (meta tag, `X-Robots-Tag`, robots.txt without sitemap).
- Run commands from `web/old` with Node from the repository root: `direnv exec ../.. npm run build`.
