// Oblikovanje brojeva na hrvatskom: decimalni zarez, tisućice odvojene uskim razmakom.
const NBSP = ' ';

const cache = new Map();
function fmt(digits) {
  if (!cache.has(digits)) {
    cache.set(digits, new Intl.NumberFormat('hr-HR', {
      minimumFractionDigits: digits, maximumFractionDigits: digits,
    }));
  }
  return cache.get(digits);
}

/** Broj s `d` decimala i razmakom za tisućice. */
export function num(v, d = 0) {
  if (v == null || Number.isNaN(v)) return '–';
  return fmt(d).formatToParts(v)
    .map((p) => (p.type === 'group' ? NBSP : p.value))
    .join('');
}

/** Veliki brojevi skraćeno: 5,9 mil., 1,74 mlrd. */
export function big(v) {
  if (v == null || Number.isNaN(v)) return '–';
  const a = Math.abs(v);
  if (a >= 1e9) return `${num(v / 1e9, a >= 1e10 ? 1 : 2)} mlrd.`;
  if (a >= 1e6) return `${num(v / 1e6, a >= 1e7 ? 0 : 1)} mil.`;
  if (a >= 1e4) return num(v, 0);
  if (a >= 100) return num(v, 0);
  if (a >= 10) return num(v, 1).replace(/,0$/, '');
  return num(v, 1).replace(/,0$/, '');
}

/** Iznos u eurima. */
export function eur(v) {
  if (!v) return '–';
  return `${v >= 1e6 ? big(v) : num(Math.round(v / 100) * 100)} €`;
}

/** Površina u hektarima (za usporedbu četvrti). */
export function ha(m2) {
  const h = m2 / 1e4;
  return `${h >= 100 ? num(h) : num(h, 1)} ha`;
}

/** Energija iz GWh u najprikladnijoj jedinici. */
export function gwh(v) {
  if (v >= 1000) return `${num(v / 1000, 2)} TWh`;
  if (v >= 1) return `${num(v, v >= 100 ? 0 : 1)} GWh`;
  return `${num(v * 1000)} MWh`;
}

/** kWh za jednu zgradu. */
export function kwh(v) {
  if (!v) return '–';
  if (v >= 1e6) return `${num(v / 1e6, 2)} GWh`;
  if (v >= 1e4) return `${num(v / 1e3, 0)} MWh`;
  return `${num(v)} kWh`;
}

/** Imenica uz broj: 1 zgrada, 2 zgrade, 5 zgrada. */
export function plural(n, one, few, many) {
  const n10 = n % 10, n100 = n % 100;
  if (n10 === 1 && n100 !== 11) return one;
  if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return few;
  return many;
}
