import importlib.util
from time import perf_counter
from typing import assert_never

import polars as pl
import pyarrow as pa

from fdp.api import (
    db_connection,
    default_db_path,
    quote_identifier,
    quote_literal,
    quote_table_key,
    table_exists,
)
from fdp.assets import Asset, load_assets
from fdp.inspect import validate_materialized_asset
from fdp.resources import lily
from fdp.selectors import expand_asset_selectors


def materialize(selectors: list[str], *, include_dependencies: bool = False) -> None:
    loaded = load_assets()
    if selectors:
        selected = set(expand_asset_selectors(loaded, selectors))
    else:
        selected = set(loaded.assets)
    if include_dependencies:
        stack = list(selected)
        while stack:
            for dependency in loaded.assets[stack.pop()].depends:
                if dependency not in selected:
                    selected.add(dependency)
                    stack.append(dependency)
    assets = [loaded.assets[key] for key in loaded.ordered_keys if key in selected]
    if not include_dependencies:
        validate_materialized_dependencies(assets, loaded.assets)
    materialize_assets(assets)


def validate_materialized_dependencies(
    assets: list[Asset], all_assets: dict[str, Asset]
) -> None:
    dependencies = sorted(
        {d for a in assets for d in a.depends} - {a.key for a in assets}
    )
    if not dependencies:
        return

    with db_connection() as conn:
        missing_tables = [
            key
            for key in dependencies
            if not table_exists(conn, all_assets[key].schema, all_assets[key].name)
        ]

    if missing_tables:
        raise ValueError(
            "Cannot materialize selected assets because these dependencies are "
            f"not materialized: {', '.join(missing_tables)}. Materialize them "
            "first or rerun with --with-deps."
        )


def materialize_assets(assets: list[Asset]) -> None:
    total = len(assets)
    count_width = len(str(total))
    asset_width = max((len(asset.key) for asset in assets), default=0)
    kept_existing: list[str] = []

    for index, asset in enumerate(assets, start=1):
        label = f"[{index:>{count_width}}/{total}] {asset.key:<{asset_width}}"
        print(f"{label} RUN", flush=True)
        started_at = perf_counter()
        try:
            materialize_asset(asset)
        except Exception as exc:
            elapsed = perf_counter() - started_at
            if not can_keep_existing(asset):
                print(f"{label} FAIL {elapsed:.1f}s", flush=True)
                raise
            kept_existing.append(asset.key)
            print(f"{label} KEEP_EXISTING {elapsed:.1f}s", flush=True)
            print(f"  {type(exc).__name__}: {exc}", flush=True)
            continue
        print(f"{label} OK {perf_counter() - started_at:.1f}s", flush=True)

    if kept_existing:
        print("Kept existing tables after refresh failures:", flush=True)
        for key in kept_existing:
            print(f"  - {key}", flush=True)


def can_keep_existing(asset: Asset) -> bool:
    if not asset.keep_existing_on_failure:
        return False
    if not default_db_path().exists():
        return False
    with db_connection(read_only=True) as conn:
        return table_exists(conn, asset.schema, asset.name)


def materialize_asset(asset: Asset) -> None:
    source: str | pa.Table | None
    match asset.runtime:
        case "sql":
            source = asset.path.read_text(encoding="utf-8").strip()
        case "lily":
            source = lily.query_arrow(asset.path.read_text(encoding="utf-8").strip())
        case "dataframe":
            result = call_python_asset(asset)
            if not isinstance(result, pl.DataFrame):
                raise TypeError(
                    f"Python asset {asset.path} declares asset.materialization = "
                    "dataframe and must return polars.DataFrame"
                )
            source = result.to_arrow()
        case "custom":
            if call_python_asset(asset) is not None:
                raise TypeError(
                    f"Python asset {asset.path} declares asset.materialization = "
                    "custom and must return None"
                )
            source = None
        case _:
            assert_never(asset.runtime)

    with db_connection() as conn:
        if isinstance(source, pa.Table):
            conn.register("asset_result", source)
            source = "select * from asset_result"
        if source is not None:
            conn.execute(
                f"create schema if not exists {quote_identifier(asset.schema)}"
            )
            conn.execute(
                f"create or replace table {quote_table_key(asset.schema, asset.name)} "
                f"as {source}"
            )
        validate_materialized_asset(conn, asset)
        apply_asset_comments(conn, asset)


def call_python_asset(asset: Asset) -> object:
    module_name = (
        f"fdp_asset_{asset.path.as_posix().replace('/', '_').replace('.', '_')}"
    )
    spec = importlib.util.spec_from_file_location(module_name, asset.path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load asset module: {asset.path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, asset.path.stem, None)
    if not callable(func):
        raise ValueError(
            f"Python asset {asset.path} must define callable {asset.path.stem}"
        )
    return func()


def apply_asset_comments(conn, asset: Asset) -> None:
    quoted_asset_key = quote_table_key(asset.schema, asset.name)
    if asset.description:
        conn.execute(
            f"comment on table {quoted_asset_key} is {quote_literal(asset.description)}"
        )

    for column in asset.columns:
        conn.execute(
            "comment on column "
            f"{quoted_asset_key}.{quote_identifier(column.name)} "
            f"is {quote_literal(column.description)}"
        )
