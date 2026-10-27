# asset.description = Current Filecoin Pay rail snapshot from the Filecoin API.
# https://api.filecoin.io/openapi.json

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = rail_id | Filecoin Pay rail identifier.
# asset.column = state | Rail lifecycle state (active, terminated, finalized).
# asset.column = payer | Payer address.
# asset.column = payee | Payee address.
# asset.column = token | ERC20 token address.
# asset.column = operator | Operator address.
# asset.column = validator | Validator address.
# asset.column = service_fee_recipient | Service fee recipient address.
# asset.column = commission_rate_bps | Commission rate in basis points.
# asset.column = payment_rate | Current rate, in token base units per epoch.
# asset.column = lockup_period | Current lockup period, in epochs.
# asset.column = lockup_fixed | Current fixed lockup, in token base units.
# asset.column = end_epoch | Termination end epoch, if any.
# asset.column = terminated_by | Address that terminated the rail, if any.
# asset.column = settled_up_to | Epoch the rail is settled up to.
# asset.column = total_settled_amount | Settled amount, in token base units.
# asset.column = total_net_payee_amount | Settled amount net to payee.
# asset.column = total_one_time_amount | One-time payments, in token base units.
# asset.column = total_one_time_net_payee_amount | One-time payments net to payee.
# asset.column = data_set_id | Warm Storage data set paid by the rail, if any.
# asset.column = created_at_block | Creation block number.
# asset.column = indexed_block | API indexer head before paging, not the state block.
# asset.column = observed_at | UTC fetch timestamp.

# asset.not_null = rail_id
# asset.not_null = state
# asset.not_null = payment_rate
# asset.not_null = settled_up_to
# asset.not_null = total_settled_amount
# asset.not_null = indexed_block
# asset.not_null = observed_at
# asset.unique = rail_id

import datetime as dt

import httpx
import polars as pl

URL = "https://api.filecoin.io/mainnet"
AMOUNT = pl.Decimal(38, 0)
COLUMNS = {
    "railId": ("rail_id", pl.Int64),
    "state": ("state", pl.String),
    "payer": ("payer", pl.String),
    "payee": ("payee", pl.String),
    "token": ("token", pl.String),
    "operator": ("operator", pl.String),
    "validator": ("validator", pl.String),
    "serviceFeeRecipient": ("service_fee_recipient", pl.String),
    "commissionRateBps": ("commission_rate_bps", pl.Int64),
    "paymentRate": ("payment_rate", AMOUNT),
    "lockupPeriod": ("lockup_period", pl.Int64),
    "lockupFixed": ("lockup_fixed", AMOUNT),
    "endEpoch": ("end_epoch", pl.Int64),
    "terminatedBy": ("terminated_by", pl.String),
    "settledUpTo": ("settled_up_to", pl.Int64),
    "totalSettledAmount": ("total_settled_amount", AMOUNT),
    "totalNetPayeeAmount": ("total_net_payee_amount", AMOUNT),
    "totalOneTimeAmount": ("total_one_time_amount", AMOUNT),
    "totalOneTimeNetPayeeAmount": ("total_one_time_net_payee_amount", AMOUNT),
    "dataSetId": ("data_set_id", pl.Int64),
    "createdAtBlock": ("created_at_block", pl.Int64),
}


def rails() -> pl.DataFrame:
    observed_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    with httpx.Client(base_url=URL, timeout=60) as client:
        status = client.get("/status").raise_for_status().json()
        rows, cursor = [], None
        while True:
            params = {"limit": 200} | ({"cursor": cursor} if cursor else {})
            page = client.get("/rails", params=params).raise_for_status().json()
            rows += page["data"]
            cursor = page["nextCursor"]
            if cursor is None:
                break

    addresses = [
        "payer",
        "payee",
        "token",
        "operator",
        "validator",
        "service_fee_recipient",
        "terminated_by",
    ]
    return (
        pl
        .DataFrame(rows, infer_schema_length=None)
        .select(pl.col(k).cast(t).alias(name) for k, (name, t) in COLUMNS.items())
        .with_columns(
            pl.col(addresses).str.to_lowercase(),
            indexed_block=pl.lit(
                status["data"]["indexers"][0]["latest"]["blockNumber"], pl.Int64
            ),
            observed_at=pl.lit(observed_at),
        )
        .sort("rail_id", descending=True)
    )
