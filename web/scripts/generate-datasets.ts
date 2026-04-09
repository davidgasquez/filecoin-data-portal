import { mkdir, readdir, unlink, writeFile } from "node:fs/promises"
import type { Dirent } from "node:fs"
import path from "node:path"
import { pathToFileURL } from "node:url"

type JsonPrimitive = boolean | number | string | null
type DatasetRow = Record<string, JsonPrimitive>
type DatasetGenerator = () => Promise<DatasetRow[]>

function assertDatasetRows(dataset: unknown, datasetFile: string): asserts dataset is DatasetRow[] {
  if (!Array.isArray(dataset)) {
    throw new Error(`Dataset script ${datasetFile} must return an array of rows`)
  }

  for (const [rowIndex, row] of dataset.entries()) {
    if (row == null || Array.isArray(row) || typeof row !== "object") {
      throw new Error(`Dataset script ${datasetFile} row ${rowIndex} must be a plain object`)
    }

    for (const [column, value] of Object.entries(row)) {
      const valueType = typeof value

      if (value == null || valueType === "boolean" || valueType === "string") {
        continue
      }

      if (valueType === "number" && Number.isFinite(value)) {
        continue
      }

      throw new Error(
        `Dataset script ${datasetFile} row ${rowIndex} column ${column} must be a JSON primitive`,
      )
    }
  }
}

const datasetsDir = path.resolve(process.cwd(), "datasets")
const generatedDir = path.resolve(process.cwd(), "src/data/generated")

await mkdir(generatedDir, { recursive: true })

const entries = await readdir(datasetsDir, { withFileTypes: true })
const datasetFiles = entries
  .filter((entry: Dirent) => entry.isFile() && entry.name.endsWith(".ts"))
  .map((entry: Dirent) => entry.name)
  .sort()

const expectedOutputFiles = new Set(
  datasetFiles.map((datasetFile) => `${path.basename(datasetFile, ".ts")}.json`),
)

for (const datasetFile of datasetFiles) {
  const modulePath = path.join(datasetsDir, datasetFile)
  const datasetModule = (await import(pathToFileURL(modulePath).href)) as {
    default?: DatasetGenerator
  }

  if (!datasetModule.default) {
    throw new Error(`Dataset script ${modulePath} must export a default async function`)
  }

  console.log(`Generating dataset from ${path.relative(process.cwd(), modulePath)}`)
  const dataset = await datasetModule.default()
  assertDatasetRows(dataset, datasetFile)
  const outputPath = path.join(
    generatedDir,
    `${path.basename(datasetFile, path.extname(datasetFile))}.json`,
  )
  await writeFile(outputPath, JSON.stringify(dataset))
}

const generatedEntries = await readdir(generatedDir, { withFileTypes: true })

for (const entry of generatedEntries) {
  if (!entry.isFile() || !entry.name.endsWith(".json")) {
    continue
  }

  if (expectedOutputFiles.has(entry.name)) {
    continue
  }

  const staleOutputPath = path.join(generatedDir, entry.name)
  console.log(`Removing stale generated dataset ${path.relative(process.cwd(), staleOutputPath)}`)
  await unlink(staleOutputPath)
}

if (datasetFiles.length === 0) {
  console.log(`No dataset scripts found in ${datasetsDir}`)
}
