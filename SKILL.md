---
name: novastar-module-config
description: Pronalazi i bira tačan NovaStar konfiguracioni fajl (.rcfgx/.rcfg) za LED modul iz podataka ili slika modula (naljepnica, čipovi, PCB) i iz slike liste fajlova u NovaLCT-u. Koristi kad treba pokrenuti LED modul na NovaStar kartici, kad modul ne svijetli ili kad se bira fajl iz Load from... ili baze. Find the right NovaStar receiving-card config for an LED module.
---

# NovaStar: konfiguracioni fajl za LED modul

Cilj je da korisnik na NovaStar receiving karticu (MRV, A serija i slične) učita **fabrički konfiguracioni fajl** za tačnu kombinaciju **driver čip + dekoder + model ploče**. Ručno pogađanje parametara (Smart Setting) je zadnja opcija.

Odgovaraj na jeziku korisnika. Ako piše srpski, bosanski ili hrvatski, koristi ijekavicu. Vodi ga **korak po korak** i čekaj njegovu sliku ili odgovor prije sljedećeg koraka. Ne izmišljaj. Gdje nisi siguran, napiši „pretpostavka“ ili pitaj.

## Tok rada

1. Traži sliku poleđine modula i pročitaj je.
2. Reci korisniku tačno šta piše i gdje, šta da traži i gdje da traži. Ako možeš pokretati kod, pošalji mu i označenu sliku.
3. Prevedi oznake čipova u imena koja koristi NovaLCT.
4. Nađi fajl (izvori redom) ili izaberi iz liste koju korisnik slika.
5. Provjeri fajl prije Send.
6. Send → test boja → tek onda Save.

Ako modul ne prođe test boja, ništa se ne snima. Vrati se na korak 4 i uzmi sljedećeg kandidata.

## 0. Počni od slike modula

Ako korisnik nije poslao sliku, prvo je traži:
- **cijela poleđina modula**, snimljena ravno odozgo, oštro i dobro osvijetljeno;
- **izbliza**: svaka naljepnica i natpis odštampan na PCB-u;
- po potrebi **makro** jednog većeg i jednog manjeg čipa.

Ako je nešto mutno ili nečitljivo, reci tačno šta da ponovo slika i gdje se to nalazi (npr. „bijela naljepnica u donjem srednjem polju, izbliza“). Ne izmišljaj natpise.

Zatim odgovori ovim redom:

**Šta piše na tvom modulu** (tabela)

| # | Gdje na slici | Šta piše | Šta je |
|---|---|---|---|
| 1 | npr. natpis odštampan gore u sredini, uspravno | Q8H35B5U1-40x20 | model ploče, rezolucija |
| 2 | npr. bijela naljepnica dolje u sredini, 3. red | IC: SM16208SJ + RUL5158C | driver + dekoder |

Mjesto opiši prostim riječima (polje, strana, boja naljepnice, red), da ga korisnik nađe na modulu bez tebe.

**Šta tražiš**
- Obrazac imena fajla: `<početak modela>*(<cifre drivera>+<cifre dekodera>)`, npr. `Q8H35*(16208+5158)`. Zvjezdica je revizija ploče, koja se u bazi može razlikovati.
- Folder proizvođača u bazi (npr. *Qiangli*) i pojmove za pretragu: model, kod sa naljepnice, čipovi, kineski naziv proizvođača.

**Gdje tražiš:** izvori iz odjeljka 3, redom. Ako korisnik ima ekran sa istim modulima, počni od njega.

**Označena slika** (kad imaš izvršavanje koda i fotografiju kao fajl; treba Pillow):
1. `python scripts/annotate_module.py foto.jpg --grid mreza.png` daje veličinu fotografije i mrežu koordinata. Pogledaj mrežu i odredi pravougaonike u pikselima originala.
2. Napiši `oznake.json` po uzoru na `tutorijal/primjer_oznake_Q8.json`: brojevi, okviri, uvećani isječci naljepnice i PCB natpisa (sa `rotate` da tekst bude uspravan) i `ime_fajla`.
3. `python scripts/annotate_module.py foto.jpg oznake.json oznake.png`. **Pogledaj rezultat.** Ako okvir promašuje natpis ili je isječak okrenut naopako, ispravi JSON i ponovi. Tek onda pošalji sliku korisniku.

