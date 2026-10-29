export {}

const root = document.documentElement
const button = document.querySelector<HTMLButtonElement>('[data-theme-toggle]')!
const system = matchMedia('(prefers-color-scheme: dark)')
const current = () => root.dataset.theme ?? (system.matches ? 'dark' : 'light')
function update() {
  const dark = current() === 'dark'
  const next = dark ? 'light' : 'dark'
  // The icon shows the destination theme; both SVGs stay in the markup.
  button.dataset.next = next
  button.setAttribute('aria-label', `Switch to ${next} theme`)
  button.title = `Switch to ${next} theme`
  document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]').forEach(meta => meta.content = dark ? '#0a0a0a' : '#fbfbfa')
}
button.hidden = false
button.addEventListener('click', () => {
  root.dataset.theme = current() === 'dark' ? 'light' : 'dark'
  try { localStorage.setItem('fdp-theme', root.dataset.theme) } catch { /* Works even if storage is blocked. */ }
  update()
})
system.addEventListener('change', update)
addEventListener('storage', event => {
  if (event.key !== 'fdp-theme' && event.key !== null) return
  if (event.newValue === 'light' || event.newValue === 'dark') root.dataset.theme = event.newValue
  else delete root.dataset.theme
  update()
})
update()
