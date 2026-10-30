import { defineConfig, fontProviders } from 'astro/config'

// Build origin for canonicals, generated Markdown, robots.txt and the post-build header step.
// Defaults to production; preview builds pass their workers.dev URL.
export default defineConfig({
  site: process.env.SITE_URL || 'https://filecoindataportal.xyz',
  trailingSlash: 'never',
  devToolbar: { enabled: false },
  server: { port: 4322, allowedHosts: ['helix.shad-hamal.ts.net'] },
  build: { format: 'directory' },
  // The explorer supplies delegated, intent-only native hints; other pages need no prefetch script.
  prefetch: false,
  fonts: [
    { provider: fontProviders.bunny(), name: 'IBM Plex Sans', cssVariable: '--font-sans', weights: [400, 500], styles: ['normal'] },
    { provider: fontProviders.bunny(), name: 'IBM Plex Mono', cssVariable: '--font-mono', weights: [400, 500], styles: ['normal'] },
  ],
})
