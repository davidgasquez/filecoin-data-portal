# Repository Guidelines

The repository containes the code for the core of the data platform (`fdp` and `dbt` transformations) alongside other derived subprojects.

## Project Structure & Module Organization

- `fdp/`: Python package with Dagster assets and resources (`dbt/`, `dune/`, `spacescope/`, `bigquery/`, `apis/`). Entrypoint: `fdp/definitions.py`.
- `dbt/`: dbt project (`dbt_project.yml`, `models/`, `macros/`, `profiles.yml`).
- `data/`: local artifacts and exported tables (`make tables`).
- Tooling: `Makefile`, `pyproject.toml`, `uv`.

### Applications

All web applications use the published public Parquet files on `https://data.filecoindataportal.xyz/`.

- **Web** (`web/`): Main website, Astro-based static site.
- **Numbers** (`numbers/`): Observable Framework dashboard for visualizing the core ecosystem metrics.
- **Pulse** (`pulse/`): Evidence BI framework for mode operational dashboards.

## Build, Test, and Development Commands

- `make setup`: Install Python deps with `uv` and create `.venv`.
- `make dev`: Launch Dagster UI locally at http://127.0.0.1:3000.
- `make run`: Package dbt and materialize all Dagster assets.
- `make tables`: Export Parquet tables into `data/tables/` and clean raw dumps.
- `make lint`: Lint with Ruff and type-check (Pyright via `ty`).
- Frontends: `make web` (Astro dev), `make numbers` (Observable preview), `make pulse` (Evidence dev).
- Clean: `make clean` to remove local build artifacts.

### Workflow

1. Add/modify assets in appropriate module under `fdp/`.
2. Create or update the relevant `dbt` models in `dbt/models/`.
3. Test locally with `make dev` and Dagster UI or with `uv run dagster asset materialize --select ...` CLI.
4. Verify the data in the DuckDB table.
5. Update or add new charts on Pulse or Numbers.

## Coding Style & Naming Conventions

- Python: Standard checks and lints with `make lint`.
- Modules/files/functions: `snake_case`; classes: `PascalCase`. Keep assets small and composable.
- dbt: model names `filecoin_*`; prefer `table` materialization; colocate tests in `dbt/models/models.yml`.

## Commit & Pull Request Guidelines

- Commits: concise, imperative, often emoji-prefixed (e.g., `🐛 Fix …`, `📈 Add …`); reference issues/PRs when applicable.
- PRs: include purpose, scope, and impact; link issues; add before/after screenshots for UI; note data changes (model names); ensure `make lint` and `make run` pass.
