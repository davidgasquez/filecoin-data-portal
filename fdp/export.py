import os
from pathlib import Path

import duckdb

from fdp.api import default_db_path, find_project_root, quote_identifier
from fdp.assets import main_assets


def default_export_path() -> Path:
    return find_project_root() / "build" / "fdp.duckdb"


def sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def export(out: Path | str | None = None, db_path: Path | str | None = None) -> Path:
    source = (default_db_path() if db_path is None else Path(db_path)).resolve()
    target = (default_export_path() if out is None else Path(out)).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Database not found: {source}")
    if target == source or (target.exists() and target.samefile(source)):
        raise ValueError(f"Refusing to overwrite the working database: {source}")
    names = sorted(asset.name for asset in main_assets())
    if not names:
        raise ValueError("No main assets found.")

    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temp.unlink(missing_ok=True)
    try:
        with duckdb.connect(temp) as conn:
            conn.execute(f"attach {sql_string(str(source))} as src (read_only)")
            columns = conn.execute(
                "select t.table_name, t.comment, c.column_name, c.comment "
                "from duckdb_tables() t left join duckdb_columns() c "
                "using (database_name, schema_name, table_name) "
                "where database_name = 'src' and schema_name = 'main'"
            ).fetchall()
            missing = set(names) - {row[0] for row in columns}
            if missing:
                raise ValueError(f"Main assets not materialized: {sorted(missing)}")
            for name in names:
                table = f"main.{quote_identifier(name)}"
                conn.execute(f"create table {table} as select * from src.{table}")
            for name, table_comment in {(row[0], row[1]) for row in columns}:
                if name in names and table_comment is not None:
                    table = f"main.{quote_identifier(name)}"
                    conn.execute(
                        f"comment on table {table} is {sql_string(table_comment)}"
                    )
            for name, _, column, comment in columns:
                if name in names and comment is not None:
                    table = f"main.{quote_identifier(name)}"
                    conn.execute(
                        f"comment on column {table}.{quote_identifier(column)} "
                        f"is {sql_string(comment)}"
                    )
            conn.execute("detach src")
            conn.execute("checkpoint")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
        temp.with_name(f"{temp.name}.wal").unlink(missing_ok=True)
    return target
