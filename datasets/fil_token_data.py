from datetime import date
from pathlib import Path

import duckdb
import httpx

BASE_URL = (
    "https://coincodex.com/api/coincodexcoins/get_historical_data_by_slug/filecoin"
)
START_DATE = "2020-01-01"


def fetch(start: str, end: str) -> list[dict]:
    r = httpx.get(f"{BASE_URL}/{start}/{end}", timeout=30.0)
    r.raise_for_status()
    return r.json()["data"]


def main() -> None:
    end_date = date.today().isoformat()
    rows = fetch(START_DATE, end_date)
    assert rows, "No rows returned"

    db_path = Path(__file__).resolve().parents[1] / "fdp.duckdb"

    with duckdb.connect(str(db_path)) as con:
        con.execute("create schema if not exists raw")
        con.execute(
            """
            create or replace table raw.fil_token_data as
            select
                r.* replace (
                    cast(r.time_start as timestamp) as time_start,
                    cast(r.time_end as timestamp) as time_end
                )
            from unnest(?) as t(r)
            order by time_start
            """,
            [rows],
        )

    print(f"Wrote {len(rows)} rows to {db_path} (table raw.fil_token_data)")


if __name__ == "__main__":
    main()
