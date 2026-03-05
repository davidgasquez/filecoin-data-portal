import { readdir } from "node:fs/promises"
import type { Dirent } from "node:fs"
import path from "node:path"
import { pathToFileURL } from "node:url"

type DatasetGenerator = () => Promise<void>

const datasetsDir = path.resolve(process.cwd(), "datasets")

const entries = await readdir(datasetsDir, { withFileTypes: true })
const datasetFiles = entries
  .filter((entry: Dirent) => entry.isFile() && entry.name.endsWith(".ts"))
  .map((entry: Dirent) => entry.name)
  .sort()

if (datasetFiles.length === 0) {
  console.log(`No dataset scripts found in ${datasetsDir}`)
  process.exit(0)
}

for (const datasetFile of datasetFiles) {
  const modulePath = path.join(datasetsDir, datasetFile)
  const datasetModule = (await import(pathToFileURL(modulePath).href)) as {
    default?: DatasetGenerator
  }

  if (!datasetModule.default) {
    throw new Error(`Dataset script ${modulePath} must export a default async function`)
  }

  console.log(`Generating dataset from ${path.relative(process.cwd(), modulePath)}`)
  await datasetModule.default()
}
