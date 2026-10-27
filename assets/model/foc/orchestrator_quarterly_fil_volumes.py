# asset.description = FIL settlements priced by Filecoin Pay fee-auction prints.

# asset.depends = raw.blockscout_fee_auction_traces
# asset.depends = raw.contracts_registry
# asset.depends = raw.riba_eth_logs
# asset.depends = raw.riba_eth_logs_decoded
# asset.depends = model.foc_orchestrator_bindings
# asset.depends = model.foc_orchestrator_settlements
# asset.depends = model.foc_service_quarters
# asset.depends = model.pay_rails

# asset.materialization = dataframe

# asset.column = quarter | Solstice quarter whose qualifying prints priced the FIL.
# asset.column = orchestrator | ServiceOrchestrator identity address.
# asset.column = fil_volume_atto_fil | FIL priced into the quarter, in attoFIL.
# asset.column = fil_volume_atto_usd | FIL priced into the quarter, in atto-USD.
# asset.column = fil_pending_atto_fil | FIL settled by quarter end, not yet priced.

# asset.not_null = quarter
# asset.not_null = orchestrator

"""FIP-0118 (c92ec60) §2.3 FIL pricing rule. NULL means unknown, never zero."""

import functools
import json
from typing import Any

import polars as pl

import fdp

ZERO = "0x0000000000000000000000000000000000000000"
BURN_FOR_FEES = (
    "0x1a257300"  # burnForFees(address token, address to, uint256 requested)
)
BALANCE_OF = "0x70a08231"
TRANSFER = "0xa9059cbb"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BURN_ACTOR = "0xff00000000000000000000000000000000000063"
SEED = 5  # Band seeding: median of the first five candidate prints.
LAST = 1 << 62  # Past every log index of a block.
BIG = pl.Decimal(38, 0)
SCHEMA = {
    "quarter": pl.Int64,
    "orchestrator": pl.String,
    "fil_volume_atto_fil": BIG,
    "fil_volume_atto_usd": BIG,
    "fil_pending_atto_fil": BIG,
}


def parse_claims(trace: list[dict], pays: set, logs: list[tuple]) -> list[dict]:
    """Successful burnForFees calls (FilecoinPayV1.sol: burns msg.value, sends
    transferOut's balance delta) with the Transfer log index of their send."""
    calls = {tuple(t["traceAddress"]): t for t in trace if t["type"] == "call"}
    failed = [tuple(t["traceAddress"]) for t in trace if t.get("error")]  # Any type.

    def ok(path: tuple) -> bool:
        return not any(path[: len(f)] == f for f in failed)

    def action(path: tuple) -> dict:
        return calls.get(path, {}).get("action", {})

    def output(path: tuple) -> str:
        return (calls.get(path, {}).get("result") or {}).get("output") or ""

    def is_call(path: tuple, selector: str) -> bool:
        a = action(path)
        return ok(path) and a["callType"] == "call" and a["input"][:10] == selector

    # Successful Pay token sends, in execution order, pair 1:1 with Transfer logs.
    sends = [
        p for p in sorted(calls) if is_call(p, TRANSFER) and action(p)["from"] in pays
    ]
    tokens = [action(p)["to"] for p in sends]
    paired = tokens == [t for t, _ in logs]
    log_of = dict(zip(sends, [li for _, li in logs], strict=False)) if paired else {}

    claims: list[dict[str, Any]] = []
    for path in sorted(calls):
        a = action(path)
        if not (is_call(path, BURN_FOR_FEES) and a["to"] in pays):
            continue
        value, token = int(a["value"], 16), "0x" + a["input"][34:74]
        children = [(*path, i) for i in range(4)]
        burn, before, send, after = (action(c) for c in children)
        expected = (
            calls[path].get("subtraces") == 4
            and burn.get("to") == BURN_ACTOR
            and int(burn.get("value", "0x0"), 16) == value
            and all(
                c.get("to") == token and c.get("input", "")[:10] == s
                for c, s in (
                    (before, BALANCE_OF),
                    (send, TRANSFER),
                    (after, BALANCE_OF),
                )
            )
            and output(children[1])
            and output(children[3])
        )
        balances = [int(output(children[i]), 16) for i in (1, 3)] if expected else None
        claims.append({
            "contract": a["to"],
            "token": token,
            "claim": value,
            "lot": balances[0] - balances[1] if balances else None,
            "log_index": log_of.get(children[2]),
            "trace_address": ".".join(map(str, path)),
        })
    return claims


def lower(value: Any) -> Any:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return {k: lower(v) for k, v in value.items()}
    if isinstance(value, list):
        return [lower(v) for v in value]
    return value


