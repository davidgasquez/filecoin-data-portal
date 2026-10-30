// Server-side HTML atoms for /foc. Pure functions over exporter JSON; client.ts only enhances.
import { chart } from '../charts.mjs'
import { GENESIS, format, number, plural, shiftDate } from '../metrics.mjs'
import { labels as labelData, routes, coverage } from './data'

export type Row = Record<string, any>
export const BLOCKSCOUT = 'https://filecoin.blockscout.com'
export const STABLE = new Set(['USDFC', 'USDC.axl'])
export const ZERO = '0x0000000000000000000000000000000000000000'
export const USDFC = '0x80b98d3aa09ffff255c3ba4a241111ff1262f045'

const labels = new Map<string, Row>((labelData?.labels ?? []).map((l: Row) => [l.address, l]))
const built = new Set(routes.map((r) => r.route ?? ''))
export const label = (a: string) => labels.get(a)?.label as string | undefined
// Link only to pages that were actually generated.
export const url = (route = '') => route ? `/foc/${route}` : '/foc'
const routeUrl = (route: string) => built.has(route) ? url(route) : null

// ---------------------------------------------------------------- format

export const esc = (s: unknown) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!)
export const NA = '<span class="null" title="Not observed">—</span>'
const nf = (o: Intl.NumberFormatOptions) => new Intl.NumberFormat('en-US', o)
const F = { int: nf({ maximumFractionDigits: 0 }), d2: nf({ minimumFractionDigits: 2, maximumFractionDigits: 2 }), s3: nf({ maximumSignificantDigits: 3 }) }
export const num = (v: unknown): number | null => number(v)
export const isNum = (v: unknown) => num(v) != null
export const sum = (rows: Row[], f: (r: Row) => unknown) => rows.reduce((a, r) => a + (num(f(r)) ?? 0), 0)
export const count = (v: unknown) => isNum(v) ? F.int.format(Number(v)) : NA
export { plural }
// A network or quality column exactly as /numbers and chart hover show it (unit and precision from the key).
// Headlines may summarize differently (totals, pooled windows); the caption says so.
export const metric = (v: unknown, key: string) => isNum(v) ? format(v, key) : NA
const amount = (a: number) => a >= 0.1 ? F.d2.format(a) : F.s3.format(a)
export function usd(v: unknown) {
  if (!isNum(v)) return NA
  const n = Number(v), a = Math.abs(n), s = n < 0 ? '-' : ''
  if (a === 0) return '$0'
  return a < 0.0001 ? `${s}&lt;$0.0001` : `${s}$${amount(a)}`
}
// Stablecoins at face value; every other token keeps its native unit.
export function amt(v: unknown, sym?: string | null) {
  if (sym && STABLE.has(sym)) return usd(v)
  if (!isNum(v)) return NA
  const n = Number(v)
  return `${n < 0 ? '-' : ''}${n === 0 ? '0' : amount(Math.abs(n))} <span class="unit">${sym && sym !== 'Unknown' ? esc(sym) : 'unknown token'}</span>`
}
export const zeroMuted = (v: unknown, html: string) => num(v) === 0 ? `<span class="null">${html}</span>` : html
export const pct = (v: unknown, d = 1) => isNum(v) ? `${(Number(v) * 100).toFixed(d)}%` : NA
export function bytes(v: unknown) {
  if (!isNum(v)) return NA
  let n = Number(v), i = 0
  const u = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++ }
  return `${F.d2.format(n).replace(/\.00$/, '')} ${u[i]}`
}
const iso = (ts: number) => new Date(ts * 1000).toISOString()
export const date = (ts: unknown) => isNum(ts) ? `<time datetime="${iso(Number(ts))}" title="${iso(Number(ts)).slice(0, 16).replace('T', ' ')} UTC">${iso(Number(ts)).slice(0, 10)}</time>` : NA
export const day = (ts: unknown) => isNum(ts) ? iso(Number(ts)).slice(0, 10) : NA
export const dateTime = (ts: unknown) => isNum(ts) ? `<time datetime="${iso(Number(ts))}">${iso(Number(ts)).slice(0, 16).replace('T', ' ')}</time>` : NA
export const epochTs = (e: unknown) => GENESIS + Number(e) * 30
export const days = (epochs: unknown) => isNum(epochs) ? `${F.s3.format(Number(epochs) / 2880)} days` : NA
export const short = (a: string) => a ? `${a.slice(0, 6)}…${a.slice(-4)}` : ''
export const pname = (n?: string) => n && n.length > 32 ? `${n.slice(0, 14)}…${n.slice(-4)}` : n || ''
export const lastVal = (arr: unknown[] = []): [number | null, number] => {
  for (let i = arr.length - 1; i >= 0; i--) if (isNum(arr[i])) return [Number(arr[i]), i]
  return [null, -1]
}
export const isStable = (r: Row) => r.stable ?? STABLE.has(r.token_symbol)

