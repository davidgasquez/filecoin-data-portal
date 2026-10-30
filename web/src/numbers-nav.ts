export {}

// The header's Numbers menu names and marks the current section. The introduction's contents stay plain links.
const menu = document.querySelector<HTMLDetailsElement>('.nav-menu')!
const label = menu.querySelector<HTMLElement>('[data-section-current]')!
const links = [...menu.querySelectorAll<HTMLAnchorElement>('[data-section-nav] a')]
// The first link returns to the contents; it is never the current section.
const tracked = links.slice(1)
const sections = tracked.map(link => document.getElementById(link.hash.slice(1))!)
let active: string | undefined = '', frame = 0
function update() {
  // Anchors land at the scroll padding, which clears the sticky header.
  const edge = (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0) + 24
  // The final section can be too short to reach the top of the viewport.
  const atEnd = scrollY + innerHeight >= document.documentElement.scrollHeight - 1
  const current = atEnd ? sections.at(-1) : sections.findLast(section => section.getBoundingClientRect().top <= edge)
  if (current?.id === active) return
  active = current?.id
  label.textContent = `/ ${links[0].textContent}`
  for (const link of tracked) {
    if (link.hash === `#${active}`) {
      link.setAttribute('aria-current', 'location')
      label.textContent = `/ ${link.textContent}`
    } else link.removeAttribute('aria-current')
  }
  label.title = label.textContent
}
const queue = () => { if (!frame) frame = requestAnimationFrame(() => { frame = 0; update() }) }
addEventListener('scroll', queue, { passive: true })
addEventListener('resize', queue)
// Native anchors scroll; the menu closes and focus moves to the destination.
for (const link of links) link.addEventListener('click', () => {
  menu.open = false
  const target = document.getElementById(link.hash.slice(1))!
  target.tabIndex = -1
  target.focus({ preventScroll: true })
})
// Tabbing out of the open menu closes it. Escape and outside clicks are handled with Info disclosures.
menu.addEventListener('focusout', (event) => {
  if (event.relatedTarget && !menu.contains(event.relatedTarget as Node)) menu.open = false
})
update()
