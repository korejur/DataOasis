"""Izvoz rezultata za web aplikaciju.

Ulaz:  data/processed/buildings_metrics.parquet, data/processed/district_summary.csv
       ako postoje: heritage_buildings.parquet, isge_buildings.parquet (pipeline.geocode),
       building_institutions.parquet (uloga podaci)
Izlaz (app/public/data/):
    buildings.pmtiles   vektorske pločice zgrada (sloj "buildings", zoom 13-16)
    districts.json      sažetak po četvrtima + bbox/središte za zumiranje
    city.json           ukupno za grad + parametri izračuna
    (oba imaju i ključ "javno": isti zbrojevi samo za objekte Grada iz ISGE-a)

Pokrenuti nakon `pipeline.metrics` (ponovno nakon svake promjene parametara):

    python -m pipeline.export_app               # JSON + pločice (~7 min)
    python -m pipeline.export_app --samo-json   # samo JSON sažeci (nekoliko sekundi)
"""
import argparse
import json
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from .config import CRS_WGS84, PARAMS, PROCESSED, ROOT
from .metrics import summarize

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
    out = out.merge(linked_tables(), left_on="id", right_index=True, how="left")
    geom = b.geometry.simplify(SIMPLIFY_M, preserve_topology=True)
    return gpd.GeoDataFrame(out, geometry=geom.values, crs=b.crs)


def _join_names(s: pd.Series, limit: int = 3) -> str:
    names = list(dict.fromkeys(s.dropna()))
    return " · ".join(names[:limit]) + (f" (+{len(names) - limit})" if len(names) > limit else "")


def linked_tables() -> pd.DataFrame:
    """Atributi iz tablica drugih izvora (STATUS → „Predane tablice“), indeks bldg_id.

    Spaja se samo ono što postoji u data/processed/; nedostajuća tablica se preskače.
    """
    parts = []
    p = PROCESSED / "heritage_buildings.parquet"
    if p.exists():  # Registar kulturnih dobara
        h = pd.read_parquet(p).groupby("bldg_id").agg(
            bastina=("naziv", _join_names), bastina_id=("heritage_id", _join_names))
        parts.append(h)
    p = PROCESSED / "isge_buildings.parquet"
    if p.exists():  # ISGE: potrošnja struje objekata Grada
        i = pd.read_parquet(p).set_index("bldg_id")
        parts.append(pd.DataFrame({
            "javno": i["objekt"].str.slice(0, 120),
            "javno_kwh": i["kwh_god"].round(-1).astype("int64"),
            "javno_udio": (i["fn_udio"] * 100).round().clip(upper=9999).astype("Int32"),  # prazno za male potrošače
        }))
    p = PROCESSED / "building_institutions.parquet"
    if p.exists():  # javne ustanove (uloga podaci)
        u = pd.read_parquet(p).groupby("bldg_id").agg(
            ustanova=("institution_name", _join_names), ustanova_tip=("institution_type", _join_names))
        parts.append(u)
    for t in parts:
        print(f"[spoj] {', '.join(t.columns)}: {len(t)} zgrada")
    return pd.concat(parts, axis=1) if parts else pd.DataFrame(index=pd.Index([], name="bldg_id"))


def _public(g: pd.DataFrame) -> dict:
    """Zbrojevi za objekte Grada (isti ključevi kao za grad) + potrošnja struje iz ISGE-a.

    Udio potrošnje koji FN može pokriti računa se samo na objektima s >= 20 MWh/god
    (stupac fn_udio postoji samo za njih, vidi pipeline/geocode.py i METODOLOGIJA.md 7.1).
    """
    out = {k: round(float(v), 3) for k, v in summarize(g).items()}
    big = g[g["fn_udio"].notna()]
    out["potrosnja_GWh_god"] = round(float(g["kwh_god"].sum()) / 1e6, 3)
    out["veliki_potrosaci"] = len(big)
    out["veliki_potrosnja_GWh_god"] = round(float(big["kwh_god"].sum()) / 1e6, 3)
    out["veliki_fn_GWh_god"] = round(float(big.loc[big["pv_candidate"], "pv_kwh"].sum()) / 1e6, 3)
    return out


def public_summary(b: pd.DataFrame) -> tuple[dict, dict[str, dict]]:
    """Scenarij „samo objekti Grada“: zbrojevi za grad i po četvrtima (prazno bez ISGE tablice)."""
    p = PROCESSED / "isge_buildings.parquet"
    if not p.exists():
        return {}, {}
    i = pd.read_parquet(p, columns=["bldg_id", "kwh_god", "fn_udio"])
    j = pd.DataFrame(b.drop(columns="geometry")).merge(i, on="bldg_id", how="inner")
    by_district = {name: _public(g) for name, g in j.groupby("district_name")}
    by_district[None] = _public(j.iloc[0:0])  # četvrt bez objekata Grada
    print(f"[javno] {len(j)} zgrada, {int(j['fn_udio'].notna().sum())} s >= 20 MWh/god")
    return _public(j), by_district


def district_json(b: gpd.GeoDataFrame, public: dict[str, dict]) -> list[dict]:
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
                    **{k: round(float(v), 1) for k, v in row.items()},
                    **({"javno": public.get(name, public[None])} if public else {})})
    return sorted(out, key=lambda d: d["naziv"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--samo-json", action="store_true", help="samo districts.json i city.json, bez pločica")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t = time.time()
    b = gpd.read_parquet(PROCESSED / "buildings_metrics.parquet")
    b = b[b.geometry.notna() & ~b.geometry.is_empty].reset_index(drop=True)
    print(f"Zgrada: {len(b)}")

    # --- JSON sažeci ---------------------------------------------------------------
    public_city, public_districts = public_summary(b)
    districts = district_json(b, public_districts)
    (OUT / "districts.json").write_text(json.dumps(districts, ensure_ascii=False), encoding="utf-8")
    city = json.loads((PROCESSED / "city_summary.json").read_text(encoding="utf-8"))
    city["parametri"]["green_slope_classes"] = PARAMS["green_slope_classes"]
    if public_city:
        city["javno"] = public_city
    city["izvoz"] = {"datum": time.strftime("%Y-%m-%d"), "minzoom": MINZOOM, "maxzoom": MAXZOOM}
    (OUT / "city.json").write_text(json.dumps(city, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[ok] districts.json ({len(districts)} četvrti), city.json")
    if args.samo_json:
        return

    # --- vektorske pločice ---------------------------------------------------------
    t2 = building_table(b).to_crs("EPSG:3857")
    print("Razredi zelenog krova:", t2["zk"].value_counts().to_dict())
    dst = OUT / "buildings.pmtiles"
    dst.unlink(missing_ok=True)
    pyogrio.write_dataframe(
        t2, dst, driver="PMTiles", layer="buildings", encoding="UTF-8",  # inače na Windowsu cp1252
        dataset_options={
            "MINZOOM": MINZOOM, "MAXZOOM": MAXZOOM,
            "NAME": "Krov+ - zgrade Zagreba",
            "DESCRIPTION": "Potencijal zelenih krovova i fotonapona (ZG3D 2022, LoD 2.2)",
            "MAX_SIZE": MAX_TILE_BYTES, "MAX_FEATURES": 400_000,
        },
    )
    print(f"[ok] buildings.pmtiles {dst.stat().st_size / 1e6:.1f} MB, {time.time() - t:.0f} s")


if __name__ == "__main__":
    main()
