import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, getcontext
from typing import Any

import dagster as dg
import httpx
import pandas as pd
from dagster_duckdb import DuckDBResource

DEFAULT_URL = "https://api.goldsky.com/api/public/project_cmb9tuo8r1xdw01ykb8uidk7h/subgraphs/filecoin-pay-mainnet-tim/1.2.0/gn"
HEADERS = {"Content-Type": "application/json", "User-Agent": "curl"}
PAGE_SIZE = 1000

getcontext().prec = 50


def gql(
    url: str, query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    body: dict[str, Any] = {"query": query}
    if variables:
        body["variables"] = variables

    r = httpx.post(url, json=body, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], indent=2))

    return data["data"]


def _to_date(ts_seconds: str) -> date:
    return datetime.fromtimestamp(int(ts_seconds), tz=timezone.utc).date()


def fetch_accounts(url: str, page_size: int) -> list[dict[str, Any]]:
    query = """
    query Accounts($first: Int!, $last: Bytes) {
      accounts(
        first: $first
        where: { id_gt: $last }
        orderBy: id
        orderDirection: asc
      ) {
        id
        userTokens { lockupRate }
        payerRails { state createdAt }
      }
    }
    """

    out: list[dict[str, Any]] = []
    last = "0x00"
    while True:
        data = gql(url, query, {"first": page_size, "last": last})["accounts"]
        if not data:
            break
        out.extend(data)
        last = data[-1]["id"]
    return out


def fetch_daily_token_metrics(url: str, page_size: int) -> list[dict[str, Any]]:
    query = """
    query DailyTokenMetrics($first: Int!, $last: Bytes) {
      dailyTokenMetrics(
        first: $first
        where: { id_gt: $last, token_: { symbol: "USDFC" } }
        orderBy: id
        orderDirection: asc
      ) {
        id
        timestamp
        settledAmount
      }
    }
    """

    out: list[dict[str, Any]] = []
    last = "0x00"
    while True:
        data = gql(url, query, {"first": page_size, "last": last})["dailyTokenMetrics"]
        if not data:
            break
        out.extend(data)
        last = data[-1]["id"]
    return out


def build_total_active_payers(
    accounts: list[dict[str, Any]],
) -> list[tuple[date, Decimal]]:
    counts: dict[Any, int] = {}
    for account in accounts:
        payer_rails = account.get("payerRails") or []
        if not payer_rails:
            continue

        has_active_rail = any(
            str(r["state"]).upper() in ("ACTIVE", "0") for r in payer_rails
        )
        if not has_active_rail:
            continue

        has_positive_lockup = any(
            int(t["lockupRate"]) > 0 for t in account.get("userTokens") or []
        )
        if not has_positive_lockup:
            continue

        earliest_created_at = min(int(r["createdAt"]) for r in payer_rails)
        d = _to_date(str(earliest_created_at))
        counts[d] = counts.get(d, 0) + 1

    if not counts:
        return []

    start = min(counts)
    end = max(counts)

    values: list[tuple] = []
    running = 0
    current = start
    while current <= end:
        running += counts.get(current, 0)
        values.append((current, Decimal(running)))
        current += timedelta(days=1)

    return values


def build_total_usdfc_settled(
    metrics: list[dict[str, Any]],
) -> list[tuple[date, Decimal]]:
    scale = Decimal(10) ** 18
    daily: dict[Any, Decimal] = {}

    for row in metrics:
        d = _to_date(row["timestamp"])
        amt = Decimal(row["settledAmount"])
        daily[d] = daily.get(d, Decimal(0)) + amt

    if not daily:
        return []

    start = min(daily)
    end = max(daily)

    values: list[tuple] = []
    running = Decimal(0)
    current = start
    while current <= end:
        running += daily.get(current, Decimal(0))
        values.append((current, running / scale))
        current += timedelta(days=1)

    return values


def build_foc_metrics_df(
    accounts: list[dict[str, Any]],
    daily_token_metrics: list[dict[str, Any]],
) -> pd.DataFrame:
    active = build_total_active_payers(accounts)
    settled = build_total_usdfc_settled(daily_token_metrics)

    active_map = {d: v for d, v in active}
    settled_map = {d: v for d, v in settled}

    all_dates = sorted(set(active_map) | set(settled_map))
    if not all_dates:
        return pd.DataFrame(
            {
                "date": pd.Series(dtype="datetime64[ns]"),
                "total_active_payers": pd.Series(dtype="object"),
                "total_usdfc_settled": pd.Series(dtype="object"),
            }
        )

    df = pd.DataFrame(
        {
            "date": all_dates,
            "total_active_payers": [active_map.get(d) for d in all_dates],
            "total_usdfc_settled": [settled_map.get(d) for d in all_dates],
        }
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


@dg.asset(compute_kind="python")
def goldsky_foc_metrics(
    context: dg.AssetExecutionContext, duckdb: DuckDBResource
) -> dg.MaterializeResult:
    accounts = fetch_accounts(DEFAULT_URL, PAGE_SIZE)
    daily_token_metrics = fetch_daily_token_metrics(DEFAULT_URL, PAGE_SIZE)

    df = build_foc_metrics_df(accounts, daily_token_metrics)

    asset_name = context.asset_key.to_user_string()
    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.shape[0]} rows to raw.{asset_name}")
    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})
