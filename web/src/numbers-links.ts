export {}

// Chart deeplinks: legacy metric ids (#raw-power), column ids (#raw_power_pibs) and combined-chart aliases.
// Native anchors scroll on their own; this opens closed ancestors (related measures, audits) and moves focus.
const root = document.querySelector<HTMLElement>('.numbers')!

function reveal() {
  let id = ''
  try { id = decodeURIComponent(location.hash.slice(1)) } catch { return }
  const node = id ? document.getElementById(id) : null
  // Sections and the contents are plain native anchors, handled by the browser and the section menu.
  if (!node || !root.contains(node) || node.matches('section.board, #contents')) return
  const target = node.classList.contains('anchor-alias') ? node.parentElement! : node
  for (let el: HTMLElement | null = target; el && el !== root; el = el.parentElement) {
    if (el instanceof HTMLDetailsElement) el.open = true
  }
  requestAnimationFrame(() => {
    target.scrollIntoView({ block: 'start' })
    if (target.contains(document.activeElement)) return
    if (!target.hasAttribute('tabindex')) target.tabIndex = -1
    target.focus({ preventScroll: true })
  })
}

addEventListener('hashchange', reveal)
reveal()
