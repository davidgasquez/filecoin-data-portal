# Web

Static Astro pages, build-time DuckDB, SVG charts, vanilla CSS, and small progressive-enhancement scripts. No browser database, runtime API, UI framework, or shared package with the independent [previous site](old/README.md).

**Release boundary:** preview deployment is authorized. The apex switch still requires explicit approval; the production CI gate remains unset. Data assets, models, publishing, and `data.filecoindataportal.xyz` are unchanged.

## Develop and check

Use Node 24+ and `uv` from the repository's `direnv` shell:

```sh
cd web
npm ci
export FDP_DB=/absolute/path/to/fdp.duckdb
npm run dev # http://127.0.0.1:4322
```

For local development only, `FDP_DB` defaults to `../fdp.duckdb`. Both adapters read it without writes. Release builds must use one downloaded public snapshot, with the same absolute `FDP_DB` for Node and Python.

`dev`, `check`, and `build` first prepare ignored `.foc/` inputs. The exporter reuses unchanged inputs, keys its cache by source/WAL metadata, exporter content and UTC day, and serializes concurrent exports. Remove `.foc/` to regenerate; restart development after replacing the source database.

```sh
npm run check
npm test
npm run test:foc
npm run build
npm run test:site
npm run preview # serves dist on 4322; stop dev first
```

Static tests take `SITE_URL` and `ARCHIVE_URL` matching the build; `SITE_DIST` can select another output directory. Browser review must also cover desktop/mobile, light/dark, keyboard/touch, copying, range URLs and Back/Forward, entity relationships, and no JavaScript. Inspect actual screenshots, not just automated accessibility results.

## Public surface

- `/`: lineage diagram, query/agent entry points, six dated headlines, dataset discovery.
- `/numbers`: the carried-over metric inventory, related charts, and the full ledger. `/numbers-history.json` is static wider-history data, not a runtime API.
- `/foc`: overview and entity/relationship pages, all pre-rendered. Filtering, sorting, search and paging enhance complete HTML tables.
- `/datasets` and `/datasets/<id>`: description, grain, coverage, sources, schema and samples. Their `.md` counterparts use the same `Dataset` objects and exact values.
- `/docs`, `/about`, authored `/SKILL.md` and `/llms.txt`, and generated `/sitemap.xml`.

`/guide`, `/numbers.json` and `/assets/*.md` are not main-site compatibility endpoints. The old app keeps its own original routes. Numbers preserves legacy chart slugs and column anchors, including onboarding/termination aliases, related measures, provider comparison and Solstice rows.

## Preview and production

| Target | Worker | Publication |
| --- | --- | --- |
| Main preview (default) | `filecoindataportal-preview` | `https://filecoindataportal-preview.davidgasquez.workers.dev` |
| Archive preview | `filecoindataportal-old` | `https://filecoindataportal-old.davidgasquez.workers.dev` |
| Production (approval required) | `filecoindataportal` | Existing apex custom domain and zone route |
| Archive domain (approval required) | `filecoindataportal-old` | `old.filecoindataportal.xyz` |

Build and validate a preview from the public database:

```sh
curl -fL --retry 3 -o /tmp/fdp-public.duckdb https://data.filecoindataportal.xyz/fdp.duckdb
export FDP_DB=/tmp/fdp-public.duckdb
export SITE_URL=https://filecoindataportal-preview.davidgasquez.workers.dev
export ARCHIVE_URL=https://filecoindataportal-old.davidgasquez.workers.dev
npm run check && npm test && npm run test:foc
npm run build && npm run test:site
npm run deploy -- --dry-run
npm run deploy:preview
BASE_URL="$SITE_URL" npm run test:http
```

`build:preview` is a convenience that sets both origins for the build only; export them separately for subsequent static tests. `SITE_URL` defaults to the apex; `ARCHIVE_URL` defaults to the archive domain. The footer and About page make the archive discoverable.

The post-build step regenerates headers and robots rules, applies preview `noindex`, sets Markdown/XML MIME types and hashed-asset caching, and checks conservative Workers limits (20,000 files, 25 MiB per file). Production builds do not inherit preview headers. All targets use clean URLs and real 404s, not SPA fallback.

