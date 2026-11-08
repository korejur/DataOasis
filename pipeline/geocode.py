"""Geokodiranje adresa kulturnih dobara i objekata Grada (ISGE) i spajanje sa zgradama.

Ulaz:  data/reference/kulturna_dobra/data.csv      Registar kulturnih dobara (MinKulture)
       data/reference/isge/potrosnja_2019_2024.csv  potrošnja objekata Grada Zagreba (ISGE)
       data/processed/buildings/*.parquet           tlocrti zgrada (iz extract_roofs)
       data/processed/buildings_metrics.parquet     FN proizvodnja po zgradi (iz metrics)
Izlaz: data/processed/heritage_buildings.parquet    bldg_id, heritage_id, naziv, status, adresa
       data/processed/isge_buildings.parquet        bldg_id, objekt, kwh_god, eur_god, fn_udio, adresa
       data/reference/geocode/nominatim.json        predmemorija upita (u gitu, da se ne ponavljaju)

Geokodira se preko Nominatima (OpenStreetMap), najviše 1 upit u sekundi, prema pravilima
korištenja. Prihvaća se samo pogodak s kućnim brojem. Točka se veže uz zgradu čiji tlocrt
je sadrži, a ako takve nema, uz najbližu zgradu do MAX_DIST_M metara.

Pokretanje:  python -m pipeline.geocode            (sve; geokodira samo adrese kojih nema u predmemoriji)
             python -m pipeline.geocode --samo-geokodiranje
"""
from __future__ import annotations

import json
import re
import sys
import time

import geopandas as gpd
import pandas as pd
import requests

from .config import BUILDINGS_DIR, CRS_METRIC, CRS_WGS84, PROCESSED, REFERENCE

HERITAGE_CSV = REFERENCE / "kulturna_dobra" / "data.csv"
ISGE_CSV = REFERENCE / "isge" / "potrosnja_2019_2024.csv"
CACHE = REFERENCE / "geocode" / "nominatim.json"

NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "KrovoviZaKlimu/0.1 (Datathon 2026; https://github.com/korejur/DataOasis)"
VIEWBOX = "15.75,46.00,16.25,45.60"  # Grad Zagreb (lon_min, lat_max, lon_max, lat_min)
MAX_DIST_M = 15.0
ISGE_YEAR = 2023  # zadnja godina sa svih 12 mjeseci (2024. ima samo siječanj–lipanj)
MAX_ADDR_PER_RECORD = 4
# Udio potrošnje koji FN može pokriti računa se samo za objekte s barem ovoliko kWh godišnje.
# Manji potrošači (uredi mjesne samouprave, knjižnice, ambulante) obično koriste samo dio zgrade,
# pa bi omjer prema elektrani na cijelom krovu bio višestruko prevelik (medijan ~250 %).
MIN_KWH_FOR_SHARE = 20_000

# ---------------------------------------------------------------------------
# Čišćenje adresa
# ---------------------------------------------------------------------------
_SPLIT = re.compile(r"\s*(?:/|;|,|\s[-–]\s|[-–](?=\s*[A-ZČĆŠŽĐ]))\s*")
_ADDR = re.compile(r"^(?P<street>[^\d]*[A-Za-zČĆŠŽĐčćšžđ]{2}[^\d]*?)\s*0*(?P<num>\d+)\s*(?P<suf>[a-zA-Z])?\b")
_NUM_ONLY = re.compile(r"^0*(?P<num>\d+)\s*(?P<suf>[a-zA-Z])?\b")
_ABBR = [(re.compile(r"^Av(?:\.\s*|\s+)", re.I), "Avenija "), (re.compile(r"^Al(?:\.\s*|\s+)", re.I), "Aleja "),
         (re.compile(r"^Ul(?:\.\s*|\s+)", re.I), "Ulica "), (re.compile(r"\.(?=\S)"), ". ")]


def normalize_street(s: str) -> str:
    """'Av.Većeslava Holjevca' -> 'Avenija Većeslava Holjevca'; 'B.Magovca' -> 'B. Magovca'."""
    for rx, rep in _ABBR:
        s = rx.sub(rep, s)
    return " ".join(s.split())


def split_addresses(raw: str) -> list[str]:
    """'Opatička 02-Kamenita 02' -> ['Opatička 2', 'Kamenita 2']; 'Klaićeva 09, 09a' -> ['Klaićeva 9', 'Klaićeva 9a'].

    Raspon '15-17' daje prvi broj. Dijelovi bez kućnog broja se preskaču.
    """
    out: list[str] = []
    street = None
    for part in _SPLIT.split(" ".join(str(raw).split())):
        if not part:
            continue
        m = _ADDR.match(part)
        if m:
            street = normalize_street(m["street"].strip(" ,"))
            num, suf = m["num"], m["suf"]
        elif street and (m := _NUM_ONLY.match(part)):
            num, suf = m["num"], m["suf"]
        else:
            continue
        a = f"{street} {num}{(suf or '').lower()}"
        if a not in out:
            out.append(a)
    return out[:MAX_ADDR_PER_RECORD]


