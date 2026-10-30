# Assets

- Write assets (`.py` and `.sql`) inside `assets/`
- The first folder under `assets/` is the schema
  - Remaining folders plus the file stem are joined with `_` to form the table name (`raw/riba/eth_logs.py` → `raw.riba_eth_logs`, `model/foc/providers.sql` → `model.foc_providers`)
  - Keep `main` flat (`main/providers.sql` → `main.providers`)
  - Table names must be unique per schema
- Prefer SQL, then Python with `asset.materialization = dataframe`, then Python with `asset.materialization = custom`
- Define asset metadata only in the asset header.

## Header format

- Optional `asset.description`
- Optional and repeatable `asset.depends`
- Required on Python assets: `asset.materialization` (`dataframe` or `custom`)
- Optional on SQL assets: `asset.resource` (currently `bigquery.lily`)
- Optional: `asset.keep_existing_on_failure = true` to continue with the existing table when refresh fails
- Optional and repeatable `asset.column` as `column_name | description`
- Optional and repeatable `asset.not_null`
- Optional and repeatable `asset.unique`
- Optional and repeatable `asset.assert`

## Rules

- `main.*` assets must fully document columns with `asset.column`
- If `asset.column` is present, documented columns must exactly match the materialized columns by name
- Inline tests (`asset.not_null`, `asset.unique`, `asset.assert`) are declared in the asset header and run against the materialized table
- `asset.keep_existing_on_failure = true` requires the table to already exist; first materialization still fails if refresh fails
- Leave a blank line between metadata sections, such as `description`, `materialization`, and tests
- Custom SQL tests live next to their asset as `<asset file stem>__name.test.sql` (`model/foc/pieces__unique_piece.test.sql` → `model.foc_pieces`)
- `uv run fdp materialize schema.table` refreshes only the selected assets by default
- `uv run fdp materialize schema` refreshes all assets under `assets/schema/**`
- `uv run fdp materialize model.foc` refreshes all assets under `assets/model/foc/**`
- `uv run fdp materialize assets/model/foc/providers.sql` refreshes exactly that asset
- You can also pass asset folder paths like `assets/model/foc`
- Use `uv run fdp materialize --with-deps schema.table`, `uv run fdp materialize --with-deps model.foc`, or `uv run fdp materialize --with-deps assets/model/foc/providers.sql` to also refresh all direct and indirect dependencies
- Selectors fail when ambiguous, such as when a folder and a table share a name in the same schema

## Python assets

- Define a top-level function whose name matches the file name
- Declare `asset.materialization = dataframe` when FDP should materialize the returned `pl.DataFrame`
- Declare `asset.materialization = custom` when the asset materializes itself and returns `None`
- Return annotations are optional and do not affect execution
- Use `fdp.table("schema.table")` to load a dependency
- Use `fdp.sql("...")` to run SQL against the database
- Use `fdp.db_connection()` when the asset needs custom or incremental materialization
- Use a SQL asset with `asset.resource = bigquery.lily` when the query must run in Lily BigQuery and the result should be copied into DuckDB
- Use `fdp.resources.*` helpers inside a custom Python asset when the upstream source is not a SQL backend

## SQL assets

- File content is a SQL query only
- SQL assets run in DuckDB by default
- SQL assets with `asset.resource = bigquery.lily` run in Lily BigQuery and copy the result into DuckDB
- DuckDB-backed SQL assets execute `create or replace table schema.table as <sql>`
