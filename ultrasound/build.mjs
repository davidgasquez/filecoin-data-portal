// Keep the prototype's extraction and columnar payload; no runtime API or framework.
import fs from 'node:fs'

const r = (v, p = 6) => v == null ? null : Math.abs(v) < 1e-9 ? 0 : Math.round(v * 10 ** p) / 10 ** p
const cols = (rows, spec) => {
  const o = { date: rows.map(x => x.date) }
  for (const [k, p] of Object.entries(spec)) o[k] = rows.map(x => p == null ? (x[k] ?? null) : r(x[k], p))
  return o
}
const trim = (rows, hasValue) => rows.slice(Math.max(0, rows.findIndex(hasValue) - 1))
const hasFlow = row => Object.entries(row).some(([k, v]) => k !== 'date' && v > 0)
const categories = ['fwss_pdp', 'fwss_cdn', 'fwss_cache', 'fwss_unmapped', 'fwss_monitor', 'filone', 'storacha', 'other']

export function pack(d) {
  return {
    meta: {
      checkpoint: d.checkpoint, ends: d.ends, extracted_at: d.generated_at, monitor_payers: d.monitor_payers,
      providers: d.providers, snapshot: d.snapshot, other_pdp: d.other_pdp, concentration: d.concentration,
      gpv_top_operator: d.gpv_top_operator, solstice: d.solstice, solstice_orch: d.solstice_orch,
      solstice_admitted: d.solstice_admitted, nonstable: d.payments_nonstable, dupe_roles: d.payment_dupe_roles,
    },
    storage: cols(trim(d.storage, x => x.b > 0 || x.mb > 0), { b: null, mb: null, sets: null, payers: null, msets: null, all_fwss: null }),
    pay: cols(trim(d.payments_daily, hasFlow), Object.fromEntries([...categories, 'fwss_f_onetime', 'broad_onetime'].map(k => [k, 6]))),
    gpv: cols(trim(d.gpv, hasFlow), Object.fromEntries([...categories, 'fdp_eligible'].map(k => [k, 4]))),
    quality: cols(d.quality, { sc: null, ss: null, sk: null, rc: null, rs: null, stc: null, sts: null, pc: null, pf: null, sp: null, pp: null }),
    econ: cols(d.econ, {
      circulating_fil: 1, locked_fil: 1, minted_rewards_fil: 3, miner_rewards_fil: 3, service_rewards_fil: 3, emission_burn_fil: 3, reward_burn_fil: 3,
      total_burn_fil: 3, non_emission_burn_fil: 3, base_fee_burn_fil: 3, overestimation_burn_fil: 3, message_storage_provider_penalty_fil: 3,
      storage_provider_cron_burn_fil: 3, unattributed_burn_fil: 3, raw_power_pibs: 3, quality_adjusted_power_pibs: 3, fil_token_price_avg_usd: 5,
    }),
    providers: d.provider_quality.map(p => ({ ...p, billed: d.provider_billing.find(b => b.provider_id === p.provider_id) ?? null })),
  }
}

const DAY = 86400000
export function validate(d, today = new Date().toISOString().slice(0, 10)) {
  for (const name of ['storage', 'pay', 'gpv', 'quality', 'econ']) {
    const series = d[name], dates = series.date
    if (!dates.length) throw new Error(`${name}: empty series`)
    for (const [key, values] of Object.entries(series)) {
      if (values.length !== dates.length) throw new Error(`${name}.${key}: column length mismatch`)
    }
    for (let i = 0; i < dates.length; i++) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(dates[i]) || !Number.isFinite(Date.parse(dates[i])) || dates[i] >= today) throw new Error(`${name}: invalid daily date ${dates[i]}`)
      if (i && Date.parse(dates[i]) - Date.parse(dates[i - 1]) !== DAY) throw new Error(`${name}: non-contiguous dates`)
    }
  }
  for (const name of ['storage', 'pay', 'gpv']) {
    if (d[name].date.at(-1) !== d.meta.checkpoint.date) throw new Error(`${name}: checkpoint mismatch`)
  }
  for (const [key, date] of Object.entries(d.meta.ends)) {
    if (key !== 'rails_api' && (!date || date >= today)) throw new Error(`${key}: invalid source end date`)
  }
  for (const key of ['circulating_fil', 'locked_fil', 'minted_rewards_fil', 'total_burn_fil', 'raw_power_pibs', 'fil_token_price_avg_usd']) {
    if (!d.econ[key].some(v => v != null)) throw new Error(`econ.${key}: no observations`)
  }
  for (const key of ['sc', 'pc']) {
    if (!d.quality[key].some(v => v > 0)) throw new Error(`quality.${key}: no observations`)
  }
  if (d.meta.dupe_roles !== 0) throw new Error('Rails mapped to multiple payment roles')
  if (!d.meta.solstice.length) throw new Error('Missing Solstice quarter')
  if (d.storage.b.at(-1) !== d.meta.snapshot.f_bytes || d.storage.mb.at(-1) !== d.meta.snapshot.m_bytes) throw new Error('Billing series and snapshot disagree')
  // JSON.stringify silently turns non-finite numbers into null; never deploy that.
  serialize(d)
}

