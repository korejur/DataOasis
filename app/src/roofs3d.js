// Eksperiment: stvarna 3D geometrija krovova (kose plohe + zidovi do tla) kao WebGL sloj.
//
// MapLibre `fill-extrusion` zna samo prizme s ravnim vrhom („kocke“). Ovdje se iz sloja
// krovnih ravnina (planes.pmtiles) za svaku plohu računa visina u svakom vrhu iz jednadžbe
// ravnine h = z0 + gx·dx + gy·dy (dx, dy u metrima od referentne točke plohe), krov se
// triangulira (earcut), a ispod svakog ruba plohe spušta se zid do tla. Zidovi unutar zgrade
// (između ploha) skriveni su ispod krova, a vanjski zatvaraju zgradu, uključivo i zabate.
import earcut from 'earcut';
import { COLORS, FN_BREAKS, PLANE_BAD } from './layers.js';

export const ROOFS_MINZOOM = 15;
const LIGHT = normalize([-0.35, -0.55, 0.76]); // svjetlo s jugozapada, visoko (istok, sjever, gore)
const M_PER_DEG_LAT = 110574;

function normalize(v) { const l = Math.hypot(...v) || 1; return v.map((x) => x / l); }
function rgb(hex) { const n = parseInt(hex.slice(1), 16); return [(n >> 16) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]; }

const C = {
  fn: { odlican: rgb(COLORS.fn.odlican), dobar: rgb(COLORS.fn.dobar), umjeren: rgb(COLORS.fn.umjeren), nije: rgb(COLORS.fn.nije), bad: rgb(PLANE_BAD) },
  zk: { visoka: rgb(COLORS.zk.visoka), srednja: rgb(COLORS.zk.srednja), niska: rgb(COLORS.zk.niska), nije: rgb(COLORS.zk.nije) },
};

function planeRgb(p, mode) {
  if (mode === 'zk') {
    const s = p.s ?? 0;
    return s <= 10 ? C.zk.visoka : s <= 20 ? C.zk.srednja : s <= 35 ? C.zk.niska : C.zk.nije;
  }
  if (p.c === 0) return C.fn.nije;
  if (p.c === 1) return C.fn.bad;
  return p.y >= FN_BREAKS.odlican ? C.fn.odlican : p.y >= FN_BREAKS.dobar ? C.fn.dobar : C.fn.umjeren;
}

const mercX = (lng) => (lng + 180) / 360;
const mercY = (lat) => (1 - Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360)) / Math.PI) / 2;

const VS = `#version 300 es
uniform mat4 u_matrix;
uniform float u_zscale;
in vec3 a_pos;
in vec3 a_color;
out vec3 v_color;
void main() {
  gl_Position = u_matrix * vec4(a_pos.xy, a_pos.z * u_zscale, 1.0);
  v_color = a_color;
}`;
const FS = `#version 300 es
precision mediump float;
in vec3 v_color;
out vec4 fragColor;
void main() { fragColor = vec4(v_color, 1.0); }`;

export class RoofsLayer {
  /** @param getView () => ({ mode, pub }) */
  constructor(getView) {
    this.id = 'roofs-3d';
    this.type = 'custom';
    this.renderingMode = '3d';
    this.getView = getView;
    this.active = false;
    this.count = 0;
    this.timer = null;
  }

  onAdd(map, gl) {
    this.map = map;
    const sh = (type, src) => {
      const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(s));
      return s;
    };
    this.prog = gl.createProgram();
    gl.attachShader(this.prog, sh(gl.VERTEX_SHADER, VS));
    gl.attachShader(this.prog, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(this.prog);
    this.loc = {
      pos: gl.getAttribLocation(this.prog, 'a_pos'), color: gl.getAttribLocation(this.prog, 'a_color'),
      matrix: gl.getUniformLocation(this.prog, 'u_matrix'), zscale: gl.getUniformLocation(this.prog, 'u_zscale'),
    };
    this.buf = gl.createBuffer();
    this.gl = gl;
    this.onData = (e) => { if (e.sourceId === 'pl' && e.tile) this.schedule(); };
    map.on('sourcedata', this.onData);
    map.on('moveend', () => this.schedule());
  }

  onRemove(map, gl) {
    map.off('sourcedata', this.onData);
    gl.deleteBuffer(this.buf);
    gl.deleteProgram(this.prog);
  }

  setActive(on) {
    this.active = on;
    this.schedule(0);
    this.map?.triggerRepaint();
  }

