import { LineChart } from "echarts/charts"
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components"
import * as echarts from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import type { ChartConfig, MetricFormat } from "../types/numbers"

echarts.use([LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

type DatasetValue = string | number | null
type ColumnarDataset = Record<string, DatasetValue[]>
type ChartPoint = [timestamp: number, value: number]
type ChartRange = "6m" | "1y" | "all"
type ChartMode = "compact" | "expanded" | "detail"
type ChartInstance = ReturnType<typeof echarts.init>

type DetailView = {
  canvas: HTMLElement
  value: HTMLElement
  title: string
  config: ChartConfig
  chart?: ChartInstance
}

type CardView = {
  node: HTMLElement
  canvas: HTMLElement
  value: HTMLElement
  trend: HTMLElement
  headline: HTMLElement
  titleLink: HTMLAnchorElement
  toggle: HTMLButtonElement
  id: string
  title: string
  config: ChartConfig
  chart?: ChartInstance
  details: DetailView[]
}

type TooltipParam = {
  axisValue?: unknown
  seriesName?: string
  value?: unknown
}

const datasetNode = document.querySelector<HTMLScriptElement>("[data-numbers-dataset]")
const cardNodes = Array.from(document.querySelectorAll<HTMLElement>("[data-stat-card]"))

if (!datasetNode?.textContent) {
  throw new Error("Numbers dataset is missing")
}

if (cardNodes.length === 0) {
  throw new Error("Numbers page has no metric cards")
}

const dataset = parseDataset(datasetNode.textContent)
const dates = parseDates(dataset.date)
const pointsByMetric = new Map<string, ChartPoint[]>()
const rootStyle = getComputedStyle(document.documentElement)
const bodyStyle = getComputedStyle(document.body)
const colors = {
  background: rootStyle.getPropertyValue("--color-bg").trim(),
  border: rootStyle.getPropertyValue("--color-border").trim(),
  strong: rootStyle.getPropertyValue("--color-border-strong").trim(),
  text: rootStyle.getPropertyValue("--color-text").trim(),
  muted: rootStyle.getPropertyValue("--color-text-muted").trim(),
}
const fontFamily = bodyStyle.fontFamily
const seriesColors = [colors.strong, colors.muted]
const tooltipDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
})
const axisDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  year: "2-digit",
  timeZone: "UTC",
})
const compactNumberFormatter = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
})
const scientificNumberFormatter = new Intl.NumberFormat("en-US", {
  notation: "scientific",
  maximumFractionDigits: 1,
})
const formatSet = new Set<MetricFormat>([
  "integer",
  "number",
  "pib",
  "fil",
  "mfil",
  "usd",
  "percent",
])

let currentRange = getInitialRange()
const linkedCardId = getLinkedCardId()
let expandedIds = new Set(linkedCardId ? [linkedCardId] : [])
const cards = cardNodes.map(createCard)

function parseDataset(source: string): ColumnarDataset {
  const parsed = JSON.parse(source) as unknown

  if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Numbers dataset must be a columnar object")
  }

  for (const [key, value] of Object.entries(parsed)) {
    if (!Array.isArray(value)) {
      throw new Error(`Numbers dataset column ${key} must be an array`)
    }
  }

  return parsed as ColumnarDataset
}

function parseDates(column: DatasetValue[] | undefined): number[] {
  if (!column) {
    throw new Error("Numbers dataset has no date column")
  }

  return column.map((value, index) => {
    const timestamp = typeof value === "number" ? value : Date.parse(String(value))

    if (!Number.isFinite(timestamp)) {
      throw new Error(`Numbers dataset has an invalid date at row ${index}`)
    }

    return timestamp
  })
}

