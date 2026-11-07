// Pretraga: gradske četvrti lokalno, adrese preko Nominatima (OpenStreetMap).
// Nominatim se poziva tek na Enter ili klik (pravila korištenja: najviše 1 upit u sekundi).

const NOMINATIM = 'https://nominatim.openstreetmap.org/search';
const ZAGREB_VIEWBOX = '15.77,45.97,16.23,45.62';

/** "Ulica grada Vukovara 56, Trnje" umjesto punog Nominatimova naziva. */
function label(h) {
  const a = h.address ?? {};
  const street = [a.road ?? a.pedestrian ?? a.square ?? h.name, a.house_number].filter(Boolean).join(' ');
  const area = a.city_district ?? a.suburb ?? a.quarter ?? a.neighbourhood;
  return [street || h.display_name.split(', ')[0], area].filter(Boolean).join(', ');
}

const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd');

export function initSearch({ form, input, list, districts, onDistrict, onPlace }) {
  let items = [];
  let active = -1;
  let lastQuery = 0;

  const close = () => { list.hidden = true; active = -1; };

  function render() {
    list.innerHTML = items.map((it, i) => `
      <li role="option" id="sr-${i}" class="${i === active ? 'is-active' : ''}" data-i="${i}" aria-selected="${i === active}">
        <span class="sr-kind">${it.kind}</span><span class="sr-text">${it.text}</span>
      </li>`).join('');
    list.hidden = items.length === 0;
    input.setAttribute('aria-activedescendant', active >= 0 ? `sr-${active}` : '');
  }

  function suggest() {
    const q = norm(input.value.trim());
    if (!q) { items = []; render(); return; }
    items = districts
      .filter((d) => norm(d.naziv).includes(q))
      .slice(0, 5)
      .map((d) => ({ kind: 'Četvrt', text: d.naziv, district: d }));
    if (q.length >= 3) items.push({ kind: 'Adresa', text: `Traži adresu „${input.value.trim()}“`, address: true });
    active = items.length ? 0 : -1;
    render();
  }

  async function geocode(q) {
    const wait = 1100 - (Date.now() - lastQuery);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
    lastQuery = Date.now();
    items = [{ kind: '…', text: 'Tražim adresu…' }];
    active = -1; render();
    try {
      const url = `${NOMINATIM}?format=jsonv2&addressdetails=1&limit=5&countrycodes=hr&bounded=1`
        + `&viewbox=${ZAGREB_VIEWBOX}&accept-language=hr&q=${encodeURIComponent(q)}`;
      const res = await fetch(url, { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error(res.statusText);
      const hits = await res.json();
      items = hits.length
        ? hits.map((h) => ({ kind: 'Adresa', text: label(h),
          place: { lon: +h.lon, lat: +h.lat, label: h.display_name } }))
        : [{ kind: '', text: 'Adresa nije pronađena u Zagrebu. Pokušajte s ulicom i kućnim brojem.' }];
    } catch {
      items = [{ kind: '', text: 'Pretraga adresa trenutačno nije dostupna.' }];
    }
    active = items.findIndex((it) => it.place);
    render();
  }

  function choose(it) {
    if (!it) return;
    if (it.district) { input.value = it.district.naziv; close(); onDistrict(it.district); }
    else if (it.address) geocode(input.value.trim());
    else if (it.place) { input.value = it.text; close(); onPlace(it.place); }
  }

  input.addEventListener('input', suggest);
  input.addEventListener('focus', () => { if (items.length) list.hidden = false; });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!items.length) return;
      active = (active + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      render();
    } else if (e.key === 'Escape') close();
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    if (active >= 0 && items[active]) choose(items[active]);
    else geocode(q);
  });
  list.addEventListener('mousedown', (e) => e.preventDefault()); // ne gubi fokus
  list.addEventListener('click', (e) => {
    const li = e.target.closest('li[data-i]');
    if (li) choose(items[+li.dataset.i]);
  });
  document.addEventListener('click', (e) => { if (!form.contains(e.target)) close(); });
}
