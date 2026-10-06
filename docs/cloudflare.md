# Cloudflare

The static website uses Pages; public datasets use the `filecoindataportal` R2 bucket.
Account: `fbe814d4a37d3d3d7fcfeec0ab929ff6`. Zone: `d301192e601454a9cf7a87b4cd6ee243`.

- Zone Browser Cache TTL: Respect Existing Headers (`0`).
- Always Use HTTPS: on. Minimum TLS: 1.2. SSL mode: Full (strict).
- Pages HTML/docs: `public, max-age=0, must-revalidate`.
- Hashed `/_astro/*` assets: `public, max-age=31536000, immutable`.
- Cache rule for `data.filecoindataportal.xyz` JSON/Parquet: eligible for cache,
  two-hour edge TTL, browser revalidation. Do not cache error responses.
- Response header rule for successful dataset JSON responses: `Content-Type: application/json`.
- R2 CORS: any origin, GET/HEAD, any request header; expose ETag, Accept-Ranges,
  Content-Range, and Content-Encoding. Cache preflight responses for one hour.
- Public `r2.dev` access remains enabled; production links use the custom domain.

`fdp publish r2` requires a Cloudflare API token with Cache Purge permission and
`CLOUDFLARE_ZONE_ID`. It invalidates all cache variants on the dataset hostname
after uploading. The daily pipeline supplies these variables and only triggers
the website build after publishing succeeds.

Verify with repeated GETs: datasets and CSS/fonts should transition from MISS to
HIT, and mutable Pages content should require browser revalidation. Check CORS
with an Origin header and Parquet ranges with `Range: bytes=0-3` (206 response).
