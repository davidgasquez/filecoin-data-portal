---
toc: true
---

<center>

<h1 style="font-weight: 500; font-size: 3em; letter-spacing: 0.0em; align-items: center; justify-content: center; gap: 0.5em"><span style="color: var(--theme-blue)">Filecoin</span> in Numbers</h1>

Your **high level** view into the Filecoin Ecosystem!

</center>

```js
const params = new URLSearchParams(window.location.search);
const from_date = params.get('from_date') ?? '2024-01-01';
const to_date = params.get('to_date') ?? new Date().toISOString().split('T')[0];

// Add scroll correction for anchor links
const hash = window.location.hash;
if (hash) {
  const element = document.querySelector(hash);
  if (element) {
    setTimeout(() => element.scrollIntoView({ behavior: 'auto', block: 'start' }), 100);
  }
}
```

```js
// Update URL params when dates change
function updateURLParams(fromDate, toDate) {
  const params = new URLSearchParams(window.location.search);
  params.set('from_date', fromDate);
  params.set('to_date', toDate);
  window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
}
```

```js
const am = await FileAttachment("./data/daily_metrics.csv").csv({typed: true});
const drm_all = await FileAttachment("./data/daily_region_metrics.csv").csv({typed: true});
const dim_all = await FileAttachment("./data/daily_industry_metrics.csv").csv({typed: true});
const dt = await FileAttachment("./data/daily_transactions.csv").csv({typed: true});
```

```js
const fdt_all = dt.filter(d => new Date(d.date) > new Date('2021-12-31')).map(d => ({...d, transactions: d.transactions ?? 0}));
```

```js
import { movingAverageLinePlot } from "./components/movingAverageLinePlot.js";
```




```js
function getFilteredData(data, timeframe, startDate, endDate) {
  if (timeframe === "All") return data;
  if (timeframe === "Custom") return data.filter(d => d.date >= startDate && d.date <= endDate);

  const days = parseInt(timeframe.replace('d', ''));
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  return data.filter(d => d.date >= cutoffDate);
}

const metrics = getFilteredData(am, timeframe, startDate, endDate);
const drm = getFilteredData(drm_all, timeframe, startDate, endDate);
const dim = getFilteredData(dim_all, timeframe, startDate, endDate);
const fdt = getFilteredData(fdt_all, timeframe, startDate, endDate);

```

```js
const data_flow = ["onboarded_data_pibs", "ended_data_pibs"].flatMap((metric) => metrics.map(({date, [metric]: value}) => ({date, metric, value})));
```

## Data Onboarding

```js
function link(title, anchor) {
  return htl.html`<a href="#${anchor}">${title}</a>`
}

function title_anchor(title, anchor) {
  return htl.html`<h2>${link(title, anchor)}</h2>`
}
```

<div class="card" id="data-flow">

```js
Plot.plot({
  title: title_anchor("Data Flow", "data-flow"),
  subtitle: "How much data (PiBs) is being onboarded and offboarded on State Market Deals.",
  caption: "Displaying 30-day moving average for State Market Deals data.",
  x: {label: "Date"},
  y: {grid: true, label: "PiBs"},
  width,
  color: {
    range: ["var(--theme-red)", "var(--theme-green)"],
    legend: true,
    tickFormat: (d) => d === "onboarded_data_pibs" ? "Onboarded" : "Ended"
  },
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(data_flow, {
      x: "date",
      y: "value",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(data_flow, Plot.windowY(30, {
      x: "date",
      y: "value",
      stroke: "metric",
      strokeWidth: 2,
      tip: true
    })),
  ]
})
```

</div>

<div class="grid grid-cols-2">

<div class="card" id="data-on-active-deals">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Data On Active Deals", "data-on-active-deals"),
  subtitle: "How much data was active on State Market Deals on the network at a given time.",
  caption: "Only displaying data from State Market Deals.",
  yField: "data_on_active_deals_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card" id="data-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Data Delta", "data-delta"),
  subtitle: "Daily change in data on State Market Deals over time.",
  yField: "data_delta_pibs",
  yLabel: "PiBs",
})
```
</div>

<div class="card" id="data-onboarding-with-payments">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Data Onboarding with Payments", "data-onboarding-with-payments"),
  subtitle: "Daily data onboarded with payments via State Market Deals.",
  yField: "onboarded_data_tibs_with_payments",
  yLabel: "TiBs",
})
```
</div>

