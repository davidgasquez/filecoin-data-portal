export type MetricFormat =
  | "integer"
  | "number"
  | "pib"
  | "fil"
  | "mfil"
  | "usd"
  | "percent"

export type MetricSeries = {
  label: string
  y: string
}

export type ChartConfig = {
  y: string
  format: MetricFormat
  scale?: number
  suffix?: string
  series?: MetricSeries[]
}

export type NumbersMetric = ChartConfig & {
  id: string
  title: string
  description: string
  details?: (ChartConfig & { title: string; description: string })[]
}

export type NumbersSection = {
  id: string
  title: string
  columns: 2 | 3 | 4
  charts: NumbersMetric[]
}
