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
// Goals used for rule lines and WBR snippets
// Note: keep these in sync with the visual thresholds in the charts below.
// If the WBR goals change, update only here.
const KPI_GOALS = {
  dataOnboardingPiBPerDay: 5,            // PiB/day
  clientsGt1TiB: 1000,                   // clients
  paidDealsFilPerDay: 100,               // FIL/day
  valueFlowFilPerDay: 100_000_000        // FIL/day (displayed as millions of FIL)
};

// Date helpers (ISO week: Monday-Sunday) anchored to latest available metric date
function startOfISOWeekUTC(d) {
  const dt = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const day = dt.getUTCDay(); // 0=Sun,1=Mon,...
  const diff = day === 0 ? -6 : 1 - day; // shift to Monday
  dt.setUTCDate(dt.getUTCDate() + diff);
  dt.setUTCHours(0, 0, 0, 0);
  return dt;
}

function addDaysUTC(d, days) {
  const r = new Date(d); r.setUTCDate(r.getUTCDate() + days); return r;
}

// Compute averages over date windows using a field accessor
function averageOver(metrics, fromInclusive, toExclusive, accessor) {
  const vals = metrics
    .filter((row) => row.date >= fromInclusive && row.date < toExclusive)
    .map(accessor)
    .filter((v) => Number.isFinite(v));
  if (!vals.length) return NaN;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

function latestDateIn(series) {
  let max = new Date(0);
  for (const d of series) if (d.date > max) max = d.date;
  return max;
}

function weeklyAverages(metrics, accessor) {
  const latest = latestDateIn(metrics);
  const thisWeekStart = startOfISOWeekUTC(latest);
  const nextWeekStart = addDaysUTC(thisWeekStart, 7);
  const lastWeekStart = addDaysUTC(thisWeekStart, -7);
  const thirteenWeeksStart = addDaysUTC(thisWeekStart, -13 * 7);

  const thisWeek = averageOver(metrics, thisWeekStart, nextWeekStart, accessor);
  const lastWeek = averageOver(metrics, lastWeekStart, thisWeekStart, accessor);
  const avg13w = averageOver(metrics, thirteenWeeksStart, thisWeekStart, accessor);
  return { thisWeek, lastWeek, avg13w, thisWeekStart };
}

// Formatting helpers
const fmt = (n, d=1) => Number.isFinite(n) ? n.toLocaleString(undefined, {maximumFractionDigits: d, minimumFractionDigits: d}) : "n/a";
const fmtInt = (n) => Number.isFinite(n) ? Math.round(n).toLocaleString() : "n/a";
const fmtMillions = (n, d=1) => Number.isFinite(n) ? (n/1e6).toLocaleString(undefined, {maximumFractionDigits: d, minimumFractionDigits: d}) : "n/a";
const fmtSigned = (n, d=1) => Number.isFinite(n) ? `${n >= 0 ? "+" : ""}${n.toLocaleString(undefined, {maximumFractionDigits: d, minimumFractionDigits: d})}` : "n/a";
const fmtSignedMillions = (n, d=1) => Number.isFinite(n) ? `${n >= 0 ? "+" : ""}${(n/1e6).toLocaleString(undefined, {maximumFractionDigits: d, minimumFractionDigits: d})}` : "n/a";

function kpiSnippet({
  accessor,
  goal,
  unit = "",            // e.g., "PiB", "FIL", "clients"
  showMillions = false,  // if true, display values and goal in millions
  decimals = 1,          // decimals for non-integer formatting
  integer = false        // integer formatting (e.g., clients)
}) {
  const { thisWeek, lastWeek, avg13w, thisWeekStart } = weeklyAverages(metrics, accessor);
  const wow = thisWeek - lastWeek;
  const gapThis = thisWeek - goal;
  const gap13 = avg13w - goal;

  const weekStr = thisWeekStart.toISOString().slice(0,10); // anchor for debugging/context if needed

  const v = (n) => integer ? fmtInt(n) : (showMillions ? fmtMillions(n, decimals) : fmt(n, decimals));
  const g = showMillions ? fmtMillions(goal, decimals) : (integer ? fmtInt(goal) : fmt(goal, decimals));
  const wowStr = integer ? fmtSigned(wow, 0) : (showMillions ? fmtSignedMillions(wow, decimals) : fmtSigned(wow, decimals));
  const gapThisStr = integer ? fmtSigned(gapThis, 0) : (showMillions ? fmtSignedMillions(gapThis, decimals) : fmtSigned(gapThis, decimals));
  const gap13Str = integer ? fmtSigned(gap13, 0) : (showMillions ? fmtSignedMillions(gap13, decimals) : fmtSigned(gap13, decimals));
  const unitStr = unit ? ` ${unit}` : "";

  const gapThisCls = gapThis >= 0 ? 'delta-pos' : 'delta-neg';
  const wowCls = wow >= 0 ? 'delta-pos' : 'delta-neg';
  const gap13Cls = gap13 >= 0 ? 'delta-pos' : 'delta-neg';

  // Single-line markup, no extra whitespace around parentheses
  return htl.html`<p class="kpi-snippet"><strong>${v(thisWeek)}${unitStr}</strong> this week vs <strong>${g}${unitStr}</strong> goal (<span class="${gapThisCls}"><strong>${gapThisStr}${unitStr}</strong></span> gap), last week <strong>${v(lastWeek)}${unitStr}</strong> (<span class="${wowCls}"><strong>${wowStr}${unitStr}</strong></span> WoW change), 13-wk average <strong>${v(avg13w)}${unitStr}</strong> vs <strong>${g}${unitStr}</strong> goal (<span class="${gap13Cls}"><strong>${gap13Str}${unitStr}</strong></span> gap).</p>`;
}
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
  title: "Daily Data Onboarding",
  subtitle: "How much raw power was onboarded to the network at a given time.",
  yField: "sector_onboarding_raw_power_pibs",
  yLabel: "PiBs",
  showArea: true,
  marks: [
    Plot.ruleY([KPI_GOALS.dataOnboardingPiBPerDay], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```
---

```js
kpiSnippet({
  accessor: (d) => d.sector_onboarding_raw_power_pibs,
  goal: KPI_GOALS.dataOnboardingPiBPerDay,
  unit: "PiB",
  decimals: 1
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
    Plot.ruleY([KPI_GOALS.clientsGt1TiB], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

---

```js
kpiSnippet({
  accessor: (d) => d.clients_with_active_data_gt_1_tibs,
  goal: KPI_GOALS.clientsGt1TiB,
  integer: true
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Total FIL in Paid Deals",
  subtitle: "Total FIL in paid deals on the network.",
  yField: "deal_storage_cost_fil",
  yLabel: "FIL",
  showArea: true,
  marks: [
    Plot.ruleY([KPI_GOALS.paidDealsFilPerDay], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

---

```js
kpiSnippet({
  accessor: (d) => d.deal_storage_cost_fil,
  goal: KPI_GOALS.paidDealsFilPerDay,
  unit: "FIL",
  decimals: 1
})
```

</div>

<div class="card">

```js
movingAverageLinePlot({
  metrics,
  title: "Total Value Flow",
  subtitle: "Total value flow on the network.",
  yField: (d) => d.total_value_fil + d.total_gas_used_millions,
  yLabel: "FIL (Millions)",
  yTransform: (d) => d / 1e6,
  showArea: true,
  marks: [
    Plot.ruleY([KPI_GOALS.valueFlowFilPerDay], {
      stroke: "var(--theme-blue)",
      strokeWidth: 2,
      strokeDasharray: "4 4"
    })
  ]
})
```

---

```js
kpiSnippet({
  accessor: (d) => d.total_value_fil + d.total_gas_used_millions,
  goal: KPI_GOALS.valueFlowFilPerDay,
  unit: "M FIL",
  showMillions: true,
  decimals: 1
})
```

</div>
