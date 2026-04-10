# Assets

- Write assets (`.py` and `.sql`) inside the `assets/` folder
- The first folder under `assets/` is the schema.
  - Remaining folders plus the file stem are joined with `_` to form the table name.
- When writting assets the prefered order should be: SQL, then Python returning a `polars.DataFrame`, then Python with custom materialization.
  - A derived model can be done in SQL, decoding logs for a 500GB table needs incremental logic and a custom materialization.
- Metadata block at file top as language comments
  - Optional `asset.description`
  - Optional `asset.resource` (`duckdb` by default, or `bigquery` for SQL assets)
  - Optional and repeatable `asset.depends`
  - Optional and repeatable `asset.column` as `column_name | description`
  - Optional and repeatable `asset.not_null`
  - Optional and repeatable `asset.unique`
  - Optional and repeatable `asset.assert`

## Python Assets

- Python assets must define a top-level function whose name matches the file name
- Return type must be `-> pl.DataFrame` (`fdp` materializes it) or `-> None` (custom self-materialization)
- Use `fdp.table("schema.table")` to load a dependency
- Use `fdp.sql("sql query")` to run arbitrary SQL against the database
- Use `fdp.db_connection()` when the asset needs manual or incremental materialization

## SQL Assets

- File content is a SQL query only
- DuckDB runner executes `create or replace table schema.table as <sql>`
- Use `asset.resource = bigquery` to run the query in BigQuery and copy the result into DuckDB
