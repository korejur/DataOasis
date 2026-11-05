# Upute za agente (Claude Code, Codex, Cursor…) i članove tima

## Prije bilo čega

1. Pročitaj **[`STATUS.md`](STATUS.md)**: što je gotovo, što je u tijeku, tko na što čeka.
2. Pročitaj **[`docs/PLAN_RADA.md`](docs/PLAN_RADA.md)**: uloge, raspored do predaje (9. 11. 2026.) i tko je vlasnik kojih datoteka.
   Za odluke o tome što je važno pogledaj **[`docs/NATJECANJE.md`](docs/NATJECANJE.md)** (kriteriji i bodovi).
3. Pitaj korisnika **koju ulogu ima** (aplikacija / podaci / metodologija), ako to nije jasno. Radi samo na datotekama te uloge.
4. Na kraju rada **ažuriraj `STATUS.md`** u istom commitu (pravila su na dnu te datoteke).

## Projekt u dvije rečenice

„Krovovi za klimu“ je alat za urbaniste Grada Zagreba. Iz otvorenog 3D modela zgrada (ZG3D, LoD 2.2)
pronalazi krovove pogodne za **zelene krovove** (srž) i **fotonapon** (dodatni sloj), procjenjuje doprinos
(kišnica, energija, CO₂, trošak) i pomaže odrediti gdje krenuti prvo. Natjecanje: Datathon Portala
otvorenih podataka 2026., izazov **B – Okoliš i održivi prostor**.

## Struktura i tok podataka

```
pipeline/download.py      ZG3D FGDB s data.gov.hr (CKAN)          -> data/raw/zg3d/        (1,2 GB, nije u gitu)
pipeline/extract_roofs.py 3D plohe -> krovne plohe                -> data/processed/faces/ (nije u gitu)
pipeline/pvgis.py         prinos FN za Zagreb (PVGIS, JRC)        -> data/reference/pvgis_zagreb.json
pipeline/metrics.py       potencijal po zgradi, četvrti, gradu    -> data/processed/buildings_metrics.parquet
pipeline/export_app.py    izvoz za web                            -> app/public/data/ (buildings.pmtiles, *.json)
app/                      statička web aplikacija (Vite + MapLibre + PMTiles), bez backenda
```

* Svi parametri izračuna su u `pipeline/config.py` (`PARAMS`). Promjena parametra znači ponovno pokretanje
  `metrics` (~30 s) i `export_app` (~6 min). Geometriju ne treba ponovno obrađivati.
* Koordinatni sustav za izračune je **EPSG:3765** (HTRS96/TM, metri). Za web se koristi WGS84 / Web Mercator.
* Ključ zgrade je **`bldg_id`** (npr. `trnje:1234`). Sve nove tablice po zgradi moraju ga imati.

## Pokretanje (Windows)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.metrics
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.export_app
```

* `data/raw` i `data/processed` nisu u gitu. Dobiju se pokretanjem cijelog pipelinea (vidi README)
  ili se kopiraju od člana tima koji ih ima.
* Na Windowsu uvijek postavi `PYTHONIOENCODING=utf-8` (dijakritici u ispisu).
* U PowerShellu se program s razmakom u putanji pokreće s `&`: `& "C:\Program Files\...\x.exe" args`.
* Aktivacija venva u PowerShellu može biti blokirana execution policyjem. Koristi `.venv\Scripts\python` izravno.
* Duge naredbe (`extract_roofs`, `export_app`) pokreći u pozadini.

## Pravila rada

* **Grane:** svaka uloga radi na svojoj grani i otvara PR prema `main`. Ne pushaj izravno na `main`
  bez dogovora.
* **Vlasništvo datoteka:** vidi `docs/PLAN_RADA.md`. Ako trebaš promjenu u tuđoj datoteci, upiši je u
  `STATUS.md` → „Blokirano / čeka“ umjesto da je sam mijenjaš.
* **Predaja podataka drugoj ulozi:** `data/processed/<naziv>.parquet` sa stupcem `bldg_id`, i redak u
  `STATUS.md` → „Predane tablice“.
* **Veliki podaci:** datoteke > 50 MB ne idu u git. Zapiši izvor i postupak preuzimanja (skripta ili README).
* **Izvori:** svaki novi skup podataka odmah upiši u README → „Izvori podataka“ (izdavatelj, poveznica,
  licenca). Pravila natjecanja to traže, a skupljati izvore na kraju je spor posao.
* **Alati:** novu biblioteku ili alat upiši u `requirements.txt` / `package.json` i u README → „Korišteni alati“.
  Samo softver otvorenog koda.
* **Imena:** u dokumentima repozitorija ne pišu se imena članova tima, samo uloge.
* **Jezik:** dokumentacija, komentari i poruke commitova na hrvatskom. Imena varijabli mogu biti engleska.
* **Brojke koje idu u aplikaciju ili video** moraju imati izvor u `docs/METODOLOGIJA.md`. Parametri s oznakom
  `TODO izvor` su privremeni.

## Zahtjevi natjecanja koji utječu na kod (detalji u `docs/NATJECANJE.md`)

* **Najviše bodova:** izvedivost (10), dojam UI/UX (10), video (10). Kad biraš između nove funkcionalnosti
  i dorade postojećeg sučelja, dorada obično donosi više.

* Koriste se otvoreni podaci javnog sektora, prednost imaju oni s data.gov.hr. Svaki izvor se navodi.
* Samo softver otvorenog koda. **Korišteni AI alati moraju biti navedeni u dokumentaciji.**
* Javni repozitorij s licencom otvorenog koda donosi bodove.
* Predaje se: kod, tehnička dokumentacija (arhitektura + popis podataka), demo (link + snimke zaslona)
  i video do 3 min. Kontrolni popis je u `STATUS.md`.
* Kod jednakih bodova odlučuju „Izvedivost rješenja“, pa „Upotreba otvorenih podataka“. Aplikacija
  mora pouzdano raditi na javnom linku.
