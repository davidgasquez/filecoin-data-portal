import os

import duckdb

DATA_DIR = os.getenv("DATA_DIR", "../../data")
DATABASE_PATH = os.getenv("DATABASE_PATH", f"{DATA_DIR}/database.duckdb")


def query(sql):
    with duckdb.connect(database=DATABASE_PATH) as con:
        return con.sql(sql).df()


def export(export_path):
    with duckdb.connect(database=DATABASE_PATH) as con:
        export_query = f"""
        -- set preserve_insertion_order = false;
        set temp_directory = '/tmp/temp.tmp';
        export database '{export_path}' (format 'parquet', compression 'zstd', row_group_size 1000000);
        """
        con.execute(export_query)
