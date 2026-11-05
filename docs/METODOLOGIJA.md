# Metodologija izračuna

Svi parametri navedeni ovdje nalaze se u `pipeline/config.py` (`GEOM`, `PARAMS`).
Vrijednosti označene s **TODO izvor** treba potvrditi i citirati prije predaje.

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

Okvirno prema FLL smjernicama (Njemačka): do ~15° bez posebnih mjera, iznad
treba zaštita od klizanja supstrata. **TODO izvor**

* `prikladna površina = Σ A (visoka + srednja)`
* `iskoristiva površina = prikladna × 0,75` (rubovi, instalacije, izlazi na krov)
* zgrada je **kandidat** ako je prikladna površina ≥ 50 m²

### 3.2 Doprinosi

* **Zadržana oborinska voda** [m³/god]: `V = A_isk × P × r`,
  gdje je `P` = 880 mm/god, a `r` = 0,50 (udio zadržane godišnje oborine).
  Literatura za ekstenzivne krovove daje 35–90 % pa je 50 % konzervativno.
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

* **CO₂** [t/god] = `E × 0,134 kg/kWh / 1000` (EEA, intenzitet emisija proizvodnje el. energije RH, 2020.) **TODO ažurirati**
* **Ekvivalent kućanstava** = `E / 3500 kWh` **TODO izvor (DZS/HERA)**
* **Investicija** = `P × 1300 €/kWp` (hrvatski izvori 2025.: 1200–1500 €/kWp)
* **Jednostavni povrat** = `investicija / (E × 0,15 €/kWh)`. Bez subvencija.
  FZOEU sufinancira do 600 €/kW za obiteljske kuće.

### 4.4 Zeleno ili solarno?

Na ravnim krovovima obje mjere se natječu za istu površinu. Aplikacija
prikazuje oba potencijala odvojeno i nudi tri scenarija:
(a) samo zeleno, (b) samo FN, (c) **biosolarni krov**, gdje FN na nosačima
stoji iznad ekstenzivnog zelenog krova. Zelenilo hladi module, pa raste
učinkovitost. Literatura navodi nekoliko posto. **TODO izvor**

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
