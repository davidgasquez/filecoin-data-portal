// Solstice quarter decisions shared by /numbers and /foc. Values are as published; pages only label them.
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
// Exact atto USD, rounded to cents for display only. null stays unknown, never $0.
export const usd = (value) => value == null ? null : `$${atto(value)}`