def heritage_records() -> pd.DataFrame:
    """Pojedinačna nepokretna kulturna dobra u Gradu Zagrebu s adresom, jedan redak po adresi."""
    k = pd.read_csv(HERITAGE_CSV, sep=None, engine="python")
    k = k[k["Zupanija"].eq("Grad Zagreb")
          & k["Vrsta_kulturnog_dobra"].str.startswith("nepokretno kulturno dobro - pojedin", na=False)
          & k["Adresa_smjestaja"].notna()]
    rows = []
    for r in k.itertuples():
        place = r.Mjesto_smjestaja if isinstance(r.Mjesto_smjestaja, str) else "Zagreb"
        for a in split_addresses(r.Adresa_smjestaja):
            rows.append({"heritage_id": r.Oznaka_dobra, "naziv": r.Naziv.strip(), "status": r.Pravni_status,
                         "adresa": a, "mjesto": place})
    return pd.DataFrame(rows)


def isge_records() -> pd.DataFrame:
    """Objekti Grada s potrošnjom električne energije u ISGE_YEAR, jedan redak po objektu i adresi."""
    i = pd.read_csv(ISGE_CSV, sep=";", decimal=",", encoding_errors="replace",
                    usecols=["Naziv objekta", "Naziv grada/mjesta.1", "Adresa", "Naziv energenta", "Godina",
                             "Izračunata potrošnja [kWh]", "Trošak s PDV-om [€]"])
    e = i[(i["Naziv energenta"] == "Električna energija") & (i["Godina"] == ISGE_YEAR) & i["Adresa"].notna()]
    g = (e.groupby(["Naziv objekta", "Adresa", "Naziv grada/mjesta.1"], as_index=False)
          .agg(kwh_god=("Izračunata potrošnja [kWh]", "sum"), eur_god=("Trošak s PDV-om [€]", "sum")))
    g = g[g["kwh_god"] > 0]
    rows = []
    for r in g.itertuples(index=False):
        raw, place = r[1], str(r[2]).split("-")[0].strip() or "Zagreb"
        # 'Sesvete, Ulica Otona Ivekovića 16' -> mjesto Sesvete
        if (m := re.match(r"^([A-ZČĆŠŽĐ][\wčćšžđ ]+),\s*(.+\d.*)$", raw)) and not re.search(r"\d", m[1]):
            place, raw = m[1].strip(), m[2]
        addrs = split_addresses(raw)
        if addrs:
            rows.append({"objekt": " ".join(str(r[0]).replace("|", " ").split()), "adresa": addrs[0],
                         "mjesto": place, "kwh_god": r.kwh_god, "eur_god": r.eur_god})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Nominatim
# ---------------------------------------------------------------------------
def load_cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")


def _query(session: requests.Session, street: str, city: str, free: bool = False) -> dict | None:
    """Strukturirani upit (ulica + mjesto) ili, uz free=True, slobodni upit 'ulica broj, mjesto'."""
    q = {"q": f"{street}, {city}"} if free else {"street": street, "city": city, "country": "Hrvatska"}
    r = session.get(NOMINATIM, params={
        **q, "format": "jsonv2", "addressdetails": 1,
        "limit": 1, "viewbox": VIEWBOX, "bounded": 1, "accept-language": "hr"}, timeout=30)
    time.sleep(1.1)
    r.raise_for_status()
    res = r.json()
    if not res:
        return None
    h = res[0]
    return {"lat": float(h["lat"]), "lon": float(h["lon"]), "housenumber": h["address"].get("house_number"),
            "osm": f"{h['osm_type']}/{h['osm_id']}", "display": h["display_name"]}


def geocode(addresses: pd.DataFrame) -> dict:
    """Geokodira parove (adresa, mjesto) kojih nema u predmemoriji. Ključ je 'adresa|mjesto'."""
    cache = load_cache()
    todo = sorted({f"{a}|{m}" for a, m in zip(addresses["adresa"], addresses["mjesto"])} - cache.keys())
    print(f"Geokodiranje: {len(todo)} novih adresa (u predmemoriji {len(cache)}), ~{len(todo) * 1.1 / 60:.0f} min")
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    for n, key in enumerate(todo, 1):
        street, city = key.split("|")
        # Redom dok se ne nađe kućni broj: strukturirano, slobodno, pa (ako mjesto nije Zagreb) isto za Zagreb.
        # Mjesto iz izvora nije uvijek naselje u OSM-u, a slobodni upit bolje podnosi kratice imena.
        tries = [(city, False), (city, True)] + ([("Zagreb", False), ("Zagreb", True)] if city != "Zagreb" else [])
        hit = None
        for c, free in tries:
            h = _query(s, street, c, free)
            if h and h["housenumber"]:
                hit = h
                break
            hit = hit or h
        cache[key] = hit
        if n % 50 == 0:
            save_cache(cache)
            print(f"  {n}/{len(todo)}")
    save_cache(cache)
    return cache


