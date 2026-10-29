import { numbersSections } from './numbers-sections.ts'

// Reuse the public inventory. Keep the explicitly requested legacy zero separate
// from measured series: it has no source table or dated observations.
export const declaredMetrics = numbersSections.flatMap(section => section.groups.flatMap(group => group.charts))
  .filter(metric => metric.id === 'high-profile-paying-clients' && metric.source === null)
  .map(metric => ({ ...metric, value: 0, reason: 'Declared legacy value; no dated source or client registry.' }))
export const sections = numbersSections.filter(section => section.id !== 'solstice').map(section => ({
  ...section,
  groups: section.groups.map(group => ({
    ...group,
    charts: group.charts
      .filter(metric => metric.source !== null || declaredMetrics.some(item => item.id === metric.id))
      .map(metric => metric.y === 'burn_coverage_ratio'
        ? { ...metric, details: metric.details?.filter(detail => detail.y !== 'annual_coverage_days') }
        : metric),
  })),
}))
export type { NumbersMetric } from './numbers-sections.ts'
