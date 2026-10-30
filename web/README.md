# Web

Two static Astro sites from one project: the portal and the Filecoin Onchain Cloud explorer. Build-time DuckDB, SVG charts, vanilla CSS, and small progressive-enhancement scripts. No browser database, runtime API, UI framework, or shared package with the independent [previous site](old/README.md).

**Release boundary:** manual production deployments require explicit approval and the guarded commands below. Data publishing is a separate lifecycle; website builds only consume the published snapshot. The archive stays frozen and is never rebuilt by daily CI.

## Develop and check

Use Node 24+ and `uv` from the repository's `direnv` shell:

```sh
cd web
npm ci
export FDP_DB=/absolute/path/to/fdp.duckdb
npm run dev # portal, http://127.0.0.1:4322
npm run dev:foc # explorer, http://127.0.0.1:4323 (may run alongside)
```

`FDP_SITE=foc` selects the explorer target in the one `astro.config.mjs`: pages from `src/foc/pages`, output in `dist-foc/`. The portal (default) uses `src/pages` and `dist/`. Both share layout, styles and modules. The explorer links back to the portal, but the portal currently does not advertise it. Origins: `SITE_URL` (portal, default `https://filecoindataportal.xyz`) and `FOC_URL` (explorer, default `https://foc.filecoindataportal.xyz`). Set both for previews and local servers, e.g. `SITE_URL=http://127.0.0.1:4322 FOC_URL=http://127.0.0.1:4323`.

For local development only, `FDP_DB` defaults to `../fdp.duckdb`. Both adapters read it without writes. Release builds must use one downloaded public snapshot, with the same absolute `FDP_DB` for Node and Python.

`dev`, `check`, and `build` first prepare ignored `.foc/` inputs. The exporter reuses unchanged inputs, keys its cache by source/WAL metadata, exporter content and UTC day, and serializes concurrent exports. Remove `.foc/` to regenerate; restart development after replacing the source database.

```sh
npm run check
npm test
npm run test:foc
npm run build && npm run build:foc
npm run test:site # reads dist/ and dist-foc/
npm run preview # dist on 4322; stop dev first
npm run preview:foc # dist-foc on 4323
```

Astro 7 backgrounds preview when run by an agent. Use `npx astro preview status` / `stop` to manage that server; an existing preview keeps its original port. Pass `--ignore-lock` for a separate foreground preview.

Static tests take `SITE_URL`, `FOC_URL` and `ARCHIVE_URL` matching the builds; `SITE_DIST` can select another portal output directory. Browser review must also cover desktop/mobile, light/dark, keyboard/touch, copying, range URLs and Back/Forward, entity relationships, and no JavaScript. Inspect actual screenshots, not just automated accessibility results.

## Public surface

- `/`: lineage diagram, query/agent entry points, six dated headlines, dataset discovery.
- `/numbers`: the carried-over metric inventory, related charts, and the full ledger. It opens like a report: title, chart history and numbered contents scroll away; the pinned header's Numbers menu reaches every section further down. `/numbers-history.json` is static wider-history data, not a runtime API.
- Filecoin Onchain Cloud explorer (`foc.filecoindataportal.xyz`, its own build): `/` overview, `/providers`, `/datasets` (storage data sets, not the portal catalog), `/rails`, `/clients`, `/operators`, `/solstice`, and entity pages (`/provider/<id>`, `/dataset/<id>`, `/rail/<id>`, `/address/<0x>`), all pre-rendered, with its own sitemap and 404. Its one header replaces the site navigation: the seven explorer sections (inside a menu naming the current section on narrow screens), a "Filecoin Onchain Cloud" menu out to the portal origin, and entity search. Brand, footer, Numbers/Datasets/Docs and source disclosures link the portal. Entity pages mark their list as the parent. Filtering, sorting, search and paging enhance complete HTML tables. Explorer navigation swaps pages without animation; portal links load normally. Marked internal links receive native prefetch hints on hover/focus, not touch or constrained connections. Browsers without hint support navigate normally.
- `/datasets` and `/datasets/<id>`: description, grain, coverage, sources, schema and samples. Their `.md` counterparts use the same `Dataset` objects and exact values.
- `/docs`, `/about`, authored `/SKILL.md` and `/llms.txt` (portal only; the explorer does not publish them), and generated `/sitemap.xml` (portal pages only).

`/guide`, `/numbers.json` and `/assets/*.md` are not main-site compatibility endpoints. The old app keeps its own original routes. Numbers preserves legacy chart slugs and column anchors, including onboarding/termination aliases, related measures, provider comparison and Solstice rows.

