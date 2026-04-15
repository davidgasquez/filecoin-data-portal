# Filecoin Data Portal

This repository now has two data platform implementations:

- `next/`: current local-first FDP implementation and primary Python project
- `legacy/`: old Dagster/dbt pipeline, kept for reference and existing scheduled jobs

## Repository structure

- `next/`: current FDP CLI, assets, docs, and Python tooling
- `legacy/`: legacy Dagster/dbt stack, exported tables, helper scripts, and old docs
- `web/`: Astro website
- `numbers/`: Observable dashboard
- `pulse/`: Evidence dashboard

## CI

- `next.yml`: current FDP pipeline under `next/`
- `pipeline.yml` and `tables.yml`: legacy Dagster/dbt jobs under `legacy/`

## Start here

- Current platform: `next/README.md`
- Legacy Dagster/dbt stack: `legacy/README.md`
