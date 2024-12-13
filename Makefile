.DEFAULT_GOAL := run

.PHONY: run
run:
	@uv run dagster-dbt project prepare-and-package --file fdp/dbt/resources.py
	@uv run dagster asset materialize --select \* -m fdp.definitions

.PHONY: dev
dev:
	@uv run dagster dev

.PHONY: setup
setup:
	@command -v uv >/dev/null 2>&1 || pip install -U uv
	@uv sync
	@echo "source .venv/bin/activate"

.PHONY: tables
tables:
	@mkdir -p data/tables/
	@uv run python -c 'from fdp.db import export; export("data/tables/")'
	@ls -lh data/tables/
	@rm data/tables/raw_*.parquet

.PHONY: preview
preview:
	@quarto preview portal

.PHONY: render
render:
	@quarto render portal

.PHONY: numbers
numbers:
	@npm run dev --prefix numbers

.PHONY: clean
clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
