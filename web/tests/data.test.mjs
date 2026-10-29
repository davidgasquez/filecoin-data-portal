import { test } from 'node:test'
import assert from 'node:assert/strict'
import { latest, series, windowTotal, qualityWindow, pooledQuality, change, atto, format, kind } from '../src/metrics.mjs'
import { chart, geometry, thin } from '../src/charts.mjs'

const rows = [{ date: '2026-01-01', n: 0 }, { date: '2026-01-03', n: 10 }, { date: '2026-01-04', n: null }]

test('unknown and zero are distinct, and latest is metric-specific', () => {
  assert.equal(format(null), 'Not observed')
  assert.equal(format(0), '0')
  assert.equal(format(1.37e-14, 'emission_burn_fil'), '0 FIL')
  assert.equal(format(0.000001, 'emission_burn_fil'), '0.000001 FIL')
  assert.equal(format(1285.4818, 'raw_power_pibs'), '1,285.48 PiB')
  assert.equal(format(136264.7558, 'value_usd'), '$136,264.76')
  assert.deepEqual(latest(rows, 'n'), { date: '2026-01-03', value: 10 })
  assert.equal(latest(rows, 'absent'), null)
})
test('FIL presentation removes arithmetic residue without changing source facts', () => {
  const source = [{ date: '2026-10-26', emission_burn_fil: 1.3748e-14 }]
  assert.equal(series(source, 'emission_burn_fil')[0].value, 0)
  assert.equal(latest(source, 'emission_burn_fil').value, 1.3748e-14)
  assert.equal(format(1.3748e-14, 'emission_burn_fil', false), '0 FIL')
})
test('series inserts missing days rather than joining gaps', () => {
  assert.deepEqual(series(rows, 'n', 0), [{ date: '2026-01-01', value: 0 }, { date: '2026-01-02', value: null }, { date: '2026-01-03', value: 10 }])
  const g = geometry(series(rows, 'n', 0))
  assert.equal((g.path.match(/M/g) ?? []).length, 2)
  assert.equal((g.path.match(/L/g) ?? []).length, 0)
})
test('partial windows report observed days instead of implying completeness', () => {
  assert.equal(windowTotal(rows, 'n', 30).count, 2)
  assert.equal(windowTotal(rows, 'n', 30).value, 10)
  assert.equal(windowTotal(rows, 'n', 30).days, 30)
  assert.equal(change(rows, 'n', 2), 10)
  assert.equal(change(rows, 'n', 1), null)
})
test('pooled quality counts, not mean rates; zero attempts stay undefined', () => {
  const q = qualityWindow([
    { date: '2026-01-01', provider_id: 1, wins: 1, tries: 1 },
    { date: '2026-01-01', provider_id: 2, wins: 0, tries: 9 },
    { date: '2026-01-01', provider_id: 3, wins: 0, tries: 0 },
    { date: '2026-01-02', provider_id: 1, wins: null, tries: null },
  ], [], 'wins', 'tries')
  assert.equal(q.end, '2026-01-01')
  assert.equal(q.successes / q.attempts, 0.1)
  assert.equal(q.rows.find((row) => row.id === '3').rate, null)
  assert.equal(q.rows.filter((row) => row.attempts > 0).length, 2)
})
test('quality windows do not combine different latest dates', () => {
  const q = qualityWindow([
    { date: '2025-11-01', provider_id: 1, a: 99, b: 100 },
    { date: '2026-01-01', provider_id: 1, a: 1, b: 2 },
  ], [], 'a', 'b')
  assert.equal(q.attempts, 2)
  assert.equal(q.start, '2025-12-03')
})
test('positive and negative bars include zero; flat lines do not divide by zero', () => {
  for (const values of [[4, 9], [-9, -4], [-4, 9], [0, 0]]) {
    const g = geometry(values.map((value, i) => ({ date: `2026-01-0${i + 1}`, value })), 'bar')
    assert.ok(g.min <= 0 && g.max >= 0)
    const zero = Number(g.baseline.match(/^M[\d.]+,([\d.]+)/)[1])
    assert.ok(zero >= 4 && zero <= 140)
    assert.doesNotMatch(g.path, /NaN|Infinity/)
  }
  assert.doesNotMatch(chart([{ date: '2026-01-01', value: 0 }], 'n'), /NaN|Infinity/)
})
test('min/max reduction retains spikes and missing intervals', () => {
  const points = Array.from({ length: 1000 }, (_, i) => ({ date: String(i), value: i === 301 ? 9999 : i >= 490 && i < 510 ? null : i % 7 }))
  const reduced = thin(points, 10)
  assert.ok(reduced.some((p) => p.value === 9999))
  assert.ok(reduced.some((p) => p.value === null))
  assert.deepEqual(reduced[0], points[0])
  assert.deepEqual(reduced.at(-1), points.at(-1))
})
test('daily quality series pool counts and preserve absent and zero-attempt days', () => {
  const pooled = pooledQuality([
    { date: '2026-01-01', storage_successes: 1, storage_checks: 1 },
    { date: '2026-01-01', storage_successes: 0, storage_checks: 9 },
    { date: '2026-01-02', storage_successes: 0, storage_checks: 0 },
    { date: '2026-01-03', storage_successes: null, storage_checks: null },
  ])
  assert.equal(pooled[0].provider_storage_success_rate, 0.1)
  assert.equal(pooled[0].provider_storage_checks, 10)
  assert.equal(pooled[1].provider_storage_success_rate, null)
  assert.equal(pooled[1].provider_storage_checks, 0)
  assert.equal(pooled[2].provider_storage_successes, null)
  assert.equal(pooled[2].provider_retrieval_success_rate, null)
})
test('interactive charts expose each real daily value and its actual UTC start', () => {
  const output = chart([{ date: '2026-01-01', value: 0 }, { date: '2026-01-02', value: null }, { date: '2026-01-03', value: 10 }], 'raw_power_pibs', 'bar', { interactive: true })
  assert.match(output, /data-values="\[0,null,10\]"/)
  assert.match(output, /data-start="2026-01-01"/)
  assert.match(output, /tabindex="0"/)
  assert.match(output, /data-kind="bar"/)
  assert.match(output, /class="bars" d="[^"]+" fill="currentColor"/)
  assert.doesNotMatch(output, /Scale|Zero baseline/)
})
test('chart readouts stay concise without abbreviating or hiding small values', () => {
  assert.equal(format(136264.755837, 'value_usd'), '$136,264.76')
  assert.equal(format(0.391998, 'onboarded_pibs'), '0.392 PiB')
  assert.equal(format(0.000000123, 'value_usd'), '$0.000000123')
  assert.equal(format(0.000000123, 'value_usd', false), '$0.000000123')
  assert.equal(format(136264.755837, 'value_usd', false), '$136,264.755837')
})

test('latency readouts retain their milliseconds unit', () => {
  assert.equal(format(1234.5, 'retrieval_median_ttfb_ms'), '1,234.5 ms')
})

test('replication coverage is displayed as a percentage, not a fraction', () => {
  assert.equal(format(0.985, 'pdp_replication_coverage'), '98.5%')
})

test('atto amounts stay exact beyond Number precision', () => {
  assert.equal(atto('12345678901234567890123456789012345678'), '12,345,678,901,234,567,890.12')
  assert.equal(atto('1995000000000000000'), '2.00')
  assert.equal(atto('12345678901234567890123456789012345678', 4), '12,345,678,901,234,567,890.1235')
  assert.equal(atto('-1500000000000000000'), '-1.50')
  assert.equal(atto(null), 'Not observed')
})
test('chart descriptions escape markup and flow types are meaningful', () => {
  assert.equal(kind('filecoin_pay_paid_usd'), 'bar')
  assert.equal(kind('warm_storage_billing_payers'), 'step')
  assert.equal(kind('raw_power_pibs'), 'line')
  assert.doesNotMatch(chart([{ date: '2026-01-01', value: 1 }], 'n', 'line', { label: '<script>' }), /<script>/)
})
