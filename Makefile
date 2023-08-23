.DEFAULT_GOAL := run

run:
	@dbt run --project-dir dbt;
	# @dagster asset materialize --select \* -m fdp;

dagster:
	@dagster dev -m fdp;

preview:
	@quarto preview

publish:
	@quarto publish gh-pages --no-prompt

clean:
	@dbt clean --project-dir dbt;
	@rm -rf output .quarto target dbt_packages logs

render:
	@quarto render
