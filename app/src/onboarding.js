// Uvod za prvi posjet. Umjesto prozora preko karte: karta je odmah upotrebljiva, a uvod se
// zatvara sam čim korisnik klikne zgradu. Tri prijedloga (PRIVREMENO, ostaje jedan):
//   atlas  – naslovnica u lijevom panelu
//   grad   – vođeni obilazak u tri koraka s oblačićem uz element
//   teren  – oznaka na stvarnoj pogodnoj zgradi na karti + kratka uputa u panelu
import { num } from './format.js';

const KEY = 'kzk-intro';

export function introSeen() {
  try { return localStorage.getItem(KEY) === '1'; } catch { return false; }
}
function markSeen() {
  try { localStorage.setItem(KEY, '1'); } catch { /* privatni način rada */ }
}
export function resetIntro() {
  try { localStorage.removeItem(KEY); } catch { /* ignore */ }
}

const mobile = () => window.matchMedia('(max-width: 760px)').matches;

/** Točka u sredini vidljivog dijela karte (bez panela). */
function viewCenter() {
  const W = window.innerWidth;
  const H = window.innerHeight;
  if (mobile()) return { x: W / 2, y: H * 0.38 }; // između legende i donjeg panela
  const left = document.getElementById('panel').getBoundingClientRect().right;
  return { x: left + (W - left) / 2, y: H / 2 };
}

/** Velik pogodan krov blizu sredine vidljivog dijela karte, kao primjer za klik. */
function findCandidate(map, mode) {
  if (!map.getLayer('bld-fill') || map.getZoom() < 13) return null;
  const c = viewCenter();
  const dy = mobile() ? 70 : 160;
  const box = [[c.x - 220, c.y - dy], [c.x + 220, c.y + dy]];
  const good = (p) => (mode === 'zk' ? p.zk === 'visoka' : p.fn === 1 && p.fn_prinos >= 1150);
  let best = null;
  for (const f of map.queryRenderedFeatures(box, { layers: ['bld-fill'] })) {
    const p = f.properties;
    if (!good(p) || p.krov_m2 < 250 || p.krov_m2 > 4000) continue;
    const ring = f.geometry.type === 'Polygon' ? f.geometry.coordinates[0] : f.geometry.coordinates[0][0];
    const lng = ring.reduce((s, q) => s + q[0], 0) / ring.length;
    const lat = ring.reduce((s, q) => s + q[1], 0) / ring.length;
    const pt = map.project([lng, lat]);
    const score = p.krov_m2 / (1 + Math.hypot(pt.x - c.x, pt.y - c.y) / 60);
    if (!best || score > best.score) best = { score, lngLat: [lng, lat] };
  }
  return best;
}

function makePin(Marker, map, lngLat, bubble = '') {
  const el = document.createElement('div');
  el.className = 'hint-pin';
  el.innerHTML = `<span class="pulse"></span><span class="dot"></span>${bubble}`;
  return new Marker({ element: el, anchor: 'center' }).setLngLat(lngLat).addTo(map);
}

const TEXT = {
  lead: 'Koji krovovi u Zagrebu mogu postati zeleni ili proizvoditi struju iz sunca, i koliko bi to pomoglo gradu?',
  layer: ['Odaberite sloj', 'Zeleni krovovi ili fotonapon. Boja zgrade pokazuje koliko je krov pogodan.'],
  click: ['Kliknite zgradu', 'Za površinu zelenila, zadržanu kišnicu, snagu elektrane, trošak i povrat.'],
  compare: ['Usporedite četvrti', 'Ili potražite adresu. Scenarij pokazuje učinak ako se iskoristi 10 %, 30 % ili svi pogodni krovovi.'],
  caveat: 'Brojke su tehnički potencijal: gornja granica prije statičke provjere, zaštite kulturnih dobara i vlasničkih odnosa.',
};

// ---------------------------------------------------------------------------
// A · naslovnica u panelu
// ---------------------------------------------------------------------------
function panelIntro({ city, openAbout }) {
  const el = document.createElement('section');
  el.className = 'intro';
  el.innerHTML = `
    <p class="intro-lead">${TEXT.lead}</p>
    <p class="intro-fact">Iz otvorenog 3D modela Grada izračunali smo nagib i orijentaciju krovova za
      ${num(city.zgrade)} zgrada. Za zeleni krov pogodno je <b>${num(city.zk_kandidati)}</b> krovova,
      a za sunčanu elektranu <b>${num(city.fn_kandidati)}</b>.</p>
    <ol class="intro-steps">
      ${[TEXT.layer, TEXT.click, TEXT.compare].map(([t, d]) => `<li><b>${t}</b>${d}</li>`).join('')}
    </ol>
    <div class="intro-actions">
      <button type="button" class="primary" data-start>Istraži kartu</button>
      <button type="button" class="link-btn" data-about>Metodologija i izvori</button>
    </div>
    <p class="intro-note">${TEXT.caveat}</p>`;
  document.querySelector('#panel .brand').after(el);
  document.body.classList.add('intro-on');

  const close = () => {
    el.remove();
    document.body.classList.remove('intro-on');
    markSeen();
  };
  el.querySelector('[data-start]').addEventListener('click', close);
  el.querySelector('[data-about]').addEventListener('click', openAbout);
  return close;
}

