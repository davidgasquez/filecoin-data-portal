import type { APIRoute } from "astro"
import { archiveNote } from "../archive"

export const GET: APIRoute = ({ site }) => {
  const url = (path: string) => new URL(path, site).href
  return new Response(`# Filecoin Data Portal (archive)

> ${archiveNote}

## When to use

Use the current site (https://filecoindataportal.xyz/llms.txt) for up-to-date Filecoin datasets and metrics. Use this archive only to see how the previous site looked and what it reported at capture time.

## Agent resources

- [Agent instructions](${url("/SKILL.md")}): How to choose, inspect, and query datasets.
- [Dataset catalog](${url("/datasets")}): Available datasets, schemas, samples, downloads, and source code.
- [Dataset documentation](${url("/assets/daily_network_metrics.md")}): Markdown documentation is also available under \`/assets/<dataset>.md\` for every dataset listed in the agent instructions.
- [Documentation](${url("/docs")}): Data sources and usage examples.

## Project

- [About](${url("/about")}): Licensing, updates, and maintainers.
- [Source code](https://github.com/davidgasquez/filecoin-data-portal): Data pipelines, models, tests, and website.
- [Report an issue](https://github.com/davidgasquez/filecoin-data-portal/issues/new): Report incorrect, unclear, stale, or missing data.
`, { headers: { "Content-Type": "text/plain; charset=utf-8" } })
}
