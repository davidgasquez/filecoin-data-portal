import { sections } from './sections.ts'

// Validate stored inputs, not derived chart names (pooled rates and the locked ratio).
export const metricSources = [...new Set(sections.flatMap(section => section.groups.flatMap(group => group.charts))
  .filter(metric => metric.source !== null)
  .flatMap(metric => {
    const table = metric.source ?? 'daily_network_metrics'
    const columns = [...(metric.columns ?? [metric.y]), ...(metric.details ?? []).map(item => item.y), ...(metric.series ?? []).map(item => item.y)]
    return columns.map(column => `${table}.${table === 'daily_provider_quality' ? column.replace(/^provider_/, '') : column}`)
  }))].sort()

export function missingMetricSources(datasets: { id: string; columns: { name: string }[] }[]) {
  const available = new Set(datasets.flatMap(dataset => dataset.columns.map(column => `${dataset.id}.${column.name}`)))
  return metricSources.filter(source => !available.has(source))
}
