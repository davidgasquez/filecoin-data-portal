// @ts-check
import { defineConfig, fontProviders } from "astro/config";

export default defineConfig({
  site: "https://filecoindataportal.xyz",
  prefetch: {
    prefetchAll: true,
  },
  trailingSlash: "never",
  build: {
    format: "file",
  },
  experimental: {
    fonts: [
      {
        provider: fontProviders.bunny(),
        name: "Inter",
        cssVariable: "--font-sans",
      },
      {
        provider: fontProviders.bunny(),
        name: "JetBrains Mono",
        cssVariable: "--font-monospace",
      },
    ],
  },
});
