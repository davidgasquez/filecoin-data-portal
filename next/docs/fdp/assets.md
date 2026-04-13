# Assets

- Write assets (`.py` and `.sql`) inside `assets/`
- The first folder under `assets/` is the schema
  - Remaining folders plus the file stem are joined with `_` to form the table name
- Prefer SQL first, then Python returning `pl.DataFrame`, then Python with custom materialization
- Asset header metadata is the only source of truth for asset semantics.

## Header Format

- Optional `asset.description`
- Optional `asset.resource` (`duckdb` by default, or `bigquery` for SQL assets)
- Optional and repeatable `asset.depends`
- Optional and repeatable `asset.column` as `column_name | description`
- Optional and repeatable `asset.not_null`
- Optional and repeatable `asset.unique`
- Optional and repeatable `asset.assert`

## Rules

- `main.*` assets must fully document columns with `asset.column`
- If `asset.column` is present, documented columns must exactly match the materialized columns by name
- Inline tests (`asset.not_null`, `asset.unique`, `asset.assert`) are declared in the asset header and run against the materialized table
- Custom SQL tests live under `assets/` as `*.test.sql` files and are attached to assets by path

## Python assets

- Define a top-level function whose name matches the file name
- Return `-> pl.DataFrame` for FDP-managed materialization or `-> None` for self-materialization
- Use `fdp.table("schema.table")` to load a dependency
- Use `fdp.sql("...")` to run SQL against the database
- Use `fdp.db_connection()` when the asset needs manual or incremental materialization

## SQL assets

- File content is a SQL query only
- DuckDB runner executes `create or replace table schema.table as <sql>`
- Use `asset.resource = bigquery` to run the query in BigQuery and copy the result into DuckDB
