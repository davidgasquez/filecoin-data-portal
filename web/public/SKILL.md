---
name: fdp
description: Help users explore and use Filecoin Data Portal (fdp) datasets.
---

# Filecoin Data Portal

Guidelines on how to help users explore and use Filecoin Data Portal (fdp) datasets.

## Datasets

- [`beta_daily_filecoin_clients_metrics`](assets/beta_daily_filecoin_clients_metrics.md) — Daily Filecoin client metrics from verified claims, with sparse client-day rows.
- [`beta_filecoin_clients`](assets/beta_filecoin_clients.md) — Verified Filecoin clients
- [`beta_daily_filecoin_storage_providers_metrics`](assets/beta_daily_filecoin_storage_providers_metrics.md) — Daily Filecoin storage provider metrics from power snapshots, sector lifecycle activity, and verified claims, with sparse provider-day rows.
- [`beta_filecoin_storage_providers`](assets/beta_filecoin_storage_providers.md) — Historically active Filecoin storage providers enriched with current miner info, current power, market deal activity, and verified claim activity.
- [`foc_filecoin_pay_rails`](assets/foc_filecoin_pay_rails.md) — Mainnet Filecoin Pay rails reconstructed from onchain events. Includes creation and termination lifecycle, ARR eligibility, and service classification.
- [`foc_filecoin_warm_storage_datasets`](assets/foc_filecoin_warm_storage_datasets.md) — Mainnet Filecoin Warm Storage Service datasets created onchain. Includes dataset parties, payment rail identifiers, and billing lifecycle derived from FWSS events.
- [`foc_pdp_service_providers`](assets/foc_pdp_service_providers.md) — Mainnet Filecoin service providers reconstructed from ServiceProviderRegistry and FWSS events. Includes registry identity, event-derived PDP offering state, parsed capability fields, and FWSS approval status.
- [`foc_filecoin_pay_rail_rate_intervals`](assets/foc_filecoin_pay_rail_rate_intervals.md) — Mainnet Filecoin Pay rail rate intervals reconstructed from onchain events. Each row is a half-open interval [start_ordinal, end_ordinal) where a rail's recurring payment rate is constant.
- [`beta_daily_filecoin_core_metrics`](assets/beta_daily_filecoin_core_metrics.md) — Daily mainnet Filecoin core metrics.
- [`beta_daily_filecoin_pay_operator_metrics`](assets/beta_daily_filecoin_pay_operator_metrics.md) — Daily end-of-day Filecoin Pay operator metrics from active rail snapshots, with sparse operator-day rows.

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
