import 'maplibre-gl/dist/maplibre-gl.css';
import './style.css';

import {
  AttributionControl, GeolocateControl, Map as MapLibre, Marker, NavigationControl,
  addProtocol, setWorkerUrl,
} from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';
import { Protocol } from 'pmtiles';

import { renderCard } from './card.js';
import { gwh, ha } from './format.js';
import { LEGEND, fillColor, isCandidate } from './layers.js';
import { SORTS, renderDistricts, renderKpis, renderSortOptions } from './panel.js';
import { initSearch } from './search.js';

setWorkerUrl(workerUrl);
const protocol = new Protocol();
addProtocol('pmtiles', protocol.tile);

const STYLE_URL = 'https://tiles.openfreemap.org/styles/positron';
const dataUrl = (f) => new URL(`data/${f}`, document.baseURI).href;
const BUILDINGS_MINZOOM = 13;
const $ = (id) => document.getElementById(id);
const mobile = () => window.matchMedia('(max-width: 760px)').matches;

const state = {
  mode: 'zk',          // 'zk' zeleni krovovi | 'fn' fotonapon
  share: 1,            // scenarij: udio iskorištenih kandidata
  district: null,      // slug odabrane četvrti
  sort: { zk: SORTS.zk[0].key, fn: SORTS.fn[0].key },
  selected: null,      // id odabrane zgrade
  selectedProps: null,
  threeD: false,
};

let city;
let districts = [];
const bySlug = new Map();

// ---------------------------------------------------------------------------
// Karta
// ---------------------------------------------------------------------------
const map = new MapLibre({
  container: 'map',
  style: STYLE_URL,
  center: [15.9775, 45.8075],
  zoom: 14,
  minZoom: 9.5,
  maxZoom: 19,
  maxBounds: [[15.3, 45.45], [16.65, 46.15]],
  hash: true,
  attributionControl: false,
  dragRotate: true,
});
// registrira se odmah, da se događaj ne propusti dok se učitavaju JSON sažeci
const mapLoaded = new Promise((resolve) => map.once('load', resolve));
map.addControl(new AttributionControl({
  compact: true,
  customAttribution: 'ZG3D © Grad Zagreb · PVGIS © EU JRC',
}), 'bottom-right');
map.addControl(new NavigationControl({ visualizePitch: true }), 'top-right');
map.addControl(new GeolocateControl({ positionOptions: { enableHighAccuracy: true } }), 'top-right');

class ThreeDControl {
  onAdd() {
    this.el = document.createElement('div');
    this.el.className = 'maplibregl-ctrl maplibregl-ctrl-group';
    this.el.innerHTML = '<button type="button" class="ctrl-3d" aria-pressed="false" title="3D prikaz zgrada">3D</button>';
    this.el.querySelector('button').addEventListener('click', () => setThreeD(!state.threeD));
    return this.el;
  }
  onRemove() { this.el.remove(); }
}
map.addControl(new ThreeDControl(), 'top-right');

function firstSymbolLayer() {
  return map.getStyle().layers.find((l) => l.type === 'symbol')?.id;
}

