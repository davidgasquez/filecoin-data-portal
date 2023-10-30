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
	@dbt clean --project-dir dbt;
	@rm -rf output .quarto target dbt_packages logs data/*.parquet data/*.duckdb

render:
	@quarto render
