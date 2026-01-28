from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import tempfile

import duckdb
import polars as pl

from fdp.datasets import DatasetFn, discover_datasets, find_datasets_root

DEFAULT_DB_PATH = Path("fdp.duckdb")


def materialize(
    names: Iterable[str] | None = None,
    *,
    all_datasets: bool = False,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    datasets_root = find_datasets_root()
    datasets = discover_datasets(datasets_root)
    selected = _select_datasets(names, all_datasets, datasets)
    with duckdb.connect(db_path) as conn:
        for dataset_name, loader in selected:
            schema, table = _split_name(dataset_name)
            _write_table(conn, schema, table, loader())


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


def _write_table(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    frame: pl.DataFrame,
) -> None:
    conn.execute(f"create schema if not exists {schema}")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / f"{schema}.{table}.parquet"
        frame.write_parquet(path)
        conn.execute(
            f"create or replace table {schema}.{table} as "
            "select * from parquet_scan(?)",
            [str(path)],
        )
