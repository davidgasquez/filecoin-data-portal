# Tests

- Run data tests with `uv run --env-file .env fdp test` after materializing assets
- Inline data tests come from `asset.not_null`, `asset.unique`, and `asset.assert`
- `fdp test` also validates that every documented `asset.column` exists in the materialized table
- Custom SQL data tests are `*.test.sql` files under `assets/` (e.g. `assets/raw/asset_name__test_name.test.sql`) and should return failing rows
