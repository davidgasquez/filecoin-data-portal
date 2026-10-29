// One render function per /foc route kind. Each returns static HTML for the page body.
import { chart } from '../charts.mjs'
import { atto, shiftDate } from '../metrics.mjs'
import { readFoc, coverage as covered } from './data'
import {
  type Row, BLOCKSCOUT, ZERO, NA, esc, num, sum, count, plural, usd, amt, pct, bytes, ms, date, dateTime, epochTs, days, short, pname, lastVal, isStable,
  copy, ext, blockscout, txLink, tag, safeUrl, addr, dsLink, railLink, provLink, dsStatus, railState, provStatus, provState, flag, label,
  head, section, more, figures, kv, empty, sources, points, plot, table, dsTable, railTable, payTable, paySection, col, url, zeroMuted,
} from './ui'

export type Page = { title: string; description: string; html: string }
const optional = (file: string) => { try { return readFoc(file) } catch { return null } }
const coverage = (name: string): Row | undefined => (covered ?? []).find((c: Row) => c.source === name)
const quarterSpan = (end?: string) => end ? `${shiftDate(end, -29)} to ${end}` : 'the last 30 observed days'
const share = (a: number | null, b: number | null) => a != null && b ? ` (${(a / b * 100).toFixed(1)}%)` : ''

// ---------------------------------------------------------------- overview

