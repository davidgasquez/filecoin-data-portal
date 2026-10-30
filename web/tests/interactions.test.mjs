import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import { runInNewContext } from 'node:vm'

const script = stripTypeScriptTypes(readFileSync(new URL('../src/interactions.ts', import.meta.url), 'utf8')).replace('export function onPage', 'function onPage')

// Just enough DOM for the script: elements with attributes, siblings, containment and listeners.
function element(tag, attrs = {}) {
  const el = {
    tag, attrs: { ...attrs }, dataset: {}, listeners: {}, parent: null, children: [], textContent: '', hidden: true,
    getAttribute: name => el.attrs[name] ?? null,
    setAttribute: (name, value) => { el.attrs[name] = String(value) },
    addEventListener: (name, callback, options) => {
      el.listeners[name] = callback
      options?.signal?.addEventListener('abort', () => { if (el.listeners[name] === callback) delete el.listeners[name] })
    },
    hasAttribute: name => name in el.attrs,
    get nextElementSibling() { const s = el.parent?.children; return s?.[s.indexOf(el) + 1] ?? null },
    get previousElementSibling() { const s = el.parent?.children; return s?.[s.indexOf(el) - 1] ?? null },
    before: node => { node.parent = el.parent; el.parent.children.splice(el.parent.children.indexOf(el), 0, node) },
    contains: node => { for (let n = node; n; n = n.parent) if (n === el) return true; return false },
    closest: selector => { for (let n = el; n; n = n.parent) if (n.matches?.(selector)) return n; return null },
    matches: selector => selector.split(',').some(s => s.trim() === tag || s.trim() === `.${el.attrs.class}`),
    querySelector: selector => el.children.find(child => child.matches(selector)) ?? null,
    focus: () => { state.focused = el },
    set className(value) { el.attrs.class = value },
  }
  return el
}
function append(parent, ...children) { for (const child of children) { child.parent = parent; parent.children.push(child) }; return parent }
let state

function page({ clipboard = true, execCommand = false, href = 'https://example.test/numbers?range=1y#old' } = {}) {
  state = { focused: null, copied: [], timers: [], selected: null, listeners: {}, nodes: 0 }
  const body = element('body')
  const block = append(element('div', { class: 'copy' }), element('pre'), element('button'))
  const text = block.children[1]; text.dataset.copy = 'select 1'
  const row = append(element('p'), element('button'), element('span', { role: 'status' }))
  const link = row.children[0]; link.dataset.copyLink = 'raw-power'
  const address = append(element('dd'), element('button', { 'aria-label': 'Copy address' }))
  const plain = address.children[0]; plain.dataset.copy = '0xabc'
  const info = append(element('details', { class: 'metric-info' }), element('summary'), element('button'))
  const audit = element('details', { class: 'audit' })
  const menu = append(element('details', { class: 'nav-menu' }), element('summary'), element('a'))
  const explorer = append(element('details', { class: 'foc-menu' }), element('summary'), element('a'))
  append(body, block, row, address, info, menu, audit)
  info.open = menu.open = explorer.open = audit.open = true
  const context = {
    URL, AbortController,
    location: { href },
    navigator: clipboard ? { clipboard: { writeText: async value => { state.copied.push(value) } } } : {},
    getSelection: () => ({ selectAllChildren: node => { state.selected = node } }),
    document: {
      body,
      get activeElement() { return state.focused },
      querySelectorAll: selector => selector.includes('data-copy')
        ? [text, link, plain]
        : [info, menu, explorer, audit].filter(d => d.open && selector.includes(`.${d.attrs.class}`)),
      createElement: tag => {
        state.nodes++
        const el = element(tag)
        el.select = () => { state.focused = el }
        el.remove = () => { body.children.splice(body.children.indexOf(el), 1) }
        el.style = {}
        return el
      },
      execCommand: () => { if (execCommand) state.copied.push(state.focused.value); return execCommand },
      addEventListener: (name, callback) => { state.listeners[name] = callback },
    },
  }
  body.append = el => append(body, el)
  context.window = { setTimeout: (callback, ms) => state.timers.push({ callback, ms }) && state.timers.length, clearTimeout: id => { if (id) state.timers[id - 1].callback = () => {} } }
  context.requestAnimationFrame = callback => context.window.setTimeout(callback, 0)
  context.cancelAnimationFrame = context.window.clearTimeout
  runInNewContext(script, context)
  const tick = () => { while (state.timers.some(t => t.callback)) state.timers.forEach(t => { const c = t.callback; t.callback = null; c?.() }) }
  const flush = () => { const t = state.timers.findLast(t => t.callback); const c = t.callback; t.callback = null; c() }
  const click = async button => { await button.listeners.click(); flush() }
  // An explorer router swap: abort the old page, then page-load with a new <body> (here holding the same buttons).
  const swap = () => { state.listeners['astro:before-swap']({ newDocument: {} }); context.document.body = element('body'); state.listeners['astro:page-load']() }
  return { block, text, row, link, address, plain, info, menu, explorer, audit, body, click, tick, swap, context }
}

