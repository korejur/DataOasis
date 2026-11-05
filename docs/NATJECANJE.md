# Natjecanje – pravila i kriteriji ocjenjivanja

Sažetak *Pravila za Datathon Portala otvorenih podataka* i *Javnog poziva* (MPUDT, 2026.).
Izvorni PDF-ovi su na stranicama data.gov.hr i mpudt.gov.hr. U ovom dokumentu je samo ono što utječe na naš rad.

## Rokovi

| Što | Rok |
|---|---|
| **Dostava rješenja** e-poštom na **open.data@mpudt.hr** | **pon 9. 11. 2026. do 24:00** |
| Objava rezultata | do 17. 11. 2026. |
| Predstavljanje prva tri mjesta (konferencija MPUDT-a, Zagreb) | 23. 11. 2026. |

Prijavljujemo se u **izazov B – Okoliš i održivi prostor**. Primjeri iz poziva koji nam odgovaraju:
*procjena izloženosti poplavama, požarima i drugim klimatskim rizicima* (zadržavanje kišnice,
toplinski otoci) te *održivo upravljanje resursima* i *građanska osviještenost*.

## Što se predaje (Pravila, pogl. VIII)

1. Izvorni kod ili poveznica na **javni repozitorij** (github.com)
2. Tehnička i projektna dokumentacija, uključujući **opis tehničke arhitekture** i **popis skupova podataka s izvorima**
3. Demo materijali: **poveznica na radni prototip**, snimke zaslona
4. **Video do 3 minute** koji prikazuje rješenje u primjeni: problem, ciljni korisnici, izvori podataka,
   funkcionalnosti, tehnička arhitektura, korisnička vrijednost, daljnji razvoj

Rješenje bez videa ili dostavljeno nakon roka **ne ocjenjuje se**. Ako je nešto preveliko za e-poštu,
šalje se poveznica koja mora raditi barem do objave rezultata.

**Ostali uvjeti:**
* Za podatke s Portala navodi se izvor, uz poštivanje licence. U dokumentaciji se navode **svi** skupovi, njihovi izdavatelji i poveznice.
* Koristi se softver otvorenog koda. Postojeći alati i biblioteke, **uključujući AI alate**, smiju se koristiti ako se navedu u dokumentaciji.
* Objava pod open-source licencom na GitHubu se boduje. Izbor licence je na timu.
* Tim zadržava autorska prava. Organizator smije javno prikazati rješenje i video.

## Kriteriji ocjenjivanja (Javni poziv, pogl. VII) – najviše 60 bodova

Kod jednakih bodova prednost imaju veći bodovi za **Izvedivost**, a zatim za **Upotrebu otvorenih podataka**.

| Kriterij | Bod. | Što se pita | Što radimo za bodove | Uloga |
|---|---|---|---|---|
| **Izvedivost rješenja** | **10** | Radni prototip ili kod koji se može nastaviti razvijati? Je li dovršeno i spremno za upotrebu? | aplikacija na **javnom linku** koja radi bez instalacije; pipeline se može ponovno pokrenuti; README s uputama | aplikacija |
| **Dojam rješenja (UI/UX)** | **10** | Je li se razmišljalo o sučelju i iskustvu? Je li jednostavno za korištenje? | čista karta, jasna legenda, kartica zgrade na hrvatskom, pretraga adrese ili četvrti, radi na mobitelu, brzo učitavanje; testiranje s osobom izvan tima | aplikacija + metodologija (test) |
| **Prezentacija (video)** | **10** | Jasno, strukturirano i uvjerljivo: problem, korisnici, podaci, funkcionalnosti, tehnika, korist? Demonstracija? | scenarij po zadanim točkama, snimka **stvarnog korištenja** aplikacije, titlovi, točno 3 min | metodologija |
| Upotreba otvorenih podataka | 5 | Podaci izravno preko API-ja tijela javnog sektora ili s portala, odnosno preuzeti i pripremljeni? | **CKAN API data.gov.hr** (automatsko preuzimanje ZG3D), **PVGIS API (JRC)**; istaknuti u dokumentaciji i videu | metodologija |
| Povezivanje javno dostupnih podataka | 5 | Koliko relevantnih izvora? Jesu li smisleno povezani? Stvara li povezivanje novu vrijednost? | ZG3D + PVGIS + ustanove + ISGE potrošnja + kulturna dobra + granice (+ LST/NDVI); **pokazati spoj** u kartici zgrade (npr. „vrtić, troši X kWh, FN pokriva Y %“) | podaci + aplikacija |
| Relevantnost za izazov | 5 | Je li rješenje svrsishodno za temu? | uokviriti kao **klimatska prilagodba**: kišnica i rizik od poplava, toplinski otoci, CO₂ | metodologija |
| Utjecaj i korist za zajednicu | 5 | Donosi li korist korisnicima? | brojke za grad i četvrti (m³ vode, MWh, t CO₂, €), scenariji, prioritet za osjetljive skupine; ciljni korisnici: Grad, četvrti, upravitelji zgrada, građani | metodologija + aplikacija |
| Inovativnost i primjena tehnologija | 5 | Napredne tehnologije (AI, IoT, big data…) na inovativan način? | obrada 3D modela (LoD 2.2, ~357 tis. zgrada, 1,2 GB) – **big data / 3D geoprocesiranje**, vlastiti parser geometrije, vektorske pločice; AI kao daljnji razvoj (npr. prepoznavanje postojećih zelenih krovova na ortofotu) | aplikacija + metodologija |
| Tehnička arhitektura i integracijski potencijal | 5 | Je li arhitektura jasno opisana? Interoperabilni standardi? Povezivost s javnim sustavima? Tehnički, organizacijski i pravni preduvjeti? | `docs/ARHITEKTURA.md`: dijagram, standardi (**OGC GeoParquet, MVT/PMTiles, GeoJSON, EPSG:3765/4326, CKAN API**), integracija (Geoportal Zagreb, ZG Solari, ISGE, FZOEU), preduvjeti | aplikacija |

**Zaključak za prioritete:** UI/UX, radni prototip na javnom linku i video zajedno nose pola bodova.
Zato se funkcionalnosti zamrzavaju u nedjelju u 18:00, a ostatak vremena ide na doradu sučelja, dokumentaciju i video.