Bare `npm run deploy` targets only preview. The deploy wrapper rejects target/config/route overrides; only `--dry-run` passes through. Production requires an explicit `deploy:production`, `FDP_PRODUCTION_DEPLOY=true`, and an indexable production-origin build. These are accident guards, not replacements for approval or Cloudflare permissions.

`.github/workflows/website.yml` downloads one snapshot, records its checksum, checks/builds/tests it, and deploys preview only from `portal-migration`. Main pushes and successful main Pipeline runs can deploy production only when repository variable `FDP_PRODUCTION_DEPLOY` is `true`. Archive-only changes do not trigger it; the archive is never rebuilt daily.

### Current data prerequisite

The public snapshot published **2026-10-28 20:16:33 UTC**, SHA-256 `e624e3fb2e6549a107ec75ccd1d17fe9f8635f522469d5dad768ddc4f1619e67`, predates the four `pdp_*` columns added in `7793d6e`. Previews honestly show those metrics as unavailable and explain the missing source columns; they do not borrow local values or invent zero/history. **A production build rejects this incomplete schema.** Recheck the next normally published snapshot before cutover; this website migration does not run or change data publishing.

### Approved cutover checklist

Keep this branch unmerged until a fresh public snapshot passes the production build. A disabled deploy gate does not skip schema validation; merging earlier would make main's Website runs fail safely.

1. Validate a fresh public snapshot and the complete production-origin build, including browser/header/404/deeplink checks. Keep the archive snapshot identified in `old/README.md` frozen.
2. Record the then-current production Worker version and retain candidate artifacts. The daily job may have changed the version since preflight.
3. Publish the archive domain first and verify its notice, noindex, dates, downloads and link back.
4. Deploy to the existing apex Worker without moving its bindings. Smoke-test, then enable normal production CI only after success.
5. Before rollback, pause production CI by clearing its gate. Roll back the same Worker to the recorded version; Worker versions include static assets, not external datasets. Check routes and assets again.

## Data and interface contracts

- UTC yesterday is the latest allowed daily observation. Each metric ends at its own last known date; null is not zero and missing days break history.
- Unique PDP data, registered copies, warm-storage billing populations and raw network power are different measures. Filecoin Pay volume is not storage-only revenue.
- Pool provider numerator/denominator counts; do not average percentages. Zero-attempt rates stay undefined. The latency summary is a median of daily medians, not a pooled request median.
- Stablecoin-at-par aggregates never sum unlike native tokens. Individual rails retain their own tokens; registry zero-address quotes mean FIL. API timestamps/counters remain separate from event-history coverage and paid totals. Incoming address totals and charts use net receipts.
- Exact atto quantities remain strings. Display rounding never rewrites source facts; FIL presentation avoids floating-point subtraction residue.
- High-profile paying clients is explicitly declared zero, not measured history. Its flat line has no invented dates. Complete Days is omitted as a related plot, not from source facts or coverage disclosures.
- Six calendar months is the default chart window; 1y/All fetch wider static history once. Fixed comparisons keep their windows. Failed fetches preserve the previous view and offer retry.
- Daily bars share edges and start at zero. Onboarding/termination retain independent missingness and positive source readouts; termination is drawn below zero, not netted. Ledger reductions preserve extrema and gaps.
- Keep title + Info, latest value, then plot aligned within each full-width wrapping row. Separate neighbors with whitespace, not card boxes or chart-top rules. No ornamental animation.
- Static evidence, disclosures and relationships work without JavaScript. Enhancements add keyboard/touch inspection, URL-addressable state and optional persisted theme.

Design references: [Impeccable](https://github.com/pbakaus/impeccable), [Interface Design](https://github.com/Dammyjay93/interface-design), [Web Interface Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md), and [Tufte](https://github.com/aref-vc/tufte-claude-skill). The accepted monochrome Filecoin interface and `AGENTS.md` take precedence over generic design prescriptions.
