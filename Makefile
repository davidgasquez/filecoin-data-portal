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

run:
	$(FDP) materialize

restore:
	@set -eu; \
	test -n "$${SNAPSHOT_URL:-}" || { echo "Set SNAPSHOT_URL to a full-state fdp.duckdb (raw/model/main)." >&2; exit 1; }; \
	test ! -e fdp.duckdb.wal || { echo "Stop FDP and checkpoint fdp.duckdb before restoring." >&2; exit 1; }; \
	tmp=$$(mktemp ./fdp.duckdb.XXXXXX); \
	trap 'rm -f "$$tmp"' EXIT; \
	curl --fail --location "$$SNAPSHOT_URL" --output "$$tmp"; \
	uv run python -c 'import duckdb, sys; c = duckdb.connect(sys.argv[1], read_only=True); s = {r[0] for r in c.sql("select distinct schema_name from duckdb_tables()").fetchall()}; sys.exit(None if {"raw", "model"} <= s else "Snapshot lacks raw/model tables; not a full-state DuckDB.")' "$$tmp"; \
	test ! -e fdp.duckdb.wal || { echo "Stop FDP and checkpoint fdp.duckdb before restoring." >&2; exit 1; }; \
	mv "$$tmp" fdp.duckdb

qmd:
	qmd update
	qmd embed --chunk-strategy auto
