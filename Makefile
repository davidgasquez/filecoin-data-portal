.DEFAULT_GOAL := run

DAGSTER_JOB := uv run dagster job execute -j __ASSET_JOB -m fdp.definitions

.PHONY: run
run:
	@uv run dagster-dbt project prepare-and-package --file fdp/dbt/resources.py
	@$(DAGSTER_JOB)

.PHONY: run-ci
run-ci:
	@uv run dagster-dbt project prepare-and-package --file fdp/dbt/resources.py
	@set -e; \
	tmp=$$(mktemp); \
	trap 'rm -f "$$tmp"' EXIT; \
	printf '%s\n' \
	  'execution:' \
	  '  config:' \
	  '    multiprocess:' \
	  '      max_concurrent: 2' > "$$tmp"; \
	$(DAGSTER_JOB) --config "$$tmp"

.PHONY: dev
dev:
	@uv run dagster dev

.PHONY: lint
lint:
	@uv run ruff check
	@uv run ty check
	@uv run prek -a

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

.PHONY: web
web:
	@npm run dev --prefix web

.PHONY: numbers
numbers:
	@npm run dev --prefix numbers

.PHONY: pulse
pulse:
	@npm run sources --prefix pulse
	@npm run dev --prefix pulse

.PHONY: clean
clean:
	@rm -rf data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
