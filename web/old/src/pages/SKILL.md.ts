import skill from "../SKILL.md?raw"
import { archiveNote } from "../archive"
import { datasets } from "../datasets"

const catalog = datasets.map((d) => `- [\`${d.id}\`](assets/${d.id}.md) — ${d.description || "No description."}`).join("\n")

// Archive note goes right after the frontmatter so agents see it first.
export const GET = () => new Response(skill.replace("{{ dataset_catalog }}", catalog).replace(/^(---\n[\s\S]*?\n---\n)/, `$1\n> ${archiveNote}\n`))
