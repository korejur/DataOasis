# Handoff – Datathon "Krovovi za klimu" (sesija 3. 11. 2026.)

## Cilj

Studentski tim (FER) sudjeluje na **Datathonu Portala otvorenih podataka**
(Ministarstvo pravosuđa, uprave i digitalne transformacije). Rješenje se razvija
na podacima s data.gov.hr, a predaje se e-poštom s kratkim videom.

Odabrana ideja je **alat za urbaniste za Zagreb**. Iz otvorenog 3D modela zgrada
(ZG3D, LoD 2.2) pronalazi krovove pogodne za **zelene krovove** (srž projekta)
i **fotonapon** (dodatni sloj). Procjenjuje doprinos (zadržana kišnica, energija,
CO₂, trošak) i prioritizira krovove **prema potrebi**: toplinski otoci,
nedostatak zelenila, osjetljivi korisnici, javne zgrade.

Pozicioniranje: Grad Zagreb već ima solarni kalkulator za građane (EIC
"Solarna karta Zagreba" / "ZG Solari"), pa sam solar nije nov. Karta potencijala
zelenih krovova za Zagreb nije pronađena. Smjer aplikacije **još nije
dogovoren**. Tim je tražio pregled literature prije te odluke.

## Trenutno stanje

Mapa projekta: `C:\DATATHON\Datathon` (izvorno kod Marija `D:\Obrazovanje\FER_2026_2027\Datathon`).
Sve putanje u kodu su relativne (`pipeline/config.py` → `ROOT`), pa projekt radi iz bilo koje mape.
`.venv` je ponovno izgrađen 5. 11. 2026. s Pythonom 3.12.6 (geopandas 1.2, GDAL 3.12.4, shapely 2.2).

Pipeline za podatke je gotov i pokrenut za cijeli grad (svih 17 gradskih četvrti).
Aplikacija još nije započeta (`app/` je prazna).

Datoteke napravljene u ovoj sesiji:

| Datoteka | Sadržaj |
|---|---|
| `requirements.txt`, `.gitignore` | ovisnosti (numpy, pandas, shapely, pyproj, pyogrio, geopandas, pyarrow, requests); `data/raw` i `data/processed` su ignorirani |
| `.venv/` | Python 3.12 okruženje (ponovno izgrađeno) (GDAL 3.12 preko pyogrio, geopandas 1.2) |
| `pipeline/config.py` | putanje, popis 17 četvrti (CKAN id), `GEOM` pragovi i **svi parametri izračuna `PARAMS`**, neki s oznakom `TODO izvor` |
| `pipeline/download.py` | preuzima FGDB po četvrti preko CKAN API-ja uz ponovne pokušaje; ako FGDB nije čitljiv, preuzima SHP (`ensure_readable`) |
| `pipeline/extract_roofs.py` | vlastiti WKB parser (TIN/GeometryCollection), vektorizirane Newellove normale, klasifikacija krov/zid/ostalo, okretanje orijentacije po zgradi, izlaz plohe i zgrade u GeoParquet (EPSG:3765) |
| `pipeline/pvgis.py` | tablica prinosa FN za Zagreb iz PVGIS v5.3 (nagib 0–90 × azimut 0–345) + bilinearna interpolacija |
| `pipeline/metrics.py` | prikladnost za zeleni krov i FN po plohi, zatim po zgradi; uklanja duplikate; sažetak po četvrtima i za grad |
| `README.md` | struktura, upute za pokretanje, prvi rezultati, izvori podataka |
| `docs/METODOLOGIJA.md` | formule, klasifikacija, validacija, posebnosti podataka, plan prioritizacije, ograničenja |
| `docs/PREGLED_LITERATURE.md` | pregled Beča, NRW-a, Wuppertala, Marburga, Liègea, San Sebastiána, Chicaga i NYC-a; usporedna tablica kriterija; prijedlozi |
| `data/raw/zg3d/<četvrt>/` | preuzeti FGDB (~1,2 GB); za `novi_zagreb_zapad` i SHP u `shp/` |
| `data/reference/pvgis_zagreb.json` | PVGIS tablica (optimum 35° J = 1242 kWh/kWp; vodoravno 1053) |
| `data/reference/isge/`, `kulturna_dobra/`, `topo_objekti/` | preuzeto, **još neobrađeno** (potrošnja objekata Grada 2019.–2024.; registar kulturnih dobara; topografska osnova 2018 – objekti) |
| `data/processed/faces/*.parquet` (349 MB) | sve krovne plohe s 3D geometrijom |
| `data/processed/buildings/*.parquet` (88 MB) | zgrade po četvrtima |
| `data/processed/buildings_metrics.parquet` (120 MB) | zgrade s potencijalom (bez duplikata) |
| `data/processed/district_summary.csv`, `city_summary.json` | sažeci |

