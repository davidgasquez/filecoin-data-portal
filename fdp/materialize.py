from __future__ import annotations

from collections.abc import Iterable
from graphlib import CycleError, TopologicalSorter
import inspect

import duckdb
import polars as pl

from fdp import DatasetFn, db_connection, discover_datasets, find_datasets_root


def materialize(
    names: Iterable[str] | None = None,
    *,
    all_datasets: bool = False,
) -> None:
    datasets_root = find_datasets_root()
    datasets = discover_datasets(datasets_root)
    deps_map = {name: _dataset_deps(fn) for name, fn in datasets.items()}
    params_map = {name: _dataset_params(name, fn) for name, fn in datasets.items()}
    _validate_datasets(datasets, deps_map, params_map)
    selected = _resolve_selection(names, all_datasets, datasets, deps_map)
    graph = {name: list(deps_map[name].values()) for name in selected}
    try:
        order = list(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise ValueError(f"Dependency cycle detected: {exc}") from exc
    frames: dict[str, pl.DataFrame] = {}
    with db_connection() as conn:
        for name in order:
            fn = datasets[name]
            deps = deps_map[name]
            param_names = params_map[name]
            kwargs = _resolve_kwargs(name, deps, frames, param_names)
            result = fn(**kwargs) if param_names else fn()
            if result is None:
                continue
            if not isinstance(result, pl.DataFrame):
                raise TypeError("Dataset must return None or polars.DataFrame.")
            frames[name] = result
            schema, table = _dataset_meta(fn)
            if schema is None or table is None:
                continue
            _write_table(conn, schema, table, result)


def _dataset_deps(fn: DatasetFn) -> dict[str, str]:
    return getattr(fn, "_fdp_depends", {})


def _dataset_params(name: str, fn: DatasetFn) -> list[str]:
    signature = inspect.signature(fn)
    parameters = list(signature.parameters.values())
    if any(
        param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        for param in parameters
    ):
        raise ValueError(f"{name} uses *args or **kwargs. Not supported.")
    return [param.name for param in parameters]


def _dataset_meta(fn: DatasetFn) -> tuple[str | None, str | None]:
    schema = getattr(fn, "_fdp_schema", "raw")
    fn_name = getattr(fn, "__name__", fn.__class__.__name__)
    table = getattr(fn, "_fdp_table", fn_name)
    return schema, table


def _validate_datasets(
    datasets: dict[str, DatasetFn],
    deps_map: dict[str, dict[str, str]],
    params_map: dict[str, list[str]],
) -> None:
    names = set(datasets)
    for name, deps in deps_map.items():
        missing_deps = sorted({dep for dep in deps.values() if dep not in names})
        if missing_deps:
            missing_list = ", ".join(missing_deps)
            raise ValueError(f"Unknown dependencies for {name}: {missing_list}")
        param_names = set(params_map[name])
        if not param_names:
            continue
        dep_names = set(deps)
        missing_params = sorted(dep_names - param_names)
        extra_params = sorted(param_names - dep_names)
        if missing_params or extra_params:
            problems = []
            if missing_params:
                problems.append(f"missing params: {', '.join(missing_params)}")
            if extra_params:
                problems.append(f"unexpected params: {', '.join(extra_params)}")
            raise ValueError(f"{name} dependency mismatch: {', '.join(problems)}")


def _resolve_selection(
    names: Iterable[str] | None,
    all_datasets: bool,
    datasets: dict[str, DatasetFn],
    deps_map: dict[str, dict[str, str]],
) -> set[str]:
    if all_datasets:
        selected = set(datasets)
    else:
        if not names:
            raise ValueError("Pass --all or dataset names to materialize.")
        requested = list(names)
        unknown = sorted({name for name in requested if name not in datasets})
        if unknown:
            unknown_list = ", ".join(unknown)
            raise ValueError(f"Unknown datasets: {unknown_list}")
        selected = set(requested)
    stack = list(selected)
    while stack:
        name = stack.pop()
        for dep in deps_map[name].values():
            if dep not in selected:
                selected.add(dep)
                stack.append(dep)
    return selected


def _resolve_kwargs(
    name: str,
    deps: dict[str, str],
    frames: dict[str, pl.DataFrame],
    param_names: list[str],
) -> dict[str, pl.DataFrame]:
    if not param_names:
        return {}
    missing = sorted({dep for dep in deps.values() if dep not in frames})
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Missing dependency frames for {name}: {missing_list}")
    return {alias: frames[dep] for alias, dep in deps.items()}


def _write_table(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    frame: pl.DataFrame,
) -> None:
    conn.execute(f"create schema if not exists {schema}")
    table_name = f"{schema}.{table}"
    conn.register("_fdp_frame", frame)
    try:
        conn.execute(
            f"create or replace table {table_name} as select * from _fdp_frame",
        )
    finally:
        conn.unregister("_fdp_frame")
