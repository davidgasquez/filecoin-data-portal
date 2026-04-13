import importlib.util
from collections.abc import Iterable
from pathlib import Path
from time import perf_counter
from types import ModuleType

import polars as pl

from fdp.api import db_connection
from fdp.assets import Asset, ordered_assets, python_asset_function_name
from fdp.bigquery import materialize_query
from fdp.inspect import validate_materialized_asset


def materialize(names: Iterable[str] | None = None) -> None:
    assets = ordered_assets(names)
    materialize_assets(assets)


def materialize_assets(assets: list[Asset]) -> None:
    total = len(assets)
    count_width = len(str(total))
    asset_width = max((len(asset.key) for asset in assets), default=0)

    for index, asset in enumerate(assets, start=1):
        started_at = perf_counter()
        try:
            materialize_asset(asset)
        except Exception:
            print(
                format_materialize_status(
                    index,
                    total,
                    count_width,
                    asset_width,
                    asset,
                    "FAIL",
                    perf_counter() - started_at,
                ),
                flush=True,
            )
            raise
        print(
            format_materialize_status(
                index,
                total,
                count_width,
                asset_width,
                asset,
                "OK",
                perf_counter() - started_at,
            ),
            flush=True,
        )


def format_materialize_status(
    index: int,
    total: int,
    count_width: int,
    asset_width: int,
    asset: Asset,
    status: str,
    elapsed_seconds: float,
) -> str:
    return (
        f"[{index:>{count_width}}/{total:>{count_width}}] "
        f"{asset.key:<{asset_width}} {status} {elapsed_seconds:.1f}s"
    )


def materialize_asset(asset: Asset) -> None:
    if asset.kind == "python":
        materialize_python(asset)
        return
    materialize_sql(asset)


def materialize_sql(asset: Asset) -> None:
    query = asset.path.read_text(encoding="utf-8").strip()
    if not query:
        raise ValueError(f"SQL asset is empty: {asset.path}")

    if asset.resource == "bigquery":
        materialize_query(asset.key, query, schema=asset.schema)
        with db_connection() as conn:
            validate_materialized_asset(conn, asset)
            apply_asset_comments(conn, asset)
        return

    with db_connection() as conn:
        conn.execute(f"create schema if not exists {asset.schema}")
        conn.execute(f"create or replace table {asset.key} as {query}")
        validate_materialized_asset(conn, asset)
        apply_asset_comments(conn, asset)


def materialize_python(asset: Asset) -> None:
    module = load_module(asset.path)
    function_name = python_asset_function_name(asset.path)
    func = getattr(module, function_name, None)
    if func is None or not callable(func):
        raise ValueError(
            f"Python asset {asset.path} must define callable {function_name}"
        )

    result = func()
    if asset.python_materialization == "custom":
        if result is not None:
            raise TypeError(
                f"Python asset {asset.path} declares asset.materialization = custom "
                "and must return None"
            )
        with db_connection() as conn:
            validate_materialized_asset(conn, asset)
            apply_asset_comments(conn, asset)
        return

    if asset.python_materialization != "dataframe":
        raise TypeError(f"Invalid Python materialization mode for {asset.path}")
    if not isinstance(result, pl.DataFrame):
        raise TypeError(
            f"Python asset {asset.path} declares asset.materialization = "
            "dataframe and must return polars.DataFrame"
        )
    materialize_polars_frame(asset, result)


def materialize_polars_frame(asset: Asset, frame: pl.DataFrame) -> None:
    with db_connection() as conn:
        conn.execute(f"create schema if not exists {asset.schema}")
        conn.register("frame", frame)
        conn.execute(f"create or replace table {asset.key} as select * from frame")
        validate_materialized_asset(conn, asset)
        apply_asset_comments(conn, asset)


def apply_asset_comments(conn, asset: Asset) -> None:
    if asset.description:
        escaped = asset.description.replace("'", "''")
        conn.execute(f"comment on table {asset.key} is '{escaped}'")

    for column in asset.columns:
        escaped = column.description.replace("'", "''")
        conn.execute(f"comment on column {asset.key}.{column.name} is '{escaped}'")


def load_module(module_path: Path) -> ModuleType:
    module_name = module_name_from_path(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load asset module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_name_from_path(module_path: Path) -> str:
    sanitized = module_path.as_posix().replace("/", "_").replace(".", "_")
    return f"fdp_asset_{sanitized}"
