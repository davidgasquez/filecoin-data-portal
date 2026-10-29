# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.1"]
# ///
# ruff: file-ignore[line-too-long] -- keep the SQL field lists readable as query fragments.
"""Prepare local-only FOC page inputs from a read-only DuckDB snapshot.

Adapted from the supplied foc-explorer/build.py. JSON is an intermediate build
artifact, not an API or published dataset. Astro renders it into static pages.
Run from web: uv run scripts/foc.py [--source /path/to/fdp.duckdb]
"""

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = os.environ.get("FDP_DB", str(ROOT.parent / "fdp.duckdb"))
EPOCHS_PER_DAY = 2880
EPOCHS_PER_MONTH = EPOCHS_PER_DAY * 30
LATEST_EVENTS = 50

TABLES = [
    "providers",
    "data_sets",
    "rails",
    "payments",
    "daily_provider_quality",
    "daily_operator_metrics",
    "service_orchestrators",
    "orchestrator_quarters",
    "service_quarters",
]

NETWORK_COLUMNS = """
    date,
    filecoin_pay_gross_payment_volume_run_rate_usd as run_rate,
    filecoin_pay_network_fee_arr_usd as fee_arr,
    filecoin_pay_active_rails as active_rails,
    filecoin_pay_active_payers as active_payers,
    filecoin_pay_active_operators as active_operators,
    filecoin_pay_paid_usd as paid,
    warm_storage_billing_data_sets as billing_data_sets,
    warm_storage_billing_payers as billing_payers,
    warm_storage_new_billing_data_sets as new_data_sets,
    warm_storage_stored_bytes as stored_bytes,
    usdfc_supply
"""


def ts(col: str) -> str:
    return f"epoch({col})::bigint"


def connect(source: str) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("set TimeZone = 'UTC'")
    source = str(Path(source).resolve()).replace("'", "''")
    con.execute(f"attach '{source}' as fdp (read_only)")
    for t in TABLES:
        cutoff = (
            " where date < current_date"
            if t.startswith("daily_") or t == "payments"
            else ""
        )
        con.execute(f"create table {t} as select * from fdp.main.{t}{cutoff}")
    con.execute(
        f"""create table network as
        select {NETWORK_COLUMNS} from fdp.main.daily_network_metrics
        where date >= '2025-11-01' and date < current_date order by date"""
    )
    con.execute("detach fdp")
    return con


