import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import { runInNewContext } from 'node:vm'

const script = stripTypeScriptTypes(readFileSync(new URL('../src/numbers-nav.ts', import.meta.url), 'utf8')).replace('export {};', '').replace('export {}', '')

function navigation() {
  const events = {}, frames = []
  const state = { tops: [200, 800, 1400], focused: null }
  const targets = ['contents', 'first', 'middle', 'last'].map((id, i) => ({
    id, getBoundingClientRect: () => ({ top: i ? state.tops[i - 1] : 0 }),
    focus: () => { state.focused = id },
  }))
  const link = ({ id }) => ({
    hash: `#${id}`, textContent: id === 'contents' ? 'Contents' : `Section ${id}`, current: null,
    setAttribute(name, value) { assert.equal(name, 'aria-current'); this.current = value },
    removeAttribute() { this.current = null },
    addEventListener(name, callback) { this[name] = callback },
  })
  const links = targets.map(link)
  // The introduction's contents link the same sections; they are never marked.
  const intro = targets.slice(1).map(link)
  const label = { textContent: '', title: '' }
  const menu = {
    open: true,
    querySelector: selector => selector === '[data-section-current]' ? label : null,
    querySelectorAll: () => links,
    contains: node => links.includes(node),
    addEventListener(name, callback) { this[name] = callback },
  }
  const context = {
    document: {
      documentElement: { scrollHeight: 3000 },
      querySelector: selector => selector === '.nav-menu' ? menu : null,
      querySelectorAll: () => [...links, ...intro],
      getElementById: id => targets.find(target => target.id === id),
    },
    scrollY: 0, innerHeight: 900,
    getComputedStyle: () => ({ scrollPaddingTop: '76px' }),
    addEventListener: (name, callback) => { events[name] = callback },
    requestAnimationFrame: callback => frames.push(callback),
  }
  runInNewContext(script, context)
  const update = (event = 'scroll') => { events[event](); frames.splice(0).forEach(callback => callback()) }
  const active = () => [...links, ...intro].filter(link => link.current === 'location').map(link => `${intro.includes(link) ? 'intro' : 'menu'}${link.hash}`)
  return { state, targets, links, intro, menu, label, context, update, active }
}

test('only the header menu marks the section at the anchor landing line below the sticky header', () => {
  const nav = navigation()
  assert.deepEqual(nav.active(), [])
  // Still below the scroll padding (76px + 24px).
  nav.state.tops = [120, 700, 1300]
  nav.update()
  assert.deepEqual(nav.active(), [])
  // A clicked anchor lands at the scroll padding.
  nav.state.tops = [-600, 76, 600]
  nav.update('resize')
  assert.deepEqual(nav.active(), ['menu#middle'])
  // Moving on leaves exactly one marked link.
  nav.state.tops = [-1400, -500, 50]
  nav.update()
  assert.deepEqual(nav.active(), ['menu#last'])
  // Back in the introduction: nothing is current, and Contents never is.
  nav.state.tops = [300, 900, 1500]
  nav.update()
  assert.deepEqual(nav.active(), [])
})

test('the closed menu names the current section using the same labels as its links', () => {
  const nav = navigation()
  nav.menu.open = false
  assert.equal(nav.label.textContent, '/ Contents')
  nav.state.tops = [-600, 76, 600]
  nav.update()
  assert.equal(nav.label.textContent, '/ Section middle')
  assert.equal(nav.label.title, '/ Section middle')
  nav.state.tops = [300, 900, 1500]
  nav.update()
  assert.equal(nav.label.textContent, '/ Contents')
})

test('the short final section becomes current at the page bottom', () => {
  const nav = navigation()
  nav.state.tops = [-1400, -500, 500]
  nav.context.scrollY = 2100
  nav.update()
  assert.deepEqual(nav.active(), ['menu#last'])
})

test('choosing a section closes the menu and moves focus without replacing native anchor scrolling', () => {
  const nav = navigation()
  nav.links[2].click()
  assert.equal(nav.menu.open, false)
  assert.equal(nav.targets[2].tabIndex, -1)
  assert.equal(nav.state.focused, 'middle')
  nav.menu.open = true
  nav.links[0].click()
  assert.equal(nav.menu.open, false)
  assert.equal(nav.state.focused, 'contents')
  // The introduction's links keep native behavior: no handlers.
  assert.ok(nav.intro.every(link => !link.click))
})

test('tabbing out of the menu closes it; moving within it or losing window focus does not', () => {
  const nav = navigation()
  nav.menu.focusout({ relatedTarget: nav.links[1] })
  assert.equal(nav.menu.open, true)
  nav.menu.focusout({ relatedTarget: null })
  assert.equal(nav.menu.open, true)
  nav.menu.focusout({ relatedTarget: {} })
  assert.equal(nav.menu.open, false)
})
