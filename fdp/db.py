import os

import duckdb

DATA_DIR = os.getenv("DATA_DIR", "../../data")


def query(sql):
    with duckdb.connect(database=f"{DATA_DIR}/local.duckdb") as con:
        return con.sql(sql).df()


def export(db_path, export_path):
    with duckdb.connect(database=f"{db_path}") as con:
        export_query = f"""
        set preserve_insertion_order = false;
        set memory_limit = '10GB';
        set temp_directory = '/tmp/temp.tmp';
        export database '{export_path}' (format 'parquet', compression 'zstd', row_group_size 1000000);
        """
        con.execute(export_query)
