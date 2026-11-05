# Pregled postojećih katastara i istraživanja zelenih krovova

Pregledano 3. 11. 2026. Svrha: vidjeti što je već napravljeno i provjereno,
koje parametre koriste, i gdje naš projekt donosi nešto novo.

## 1. Sažetak u pet točaka

1. **Kataster zelenih krovova je ustaljen alat** (Beč 2011, Marburg 2016,
   NRW, Wuppertal, Münster...). Osnovni princip je svugdje isti:
   **nagib krovne plohe → klasa prikladnosti → površina → procjena koristi**.
   Naš pristup je u tom smislu standardan i usporediv.
2. **Pragovi nagiba su slični**, ali ne i jednaki. Najdetaljnije dokumentiran je
   NRW: 0–5 / 5–10 / 10–15 / 15–35 / >35°. Koristi računa samo do 15°.
3. **Koeficijenti koristi su objavljeni i citirani** (FLL 2018, Pfoser 2014,
   Herfort 2012). Možemo ih preuzeti umjesto vlastitih procjena:
   zadržavanje vode 50/60/70 % za 10/20/30 cm supstrata, CO₂ 0,8–1,0 kg/m²/god,
   masa 130/280/420 kg/m², hlađenje isparavanjem 688 kWh/m³ vode.
4. **Prioritizacija prema potrebi je istraživačka praksa**, ne praksa katastara.
   Njemački katastri prikazuju samo prikladnost. Liège, San Sebastián i
   Chicago dodaju toplinu, nedostatak zelenila i socijalnu ranjivost, svaki
   na svoj način. Nijedan to ne spaja s fotonaponom ni s potrošnjom javnih zgrada.
5. **Nitko ozbiljno ne validira rezultate.** Svi navode da statika nije
   provjerena. Liège izričito kaže da validacija tek predstoji. NYC je jedini
   kartirao *postojeće* zelene krovove. Validacija na uzorku bila bi nam
   jasna prednost.

## 2. Pregled po projektu

### Beč – Gründachpotenzialkataster (MA 22, 2011.)
* **Podaci:** zračni laserski sken (ALS). **Klase:** 0–5° (intenzivno i
  ekstenzivno), 5–20° (samo ekstenzivno).
* Na karti su i **zone zaštite** (UNESCO baština, Schutzzonen) i
  zaštićena priroda (Natura 2000...), kao sloj upozorenja, a ne kao isključenje.
* Izričito **ne uzima u obzir** statiku, stanje krova ni druge namjene (npr. solar).
* Brojke (2020.): 1079 ha pogodno za intenzivno, 716 ha samo za ekstenzivno.

### Gründachkataster NRW (LANUV, IP SYSCON; ažurirano 28. 3. 2026.)
Najbolje dokumentiran sustav. Pokriva 11,3 mil. zgrada i 50 mil. krovnih ploha.
* **Podaci:** DOM iz LiDAR-a (~4 toč/m², 2013.–2019.) i ALKIS tlocrti.
  Plohe dobiva segmentacijom metodom *region growing*, pri čemu izdvaja
  dimnjake, krovne prozore i antene. Pragovi i 5 klasa nagiba su u tablici u 3. poglavlju.
* **Zasjenjenje:** dvije analize globalnog zračenja, sa sjenama zgrada, terena
  i vegetacije i bez njih. Dio plohe sa sjenom > 40 % (ćelije ≥ 2,25 m²)
  spušta se jednu klasu (sunčano → polusjena → sjena = neprikladno).
* **Izloženost** (za popis biljaka): 0–15° je sunčano. Za 15–35° je
  sunčano kad je azimut 90–270°, a polusjena kad je okrenuto prema sjeveru.
* **Toplinski prioritet:** "Handlungsprioritäten" 1–6 s karte
  Klimaanaliza NRW (1–2 = hitno, 3–4 = prošireno, 5 = umjereno, 6 = nema potrebe).
* **Kalkulator po plohi:** korisnik bira supstrat 10 / 20 / 30 cm i dobiva
  masu, zadržavanje pri jakom pljusku, godišnje zadržavanje, hlađenje
  isparavanjem, uštedu na naknadi za oborinske vode, CO₂, fine čestice i
  troškove po razredima veličine (BuGG, od 10–100 m² do > 5000 m²).
* **FN:** pita "planirate li i FN na nosačima?". Ako da, mijenja izloženost
  u polusjenu i daje poveznicu na zasebni solarni katastar. FN i zeleni krov
  **nisu zajedno izračunati**.
* Napomena: šljunčani krov težinom ≈ ekstenzivni zeleni krov od 10 cm, pa se
  takvi krovovi mogu prenamijeniti bez većih statičkih zahvata.

