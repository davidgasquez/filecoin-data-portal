import {
  columnPoints,
  formatDate,
  formatMetricValue,
  parseDates,
  rangePoints,
  type ChartConfig,
  type ChartPoint,
  type ChartRange,
  type DatasetRow,
  type RangeValues,
} from "./numbers"
import { copyButtons } from "./clipboard"

type ChartRuntime = typeof import("echarts/core")
type ChartInstance = ReturnType<ChartRuntime["init"]>
type Chart = { canvas: HTMLElement; title: string; config: ChartConfig; expanded: boolean; value?: HTMLElement; instance?: ChartInstance }
type Metric = { node: HTMLElement; panel: HTMLElement; toggle: HTMLButtonElement; status: HTMLElement; charts: Chart[] }
type TooltipParam = { axisValue?: unknown; seriesName?: string; value?: unknown }

const root = document.querySelector<HTMLElement>("[data-numbers-dashboard]")!
const rootStyle = getComputedStyle(document.documentElement)
const color = (name: string) => rootStyle.getPropertyValue(name).trim()
const colors = { background: color("--color-surface"), border: color("--color-border"), strong: color("--color-border-strong"), text: color("--color-text"), muted: color("--color-text-muted") }
const fontFamily = getComputedStyle(document.body).fontFamily
const seriesColors = [colors.strong, colors.muted]
const axisDate = new Intl.DateTimeFormat("en-US", { month: "short", year: "2-digit", timeZone: "UTC" })

const parseRange = (value: unknown): ChartRange | null => value === "6m" || value === "1y" || value === "all" ? value : null
let range: ChartRange = parseRange(new URL(location.href).searchParams.get("range")) ?? "1y"
let dataset: DatasetRow[] | undefined
let dates: number[] = []
let loading: Promise<ChartRuntime> | undefined
let runtime: ChartRuntime | undefined
const pointsByColumn = new Map<string, ChartPoint[]>()

const metrics: Metric[] = Array.from(root.querySelectorAll<HTMLElement>("[data-stat-card]")).map((node) => ({
  node,
  panel: node.querySelector<HTMLElement>("[data-chart-panel]")!,
  toggle: node.querySelector<HTMLButtonElement>("[data-chart-toggle]")!,
  status: node.querySelector<HTMLElement>("[data-chart-status]")!,
  charts: [
    { canvas: node.querySelector<HTMLElement>(".stat-card__chart")!, title: node.querySelector<HTMLElement>("[data-chart-title]")!.textContent!.trim(), config: JSON.parse(node.dataset.chart!), expanded: true },
    ...Array.from(node.querySelectorAll<HTMLElement>("[data-detail-chart]")).map((detail) => ({
      canvas: detail.querySelector<HTMLElement>("[data-chart-canvas]")!,
      value: detail.querySelector<HTMLElement>("[data-detail-value]")!,
      title: detail.querySelector("h3")!.textContent!.trim(),
      config: JSON.parse(detail.dataset.chart!),
      expanded: false,
    })),
  ],
}))

// Data and ECharts load once, on the first opened metric.
function load(): Promise<ChartRuntime> {
  loading ??= Promise.all([
    fetch(root.dataset.chartDataUrl!, { headers: { Accept: "application/json" } }).then((response) => {
      if (!response.ok) throw new Error(`Numbers dataset request failed with ${response.status}`)
      return response.json()
    }),
    import("echarts/core"),
    // @ts-expect-error ECharts does not publish types for its tree-shakable side-effect modules.
    import("echarts/lib/chart/line"),
    // @ts-expect-error ECharts does not publish types for its tree-shakable side-effect modules.
    import("echarts/lib/chart/bar"),
    // @ts-expect-error ECharts does not publish types for its tree-shakable side-effect modules.
    import("echarts/lib/component/grid"),
    // @ts-expect-error ECharts does not publish types for its tree-shakable side-effect modules.
    import("echarts/lib/component/tooltip"),
    import("echarts/renderers"),
  ]).then(([rows, echarts, , , , , { CanvasRenderer }]) => {
    if (!Array.isArray(rows)) throw new Error("Numbers dataset must be an array")
    dataset = rows as DatasetRow[]
    dates = parseDates(dataset)
    echarts.use([CanvasRenderer])
    return runtime = echarts
  })
  loading.catch(() => { loading = undefined })
  return loading
}

