import os

import duckdb

DATA_DIR = os.getenv("DATA_DIR", "../data")


def query(sql):
    with duckdb.connect(database=f"{DATA_DIR}/local.duckdb") as con:
        return con.sql(sql).df()