### Wuppertal – Gründachpotenzialkataster 2022 (tetraeder.solar, CC BY 4.0)
* Izveden iz **solarnog katastra** (isti LiDAR model krovova, prosinac 2020.).
* **Otvoreni podaci po zgradi** (CSV/XLSX, 81 045 zapisa): adresa, klasa
  (gut / geeignet / bedingt), površine po klasi, fine čestice, CO₂, zadržana
  voda, oborine (DWD). Minimalna površina 10 m².
* **Iz CSV-a smo izračunali koeficijente:** zadržavanje 50 % (gut/geeignet) i
  40 % (bedingt), CO₂ 0,75 kg/m²/god, fine čestice 9,8 g/m²/god.
* Rezultat: od 154 175 objekata 32,6 % gut, 10,1 % geeignet, 9,8 % bedingt;
  8,74 km² krovova; 4,38 mil. m³ vode/god; 6556 t CO₂; 86 t čestica.

### Marburg – Gründachkataster (prof. M. Klärle, 2016.)
* Prvi "pametni" njemački kataster. Podaci: laserski sken, ortofoto, katastar.
  Dijeli podatke sa solarnim katastrom.
* Po krovu daje nagib, orijentaciju, zasjenjenje, tip krova, **preporuku biljaka**,
  zadržavanje vode, uštede na naknadama, isplativost FN-a, CO₂ i fine čestice.
* Metode za CO₂ i čestice nisu objavljene. Validacije nema.
  Nije zamjena za statičku analizu.

### Liège (Joshi i sur., ISPRS Annals 2020)
* **Podaci:** LiDAR 0,8 toč/m², RANSAC detekcija ravnina (najviše 20 ravnina po
  zgradi, tolerancija 10 cm). **Kriterij:** ravnina 0–10° i ≥ 10 m².
* **Statika (procjena):** zgrade ≥ 20 m smatraju betonskima i pogodnima.
  Niže zgrade su pogodne ako su građene prije 1977. (prije Eurokoda, kad se
  dimenzioniralo konzervativnije). Autori sami traže validaciju.
* **Prioritet:** NDVI (Sentinel-2, 10 m), LST (Landsat 8, B11) i indeks
  socioekonomske deprivacije. Vrijednosti su normirane 0–1, pomnožene uz
  jednake težine, a razredi se određuju po kvartilima (< 25 / 25–75 / ≥ 75 %).
  **NDVI i LST su jako negativno korelirani**, pa su koristili samo NDVI zbog bolje rezolucije.
* Rezultat: 20 % zgrada (351 ha). Najprioritetnije zone su i najsiromašnije,
  pa preporučuju ciljati velike krovove (tvrtke) i poticaje.

### San Sebastián (Gandini, Navarro, Feliu – Tecnalia, projekt CURE)
* **Podaci:** LiDAR 2,2 toč/m² → DSM 1 m, tlocrti, godina gradnje iz
  katastra, Copernicus (Urban Atlas, HRL Imperviousness, HR-VPP, LST iz ERA5/UERRA).
* **Prikladnost:** nagib ≤ 10 % (≈ 5,7°). Zgrade prije 1900. su isključene (baština).
* **Prioritet zgrade** = godina gradnje (prije 1900. isključeno, 1901.–1961.
  nisko jer treba statička analiza, nakon 1962. visoko zbog uvođenja propisa)
  × maksimalni potencijal × **prioritet područja** (normirani NDVI, nepropusnost, LST).
  **Težine bira korisnik** u aplikaciji. Indeks je u rasponu 0–1.
* Rezultat: 118 ha, 3554 krova (oko 20 % krovova); 1204 visoko, 1091 srednje
  i 959 nisko prioritetnih.
* **Kao sljedeći korak navode spajanje sa solarnim panelima.** To je točno ono što mi radimo.

### Chicago (Sharma i sur., Environ. Res. Lett. 13, 094011, 2018.)
* WRF model 1 km, 15.–18. 8. 2013., scenariji 25–100 % zelenih krovova.
* Kod 100 % pokrivenosti: krov **−5,1 °C**, tlo −4,1 °C, **zrak (2 m) −1,7 °C**
  (prosjek 14–17 h). Svakih 25 % pokrivenosti ≈ −1,25 °C na krovu.
* Prioritet = indeks toplinske ranjivosti (28 varijabli, PCA) + smanjenje
  temperature + potrošnja klime. Prag je 50. percentil, a "visok" prioritet
  znači da su ispunjena sva tri uvjeta.
* **Važno:** hlađenje najviše ovisi o tome koliko je krov bio vruć, a gotovo
  nimalo o ranjivosti stanovnika. Socijalni kriterij zato treba uvesti **izričito**.

