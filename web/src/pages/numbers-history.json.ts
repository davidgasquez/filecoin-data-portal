import { daily } from '../data'
import { series } from '../metrics.mjs'
import { sections } from '../sections'

// Full daily history for the Numbers range control, fetched only when a reader widens a chart past
// the default window. A static build artifact, not an API. Same values (and FIL display precision) as the page.
export function GET() {
  const metrics = sections.flatMap(section => section.groups.flatMap(group => group.charts)).filter(metric => metric.source !== null)
  const columns = [...new Set(metrics.flatMap(metric => [metric.y, ...(metric.details ?? []).map(item => item.y), ...(metric.series ?? []).map(item => item.y)]))]
  const history: Record<string, { start: string; values: (number | null)[] }> = {}
  for (const key of columns) {
    const points: { date: string; value: number | null }[] = series(daily, key, 0)
    if (points.length) history[key] = { start: points[0].date, values: points.map((point) => point.value) }
  }
  return new Response(JSON.stringify(history), { headers: { 'Content-Type': 'application/json' } })
}