function addLayers() {
  // OSM zgrade iz podloge zamjenjujemo našima; oznake cesta (brojevi) samo smetaju
  for (const l of map.getStyle().layers) {
    if (l['source-layer'] === 'building' || /shield/.test(l.id)) map.setLayoutProperty(l.id, 'visibility', 'none');
  }
  const before = firstSymbolLayer();

  map.addSource('bld', {
    type: 'vector',
    url: `pmtiles://${dataUrl('buildings.pmtiles')}`,
    attribution: '',
  });
  const src = { source: 'bld', 'source-layer': 'buildings', minzoom: BUILDINGS_MINZOOM };

  map.addLayer({
    id: 'bld-fill', type: 'fill', ...src,
    paint: { 'fill-color': fillColor.zk, 'fill-opacity': opacityExpr() },
  }, before);
  map.addLayer({
    id: 'bld-line', type: 'line', ...src, minzoom: 15,
    paint: {
      'line-color': '#ffffff',
      'line-width': ['interpolate', ['linear'], ['zoom'], 15, 0.3, 18, 1.2],
      'line-opacity': 0.8,
    },
  }, before);
  map.addLayer({
    id: 'bld-3d', type: 'fill-extrusion', ...src,
    layout: { visibility: 'none' },
    paint: {
      'fill-extrusion-color': fillColor.zk,
      'fill-extrusion-height': ['get', 'h'],
      'fill-extrusion-opacity': 0.92,
      'fill-extrusion-vertical-gradient': true,
    },
  });
  map.addLayer({
    id: 'bld-sel', type: 'line', ...src,
    filter: ['==', ['get', 'id'], ''],
    paint: {
      'line-color': '#0d1b14',
      'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1.5, 17, 3],
    },
  });

  // Pregled po četvrtima ispod zuma 13 (granice četvrti još nisu predane)
  map.addSource('districts', { type: 'geojson', data: districtsGeojson() });
  const fade = ['interpolate', ['linear'], ['zoom'], 12.4, 1, 13.1, 0];
  map.addLayer({
    id: 'd-circle', type: 'circle', source: 'districts', maxzoom: 13.2,
    paint: {
      'circle-radius': circleRadius(),
      'circle-color': state.mode === 'zk' ? '#2f9a55' : '#ef8a1f',
      'circle-opacity': ['interpolate', ['linear'], ['zoom'], 12.4, 0.55, 13.1, 0],
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 1.5,
      'circle-stroke-opacity': fade,
    },
  });
  map.addLayer({
    id: 'd-label', type: 'symbol', source: 'districts', maxzoom: 13.2,
    layout: {
      'text-field': ['format', ['get', 'naziv'], { 'font-scale': 1 }, '\n', {},
        ['get', `lbl_${state.mode}`], { 'font-scale': 0.85, 'text-font': ['literal', ['Noto Sans Regular']] }],
      'text-font': ['Noto Sans Bold'],
      'text-size': 12.5,
      'text-line-height': 1.25,
      'text-variable-anchor': ['center', 'top', 'bottom', 'left', 'right'],
      'text-radial-offset': 0.6,
      'text-padding': 2,
    },
    paint: {
      'text-color': '#13281c',
      'text-halo-color': 'rgba(255,255,255,0.92)',
      'text-halo-width': 1.6,
      'text-opacity': fade,
    },
  });

  for (const id of ['bld-fill', 'bld-3d']) {
    map.on('click', id, (e) => selectBuilding(e.features[0]?.properties));
    map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
  }
  for (const id of ['d-circle', 'd-label']) {
    map.on('click', id, (e) => {
      const slug = e.features[0]?.properties.slug;
      if (slug) selectDistrict(slug, { fly: true });
    });
    map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
  }
}

function opacityExpr() {
  const name = state.district ? bySlug.get(state.district)?.naziv : null;
  const cand = isCandidate[state.mode];
  const base = ['case', cand, 0.92, 0.6];
  if (!name) return base;
  return ['case', ['==', ['get', 'cetvrt'], name], base, 0.18];
}

const metricFor = (mode) => (mode === 'zk' ? 'zk_iskoristivo_m2' : 'fn_proizvodnja_GWh_god');

function circleRadius() {
  const key = metricFor(state.mode);
  const max = Math.max(...districts.map((d) => d[key]));
  return ['interpolate', ['linear'], ['zoom'],
    10, ['*', 30, ['sqrt', ['/', ['get', key], max]]],
    13, ['*', 60, ['sqrt', ['/', ['get', key], max]]]];
}

function districtsGeojson() {
  return {
    type: 'FeatureCollection',
    features: districts.map((d) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: d.centar },
      properties: {
        slug: d.slug,
        naziv: d.naziv,
        zk_iskoristivo_m2: d.zk_iskoristivo_m2,
        fn_proizvodnja_GWh_god: d.fn_proizvodnja_GWh_god,
        lbl_zk: `${ha(d.zk_iskoristivo_m2 * state.share)} zelenila`,
        lbl_fn: `${gwh(d.fn_proizvodnja_GWh_god * state.share)}/god.`,
      },
    })),
  };
}

