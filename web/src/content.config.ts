import { defineCollection } from "astro:content"
import { glob } from "astro/loaders"
import { z } from "astro/zod"

const datasetDocs = defineCollection({
  loader: glob({
    base: "./src/content/dataset-docs",
    pattern: "**/*.md",
  }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    codeUrl: z.string().url().optional(),
  }),
})

export const collections = {
  "dataset-docs": datasetDocs,
}
