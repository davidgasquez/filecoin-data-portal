# Repository Guidelines

The repository contains the code for an open source data platform for Filecoin alongside other derived subprojects like dashboards.

## Project Structure

- `fdp`: Python package with Dagster assets and resources. One folder per category/type
- `dbt`: dbt project. Linked to Dagster assets
- `data`: local artifacts and exported tables (`make tables`)
- `Makefile` as the entrypoint to the core tasks

### Applications

All web applications use the published public Parquet files on `https://data.filecoindataportal.xyz/$DBT_MODEL_FILE_NAME.parquet`.

- **Web** (`web/`): Astro-based static site. Contains docs, showcases the datasets, and links to the other applications
- **Numbers** (`numbers/`): Observable Framework dashboard for visualizing the core ecosystem metrics
- **Pulse** (`pulse/`): Evidence BI framework for more operational dashboards (e.g: metrics per Client, Storage Provider, Allocator, ...)

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
uv run --env-file .env bash -lc 'duckdb "$DATABASE_PATH" -c "select count(*) from fdp.main.filecoin_clients;"'
```
