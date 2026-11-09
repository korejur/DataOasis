# STATUS – Krov+

> **Živi dokument.** Svaki član tima i svaki agent ga **čita na početku rada** i **ažurira na kraju**
> (u istom commitu kao i sam rad). Pravila ažuriranja su na dnu.
> Plan i podjela uloga: [`docs/PLAN_RADA.md`](docs/PLAN_RADA.md) · kriteriji i bodovi: [`docs/NATJECANJE.md`](docs/NATJECANJE.md) · upute za agente: [`AGENTS.md`](AGENTS.md)

**Zadnje ažuriranje:** 2026-11-08 · uloga: aplikacija · projektna i tehnička dokumentacija za PDF, sa snimkama zaslona i dijagramima
**Predaja:** pon 9. 11. 2026. do 24:00 · **Zamrzavanje funkcionalnosti:** ned 8. 11. u 18:00
**Najviše bodova (30/60):** izvedivost (radni prototip na javnom linku), dojam UI/UX, video

## Gotovo

| Datum | Uloga | Što | Gdje |
|---|---|---|---|
| 2026-11-03 | – | Pipeline: preuzimanje ZG3D, krovne plohe, PVGIS, potencijal po zgradi (356 984 zgrade) | `pipeline/`, `data/processed/` |
| 2026-11-03 | – | Pregled literature i metodologija | `docs/` |
| 2026-11-05 | aplikacija | **Korak 1:** izvoz za kartu – `buildings.pmtiles` (z13–16), `districts.json`, `city.json` | `pipeline/export_app.py`, `app/public/data/` |
| 2026-11-05 | – | Plan rada s rasporedom, STATUS, upute za agente | `docs/PLAN_RADA.md`, `STATUS.md`, `AGENTS.md` |
| 2026-11-05 | – | Sažetak pravila i kriterija ocjenjivanja s planom za bodove | `docs/NATJECANJE.md` |
| 2026-11-05 | – | `handoff.md` obrisan; otvorena pitanja prenesena u STATUS, napomene o podacima u `METODOLOGIJA.md` | – |
| 2026-11-07 | aplikacija | **Karta:** Vite + MapLibre + PMTiles; prekidač zeleni krov / FN, kartica zgrade, legenda, uvodni ekran s izvorima, 3D prikaz, prikaz na mobitelu | `app/` |
| 2026-11-07 | aplikacija | **Panel s četvrtima:** brojke za grad i četvrt, scenarij 10 / 30 / 100 % kandidata, rang-lista (3 kriterija po sloju), pregled ispod z13 krugovima | `app/src/panel.js` |
| 2026-11-07 | aplikacija | Pretraga četvrti (bez dijakritika) i adresa (Nominatim) s otvaranjem kartice pogođene zgrade | `app/src/search.js` |
| 2026-11-07 | aplikacija | **Objava na GitHub Pages:** workflow pri pushu na `main`, `buildings.pmtiles` iz Releasea `podaci`; repo javan; `LICENSE` (MIT); uklonjen tuđi PDF (LANUV NRW) | `.github/workflows/pages.yml`, `LICENSE` |
| 2026-11-07 | aplikacija | Javni link provjeren u pregledniku: zgrade se iscrtavaju (z14 središte: ~2,4 MB pločica), kartica zgrade radi; HTTP Range na Pages radi | – |
| 2026-11-08 | aplikacija | Legenda na širinama 761–1040 px uz otvorenu karticu ide ispod kartice (prije pod lijevi panel); provjereno na 400 / 800 / 1000 / 1280 px | `app/src/style.css`, `app/src/main.js` |
| 2026-11-08 | aplikacija | **Geokodiranje** (Nominatim, predmemorija u gitu): kulturna dobra 368/470 spojeno (393 zgrade), ISGE 854 zgrade od 1 082 objekta | `pipeline/geocode.py`, `data/reference/geocode/` |
| 2026-11-08 | aplikacija | **Spajanje tablica u izvoz** (baština, ISGE, ustanove kad stignu); kartica: kulturno dobro, objekt Grada s potrošnjom i udjelom FN; obrub na karti + legenda | `pipeline/export_app.py`, `app/src/card.js` |
| 2026-11-08 | metodologija | **Parametri s izvorima:** uklonjeni svi `TODO izvor` (DHMZ, FLL/LANUV NRW, Mentens i sur. 2006, EEA, Eurostat); cijena struje 0,15 → 0,18 €/kWh, potrošnja kućanstva 3 500 → 4 630 kWh; tablica izvora | `pipeline/config.py`, `docs/METODOLOGIJA.md` (pogl. 8) |
| 2026-11-08 | metodologija | Ponovni izračun i izvoz: ekvivalent kućanstava za grad 1,09 mil. → 824 tis., povrat FN ~7,7 → ~6,4 god.; kartica zgrade čita potrošnju kućanstva iz `city.json` | `app/public/data/`, Release `podaci` |
| 2026-11-08 | metodologija | Opis geokodiranja i povezivanja s ISGE u metodologiji (zahtjev aplikacije) | `docs/METODOLOGIJA.md` 7.1 |
| 2026-11-08 | aplikacija | **Redizajn „Atlas“:** Source Serif 4 + Source Sans 3 (Fontsource, bez Google Fonts), panel uz lijevi rub, tanke crte bez sjena i zaobljenja; uvod pri prvom posjetu kao naslovnica u panelu (zatvara se gumbom ili klikom na zgradu), „O projektu“ samo na klik; tekst u pasivu. Provjereno na 1440 / 900 / 390 px | `app/src/style.css`, `app/src/onboarding.js`, `app/index.html` |
| 2026-11-08 | aplikacija | **Prikaz „samo objekti Grada“** (ISGE, 853 zgrade): brojke, rang-lista četvrti i karta samo za objekte Grada; pokrivenost vlastite potrošnje struje FN-om ≈ 75 % (objekti ≥ 20 MWh/god); `export_app.py --samo-json` za brzi izvoz sažetaka | `app/src/panel.js`, `app/src/main.js`, `pipeline/export_app.py`, `docs/METODOLOGIJA.md` 7.2 |
| 2026-11-08 | aplikacija | „O projektu i izvorima podataka“ uvijek vidljivo na dnu panela | `app/index.html`, `app/src/style.css` |
| 2026-11-08 | aplikacija | Novi naziv **Krov+** i tekst (podnaslov, uvod, „O projektu“, naslov stranice); poveznica na repozitorij u „O projektu“ | `app/index.html`, `app/src/onboarding.js`, README, LICENSE |
| 2026-11-08 | aplikacija | **Tehnička i projektna dokumentacija** (službeni dokumenti za PDF, 15 snimki zaslona, 3 dijagrama): arhitektura, obrada podataka s formulama, model podataka, aplikacija korak po korak, standardi, integracija, preduvjeti, popis svih skupova s izdavateljem, poveznicom i licencom (provjereno preko CKAN API-ja) | `docs/PROJEKTNA_DOKUMENTACIJA.md`, `docs/TEHNICKA_DOKUMENTACIJA.md`, `docs/slike/`, README |
| 2026-11-08 | aplikacija | Kartica zgrade: za razred „visoka“ kod pretežno kosog krova tekst više ne piše „Pretežno ravan krov“, nego da su pogodni ravni dijelovi; legenda „ravni dijelovi krova (0–10°)“ | `app/src/card.js`, `app/src/layers.js` |
| 2026-11-09 | aplikacija | Tehnička dokumentacija: slika 2 smanjena da stane ispod naslova 3.3 (u PDF-u naslov više ne ostaje sam na stranici); ispravljen redak „zid“ u tablici klasifikacije ploha | `docs/TEHNICKA_DOKUMENTACIJA.md` |

