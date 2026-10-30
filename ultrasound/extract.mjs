// Read-only extraction from the full materialized FDP database (raw/model/main).
import { DuckDBInstance } from '@duckdb/node-api'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export async function extract(database = process.env.FDP_DB ?? fileURLToPath(new URL('../fdp.duckdb', import.meta.url))) {
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ultrasound-'))
const db = await DuckDBInstance.create(database, { access_mode: 'READ_ONLY', temp_directory: temp, max_temp_directory_size: '2GiB', memory_limit: '2GiB', threads: '2' })
const c = await db.connect()
try {
await c.run("SET TimeZone='UTC'")
// Apply the daily ceiling once, including source-end metadata and rolling windows.
for (const [name, source] of Object.entries({
  checkpoints: 'model.network_daily_fevm_checkpoints',
  network: 'main.daily_network_metrics',
  quality: 'main.daily_provider_quality',
  uss_payments: 'main.payments',
})) await c.run(`create temp view ${name} as select * from ${source} where date < current_date`)
const q = async (sql) => (await c.runAndReadAll(sql)).getRowObjectsJson().map(r => Object.fromEntries(Object.entries(r).map(([k, v]) =>
  [k, typeof v === 'string' && /^-?\d+$/.test(v) && !k.endsWith('_atto') && !k.includes('_atto_') ? Number(v) : v])))
const dealbot = fs.readFileSync(new URL('./dealbot.sql', import.meta.url), 'utf8')
const INF = '9223372036854775807'

// Billing spans: merge contiguous positive-rate intervals per PDP rail.
const common = `
${dealbot},
cp as (select date, checkpoint_ordinal from checkpoints),
days as (select checkpoint_ordinal, min(date) as date from cp group by 1),
iv as (
  select rail_id, start_ordinal, end_ordinal, rate_wei_per_epoch > 0 as pos,
    lag(rate_wei_per_epoch > 0) over w as prev_pos, lag(end_ordinal) over w as prev_end
  from model.pay_rail_rate_intervals where rail_id in (select pdp_rail_id from main.data_sets)
  window w as (partition by rail_id order by start_ordinal)
),
grp as (
  select *, sum(case when pos and coalesce(prev_pos,false) and prev_end = start_ordinal then 0 else 1 end)
    over (partition by rail_id order by start_ordinal) g from iv
),
spans as (select rail_id, min(start_ordinal) s, max(coalesce(end_ordinal, ${INF})) e from grp where pos group by rail_id, g),
ds as (
  select d.data_set_id, d.pdp_rail_id, d.provider_id, r.payer, r.is_stablecoin,
    r.payer in (select payer from dealbot_payers) as is_monitor
  from main.data_sets d join main.rails r on r.rail_id = d.pdp_rail_id
)`

const out = {}
out.generated_at = new Date().toISOString()

out.checkpoint = (await q(`select strftime(max(date),'%Y-%m-%d') date, max(checkpoint_ordinal) ordinal, count(*) n_days, strftime(min(date),'%Y-%m-%d') first_date from checkpoints`))[0]
out.monitor_payers = (await q(`with ${dealbot} select payer from dealbot_payers order by 1`)).map(r => r.payer)

// 1. Daily active-billing stock (bytes), filtered and monitoring, plus billing datasets/payers counts.
out.storage = await q(`with ${common.trim().replace(/^,/, '')},
ov as (
  select ds.is_monitor, greatest(p.added_ordinal, sp.s) s, least(coalesce(p.removed_ordinal, ${INF}), sp.e) e, p.raw_size_bytes bytes
  from model.foc_pieces p join ds using (data_set_id) join spans sp on sp.rail_id = ds.pdp_rail_id
),
deltas as (
  select is_monitor, s as ordinal, bytes from ov where s < e
  union all select is_monitor, e, -bytes from ov where s < e and e < ${INF}
),
dated as (select d.date, deltas.is_monitor, deltas.bytes from deltas asof join days d on d.checkpoint_ordinal >= deltas.ordinal),
agg as (
  select a.date, coalesce(sum(bytes) filter (where not is_monitor),0) f, coalesce(sum(bytes) filter (where is_monitor),0) m
  from cp a left join dated using (date) group by 1
),
cnt as (
  select cp.date,
    count(distinct ds.data_set_id) filter (where not ds.is_monitor) sets,
    count(distinct ds.payer) filter (where not ds.is_monitor) payers,
    count(distinct ds.data_set_id) filter (where ds.is_monitor) msets
  from cp left join spans sp on sp.s <= cp.checkpoint_ordinal and sp.e > cp.checkpoint_ordinal
  left join ds on ds.pdp_rail_id = sp.rail_id group by 1
)
select strftime(agg.date,'%Y-%m-%d') date,
  (sum(f) over (order by agg.date))::bigint as b, (sum(m) over (order by agg.date))::bigint as mb,
  cnt.sets, cnt.payers, cnt.msets, n.warm_storage_stored_bytes as all_fwss
from agg join cnt using (date) left join network n on n.date = agg.date
order by agg.date`)

// 1b. Snapshot at latest checkpoint
out.snapshot = (await q(`with ${common.trim()},
o as (select max(checkpoint_ordinal) o from cp),
live as (select data_set_id, sum(raw_size_bytes) bytes, count(*) pieces from model.foc_pieces, o
  where added_ordinal <= o.o and (removed_ordinal is null or removed_ordinal > o.o) group by 1),
billing as (select distinct rail_id from spans, o where s <= o.o and e > o.o),
cls as (
  select ds.*, ds.pdp_rail_id in (select rail_id from billing) is_billing, coalesce(l.bytes,0) bytes, coalesce(l.pieces,0) pieces
  from ds left join live l using (data_set_id)
)
select
  sum(bytes) filter (where is_billing and not is_monitor)::bigint f_bytes,
  count(*) filter (where is_billing and not is_monitor) f_sets,
  count(*) filter (where is_billing and not is_monitor and bytes > 0) f_sets_nonempty,
  count(distinct payer) filter (where is_billing and not is_monitor) f_payers,
  count(distinct provider_id) filter (where is_billing and not is_monitor and bytes > 0) f_providers,
  bool_and(is_stablecoin) filter (where is_billing and not is_monitor) f_all_stable,
  sum(pieces) filter (where is_billing and not is_monitor)::bigint f_pieces,
  sum(bytes) filter (where is_billing and is_monitor)::bigint m_bytes,
  count(*) filter (where is_billing and is_monitor) m_sets,
  count(distinct payer) filter (where is_billing and is_monitor) m_payers,
  sum(bytes) filter (where not is_billing)::bigint nb_bytes,
  count(*) filter (where not is_billing and bytes > 0) nb_sets_nonempty,
  sum(bytes)::bigint fwss_bytes,
  (select sum(raw_size_bytes) from model.foc_pieces, o where added_ordinal <= o.o and (removed_ordinal is null or removed_ordinal > o.o)
     and data_set_id not in (select data_set_id from main.data_sets))::bigint other_pdp_bytes,
  (select count(distinct data_set_id) from model.foc_pieces, o where added_ordinal <= o.o and (removed_ordinal is null or removed_ordinal > o.o)
     and data_set_id not in (select data_set_id from main.data_sets)) other_pdp_sets
from cls`))[0]

// Other PDP sets last proof observed (registry lifecycle context)

// 2. Payments: daily gross by category (stablecoin only; non-stablecoin noted separately)
const railClass = `
${dealbot},
roles as (
  select pdp_rail_id rail_id, 'pdp' role from main.data_sets where pdp_rail_id is not null
  union all select cdn_rail_id, 'cdn' from main.data_sets where cdn_rail_id is not null
  union all select cache_miss_rail_id, 'cache' from main.data_sets where cache_miss_rail_id is not null
),
rc as (
  select r.rail_id, r.payer, r.is_stablecoin, r.is_arr_eligible, r.token_symbol,
    r.payer in (select payer from dealbot_payers) is_monitor,
    case
      when r.service = 'FWSS' and r.payer in (select payer from dealbot_payers) then 'fwss_monitor'
      when r.service = 'FWSS' then 'fwss_' || coalesce(roles.role, 'unmapped')
      when r.service = 'FIL One Storage' then 'filone'
      when r.service = 'Storacha' then 'storacha'
      else 'other' end as cat,
    r.service
  from main.rails r left join roles using (rail_id)
)`
out.payment_dupe_roles = (await q(`with ${railClass} select count(*) n from (select rail_id from roles group by 1 having count(*) > 1)`))[0].n
out.payments_daily = await q(`with ${railClass},
cal as (select date from checkpoints)
select strftime(cal.date,'%Y-%m-%d') date,
  ${['fwss_pdp','fwss_cdn','fwss_cache','fwss_unmapped','fwss_monitor','filone','storacha','other'].map(k => `coalesce(sum(p.gross_amount_usd) filter (where rc.cat='${k}'),0) ${k}`).join(',\n  ')},
  coalesce(sum(p.gross_amount_usd) filter (where rc.cat like 'fwss_%' and rc.cat <> 'fwss_monitor' and p.event_name = 'RailOneTimePaymentProcessed'),0) fwss_f_onetime,
  coalesce(sum(p.gross_amount_usd) filter (where rc.cat not like 'fwss_%' and p.event_name = 'RailOneTimePaymentProcessed'),0) broad_onetime
from cal left join uss_payments p on p.date = cal.date and p.is_stablecoin
left join rc using (rail_id)
group by cal.date order by cal.date`)
out.payments_nonstable = await q(`select strftime(date,'%Y-%m-%d') date, event_name, rail_id from uss_payments where not is_stablecoin or gross_amount_usd is null`)

// Concentration: same-window filtered-FWSS gross settlements by payer, fixed windows
const end = out.checkpoint.date
out.concentration = {}
for (const [key, days] of [['30d', 30], ['90d', 90], ['1y', 365], ['all', 100000]]) {
  const rows = await q(`with ${railClass},
  per as (select p.payer, sum(gross_amount_usd) usd from uss_payments p join rc using (rail_id)
    where p.is_stablecoin and rc.cat like 'fwss_%' and rc.cat <> 'fwss_monitor'
      and p.date > date '${end}' - interval ${days} day and p.date <= date '${end}' group by 1)
  select count(*) payers, sum(usd) total, max(usd) top1,
    (select sum(usd) from (select usd from per order by usd desc limit 5)) top5 from per`)
  out.concentration[key] = rows[0]
}

// 2b. Annualized recurring GPV, end-of-day, by category. Delta method over rate intervals (stablecoin rails only).
out.gpv = await q(`with ${railClass},
days as (select checkpoint_ordinal, min(date) as date from checkpoints group by 1),
iv as (select i.rail_id, rc.cat, i.start_ordinal, i.end_ordinal, i.rate_token_per_epoch * 2880 * 365 usd_yr
  from model.pay_rail_rate_intervals i join rc using (rail_id) where rc.is_stablecoin and i.rate_wei_per_epoch > 0),
deltas as (select cat, start_ordinal o, usd_yr v from iv union all select cat, end_ordinal, -usd_yr from iv where end_ordinal is not null),
dated as (select d.date, cat, v from deltas asof join days d on d.checkpoint_ordinal >= deltas.o),
agg as (select c.date, ${['fwss_pdp','fwss_cdn','fwss_cache','fwss_unmapped','fwss_monitor','filone','storacha','other'].map(k => `coalesce(sum(v) filter (where cat='${k}'),0) ${k}`).join(', ')}
  from checkpoints c left join dated using (date) group by 1)
select strftime(date,'%Y-%m-%d') date, ${['fwss_pdp','fwss_cdn','fwss_cache','fwss_unmapped','fwss_monitor','filone','storacha','other'].map(k => `sum(${k}) over (order by date) ${k}`).join(', ')},
  r.filecoin_pay_gross_payment_volume_run_rate_usd fdp_eligible
from agg left join network r using (date) order by date`)
out.gpv_top_operator = (await q(`with ${railClass},
o as (select max(checkpoint_ordinal) o from checkpoints),
cur as (select r.operator, r.service, sum(i.rate_token_per_epoch*2880*365) usd from model.pay_rail_rate_intervals i join main.rails r using (rail_id), o
  where r.is_arr_eligible and i.rate_wei_per_epoch > 0 and i.start_ordinal <= o.o and (i.end_ordinal is null or i.end_ordinal > o.o) group by 1,2)
select operator, service, usd, usd / sum(usd) over () share from cur order by usd desc limit 3`))

// 3. Quality: pooled daily, continuous calendar with nulls where no observation
out.quality = await q(`with cal as (select unnest(generate_series((select min(date) from quality), (select max(date) from quality), interval 1 day))::date date),
d as (select date,
  sum(sampled_retrieval_checks) sc, sum(sampled_retrieval_successes) ss, sum(sampled_retrieval_skipped) sk,
  sum(retrieval_checks) rc, sum(retrieval_successes) rs,
  sum(storage_checks) stc, sum(storage_successes) sts,
  sum(proving_periods_closed) pc, sum(proving_periods_faulted) pf,
  count(distinct provider_id) filter (where sampled_retrieval_checks > 0) sp,
  count(distinct provider_id) filter (where proving_periods_closed > 0) pp
  from quality group by 1)
select strftime(cal.date,'%Y-%m-%d') date, sc::bigint sc, ss::bigint ss, sk::bigint sk, rc::bigint rc, rs::bigint rs, stc::bigint stc, sts::bigint sts, pc::bigint pc, pf::bigint pf, sp, pp
from cal left join d using (date) order by cal.date`)

out.provider_quality = await q(`with ends as (select
  max(date) filter (where sampled_retrieval_checks is not null) s_end,
  max(date) filter (where proving_periods_closed is not null) p_end from quality)
select q.provider_id, any_value(p.name) name, any_value(p.is_fwss_approved) approved, any_value(p.location_country_code) cc,
  sum(sampled_retrieval_checks) filter (where q.date > s_end - 30)::bigint sc,
  sum(sampled_retrieval_successes) filter (where q.date > s_end - 30)::bigint ss,
  sum(sampled_retrieval_skipped) filter (where q.date > s_end - 30)::bigint sk,
  sum(retrieval_checks) filter (where q.date > s_end - 30)::bigint rc,
  sum(retrieval_successes) filter (where q.date > s_end - 30)::bigint rs,
  sum(storage_checks) filter (where q.date > s_end - 30)::bigint stc,
  sum(storage_successes) filter (where q.date > s_end - 30)::bigint sts,
  sum(proving_periods_closed) filter (where q.date > p_end - 30)::bigint pc,
  sum(proving_periods_faulted) filter (where q.date > p_end - 30)::bigint pf,
  count(distinct q.date) filter (where q.date > s_end - 30 and sampled_retrieval_checks > 0) s_days
from quality q left join main.providers p using (provider_id), ends
where q.date > least(s_end, p_end) - 30
group by q.provider_id order by q.provider_id`)

// billing bytes by provider (filtered) at latest checkpoint for provider table context
out.provider_billing = await q(`with ${common.trim()},
o as (select max(checkpoint_ordinal) o from cp),
billing as (select distinct rail_id from spans, o where s <= o.o and e > o.o)
select ds.provider_id, sum(p.raw_size_bytes)::bigint bytes, count(distinct ds.data_set_id) sets
from ds join model.foc_pieces p using (data_set_id), o
where not ds.is_monitor and ds.pdp_rail_id in (select rail_id from billing)
  and p.added_ordinal <= o.o and (p.removed_ordinal is null or p.removed_ordinal > o.o)
group by 1 order by 2 desc`)

out.providers = (await q(`select count(*) filter (where is_registered) registered, count(*) filter (where is_removed) removed,
  count(*) filter (where is_registered and not is_removed and offers_pdp_storage) offering,
  count(*) filter (where is_fwss_approved) approved, strftime(max(registry_fetched_at),'%Y-%m-%d') fetched from main.providers`))[0]

// 4. Economics daily
// Reward-allocation burn comes from the block-reward source, masked like minted (null if any tipset unobservable).
out.econ = await q(`select strftime(n.date,'%Y-%m-%d') date, n.circulating_fil, n.locked_fil, n.mined_fil, n.vested_fil, n.burnt_fil, n.pledge_collateral_fil,
  n.minted_rewards_fil, n.miner_rewards_fil, n.service_rewards_fil, n.emission_burn_fil,
  if(br.unobservable_tipsets = 0, br.burn_rewards_fil, null) reward_burn_fil,
  n.total_burn_fil, n.non_emission_burn_fil, n.base_fee_burn_fil, n.overestimation_burn_fil, n.message_storage_provider_penalty_fil,
  n.storage_provider_cron_burn_fil, n.unattributed_burn_fil, n.raw_power_pibs, n.quality_adjusted_power_pibs, n.fil_token_price_avg_usd
from network n left join model.network_daily_block_rewards br using (date)
where n.date < current_date and n.date >= date '2025-01-01' order by n.date`)

out.other_pdp = await q(`with o as (select distinct data_set_id from model.foc_pieces where data_set_id not in (select data_set_id from main.data_sets) and removed_ordinal is null)
select o.data_set_id, strftime(max(file_date),'%Y-%m-%d') last_proof, count(e.block_number) proofs from o left join raw.riba_eth_logs_decoded e
on e.contract_name='pdp_verifier' and e.event_name='PossessionProven' and cast(json_extract_string(e.args,'$.setId') as bigint)=o.data_set_id group by 1 order by 1`)
// 5. Solstice
const toDate = (b) => `strftime(to_timestamp(${b} * 30 + 1598306400),'%Y-%m-%d %H:%M')`
out.solstice = await q(`select quarter, start_block, end_block, ${toDate('start_block')} start_at, ${toDate('end_block')} end_at,
  ${toDate('bound_block')} bound_at, bound_block, as_of_block, ${toDate('as_of_block')} as_of_at, is_bound, gate_passed, gate_checked_at::varchar gate_checked_at,
  share_recipients, shares_submitted_at::varchar shares_submitted_at from main.service_quarters order by quarter desc`)
out.solstice_orch = await q(`select quarter, orchestrator, is_complete, is_bound, stablecoin_settlements, volume_atto_usd::varchar volume_atto_usd,
  posted_at::varchar posted_at, corrections from main.orchestrator_quarters order by quarter desc, orchestrator`)
out.solstice_admitted = (await q(`select count(*) filter (where is_admitted) n from main.service_orchestrators`))[0].n

// Source end dates
out.ends = (await q(`select
  (select strftime(max(date),'%Y-%m-%d') from network where circulating_fil is not null) econ_snapshot,
  (select strftime(max(date),'%Y-%m-%d') from network where minted_rewards_fil is not null) minted,
  (select strftime(max(date),'%Y-%m-%d') from network where total_burn_fil is not null) burn,
  (select strftime(max(date),'%Y-%m-%d') from network where raw_power_pibs is not null) power,
  (select strftime(max(date),'%Y-%m-%d') from uss_payments) payments,
  (select strftime(max(date),'%Y-%m-%d') from quality where sampled_retrieval_checks is not null) sampled,
  (select strftime(max(date),'%Y-%m-%d') from quality where proving_periods_closed is not null) proving,
  (select strftime(max(api_observed_at),'%Y-%m-%d %H:%M') from main.rails) rails_api
`))[0]

return out
} finally {
  c.closeSync()
  db.closeSync()
  fs.rmSync(temp, { recursive: true, force: true })
}
}