export function serialize(d) {
  return JSON.stringify(d, (_key, value) => {
    if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('Non-finite number in data')
    return value
  }).replace(/</g, '\\u003c')
}

const dateLabel = s => new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(s))
const nf = (v, p = 0) => v == null ? '—' : v.toLocaleString('en-US', { minimumFractionDigits: p, maximumFractionDigits: p })
const sum = (o, keys, start, end) => keys.reduce((total, key) => total + o[key].slice(Math.max(0, start), end + 1).reduce((a, b) => a + (b ?? 0), 0), 0)

export function render(d, template = fs.readFileSync(new URL('./template.html', import.meta.url), 'utf8')) {
  const S = d.storage, P = d.pay, Q = d.quality, pe = P.date.length - 1, ps = Math.max(0, pe - 29)
  const pooled = (n, den) => {
    const e = Q[den].findLastIndex(v => v != null), s = Math.max(0, e - 29)
    const attempts = sum(Q, [den], s, e)
    return attempts ? nf(sum(Q, [n], s, e) / attempts * 100, 2) + '%' : '—'
  }
  const noscript = `<noscript><div class="wrap"><div class="card"><ul class="facts" aria-label="Snapshot summary">
  <li><span class="k">billing storage · monitoring excluded</span><span class="v">${nf(S.b.at(-1) / 2 ** 40, 2)} TiB</span><span class="n">end of day ${dateLabel(S.date.at(-1))}</span></li>
  <li><span class="k">billing payers</span><span class="v">${nf(S.payers.at(-1))}</span><span class="n">${nf(S.sets.at(-1))} billing data sets</span></li>
  <li><span class="k">FWSS settled · monitoring excluded · up to 30 days</span><span class="v">$${nf(sum(P, categories.slice(0, 4), ps, pe), 2)}</span><span class="n">${dateLabel(P.date[ps])} – ${dateLabel(P.date[pe])}</span></li>
  <li><span class="k">sampled retrieval · up to 30 days</span><span class="v">${pooled('ss', 'sc')}</span><span class="n">PDP faulted periods ${pooled('pf', 'pc')}</span></li>
</ul><p class="note">Built ${d.meta.extracted_at.slice(0, 10)} UTC. Refreshed after each successful daily pipeline; source dates may lag. Charts and the provider table need JavaScript; all data is embedded in this file.</p></div></div></noscript>`
  for (const slot of ['<!--__NOSCRIPT__-->', '/*__DATA__*/null']) {
    if (template.split(slot).length !== 2) throw new Error(`Expected exactly one ${slot} slot`)
  }
  return template.replace('<!--__NOSCRIPT__-->', () => noscript).replace('/*__DATA__*/null', () => serialize(d))
}

if (import.meta.main) {
  const { extract } = await import('./extract.mjs')
  const data = pack(await extract())
  validate(data)
  const html = render(data), dist = new URL('./dist/', import.meta.url)
  fs.mkdirSync(dist, { recursive: true })
  fs.writeFileSync(new URL('index.html.tmp', dist), html)
  fs.renameSync(new URL('index.html.tmp', dist), new URL('index.html', dist))
  console.log(`Built ${Buffer.byteLength(html)} bytes; checkpoint ${data.meta.checkpoint.date}; extracted ${data.meta.extracted_at}`)
}
