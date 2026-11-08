# Popis skupova podataka

Svi skupovi podataka koje Krov+ koristi, s izdavateljem, poveznicom i licencom.
Metapodaci skupova s Portala otvorenih podataka (izdavatelj, licenca) provjereni su preko CKAN API-ja
data.gov.hr 8. 11. 2026. Način obrade opisan je u [`METODOLOGIJA.md`](METODOLOGIJA.md), a tok podataka
u [`ARHITEKTURA.md`](ARHITEKTURA.md).

## 1. Portal otvorenih podataka (data.gov.hr)

| Skup podataka | Izdavatelj | Licenca | Kako se dohvaća | Uporaba u projektu |
|---|---|---|---|---|
| **ZG3D – 3D model zgrada Grada Zagreba**, LoD 2.2, 17 skupova (po jedan za svaku gradsku četvrt, tablica 1a) | Grad Zagreb | [Otvorena dozvola](https://data.gov.hr/id/licence/otvorena-dozvola-rh) | automatski, **CKAN API** (`pipeline/download.py`), format FGDB (multipatch 3D) | geometrija svih krovnih ploha: nagib, orijentacija, površina, visina zgrade, godina snimanja |
| [**Podaci o potrošnji i trošku za objekte Grada Zagreba**](https://data.gov.hr/ckan/dataset/podaci-o-potrosnji-i-trosku-za-objekte-grada-zagreba) (ISGE, 2019.–2024.) | Grad Zagreb | [Otvorena dozvola](https://data.gov.hr/id/licence/otvorena-dozvola-rh) | preuzet CSV (`data/reference/isge/`) | potrošnja električne energije objekata Grada u 2023.; udio koji FN na krovu može pokriti; prikaz „samo objekti Grada“ |
| [**Registar kulturnih dobara**](https://data.gov.hr/ckan/dataset/kulturna-dobra) | Ministarstvo kulture i medija | [Otvorena dozvola](https://data.gov.hr/id/licence/otvorena-dozvola-rh) | preuzet CSV (`data/reference/kulturna_dobra/`) | oznaka zaštićenih zgrada u kartici i na karti (suglasnost konzervatora) |

**Tablica 1a – ZG3D po gradskim četvrtima** (svi skupovi: izdavatelj Grad Zagreb, Otvorena dozvola).
Identifikatori su u `pipeline/config.py` (`DISTRICTS`).

| Gradska četvrt | Skup podataka |
|---|---|
| Donji grad | [ZG3D Gradska četvrt Donji Grad 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-donji-grad-2022) |
| Gornji grad – Medveščak | [ZG3D Gradska četvrt Gornji Grad 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-gornji-grad-2022) |
| Trnje | [ZG3D Gradska četvrt Trnje 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-trnje-2022) |
| Maksimir | [ZG3D Gradska četvrt Maksimir 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-maksimir-2022) |
| Peščenica – Žitnjak | [ZG3D Gradska četvrt Peščenica Žitnjak 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-pescenica-zitnjak-2022) |
| Novi Zagreb – istok | [ZG3D Gradska četvrt Novi Zagreb istok 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-novi-zagreb-istok-2022) |
| Novi Zagreb – zapad | [ZG3D Gradska četvrt Novi Zagreb zapad 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-novi-zagreb-zapad-2022) |
| Trešnjevka – sjever | [ZG3D Gradska četvrt Trešnjevka sjever 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-tresnjevka-sjever-2022) |
| Trešnjevka – jug | [ZG3D Gradska četvrt Trešnjevka jug 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-tresnjevka-jug-2022) |
| Črnomerec | [ZG3D Gradska četvrt Črnomerec 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-crnomerec-2022) |
| Gornja Dubrava | [ZG3D Gradska četvrt Gornja Dubrava 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-gornja-dubrava-2022) |
| Donja Dubrava | [ZG3D Gradska četvrt Donja Dubrava 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-donja-dubrava-2022) |
| Stenjevec | [ZG3D Gradska četvrt Stenjevec 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-stenjevec-2022) |
| Podsused – Vrapče | [ZG3D Gradska četvrt Podsused Vrapče 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-podsused-vrapce-2022) |
| Podsljeme | [ZG3D Gradska četvrt Podsljeme 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-podsljeme-2022) |
| Sesvete | [ZG3D Gradska četvrt Sesvete](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-sesvete) |
| Brezovica | [ZG3D Gradska četvrt Brezovica 2022](https://data.gov.hr/ckan/dataset/zg3d-gradska-cetvrt-brezovica-2022) |

**Navođenje izvora prema Otvorenoj dozvoli:** u aplikaciji (prozor „O projektu i izvorima podataka“),
u ovom dokumentu i u README-u navodi se izdavatelj i Portal otvorenih podataka. Izvorni podaci se ne
mijenjaju; izvedeni podaci (potencijal po zgradi, četvrti i gradu) objavljuju se pod CC BY 4.0 uz
navođenje ovih izvora (vidi poglavlje 4).

## 2. Ostali javni izvori podataka (tijela javnog sektora i EU)

| Skup podataka | Izdavatelj | Licenca / uvjeti | Kako se dohvaća | Uporaba u projektu |
|---|---|---|---|---|
| [**PVGIS 5.3**](https://re.jrc.ec.europa.eu/pvg_tools/en/) (sunčevo zračenje SARAH3, 2005.–2023.) | Zajednički istraživački centar Europske komisije (JRC) | ponovna uporaba uz navođenje izvora ([Odluka Komisije 2011/833/EU](https://eur-lex.europa.eu/eli/dec/2011/833/oj)) | automatski, **PVGIS API** (`pipeline/pvgis.py`), ~300 upita | godišnji prinos FN (kWh/kWp) za svaku kombinaciju nagiba i orijentacije u Zagrebu (`data/reference/pvgis_zagreb.json`) |
| Klimatološki podaci, postaje [Zagreb-Grič](https://meteo.hr/klima.php?section=klima_podaci&param=k1&Grad=zagreb_gric) i [Zagreb-Maksimir](https://meteo.hr/klima.php?section=klima_podaci&param=k1&Grad=zagreb_maksimir) | Državni hidrometeorološki zavod (DHMZ) | javno objavljeni podaci, uz navođenje izvora | ručno, vrijednost u `pipeline/config.py` | godišnja oborina (880 mm) za zadržanu kišnicu |
| [Intenzitet emisija stakleničkih plinova proizvodnje el. energije](https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1/greenhouse-gas-emission-intensity-of-electricity-generation-country-level) | Europska agencija za okoliš (EEA) | [CC BY 4.0](https://www.eea.europa.eu/en/legal-notice) | ručno, vrijednost u `pipeline/config.py` | izbjegnute emisije CO₂ (0,134 kg CO₂e/kWh) |
| [Cijene el. energije za kućanstva (nrg_pc_204)](https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table) | Eurostat | ponovna uporaba uz navođenje izvora ([Odluka Komisije 2011/833/EU](https://eur-lex.europa.eu/eli/dec/2011/833/oj)) | ručno, vrijednost u `pipeline/config.py` | ušteda i povrat ulaganja u FN (0,18 €/kWh) |
| [Energetska bilanca (nrg_bal_c)](https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table) i [broj kućanstava (lfst_hhnhtych)](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhnhtych/default/table) | Eurostat | kao gore | ručno | prosječna potrošnja kućanstva u RH (4 630 kWh/god) za ekvivalent kućanstava |

Svi parametri izračuna s vrijednostima i izvorima navedeni su u [`METODOLOGIJA.md`](METODOLOGIJA.md), poglavlje 8.

## 3. Otvoreni podaci zajednice (OpenStreetMap)

| Skup podataka / usluga | Izdavatelj | Licenca / uvjeti | Uporaba u projektu |
|---|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | suradnici OpenStreetMapa | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/) | izvor podloge karte i adresa za geokodiranje |
| Podloga karte [OpenFreeMap](https://openfreemap.org) (stil Positron, shema OpenMapTiles) | OpenFreeMap, © OpenMapTiles, © suradnici OSM-a | ODbL (podaci), uvjeti OpenFreeMapa | podloga web karte (ceste, nazivi, voda), bez API ključa |
| [Nominatim](https://nominatim.org) (geokoder za OSM) | OpenStreetMap Foundation | [pravila korištenja](https://operations.osmfoundation.org/policies/nominatim/), rezultati pod ODbL | (1) geokodiranje adresa kulturnih dobara i ISGE objekata, najviše 1 upit/s, odgovori spremljeni u `data/reference/geocode/nominatim.json`; (2) pretraga adresa u aplikaciji, samo na Enter |

Atribucija „© suradnici OpenStreetMapa“ prikazuje se na karti i u prozoru „O projektu“.
Predmemorija geokodiranja (`data/reference/geocode/nominatim.json`) izvedena je iz OSM-a i dijeli se pod ODbL.

## 4. Podaci koje projekt objavljuje

| Skup | Sadržaj | Licenca |
|---|---|---|
| `app/public/data/buildings.pmtiles` (prilog Releasea [`podaci`](https://github.com/korejur/DataOasis/releases/tag/podaci)) | potencijal zelenog krova i FN za 356 437 zgrada, oznake kulturnih dobara i objekata Grada | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.hr) |
| `app/public/data/districts.json`, `city.json` | zbrojevi po gradskim četvrtima i za grad, korišteni parametri | CC BY 4.0 |
| `data/processed/*.parquet` (nastaje pokretanjem pipelinea) | krovne plohe, zgrade s metrikama, veze zgrada s kulturnim dobrima i ISGE-om | CC BY 4.0 |

Uz izvedene podatke treba navesti izvore iz poglavlja 1–3.

## 5. Razmotreni, a nekorišteni skupovi

| Skup podataka | Izdavatelj | Zašto nije korišten |
|---|---|---|
| Topografska osnova 2018 – objekti (`data/reference/topo_objekti/`) | Grad Zagreb | stupac „Tip objekta“ je brojčani kod bez dostupnog šifrarnika; ZG3D ima bolju geometriju |
| Geoportal Grada Zagreba: vrtići, škole, domovi za starije, zdravstvo; granice gradskih četvrti i mjesnih odbora | Grad Zagreb | planirano za prioritizaciju po osjetljivim korisnicima; nije predano do predaje (vidi `STATUS.md`) |
| Landsat 8/9 (temperatura površine), Sentinel-2 (NDVI), GHSL (stanovništvo) | USGS/NASA, ESA/Copernicus, JRC | planirano za toplinske otoke i prioritizaciju (daljnji razvoj, [`PROJEKT.md`](PROJEKT.md)) |
