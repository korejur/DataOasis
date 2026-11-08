# Metodologija izračuna

Svi parametri navedeni ovdje nalaze se u `pipeline/config.py` (`GEOM`, `PARAMS`).
Izvori svih parametara su u poglavlju 8. Gdje izvora nema, vrijednost je označena kao vlastita pretpostavka.

## 1. Tok obrade

```
ZG3D FGDB (17 četvrti)  ──►  3D plohe zgrade  ──►  klasifikacija ploha  ──►  krovne plohe
                                                                              │ nagib, azimut, površina
PVGIS (JRC) ──► tablica prinosa kWh/kWp (nagib × azimut) ─────────────────────┤
                                                                              ▼
                                          potencijal po plohi ──► po zgradi ──► po četvrti / gradu
                                                                              ▲
            (planirano) toplinski otoci, stanovništvo, osjetljivi korisnici, ─┘ prioritet
            kulturna dobra, javne zgrade i njihova potrošnja (ISGE)
```

## 2. Geometrija krovova iz ZG3D

ZG3D je LoD 2.2 model: svaka zgrada je skup ravnih 3D ploha (krovne plohe,
zidovi, tlo). Format FGDB čuva tu geometriju (multipatch). CSV, GeoJSON i SHP
sadrže samo 2D tlocrt, pa se za analizu krovova koristi isključivo FGDB.

Za svaku plohu (koordinate u HTRS96/TM, EPSG:3765, metri):

* **Vektor površine** (Newellova metoda) za prsten s točkama (xᵢ, yᵢ, zᵢ):
  `Nx = ½ Σ (yᵢ − yᵢ₊₁)(zᵢ + zᵢ₊₁)`, `Ny = ½ Σ (zᵢ − zᵢ₊₁)(xᵢ + xᵢ₊₁)`, `Nz = ½ Σ (xᵢ − xᵢ₊₁)(yᵢ + yᵢ₊₁)`
* **Stvarna (kosa) površina** `A = |N_vanjski| − Σ |N_rupa|`
* **Jedinična normala** `n = −N/|N|` (Esri zapis: prstenovi u smjeru kazaljke na satu)
* **Nagib** `β = arccos(n_z)`
* **Azimut** (smjer u koji ploha "gleda") `γ = atan2(n_x, n_y)`: 0° = S, 90° = I, 180° = J, 270° = Z
* **Tlocrtna površina** `A_2D = A · n_z`

**Klasifikacija:**

| Klasa | Uvjet |
|---|---|
| krov | `n_z > 0,17` (nagib < ~80°) i ploha je > 0,3 m iznad najniže točke zgrade |
| zid | `|n_z| ≤ 0,17` |
| ostalo | tlo zgrade, donje strane prepusta (`n_z < −0,17`) |

**Kontrola orijentacije:** 190 od 15 029 zgrada u Gornjem gradu zapisano je
s obrnutim redoslijedom točaka. Ako je kod zgrade površina ploha iznad tla
okrenutih prema dolje veća od onih okrenutih prema gore, normale te zgrade
se okreću.

**Validacija (Gornji grad):**

* tlocrt dobiven iz krovnih ploha / službeni 2D tlocrt iz GeoJSON-a: medijan 1,000 (p5 0,999; p95 1,000)
* visina zgrade = atribut `Z_Delta` (medijan razlike 0,000 m)
* bez krova ostaje 60 objekata: ploče niže od 0,3 m i otvorene ljuske bez
  krova (tornjevi, dimnjaci; `Volume = 0`). Njih je ispravno izostaviti.
* Donji grad: 1598 okrenutih zgrada ima tlocrt jednak službenom (medijan 1,000),
  pa je ispravak orijentacije točan.

**Posebnosti izvornih podataka (riješeno u pipelineu):**

