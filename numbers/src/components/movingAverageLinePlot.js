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
    caption = "Displaying 30-day moving average", // Optional caption
    horizontalRule = null, // Optional horizontal rule value (e.g., 0.3 for 30%)
    marks: customMarks, // Explicitly capture custom marks if provided
    ...otherPlotOptions // Capture the rest of the plot options
}) {

    // Default marks
    const defaultMarks = [
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
        horizontalRule !== null && Plot.ruleY([horizontalRule], {
            stroke: "var(--theme-red)",
            strokeDasharray: "4 4",
            strokeWidth: 1.5
        }),
    ].filter(Boolean);

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
        // Merge default marks with any provided marks
        marks: customMarks ? [...defaultMarks, ...customMarks] : defaultMarks,
        // Spread the rest of the plot options
        ...otherPlotOptions,
    }));
}