function parseConfig(node: HTMLElement): ChartConfig {
  if (!node.dataset.chart) {
    throw new Error("Metric card is missing its chart configuration")
  }

  const parsed = JSON.parse(node.dataset.chart) as unknown

  if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Metric card chart configuration must be an object")
  }

  const config = parsed as Partial<ChartConfig>

  if (typeof config.y !== "string" || !config.y || !formatSet.has(config.format as MetricFormat)) {
    throw new Error("Metric card has an invalid chart configuration")
  }

  if (config.scale !== undefined && (!Number.isFinite(config.scale) || config.scale <= 0)) {
    throw new Error(`Metric ${config.y} must use a positive scale`)
  }

  if (
    config.series !== undefined &&
    (!Array.isArray(config.series) || config.series.some(
      (series) => typeof series?.label !== "string" || typeof series?.y !== "string",
    ))
  ) {
    throw new Error(`Metric ${config.y} series must contain labels and dataset columns`)
  }

  return config as ChartConfig
}

function requiredElement<T extends Element>(node: ParentNode, selector: string, label: string): T {
  const element = node.querySelector<T>(selector)

  if (!element) {
    throw new Error(`Metric card is missing ${label}`)
  }

  return element
}

function createCard(node: HTMLElement): CardView {
  const id = node.dataset.chartId
  const titleLink = requiredElement<HTMLAnchorElement>(node, "[data-chart-title]", "a title")
  const title = titleLink.textContent?.trim()

  if (!id || !title) {
    throw new Error("Metric card must have an id and title")
  }

  const canvas = requiredElement<HTMLElement>(node, ":scope > [data-chart-canvas]", "a chart")
  const details = Array.from(node.querySelectorAll<HTMLElement>("[data-detail-chart]")).map(
    (detailNode): DetailView => {
      const detailTitle = requiredElement<HTMLElement>(
        detailNode,
        ".stat-card__detail-header span",
        "a detail title",
      ).textContent?.trim()

      if (!detailTitle) {
        throw new Error(`Metric card ${id} has an empty detail title`)
      }

      return {
        canvas: requiredElement(detailNode, "[data-chart-canvas]", "a detail chart"),
        value: requiredElement(detailNode, "[data-detail-value]", "a detail value"),
        title: detailTitle,
        config: parseConfig(detailNode),
      }
    },
  )

  return {
    node,
    canvas,
    value: requiredElement(node, ":scope > [data-chart-value]", "a value"),
    trend: requiredElement(node, ":scope > [data-chart-trend]", "a trend"),
    headline: requiredElement(node, "[data-chart-headline]", "a headline"),
    titleLink,
    toggle: requiredElement(node, "[data-chart-toggle]", "an expand button"),
    id,
    title,
    config: parseConfig(node),
    details,
  }
}

function metricPoints(metric: string): ChartPoint[] {
  const cached = pointsByMetric.get(metric)
  if (cached) return cached

  const column = dataset[metric]
  if (!column) {
    throw new Error(`Numbers dataset has no ${metric} column`)
  }

  if (column.length !== dates.length) {
    throw new Error(`Numbers dataset column ${metric} must match the date column length`)
  }

  const points: ChartPoint[] = []
  for (let index = 0; index < column.length; index++) {
    const rawValue = column[index]
    if (rawValue === null) continue

    const value = typeof rawValue === "number" ? rawValue : Number(rawValue)
    if (!Number.isFinite(value)) {
      throw new Error(`Numbers dataset column ${metric} has an invalid value at row ${index}`)
    }

    points.push([dates[index], value])
  }

  points.sort((left, right) => left[0] - right[0])
  pointsByMetric.set(metric, points)
  return points
}

function rangePoints(points: ChartPoint[]): ChartPoint[] {
  if (currentRange === "all" || points.length === 0) return points

  const latest = new Date(points[points.length - 1][0])
  const months = currentRange === "6m" ? 6 : 12
  const cutoff = Date.UTC(
    latest.getUTCFullYear(),
    latest.getUTCMonth() - months,
    latest.getUTCDate(),
  )

  return points.filter(([timestamp]) => timestamp >= cutoff)
}

function formatDecimal(value: number, maximumFractionDigits: number): string {
  return value.toLocaleString("en-US", { maximumFractionDigits })
}

function formatTickNumber(value: number): string {
  const magnitude = Math.abs(value)

  if ((magnitude > 0 && magnitude < 0.01) || magnitude >= 1_000_000_000_000_000) {
    return scientificNumberFormatter.format(value)
  }

  return magnitude >= 1_000 ? compactNumberFormatter.format(value) : formatDecimal(value, 1)
}

