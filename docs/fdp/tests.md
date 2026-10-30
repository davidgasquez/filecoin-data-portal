# Tests

- Run data tests with `uv run --env-file .env fdp test` after materializing assets
- FDP discovers tests when loading assets:
  - Inline tests come from `asset.not_null`, `asset.unique`, and `asset.assert`
  - Custom SQL tests come from `*.test.sql` files
- `fdp test` checks materialized columns against the asset header before running data tests
- If `asset.column` is present, documented columns must exactly match the materialized columns by name
- `main.*` assets must define `asset.column` metadata
- Custom SQL data tests should return failing rows
