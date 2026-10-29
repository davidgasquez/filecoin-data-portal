import { draw, scaleNote } from './charts.mjs'
import { align, defaultRange, expand, ranges, within } from './metrics.mjs'

// Global 6m / 1y / all window for every Numbers time series, including closed related measures.
// The page ships the default window; wider ranges redraw from the static full history, loaded once.
type Point = { date: string; value: number | null }
type History = Record<string, { start: string; values: (number | null)[] }>
const control = document.querySelector<HTMLFieldSetElement>('[data-chart-range]')
const status = document.querySelector<HTMLElement>('[data-range-status]')!
const figures = [...document.querySelectorAll<HTMLElement>('figure[data-range]')]
const valid = (range: string | null) => range != null && Object.hasOwn(ranges, range) ? range : defaultRange
const fromUrl = () => valid(new URLSearchParams(location.search).get('range'))
let loading: Promise<History> | undefined
let requested = defaultRange, shown = defaultRange

function redraw(figure: HTMLElement, data: History, range: string) {
  const plot = figure.querySelector<HTMLElement>('[data-chart]')
  const column = data[figure.dataset.metric!], other = figure.dataset.negativeMetric
  if (!plot || !column) return
  let full = expand(column), negativeFull = other && data[other] ? expand(data[other]) : undefined
  if (negativeFull) [full, negativeFull] = align(full, negativeFull)
  const points = within(full, range), negativePoints = negativeFull && within(negativeFull, range)
  const { key = '', kind = 'line', label, negativeKey = '', negativeLabel = '' } = plot.dataset
  const result = draw(points, key, kind, { label, focal: !!plot.querySelector('svg .accent'), negative: negativePoints && { points: negativePoints, key: negativeKey, label: negativeLabel } })
  const svg = plot.querySelector('svg')
  if (!result || !svg) return
  svg.outerHTML = result.svg
  plot.querySelector('svg title')?.remove()
  Object.assign(plot.dataset, { start: points[0].date, values: JSON.stringify(points.map((point: Point) => point.value)), min: String(result.g.min), max: String(result.g.max) })
  if (negativePoints) plot.dataset.negativeValues = JSON.stringify(negativePoints.map((point: Point) => point.value))
  const dates = figure.querySelectorAll<HTMLElement>('.chart-dates span')
  dates[0].textContent = points[0].date
  dates[1].textContent = points.at(-1)!.date
  const scale = figure.querySelector<HTMLElement>('[data-chart-scale]')
  if (scale) scale.textContent = `Shown ${points[0].date} → ${points.at(-1)!.date}. ${scaleNote(result.g, key, kind)}`
  plot.dispatchEvent(new Event('chartredraw'))
}

const check = (range: string) => { control!.querySelector<HTMLInputElement>(`input[value="${range}"]`)!.checked = true }
function address(range: string, replace = false) {
  const url = new URL(location.href)
  if (range === defaultRange) url.searchParams.delete('range')
  else url.searchParams.set('range', range)
  if (url.href !== location.href) window.history[replace ? 'replaceState' : 'pushState'](null, '', url)
}

async function apply(range: string) {
  if (!control || range === requested) return
  requested = range
  check(range)
  control.setAttribute('aria-busy', 'true')
  status.hidden = false
  status.textContent = 'Loading chart history…'
  try {
    loading ??= fetch(`${import.meta.env.BASE_URL.replace(/\/$/, '')}/numbers-history.json`).then((response) => response.ok ? response.json() : Promise.reject(new Error(String(response.status))))
    const data = await loading
    if (requested !== range) return
    for (const figure of figures) redraw(figure, data, range)
    shown = range
    delete control.dataset.state
    status.hidden = true
    status.textContent = ''
  } catch {
    // Keep what is drawn, and the URL and control in step with it. A later choice retries.
    loading = undefined
    if (requested !== range) return
    requested = shown
    check(shown)
    address(shown, true)
    control.dataset.state = 'error'
    status.hidden = false
    status.textContent = 'Could not load history. Showing the previous range; choose a range to retry.'
  }
  control.removeAttribute('aria-busy')
}

if (control && figures.length) {
  control.hidden = false
  control.addEventListener('change', (event) => {
    const range = valid((event.target as HTMLInputElement).value)
    address(range)
    apply(range)
  })
  addEventListener('popstate', () => apply(fromUrl()))
  apply(fromUrl())
}
