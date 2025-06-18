import * as Plot from "npm:@observablehq/plot";
import * as d3 from "npm:d3@7";
import { resize } from "npm:@observablehq/stdlib";

const NPL_SCALING = 2.66;
const URL_SCALING = 3.268;

function getMovements(data) {
  const movements = [];
  for (let i = 1; i < data.length; i++) {
    movements.push({
      ...data[i],
      movingRange: Math.abs(data[i].value - data[i - 1].value)
    });
  }
  return movements;
}

function calculateLimits(data, movements) {
  const avgX = d3.mean(data, d => d.value);
  const avgMovement = movements.length > 0 ? d3.mean(movements, d => d.movingRange) : 0;

  const delta = NPL_SCALING * avgMovement;
  const UNPL = avgX + delta;
  const LNPL = avgX - delta;
  const URL = URL_SCALING * avgMovement;

  return { avgX, avgMovement, UNPL, LNPL, URL };
}

export function xmrChart({
  metrics,
  title,
  subtitle,
  yField,
  yLabel,
  yTransform = d => d,
  dateField = "date",
  showMovingRange = true
}) {
  return resize((width) => {
    const data = metrics.map(d => ({
      date: d[dateField],
      value: yTransform(typeof yField === "function" ? yField(d) : d[yField])
    })).filter(d => d.value != null && !isNaN(d.value));
    
    const movements = getMovements(data);
    const { avgX, avgMovement, UNPL, LNPL, URL } = calculateLimits(data, movements);
    
    const xPlot = Plot.plot({
      title,
      subtitle,
      width,
      height: 300,
      y: {
        label: yLabel,
        grid: true
      },
      marks: [
        Plot.ruleY([avgX], {
          stroke: "green",
          strokeWidth: 2,
          strokeDasharray: "5 5"
        }),
        Plot.ruleY([UNPL], {
          stroke: "red",
          strokeWidth: 1,
          strokeDasharray: "3 3"
        }),
        Plot.ruleY([LNPL], {
          stroke: "red",
          strokeWidth: 1,
          strokeDasharray: "3 3"
        }),
        Plot.line(data, {
          x: "date",
          y: "value",
          stroke: "steelblue",
          strokeWidth: 1.5
        }),
        Plot.dot(data, {
          x: "date",
          y: "value",
          fill: d => (d.value > UNPL || d.value < LNPL) ? "red" : "steelblue",
          r: 3
        }),
        Plot.text([
          { y: avgX, label: `CL: ${avgX.toFixed(2)}` },
          { y: UNPL, label: `UCL: ${UNPL.toFixed(2)}` },
          { y: LNPL, label: `LCL: ${LNPL.toFixed(2)}` }
        ], {
          x: () => d3.max(data, d => d.date),
          y: d => d.y,
          text: d => d.label,
          textAnchor: "start",
          dx: 5,
          fontSize: 10,
          fill: "black"
        })
      ]
    });
    
    if (!showMovingRange) {
      return xPlot;
    }
    
    const mrPlot = Plot.plot({
      title: "Moving Range",
      width,
      height: 200,
      y: {
        label: "Moving Range",
        grid: true
      },
      marks: [
        Plot.ruleY([avgMovement], {
          stroke: "green",
          strokeWidth: 2,
          strokeDasharray: "5 5"
        }),
        Plot.ruleY([URL], {
          stroke: "red",
          strokeWidth: 1,
          strokeDasharray: "3 3"
        }),
        Plot.line(movements, {
          x: "date",
          y: "movingRange",
          stroke: "orange",
          strokeWidth: 1.5
        }),
        Plot.dot(movements, {
          x: "date",
          y: "movingRange",
          fill: d => d.movingRange > URL ? "red" : "orange",
          r: 3
        }),
        Plot.text([
          { y: avgMovement, label: `CL: ${avgMovement.toFixed(2)}` },
          { y: URL, label: `UCL: ${URL.toFixed(2)}` }
        ], {
          x: () => d3.max(movements, d => d.date),
          y: d => d.y,
          text: d => d.label,
          textAnchor: "start",
          dx: 5,
          fontSize: 10,
          fill: "black"
        })
      ]
    });
    
    const container = document.createElement("div");
    container.appendChild(xPlot);
    container.appendChild(mrPlot);
    return container;
  });
}