test('copy buttons reveal, keep their names, and reuse one status each', async () => {
  const p = page()
  for (const button of [p.text, p.link, p.plain]) assert.equal(button.hidden, false)
  // The chart link reuses its existing status; other buttons get one inserted just before them.
  assert.equal(p.row.children.length, 2)
  assert.deepEqual(p.block.children.map(c => c.tag), ['pre', 'span', 'button'])
  const status = p.block.children[1]
  assert.equal(status.getAttribute('role'), 'status')
  assert.equal(status.attrs.class, 'meta')
  await p.click(p.text)
  await p.click(p.text)
  assert.equal(status.textContent, 'Copied')
  assert.equal(p.text.textContent, '')
  assert.equal(p.block.children.length, 3)
  assert.equal(p.body.children.length, 6)
  p.tick()
  assert.equal(status.textContent, '')
})

test('chart links keep origin, path and range query and replace only the fragment', async () => {
  const p = page()
  await p.click(p.link)
  assert.deepEqual(state.copied, ['https://example.test/numbers?range=1y#raw-power'])
  assert.equal(p.row.children[1].textContent, 'Link copied')
})

test('plain HTTP falls back to execCommand and returns focus to the button', async () => {
  const p = page({ clipboard: false, execCommand: true, href: 'http://100.64.0.1:4322/numbers?range=all' })
  await p.click(p.link)
  assert.deepEqual(state.copied, ['http://100.64.0.1:4322/numbers?range=all#raw-power'])
  assert.equal(state.focused, p.link)
  assert.equal(p.row.children[1].textContent, 'Link copied')
  assert.equal(p.body.children.length, 6)
})

test('failed copies announce a fallback: select code, use the link, or report', async () => {
  const p = page({ clipboard: false })
  await p.click(p.text)
  assert.equal(state.selected, p.block.children[0])
  assert.equal(p.block.children[1].textContent, 'Selected, press Ctrl+C or ⌘C')
  await p.click(p.link)
  assert.equal(p.row.children[1].textContent, 'Could not copy. Use the link instead.')
  await p.click(p.plain)
  assert.equal(p.address.children[0].textContent, 'Could not copy')
  assert.equal(p.plain.getAttribute('aria-label'), 'Copy address')
})

test('a clipboard rejection after leaving the page cannot focus or modify the new page', async () => {
  const p = page()
  let reject
  p.context.navigator.clipboard.writeText = () => new Promise((_, r) => { reject = r })
  const copying = p.text.listeners.click()
  const nodes = state.nodes
  p.swap()
  reject(new Error('Permission denied'))
  await copying
  assert.equal(state.nodes, nodes, 'No fallback textarea on the new page')
  assert.equal(state.focused, null)
  assert.equal(state.selected, null)
  assert.equal(state.timers.length, 0)
})

