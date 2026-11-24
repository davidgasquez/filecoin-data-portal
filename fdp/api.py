from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import duckdb


def find_project_root() -> Path:
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / "assets").is_dir():
            return parent
    raise FileNotFoundError("assets directory not found")


def default_db_path() -> Path:
    return find_project_root() / "fdp.duckdb"


@contextmanager
def db_connection(*, read_only: bool = False) -> Generator[duckdb.DuckDBPyConnection]:
    with duckdb.connect(default_db_path(), read_only=read_only) as conn:
        yield conn


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


def quote_identifier(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def quote_literal(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def quote_table_key(schema: str, name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(name)}"