## U tijeku

| Uloga | Zadatak | Grana | Stanje / napomena |
|---|---|---|---|
| podaci | Granice četvrti i MO → javne ustanove | | zadatak poslan |

## Sljedeće (redom)

1. **aplikacija:** pretvoriti dokumentaciju u PDF za e-poštu → pospremanje repoa i README (stavka 10a)
2. **podaci:** granice → `building_institutions.parquet` → LST/NDVI (`building_env.parquet`)
3. **metodologija:** validacija (~200 zgrada, popis dobiva od aplikacije) → scenarij videa → UX test s osobom izvan tima

**Za preuzimanje aplikacije:** `cd app && npm install && npm run dev` (treba `app/public/data/buildings.pmtiles`, vidi README).
Ako Vite javi „Cannot find native binding“ (npm greška s opcionalnim ovisnostima): `npm i --no-save @rolldown/binding-win32-x64-msvc@<verzija rolldowna>`.
Objava ide sama pri spajanju u `main` (workflow „Objava aplikacije“). Nakon novog izvoza zamijeniti prilog Releasea `podaci`
(README → „Objava aplikacije“). Pages uz `Accept-Encoding: gzip` vraća Range iz sažete datoteke; preglednici to ne šalju,
ali alati poput `curl --compressed` ili Node `fetch` trebaju `Accept-Encoding: identity`.

## Blokirano / čeka

| Tko čeka | Na što | Od koga |
|---|---|---|
| aplikacija (sloj četvrti) | `data/reference/granice/*.geojson` | podaci |

## Predane tablice (sučelje prema izvozu)

Sve tablice vezane uz zgradu: `data/processed/<naziv>.parquet` sa stupcem `bldg_id`.
Kad tablica postoji, upiši je ovdje – aplikacija je tada spaja u `export_app.py`.