export function overview(o: Row): Page {
  const s = o.series ?? {}, c: Row = (Array.isArray(o.counts) ? o.counts[0] : o.counts) ?? {}
  const dates: string[] = s.date ?? []
  const at = (k: string) => { const [v, i] = lastVal(s[k]); return { v, date: dates[i] } }
  const net = (k: string) => points(dates, s[k])
  const rr = at('run_rate')
  const before = rr.date ? num(s.run_rate?.[dates.indexOf(shiftDate(rr.date, -30))]) : null
  const delta = rr.v != null && before != null ? `${rr.v >= before ? '+' : '−'}${usd(Math.abs(rr.v - before))}${before ? ` (${rr.v >= before ? '+' : '−'}${Math.abs((rr.v - before) / before * 100).toFixed(1)}%)` : ''} since ${shiftDate(rr.date!, -30)}` : 'No 30-day comparison observed'
  const ops: Row[] = optional('operators.json') ?? []
  const top = [...ops].sort((a, b) => (num(b.run_rate) ?? 0) - (num(a.run_rate) ?? 0))[0]
  const dealbots = (optional('clients.json') ?? []).filter((r: Row) => r.dealbot).length
  const pay = coverage('payments'), lead = o.providers?.[0]
  const fact = (dt: string, dd: string, note = '') => `<div><dt>${dt}</dt><dd>${dd}${note ? `<span class="meta">${note.replace(/\d{4}-\d{2}-\d{2}/g, d => `<time datetime="${d}">${d}</time>`)}</span>` : ''}</dd></div>`
  const billing = at('billing_data_sets'), stored = at('stored_bytes'), payers = at('billing_payers'), rails = at('active_rails'), fee = at('fee_arr')
  const observations = [
    `${count(c.live_data_sets)} of ${count(c.data_sets)} storage data sets are live${share(num(c.live_data_sets), num(c.data_sets))}; ${count(c.approved)} of ${count(c.providers)} registered providers are approved for warm storage.`,
    top && top.run_rate != null && `Operator ${addr(top.address)} carries ${usd(top.run_rate)} of run rate${share(num(top.run_rate), rr.v)} across ${plural(num(top.active_rails) ?? 0, "active rail")}.`,
    lead && `${provLink(lead.id, lead.name)} stores the most live data sets: ${count(lead.live)}.`,
    dealbots && `${plural(dealbots, 'Dealbot wallet')} fund synthetic quality checks. Their rails are excluded from run rate.`,
    pay?.start && `Payment events observed ${pay.start} to ${pay.end} (UTC).`,
  ].filter(Boolean)

  const hero = `<section class="foc-hero" aria-labelledby="run-rate-title">
    <figure class="chart foc-hero-chart">
      <div class="foc-hero-lead">
        <details class="metric-info"><summary><h2 id="run-rate-title">Annualized Filecoin Pay run rate</h2><span class="meta">Info</span></summary>
          <div class="metric-info-body"><p>Gross stablecoin payment rate of active, recurring, eligible rails, annualized. Excludes Dealbot. Covers every operator, so it is payment volume, not storage-only revenue.</p><p class="meta">Source: <a href="/datasets/daily_network_metrics#filecoin_pay_gross_payment_volume_run_rate_usd">daily_network_metrics</a> · filecoin_pay_gross_payment_volume_run_rate_usd</p></div></details>
        <p class="foc-big">${usd(rr.v)}</p>
        <p class="meta">${rr.date ? `${rr.date} (UTC) · ${delta}` : 'Not observed'}</p>
      </div>
      ${chart(net('run_rate'), 'filecoin_pay_gross_payment_volume_run_rate_usd', 'line', { label: 'Annualized Filecoin Pay run rate', interactive: true })}
    </figure>
    <div class="foc-hero-side">
      <dl class="facts foc-facts">
        ${fact('Network fee ARR', usd(fee.v), fee.date && `Annualized Filecoin Pay fees · ${fee.date}`)}
        ${fact('Stablecoin paid', usd(c.paid_total), `All time · ${count(c.payments)} payment events, all tokens`)}
        ${fact('Billing data sets', count(billing.v), `${count(c.data_sets)} created · ${billing.date ?? 'not observed'}`)}
        ${fact('Billing clients', count(payers.v), `${count(c.payers)} payer addresses in total · ${payers.date ?? 'not observed'}`)}
        ${fact('Warm storage data (including copies)', bytes(stored.v), `Raw bytes, every copy · ${stored.date ?? 'not observed'}`)}
        ${fact('Active rails', count(rails.v), `${count(c.rails)} rails · ${count(c.operators)} operators · ${rails.date ?? 'not observed'}`)}
      </dl>
    </div>
  </section>`

  const grid = `<div class="chart-grid foc-grid">
    ${plot({ title: 'Paid through Filecoin Pay', value: usd(c.paid_total), key: 'filecoin_pay_paid_usd', kind: 'bar', pts: net('paid'), info: 'Daily gross stablecoin payments settled or paid one-time. Headline is the all-time stablecoin total.', source: 'daily_network_metrics', column: 'filecoin_pay_paid_usd' })}
    ${plot({ title: 'New billing data sets', value: count(at('new_data_sets').v), key: 'warm_storage_new_billing_data_sets', kind: 'bar', pts: net('new_data_sets'), info: 'Data sets whose billing started that day. Headline is the latest day.', source: 'daily_network_metrics', column: 'warm_storage_new_billing_data_sets' })}
    ${plot({ title: 'Billing data sets', value: count(billing.v), key: 'warm_storage_billing_data_sets', kind: 'step', pts: net('billing_data_sets'), info: 'Data sets billing at a positive PDP rail rate at the end of the day.', source: 'daily_network_metrics', column: 'warm_storage_billing_data_sets' })}
    ${plot({ title: 'Warm storage data (including copies)', value: bytes(stored.v), key: 'warm_storage_stored_bytes', kind: 'step', pts: net('stored_bytes'), info: 'Raw payload bytes across warm storage data sets, counting every stored copy, including non-billing copies.', source: 'daily_network_metrics', column: 'warm_storage_stored_bytes' })}
    ${plot({ title: 'Active payers', value: count(at('active_payers').v), key: 'filecoin_pay_active_payers', kind: 'step', pts: net('active_payers'), info: 'Payers with at least one unterminated rail at the end of the day, whether or not it is billing.', source: 'daily_network_metrics', column: 'filecoin_pay_active_payers' })}
    ${plot({ title: 'Active rails', value: count(rails.v), key: 'filecoin_pay_active_rails', kind: 'step', pts: net('active_rails'), info: 'Unterminated Filecoin Pay rails at the end of the day, whether or not they are billing.', source: 'daily_network_metrics', column: 'filecoin_pay_active_rails' })}
  </div>`

  const topProviders = table({
    caption: 'Top providers by live data sets', rows: o.providers ?? [], href: (r) => url(`provider/${r.id}`),
    cols: [
      { label: 'Provider', html: (r) => `${provLink(r.id, r.name)} <span class="meta">#${r.id}</span>` },
      { label: 'Country', html: (r) => r.country ? esc(r.country) : NA },
      { label: 'Live', num: true, html: (r) => count(r.live) },
      { label: 'Paid', num: true, html: (r) => zeroMuted(r.paid, usd(r.paid)) },
    ],
  })
  const latestSets = table({
    caption: 'Latest data sets', rows: o.data_sets ?? [], href: (r) => url(`dataset/${r.id}`),
    cols: [
      { label: 'Data set', num: true, html: (r) => dsLink(r.id) }, { label: 'Status', html: (r) => dsStatus(r.status) },
      col.provider(), col.addr('Client', 'owner'), col.created(),
    ],
  })
  return {
    title: 'Filecoin Onchain Cloud',
    description: 'Filecoin Onchain Cloud: providers, storage data sets, Filecoin Pay rails, payments and clients.',
    html: `${head({ title: 'Filecoin Onchain Cloud', lede: 'Verifiable warm storage paid onchain. Clients pay storage providers through Filecoin Pay rails; providers prove possession of each data set with PDP.' })}
    ${hero}
    ${section('Observations', `<ul class="foc-observations">${observations.map((x) => `<li>${x}</li>`).join('')}</ul>`, { sub: `Network series through ${o.as_of ?? 'unknown'} (UTC). Current-state counts reflect the latest snapshot.` })}
    ${section('Daily activity', grid, { sub: 'Daily, UTC. Flows are bars, end-of-day states are steps. Missing days are gaps.' })}
    <div class="foc-cols">
      ${section('Top providers', topProviders, { sub: 'By live data sets. Paid is stablecoin only.', more: more(url('providers'), 'All providers') })}
      ${section('Latest data sets', latestSets, { more: more(url('datasets'), 'All data sets') })}
    </div>
    ${section('Latest payments', payTable(o.payments ?? [], { prefix: 'latest' }), { sub: 'Settlements and one-time payments across all rails, in each rail’s token.', more: more(url('rails'), 'All rails') })}
    ${sources(['daily_network_metrics', 'providers', 'data_sets', 'rails', 'payments'], 'Stablecoins (USDFC, USDC.axl) are counted at face value in US dollars.')}`,
  }
}

// ---------------------------------------------------------------- providers

