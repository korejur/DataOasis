// Boje, izrazi za stil karte i sadržaj legende za oba sloja.

export const COLORS = {
  zk: { visoka: '#17803d', srednja: '#6fc274', niska: '#d6cc85', nije: '#cdd2d6' },
  fn: { odlican: '#de5a12', dobar: '#f4a12c', umjeren: '#fbd789', nije: '#cdd2d6' },
};

// Granice specifičnog prinosa FN [kWh/kWp godišnje]. Ravni krovovi s modulima na
// nosačima (15° prema jugu) daju ~1174, optimum za Zagreb je 1242 (PVGIS).
export const FN_BREAKS = { dobar: 1050, odlican: 1150 };

const isFn = ['==', ['get', 'fn'], 1];

export const fillColor = {
  zk: ['match', ['get', 'zk'],
    'visoka', COLORS.zk.visoka,
    'srednja', COLORS.zk.srednja,
    'niska', COLORS.zk.niska,
    COLORS.zk.nije],
  fn: ['case',
    ['!', isFn], COLORS.fn.nije,
    ['>=', ['get', 'fn_prinos'], FN_BREAKS.odlican], COLORS.fn.odlican,
    ['>=', ['get', 'fn_prinos'], FN_BREAKS.dobar], COLORS.fn.dobar,
    COLORS.fn.umjeren],
};

/** Je li zgrada kandidat u odabranom sloju (za prozirnost). */
export const isCandidate = {
  zk: ['match', ['get', 'zk'], ['visoka', 'srednja'], true, false],
  fn: isFn,
};

export const LEGEND = {
  zk: {
    title: 'Pogodnost za zeleni krov',
    items: [
      { color: COLORS.zk.visoka, label: 'Visoka', desc: 'pretežno ravan krov (0–10°)' },
      { color: COLORS.zk.srednja, label: 'Srednja', desc: 'blagi nagib (10–20°)' },
      { color: COLORS.zk.niska, label: 'Niska', desc: '20–35°, samo uz zaštitu od klizanja' },
      { color: COLORS.zk.nije, label: 'Nije pogodno', desc: 'strm krov ili premala površina' },
    ],
    foot: 'Pogodan krov ima barem 50 m² površine nagiba do 20°.',
  },
  fn: {
    title: 'Prinos sunčane elektrane',
    items: [
      { color: COLORS.fn.odlican, label: 'Odličan', desc: `≥ ${FN_BREAKS.odlican} kWh po kWp godišnje` },
      { color: COLORS.fn.dobar, label: 'Dobar', desc: `${FN_BREAKS.dobar}–${FN_BREAKS.odlican} kWh/kWp` },
      { color: COLORS.fn.umjeren, label: 'Umjeren', desc: `900–${FN_BREAKS.dobar} kWh/kWp` },
      { color: COLORS.fn.nije, label: 'Nije pogodno', desc: 'manje od 3 kWp ili loša orijentacija' },
    ],
    foot: 'Prinos prema PVGIS-u za nagib i orijentaciju svake plohe.',
  },
};
