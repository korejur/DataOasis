"""Zajednička konfiguracija pipelinea: putanje, popis četvrti i parametri izračuna.

Sve pretpostavke za izračun doprinosa nalaze se ovdje (PARAMS) kako bi ih tim
mogao mijenjati na jednom mjestu i navesti izvor u prezentaciji/aplikaciji.
Vrijednosti označene s `TODO izvor` treba potvrditi i citirati prije predaje.
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
    # Okvirno prema FLL smjernicama: do ~15° bez posebnih mjera, iznad treba
    # zaštita od klizanja supstrata, iznad ~35° praktički neizvedivo.  TODO izvor
    "green_slope_classes": [
        ("visoka", 0.0, 10.0),   # ravni krovovi: ekstenzivni i intenzivni
        ("srednja", 10.0, 20.0),  # ekstenzivni
        ("niska", 20.0, 35.0),    # ekstenzivni uz protuklizne mjere
    ],
    # Udio krovne plohe koji je realno iskoristiv (rubovi, instalacije, izlazi...)
    "green_usable_fraction": 0.75,  # TODO izvor / procjena
    # Zgrada je kandidat za zeleni krov ako ima barem ovoliko prikladne površine [m2]
    "green_min_building_area": 50.0,

    # Oborine i zadržavanje vode
    # ~880 mm/god prema brošuri ZEC-a "Program ublažavanja klimatskih promjena Grada
    # Zagreba"; TODO zamijeniti službenom DHMZ normalom 1991.-2020. (Zagreb-Grič)
    "annual_precip_mm": 880.0,
    # Literatura daje ~35-90 % godišnjeg zadržavanja za ekstenzivne krovove ovisno o
    # supstratu i klimi; 50 % je konzervativna pretpostavka.  TODO citirati rad
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
    # TODO ažurirati na najnoviju godinu s EEA indikatora.
    "grid_co2_kg_per_kwh": 0.134,
    # eMajstor (2026.): 108-180 EUR/m2 kompletna izvedba bez hidroizolacije
    "green_cost_eur_m2": 130.0,
    # Hrvatski izvori 2025.: ~1.200-1.500 EUR/kWp prije subvencija (FZOEU do 600 EUR/kW)
    "pv_cost_eur_kwp": 1300.0,
    "electricity_price_eur_kwh": 0.15,  # TODO izvor: HEP/HERA prosječna cijena za korisnika
    "household_kwh_year": 3500.0,       # TODO izvor: DZS/HERA prosječna potrošnja kućanstva
}

# Lokacija za PVGIS upite (središte Zagreba)
PVGIS_LAT = 45.8130
PVGIS_LON = 15.9770
