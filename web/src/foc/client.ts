// Progressive enhancement for /foc: table sort, filter, search, show-more and URL state,
// row navigation, and the explorer search box. Every page is complete without it.
import '../hover'
import labelFile from '../../.foc/data/labels.json'
import lookup from '../../.foc/data/lookup.json'

const foc = document.querySelector<HTMLElement>('.foc')!
foc.classList.add('js')

// ---------------------------------------------------------------- tables

type Item = { tr: HTMLTableRowElement; i: number; f: string; q: string; cells: HTMLTableCellElement[] }
type Table = {
  root: HTMLElement; prefix: string; page: number; shown: number; def: string
  items: Item[]; tbody: HTMLTableSectionElement; ths: HTMLTableCellElement[]
  input?: HTMLInputElement | null; radios: HTMLInputElement[]; q: string; f: string; sort: string
}
const tables: Table[] = []
const num = new Intl.NumberFormat('en-US')
const param = (t: Table, k: string) => t.prefix ? `${t.prefix}.${k}` : k
const empty = (v?: string) => v == null || v === ''
// Mirrors ui.ts: without data-v the key is the text (numbers without #, $ and grouping commas).
const cellKey = (cell: HTMLTableCellElement | undefined, numeric: boolean) => {
  const text = cell?.dataset.v ?? cell?.textContent?.trim()
  return numeric && cell?.dataset.v == null ? text?.replace(/^[#$]/, '').replaceAll(',', '') : text
}

function compare(a?: string, b?: string, numeric = false) {
  if (empty(a)) return empty(b) ? 0 : 1
  if (empty(b)) return -1
  return numeric ? Number(a) - Number(b) : a!.localeCompare(b!, 'en', { numeric: true })
}

function apply(t: Table) {
  const terms = t.q.toLowerCase().split(/\s+/).filter(Boolean)
  const key = t.sort.replace(/^-/, ''), dir = t.sort.startsWith('-') ? -1 : 1
  const c = t.ths.findIndex((th) => th.dataset.sort === key)
  const numeric = t.ths[c]?.classList.contains('numeric')
  const order = c < 0 ? t.items : [...t.items].sort((a, b) => {
    const x = cellKey(a.cells[c], numeric), y = cellKey(b.cells[c], numeric)
    return (empty(x) || empty(y) ? compare(x, y) : compare(x, y, numeric) * dir) || a.i - b.i
  })
  t.ths.forEach((th, i) => i === c ? th.setAttribute('aria-sort', dir < 0 ? 'descending' : 'ascending') : th.removeAttribute('aria-sort'))
  let matched = 0
  for (const item of order) {
    const hit = (t.f === 'all' || item.f === t.f) && terms.every((term) => item.q.includes(term))
    item.tr.hidden = !hit || matched >= t.shown
    if (hit) matched++
    t.tbody.append(item.tr)
  }
  const visible = Math.min(matched, t.shown), left = matched - visible
  const status = t.root.querySelector('[data-count]')
  if (status) status.textContent = `${visible < matched ? `Showing ${num.format(visible)} of ` : ""}${num.format(matched)} ${matched === t.items.length ? "rows" : `matching rows (${num.format(t.items.length)} total)`}`
  t.root.querySelector<HTMLElement>('[data-none]')!.hidden = matched > 0 || !t.items.length
  const pager = t.root.querySelector<HTMLElement>('.foc-pager')!
  pager.hidden = left <= 0
  pager.querySelector('[data-more]')!.textContent = `Show ${num.format(Math.min(left, t.page * 2))} more`
  pager.querySelector('[data-all]')!.textContent = `Show all ${num.format(matched)}`
}

function read(t: Table) {
  const params = new URLSearchParams(location.search)
  t.q = params.get(param(t, 'q')) ?? ''
  t.f = params.get(param(t, 'f')) ?? 'all'
  if (!t.radios.some((r) => r.value === t.f)) t.f = 'all'
  t.sort = params.get(param(t, 'sort')) ?? t.def
  if (t.input) t.input.value = t.q
  for (const r of t.radios) r.checked = r.value === t.f
  t.shown = t.page
  apply(t)
}

// Filters and sorting are history entries (Back undoes them); typing replaces the current one.
function write(push: boolean) {
  const u = new URL(location.href)
  for (const t of tables) {
    const set = (k: string, v: string, def: string) => v && v !== def ? u.searchParams.set(param(t, k), v) : u.searchParams.delete(param(t, k))
    set('q', t.q.trim(), ''); set('f', t.f, 'all'); set('sort', t.sort, t.def)
  }
  if (u.href !== location.href) history[push ? 'pushState' : 'replaceState'](null, '', u)
}

for (const root of document.querySelectorAll<HTMLElement>('[data-table]')) {
  const tbody = root.querySelector('tbody')!
  const items = [...tbody.rows].filter((tr) => !tr.querySelector('td[colspan]')).map((tr, i) => ({
    tr, i, f: tr.dataset.f ?? '', q: `${tr.textContent} ${[...tr.querySelectorAll<HTMLElement>("[title]")].map((e) => e.title).join(" ")} ${tr.dataset.q ?? ""}`.toLowerCase(), cells: [...tr.cells],
  }))
  const t: Table = {
    root, tbody, items, prefix: root.dataset.prefix ?? '', page: Number(root.dataset.page) || 50, shown: 0, def: root.dataset.default ?? '',
    ths: [...root.querySelectorAll<HTMLTableCellElement>('thead th')], input: root.querySelector<HTMLInputElement>('input[data-q]'),
    radios: [...root.querySelectorAll<HTMLInputElement>('input[data-f]')], q: '', f: 'all', sort: '',
  }
  tables.push(t)
  const tools = root.querySelector<HTMLElement>('.foc-tools')
  if (tools) tools.hidden = false
  for (const th of t.ths) {
    if (!th.dataset.sort || items.length < 2) continue
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'foc-sort'
    button.textContent = th.textContent
    th.replaceChildren(button)
    button.addEventListener('click', () => {
      const key = th.dataset.sort!
      t.sort = t.sort.replace(/^-/, '') === key ? (t.sort.startsWith('-') ? key : `-${key}`) : th.classList.contains('numeric') ? `-${key}` : key
      t.shown = t.page; apply(t); write(true)
    })
  }
  t.input?.addEventListener('input', () => { t.q = t.input!.value; t.shown = t.page; apply(t); write(false) })
  t.input?.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || !t.input!.value) return
    e.preventDefault(); t.input!.value = ''; t.q = ''; apply(t); write(false)
  })
  for (const r of t.radios) r.addEventListener('change', () => { t.f = r.value; t.shown = t.page; apply(t); write(true) })
  root.querySelector('[data-more]')!.addEventListener('click', () => { t.shown += t.page * 2; apply(t) })
  root.querySelector('[data-all]')!.addEventListener('click', () => { t.shown = Infinity; apply(t) })
  root.querySelector('[data-reset]')!.addEventListener('click', () => {
    t.q = ''; t.f = 'all'; if (t.input) t.input.value = ''
    for (const r of t.radios) r.checked = r.value === 'all'
    apply(t); write(true); (t.input ?? t.radios[0])?.focus()
  })
  // Whole rows open their page; links, buttons and text selection keep their own behaviour.
  if ('go' in root.dataset) tbody.addEventListener('click', (e) => {
    const tr = (e.target as Element).closest('tr')
    const href = tr?.dataset.href ?? tr?.querySelector('a')?.getAttribute('href')
    if (!href || (e.target as Element).closest('a, button, input, label') || getSelection()?.toString()) return
    if (e.metaKey || e.ctrlKey) open(href, '_blank')
    else location.href = href
  })
  read(t)
}
addEventListener('popstate', () => tables.forEach(read))

