import os
from pathlib import Path

import duckdb

from fdp.api import default_db_path, find_project_root, quote_identifier, quote_literal
from fdp.assets import main_assets


def export(out: Path | str | None = None) -> Path:
    source = default_db_path().resolve()
    target = (
        Path(out) if out is not None else find_project_root() / "build" / "fdp.duckdb"
    ).resolve()
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
            conn.execute(f"attach {quote_literal(str(source))} as src (read_only)")
            columns = conn.execute(
                "select t.table_name, t.comment, c.column_name, c.comment "
                "from duckdb_tables() t left join duckdb_columns() c "
                "using (database_name, schema_name, table_name) "
                "where database_name = 'src' and schema_name = 'main'"
            ).fetchall()
            missing = set(names) - {row[0] for row in columns}
            if missing:
                raise ValueError(f"Main assets not materialized: {sorted(missing)}")
            columns = [row for row in columns if row[0] in names]
            for name in names:
                table = f"main.{quote_identifier(name)}"
                conn.execute(f"create table {table} as select * from src.{table}")
            for name, table_comment in {(row[0], row[1]) for row in columns}:
                if table_comment is not None:
                    conn.execute(
                        f"comment on table main.{quote_identifier(name)} "
                        f"is {quote_literal(table_comment)}"
                    )
            for name, _, column, comment in columns:
                if comment is not None:
                    conn.execute(
                        f"comment on column main.{quote_identifier(name)}."
                        f"{quote_identifier(column)} is {quote_literal(comment)}"
                    )
            conn.execute("detach src")
            conn.execute("checkpoint")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
        temp.with_name(f"{temp.name}.wal").unlink(missing_ok=True)
    return target
