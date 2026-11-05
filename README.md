# Krovovi za klimu – Zagreb

Datathon Portala otvorenih podataka 2026. Alat za urbaniste koji iz 3D modela
zgrada Grada Zagreba (ZG3D, LoD 2.2) pronalazi krovove pogodne za **zelene
krovove** i **fotonapon**, procjenjuje njihov doprinos (zadržana oborinska
voda, proizvedena energija, smanjenje CO₂, trošak) i pomaže odrediti gdje
krenuti prvo.

Metodologija i formule: [docs/METODOLOGIJA.md](docs/METODOLOGIJA.md)

## Struktura

```
pipeline/           obrada podataka (Python)
  config.py         putanje, popis četvrti, SVI parametri izračuna
  download.py       1) preuzimanje ZG3D FGDB-a za 17 četvrti (CKAN API)
  extract_roofs.py  2) 3D plohe -> krovne plohe (nagib, azimut, površina)
  pvgis.py          3) tablica FN prinosa za Zagreb (PVGIS, JRC)
  metrics.py        4) potencijal po zgradi, četvrti i gradu
data/
  raw/              preuzeti izvorni podaci (nije u gitu)
  reference/        pomoćni skupovi (PVGIS, kulturna dobra, ISGE...)
  processed/        rezultati (nije u gitu)
docs/               metodologija, bilješke
app/                web aplikacija (u izradi)
```

## Pokretanje

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# .venv/bin/python ...                                     # Linux/macOS

.venv/Scripts/python -m pipeline.download        # ~1,2 GB raspakirano, nekoliko minuta
.venv/Scripts/python -m pipeline.extract_roofs   # paralelno po četvrtima
.venv/Scripts/python -m pipeline.pvgis           # ~300 upita prema PVGIS-u
.venv/Scripts/python -m pipeline.metrics         # ~10 s, ponoviti nakon promjene parametara
```

Na Windowsu za ispis dijakritika postaviti `PYTHONIOENCODING=utf-8`.

## Izlazi (`data/processed/`)

| Datoteka | Sadržaj |
|---|---|
| `faces/<četvrt>.parquet` | sve krovne plohe: 3D poligon (EPSG:3765), površina, nagib, azimut, visina |
| `buildings/<četvrt>.parquet` | zgrade: tlocrt krova, visina, površine krova/zidova |
| `buildings_metrics.parquet` | zgrade + potencijal zelenog krova i FN, troškovi, doprinosi |
| `district_summary.csv` | zbirni pokazatelji po gradskim četvrtima i za grad |
| `city_summary.json` | ukupno za grad + korišteni parametri |

## Prvi rezultati (tehnički potencijal, 3. 11. 2026.)

| Pokazatelj | Grad Zagreb |
|---|---|
| Zgrade (bez duplikata) | 356 984 |
| Ukupna krovna površina | 40,5 km² |
| Ravni krovovi (< 10°) | 16,0 km² (142 306 zgrada s pretežno ravnim krovom) |
| **Kandidati za zeleni krov** (≥ 50 m² nagiba ≤ 20°) | **82 029 zgrada**, 13,4 km² iskoristivo |
| Zadržana oborinska voda (ako se ozelene svi kandidati) | ~5,9 mil. m³/god |
| **Kandidati za FN** (≥ 3 kWp) | **209 598 zgrada**, 3,4 GWp, ~3,8 TWh/god |
| Izbjegnute emisije CO₂ (FN) | ~511 000 t/god |

To je *tehnički* potencijal, odnosno gornja granica. U aplikaciji se
prikazuju scenariji (npr. 10 % ili 30 % kandidata, samo javne zgrade).
Pretpostavke su u `docs/METODOLOGIJA.md`.

## Izvori podataka

| Skup podataka | Izdavač | Uporaba |
|---|---|---|
| ZG3D 3D model zgrada (17 četvrti), LoD 2.2 | Grad Zagreb, data.gov.hr | geometrija krovova |
| PVGIS v5.3 (SARAH3, 2005.–2023.) | JRC, Europska komisija | prinos FN po nagibu/orijentaciji |
| Podaci o potrošnji i trošku za objekte Grada Zagreba (ISGE) | Grad Zagreb | potrošnja javnih zgrada (planirano) |
| Registar kulturnih dobara | Ministarstvo kulture i medija | isključenje/oznaka zaštićenih zgrada (planirano) |
| Geoportal: vrtići, škole, domovi za starije, zdravstvo | Grad Zagreb | osjetljivi korisnici (planirano) |
| Gradske četvrti, mjesni odbori (RPJ) | Grad Zagreb | agregacija (planirano) |
| Planirana namjena 2023, Topografska osnova 2018 | Grad Zagreb | namjena prostora, vegetacija (planirano) |