// ---------------------------------------------------------------- atoms

export const copy = (text: string, what = 'address') => `<button class="button foc-copy" type="button" data-copy="${esc(text)}" aria-label="Copy ${esc(what)}" hidden>Copy</button>`
export const ext = (href: string, text = 'Blockscout') => `<a class="foc-ext" href="${esc(href)}" rel="noopener">${esc(text)} ↗</a>`
export const blockscout = (a: string) => ext(`${BLOCKSCOUT}/address/${a}`)
export const txLink = (tx?: string, text?: string) => tx ? `<a class="mono" href="${BLOCKSCOUT}/tx/${esc(tx)}" title="${esc(tx)}" rel="noopener">${esc(text ?? short(tx))}</a>` : NA
export const tag = (text: string) => `<span class="tag">${esc(text)}</span>`
const link = (href: string | null, html: string, title?: string, cls = '') => href ? `<a${cls ? ` class="${cls}"` : ''} href="${href}" data-astro-prefetch="hover"${title ? ` title="${esc(title)}"` : ''}>${html}</a>` : cls || title ? `<span${cls ? ` class="${cls}"` : ''}${title ? ` title="${esc(title)}"` : ''}>${html}</span>` : html
export const safeUrl = (u?: string) => /^https?:\/\//i.test(u || '') ? u! : null

// An address with its known label, linking to the most specific generated page.
export function addr(a?: string | null, { full = false, self = false } = {}) {
  if (!a) return NA
  if (a === ZERO) return '<span class="mono null">0x0 (none)</span>'
  const l = labels.get(a)
  const provider = l?.kind === 'provider' && !full && !self ? routeUrl(`provider/${l.id}`) : null
  const text = full ? esc(a) : l && !self ? esc(pname(l.label)) : short(a)
  return link(provider ?? routeUrl(`address/${a}`), text, a, full || !l || self ? 'mono' : '')
}
export const dsLink = (id: unknown) => id == null ? NA : link(routeUrl(`dataset/${id}`), `#${id}`)
export const railLink = (id: unknown) => id == null ? NA : link(routeUrl(`rail/${id}`), `#${id}`)
export const provLink = (id: unknown, name?: string) => id == null ? NA : link(routeUrl(`provider/${id}`), esc(pname(name) || `Provider #${id}`), name)

const status = (kind: string, text: string) => `<span class="st st-${kind}">${esc(text)}</span>`
const DS = { live: ['on', 'Live'], pending: ['open', 'Pending'], terminated: ['off', 'Terminated'], deleted: ['off', 'Deleted'] } as Record<string, string[]>
const RAIL = { active: ['on', 'Active'], terminated: ['off', 'Terminated'], finalized: ['off', 'Finalized'] } as Record<string, string[]>
export const dsStatus = (s?: string) => status(...((DS[s!] ?? ['off', s || 'Unknown']) as [string, string]))
export const railState = (s?: string) => status(...((RAIL[s!] ?? ['off', s || 'Unknown']) as [string, string]))
export const provState = (p: Row) => p.removed ? 'removed' : p.approved ? 'approved' : p.active ? 'registered' : 'inactive'
export const provStatus = (p: Row) => status(...(({ removed: ['off', 'Removed'], approved: ['on', 'Approved'], registered: ['open', 'Registered'], inactive: ['off', 'Inactive'] } as Record<string, [string, string]>)[provState(p)]))
export const flag = (on: unknown, yes: string, no: string) => status(on ? 'on' : 'off', on ? yes : no)

// ---------------------------------------------------------------- layout blocks

