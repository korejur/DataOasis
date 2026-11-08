// Kartica zgrade: sve brojke za jednu zgradu iz atributa vektorske pločice.
import { COLORS, FN_BREAKS } from './layers.js';
import { eur, kwh, num } from './format.js';

const ROOF = { ravni: 'ravni', kosi: 'kosi', 'mješoviti': 'mješoviti (ravni i kosi dijelovi)', 'bez krova': 'bez krovne plohe' };
const HEAD = { ravni: 's ravnim krovom', kosi: 's kosim krovom', 'mješoviti': 's mješovitim krovom', 'bez krova': 'bez krovne plohe' };

const ZK_CLASS = {
  visoka: { label: 'Visoka pogodnost', text: 'Pretežno ravan krov, pogodan za ekstenzivni i intenzivni zeleni krov.' },
  srednja: { label: 'Srednja pogodnost', text: 'Blagi nagib, pogodan za ekstenzivni zeleni krov (sedumi, trave).' },
  niska: { label: 'Niska pogodnost', text: 'Nagib 20–35°: moguće samo uz zaštitu supstrata od klizanja.' },
  nije: { label: 'Nije pogodno', text: 'Krov je prestrm ili ima premalo površine s malim nagibom.' },
};

function fnClass(p) {
  if (p.fn !== 1) return { key: 'nije', label: 'Nije pogodno' };
  if (p.fn_prinos >= FN_BREAKS.odlican) return { key: 'odlican', label: 'Odličan prinos' };
  if (p.fn_prinos >= FN_BREAKS.dobar) return { key: 'dobar', label: 'Dobar prinos' };
  return { key: 'umjeren', label: 'Umjeren prinos' };
}

const row = (k, v, hint = '') =>
  `<div class="row"><dt>${k}${hint ? `<small>${hint}</small>` : ''}</dt><dd>${v}</dd></div>`;

const badge = (color, label) =>
  `<span class="badge"><i style="background:${color}"></i>${label}</span>`;

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

/** Oznake iz povezanih izvora: kulturno dobro, javna zgrada (ISGE), ustanova. */
function linked(p) {
  const out = [];
  if (p.bastina) {
    out.push(`<div class="tag tag-heritage">
      <b>Zaštićeno kulturno dobro</b>
      <span>${esc(p.bastina)}${p.bastina_id ? ` <small>(${esc(p.bastina_id)})</small>` : ''}</span>
      <small>Svaki zahvat na krovu traži suglasnost konzervatora.</small></div>`);
  }
  if (p.ustanova) {
    out.push(`<div class="tag"><b>${esc(p.ustanova_tip ?? 'Ustanova')}</b><span>${esc(p.ustanova)}</span></div>`);
  }
  if (p.javno) {
    const share = p.javno_udio;
    const cover = share == null ? 'Manji potrošač: vjerojatno koristi samo dio zgrade, pa udio nije izračunat.'
      : p.fn !== 1 ? ''
      : share >= 100 ? 'Sunčana elektrana na krovu mogla bi proizvesti <b>više struje nego što zgrada troši</b>.'
      : `Sunčana elektrana na krovu mogla bi pokriti <b>${num(share)} %</b> te potrošnje.`;
    out.push(`<div class="tag tag-public">
      <b>Objekt Grada Zagreba</b><span>${esc(p.javno)}</span>
      <span>Troši ${kwh(p.javno_kwh)} struje godišnje <small>(ISGE, 2023.)</small></span>
      ${cover ? `<span>${cover}</span>` : ''}</div>`);
  }
  return out.length ? `<div class="tags">${out.join('')}</div>` : '';
}

export function renderCard(p, mode, params) {
  const zk = ZK_CLASS[p.zk] ?? ZK_CLASS.nije;
  const fn = fnClass(p);
  const zkCand = p.zk === 'visoka' || p.zk === 'srednja';
  const old = p.god && p.god < 2015;

  const green = `
    <section class="card-sec ${mode === 'zk' ? 'is-active' : ''}">
      <h3>Zeleni krov ${badge(COLORS.zk[p.zk] ?? COLORS.zk.nije, zk.label)}</h3>
      <p class="card-text">${zk.text}</p>
      ${zkCand ? `<dl>
        ${row('Površina za zelenilo', `${num(p.zk_m2)} m²`, 'iskoristivo, bez rubova i instalacija')}
        ${row('Zadržana kišnica', `${num(p.zk_voda_m3)} m³ godišnje`, 'ne opterećuje kanalizaciju')}
        ${row('Okvirna investicija', eur(p.zk_eur))}
      </dl>` : ''}
    </section>`;

  const solar = `
    <section class="card-sec ${mode === 'fn' ? 'is-active' : ''}">
      <h3>Fotonapon ${badge(COLORS.fn[fn.key], fn.label)}</h3>
      ${p.fn === 1 ? `<dl>
        ${row('Snaga elektrane', `${num(p.fn_kwp, 1)} kWp`)}
        ${row('Proizvodnja', `${kwh(p.fn_kwh)} godišnje`, `${num(p.fn_prinos)} kWh po kWp`)}
        ${row('Struja za kućanstva', `≈ ${num(p.fn_kuc, p.fn_kuc < 10 ? 1 : 0)}`, `pri ${num(params.household_kwh_year)} kWh godišnje`)}
        ${row('Manje CO₂', `${num(p.fn_co2_t, p.fn_co2_t < 10 ? 1 : 0)} t godišnje`)}
        ${row('Okvirna investicija', eur(p.fn_eur))}
        ${row('Jednostavni povrat', `${num(p.fn_povrat_god, 1)} god.`, 'bez subvencija')}
      </dl>` : '<p class="card-text">Na krov stane manje od 3 kWp ili su plohe loše orijentirane.</p>'}
    </section>`;

  return `
    <header class="card-head">
      <p class="eyebrow">${p.cetvrt ?? ''}</p>
      <h2>Zgrada ${HEAD[p.krov] ?? ''}</h2>
      <dl class="facts">
        ${row('Krovna površina', `${num(p.krov_m2)} m²`, `${num(p.ravno_pct)} % ravno`)}
        ${row('Visina', `${num(p.h, 1)} m`)}
        ${row('Tip krova', ROOF[p.krov] ?? p.krov)}
        ${row('Podaci snimljeni', p.god ? `${p.god}.` : '–', old ? 'moguće su novije promjene' : '')}
      </dl>
      ${linked(p)}
    </header>
    ${mode === 'zk' ? green + solar : solar + green}
    <p class="card-foot">Tehnički potencijal iz 3D modela. Prije izvedbe potrebna je statička provjera krova.
      <span class="bid">ID: ${p.id}</span></p>`;
}
