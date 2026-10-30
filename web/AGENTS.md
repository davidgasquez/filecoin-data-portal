# Web

- Production site, with the previous app archived in `old/` (separate package; never import from it).
- Manual deployment defaults to preview. Production changes require explicit approval and a validated public snapshot. Keep data publishing independent; do not modify pipelines or data models as part of web work.
- Astro static HTML, vanilla CSS, small progressive-enhancement scripts. No React, ECharts, Tailwind, or UI framework.
- Editorial data atlas: continuous monochrome canvas, IBM Plex Sans and Mono, typography-led hierarchy, sharp controls, sparse rules. No card grid, ornamental icons, gradients, or animation. A small light/dark toggle follows the system until a choice is saved.
- Data is evidence: source, observation date, population, units, denominator, missingness and partial coverage remain visible. UTC yesterday is the latest allowed daily date.
- Never equate Filecoin Pay volume with storage-only revenue or divide warm storage by raw network power. Different populations.
- Flow = bars; state = lines/steps; comparison = aligned bars/dots; exact lookup = tables. Bars start at zero. Missing days break lines. No dual axes.
- `/` is the portal landing page; `/numbers` holds all sourced charts and the full metric ledger. Reuse the v1 metric inventory. The explicitly requested high-profile-clients zero is declared, not a fabricated dated series.
- Use full grouped numbers, not K/M/B abbreviations. Headlines and hover use the same concise precision; the audit retains more decimals. Integrate definitions and sources into chart-title disclosures, not repetitive scale rows. Numbers time-series history defaults to 6 months, with 1 year and all-history options; labelled fixed-window comparisons stay fixed.
- Native HTML controls and disclosures, visible focus, responsive light/dark views. Hover also works with touch and arrow keys. Everything essential works without JavaScript.
- The Filecoin Onchain Cloud explorer is a second static build of this project (`FDP_SITE=foc`, pages in `src/foc/pages`, output `dist-foc/`, origin `foc.filecoindataportal.xyz`) with real, pre-rendered entity routes at its root, not an iframe or JS-only app. The explorer links to the portal origin (`SITE_URL`); the portal intentionally has no explorer links. Explorer `/datasets` are storage data sets, so catalog links go to the portal origin. Its intermediate `.foc/` data is generated locally from a read-only snapshot; do not copy publishing workflows from the prototype. Keep preparation idempotent: unchanged inputs must not rewrite imported JSON or trigger dev reload loops.
- Explorer aggregates must not add different native tokens. Keep stablecoin-at-par totals separate from native rail amounts, API snapshot timestamps separate from daily event coverage, and exact Solstice atto strings separate from display rounding.
- Validate with `npm run check`, `npm test`, `npm run test:foc`, `npm run build`, `npm run build:foc`, and `npm run test:site`, plus actual desktop/mobile interaction checks.
- Design rationale and guideline summary live in README.md. Keep authored code small and avoid framework-like abstractions.