export function providers(rows: Row[]): Page {
  const approved = rows.filter((r) => r.approved && !r.removed).length
  const removed = rows.filter((r) => r.removed).length
  const q = coverage('quality')
  return {
    title: 'Storage providers',
    description: 'PDP storage providers: status, location, data sets, payments and 30-day quality checks.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Providers']], title: 'Storage providers', lede: `${count(rows.length - removed)} registered PDP providers (plus ${count(removed)} removed); ${count(approved)} approved for Filecoin Warm Storage. Quality spans ${quarterSpan(q?.end)}: storage and retrieval pool Dealbot probes, not client traffic; faults measure onchain proving periods.` })}
    ${table({
      caption: 'Storage providers', rows, prefix: '', page: 100, href: (r) => url(`provider/${r.id}`),
      filter: { label: 'Status', get: provState, options: [['all', 'All'], ['approved', 'Approved'], ['registered', 'Registered'], ['inactive', 'Inactive'], ['removed', 'Removed']] },
      search: (r) => [r.address, r.payee].filter(Boolean).join(" "), searchLabel: 'Filter by name, location or address',
      sort: ['live', 'desc'],
      cols: [
        { label: 'Provider', html: (r) => `${provLink(r.id, r.name)} <span class="meta">#${r.id}</span>`, sort: (r) => r.name?.toLowerCase() },
        { label: 'Status', html: provStatus, sort: (r) => ({ approved: 0, registered: 1, inactive: 2, removed: 3 } as Row)[provState(r)] },
        { label: 'Location', html: (r) => r.country ? esc([r.city, r.country].filter(Boolean).join(', ')) : NA, sort: (r) => r.country },
        { key: 'live', label: 'Live / data sets', num: true, html: (r) => `${count(r.live)}<span class="meta"> / ${count(r.data_sets)}</span>`, sort: (r) => num(r.live) },
        { label: 'Clients', num: true, html: (r) => count(r.clients), sort: (r) => num(r.clients) },
        { key: 'rate', label: 'Rate / month', num: true, html: (r) => zeroMuted(r.rate_month, usd(r.rate_month)), sort: (r) => num(r.rate_month) },
        { key: 'paid', label: 'Paid', num: true, html: (r) => zeroMuted(r.paid, usd(r.paid)), sort: (r) => num(r.paid) },
        { key: 'storage', label: 'Storage ok', num: true, html: (r) => pct(r.storage), sort: (r) => num(r.storage) },
        { key: 'retrieval', label: 'Retrieval ok', num: true, html: (r) => pct(r.retrieval), sort: (r) => num(r.retrieval) },
        { key: 'faults', label: 'Fault rate', num: true, html: (r) => pct(r.faults, 2), sort: (r) => num(r.faults) },
      ],
    })}
    ${sources(['providers', 'data_sets', 'rails', 'payments', 'daily_provider_quality'], 'Rate is the recurring stablecoin rate of still-streaming rails, including Dealbot; paid is stablecoin only. Blank quality means no probes in the window.')}`,
  }
}

function priceText(p: Row) {
  if (p.price_tib_month == null) return NA
  const value = p.price_symbol ? `${amt(p.price_tib_month, p.price_symbol)}${p.price_symbol.startsWith('USD') ? ` <span class="unit">${esc(p.price_symbol)}</span>` : ''}` : `${esc(p.price_tib_month)} <span class="unit">of an unidentified token</span>`
  return `${value} per TiB / month`
}

export function provider(x: Row): Page {
  const p: Row = x.provider ?? {}, q: Row = x.quality30 ?? {}, qs: Row | null = x.quality?.d?.length ? x.quality : null
  const sets: Row[] = x.data_sets ?? [], rails: Row[] = x.rails ?? []
  const live = sets.filter((d) => d.status === 'live').length
  const clients = new Set(sets.map((d) => d.owner)).size
  const rate = sum(rails.filter((r) => r.streaming && isStable(r)), (r) => r.rate_month)
  const paid = sum(rails.filter(isStable), (r) => r.paid)
  const loc = [p.city, p.region, p.country].filter(Boolean).join(', ')
  const token = !p.payment_token ? null : p.payment_token === ZERO ? 'FIL' : p.price_symbol ?? short(p.payment_token)
  const span = q.start ? `${q.start} to ${q.end}` : quarterSpan(coverage('quality')?.end)
  const ratio = (a: unknown, b: unknown, what: string) => num(b) == null ? 'Not observed' : num(b) ? `${count(a)} / ${count(b)} ${what}` : `No ${what} observed`
  const qplot = (title: string, k: string, column: string, value: string, note: string, info: string) => plot({ title, value, key: column === 'retrieval_median_ttfb_ms' ? column : `provider_${column}`, kind: 'line', pts: points(qs!.d, qs![k]), note, info, source: 'daily_provider_quality', column })
  const quality = qs ? `<div class="chart-grid foc-grid">
    ${qplot('Storage success', 'storage', 'storage_success_rate', pct(q.storage, 2), ratio(q.storage_successes, q.storage_checks, 'probes'), 'Dealbot storage probes that succeeded. Headline pools the 30-day window.')}
    ${qplot('Retrieval success', 'retrieval', 'retrieval_success_rate', pct(q.retrieval, 2), ratio(q.retrieval_successes, q.retrieval_checks, 'retrievals'), 'Dealbot retrievals of its own uploads that succeeded.')}
    ${qplot('Sampled retrieval success', 'sampled', 'sampled_retrieval_success_rate', pct(q.sampled, 2), ratio(q.sampled_retrieval_successes, q.sampled_retrieval_checks, 'sampled pieces'), 'Retrievals of randomly sampled stored pieces that succeeded. Skips excluded.')}
    ${qplot('Proving fault rate', 'faults', 'proving_fault_rate', pct(q.faults, 2), `${ratio(q.proving_periods_faulted, q.proving_periods_closed, 'proving periods faulted')} · ${count(q.proofs)} proofs`, 'Closed proving periods that faulted. Onchain PDP, not probes.')}
    ${qplot('Retrieval time to first byte (ms)', 'ttfb', 'retrieval_median_ttfb_ms', ms(q.ttfb), esc(q.ttfb_label ?? 'Median of daily medians'), 'Daily median time to first byte of Dealbot retrievals, in milliseconds.')}
  </div>` : empty('No quality checks recorded for this provider.')
  const history = [
    ['Registered', p.registered_at, p.registered_tx],
    p.approved_at && ['Approved for warm storage', p.approved_at, p.approval_tx],
    p.product_updated_at && p.product_updated_at !== p.registered_at && ['PDP product updated', p.product_updated_at],
    p.removed_at && ['Removed', p.removed_at, p.removed_tx],
  ].filter(Boolean) as [string, number, string?][]
  return {
    title: `${pname(p.name) || `Provider #${p.id}`}`,
    description: `Storage provider ${p.name ?? p.id}: data sets, rails, payments and service quality.`,
    html: `${head({
      crumbs: [['Onchain Cloud', url()], ['Providers', url('providers')], [`#${p.id}`]],
      title: `${esc(p.name ?? `Provider #${p.id}`)} <span class="foc-id">#${p.id}</span>`,
      lede: p.description && p.description !== p.name ? esc(p.description) : '',
      meta: [provStatus(p), p.endorsed && tag('Endorsed'), p.service_status && tag(p.service_status), loc && esc(loc),
        p.address && `${addr(p.address, { self: true })} ${copy(p.address)} ${blockscout(p.address)}`,
        safeUrl(p.service_url) && `<a href="${esc(p.service_url)}" rel="noopener">${esc(p.service_url.replace(/^https?:\/\//, ''))}</a>`],
    })}
    ${figures([
      ['Live data sets', count(live), `${count(sets.length)} in total`],
      ['Clients', count(clients), 'Distinct data set owners'],
      ['Recurring rate', usd(rate), 'Per 30 days, streaming stablecoin rails'],
      ['Paid to provider', usd(paid), `Stablecoin · ${plural(rails.length, 'rail')}`],
      ['Proving fault rate', pct(q.faults, 2), ratio(q.proving_periods_faulted, q.proving_periods_closed, 'periods')],
    ])}
    ${section('Service quality', quality, { sub: `Daily Dealbot probes and onchain proving. Headlines pool numerators and denominators over ${span}. Probes are synthetic checks, not client traffic.` })}
    ${paySection(x.daily, x.payments, { title: 'Payments received', hide: ['payee'] })}
    ${section('Data sets', dsTable(sets, { provider: false }), { sub: `${plural(sets.length, 'storage data set')} with this provider.` })}
    ${section('Rails', railTable(rails, { hide: ['payee'] }), { sub: 'Filecoin Pay rails with this provider as payee. Amounts in each rail’s token.' })}
    ${section('Offering', kv([
      ['Storage price', priceText(p)],
      ['Payment token', token ? `${esc(token)}${p.payment_token && p.payment_token !== ZERO ? ` <span class="mono meta">${short(p.payment_token)}</span> ${copy(p.payment_token, 'token address')}` : ''}` : NA],
      ['Capacity', num(p.capacity_tib) != null ? `${count(p.capacity_tib)} TiB` : NA],
      ['Piece size', p.min_piece ? `${bytes(p.min_piece)} to ${bytes(p.max_piece)}` : NA],
      ['Min proving period', p.proving_period ? `${count(p.proving_period)} epochs` : NA],
      ['IPNI', [p.ipni_piece && 'Pieces', p.ipni_ipfs && 'IPFS'].filter(Boolean).join(', ') || 'No'],
      ['Product', p.product_type ? esc(p.product_type) : NA],
      ['Service URL', safeUrl(p.service_url) ? `<a href="${esc(p.service_url)}" rel="noopener">${esc(p.service_url)}</a>` : p.service_url ? esc(p.service_url) : NA],
      ['Control address', p.address ? `${addr(p.address, { full: true })} ${copy(p.address)}` : NA],
      ['Payee', p.payee ? `${addr(p.payee, { full: true })} ${copy(p.payee)}` : NA],
    ]), { sub: 'Declared in the service provider registry.' })}
    ${section('History', `<ol class="foc-timeline">${history.map(([what, ts, tx]) => `<li><span>${what}</span> ${date(ts)}${tx ? ` · ${txLink(tx)}` : ''}</li>`).join('')}</ol>`)}
    ${sources(['providers', 'data_sets', 'rails', 'payments', 'daily_provider_quality'])}`,
  }
}

// ---------------------------------------------------------------- data sets

export function datasets(rows: Row[]): Page {
  const live = rows.filter((r) => r.status === 'live').length
  return {
    title: 'Storage data sets',
    description: 'Warm storage data sets: client, provider, status, rails and payments.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Data sets']], title: 'Storage data sets', lede: `${count(rows.length)} warm storage data sets, ${count(live)} live. Each is owned by a client, stored by one provider and paid through a PDP rail, plus CDN rails when enabled. Not to be confused with the portal’s <a href="/datasets">published datasets</a>.` })}
    ${dsTable(rows, { prefix: '', page: 100, caption: 'Storage data sets' })}
    ${sources(['data_sets', 'rails', 'payments'], 'Rate and paid are stablecoin only.')}`,
  }
}