Dok fajl nije nađen, izostavi `revizija` i slika će pokazivati obrazac pretrage. Kad se fajl nađe, dodaj reviziju iz baze i slika pokazuje kako nastaje ime.

## 1. Podaci o modulu

Traži ili pročitaj sa slika:

| Podatak | Gdje |
|---|---|
| Proizvođač | naljepnica, logo na PCB-u (često kineski naziv) |
| Model ploče | natpis na PCB-u (npr. Q8H35B5U1-40x20) |
| Rezolucija Š×V (px), pitch | naljepnica ili PCB |
| Unutrašnji / spoljašnji | naljepnica |
| Driver IC (kolone) | veći čipovi, obično 24 nožice |
| Dekoder / row driver (redovi) | manji čipovi, obično kod ulaznog konektora |
| Kod za podešavanje | naljepnica, kineski 调试代码 |
| Receiving kartica + firmver | NovaLCT ili natpis na kartici (npr. MRV208-N V1.3.0.0) |

Primjer gotove označene slike: `tutorijal/modul_oznake_Q8.png`.

Iz slika napravi tabelu: podatak | vrijednost | izvor (naljepnica / čip / PCB) | sigurnost. **Natpis na samom čipu ima prednost nad naljepnicom.** Ako se razlikuju, upozori. Ako nešto nije čitljivo, reci tačno šta da slika izbliza.

## 2. Imena čipova u NovaLCT-u

- Slova na kraju oznake (SJ, S, GP...) obično označavaju kućište, a ne drugi čip. **Sličan broj je drugi čip** (SM16207 ≠ SM16208).
- Kompatibilni čipovi se u fabričkim fajlovima često vode pod imenom drugog proizvođača.
- Dekoderi se često ne nalaze pod svojim imenom, nego pod porodicom u kategoriji *Other* (npr. „5958 Decoding“, „74HC138 Decoding“).
- Zatečena konfiguracija u kartici nije dokaz da je ispravna.

Potvrđeno u praksi (dopunjavaj kad potvrdiš nove):

| Na modulu | U NovaLCT-u / fajlu | ChipCode u XML-u |
|---|---|---|
| SM16208SJ | ICN2038A | 74 |
| RUL5158C | 5958 Decoding (`Decode5958`) | – |
| SM16188B | SM16188B | 115 |
| 74HC138 | 74HC138 Decoding (`Decode138`) | – |

Sve ostale ekvivalente navedi samo ako ih zaista znaš, i označi ih kao pretpostavku.

## 3. Izbor fajla (izvori i lista)

### Iz liste koju je korisnik slikao

Lista dolazi iz Load from..., baze konfiguracija ili od NovaStar podrške. Imena su obično `Model(driver+dekoder).rcfgx`, npr. `Q8H35A5V1(16208+5158).rcfgx`.

1. Pročitaj **svaki red** liste. Ako je slika odsječena, traži nastavak.
2. Svakom kandidatu ocijeni poklapanje: driver (najvažnije), dekoder, model ploče, rezolucija, unutra/vani.
3. Daj **TOP 3** u tabeli: tačno ime reda | šta se poklapa | šta ne | sigurnost.
4. Jasno reci koji red da učita prvi (dugme Load pored njega).
5. Upozori na:
   - drugu reviziju ploče (B5U1 umjesto A5V1). Ako se čipovi poklapaju, obično radi, ali neka pita podršku;
   - fajl kome se ime i XML unutra ne slažu (preimenovan fajl).

Ako nijedan red ne odgovara, reci to otvoreno i pređi na izvore.

### Izvori, od najsigurnijeg

1. **Ekran koji radi sa istim modulima.** NovaLCT preko LAN-a na njegov player (npr. Taurus) → tab Receiving Card → Readback → Export.
2. **NovaStar podrška i njihova baza konfiguracija**, gdje su folderi po proizvođaču modula. Pošalji podatke iz odjeljka 1 i karticu sa firmverom.
3. **NovaLCT:** Smart Set → Option 3 (baza modula/kabineta) ili Load from Cloud (Pingboss, traži prijavu).
4. **Prodavac ili instalater ekrana.** Poruka na engleskom i kineskom, šablon ispod.
5. **Smart Setting, Option 1.** Ručni izbor čipa i dekodera kroz čarobnjak. Samo ako nema fajla.