<div class="card" id="deal-storage-cost">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Deal Storage Cost", "deal-storage-cost"),
  subtitle: "Total daily spent FIL on paid deals.",
  yField: "deal_storage_cost_fil",
  yLabel: "FIL",
})
```
</div>

<div class="card" id="data-onboarding-by-region">

```js
resize((width) => Plot.plot({
  title: title_anchor("Data Onboarding by Region", "data-onboarding-by-region"),
  subtitle: "Daily data (TiBs) onboarded by region (from Client's Datacap application).",
  caption: "Only displaying onboarded data from known regions.",
  x: {label: "Date"},
  y: {grid: true, label: "TiBs"},
  color: {
    legend: true
  },
  width,
  height: 350,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(drm.filter(d => d.region != null), Plot.windowY(30, {
      x: "date",
      y: "onboarded_data_tibs",
      stroke: "region",
      strokeWidth: 2,
      tip: true
    })),
  ]
}))
```

</div>

<div class="card" id="data-onboarding-by-industry">

```js
resize((width) => Plot.plot({
  title: title_anchor("Data Onboarding by Industry", "data-onboarding-by-industry"),
  subtitle: "Daily data (TiBs) onboarded by industry (from Client's Datacap application).",
  caption: "Only displaying onboarded data from known industries.",
  x: {label: "Date"},
  y: {grid: true, label: "TiBs"},
  width,
  height: 350,
  color: {
    legend: true,
  },
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(dim.filter(d => d.industry != null), Plot.windowY(30, {
      x: "date",
      y: "onboarded_data_tibs",
      stroke: "industry",
      strokeWidth: 2,
      tip: true
    })),
  ]
}))
```

</div>

</div>

<div class="card" id="direct-data-onboarding">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Direct Data Onboarding", "direct-data-onboarding"),
  subtitle: "Onboarded data to the network via Direct Data Onboarding.",
  caption: "Displaying 30-day moving average.",
  yField: "ddo_sector_onboarding_raw_power_tibs",
  yLabel: "TiBs / day",
})
```
</div>

## Users

<div class="grid grid-cols-2">

<div class="card" id="dealmaking-clients">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Dealmaking Clients", "dealmaking-clients"),
  subtitle: "Clients making State Market Deals on the network.",
  yField: "unique_deal_making_clients",
  yLabel: "Clients",
})
```
</div>

<div class="card" id="dealmaking-providers">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Dealmaking Providers", "dealmaking-providers"),
  subtitle: "Providers making State Market Deals on the network.",
  yField: "unique_deal_making_providers",
  yLabel: "Providers",
})
```
</div>

<div class="card" id="clients-with-active-deals">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Clients With Active Deals", "clients-with-active-deals"),
  subtitle: "How many clients have active (State Market) deals on the network at a given time.",
  yField: "clients_with_active_deals",
  yLabel: "Clients",
  showArea: true,
})
```
</div>

<div class="card" id="providers-with-active-deals">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Providers With Active Deals", "providers-with-active-deals"),
  subtitle: "How many providers have active (State Market) deals on the network at a given time.",
  yField: "providers_with_active_deals",
  yLabel: "Providers",
  showArea: true,
})
```
</div>

<div class="card" id="providers-with-power">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Providers With Power", "providers-with-power"),
  subtitle: "How many providers had power on the network at a given time.",
  yField: "providers_with_power",
  yLabel: "Providers",
  showArea: true,
})
```
</div>

<div class="card" id="active-addresses">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Active Addresses", "active-addresses"),
  subtitle: "Addresses that appeared on chain at a given time.",
  caption: "Displaying 30-day moving average",
  yField: "active_address_count_daily",
  yLabel: "Active Addresses",
  yDomain: timeframe === "All" ? [0, 30000] : [0, 10000],
  // yType: "log",
})
```
</div>

