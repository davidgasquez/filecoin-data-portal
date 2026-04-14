# Filecoin Data Portal

Open, minimal, local-first Data Platform for the Filecoin Ecosystem.

- Open source code producing open datasets in open formats using public infrastructure.
- Runs on a laptop, server, or CI runner without any lock-ins.

## 🚀 Quickstart

The `fdp/` folder contains the CLI and lightweight orchestrator while the `assets/` folder hosts data assets and custom SQL data tests. FDP assumes the environment is already loaded (you can autoload it running `uv` with `--env-file .env`).

- `uv run fdp list`
- `uv run fdp check`
- `uv run fdp materialize`
- `uv run fdp materialize main`
- `uv run fdp materialize main.beta`
- `uv run fdp materialize raw.some_asset`
- `uv run fdp materialize --with-deps main.beta`
- `uv run fdp materialize --with-deps raw.some_asset`
- `uv run fdp status`
- `uv run fdp prune`
- `uv run fdp docs`
- `uv run fdp test`
- `uv run fdp publish r2`
- `uv run fdp publish gsheet`
- `uv run fdp show raw.daily_network_activity_by_method`
- `uv run fdp query "select * from raw.daily_network_activity_by_method limit 10"`

FDP detects the project root from the nearest parent containing `assets/`. By default, DuckDB lives at `<project>/fdp.duckdb` and `fdp docs` writes to `<project>/build/docs`.
When you pass explicit asset keys or folder selectors to `fdp materialize`, FDP refreshes only the matched assets by default and expects their dependencies to already be materialized. Use `--with-deps` to refresh the full dependency closure. Folder selectors map to folders under `assets/`, so `main` selects `assets/main/**` and `main.beta` selects `assets/main/beta/**`.

## ⚙️ Development

You can run the Filecoin Data Portal anywhere using `uv`. You'll need the following secrets in your environment:

- `ENCODED_GOOGLE_APPLICATION_CREDENTIALS` (base64-encoded Google service account JSON)
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_ACCOUNT_ID`
- `R2_BUCKET`
- `FDP_GSHEET_SPREADSHEET_ID`

`uv run fdp publish r2` writes one parquet file per `main.*` table to R2.
`uv run fdp publish gsheet` writes one worksheet per `main.*` table to a Google spreadsheet.
Share the target spreadsheet with the Google service account from `ENCODED_GOOGLE_APPLICATION_CREDENTIALS`.

For local development, load them explicitly with `uv run --env-file .env ...`.

## 📃 Disclaimer

The datasets provided by this service are made available "as is", without any warranties or guarantees of any kind, either expressed or implied. By using these datasets, you agree that you do so at your own risk.

## 📝 Licenses

The Filecoin Data Portal is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
