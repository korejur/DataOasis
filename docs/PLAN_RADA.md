# Plan rada – tri uloge

Tim se sam dijeli po ulogama:

* **Osoba za aplikaciju:** karta, geokodiranje, javne zgrade, prioritizacija, objava. Najviše koda.
* **Osoba za podatke:** granice, javne ustanove, toplina i zelenilo, otvoreni podaci. Srednje koda.
* **Osoba za metodologiju:** parametri i izvori, validacija, metodologija, video i prijava. Bez kodiranja.

Korak 1 (izvoz podataka za kartu) je **gotov** (`pipeline/export_app.py`).

**Predaja: ponedjeljak 9. 11. 2026. do 24:00** e-poštom na open.data@mpudt.hr (izazov B – Okoliš i održivi prostor).
Što se točno predaje i koliko je gotovo vodi se u [`STATUS.md`](../STATUS.md). Kriteriji i bodovi: [`NATJECANJE.md`](NATJECANJE.md).

> **Pola bodova (30/60) nose izvedivost (radni prototip), dojam UI/UX i video.** Zato je dorada sučelja
> i video planirana kao poseban posao, a ne nešto što se radi „ako ostane vremena“.

## Raspored (4 dana)

| Dan | Cilj dana | Kraj dana – mora postojati |
|---|---|---|
| **čet 5. 11.** | Faza 1 počinje | uloge podijeljene, svatko na svojoj grani |
| **pet 6. 11.** | Faza 1 gotova, **spajanje 1** | karta radi lokalno; granice i ustanove predane; parametri s izvorima predani |
| **sub 7. 11.** | Faza 2, **spajanje 2** | panel s četvrtima, javne zgrade i ustanove na karti; validacija gotova; LST/NDVI ako stigne |
| **ned 8. 11.** | Dorada UI/UX, **zamrzavanje funkcionalnosti u 18:00**, zatim samo popravci | aplikacija objavljena na javnom linku; dokumentacija i `ARHITEKTURA.md`; video snimljen |
| **pon 9. 11.** | Predaja (rezerva za probleme) | repo javan s licencom, e-pošta poslana |

**Ako kasnimo, režemo ovim redom** (zadnje se reže prvo): LST/NDVI → prioritizacija s klizačima
(ostaje fiksni filtar „javne ustanove“) → geokodiranje baštine → validacija na 100 umjesto 200 zgrada.
**Ne režu se:** karta s karticom zgrade, panel s četvrtima, dorada sučelja, javni link, dokumentacija s izvorima i arhitekturom, video.
Javne ustanove i ISGE se ne režu olako jer nose bodove za *povezivanje podataka*.

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
| aplikacija | **UX osnove**: legenda, pretraga četvrti ili adrese, uvodni ekran „što je ovo“, prikaz na mobitelu, hrvatski tekstovi | aplikacija |
| aplikacija | Spajanje tablica u izvoz: oznake ustanova, baštine i javnih zgrada na karti i u kartici zgrade | novi `buildings.pmtiles` |
| aplikacija | **Javne zgrade**: ISGE potrošnja + ustanove → koliki udio potrošnje FN može pokriti | stupci u `isge_buildings.parquet` |
| podaci | **Toplina i zelenilo**: ljetni LST (Landsat), NDVI (Sentinel-2), po želji stanovništvo (GHSL); vrijednost po zgradi | `data/processed/building_env.parquet` (`bldg_id`, `lst`, `ndvi`, `pop`) |
| metodologija | **Validacija**: ručna provjera ~200 nasumičnih kandidata na ortofotu DGU-a (popis s linkovima priprema aplikacija, upisuje se samo DA/NE) | `docs/VALIDACIJA.md` + postotak točnosti u `METODOLOGIJA.md` |
| metodologija | **Scenarij videa** po točkama iz kriterija (problem, korisnici, podaci, funkcionalnosti, arhitektura, korist, daljnji razvoj) | `docs/VIDEO_SCENARIJ.md` |
| metodologija | **Test s osobom izvan tima**: može li bez objašnjenja pronaći četvrt i pročitati karticu zgrade? Zapisati što je zbunjivalo | popis za doradu u `STATUS.md` |

**Točka spajanja 2:** podaci predaju `building_env` → aplikacija radi **prioritizaciju s klizačima**
(težine: toplina, manjak zelenila, stanovništvo, osjetljivi korisnici, javna zgrada).

## Faza 3 – predaja

| Uloga | Zadatak |
|---|---|
| aplikacija | Prioritizacija s klizačima, objava aplikacije (statički hosting), dorada prema UX testu, **`docs/ARHITEKTURA.md`** (dijagram, standardi, integracija, preduvjeti) |
| podaci | Izvoz otvorenih podataka: CSV/GeoJSON po zgradi i po četvrtima |
| metodologija | Stranica s metodologijom i izvorima u aplikaciji, snimanje i montaža videa (≤ 3 min), snimke zaslona, tekst e-pošte |
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