function refreshMapStyle() {
  if (!map.getLayer('bld-fill')) return;
  map.setPaintProperty('bld-fill', 'fill-color', fillColor[state.mode]);
  map.setPaintProperty('bld-fill', 'fill-opacity', opacityExpr());
  map.setPaintProperty('bld-3d', 'fill-extrusion-color', fillColor[state.mode]);
  map.setPaintProperty('d-circle', 'circle-color', state.mode === 'zk' ? '#2f9a55' : '#ef8a1f');
  map.setPaintProperty('d-circle', 'circle-radius', circleRadius());
  map.getSource('districts').setData(districtsGeojson());
  map.setLayoutProperty('d-label', 'text-field', ['format', ['get', 'naziv'], { 'font-scale': 1 }, '\n', {},
    ['get', `lbl_${state.mode}`], { 'font-scale': 0.85, 'text-font': ['literal', ['Noto Sans Regular']] }]);
}

function applyThreeD() {
  const on = state.threeD;
  document.querySelector('.ctrl-3d')?.setAttribute('aria-pressed', String(on));
  if (!map.getLayer('bld-3d')) return;
  map.setLayoutProperty('bld-3d', 'visibility', on ? 'visible' : 'none');
  map.setLayoutProperty('bld-fill', 'visibility', on ? 'none' : 'visible');
  map.setLayoutProperty('bld-line', 'visibility', on ? 'none' : 'visible');
}

function setThreeD(on) {
  state.threeD = on;
  applyThreeD();
  map.easeTo({
    pitch: on ? 55 : 0,
    bearing: on ? map.getBearing() || -17 : 0,
    zoom: on ? Math.max(map.getZoom(), 15) : map.getZoom(),
    duration: 900,
  });
}

// ---------------------------------------------------------------------------
// Odabir zgrade i četvrti
// ---------------------------------------------------------------------------
const card = $('card');
const cardBody = $('card-body');

function selectBuilding(props) {
  if (!props) return;
  state.selected = props.id;
  state.selectedProps = props;
  map.setFilter('bld-sel', ['==', ['get', 'id'], props.id]);
  cardBody.innerHTML = renderCard(props, state.mode);
  card.hidden = false;
  card.scrollTop = 0;
  document.body.classList.add('has-card');
}

function closeCard() {
  state.selected = null;
  state.selectedProps = null;
  if (map.getLayer('bld-sel')) map.setFilter('bld-sel', ['==', ['get', 'id'], '']);
  card.hidden = true;
  document.body.classList.remove('has-card');
}
$('card-close').addEventListener('click', closeCard);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !card.hidden && !$('about').open) closeCard();
});

function fitPadding() {
  if (mobile()) return { top: 40, bottom: window.innerHeight * 0.35, left: 20, right: 20 };
  return { top: 40, bottom: 40, left: $('panel').offsetWidth + 40, right: card.hidden ? 60 : card.offsetWidth + 40 };
}

function selectDistrict(slug, { fly = false } = {}) {
  state.district = slug;
  const d = slug ? bySlug.get(slug) : null;
  if (fly && d) {
    map.fitBounds([[d.bbox[0], d.bbox[1]], [d.bbox[2], d.bbox[3]]], { padding: fitPadding(), duration: 1200, maxZoom: 15.5 });
  }
  renderPanel();
  refreshMapStyle();
  document.querySelector('.panel-body').scrollTo({ top: 0, behavior: 'smooth' });
}

// ---------------------------------------------------------------------------
// Panel, legenda, način prikaza
// ---------------------------------------------------------------------------
function renderPanel() {
  const d = state.district ? bySlug.get(state.district) : city;
  $('summary-title').textContent = state.district ? d.naziv : 'Cijeli grad';
  $('back-city').hidden = !state.district;
  renderKpis($('kpis'), $('kpi-note'), d, state.mode, state.share, city.parametri);
  renderSortOptions($('district-sort'), state.mode, state.sort[state.mode]);
  renderDistricts($('district-list'), districts, state.mode, state.sort[state.mode], state.share, state.district);
}

function renderLegend() {
  const L = LEGEND[state.mode];
  $('legend').innerHTML = `
    <h3>${L.title}</h3>
    <ul>${L.items.map((i) => `<li><i style="background:${i.color}"></i><span><b>${i.label}</b> <small>${i.desc}</small></span></li>`).join('')}</ul>
    <p>${L.foot}</p>`;
}

function setMode(mode) {
  state.mode = mode;
  document.body.dataset.mode = mode;
  for (const b of document.querySelectorAll('.mode-btn')) b.setAttribute('aria-selected', String(b.dataset.mode === mode));
  renderPanel();
  renderLegend();
  refreshMapStyle();
  if (state.selectedProps) cardBody.innerHTML = renderCard(state.selectedProps, mode);
}