def attach_points(df: pd.DataFrame, cache: dict) -> gpd.GeoDataFrame:
    """Dodaje točke iz predmemorije; zadržava samo pogotke s kućnim brojem."""
    hits = [cache.get(f"{a}|{m}") for a, m in zip(df["adresa"], df["mjesto"])]
    ok = [h is not None and h.get("housenumber") is not None for h in hits]
    d = df[ok].copy()
    h = [x for x, k in zip(hits, ok) if k]
    d["osm"] = [x["osm"] for x in h]
    pts = gpd.points_from_xy([x["lon"] for x in h], [x["lat"] for x in h], crs=CRS_WGS84)
    return gpd.GeoDataFrame(d, geometry=pts).to_crs(CRS_METRIC)


# ---------------------------------------------------------------------------
# Spajanje sa zgradama
# ---------------------------------------------------------------------------
def load_footprints() -> gpd.GeoDataFrame:
    parts = [gpd.read_parquet(p, columns=["bldg_id", "geometry"]) for p in sorted(BUILDINGS_DIR.glob("*.parquet"))]
    if not parts:
        sys.exit(f"Nema tlocrta u {BUILDINGS_DIR}. Pokreni pipeline.extract_roofs ili koristi --samo-geokodiranje.")
    return gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=CRS_METRIC).drop_duplicates("bldg_id")


def match_buildings(pts: gpd.GeoDataFrame, fp: gpd.GeoDataFrame) -> pd.DataFrame:
    """bldg_id za svaku točku: tlocrt koji je sadrži, inače najbliži do MAX_DIST_M."""
    pts = pts.reset_index(drop=True)
    inside = gpd.sjoin(pts, fp, how="left", predicate="within")
    inside = inside[~inside.index.duplicated()]
    miss = inside["bldg_id"].isna()
    if miss.any():
        near = gpd.sjoin_nearest(pts[miss.values], fp, how="left", max_distance=MAX_DIST_M, distance_col="dist")
        near = near[~near.index.duplicated()]
        inside.loc[near.index, "bldg_id"] = near["bldg_id"]
    inside["nacin"] = "unutar tlocrta"
    inside.loc[miss & inside["bldg_id"].notna(), "nacin"] = f"najbliža do {MAX_DIST_M:.0f} m"
    return pd.DataFrame(inside.drop(columns=["geometry", "index_right"]))


def main(argv: list[str]) -> None:
    her, isge = heritage_records(), isge_records()
    print(f"Kulturna dobra: {her['heritage_id'].nunique()} dobara, {len(her)} adresa")
    print(f"ISGE {ISGE_YEAR}: {len(isge)} objekata s potrošnjom struje")
    cache = geocode(pd.concat([her[["adresa", "mjesto"]], isge[["adresa", "mjesto"]]]))
    if "--samo-geokodiranje" in argv:
        return

    fp = load_footprints()

    h = match_buildings(attach_points(her, cache), fp)
    n_geo = h["heritage_id"].nunique()
    h = h.dropna(subset=["bldg_id"]).drop_duplicates(["bldg_id", "heritage_id"])
    h[["bldg_id", "heritage_id", "naziv", "status", "adresa", "nacin"]].to_parquet(
        PROCESSED / "heritage_buildings.parquet", index=False)
    print(f"Kulturna dobra: geokodirano {n_geo}/{her['heritage_id'].nunique()}, "
          f"spojeno sa zgradom {h['heritage_id'].nunique()} ({h['bldg_id'].nunique()} zgrada)")
    print(h["nacin"].value_counts().to_string())

    i = match_buildings(attach_points(isge, cache), fp).dropna(subset=["bldg_id"])
    # Više objekata (mjernih mjesta) na istoj zgradi se zbraja.
    i = (i.groupby("bldg_id", as_index=False)
          .agg(objekt=("objekt", lambda s: " · ".join(sorted(set(s)))), adresa=("adresa", "first"),
               kwh_god=("kwh_god", "sum"), eur_god=("eur_god", "sum"), nacin=("nacin", "first")))
    m = pd.read_parquet(PROCESSED / "buildings_metrics.parquet", columns=["bldg_id", "pv_kwh"])
    i = i.merge(m, on="bldg_id", how="left")
    i["fn_udio"] = (i["pv_kwh"].fillna(0) / i["kwh_god"]).where(i["kwh_god"] >= MIN_KWH_FOR_SHARE)
    i[["bldg_id", "objekt", "adresa", "kwh_god", "eur_god", "fn_udio", "nacin"]].to_parquet(
        PROCESSED / "isge_buildings.parquet", index=False)
    print(f"ISGE: spojeno {len(i)} zgrada od {len(isge)} objekata; "
          f"udio FN za {i['fn_udio'].notna().sum()} zgrada s ≥ {MIN_KWH_FOR_SHARE} kWh: "
          f"≥ 100 % na {(i['fn_udio'] >= 1).sum()}, medijan {i['fn_udio'].median():.0%}")


if __name__ == "__main__":
    main(sys.argv[1:])