def model(con: duckdb.DuckDBPyConnection) -> None:
    """Derive explorer-friendly tables (amounts in token units, timestamps in epoch seconds)."""
    con.execute(f"""
    create table r as
    select
        rail_id as id,
        payer, payee, operator, validator, service_fee_recipient as fee_recipient,
        service, token, coalesce(token_symbol, 'Unknown') as token_symbol,
        is_stablecoin as stable, is_arr_eligible as eligible,
        commission_rate_bps as commission_bps,
        state, data_set_id, epoch(api_observed_at)::bigint as api_observed_at,
        (state = 'active' or (state = 'terminated' and terminated_end_at > api_observed_at)) as streaming,
        (payment_rate / pow(10, token_decimals))::double as rate_epoch,
        payment_rate / pow(10, token_decimals) * {EPOCHS_PER_MONTH} as rate_month,
        lockup_period as lockup_epochs,
        lockup_fixed / pow(10, token_decimals) as lockup_fixed,
        total_settled_amount / pow(10, token_decimals) as settled,
        total_net_payee_amount / pow(10, token_decimals) as settled_net,
        total_one_time_amount / pow(10, token_decimals) as one_time,
        total_one_time_net_payee_amount / pow(10, token_decimals) as one_time_net,
        settled_up_to,
        created_block, created_transaction_hash as created_tx, {ts("created_at")} as created_at,
        terminated_block, terminated_transaction_hash as terminated_tx, terminated_by,
        terminated_end_epoch, {ts("terminated_at")} as terminated_at, {ts("terminated_end_at")} as terminated_end_at
    from rails
    """)
    # Dealbot payers: stablecoin rails that are not ARR eligible (see FDP model.pay_rails).
    con.execute(
        "create table dealbot as select distinct payer from r where stable and not eligible"
    )
    con.execute("""
    create table p as
    select
        provider_id as id, name, description, provider_address as address, payee,
        is_provider_active as active, is_endorsed as endorsed, is_fwss_approved as approved,
        is_removed as removed, offers_pdp_storage as offers_pdp, product_type,
        service_url, location, location_country_code as country, location_region as region, location_city as city,
        payment_token_address as payment_token,
        -- The registry uses address(0) for FIL; ERC20 quotes need known decimals.
        case when payment_token_address = '0x0000000000000000000000000000000000000000' then 'FIL'
            else (select any_value(token_symbol) from rails where token = payment_token_address) end as price_symbol,
        storage_price_per_tib_per_day / pow(10,
            case when payment_token_address = '0x0000000000000000000000000000000000000000' then 18
            else (select any_value(token_decimals) from rails where token = payment_token_address) end) * 30 as price_tib_month,
        min_piece_size_bytes as min_piece, max_piece_size_bytes as max_piece,
        min_proving_period_epochs as proving_period,
        supports_ipni_piece as ipni_piece, supports_ipni_ipfs as ipni_ipfs,
        capacity_tib, service_status,
        registered_block, registered_transaction_hash as registered_tx, epoch(registered_at)::bigint as registered_at,
        epoch(fwss_first_approved_at)::bigint as approved_at,
        fwss_last_approval_transaction_hash as approval_tx,
        epoch(removed_at)::bigint as removed_at, removed_transaction_hash as removed_tx,
        epoch(product_updated_at)::bigint as product_updated_at
    from providers
    """)
    con.execute(f"""
    create table d as
    select
        data_set_id as id, owner, provider_id, provider_address, payee,
        pdp_rail_id, cdn_rail_id, cache_miss_rail_id, has_cdn,
        created_block, {ts("created_at")} as created_at,
        {ts("billing_started_at")} as billing_started_at,
        {ts("billing_terminated_at")} as billing_terminated_at,
        {ts("settlement_end_at")} as settlement_end_at,
        source, metadata, with_ipfs_indexing as ipfs, is_cdn_enabled as cdn, is_deleted as deleted,
        epoch(api_observed_at)::bigint as api_observed_at,
        case
            when is_deleted then 'deleted'
            when billing_terminated_at is not null
                or (select state from r where r.id = pdp_rail_id) in ('terminated', 'finalized') then 'terminated'
            when billing_started_at is not null then 'live'
            else 'pending'
        end as status
    from data_sets
    """)
    con.execute("""
    create table pay as
    select
        date, epoch(event_at)::bigint as ts, block_number as block, transaction_hash as tx,
        case event_name when 'RailSettled' then 'settled' else 'one-time' end as kind,
        rail_id, payer, payee, operator, coalesce(token_symbol, 'Unknown') as token, is_stablecoin as stable,
        gross_amount as gross, net_payee_amount as net, operator_commission as commission, network_fee as fee
    from payments
    """)
    # Per-rail payment totals, used by most pages.
    con.execute("""
    create table rail_pay as
    select rail_id, count(*) as events, sum(gross) as gross, sum(net) as net, sum(fee) as fee,
           max(ts) as last_payment_at
    from pay group by 1
    """)
    con.execute("""
    create table r2 as
    select r.*, coalesce(rp.events, 0) as events,
           case when rp.events is null then 0 else rp.gross end as paid, rp.last_payment_at,
           -- Attribute a rail to a provider only when the provider is its payee: CDN rails of a
           -- data set pay the CDN, and rails without a data set are matched on the payee address.
           coalesce(case when r.payee = d.payee then d.provider_id end, pm.provider_id) as provider_id,
           (r.payer in (select payer from dealbot)) as dealbot
    from r
    left join rail_pay rp on rp.rail_id = r.id
    left join d on d.id = r.data_set_id
    left join (
        select payee, arg_min(id, (removed, id)) as provider_id from p group by 1
    ) pm on pm.payee = r.payee and r.data_set_id is null
    """)
    con.execute("""
    create table q30 as
    select provider_id,
        sum(storage_successes) filter (where storage_checks is not null) / nullif(sum(storage_checks) filter (where storage_successes is not null), 0) as storage,
        sum(retrieval_successes) filter (where retrieval_checks is not null) / nullif(sum(retrieval_checks) filter (where retrieval_successes is not null), 0) as retrieval,
        sum(sampled_retrieval_successes) filter (where sampled_retrieval_checks is not null) / nullif(sum(sampled_retrieval_checks) filter (where sampled_retrieval_successes is not null), 0) as sampled,
        sum(pull_successes) filter (where pull_checks is not null) / nullif(sum(pull_checks) filter (where pull_successes is not null), 0) as pull,
        sum(sampled_ipni_successes) filter (where sampled_ipni_checks is not null) / nullif(sum(sampled_ipni_checks) filter (where sampled_ipni_successes is not null), 0) as ipni,
        sum(proving_periods_faulted) filter (where proving_periods_closed is not null) / nullif(sum(proving_periods_closed) filter (where proving_periods_faulted is not null), 0) as faults,
        sum(proving_proofs)::bigint as proofs,
        median(retrieval_median_ttfb_ms) as ttfb,
        'Median of daily retrieval medians' as ttfb_label,
        strftime((select max(date) from daily_provider_quality) - 29, '%Y-%m-%d') as start,
        strftime((select max(date) from daily_provider_quality), '%Y-%m-%d') as end,
        sum(storage_successes) filter (where storage_checks is not null) as storage_successes, sum(storage_checks) filter (where storage_successes is not null) as storage_checks,
        sum(retrieval_successes) filter (where retrieval_checks is not null) as retrieval_successes, sum(retrieval_checks) filter (where retrieval_successes is not null) as retrieval_checks,
        sum(sampled_retrieval_successes) filter (where sampled_retrieval_checks is not null) as sampled_retrieval_successes, sum(sampled_retrieval_checks) filter (where sampled_retrieval_successes is not null) as sampled_retrieval_checks,
        sum(proving_periods_faulted) filter (where proving_periods_closed is not null) as proving_periods_faulted, sum(proving_periods_closed) filter (where proving_periods_faulted is not null) as proving_periods_closed
    from daily_provider_quality
    where provider_id is not null and date > (select max(date) from daily_provider_quality) - 30
    group by 1
    """)
    con.execute("""
    create table op_latest as
    select * exclude (date) from daily_operator_metrics
    where date = (select max(date) from daily_operator_metrics)
    """)