| Datoteka | Stupci | Uloga | Stanje |
|---|---|---|---|
| `buildings_metrics.parquet` | sve metrike (vidi `pipeline/metrics.py`) | – | gotovo |
| `building_institutions.parquet` | `bldg_id`, `institution_type`, `institution_name` | podaci | – |
| `building_env.parquet` | `bldg_id`, `lst`, `ndvi`, `pop` | podaci | – |
| `heritage_buildings.parquet` | `bldg_id`, `heritage_id`, `naziv`, `status`, `adresa`, `nacin` | aplikacija | gotovo (393 zgrade) |
| `isge_buildings.parquet` | `bldg_id`, `objekt`, `adresa`, `kwh_god`, `eur_god`, `fn_udio`, `nacin` | aplikacija | gotovo (854 zgrade) |

## Odluke

| Datum | Odluka | Zašto |
|---|---|---|
| 2026-11-05 | Izazov **B – Okoliš i održivi prostor** | tema zelenih krovova i klime |
| 2026-11-05 | 2D web karta (MapLibre) + panel s četvrtima; 3D samo ako ostane vremena | brže, pouzdan demo |
| 2026-11-05 | Statička aplikacija bez backenda, sve se računa unaprijed u Pythonu | besplatan hosting, nema servera koji može pasti |
| 2026-11-05 | Zgrade na karti od zuma 13; ispod toga četvrti | na z12 GDAL odbacuje ~45 % zgrada zbog veličine pločica |
| 2026-11-05 | `buildings.pmtiles` nije u gitu (80 MB), regenerira se s `pipeline.export_app` | veličina |
| 2026-11-05 | Dorada UI/UX i video su zasebni zadaci s vlastitim vremenom | zajedno s izvedivošću nose 30/60 bodova |
| 2026-11-07 | Podloga karte: OpenFreeMap (stil Positron, OSM); OSM zgrade i oznake cesta skrivene | besplatno, bez API ključa, otvoreni podaci |
| 2026-11-07 | Pretraga adresa preko Nominatima, samo na Enter (najviše 1 upit/s) | pravila korištenja Nominatima; nema vlastitog geokodera |
| 2026-11-07 | Ispod z13 četvrti su krugovi u središtu (veličina = potencijal) dok ne stignu granice | granice još nisu predane |
| 2026-11-07 | Scenarij u panelu linearno skalira brojke (10 / 30 / 100 % kandidata) | jednostavno i lako objasniti |
| 2026-11-07 | **Hosting: GitHub Pages**; `buildings.pmtiles` je prilog GitHub Releasea `podaci` (ne u gitu) | besplatno, isti repo, HTTP Range; nakon novog izvoza `gh release upload podaci … --clobber` |
| 2026-11-07 | **Repo javan** od 7. 11. | Pages na besplatnom računu traži javni repo; ionako uvjet predaje |
| 2026-11-07 | **Licenca:** MIT za kod, CC BY 4.0 za izvedene podatke | prijedlog iz otvorenih pitanja, boduje se |
| 2026-11-07 | Tuđi PDF (LANUV NRW) uklonjen iz repoa, poveznica u `PREGLED_LITERATURE.md` | autorska prava u javnom repou |
| 2026-11-08 | Geokodiranje preko Nominatima uz predmemoriju u gitu; prihvaća se samo pogodak s kućnim brojem | nema otvorenog adresnog registra s koordinatama pri ruci; bolje bez oznake nego s krivom |
| 2026-11-08 | ISGE: potrošnja **struje u 2023.** (2024. ima samo 6 mjeseci); udio FN samo za objekte s ≥ 20 MWh/god | manji potrošači koriste dio zgrade, omjer prema cijelom krovu bio bi višestruko prevelik |
| 2026-11-08 | „Struja za kućanstva“ za cijeli grad ostaje kao tehnički potencijal uz napomenu (`METODOLOGIJA.md` 4.3); u videu navoditi scenarij 10 % ili 30 % | brojka je usporediva s drugim pokazateljima; scenariji daju realan red veličine |
| 2026-11-08 | Iskoristivi udio krova 0,75 ostaje kao vlastita pretpostavka | izvor nije pronađen; jasno označeno u metodologiji |
| 2026-11-08 | Predložene izmjene metodologije (NRW klase, supstrat, hlađenje isparavanjem) ne primjenjuju se prije predaje | zamrzavanje funkcionalnosti; navode se kao daljnji razvoj |
| 2026-11-08 | Izgled „Atlas“ (odabran od tri prijedloga: Atlas, Gradski servis, Teren) | manje generičko sučelje, karta i brojke čitljive i na videu |
| 2026-11-08 | Uvod nije prozor preko karte, nego naslovnica u lijevom panelu | prozor je djelovao kao otvorene postavke; karta je odmah upotrebljiva |
| 2026-11-08 | Tekstovi u aplikaciji i materijalima bez 1. lica množine, u pasivu („izračunato je“, „procjenjuje se“) | odluka tima o tonu |
| 2026-11-08 | Naziv projekta **Krov+** (umjesto „Krovovi za klimu“); naslov bez imena grada, Zagreb u podnaslovu | projekt se predstavlja kao primjenjiv na cijelu Hrvatsku; repozitorij i javni link ostaju `DataOasis` |

