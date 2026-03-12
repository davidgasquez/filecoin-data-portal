// @ts-check
import { defineConfig, fontProviders } from "astro/config";

export default defineConfig({
  site: "https://filecoindataportal.xyz",
  prefetch: {
    prefetchAll: true,
  },
  fonts: [
    {
      provider: fontProviders.bunny(),
      name: "JetBrains Mono",
      cssVariable: "--font-monospace",
    },
  ],
  trailingSlash: "never",
  build: {
    format: "file",
  },
});
