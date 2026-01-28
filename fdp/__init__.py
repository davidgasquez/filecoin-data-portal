from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
import os
from typing import TypeAlias
import httpx
import importlib.util
from pathlib import Path
from types import ModuleType

import duckdb
import polars as pl

DATASETS_DIR_NAME = "datasets"
DatasetResult: TypeAlias = None | pl.DataFrame
DatasetFn = Callable[..., DatasetResult]
DatasetDeps: TypeAlias = dict[str, str]
DEFAULT_DB_PATH = Path(os.environ.get("FDP_DB_PATH", "fdp.duckdb"))


def dataset(
    func: DatasetFn | None = None,
    *,
    depends_on: DatasetDeps | None = None,
    schema: str | None = "raw",
    table: str | None = None,
) -> DatasetFn | Callable[[DatasetFn], DatasetFn]:
    def wrap(fn: DatasetFn) -> DatasetFn:
        setattr(fn, "_fdp_dataset", True)
        setattr(fn, "_fdp_depends", dict(depends_on or {}))
        fn_name = getattr(fn, "__name__", fn.__class__.__name__)
        resolved_table = fn_name if table is None else table
        setattr(fn, "_fdp_schema", schema)
        setattr(fn, "_fdp_table", resolved_table)
        return fn

    if func is None:
        return wrap
    return wrap(func)


@contextmanager
def db_connection(
    db_path: Path | str | None = None,
) -> Iterator[duckdb.DuckDBPyConnection]:
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    with duckdb.connect(path) as conn:
        yield conn


def query(sql: str, params: list[object] | None = None) -> None:
    with db_connection() as conn:
        if params is None:
            conn.execute(sql)
            return
        conn.execute(sql, params)


def fetch_json(url: str) -> dict:
    response = httpx.get(url, timeout=30, follow_redirects=True)
    response.raise_for_status()
    return response.json()


def find_datasets_root() -> Path:
    for parent in [Path.cwd(), *Path.cwd().parents]:
        candidate = parent / DATASETS_DIR_NAME
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("datasets directory not found")


def discover_datasets(datasets_root: Path) -> dict[str, DatasetFn]:
    datasets: dict[str, DatasetFn] = {}
    for module_path in _dataset_files(datasets_root):
        module = _load_module(module_path)
        for dataset_name, loader in _module_datasets(module).items():
            if dataset_name in datasets:
                raise ValueError(f"Duplicate dataset name: {dataset_name}")
            datasets[dataset_name] = loader
    return datasets


def _dataset_files(datasets_root: Path) -> list[Path]:
    return sorted(
        path
        for path in datasets_root.rglob("*.py")
        if path.is_file() and not path.name.startswith("_")
    )


def _load_module(module_path: Path) -> ModuleType:
    module_name = _module_name(module_path)
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"Unable to load dataset module: {module_path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def _module_name(module_path: Path) -> str:
    sanitized = module_path.as_posix().replace("/", "_").replace(".", "_")
    return f"fdp_dataset_{sanitized}"


def _module_datasets(module: ModuleType) -> dict[str, DatasetFn]:
    datasets: dict[str, DatasetFn] = {}
    for name, value in vars(module).items():
        if callable(value) and getattr(value, "_fdp_dataset", False):
            datasets[name] = value
    if datasets:
        return datasets
    raise ValueError(f"No @dataset functions found in {module.__file__}")
