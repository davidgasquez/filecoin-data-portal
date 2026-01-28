import polars as pl

from fdp import dataset, query


@dataset(schema="demo", table="numbers")
def demo_numbers() -> None:
    query("create schema if not exists demo")
    query(
        "create or replace table demo.numbers as "
        "select * from (values (1), (2), (3), (4)) as t(value)"
    )


@dataset(schema="demo", table="numbers_sum", depends_on={"numbers": "demo_numbers"})
def demo_numbers_sum(numbers: pl.DataFrame) -> pl.DataFrame:
    return numbers.select(pl.sum("value").alias("total"))