Šablon poruke (popuni podacima korisnika):

> Hello, we have a [proizvođač model P_ unutra/vani] module ([Š×V], IC [driver] + [dekoder], debug code [kod]). Please send the NovaStar receiving card configuration file (.rcfg / .rcfgx) for [kartica, firmver]. Thank you!

> 您好，我们有一块[proizvođač model P_ 户外/户内]模组（[Š×V]，IC：[driver] + [dekoder]，调试代码 [kod]）。请提供诺瓦（NovaStar）接收卡 [kartica] 的配置文件（.rcfg / .rcfgx）。谢谢！

## 4. Provjera fajla prije Send

`.rcfgx` je ZIP sa XML-om (`ScanBoardProperty`), a `.oscfg` je ZIP sa `backup/*.rcfgx`. Ako imaš fajl i Python, pokreni skriptu iz ovog skilla (radi i za poređenje više fajlova):

```
python scripts/inspect_rcfgx.py novi.rcfgx zateceni.rcfgx
```

Ključne XML oznake: `ModulePixelCols`/`ModulePixelRows` (modul), `ScanType`, `DataGroup`, `DecType`, `ChipCode`, `Width`/`Height` i `ModuleCols`/`ModuleRows` (**kabinet**, često veći od jednog modula), `ScanBoardName` (za koju karticu je fajl pravljen; fajl za RV-S je radio na MRV208-N).

Učitavanje: tab Receiving Card → dugme **Load from...**. Smart Set → Option 2 traži drugu vrstu fajla (konfiguraciju modula) i ne prihvata .rcfgx.

Kad korisnik pošalje sliku taba Receiving Card nakon učitavanja, provjeri čip, dekoder, širinu i visinu modula, scan, data grupe, refresh i takt. Neka u **Cabinet Information** upiše stvarnu veličinu (jedan modul ili stvarni kabinet). Tek onda Send.

## 5. Proba i trajni upis

1. Prije svega: kabl na izlazu kartice (J1) i na **ulazu** modula, 5 V na modulu, svjetlina nije 0.
2. **Export zatečenog stanja** (Readback → Export).
3. Load from... → Cabinet Information → **Send** (privremeno).
4. Screen Connection → **Test Pattern**: crvena, zelena, plava, bijela. Moraju svijetliti ravnomjerno, bez traka, ponavljanja i pogrešnih boja.
5. Ne radi: **ne snimaj**, uzmi sljedećeg kandidata (isti driver, drugi dekoder ili druga revizija).
6. Radi: **Save** → Export kao `ISPRAVNO_<model>_<pitch>_<ŠxV>_<driver>_<dekoder>.rcfgx` → isključi i uključi napajanje → Readback mora pokazati isto.

## Pravila

- Nikad ne predlaži Save prije uspješnog testa boja.
- Jedan korak po poruci. Prije Send uvijek traži sliku taba.
- Ne tvrdi ekvivalenciju čipova koju ne znaš. Ako fali podatak, pitaj.

## Primjer iz prakse

Qiangli (强力巨彩) Q8 P8 spoljašnji, 40×20, PCB Q8H35B5U1, naljepnica SM16208SJ + RUL5158C, kod M23071337, kartica MRV208-N V1.3.0.0.

- Zatečeno u kartici: SM16188B + 74HC138. Modul taman.
- Ručno SM16208 + 5958 kroz Smart Setting: nije radilo.
- Fajl od podrške nazvan „16208+5158“ imao je unutra XML „5125+5158“, dakle bio je preimenovan.
- **Radio je** `Q8H35A5V1(16208+5158).rcfgx` iz NovaStar baze (folder Qiangli): ICN2038A, 5958 Decoding, scan 1/5, 2 data grupe, 1920 Hz, 17,9 MHz. Kabinet u fajlu je bio 120×160 i promijenjen je na 40×20.
