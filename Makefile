.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m fdp

dev:
	@dagster dev -m fdp

preview:
	@quarto preview portal

render:
	@quarto render portal

publish:
	@quarto publish gh-pages --no-prompt portal

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