| Problem | Rješenje |
|---|---|
| Trešnjevka – sjever, Stenjevec i Podsljeme objavljeni su u EPSG:3765, ostale četvrti u EPSG:4326 | CRS se čita iz izvora |
| FGDB za Novi Zagreb – zapad ima sloj tipa "Unknown ZM", koji GDAL ne čita | automatski se koristi SHP verzija (također multipatch 3D) |
| Geometrija je GeometryCollection(TIN, Polygon), koju shapely ne čita | vlastiti WKB parser (`parse_faces`) |
| 537 zgrada na granicama četvrti je u dva skupa, a 685 objekata je upisano dvaput u istoj četvrti | uklanjanje duplikata (isti centroid na 10 cm, visina, površina krova) |
| 54,5 % zgrada potječe iz snimanja 2008., a 45,3 % iz 2022. | `godina_izv` se prikazuje kao pouzdanost |

## 3. Zeleni krovovi

### 3.1 Prikladnost

| Klasa | Nagib | Tip zelenog krova |
|---|---|---|
| visoka | 0–10° | ekstenzivni i intenzivni |
| srednja | 10–20° | ekstenzivni |
| niska | 20–35° | ekstenzivni uz protuklizne mjere (ne ulazi u kandidate) |
| neprikladno | > 35° | — |

Prema FLL smjernicama (2018), kako ih prenosi metodologija Gründachkataster NRW
(LANUV): do ~15° bez posebnih mjera, iznad treba zaštita od klizanja supstrata,
a iznad ~35° zeleni krov praktički nije izvediv. Naše klase su grublje od NRW-ovih.

* `prikladna površina = Σ A (visoka + srednja)`
* `iskoristiva površina = prikladna × 0,75` (rubovi, instalacije, izlazi na krov;
  **vlastita pretpostavka**, nije iz literature)
* zgrada je **kandidat** ako je prikladna površina ≥ 50 m²

### 3.2 Doprinosi

* **Zadržana oborinska voda** [m³/god]: `V = A_isk × P × r`,
  gdje je `P` = 880 mm/god, a `r` = 0,50 (udio zadržane godišnje oborine).
  `P`: DHMZ, zbroj srednjih mjesečnih oborina: Zagreb-Grič 887 mm (1861.–2024.),
  Zagreb-Maksimir 868 mm (1949.–2024.). `r`: FLL (2018) daje 50 % za 10 cm supstrata,
  a Mentens i sur. (2006) ~45 % za ekstenzivne krovove.
  To je voda koja ne opterećuje kanalizaciju (Zagreb ima mješoviti sustav).
* **Trošak** [€]: `A_isk × 130 €/m²` (eMajstor 2026.: 108–180 €/m² bez hidroizolacije)
* **Hlađenje / toplinski otok** (planirano): povezivanje s temperaturom
  površine iz Landsata (vidi 5.). Iznos u °C ne računamo jer ovisi o
  mikroklimi, pa se koristi kao kriterij prioriteta.
* Moguće dodati: površina staništa za oprašivače (m²), smanjenje potrošnje
  za hlađenje zadnjeg kata (kvalitativno).

## 4. Fotonapon (FN)

### 4.1 Prinos

PVGIS v5.3 (JRC; SARAH3 2005.–2023.; gubici sustava 14 %; horizont iz DEM-a)
za Zagreb (45,813° N, 15,977° E), mreža nagib 0–90° (korak 5°) × azimut
0–345° (korak 15°), s bilinearnom interpolacijom.
Optimum: 35° prema jugu, 1242 kWh/kWp. Vodoravno: 1053 kWh/kWp.

### 4.2 Snaga i proizvodnja po plohi

* **Kosa ploha** (nagib > 10°): moduli položeni po krovu
  `P = A × 0,70 × 0,20 kWp/m²`, prinos `Y(β, γ)`
* **Ravna ploha** (nagib ≤ 10°): moduli na nosačima 15° prema jugu, u redovima
  `P = A_2D × 0,50 × 0,20 kWp/m²`, prinos `Y(15°, 180°)` = ~1174 kWh/kWp
* plohe se ne koriste ako su strmije od 60°, imaju prinos < 900 kWh/kWp
  (npr. sjeverne plohe) ili su manje od 5 m²
