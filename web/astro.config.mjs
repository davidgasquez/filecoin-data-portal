import { defineConfig, fontProviders } from 'astro/config'
import { explorer, origin, outDir } from './src/site.mjs'

// FDP_SITE=foc builds the Onchain Cloud explorer from src/foc/pages; the portal is the default.
// `site` is that target's origin for canonicals, generated Markdown, robots.txt and the post-build step.
export default defineConfig({
  site: origin,
  srcDir: explorer ? './src/foc' : './src',
  outDir,
  trailingSlash: 'never',
  devToolbar: { enabled: false },
  server: { port: explorer ? 4323 : 4322, allowedHosts: ['helix.shad-hamal.ts.net'] },
  build: { format: 'directory' },
  // Separate dependency caches, so both development servers can run at once.
  vite: { cacheDir: explorer ? 'node_modules/.vite-foc' : 'node_modules/.vite' },
  // The explorer supplies delegated, intent-only native hints; other pages need no prefetch script.
  prefetch: false,
  fonts: [
    { provider: fontProviders.bunny(), name: 'IBM Plex Sans', cssVariable: '--font-sans', weights: [400, 500], styles: ['normal'] },
    { provider: fontProviders.bunny(), name: 'IBM Plex Mono', cssVariable: '--font-mono', weights: [400, 500], styles: ['normal'] },
  ],
})