### New York (The Nature Conservancy, 2019.)
* Kartirali su **postojeće** zelene krovove (ortofoto 2016. i evidencije):
  736 krovova, 60 acres, **0,15 % krovne površine**, nejednako raspoređeno.
  Najmanje ih ima u toplinski najranjivijim četvrtima.
* Preporuke: procijeniti **realni** potencijal uz prikladnost i
  pristupačnost, razmatrati i solarne, plave (retencijske) i bijele krovove,
  koristiti stupnjevane poticaje, paziti na pravednost i pratiti namjenu krovova kroz vrijeme.

## 3. Usporedba kriterija i koeficijenata

| Parametar | NRW | Wuppertal | Beč | Liège | San Sebastián | **Mi (sada)** |
|---|---|---|---|---|---|---|
| Ulaz | LiDAR DOM | LiDAR | ALS | LiDAR | LiDAR | **LoD2.2 3D model** |
| Nagib "najbolje" | 0–5° | – | 0–5° (int.) | 0–10° | ≤ 5,7° | 0–10° |
| Gornja granica za izračun | 15° | ~35° (bedingt) | 20° | 10° | 5,7° | 20° |
| Min. površina | ploha (sjena ≥ 2,25 m²) | 10 m² | – | 10 m² ravnine | – | 50 m² po zgradi |
| Godišnje zadržavanje | 50/60/70 % (10/20/30 cm) | 50 % / 40 % | – | – | – | 50 % |
| CO₂ | 0,8/0,9/1,0 kg/m²/god | 0,75 | – | – | – | – |
| Fine čestice | 1,4 g/m²/god | 9,8 g/m²/god | – | – | – | – |
| Masa (zasićeno) | 130/280/420 kg/m² | – | – | – | – | – |
| Hlađenje isparavanjem | 688 kWh/m³ | – | – | – | – | – |
| Zasjenjenje | da (DOM + vegetacija) | da | – | – | – | **ne** |
| Statika | ne (napomena) | ne | ne | visina + godina | godina gradnje | ne |
| Baština | – | – | sloj upozorenja | – | prije 1900. isključeno | planirano |
| Prioritet prema potrebi | karta klimatske analize | – | – | NDVI × deprivacija | NDVI+nepropusnost+LST, težine | planirano |
| FN | poveznica na drugi alat | izveden iz solarnog katastra | – | – | "sljedeći korak" | **integrirano** |

*Napomena:* koeficijent za fine čestice razlikuje se ~7 puta između NRW-a
(1,4 g) i Wuppertala (9,8 g). Izvor NRW-a je objavljen
(Gorbachevskaya & Herfort 2012), pa njega treba koristiti i navesti raspon.

## 4. Usporedba s Zagrebom (naši podaci, nagib po NRW klasama)

| Klasa nagiba | Zagreb [ha] |
|---|---|
| 0–5° | 1170 |
| 5–10° | 428 |
| 10–15° | 298 |
| 15–20° | 257 |
| 20–35° | 1328 |
| > 35° | 567 |

* Zgrade s ≥ 10 m² nagiba ≤ 15°: **188 413**, ukupno 1867 ha. Uz prag ≥ 50 m²:
  67 481 zgrada i 1563 ha.
* Beč (2020.): 1795 ha do 20°. Zagreb do 20° (≥ 10 m²): 2122 ha.
  Wuppertal: 8,74 km², odnosno ~25 m²/stanovniku, a Zagreb ~24 m²/st. (≤ 15°, ≥ 10 m²).
  **Redovi veličine se slažu**, pa rezultat nije sumnjiv.
* Zagreb ima mnogo malih ravnih krovova (garaže, pomoćni objekti). Zato je
  važno prikazivati razrede veličine i ne brojati samo zgrade.

## 5. Što to znači za naš projekt

### Što preuzeti (provjereno, citirano)
1. **NRW klase nagiba** (0–5 / 5–10 / 10–15 / 15–35 / > 35°) i izračun koristi
   do 15°. Plohe od 0–5° označiti kao pogodne i za intenzivni krov (kao Beč).
2. **Odabir supstrata 10 / 20 / 30 cm** s NRW koeficijentima: masa,
   zadržavanje (godišnje i pri pljusku), CO₂, fine čestice.
3. **Hlađenje isparavanjem:** zadržana voda × ~686 kWh/m³ (latentna toplina
   pri ~12 °C, srednjoj temperaturi Zagreba). Jednostavno i fizikalno utemeljeno.
4. **Izloženost** (sunčano / polusjena) iz nagiba i azimuta, kao u NRW-u, za
   preporuku vrste ozelenjavanja.
5. **Razredi veličine i troškova** (10–100, 100–1000, 1000–5000, > 5000 m²).
   Cijena po m² pada s veličinom krova.