def load_claims(
    conn: Any, pays: set, start: int, as_of: int
) -> tuple[list[dict[str, Any]], list[tuple[int, int]], int | None]:
    """Claims in [start, as_of], positions where the print sequence becomes
    uncertain, and the discovery coverage."""
    traces = conn.execute(
        "select transaction_hash, block_number, block_hash, trace, scanned_to_block "
        "from raw.blockscout_fee_auction_traces"
    ).fetchall()
    logs: dict[str, list] = {}
    for tx, block, block_hash, token, li in conn.execute(
        """
        select distinct
            lower(transactionHash), blockNumber::bigint, lower(blockHash),
            lower(address), logIndex::bigint
        from raw.riba_eth_logs
        where lower(topics[1]) = ? and not removed
          and lower(topics[2]) in (
              select '0x' || repeat('0', 24) || substr(unnest(?::varchar[]), 3)
          )
          and blockNumber::bigint between ? and ?
        order by 5
        """,
        [TRANSFER_TOPIC, sorted(pays), start, as_of],
    ).fetchall():
        logs.setdefault(tx, []).append((block, block_hash, token, li))
    traced = {t[0] for t in traces}
    # A RIBA candidate missing from the trace table (new or refreshed day) is unseen.
    unknown = [(rows[0][0], -1) for tx, rows in logs.items() if tx not in traced]
    claims: list[dict[str, Any]] = []
    for tx, block, block_hash, trace, _ in traces:
        if tx is None or not start <= block <= as_of:
            continue
        tx_logs = logs.get(tx, [])
        if trace is None or any(h != block_hash for _, h, _, _ in tx_logs):
            unknown.append((block, -1))  # Untraced or reorged: may hide a claim.
            continue
        found = parse_claims(
            lower(json.loads(trace)), pays, [(t, li) for _, _, t, li in tx_logs]
        )
        claims += [{**c, "transaction_hash": tx, "block": block} for c in found]
    return claims, unknown, min((t[4] for t in traces), default=None)


