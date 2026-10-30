import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import { runInNewContext } from 'node:vm'

// Exercise the page/history hooks with a router that can omit its lifecycle on fragment traversals.
const source = readFileSync(new URL('../src/foc/client.ts', import.meta.url), 'utf8')
const script = stripTypeScriptTypes(source.slice(source.indexOf('// ---------------------------------------------------------------- pages')))
function page() {
  const handlers = new Map(), timers = new Map(), reads = [], scrolls = [], links = []
  let id = 0
  const listen = (type, fn) => handlers.set(type, [...(handlers.get(type) ?? []), fn])
  const context = {
    location: new URL('https://example.test/providers#main'), history: { state: { scrollX: 0, scrollY: 600 } },
    performance: { getEntriesByType: () => [] }, onPage: () => {}, tables: ['providers'],
    read: table => reads.push(table), scrollTo: options => scrolls.push(options),
    addEventListener: listen, navigator: { connection: {} },
    clearTimeout: id => timers.delete(id), window: { setTimeout: fn => { timers.set(++id, fn); return id } },
    document: {
      addEventListener: listen,
      querySelectorAll: () => [],
      createElement: () => ({ remove() { links.splice(links.indexOf(this), 1) } }),
      head: { append: link => links.push(link) },
    },
  }
  runInNewContext(`${script}\npath = location.pathname`, context)
  const emit = (type, event = {}) => { for (const fn of handlers.get(type) ?? []) fn(event) }
  const flush = () => { for (const [id, fn] of [...timers]) { timers.delete(id); fn() } }
  const anchor = href => Object.assign(new URL(href, context.location), { isConnected: true })
  const intent = (a, type = 'pointerover', pointerType = 'mouse') => emit(type, { target: { closest: () => a }, pointerType })
  return { context, emit, flush, reads, scrolls, links, anchor, intent }
}

test('fragment Back/Forward reads table state even without Astro swap events', () => {
  const p = page()
  for (const url of ['/providers#main', '/providers?sort=provider#main', '/providers?f=active#main']) {
    p.context.location = new URL(url, p.context.location)
    p.emit('popstate')
  }
  assert.deepEqual(p.reads, ['providers', 'providers', 'providers'])
  assert.equal(p.scrolls.length, 3)
  assert.ok(p.scrolls.every(s => s.top === 600 && s.behavior === 'instant'))
  p.context.location = new URL('https://example.test/provider/1')
  p.emit('popstate')
  assert.equal(p.reads.length, 3, 'Other routes wait for their new page setup')
})

test('hover/focus prefetch once per URL, ignoring fragments, and remove completed hints', () => {
  const p = page(), a = p.anchor('/provider/1#quality')
  p.intent(a); assert.equal(p.links.length, 0, 'Wait for intent, not a passing pointer')
  p.flush(); assert.equal(p.links.length, 1)
  assert.equal(p.links[0].rel, 'prefetch')
  assert.equal(p.links[0].href, 'https://example.test/provider/1')
  p.links[0].onload(); assert.equal(p.links.length, 0)
  p.intent(p.anchor('/provider/1'), 'focusin'); p.flush()
  assert.equal(p.links.length, 0, 'No duplicate request after revisiting or swapping')
  p.intent(p.anchor('/provider/2'), 'focusin'); p.flush()
  assert.equal(p.links.length, 1, 'Delegated focus still handles new links')
  p.links[0].onerror()
  p.intent(p.anchor('/provider/2'), 'focusin'); p.flush()
  assert.equal(p.links.length, 1, 'A failed hint can be retried')
})

test('prefetch skips unmarked, portal, current, touch and constrained-network links', () => {
  const p = page()
  for (const a of [null, p.anchor('https://portal.test/numbers'), p.anchor('/providers#main'), p.anchor('https://other.test/provider/1')]) {
    p.intent(a); p.flush()
  }
  const a = p.anchor('/provider/1')
  p.intent(a, 'pointerover', 'touch'); p.flush()
  p.context.navigator.connection.saveData = true
  p.intent(a, 'focusin'); p.flush()
  p.context.navigator.connection = { effectiveType: 'slow-2g' }
  p.intent(a); p.flush()
  assert.equal(p.links.length, 0)
})

test('prefetch cancels on departure, navigation, and detached anchors', () => {
  const p = page(), a = p.anchor('/provider/1')
  for (const type of ['pointerout', 'focusout', 'astro:before-preparation']) {
    p.intent(a)
    p.emit(type, { to: p.anchor('/clients'), navigationType: 'push' })
    p.flush()
  }
  p.intent(a); a.isConnected = false; p.flush()
  assert.equal(p.links.length, 0)
})