<div class="card" id="total-addresses">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Total Addresses", "total-addresses"),
  subtitle: "How many addresses have interacted with the network.",
  yField: "total_address_count",
  yLabel: "Addresses (Millions)",
  showArea: true,
  yTransform: (d) => d / 1e6,
})
```
</div>

<div class="card" id="mean-active-deal-duration">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Mean Active Deal Duration", "mean-active-deal-duration"),
  subtitle: "How many days deals active on a date are expected to last.",
  caption: "Displaying 30-day moving average",
  yField: "mean_deal_duration_days",
  yLabel: "Days",
  showArea: true,
})
```
</div>

<div class="card" id="average-piece-replication-factor">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Average Piece Replication Factor", "average-piece-replication-factor"),
  subtitle: "Average piece replication of pieces onboarded on a date.",
  caption: "Displaying 30-day moving average",
  yField: "average_piece_replication_factor",
  yLabel: "Piece Replication Factor",
  yDomain: [0, 40],
  showArea: true,
})
```
</div>

</div>

## Power

<div class="grid grid-cols-2">

<div class="card" id="raw-power">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Raw Power", "raw-power"),
  subtitle: "Total raw power (PiBs) capacity on the network over time.",
  yField: "raw_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card" id="raw-power-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Raw Power Delta", "raw-power-delta"),
  subtitle: "Daily change in raw power on the network over time.",
  caption: "Displaying 30-day moving average",
  yField: "raw_power_delta_pibs",
  yLabel: "PiBs / day",
  yDomain: [-70, 70],
})
```
</div>

<div class="card" id="quality-adjusted-power">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Quality Adjusted Power", "quality-adjusted-power"),
  subtitle: "Total quality adjusted power (PiBs) capacity on the network over time.",
  yField: "quality_adjusted_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card" id="quality-adjusted-power-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Quality Adjusted Power Delta", "quality-adjusted-power-delta"),
  subtitle: "Daily change in quality adjusted power on the network over time.",
  caption: "Displaying 30-day moving average",
  yField: "quality_adjusted_power_delta_pibs",
  yLabel: "PiBs / day",
  yDomain: [-70, 70]
})
```
</div>

<div class="card" id="verified-data-power">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Verified Data Power", "verified-data-power"),
  subtitle: "Total verified data power (PiBs) capacity on the network over time.",
  yField: "verified_data_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```
</div>

<div class="card" id="network-utilization-ratio">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Network Utilization Ratio", "network-utilization-ratio"),
  subtitle: "How much of the network's power is being used.",
  yField: "network_utilization_ratio",
  yLabel: "Percentage (%)",
  showArea: true,
})
```
</div>
</div>

## Retrievals

<details>

<summary>About</summary>

These metrics track the success rate of retrievals via Spark over time.
You can see more fine grained charts on the [Official Spark Dashboards](https://dashboard.filspark.com/).

</details>

<div class="grid grid-cols-2">
<div class="card" id="spark-retrieval-success-rate">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Spark Retrieval Success Rate", "spark-retrieval-success-rate"),
  subtitle: "Average success rate of retrievals via Spark over time.",
  yField: "mean_spark_retrieval_success_rate",
  yLabel: "Percentage (%)",
  yTransform: (d) => d * 100,
})
```
</div>

