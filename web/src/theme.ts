export {}

const root = document.documentElement
const system = matchMedia('(prefers-color-scheme: dark)')
const current = () => root.dataset.theme ?? (system.matches ? 'dark' : 'light')
// Labels the toggle and theme colour of a document: the current one, or an incoming /foc page before it paints.
function update(doc: Document = document) {
  const dark = current() === 'dark'
  const next = dark ? 'light' : 'dark'
  const button = doc.querySelector<HTMLButtonElement>('[data-theme-toggle]')
  if (button) {
    // The icon shows the destination theme; both SVGs stay in the markup.
    button.dataset.next = next
    button.setAttribute('aria-label', `Switch to ${next} theme`)
    button.title = `Switch to ${next} theme`
    button.hidden = false
  }
  doc.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]').forEach(meta => meta.content = dark ? '#0a0a0a' : '#fbfbfa')
}
document.addEventListener('click', event => {
  if (!(event.target as Element).closest?.('[data-theme-toggle]')) return
  root.dataset.theme = current() === 'dark' ? 'light' : 'dark'
  try { localStorage.setItem('fdp-theme', root.dataset.theme) } catch { /* Works even if storage is blocked. */ }
  update()
})
// Router swaps replace the root attributes and header: carry the theme over before the new page renders.
document.addEventListener('astro:before-swap', event => {
  const incoming = event.newDocument.documentElement
  if (root.dataset.theme) incoming.dataset.theme = root.dataset.theme
  else delete incoming.dataset.theme
  update(event.newDocument)
})
system.addEventListener('change', () => update())
addEventListener('storage', event => {
  if (event.key !== 'fdp-theme' && event.key !== null) return
  if (event.newValue === 'light' || event.newValue === 'dark') root.dataset.theme = event.newValue
  else delete root.dataset.theme
  update()
})
update()
