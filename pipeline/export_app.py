"""Izvoz rezultata za web aplikaciju.

Ulaz:  data/processed/buildings_metrics.parquet, data/processed/district_summary.csv
Izlaz (app/public/data/):
    buildings.pmtiles   vektorske pločice zgrada (sloj "buildings", zoom 13-16)
    districts.json      sažetak po četvrtima + bbox/središte za zumiranje
    city.json           ukupno za grad + parametri izračuna

Pokrenuti nakon `pipeline.metrics` (ponovno nakon svake promjene parametara):

    python -m pipeline.export_app
"""
import json
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from .config import CRS_WGS84, PARAMS, PROCESSED, ROOT

OUT = ROOT / "app" / "public" / "data"

# Pločice: ispod MINZOOM zgrade se ne prikazuju (karta tada prikazuje četvrti).
# Na z12 pločice središta grada prelaze MAX_SIZE pa GDAL odbacuje ~45 % zgrada,
# zato zgrade kreću od z13. MAX_SIZE je podignut s 500 kB da se ništa ne gubi.
MINZOOM, MAXZOOM = 13, 16
MAX_TILE_BYTES = 3_000_000
SIMPLIFY_M = 0.3  # pojednostavljenje tlocrta [m] - ispod vizualnog praga na z16


def green_class(b: pd.DataFrame) -> np.ndarray:
    """Razred prikladnosti za zeleni krov (za bojanje karte).

    visoka  - kandidat, većina prikladne površine je ravna (< 10°)
    srednja - kandidat, pretežno 10-20°
    niska   - nije kandidat, ali ima >= 50 m2 nagiba 20-35° (uz protuklizne mjere)
    nije    - ostalo
    """
    cand = b["green_candidate"].to_numpy()
    mostly_flat = b["g_visoka"] >= 0.5 * b["green_suitable_m2"]
    niska = ~cand & (b["g_niska"] >= PARAMS["green_min_building_area"])
    return np.select([cand & mostly_flat, cand, niska], ["visoka", "srednja", "niska"], "nije")


def building_table(b: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Samo atributi potrebni karti, zaokruženi radi manjih pločica."""
    r = lambda s, d=0: s.round(d)  # noqa: E731
    out = pd.DataFrame({
        "id": b["bldg_id"],
        "cetvrt": b["district_name"],
        "god": b["godina_izv"].fillna(0).astype("int32"),
        "h": r(b["height"], 1),
        "krov": b["roof_type"],
        "krov_m2": r(b["roof_area"]).astype("int32"),
        "ravno_pct": r(b["flat_share"] * 100).astype("int16"),
        # zeleni krov
        "zk": green_class(b),
        "zk_m2": r(b["green_usable_m2"]).astype("int32"),
        "zk_voda_m3": r(b["green_retention_m3"]).astype("int32"),
        "zk_eur": r(b["green_cost_eur"], -2).astype("int64"),
        # fotonapon
        "fn": b["pv_candidate"].astype("int8"),
        "fn_kwp": r(b["pv_kwp"], 1),
        "fn_kwh": r(b["pv_kwh"], -1).astype("int64"),
        "fn_prinos": r(b["pv_yield"].fillna(0)).astype("int16"),
        "fn_co2_t": r(b["pv_co2_t"], 2),
        "fn_kuc": r(b["pv_households"], 1),
        "fn_eur": r(b["pv_cost_eur"], -2).astype("int64"),
        "fn_povrat_god": r(b["pv_payback_years"].fillna(0), 1),
    })
    geom = b.geometry.simplify(SIMPLIFY_M, preserve_topology=True)
    return gpd.GeoDataFrame(out, geometry=geom.values, crs=b.crs)


def district_json(b: gpd.GeoDataFrame) -> list[dict]:
    summary = pd.read_csv(PROCESSED / "district_summary.csv", encoding="utf-8-sig", index_col=0)
    w = b[["district", "district_name", "geometry"]].to_crs(CRS_WGS84)
    bounds = w.geometry.bounds.join(w[["district", "district_name"]])
    out = []
    for name, g in bounds.groupby("district_name"):
        # bbox bez ekstremnih 0,5 % zgrada (izolirani objekti na rubu)
        q = lambda c, p: float(g[c].quantile(p))  # noqa: E731
        bbox = [q("minx", 0.005), q("miny", 0.005), q("maxx", 0.995), q("maxy", 0.995)]
        row = summary.loc[name].to_dict()
        out.append({"slug": g["district"].iloc[0], "naziv": name,
                    "bbox": [round(v, 5) for v in bbox],
                    "centar": [round((bbox[0] + bbox[2]) / 2, 5), round((bbox[1] + bbox[3]) / 2, 5)],
                    **{k: round(float(v), 1) for k, v in row.items()}})
    return sorted(out, key=lambda d: d["naziv"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t = time.time()
    b = gpd.read_parquet(PROCESSED / "buildings_metrics.parquet")
    b = b[b.geometry.notna() & ~b.geometry.is_empty].reset_index(drop=True)
    print(f"Zgrada: {len(b)}")

    # --- JSON sažeci ---------------------------------------------------------------
    districts = district_json(b)
    (OUT / "districts.json").write_text(json.dumps(districts, ensure_ascii=False), encoding="utf-8")
    city = json.loads((PROCESSED / "city_summary.json").read_text(encoding="utf-8"))
    city["parametri"]["green_slope_classes"] = PARAMS["green_slope_classes"]
    city["izvoz"] = {"datum": time.strftime("%Y-%m-%d"), "minzoom": MINZOOM, "maxzoom": MAXZOOM}
    (OUT / "city.json").write_text(json.dumps(city, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[ok] districts.json ({len(districts)} četvrti), city.json")

    # --- vektorske pločice ---------------------------------------------------------
    t2 = building_table(b).to_crs("EPSG:3857")
    print("Razredi zelenog krova:", t2["zk"].value_counts().to_dict())
    dst = OUT / "buildings.pmtiles"
    dst.unlink(missing_ok=True)
    pyogrio.write_dataframe(
        t2, dst, driver="PMTiles", layer="buildings",
        dataset_options={
            "MINZOOM": MINZOOM, "MAXZOOM": MAXZOOM,
            "NAME": "Krovovi za klimu - zgrade Zagreba",
            "DESCRIPTION": "Potencijal zelenih krovova i fotonapona (ZG3D 2022, LoD 2.2)",
            "MAX_SIZE": MAX_TILE_BYTES, "MAX_FEATURES": 400_000,
        },
    )
    print(f"[ok] buildings.pmtiles {dst.stat().st_size / 1e6:.1f} MB, {time.time() - t:.0f} s")


if __name__ == "__main__":
    main()