<div class="card" id="providers-with-successful-retrieval">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Providers With Successful Retrievals", "providers-with-successful-retrieval"),
  subtitle: "How many providers have successfully retrieved data via Spark over time.",
  yField: "providers_with_successful_retrieval",
  yLabel: "Providers",
})
```

</div>
</div>

## Sectors

<div class="card" id="sector-metrics">

```js
const sectorMetricType = view(Inputs.radio(["Raw Power", "Quality-Adjusted Power"], {label: "Power Type", value: "Raw Power"}));
```

</div>

<div class="card" id="sector-data-by-event">

```js
const sector_metrics = sectorMetricType === "Raw Power"
  ? [
      {metric: "Snap", values: metrics.map(d => ({date: d.date, value: d.sector_snap_raw_power_pibs}))},
      {metric: "Expire", values: metrics.map(d => ({date: d.date, value: d.sector_expire_raw_power_pibs}))},
      {metric: "Recover", values: metrics.map(d => ({date: d.date, value: d.sector_recover_raw_power_pibs}))},
      {metric: "Fault", values: metrics.map(d => ({date: d.date, value: d.sector_fault_raw_power_pibs}))},
      {metric: "Extended", values: metrics.map(d => ({date: d.date, value: d.sector_extended_raw_power_pibs}))},
      {metric: "Terminated", values: metrics.map(d => ({date: d.date, value: d.sector_terminated_raw_power_pibs}))},
      {metric: "Onboarding", values: metrics.map(d => ({date: d.date, value: d.sector_onboarding_raw_power_pibs}))}
    ]
  : [
      {metric: "Snap", values: metrics.map(d => ({date: d.date, value: d.sector_snap_quality_adjusted_power_pibs}))},
      {metric: "Expire", values: metrics.map(d => ({date: d.date, value: d.sector_expire_quality_adjusted_power_pibs}))},
      {metric: "Recover", values: metrics.map(d => ({date: d.date, value: d.sector_recover_quality_adjusted_power_pibs}))},
      {metric: "Fault", values: metrics.map(d => ({date: d.date, value: d.sector_fault_quality_adjusted_power_pibs}))},
      {metric: "Extended", values: metrics.map(d => ({date: d.date, value: d.sector_extended_quality_adjusted_power_pibs}))},
      {metric: "Terminated", values: metrics.map(d => ({date: d.date, value: d.sector_terminated_quality_adjusted_power_pibs}))},
      {metric: "Onboarding", values: metrics.map(d => ({date: d.date, value: d.sector_onboarding_quality_adjusted_power_pibs}))}
    ];

const sector_metrics_data = sector_metrics.flatMap(({metric, values}) => values.map(v => ({...v, metric})));
```

```js
resize((width) => Plot.plot({
  title: title_anchor(`Sector Data by Event (${sectorMetricType})`, "sector-data-by-event"),
  subtitle: "How much data each event type has on the network on a given date.",
  caption: "Displaying 30-day moving average",
  x: {label: "Date"},
  y: {grid: true, label: "PiBs"},
  width,
  color: {
    legend: true,
  },
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(sector_metrics_data, Plot.windowY(30, {
      x: "date",
      y: "value",
      stroke: "metric",
      strokeWidth: 2,
      tip: true
    })),
  ]
}))
```
</div>

<div class="grid grid-cols-2">

<div class="card" id="sector-onboarding">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Onboarding", "sector-onboarding"),
  subtitle: `Daily ${sectorMetricType} PiBs onboarded into sector.`,
  yField: sectorMetricType === "Raw Power" ? "sector_onboarding_raw_power_pibs" : "sector_onboarding_quality_adjusted_power_pibs",
  yLabel: "PiBs",
})
```
</div>

<div class="card" id="sector-termination">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Termination", "sector-termination"),
  subtitle: `Daily ${sectorMetricType} PiBs terminated from sector.`,
  yField: sectorMetricType === "Raw Power" ? "sector_terminated_raw_power_pibs" : "sector_terminated_quality_adjusted_power_pibs",
  yLabel: "PiBs",
  yDomain: [0, 100]
})
```
</div>

</div>

### Sector Events

<div class="grid grid-cols-2">

<div class="card" id="commit-capacity-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Commit Capacity Events", "commit-capacity-events"),
  subtitle: "Number of commit capacity events per day",
  caption: "Displaying 30-day moving average",
  yField: "commit_capacity_added_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6
})
```
</div>

<div class="card" id="precommit-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Precommit Events", "precommit-events"),
  subtitle: "Number of precommit events per day",
  caption: "Displaying 30-day moving average",
  yField: "precommit_added_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6
})
```
</div>

<div class="card" id="sector-added-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Added Events", "sector-added-events"),
  subtitle: "Number of sector added events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_added_events_count",
  yLabel: "Events"
})
```
</div>

