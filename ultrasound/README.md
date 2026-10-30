# Ultra Sound Storage

A single-file Filecoin storage dashboard at **https://ultrasoundstorage.filecoindataportal.xyz**. No runtime API, backend, or framework; CSS, fonts, charts, and data are embedded in the page.

## Update

The daily [Pipeline](../.github/workflows/pipeline.yml) (14:00 UTC) rebuilds and deploys it after successful publication on `main`. Code changes go live on the next successful run; dispatch Pipeline manually for an earlier update. POC failures warn in Actions and retain the previous page without blocking the main portal.

The build reads the **full materialized `fdp.duckdb`**, including `raw` and `model`. The public download only contains `main` and is insufficient. Daily series stop at UTC yesterday; source lag is preserved, not filled with invented observations. The page shows build/source dates and warns when a daily source is more than three days old.

```sh
npm ci --prefix ultrasound
npm test --prefix ultrasound
npm run build --prefix ultrasound
# Optional: FDP_DB=/path/to/full/fdp.duckdb npm run build --prefix ultrasound
```

Open `ultrasound/dist/index.html` directly. No local server is necessary.

## Deploy

```sh
npm exec --prefix ultrasound -- wrangler login
npm run deploy --prefix ultrasound
```

The assets-only Worker has its own custom domain, isolated from the main portal. Cloudflare provisions DNS and TLS on the first deployment; resolve any conflicting record first. CI uses the existing `CLOUDFLARE_WORKERS_API_TOKEN` secret, which must permit this Worker and its custom domain. If it cannot create the domain, perform the first deploy locally with an authorized account, then verify CI deployment permissions.

## Files

- `template.html`: the original prototype, with data and no-JavaScript summary placeholders.
- `extract.mjs` / `dealbot.sql`: read-only queries recovered from the prototype; daily inputs are filtered before querying.
- `build.mjs`: columnar payload, validation, and HTML generation.
- `wrangler.jsonc`: static hosting configuration.

This directory is now the source of truth; edits to the original sibling `ultra-sound-storage/` directory are not synced. The prototype embeds Inter and Roboto Mono fonts (SIL OFL).
