import os
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

import duckdb
import polars as pl

SYSTEM_SCHEMAS = ("information_schema", "pg_catalog")


def get_db_path(db_path: Path | str | None = None) -> Path:
    if db_path is None:
        return Path(os.environ.get("FDP_DB_PATH", "fdp.duckdb"))
    return Path(db_path)


@contextmanager
def db_connection(
    db_path: Path | str | None = None,
    *,
    read_only: bool = False,
) -> Iterator[duckdb.DuckDBPyConnection]:
    path = get_db_path(db_path)
    with duckdb.connect(path, read_only=read_only) as conn:
        yield conn


def sql(
    statement: str,
    params: list[object] | None = None,
    *,
    db_path: Path | str | None = None,
) -> None:
    cleaned = statement.strip()
    with db_connection(db_path) as conn:
        if params is None:
            conn.execute(cleaned)
            return
        conn.execute(cleaned, params)


def table(name: str, *, db_path: Path | str | None = None) -> pl.DataFrame:
    with db_connection(db_path, read_only=True) as conn:
        arrow_table = conn.execute(f"select * from {name}").fetch_arrow_table()
    return pl.DataFrame(arrow_table)


def table_exists(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    name: str,
) -> bool:
    row = conn.execute(
        "select 1 from information_schema.tables "
        "where table_schema = ? and table_name = ? limit 1",
        [schema, name],
    ).fetchone()
    return row is not None


class TableAsset(Protocol):
    key: str
    schema: str
    name: str


def ensure_tables_exist(
    conn: duckdb.DuckDBPyConnection,
    assets: Iterable[TableAsset],
) -> None:
    missing_assets = [
        asset.key
        for asset in assets
        if not table_exists(conn, asset.schema, asset.name)
    ]
    if missing_assets:
        missing = ", ".join(missing_assets)
        raise ValueError(
            "Assets are not materialized: "
            f"{missing}. Run `uv run --env-file .env fdp materialize` first."
        )


def materialized_tables(conn: duckdb.DuckDBPyConnection) -> list[tuple[str, str]]:
    return conn.execute(
        "select table_schema, table_name from information_schema.tables "
        "where table_schema not in (?, ?) order by 1, 2",
        list(SYSTEM_SCHEMAS),
    ).fetchall()


def quote_identifier(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def find_assets_root() -> Path:
    for parent in [Path.cwd(), *Path.cwd().parents]:
        candidate = parent / "assets"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("assets directory not found")
