---
toc: true
---

<center>

<h1 style="font-weight: 500; font-size: 3em; letter-spacing: 0.0em; align-items: center; justify-content: center; gap: 0.5em"><span style="color: var(--theme-blue)">Filecoin</span> in Numbers</h1>

Your **high level** view into the Filecoin Ecosystem!

</center>

```js
const am = await FileAttachment("./data/daily_metrics.csv").csv({typed: true});
const drm = await FileAttachment("./data/daily_region_metrics.csv").csv({typed: true});
const dim = await FileAttachment("./data/daily_industry_metrics.csv").csv({typed: true});
const dt = await FileAttachment("./data/daily_transactions.csv").csv({typed: true});
```

```js
const fdt = dt.filter(d => new Date(d.date) > new Date('2021-12-31')).map(d => ({...d, transactions: d.transactions ?? 0}));
```

```js
import { movingAverageLinePlot } from "./components/movingAverageLinePlot.js";
```


<div class="card">
<h2>TIMEFRAME</h2>

```js
const timeframe = view(Inputs.radio(["All", "Last Year"], {value: "All"}));
```

</div>


```js
const metrics = timeframe === "All" ? am : am.slice(am.length - 365);
```

```js
const data_flow = ["onboarded_data_pibs", "ended_data_pibs"].flatMap((metric) => metrics.map(({date, [metric]: value}) => ({date, metric, value})));
```

## Data Onboarding

<div class="card">

```js
Plot.plot({
  title: "Data Flow",
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Data On Active Deals",
  subtitle: "How much data was active on State Market Deals on the network at a given time.",
  caption: "Only displaying data from State Market Deals.",
  yField: "data_on_active_deals_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Data Delta",
  subtitle: "Daily change in data on State Market Deals over time.",
  yField: "data_delta_pibs",
  yLabel: "PiBs",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Data Onboarding with Payments",
  subtitle: "Daily data onboarded with payments via State Market Deals.",
  yField: "onboarded_data_tibs_with_payments",
  yLabel: "TiBs",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Deal Storage Cost",
  subtitle: "Total daily spent FIL on paid deals.",
  yField: "deal_storage_cost_fil",
  yLabel: "FIL",
})
```
</div>

<div class="card">

```js
resize((width) => Plot.plot({
  title: "Data Onboarding by Region",
  subtitle: "Daily data (TiBs) onboarded by region (from Client's Datacap application).",
  caption: "Only displaying onboarded data from known regions.",
  x: {label: "Date"},
  y: {grid: true, label: "PiBs"},
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

<div class="card">

```js
resize((width) => Plot.plot({
  title: "Data Onboarding by Industry",
  subtitle: "Daily data (TiBs) onboarded by industry (from Client's Datacap application).",
  caption: "Only displaying onboarded data from known industries.",
  x: {label: "Date"},
  y: {grid: true, label: "PiBs"},
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Direct Data Onboarding",
  subtitle: "Onboarded data to the network via Direct Data Onboarding.",
  caption: "Displaying 30-day moving average.",
  yField: "ddo_sector_onboarding_raw_power_tibs",
  yLabel: "TiBs / day",
})
```
</div>

## Users

<div class="grid grid-cols-2">

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Dealmaking Clients",
  subtitle: "Clients making State Market Deals on the network.",
  yField: "unique_deal_making_clients",
  yLabel: "Clients",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Dealmaking Providers",
  subtitle: "Providers making State Market Deals on the network.",
  yField: "unique_deal_making_providers",
  yLabel: "Providers",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Clients With Active Deals",
  subtitle: "How many clients have active (State Market) deals on the network at a given time.",
  yField: "clients_with_active_deals",
  yLabel: "Clients",
  showArea: true,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Providers With Active Deals",
  subtitle: "How many providers have active (State Market) deals on the network at a given time.",
  yField: "providers_with_active_deals",
  yLabel: "Providers",
  showArea: true,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Providers With Power",
  subtitle: "How many providers had power on the network at a given time.",
  yField: "providers_with_power",
  yLabel: "Providers",
  showArea: true,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Active Addresses",
  subtitle: "Addresses that appeared on chain at a given time.",
  caption: "Displaying 30-day moving average",
  yField: "active_address_count_daily",
  yLabel: "Active Addresses",
  yDomain: timeframe === "All" ? [0, 30000] : [0, 10000],
  // yType: "log",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Total Addresses",
  subtitle: "How many addresses have interacted with the network.",
  yField: "total_address_count",
  yLabel: "Addresses (Millions)",
  showArea: true,
  yTransform: (d) => d / 1e6,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Mean Active Deal Duration",
  subtitle: "How many days deals active on a date are expected to last.",
  caption: "Displaying 30-day moving average",
  yField: "mean_deal_duration_days",
  yLabel: "Days",
  showArea: true,
})
```
</div>

</div>

## Power

<div class="grid grid-cols-2">

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Raw Power",
  subtitle: "Total raw power (PiBs) capacity on the network over time.",
  yField: "raw_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Raw Power Delta",
  subtitle: "Daily change in raw power on the network over time.",
  caption: "Displaying 30-day moving average",
  yField: "raw_power_delta_pibs",
  yLabel: "PiBs / day",
  yDomain: [-70, 70],
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Quality Adjusted Power",
  subtitle: "Total quality adjusted power (PiBs) capacity on the network over time.",
  yField: "quality_adjusted_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Quality Adjusted Power Delta",
  subtitle: "Daily change in quality adjusted power on the network over time.",
  caption: "Displaying 30-day moving average",
  yField: "quality_adjusted_power_delta_pibs",
  yLabel: "PiBs / day",
  yDomain: [-70, 70]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Verified Data Power",
  subtitle: "Total verified data power (PiBs) capacity on the network over time.",
  yField: "verified_data_power_pibs",
  yLabel: "PiBs",
  showArea: true,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Network Utilization Ratio",
  subtitle: "How much of the network's power is being used.",
  yField: "network_utilization_ratio",
  yLabel: "Percentage (%)",
  showArea: true,
})
```
</div>
</div>

## Retrievals

<div class="grid grid-cols-2">
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Spark Retrieval Success Rate",
  subtitle: "Average success rate of retrievals via Spark over time.",
  yField: "mean_spark_retrieval_success_rate",
  yLabel: "Percentage (%)",
  yTransform: (d) => d * 100,
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Providers With Successful Retrievals",
  subtitle: "How many providers have successfully retrieved data via Spark over time.",
  yField: "providers_with_successful_retrieval",
  yLabel: "Providers",
})
```