test('Escape and outside clicks close only Info disclosures and the Numbers menu, returning focus when it was inside', () => {
  let p = page()
  state.focused = p.info.children[1]
  state.listeners.keydown({ key: 'Escape', target: state.focused })
  assert.equal(p.info.open, false)
  assert.equal(p.menu.open, false)
  assert.equal(p.audit.open, true)
  assert.equal(state.focused, p.info.children[0])

  p = page()
  state.focused = p.menu.children[1]
  state.listeners.keydown({ key: 'Escape', target: state.focused })
  assert.equal(p.menu.open, false)
  assert.equal(state.focused, p.menu.children[0])
  p.menu.open = true
  state.listeners.click({ target: p.menu.children[1] })
  assert.equal(p.menu.open, true)
  state.listeners.click({ target: p.audit })
  assert.equal(p.menu.open, false)

  p = page()
  state.focused = p.text
  state.listeners.keydown({ key: 'Escape', target: p.text })
  assert.equal(p.info.open, false)
  assert.equal(state.focused, p.text)

  p = page()
  const search = element('input')
  state.listeners.keydown({ key: 'Escape', target: search })
  state.listeners.keydown({ key: 'Escape', target: p.text, defaultPrevented: true })
  assert.equal(p.info.open, true)

  state.listeners.click({ target: p.info.children[1] })
  assert.equal(p.info.open, true)
  state.listeners.click({ target: p.audit })
  assert.equal(p.info.open, false)
  assert.equal(p.audit.open, true)
})

test('the explorer menu closes on Escape, outside clicks, a link choice and tabbing out, but not inside', () => {
  let p = page()
  const [summary, link] = p.explorer.children
  state.focused = link
  state.listeners.keydown({ key: 'Escape', target: link })
  assert.equal(p.explorer.open, false)
  assert.equal(state.focused, summary, 'Escape returns focus to the summary')

  p = page()
  state.listeners.click({ target: p.explorer.children[0] })
  assert.equal(p.explorer.open, true, 'Toggling stays native')
  state.listeners.click({ target: p.explorer.children[1] })
  assert.equal(p.explorer.open, false, 'A choice closes it, including the current page that does not swap')
  p.explorer.open = true
  state.listeners.click({ target: p.audit })
  assert.equal(p.explorer.open, false)

  p = page()
  state.listeners.focusout({ target: p.explorer.children[1], relatedTarget: p.explorer.children[0] })
  state.listeners.focusout({ target: p.explorer.children[1], relatedTarget: null })
  assert.equal(p.explorer.open, true, 'Moving within the menu or leaving the window keeps it open')
  state.listeners.focusout({ target: p.explorer.children[1], relatedTarget: p.audit })
  assert.equal(p.explorer.open, false)
  assert.equal(p.menu.open, true, 'The Numbers menu keeps its own focus handling')
})

test('page setup runs once per page and drops the old page work on a router swap', async () => {
  const p = page()
  const listener = p.text.listeners.click
  // The router's first page-load repeats the initial page: nothing is set up twice.
  state.listeners['astro:page-load']()
  assert.equal(p.text.listeners.click, listener)
  // Same-page Back/Forward keeps the document: nothing is aborted.
  state.listeners['astro:before-swap']({ newDocument: p.context.document })
  state.listeners['astro:page-load']()
  assert.equal(p.text.listeners.click, listener)
  // A pending message is cancelled by the swap and the next setup reuses the created status.
  await p.text.listeners.click()
  p.swap()
  assert.notEqual(p.text.listeners.click, listener)
  assert.deepEqual(p.block.children.map(c => c.tag), ['pre', 'span', 'button'])
  assert.equal(p.row.children.length, 2)
  p.tick()
  assert.equal(p.block.children[1].textContent, '')
  await p.click(p.text)
  assert.equal(p.block.children[1].textContent, 'Copied')
})
