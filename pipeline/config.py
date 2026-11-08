"""Zajednička konfiguracija pipelinea: putanje, popis četvrti i parametri izračuna.

Sve pretpostavke za izračun doprinosa nalaze se ovdje (PARAMS) kako bi ih tim
mogao mijenjati na jednom mjestu i navesti izvor u prezentaciji/aplikaciji.
Izvor svake vrijednosti je u komentaru i u docs/METODOLOGIJA.md (pogl. 8).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_ZG3D = RAW / "zg3d"
REFERENCE = DATA / "reference"
PROCESSED = DATA / "processed"
FACES_DIR = PROCESSED / "faces"
BUILDINGS_DIR = PROCESSED / "buildings"

CKAN_API = "https://data.gov.hr/ckan/api/3/action/"

# HTRS96/TM - službena projekcija RH (metri), koristi se za sve izračune površina.
CRS_METRIC = "EPSG:3765"
CRS_WGS84 = "EPSG:4326"

# slug -> (CKAN id skupa podataka, puni naziv gradske četvrti)
DISTRICTS = {
    "donji_grad": ("zg3d-gradska-cetvrt-donji-grad-2022", "Donji grad"),
    "gornji_grad": ("zg3d-gradska-cetvrt-gornji-grad-2022", "Gornji grad – Medveščak"),
    "trnje": ("zg3d-gradska-cetvrt-trnje-2022", "Trnje"),
    "maksimir": ("zg3d-gradska-cetvrt-maksimir-2022", "Maksimir"),
    "pescenica_zitnjak": ("zg3d-gradska-cetvrt-pescenica-zitnjak-2022", "Peščenica – Žitnjak"),
    "novi_zagreb_istok": ("zg3d-gradska-cetvrt-novi-zagreb-istok-2022", "Novi Zagreb – istok"),
    "novi_zagreb_zapad": ("zg3d-gradska-cetvrt-novi-zagreb-zapad-2022", "Novi Zagreb – zapad"),
    "tresnjevka_sjever": ("zg3d-gradska-cetvrt-tresnjevka-sjever-2022", "Trešnjevka – sjever"),
    "tresnjevka_jug": ("zg3d-gradska-cetvrt-tresnjevka-jug-2022", "Trešnjevka – jug"),
    "crnomerec": ("zg3d-gradska-cetvrt-crnomerec-2022", "Črnomerec"),
    "gornja_dubrava": ("zg3d-gradska-cetvrt-gornja-dubrava-2022", "Gornja Dubrava"),
    "donja_dubrava": ("zg3d-gradska-cetvrt-donja-dubrava-2022", "Donja Dubrava"),
    "stenjevec": ("zg3d-gradska-cetvrt-stenjevec-2022", "Stenjevec"),
    "podsused_vrapce": ("zg3d-gradska-cetvrt-podsused-vrapce-2022", "Podsused – Vrapče"),
    "podsljeme": ("zg3d-gradska-cetvrt-podsljeme-2022", "Podsljeme"),
    "sesvete": ("zg3d-gradska-cetvrt-sesvete", "Sesvete"),
    "brezovica": ("zg3d-gradska-cetvrt-brezovica-2022", "Brezovica"),
}

# --- Geometrijska klasifikacija ploha (korak extract_roofs) -------------------
GEOM = {
    # ploha je zid ako je |n_z| manji od ovoga (nagib > ~80°)
    "wall_nz": 0.17,
    # krovna ploha mora biti barem ovoliko iznad najniže točke zgrade [m]
    "min_roof_height": 0.3,
    # zanemari degenerirane plohe manje od ovoga [m2]
    "min_face_area": 0.05,
}

# --- Parametri izračuna (korak metrics) --------------------------------------
PARAMS = {
    # Klase prikladnosti za zeleni krov prema nagibu [°].
    # FLL Dachbegrünungsrichtlinien (2018), preneseno u metodologiji Gründachkataster
    # NRW (LANUV): do ~15° bez posebnih mjera, iznad treba zaštita od klizanja
    # supstrata, iznad ~35° praktički neizvedivo. Naše klase su grublje (0/10/20/35°).
    "green_slope_classes": [
        ("visoka", 0.0, 10.0),   # ravni krovovi: ekstenzivni i intenzivni
        ("srednja", 10.0, 20.0),  # ekstenzivni
        ("niska", 20.0, 35.0),    # ekstenzivni uz protuklizne mjere
    ],
    # Udio krovne plohe koji je realno iskoristiv (rubovi, instalacije, izlazi...)
    # Vlastita pretpostavka: paušalno 25 % odbitka za rubove (sigurnosni pojas),
    # instalacije, svjetlarnike i izlaze na krov. Nije iz literature.
    "green_usable_fraction": 0.75,
    # Zgrada je kandidat za zeleni krov ako ima barem ovoliko prikladne površine [m2]
    "green_min_building_area": 50.0,

    # Oborine i zadržavanje vode
    # DHMZ, srednje mjesečne vrijednosti (zbroj 12 mjeseci): Zagreb-Grič 887 mm
    # (1861.-2024.), Zagreb-Maksimir 868 mm (1949.-2024.). 880 mm je između njih.
    "annual_precip_mm": 880.0,
    # FLL (2018) preko LANUV NRW: 50 % za 10 cm supstrata (60 % za 20 cm, 70 % za 30 cm);
    # Mentens i sur. (2006), Landscape and Urban Planning 77(3): ~45 % za ekstenzivne.
    "green_retention_fraction": 0.50,

    # Fotonapon
    "pv_kwp_per_m2": 0.20,              # snaga modula po m2 modula (~400-450 W / ~2 m2)
    "pv_pitched_coverage": 0.70,        # udio kose plohe pokriven modulima
    "pv_flat_gcr": 0.50,                # pokrivenost ravnog krova (redovi s razmakom)
    "pv_flat_tilt": 15.0,               # nagib modula na ravnim krovovima [°]
    "pv_flat_azimuth": 180.0,           # orijentacija modula na ravnim krovovima (180 = jug)
    "pv_flat_max_slope": 10.0,          # plohe ispod ovog nagiba tretiraju se kao ravne
    "pv_max_slope": 60.0,               # strmije plohe se ne koriste
    "pv_min_yield_kwh_kwp": 900.0,      # plohe s manjim specifičnim prinosom se ne koriste
    "pv_min_face_area": 5.0,            # manje plohe se ne koriste za module [m2]
    "pv_min_building_kwp": 3.0,         # zgrada je kandidat ako stane barem ovoliko kWp
    "pv_system_loss_pct": 14.0,         # gubici sustava za PVGIS

    # Emisije i troškovi
    # EEA: intenzitet emisija proizvodnje el. energije RH 133,8 gCO2e/kWh (2020.).
    # Novije godine EEA objavljuje samo u interaktivnom grafikonu (provjereno 8. 11. 2026.).
    "grid_co2_kg_per_kwh": 0.134,
    # eMajstor (2026.): 108-180 EUR/m2 kompletna izvedba bez hidroizolacije
    "green_cost_eur_m2": 130.0,
    # Hrvatski izvori 2025.: ~1.200-1.500 EUR/kWp prije subvencija (FZOEU do 600 EUR/kW)
    "pv_cost_eur_kwp": 1300.0,
    # Eurostat nrg_pc_204: kućanstva, razred 2500-4999 kWh, sa svim porezima, HR 2026-S1:
    # 0,1816 EUR/kWh (2025-S2: 0,1652).
    "electricity_price_eur_kwh": 0.18,
    # Eurostat: potrošnja el. energije kućanstava HR 2024. 6818 GWh (nrg_bal_c, FC_OTH_HH_E)
    # / 1471,9 tis. kućanstava (lfst_hhnhtych, 2024.) = ~4630 kWh po kućanstvu.
    "household_kwh_year": 4630.0,
}

# Lokacija za PVGIS upite (središte Zagreba)
PVGIS_LAT = 45.8130
PVGIS_LON = 15.9770
