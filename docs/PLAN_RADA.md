# Plan rada – tri uloge

Tim se sam dijeli po ulogama:

* **Osoba za aplikaciju:** karta, geokodiranje, javne zgrade, prioritizacija, objava. Najviše koda.
* **Osoba za podatke:** granice, javne ustanove, toplina i zelenilo, otvoreni podaci. Srednje koda.
* **Osoba za metodologiju:** parametri i izvori, validacija, metodologija, video i prijava. Bez kodiranja.

Korak 1 (izvoz podataka za kartu) je **gotov** (`pipeline/export_app.py`).

## Pravila da se ne sudaramo

* Svatko radi na **svojoj grani** i otvara PR prema `main`.
* Svatko ima **svoje datoteke**:
  * **aplikacija:** `app/`, `pipeline/export_app.py`, `pipeline/geocode.py`, `pipeline/public_buildings.py`
  * **podaci:** `pipeline/institutions.py`, `pipeline/raster_stats.py`, `data/reference/ustanove|granice|raster/`
  * **metodologija:** `pipeline/config.py` (samo vrijednosti u `PARAMS`), `docs/METODOLOGIJA.md`, `docs/VALIDACIJA.md`
* **Dogovor o predaji podataka:** sve što se veže uz zgrade sprema se kao
  `data/processed/<naziv>.parquet` sa stupcem **`bldg_id`** (isti kao u `buildings_metrics.parquet`).
  Osoba za aplikaciju te tablice spaja u `export_app.py` i one se pojavljuju na karti.
* Datoteke veće od 50 MB ne idu u git. Umjesto toga se zapišu izvor i postupak preuzimanja.

## Faza 1 – sada (svi paralelno, nitko nikoga ne čeka)

| Uloga | Zadatak | Rezultat |
|---|---|---|
| aplikacija | **Karta**: Vite + MapLibre + PMTiles, krovovi obojeni po pogodnosti, prebacivanje zeleni krov / FN, kartica zgrade na klik | `app/` se pokreće s `npm run dev` |
| aplikacija | **Geokodiranje adresa** (nakon karte): registar kulturnih dobara (547 adresa) i ISGE objekti | `data/processed/heritage_buildings.parquet`, `isge_buildings.parquet` (`bldg_id` + atributi) |
| podaci | **Granice** gradskih četvrti i mjesnih odbora | `data/reference/granice/*.geojson` |
| podaci | **Javne ustanove**: vrtići, škole, domovi za starije, zdravstvo; prostorno spajanje sa zgradama | `data/processed/building_institutions.parquet` (`bldg_id`, `institution_type`, `institution_name`) |
| metodologija | **Parametri s `TODO izvor`** (istraživanje na webu, upisivanje brojki i izvora) u `config.py`: oborine (DHMZ), CO₂ (EEA), cijena struje, potrošnja kućanstva, FLL klase, iskoristivi udio krova. Izvori idu i u `METODOLOGIJA.md` | PR s parametrima i izvorima |

**Točka spajanja 1:**
* Podaci predaju granice → aplikacija dodaje sloj četvrti (pregled ispod z13).
* Metodologija predaje parametre → aplikacija ponovno pokreće `metrics` i `export_app`.

## Faza 2 – kad je karta gotova

| Uloga | Zadatak | Rezultat |
|---|---|---|
| aplikacija | **Panel s četvrtima**: rang-lista, ključni brojevi, scenariji (10 % / 30 % kandidata, samo javne zgrade) | panel u aplikaciji |
| aplikacija | Spajanje tablica u izvoz: oznake ustanova, baštine i javnih zgrada na karti i u kartici zgrade | novi `buildings.pmtiles` |
| aplikacija | **Javne zgrade**: ISGE potrošnja + ustanove → koliki udio potrošnje FN može pokriti | stupci u `isge_buildings.parquet` |
| podaci | **Toplina i zelenilo**: ljetni LST (Landsat), NDVI (Sentinel-2), po želji stanovništvo (GHSL); vrijednost po zgradi | `data/processed/building_env.parquet` (`bldg_id`, `lst`, `ndvi`, `pop`) |
| metodologija | **Validacija**: ručna provjera ~200 nasumičnih kandidata na ortofotu DGU-a (popis s linkovima priprema aplikacija, upisuje se samo DA/NE) | `docs/VALIDACIJA.md` + postotak točnosti u `METODOLOGIJA.md` |

**Točka spajanja 2:** podaci predaju `building_env` → aplikacija radi **prioritizaciju s klizačima**
(težine: toplina, manjak zelenila, stanovništvo, osjetljivi korisnici, javna zgrada).

## Faza 3 – predaja

| Uloga | Zadatak |
|---|---|
| aplikacija | Prioritizacija s klizačima, objava aplikacije (statički hosting), završno uređivanje |
| podaci | Izvoz otvorenih podataka: CSV/GeoJSON po zgradi i po četvrtima |
| metodologija | Stranica s metodologijom i izvorima u aplikaciji, scenarij i snimanje videa, tekst prijave |
| svi | Proba demo prezentacije, zajednička provjera brojki |

## Redoslijed ukratko

```
Faza 1:  APLIKACIJA karta, geokod.   PODACI granice → ustanove   METODOLOGIJA parametri i izvori
              │                            │                            │
              ├──────── spajanje 1 ────────┴────────────────────────────┘
Faza 2:  APLIKACIJA panel, javne zgr. PODACI LST/NDVI             METODOLOGIJA validacija
              │                            │                            │
              ├──────── spajanje 2 ────────┴────────────────────────────┘
Faza 3:  APLIKACIJA prioritizacija   PODACI otvoreni podaci      METODOLOGIJA metod. stranica, video
```
