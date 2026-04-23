<div align="center">
  <img width="80px" src="https://filecoindataportal.xyz/favicon.svg">

  # Filecoin Data Portal

  Open, minimal, local-first Data Platform for the Filecoin Ecosystem.

  ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/davidgasquez/filecoin-data-portal/pipeline.yml?style=flat-square)
  ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/davidgasquez/filecoin-data-portal/tables.yml?style=flat-square)
  ![GitHub](https://img.shields.io/github/license/davidgasquez/filecoin-data-portal?style=flat-square)
  ![GitHub Repo stars](https://img.shields.io/github/stars/davidgasquez/filecoin-data-portal?style=flat-square)
</div>

- Open source code producing open datasets in open formats using public infrastructure.
- Runs on a laptop, server, or CI runner without any lock-ins.

<div align="center">
  <a href="https://drips.network/app/projects/github/davidgasquez/filecoin-data-portal">
    <img src="https://filecoin.drips.network/api/embed/project/https%3A%2F%2Fgithub.com%2Fdavidgasquez%2Ffilecoin-data-portal/support.png?background=light&style=drips&text=project&stat=none" alt="Support filecoin-data-portal on drips.network" height="21">
  </a>
</div>

## 🚀 Quickstart

The `fdp/` folder contains the CLI and lightweight orchestrator while the `assets/` folder hosts data assets and custom SQL data tests. The environment is assumed to be already loaded (you can autoload it running `uv` with `--env-file .env`).

- `uv run fdp list`
- `uv run fdp check`
- `uv run fdp materialize`
- `uv run fdp materialize main`
- `uv run fdp materialize main.daily`
- `uv run fdp materialize raw.some_asset`
- `uv run fdp materialize assets/main/daily/filecoin_pay_operators_metrics.sql`
- `uv run fdp materialize --with-deps main.daily`
- `uv run fdp materialize --with-deps raw.some_asset`
- `uv run fdp status`
- `uv run fdp prune`
- `uv run fdp docs`
- `uv run fdp test`
- `uv run fdp publish r2`
- `uv run fdp publish r2 assets/main/daily/filecoin_pay_operators_metrics.sql`
- `uv run fdp publish gsheet`
- `uv run fdp show raw.daily_network_activity_by_method`
- `uv run fdp query "select * from raw.daily_network_activity_by_method limit 10"`

FDP detects the project root from the nearest parent containing `assets/`. By default, DuckDB lives at `<project>/fdp.duckdb` and `fdp docs` writes to `<project>/build/docs`.

When you pass explicit selectors to `fdp materialize`, FDP refreshes only the matched assets by default and expects their dependencies to already be materialized.
Selectors can be asset keys, folder selectors, or asset file/folder paths under `assets/`. Use `--with-deps` to refresh the full dependency closure.

## ⚙️ Development

You can run the Filecoin Data Portal anywhere using `uv`. You'll need the following secrets in your environment:

- `ENCODED_GOOGLE_APPLICATION_CREDENTIALS` (base64-encoded Google service account JSON)
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_ACCOUNT_ID`
- `R2_BUCKET`
- `FDP_GSHEET_SPREADSHEET_ID`

`uv run fdp publish r2` writes one parquet file per `main.*` table to R2.
`uv run fdp publish gsheet` syncs one worksheet per `main.*` table to a Google spreadsheet and removes stale worksheets.
Share the target spreadsheet with the Google service account from `ENCODED_GOOGLE_APPLICATION_CREDENTIALS`.

For local development, load them explicitly with `uv run --env-file .env ...`.

## 📃 Disclaimer

The datasets provided by this service are made available "as is", without any warranties or guarantees of any kind, either expressed or implied. By using these datasets, you agree that you do so at your own risk.

## 📝 Licenses

The Filecoin Data Portal is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
