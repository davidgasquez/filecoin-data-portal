.DEFAULT_GOAL := run

deps: clean
	@dbt deps --project-dir dbt;

run: deps
	@dbt run --project-dir dbt;

preview:
	@quarto preview

clean:
	@dbt clean --project-dir dbt;
	@rm -rf output .quarto target dbt_packages logs