def orchestrator_quarterly_fil_volumes() -> pl.DataFrame:
    with fdp.db_connection(read_only=True) as conn:
        quarters = conn.execute(
            "select quarter, start_block, end_block, as_of_block, "
            "bound_volume_atto_usd::varchar from model.foc_service_quarters "
            "order by quarter"
        ).fetchall()
        sra = conn.execute(
            "select event_name, block_number, args from raw.riba_eth_logs_decoded "
            "where contract_name = 'service_rewards_actor' "
            "and event_name in ('AdmittedListsUpdated', 'PricingParamsUpdated') "
            "order by block_number, log_index"
        ).fetchall()
        pays = {
            r[0]
            for r in conn.execute(
                "select lower(address) from raw.contracts_registry "
                "where contract_name = 'filecoin_pay_v1'"
            ).fetchall()
        }
        decimals = dict(
            conn.execute(
                "select token, any_value(token_decimals) from model.pay_rails "
                "where token_decimals is not null group by 1"
            ).fetchall()
        )
        if not quarters:
            return pl.DataFrame(schema=SCHEMA)
        a, as_of = quarters[0][1], quarters[-1][3]
        # Only facts within contiguous coverage; later ones are not yet comparable.
        fil = conn.execute(
            "select contract, block_number, log_index, amount::varchar, orchestrator, "
            "payer, operator from model.foc_orchestrator_settlements "
            "where token = ? and block_number <= ?",
            [ZERO, as_of],
        ).fetchall()
        unknown_spans = conn.execute(
            "select payer, operator, orchestrator, start_block, effective_to_block, "
            "effective_to_log_index from model.foc_orchestrator_bindings "
            "where effective_from_block is null and start_block <= ?",
            [as_of],
        ).fetchall()
        claims, unknown_at, scanned_to = load_claims(conn, pays, a, as_of)

    # Positions are (block, log_index): Filecoin log indexes are tipset-wide and
    # follow execution order, so they order prints and settlements within a block.
    length = quarters[0][2] - quarters[0][1] + 1

    def quarter_of(block: int) -> int:
        return (block - a) // length + 1

    start = {r[0]: r[1] for r in quarters}
    end = {r[0]: (min(r[2], r[3]), LAST) for r in quarters}  # Last covered position.
    bound: dict[int, int | None] = {
        r[0]: None if r[4] is None else int(r[4]) for r in quarters
    }

    # Admitted lists and pricing params for Q: the latest event before Start(Q).
    contracts: dict[int, set] = {}
    stables: dict[int, set] = {}
    params: dict[int, dict] = {}
    for qn, s in start.items():
        for name, block, args in sra:
            if block < s:
                x = json.loads(args)
                if name == "AdmittedListsUpdated":
                    contracts[qn] = {c.lower() for c in x["filecoinPayContracts"]}
                    stables[qn] = {c.lower() for c in x["stablecoins"]}
                else:
                    params[qn] = x
        if qn not in contracts or contracts[qn] - pays:
            # No admitted lists, or an admitted contract without ABI: unseen scope.
            unknown_at.append((s, -1))
    if scanned_to is None or scanned_to < as_of:
        unknown_at.append((a if scanned_to is None else scanned_to + 1, -1))

    # N(Q): every cleared claim on contracts admitted for Q, whatever token or lot.
    n = {
        qn: sum(
            quarter_of(c["block"]) == qn and c["contract"] in contracts.get(qn, set())
            for c in claims
        )
        for qn in start
    }

    def min_lot(qn: int) -> int | None:
        p = params.get(qn)
        if p is None:
            return None
        if qn == 1 or n[qn - 1] == 0:
            return int(p["minLotFloor"])
        previous = bound[qn - 1]
        if previous is None:
            return None  # BoundVolume(Q-1) is only final once Q-1 binds.
        num, den = int(p["minLotAlphaNum"]), int(p["minLotAlphaDen"])
        return max(int(p["minLotFloor"]), num * previous // (den * n[qn - 1]))

    def compare(x: tuple, y: tuple) -> int:  # Rates (lotUsd, claimFil), cross-mult.
        return (x[0] * y[1] > y[0] * x[1]) - (x[0] * y[1] < y[0] * x[1])

    def position(c: dict) -> tuple:
        return (c["block"], -1 if c["log_index"] is None else c["log_index"])

    settlements: list[dict[str, Any]] = []
    for contract, block, li, amount, orch, payer, operator in fil:
        # A span with unknown start may back-cover the pair from its quarter start.
        maybe = {
            o
            for p_, op, o, sb, tb, tl in unknown_spans
            if (p_, op) == (payer, operator)
            and ((start[max(quarter_of(sb), 1)] if sb >= a else a), -1) <= (block, li)
            and (tb is None or (block, li) < (tb, tl))
        }
        settlements.append({
            "contract": contract,
            "pos": (block, li),
            "amount": int(amount),
            "orch": orch,
            "maybe": maybe,
            "print": None,
        })

    failure = min(unknown_at, default=None)
    seed: list[tuple[int, int]] = []
    reference: tuple[int, int] | None = None
    prints: list[dict[str, Any]] = []
    pending = settlements
    for c in sorted(claims, key=position):
        pos, qn = position(c), quarter_of(c["block"])
        if failure is not None and pos >= failure:
            break
        if c["contract"] not in contracts[qn] or c["token"] not in stables[qn]:
            continue
        dec, threshold = decimals.get(c["token"]), min_lot(qn)
        if c["lot"] is None or dec is None or dec > 18 or threshold is None:
            failure = pos  # Cannot tell whether this claim is a candidate.
            break
        lot_usd = c["lot"] * 10 ** (18 - dec)
        if lot_usd < threshold:
            continue
        # Zero FIL is outside the band once a finite reference exists.
        if c["claim"] == 0 and reference is not None:
            continue
        if c["log_index"] is None or c["claim"] == 0:
            failure = pos  # Candidate without execution position or with no rate.
            break
        rate = (lot_usd, c["claim"])
        if reference is None:
            seed.append(rate)
            if len(seed) == SEED:  # Seed prints price nothing.
                reference = sorted(seed, key=functools.cmp_to_key(compare))[SEED // 2]
            continue
        l0, c0 = reference
        bps = int(params[qn]["priceBand"])
        if abs(rate[0] * c0 - l0 * rate[1]) * 10000 > bps * l0 * rate[1]:
            continue  # Outside PRICE_BAND (inclusive, basis points).
        reference = rate
        prints.append({**c, "quarter": qn, "rate": rate, "pos": pos})
        for s in pending:
            if s["pos"] < pos:  # Strictly after the settlement.
                s["print"] = len(prints) - 1
        pending = [s for s in pending if s["print"] is None]

    orchestrators = {s["orch"] for s in settlements} | {
        o for s in settlements for o in s["maybe"]
    }
    rows = []
    for qn in start:
        for o in sorted(orchestrators - {None}):
            mine = [s for s in settlements if s["orch"] == o or o in s["maybe"]]
            # With an uncertain sequence by Q's end, unpriced FIL could still land in Q.
            is_open = (
                failure is not None
                and failure <= end[qn]
                and any(s["print"] is None and s["pos"] <= end[qn] for s in mine)
            )
            priced = [
                s
                for s in mine
                if s["print"] is not None and prints[s["print"]]["quarter"] == qn
            ]
            # Contract admission is the pricing quarter's (FIP-0118 §2.2 step 5).
            counted = [s for s in priced if s["contract"] in contracts.get(qn, set())]
            atto_fil = atto_usd = 0
            for i in sorted({s["print"] for s in counted}):
                period = sum(s["amount"] for s in counted if s["print"] == i)
                lot_usd, claim = prints[i]["rate"]
                atto_fil += period
                atto_usd += period * lot_usd // claim  # One floor per pricing period.
            waiting = [
                s
                for s in mine
                if s["pos"] <= end[qn]
                and (s["print"] is None or prints[s["print"]]["pos"] > end[qn])
            ]
            is_unknown = is_open or any(s["orch"] != o for s in priced)
            rows.append({
                "quarter": qn,
                "orchestrator": o,
                "fil_volume_atto_fil": None if is_unknown else atto_fil,
                "fil_volume_atto_usd": None if is_unknown else atto_usd,
                "fil_pending_atto_fil": None
                if is_open or any(s["orch"] != o for s in waiting)
                else sum(s["amount"] for s in waiting),
            })
    return pl.DataFrame(rows, schema=SCHEMA).sort(
        ["quarter", "orchestrator"], descending=[True, False]
    )
