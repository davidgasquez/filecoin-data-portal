import { test } from 'node:test'
import assert from 'node:assert/strict'
import { metricSources, missingMetricSources } from '../src/schema.ts'

const complete = Object.entries(Object.groupBy(metricSources, source => source.split('.')[0]))
  .map(([id, sources]) => ({ id, columns: sources.map(source => ({ name: source.split('.')[1] })) }))

test('metric schema checks stored inputs and every plotted companion, not declared/derived values', () => {
  assert.deepEqual(missingMetricSources(complete), [])
  for (const column of ['locked_fil', 'circulating_fil', 'pdp_unique_bytes', 'pdp_replicated_bytes', 'pdp_registered_bytes', 'pdp_replication_coverage', 'terminated_pibs']) {
    assert.ok(metricSources.includes(`daily_network_metrics.${column}`), column)
  }
  assert.ok(metricSources.includes('daily_provider_quality.storage_checks'))
  assert.ok(metricSources.includes('daily_provider_quality.sampled_retrieval_skipped'))
  for (const column of ['high_profile_paying_clients', 'locked_to_circulating_ratio', 'annual_coverage_days']) {
    assert.ok(!metricSources.includes(`daily_network_metrics.${column}`), column)
  }
  assert.ok(!metricSources.some(source => source.includes('.provider_')))
})

test('an older published schema reports exact missing columns without substituting zero', () => {
  const old = complete.map(table => ({ ...table, columns: table.columns.filter(column => !column.name.startsWith('pdp_')) }))
  assert.deepEqual(missingMetricSources(old), [
    'daily_network_metrics.pdp_registered_bytes', 'daily_network_metrics.pdp_replicated_bytes',
    'daily_network_metrics.pdp_replication_coverage', 'daily_network_metrics.pdp_unique_bytes',
  ])
  assert.deepEqual(missingMetricSources([]), metricSources)
})
