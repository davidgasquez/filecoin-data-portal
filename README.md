<div align="center">
  <img width="80px" src="https://filecoindataportal.xyz/favicon.svg">

  # Filecoin Data Portal

  Open datasets for the Filecoin ecosystem, built from open source code and published daily.

  [Website](https://filecoindataportal.xyz) · [Datasets](https://filecoindataportal.xyz/datasets) · [Docs](https://filecoindataportal.xyz/docs) · [SKILL.md](https://filecoindataportal.xyz/SKILL.md)

  ![Build](https://img.shields.io/github/actions/workflow/status/davidgasquez/filecoin-data-portal/pipeline.yml?style=flat-square)
  ![License](https://img.shields.io/github/license/davidgasquez/filecoin-data-portal?style=flat-square)
  ![Stars](https://img.shields.io/github/stars/davidgasquez/filecoin-data-portal?style=flat-square)
</div>

## 🚀 Quickstart

Every dataset is a Parquet file, rebuilt daily. Browse them at [filecoindataportal.xyz/datasets](https://filecoindataportal.xyz/datasets).

```
https://data.filecoindataportal.xyz/<dataset>.parquet
```

Query them with any Parquet reader. With [DuckDB](https://duckdb.org/) (or [SQL Workbench](https://sql-workbench.com/) in the browser):

```sql
select date, onboarded_pibs
from 'https://data.filecoindataportal.xyz/daily_network_metrics.parquet'
order by date desc
limit 10;
```

With Python:

```python
import polars as pl

pl.read_parquet("https://data.filecoindataportal.xyz/miners.parquet")
```

Or get everything at once in a single DuckDB file (DuckDB 2.0+):

```sql
attach 'https://data.filecoindataportal.xyz/fdp.duckdb' as fdp (read_only);
```

### 🤖 Agents

Point your agent to [`SKILL.md`](https://filecoindataportal.xyz/SKILL.md). It lists every dataset and explains how to query them.

## ⚙️ Development

Runs anywhere with `uv`. On Nix, `nix develop` gives a pinned shell with all the tools.

- `uv run fdp list`: list assets
- `uv run fdp materialize`: materialize all assets
- `uv run fdp materialize main.providers`: materialize one asset (add `--with-deps` to refresh its dependencies)
- `uv run fdp query "select * from main.providers limit 10"`: query the local database
- `make check`: lint and validate assets
- `make test`: run data tests
- `make publish`: publish datasets to R2
- `make restore SNAPSHOT_URL=...`: replace local `fdp.duckdb` with a full-state snapshot

Secrets live in `.env` (load with `uv run --env-file .env ...`):

```bash
ENCODED_GOOGLE_APPLICATION_CREDENTIALS= # base64 Google service account JSON
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_ACCOUNT_ID=
R2_BUCKET=
CLOUDFLARE_API_TOKEN= # needs Cache Purge on filecoindataportal.xyz
CLOUDFLARE_ZONE_ID=d301192e601454a9cf7a87b4cd6ee243
```

## 📃 Disclaimer

The datasets provided by this service are made available "as is", without any warranties or guarantees of any kind, either expressed or implied. By using these datasets, you agree that you do so at your own risk.

## 📝 Licenses

The Filecoin Data Portal is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
