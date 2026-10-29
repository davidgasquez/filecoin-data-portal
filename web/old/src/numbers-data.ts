import { archivedOn } from "./archive"
import { query } from "./db"
import { parseDates } from "./numbers"
import { numbersSections } from "./numbers-sections"

const beforeToday = `date < DATE '${archivedOn}'`
export const providerWindowDays = 30

// Only the columns charts use, from the section config.
const columns = [...new Set(numbersSections.flatMap((section) => section.groups.flatMap((group) => group.charts.flatMap((chart) => [
  chart.y,
  ...(chart.series ?? []).map((series) => series.y),
  ...(chart.details ?? []).map((detail) => detail.y),
]))))]

// Pooled across providers: sum of numerators over sum of denominators, never averaged rates.
const pooled = (rate: string, numerator: string, denominator: string) => `
  sum(${numerator})::bigint AS provider_${numerator},
  sum(${denominator})::bigint AS provider_${denominator},
  sum(${numerator})::double / nullif(sum(${denominator}), 0) AS provider_${rate}`

export const daily = await query(`
  WITH quality AS (
    SELECT
      date,${pooled("storage_success_rate", "storage_successes", "storage_checks")},${pooled("retrieval_success_rate", "retrieval_successes", "retrieval_checks")},${pooled("sampled_retrieval_success_rate", "sampled_retrieval_successes", "sampled_retrieval_checks")},${pooled("proving_fault_rate", "proving_periods_faulted", "proving_periods_closed")},
      sum(sampled_retrieval_skipped)::bigint AS provider_sampled_retrieval_skipped
    FROM main.daily_provider_quality
    GROUP BY date
  ), daily AS (
    SELECT *, locked_fil / nullif(circulating_fil, 0) AS locked_to_circulating_ratio, 0 AS high_profile_paying_clients
    FROM main.daily_network_metrics
    FULL JOIN quality USING (date)
  )
  SELECT strftime(date, '%Y-%m-%d') AS date, ${columns.join(", ")}
  FROM daily
  WHERE ${beforeToday}
  ORDER BY date
`)
if (daily.length === 0) throw new Error("No daily metrics rows")
export const dates = parseDates(daily)

// Check types come from different sources, so each window ends at that check's own last covered date.
const checks = {
  storage: ["storage_successes", "storage_checks"],
  retrieval: ["retrieval_successes", "retrieval_checks"],
  sampled: ["sampled_retrieval_successes", "sampled_retrieval_checks", "sampled_retrieval_skipped"],
  proving: ["proving_periods_faulted", "proving_periods_closed"],
}
const checkEnds = Object.entries(checks)
  .map(([check, [, denominator]]) => `strftime(max(date) FILTER (WHERE ${denominator} IS NOT NULL), '%Y-%m-%d') AS ${check}_end`)
  .join(", ")
const checkSums = Object.entries(checks)
  .flatMap(([check, columns]) => columns.map((column) =>
    `sum(${column}) FILTER (WHERE q.date > ends.${check}_end::date - INTERVAL ${providerWindowDays} DAY)::bigint AS ${column}`))
  .join(",\n    ")

export const [providerWindowEnds] = await query(`SELECT ${checkEnds} FROM main.daily_provider_quality WHERE ${beforeToday}`)

export const providers = await query(`
  WITH ends AS (SELECT ${checkEnds} FROM main.daily_provider_quality WHERE ${beforeToday})
  SELECT
    q.provider_id,
    any_value(p.name) AS name,
    ${checkSums}
  FROM main.daily_provider_quality AS q
  LEFT JOIN main.providers AS p USING (provider_id)
  CROSS JOIN ends
  WHERE q.${beforeToday}
    AND q.date > least(${Object.keys(checks).map((check) => `ends.${check}_end::date`).join(", ")}) - INTERVAL ${providerWindowDays} DAY
  GROUP BY q.provider_id
  ORDER BY q.provider_id NULLS LAST
`)

// Atto amounts stay exact strings (DECIMAL(38,0) would lose precision as JSON numbers).
export const quarters = await query(`
  SELECT * REPLACE (
    bound_volume_atto_usd::varchar AS bound_volume_atto_usd,
    shares_total_atto_usd::varchar AS shares_total_atto_usd,
    gate_threshold_atto_usd::varchar AS gate_threshold_atto_usd,
    strftime(gate_checked_at, '%Y-%m-%dT%H:%M:%SZ') AS gate_checked_at,
    strftime(shares_submitted_at, '%Y-%m-%dT%H:%M:%SZ') AS shares_submitted_at
  )
  FROM main.service_quarters
  ORDER BY quarter DESC
`)

export const orchestratorQuarters = await query(`
  SELECT
    quarter, orchestrator, volume_as_of_block, is_complete, is_removed_in_quarter, as_of_block, is_bound, corrections,
    volume_atto_usd::varchar AS volume_atto_usd,
    fil_pending_atto_fil::varchar AS fil_pending_atto_fil,
    reported_volume_atto_usd::varchar AS reported_volume_atto_usd,
    bound_volume_atto_usd::varchar AS bound_volume_atto_usd
  FROM main.orchestrator_quarters
  ORDER BY quarter DESC, orchestrator
`)
