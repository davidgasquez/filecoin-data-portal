# Tests

- Run data tests with `uv run --env-file .env fdp test` after materializing assets
- Test discovery comes from the loaded asset model:
  - inline tests from `asset.not_null`, `asset.unique`, and `asset.assert`
  - custom SQL tests from `*.test.sql` files discovered while loading assets
- `fdp test` validates the materialized table shape against canonical header metadata before running data tests
- If `asset.column` is present, documented columns must exactly match the materialized columns by name
- `main.*` assets must define `asset.column` metadata
- Custom SQL data tests should return failing rows
