# Scenarij videa – Krov+

Video do **3:00** (pravila: problem, ciljni korisnici, izvori podataka, funkcionalnosti, tehnička
arhitektura, korisnička vrijednost, daljnji razvoj; vidi `docs/NATJECANJE.md`). Ocjenjuje se jasnoća,
struktura i **demonstracija stvarnog korištenja**, pa je veći dio videa snimka zaslona javne aplikacije.

* **Glas:** jedan glas, smireno, ~135 riječi u minuti. Tekst je u pasivu, bez „mi“ i „naš“.
* **Titlovi:** cijeli govor kao titlovi (gledatelji često gledaju bez zvuka).
* **Format:** 1920 × 1080, preglednik preko cijelog zaslona, bez traka s karticama (F11).
* **Brojke** su iz `app/public/data/city.json` (izvoz 8. 11. 2026.) i `docs/METODOLOGIJA.md`.
  Za cijeli grad koristi se scenarij **30 %** (odluka u STATUS-u), ne „svi kandidati“.

## Pregled po vremenu

| Vrijeme | Dio | Na zaslonu |
|---|---|---|
| 0:00–0:15 | Uvod | Karta Zagreba izdaleka, polako zumiranje prema središtu; naslov **Krov+** |
| 0:15–0:40 | Problem | Karta središta, sloj zelenih krovova |
| 0:40–0:55 | Korisnici | Panel s brojkama za grad |
| 0:55–1:20 | Podaci | Grafika s izvorima (popis ispod) |
| 1:20–2:15 | Funkcionalnosti (demo) | Snimka korištenja aplikacije |
| 2:15–2:35 | Arhitektura | Dijagram toka podataka |
| 2:35–2:50 | Vrijednost | Panel „samo objekti Grada“ |
| 2:50–3:00 | Daljnji razvoj i kraj | Karta izdaleka, naslov i poveznica |

## Tekst i kadrovi

### 0:00–0:15 · Uvod

> Zagreb ima oko četrdeset četvornih kilometara krovova.
> Krov+ pokazuje koji od njih mogu postati zeleni ili dobiti solarne panele, i koliko bi to pomoglo gradu.

*Kadar:* javni link, zum 11 → 15 na središte grada; u kutu naslov **Krov+ · Krov za zelenije sutra**.

### 0:15–0:40 · Problem

> Ljeta su sve toplija, a pljuskovi sve jači. Beton i asfalt zagrijavaju grad, a kišnica s krovova
> odlazi ravno u mješovitu kanalizaciju i opterećuje je kad je najteže.
> Zeleni krov zadržava kišu i hladi zgradu, a solarni paneli na krovu proizvode struju i smanjuju emisije CO₂.
> Pitanje je samo: koji krovovi, gdje, i gdje krenuti prvo?

*Kadar:* sloj **Zeleni krovovi**, zum na Donji grad (tamnozeleni ravni krovovi), zatim prijelaz na **Fotonapon**.

### 0:40–0:55 · Ciljni korisnici

> Alat je namijenjen urbanistima i stručnim službama Grada koje planiraju mjere prilagodbe klimatskim
> promjenama, a jednako ga mogu koristiti upravitelji zgrada i građani koji razmišljaju o svom krovu.

*Kadar:* panel „Cijeli grad“, polagano pomicanje preko brojki.

### 0:55–1:20 · Izvori podataka

> Osnova je otvoreni 3D model zgrada Grada Zagreba s Portala otvorenih podataka, preuzet automatski
> preko njegova API-ja. Za svaku od gotovo 357 tisuća zgrada izračunati su nagib i orijentacija svake
> krovne plohe. Prinos sunčanih elektrana dolazi iz PVGIS-a Europske komisije, potrošnja struje javnih
> zgrada iz gradskog sustava ISGE, a zaštićene zgrade iz Registra kulturnih dobara.
> Oborine su prema DHMZ-u, a cijene i potrošnja kućanstava prema Eurostatu.

*Kadar:* grafika s logotipima ili nazivima izvora (poredak kao u govoru):
ZG3D (data.gov.hr, CKAN API) · PVGIS 5.3 (JRC) · ISGE (Grad Zagreb) · Registar kulturnih dobara
(Ministarstvo kulture i medija) · DHMZ · Eurostat · OpenStreetMap.

### 1:20–2:15 · Funkcionalnosti (demo)

Snima se stvarno korištenje javnog linka, redom:

1. **Uvod u panelu** (prvi posjet, `localStorage` očišćen) → klik **Istraži kartu**.
   > Pri prvom otvaranju kratki uvod objašnjava tri koraka.
2. **Scenarij 30 %** u sloju zelenih krovova.
   > Ako se iskoristi tek trećina pogodnih krovova, Zagreb bi dobio oko 400 hektara zelenila,
   > a krovovi bi godišnje zadržali oko 1,8 milijuna kubika kišnice, kao sedamsto olimpijskih bazena.