<div class="card" id="sector-extended-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Extended Events", "sector-extended-events"),
  subtitle: "Number of sector extended events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_extended_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card" id="sector-fault-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Fault Events", "sector-fault-events"),
  subtitle: "Number of sector fault events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_faulted_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card" id="sector-recovery-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Recovery Events", "sector-recovery-events"),
  subtitle: "Number of sector recovery events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_recovered_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card" id="sector-snap-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Snap Events", "sector-snap-events"),
  subtitle: "Number of sector snap events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_snapped_events_count",
  yLabel: "Events"
})
```
</div>

<div class="card" id="sector-terminated-events">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Sector Terminated Events", "sector-terminated-events"),
  subtitle: "Number of sector terminated events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_terminated_events_count",
  yLabel: "Events",
  yDomain: [0, 950000]
})
```
</div>

</div>

## Economics

<div class="grid grid-cols-2">

<div class="card" id="circulating-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Circulating FIL", "circulating-fil"),
  subtitle: "Amount of FIL circulating and tradeable in the economy.",
  yField: "circulating_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card" id="circulating-fil-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Circulating FIL Delta", "circulating-fil-delta"),
  subtitle: "Daily change in circulating FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "circulating_fil_delta",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 1]
})
```
</div>

<div class="card" id="mined-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Mined FIL", "mined-fil"),
  subtitle: "Amount of FIL that has been mined by storage miners.",
  yField: "mined_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card" id="mined-fil-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Mined FIL Delta", "mined-fil-delta"),
  subtitle: "Daily change in mined FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "mined_fil_delta",
  yLabel: "FIL"
})
```
</div>

<div class="card" id="mining-yield">

```js
movingAverageLinePlot({
  metrics: metrics.map(d => ({...d, mining_yield: d.locked_fil > 0 ? (d.mined_fil_delta / d.locked_fil) * 100 * 365 : 0})),
  title: title_anchor("Mining Yield", "mining-yield"),
  subtitle: "Pure yield through time. Daily mined FIL relative to locked FIL, annualized.",
  caption: "Shows the annualized percentage return on locked tokens. Displaying 30-day moving average.",
  yField: "mining_yield",
  yLabel: "Annual Yield (%)",
  showArea: true
})
```
</div>

<div class="card" id="vested-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Vested FIL", "vested-fil"),
  subtitle: "Amount of FIL that is vested from genesis allocation.",
  yField: "vested_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card" id="vested-fil-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Vested FIL Delta", "vested-fil-delta"),
  subtitle: "Daily change in vested FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "vested_fil_delta",
  yLabel: "FIL",
  yDomain: [0, 1000000]
})
```
</div>

<div class="card" id="locked-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Locked FIL", "locked-fil"),
  subtitle: "Amount of FIL locked as part of initial pledge, deal pledge, locked rewards, and other locking mechanisms.",
  yField: "locked_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card" id="locked-fil-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Locked FIL Delta", "locked-fil-delta"),
  subtitle: "Daily change in locked FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "locked_fil_delta",
  yLabel: "FIL",
  yDomain: [-400000, 500000]
})
```
</div>

<div class="card" id="locked-to-circulating-ratio">

```js
movingAverageLinePlot({
  metrics: metrics.map(d => ({...d, locked_to_circulating_ratio: (d.locked_fil / d.circulating_fil) * 100})),
  title: title_anchor("Locked to Circulating Ratio", "locked-to-circulating-ratio"),
  subtitle: "Percentage of circulating FIL that is locked.",
  caption: "The network targets approximately 30% of the network’s circulating supply locked up in initial consensus pledge when it is at or above the baseline.",
  yField: "locked_to_circulating_ratio",
  yLabel: "Percentage (%)",
  showArea: true,
  horizontalRule: 30
})
```
</div>