function flow(items: [string, string][], arrows: [string, string][]) {
  return `<ol class="foc-flow">${items.map(([l, v], i) => `<li class="foc-node"><span class="meta">${l}</span><span>${v}</span></li>${arrows[i] ? `<li class="foc-arrow" aria-label="${esc(arrows[i][1])}"><b>${arrows[i][0]}</b><span class="meta">${arrows[i][1]}</span></li>` : ''}`).join('')}</ol>`
}

export function dataset(x: Row): Page {
  const d: Row = x.data_set ?? {}, p: Row | null = x.provider, rails: Row[] = x.rails ?? []
  const rate = sum(rails.filter((r) => r.streaming && isStable(r)), (r) => r.rate_month)
  const paid = sum(rails.filter(isStable), (r) => r.paid)
  let meta: Row = {}
  try { meta = typeof d.metadata === 'string' ? JSON.parse(d.metadata || '{}') : d.metadata ?? {} } catch {}
  const role = (r: Row) => r.id === d.pdp_rail_id ? 'Storage (PDP)' : r.id === d.cdn_rail_id ? 'CDN' : r.id === d.cache_miss_rail_id ? 'Cache miss' : 'Other'
  return {
    title: `Data set #${d.id}`,
    description: `Storage data set #${d.id}: client, provider, rails and payments.`,
    html: `${head({
      crumbs: [['Onchain Cloud', url()], ['Data sets', url('datasets')], [`#${d.id}`]],
      title: `Data set <span class="foc-id">#${d.id}</span>`,
      meta: [dsStatus(d.status), d.source && tag(d.source), d.cdn && tag('CDN'), d.ipfs && tag('IPFS indexing'), `Created ${date(d.created_at)}`, d.api_observed_at != null && `API snapshot ${dateTime(d.api_observed_at)} UTC`],
    })}
    ${flow([['Client', addr(d.owner)], ['Payment rails', rails.map((r) => railLink(r.id)).join(', ') || NA], ['Payees', [...new Set(rails.map((r) => addr(r.payee)))].join(', ') || NA]],
      [[rate ? usd(rate) : 'No active rate', 'per month'], [usd(paid), 'paid so far']])}
    ${section('Rails', table({
      caption: 'Rails attached to this data set', rows: rails, prefix: 'rails', href: (r) => url(`rail/${r.id}`),
      cols: [
        { label: 'Rail', num: true, html: (r) => railLink(r.id) }, { label: 'Role', html: role }, { label: 'State', html: (r) => railState(r.state) },
        { label: 'Rate / month', num: true, html: (r) => amt(r.rate_month, r.token_symbol) },
        { label: 'Lockup', num: true, html: (r) => days(r.lockup_epochs) },
        { label: 'Settled', num: true, html: (r) => amt(r.settled, r.token_symbol) },
        { label: 'One-time', num: true, html: (r) => amt(r.one_time, r.token_symbol) },
        { label: 'Payments', num: true, html: (r) => count(r.events) },
      ],
    }), { sub: 'Filecoin Pay rails attached to this data set, in each rail’s token. Flow totals above are stablecoin only; payees can include CDN services.' })}
    ${paySection(x.daily, x.payments, { hide: ['payer', 'payee'] })}
    ${section('Details', kv([
      ['Client', d.owner ? `${addr(d.owner, { full: true })} ${copy(d.owner)}` : NA],
      ['Provider', p ? `${provLink(p.id, p.name)} <span class="meta">#${p.id}</span>` : NA],
      ['Payee', addr(d.payee, { full: true })],
      ['Created', `${date(d.created_at)} <span class="meta">block ${count(d.created_block)}</span>`],
      ['Billing started', date(d.billing_started_at)],
      ['Billing terminated', date(d.billing_terminated_at)],
      ['Settlement ends', date(d.settlement_end_at)],
      ['Metadata', Object.keys(meta).length ? Object.entries(meta).map(([k, v]) => `<span class="tag mono">${esc(k)}${v !== '' ? `=${esc(v)}` : ''}</span>`).join(' ') : NA],
    ]))}
    ${sources(['data_sets', 'rails', 'payments'])}`,
  }
}

// ---------------------------------------------------------------- rails

export function rails(rows: Row[]): Page {
  const active = rows.filter((r) => r.state === 'active').length
  return {
    title: 'Payment rails',
    description: 'Filecoin Pay rails: payer, payee, operator, rate and payments.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Rails']], title: 'Payment rails', lede: `${count(rows.length)} Filecoin Pay rails, ${count(active)} active. A rail streams tokens from a payer to a payee under an operator contract. Rates settle per epoch, with optional one-time payments.` })}
    ${railTable(rows, { prefix: '', page: 100, caption: 'Payment rails' })}
    ${sources(['rails', 'payments'], 'Rate and paid are in each rail’s own token; sorting compares raw amounts across tokens.')}`,
  }
}

