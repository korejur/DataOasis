# Krov+ – projektna dokumentacija

*Krov za zelenije sutra.* Datathon Portala otvorenih podataka 2026., izazov **B – Okoliš i održivi prostor**.

* Aplikacija: https://korejur.github.io/DataOasis/
* Izvorni kod: https://github.com/korejur/DataOasis (MIT)
* Tehnička arhitektura: [`ARHITEKTURA.md`](ARHITEKTURA.md) · skupovi podataka: [`PODACI.md`](PODACI.md) ·
  metodologija: [`METODOLOGIJA.md`](METODOLOGIJA.md)

## 1. Problem

Gradovi se zagrijavaju, a ljetni toplinski valovi i jaki pljuskovi sve su češći. U gusto izgrađenim
dijelovima Zagreba asfalt i krovovi upijaju toplinu, a kišnica s nepropusnih površina odmah ide u
mješovitu kanalizaciju, koja se pri jakom pljusku preljeva. Istodobno Hrvatska treba više obnovljive
energije.

**Krovovi su najveća neiskorištena površina u gradu.** Zeleni krov zadržava kišnicu, isparavanjem hladi
zgradu i okolicu te stvara prostor za bioraznolikost. Sunčana elektrana na krovu proizvodi struju tamo
gdje se troši. Ali grad ne zna:

* koji su od ~357 000 krovova pogodni (nagib, površina, orijentacija);
* koliko bi to ukupno donijelo (m³ vode, MWh, t CO₂) i koliko bi koštalo;
* gdje krenuti prvo, posebno na zgradama koje su u vlasništvu ili korištenju Grada.

Ti podaci već postoje u otvorenom 3D modelu zgrada (ZG3D), ali kao 1,2 GB geometrije koju urbanist
ne može izravno koristiti.

## 2. Rješenje

Krov+ iz otvorenog 3D modela zgrada Grada Zagreba (ZG3D, LoD 2.2) izračunava nagib, orijentaciju i
površinu **svake krovne plohe** i iz toga za svaku zgradu procjenjuje:

* **zeleni krov:** razred pogodnosti, površinu za zelenilo, zadržanu kišnicu i okvirnu investiciju;
* **fotonapon:** snagu elektrane, godišnju proizvodnju prema PVGIS-u (JRC), izbjegnute emisije CO₂,
  ekvivalent kućanstava, investiciju i povrat ulaganja.

Rezultat se povezuje s drugim otvorenim podacima: **potrošnjom struje objekata Grada (ISGE)** i
**Registrom kulturnih dobara**. Tako kartica zgrade može reći, primjerice: „objekt Grada, troši 1,78 GWh
godišnje, sunčana elektrana na krovu mogla bi pokriti 39 %; zaštićeno kulturno dobro, zahvat traži
suglasnost konzervatora“.

### Funkcionalnosti aplikacije

* **Karta krovova** za cijeli grad, obojena po pogodnosti za zeleni krov ili po prinosu FN (prekidač).
* **Kartica zgrade** na klik: krov, zeleni krov, FN, oznake kulturnog dobra i objekta Grada.
* **Panel s brojkama** za grad i svaku gradsku četvrt, s **rang-listom četvrti** po tri kriterija za svaki sloj.
* **Scenariji:** učinak ako se iskoristi 10 %, 30 % ili svi pogodni krovovi.
* **„Samo objekti Grada“:** brojke i karta za 853 zgrade iz ISGE-a, uz udio vlastite potrošnje koji FN može pokriti.
* **Pretraga** gradske četvrti ili adrese, 3D prikaz zgrada, prikaz na mobitelu.
* Uvod pri prvom posjetu i prozor „O projektu i izvorima podataka“ s metodologijom i izvorima.

## 3. Ciljni korisnici

| Korisnik | Što dobiva |
|---|---|
| **Urbanisti i gradski uredi** (prostorno uređenje, zaštita okoliša, energetika) | gradski pregled potencijala, usporedba četvrti, podloga za strategije prilagodbe klimatskim promjenama i za planove |
| **Upravitelji gradske imovine** | popis objekata Grada s ravnim krovom i velikom potrošnjom, gdje se ulaganje najbrže isplati i gdje Grad sam odlučuje |
| **Gradske četvrti i mjesni odbori** | brojke za svoje područje, argument za projekte i javne pozive |
| **Upravitelji zgrada i građani** | brza provjera vlastite zgrade prije razgovora s projektantom ili prijave na sufinanciranje |