<div class="card" id="burnt-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Burnt FIL", "burnt-fil"),
  subtitle: "Amount of FIL burned as part of on-chain computations and penalties",
  yField: "burnt_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card" id="burnt-fil-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Burnt FIL Delta", "burnt-fil-delta"),
  subtitle: "Daily change in burnt FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "burnt_fil_delta",
  yLabel: "FIL",
  yType: "log"
})
```
</div>

<div class="card" id="reward-per-wincount">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Reward Per Wincount", "reward-per-wincount"),
  subtitle: "Weighted average block rewards awarded by the Filecoin Network per WinCount over time.",
  yField: "reward_per_wincount",
  yLabel: "FIL",
  showArea: true
})
```
</div>

<div class="card" id="reward-per-wincount-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Reward per Wincount FIL Delta", "reward-per-wincount-delta"),
  subtitle: "Daily change in reward per Wincount over time.",
  caption: "Displaying 30-day moving average",
  yField: "reward_per_wincount_delta",
  yLabel: "FIL"
})
```

</div>

<div class="card" id="yearly-inflation-rate">

```js
movingAverageLinePlot({
  metrics: metrics.filter(d => new Date(d.date) >= new Date('2021-10-01')),
  title: title_anchor("Yearly Inflation Rate", "yearly-inflation-rate"),
  subtitle: "Yearly change in circulating FIL over time.",
  caption: "Displaying 30-day moving average. The first year does not have any values as there is no data for the previous year.",
  yField: "yearly_inflation_rate",
  yLabel: "%"
})
```
</div>


<div class="card" id="total-value-fil">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Total Value FIL", "total-value-fil"),
  subtitle: "Total value of FIL in transactions per day on the network.",
  yField: "total_value_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 150]
})
```
</div>

<div class="card" id="fil-plus-share">

```js
const fil_plus_share = ["fil_plus_bytes_share", "fil_plus_rewards_share"].flatMap((metric) => metrics.map(({date, [metric]: value}) => ({date, metric, value})));
```

```js
resize((width) => Plot.plot({
  title: title_anchor("Filecoin Plus Share", "fil-plus-share"),
  subtitle: "How much share does Filecoin Plus get in the network.",
  caption: "Metrics derived from the ratio of quality-adjusted power to raw power.",
  x: {label: "Date"},
  y: {grid: true, label: "Share (%)"},
  width,
  color: {
    legend: true,
    tickFormat: (d) => d === "fil_plus_bytes_share" ? "Bytes" : "Rewards"
  },
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(fil_plus_share, {
      x: "date",
      y: "value",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(fil_plus_share, Plot.windowY(30, {
      x: "date",
      y: "value",
      stroke: "metric",
      strokeWidth: 2,
      tip: true
    })),
  ]
}))
```

</div>

<div class="card" id="fil-supply-dynamics">

```js
const fil_supply_dynamics = ["burned_locked_fil", "released_fil"].flatMap((metric) => 
  metrics.map(({date, burnt_fil, locked_fil, mined_fil, vested_fil}) => ({
    date, 
    metric, 
    value: metric === "burned_locked_fil" ? (burnt_fil + locked_fil) : (mined_fil + vested_fil)
  }))
);
```

```js
resize((width) => Plot.plot({
  title: title_anchor("FIL Supply Dynamics", "fil-supply-dynamics"),
  subtitle: "FIL burned and locked vs released to the economy over time.",
  caption: "Burned + Locked represents FIL removed from or temporarily unavailable for circulation. Released represents mined + vested FIL made available to the economy. Displaying 30-day moving average.",
  x: {label: "Date"},
  y: {grid: true, label: "FIL (Millions)"},
  width,
  color: {
    range: ["var(--theme-red)", "var(--theme-green)"],
    legend: true,
    tickFormat: (d) => d === "burned_locked_fil" ? "Burned + Locked" : "Released"
  },
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(fil_supply_dynamics, {
      x: "date",
      y: (d) => d.value / 1e6,
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(fil_supply_dynamics, Plot.windowY(30, {
      x: "date",
      y: (d) => d.value / 1e6,
      stroke: "metric",
      strokeWidth: 2,
      tip: true
    })),
  ]
}))
```

</div>

</div>

## Transactions