Memorija za Claudea i pomoćne skripte ostale su na Marijevom računalu (nisu u zipu):
memorija (`datathon-green-roofs-project.md`, `datathon-user-profile.md`, `MEMORY.md`) i scratchpad
(`validate.py`, `validate2.py`, `odd.py`, `crs.py`, `layers.py`, `pdf2txt.py`,
tekst literature u `lit_txt/`, Wuppertal CSV u `lit/wuppertal/`).

### Prvi rezultati (tehnički potencijal, trenutni parametri)

* 356 984 zgrade (bez duplikata); krovna površina 40,5 km²; ravni krovovi (< 10°) 16,0 km²
* Kandidati za zeleni krov (≥ 50 m² nagiba ≤ 20°): **82 029 zgrada**, 13,4 km² iskoristivo, ~5,9 mil. m³ kišnice/god
* Kandidati za FN (≥ 3 kWp): **209 598 zgrada**, 3,4 GWp, ~3,8 TWh/god, ~511 kt CO₂/god
* Po NRW klasama: 0–5° 1170 ha, 5–10° 428 ha, 10–15° 298 ha, 15–20° 257 ha, 20–35° 1328 ha, > 35° 567 ha
* 54,5 % zgrada potječe iz snimanja 2008., a 45,3 % iz 2022.
* Validacija: tlocrti iz krovnih ploha / službeni 2D tlocrti = 1,000 (Gornji grad i Donji grad); visine u Gornjem gradu = `Z_Delta`

## Najvažnije promjene (opisno)

1. Postavljena struktura projekta, venv i dokumentacija.
2. Napravljen pipeline od 4 koraka (download → extract_roofs → pvgis → metrics) i pokrenut za cijeli Zagreb.
3. Tijekom razvoja riješene posebnosti podataka:
   * Geometrija je GeometryCollection(TIN, Polygon), koju shapely ne čita → vlastiti parser.
   * Prstenovi su u Esri konvenciji (vanjska normala = −Newell), a dio zgrada je
     zapisan obrnuto (npr. 1598 u Donjem gradu) → automatsko okretanje po zgradi.
   * Trešnjevka – sjever, Stenjevec i Podsljeme su u EPSG:3765, ostale četvrti u EPSG:4326 → CRS se čita iz izvora.
   * FGDB za Novi Zagreb – zapad GDAL ne može pročitati → automatski se koristi SHP.
   * ~1222 duplikata (537 na granicama četvrti, 685 unutar iste četvrti) → uklanjaju se u `metrics.py`.
4. Parametri iz `config.py` dijelom vezani uz izvore (oborine 880 mm – brošura ZEC-a;
   CO₂ 0,134 kg/kWh – EEA 2020; zeleni krov 130 €/m² – eMajstor; FN 1300 €/kWp).
5. Napravljen pregled literature s izvedenim koeficijentima (NRW; Wuppertal
   izračunato iz njihovog CSV-a: zadržavanje 50/40 %, CO₂ 0,75 kg/m², čestice 9,8 g/m²).

