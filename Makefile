.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m fdp

dev:
	@dagster dev -m fdp

tables:
	@python -c 'from fdp.db import export; export("data/local.duckdb", "data/tables")'

preview:
	@quarto preview portal

render:
	@quarto render portal

publish:
	@fleek sites deploy

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
