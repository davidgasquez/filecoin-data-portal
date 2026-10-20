# Cloudflare

The static website uses Workers Static Assets; public datasets use the
`filecoindataportal` R2 bucket. Website deployment is declared in
[`web/wrangler.jsonc`](../web/wrangler.jsonc), with a native custom domain and no
application Worker code. Shared `workers.dev` and preview URLs are disabled.
Account: `fbe814d4a37d3d3d7fcfeec0ab929ff6`. Zone: `d301192e601454a9cf7a87b4cd6ee243`.

## Public access

- No Access applications, IP/user-agent blocks, or Page Rules.
- Bot Fight Mode, JavaScript detection, and AI/crawler blocking are off.
- Cloudflare robots policy injection is off; the website's `robots.txt` allows all crawlers.
- Browser Integrity Check is off zone-wide. No per-host exceptions are needed.
- R2 custom-domain and `r2.dev` public reads are enabled. Writes require credentials.
- Public website responses allow cross-origin reads (`Access-Control-Allow-Origin: *`).
- R2 CORS allows any origin and request header for GET/HEAD; exposes ETag,
  Accept-Ranges, Content-Range, and Content-Encoding; preflight TTL is one hour.

Browser Integrity Check can reject ordinary Python urllib clients with `1010`.
Verify using actual `urllib.request.urlopen()` calls to both hosts, without
custom user agents. Also check DuckDB remote queries, CORS, and byte ranges.
All Markdown documents, including `/SKILL.md` and `/assets/*.md`, are published
unchanged with `Content-Type: text/plain; charset=utf-8` for every client.

For [#301](https://github.com/davidgasquez/filecoin-data-portal/issues/301), Pages
continued returning `1010` after disabling Browser Integrity Check. The same
static build passed on a native Worker custom domain, so production now uses that
delivery path. The old Pages project is retained without the custom domain for
rollback. Temporary diagnostic Workers and exception rules were removed.

## Delivery

- Zone Browser Cache TTL: Respect Existing Headers (`0`).
- Always Use HTTPS: on. Minimum TLS: 1.2. SSL mode: Full (strict).
- Website HTML/docs: `public, max-age=0, must-revalidate`.
- Hashed `/_astro/*` assets: `public, max-age=31536000, immutable`.
- Cache rule for `data.filecoindataportal.xyz` JSON/Parquet: eligible for cache,
  two-hour edge TTL, browser revalidation. Do not cache error responses.
- Response header rule for successful dataset JSON responses: `Content-Type: application/json`.
- Production dataset links use the custom domain.

The website workflow deploys with `wrangler deploy --config web/wrangler.jsonc`.
It uses the GitHub Actions secret `CLOUDFLARE_WORKERS_API_TOKEN`, which needs Workers
Scripts Edit and Workers Routes Edit permissions for this account/zone. The
pipeline uses the separate `CLOUDFLARE_API_TOKEN` secret for cache purges.

`fdp publish r2` requires a Cloudflare API token with Cache Purge permission and
`CLOUDFLARE_ZONE_ID`. It invalidates all cache variants on the dataset hostname
after uploading. The daily pipeline supplies these variables and only triggers
the website build after publishing succeeds.

Verify with repeated GETs: datasets and CSS/fonts should transition from MISS to
HIT, and mutable website content should require browser revalidation. Check CORS
with an Origin header and Parquet ranges with `Range: bytes=0-3` (206 response).
