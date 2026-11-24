from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import duckdb
import polars as pl

SYSTEM_SCHEMAS = ("information_schema", "pg_catalog")


def find_project_root() -> Path:
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / "assets").is_dir():
            return parent
    raise FileNotFoundError("assets directory not found")


def default_db_path() -> Path:
    return find_project_root() / "fdp.duckdb"


@contextmanager
def db_connection(
    db_path: Path | str | None = None,
    *,
    read_only: bool = False,
) -> Generator[duckdb.DuckDBPyConnection]:
    path = default_db_path() if db_path is None else Path(db_path)
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
        return conn.sql(f"select * from {name}").pl()


def table_exists(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    name: str,
) -> bool:
    row = conn.execute(
        "select 1 from information_schema.tables "
        "where table_schema = ? and table_name = ? limit 1",
        [schema, name],
    ).fetchall()
    return bool(row)


def materialized_tables(conn: duckdb.DuckDBPyConnection) -> list[tuple[str, str]]:
    return conn.execute(
        "select table_schema, table_name from information_schema.tables "
        "where table_schema not in (?, ?) order by 1, 2",
        list(SYSTEM_SCHEMAS),
    ).fetchall()


def quote_identifier(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def quote_literal(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def quote_table_key(schema: str, name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(name)}"
