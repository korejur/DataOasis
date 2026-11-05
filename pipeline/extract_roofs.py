"""Ekstrakcija krovnih ploha iz ZG3D LoD2.2 modela (FGDB, multipatch).

Svaka zgrada u FGDB-u je skup 3D ploha (krov, zidovi, tlo). Za svaku plohu
računamo normalu (Newellova metoda), pa iz nje nagib, orijentaciju i stvarnu
(3D) površinu. Plohe se klasificiraju na:

* krov  - normala prema gore, nagib < ~80°, iznad razine tla zgrade
* zid   - (gotovo) okomita ploha
* ostalo - tlo zgrade i donje strane prepusta (normala prema dolje)

Napomena o orijentaciji: prstenovi su zapisani u Esri konvenciji (u smjeru
kazaljke na satu gledano izvana), pa je vanjska normala = -Newell normala.
To je provjereno na uzorku: ~99,8 % ploha iznad tla ima tako izračunatu
normalu prema gore.

Izlaz po četvrti:
    data/processed/faces/<slug>.parquet      krovne plohe (3D poligoni, EPSG:3765)
    data/processed/buildings/<slug>.parquet  zgrade (tlocrt krova, EPSG:3765)

    python -m pipeline.extract_roofs              # sve preuzete četvrti
    python -m pipeline.extract_roofs trnje maksimir
"""
from __future__ import annotations

import json
import struct
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely
from pyproj import Transformer

from .config import (BUILDINGS_DIR, CRS_METRIC, CRS_WGS84, DISTRICTS, FACES_DIR,
                     GEOM, RAW_ZG3D)

warnings.filterwarnings("ignore", message=".*Measured \\(M\\) geometry.*")