let ids = 0
export const resetIds = () => { ids = 0 }
export const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
export function head({ crumbs = [], title, lede, meta = [] }: { crumbs?: [string, string?][]; title: string; lede?: string; meta?: (string | false | null | undefined)[] }) {
  return `<header class="page-head foc-head">
    ${crumbs.length ? `<nav class="crumbs meta" aria-label="Breadcrumb">${crumbs.map(([text, href]) => href ? `<a href="${href}">${esc(text)}</a>` : `<span aria-current="page">${esc(text)}</span>`).join(' / ')}</nav>` : ''}
    <h1>${title}</h1>
    ${lede ? `<p>${lede}</p>` : ''}
    ${meta.filter(Boolean).length ? `<div class="foc-meta">${meta.filter(Boolean).map((m) => `<span>${m}</span>`).join('')}</div>` : ''}
  </header>`
}
export function section(title: string, body: string, { sub = '', more = '', id = slug(title) } = {}) {
  return `<section class="foc-section" id="${id}" aria-labelledby="${id}-title">
    <div class="foc-sh"><h2 id="${id}-title">${title}</h2>${more}</div>
    ${sub ? `<p class="foc-sub">${sub}</p>` : ''}${body}</section>`
}
export const more = (href: string, text: string) => `<a class="foc-more" href="${href}">${esc(text)} →</a>`
type Figure = [string, string, string?] | false | null | undefined | 0
export const figures = (items: Figure[]) => `<dl class="foc-figures">${items.filter((x): x is [string, string, string?] => !!x).map(([l, v, s]) => `<div><dt>${esc(l)}</dt><dd>${v}${s ? `<span class="meta">${s}</span>` : ''}</dd></div>`).join('')}</dl>`
export const kv = (items: ([string, string | null | undefined] | false | null | undefined)[]) => `<dl class="facts wide foc-kv">${items.filter((x): x is [string, string] => !!x).map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${v ?? NA}</dd></div>`).join('')}</dl>`
export const empty = (text: string) => `<p class="foc-empty">${esc(text)}</p>`
export function sources(ids: string[], note = '') {
  const names: Record<string, string> = { daily_network_metrics: 'network', daily_provider_quality: 'quality', daily_operator_metrics: 'operators' }
  const windows = ids.map(id => ({ id, row: coverage.find((r: Row) => r.source === (names[id] ?? id)) })).filter(({ row }) => row)
  const detail = windows.length ? `<details><summary>Observation windows</summary><dl class="facts wide foc-kv">${windows.map(({ id, row }) => `<div><dt>${id}</dt><dd>${row.observed_at ? `API snapshot ${esc(row.observed_at.replace('T', ' ').replace('Z', ' UTC'))}` : `${row.start ?? 'Unknown'} to ${row.end ?? 'unknown'} (UTC)`}</dd></div>`).join('')}</dl>${ids.includes('rails') ? '<p>State, rates, lockups and settlement counters are API snapshots. Paid totals and charts use event history and can differ. Monthly rates mean 30 days and include terminated rails still streaming at the snapshot.</p>' : ''}</details>` : ''
  return `<aside class="foc-sources meta" aria-label="Sources">Sources: ${ids.map((id) => `<a href="/datasets/${id}">${id}</a>`).join(' · ')}.${note ? ` ${note}` : ''}${detail}</aside>`
}

// ---------------------------------------------------------------- charts

// Contiguous daily points through the last observation, at least `minDays` long so short histories
// keep a readable scale. Absent days stay null (gaps), never zero.
export function points(dates?: string[] | null, values?: unknown[] | null, minDays = 30) {
  if (!dates?.length) return []
  const byDate = new Map(dates.map((d, i) => [d, num(values?.[i])]))
  const out: { date: string; value: number | null }[] = []
  const end = dates.findLast((_, i) => num(values?.[i]) != null)
  if (!end) return []
  const start = [dates[0], shiftDate(end, 1 - minDays)].sort()[0]
  for (let d = start; d <= end; d = shiftDate(d, 1)) out.push({ date: d, value: byDate.get(d) ?? null })
  return out
}
// key selects units in metrics.mjs (…_usd → $, …_bytes → TiB, provider_…_rate → %, …_fil → FIL).
// Definitions and sources live in the title disclosure, as on /numbers.
export function plot({ title, value, key, kind, pts, note = '', cls = '', info = '', source = '', column = '' }: { title: string; value: string; key: string; kind: 'bar' | 'line' | 'step'; pts: { date: string; value: number | null }[]; note?: string; cls?: string; info?: string; source?: string; column?: string }) {
  const latest = pts.findLast((p) => p.value != null)?.date
  const heading = info || source ? `<details class="metric-info"><summary><h3>${esc(title)}</h3><span class="meta">Info</span></summary><div class="metric-info-body">${info ? `<p>${info}</p>` : ''}<p class="meta">Latest observation: ${latest ?? 'not observed'} (UTC).</p>${source ? `<p class="meta">Source: <a href="/datasets/${source}${column ? `#${column}` : ''}">${source}</a>${column ? ` · ${column}` : ''}</p>` : ''}</div></details>` : `<h3>${esc(title)}</h3>`
  return `<figure class="chart foc-chart ${cls}">
    <div class="chart-heading">${heading}<span class="chart-value">${value}</span></div>
    ${chart(pts, key, kind, { label: title, interactive: true })}
    ${note ? `<figcaption class="meta">${note}</figcaption>` : ''}
  </figure>`
}

