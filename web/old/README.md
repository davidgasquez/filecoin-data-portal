# Filecoin Data Portal archive

Frozen copy of the previous site, without a notice banner. Every page is noindex and links to https://filecoindataportal.xyz in the footer. Snapshot dates and provenance remain in the agent resources.
Pages and data are frozen; Parquet download links still point to `data.filecoindataportal.xyz`, which keeps updating.

## Snapshot

| parameter | value |
|---|---|
| source | `d952d88` web app (what production served), plus archive provenance/noindex/origin changes |
| database | `https://data.filecoindataportal.xyz/fdp.duckdb` as published 2026-10-28 20:16:33 UTC (223,621,120 bytes) |
| sha256 | `e624e3fb2e6549a107ec75ccd1d17fe9f8635f522469d5dad768ddc4f1619e67` |
| `ARCHIVE_DATE` | `2026-10-28` (default in `src/archive.ts`, replaces "today"; observations end 2026-10-27) |

Asset-code and data-source documentation links are pinned to the archived source revision, not the evolving main branch.

The database is a build input only and is never shipped in `dist/`. `FDP_DB` is required so the archive never builds from the live database.

## Build

Run from `web/old` (Node 24 via the root `direnv`):

```bash
direnv exec ../.. npm ci
direnv exec ../.. env FDP_DB=/path/to/fdp.duckdb npm run build   # SITE_URL defaults to https://old.filecoindataportal.xyz
direnv exec ../.. npm test                                       # static checks on dist/
```

Preview build: add `SITE_URL=https://filecoindataportal-old.davidgasquez.workers.dev` to both `build` and `test`.

## Deploy

Worker `filecoindataportal-old`, static assets from `dist/`.

- `npm run deploy`: workers.dev only (`https://filecoindataportal-old.davidgasquez.workers.dev`), no routes.
- `npm run deploy:production`: **explicit approval required**. Requires `FDP_PRODUCTION_DEPLOY=true` and a build canonical to `https://old.filecoindataportal.xyz`; binds that domain to the same Worker. Never the apex.

Both paths require archive noindex headers and reject target/config overrides. Only `--dry-run` may be passed through. The production domain is not authorized during preview review.