# Field lists reused across shards.
RAIL_ROW = """id, payer, payee, operator, service, token_symbol, state, data_set_id, provider_id,
    rate_month, settled, paid, events, created_at, terminated_at, eligible, dealbot, stable, streaming, api_observed_at"""
DS_ROW = """d.id, d.owner, d.provider_id, p.name as provider, d.status, d.source, d.cdn, d.ipfs,
    d.created_at, d.billing_started_at, d.billing_terminated_at,
    coalesce((select sum(rate_month) from r2 where r2.data_set_id = d.id and r2.streaming and r2.stable), 0) as rate_month,
    coalesce((select sum(paid) from r2 where r2.data_set_id = d.id and r2.stable), 0) as paid"""


class Writer:
    def __init__(self, con: duckdb.DuckDBPyConnection, out: Path):
        self.con, self.out, self.files, self.bytes = con, out, 0, 0

    def rows(self, sql: str) -> str:
        """JSON array of objects for a query."""
        return self.con.execute(
            f"select coalesce(to_json(list(t)), '[]') from ({sql}) t"
        ).fetchall()[0][0]

    def put(self, rel: str, text: str) -> None:
        # Preserve source precision. Wide integers must survive JavaScript JSON parsing.
        text = json.dumps(
            json.loads(
                text, parse_int=lambda n: str(n) if abs(int(n)) > 2**53 - 1 else int(n)
            ),
            separators=(",", ":"),
        )
        path = self.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.files += 1
        self.bytes += len(text)

    def obj(self, rel: str, parts: dict[str, str]) -> None:
        """Write an object whose values are JSON fragments."""
        self.put(rel, "{" + ",".join(f'"{k}":{v}' for k, v in parts.items()) + "}")

    def shards(self, folder: str, sql: str) -> None:
        """`sql` returns (key, json) rows, one intermediate input per static page."""
        for key, text in self.con.execute(sql).fetchall():
            self.put(f"{folder}/{key}.json", text)