// ---------------------------------------------------------------- tables

export type Col = { key?: string; label: string; num?: boolean; html: (r: Row) => string; sort?: (r: Row) => unknown; wrap?: boolean }
export type TableOptions = {
  caption: string; rows: Row[]; cols: (Col | false | null | undefined)[]
  prefix?: string; page?: number; empty?: string; href?: (r: Row) => string | null
  sort?: [string, 'asc' | 'desc']; search?: true | ((r: Row) => string); searchLabel?: string
  filter?: { label: string; get: (r: Row) => string; options: [string, string][] }
}
const strip = (html: string) => html.replace(/<[^>]*>/g, '').trim().toLowerCase()
// Mirrors client.ts: numeric cells fall back to their text without #, $ and grouping commas.
export const plainNumber = (text: string) => text.trim().replace(/^[#$]/, '').replaceAll(',', '')
export function compare(a: unknown, b: unknown) {
  if (a == null || a === '') return b == null || b === '' ? 0 : 1
  if (b == null || b === '') return -1
  return typeof a === 'number' && typeof b === 'number' ? a - b : String(a).localeCompare(String(b), 'en', { numeric: true })
}
// Static, complete HTML table. Without JavaScript every row is present; client.ts adds
// sorting, filtering, search, show-more and URL state.
export function table(o: TableOptions) {
  const cols = o.cols.filter((c): c is Col => !!c).map((c) => ({ ...c, key: c.key ?? slug(c.label) }))
  const id = `t${++ids}`
  let rows = o.rows
  const sortCol = o.sort && cols.find((c) => c.key === o.sort![0] && c.sort)
  if (sortCol) {
    const dir = o.sort![1] === 'asc' ? 1 : -1
    rows = rows.map((r, i) => [r, sortCol.sort!(r), i] as const).sort((a, b) => {
      const empty = (v: unknown) => v == null || v === ''
      return empty(a[1]) || empty(b[1]) ? compare(a[1], b[1]) || a[2] - b[2] : compare(a[1], b[1]) * dir || a[2] - b[2]
    }).map(([r]) => r)
  }
  const tools = (o.search || o.filter) && o.rows.length > 8
  const counts = o.filter ? new Map(o.filter.options.map(([k]) => [k, k === 'all' ? o.rows.length : o.rows.filter((r) => o.filter!.get(r) === k).length])) : null
  const control = (name: string) => o.prefix ? `${o.prefix}.${name}` : name
  const toolbar = tools ? `<div class="foc-tools" hidden>
      ${o.search ? `<label class="foc-filter"><span class="meta">${esc(o.searchLabel ?? 'Filter rows')}</span><input type="search" name="${control('q')}" autocomplete="off" spellcheck="false" data-q /></label>` : ''}
      ${o.filter ? `<fieldset class="foc-seg"><legend class="meta">${esc(o.filter.label)}</legend>${o.filter.options.filter(([k]) => k === 'all' || counts!.get(k)).map(([k, l], i) => `<label><input type="radio" name="${control('f')}-${id}" value="${k}"${i ? '' : ' checked'} data-f /><span>${esc(l)} <span class="meta">${count(counts!.get(k))}</span></span></label>`).join('')}</fieldset>` : ''}
      <p class="meta foc-count" role="status" data-count></p>
    </div>` : ''
  const th = cols.map((c) => `<th scope="col"${c.num ? ' class="numeric"' : ''}${c.sort ? ` data-sort="${c.key}"` : ''}${sortCol === c ? ` aria-sort="${o.sort![1] === 'asc' ? 'ascending' : 'descending'}"` : ''}>${esc(c.label)}</th>`).join('')
  const body = rows.length ? rows.map((r) => {
    const cells = cols.map((c) => {
      const html = c.html(r), cls = [c.num && 'n', c.wrap && 'wrap'].filter(Boolean).join(' ')
      // Sort keys only where the visible text is not already the key (client falls back to text).
      const v = c.sort?.(r), key = typeof v === 'number' ? String(v) : String(v ?? '')
      const same = c.num ? key !== '' && Number(plainNumber(strip(html))) === Number(key) : key.toLowerCase() === strip(html)
      return `<td${cls ? ` class="${cls}"` : ''}${c.sort && !same ? ` data-v="${esc(key)}"` : ''}>${html}</td>`
    }).join('')
    // Rows open their page; data-href only when it differs from the row's first link.
    const href = o.href?.(r), first = /<a[^>]* href="([^"]*)"/.exec(cells)?.[1]
    const q = typeof o.search === 'function' ? o.search(r).toLowerCase() : ''
    return `<tr${href && href !== first ? ` data-href="${href}"` : ''}${o.filter ? ` data-f="${esc(o.filter.get(r))}"` : ''}${q ? ` data-q="${esc(q)}"` : ''}>${cells}</tr>`
  }).join('') : `<tr><td colspan="${cols.length}" class="null">${esc(o.empty ?? 'No rows')}</td></tr>`
  return `<div class="foc-table" data-table${o.href ? ' data-go' : ''} data-prefix="${esc(o.prefix ?? '')}" data-page="${o.page ?? 50}"${o.sort ? ` data-default="${o.sort[1] === 'asc' ? '' : '-'}${o.sort[0]}"` : ''}>
    ${toolbar}
    <div class="table-scroll" tabindex="0" role="region" aria-label="${esc(o.caption)}"><table><caption class="sr">${esc(o.caption)}</caption><thead><tr>${th}</tr></thead><tbody>${body}</tbody></table></div>
    <p class="foc-empty" data-none hidden>No rows match. <button class="button" type="button" data-reset>Clear filters</button></p>
    <div class="foc-pager" hidden><button class="button" type="button" data-more></button><button class="button" type="button" data-all>Show all</button></div>
  </div>`
}

