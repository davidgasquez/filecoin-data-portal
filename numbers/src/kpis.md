<center>

<h1 style="font-weight: 500; font-size: 2.5em; letter-spacing: 0.1em; align-items: center; justify-content: center; gap: 0.5em"><span style="color: var(--theme-blue)">Filecoin</span> KPIs</h1>

</center>


```js
import { movingAverageLinePlot } from "./components/movingAverageLinePlot.js";
```

```js
const am = await FileAttachment("./data/daily_metrics.csv").csv({typed: true});
```

```js
const metrics = am.filter(d => {
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
  return d.date >= oneYearAgo;
});
```

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Sector Onboarding",
  subtitle: "How much raw power was onboarded to the network at a given time.",
  yField: "sector_onboarding_raw_power_pibs",
  yLabel: "PiBs",
  showArea: true,
  marks: [
    Plot.ruleY([5], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

</div>

<div class="card" id="total-value-fil">

```js
movingAverageLinePlot({
  metrics,
  title: "Total Value FIL",
  subtitle: "Total value of FIL in transactions per day on the network.",
  yField: "total_value_fil",
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true,
  yDomain: [0, 18],
  marks: [
    Plot.ruleY([16000000], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Clients with 1 TiB or more active data",
  subtitle: "Number of clients with 1 TiB or more active data on State Market Deals.",
  yField: "clients_with_active_data_gt_1_tibs",
  yLabel: "Number of Clients",
  showArea: true,
  marks: [
    Plot.ruleY([1000], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

</div>
