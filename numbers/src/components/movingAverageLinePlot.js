import * as Plot from "npm:@observablehq/plot";
import { resize } from "npm:@observablehq/stdlib";


export function movingAverageLinePlot({
    metrics,           // Data array
    title,            // Plot title
    subtitle,         // Plot subtitle
    xField = "date",  // X-axis field name
    yField,           // Y-axis field name
    yLabel,           // Y-axis label
    yDomain,          // Optional y-axis domain
    yType,            // Optional y-axis type
    yTransform,       // Optional y-axis transform function
    showArea = false, // Optional boolean to show area instead of line
    caption = "Displaying 30-day moving average" // Optional caption
}) {

    return resize((width) => Plot.plot({
        title,
        subtitle,
        caption,
        width,
        x: { label: "Date" },
        y: {
            grid: true,
            label: yLabel,
            ...(yDomain && { domain: yDomain }),
            ...(yType && { type: yType }),
            ...(yTransform && { transform: yTransform })
        },
        marks: [
            // Plot.text(["⬣ Nexus Data Labs"], {
            //     fontSize: 14,
            //     frameAnchor: "top-right",
            //     dy: -14,
            //     opacity: 0.2
            // }),
            Plot.lineY(metrics, {
                x: xField,
                y: yField,
                tip: false,
                stroke: "var(--theme-foreground-fainter)",
                ...(yDomain && { clip: true })
            }),
            Plot.ruleY([0]),
            showArea && Plot.areaY(metrics, Plot.windowY(30, {
                x: xField,
                y: yField,
                tip: false,
                fill: "var(--theme-foreground-fainter)",
                ...(yDomain && { clip: true })
            })),
            Plot.lineY(metrics, Plot.windowY(30, {
                x: xField,
                y: yField,
                stroke: "var(--theme-foreground-focus)",
                tip: true,
                ...(yDomain && { clip: true })
            })),
        ].filter(Boolean)
    }));
}
