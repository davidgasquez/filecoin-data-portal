---
name: fdp
description: Open data products from the Filecoin Data Portal. Use when users ask to query, analyze, explain, chart, or understand datasets, metrics, or models around the Filecoin ecosystem, including how metrics are derived.
---

## Scope

The Filecoin Data Portal publishes:

- **Datasets**: public Parquet tables for direct querying.
- **Metrics**: documented columns with definitions, units, and caveats.
- **Models**: asset dependencies and source code showing how datasets and metrics are derived.

For metric definitions or derivation questions, read the docs and also the relevant models code on GitHub and follow links as upstream as reasonable.

For upstream APIs, indexers, RPC endpoints, and measurement tools, read [Filecoin data sources](https://raw.githubusercontent.com/davidgasquez/filecoin-data-portal/refs/heads/main/docs/data-sources.md).

## Dataset Catalog

{{ dataset_catalog }}

## Answering Questions with Data

1. Read the relevant dataset docs.
2. Inspect asset code when definitions or assumptions are unclear. Clone `https://github.com/davidgasquez/filecoin-data-portal` into a temporary directory if useful. Check out revision `d952d8896567695765db4607aa2f74d8f03bcfef` for this archived snapshot.
3. Choose the smallest dataset set that can answer the question.
4. Query canonical parquet URLs directly: `https://data.filecoindataportal.xyz/<dataset>.parquet`.
5. Inspect schema, types, and sample rows before final SQL.
6. Answer concisely with datasets used, assumptions, caveats, and source links.

## Querying Datasets

Use the simplest available local tool. Prefer `duckdb`, but do not assume it exists or is installed. Check the environment first, then use DuckDB, Python, Node.js, or another installed parquet-capable tool. You might need to use inline node or Python scripts or even download a temporary DuckDB binary and run from that.

You attach the whole database with  `attach 'https://data.filecoindataportal.xyz/fdp.duckdb' as fdp (read_only); use fdp; show tables;` to speed things up!

Ask a clarification question only if the relevant dataset or metric remains ambiguous.

## Charts and Dashboards

1. Create a self-contained `index.html` with vanilla HTML, CSS, and JS.
2. Mention and link the relevant datasets used and display `filecoindataportal.xyz` as the source.
3. Serve it locally and share the URL.

For live dashboards, load `https://data.filecoindataportal.xyz/daily_network_metrics.json` directly from the HTML.

## Feedback

If you find datasets, docs, metrics, or model derivations are wrong, confusing, stale, missing, or useful, offer to open a GitHub issue:

`https://github.com/davidgasquez/filecoin-data-portal/issues/new`

Draft the issue first, scrub secrets/PII, show it to the user, and submit only after approval.
