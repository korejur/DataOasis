// PRIVREMENO (grana aplikacija/redizajn): tri prijedloga izgleda za usporedbu, bira se s ?dizajn=…
// Nakon odabira ostaje jedan prijedlog, a ova datoteka, prekidač i themes.css se brišu.

export const THEMES = [
  { key: '', label: 'Sadašnji' },
  { key: 'atlas', label: 'A · Atlas' },
  { key: 'grad', label: 'B · Gradski servis' },
  { key: 'teren', label: 'C · Teren' },
];

export const theme = (() => {
  const t = new URLSearchParams(location.search).get('dizajn') ?? '';
  return THEMES.some((x) => x.key === t) ? t : '';
})();

if (theme) document.documentElement.dataset.theme = theme;

/** Prekidač za usporedbu prijedloga (samo na ovoj grani). */
export function mountSwitcher(resetIntro) {
  const nav = document.createElement('nav');
  nav.className = 'theme-switch';
  nav.setAttribute('aria-label', 'Prijedlozi izgleda');
  nav.innerHTML = `<span>Prijedlog</span>${THEMES.map((t) => `
    <button type="button" data-theme-key="${t.key}" aria-pressed="${t.key === theme}">${t.label}</button>`).join('')}
    <button type="button" data-reset>Ponovi uvod</button>`;
  nav.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    resetIntro();
    if (b.dataset.reset !== undefined) { location.reload(); return; }
    const url = new URL(location.href);
    if (b.dataset.themeKey) url.searchParams.set('dizajn', b.dataset.themeKey);
    else url.searchParams.delete('dizajn');
    location.href = url.href;
  });
  document.body.append(nav);
}

/** Gornja traka za prijedlog B (naslov i poveznice kao na stranici javne službe). */
export function mountTopbar(openAbout) {
  if (theme !== 'grad') return;
  const logo = document.querySelector('.brand-logo').outerHTML;
  const bar = document.createElement('header');
  bar.className = 'topbar';
  bar.innerHTML = `
    <a class="topbar-brand" href="./${location.search}">${logo}<span>Krovovi za klimu</span></a>
    <span class="topbar-sub">Zagreb · potencijal krovova za zelenilo i sunčane elektrane</span>
    <nav>
      <button type="button" data-about>O projektu i izvorima</button>
      <a href="https://github.com/korejur/DataOasis" target="_blank" rel="noopener">Izvorni kod</a>
    </nav>`;
  bar.querySelector('[data-about]').addEventListener('click', openAbout);
  document.body.prepend(bar);
}
