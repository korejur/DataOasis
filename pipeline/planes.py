"""Spajanje triangulacije ZG3D-a u krovne ravnine (eksperiment, lokalna kopija).

ZG3D zapisuje krov kao mrežu trokuta i četverokuta. Pravilo „ploha ≥ 5 m²“ tada se
primjenjuje na pojedini trokut, pa sitni dijelovi velikih krovova ispadaju iz izračuna
(~10 % dobre krovne površine). Ovaj korak spaja plohe iste zgrade sa sličnim nagibom
i azimutom u jednu ravninu, a zatim je razdvaja na povezane dijelove.

Ulaz:  data/processed/faces/<četvrt>.parquet
Izlaz: data/processed/planes/<četvrt>.parquet  (isti stupci kao faces + geometrija 2D)

    python -m pipeline.planes
"""
import time
from multiprocessing import Pool

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from .config import DISTRICTS, FACES_DIR, PARAMS as P, PROCESSED

PLANES_DIR = PROCESSED / "planes"
SLOPE_BIN = 0.5   # [°] plohe unutar istog razreda nagiba ...
AZ_BIN = 2.0      # [°] ... i azimuta smatraju se istom ravninom (usko: zakrivljeni krovovi
                  #     poput kupola i svodova ostaju razdvojeni na sitne plohe)
FLAT_MERGE = 1.0  # [°] samo posve ravne plohe spajaju se bez obzira na azimut
LEVEL_BIN = 1.0   # [m] razred visine ravnine (odvaja paralelne krovove na različitim visinama)
GRID = 0.01       # [m] mreža za spajanje rubova (uklanja pukotine od zaokruživanja)


