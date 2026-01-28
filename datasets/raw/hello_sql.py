from fdp import dataset, query


@dataset
def hello_sql() -> None:
    """
    Silly example dataset running a SQL query.
    """
    query("create schema if not exists raw")
    query("create or replace table raw.hello_sql as select 1 as value")
