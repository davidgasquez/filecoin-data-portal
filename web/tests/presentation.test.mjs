import { test } from 'node:test'
import assert from 'node:assert/strict'
import { atto, epochTime, format, grouped, kind, percent, plural } from '../src/metrics.mjs'
import { gate, phase, usd } from '../src/solstice.mjs'
import { numbersSections } from '../src/numbers-sections.ts'
import { definition } from '../src/sections.ts'

const primary = numbersSections.flatMap(section => section.groups.flatMap(group => group.charts))

test('concise dollars keep cents; audits and sub-dollar amounts keep their digits', () => {
  assert.equal(format(1234.5, 'filecoin_pay_paid_usd'), '$1,234.50')
  assert.equal(format(12, 'filecoin_pay_paid_usd'), '$12.00')
  assert.equal(format(1234.565, 'filecoin_pay_paid_usd', false), '$1,234.565')
  assert.equal(format(0.5, 'filecoin_pay_paid_usd'), '$0.5')
  assert.equal(format(0.0001234, 'filecoin_pay_paid_usd'), '$0.000123')
  assert.equal(format(-2.5, 'filecoin_pay_paid_usd'), '-$2.50')
  assert.equal(format(0, 'filecoin_pay_paid_usd'), '$0')
})

test('missing, zero and declared values stay distinct', () => {
  for (const missing of [null, undefined, '', 'abc', Infinity]) assert.equal(format(missing, 'filecoin_pay_paid_usd'), 'Not observed')
  assert.equal(percent(null), 'Not observed')
  assert.equal(percent(0), '0%')
  assert.equal(usd(null), null)
  assert.equal(usd('0'), '$0.00')
  assert.equal(epochTime(null), null)
})

test('the same column has one unit and precision on /numbers, /foc headlines and hover', () => {
  // Formerly /foc rendered warm storage with auto-scaled units (PiB) while hover used TiB.
  assert.equal(format(1234.567 * 2 ** 40, 'warm_storage_stored_bytes'), '1,234.57 TiB')
  assert.equal(format(0.98765, 'provider_storage_success_rate'), '98.77%')
  assert.equal(format(0.98765, 'provider_proving_fault_rate'), percent(0.98765))
  assert.equal(format(1234.56, 'retrieval_median_ttfb_ms'), '1,234.56 ms')
  assert.equal(format(1234, 'warm_storage_billing_data_sets'), grouped(1234))
  assert.equal(percent(0.5), '50%')
  assert.equal(plural(1, 'dataset'), '1 dataset')
  assert.equal(plural(12345, 'dataset'), '12,345 datasets')
})

test('shared definitions come from the inventory and never borrow another population', () => {
  for (const column of ['filecoin_pay_gross_payment_volume_run_rate_usd', 'filecoin_pay_paid_usd', 'warm_storage_billing_data_sets', 'warm_storage_stored_bytes', 'filecoin_pay_active_payers', 'filecoin_pay_active_rails'])
    assert.equal(definition(column), primary.find(metric => metric.y === column).description)
  assert.match(definition('warm_storage_stored_bytes'), /every stored copy/)
  assert.equal(definition('provider_storage_success_rate'), '', 'quality columns are pooled differently on /foc')
  assert.equal(definition('high_profile_paying_clients'), '', 'the declared zero has no source definition')
  assert.equal(definition('absent'), '')
})

test('the inventory keeps ids, columns and marks without unused presentation fields', () => {
  assert.equal(new Set(primary.map(metric => metric.id)).size, 52)
  for (const section of numbersSections) assert.deepEqual(Object.keys(section).sort(), ['groups', 'id', 'title'])
  for (const item of [...primary, ...primary.flatMap(metric => metric.details ?? [])])
    for (const field of ['format', 'scale', 'suffix', 'period', 'bounded']) assert.ok(!(field in item), `${item.y}.${field}`)
  // Primary marks are documentation of the column default; they must agree with what is drawn.
  for (const metric of primary.filter(metric => metric.kind)) assert.equal(kind(metric.y), metric.kind, metric.y)
})

test('atto amounts round half up exactly, beyond Number precision', () => {
  assert.equal(atto('1004999999999999999'), '1.00')
  assert.equal(atto('1005000000000000000'), '1.01')
  assert.equal(atto('-1005000000000000000'), '-1.01')
  assert.equal(atto('999999999999999999999999999999'), '1,000,000,000,000.00')
  assert.equal(atto('123456789012345678901234567890', 4), '123,456,789,012.3457')
  assert.equal(usd('9007199254740993000000000000000000'), '$9,007,199,254,740,993.00')
})

test('Solstice phases change exactly at each block boundary', () => {
  const q = { quarter: 2, start_block: '100', end_block: '200', verification_start_block: '300', is_bound: false }
  const at = (as_of_block, extra = {}) => phase({ ...q, as_of_block, ...extra })
  assert.equal(at(null), 'Unknown')
  assert.equal(at(undefined), 'Unknown')
  assert.equal(at('99'), 'Not started')
  assert.equal(at('100'), 'In quarter, partial')
  assert.equal(at(200), 'In quarter, partial')
  assert.equal(at(201), 'Posting window')
  assert.equal(at(299), 'Posting window')
  assert.equal(at(300), 'Verification window')
  assert.equal(at(300, { is_bound: true }), 'Bound')
  assert.equal(at(250, { is_bound: true }), 'Posting window', 'binding is only read after verification starts')
})

test('Solstice gates distinguish not gated, not observed, passed and failed', () => {
  assert.equal(gate({ quarter: 1, gate_checked_at: '2026-01-01', gate_passed: false }), 'Not gated')
  assert.equal(gate({ quarter: '1' }), 'Not gated')
  assert.equal(gate({ quarter: 2, gate_checked_at: null, gate_passed: null }), null)
  assert.equal(gate({ quarter: 2, gate_checked_at: 1767225600, gate_passed: null }), null)
  assert.equal(gate({ quarter: 2, gate_checked_at: 1767225600, gate_passed: true }), 'Passed')
  assert.equal(gate({ quarter: 2, gate_checked_at: '2026-01-01 00:00:00', gate_passed: false }), 'Failed')
})

test('epochs map to UTC minutes from mainnet genesis', () => {
  assert.equal(epochTime(0), '2020-08-24 22:00')
  assert.equal(epochTime('2880'), '2020-08-25 22:00')
})