function points(column: string): ChartPoint[] {
  let result = pointsByColumn.get(column)
  if (!result) pointsByColumn.set(column, result = columnPoints(dataset!, dates, column))
  return result
}

const escapeHtml = (value: string) => value.replace(/[&<>"']/g, (character) => `&#${character.charCodeAt(0)};`)

function tooltip(raw: unknown, config: ChartConfig, named: boolean): string {
  const params = (Array.isArray(raw) ? raw : [raw]).filter((value): value is TooltipParam => value !== null && typeof value === "object")
  if (params.length === 0) return ""
  const first = params[0].value
  const timestamp = Number(params[0].axisValue ?? (Array.isArray(first) ? first[0] : undefined))
  const values = params.map((param) => {
    const value = Array.isArray(param.value) ? param.value[1] : param.value
    const text = value == null ? "No observation" : formatMetricValue(Number(value), config)
    return named ? `${escapeHtml(param.seriesName ?? "Value")} ${text}` : text
  })
  return [`<strong>${escapeHtml(formatDate(timestamp))}</strong>`, ...values].join("<br>")
}

function option({ title, config, expanded }: Chart) {
  const seriesConfig = expanded && config.series?.length ? config.series : [{ label: title, y: config.y }]
  const labelled = expanded && seriesConfig.length > 1
  const series = seriesConfig.map(({ label, y }, index) => {
    const stroke = seriesColors[index % seriesColors.length]
    const data = rangePoints(points(y), range)
    // Isolated observations need a marker, otherwise gaps hide them.
    const isolated = data.some(([, value], i) => value != null && data[i - 1]?.[1] == null && data[i + 1]?.[1] == null)
    return config.kind === "bar"
      ? { name: label, type: "bar" as const, data, barMaxWidth: 6, itemStyle: { color: stroke } }
      : {
        name: label,
        type: "line" as const,
        data,
        step: config.kind === "step" ? "end" as const : undefined,
        connectNulls: false,
        showSymbol: isolated,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: stroke, type: (["solid", "dashed", "dotted"] as const)[index % 3], width: 1.5 },
        itemStyle: { color: colors.background, borderColor: stroke },
        endLabel: { show: labelled, formatter: "{a}", color: stroke, fontFamily, fontSize: 10, distance: 4, width: 126, overflow: "break" as const, lineHeight: 12 },
        labelLayout: { moveOverlap: "shiftY" as const },
      }
  })
  const axis = { axisLine: { show: false }, axisTick: { show: false } }
  return {
    animation: false,
    useUTC: true,
    textStyle: { color: colors.text, fontFamily },
    grid: expanded ? { left: 8, right: labelled ? 140 : 28, top: 8, bottom: 26, containLabel: true } : { left: 2, right: 2, top: 3, bottom: 3 },
    tooltip: {
      trigger: "axis" as const,
      confine: true,
      backgroundColor: colors.background,
      borderColor: colors.strong,
      borderWidth: 1,
      padding: [3, 6],
      extraCssText: "border-radius:0;box-shadow:none;",
      textStyle: { color: colors.text, fontFamily, fontSize: 11 },
      axisPointer: { lineStyle: { color: colors.strong, type: "dashed" as const, width: 1 } },
      formatter: (params: unknown) => tooltip(params, config, series.length > 1),
    },
    xAxis: {
      ...axis,
      type: "time" as const,
      show: expanded,
      axisLabel: { color: colors.muted, fontFamily, fontSize: 10, hideOverlap: true, formatter: (value: number) => axisDate.format(new Date(value)) },
      splitLine: { show: false },
    },
    yAxis: {
      ...axis,
      type: "value" as const,
      show: expanded,
      min: config.bounded ? 0 : undefined,
      max: config.bounded ? 1 : undefined,
      axisLabel: { color: colors.muted, fontFamily, fontSize: 10, formatter: (value: number) => formatMetricValue(value, config, true) },
      splitLine: { lineStyle: { color: colors.border, type: "dashed" as const, width: 0.5 } },
    },
    series,
  }
}

function render(metric: Metric): void {
  if (!isOpen(metric) || !runtime) return
  for (const chart of metric.charts) {
    if (chart.value) {
      const latest = rangePoints(points(chart.config.y), range).findLast(([, value]) => value != null)
      chart.value.textContent = latest ? `${formatMetricValue(latest[1]!, chart.config)} · ${formatDate(latest[0])}` : "—"
    }
    chart.instance ??= runtime.init(chart.canvas, null, { renderer: "canvas" })
    chart.instance.setOption(option(chart), { notMerge: true })
    chart.instance.resize()
  }
}

async function open(metric: Metric): Promise<void> {
  if (runtime) return render(metric)
  metric.node.setAttribute("aria-busy", "true")
  metric.status.textContent = "Loading historical data…"
  try {
    await load()
    metric.status.textContent = ""
    render(metric)
  } catch (error) {
    metric.status.textContent = "Historical chart unavailable. Close and reopen to retry."
    console.error(error)
  } finally {
    metric.node.removeAttribute("aria-busy")
  }
}

// 1Y is the default range, so it stays out of URLs.
function withRange(href: string): URL {
  const url = new URL(href)
  if (range === "1y") url.searchParams.delete("range")
  else url.searchParams.set("range", range)
  return url
}

function setRange(next: ChartRange): void {
  range = next
  for (const metric of metrics) {
    const path = metric.node.querySelector<SVGPathElement>("[data-chart-sparkline]")!
    path.setAttribute("d", (JSON.parse(path.dataset.rangePaths!) as RangeValues<string>)[range])
    const summary = metric.node.querySelector<HTMLElement>("[data-chart-summary]")!
    summary.textContent = `${summary.dataset.summaryBase} Daily trend: ${(JSON.parse(summary.dataset.rangeLabels!) as RangeValues<string>)[range]}.`
    render(metric)
  }
  history.replaceState(null, "", withRange(location.href))
}

const expandAll = document.querySelector<HTMLButtonElement>("[data-expand-all]")!
const rangeButtons = document.querySelectorAll<HTMLButtonElement>("[data-chart-range]")
const toolbar = document.querySelector<HTMLElement>(".numbers-toolbar")!
const isOpen = (metric: Metric) => metric.node.classList.contains("is-expanded")
const quarterSelect = document.querySelector<HTMLSelectElement>("[data-quarter-select]")
function showQuarter(value: string): void {
  for (const node of document.querySelectorAll<HTMLElement>("[data-quarter]")) node.hidden = node.dataset.quarter !== value
  if (quarterSelect) quarterSelect.value = value
}
quarterSelect?.addEventListener("change", () => showQuarter(quarterSelect.value))

function syncControls(): void {
  const allOpen = metrics.every(isOpen)
  expandAll.textContent = allOpen ? "Collapse All" : "Expand All"
  expandAll.setAttribute("aria-label", allOpen ? "Collapse all charts" : "Expand all charts")
  expandAll.setAttribute("aria-pressed", String(allOpen))
  for (const button of rangeButtons) button.setAttribute("aria-pressed", String(button.dataset.chartRange === range))
  for (const button of document.querySelectorAll<HTMLButtonElement>("[data-chart-copy-link]")) {
    button.dataset.copy = withRange(button.dataset.copy!).href
  }
}

function setExpanded(metric: Metric, expanded: boolean): void {
  metric.node.classList.toggle("is-expanded", expanded)
  metric.panel.hidden = !expanded
  metric.toggle.textContent = expanded ? "−" : "+"
  metric.toggle.setAttribute("aria-expanded", String(expanded))
  metric.toggle.setAttribute("aria-label", `${expanded ? "Collapse" : "Expand"} ${metric.charts[0].title}`)
  if (expanded) void open(metric)
}

function openTarget(): void {
  let id = ""
  try { id = decodeURIComponent(location.hash.slice(1)) } catch {}
  const node = document.getElementById(id)
  const metric = metrics.find((metric) => metric.node === node)
  if (metric) {
    setExpanded(metric, true)
    syncControls()
  } else if (node instanceof HTMLDetailsElement) node.open = true
  else if (node?.dataset.quarter) showQuarter(node.dataset.quarter)
  if (metric || node instanceof HTMLDetailsElement || node?.dataset.quarter) requestAnimationFrame(() => node!.scrollIntoView())
}

for (const metric of metrics) {
  metric.toggle.addEventListener("click", () => {
    const expanded = !isOpen(metric)
    setExpanded(metric, expanded)
    syncControls()
    if (expanded) {
      history.replaceState(null, "", `${location.pathname}${location.search}#${metric.node.id}`)
      requestAnimationFrame(() => metric.node.scrollIntoView())
    }
  })
}
expandAll.addEventListener("click", () => {
  const expanded = !metrics.every(isOpen)
  for (const metric of metrics) setExpanded(metric, expanded)
  syncControls()
})
for (const button of rangeButtons) {
  button.addEventListener("click", () => {
    setRange(parseRange(button.dataset.chartRange)!)
    syncControls()
  })
}
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return
  const focused = document.activeElement?.closest("[data-stat-card]")
  const metric = metrics.find((metric) => metric.node === focused && isOpen(metric)) ?? metrics.findLast(isOpen)
  if (!metric) return
  setExpanded(metric, false)
  syncControls()
})