// ---------------------------------------------------------------------------
// B · vođeni obilazak
// ---------------------------------------------------------------------------
function tour({ map, Marker, getMode }) {
  const steps = [
    { title: TEXT.layer[0], text: TEXT.layer[1], el: () => document.querySelector('#panel .mode') },
    { title: TEXT.click[0], text: TEXT.click[1], pin: true },
    { title: TEXT.compare[0], text: TEXT.compare[1], el: () => document.getElementById('search') },
  ];
  let i = 0;
  let pin = null;
  let target = null;

  const box = document.createElement('div');
  box.className = 'coach';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-live', 'polite');
  document.body.append(box);

  function place() {
    const s = steps[i];
    const bw = box.offsetWidth;
    const bh = box.offsetHeight;
    if (mobile()) {
      // na mobitelu uz vrh karte (preko legende); oznaka je niže, iznad donjeg panela
      box.dataset.side = 'none';
      Object.assign(box.style, { left: '12px', top: `${(document.querySelector('.topbar')?.offsetHeight ?? 0) + 12}px` });
      return;
    }
    let x;
    let y;
    let ay;
    if (s.pin && pin) {
      const p = map.project(pin.getLngLat());
      x = p.x + 30;
      y = p.y - 34;
      ay = 34;
    } else if (target) {
      const r = target.getBoundingClientRect();
      x = document.getElementById('panel').getBoundingClientRect().right + 18;
      y = r.top + r.height / 2 - 30;
      ay = 30;
    } else {
      const c = viewCenter();
      box.dataset.side = 'none';
      Object.assign(box.style, { left: `${c.x - bw / 2}px`, top: `${c.y - bh / 2}px` });
      return;
    }
    const maxY = window.innerHeight - bh - 12;
    const yy = Math.min(Math.max(y, 12), maxY);
    box.dataset.side = 'right';
    box.style.setProperty('--arrow-y', `${ay + (y - yy) + 4}px`);
    Object.assign(box.style, { left: `${Math.min(x, window.innerWidth - bw - 12)}px`, top: `${yy}px` });
  }

  function show() {
    const s = steps[i];
    target?.classList.remove('coach-target');
    target = s.el?.() ?? null;
    target?.classList.add('coach-target');
    pin?.remove();
    pin = null;
    if (s.pin) {
      const c = findCandidate(map, getMode());
      if (c) pin = makePin(Marker, map, c.lngLat);
    }
    const last = i === steps.length - 1;
    box.innerHTML = `
      <p class="coach-step">Korak ${i + 1} od ${steps.length}</p>
      <h3>${s.title}</h3>
      <p>${s.text}</p>
      <div class="coach-actions">
        <button type="button" class="coach-skip">${last ? '' : 'Preskoči uvod'}</button>
        <button type="button" class="primary coach-next">${last ? 'Kreni' : 'Dalje'}</button>
      </div>`;
    box.querySelector('.coach-next').addEventListener('click', () => (last ? close() : (i += 1, show())));
    box.querySelector('.coach-skip').addEventListener('click', close);
    place();
    box.querySelector('.coach-next').focus({ preventScroll: true });
  }

  const onMove = () => { if (steps[i].pin) place(); };
  map.on('move', onMove);
  window.addEventListener('resize', place);

  function close() {
    target?.classList.remove('coach-target');
    pin?.remove();
    box.remove();
    map.off('move', onMove);
    window.removeEventListener('resize', place);
    markSeen();
  }
  show();
  return close;
}

// ---------------------------------------------------------------------------
// C · oznaka na karti
// ---------------------------------------------------------------------------
function mapHint({ map, Marker, getMode }) {
  let pin = null;
  let tries = 0;

  const note = document.createElement('div');
  note.className = 'panel-hint';
  note.innerHTML = `
    <p><b>Kliknite bilo koju zgradu</b> za površinu zelenila, kišnicu, snagu elektrane i trošak.
      Četvrti ispod rangirane su po potencijalu.</p>
    <button type="button" class="icon-btn" aria-label="Sakrij uputu">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>`;
  document.querySelector('#panel .panel-body').prepend(note);

  function tryPin() {
    if (pin || tries > 6) return;
    tries += 1;
    const c = findCandidate(map, getMode());
    if (!c) return;
    pin = makePin(Marker, map, c.lngLat,
      '<span class="hint-bubble">Kliknite krov<small>npr. ovaj: velik i ravan</small></span>');
    map.off('idle', tryPin);
  }
  map.on('idle', tryPin);
  tryPin();

  function close() {
    pin?.remove();
    note.remove();
    map.off('idle', tryPin);
    markSeen();
  }
  note.querySelector('button').addEventListener('click', close);
  return close;
}

/** Pokreće uvod za odabrani prijedlog; zatvara se sam kad korisnik klikne zgradu. */
export function startOnboarding(theme, ctx) {
  const run = { atlas: panelIntro, grad: tour, teren: mapHint }[theme];
  if (!run || introSeen()) return;
  const close = run(ctx);
  document.addEventListener('kzk:building', close, { once: true });
}
