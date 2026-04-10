.DEFAULT_GOAL := run

ENV_FILE ?= .env
FDP := uv run --env-file $(ENV_FILE) fdp

lint:
	uv run ruff check
	uv run ty check

test:
	$(FDP) test

check: lint
	$(FDP) check

run:
	$(FDP) materialize

qmd-update:
	qmd update
	qmd embed