* `E [kWh/god] = P × Y`
* zgrada je **kandidat** ako stane ≥ 3 kWp

### 4.3 Doprinosi

* **CO₂** [t/god] = `E × 0,134 kg/kWh / 1000` (EEA, intenzitet emisija proizvodnje el. energije RH, 2020.;
  novije godine EEA objavljuje samo u interaktivnom grafikonu)
* **Ekvivalent kućanstava** = `E / 4630 kWh` (Eurostat: potrošnja el. energije kućanstava u RH 2024.
  6 818 GWh / 1 471,9 tis. kućanstava). Za cijeli grad je to tehnički potencijal, veći od broja kućanstava u Zagrebu.
* **Investicija** = `P × 1300 €/kWp` (hrvatski izvori 2025.: 1200–1500 €/kWp)
* **Jednostavni povrat** = `investicija / (E × 0,18 €/kWh)` (Eurostat, cijena za kućanstva u RH,
  razred 2 500–4 999 kWh, sa svim porezima, 1. pol. 2026.). Bez subvencija. Pretpostavlja da se
  sva proizvedena energija troši na mjestu, pa je za zgrade s viškom proizvodnje optimistično.
  FZOEU sufinancira do 600 €/kW za obiteljske kuće.

### 4.4 Zeleno ili solarno?

Na ravnim krovovima obje mjere se natječu za istu površinu. Aplikacija
prikazuje oba potencijala odvojeno i nudi tri scenarija:
(a) samo zeleno, (b) samo FN, (c) **biosolarni krov**, gdje FN na nosačima
stoji iznad ekstenzivnog zelenog krova. Zelenilo hladi module, pa raste
učinkovitost: na krovu u Sydneyju prosječno +3,6 % (UTS, 2021.), na većem krovu u Bradfieldu
prosječno +11 %, a u toplinskim valovima do +23 % (UTS, 2026.). Taj učinak ne ulazi u izračun.

### 4.5 Usporedba s postojećim alatom

Solarna karta Grada Zagreba (EIC) radi izračun za pojedinu zgradu. Naš
pristup je prostorni i gradski: rang-lista, scenariji i kombinacija sa
zelenim krovovima. Rezultate po zgradi možemo usporediti s EIC kartom za
nekoliko adresa kao validaciju.

## 5. Prioritizacija (planirano)

Cilj nije samo "gdje je moguće", nego **"gdje najviše treba"**.

```
Prioritet_ZK = Prikladnost × (w₁·Toplina + w₂·Stanovništvo + w₃·NedostatakZelenila + w₄·Osjetljivi) × Izvedivost
```

| Komponenta | Podatak | Izvor |
|---|---|---|
| Prikladnost | log(iskoristiva površina), normirano 0–1 | ZG3D (ovaj pipeline) |
| Toplina | ljetna temperatura površine (LST), percentil u gradu | Landsat 8/9 Collection 2 L2 (USGS/NASA, otvoreno), lipanj–kolovoz 2022.–2025. |
| Stanovništvo | gustoća stanovnika u okolici zgrade | GHSL GHS-POP 100 m (JRC) ili Popis 2021 (DZS) |
| Nedostatak zelenila | udio vegetacije u radijusu 300 m (manje → veći prioritet) | Topografska osnova 2018 – vegetacija (Grad Zagreb) ili Sentinel-2 NDVI |
| Osjetljivi korisnici | zgrada je ili je blizu vrtića, škole, doma za starije, zdravstvene ustanove | Geoportal Grada Zagreba (data.gov.hr) |
| Izvedivost | kulturno dobro → oznaka/isključenje; starost podataka (`Godina_izv`) → pouzdanost | Registar kulturnih dobara (MinKulture), ZG3D |

Težine `w` bira urbanist u aplikaciji (klizači). Zadane su jednake.

