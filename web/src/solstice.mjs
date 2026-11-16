// Solstice quarter decisions shared by /numbers and the explorer. Values are as published; pages only label them.
// Callers keep their own field names, timestamps and markup.
import { atto, number } from './metrics.mjs'

// Phase from the latest observed block against the quarter's block windows.
export function phase(q) {
  const at = number(q.as_of_block)
  if (at == null) return 'Unknown'
  if (at < Number(q.start_block)) return 'Not started'
  if (at <= Number(q.end_block)) return 'In quarter, partial'
  if (at < Number(q.verification_start_block)) return 'Posting window'
  return q.is_bound ? 'Bound' : 'Verification window'
}
// Quarter 1 is never gated. Otherwise null until a check (and its outcome) is observed.
export const gate = (q) => Number(q.quarter) === 1 ? 'Not gated'
  : q.gate_checked_at == null || q.gate_passed == null ? null
  : q.gate_passed ? 'Passed' : 'Failed'
// Sum published orchestrator facts exactly. Missing calculated values invalidate the total;
// posted sums cover observed posts only, and no posts is not a posted zero.
export function totals(rows) {
  const sum = (key, all) => {
    const known = rows.filter(r => r[key] != null)
    return !known.length || (all && known.length !== rows.length) ? null
      : known.reduce((n, r) => n + BigInt(r[key]), 0n).toString()
  }
  return { calculated: sum('volume', true), posted: sum('posted_volume', false),
    posts: rows.filter(r => r.posted_volume != null).length, orchestrators: rows.length }
}

// Exact native token units from published base units; unknown decimals stay unknown.
export function nativeAmount(value, decimals) {
  if (value == null || decimals == null) return null
  const d = Number(decimals), n = BigInt(value), scale = 10n ** BigInt(d)
  const fraction = d ? (n % scale).toString().padStart(d, '0').replace(/0+$/, '') : ''
  return `${(n / scale).toLocaleString('en-US')}${fraction ? `.${fraction}` : ''}`
}

// Exact atto USD, rounded to cents for display only. null stays unknown, never $0.
export const usd = (value) => value == null ? null : `$${atto(value)}`
