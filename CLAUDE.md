# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

- The @README provides the overall description and principles.
- The @Makefile containes the most important commands to use as entrypoint.

## Architecture

The repository containes the code for the core of the data platform (`fdp` and `dbt` transformations) alongside other derived subprojects.

### Data Pipeline (`fdp`)

- **Dagster**: Orchestration layer managing all raw data assets and pipeline execution.
  - Each source has its own module with asset definitions
  - Data is loaded into DuckDB tables prefixed with `raw_`
- **dbt**: SQL-based transformations on top of DuckDB, all models materialized as tables
- **Diverse Data Sources**: BigQuery (Lily), SpaceScope API, Dune Analytics, DatacapStats, direct blockchain APIs, ...
- **Data Export** (`fdp/db.py`)
   - All processed tables are exported as Parquet files
   - Available at `https://filecoindataportal.xyz/data`

### Applications

- **Web** (`web/`): Main website, Astro-based static site.
- **Numbers** (`numbers/`): Observable Framework dashboard for visualizing the core ecosystem metrics.
- **Pulse** (`pulse/`): Evidence BI framework for mode operational dashboards.

All web applications use the published public Parquet files.

## Workflow

1. Add/modify assets in appropriate module under `fdp/`
2. Create or update the relevant `dbt` models in `dbt/models/`
3. Test locally with `make dev` and Dagster UI or with `uv run dagster asset materialize --select ...` CLI
4. Verify the data in the DuckDB table
5. Update or add new charts on Pulse or Numbers
