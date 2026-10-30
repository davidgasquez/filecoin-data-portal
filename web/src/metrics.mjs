export const DAY = 86_400_000
export const number = (value) => value == null || value === '' || !Number.isFinite(Number(value)) ? null : Number(value)
// Presentation precision only. Preserve raw source values and exact atto strings.
export const displayNumber = (value, key = '') => {
  const n = number(value)
  return n == null ? null : key.endsWith('_fil') ? Number(n.toFixed(6)) : n
}
export const dateLabel = (date) => new Intl.DateTimeFormat('en', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(date))
export const shiftDate = (date, days) => new Date(Date.parse(date) + days * DAY).toISOString().slice(0, 10)
export const title = (key) => key.replaceAll('_', ' ').replace(/\b(fil|usd|gpv|apy|tvl|usdfc)\b/g, (word) => word.toUpperCase()).replace(/^./, (word) => word.toUpperCase())
const percentages = new Set(['burn_coverage_ratio', 'yearly_inflation_rate', 'mining_yield', 'ifil_base_apy', 'locked_to_circulating_ratio', 'pdp_replication_coverage'])
const flows = new Set(`transactions onboarded_pibs terminated_pibs expired_pibs removed_pibs gas_used_millions total_value_fil total_value_flow_fil total_gas_fee_fil base_fee_burn_fil base_fee_burn_usd overestimation_burn_fil overestimation_burn_usd message_burn_fil message_burn_usd miner_tip_fil miner_tip_usd message_storage_provider_penalty_fil message_storage_provider_penalty_usd storage_provider_cron_burn_fil storage_provider_cron_burn_usd storage_provider_cron_fee_assessed_fil storage_provider_cron_penalty_assessed_fil unattributed_burn_fil unattributed_burn_usd total_burn_fil total_burn_usd emission_burn_fil emission_burn_usd non_emission_burn_fil non_emission_burn_usd filecoin_pay_paid_usd warm_storage_new_billing_payers warm_storage_new_billing_data_sets fil_token_volume_usd blocks_mined win_count minted_rewards_fil minted_rewards_usd miner_rewards_fil miner_rewards_usd service_rewards_fil service_rewards_usd`.split(' '))
export const kind = (key) => flows.has(key) ? 'bar' : /billing_|active_|stored_bytes|providers_with_power/.test(key) ? 'step' : 'line'
export function unit(key) {
  if (percentages.has(key) || /^provider_.*_rate$/.test(key)) return { scale: 0.01, suffix: '%' }
  if (key.endsWith('_ms')) return { scale: 1, suffix: ' ms' }
  if (key.endsWith('_bytes')) return { scale: 2 ** 40, suffix: ' TiB' }
  if (key.endsWith('_pibs')) return { scale: 1, suffix: ' PiB' }
  if (key.endsWith('_usd')) return { scale: 1, prefix: '$', suffix: '' }
  if (key.endsWith('_fil')) return { scale: 1, suffix: ' FIL' }
  if (key === 'gas_used_millions') return { scale: 1, suffix: ' million gas' }
  if (key === 'usdfc_supply') return { scale: 1, suffix: ' USDFC' }
  return { scale: 1, suffix: '' }
}
// One precision per column wherever it appears: chart headlines and hover are concise, audits keep 6 decimals.
// Concise amounts of at least $1 keep cents; smaller ones keep 3 significant digits rather than rounding to zero.
export function format(value, key = '', concise = true, u = unit(key)) {
  const n = displayNumber(value, key)
  if (n == null) return 'Not observed'
  const scaled = n / u.scale, cents = concise && u.prefix === '$' && Math.abs(scaled) >= 1
  const formatted = new Intl.NumberFormat('en', {
    notation: 'standard',
    ...(cents ? { minimumFractionDigits: 2, maximumFractionDigits: 2 } : Math.abs(scaled) < 1 ? { maximumSignificantDigits: concise ? 3 : 6 } : { maximumFractionDigits: concise ? 2 : 6 }),
  }).format(u.prefix ? Math.abs(scaled) : scaled)
  return `${u.prefix && scaled < 0 ? '-' : ''}${u.prefix ?? ''}${formatted}${u.suffix}`
}
export const percent = (value, concise = true) => format(value, '', concise, { scale: 0.01, suffix: '%' })
export const grouped = (n) => new Intl.NumberFormat('en').format(n)
export const plural = (n, word, many = `${word}s`) => `${grouped(n)} ${n === 1 ? word : many}`
// Mainnet epochs are 30 s apart from genesis (unix seconds). `YYYY-MM-DD HH:MM` UTC, or null when unknown.
export const GENESIS = 1_598_306_400
export const epochTime = (epoch) => number(epoch) == null ? null : new Date((GENESIS + Number(epoch) * 30) * 1000).toISOString().slice(0, 16).replace('T', ' ')
export function latest(rows, key) {
  const row = rows.findLast((row) => number(row[key]) != null)
  return row ? { date: String(row.date), value: number(row[key]) } : null
}
/** @returns {{ date: string, value: number | null }[]} */
export function series(rows, key, days = 365) {
  const end = latest(rows, key)?.date
  if (!end) return []
  const first = rows.find((row) => number(row[key]) != null).date
  const start = days ? [String(first), shiftDate(end, 1 - days)].sort().at(-1) : String(first)
  const byDate = new Map(rows.map((row) => [String(row.date), displayNumber(row[key], key)]))
  const points = []
  for (let date = start; date <= end; date = shiftDate(date, 1)) points.push({ date, value: byDate.get(date) ?? null })
  return points
}
// Chart windows end at each chart's own last observation and cover whole calendar months: the day after
// the same date N months earlier, clamped to month end (6m ending 2026-08-31 starts 2026-03-01). `all` has no start.
export const ranges = { '6m': 6, '1y': 12, all: 0 }
export const defaultRange = '6m'
export function rangeStart(end, range) {
  const months = ranges[range]
  if (!months) return null
  const [y, m, d] = end.split('-').map(Number)
  const days = new Date(Date.UTC(y, m - months, 0)).getUTCDate()
  return shiftDate(new Date(Date.UTC(y, m - 1 - months, Math.min(d, days))).toISOString().slice(0, 10), 1)
}
export function within(points, range) {
  const start = points.length ? rangeStart(points.at(-1).date, range) : null
  return start ? points.filter((point) => point.date >= start) : points
}
export const expand = ({ start, values }) => values.map((value, i) => ({ date: shiftDate(start, i), value }))
// Two series on one daily axis, from the earlier first to the later last observation. Each keeps its own nulls.
export function align(a, b) {
  const dates = [a[0]?.date, a.at(-1)?.date, b[0]?.date, b.at(-1)?.date].filter(Boolean).sort()
  const byDate = [new Map(a.map((point) => [point.date, point.value])), new Map(b.map((point) => [point.date, point.value]))]
  const out = [[], []]
  for (let date = dates[0]; dates.length && date <= dates.at(-1); date = shiftDate(date, 1)) byDate.forEach((map, i) => out[i].push({ date, value: map.get(date) ?? null }))
  return out
}
export function windowTotal(rows, key, days = 30) {
  const points = series(rows, key, days)
  return { value: points.reduce((sum, point) => sum + (point.value ?? 0), 0), count: points.filter((point) => point.value != null).length, days, start: points[0]?.date, end: points.at(-1)?.date }
}
export function change(rows, key, days = 30) {
  const end = latest(rows, key)
  const before = end && number(rows.find((row) => row.date === shiftDate(end.date, -days))?.[key])
  return end && before != null ? end.value - before : null
}
export function qualityWindow(rows, providers, numerator, denominator, days = 30) {
  const end = latest(rows, denominator)?.date
  if (!end) return { end: null, start: null, rows: [], successes: 0, attempts: 0 }
  const start = shiftDate(end, 1 - days)
  const groups = new Map()
  for (const row of rows) {
    if (row.date < start || row.date > end || number(row[numerator]) == null || number(row[denominator]) == null) continue
    const id = row.provider_id == null ? 'unrecorded' : String(row.provider_id)
    const group = groups.get(id) ?? { id, name: providers.find((p) => String(p.provider_id) === id)?.name ?? `Provider ${id}`, successes: 0, attempts: 0 }
    group.successes += number(row[numerator]); group.attempts += number(row[denominator])
    groups.set(id, group)
  }
  const result = [...groups.values()].map((row) => ({ ...row, rate: row.attempts > 0 ? row.successes / row.attempts : null }))
    .sort((a, b) => (b.rate ?? -1) - (a.rate ?? -1) || b.attempts - a.attempts)
  return { start, end, rows: result, successes: result.reduce((sum, row) => sum + row.successes, 0), attempts: result.reduce((sum, row) => sum + row.attempts, 0) }
}
export const qualityChecks = [
  ['storage_success_rate', 'storage_successes', 'storage_checks'],
  ['retrieval_success_rate', 'retrieval_successes', 'retrieval_checks'],
  ['sampled_retrieval_success_rate', 'sampled_retrieval_successes', 'sampled_retrieval_checks'],
  ['proving_fault_rate', 'proving_periods_faulted', 'proving_periods_closed'],
]
export function pooledQuality(rows) {
  const dates = new Map()
  const columns = [...new Set(qualityChecks.flatMap(([, a, b]) => [a, b])), 'sampled_retrieval_skipped']
  for (const row of rows) {
    const result = dates.get(row.date) ?? { date: row.date }
    for (const column of columns) {
      const key = `provider_${column}`, value = number(row[column])
      result[key] = value == null ? (result[key] ?? null) : (result[key] ?? 0) + value
    }
    dates.set(row.date, result)
  }
  return [...dates.values()].map((row) => {
    for (const [rate, numerator, denominator] of qualityChecks) {
      const a = row[`provider_${numerator}`], b = row[`provider_${denominator}`]
      row[`provider_${rate}`] = a != null && b > 0 ? a / b : null
    }
    return row
  })
}
// Atto amounts never pass through floating-point numbers.
export function atto(value, decimals = 2) {
  if (value == null) return 'Not observed'
  const amount = BigInt(String(value).replace(/\.0+$/, ''))
  const negative = amount < 0n
  const divisor = 10n ** BigInt(18 - decimals), places = 10n ** BigInt(decimals)
  const rounded = ((negative ? -amount : amount) + divisor / 2n) / divisor
  return `${negative ? '-' : ''}${new Intl.NumberFormat('en').format(rounded / places)}.${String(rounded % places).padStart(decimals, '0')}`
}
