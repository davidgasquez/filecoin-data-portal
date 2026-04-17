---
name: fdp
description: Help users explore and use Filecoin Data Portal (fdp) datasets.
---

# Filecoin Data Portal

Guidelines on how to help users explore and use Filecoin Data Portal (fdp) datasets.

## Datasets

- [`clients`](assets/clients.md) — Published clients.
- [`storage_providers`](assets/storage_providers.md) — Published storage providers.
- [`daily_clients_metrics`](assets/daily_clients_metrics.md) — Published daily clients metrics.
- [`daily_storage_providers_metrics`](assets/daily_storage_providers_metrics.md) — Published daily metrics for storage providers.
- [`pdp_service_providers`](assets/pdp_service_providers.md) — Published PDP service providers.
- [`filecoin_pay_rails`](assets/filecoin_pay_rails.md) — Published Filecoin Pay rails.
- [`warm_storage_datasets`](assets/warm_storage_datasets.md) — Published warm storage datasets.
- [`daily_filecoin_pay_operators_metrics`](assets/daily_filecoin_pay_operators_metrics.md) — Published daily Filecoin Pay operators metrics.
- [`daily_network_metrics`](assets/daily_network_metrics.md) — Published daily network metrics.

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
- Clone the repo for deeper exploration if needed.

## Charts & Dashboards

When the user asks for a chart, dashboard, or visualization:

1. Write a self-contained `index.html` using vanilla HTML, CSS, and JS.
2. Serve it locally and share the URL.
