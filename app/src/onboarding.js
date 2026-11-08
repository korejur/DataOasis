// Uvod za prvi posjet: naslovnica u lijevom panelu umjesto prozora preko karte.
// Karta je odmah upotrebljiva; uvod se zatvara gumbom „Istraži kartu“ ili prvim klikom na zgradu.
import { num, plural } from './format.js';

const KEY = 'kzk-intro';

function seen() {
  try { return localStorage.getItem(KEY) === '1'; } catch { return false; }
}
function markSeen() {
  try { localStorage.setItem(KEY, '1'); } catch { /* privatni način rada */ }
}

const STEPS = [
  ['Odaberite sloj', 'Zeleni krovovi ili fotonapon. Boja zgrade pokazuje koliko je krov pogodan.'],
  ['Kliknite zgradu', 'Za površinu zelenila, zadržanu kišnicu, snagu elektrane, trošak i povrat.'],
  ['Usporedite četvrti', 'Ili potražite adresu. Scenarij pokazuje učinak ako se iskoristi 10 %, 30 % ili svi pogodni krovovi.'],
];

/** Prikazuje uvod ako ga korisnik još nije vidio. `city` daje brojke za grad. */
export function startOnboarding({ city }) {
  if (seen()) return;
  const el = document.createElement('section');
  el.className = 'intro';
  el.setAttribute('aria-label', 'Uvod');
  el.innerHTML = `
    <p class="intro-fact">Iz otvorenog 3D modela izračunati su nagib i orijentacija krovova za
      ${num(city.zgrade)} ${plural(city.zgrade, 'zgradu', 'zgrade', 'zgrada')} u Zagrebu. Za zeleni krov pogodno je
      <b>${num(city.zk_kandidati)}</b> ${plural(city.zk_kandidati, 'krov', 'krova', 'krovova')},
      a za sunčanu elektranu <b>${num(city.fn_kandidati)}</b>.</p>
    <ol class="intro-steps">
      ${STEPS.map(([t, d]) => `<li><b>${t}</b>${d}</li>`).join('')}
    </ol>
    <div class="intro-actions">
      <button type="button" class="primary" data-start>Istraži kartu</button>
    </div>
    <p class="intro-note">Brojke su tehnički potencijal: gornja granica prije statičke provjere,
      zaštite kulturnih dobara i vlasničkih odnosa.</p>`;
  document.querySelector('#panel .brand').after(el);
  document.body.classList.add('intro-on');

  const close = () => {
    el.remove();
    document.body.classList.remove('intro-on');
    markSeen();
  };
  el.querySelector('[data-start]').addEventListener('click', close);
  document.addEventListener('kzk:building', close, { once: true });
}
