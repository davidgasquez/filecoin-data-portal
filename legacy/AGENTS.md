# Repository Guidelines

Legacy Dagster/dbt stack for Filecoin Data Portal.

## Project Structure

All paths below are relative to `legacy/`.

- `fdp`: Dagster assets and resources
- `dbt`: dbt project
- `data`: local artifacts and exported tables (`make tables`)
- `tools`: helper query scripts
- `Makefile` as the entrypoint to the core tasks

### Applications

Downstream applications use the published public Parquet files at `https://data.filecoindataportal.xyz/$DBT_MODEL_FILE_NAME.parquet`.

- **Web** (`../web/`): Astro-based static site. Contains docs, showcases the datasets, and links to the other applications
- **Numbers** (`../numbers/`): Observable Framework dashboard for visualizing the core ecosystem metrics
- **Pulse** (`../pulse/`): Evidence BI framework for more operational dashboards (e.g: metrics per Client, Storage Provider, Allocator, ...)

## Development

- The `Makefile` contains useful tasks' commands
- Run `make lint` after changes

### Asset Workflow

1. Add/modify assets within the appropriate module under `fdp/`
2. Create or update the relevant `dbt` models in `dbt/models/`
3. Run the asset with `uv run dagster asset materialize --select $ASSET_NAME -m fdp.definitions` CLI

### Making Queries to FDP Database

You can query the production database directly using DuckDB.

```bash
uv run --env-file ../.env bash -lc 'duckdb "$DATABASE_PATH" -c "select count(*) from fdp.main.filecoin_clients;"'
```
## Tools

### BigQuery CLI

Run arbitrary queries against BigQuery with `uv run tools/bq_query.py` from `legacy/`.

- Run: `uv run tools/bq_query.py "SELECT 1 AS value"`
- Query input: argument, `--file path.sql`, or stdin
- Useful flags: `--dry-run`, `--project`, `--location`, `--max-results`, `--pretty`
- Limit results to avoid large outputs

### MotherDuck CLI

Run arbitrary queries against MotherDuck with `uv run --env-file ../.env tools/md_query.py` from `legacy/`.

- Run: `uv run --env-file ../.env tools/md_query.py "SELECT 1 AS value"`
- Query input: argument, `--file path.sql`, or stdin
- Useful flags: `--database`, `--max-results`, `--pretty`, `--read-only`
- Requires `DATABASE_PATH` and MotherDuck token (`motherduck_token` or `MOTHERDUCK_TOKEN`)
