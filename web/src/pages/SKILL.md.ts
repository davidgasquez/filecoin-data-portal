import skill from "../SKILL.md?raw"
import { datasets } from "../datasets"

const catalog = datasets.map((d) => `- [\`${d.id}\`](assets/${d.id}.md) — ${d.description || "No description."}`).join("\n")

export const GET = () => new Response(skill.replace("{{ dataset_catalog }}", catalog))