def merge_district(slug: str) -> tuple[str, int, int, float]:
    t = time.time()
    f = gpd.read_parquet(FACES_DIR / f"{slug}.parquet")
    n0 = len(f)
    flat = (f["slope"] <= FLAT_MERGE).to_numpy()
    sb = np.where(flat, -1, np.round(f["slope"].to_numpy() / SLOPE_BIN)).astype(int)
    nb = int(round(360 / AZ_BIN))
    ab = np.where(flat, -1, np.round(f["azimuth"].fillna(0).to_numpy() / AZ_BIN) % nb).astype(int)
    a = f["area"].to_numpy()
    az = np.radians(f["azimuth"].fillna(0).to_numpy())
    # jednadžba ravnine svake plohe u lokalnim metrima zgrade: h = c + gx*x + gy*y
    # (h = visina iznad najniže točke zgrade, x prema istoku, y prema sjeveru)
    cen = shapely.centroid(shapely.force_2d(f.geometry.values))
    cx, cy = shapely.get_x(cen), shapely.get_y(cen)
    bx = pd.Series(cx).groupby(f["bldg_id"].to_numpy()).transform("min").to_numpy()
    by = pd.Series(cy).groupby(f["bldg_id"].to_numpy()).transform("min").to_numpy()
    xl, yl = cx - bx, cy - by
    tan_s = np.tan(np.radians(f["slope"].to_numpy()))
    gxf, gyf = -tan_s * np.sin(az), -tan_s * np.cos(az)
    cf = f["h_rel"].to_numpy() - gxf * xl - gyf * yl
    lb = np.round(cf / LEVEL_BIN).astype(int)  # paralelne plohe na različitim visinama ostaju odvojene
    d = pd.DataFrame({
        "bldg_id": f["bldg_id"].to_numpy(), "sb": sb, "ab": ab, "lb": lb,
        "bx": bx, "by": by, "xl": xl, "yl": yl, "h_rel": f["h_rel"].to_numpy(), "a2d": f["area_2d"].to_numpy(),
        "area": a, "area_2d": f["area_2d"].to_numpy(),
        "sw": f["slope"].to_numpy() * a, "s_sin": np.sin(az) * a, "s_cos": np.cos(az) * a,
        "has_az": f["azimuth"].notna().to_numpy(),
        # vrh plohe iznad najniže točke zgrade [m] (za 3D prikaz)
        "h_top": (f["h_rel"] + f["z_max"] - f["z_mean"]).to_numpy(),
    })
    key = ["bldg_id", "sb", "ab", "lb"]
    gid = d.groupby(key, sort=False).ngroup().to_numpy()
    agg = d.groupby(gid).agg(bldg_id=("bldg_id", "first"), area=("area", "sum"), area_2d=("area_2d", "sum"),
                             sw=("sw", "sum"), s_sin=("s_sin", "sum"), s_cos=("s_cos", "sum"),
                             has_az=("has_az", "any"), h_top=("h_top", "max"))
    agg["slope"] = agg["sw"] / agg["area"]
    agg["azimuth"] = np.where(agg["has_az"], np.degrees(np.arctan2(agg["s_sin"], agg["s_cos"])) % 360, np.nan)
    # jednadžba ravnine grupe: nagib i smjer grupe, odsječak = težinska sredina po plohama
    ts = np.tan(np.radians(agg["slope"].to_numpy()))
    azg = np.radians(np.nan_to_num(agg["azimuth"].to_numpy()))
    agg["gx"], agg["gy"] = -ts * np.sin(azg), -ts * np.cos(azg)
    d["gid"] = gid
    gxx, gyy = agg["gx"].reindex(gid).to_numpy(), agg["gy"].reindex(gid).to_numpy()
    d["cw"] = (d["h_rel"] - gxx * d["xl"] - gyy * d["yl"]) * d["a2d"]
    cw = d.groupby("gid").agg(cw=("cw", "sum"), a2d=("a2d", "sum"), bx=("bx", "first"), by=("by", "first"))
    agg["c"] = (cw["cw"] / cw["a2d"].where(cw["a2d"] > 0)).reindex(agg.index).fillna(0).to_numpy()
    agg["bx"], agg["by"] = cw["bx"].reindex(agg.index).to_numpy(), cw["by"].reindex(agg.index).to_numpy()

    # unija geometrije po grupi; grupe s jednom plohom ne treba spajati
    geoms = shapely.make_valid(shapely.force_2d(f.geometry.values))
    order = np.argsort(gid, kind="stable")
    bounds = np.flatnonzero(np.diff(gid[order])) + 1
    out = []
    for idx in np.split(order, bounds):
        if len(idx) == 1:
            out.append(geoms[idx[0]])
            continue
        try:
            out.append(shapely.union_all(geoms[idx], grid_size=GRID))
        except shapely.errors.GEOSException:
            out.append(shapely.union_all(shapely.buffer(geoms[idx], 0)))
    agg = agg.loc[np.unique(gid)]  # isti redoslijed kao np.split (sortirani gid)
    m = gpd.GeoDataFrame(agg[["bldg_id", "area", "area_2d", "slope", "azimuth", "h_top", "gx", "gy", "c", "bx", "by"]].reset_index(drop=True),
                         geometry=shapely.make_valid(np.array(out, dtype=object)), crs=f.crs)
    m["grp"] = np.arange(len(m))

    # razdvoji nepovezane dijelove iste orijentacije; površinu raspodijeli prema 2D udjelu
    m = m.explode(index_parts=False).reset_index(drop=True)
    m = m[m.geometry.geom_type == "Polygon"].copy()
    m["a2"] = m.geometry.area
    share = m["a2"] / m.groupby("grp")["a2"].transform("sum")
    m["area"] = m["area"] * share
    m["area_2d"] = m["area_2d"] * share
    m = m.drop(columns=["grp", "a2"])
    m = m[m["area"] > 0.01]
    PLANES_DIR.mkdir(parents=True, exist_ok=True)
    m.to_parquet(PLANES_DIR / f"{slug}.parquet", index=False)
    return slug, n0, len(m), time.time() - t


def main() -> None:
    t = time.time()
    slugs = [s for s in DISTRICTS if (FACES_DIR / f"{s}.parquet").exists()]
    with Pool(min(len(slugs), 8)) as pool:
        for slug, n0, n1, dt in pool.imap_unordered(merge_district, slugs):
            print(f"[ok] {slug}: {n0} ploha -> {n1} ravnina ({dt:.0f} s)", flush=True)
    print(f"Gotovo za {time.time() - t:.0f} s -> {PLANES_DIR}")


if __name__ == "__main__":
    main()
