"""Izračun potencijala zelenih krovova i fotonapona po zgradi, četvrti i gradu.

Ulaz:  data/processed/faces/*.parquet, data/processed/buildings/*.parquet,
       data/reference/pvgis_zagreb.json
Izlaz: data/processed/buildings_metrics.parquet   (GeoParquet, EPSG:3765)
       data/processed/district_summary.csv
       data/processed/city_summary.json

Sve pretpostavke su u config.PARAMS -> promjena parametra = samo ponovno
pokretanje ovog koraka (traje desetak sekundi), bez ponovne obrade geometrije.

    python -m pipeline.metrics
"""
import json

import geopandas as gpd
import numpy as np
import pandas as pd

from .config import BUILDINGS_DIR, DISTRICTS, FACES_DIR, PARAMS, PROCESSED
from .pvgis import load_interpolator

P = PARAMS


def face_metrics(f: pd.DataFrame, yld) -> pd.DataFrame:
    slope = f["slope"].to_numpy()
    area = f["area"].to_numpy()
    area2d = f["area_2d"].to_numpy()

    # --- zeleni krov: klasa prema nagibu --------------------------------------
    for name, lo, hi in P["green_slope_classes"]:
        f[f"g_{name}"] = np.where((slope >= lo) & (slope < hi), area, 0.0)

    # --- fotonapon -------------------------------------------------------------
    flat = slope <= P["pv_flat_max_slope"]
    y_flat = float(yld(P["pv_flat_tilt"], P["pv_flat_azimuth"]))
    y = np.where(flat, y_flat, yld(slope, f["azimuth"].to_numpy()))
    kwp = np.where(flat, area2d * P["pv_flat_gcr"], area * P["pv_pitched_coverage"]) * P["pv_kwp_per_m2"]
    usable = (slope <= P["pv_max_slope"]) & (y >= P["pv_min_yield_kwh_kwp"]) & (area >= P["pv_min_face_area"])
    f["pv_kwp"] = np.where(usable, kwp, 0.0)
    f["pv_kwh"] = f["pv_kwp"] * y
    f["flat_area"] = np.where(slope < 10.0, area, 0.0)
    return f


def building_metrics(b: gpd.GeoDataFrame, f: pd.DataFrame) -> gpd.GeoDataFrame:
    gcols = [f"g_{n}" for n, _, _ in P["green_slope_classes"]]
    agg = f.groupby("bldg_id")[gcols + ["pv_kwp", "pv_kwh", "flat_area"]].sum()
    b = b.merge(agg, left_on="bldg_id", right_index=True, how="left")
    b[agg.columns] = b[agg.columns].fillna(0.0)

    # tip krova
    share_flat = np.where(b["roof_area"] > 0, b["flat_area"] / b["roof_area"], 0)
    b["flat_share"] = share_flat
    b["roof_type"] = np.select([b["roof_area"] <= 0, share_flat >= 0.7, share_flat <= 0.3],
                               ["bez krova", "ravni", "kosi"], "mješoviti")

    # zeleni krov
    b["green_suitable_m2"] = b["g_visoka"] + b["g_srednja"]
    b["green_usable_m2"] = b["green_suitable_m2"] * P["green_usable_fraction"]
    b["green_candidate"] = b["green_suitable_m2"] >= P["green_min_building_area"]
    b["green_retention_m3"] = (b["green_usable_m2"] * P["annual_precip_mm"] / 1000.0
                               * P["green_retention_fraction"])
    b["green_cost_eur"] = b["green_usable_m2"] * P["green_cost_eur_m2"]

    # fotonapon
    b["pv_candidate"] = b["pv_kwp"] >= P["pv_min_building_kwp"]
    b["pv_yield"] = np.where(b["pv_kwp"] > 0, b["pv_kwh"] / b["pv_kwp"].where(b["pv_kwp"] > 0), np.nan)
    b["pv_co2_t"] = b["pv_kwh"] * P["grid_co2_kg_per_kwh"] / 1000.0
    b["pv_households"] = b["pv_kwh"] / P["household_kwh_year"]
    b["pv_cost_eur"] = b["pv_kwp"] * P["pv_cost_eur_kwp"]
    b["pv_savings_eur"] = b["pv_kwh"] * P["electricity_price_eur_kwh"]
    b["pv_payback_years"] = np.where(b["pv_savings_eur"] > 0, b["pv_cost_eur"] / b["pv_savings_eur"].where(b["pv_savings_eur"] > 0), np.nan)
    return b


