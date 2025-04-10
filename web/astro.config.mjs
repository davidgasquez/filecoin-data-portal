// @ts-check
import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  site: "https://filecoindataportal.xyz",
  prefetch: {
    prefetchAll: true,
  },
  trailingSlash: "never",
  build: {
    format: "file",
  },
});
