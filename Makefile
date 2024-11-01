.DEFAULT_GOAL := run

run:
	@uv run dagster-dbt project prepare-and-package --file fdp/dbt/resources.py
	@uv run dagster asset materialize --select \* -m fdp.definitions

dev:
	@uv run dagster dev

setup:
	@command -v uv >/dev/null 2>&1 || pip install -U uv
	@uv sync
	@echo "source .venv/bin/activate"

tables:
	@mkdir -p data/tables/
	@uv run python -c 'from fdp.db import export; export("data/tables/")'
	@ls -lh data/tables/
	@rm data/tables/raw_*.parquet

preview:
	@quarto preview portal

render:
	@quarto render portal

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
