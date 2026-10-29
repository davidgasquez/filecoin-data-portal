// @ts-check
import { defineConfig, fontProviders } from "astro/config"

export default defineConfig({
  site: process.env.SITE_URL ?? "https://old.filecoindataportal.xyz",
  trailingSlash: "never",
  build: { format: "file" },
  compressHTML: true,
  fonts: [{ provider: fontProviders.bunny(), name: "JetBrains Mono", cssVariable: "--font-monospace" }],
})