<div class="card" id="all-transactions">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("All Transactions", "all-transactions"),
  subtitle: "Number of transactions per day on the network.",
  yField: "transactions",
  yLabel: "Transactions (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 1.7]
})
```

</div>

<div class="card" id="transactions-by-method">

```js
const tx_method = view(Inputs.select([...new Set(fdt.map(d => d.method).sort())], {value: "storagemarket/4/PublishStorageDeals", label: "Method"}));
```

```js
Plot.plot({
  title: title_anchor(`Transactions by ${tx_method}`, "transactions-by-method"),
  subtitle: "Total transactions for this method over time",
  caption: "Displaying 30-day moving average since 2022",
  x: {label: "Date"},
  y: {grid: true, label: "Transactions"},
  width,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(getFilteredData(fdt, timeframe, startDate, endDate).filter(d => d.method === tx_method), {
      x: "date",
      y: "transactions",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(
      getFilteredData(fdt, timeframe, startDate, endDate).filter(d => d.method === tx_method),
      Plot.windowY(30, {
        x: "date",
        y: "transactions",
        stroke: "var(--theme-foreground-focus)",
        strokeWidth: 2,
        tip: true
      })
    )
  ]
})
```

</div>

## Gas

<div class="card" id="total-gas-used">

```js
movingAverageLinePlot({
metrics,
title: title_anchor("Total Gas Used", "total-gas-used"),
subtitle: "Total gas used per day on the network.",
caption: "Displaying 30-day moving average",
yField: "total_gas_used_millions",
yTransform: (d) => d / 1e6,
yLabel: "Gas Units (10^12)",
})
```
</div>


<div class="card" id="gas-used-by-method">

```js
const method = view(Inputs.select([...new Set(fdt.map(d => d.method).sort())], {value: "storagemarket/4/PublishStorageDeals", label: "Method"}));
```

```js
Plot.plot({
  title: title_anchor(`Gas Used by ${method}`, "gas-used-by-method"),
  subtitle: "Total gas used for this method over time",
  caption: "Displaying 30-day moving average since 2022",
  x: {label: "Date"},
  y: {grid: true, label: "Gas Units (Millions)", transform: (d) => d / 1e6},
  width,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(getFilteredData(fdt, timeframe, startDate, endDate).filter(d => d.method === method), {
      x: "date",
      y: "gas_used_millions",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(getFilteredData(fdt, timeframe, startDate, endDate).filter(d => d.method === method), Plot.windowY(30, {
      x: "date",
      y: "gas_used_millions",
      stroke: "var(--theme-foreground-focus)",
      tip: true
    }))
  ]
})
```

</div>

<div class="grid grid-cols-2">

<div class="card" id="unit-base-fee">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Unit Base Fee", "unit-base-fee"),
  subtitle: "The average set price per unit of gas to be burned.",
  yField: "unit_base_fee",
  yLabel: "nanoFIL",
  showArea: true
})
```
</div>

<div class="card" id="unit-base-fee-delta">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Unit Base Fee Delta", "unit-base-fee-delta"),
  subtitle: "Daily change in unit base fee over time.",
  caption: "Displaying 30-day moving average",
  yField: "unit_base_fee_delta",
  yDomain: [-0.2, 0.2],
  yLabel: "nanoFIL"
})
```
</div>

<div class="card" id="provecommit-sector-gas-used">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Provecommit Sector Gas Used", "provecommit-sector-gas-used"),
  subtitle: "Total gas used for provecommit sector operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "provecommit_sector_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card" id="precommit-sector-batch-gas-used">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Precommit Sector Batch Gas Used", "precommit-sector-batch-gas-used"),
  subtitle: "Total gas used for precommit sector batch operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "precommit_sector_batch_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card" id="publish-storage-deals-gas-used">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Publish Storage Deals Gas Used", "publish-storage-deals-gas-used"),
  subtitle: "Total gas used for publish storage deals operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "publish_storage_deals_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card" id="submit-windowed-post-gas-used">

```js
movingAverageLinePlot({
  metrics,
  title: title_anchor("Submit Windowed PoSt Gas Used", "submit-windowed-post-gas-used"),
  subtitle: "Total gas used for submit windowed PoSt operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "submit_windowed_post_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>
</div>

## Developer Activity

<details>
<summary>About</summary>
<p>
These metrics track developer activity related to the Filecoin project on GitHub, sourced via <a href="https://opensource.observer/">Open Source Observer (OSO)</a>. The data includes contributions, comments, stars, forks, releases, and commits across several Filecoin ecosystems repositories. Check them out under the <a href="https://github.com/opensource-observer/oss-directory/blob/main/data/collections/filecoin-foundation.yaml">'filecoin-foundation'</a> and <a href="https://github.com/opensource-observer/oss-directory/blob/main/data/collections/filecoin-core.yaml">'filecoin-core'</a> collections.
</p>
</details>


<div class="grid grid-cols-2">

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Contributors",
  subtitle: "Number of contributors per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_contributors",
  yLabel: "Contributors"
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Comments",
  subtitle: "Number of comments per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_comments",
  yLabel: "Comments"
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Stars",
  subtitle: "Number of stars per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_stars",
  yLabel: "Stars"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Forks",
  subtitle: "Number of forks per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_forks",
  yLabel: "Forks"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Releases",
  subtitle: "Number of releases per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_releases",
  yLabel: "Releases"
})
```
</div>

</div>

---

## Resources

Here are some resources for you to explore and learn more about Filecoin data.

<div class="grid grid-cols-2">
  <div class="card">
    Build your own data apps using <a href="https://github.com/davidgasquez/filecoin-data-portal/">Filecoin Data Portal</a> datasets.
  </div>
  <div class="card">
    Dig deeper into the Clients, Providers, and Allocators data using <a href="https://filecoinpulse.pages.dev/">Filecoin Pulse</a>.
  </div>
  <div class="card">
    Contributing to the Filecoin Data Portal is easy! <a href="https://github.com/davidgasquez/filecoin-data-portal/">Check out the GitHub repo</a>.
  </div>
  <div class="card">
    Explore these metrics in <a href="https://dune.com/kalen/filecoin-daily-metrics">Dune Analytics</a> and create your own dashboards and queries.
  </div>
</div>

#### Disclaimer


_Charts shown here are for informational purposes only. The data pipelines powering this are optimized for analytical purposes and might not be 100% accurate._

<div id="timeframe-selector">
<h3>Timeframe</h3>

```js
const timeframe = view(Inputs.radio(["All", "365d", "180d", "90d", "30d", "Custom"], {value: params.has('from_date') || params.has('to_date') ? "Custom" : "All"}));
```

```js
const startDate = timeframe === "Custom" ? view(Inputs.date({
  label: "Start",
  value: from_date,
})) : from_date;

