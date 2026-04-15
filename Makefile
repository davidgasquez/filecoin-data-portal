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

run:
	$(FDP) materialize

qmd:
	qmd update
	qmd embed
