.DEFAULT_GOAL := run

ENV_FILE ?= .env
FDP := uv run --env-file $(ENV_FILE) fdp
PYTHON_DIRS := fdp assets

lint:
	uv run ruff check $(PYTHON_DIRS)
	uv run ty check $(PYTHON_DIRS)

test:
	$(FDP) test

check: lint
	$(FDP) check

publish:
	uv run fdp publish r2
	uv run fdp publish gsheet

run:
	$(FDP) materialize

restore:
	@set -eu; \
	test ! -e fdp.duckdb.wal || { echo "Stop FDP and checkpoint fdp.duckdb before restoring." >&2; exit 1; }; \
	tmp=$$(mktemp ./fdp.duckdb.XXXXXX); \
	trap 'rm -f "$$tmp"' EXIT; \
	curl --fail --location "$${SNAPSHOT_URL:-https://data.filecoindataportal.xyz/fdp.duckdb}" --output "$$tmp"; \
	uv run python -c 'import duckdb, sys; duckdb.connect(sys.argv[1], read_only=True).close()' "$$tmp"; \
	test ! -e fdp.duckdb.wal || { echo "Stop FDP and checkpoint fdp.duckdb before restoring." >&2; exit 1; }; \
	mv "$$tmp" fdp.duckdb

qmd:
	qmd update
	qmd embed --chunk-strategy auto