const endDate = timeframe === "Custom" ? view(Inputs.date({
  label: "End",
  value: to_date,
})) : to_date;
```

```js
if (timeframe === "Custom") {
  updateURLParams(startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]);
} else if (timeframe === "365d") {
  const daysAgo = new Date();
  daysAgo.setDate(daysAgo.getDate() - 365);
  updateURLParams(daysAgo.toISOString().split('T')[0], new Date().toISOString().split('T')[0]);
} else if (timeframe === "180d") {
  const daysAgo = new Date();
  daysAgo.setDate(daysAgo.getDate() - 180);
  updateURLParams(daysAgo.toISOString().split('T')[0], new Date().toISOString().split('T')[0]);
} else if (timeframe === "90d") {
  const daysAgo = new Date();
  daysAgo.setDate(daysAgo.getDate() - 90);
  updateURLParams(daysAgo.toISOString().split('T')[0], new Date().toISOString().split('T')[0]);
} else if (timeframe === "30d") {
  const daysAgo = new Date();
  daysAgo.setDate(daysAgo.getDate() - 30);
  updateURLParams(daysAgo.toISOString().split('T')[0], new Date().toISOString().split('T')[0]);
} else if (timeframe === "All") {
  // Clear URL params
  window.history.replaceState({}, '', window.location.pathname);
}
```

</div>
