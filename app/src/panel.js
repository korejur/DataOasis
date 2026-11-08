// Panel: ključni brojevi (grad ili odabrana četvrt), scenarij i rang-lista četvrti.
import { big, eur, gwh, ha, num, plural } from './format.js';

const OLYMPIC_POOL_M3 = 2500; // 50 m × 25 m × 2 m

const pct = (v) => (Number.isFinite(v) ? `${num(v * 100, v < 0.1 ? 1 : 0)} %` : '–');

const PUBLIC_NOTE = 'Obuhvat: objekti Grada iz ISGE-a, povezani s 3D modelom po adresi. Državne zgrade nisu uključene.';

/** Ključni brojevi za odabrani sloj; `s` je udio kandidata u scenariju, `pub` = samo objekti Grada. */
function kpis(d, mode, s, params, pub) {
  const of = pub ? 'objekata Grada' : 'svih zgrada';
  if (mode === 'zk') {
    const n = Math.round(d.zk_kandidati * s);
    const water = d.zk_zadrzana_voda_m3_god * s;
    return {
      tiles: [
        { label: 'Pogodnih krovova', value: num(n), unit: plural(n, 'zgrada', 'zgrade', 'zgrada'),
          sub: `${pct(d.zk_kandidati / d.zgrade)} ${of}` },
        { label: 'Površina za zelenilo', value: ha(d.zk_iskoristivo_m2 * s),
          sub: 'iskoristivi dio krovova' },
        { label: 'Zadržana kišnica', value: `${big(water)} m³`, unit: 'godišnje',
          sub: `≈ ${num(water / OLYMPIC_POOL_M3)} olimpijskih bazena` },
        { label: 'Okvirna investicija', value: eur(d.zk_trosak_eur * s),
          sub: `${num(params.green_cost_eur_m2)} €/m², bez hidroizolacije` },
      ],
      note: pub ? PUBLIC_NOTE
        : 'Kišnica zadržana na krovu ne opterećuje mješovitu kanalizaciju za jakih pljuskova, '
          + 'a isparavanjem hladi zgradu i okolicu.',
    };
  }
  const n = Math.round(d.fn_kandidati * s);
  const kwhYear = d.fn_proizvodnja_GWh_god * 1e6;
  const payback = d.fn_trosak_eur / (kwhYear * params.electricity_price_eur_kwh);
  // Objekti Grada: udio vlastite potrošnje (samo objekti s >= 20 MWh/god, METODOLOGIJA 7.2)
  const third = pub
    ? { label: 'Pokrivenost potrošnje', value: pct((d.veliki_fn_GWh_god * s) / d.veliki_potrosnja_GWh_god),
      sub: `struje ${num(d.veliki_potrosaci)} ${plural(d.veliki_potrosaci, 'objekta', 'objekta', 'objekata')} `
        + 's ≥ 20 MWh godišnje (ISGE, 2023.)' }
    : { label: 'Struja za kućanstva', value: big(d.fn_kucanstva * s),
      sub: `pri ${num(params.household_kwh_year)} kWh godišnje` };
  return {
    tiles: [
      { label: 'Pogodnih krovova', value: num(n), unit: plural(n, 'zgrada', 'zgrade', 'zgrada'),
        sub: `${pct(d.fn_kandidati / d.zgrade)} ${of}` },
      { label: 'Proizvodnja struje', value: gwh(d.fn_proizvodnja_GWh_god * s), unit: 'godišnje',
        sub: `snaga ${num(d.fn_snaga_MWp * s, d.fn_snaga_MWp * s < 10 ? 1 : 0)} MWp` },
      third,
      { label: 'Manje CO₂', value: `${big(d.fn_co2_t_god * s)} t`, unit: 'godišnje',
        sub: `${num(params.grid_co2_kg_per_kwh, 3)} kg po kWh iz mreže` },
    ],
    note: `Okvirna investicija ${eur(d.fn_trosak_eur * s)}, jednostavni povrat oko ${num(payback, 1)} god. `
      + `(${num(params.electricity_price_eur_kwh, 2)} €/kWh, bez subvencija).${pub ? ` ${PUBLIC_NOTE}` : ''}`,
  };
}

export const SORTS = {
  zk: [
    { key: 'zk_iskoristivo_m2', label: 'Površina za zelenilo', fmt: ha, scale: true },
    { key: 'zk_kandidati', label: 'Broj pogodnih krovova', fmt: (v) => num(v), scale: true },
    { key: 'zk_udio', label: 'Udio pogodnih zgrada', fmt: pct, get: (d) => d.zk_kandidati / d.zgrade },
  ],
  fn: [
    { key: 'fn_proizvodnja_GWh_god', label: 'Proizvodnja struje', fmt: gwh, scale: true },
    { key: 'fn_kandidati', label: 'Broj pogodnih krovova', fmt: (v) => num(v), scale: true },
    { key: 'fn_udio', label: 'Udio pogodnih zgrada', fmt: pct, get: (d) => d.fn_kandidati / d.zgrade },
  ],
};

export function renderKpis(el, noteEl, data, mode, share, params, pub = false) {
  const k = kpis(data, mode, share, params, pub);
  el.innerHTML = k.tiles.map((t) => `
    <div class="kpi">
      <div class="kpi-label">${t.label}</div>
      <div class="kpi-value">${t.value}${t.unit ? ` <span>${t.unit}</span>` : ''}</div>
      <div class="kpi-sub">${t.sub}</div>
    </div>`).join('');
  noteEl.textContent = k.note;
}

export function renderSortOptions(select, mode, current) {
  select.innerHTML = SORTS[mode]
    .map((o) => `<option value="${o.key}" ${o.key === current ? 'selected' : ''}>${o.label}</option>`)
    .join('');
}

export function renderDistricts(el, districts, mode, sortKey, share, selected) {
  const sort = SORTS[mode].find((o) => o.key === sortKey) ?? SORTS[mode][0];
  const raw = (d) => (sort.get ? sort.get(d) : d[sort.key] * (sort.scale ? share : 1));
  const val = (d) => (Number.isFinite(raw(d)) ? raw(d) : 0); // četvrt bez objekata Grada
  const rows = [...districts].sort((a, b) => val(b) - val(a));
  const max = Math.max(...rows.map(val)) || 1;
  el.innerHTML = rows.map((d, i) => `
    <li>
      <button class="district ${d.slug === selected ? 'is-selected' : ''}" data-slug="${d.slug}"
        aria-pressed="${d.slug === selected}">
        <span class="d-rank">${i + 1}</span>
        <span class="d-name">${d.naziv}</span>
        <span class="d-val">${sort.fmt(val(d))}</span>
        <span class="d-bar mode-${mode}"><i style="width:${(100 * val(d)) / max}%"></i></span>
      </button>
    </li>`).join('');
}
