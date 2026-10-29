import { test } from 'node:test'
import assert from 'node:assert/strict'
import { numbersSections } from '../src/numbers-sections.ts'
import { sections, declaredMetrics } from '../src/sections.ts'

const primary = items => items.flatMap(section => section.groups.flatMap(group => group.charts))
const allColumns = items => primary(items).flatMap(metric => [metric.y, ...(metric.details ?? []).map(item => item.y), ...(metric.series ?? []).filter(item => item.y !== metric.y).map(item => item.y)])

test('v1 inventory stays represented except the intentionally omitted Complete Days detail', () => {
  assert.deepEqual(allColumns(sections).sort(), allColumns(numbersSections).filter(column => column !== 'annual_coverage_days').sort())
  assert.ok(primary(numbersSections).find(metric => metric.y === 'burn_coverage_ratio').details.some(detail => detail.y === 'annual_coverage_days'), 'The upstream inventory is not mutated')
  assert.ok(primary(sections).some(metric => metric.y === 'locked_to_circulating_ratio'))
  assert.ok(primary(sections).some(metric => metric.y === 'provider_proving_fault_rate'))
})
test('PDP volume headlines unique bytes and labels copies separately in both inventories', () => {
  for (const inventory of [numbersSections, sections]) {
    const charts = primary(inventory)
    const volume = charts.find(metric => metric.id === 'pdp-data-volume')
    assert.equal(volume.title, 'PDP Data Volume')
    assert.equal(volume.y, 'pdp_unique_bytes')
    assert.deepEqual(volume.series, [
      { label: 'Unique data', y: 'pdp_unique_bytes' },
      { label: 'Unique data on 2+ providers', y: 'pdp_replicated_bytes' },
      { label: 'Total registered data (including copies)', y: 'pdp_registered_bytes' },
    ])
    assert.equal(charts.find(metric => metric.y === 'pdp_replication_coverage').title, 'PDP Replication Coverage')
    assert.match(charts.find(metric => metric.y === 'warm_storage_stored_bytes').title, /Including Copies/)
  }
})
test('the requested legacy zero remains explicitly declared, not an invented time series', () => {
  assert.deepEqual(declaredMetrics.map(metric => metric.id), ['high-profile-paying-clients'])
  assert.equal(declaredMetrics[0].value, 0)
  assert.equal(declaredMetrics[0].source, null)
  assert.match(declaredMetrics[0].reason, /no dated source/)
})
