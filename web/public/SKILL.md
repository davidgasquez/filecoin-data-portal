---
name: fdp
description: Open Filecoin datasets from the Filecoin Data Portal. Use when asked to query, analyze, explain, or chart Filecoin network, storage provider, PDP, Filecoin Pay, or market data, including how a metric is derived.
---

# Filecoin Data Portal

Public Parquet tables, rebuilt daily from chain data, FEVM events, APIs, probes, and market data.

## Choose datasets

1. Read the [Markdown catalog](/datasets.md). It lists every dataset with a one-line description and links to a Markdown page per dataset (`/datasets/<dataset>.md`) with columns, types, units, coverage, sources, and asset code.
2. Read the page of each candidate dataset. Pick the smallest set that answers the question.
3. If a definition is still unclear, read the asset SQL linked from the dataset page, following upstream assets as far as needed. Cloning `https://github.com/davidgasquez/filecoin-data-portal` into a temporary directory is fine.
4. For upstream APIs, indexers, and RPC endpoints, read [Filecoin data sources](https://raw.githubusercontent.com/davidgasquez/filecoin-data-portal/refs/heads/main/docs/data-sources.md).

Ask a clarifying question only if the dataset or metric stays ambiguous.

## Query

- Each dataset is at `https://data.filecoindataportal.xyz/<dataset>.parquet`.
- All public tables are in one DuckDB 2.0+ file: `attach 'https://data.filecoindataportal.xyz/fdp.duckdb' as fdp (read_only); use fdp; show tables;`
- `daily_network_metrics` is also at `https://data.filecoindataportal.xyz/daily_network_metrics.json` for live dashboards.
- Prefer DuckDB, but check what is installed first; Python or Node.js with any Parquet reader also works.
- Inspect schema and a few rows before writing the final query.

```sql
select date, onboarded_pibs, raw_power_pibs
from 'https://data.filecoindataportal.xyz/daily_network_metrics.parquet'
order by date desc
limit 7;
```

## Interpret

- Dates are UTC. Daily tables end at UTC yesterday at the latest, and tables can end on different dates. Report the latest date each answer covers.
- Null means unknown or undefined, not zero. Do not fill gaps with zeros.
- Use the units in column names and descriptions (`_pibs`, `_usd`, `_fil`, ...).
- Atto-denominated columns (`_atto_fil`, `_atto_usd`, ...) are exact `DECIMAL(38,0)` integers. Keep them exact in arithmetic and divide by 1e18 only for display. Never add amounts of different tokens.
- Filecoin Pay volume covers all rails, not only storage. Warm storage capacity and network power measure different populations; do not divide one by the other.
- Provider checks are synthetic probes, not client traffic.
- Compute ratios from pooled counts; do not average per-provider percentages.

## Answer

Answer concisely with the datasets used, the SQL you ran, the latest date covered, assumptions, caveats, and links to the dataset pages. Do not invent numbers that the data does not contain.

For charts, build a self-contained `index.html` with vanilla HTML, CSS, and JS, link the datasets used, credit `filecoindataportal.xyz` as the source, and serve it locally.

## Feedback

If a dataset, definition, or derivation looks wrong, stale, missing, or confusing, offer to open an issue at `https://github.com/davidgasquez/filecoin-data-portal/issues/new`. Draft it first, remove secrets and personal data, show it to the user, and submit only after approval.

More: [docs](/docs), [about](/about), [llms.txt](/llms.txt).
