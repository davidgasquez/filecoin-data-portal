import { format, number } from './metrics.mjs'

export const escape = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]))
// Keep local extrema and gaps. This reduces SVG coordinates, never averages flows.
export function thin(points, buckets = 80) {
  if (points.length <= buckets * 4) return points
  const out = []
  const size = Math.ceil(points.length / buckets)
  for (let i = 0; i < points.length; i += size) {
    const bucket = points.slice(i, i + size)
    const valid = bucket.filter((point) => point.value != null)
    const selected = new Set([bucket[0], bucket.at(-1)])
    if (valid.length) {
      selected.add(valid.reduce((a, b) => a.value < b.value ? a : b))
      selected.add(valid.reduce((a, b) => a.value > b.value ? a : b))
    }
    // Retain each boundary around missing spans, not just one null per bucket.
    bucket.forEach((point, j) => {
      if (point.value == null || bucket[j - 1]?.value == null || bucket[j + 1]?.value == null) selected.add(point)
    })
    out.push(...bucket.filter((point) => selected.has(point)))
  }
  return out
}
// Shared by SVG and hover. Bars fill whole daily bins; lines and steps sit on the day itself.
const PAD = 3
export const xAt = (i, n, kind, width = 640) => PAD + (kind === 'bar' ? (i + 0.5) / n : i / Math.max(1, n - 1)) * (width - 2 * PAD)
export const indexAt = (x, n, kind, width = 640) => kind === 'bar' ? Math.floor((x - PAD) / (width - 2 * PAD) * n) : Math.round((x - PAD) / (width - 2 * PAD) * (n - 1))
export const yAt = (value, min, max, height = 144) => 4 + (1 - (value - min) / (max - min)) * (height - 8)
const fixed = (value) => value.toFixed(2)
// Daily bars as filled step silhouettes: each day spans its bin and neighbours share edges, so dense
// histories read as one solid shape rather than hairline stripes. No smoothing. Miniatures group `size`
// days per column but keep each column's extremes; a column is a gap only when all its days are missing.
function bars(values, size, width, y) {
  const n = values.length, base = fixed(y(0))
  const edge = (j) => fixed(PAD + Math.min(n, j * size) / n * (width - 2 * PAD))
  const bins = []
  for (let i = 0; i < n; i += size) {
    const valid = values.slice(i, i + size).filter((value) => value != null)
    bins.push(valid.length ? [Math.min(0, ...valid), Math.max(0, ...valid)] : null)
  }
  const side = (s) => {
    if (!bins.some((bin) => bin?.[s])) return ''
    let path = '', open = false, level
    bins.forEach((bin, j) => {
      if (!bin?.[s]) { if (open) path += `H${edge(j)}V${base}Z`; open = false; return }
      const top = fixed(y(bin[s]))
      if (!open) path += `M${edge(j)},${base}V${top}`
      else if (top !== level) path += `H${edge(j)}V${top}`
      open = true; level = top
    })
    return open ? `${path}H${edge(bins.length)}V${base}Z` : path
  }
  // The zero line spans observed days only: zero shows as baseline, missing as nothing.
  let baseline = ''
  bins.forEach((bin, j) => { if (bin && !bins[j - 1]) baseline += `M${edge(j)},${base}`; if (bin && !bins[j + 1]) baseline += `H${edge(j + 1)}` })
  return { path: side(1) + side(0), baseline }
}
// `negative` (bars only) is a second series on the same days, drawn below zero. Its source values stay positive.
export function geometry(points, kind = 'line', width = 640, height = 144, miniature = false, negative) {
  const valid = points.filter((point) => number(point.value) != null)
  const below = (negative ?? []).map((point) => point.value == null ? null : -point.value)
  const drawn = [...valid.map((point) => Number(point.value)), ...below.filter((value) => value != null)]
  if (!drawn.length) return null
  const values = valid.length ? valid.map((point) => Number(point.value)) : drawn
  const low = Math.min(...values), high = Math.max(...values)
  const dl = Math.min(...drawn), dh = Math.max(...drawn)
  // Length encodings and flat zero values must have a real zero baseline.
  const min = kind === 'bar' || dl === dh || (dl >= 0 && dl < dh * 0.01) ? Math.min(0, dl) : dl
  const max = Math.max(kind === 'bar' ? Math.max(0, dh) : dh, min + (Math.abs(dh) * 0.01 || 1))
  const start = Date.parse(points[0].date), span = Math.max(1, Date.parse(points.at(-1).date) - start)
  const x = (point) => PAD + (Date.parse(point.date) - start) / span * (width - 2 * PAD)
  const y = (value) => yAt(value, min, max, height)
  const last = valid.at(-1), first = valid[0]
  const dot = last ? { x: x(last), y: y(last.value) } : { x: 0, y: 0 }
  if (kind === 'bar') {
    const size = miniature ? Math.max(1, Math.ceil(points.length / 80)) : 1
    const positive = bars(points.map((point) => number(point.value)), size, width, y)
    const lower = negative ? bars(below, size, width, y) : { path: '', baseline: '' }
    // One zero line across days where either series is observed.
    const either = negative ? points.map((point, i) => number(point.value) ?? below[i]) : null
    return { path: positive.path, negativePath: lower.path, baseline: either ? bars(either, size, width, y).baseline : positive.baseline, size, min, max, low, high, last, first, ...dot }
  }
  let path = '', previous = null
  for (const point of miniature ? thin(points, 24) : points) {
    if (point.value == null) { previous = null; continue }
    const px = fixed(x(point)), py = fixed(y(point.value))
    path += previous ? (kind === 'step' ? `H${px}V${py}` : `L${px},${py}`) : `M${px},${py}`
    previous = point
  }
  return { path, min, max, low, high, last, first, ...dot }
}
export const scaleNote = (g, key, kind) => `Vertical scale ${format(g.min, key)} to ${format(g.max, key)}${kind === 'bar' ? ', bars from zero' : g.min <= 0 && g.max >= 0 ? ', includes zero' : ', not from zero'}.`
function summary(points, key, label) {
  const valid = points.filter((point) => point.value != null)
  if (!valid.length) return `${label}: no observations.`
  const values = valid.map((point) => point.value)
  return `${label}. ${valid[0].date}: ${format(valid[0].value, key)}. Latest ${valid.at(-1).date}: ${format(valid.at(-1).value, key)}. Minimum ${format(Math.min(...values), key)}; maximum ${format(Math.max(...values), key)}.`
}
/** @typedef {{ date: string, value: number | null }} Point */
/** @typedef {{ mini?: boolean, focal?: boolean, label?: string, interactive?: boolean, negative?: { points: Point[], key: string, label: string } }} ChartOptions */
// SVG only, reused by range redraws. `negative` is aligned to `points`.
/** @param {Point[]} points @param {string} key @param {string} kind @param {ChartOptions} [options] */
export function draw(points, key, kind = 'line', { mini = false, focal = false, label = '', negative } = {}) {
  const width = mini ? 160 : 640, height = mini ? 28 : 144
  const g = geometry(points, kind, width, height, mini, negative?.points)
  if (!g) return null
  const description = [
    summary(points, key, label || key),
    negative && `${summary(negative.points, negative.key, negative.label)} Drawn below zero.`,
    scaleNote(g, key, kind),
    g.size > 1 ? `Each column spans ${g.size} days, extending to the greatest positive and negative daily amounts, not totals or averages. Only all-missing columns are gaps.` : 'Missing observations are gaps.',
  ].filter(Boolean).join(' ')
  const accent = focal ? ' accent' : ''
  const marks = kind === 'bar'
    ? `<path class="bars${accent}" d="${g.path}" fill="currentColor"/>${negative ? `<path class="bars negative" d="${g.negativePath}" fill="currentColor"/>` : ''}<path class="gridline" d="${g.baseline}" fill="none" stroke="currentColor" stroke-width="1" vector-effect="non-scaling-stroke"/>`
    : `<path class="series${accent}" d="${g.path}" fill="none" stroke="currentColor" stroke-width="${mini ? 1.3 : 1.8}" vector-effect="non-scaling-stroke"/><path class="dot${accent}" d="M${g.x},${g.y}h0" stroke="currentColor" stroke-width="${mini ? 3.4 : 6}" stroke-linecap="round" vector-effect="non-scaling-stroke"/>`
  return { g, svg: `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" role="img" aria-label="${escape(description)}"><title>${escape(description)}</title>${marks}</svg>` }
}
/** @param {Point[]} points @param {string} key @param {string} kind @param {ChartOptions} [options] */
export function chart(points, key, kind = 'line', { mini = false, focal = false, label = '', interactive = false, negative } = {}) {
  const drawn = draw(points, key, kind, { mini, focal, label, negative })
  if (!drawn) return '<p class="meta">No observations in this window.</p>'
  if (mini) return drawn.svg
  const { g, svg } = drawn
  const values = (series) => escape(JSON.stringify(series.map((point) => point.value)))
  const plot = interactive ? `<div class="chart-interactive" data-chart data-key="${escape(key)}" data-kind="${kind}" data-label="${escape(label || key)}" data-start="${escape(points[0].date)}" data-values="${values(points)}"${negative ? ` data-negative-key="${escape(negative.key)}" data-negative-label="${escape(negative.label)}" data-negative-values="${values(negative.points)}"` : ''} data-min="${g.min}" data-max="${g.max}" tabindex="0" role="group" aria-label="${escape(label || key)}${negative ? ` and ${escape(negative.label)}` : ''}. Use left and right arrow keys to inspect daily values; Home and End jump to the ends; Escape dismisses.">${svg}<span class="chart-cursor" hidden aria-hidden="true"></span><span class="chart-marker" hidden aria-hidden="true"></span>${negative ? '<span class="chart-marker" hidden aria-hidden="true"></span>' : ''}<output class="chart-tooltip" hidden aria-live="off"><span class="meta"></span><strong></strong>${negative ? '<strong></strong>' : ''}</output></div>` : svg
  return `${plot}<div class="chart-dates meta mono"><span>${escape(points[0].date)}</span><span>${escape(points.at(-1).date)}</span></div>`
}
