import { defineConfig, fontProviders } from 'astro/config'

// Build origin for canonicals, generated Markdown, robots.txt and the post-build header step.
// Defaults to production; preview builds pass their workers.dev URL.
export default defineConfig({
  site: process.env.SITE_URL || 'https://filecoindataportal.xyz',
  trailingSlash: 'never',
  devToolbar: { enabled: false },
  server: { allowedHosts: ['helix.shad-hamal.ts.net'] },
  build: { format: 'directory' },
  fonts: [
    { provider: fontProviders.bunny(), name: 'IBM Plex Sans', cssVariable: '--font-sans', weights: [400, 500] },
    { provider: fontProviders.bunny(), name: 'IBM Plex Mono', cssVariable: '--font-mono', weights: [400, 500] },
  ],
})
