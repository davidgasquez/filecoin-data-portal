.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m fdp;

dev:
	@dagster dev -m fdp;

preview:
	@quarto preview

publish:
	@quarto publish gh-pages --no-prompt

clean:
	@rm -rf output .quarto target logs data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages

render:
	@quarto render