function formatValue(
  value: number,
  config: ChartConfig,
  context: "headline" | "tick" | "tooltip",
): string {
  const scaledValue = value / (config.scale ?? 1)
  const fractionDigits = context === "tick" ? 1 : 2

  if (config.format === "integer") {
    const formatted = context === "tick"
      ? formatTickNumber(Math.round(scaledValue))
      : Math.round(scaledValue).toLocaleString("en-US")
    return `${formatted}${config.suffix ?? ""}`
  }

  if (config.format === "mfil") {
    const valueInMillions = scaledValue / 1_000_000
    const formatted = context === "tick"
      ? formatTickNumber(valueInMillions)
      : formatDecimal(valueInMillions, fractionDigits)
    return `${formatted}${context === "tick" ? "M" : " M FIL"}${config.suffix ?? ""}`
  }

  if (config.format === "usd") {
    if (context === "tick") {
      const sign = scaledValue < 0 ? "-" : ""
      return `${sign}$${formatTickNumber(Math.abs(scaledValue))}${config.suffix ?? ""}`
    }

    const formatted = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2,
    }).format(scaledValue)
    return `${formatted}${config.suffix ?? ""}`
  }

  if (config.format === "percent") {
    const percentage = scaledValue * 100
    const formatted = context === "tick"
      ? formatTickNumber(percentage)
      : formatDecimal(percentage, 2)
    return `${formatted}%${config.suffix ?? ""}`
  }

  const unit = { number: "", pib: " PiB", fil: " FIL" }[config.format]
  const formatted = context === "tick"
    ? formatTickNumber(scaledValue)
    : formatDecimal(scaledValue, fractionDigits)
  return `${formatted}${unit}${config.suffix ?? ""}`
}

function escapeHtml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]!,
  )
}

function tooltipValue(value: unknown): number {
  const rawValue = Array.isArray(value) ? value[1] : value
  const number = Number(rawValue)

  if (!Number.isFinite(number)) {
    throw new Error("Chart tooltip received an invalid value")
  }

  return number
}

function formatTooltip(rawParams: unknown, config: ChartConfig, showSeriesNames: boolean): string {
  const params = (Array.isArray(rawParams) ? rawParams : [rawParams]).filter(
    (value): value is TooltipParam => value !== null && typeof value === "object",
  )
  if (params.length === 0) return ""

  const firstValue = params[0].value
  const fallbackTimestamp = Array.isArray(firstValue) ? firstValue[0] : undefined
  const timestamp = Number(params[0].axisValue ?? fallbackTimestamp)
  const date = Number.isFinite(timestamp)
    ? tooltipDateFormatter.format(new Date(timestamp))
    : String(params[0].axisValue ?? "")
  const values = params.map((param) => {
    const value = formatValue(tooltipValue(param.value), config, "tooltip")
    return showSeriesNames ? `${escapeHtml(param.seriesName ?? "Value")} ${value}` : value
  })

  return [`<strong>${escapeHtml(date)}</strong>`, ...values].join("<br>")
}