## Otvorena pitanja i nedovršeno

* **Smjer aplikacije nije odlučen.** Preporuka je spoj tri stvari: karta
  prikladnosti s karticom krova (NRW), prioritet s klizačima (San Sebastián) i naš
  dodatak (zeleno + FN + biosolarno, scenariji, javne zgrade). Tim treba odgovoriti na:
  1. Zasjenjenje: samo od zgrada iz 3D modela? (drveće nema otvorenih podataka)
  2. Statika: Zagreb nema otvorenu godinu gradnje; istražiti registar energetskih certifikata ili podatke o obnovi nakon potresa 2020.?
  3. Otkrivati postojeće zelene krovove na ortofotu (kao NYC)?
  4. Iz prošlog kruga: web karta s 3D zgradama ili jednostavniji dashboard? Kreće li se od javnih zgrada ili od toplinskih otoka?
* **Predložene izmjene metodologije nisu primijenjene** (čeka se odluka tima):
  NRW klase nagiba 0–5 / 5–10 / 10–15 / 15–35 / > 35° s izračunom do 15°
  (sada do 20°); izbor supstrata 10 / 20 / 30 cm (masa 130/280/420 kg/m²,
  zadržavanje 50/60/70 %, CO₂ 0,8/0,9/1,0 kg/m²); hlađenje isparavanjem
  (~686 kWh/m³); razredi veličine i troškova; izloženost sunčano/polusjena;
  baština kao sloj upozorenja; minimalna površina plohe 10 m² (sada 50 m² po zgradi).
* **Parametri s `TODO izvor`** u `pipeline/config.py`: DHMZ normala oborina
  1991.–2020. (Zagreb-Grič), EEA emisijski faktor za najnoviju godinu, cijena
  struje (HEP/HERA), prosječna potrošnja kućanstva (DZS/HERA), izvor za FLL klase.
* Koeficijent za fine čestice razlikuje se ~7 puta (NRW 1,4 g/m² prema Wuppertalu 9,8 g/m²). Treba odlučiti i navesti raspon.
* Zasjenjenje od susjednih zgrada nije uključeno (PVGIS uzima u obzir samo teren).
* Prioritizacija nije implementirana: nema još NDVI, LST, nepropusnosti, stanovništva ni osjetljivih korisnika.
* Registar kulturnih dobara (763 zapisa za Zagreb, 547 s adresom) **nema koordinate**, pa treba geokodirati.
* ISGE potrošnja (CSV s `;`, 419 tis. redaka) ima adrese, a ne koordinate, pa treba spajanje sa zgradama.
* `topografska-osnova-2018-objekti`: stupac "Tip objekta" je brojčani kod. Šifrarnik nije pronađen.
* U Donjem gradu visina se poklapa sa `Z_Delta` samo kod 79 % zgrada (u Gornjem gradu ~100 %). **Nije istraženo.**
* 547 objekata nema krovnu plohu (ploče < 0,3 m, otvorene ljuske poput tornjeva i dimnjaka). To je namjerno.
* Validacija na uzorku (ortofoto DGU) nije napravljena.
* Format izvoza za aplikaciju nije odlučen (GeoJSON za ~357 tis. zgrada bio bi velik; razmotriti FlatGeobuf/PMTiles).
* Projekt nije pod gitom (ponuđen `git init`, korisnik nije odgovorio).

## Što nije uspjelo