</div>
</div>

## Sectors

<div class="card">

```js
const sectorMetricType = view(Inputs.radio(["Raw Power", "Quality-Adjusted Power"], {label: "Power Type", value: "Raw Power"}));
```

</div>

<div class="card">

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
  title: `Sector Data by Event (${sectorMetricType})`,
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Onboarding",
  subtitle: `Daily ${sectorMetricType} PiBs onboarded into sector.`,
  yField: sectorMetricType === "Raw Power" ? "sector_onboarding_raw_power_pibs" : "sector_onboarding_quality_adjusted_power_pibs",
  yLabel: "PiBs",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Termination",
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Commit Capacity Events",
  subtitle: "Number of commit capacity events per day",
  caption: "Displaying 30-day moving average",
  yField: "commit_capacity_added_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Precommit Events",
  subtitle: "Number of precommit events per day",
  caption: "Displaying 30-day moving average",
  yField: "precommit_added_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Added Events",
  subtitle: "Number of sector added events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_added_events_count",
  yLabel: "Events"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Extended Events",
  subtitle: "Number of sector extended events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_extended_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Fault Events",
  subtitle: "Number of sector fault events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_faulted_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Recovery Events",
  subtitle: "Number of sector recovery events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_recovered_events_count",
  yLabel: "Events (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 4]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Snap Events",
  subtitle: "Number of sector snap events per day",
  caption: "Displaying 30-day moving average",
  yField: "sector_snapped_events_count",
  yLabel: "Events"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Terminated Events",
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Circulating FIL",
  subtitle: "Amount of FIL circulating and tradeable in the economy.",
  yField: "circulating_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Circulating FIL Delta",
  subtitle: "Daily change in circulating FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "circulating_fil_delta",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 1]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Mined FIL",
  subtitle: "Amount of FIL that has been mined by storage miners.",
  yField: "mined_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Mined FIL Delta",
  subtitle: "Daily change in mined FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "mined_fil_delta",
  yLabel: "FIL"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Vested FIL",
  subtitle: "Amount of FIL that is vested from genesis allocation.",
  yField: "vested_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Vested FIL Delta",
  subtitle: "Daily change in vested FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "vested_fil_delta",
  yLabel: "FIL",
  yDomain: [0, 1000000]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Locked FIL",
  subtitle: "Amount of FIL locked as part of initial pledge, deal pledge, locked rewards, and other locking mechanisms.",
  yField: "locked_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Locked FIL Delta",
  subtitle: "Daily change in locked FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "locked_fil_delta",
  yLabel: "FIL",
  yDomain: [-400000, 500000]
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Burnt FIL",
  subtitle: "Amount of FIL burned as part of on-chain computations and penalties",
  yField: "burnt_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Burnt FIL Delta",
  subtitle: "Daily change in burnt FIL over time.",
  caption: "Displaying 30-day moving average",
  yField: "burnt_fil_delta",
  yLabel: "FIL",
  yType: "log"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Reward Per Wincount",
  subtitle: "Weighted average block rewards awarded by the Filecoin Network per WinCount over time.",
  yField: "reward_per_wincount",
  yLabel: "FIL",
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Reward per Wincount FIL Delta",
  subtitle: "Daily change in reward per Wincount over time.",
  caption: "Displaying 30-day moving average",
  yField: "reward_per_wincount_delta",
  yLabel: "FIL"
})
```
</div>

</div>

<div class="card">

```js
const fil_plus_share = ["fil_plus_bytes_share", "fil_plus_rewards_share"].flatMap((metric) => metrics.map(({date, [metric]: value}) => ({date, metric, value})));
```

```js
Plot.plot({
  title: "Filecoin Plus Share",
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
})
```

</div>


## Transactions

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Transactions",
  subtitle: "Number of transactions per day on the network.",
  yField: "transactions",
  yLabel: "Transactions (Millions)",
  yTransform: (d) => d / 1e6,
  yDomain: [0, 1.7]
})
```

