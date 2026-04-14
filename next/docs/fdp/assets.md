# Assets

- Write assets (`.py` and `.sql`) inside `assets/`
- The first folder under `assets/` is the schema
  - Remaining folders plus the file stem are joined with `_` to form the table name
- Prefer SQL first, then Python with `asset.materialization = dataframe`, then Python with `asset.materialization = custom`
- Asset header metadata is the only source of truth for asset semantics.

## Header Format

- Optional `asset.description`
- Optional and repeatable `asset.depends`
- Required on Python assets: `asset.materialization` (`dataframe` or `custom`)
- Optional and repeatable `asset.column` as `column_name | description`
- Optional and repeatable `asset.not_null`
- Optional and repeatable `asset.unique`
- Optional and repeatable `asset.assert`

## Rules

- `main.*` assets must fully document columns with `asset.column`
- If `asset.column` is present, documented columns must exactly match the materialized columns by name
- Inline tests (`asset.not_null`, `asset.unique`, `asset.assert`) are declared in the asset header and run against the materialized table
- Leave a blank line between the different metadata sections (`description`, `materialization`, tests, ...)
- Custom SQL tests live under `assets/` as `*.test.sql` files and are attached to assets by path
- `uv run fdp materialize schema.table` refreshes only the selected assets by default
- Use `uv run fdp materialize --with-deps schema.table` to refresh their transitive dependency closure too

## Python assets

- Define a top-level function whose name matches the file name
- Declare `asset.materialization = dataframe` when FDP should materialize the returned `pl.DataFrame`
- Declare `asset.materialization = custom` when the asset materializes itself and returns `None`
- Return annotations are optional developer ergonomics, not framework behavior
- Use `fdp.table("schema.table")` to load a dependency
- Use `fdp.sql("...")` to run SQL against the database
- Use `fdp.db_connection()` when the asset needs custom or incremental materialization
- Use `fdp.bigquery.materialize_query(...)` inside a custom Python asset when the query must run in BigQuery and the result should be copied into DuckDB

## SQL assets

- File content is a SQL query only
- SQL assets always run in DuckDB
- DuckDB runner executes `create or replace table schema.table as <sql>`
