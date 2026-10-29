export {}

const toolbar = document.querySelector<HTMLElement>('.numbers-toolbar')!
const menu = toolbar.querySelector<HTMLDetailsElement>('.section-menu')!
const links = [...toolbar.querySelectorAll<HTMLAnchorElement>('[data-section-nav] a')]
const sections = [...new Set(links.map(link => document.getElementById(link.hash.slice(1))!))]
let active = '', frame = 0
function update() {
  const edge = toolbar.getBoundingClientRect().bottom + 24
  const current = sections.findLast(section => section.getBoundingClientRect().top <= edge) ?? sections[0]
  if (current.id === active) return
  active = current.id
  for (const link of links) {
    if (link.hash === `#${active}`) link.setAttribute('aria-current', 'location')
    else link.removeAttribute('aria-current')
  }
}
const queue = () => { if (!frame) frame = requestAnimationFrame(() => { frame = 0; update() }) }
addEventListener('scroll', queue, { passive: true })
addEventListener('resize', queue)
for (const link of links) link.addEventListener('click', () => {
  menu.open = false
  const section = document.getElementById(link.hash.slice(1))!
  section.tabIndex = -1
  section.focus({ preventScroll: true })
})
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary')?.focus() }
})
document.addEventListener('click', event => { if (!menu.contains(event.target as Node)) menu.open = false })
update()