const railKey = (sym?: string) => sym && ['USDFC', 'USDC.axl'].includes(sym) ? 'rail_payments_usd' : sym === 'FIL' ? 'rail_payments_fil' : 'rail_payments'

export function rail(x: Row): Page {
  const r: Row = x.rail ?? {}, sym: string = r.token_symbol
  const totals: Row[] = x.totals ?? []
  const events = sum(totals, (t) => t.events)
  const sub = totals.length ? `${totals.map((t) => `${plural(Number(t.events), t.kind === 'settled' ? 'settlement' : 'one-time payment')} (${amt(t.gross, sym)})`).join(' and ')}. Amounts in ${esc(sym === 'Unknown' ? 'an unidentified token' : sym)}.${events > (x.payments?.length ?? 0) ? ` Latest ${count(x.payments?.length)} listed.` : ''} Days without events are gaps.` : ''
  return {
    title: `Rail #${r.id}`,
    description: `Filecoin Pay rail #${r.id}: payer, payee, operator, rate and payments.`,
    html: `${head({
      crumbs: [['Onchain Cloud', url()], ['Rails', url('rails')], [`#${r.id}`]],
      title: `Rail <span class="foc-id">#${r.id}</span>`,
      meta: [railState(r.state), r.service && tag(r.service), sym && tag(sym), r.dealbot && tag('Dealbot'),
        x.data_set && `Data set ${dsLink(x.data_set.id)}`, `Created ${date(r.created_at)} · ${txLink(r.created_tx)}`, r.api_observed_at != null && `API snapshot ${dateTime(r.api_observed_at)} UTC`],
    })}
    ${flow([['Payer', addr(r.payer)], ['Operator', addr(r.operator)], ['Payee', x.provider ? provLink(x.provider.id, x.provider.name) : addr(r.payee)]],
      [[amt(r.rate_month, sym), 'per month'], [amt(r.paid, sym), 'paid so far']])}
    ${figures([
      ['Rate', amt(r.rate_month, sym), 'per month'],
      ['Settled (snapshot)', amt(r.settled, sym), `Net to payee ${amt(r.settled_net, sym)}`],
      ['One-time (snapshot)', amt(r.one_time, sym), `Net to payee ${amt(r.one_time_net, sym)}`],
      ['Lockup', days(r.lockup_epochs), num(r.lockup_fixed) ? `plus ${amt(r.lockup_fixed, sym)} fixed` : 'rate lockup'],
      ['Commission', num(r.commission_bps) == null ? NA : `${Number(r.commission_bps) / 100}%`, 'operator'],
    ])}
    ${paySection(x.daily, x.payments, { hide: ['rail', 'payer', 'payee'], key: railKey(sym), unit: sym, sub })}
    ${section('Details', kv([
      ['Payer', r.payer ? `${addr(r.payer, { full: true })} ${copy(r.payer)}` : NA],
      ['Payee', r.payee ? `${addr(r.payee, { full: true })} ${copy(r.payee)}` : NA],
      ['Operator', addr(r.operator, { full: true })],
      ['Validator', addr(r.validator, { full: true })],
      ['Fee recipient', addr(r.fee_recipient, { full: true })],
      ['Token', `${esc(sym)}${r.token ? ` <span class="mono meta">${short(r.token)}</span> ${ext(`${BLOCKSCOUT}/address/${r.token}`)}` : ''}`],
      ['Data set', x.data_set ? `${dsLink(x.data_set.id)} ${dsStatus(x.data_set.status)}` : NA],
      ['Provider', x.provider ? provLink(x.provider.id, x.provider.name) : NA],
      ['Settled up to', r.settled_up_to ? `${date(epochTs(r.settled_up_to))} <span class="meta">epoch ${count(r.settled_up_to)}</span>` : NA],
      ['Last payment', date(r.last_payment_at)],
      ['Created', `${date(r.created_at)} · ${txLink(r.created_tx)}`],
      r.terminated_at && ['Terminated', `${date(r.terminated_at)} by ${addr(r.terminated_by)} · ${txLink(r.terminated_tx)}`],
      r.terminated_end_at && ['Payments end', date(r.terminated_end_at)],
      ['Counts toward run rate', r.eligible ? 'Yes' : 'No'],
    ]))}
    ${sources(['rails', 'payments'])}`,
  }
}

// ---------------------------------------------------------------- clients and operators

export function clients(rows: Row[]): Page {
  const bots = rows.filter((r) => r.dealbot).length
  return {
    title: 'Clients',
    description: 'Addresses that own storage data sets or pay through Filecoin Pay rails.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Clients']], title: 'Clients', lede: `${count(rows.length)} addresses that own data sets or pay through Filecoin Pay rails. ${plural(bots, 'is a Dealbot wallet', 'are Dealbot wallets')} running synthetic checks.` })}
    ${table({
      caption: 'Clients', rows, prefix: '', page: 100, href: (r) => url(`address/${r.address}`),
      filter: { label: 'Kind', get: (r) => r.dealbot ? 'dealbot' : 'client', options: [['all', 'All'], ['client', 'Excluding Dealbot'], ['dealbot', 'Dealbot']] },
      search: true, searchLabel: 'Filter by address or label',
      sort: ['paid', 'desc'],
      cols: [
        { label: 'Client', html: (r) => addr(r.address) + (r.dealbot && label(r.address) !== 'Dealbot' ? ` ${tag('Dealbot')}` : ''), sort: (r) => label(r.address) ?? r.address },
        { key: 'live', label: 'Live / data sets', num: true, html: (r) => `${count(r.live)}<span class="meta"> / ${count(r.data_sets)}</span>`, sort: (r) => num(r.live) },
        { label: 'Providers', num: true, html: (r) => count(r.providers), sort: (r) => num(r.providers) },
        { key: 'rails', label: 'Active / rails', num: true, html: (r) => `${count(r.active_rails)}<span class="meta"> / ${count(r.rails)}</span>`, sort: (r) => num(r.active_rails) },
        { key: 'rate', label: 'Rate / month', num: true, html: (r) => zeroMuted(r.rate_month, usd(r.rate_month)), sort: (r) => num(r.rate_month) },
        col.created('first_at', 'First rail'),
        { key: 'paid', label: 'Paid', num: true, html: (r) => zeroMuted(r.paid, usd(r.paid)), sort: (r) => num(r.paid) },
      ],
    })}
    ${sources(['data_sets', 'rails', 'payments'], 'Rate (still-streaming rails) and paid are stablecoin only.')}`,
  }
}

