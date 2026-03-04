# Repository Guidelines

Open source data platform for Filecoin.

## Project Structure

- `fdp`: Dagster assets and resources
- `dbt`: dbt project
- `data`: local artifacts and exported tables (`make tables`)
- `Makefile` as the entrypoint to the core tasks

### Applications

Downstream applications use the published public Parquet files at `https://data.filecoindataportal.xyz/$DBT_MODEL_FILE_NAME.parquet`.

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