# --------------------------------------------------------------------------- #
# WKB parser
# GEOS/shapely ne podržava TIN/PolyhedralSurface, a GDAL multipatch pretvara u
# GeometryCollection(TIN, Polygon, ...). Zato čitamo WKB ručno.
# --------------------------------------------------------------------------- #
def parse_faces(b: bytes) -> list[list[np.ndarray]]:
    """Vrati listu ploha; ploha = lista prstenova (n x 3), prvi je vanjski."""
    faces: list[list[np.ndarray]] = []

    def rd(o: int) -> int:
        e = "<" if b[o] == 1 else ">"
        t = struct.unpack_from(e + "I", b, o + 1)[0]
        o += 5
        iso = t & 0x0FFFFFFF
        hasz = bool(t & 0x80000000) or (iso // 1000) in (1, 3)
        hasm = bool(t & 0x40000000) or (iso // 1000) in (2, 3)
        base = iso % 1000
        dim = 2 + hasz + hasm
        if base in (3, 17):  # Polygon, Triangle
            nr = struct.unpack_from(e + "I", b, o)[0]
            o += 4
            rings = []
            for _ in range(nr):
                n = struct.unpack_from(e + "I", b, o)[0]
                o += 4
                a = np.frombuffer(b, dtype=e + "f8", count=n * dim, offset=o).reshape(n, dim)
                o += 8 * n * dim
                if not hasz:
                    raise ValueError("Geometrija bez Z koordinate")
                rings.append(a[:, :3])
            faces.append(rings)
            return o
        if base in (6, 7, 15, 16):  # MultiPolygon, GeometryCollection, PolyhedralSurface, TIN
            n = struct.unpack_from(e + "I", b, o)[0]
            o += 4
            for _ in range(n):
                o = rd(o)
            return o
        raise ValueError(f"Nepodržani WKB tip {t}")

    rd(0)
    return faces


# --------------------------------------------------------------------------- #
def process_district(slug: str) -> dict:
    t0 = time.time()
    meta_raw = json.loads((RAW_ZG3D / slug / "meta.json").read_text(encoding="utf-8"))
    # FGDB, ili SHP ako FGDB nije čitljiv (vidi download.ensure_readable)
    src = RAW_ZG3D / slug / (meta_raw.get("shp") or meta_raw["gdb"])
    district_name = DISTRICTS[slug][1]

    meta, fids, geoms, fields = pyogrio.raw.read(src, return_fids=True)
    attrs = pd.DataFrame({name: col for name, col in zip(meta["fields"], fields)})
    attrs["fid"] = fids

    # --- 1) raspakiraj sve prstenove u ravne nizove --------------------------
    pts, ring_len, ring_face, ring_ext, face_bldg = [], [], [], [], []
    bldg_rows = []
    face_counter = 0
    for i, g in enumerate(geoms):
        if g is None:
            continue
        faces = parse_faces(bytes(g))
        faces = [f for f in faces if len(f[0]) >= 4]
        if not faces:
            continue
        b = len(bldg_rows)
        bldg_rows.append(i)
        for rings in faces:
            for k, r in enumerate(rings):
                if len(r) < 4:
                    continue
                pts.append(r)
                ring_len.append(len(r))
                ring_face.append(face_counter)
                ring_ext.append(k == 0)
            face_bldg.append(b)
            face_counter += 1

    P = np.concatenate(pts)
    ring_len = np.asarray(ring_len)
    ring_face = np.asarray(ring_face)
    ring_ext = np.asarray(ring_ext)
    face_bldg = np.asarray(face_bldg)
    bldg_rows = np.asarray(bldg_rows)
    n_faces = face_counter

    # --- 2) projekcija u HTRS96/TM (metri) -----------------------------------
    # Četvrti nisu objavljene u istom CRS-u (većina EPSG:4326, neke EPSG:3765)
    src_crs = meta.get("crs") or CRS_WGS84
    if src_crs == CRS_METRIC:
        x, y = P[:, 0].astype(float), P[:, 1].astype(float)
    else:
        tr = Transformer.from_crs(src_crs, CRS_METRIC, always_xy=True)
        x, y = tr.transform(P[:, 0], P[:, 1])
    z = P[:, 2].astype(float)

    # --- 3) Newellova normala po prstenu (vektorizirano) ---------------------
    ring_start = np.concatenate([[0], np.cumsum(ring_len)[:-1]])
    nxt = np.arange(1, len(x) + 1)
    nxt[-1] = 0
    seg_valid = np.ones(len(x), bool)
    seg_valid[ring_start + ring_len - 1] = False  # zadnja točka prstena -> nema segmenta
    xn, yn, zn = x[nxt], y[nxt], z[nxt]
    cx = np.where(seg_valid, (y - yn) * (z + zn), 0.0)
    cy = np.where(seg_valid, (z - zn) * (x + xn), 0.0)
    cz = np.where(seg_valid, (x - xn) * (y + yn), 0.0)
    rv = 0.5 * np.stack([np.add.reduceat(cx, ring_start),
                         np.add.reduceat(cy, ring_start),
                         np.add.reduceat(cz, ring_start)], axis=1)
    ring_area = np.linalg.norm(rv, axis=1)

    # površina plohe = vanjski prsten - rupe; smjer iz vanjskog prstena
    face_area = np.zeros(n_faces)
    np.add.at(face_area, ring_face, np.where(ring_ext, ring_area, -ring_area))
    ext_idx = np.flatnonzero(ring_ext)          # točno jedan vanjski prsten po plohi
    ext_vec = rv[ext_idx]
    ext_norm = np.linalg.norm(ext_vec, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        normal = -ext_vec / ext_norm[:, None]   # Esri: vanjska normala = -Newell

    # z statistike po plohi (iz vanjskog prstena); reduceat po svim prstenovima
    # daje točno jedan segment po prstenu, zatim uzimamo vanjske
    r_zmin = np.minimum.reduceat(z, ring_start)
    r_zmax = np.maximum.reduceat(z, ring_start)
    r_zsum = np.add.reduceat(z, ring_start)
    es = ring_start[ext_idx]
    f_zmin = r_zmin[ext_idx]
    f_zmax = r_zmax[ext_idx]
    # zadnja točka prstena = prva, ne smije se brojati dvaput u prosjeku
    f_zmean = (r_zsum[ext_idx] - z[es]) / (ring_len[ext_idx] - 1)

    # --- 4) klasifikacija ----------------------------------------------------
    nz = normal[:, 2]
    b_zmin = np.full(len(bldg_rows), np.inf)
    np.minimum.at(b_zmin, face_bldg, f_zmin)
    b_zmax = np.full(len(bldg_rows), -np.inf)
    np.maximum.at(b_zmax, face_bldg, f_zmax)

    ok = np.isfinite(nz) & (face_area > GEOM["min_face_area"])
    above = (f_zmax - b_zmin[face_bldg]) > GEOM["min_roof_height"]

    # Provjera orijentacije po zgradi: kod ispravno orijentirane zgrade plohe
    # iznad tla s normalom prema gore (krov) imaju veću površinu od onih s
    # normalom prema dolje (prepusti). Ako je obrnuto, zgrada je zapisana s
    # obrnutim redoslijedom točaka -> okreni sve normale te zgrade.
    up = ok & above & (nz > GEOM["wall_nz"])
    down = ok & above & (nz < -GEOM["wall_nz"])
    a_up = np.bincount(face_bldg[up], weights=face_area[up], minlength=len(bldg_rows))
    a_dn = np.bincount(face_bldg[down], weights=face_area[down], minlength=len(bldg_rows))
    flip_b = a_dn > a_up
    flip_f = flip_b[face_bldg]
    normal[flip_f] *= -1
    nz = normal[:, 2]

    is_wall = ok & (np.abs(nz) <= GEOM["wall_nz"])
    is_roof = ok & (nz > GEOM["wall_nz"]) & above

    slope = np.degrees(np.arccos(np.clip(nz, -1, 1)))
    azimuth = (np.degrees(np.arctan2(normal[:, 0], normal[:, 1])) + 360.0) % 360.0
    azimuth = np.where(slope < 2.0, np.nan, azimuth)  # ravne plohe nemaju orijentaciju

    # --- 5) geometrija krovnih ploha ------------------------------------------
    roof_faces = np.flatnonzero(is_roof)
    ring_is_roof = is_roof[ring_face]
    point_ring = np.repeat(np.arange(len(ring_len)), ring_len)
    sel_pts = ring_is_roof[point_ring]
    coords = np.column_stack([x, y, z])[sel_pts]
    # shapely traži uzastopne indekse 0..n-1
    _, ring_seq = np.unique(point_ring[sel_pts], return_inverse=True)
    rings_geom = shapely.linearrings(coords, indices=ring_seq)
    # indeksi moraju biti uzastopni 0..n-1 za polygons()
    roof_ring_face = ring_face[ring_is_roof]
    _, face_seq = np.unique(roof_ring_face, return_inverse=True)
    polys = shapely.polygons(rings_geom, indices=face_seq)

    bid = np.array([f"{slug}:{attrs['fid'].iat[r]}" for r in bldg_rows])
    faces_df = gpd.GeoDataFrame({
        "bldg_id": bid[face_bldg[roof_faces]],
        "district": slug,
        "area": face_area[roof_faces],
        "area_2d": face_area[roof_faces] * nz[roof_faces],
        "slope": slope[roof_faces],
        "azimuth": azimuth[roof_faces],
        "z_min": f_zmin[roof_faces],
        "z_max": f_zmax[roof_faces],
        "z_mean": f_zmean[roof_faces],
        "h_rel": f_zmean[roof_faces] - b_zmin[face_bldg[roof_faces]],
    }, geometry=polys, crs=CRS_METRIC)

    # --- 6) zgrade: agregati + tlocrt (unija 2D projekcija krovnih ploha) -----
    def bsum(mask, values):
        out = np.zeros(len(bldg_rows))
        np.add.at(out, face_bldg[mask], values[mask])
        return out

    a = attrs.iloc[bldg_rows].reset_index(drop=True)
    # 2D projekcija ploha može biti neispravna (gotovo okomite plohe, rupe);
    # make_valid + buffer(0) ostavlja samo ispravne poligonske dijelove
    flat2d = shapely.buffer(shapely.make_valid(shapely.force_2d(polys)), 0)
    fp = (gpd.GeoDataFrame({"bldg_id": faces_df["bldg_id"].values}, geometry=flat2d, crs=CRS_METRIC)
          .dissolve(by="bldg_id"))
    bld = gpd.GeoDataFrame({
        "bldg_id": bid,
        "district": slug,
        "district_name": district_name,
        "fid": a["fid"].values,
        "godina_izv": pd.to_numeric(a.get("Godina_izv"), errors="coerce").astype("Int64"),
        "izvor": a.get("Izvor"),
        "z_ground": b_zmin,
        "z_top": b_zmax,
        "height": b_zmax - b_zmin,
        "volume": a.get("Volume"),
        "n_faces": np.bincount(face_bldg, minlength=len(bldg_rows)),
        "n_roof_faces": np.bincount(face_bldg[is_roof], minlength=len(bldg_rows)),
        "roof_area": bsum(is_roof, face_area),
        "roof_area_2d": bsum(is_roof, face_area * nz),
        "wall_area": bsum(is_wall, face_area),
        "orientation_flipped": flip_b,
    })
    bld = bld.merge(fp[["geometry"]], left_on="bldg_id", right_index=True, how="left")
    bld = gpd.GeoDataFrame(bld, geometry="geometry", crs=CRS_METRIC)
    bld["footprint_area"] = bld.geometry.area

    FACES_DIR.mkdir(parents=True, exist_ok=True)
    BUILDINGS_DIR.mkdir(parents=True, exist_ok=True)
    faces_df.to_parquet(FACES_DIR / f"{slug}.parquet", index=False)
    bld.to_parquet(BUILDINGS_DIR / f"{slug}.parquet", index=False)

    stats = {
        "district": slug,
        "buildings": int(len(bld)),
        "faces": int(n_faces),
        "roof_faces": int(is_roof.sum()),
        "wall_faces": int(is_wall.sum()),
        "buildings_without_roof": int((bld["n_roof_faces"] == 0).sum()),
        "flipped": int(flip_b.sum()),
        "roof_area_km2": round(float(bld["roof_area"].sum()) / 1e6, 3),
        "seconds": round(time.time() - t0, 1),
    }
    print(json.dumps(stats, ensure_ascii=False), flush=True)
    return stats


def main(argv: list[str]) -> None:
    slugs = argv or [s for s in DISTRICTS if (RAW_ZG3D / s / ".done").exists()]
    workers = min(4, len(slugs))
    if workers <= 1:
        results = [process_district(s) for s in slugs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(process_district, slugs))
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print("UKUPNO zgrada:", df["buildings"].sum(), "| krovna površina km2:", round(df["roof_area_km2"].sum(), 2))


if __name__ == "__main__":
    main(sys.argv[1:])