**Javne zgrade** (Grad sam odlučuje, pa su to brze pobjede): spajanje lokacija
ustanova (Geoportal) s tlocrtima i s potrošnjom iz ISGE-a (2019.–2024.,
mjesečno po objektu). Za FN se iz toga računa **udio pokrivanja vlastite
potrošnje** `E_FN / E_potrošnja`.

## 6. Ograničenja

* Dio modela potječe iz snimanja 2008. godine, pa novije promjene krovova
  (nadogradnje, postojeći FN) nisu vidljive. Svaka zgrada nosi godinu izvora.
* Nosivost konstrukcije nije poznata. Rezultat znači "kandidat za
  statičku provjeru", a ne "izvedivo".
* Zasjenjenje od susjednih zgrada i drveća još nije uključeno (PVGIS
  uzima u obzir samo teren). Moguća nadogradnja je sjena iz 3D modela.
* Krovne instalacije (klima uređaji, izlazi, svjetlarnici) obuhvaćene su
  samo paušalnim faktorom iskoristivosti.
* Ekonomski parametri (cijene, subvencije, net-metering) se mijenjaju, pa
  ih treba prikazati kao pretpostavke i dopustiti promjenu u aplikaciji.
* 547 objekata nema krovnu plohu (ploče niže od 0,3 m, otvorene ljuske poput
  tornjeva i dimnjaka). Namjerno su izostavljeni.
* U Donjem gradu se visina iz modela poklapa sa `Z_Delta` kod 79 % zgrada
  (u Gornjem gradu ~100 %). Uzrok još nije istražen.

## 7. Napomene o pomoćnim skupovima podataka

* **Registar kulturnih dobara:** 763 zapisa za Zagreb, od toga 547 s adresom,
  bez koordinata. Za spajanje sa zgradama treba geokodiranje adresa.
* **ISGE potrošnja objekata Grada (2019.–2024.):** CSV sa separatorom `;`,
  ~419 tisuća redaka (mjesečno po mjernom mjestu). Ima adrese, ali ne i koordinate.
* **Topografska osnova 2018 – objekti:** stupac „Tip objekta“ je brojčani kod,
  a šifrarnik nije pronađen.

### 7.1 Povezivanje adresa sa zgradama (geokodiranje)

Registar kulturnih dobara i ISGE imaju adrese, ali ne i koordinate (`pipeline/geocode.py`):

* adrese se čiste (vodeće nule, više adresa u jednom zapisu, rasponi kućnih brojeva, kratice „Av.“ i „Al.“)
  i geokodiraju preko **Nominatima** (OpenStreetMap), najviše 1 upit u sekundi; odgovori se čuvaju u
  `data/reference/geocode/nominatim.json`, pa je postupak ponovljiv;
* prihvaća se samo pogodak **s kućnim brojem**; točka se veže uz tlocrt zgrade u kojem leži ili uz
  najbližu zgradu udaljenu **do 15 m**;
* rezultat: kulturna dobra **368 od 470** zapisa s adresom vezano je uz zgradu (393 zgrade);
  ISGE **854 zgrade** od 1 082 objekta s potrošnjom struje.

**ISGE:** koristi se potrošnja **električne energije u 2023.** (za 2024. postoji samo siječanj–lipanj).
**Udio koji FN može pokriti** = `E_FN / E_potrošnja` prikazuje se samo za objekte s potrošnjom
**≥ 20 MWh/god**. Manji potrošači (npr. uredi mjesne samouprave, knjižnice) koriste samo dio zgrade,
pa bi omjer prema proizvodnji cijelog krova bio višestruko prevelik (medijan ~250 %, nakon praga 104 %).

### 7.2 Prikaz „samo objekti Grada“

Prekidač u panelu ograničava brojke, rang-listu četvrti i kartu na zgrade povezane s ISGE-om
(853 zgrade u izvozu; jedna od 854 povezanih, Gradsko kazalište Trešnja, vezana je uz primjerak zgrade
koji je uklonjen kao duplikat na granici četvrti, vidi `pipeline/metrics.py`). Zbrojevi se računaju istom
funkcijom kao za cijeli grad (`pipeline/metrics.py`, `summarize`) i spremaju u `city.json` i
`districts.json` pod ključem `javno` (`pipeline/export_app.py --samo-json`).

