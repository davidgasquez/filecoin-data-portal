---
name: fdp
description: Help users explore and use Filecoin Data Portal (fdp) datasets.
---

# Filecoin Data Portal

Guidelines on how to help users explore and use Filecoin Data Portal (fdp) datasets.

Generated from `assets/main/` metadata and materialized DuckDB tables.

## Datasets

- [`beta_filecoin_clients`](assets/beta_filecoin_clients.md) — Verified Filecoin clients
- [`beta_filecoin_daily_client_metrics`](assets/beta_filecoin_daily_client_metrics.md) — Daily Filecoin client metrics from verified claims, with sparse client-day rows.
- [`beta_filecoin_daily_storage_provider_metrics`](assets/beta_filecoin_daily_storage_provider_metrics.md) — Daily Filecoin storage provider metrics from power snapshots, sector lifecycle activity, and verified claims, with sparse provider-day rows.
- [`beta_filecoin_storage_providers`](assets/beta_filecoin_storage_providers.md) — Historically active Filecoin storage providers enriched with current miner info, current power, market deal activity, and verified claim activity.
- [`beta_filecoin_daily_core_metrics`](assets/beta_filecoin_daily_core_metrics.md) — Daily mainnet Filecoin core metrics.

## Using Datasets

Start with `duckdb` if available. Consider asking the user to install it or ask the user for a tool (Pandas, Javascript, ...) to use as a replacement.

Canonical dataset URLs follow `https://data.filecoindataportal.xyz/<dataset>.parquet`.

1. Inspect the dataset.
2. Read the columns, types, and a few sample rows.
3. Ask any clarification question if needed.
4. Write temporary self-contained scripts that answer the user's question.
5. Get back in a clear and concise way.

## Answering Questions

- Mention the used datasets explicitly.
- Inspect columns, types, and sample rows first.
- Offer to plot charts if it makes sense.