6. **Prioritet područja** kao u San Sebastiánu i Liègeu: normirani NDVI
   (nizak), nepropusnost (visoka) i LST (visok) iz Copernicusa i Landsata,
   uz težine koje bira korisnik i razrede po kvartilima.
7. **Socijalni kriterij izričito**, zbog nalaza iz Chicaga. Za Zagreb su moguće
   zamjene: udio starijih po četvrti, vrtići, škole i domovi za starije u
   blizini (Geoportal).
8. **Baština kao sloj upozorenja**, ne isključenje (kao Beč).

### Gdje donosimo novo
* **LoD2.2 3D model umjesto LiDAR segmentacije.** Plohe su već modelirane i
  čiste, pa je pristup brz (cijeli grad u nekoliko minuta) i ponovljiv za
  svaki grad koji ima CityGML/LoD2. U literaturi to rade samo
  istraživački radovi (Biljecki), a ne katastri.
* **Zeleno + solar + biosolarno u jednom izračunu po krovu.** NRW samo daje
  poveznicu, a Tecnalia to navodi kao budući rad.
* **Javne zgrade i njihova stvarna potrošnja (ISGE).** Nismo ga našli ni u
  jednom katastru, a Grad o tim zgradama odlučuje sam.
* **Scenariji za grad** ("ako ozelenimo X % prioritetnih krovova..."),
  odnosno "realni potencijal" koji NYC preporučuje kao sljedeći korak.
* **Validacija na uzorku**, koju nitko od navedenih ne radi sustavno:
  ručna provjera ~200 nasumičnih kandidata na ortofotu DGU-a.
* **Rezultati kao otvoreni podaci** (kao Wuppertal, CSV/GeoJSON po zgradi).
  Time vraćamo vrijednost na Portal otvorenih podataka, što je duh natjecanja.
* Prvi takav alat za neki hrvatski grad (nismo našli postojeći).

### Otvorena pitanja za tim
* Zasjenjenje: računati sjenu samo od zgrada iz 3D modela (izvedivo) ili
  pokušati i s drvećem (nema LiDAR-a vegetacije u otvorenim podacima Zagreba)?
* Statika: Zagreb nema otvorenu godinu gradnje po zgradi. Moguće zamjene:
  registar energetskih certifikata (ima godinu gradnje i adresu?), te podaci
  o obnovi nakon potresa 2020. (obnova kao prilika za zeleni krov, kao Liège).
* Hoćemo li detektirati postojeće zelene krovove (NYC) iz ortofota? To je
  zahtjevnije, ali bi dalo polaznu točku ("danas ima X, potencijal je Y").

## 6. Izvori

* Stadt Wien, MA 22 (2011): *Gründachpotenzialkataster* (karta). https://www.wien.gv.at/pdf/ma22/gruendachpotenzial.pdf
* IG Lebenszyklus Bau (2023): *Dachflächennutzung* (brojke za Beč 2020.). https://ig-lebenszyklus.at/wp-content/uploads/2023/11/Dachflaechennutzung_WEB.pdf
* LANUV NRW (2026): *Methodik – Planung und Bau: Gründachkataster NRW*. https://www.klimaatlas.nrw.de/sites/default/files/2022-11/Methodik_Planung_Bau_GruendachkatasterNRW_0.pdf
* Stadt Wuppertal / tetraeder.solar (2022): *Gründachpotenzialkataster Wuppertal 2022* (CC BY 4.0). https://ckan.open.nrw/dataset/grundachpotenzialkataster-wuppertal-2022-w
* idw (2016): *Marburg erhält Gründachkataster*. https://idw-online.de/en/news666646
* Joshi, M. Y. i sur. (2020): *Potential for urban greening with green roofs: a way towards smart cities*. ISPRS Annals VI-4/W2-2020, 87–94. https://doi.org/10.5194/isprs-annals-VI-4-W2-2020-87-2020
* Gandini, A., Navarro, D., Feliu, E.: *Identification and mapping of areas and buildings with high roof greening potential* (Tecnalia, CURE GA 870337). https://zenodo.org/records/8033216
* Sharma, A. i sur. (2018): *Role of green roofs in reducing heat stress in vulnerable urban communities*. Environ. Res. Lett. 13, 094011. https://doi.org/10.1088/1748-9326/aad93c ; popularni prikaz: https://physicsworld.com/?p=75046
* The Nature Conservancy (2019): *Look Up to Make Room for a Greener NYC*. https://www.nature.org/content/dam/tnc/nature/en/documents/NYC_GreenRoofs_Summary.pdf
* Citirano u NRW metodologiji: FLL (2018) *Dachbegrünungsrichtlinien*; Pfoser i sur. (2014) *Gebäude Begrünung Energie*; Herfort i sur. (2012) CO₂-Bindungsvermögen; Gorbachevskaya & Herfort (2012) Feinstaubbindungsvermögen.