3. **Fotonapon**, isti scenarij.
   > Solarni paneli na istoj trećini krovova proizveli bi oko 1,15 teravatsati struje godišnje,
   > uz oko 150 tisuća tona manje CO₂.
4. **Rang-lista četvrti**: klik na *Peščenica – Žitnjak* (karta zumira, ostale četvrti se prigušuju).
   > Četvrti se mogu usporediti; u Peščenici je najviše površine za zelene krovove, u Sesvetama za sunčane elektrane.
5. **Pretraga adrese** „Ulica Savezne Republike Njemačke 2a“ → otvara se kartica **OŠ Središće**.
   > Svaka zgrada ima svoju karticu: površina za zelenilo, zadržana kišnica, snaga elektrane, trošak i povrat.
   > Ova škola troši oko 228 megavatsati struje godišnje, a elektrana na krovu mogla bi proizvesti više od toga.
6. **3D** (gumb na karti), kratko okretanje.

*Napomena:* kartica škole prikazuje „Objekt Grada Zagreba“ i rečenicu o pokrivanju potrošnje; pričekati
da se vidi prije sljedećeg koraka.

### 2:15–2:35 · Tehnička arhitektura

> Sve se računa unaprijed, u Pythonu, iz otvorenih podataka. Rezultat je jedna datoteka vektorskih
> pločica koju statička web-aplikacija čita izravno, bez poslužitelja i baze. Zato je alat jeftin za
> održavanje i radi na svakom računalu i mobitelu. Sav je kod otvoren, pod licencom MIT.

*Kadar:* jednostavan dijagram:
`data.gov.hr (ZG3D) + PVGIS + ISGE + Registar → Python (krovne plohe, potencijal) → PMTiles + JSON → MapLibre u pregledniku (GitHub Pages)`.

### 2:35–2:50 · Korisnička vrijednost

> Grad može krenuti od vlastitih zgrada. Prikaz samo objekata Grada pokazuje da bi solarni paneli
> na njihovim krovovima mogli pokriti oko tri četvrtine potrošnje struje tih zgrada, bez ijednog
> dogovora s privatnim vlasnicima.

*Kadar:* prekidač **Zgrade: samo objekti Grada**, sloj Fotonapon, scenarij **svi kandidati**
(ovdje se namjerno koristi puni potencijal jer je riječ o udjelu potrošnje), istaknuti **Pokrivenost potrošnje 75 %**.

### 2:50–3:00 · Daljnji razvoj i kraj

> Isti postupak može se primijeniti na svaki hrvatski grad s 3D modelom zgrada. Sljedeći koraci su
> provjera na ortofotu, toplinske karte za prioritete i povezivanje s gradskim ustanovama.
> Krov+. Krov za zelenije sutra.

*Kadar:* karta izdaleka; završni natpis **Krov+** · korejur.github.io/DataOasis.

## Provjera brojki prije snimanja

| U govoru | Vrijednost | Izvor |
|---|---|---|
| ~40 km² krovova | 40,47 km² (zbroj krovnih ploha) | `city.json` → `krovna_povrsina_m2` |
| gotovo 357 tisuća zgrada | 356 984 | `city.json` → `zgrade` |
| ~400 ha zelenila (30 %) | 401,8 ha | `zk_iskoristivo_m2` × 0,3 |
| ~1,8 mil. m³ kišnice (30 %) | 1 768 125 m³ ≈ 707 olimpijskih bazena (2 500 m³) | `zk_zadrzana_voda_m3_god` × 0,3 |
| ~1,15 TWh (30 %) | 1 145 GWh | `fn_proizvodnja_GWh_god` × 0,3 |
| ~150 tis. t CO₂ (30 %) | 153 446 t | `fn_co2_t_god` × 0,3 |
| Peščenica / Sesvete | najveća površina za zelenilo / najveća proizvodnja FN | `districts.json` |
| OŠ Središće, ~228 MWh, > 100 % | 228 MWh (ISGE 2023.), FN ≈ 105 % potrošnje | `isge_buildings.parquet` |
| objekti Grada ~75 % | 54,4 / 72,9 GWh (objekti ≥ 20 MWh/god) | `city.json` → `javno`, METODOLOGIJA 7.2 |

Sve brojke su **tehnički potencijal** (METODOLOGIJA 4.3); u govoru se ne tvrdi da je nešto „neiskorišteno“
ili „isplativo“ izvan toga što aplikacija prikazuje.

## Prije snimanja

* Javni link otvoren u novom prozoru preglednika, `localStorage` očišćen (da se vidi uvod).
* Zum preglednika 100 %, prozor 1920 × 1080; miš se pomiče polako.
* Snimka zaslona: OBS Studio (otvoreni kod) ili ugrađeni alat sustava; glas se snima zasebno i
  montira (npr. Shotcut ili Kdenlive, oba otvorenog koda).
* Trajanje provjeriti nakon montaže: najviše **3:00**.