* **EIC stranica "ZG Solari"** (eic.zagreb.hr/pages/...) se učitava JavaScriptom. WebFetch je vratio samo naslov.
* **CKAN pretraga s dijakriticima preko `curl` u Git Bashu** vratila je neispravan JSON. Riješeno pozivima iz Pythona (`urllib`).
* **Prvi prototip analize krovova** računao je tlo zgrade kao ravni krov (precijenjeno). Riješeno klasifikacijom po normali.
* `shapely.from_wkb` ne podržava TIN (WKB 16) ni GeometryCollection (7), pa je napisan vlastiti parser.
* **Prvo preuzimanje** je palo na HTTP 500 za Donji grad (prolazna greška). Dodani ponovni pokušaji.
* `shapely.linearrings` je tražio uzastopne indekse. Ispravljeno s `np.unique(return_inverse=True)`.
* `shapely.set_precision` je bacio TopologyException na 2D projekcijama ploha. Zamijenjeno s `make_valid` + `buffer(0)`.
* 248 zgrada u Gornjem gradu bilo je "bez krova" zbog obrnute orijentacije. Riješeno okretanjem po zgradi.
* **FGDB Novi Zagreb – zapad:** i `pyogrio.raw.read` i `read_arrow` javljaju `GeometryError: type 3000`. Riješeno SHP-om.
* Tri četvrti u EPSG:3765 prvo su projicirane kao da su u WGS84, pa su imale 0 krovova. Riješeno čitanjem CRS-a.
* **WebFetch na PDF-ove iz literature** (Beč, NRW, NYC, Liège, San Sebastián) vratio je binarni sadržaj. Tekst je izvučen lokalno pomoću `pypdf`.
* `ckan-open-nrw.nrw.de` (Wuppertal) ima neispravan certifikat. Korišten je API na `ckan.open.nrw`.
* Web pretrage nisu dale: službenu DHMZ normalu oborina, EEA vrijednost za 2023., prosječnu potrošnju kućanstva u RH.
* Bečki PDF je samo karta (2011.). Detalji metodologije su iz sekundarnih izvora.

## Sljedeći koraci (po prioritetu)

1. **Dogovor tima o smjeru aplikacije** i odgovori na otvorena pitanja iznad.
2. **Primijeniti dogovorene izmjene metodologije** u `pipeline/config.py` i
   `pipeline/metrics.py` (NRW klase, supstrat, hlađenje isparavanjem, razredi
   veličine i troškova, izloženost), pa ponovno pokrenuti `python -m pipeline.metrics`
   (geometriju nije potrebno ponovno obrađivati). Ažurirati `docs/METODOLOGIJA.md` i README.
3. **Zatvoriti `TODO izvor` parametre** i citirati ih.
4. **Dodati podatke za prioritizaciju:** granice četvrti i mjesnih odbora (RPJ,
   data.gov.hr); Geoportal ustanove (vrtići, škole, domovi za starije, zdravstvo,
   druge javne ustanove); Copernicus nepropusnost i NDVI (Sentinel-2) i ljetni
   LST (Landsat 8/9); stanovništvo (GHSL 100 m ili DZS). Zatim indeks prioriteta s težinama.
5. **Javne zgrade:** spojiti Geoportal ustanove i ISGE potrošnju sa zgradama i
   izračunati udio potrošnje koji FN može pokriti.
6. **Baština:** geokodirati registar kulturnih dobara i prikazati ga kao sloj upozorenja.
7. **Validacija:** ručna provjera ~200 nasumičnih kandidata na ortofotu DGU-a. Istražiti razliku visina u Donjem gradu.
8. **Izvoz podataka za aplikaciju** i izrada aplikacije. Izvoz rezultata kao otvoreni podaci (CSV/GeoJSON po zgradi, kao Wuppertal).
9. `git init` za timski rad (`.gitignore` je spreman).
10. Opcionalno: zasjenjenje od zgrada iz 3D modela; otkrivanje postojećih zelenih krovova.

## Pokretanje (podsjetnik)

```bash
cd C:/DATATHON/Datathon
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.download
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.extract_roofs   # ~2-3 min, 4 procesa
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.pvgis           # već napravljeno
PYTHONIOENCODING=utf-8 .venv/Scripts/python -m pipeline.metrics         # ~30 s
```
