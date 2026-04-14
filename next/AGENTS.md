# Rules

Guidelines for `fdp`, a minimalistic and functional open data platform to help get, transform and publish Filecoin related datasets.

## Principles

- Minimal, simple, UNIXy, and opinionated
- Functional and idempotent transformations/pipelines with minimal cognitive load
- Modular, declarative, independent, composable steps
- Low abstractions, no frameworks, low LOC
- Everything as text/code, everything versioned
- Colocated assets, metadata, tests, and documentation
- Quick feedback cycles (run assets locally, immediately results, easy to debug)
- No backward compatibility constraints, don't care about regressions, old schemas, ...
- Clean and concise [documentation](./docs)
- This is a POC, breaking changes are ok. Goal is the simplest possible code

## Code

- Use `uv` instead of `python` (`uv run file.py`, `uv --help`, `uv run fdp`, ...)
- Run `make check` after writing assets, if it pass, materialize the asset, then query it
- Orchestration, resources, io, and platform related code lives under `fdp`, assets under `assets`
- You can learn more about how `fdp` wors in the documentation
- If an asset can be generalized, ask the user (this will reduce LOC)
- Assets are executed once a day in GitHub Actions, optimize accordingly

### Discovering Information

This repository and [relevant external Filecoin resources](.qmd/index.yml) are indexed by `qmd`, a local hybrid search engine.

Use QMD before `rg` when:

- Starting work related with Filecoin business logic or looking for specific patterns/business logic.
  - `qmd query -c agents "how does lily handle Y"` before writing some new logic
  - `qmd query -c agents "how does X work"` before reading random files
- Searching for concepts. when you know *what* you need but not *where* it lives or what it's called

Additionally, use `rg`/`grep` to explore the actual repository!