function buildOption(title: string, config: ChartConfig, mode: ChartMode) {
  const expanded = mode === "expanded"
  const compact = mode === "compact"
  const seriesConfig = expanded && config.series?.length
    ? config.series
    : [{ label: title, y: config.y }]
  const series = seriesConfig.map(({ label, y }, index) => ({
    name: label,
    type: "line" as const,
    data: rangePoints(metricPoints(y)),
    showSymbol: false,
    symbol: "circle",
    symbolSize: 6,
    sampling: "lttb" as const,
    silent: compact,
    lineStyle: {
      color: seriesColors[index % seriesColors.length],
      type: index === 0 ? "solid" as const : "dashed" as const,
      width: 1.5,
    },
    itemStyle: { color: colors.background, borderColor: seriesColors[index % seriesColors.length] },
  }))

  return {
    animation: false,
    useUTC: true,
    textStyle: { color: colors.text, fontFamily },
    grid: expanded
      ? { left: 8, right: 8, top: series.length > 1 ? 32 : 8, bottom: 24, containLabel: true }
      : { left: 2, right: 2, top: 3, bottom: 3 },
    legend: {
      show: expanded && series.length > 1,
      top: 0,
      left: 8,
      itemWidth: 14,
      itemHeight: 2,
      textStyle: { color: colors.muted, fontFamily, fontSize: 10 },
    },
    tooltip: {
      show: !compact,
      trigger: "axis" as const,
      confine: true,
      backgroundColor: colors.background,
      borderColor: colors.strong,
      borderWidth: 1,
      padding: [3, 6],
      extraCssText: "border-radius:0;box-shadow:none;",
      textStyle: { color: colors.text, fontFamily, fontSize: 11 },
      axisPointer: { lineStyle: { color: colors.strong, type: "dashed" as const, width: 1 } },
      formatter: (params: unknown) => formatTooltip(params, config, series.length > 1),
    },
    xAxis: {
      type: "time" as const,
      show: expanded,
      boundaryGap: false,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: colors.muted,
        fontFamily,
        fontSize: 9,
        hideOverlap: true,
        formatter: (value: number) => axisDateFormatter.format(new Date(value)),
      },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value" as const,
      show: expanded,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: colors.muted,
        fontFamily,
        fontSize: 9,
        formatter: (value: number) => formatValue(value, config, "tick"),
      },
      splitLine: { lineStyle: { color: colors.border, type: "dashed" as const, width: 0.5 } },
    },
    series,
  }
}

function renderSummary(card: CardView): void {
  const points = rangePoints(metricPoints(card.config.y))
  if (points.length === 0) {
    card.value.textContent = "—"
    card.headline.textContent = "—"
    card.trend.textContent = ""
    return
  }

  const latest = points[points.length - 1][1]
  const previous = points[Math.max(0, points.length - 31)][1]
  const change = previous === 0 ? 0 : ((latest - previous) / previous) * 100
  const direction = change > 0 ? "▲" : change < 0 ? "▼" : "■"
  const sign = change > 0 ? "+" : ""
  const value = formatValue(latest, card.config, "headline")

  card.value.textContent = value
  card.headline.textContent = value
  card.trend.textContent = `${direction} ${sign}${formatDecimal(change, 2)}% 30d`
}

function renderDetail(detail: DetailView): void {
  const points = rangePoints(metricPoints(detail.config.y))
  detail.value.textContent = points.length
    ? formatValue(points[points.length - 1][1], detail.config, "headline")
    : "—"
  detail.chart ??= echarts.init(detail.canvas, null, { renderer: "canvas" })
  detail.chart.setOption(buildOption(detail.title, detail.config, "detail"), { notMerge: true })
}

function initializeChart(card: CardView): void {
  card.chart ??= echarts.init(card.canvas, null, { renderer: "canvas" })
}

function renderCard(card: CardView): void {
  const expanded = expandedIds.has(card.id)
  renderSummary(card)
  if (!card.chart) return

  card.chart.setOption(
    buildOption(card.title, card.config, expanded ? "expanded" : "compact"),
    { notMerge: true },
  )

  if (expanded) {
    for (const detail of card.details) renderDetail(detail)
  }
}

function renderAllCards(): void {
  for (const card of cards) renderCard(card)
}

function resizeCharts(): void {
  for (const card of cards) {
    card.chart?.resize()
    for (const detail of card.details) detail.chart?.resize()
  }
}

function syncExpandedState(): void {
  for (const card of cards) {
    const expanded = expandedIds.has(card.id)
    card.node.classList.toggle("is-expanded", expanded)
    card.toggle.setAttribute("aria-expanded", String(expanded))
    card.toggle.setAttribute("aria-label", `${expanded ? "Collapse" : "Expand"} ${card.title}`)
    card.toggle.title = `${expanded ? "Collapse" : "Expand"} ${card.title}`
    card.toggle.textContent = expanded ? "−" : "+"
  }

  const expandAll = document.querySelector<HTMLButtonElement>("[data-expand-all]")
  if (expandAll) {
    const allExpanded = expandedIds.size === cards.length
    expandAll.setAttribute("aria-pressed", String(allExpanded))
    expandAll.textContent = allExpanded ? "Collapse Charts" : "Expand Charts"
  }
}

