export type MetricFormat = "integer" | "number" | "pib" | "fil" | "mfil" | "usd" | "percent"
export type ChartRange = "6m" | "1y" | "all"
export type RangeValues<T> = Record<ChartRange, T>
export type ChartPoint = [timestamp: number, value: number | null]
export type DatasetRow = Record<string, string | number | boolean | null>
export type ChartConfig = {
  y: string
  format: MetricFormat
  scale?: number
  suffix?: string
  kind?: "line" | "bar" | "step"
  bounded?: boolean
  series?: { label: string; y: string }[]
}
export type DetailConfig = ChartConfig & { title: string; description: string }
export type Period = keyof typeof periodLabels

export const periodLabels = {
  day: "per day",
  eod: "end of day",
  avg: "daily average",
  pooled: "pooled daily rate",
  snapshot: "daily snapshot",
  runRate: "annual run rate, end of day",
  annualized: "annualized",
  yoy: "year over year",
  trailing: "trailing 365 days",
}

export const ranges: ChartRange[] = ["6m", "1y", "all"]
export const DAY = 86_400_000

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 })
const compact = new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 })
const scientific = new Intl.NumberFormat("en-US", { notation: "scientific", maximumFractionDigits: 1 })
const dateFormatter = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" })
const units = { number: "", pib: " PiB", fil: " FIL" }

export function formatDecimal(value: number, maximumFractionDigits: number): string {
  return value.toLocaleString("en-US", { maximumFractionDigits })
}

export function formatDate(timestamp: number): string {
  return dateFormatter.format(new Date(timestamp))
}

function formatTick(value: number): string {
  const magnitude = Math.abs(value)
  if ((magnitude > 0 && magnitude < 0.01) || magnitude >= 1e15) return scientific.format(value)
  return magnitude >= 1_000 ? compact.format(value) : formatDecimal(value, 1)
}

export function formatMetricValue(value: number, config: ChartConfig, tick = false): string {
  const scaled = value / (config.scale ?? 1)
  const suffix = config.suffix ?? ""
  const number = (n: number) => tick ? formatTick(n) : formatDecimal(n, 2)

  if (config.format === "integer") {
    return `${tick ? formatTick(Math.round(scaled)) : Math.round(scaled).toLocaleString("en-US")}${suffix}`
  }
  if (config.format === "mfil") return `${number(scaled / 1_000_000)}${tick ? "M" : " M FIL"}${suffix}`
  if (config.format === "usd") {
    if (!tick) return `${currency.format(scaled)}${suffix}`
    return `${scaled < 0 ? "-" : ""}$${formatTick(Math.abs(scaled))}${suffix}`
  }
  if (config.format === "percent") return `${number(scaled * 100)}%${suffix}`
  return `${number(scaled)}${units[config.format]}${suffix}`
}

export function parseDates(rows: DatasetRow[]): number[] {
  return rows.map((row, index) => {
    const timestamp = Date.parse(String(row.date))
    if (!Number.isFinite(timestamp)) throw new Error(`Numbers dataset has an invalid date at row ${index}`)
    return timestamp
  })
}

// Values from the first to the last observation; NULLs in between stay as gaps.
export function columnPoints(rows: DatasetRow[], dates: number[], column: string): ChartPoint[] {
  if (!rows.some((row) => Object.hasOwn(row, column))) throw new Error(`Numbers dataset has no ${column} column`)

  const points: ChartPoint[] = rows.map((row, index) => {
    const raw = row[column]
    if (raw == null) return [dates[index], null]
    const value = Number(raw)
    if (!Number.isFinite(value)) throw new Error(`Numbers dataset column ${column} has an invalid value at row ${index}`)
    return [dates[index], value]
  })
  const first = points.findIndex(([, value]) => value != null)
  if (first < 0) return []
  const last = points.findLastIndex(([, value]) => value != null)
  return points.slice(first, last + 1)
}

export function rangePoints(points: ChartPoint[], range: ChartRange): ChartPoint[] {
  if (range === "all" || points.length === 0) return points
  const latest = new Date(points[points.length - 1][0])
  const cutoff = Date.UTC(latest.getUTCFullYear(), latest.getUTCMonth() - (range === "6m" ? 6 : 12), latest.getUTCDate())
  return points.filter(([timestamp]) => timestamp >= cutoff)
}

// Min/max per horizontal bucket, split at every missing observation.
export function sparklinePath(points: ChartPoint[], buckets = 60): string {
  const observed = points.filter((point): point is [number, number] => point[1] != null)
  if (observed.length === 0) return ""

  const values = observed.map(([, value]) => value)
  const minimum = Math.min(0, ...values)
  const span = Math.max(0, ...values) - minimum
  const y = (value: number) => (span === 0 ? 16 : 31 - ((value - minimum) / span) * 30).toFixed(2)
  if (observed.length === 1) return `M97 ${y(values[0])} L100 ${y(values[0])}`

  const start = points[0][0]
  const width = points[points.length - 1][0] - start || 1
  const grouped: { bucket: number; points: [number, number][]; move: boolean }[] = []
  let move = true
  for (const [timestamp, value] of points) {
    if (value == null) {
      move = true
      continue
    }
    const bucket = Math.min(buckets - 1, Math.floor(((timestamp - start) / width) * buckets))
    let group = grouped.at(-1)
    if (!group || move || group.bucket !== bucket) {
      group = { bucket, points: [], move }
      grouped.push(group)
    }
    group.points.push([timestamp, value])
    move = false
  }

  let path = ""
  const x = (timestamp: number) => (((timestamp - start) / width) * 100).toFixed(2)
  grouped.forEach((group, index) => {
    const low = group.points.reduce((a, b) => b[1] < a[1] ? b : a)
    const high = group.points.reduce((a, b) => b[1] > a[1] ? b : a)
    const selected = [group.points[0], low, high, group.points.at(-1)!]
      .sort((a, b) => a[0] - b[0])
      .filter((point, i, points) => i === 0 || point[0] !== points[i - 1][0])
    selected.forEach(([timestamp, value], i) => {
      path += `${i === 0 && group.move ? "M" : "L"}${x(timestamp)} ${y(value)} `
    })
    if (selected.length === 1 && group.move && (grouped[index + 1]?.move ?? true)) {
      const position = Number(x(selected[0][0]))
      path += `L${position === 100 ? 99.5 : Math.min(100, position + 0.5)} ${y(selected[0][1])} `
    }
  })
  return path.trim()
}

// Exact atto integer strings to display units, rounding half up.
export function formatAtto(value: string | number | boolean | null | undefined, unit: "usd" | "fil"): string {
  if (value == null || typeof value === "boolean") return "Unknown"
  const atto = BigInt(value)
  const digits = unit === "usd" ? 2 : 4
  const step = 10n ** BigInt(18 - digits)
  const sign = atto < 0n ? "-" : ""
  const rounded = ((atto < 0n ? -atto : atto) + step / 2n) / step
  const whole = (rounded / 10n ** BigInt(digits)).toLocaleString("en-US")
  const fraction = (rounded % 10n ** BigInt(digits)).toString().padStart(digits, "0")
  return unit === "usd" ? `${sign}$${whole}.${fraction}` : `${sign}${whole}.${fraction} FIL`
}