for (const b of document.querySelectorAll('.mode-btn')) b.addEventListener('click', () => setMode(b.dataset.mode));

$('scenario').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-share]');
  if (!b) return;
  state.share = +b.dataset.share;
  for (const x of $('scenario').querySelectorAll('button')) x.setAttribute('aria-checked', String(x === b));
  renderPanel();
  refreshMapStyle();
});

$('district-sort').addEventListener('change', (e) => {
  state.sort[state.mode] = e.target.value;
  renderPanel();
});

$('district-list').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-slug]');
  if (!b) return;
  const slug = b.dataset.slug;
  if (slug === state.district) selectDistrict(null);
  else {
    selectDistrict(slug, { fly: true });
    if (mobile()) document.body.classList.remove('panel-open');
  }
});
$('back-city').addEventListener('click', () => {
  selectDistrict(null);
  map.flyTo({ center: [15.98, 45.81], zoom: 11.3, duration: 1200 });
});

$('panel-handle').addEventListener('click', () => document.body.classList.toggle('panel-open'));

// Napomena o zumu
function updateZoomHint() {
  $('zoom-hint').hidden = map.getZoom() >= BUILDINGS_MINZOOM - 0.05;
}
map.on('zoomend', updateZoomHint);

// ---------------------------------------------------------------------------
// Pretraga
// ---------------------------------------------------------------------------
let searchMarker;
function goToPlace({ lon, lat }) {
  searchMarker?.remove();
  searchMarker = new Marker({ color: '#0d1b14' }).setLngLat([lon, lat]).addTo(map);
  map.flyTo({ center: [lon, lat], zoom: 17.5, duration: 1500, padding: fitPadding() });
  map.once('idle', () => {
    const pt = map.project([lon, lat]);
    const box = [[pt.x - 6, pt.y - 6], [pt.x + 6, pt.y + 6]];
    const hit = map.queryRenderedFeatures(box, { layers: [state.threeD ? 'bld-3d' : 'bld-fill'] })[0];
    if (hit) selectBuilding(hit.properties);
  });
  if (mobile()) document.body.classList.remove('panel-open');
}

// ---------------------------------------------------------------------------
// Uvodni ekran
// ---------------------------------------------------------------------------
const about = $('about');
$('open-about').addEventListener('click', () => about.showModal());
about.addEventListener('click', (e) => { if (e.target === about) about.close(); });
about.addEventListener('close', () => {
  try { localStorage.setItem('kzk-intro', '1'); } catch { /* privatni način rada */ }
});
let seen = false;
try { seen = localStorage.getItem('kzk-intro') === '1'; } catch { /* ignore */ }
if (!seen) about.showModal();

// ---------------------------------------------------------------------------
// Pokretanje
// ---------------------------------------------------------------------------
async function init() {
  const [c, d] = await Promise.all([
    fetch(dataUrl('city.json')).then((r) => r.json()),
    fetch(dataUrl('districts.json')).then((r) => r.json()),
  ]);
  city = c;
  districts = d;
  for (const x of districts) bySlug.set(x.slug, x);

  document.body.dataset.mode = state.mode;
  renderPanel();
  renderLegend();
  initSearch({
    form: $('search'), input: $('search-input'), list: $('search-results'), districts,
    onDistrict: (x) => selectDistrict(x.slug, { fly: true }),
    onPlace: goToPlace,
  });

  await mapLoaded;
  addLayers();
  syncThreeD();
  map.on('pitchend', syncThreeD);
  updateZoomHint();
  // sažeta atribucija (MapLibre je na početku otvara)
  document.querySelector('.maplibregl-ctrl-attrib')?.classList.remove('maplibregl-compact-show');
}

/** 3D prikaz prati nagib karte (gumb, desni klik + povlačenje, poveznica s nagibom). */
function syncThreeD() {
  const want = map.getPitch() > 10;
  if (want !== state.threeD) { state.threeD = want; applyThreeD(); }
}

init().catch((err) => {
  console.error(err);
  $('kpis').innerHTML = '<p class="error">Podaci se nisu učitali. Osvježite stranicu.</p>';
});

// za otklanjanje grešaka u konzoli
window.__kzk = { map, state };
