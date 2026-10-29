import { test } from 'node:test'
import assert from 'node:assert/strict'
import { rangeStart, within, align, expand, series } from '../src/metrics.mjs'
import { chart, draw, geometry, indexAt, xAt } from '../src/charts.mjs'

const days = (start, values) => expand({ start, values })
const subpaths = (path) => path.match(/M[^M]*/g) ?? []

test('ranges are whole calendar months ending at the last observation', () => {
  assert.equal(rangeStart('2026-10-28', '6m'), '2026-04-29')
  assert.equal(rangeStart('2026-10-28', '1y'), '2025-10-29')
  assert.equal(rangeStart('2026-08-31', '6m'), '2026-03-01')
  assert.equal(rangeStart('2024-02-29', '1y'), '2023-03-01')
  assert.equal(rangeStart('2026-03-31', '1y'), '2025-04-01')
  assert.equal(rangeStart('2026-01-15', '6m'), '2025-07-16')
  assert.equal(rangeStart('2026-10-28', 'all'), null)
  assert.equal(rangeStart('2026-10-28', 'bogus'), null)
})
test('windows clamp to the first observation and all keeps the full history', () => {
  const full = days('2020-08-24', Array.from({ length: 2256 }, (_, i) => i))
  assert.equal(within(full, 'all'), full)
  assert.equal(within(full, 'all')[0].date, '2020-08-24')
  const sixMonths = within(full, '6m')
  assert.equal(sixMonths.at(-1).date, full.at(-1).date)
  assert.equal(sixMonths[0].date, rangeStart(full.at(-1).date, '6m'))
  assert.ok(within(full, '1y').length > 365 - 1 && within(full, '1y').length <= 366)
  const short = days('2026-09-01', [1, 2, 3])
  assert.deepEqual(within(short, '1y'), short)
})
test('each series windows from its own latest observation', () => {
  const rows = [{ date: '2026-01-01', a: 1, b: 1 }, { date: '2026-09-30', a: 2, b: null }, { date: '2026-10-28', a: null, b: 3 }]
  assert.equal(within(series(rows, 'a', 0), '6m').at(-1).date, '2026-09-30')
  assert.equal(within(series(rows, 'a', 0), '6m')[0].date, '2026-03-31')
  assert.equal(within(series(rows, 'b', 0), '6m')[0].date, '2026-04-29')
})
test('combined series share one axis but keep independent nulls and zeros', () => {
  const [a, b] = align(days('2026-01-02', [1, null, 0]), days('2026-01-01', [5, 0, null, 2, 7]))
  assert.deepEqual(a.map((p) => p.date), b.map((p) => p.date))
  assert.equal(a[0].date, '2026-01-01')
  assert.equal(a.at(-1).date, '2026-01-05')
  assert.deepEqual(a.map((p) => p.value), [null, 1, null, 0, null])
  assert.deepEqual(b.map((p) => p.value), [5, 0, null, 2, 7])
  assert.deepEqual(align([], days('2026-01-01', [1])), [[{ date: '2026-01-01', value: null }], [{ date: '2026-01-01', value: 1 }]])
})
test('bars are contiguous filled daily bins: shared edges, exact heights, no smoothing', () => {
  const points = days('2026-01-01', [2, 2, 8, 0, 4])
  const g = geometry(points, 'bar')
  assert.equal(g.min, 0)
  assert.equal(g.max, 8)
  // Closed silhouettes; equal neighbours merge; zero closes a run; each step lands on a bin edge (634 / 5 per day).
  assert.equal(g.path, 'M3.00,140.00V106.00H256.60V4.00H383.40V140.00ZM510.20,140.00V72.00H637.00V140.00Z')
  assert.equal(subpaths(g.path).length, 2)
  assert.doesNotMatch(g.path, /NaN|Infinity/)
  assert.equal(g.baseline, 'M3.00,140.00H637.00')
})
test('missing days split bars and the zero line; observed zeros keep the zero line', () => {
  const g = geometry(days('2026-01-01', [3, null, 0, 0, null, 3]), 'bar')
  assert.equal(subpaths(g.path).length, 2)
  assert.equal(subpaths(g.baseline).length, 3)
  assert.match(g.baseline, /M3\.00,140\.00H108\.67/)
  assert.match(g.baseline, /M214\.33,140\.00H425\.67/)
  const allMissing = geometry(days('2026-01-01', [null, null]), 'bar')
  assert.equal(allMissing, null)
})
test('signed bars grow both ways from one zero baseline', () => {
  const g = geometry(days('2026-01-01', [-4, 4]), 'bar')
  assert.equal(g.min, -4)
  assert.equal(g.max, 4)
  assert.equal(subpaths(g.path).length, 2)
  assert.match(g.path, /V4\.00/)
  assert.match(g.path, /V140\.00/)
  for (const point of g.path.matchAll(/[MV](?:[\d.]+,)?([\d.]+)/g)) assert.ok(Number(point[1]) >= 4 && Number(point[1]) <= 140)
})
test('a negative companion draws below zero without netting or changing its values', () => {
  const up = days('2026-01-01', [4, null, 0])
  const down = days('2026-01-01', [2, 1, null])
  const g = geometry(up, 'bar', 640, 144, false, down)
  assert.equal(g.min, -2)
  assert.equal(g.max, 4)
  assert.equal(g.low, 0)
  assert.equal(g.high, 4)
  const zero = 4 + (4 / 6) * 136
  for (const [, y] of g.negativePath.matchAll(/V([\d.]+)/g)) assert.ok(Number(y) >= zero - 0.01)
  for (const [, y] of g.path.matchAll(/V([\d.]+)/g)) assert.ok(Number(y) <= zero + 0.01)
  // Day 2 has only a terminated value, day 3 only an onboarded zero: the zero line covers all three.
  assert.equal(subpaths(g.baseline).length, 1)
  const output = chart(up, 'onboarded_pibs', 'bar', { label: 'Onboarded', interactive: true, negative: { points: down, key: 'terminated_pibs', label: 'Terminated' } })
  assert.match(output, /data-values="\[4,null,0\]"/)
  assert.match(output, /data-negative-values="\[2,1,null\]"/)
  assert.match(output, /data-negative-key="terminated_pibs"/)
  assert.match(output, /class="bars negative"/)
  assert.equal((output.match(/chart-marker/g) ?? []).length, 2)
  assert.equal((output.match(/<strong><\/strong>/g) ?? []).length, 2)
  assert.match(output, /Terminated\. 2026-01-01: 2 PiB\. Latest 2026-01-02: 1 PiB/)
  assert.match(output, /Vertical scale -2 PiB to 4 PiB, bars from zero/)
  assert.doesNotMatch(output, /-1 PiB|Minimum -/)
})
test('scale lives in the description, not in a visible footer', () => {
  const output = chart(days('2026-01-01', [1200, 1250]), 'raw_power_pibs', 'line', { label: 'Raw', interactive: true })
  assert.doesNotMatch(output, /chart-scale|Zero baseline/)
  assert.match(output, /aria-label="Raw\. [^"]*Vertical scale 1,200 PiB to 1,250 PiB, not from zero\./)
  assert.match(output, /chart-dates[^]*2026-01-01[^]*2026-01-02/)
})
test('miniature bars group days into columns of their extremes, keeping spikes and long gaps', () => {
  const values = Array.from({ length: 2000 }, (_, i) => i === 1234 ? 999 : i >= 600 && i < 700 ? null : 1)
  const g = geometry(days('2020-01-01', values), 'bar', 160, 28, true)
  assert.equal(g.size, 25)
  assert.equal(subpaths(g.path).length, 2)
  assert.match(g.path, /V4\.00/)
  assert.ok(g.path.length < 400)
  assert.match(draw(days('2020-01-01', values), 'n', 'bar', { mini: true }).svg, /Each column spans 25 days/)
})
test('hover positions match bar bins and line points', () => {
  for (const n of [1, 5, 183, 2256]) for (const i of [0, Math.floor(n / 2), n - 1]) {
    assert.equal(indexAt(xAt(i, n, 'bar'), n, 'bar'), i)
    assert.equal(indexAt(xAt(i, n, 'line'), n, 'line'), i)
  }
  assert.equal(xAt(0, 1, 'line'), 3)
  assert.equal(indexAt(3, 5, 'bar'), 0)
  assert.equal(indexAt(636.99, 5, 'bar'), 4)
})
