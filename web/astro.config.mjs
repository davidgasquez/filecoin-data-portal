// @ts-check
import { defineConfig, fontProviders } from "astro/config"

export default defineConfig({
  site: "https://filecoindataportal.xyz",
  trailingSlash: "never",
  build: { format: "file" },
  compressHTML: true,
  fonts: [{ provider: fontProviders.bunny(), name: "JetBrains Mono", cssVariable: "--font-monospace" }],
})
