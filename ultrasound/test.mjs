import assert from 'node:assert/strict'
import fs from 'node:fs'
import { test } from 'node:test'
import { Script } from 'node:vm'
import { pack, render, serialize, validate } from './build.mjs'

const today = '2026-10-30'
function fixture() {
  const dates = ['2026-10-27', '2026-10-28']
  const rows = values => dates.map((date, i) => ({ date, ...values(i) }))
  return pack({
    generated_at: '2026-10-29T14:05:00.000Z',
    checkpoint: { date: dates.at(-1), first_date: dates[0], n_days: 2, ordinal: 123 },
    ends: { payments: dates.at(-1), sampled: dates.at(-1), proving: dates.at(-1), rails_api: '2026-10-29 08:00' },
    snapshot: { f_bytes: 2 ** 40, m_bytes: 0 },
    providers: {}, monitor_payers: [], other_pdp: [], concentration: {}, gpv_top_operator: [],
    solstice: [{ quarter: 1 }], solstice_orch: [], solstice_admitted: 0,
    payments_nonstable: [], payment_dupe_roles: 0,
    storage: rows(i => ({ b: i * 2 ** 40, mb: 0, sets: i, payers: i, msets: 0 })),
    payments_daily: rows(() => ({ fwss_pdp: 1.23456789 })),
    gpv: rows(() => ({ fwss_pdp: 12.3456789 })),
    quality: rows(() => ({ sc: 10, ss: 9, pc: 20, pf: 1 })),
    econ: rows(() => ({ circulating_fil: 100, locked_fil: 50, minted_rewards_fil: 5, total_burn_fil: 1, raw_power_pibs: 10, fil_token_price_avg_usd: 2 })),
    provider_quality: [{ provider_id: 123, name: 'Provider' }],
    provider_billing: [{ provider_id: 123, bytes: 2 ** 40 }],
  })
}

test('packs the original columnar contract, preserving nulls and zero baseline', () => {
  const d = fixture()
  validate(d, today)
  assert.deepEqual(d.storage.b, [0, 2 ** 40])
  assert.deepEqual(d.storage.all_fwss, [null, null])
  assert.equal(d.pay.fwss_pdp[0], 1.234568)
  assert.equal(d.gpv.fwss_pdp[0], 12.3457)
  assert.equal(d.providers[0].billed.bytes, 2 ** 40)
})

test('rejects invalid daily coverage before deployment', () => {
  for (const mutate of [
    d => { d.storage.date[1] = today },
    d => { d.storage.date[1] = '2026-11-01' },
    d => { d.storage.date[0] = '2026-10-25' },
    d => { d.storage.b.pop() },
    d => { d.storage.date = [] },
    d => { d.meta.checkpoint.date = '2026-10-27' },
    d => { d.meta.ends.sampled = today },
    d => { d.meta.dupe_roles = 1 },
    d => { d.meta.snapshot.f_bytes = 42 },
    d => { d.econ.minted_rewards_fil = [null, null] },
    d => { d.quality.sc = [0, 0] },
    d => { d.meta.solstice = [] },
    d => { d.econ.locked_fil[0] = NaN },
  ]) {
    const d = fixture()
    mutate(d)
    assert.throws(() => validate(d, today))
  }
})

test('allows source lag but does not mislabel it as a new observation', () => {
  const d = fixture()
  validate(d, '2027-01-01')
  const html = render(d)
  assert.match(html, /end of day 28 Oct 2026/)
  assert.match(html, /Built 2026-10-29 UTC/)
  assert.match(html, /Data may be stale/)
})

test('regenerates the no-JavaScript fallback, including short windows', () => {
  const html = render(fixture())
  assert.match(html, /1\.00 TiB/)
  assert.match(html, /\$2\.47/)
  assert.match(html, /90\.00%/)
  assert.match(html, /5\.00%/)
  assert.doesNotMatch(html, /__DATA__|__NOSCRIPT__|27\.47 TiB|77 TiB/)
  const changed = fixture()
  changed.storage.b[1] = 2 * 2 ** 40
  assert.match(render(changed), /2\.00 TiB/)
})

test('embeds untrusted text without breaking out of the script', () => {
  const d = fixture()
  d.providers[0].name = '</script><script>alert(1)</script>'
  d.meta.solstice_orch = [{ volume_atto_usd: '123456789012345678901234567890' }]
  const json = serialize(d)
  assert.doesNotMatch(json, /</)
  assert.deepEqual(JSON.parse(json), d)
  assert.throws(() => serialize({ value: Infinity }))
})

test('template placeholders are unique and generated JavaScript parses', () => {
  const template = fs.readFileSync(new URL('./template.html', import.meta.url), 'utf8')
  assert.throws(() => render(fixture(), template.replace('/*__DATA__*/null', 'null')))
  assert.throws(() => render(fixture(), template + '<!--__NOSCRIPT__-->'))
  const html = render(fixture())
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
  assert.equal(scripts.length, 1)
  assert.doesNotThrow(() => new Script(scripts[0][1]))
  assert.doesNotMatch(html, /fetch\(|<script[^>]+src=/)
})