* **Pokrivenost potrošnje** = `Σ E_FN / Σ E_potrošnja` samo za objekte s potrošnjom **≥ 20 MWh/god**
  (452 zgrade), uz isti razlog kao u 7.1; `E_FN` se zbraja samo za krovove pogodne za FN.
  Za cijeli grad: 54,4 GWh / 72,9 GWh ≈ **75 %** (tehnički potencijal, bez pohrane i vremenskog
  usklađivanja proizvodnje i potrošnje).
* Obuhvat su samo objekti čiju potrošnju Grad prati u ISGE-u. Državne zgrade (ministarstva,
  fakulteti, bolnice u vlasništvu države) i objekti bez zapisa u ISGE-u nisu uključeni.
* Scenarij (10 / 30 / 100 %) skalira proizvodnju linearno, kao i za cijeli grad.

## 8. Izvori parametara

Provjereno 8. 11. 2026. Vrijednosti su u `pipeline/config.py` (`PARAMS`).

| Parametar | Vrijednost | Izvor |
|---|---|---|
| Klase nagiba za zeleni krov | 0–10 / 10–20 / 20–35° | FLL (2018) *Dachbegrünungsrichtlinien*, preko [LANUV NRW: Methodik Gründachkataster NRW](https://www.klimaatlas.nrw.de/sites/default/files/2022-11/Methodik_Planung_Bau_GruendachkatasterNRW_0.pdf) |
| Iskoristivi udio krova | 0,75 | vlastita pretpostavka (rubovi, instalacije, izlazi) |
| Godišnja oborina | 880 mm | DHMZ, klimatološki podaci: [Zagreb-Grič](https://meteo.hr/klima.php?section=klima_podaci&param=k1&Grad=zagreb_gric) 887 mm (1861.–2024.), [Zagreb-Maksimir](https://meteo.hr/klima.php?section=klima_podaci&param=k1&Grad=zagreb_maksimir) 868 mm (1949.–2024.); zbroj srednjih mjesečnih vrijednosti |
| Godišnje zadržavanje (ekstenzivni krov) | 50 % | FLL (2018) preko LANUV NRW (50 % za 10 cm supstrata); Mentens, Raes i Hermy (2006), *Landscape and Urban Planning* 77(3), 217–226 (~45 %) |
| Trošak zelenog krova | 130 €/m² | eMajstor (2026.): 108–180 €/m² bez hidroizolacije |
| Prinos FN | PVGIS | [PVGIS 5.3, JRC](https://re.jrc.ec.europa.eu/pvg_tools/en/) (SARAH3, 2005.–2023.) |
| Trošak FN | 1 300 €/kWp | hrvatski izvori 2025.: 1 200–1 500 €/kWp |
| Emisije el. energije | 0,134 kg CO₂e/kWh | [EEA: intenzitet emisija proizvodnje el. energije](https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1/greenhouse-gas-emission-intensity-of-electricity-generation-country-level), RH 2020.: 133,8 g/kWh |
| Cijena el. energije za kućanstva | 0,18 €/kWh | [Eurostat nrg_pc_204](https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table): RH, 2 500–4 999 kWh, svi porezi, 2026-S1: 0,1816 (2025-S2: 0,1652) |
| Potrošnja kućanstva | 4 630 kWh/god | [Eurostat nrg_bal_c](https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_c/default/table) (kućanstva, el. energija, RH 2024.: 6 818 GWh) / [Eurostat lfst_hhnhtych](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhnhtych/default/table) (1 471,9 tis. kućanstava, 2024.) |
| Biosolarni krov (samo u tekstu) | +3,6 % do +11 % | UTS (Sydney, 2021.); UTS (Bradfield, 2026.), [pv magazine, 11. 8. 2026.](https://www.pv-magazine.com/2026/08/11/biosolar-design-boosts-rooftop-pv-performance-by-23-25/) |