new ResizeObserver(() => {
  document.documentElement.style.setProperty("--numbers-toolbar-height", `${toolbar.offsetHeight + 16}px`)
}).observe(toolbar)
window.addEventListener("resize", () => {
  for (const metric of metrics) if (isOpen(metric)) for (const chart of metric.charts) chart.instance?.resize()
})
window.addEventListener("hashchange", openTarget)

// The visible section drives the active pill; no parallel navigation state.
const sections = Array.from(document.querySelectorAll<HTMLElement>("[data-numbers-section]"))
const sectionLinks = Array.from(document.querySelectorAll<HTMLAnchorElement>("[data-section-link]"))
let active = ""
let scrollPending = false
function updateSection(): void {
  scrollPending = false
  const last = Math.ceil(scrollY + innerHeight) >= document.documentElement.scrollHeight - 2
  const section = last ? sections.at(-1) : sections.findLast((node) => node.getBoundingClientRect().top <= toolbar.getBoundingClientRect().bottom + 32) ?? sections[0]
  if (!section || active === section.id) return
  active = section.id
  for (const link of sectionLinks) {
    if (link.dataset.sectionLink === active) {
      link.setAttribute("aria-current", "location")
      const nav = link.parentElement!
      if (link.offsetLeft < nav.scrollLeft) nav.scrollLeft = link.offsetLeft
      else if (link.offsetLeft + link.offsetWidth > nav.scrollLeft + nav.clientWidth) nav.scrollLeft = link.offsetLeft + link.offsetWidth - nav.clientWidth
    } else link.removeAttribute("aria-current")
  }
}
window.addEventListener("scroll", () => {
  if (scrollPending) return
  scrollPending = true
  requestAnimationFrame(updateSection)
}, { passive: true })

if (range !== "1y") setRange(range)
syncControls()
copyButtons()
openTarget()
updateSection()
