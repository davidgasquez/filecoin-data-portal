// Shared enhancements loaded by the layout: copy buttons and Info disclosure dismissal.
// Copy controls ship hidden; the text, code and real links beside them stay selectable without JavaScript.

// Runs setup for the first page and for each page Astro's router swaps in (/foc only).
// Aborting the signal before a real swap drops the old page's listeners and pending work.
export function onPage(setup: (signal: AbortSignal) => void) {
  let body: HTMLElement | undefined, controller: AbortController | undefined
  const run = () => {
    if (body === document.body) return
    body = document.body
    controller?.abort()
    controller = new AbortController()
    setup(controller.signal)
  }
  document.addEventListener('astro:before-swap', (event) => { if (event.newDocument !== document) controller?.abort() })
  document.addEventListener('astro:page-load', run)
  run()
}

// Clipboard API needs a secure origin; plain-HTTP hosts (e.g. a Tailscale address) fall back to execCommand.
async function write(text: string, button: HTMLElement, signal: AbortSignal) {
  try { await navigator.clipboard.writeText(text); return true } catch {}
  if (signal.aborted) return false
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

// Chart links keep the current origin, path and range query; only the fragment changes.
function linkTo(id: string) {
  const url = new URL(location.href)
  url.hash = id
  return url.href
}

// Button names never change; one status per button announces and shows the outcome.
// Authored statuses follow the button; created ones are marked and sit before it.
function statusFor(button: HTMLElement) {
  const next = button.nextElementSibling, previous = button.previousElementSibling
  if (next?.getAttribute('role') === 'status') return next as HTMLElement
  if (previous?.hasAttribute('data-copy-status')) return previous as HTMLElement
  const status = document.createElement('span')
  status.className = 'meta'
  status.setAttribute('role', 'status')
  status.setAttribute('data-copy-status', '')
  button.before(status)
  return status
}

onPage((signal) => {
  for (const button of document.querySelectorAll<HTMLButtonElement>('[data-copy], [data-copy-link]')) {
    const link = button.dataset.copyLink
    const status = statusFor(button)
    let frame = 0, timer = 0
    const clear = () => { cancelAnimationFrame(frame); window.clearTimeout(timer) }
    signal.addEventListener('abort', clear)
    button.hidden = false
    button.addEventListener('click', async () => {
      clear()
      status.textContent = ''
      let message = link == null ? 'Copied' : 'Link copied'
      const copied = await write(link == null ? button.dataset.copy! : linkTo(link), button, signal)
      if (signal.aborted) return
      if (!copied) {
        const pre = link == null ? button.closest('.copy')?.querySelector('pre') : null
        if (pre) getSelection()?.selectAllChildren(pre)
        message = pre ? 'Selected, press Ctrl+C or ⌘C' : link == null ? 'Could not copy' : 'Could not copy. Use the link instead.'
      }
      // Set on the next frame so a repeated identical message is announced again.
      clear()
      frame = requestAnimationFrame(() => {
        status.textContent = message
        timer = window.setTimeout(() => { status.textContent = '' }, 4000)
      })
    }, { signal })
  }
})

// Info disclosures and the Numbers and explorer menus close on Escape or an outside click. Audits and related measures stay as the reader left them.
const openInfos = () => document.querySelectorAll<HTMLDetailsElement>('details:is(.metric-info, .nav-menu, .foc-menu)[open]')
document.addEventListener('keydown', (event) => {
  // Fields and widgets that handle Escape themselves (search, filters) keep it.
  if (event.key !== 'Escape' || event.defaultPrevented || (event.target as Element).closest?.('input, textarea, select')) return
  for (const info of openInfos()) {
    if (info.contains(document.activeElement)) info.querySelector('summary')?.focus()
    info.open = false
  }
})
// The explorer menu also closes on a choice: its current page stays in place rather than swapping in a closed menu.
document.addEventListener('click', (event) => {
  const target = event.target as Element
  for (const info of openInfos()) if (!info.contains(target) || (info.matches('.foc-menu') && target.closest?.('a'))) info.open = false
})
// Tabbing out of the explorer menu closes it, as the Numbers menu does.
document.addEventListener('focusout', (event) => {
  const menu = (event.target as Element).closest?.<HTMLDetailsElement>('.foc-menu')
  if (menu?.open && event.relatedTarget && !menu.contains(event.relatedTarget as Node)) menu.open = false
})
