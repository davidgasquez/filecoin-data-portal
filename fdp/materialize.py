from __future__ import annotations

from collections.abc import Iterable

import polars as pl

from fdp import DatasetFn, db_connection, discover_datasets, find_datasets_root


def materialize(
    names: Iterable[str] | None = None,
    *,
    all_datasets: bool = False,
) -> None:
    datasets_root = find_datasets_root()
    datasets = discover_datasets(datasets_root)
    selected = _select_datasets(names, all_datasets, datasets)
    with db_connection() as conn:
        for dataset_name, loader in selected:
            schema, table = _split_name(dataset_name)
            conn.execute(f"create schema if not exists {schema}")
            table_name = f"{schema}.{table}"
            result = _call_dataset(loader, conn, table_name)
            if result is None:
                continue
            if isinstance(result, pl.DataFrame):
                conn.register("_fdp_frame", result)
                try:
                    conn.execute(
                        f"create or replace table {table_name} as "
                        "select * from _fdp_frame",
                    )
                finally:
                    conn.unregister("_fdp_frame")
                continue
            raise TypeError("Dataset must return None or polars.DataFrame.")


def _select_datasets(
    names: Iterable[str] | None,
    all_datasets: bool,
    datasets: dict[str, DatasetFn],
) -> list[tuple[str, DatasetFn]]:
    if all_datasets:
        return sorted(datasets.items())
    if not names:
        raise ValueError("Pass --all or dataset names to materialize.")
    unknown = [name for name in names if name not in datasets]
    if unknown:
        unknown_list = ", ".join(sorted(set(unknown)))
        raise ValueError(f"Unknown datasets: {unknown_list}")
    return [(name, datasets[name]) for name in names]


def _split_name(dataset_name: str) -> tuple[str, str]:
    parts = dataset_name.split(".", maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "raw", parts[0]


def _call_dataset(
    loader: DatasetFn,
    conn: duckdb.DuckDBPyConnection,
    table: str,
) -> None | pl.DataFrame:
    try:
        return loader(conn, table)
    except TypeError as exc:
        message = str(exc)
        if "positional" not in message and "arguments" not in message:
            raise
        return loader()