## Otvorena pitanja (treba odluku tima)

* Koeficijent za fine čestice: NRW 1,4 g/m² ili Wuppertal 9,8 g/m² – navesti raspon?
* **Predložene izmjene metodologije** (iz pregleda literature, ne primjenjuju se prije predaje – vidi Odluke): NRW klase nagiba
  0–5 / 5–10 / 10–15 / 15–35 / > 35° s izračunom do 15° (sada do 20°); supstrat 10 / 20 / 30 cm
  (masa 130/280/420 kg/m², zadržavanje 50/60/70 %, CO₂ 0,8/0,9/1,0 kg/m²); hlađenje isparavanjem
  (~686 kWh/m³); razredi veličine i troška; minimalna površina plohe 10 m² (sada 50 m² po zgradi).
  Odlučuje metodologija; primjena znači izmjenu `metrics.py` i ponovni izvoz.

## Kontrolni popis za predaju (prema Pravilima, pogl. VIII)

| # | Stavka | Uloga | Stanje |
|---|---|---|---|
| 1 | Javni GitHub repozitorij s izvornim kodom | aplikacija | ✔ javan od 7. 11. (github.com/korejur/DataOasis) |
| 2 | Licenca otvorenog koda (`LICENSE`) | svi – odluka | ✔ MIT (kod), CC BY 4.0 (podaci) |
| 3 | Tehnička dokumentacija: dijagram, standardi, integracija s javnim sustavima, tehnički/organizacijski/pravni preduvjeti | aplikacija | ✔ `docs/TEHNICKA_DOKUMENTACIJA.md` |
| 4 | Projektna dokumentacija: problem, ciljni korisnici, vrijednost, daljnji razvoj | aplikacija | ✔ `docs/PROJEKTNA_DOKUMENTACIJA.md` |
| 5 | **Popis svih skupova podataka** s izdavateljem, poveznicom i licencom | metodologija + podaci | ✔ `docs/TEHNICKA_DOKUMENTACIJA.md` pogl. 8 |
| 6 | **Popis korištenih alata i biblioteka, uključujući AI alate** | svi | djelomično (README → „Korišteni alati“ i tehnička dokumentacija pogl. 9; svaka uloga dopisuje svoje AI alate) |
| 7 | Demo: javni link na radni prototip | aplikacija | ✔ https://korejur.github.io/DataOasis/ |
| 8 | Demo: snimke zaslona | aplikacija | ✔ `docs/slike/` (15 snimki, i u projektnoj dokumentaciji) |
| 9 | **Video ≤ 3 min:** problem, korisnici, izvori podataka, funkcionalnosti, arhitektura, vrijednost, daljnji razvoj | metodologija | ☐ |
| 10 | Video i veliki dodaci preko poveznice dostupne barem do objave rezultata (17. 11.) | metodologija | ☐ |
| 10a | **Pospremanje repoa prije objave**: README prepisati kao predstavljanje projekta (problem, link na demo, snimka zaslona, arhitektura, podaci); `STATUS.md` i `PLAN_RADA.md` po želji u `docs/tim/`; provjeriti da nigdje nema imena, osobnih putanja ni tajni; obrisati privremene datoteke | aplikacija | ☐ |
| 11 | E-pošta na open.data@mpudt.hr do 9. 11. u 24:00 (šalje voditelj tima, mentor u kopiji) – cilj poslati do 20:00 | voditelj | ☐ |

## Pravila ažuriranja (za ljude i agente)

1. **Na početku rada:** pročitaj cijeli STATUS. Ako uzimaš zadatak, upiši ga u „U tijeku“ (uloga, grana) i pushaj, da se ne radi dvaput.
2. **Na kraju rada (isti commit/PR):** premjesti stavku u „Gotovo“ (datum, uloga, putanja), ažuriraj „Sljedeće“, „Blokirano“ i tablicu predanih datoteka, promijeni redak „Zadnje ažuriranje“.
3. **Odluke** koje utječu na druge upiši u „Odluke“ s razlogom; neodlučeno ide u „Otvorena pitanja“.
4. Piši **kratko**, jedan redak po stavci, putanje u `backtickovima`. Ne briši tuđe retke, osim da ih premjestiš u „Gotovo“.
5. Kod konflikta u ovoj datoteci pri spajanju **zadrži retke obje strane**.
6. U ovu datoteku ne upisuj imena, samo uloge.