def summarize(b: pd.DataFrame) -> pd.Series:
    g = b[b["green_candidate"]]
    p = b[b["pv_candidate"]]
    return pd.Series({
        "zgrade": len(b),
        "krovna_povrsina_m2": b["roof_area"].sum(),
        "ravni_krovovi_m2": b["flat_area"].sum(),
        "zgrade_ravni_krov": int((b["roof_type"] == "ravni").sum()),
        "zk_kandidati": len(g),
        "zk_prikladno_m2": g["green_suitable_m2"].sum(),
        "zk_iskoristivo_m2": g["green_usable_m2"].sum(),
        "zk_zadrzana_voda_m3_god": g["green_retention_m3"].sum(),
        "zk_trosak_eur": g["green_cost_eur"].sum(),
        "fn_kandidati": len(p),
        "fn_snaga_MWp": p["pv_kwp"].sum() / 1000,
        "fn_proizvodnja_GWh_god": p["pv_kwh"].sum() / 1e6,
        "fn_co2_t_god": p["pv_co2_t"].sum(),
        "fn_kucanstva": p["pv_households"].sum(),
        "fn_trosak_eur": p["pv_cost_eur"].sum(),
    })


def main() -> None:
    yld = load_interpolator()
    parts = []
    for slug in DISTRICTS:
        fp, bp = FACES_DIR / f"{slug}.parquet", BUILDINGS_DIR / f"{slug}.parquet"
        if not (fp.exists() and bp.exists()):
            print(f"[preskačem] {slug}: nema obrađenih podataka")
            continue
        f = pd.read_parquet(fp, columns=["bldg_id", "area", "area_2d", "slope", "azimuth"])
        b = gpd.read_parquet(bp)
        parts.append(building_metrics(b, face_metrics(f, yld)))
        print(f"[ok] {slug}: {len(b)} zgrada")

    allb = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs)

    # Zgrade na granici četvrti pojavljuju se u oba skupa (zbroj četvrti ima
    # ~0,15 % više zgrada od skupa za cijeli grad). Duplikat = isti centroid
    # tlocrta (na 10 cm) i ista visina; zadržava se prva pojava.
    c = allb.geometry.centroid
    key = pd.DataFrame({"x": (c.x * 10).round(), "y": (c.y * 10).round(),
                        "h": (allb["height"] * 10).round(), "a": allb["roof_area"].round()})
    dup = key.duplicated() & allb.geometry.notna()
    print(f"Uklonjeno duplikata na granicama četvrti: {int(dup.sum())}")
    allb = allb[~dup].reset_index(drop=True)
    allb.to_parquet(PROCESSED / "buildings_metrics.parquet", index=False)

    summary = allb.groupby("district_name").apply(summarize, include_groups=False)
    summary.loc["GRAD ZAGREB (ukupno)"] = summarize(allb)
    summary.round(1).to_csv(PROCESSED / "district_summary.csv", encoding="utf-8-sig")
    city = summary.loc["GRAD ZAGREB (ukupno)"].round(1).to_dict()
    city["parametri"] = {k: v for k, v in P.items() if k != "green_slope_classes"}
    (PROCESSED / "city_summary.json").write_text(json.dumps(city, ensure_ascii=False, indent=2), encoding="utf-8")

    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.float_format", "{:,.0f}".format):
        print(summary)


if __name__ == "__main__":
    main()