// ---------------------------------------------------------------- explorer search

type Label = { address: string; label: string; kind: string; id: number }
type Option = { href: string; text: string; kind: string; external?: boolean }
const all = (labelFile as { labels: Label[] }).labels
const providers = lookup.providers as Label[]
const datasetIds = new Set(lookup.datasets.map(String)), railIds = new Set(lookup.rails.map(String))
const addresses = new Set(lookup.addresses)
const form = document.querySelector<HTMLFormElement>('.foc-search')!
const q = form.querySelector('input')!
const list = form.querySelector<HTMLElement>('[role="listbox"]')!
const noResults = form.querySelector<HTMLElement>('[role="status"]')!
let options: Option[] = [], sel = 0
form.hidden = false
const short = (a: string) => `${a.slice(0, 6)}…${a.slice(-4)}`

function search() {
  const v = q.value.trim().replace(/^#/, '').toLowerCase()
  options = []
  if (/^\d+$/.test(v)) {
    const id = BigInt(v).toString(), p = providers.find((x) => String(x.id) === id)
    if (datasetIds.has(id)) options.push({ href: `/foc/dataset/${id}`, text: `Data set #${id}`, kind: 'Data set' })
    if (railIds.has(id)) options.push({ href: `/foc/rail/${id}`, text: `Rail #${id}`, kind: 'Rail' })
    if (p) options.push({ href: `/foc/provider/${id}`, text: p.label, kind: `Provider #${id}` })
  } else if (/^0x[0-9a-f]{40}$/.test(v)) {
    const l = all.find((x) => x.address === v)
    if (l?.kind === 'provider') options.push({ href: `/foc/provider/${l.id}`, text: l.label, kind: `Provider #${l.id}` })
    if (addresses.has(v)) options.push({ href: `/foc/address/${v}`, text: l?.label ?? short(v), kind: 'Address' })
    else options.push({ href: `https://filecoin.blockscout.com/address/${v}`, text: short(v), kind: 'Not in snapshot · Blockscout ↗', external: true })
  } else if (/^0x[0-9a-f]{64}$/.test(v)) {
    options.push({ href: `https://filecoin.blockscout.com/tx/${v}`, text: short(v), kind: 'Transaction on Blockscout ↗', external: true })
  } else if (v) {
    for (const p of providers) if (p.label.toLowerCase().includes(v) || p.address.startsWith(v)) options.push({ href: `/foc/provider/${p.id}`, text: p.label, kind: `Provider #${p.id}` })
    for (const l of all) if (l.kind !== 'provider' && (l.label.toLowerCase().includes(v) || l.address.startsWith(v))) options.push({ href: `/foc/address/${l.address}`, text: `${l.label} ${short(l.address)}`, kind: l.kind })
    options = options.slice(0, 10)
  }
  sel = 0
  draw()
}
function draw() {
  const open = q.value.trim().length > 0 && options.length > 0
  list.hidden = !open
  noResults.hidden = !q.value.trim() || options.length > 0
  noResults.textContent = noResults.hidden ? '' : 'No matches. Try a provider name, a data set or rail id, or a full 0x address.'
  q.setAttribute('aria-expanded', String(open))
  list.replaceChildren(...options.map((o, i) => {
    const a = document.createElement('a')
    a.href = o.href; a.tabIndex = -1; a.id = `foc-option-${i}`; a.setAttribute('role', 'option'); a.setAttribute('aria-selected', String(i === sel))
    if (o.external) a.rel = 'noopener'
    a.append(Object.assign(document.createElement('span'), { textContent: o.text }), Object.assign(document.createElement('span'), { className: 'meta', textContent: o.kind }))
    a.addEventListener('mousedown', (e) => e.preventDefault()) // keep focus until click navigates
    return a
  }))
  if (options.length && open) q.setAttribute('aria-activedescendant', `foc-option-${sel}`)
  else q.removeAttribute('aria-activedescendant')
}
const close = () => { list.hidden = true; noResults.hidden = true; q.setAttribute('aria-expanded', 'false'); q.removeAttribute('aria-activedescendant') }
q.addEventListener('input', search)
q.addEventListener('focus', () => { if (q.value.trim()) search() })
q.addEventListener('blur', close)
q.addEventListener('keydown', (e) => {
  if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && options.length) {
    e.preventDefault()
    if (list.hidden) return search()
    sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length
    draw()
    document.getElementById(`foc-option-${sel}`)?.scrollIntoView({ block: 'nearest' })
  } else if (e.key === 'Escape') {
    e.preventDefault()
    if (!list.hidden || !noResults.hidden) close()
    else { q.value = ''; options = []; q.blur() }
  }
})
form.addEventListener('submit', (e) => {
  e.preventDefault()
  const o = options[sel]
  if (!o || !q.value.trim()) return
  location.href = o.href
})
document.addEventListener('keydown', (e) => {
  const typing = /^(input|textarea|select)$/i.test((e.target as Element).tagName)
  if ((e.key === '/' && !typing && !e.metaKey && !e.ctrlKey) || (e.key === 'k' && (e.metaKey || e.ctrlKey))) { e.preventDefault(); q.focus(); q.select() }
})