  schedule(ms = 150) {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.rebuild(), ms);
  }

  isOn() { return this.active && this.map && this.map.getZoom() >= ROOFS_MINZOOM; }

  rebuild() {
    if (!this.isOn()) { this.count = 0; this.map?.triggerRepaint(); return; }
    const { mode, pub } = this.getView();
    const feats = this.map.querySourceFeatures('pl', { sourceLayer: 'planes' });
    const c = this.map.getCenter();
    this.ox = mercX(c.lng); this.oy = mercY(c.lat);
    // metar u jedinicama Mercatora na ovoj širini
    this.zscale = 1 / (40075016.686 * Math.cos((c.lat * Math.PI) / 180));
    const out = [];
    const push = (x, y, z, col, k) => out.push(x, y, z, col[0] * k, col[1] * k, col[2] * k);
    for (const f of feats) {
      const p = f.properties;
      if (pub && p.j !== 1) continue;
      if (p.x0 == null) continue;
      const lng0 = p.x0 / 1e7, lat0 = p.y0 / 1e7, z0 = p.z0 / 100, gx = p.gx / 1e4, gy = p.gy / 1e4;
      const kx = Math.cos((lat0 * Math.PI) / 180) * 111320;
      const h = (lng, lat) => Math.max(0, z0 + gx * (lng - lng0) * kx + gy * (lat - lat0) * M_PER_DEG_LAT);
      const col = planeRgb(p, mode);
      const n = normalize([-gx, -gy, 1]);
      const roofShade = 0.62 + 0.38 * Math.max(0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]);
      const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.type === 'MultiPolygon' ? f.geometry.coordinates : [];
      for (const rings of polys) {
        // krov: triangulacija u lokalnim metrima, visina iz jednadžbe ravnine
        const flat = [], holes = [], pts = [];
        for (const ring of rings) {
          if (pts.length) holes.push(pts.length);
          for (let i = 0; i < ring.length - 1; i++) {
            const [lng, lat] = ring[i];
            flat.push((lng - lng0) * kx, (lat - lat0) * M_PER_DEG_LAT);
            pts.push([mercX(lng) - this.ox, mercY(lat) - this.oy, h(lng, lat)]);
          }
        }
        const tri = earcut(flat, holes.length ? holes : undefined, 2);
        for (const i of tri) push(pts[i][0], pts[i][1], pts[i][2], col, roofShade);
        // zidovi: ispod svakog ruba plohe do tla
        for (const ring of rings) {
          for (let i = 0; i < ring.length - 1; i++) {
            const [l1, a1] = ring[i], [l2, a2] = ring[i + 1];
            const x1 = mercX(l1) - this.ox, y1 = mercY(a1) - this.oy, x2 = mercX(l2) - this.ox, y2 = mercY(a2) - this.oy;
            const z1 = h(l1, a1), z2 = h(l2, a2);
            if (z1 < 0.05 && z2 < 0.05) continue;
            const ex = (l2 - l1) * kx, ey = (a2 - a1) * M_PER_DEG_LAT;
            const len = Math.hypot(ex, ey) || 1;
            const d = Math.abs((ey / len) * LIGHT[0] - (ex / len) * LIGHT[1]);
            const k = 0.5 + 0.32 * d;
            push(x1, y1, z1, col, k); push(x2, y2, z2, col, k); push(x2, y2, 0, col, k * 0.85);
            push(x1, y1, z1, col, k); push(x2, y2, 0, col, k * 0.85); push(x1, y1, 0, col, k * 0.85);
          }
        }
      }
    }
    const gl = this.gl;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(out), gl.STATIC_DRAW);
    this.count = out.length / 6;
    this.map.triggerRepaint();
  }

  render(gl, args) {
    if (!this.count || !this.isOn()) return;
    // matrica relativno na ishodište mreže (preciznost float32 na razini centimetra)
    const m = args.defaultProjectionData.mainMatrix; // Mercator 0..1 -> clip
    const r = Float32Array.from(m);
    for (let i = 0; i < 4; i++) r[12 + i] = m[i] * this.ox + m[4 + i] * this.oy + m[12 + i];
    gl.useProgram(this.prog);
    gl.uniformMatrix4fv(this.loc.matrix, false, r);
    gl.uniform1f(this.loc.zscale, this.zscale);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
    gl.enableVertexAttribArray(this.loc.pos);
    gl.vertexAttribPointer(this.loc.pos, 3, gl.FLOAT, false, 24, 0);
    gl.enableVertexAttribArray(this.loc.color);
    gl.vertexAttribPointer(this.loc.color, 3, gl.FLOAT, false, 24, 12);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.depthMask(true);
    gl.disable(gl.BLEND);
    gl.disable(gl.CULL_FACE);
    gl.drawArrays(gl.TRIANGLES, 0, this.count);
  }
}
