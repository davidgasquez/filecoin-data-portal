import { access, copyFile, mkdir, readdir, readFile, rm, unlink, writeFile } from "node:fs/promises"
import { constants } from "node:fs"
import path from "node:path"

type ParsedAssetDoc = {
  title: string
  description: string
  codeUrl: string | null
  body: string
}

const webRoot = process.cwd()
const rawDocsDir = path.resolve(webRoot, ".generated/fdp-docs/raw")
const publicSkillPath = path.resolve(webRoot, "public/SKILL.md")
const publicAssetsDir = path.resolve(webRoot, "public/assets")
const contentDir = path.resolve(webRoot, "src/content/dataset-docs")

async function pathExists(targetPath: string): Promise<boolean> {
  try {
    await access(targetPath, constants.F_OK)
    return true
  } catch {
    return false
  }
}

async function listMarkdownFiles(targetDir: string): Promise<string[]> {
  if (!(await pathExists(targetDir))) {
    return []
  }

  const entries = await readdir(targetDir, { withFileTypes: true })
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort()
}

async function hasGeneratedDocs(targetDir: string): Promise<boolean> {
  const skillExists = await pathExists(path.join(targetDir, "SKILL.md"))
  if (!skillExists) {
    return false
  }

  const assetFiles = await listMarkdownFiles(path.join(targetDir, "assets"))
  return assetFiles.length > 0
}

async function requireRawDocs(): Promise<string> {
  if (await hasGeneratedDocs(rawDocsDir)) {
    return rawDocsDir
  }

  throw new Error(
    `FDP docs not found in ${rawDocsDir}. Run "uv run fdp docs --out web/.generated/fdp-docs/raw" first.`,
  )
}

async function clearManagedMarkdownFiles(targetDir: string): Promise<void> {
  await mkdir(targetDir, { recursive: true })

  for (const fileName of await listMarkdownFiles(targetDir)) {
    await unlink(path.join(targetDir, fileName))
  }
}

function parseAssetDoc(fileName: string, markdown: string): ParsedAssetDoc {
  const normalized = markdown.replaceAll("\r\n", "\n").trim()
  const lines = normalized.split("\n")
  const title = path.basename(fileName, ".md")
  let bodyLines = lines

  if (lines[0]?.startsWith("# ")) {
    bodyLines = lines.slice(1)
  }

  const body = bodyLines.join("\n").trimStart()
  const description = body.split("\n\n", 1)[0]?.trim() ?? ""

  // Extract asset code URL from the metadata list
  const codeMatch = body.match(/- asset code: `([^`]+)`/)
  const codeUrl = codeMatch?.[1] ?? null

  // Strip: description paragraph, metadata list (asset code/dataset url/rows), Depends, Tests
  const cleanedBody = body
    .replace(/^[^\n#]+\n\n/, "") // leading description paragraph
    .replace(/^(?:- (?:asset code|dataset url|rows):.*\n)+\n?/m, "") // metadata list items
    .replace(/## Depends\n\n(?:- .*\n)*\n?/m, "") // Depends section
    .replace(/## Tests\n\n(?:- .*\n)*\n?/m, "") // Tests section
    .trim()

  // Convert CSV code blocks into markdown tables
  const withTables = cleanedBody.replace(
    /```csv\n([\s\S]*?)```/g,
    (_match, csv: string) => {
      const rows = csv.trim().split("\n")
      if (rows.length < 2) return csv
      const header = rows[0].split(",")
      const divider = header.map(() => "---")
      const dataRows = rows.slice(1).map((row) => {
        const cells: string[] = []
        let current = ""
        let inQuotes = false
        for (const char of row) {
          if (char === '"') {
            inQuotes = !inQuotes
          } else if (char === "," && !inQuotes) {
            cells.push(current)
            current = ""
          } else {
            current += char
          }
        }
        cells.push(current)
        return cells
      })
      return [
        `| ${header.join(" | ")} |`,
        `| ${divider.join(" | ")} |`,
        ...dataRows.map((cells) => `| ${cells.join(" | ")} |`),
      ].join("\n")
    },
  )

  return { title, description, codeUrl, body: withTables }
}

function renderDatasetSections(markdown: string): string {
  const sections = markdown.match(/^## Columns\n\n([\s\S]*?)\n\n## Sample\n\n([\s\S]*)$/)
  if (!sections) {
    throw new Error("Expected Columns and Sample sections in generated dataset docs.")
  }

  const columnRows = sections[1].trim().split("\n")
  if (columnRows.length < 3) {
    throw new Error("Expected a columns table in generated dataset docs.")
  }

  const columns = columnRows.slice(2).map((row) => {
    const cells = row.slice(1, -1).split("|").map((cell) => cell.trim())
    if (cells.length !== 4) {
      throw new Error(`Expected four cells in columns row: ${row}`)
    }
    return `| ${cells[0]} | ${cells[2]} |`
  })

  const columnsTable = [
    "| name | description |",
    "|---|---|",
    ...columns,
  ].join("\n")

  return [
    '<details class="dataset-section dataset-section--columns">',
    "<summary>Columns</summary>",
    "",
    columnsTable,
    "",
    "</details>",
    "",
    '<details class="dataset-section dataset-section--sample">',
    "<summary>Sample</summary>",
    "",
    sections[2].trim(),
    "",
    "</details>",
  ].join("\n")
}

function renderCollectionDoc(parsed: ParsedAssetDoc): string {
  const frontmatter = [
    "---",
    `title: ${JSON.stringify(parsed.title)}`,
    ...(parsed.description ? [`description: ${JSON.stringify(parsed.description)}`] : []),
    ...(parsed.codeUrl ? [`codeUrl: ${JSON.stringify(parsed.codeUrl)}`] : []),
    "---",
    "",
  ].join("\n")

  return `${frontmatter}${renderDatasetSections(parsed.body.trim())}\n`
}

async function syncDocs(sourceDir: string): Promise<void> {
  await clearManagedMarkdownFiles(publicAssetsDir)
  await clearManagedMarkdownFiles(contentDir)
  await rm(publicSkillPath, { force: true })

  await copyFile(path.join(sourceDir, "SKILL.md"), publicSkillPath)

  const sourceAssetsDir = path.join(sourceDir, "assets")
  for (const fileName of await listMarkdownFiles(sourceAssetsDir)) {
    const sourcePath = path.join(sourceAssetsDir, fileName)
    const rawMarkdown = await readFile(sourcePath, "utf8")

    await copyFile(sourcePath, path.join(publicAssetsDir, fileName))
    await writeFile(
      path.join(contentDir, fileName),
      renderCollectionDoc(parseAssetDoc(fileName, rawMarkdown)),
    )
  }
}

const sourceDir = await requireRawDocs()
await syncDocs(sourceDir)