def daily(where: str, stable_only: bool = True, measure: str = "gross") -> str:
    """Never aggregate different native tokens. A single rail may retain its token."""
    where = f"({where})" + (" and stable" if stable_only else "")
    return f"""(select to_json({{
        d: list(strftime(date, '%Y-%m-%d') order by date),
        v: list(amount order by date),
        n: list(n order by date)
    }}) from (select date, sum({measure}) as amount, count(*) as n from pay where {where} group by 1))"""


def latest(where: str, n: int = LATEST_EVENTS) -> str:
    return f"""(select coalesce(to_json(list(t)), '[]') from (
        select ts, block, tx, kind, rail_id, payer, payee, token, gross, net, fee
        from pay where {where} order by ts desc, block desc, tx, rail_id, kind, gross, net limit {n}) t)"""


def build(source: str, out: Path) -> None:
    # Dev-server startup probes must not rewrite imported JSON and trigger reloads.
    path = Path(source).resolve()
    fingerprint = {
        "source": str(path),
        "files": [
            [str(p), p.stat().st_mtime_ns, p.stat().st_size]
            for p in [path, Path(f"{path}.wal")]
            if p.exists()
        ],
        "exporter": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "day": datetime.now(UTC).date().isoformat(),
    }
    marker = out / "snapshot.json"
    if marker.exists():
        previous = json.loads(marker.read_text())
        if previous.get("fingerprint") == fingerprint and len(
            list((out / "data").rglob("*.json"))
        ) == previous.get("files"):
            print("FOC snapshot unchanged; using existing page inputs")
            return
    t0 = time.time()
    con = connect(source)
    model(con)
    print(f"loaded + modeled in {time.time() - t0:.1f}s")

    data = out / "data.next"
    if data.exists():
        shutil.rmtree(data)
    w = Writer(con, data)

    # Names used to label addresses everywhere.
    w.put(
        "labels.json",
        '{"pack":0,"labels":'
        + w.rows("""
        select address, label, kind, id from (
            select payee as address, name as label, 'provider' as kind, id, removed from p
            union all select address, name, 'provider', id, removed from p where address <> payee
            union all select payer, 'Dealbot', 'dealbot', 0, false from dealbot
            union all select operator, any_value(service) || ' operator', 'operator', 0, false from r
                where service <> 'Other' group by operator
            union all select orchestrator, 'ServiceOrchestrator', 'orchestrator', 0, false from service_orchestrators
        ) qualify row_number() over (partition by address order by removed, id) = 1
    """)
        + "}",
    )

    # Overview: network series + headline counts + short recent lists.
    w.obj(
        "overview.json",
        {
            "updated_at": con.execute(
                "select to_json(epoch(now())::bigint)"
            ).fetchall()[0][0],
            "as_of": con.execute(
                "select to_json(strftime(max(date), '%Y-%m-%d')) from network"
            ).fetchall()[0][0],
            "series": con.execute(f"""select to_json({{
            {", ".join(f"{c}: list({c} order by date)" for c in ["run_rate", "fee_arr", "active_rails", "active_payers", "paid", "billing_data_sets", "billing_payers", "new_data_sets", "stored_bytes"])},
            date: list(strftime(date, '%Y-%m-%d') order by date)
        }}) from network""").fetchall()[0][0],
            "counts": w.rows("""select
            (select count(*) from p where not removed) as providers,
            (select count(*) from p where approved and not removed) as approved,
            (select count(*) from d) as data_sets,
            (select count(*) from d where status = 'live') as live_data_sets,
            (select count(*) from r) as rails,
            (select count(*) from r where state = 'active') as active_rails,
            (select count(*) from (select owner from d union select payer from r)) as clients,
            (select count(distinct owner) from d) as data_set_owners,
            (select count(distinct payer) from r) as payers,
            (select count(distinct operator) from r) as operators,
            (select sum(gross) from pay where stable) as paid_total,
            (select count(*) from pay) as payments"""),
            "providers": w.rows("""
            select p.id, p.name, p.country, p.approved,
                count(d.id) filter (where d.status = 'live') as live,
                coalesce((select sum(paid) from r2 where r2.provider_id = p.id and r2.stable), 0) as paid
            from p left join d on d.provider_id = p.id
            group by all order by live desc, paid desc limit 8"""),
            "data_sets": w.rows(
                f"select {DS_ROW} from d left join p on p.id = d.provider_id order by d.id desc limit 8"
            ),
            "payments": con.execute("select " + latest("true", 10)).fetchall()[0][0],
        },
    )

    # Lists.
    w.put(
        "providers.json",
        w.rows("""
        select p.id, p.name, p.address, p.payee, p.active, p.endorsed, p.approved, p.removed, p.service_status,
            p.country, p.city, p.price_tib_month, p.price_symbol, p.capacity_tib, p.registered_at,
            count(d.id) as data_sets, count(d.id) filter (where d.status = 'live') as live,
            count(distinct d.owner) as clients,
            coalesce((select sum(paid) from r2 where r2.provider_id = p.id and r2.stable), 0) as paid,
            coalesce((select sum(rate_month) from r2 where r2.provider_id = p.id and r2.streaming and r2.stable), 0) as rate_month,
            q.storage, q.retrieval, q.faults
        from p left join d on d.provider_id = p.id left join q30 q on q.provider_id = p.id
        group by all order by p.id"""),
    )
    w.put(
        "datasets.json",
        w.rows(
            f"select {DS_ROW} from d left join p on p.id = d.provider_id order by d.id desc"
        ),
    )
    w.put("rails.json", w.rows(f"select {RAIL_ROW} from r2 order by id desc"))
    w.put(
        "clients.json",
        w.rows("""
        with a as (
            select payer as address from r union select owner from d
        )
        select a.address,
            (a.address in (select payer from dealbot)) as dealbot,
            (select count(*) from d where owner = a.address) as data_sets,
            (select count(*) from d where owner = a.address and status = 'live') as live,
            (select count(distinct provider_id) from d where owner = a.address) as providers,
            (select count(*) from r2 where payer = a.address) as rails,
            (select count(*) from r2 where payer = a.address and state = 'active') as active_rails,
            coalesce((select sum(paid) from r2 where payer = a.address and stable), 0) as paid,
            coalesce((select sum(rate_month) from r2 where payer = a.address and streaming and stable), 0) as rate_month,
            (select min(created_at) from r2 where payer = a.address) as first_at
        from a order by paid desc"""),
    )
    w.put(
        "operators.json",
        w.rows("""
        select r2.operator as address, mode(service) as service,
            count(*) as rails, count(*) filter (where state = 'active') as active_rails,
            count(distinct payer) as payers, count(distinct payee) as payees,
            sum(paid) filter (where stable) as paid,
            any_value(o.filecoin_pay_gross_payment_volume_run_rate_usd) as run_rate,
            any_value(o.filecoin_pay_network_fee_arr_usd) as fee_arr,
            min(created_at) as first_at
        from r2 left join op_latest o on o.operator = r2.operator
        group by 1 order by rails desc"""),
    )
    w.obj(
        "solstice.json",
        {
            "orchestrators": w.rows("""select orchestrator, wallet, is_admitted, admissions, bound_pairs,
            epoch(first_admitted_at)::bigint as first_admitted_at, admitted_transaction_hash as admitted_tx,
            epoch(removed_at)::bigint as removed_at from service_orchestrators"""),
            "quarters": w.rows("""select quarter, start_block, end_block, posting_start_block, verification_start_block,
            bound_block, as_of_block, is_bound, bound_volume_atto_usd::varchar as bound_volume,
            epoch(shares_submitted_at)::bigint as shares_submitted_at, share_recipients,
            shares_total_atto_usd::varchar as shares_total, epoch(gate_checked_at)::bigint as gate_checked_at, gate_passed, gate_steps,
            gate_threshold_atto_usd::varchar as gate_threshold from service_quarters order by quarter desc"""),
            "orchestrator_quarters": w.rows("""select quarter, orchestrator, is_complete, stablecoin_settlements,
            stablecoin_volume_atto_usd::varchar as stablecoin_volume, fil_volume_atto_usd::varchar as fil_volume,
            volume_atto_usd::varchar as volume, is_bound, posted_volume_atto_usd::varchar as posted_volume,
            reported_volume_atto_usd::varchar as reported_volume, corrections,
            bound_volume_atto_usd::varchar as bound_volume, fil_pending_atto_fil::varchar as fil_pending_atto_fil,
            volume_as_of_block, as_of_block, is_removed_in_quarter,
            epoch(posted_at)::bigint as posted_at from orchestrator_quarters order by quarter desc"""),
        },
    )

    # Provider shards.
    w.shards(
        "p",
        sql=f"""
        select pp.id, to_json({{
            provider: (select to_json(x) from p x where x.id = pp.id),
            capabilities: (select capabilities_json from providers where provider_id = pp.id),
            quality30: (select to_json(q) from q30 q where q.provider_id = pp.id),
            quality: (select to_json({{
                d: list(strftime(date, '%Y-%m-%d') order by date),
                storage: list(storage_success_rate order by date),
                retrieval: list(retrieval_success_rate order by date),
                sampled: list(sampled_retrieval_success_rate order by date),
                faults: list(proving_fault_rate order by date),
                ttfb: list(retrieval_median_ttfb_ms order by date),
                checks: list(coalesce(storage_checks, 0) + coalesce(retrieval_checks, 0) order by date)
            }}) from daily_provider_quality where provider_id = pp.id),
            data_sets: (select coalesce(to_json(list(x order by x.id desc)), '[]') from (
                select {DS_ROW} from d left join p on p.id = d.provider_id where d.provider_id = pp.id) x),
            rails: (select coalesce(to_json(list(x order by x.id desc)), '[]') from (
                select {RAIL_ROW} from r2 where provider_id = pp.id) x),
            daily: {daily("rail_id in (select id from r2 where provider_id = pp.id)")},
            payments: {latest("rail_id in (select id from r2 where provider_id = pp.id)", 20)}
        }}) from p pp""",
    )

    # Data set shards.
    w.shards(
        "ds",
        f"""
        select d.id, to_json({{
            data_set: (select to_json(x) from d x where x.id = d.id),
            provider: (select to_json({{id: id, name: name, country: country, city: city, approved: approved}}) from p where p.id = d.provider_id),
            rails: (select coalesce(to_json(list(x order by x.id)), '[]') from r2 x where x.data_set_id = d.id),
            daily: {daily("rail_id in (select id from r where data_set_id = d.id)")},
            payments: {latest("rail_id in (select id from r where data_set_id = d.id)", 20)}
        }}) from d""",
    )

    # Rail shards.
    w.shards(
        "r",
        f"""
        select r2.id, to_json({{
            rail: (select to_json(x) from r2 x where x.id = r2.id),
            data_set: (select to_json({{id: id, status: status, owner: owner, source: source}}) from d where d.id = r2.data_set_id),
            provider: (select to_json({{id: id, name: name}}) from p where p.id = r2.provider_id),
            totals: (select coalesce(to_json(list(x)), '[]') from (
                select kind, count(*) as events, sum(gross) as gross, sum(net) as net, sum(fee) as fee
                from pay where rail_id = r2.id group by 1 order by 1) x),
            daily: {daily("rail_id = r2.id", stable_only=False)},
            payments: {latest("rail_id = r2.id")}
        }}) from r2""",
    )

    # Address shards: every address that appears as payer, payee, operator, owner, provider or orchestrator.
    con.execute("""
        create table addrs as
        select distinct address from (
            select payer as address from r union all select payee from r union all select operator from r
            union all select validator from r union all select fee_recipient from r union all select terminated_by from r
            union all select owner from d union all select address from p union all select payee from p
            union all select orchestrator from service_orchestrators union all select wallet from service_orchestrators
        ) where address is not null and address <> '0x0000000000000000000000000000000000000000'
    """)
    w.shards(
        "a",
        f"""
        select a.address, to_json({{
            address: a.address,
            dealbot: a.address in (select payer from dealbot),
            providers: (select coalesce(to_json(list({{id: id, name: name, approved: approved}})), '[]') from p
                where p.address = a.address or p.payee = a.address),
            orchestrator: (select to_json(o) from service_orchestrators o where o.orchestrator = a.address or o.wallet = a.address),
            operator: (select to_json(o) from op_latest o where o.operator = a.address),
            operator_daily: (select to_json({{
                d: list(strftime(date, '%Y-%m-%d') order by date),
                run_rate: list(filecoin_pay_gross_payment_volume_run_rate_usd order by date),
                active_rails: list(active_rails order by date)
            }}) from daily_operator_metrics where operator = a.address),
            data_sets: (select coalesce(to_json(list(x order by x.id desc)), '[]') from (
                select {DS_ROW} from d left join p on p.id = d.provider_id where d.owner = a.address) x),
            rails_out: (select coalesce(to_json(list(x order by x.id desc)), '[]') from (
                select {RAIL_ROW} from r2 where payer = a.address) x),
            rails_in: (select coalesce(to_json(list(x order by x.id desc)), '[]') from (
                select {RAIL_ROW} from r2 where payee = a.address) x),
            rails_op: (select count(*) from r2 where operator = a.address),
            paid_out: (select sum(gross) from pay where payer = a.address and stable),
            paid_in: (select sum(net) from pay where payee = a.address and stable),
            daily_out: {daily("payer = a.address")},
            daily_in: {daily("payee = a.address", measure="net")},
            payments: {latest("payer = a.address or payee = a.address", 25)}
        }}) from addrs a""",
    )

    w.obj(
        "lookup.json",
        {
            "providers": w.rows(
                "select id, coalesce(nullif(name, ''), concat('Provider #', id)) as label, address, 'provider' as kind from p order by id"
            ),
            "datasets": con.execute(
                "select coalesce(to_json(list(id order by id)), '[]') from d"
            ).fetchone()[0],
            "rails": con.execute(
                "select coalesce(to_json(list(id order by id)), '[]') from r"
            ).fetchone()[0],
            "addresses": con.execute(
                "select coalesce(to_json(list(address order by address)), '[]') from addrs"
            ).fetchone()[0],
        },
    )
    w.put(
        "coverage.json",
        w.rows(
            """select 'payments' as source, strftime(min(date), '%Y-%m-%d') as start,
                strftime(max(date), '%Y-%m-%d') as end, null::varchar as observed_at from pay
            union all select 'quality', strftime(min(date), '%Y-%m-%d'), strftime(max(date), '%Y-%m-%d'), null from daily_provider_quality
            union all select 'operators', strftime(min(date), '%Y-%m-%d'), strftime(max(date), '%Y-%m-%d'), null from daily_operator_metrics
            union all select 'network', strftime(min(date), '%Y-%m-%d'), strftime(max(date), '%Y-%m-%d'), null from network
            union all select 'rails', null, null, strftime(max(api_observed_at), '%Y-%m-%dT%H:%M:%SZ') from rails
            union all select 'data_sets', null, null, strftime(max(api_observed_at), '%Y-%m-%dT%H:%M:%SZ') from data_sets"""
        ),
    )
    con.close()
    old = out / "data.old"
    if old.exists():
        shutil.rmtree(old)
    if (out / "data").exists():
        (out / "data").rename(old)
    data.rename(out / "data")
    if old.exists():
        shutil.rmtree(old)
    marker.write_text(json.dumps({"fingerprint": fingerprint, "files": w.files}))
    print(f"wrote {w.files} files, {w.bytes / 1e6:.1f} MB in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--source", default=SOURCE, help="local fdp.duckdb path (read-only)"
    )
    args = ap.parse_args()
    out = ROOT / ".foc"
    out.mkdir(parents=True, exist_ok=True)
    with (out / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        build(args.source, out)
