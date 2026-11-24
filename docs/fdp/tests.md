# Tests

- Run data tests with `uv run --env-file .env fdp test` after materializing assets
- FDP discovers tests when loading assets:
  - Inline tests come from `asset.not_null`, `asset.unique`, and `asset.assert`
  - Custom SQL tests come from `*.test.sql` files
- `fdp test` checks materialized columns against the asset header before running data tests (rules in [assets](./assets.md))
- Custom SQL data tests should return failing rows