function setExpanded(cardId: string, expanded: boolean): void {
  const card = cards.find(({ id }) => id === cardId)
  if (!card || expandedIds.has(cardId) === expanded) return

  if (expanded) expandedIds.add(cardId)
  else expandedIds.delete(cardId)

  syncExpandedState()
  if (expanded) initializeChart(card)
  renderCard(card)
  requestAnimationFrame(resizeCharts)
}

function setAllExpanded(expanded: boolean): void {
  expandedIds = expanded ? new Set(cards.map(({ id }) => id)) : new Set()
  syncExpandedState()
  if (expanded) {
    for (const card of cards) initializeChart(card)
  }
  renderAllCards()
  requestAnimationFrame(resizeCharts)
}

function parseRange(value: string | null): ChartRange | null {
  return value === "6m" || value === "1y" || value === "all" ? value : null
}

function getInitialRange(): ChartRange {
  return parseRange(new URL(window.location.href).searchParams.get("range")) ?? "1y"
}

function getLinkedCardId(): string | null {
  const id = window.location.hash.slice(1)
  return cardNodes.some((node) => node.dataset.chartId === id) ? id : null
}

function updateRangeState(): void {
  for (const button of document.querySelectorAll<HTMLButtonElement>("[data-chart-range]")) {
    button.setAttribute("aria-pressed", String(button.dataset.chartRange === currentRange))
  }

  const url = new URL(window.location.href)
  if (currentRange === "1y") url.searchParams.delete("range")
  else url.searchParams.set("range", currentRange)
  history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`)
}

function scrollToCard(cardId: string, behavior: ScrollBehavior = "smooth"): void {
  const card = cards.find(({ id }) => id === cardId)
  const toolbar = document.querySelector<HTMLElement>(".numbers-toolbar")
  if (!card) return

  const offset = (toolbar?.getBoundingClientRect().height ?? 0) + 16
  const top = window.scrollY + card.node.getBoundingClientRect().top - offset
  window.scrollTo({ top: Math.max(0, top), behavior })
}

for (const button of document.querySelectorAll<HTMLButtonElement>("[data-chart-range]")) {
  button.addEventListener("click", () => {
    const range = parseRange(button.dataset.chartRange ?? null)
    if (!range || range === currentRange) return

    currentRange = range
    updateRangeState()
    renderAllCards()
  })
}

document.querySelector<HTMLButtonElement>("[data-expand-all]")?.addEventListener("click", () => {
  setAllExpanded(expandedIds.size !== cards.length)
})

for (const card of cards) {
  card.titleLink.addEventListener("click", (event) => {
    event.stopPropagation()
    setExpanded(card.id, true)
  })

  card.toggle.addEventListener("click", (event) => {
    event.stopPropagation()
    setExpanded(card.id, !expandedIds.has(card.id))
  })

  card.node.addEventListener("click", (event) => {
    const target = event.target as Element
    if (
      target.closest("a, button, .stat-card__details") ||
      (expandedIds.has(card.id) && target.closest("[data-chart-canvas]"))
    ) return

    setExpanded(card.id, !expandedIds.has(card.id))
  })
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && expandedIds.size > 0) setAllExpanded(false)
})

window.addEventListener("hashchange", () => {
  const cardId = getLinkedCardId()
  if (!cardId) return
  setExpanded(cardId, true)
  scrollToCard(cardId)
})

window.addEventListener("resize", resizeCharts)

updateRangeState()
syncExpandedState()
renderAllCards()

const chartObserver = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue

    const card = cards.find(({ node }) => node === entry.target)
    if (!card) throw new Error("Observed metric card is missing")

    initializeChart(card)
    renderCard(card)
    chartObserver.unobserve(card.node)
  }
}, { rootMargin: "400px 0px" })

for (const card of cards) {
  if (expandedIds.has(card.id)) {
    initializeChart(card)
    renderCard(card)
  } else {
    chartObserver.observe(card.node)
  }
}

requestAnimationFrame(() => {
  resizeCharts()
  const cardId = getLinkedCardId()
  if (cardId) scrollToCard(cardId, "auto")
})