## Preview and production

| Target | Worker | Publication |
| --- | --- | --- |
| Main preview (default) | `filecoindataportal-preview` | `https://filecoindataportal-preview.davidgasquez.workers.dev` |
| Explorer preview (`FDP_SITE=foc`) | `filecoindataportal-foc-preview` | `https://filecoindataportal-foc-preview.davidgasquez.workers.dev` |
| Archive preview | `filecoindataportal-old` | `https://filecoindataportal-old.davidgasquez.workers.dev` |
| Production (approval required) | `filecoindataportal` | Existing apex custom domain and zone route |
| Explorer production (approval required) | `filecoindataportal-foc` | `foc.filecoindataportal.xyz` custom domain |
| Archive domain (approval required) | `filecoindataportal-old` | `old.filecoindataportal.xyz` |

Build and validate a preview from the public database:

```sh
curl -fL --retry 3 -o /tmp/fdp-public.duckdb https://data.filecoindataportal.xyz/fdp.duckdb
export FDP_DB=/tmp/fdp-public.duckdb
export SITE_URL=https://filecoindataportal-preview.davidgasquez.workers.dev
export FOC_URL=https://filecoindataportal-foc-preview.davidgasquez.workers.dev
export ARCHIVE_URL=https://filecoindataportal-old.davidgasquez.workers.dev
npm run check && npm test && npm run test:foc
npm run build && npm run build:foc && npm run test:site
FDP_SITE=foc npm run deploy -- --dry-run && npm run deploy -- --dry-run
FDP_SITE=foc npm run deploy:preview && npm run deploy:preview
BASE_URL="$SITE_URL" npm run test:http
BASE_URL="$FOC_URL" FDP_SITE=foc npm run test:http
```

`build:preview` is a convenience that builds both targets with the preview origins; export them separately for subsequent static tests. Origins default to the production domains; `ARCHIVE_URL` defaults to the archive domain. The footer and About page make the archive discoverable.

The post-build step, per target, regenerates headers and robots rules (removing the portal-relative `SKILL.md`/`llms.txt` from the explorer), applies preview `noindex`, sets Markdown/XML MIME types and hashed-asset caching, and checks conservative Workers limits (20,000 files, 25 MiB per file). Production builds do not inherit preview headers. All targets use clean URLs and real 404s, not SPA fallback.

Deploy the explorer before the portal in both stages, so a failed explorer deployment leaves the portal unchanged. Bare `npm run deploy` targets only the portal preview; `FDP_SITE=foc` deploys `dist-foc/` to the explorer Workers instead. The deploy wrapper rejects target/config/route overrides; only `--dry-run` passes through. It requires the build's canonical origin and indexing to match the target stage; the explorer must also link the portal of that stage. Production requires an explicit `deploy:production`, `FDP_PRODUCTION_DEPLOY=true`, and an indexable production-origin build. These are accident guards, not replacements for approval or Cloudflare permissions.

`.github/workflows/website.yml` downloads one snapshot, records its checksum, checks/builds/tests both targets from it, and deploys both previews only from `portal-migration`. Main pushes and successful main Pipeline runs can deploy production only when repository variable `FDP_PRODUCTION_DEPLOY` is `true`. Archive-only changes do not trigger it; the archive is never rebuilt daily.

### Published snapshot contract

Production builds require every stored metric source column, including `pdp_registered_bytes`, `pdp_replicated_bytes`, `pdp_replication_coverage`, and `pdp_unique_bytes` in `daily_network_metrics`. Previews explain missing columns and show unavailable metrics without borrowing local values or inventing zero/history. **Production builds reject incomplete schemas.** After an independently authorized data refresh, export and publish through the data pipeline, then download and identify the public snapshot before building the website.

### Production release and rollback

Before merging schema-dependent website changes, ensure a fresh public snapshot passes the production build. A disabled deploy gate does not skip schema validation.

1. Validate a fresh public snapshot and the complete production-origin build, including browser/header/404/deeplink checks. Keep the archive snapshot identified in `old/README.md` frozen.
2. Record the then-current production Worker version and retain candidate artifacts. The daily job may have changed the version since preflight.
3. For the initial migration, publish the archive domain first and verify noindex, frozen dates in its agent resources, downloads and the current-site footer link. Leave it untouched on subsequent daily releases. Do not add a notice banner.
4. Deploy the explorer, then the existing apex Worker without moving its bindings. Smoke-test, then enable normal production CI only after success.
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