// ---------------------------------------------------------------- shared tables

export const col = {
  addr: (labelText: string, k: string): Col => ({ label: labelText, html: (r) => addr(r[k]), sort: (r) => r[k] ? pname(label(r[k])) || short(r[k]) : null }),
  created: (k = 'created_at', labelText = 'Created'): Col => ({ key: 'created', label: labelText, html: (r) => day(r[k]), sort: (r) => isNum(r[k]) ? day(r[k]) : null }),
  provider: (): Col => ({ label: 'Provider', html: (r) => provLink(r.provider_id, r.provider), sort: (r) => r.provider?.toLowerCase() }),
}
export const DS_FILTER = { label: 'Status', get: (r: Row) => r.status, options: [['all', 'All'], ['live', 'Live'], ['pending', 'Pending'], ['terminated', 'Terminated'], ['deleted', 'Deleted']] as [string, string][] }
export const RAIL_FILTER = { label: 'State', get: (r: Row) => r.state, options: [['all', 'All'], ['active', 'Active'], ['terminated', 'Terminated'], ['finalized', 'Finalized']] as [string, string][] }

export function dsTable(rows: Row[], { provider = true, owner = true, prefix = 'ds', page = 25, caption = 'Data sets' } = {}) {
  return table({
    caption, rows, prefix, page, href: (r) => routeUrl(`dataset/${r.id}`),
    filter: DS_FILTER, sort: ['data-set', 'desc'],
    search: true, searchLabel: 'Filter by id, provider, client or source',
    cols: [
      { key: 'data-set', label: 'Data set', num: true, html: (r) => dsLink(r.id), sort: (r) => r.id },
      { label: 'Status', html: (r) => dsStatus(r.status), sort: (r) => r.status },
      provider && col.provider(),
      owner && col.addr('Client', 'owner'),
      { label: 'Source', html: (r) => r.source ? esc(r.source) : NA, sort: (r) => r.source },
      { label: 'Add-ons', html: (r) => [r.cdn && 'CDN', r.ipfs && 'IPFS'].filter(Boolean).map((x) => tag(x as string)).join(' ') || NA },
      { key: 'rate', label: 'Rate / month', num: true, html: (r) => zeroMuted(r.rate_month, usd(r.rate_month)), sort: (r) => num(r.rate_month) },
      { key: 'paid', label: 'Paid', num: true, html: (r) => zeroMuted(r.paid, usd(r.paid)), sort: (r) => num(r.paid) },
      col.created(),
    ],
  })
}
export function railTable(rows: Row[], { hide = [] as string[], prefix = 'rails', page = 25, caption = 'Rails' } = {}) {
  return table({
    caption, rows, prefix, page, href: (r) => routeUrl(`rail/${r.id}`),
    filter: RAIL_FILTER, sort: ['rail', 'desc'],
    search: (r) => r.token_symbol ?? '', searchLabel: 'Filter by id, address, service or token',
    cols: [
      { key: 'rail', label: 'Rail', num: true, html: (r) => railLink(r.id), sort: (r) => r.id },
      { label: 'State', html: (r) => railState(r.state), sort: (r) => r.state },
      { label: 'Service', html: (r) => esc(r.service) + (r.dealbot ? ` ${tag('Dealbot')}` : ''), sort: (r) => r.service },
      !hide.includes('payer') && col.addr('Payer', 'payer'),
      !hide.includes('payee') && col.addr('Payee', 'payee'),
      { key: 'data-set', label: 'Data set', num: true, html: (r) => dsLink(r.data_set_id), sort: (r) => r.data_set_id },
      { key: 'rate', label: 'Rate / month', num: true, html: (r) => zeroMuted(r.rate_month, amt(r.rate_month, r.token_symbol)), sort: (r) => num(r.rate_month) },
      { key: 'paid', label: 'Paid', num: true, html: (r) => zeroMuted(r.paid, amt(r.paid, r.token_symbol)), sort: (r) => num(r.paid) },
      { key: 'payments', label: 'Payments', num: true, html: (r) => count(r.events), sort: (r) => num(r.events) },
      col.created(),
    ],
  })
}
export function payTable(rows: Row[], { hide = [] as string[], prefix = 'pay', caption = 'Latest payments' } = {}) {
  return table({
    caption, rows, prefix, page: 10, empty: 'No payments recorded',
    cols: [
      { label: 'Time (UTC)', html: (r) => dateTime(r.ts) },
      { label: 'Kind', html: (r) => r.kind === 'settled' ? 'Settlement' : 'One-time' },
      !hide.includes('rail') && { label: 'Rail', num: true, html: (r) => railLink(r.rail_id) },
      !hide.includes('payer') && { label: 'From', html: (r) => addr(r.payer) },
      !hide.includes('payee') && { label: 'To', html: (r) => addr(r.payee) },
      { label: 'Amount', num: true, html: (r) => amt(r.gross, r.token) },
      { label: 'Network fee', num: true, html: (r) => amt(r.fee, r.token) },
      { label: 'Tx', html: (r) => txLink(r.tx) },
    ],
  })
}
// Daily payment flow (bars) and the latest events. `key` sets units: stablecoin totals use …_usd.
export function paySection(daily: Row | null | undefined, latest: Row[] | null | undefined, { title = 'Payments', hide = [] as string[], key = 'payments_usd', unit = 'stablecoin', sub = '', id = slug(title) } = {}) {
  const pts = points(daily?.d, daily?.v)
  const total = (daily?.v ?? []).reduce((a: number, v: unknown) => a + (num(v) ?? 0), 0)
  const events = (daily?.n ?? []).reduce((a: number, v: unknown) => a + (num(v) ?? 0), 0)
  const known = (daily?.v ?? []).some(isNum)
  // Headline is the window total, at the chart's own precision; native tokens keep their unit.
  const fmt = !known ? NA : key.endsWith('_usd') ? metric(total, key) : amt(total, unit)
  const summary = sub || (events ? `${plural(events, 'payment event')} totalling ${fmt}, ${daily!.d[0]} to ${daily!.d.at(-1)} (UTC). ${unit === 'stablecoin' ? 'Stablecoins only, at face value. ' : ''}Days without events are gaps.` : 'No payment events recorded.')
  const chartHtml = pts.length ? plot({ title: `Daily ${title.toLowerCase()}`, value: fmt, key, kind: 'bar', pts }) : ''
  const list = latest?.length ? `<h3 class="foc-h3">Latest ${plural(latest.length, 'event')}</h3>${payTable(latest, { hide, prefix: `${id}-pay` })}` : ''
  return section(title, `${chartHtml}${list}`, { sub: summary, id })
}
