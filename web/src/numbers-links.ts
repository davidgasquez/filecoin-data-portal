export {}

// Chart deeplinks: legacy metric ids (#raw-power), column ids (#raw_power_pibs) and combined-chart aliases.
// Native anchors scroll on their own; this opens closed ancestors (related measures, audits) and moves focus.
const root = document.querySelector<HTMLElement>('.numbers')!

function reveal() {
  let id = ''
  try { id = decodeURIComponent(location.hash.slice(1)) } catch { return }
  const node = id ? document.getElementById(id) : null
  // Sections are plain native anchors, handled by the section nav.
  if (!node || !root.contains(node) || node.matches('section.board')) return
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

// Clipboard API needs a secure origin; plain-HTTP hosts (e.g. a Tailscale address) fall back to execCommand.
function fallback(text: string, button: HTMLElement) {
  const area = Object.assign(document.createElement('textarea'), { value: text, readOnly: true })
  area.style.cssText = 'position:fixed;top:0;opacity:0'
  document.body.append(area)
  area.select()
  let ok = false
  try { ok = document.execCommand('copy') } catch {}
  area.remove()
  button.focus()
  return ok
}

for (const button of root.querySelectorAll<HTMLButtonElement>('[data-copy-link]')) {
  const status = button.nextElementSibling as HTMLElement
  let timer = 0
  button.hidden = false
  button.addEventListener('click', async () => {
    // Current origin, path and range; only the fragment changes.
    const url = new URL(location.href)
    url.hash = button.dataset.copyLink!
    let ok = false
    try { await navigator.clipboard.writeText(url.href); ok = true } catch { ok = fallback(url.href, button) }
    status.textContent = ok ? 'Link copied' : 'Could not copy. Use the link instead.'
    window.clearTimeout(timer)
    timer = window.setTimeout(() => { status.textContent = '' }, 4000)
  })
}

addEventListener('hashchange', reveal)
reveal()