export function operators(rows: Row[]): Page {
  return {
    title: 'Operators',
    description: 'Operator contracts that create and manage Filecoin Pay rails.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Operators']], title: 'Operators', lede: `${count(rows.length)} operator contracts create and manage Filecoin Pay rails on behalf of payers. Filecoin Warm Storage Service (FWSS) operates most of them.` })}
    ${table({
      caption: 'Operators', rows, prefix: '', page: 100, href: (r) => url(`address/${r.address}`),
      search: true, searchLabel: 'Filter by address or service',
      sort: ['rails', 'desc'],
      cols: [
        { label: 'Operator', html: (r) => addr(r.address), sort: (r) => label(r.address) ?? r.address },
        { label: 'Service', html: (r) => esc(r.service), sort: (r) => r.service },
        { key: 'rails', label: 'Active / rails', num: true, html: (r) => `${count(r.active_rails)}<span class="meta"> / ${count(r.rails)}</span>`, sort: (r) => num(r.rails) },
        { label: 'Payers', num: true, html: (r) => count(r.payers), sort: (r) => num(r.payers) },
        { label: 'Payees', num: true, html: (r) => count(r.payees), sort: (r) => num(r.payees) },
        { key: 'run-rate', label: 'Run rate / year', num: true, html: (r) => usd(r.run_rate), sort: (r) => num(r.run_rate) },
        { key: 'fee-arr', label: 'Fee ARR', num: true, html: (r) => usd(r.fee_arr), sort: (r) => num(r.fee_arr) },
        { key: 'paid', label: 'Paid', num: true, html: (r) => usd(r.paid), sort: (r) => num(r.paid) },
        col.created('first_at', 'First rail'),
      ],
    })}
    ${sources(['rails', 'payments', 'daily_operator_metrics'], `Run rate and fee ARR are the latest daily operator snapshot${coverage('operators')?.end ? ` (${coverage('operators')!.end})` : ''}; paid is stablecoin only. Blank means no snapshot.`)}`,
  }
}

export function address(x: Row): Page {
  const a: string = x.address, l = label(a)
  const sets: Row[] = x.data_sets ?? [], out: Row[] = x.rails_out ?? [], inn: Row[] = x.rails_in ?? [], provs: Row[] = x.providers ?? []
  const roles = [provs.length && 'Provider', sets.length && 'Client', out.length && 'Payer', inn.length && 'Payee',
    x.rails_op && 'Operator', x.dealbot && 'Dealbot', x.orchestrator && 'ServiceOrchestrator'].filter(Boolean) as string[]
  const live = sets.filter((d) => d.status === 'live').length
  const activeRate = (rails: Row[]) => sum(rails.filter((r) => r.streaming && isStable(r)), (r) => r.rate_month)
  const op: Row | null = x.operator, od: Row | null = x.operator_daily?.d?.length ? x.operator_daily : null
  return {
    title: l ?? short(a),
    description: `Filecoin Onchain Cloud activity of ${a}.`,
    html: `${head({
      crumbs: [['Onchain Cloud', url()], ['Clients', url('clients')], ['Address']],
      title: l ? esc(l) : `<span class="mono foc-hex">${esc(a)}</span>`,
      lede: provs.length ? `Registered as ${provs.map((p) => provLink(p.id, p.name)).join(', ')}.` : '',
      meta: [`<span class="mono">${esc(a)}</span> ${copy(a)} ${blockscout(a)}`, ...roles.map(tag)],
    })}
    ${roles.length ? figures([
      sets.length && ['Live data sets', count(live), `${count(sets.length)} owned`],
      out.length && ['Paying', usd(activeRate(out)), 'Per 30 days, streaming stablecoin rails'],
      num(x.paid_out) != null && ['Paid out', usd(x.paid_out), `Gross, stablecoin · ${plural(out.length, 'rail')} as payer`],
      inn.length && ['Receiving', usd(activeRate(inn)), 'Per 30 days, streaming stablecoin rails'],
      num(x.paid_in) != null && ['Received', usd(x.paid_in), `Net, stablecoin · ${plural(inn.length, 'rail')} as payee`],
      op && ['Operator run rate', usd(op.filecoin_pay_gross_payment_volume_run_rate_usd), `${count(op.active_rails)} active rails`],
      x.rails_op && ['Rails operated', count(x.rails_op), 'All states'],
      x.orchestrator && ['Orchestrator', x.orchestrator.is_admitted ? 'Admitted' : 'Removed', `${count(x.orchestrator.bound_pairs)} bound pairs`],
    ]) : ''}
    ${od ? section('Operator run rate', `<div class="chart-grid foc-grid foc-grid-2">
      ${plot({ title: 'Annualized run rate', value: usd(lastVal(od.run_rate)[0]), key: 'operator_run_rate_usd', kind: 'line', pts: points(od.d, od.run_rate), info: 'Gross stablecoin run rate of this operator’s eligible recurring rails, annualized.', source: 'daily_operator_metrics', column: 'filecoin_pay_gross_payment_volume_run_rate_usd' })}
      ${plot({ title: 'Active rails', value: count(lastVal(od.active_rails)[0]), key: 'operator_active_rails', kind: 'step', pts: points(od.d, od.active_rails), info: 'Rails in the active state at the end of the day.', source: 'daily_operator_metrics', column: 'active_rails' })}
    </div>`) : ''}
    ${x.daily_out?.d?.length ? paySection(x.daily_out, null, { title: 'Payments sent' }) : ''}
    ${x.daily_in?.d?.length ? paySection(x.daily_in, null, { title: 'Net payments received' }) : ''}
    ${sets.length ? section('Data sets', dsTable(sets, { owner: false }), { sub: `${plural(sets.length, 'data set')} owned by this client.` }) : ''}
    ${out.length ? section('Rails as payer', railTable(out, { hide: ['payer'], prefix: 'out' })) : ''}
    ${inn.length ? section('Rails as payee', railTable(inn, { hide: ['payee'], prefix: 'in' })) : ''}
    ${x.payments?.length ? section('Latest payments', payTable(x.payments), { sub: `Most recent ${count(x.payments.length)} events sent or received, in each rail’s token.` }) : ''}
    ${roles.length ? '' : empty('No Filecoin Onchain Cloud activity for this address in the portal data.')}
    ${sources(['data_sets', 'rails', 'payments', 'daily_operator_metrics', 'service_orchestrators'])}`,
  }
}

// ---------------------------------------------------------------- solstice

const blockTime = (block: unknown) => num(block) == null ? 'unknown time' : new Date(epochTs(block) * 1000).toISOString().slice(0, 16).replace('T', ' ')
const blockDate = (block: unknown) => num(block) == null ? NA : date(epochTs(block))
const fusd = (v: unknown) => v == null ? '<span class="null">Unknown</span>' : `$${atto(v)}`
const ffil = (v: unknown) => v == null ? '<span class="null">Unknown</span>' : `${atto(v, 4)} <span class="unit">FIL</span>`
function phase(q: Row) {
  const at = num(q.as_of_block)
  if (at == null) return 'Unknown'
  if (at < Number(q.start_block)) return 'Not started'
  if (at <= Number(q.end_block)) return 'In quarter, partial'
  if (at < Number(q.verification_start_block)) return 'Posting window'
  return q.is_bound ? 'Bound' : 'Verification window'
}
function gate(q: Row) {
  if (Number(q.quarter) === 1) return 'Not gated'
  if (q.gate_checked_at == null) return '<span class="null">Not observed</span>'
  return `${q.gate_passed ? 'Passed' : 'Failed'} ${date(q.gate_checked_at)} · ${fusd(q.gate_threshold)} threshold${q.gate_steps != null ? ` · ${count(q.gate_steps)} steps` : ''}`
}

export function solstice(x: Row): Page {
  const quarters: Row[] = x.quarters ?? [], orchestrators: Row[] = x.orchestrators ?? [], oq: Row[] = x.orchestrator_quarters ?? []
  return {
    title: 'Solstice',
    description: 'Solstice ServiceOrchestrators and quarterly Filecoin Pay Volume.',
    html: `${head({ crumbs: [['Onchain Cloud', url()], ['Solstice']], title: 'Solstice', lede: 'ServiceOrchestrators post quarterly Filecoin Pay Volume (FPV). Once bound, the aggregate is checked against a gate threshold and shares are submitted. Volumes are provisional until bound.' })}
    ${section('Quarters', table({
      caption: 'Solstice quarters', rows: quarters, prefix: 'quarters',
      cols: [
        { label: 'Quarter', html: (r) => `Q${esc(r.quarter)} <span class="mono meta">${count(r.start_block)}–${count(r.end_block)}</span>` },
        { label: 'Window (UTC)', html: (r) => `${blockDate(r.start_block)} to ${blockDate(r.end_block)}` },
        { label: 'Phase', html: phase },
        { label: 'Observed through', html: (r) => r.as_of_block == null ? '<span class="null">Unknown</span>' : `block ${count(r.as_of_block)} <span class="meta">${blockTime(r.as_of_block)} UTC</span>` },
        { label: 'Binds at', html: (r) => blockDate(r.bound_block) },
        { label: 'Bound FPV', num: true, html: (r) => r.is_bound ? fusd(r.bound_volume) : '<span class="null">Not bound</span>' },
        { label: 'Gate', html: gate, wrap: true },
        { label: 'Shares', wrap: true, html: (r) => r.shares_submitted_at == null ? '<span class="null">No event (all-zero submissions emit none)</span>' : `${fusd(r.shares_total)} · ${count(r.share_recipients)} recipients · ${date(r.shares_submitted_at)}` },
      ],
    }), { sub: 'Phases derive from the latest observed block against each quarter’s windows.' })}
    ${section('ServiceOrchestrators', table({
      caption: 'ServiceOrchestrators', rows: orchestrators, prefix: 'orchestrators', href: (r) => url(`address/${r.orchestrator}`),
      cols: [
        { label: 'Orchestrator', html: (r) => addr(r.orchestrator, { full: true }) },
        { label: 'Wallet', html: (r) => addr(r.wallet) },
        { label: 'Status', html: (r) => flag(r.is_admitted, 'Admitted', 'Removed') },
        { label: 'Admissions', num: true, html: (r) => count(r.admissions) },
        { label: 'Bound pairs', num: true, html: (r) => count(r.bound_pairs) },
        { label: 'First admitted', html: (r) => `${date(r.first_admitted_at)} · ${txLink(r.admitted_tx)}` },
        { label: 'Removed', html: (r) => date(r.removed_at) },
      ],
    }))}
    ${section('Volume by orchestrator', table({
      caption: 'Volume by orchestrator and quarter', rows: oq, prefix: 'volume',
      cols: [
        { label: 'Quarter', html: (r) => `Q${esc(r.quarter)}` },
        { label: 'Orchestrator', html: (r) => addr(r.orchestrator) + (r.is_removed_in_quarter ? ' <span class="meta">removed</span>' : '') },
        { label: 'Coverage', html: (r) => r.is_complete ? 'Complete' : `<span class="null">Partial${r.volume_as_of_block != null ? ` · block ${count(r.volume_as_of_block)}` : ''}</span>` },
        { label: 'Settlements', num: true, html: (r) => count(r.stablecoin_settlements) },
        { label: 'Stablecoin', num: true, html: (r) => fusd(r.stablecoin_volume) },
        { label: 'FIL (USD)', num: true, html: (r) => fusd(r.fil_volume) },
        { label: 'Recomputed FPV', num: true, html: (r) => fusd(r.volume) },
        { label: 'Posted', num: true, html: (r) => r.posted_volume == null ? '<span class="null">Not posted</span>' : `${fusd(r.posted_volume)}${r.posted_at ? ` <span class="meta">${dateText(r.posted_at)}</span>` : ''}` },
        { label: 'Reported', num: true, html: (r) => r.reported_volume == null ? '<span class="null">Not reported</span>' : `${fusd(r.reported_volume)}${Number(r.corrections) > 0 ? ` <span class="meta">${plural(Number(r.corrections), 'correction')}</span>` : ''}` },
        { label: 'Bound', num: true, html: (r) => r.is_bound ? fusd(r.bound_volume) : '<span class="null">Not bound</span>' },
        { label: 'Pending FIL', num: true, html: (r) => ffil(r.fil_pending_atto_fil) },
      ],
    }), { sub: 'Recomputed from settlements; posted volumes come from onchain VolumePosted events. Exact atto amounts, rounded for display.' })}
    ${sources(['service_orchestrators', 'orchestrator_quarters', 'service_quarters'])}`,
  }
}
const dateText = (ts: unknown) => new Date(Number(ts) * 1000).toISOString().slice(0, 10)

export const render: Record<string, (data: any) => Page> = { overview, providers, provider, datasets, dataset, rails, rail, clients, operators, address, solstice }
