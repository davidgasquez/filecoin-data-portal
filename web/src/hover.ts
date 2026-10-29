import { format, shiftDate } from './metrics.mjs'
import { indexAt, xAt, yAt } from './charts.mjs'

let dismissActive: (() => void) | undefined
for (const plot of document.querySelectorAll<HTMLElement>('[data-chart]')) {
  // Decode lazily: closed related measures need no work until inspected. Range redraws replace the payload.
  const cache: Record<string, { raw?: string; values: (number | null)[] }> = { values: { values: [] }, negativeValues: { values: [] } }
  const decode = (name: 'values' | 'negativeValues') => {
    const raw = plot.dataset[name], entry = cache[name]
    if (raw !== entry.raw) { entry.raw = raw; entry.values = raw ? JSON.parse(raw) as (number | null)[] : [] }
    return entry.values
  }
  let index = -1
  const tooltip = plot.querySelector<HTMLOutputElement>('.chart-tooltip')!
  const cursor = plot.querySelector<HTMLElement>('.chart-cursor')!
  const markers = [...plot.querySelectorAll<HTMLElement>('.chart-marker')]
  const date = tooltip.querySelector<HTMLElement>('span')!
  const lines = [...tooltip.querySelectorAll<HTMLElement>('strong')]
  const data = () => decode('values')
  plot.querySelector('title')?.remove()
  const hide = () => { tooltip.hidden = cursor.hidden = true; markers.forEach((marker) => { marker.hidden = true }) }
  function show(next: number, keyboard = false) {
    dismissActive?.(); dismissActive = hide
    const n = data().length, kind = plot.dataset.kind ?? 'line'
    index = Math.max(0, Math.min(n - 1, next))
    const x = xAt(index, n, kind) / 640 * 100
    const y = (v: number) => yAt(v, Number(plot.dataset.min), Number(plot.dataset.max)) / 144 * 100
    // Below-zero series are drawn negated; their readout keeps the source (positive) value.
    const series = [{ v: data()[index], key: plot.dataset.key, label: plot.dataset.label, sign: 1 }]
    if (lines[1]) series.push({ v: decode('negativeValues')[index], key: plot.dataset.negativeKey, label: plot.dataset.negativeLabel, sign: -1 })
    tooltip.setAttribute('aria-live', keyboard ? 'polite' : 'off')
    date.textContent = `${shiftDate(plot.dataset.start!, index)} · UTC`
    tooltip.style.left = x > 50 ? '0' : 'auto'
    tooltip.style.right = x > 50 ? 'auto' : '0'
    cursor.style.left = `${x}%`
    series.forEach(({ v, key, label, sign }, i) => {
      lines[i].textContent = series.length > 1 ? `${label}: ${format(v, key)}` : format(v, key)
      markers[i].style.left = `${x}%`
      markers[i].style.top = `${y(sign * (v ?? 0))}%`
      markers[i].hidden = v == null
    })
    tooltip.hidden = cursor.hidden = false
  }
  function point(event: PointerEvent) {
    const bounds = plot.getBoundingClientRect()
    show(indexAt((event.clientX - bounds.left) / bounds.width * 640, data().length, plot.dataset.kind ?? 'line'))
  }
  plot.addEventListener('pointermove', point)
  plot.addEventListener('pointerdown', point)
  plot.addEventListener('pointerleave', (event) => { if (event.pointerType !== 'touch' && document.activeElement !== plot) hide() })
  plot.addEventListener('focus', () => { if (tooltip.hidden) show(data().length - 1, true) })
  plot.addEventListener('blur', hide)
  // A new window changes every index: dismiss, and resume keyboard inspection from the latest day.
  plot.addEventListener('chartredraw', () => { hide(); index = data().length })
  plot.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { hide(); return }
    const moves: Record<string, number> = { ArrowLeft: index - 1, ArrowRight: index + 1, Home: 0, End: data().length - 1 }
    const next = moves[event.key]
    if (next == null) return
    event.preventDefault(); show(next, true)
  })
}
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') document.querySelectorAll<HTMLDetailsElement>('.metric-info[open]').forEach((info) => {
    if (info.contains(document.activeElement)) info.querySelector('summary')?.focus()
    info.open = false
  })
})
document.addEventListener('click', (event) => {
  document.querySelectorAll<HTMLDetailsElement>('.metric-info[open]').forEach((info) => {
    if (!info.contains(event.target as Node)) info.open = false
  })
})
