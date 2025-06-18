<center>

<h1 style="font-weight: 500; font-size: 2.5em; letter-spacing: 0.1em; align-items: center; justify-content: center; gap: 0.5em"><span style="color: var(--theme-blue)">Filecoin</span> KPIs</h1>

</center>


```js
import { xmrChart } from "./components/xmr.js";
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
xmrChart({
  metrics,
  title: "Daily Data Onboarding",
  subtitle: "How much raw power was onboarded to the network at a given time.",
  yField: "sector_onboarding_raw_power_pibs",
  yLabel: "PiBs",
  showMovingRange: false,
})
```

</div>

<div class="card">

```js
xmrChart({
  metrics,
  title: "Clients with 1 TiB or more active data",
  subtitle: "Number of clients with 1 TiB or more active data on State Market Deals.",
  yField: "clients_with_active_data_gt_1_tibs",
  yLabel: "Number of Clients",
  showMovingRange: false,
})
```

</div>

<div class="card">

```js
xmrChart({
  metrics,
  title: "Total FIL in Paid Deals",
  subtitle: "Total FIL in paid deals on the network.",
  yField: "deal_storage_cost_fil",
  yLabel: "FIL",
  showMovingRange: false,
})
```

</div>

<div class="card">

```js
xmrChart({
  metrics,
  title: "Total Value Flow",
  subtitle: "Total value flow on the network.",
  yField: (d) => d.total_value_fil + d.total_gas_used_millions,
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showMovingRange: false,
})
```

</div>
