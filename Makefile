.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m fdp

dev:
	@dagster dev

setup:
	@command -v uv >/dev/null 2>&1 || pip install -U uv
	@uv venv
	@uv pip install -U -e ".[dev]"

tables:
	@mkdir -p data/tables/
	@python -c 'from fdp.db import export; export("data/tables/")'
	@rm data/tables/raw_*.parquet

preview:
	@quarto preview portal

render:
	@quarto render portal
	@cp -r data/tables portal/.quarto/_site/data

publish:
	@fleek sites deploy

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