## 4. Korisnička vrijednost

Tehnički potencijal za Grad Zagreb (gornja granica prije statičke provjere, zaštite kulturnih dobara i
vlasničkih odnosa; izvor: izračun iz ZG3D-a, parametri u `METODOLOGIJA.md`):

| Pokazatelj | Cijeli grad | Samo objekti Grada (ISGE) |
|---|---|---|
| Zgrade | 356 984 | 853 |
| Kandidati za zeleni krov | **82 029 zgrada**, 1 339 ha iskoristivo | 611 zgrada, 37 ha |
| Zadržana kišnica (svi kandidati) | **~5,9 mil. m³ godišnje** | ~163 000 m³ godišnje |
| Kandidati za FN | **209 598 zgrada**, 3,4 GWp | 833 zgrade, 69 MWp |
| Proizvodnja FN | ~3,8 TWh godišnje | ~78 GWh godišnje |
| Izbjegnute emisije CO₂ | ~511 000 t godišnje | ~10 400 t godišnje |
| Pokrivenost vlastite potrošnje | – | **~75 %** (452 objekta s ≥ 20 MWh/god) |

**Zašto je to korisno:**

* **Odluke na temelju podataka:** umjesto procjene „od oka“ grad vidi gdje je potencijal najveći i koliko
  bi koštao. Scenarij 10 % ili 30 % daje realne ciljeve za prvi korak.
* **Brze pobjede na gradskim zgradama:** objekti Grada imaju poznatu potrošnju i jednog vlasnika, pa je
  odluka najjednostavnija.
* **Povezivanje podataka koje inače stoje odvojeno:** 3D model, potrošnja energije i zaštita baštine
  nalaze se na istoj karti, na razini pojedine zgrade.
* **Bez troška za korištenje:** aplikacija je statička, radi u pregledniku bez prijave, a hosting je besplatan.
* **Otvoreno i ponovljivo:** kod (MIT) i izvedeni podaci (CC BY 4.0) su javni. Pipeline se ponovno
  pokreće kad Grad objavi novu verziju modela, a isti pristup radi za svaki grad s LoD 2 modelom.

## 5. Ograničenja

* Dio modela potječe iz snimanja 2008., pa novije promjene na krovovima (nadogradnje, postojeći FN)
  nisu vidljive. Kartica zgrade prikazuje godinu snimanja.
* Nosivost krova nije poznata. Rezultat znači „kandidat za statičku provjeru“.
* Zasjenjenje od susjednih zgrada i drveća nije uključeno.
* Povezivanje kulturnih dobara i ISGE objekata sa zgradama ide preko adresa (geokodiranje), pa nisu
  povezani svi zapisi (kulturna dobra 368 od 470, ISGE 854 zgrade od 1 082 objekta).

Detalji su u [`METODOLOGIJA.md`](METODOLOGIJA.md), poglavlje 6.

## 6. Daljnji razvoj

1. **Prioritizacija „gdje najviše treba“:** spoj s ljetnom temperaturom površine (Landsat), nedostatkom
   zelenila (Sentinel-2 NDVI), gustoćom stanovništva i blizinom vrtića, škola i domova za starije
   (Geoportal Grada Zagreba), s klizačima za težine u aplikaciji.
2. **Javne ustanove i granice četvrti s Geoportala** kao sloj na karti i u kartici zgrade.
3. **Zasjenjenje iz 3D modela** (sjena susjednih zgrada) za točniji prinos FN.
4. **Prepoznavanje postojećih zelenih krovova i elektrana** na ortofotu DGU-a pomoću računalnog vida,
   kako bi se iz potencijala izuzeli već iskorišteni krovovi.
5. **Biosolarni krov** (FN iznad zelenog krova) kao treći scenarij, uz povećanje prinosa zbog hlađenja modula.
6. **Izvoz za Geoportal i data.gov.hr:** rezultati po zgradi i četvrti kao novi otvoreni skup (GeoPackage,
   CSV) i kao WMS/WFS sloj.
7. **Primjena na druge gradove** koji objave LoD 2 model zgrada.

## 7. Korišteni alati

Popis softvera i biblioteka, uključujući AI alate, nalazi se u README-u, poglavlje
[„Korišteni alati“](../README.md#korišteni-alati). Sav softver je otvorenog koda; za pisanje koda i
dokumentacije korišten je AI asistent Claude Code (Anthropic).