</div>

<div class="card">

```js
const tx_method = view(Inputs.select([...new Set(fdt.map(d => d.method).sort())], {value: "storagemarket/4/PublishStorageDeals", label: "Method"}));
```

```js
Plot.plot({
  title: `Transactions by ${tx_method}`,
  subtitle: "Total transactions for this method over time",
  caption: "Displaying 30-day moving average since 2022",
  x: {label: "Date"},
  y: {grid: true, label: "Transactions"},
  width,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(fdt.filter(d => d.method === tx_method && (timeframe === "All" || new Date(d.date) > new Date(Date.now() - 365 * 24 * 60 * 60 * 1000))), {
      x: "date",
      y: "transactions",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(
      fdt.filter(d => d.method === tx_method && (timeframe === "All" || new Date(d.date) > new Date(Date.now() - 365 * 24 * 60 * 60 * 1000))),
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

<div class="card">

```js
movingAverageLinePlot({
metrics,
title: "Total Gas Used",
subtitle: "Total gas used per day on the network.",
caption: "Displaying 30-day moving average",
yField: "total_gas_used_millions",
yTransform: (d) => d / 1e6,
yLabel: "Gas Units (10^12)",
})
```
</div>


<div class="card">

```js
const method = view(Inputs.select([...new Set(fdt.map(d => d.method).sort())], {value: "storagemarket/4/PublishStorageDeals", label: "Method"}));
```

```js
Plot.plot({
  title: `Gas Used by ${method}`,
  subtitle: "Total gas used for this method over time",
  caption: "Displaying 30-day moving average since 2022",
  x: {label: "Date"},
  y: {grid: true, label: "Gas Units (Millions)", transform: (d) => d / 1e6},
  width,
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(fdt.filter(d => d.method === method && (timeframe === "All" || new Date(d.date) > new Date(Date.now() - 365 * 24 * 60 * 60 * 1000))), {
      x: "date",
      y: "gas_used_millions",
      stroke: "var(--theme-foreground-fainter)",
    }),
    Plot.lineY(fdt.filter(d => d.method === method && (timeframe === "All" || new Date(d.date) > new Date(Date.now() - 365 * 24 * 60 * 60 * 1000))), Plot.windowY(30, {
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

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Unit Base Fee",
  subtitle: "The average set price per unit of gas to be burned.",
  yField: "unit_base_fee",
  yLabel: "nanoFIL",
  showArea: true
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Unit Base Fee Delta",
  subtitle: "Daily change in unit base fee over time.",
  caption: "Displaying 30-day moving average",
  yField: "unit_base_fee_delta",
  yDomain: [-0.2, 0.2],
  yLabel: "nanoFIL"
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Provecommit Sector Gas Used",
  subtitle: "Total gas used for provecommit sector operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "provecommit_sector_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Precommit Sector Gas Used",
  subtitle: "Total gas used for precommit sector operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "precommit_sector_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Provecommit Aggregate Gas Used",
  subtitle: "Total gas used for provecommit aggregate operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "provecommit_aggregate_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Precommit Sector Batch Gas Used",
  subtitle: "Total gas used for precommit sector batch operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "precommit_sector_batch_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Publish Storage Deals Gas Used",
  subtitle: "Total gas used for publish storage deals operations per day on the network.",
  caption: "Displaying 30-day moving average",
  yField: "publish_storage_deals_gas_used_millions",
  yTransform: (d) => d / 1e6,
  yLabel: "Gas Units (10^12)",
})
```
</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Submit Windowed PoSt Gas Used",
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

<div class="grid grid-cols-2">
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Commits",
  subtitle: "Number of commits per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_commit_code_events",
  yLabel: "Events"
})
```

</div>
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Issues Closed",
  subtitle: "Number of issues closed per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_issue_closed_events",
  yLabel: "Events"
})
```

</div>
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Issue Comments",
  subtitle: "Number of issue comments per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_issue_comment_events",
  yLabel: "Events"
})
```

</div>
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Issues Opened",
  subtitle: "Number of issues opened per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_issue_opened_events",
  yLabel: "Events"
})
```

</div>
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Pull Requests Closed",
  subtitle: "Number of pull requests closed per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_pull_request_closed_events",
  yLabel: "Events"
})
```

</div>
<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Pull Requests Merged",
  subtitle: "Number of pull requests merged per day on the core Filecoin repositories.",
  caption: "Displaying 30-day moving average",
  yField: "github_pull_request_merged_events",
  yLabel: "Events"
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
