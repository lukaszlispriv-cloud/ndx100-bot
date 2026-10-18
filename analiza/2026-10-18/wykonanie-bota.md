# Jak logika wykonawcza (app.py) zamieniła wynik modelowy koszyka w wynik rachunku — W1–W7, ze szczególnym uwzględnieniem W6–W7

Notatka analityczna (18.10.2026). Dane: `closes_5y.csv` (Yahoo, 1257 sesji, 103 spółki + indeksy), `signals.json` + 39 stanów z gita (`koszyki_historia.json`), raporty `reports/puls-2026-10-12…16.html`, `reports/raport-2026-W2…W8.html`, `app.py` (2239 linii, v1.9.0+), `INSTRUKCJA.md`, `WDROZENIE-2026-09-28.md`, `rutyny/dzienna.md`, `rutyny/PROPOZYCJA-2026-10-12-model-3.1.md`. Wszystkie liczby z rachunku podaję wyłącznie w procentach/p.p. Skrypty i wyniki: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/wyk_*.py`, `wyk_*_out.txt`, `wyk_*_wynik.json` (uruchamiane `python3 wyk_X.py` z tego katalogu; `-I` blokuje import `wyk_common`, a CSV jest tylko czytany).

n = 7 tygodni. Żaden wynik poniżej nie jest istotny statystycznie w sensie przewagi modelu; istotne są za to **tożsamości księgowe** (mnożnik 1,2; dźwignia; wariancja), które nie wymagają dużej próby.

---

## 0. Najważniejsze tożsamości, które porządkują całą resztę

1. **`spread_pp` = średni zwrot LONG − średni zwrot SHORT (bezwzględnie)** — indeks się skraca: (L−NDX) + (−(S−NDX)) = L−S. Wynik rachunku bez kosztów = 5·0,24·(śr. L) − 5·0,24·(śr. S) = **1,2 × spread_pp**. Raporty dzienne piszą „1 p.p. zwrotu nogi ≈ 0,24 % kapitału” — prawda per noga, ale **1 p.p. spreadu = 1,2 % kapitału**. W7: −21,15 p.p. → −25,4 % kapitału modelowo; rachunek −23,7 % od szczytu (stopy nieco pomogły; W8 raport, sekcja KILL SWITCH). Zgodność co do rzędu wielkości potwierdza, że rachunek gra dokładnie to, co liczy model — tylko z dźwignią 2,4.
2. **Koszyk nie jest neutralny rynkowo.** Nogi LONG to sprzęt AI (σ60 4,2–4,8 %/d), SHORT to defensywy (σ60 1,2–2,3 %/d). Przy równych dolarach na nodze różnica bety ×1,2 daje betę netto ok. +1,2…+1,7 → sam ^NDX −5,49 % w W7 kosztował ~7–9 % kapitału. Konstrukcja „równe wagi dolarowe” jest zakładem kierunkowym na rynek plus zakładem na czynnik SOX−NDX.
3. **σ dzienna kapitału przy ALLOC 0,24: 3,7–5,6 %** (sekcja c). Kill switch −25 % to 4,5–6,8 σ dziennych, ale tylko ~1,1–1,5 σ czterotygodniowych. Przy zerowej przewadze P(kill w 52 tyg.) = 80–97 %. To nie jest parametr ryzyka, to parametr czasu życia systemu.

---

## (a) Moment wejścia: poniedziałek 13:45/17:05 UTC vs D0 (piątkowe zamknięcie)

Skrypt: `wyk_a_opoznienie.py` → `wyk_a_out.txt`, `wyk_a_wynik.json`. Aproksymacja: cena wejścia = zamknięcie pierwszej sesji po D0 (bot wchodzi 13:45/17:05 UTC = 9:45/13:05 ET; brak danych intraday). Dla W5–W7 dodatkowo wariant od faktycznych `fills` nóg nowych.

| W | D0 | wejście | rozlicz. | model (od D0) | od zamkn. D+1 | **koszt opóźnienia** | konto (rotacja→rotacja) | od fills |
|---|---|---|---|---|---|---|---|---|
| W1 | 26.08 | 27.08 | 28.08 | −4,06 | −4,07 | −0,01 | −2,98 | — |
| W2 | 28.08 | 31.08 | 04.09 | +6,40 | +6,00 | −0,40 | +6,77 | — |
| W3 | 04.09 | 08.09 | 11.09 | +1,42 | −2,03 | −3,45 | −7,32 | — |
| W4 | 11.09 | 14.09 | 28.09 | +13,81 | +23,64 | **+9,83** | +27,19 | — |
| W5 | 28.09 | 29.09 | 02.10 | +5,95 | +5,49 | −0,46 | +5,57 | +4,75 |
| W6 | 02.10 | 05.10 | 09.10 | −5,59 | −4,07 | +1,51 | −8,57 | −3,97 |
| W7 | 09.10 | 12.10 | 16.10 | −21,15 | −16,65 | **+4,50** | (19.10) | −17,49 |
| **W4–W7** | | | | **−6,98** | **+8,41** | **+15,38** | | |
| W1–W7 | | | | −3,22 | +8,31 | +11,52 (śr. 1,65, sd 4,33, t = 1,0) | +20,66 (W1–W6) | |

(model W2/W6 różni się od `history` o 0,2–0,3 p.p. — korekty dywidendowe/zaokrąglenia w raportach; nieistotne).

**Wnioski (fakty):**
- Opóźnienie wejścia **nie było kosztem**, w W4–W7 było korzyścią: +15,4 p.p. spreadu ≈ +18 % kapitału przy 0,24. Mechanizm: w obu tygodniach z dużą luką poniedziałkową (W4: longi −4…−10 % 14.09; W7: LITE −9,8 %, MU −3,9 %, PANW −3,6 % 12.10) bot wszedł **po** luce. W W4 luka się odwróciła (+23,6 od D+1), w W7 nie — ale wejście po luce i tak ograniczyło stratę o 4,5 p.p.
- Rozkład jest dwumodalny i zdominowany przez dwie obserwacje; średnia +1,65 p.p. przy t = 1,0 — **nie da się stwierdzić znaku efektu**. To, co da się stwierdzić: przesunięcie wejścia o jedną sesję zmienia wynik tygodnia o ±4–10 p.p., czyli tyle, ile cała „przewaga” modelu. Metryka `spread_pp` od D0 **nie mierzy tego, co gra rachunek** — potrzebna jest seria „od zamknięcia D+1 / od fills” jako główna (PROPOZYCJA 3.1 pkt 1 to proponuje; podtrzymuję, ale jako metrykę GŁÓWNĄ, nie dodatkową).
- Seria „konto” (rotacja→rotacja, czyli jak naprawdę trzymane są pozycje) sumuje się do +20,7 p.p. za W1–W6 wobec −3,2 modelu — różnica to głównie W4 trzymane 11 sesji (+27,2) i W3 obciążone luką 14.09 (−7,3). **Rachunek rozlicza inne okna niż raport.**

**Dodatkowy koszt rotacji wykryty w fills (fakt):** w obu rotacjach część nowych nóg weszła dopiero w biegu 17:05, nie 13:45 — W6: LITE, AMAT, PAYX (commit 514dcec 13:45 → 7a1ed7a 17:05), W7: PEP, TMUS (35e7077 → 0fdb802). W W7 trzy nowe longi otwarte o 13:45 (PANW 411,82, MRVL 273,80, CSCO 116,47) zostały o 17:05 **zamknięte i otwarte ponownie** (poziom brokera 400,95 / 267,53 / 115,53 — `cena_brokera` w fills, puls 13.10 „Rozjazd cena vs cena_brokera”). Koszt: podwójny spread pierwszego dnia i **przesunięcie kotwicy stopu** na niższy poziom (PANW stop 360,86 zamiast 370,64; MRVL 240,78 zamiast 246,42). Hipoteza przyczyny (wysoce prawdopodobna, do potwierdzenia logiem `/run` z 12.10 13:45, pola `limit_depozytowy.stopa_wyliczona`, `realizacja_celu`, `alloc_po_ograniczeniu`): w `sync()` stopa depozytu = `uzyty / teraz_brutto`, gdzie `uzyty` = kapitał − dostępne (depozyt **wszystkich** pozycji, w dniu rotacji 12 sztuk), a `teraz_brutto` sumuje **tylko nogi niesione** (w W7: 5). Iloraz zawyża stopę ~2,4× → `alloc` o 13:45 spada do ~0,12 → nowe nogi otwarte na pół wielkości (PEP/TMUS przy jednym locie mogły wypaść za `MAX_OVERSHOOT`), a o 17:05 (gdy `teraz_brutto` liczy już 8 nóg) alloc wraca do 0,24 i bot dokłada przez zamknij/otwórz. Z /status pre-market (5 odczytów 12–17.10) `depozyt_zabezpieczajacy == gotówka`, więc `MARGIN_FROM_AVAILABLE=true` musi być ustawione (opcja B z `WDROZENIE-2026-09-28.md`) — inaczej alloc byłby ~0,12 także o 17:05.

---

## (b) Twardy stop 10 % od poziomu brokera + ponowne otwarcie w kolejnym biegu

Skrypt: `wyk_b_stopy.py` → `wyk_b_out.txt`.

**Co robi kod (fakty z app.py):**
- `stopy_bezpieczenstwa()`: `wejscie = p.get("wejscie") or fills[t]["cena"]` — **najpierw poziom brokera**, dopiero w braku — cena tezy. Docstring funkcji `ceny_wejscia()` i CLAUDE.md mówią odwrotnie („bramka i stopy czytają cena”). Skutek: każde wyrównanie (zamknij/otwórz) **przestawia kotwicę stopu**. MU: cena tezy 913,35 (27.08), poziom brokera 1063,70 (wyrównanie 6.10) → stop 957,33 zadziałał 13.10, gdy MU był **+4,4 % nad ceną tezy** i +12,7 % nad ceną, od której puls liczył wyzwalacze przed resetem ledgera. To ten sam błąd, który 15.09 zamknął LITE (CLOSE od D0 przy pozycji na plusie) i który bramka reakcji miała wyeliminować — bramka go wyeliminowała, stop go odtworzył.
- Po stopie: `book.pop(epic)` tylko **w tym biegu**; w następnym biegu ticker nadal jest w `sig["long"]` bez `exclude` → `desired_book` zawiera go → otwarcie w docelowym rozmiarze po niższej cenie. Puls dowiaduje się o stopie następnego dnia o 12:30 UTC i może zablokować wyłącznie wpisem CLOSE (LITE 14.10) — protokół Pulsu (2 sesje potwierdzenia, 4/8 %, blokada sektorowa) nie ma reguły „po stopie bota”.
- Stop sprawdzany dwa razy dziennie intraday (13:45 = 15 min po otwarciu, czyli na luce; 17:05) — bez danych intraday ekstrapoluję; raport W8: „każdy zrealizowany blisko dołka dnia”.

**W7 — faktyczne poziomy (fills, raport W8), wynik w % wartości pozycji i % kapitału (ALLOC 0,24):**

| noga | poziom brokera | stop | reopen | bez stopu | stop bez reopen | **faktycznie (stop=próg)** | faktycznie (stop=close dnia) | REDUCE 50 % zamiast stopu |
|---|---|---|---|---|---|---|---|---|
| MU | 1063,70 | 957,33 (13.10 13:45) | 935,73 (13.10 17:05) | −17,4 | −10,0 | −16,1 | −16,5 | −13,7 |
| LITE | 1088,08 | 979,27 (13.10 17:05) | — (CLOSE 14.10) | −24,3 | −10,0 | −10,0 | −9,2 | −17,1 |
| MRVL | 267,53 | 240,78 (15.10 13:45) | 235,93 (15.10 17:05) | −14,8 | −10,0 | −13,4 | −13,3 | −12,4 |
| PANW | 400,95 | 360,86 (16.10 13:45) | 341,71 (17:05, ½) | −14,7 | −10,0 | −10,0 | −14,7 | −12,4 |
| **suma 4 nóg** | | | | **−71,2 → −17,1 % kap.** | **−40,0 → −9,6 %** | **−49,5 → −11,9 %** | −53,6 → −12,9 % | −55,6 → −13,3 % |

- Stop 10 % w W7 **pomógł** względem braku stopu o ~4–5 % kapitału (trend był jednokierunkowy przez 5 sesji).
- **Ponowne otwarcie oddało 2,3–3,3 % kapitału** z tego zysku (MU −6,1 % od reopen, MRVL −3,4 %). Stop bez reopen byłby najlepszy z wariantów; LITE (jedyna nie otwarta ponownie dzięki wpisowi Pulsu) to jedyna noga, gdzie stop zadziałał „podręcznikowo”.
- Stop 15 % od brokera: na zamknięciach zadziałałby tylko dla MU i LITE (−14,3 % kap.) — gorzej niż 10 %.
- REDUCE zamiast stopu: −13,3 % — między „bez stopu” a „stop”.

**Symulacja W1–W7 na zamknięciach** (wejście close D+1, wyjście close rozliczenia; stop sprawdzany na zamknięciu = dolne oszacowanie liczby stopów; % kapitału przy 0,24):

| wariant | W6 | W7 | suma W1–W7 | liczba stopów |
|---|---|---|---|---|
| bez stopu | −4,89 | −19,98 | +9,97 | 0 |
| stop 10 % bez reopen | −5,10 | −18,88 | +10,85 | 5 |
| stop 10 % + reopen (bot) | −4,86 | −20,13 | +9,84 | 5 |
| stop 15 % | −4,89 | −19,98 | +9,97 | 2 |
| REDUCE 50 % przy −10 % | −4,99 | −19,43 | +10,41 | 6 |

Stopy w W1–W5 nie zadziałały ani razu (na zamknięciach); cały efekt to W6–W7. Różnice między wariantami (≤ 1,1 % kapitału) są o rząd mniejsze niż wynik tygodnia.

**Panel historyczny 2021–2026** (nogi koszyków W1–W8, 7903 nienakładających się okien 5-sesyjnych): przebicie −10 % na zamknięciu w ≤5 sesji w **5,6 %** okien; po przebiciu ruch do końca okna: śr. **+0,5 %**, mediana 0,0 %, sd 5,3 %, dalsze spadki w 30 % przypadków. Czyli: **stop 10 % nie ma dodatniej wartości oczekiwanej** (po stopie kurs średnio nie kontynuuje), ma wartość wariancyjną (obcina ogon). Ponowne otwarcie ma oczekiwaną wartość ≈ 0 minus spread, ale **podwaja liczbę transakcji na nodze i podnosi jej realizowaną zmienność**. W W7 trend kontynuował — to szczęście stopu, nie jego własność.

**Diagnoza:** stop i protokół Pulsu są rozłączne i Puls jest **zawsze wolniejszy** (potwierdzenie drugą sesją + blokada sektorowa + bieg 12:30 UTC). W szybkiej wyprzedaży stop strzela pierwszy, bez blokady sektorowej, od zmiennej kotwicy, po czym bot sam odbudowuje ekspozycję. Reakcje Pulsu wykonały się przez cały okres raz (LITE, przez nieotwieranie). `reaction_pp` skumulowane −1,36 p.p. mówi o Pulsie prawie nic — mówi o tym, że stop wyprzedza protokół.

---

## (c) Sizing 24 %/noga przy zmienności nóg → σ kapitału i P(kill switch)

Skrypty: `wyk_c_sigma.py` → `wyk_c_out.txt`, `wyk_c_wynik.json`; `wyk_c2_start.py` → `wyk_c2_out.txt`.

**σ60 dzienna (60 zwrotów c/c do D0):**

| | W6 LONG | W6 SHORT | W7 LONG | W7 SHORT |
|---|---|---|---|---|
| nogi | MU 4,9 · LITE 6,0 · TER 4,8 · AMAT 4,0 · AMD 4,1 | APP 4,1 · NFLX 2,3 · PAYX 2,1 · CMCSA 2,3 · SBUX 1,3 | MU 4,7 · LITE 5,8 · MRVL 4,8 · PANW 3,8 · CSCO 2,1 | CMCSA 2,3 · SBUX 1,2 · PEP 1,2 · TMUS 3,0 · APP 3,8 |
| średnia | **4,76 %** | 2,39 % | **4,23 %** | 2,29 % |

- P(ruch 5-sesyjny ≤ −10 % | normalny): LITE 22–23 %, MU 17–18 %, MRVL 17 %, TER 18 % — **stop 10 % na tych nogach to 0,8 σ5, zdarzenie co 4–6 tygodni bez żadnej informacji**; na PEP/SBUX (σ5 2,7 %) stop 10 % to 3,7 σ — nigdy. Jeden procentowy próg dla nóg o σ różniącej się 5× nie jest regułą ryzyka.
- **σ dzienna kapitału** (kowariancja 60/250 sesji, wagi ±0,24): W6 **5,63 % / 5,08 %** (tyg. 12,6 %, 4-tyg. 25,2 %; korelacja par LONG 0,75); W7 **4,09 % / 3,84 %** (tyg. 9,2 %, 4-tyg. 18,3 %; korelacja 0,30). Gdyby nogi były niezależne: 2,9 % / 2,7 % — **ok. 40 % σ to koncentracja czynnikowa**, reszta to dźwignia 2,4.
- Zrealizowane W7 (bez stopów/kosztów): dzienne −6,1 / −1,9 / −7,6 / −4,8 / −6,4 → **−26,8 %** w 5 sesji; każda sesja z tym samym znakiem — to nie 5 niezależnych losowań (σ dzienna zrealizowana 2,2 %, ale średnia −5,4 %/d: dryf czynnikowy, nie szum). W6: −6,7 %.
- Pula „koszyki tego typu” (7 koszyków W1–W7 × 500 sesji do swojego D0, zwrot Σlong−Σshort): σ jednostkowa 11,8–17,6 %/d, razem 15,25 %/d → **×0,24 = 3,66 %/d kapitału, 16,4 % na 4 tyg.** Średnia historyczna +1,5 %/d jednostkowo (= in-sample „AI long vs defensywy short” zarabiało w latach 2024–26; nie zakładam, że to trwa — wariant „zerowa przewaga” wyśrodkowuje).

**Bootstrap blokowy (blok 5 sesji, 20 000 ścieżek, kill = −25 % od kroczącego szczytu):**

| ALLOC | σ kap./d | P(kill ≤ 4 tyg., start na szczycie) | P(kill ≤ 4 tyg., start −21 %) | P(kill ≤ 52 tyg.) |
|---|---|---|---|---|
| 0,10 | 1,53 % | 0,0 % | 34 % | 42 % (9 % z dryfem hist.) |
| 0,12 | 1,83 % | 0,2 % | 41 % | 58 % (18 %) |
| 0,16 | 2,44 % | 1,6 % | 52 % | 80 % (41 %) |
| 0,20 | 3,05 % | 5,3 % | 59 % | 92 % (64 %) |
| **0,24** | **3,66 %** | **10,4 %** (6,3 % z dryfem) | **64,5 %** | **96,7 % (80 %)** |

Pula tylko W6/W7: 0,24 → 11,7 % / 66 %. Zgodne z PROPOZYCJĄ 3.1 (0,92–0,97 w 52 tyg.) — tam liczono inną metodą; dwa niezależne oszacowania dają ten sam wniosek.

**Stan na 19.10 (start −23,7 %, ≈ 1,7 % nad progiem), pula W1–W7 / profil W8 (σ jednostkowa W8 9,3 %/d — koszyk W8 jest o 40 % spokojniejszy):**

| ALLOC | P(kill 1. sesja) | ≤ 5 sesji | ≤ 20 sesji |
|---|---|---|---|
| 0,06 | 4,0 % / 0,6 % | 22 % / 11 % | 55 % / 40 % |
| 0,10 | 10 % / 2,9 % | 39 % / 25 % | 68 % / 56 % |
| 0,12 | 13 % / 4,6 % | 45 % / 29 % | 71 % / 60 % |
| **0,24** | **26 % / 20 %** | **60 % / 50 %** | **80 % / 74 %** |

Przy ≈ 1,7 % zapasu i gross 240 % **rotacja poniedziałkowa ma 1 na 4–5 szans skończyć się kill switchem pierwszego dnia**, i ponad połowę w tygodniu. Nawet ALLOC 0,06 daje ~40–55 % w 4 tygodnie — zapas jest za mały na jakikolwiek gross; jedyne, co zmienia skalę, to decyzja właściciela o progu/kapitale (poza zakresem tej notatki) albo przyjęcie, że system zostanie zatrzymany i uruchomiony od nowa z nowym `equity_peak`.

---

## (d) Rebalans 17:05, bramka reakcji, kontrola kapitału, ALLOC_PCT_SAFE, limit depozytowy — co pomogło, co szkodziło

| mechanizm | W6–W7: działanie | ocena | dowód |
|---|---|---|---|
| **Wyrównywanie 17:05** (`REBALANCE_HOURS=17`, pasmo 0,30–0,35, `MIN_REBALANCE_ACC=25`) | Pasmo 30 % przy cotygodniowej rotacji rzadko się wyzwala; w W7 brak śladu wyrównań poza dniem rotacji. Ale: dzień rotacji = zamknij/otwórz nowych nóg po 3,5 h (PANW/MRVL/CSCO 12.10) | neutralne w tygodniu, **szkodliwe w dniu rotacji** (podwójny spread + przestawiona kotwica stopu) | fills `cena` vs `cena_brokera`; puls 13.10 |
| **Limit depozytowy** (`MARGIN_BUDGET 0,6`, stopa = `uzyty/teraz_brutto`) | W dniu rotacji licznik (depozyt wszystkich pozycji) i mianownik (ekspozycja tylko nóg niesionych) są niespójne → zawyżona stopa → alloc o 13:45 ~½ → dokładka o 17:05 | **szkodliwe** (hipoteza do potwierdzenia logiem) | sekcja (a); `sync()` linie „uzyty = …”, „teraz_brutto” |
| **Bramka reakcji** (`REACT_GATE`, 4 %/8 % od `fills.cena`) | W W6–W7 nie przepuściła ani nie złagodziła żadnego wpisu, bo stop zawsze zadziałał wcześniej (LITE CLOSE 14.10 trafił na pozycję już zamkniętą; PANW REDUCE 16.10 — stop o 13:45 przed bramką) | **bez wpływu**; konstrukcyjnie zbędna, gdy stop 10 % od brokera jest ciaśniejszy niż CLOSE 8 % od tezy w każdym spadku >2 % między kotwicami | raport W8 WARIANT ZARZĄDZANY; `wykonanie.reakcje = {}` |
| **Kontrola kapitału → `ALLOC_PCT_SAFE`** | W `/run` managed obejmuje `fills` i taktyczne → `zgodne=true` (puls 13.10, 15.10); `/status` pokazuje false przez ERIC/APOG/PENG (książka węższa) — nie dotyczy `/run` | **bez wpływu w W6–W7**; wcześniej (29.09 AKAM) ścięła alloc do 0,10 na starcie W5 (udokumentowane w kodzie) | komentarze `sync()`; puls 12–16.10 |
| **Reset ledgera 10.10** (bieg sobotni, zmiana `version`) | Ceny tezy 7 nóg kontynuowanych nadpisane poziomem brokera (MU 913,35→1063,70). Naprawione 12.10 (noga kontynuowana), ale stop i tak czyta brokera | szkodliwe dla pomiaru Pulsu, **nieistotne dla stopu** (który i tak czyta brokera) | puls 12.10 BOT LEDGER |
| **`MAX_EXPOSURE_STEP 0,25`** | Dotyczy tylko nóg niesionych; nowe nogi wchodzą od razu na 100 % celu — po podwojeniu ALLOC 3.10 cała nowa ekspozycja weszła w jednej rotacji (5.10) | **szkodliwe**: ogranicznik tempa nie ogranicza tempa wtedy, gdy ekspozycja rośnie najszybciej (rotacja po zmianie ALLOC) | `sync()` komentarz „Nowe pozycje otwieramy od razu w docelowym rozmiarze” |
| **Kill switch 0,75 trailing** | Jedyny mechanizm portfelowy; binarny; brak schodka pośredniego | poprawny jako bezpiecznik ostateczny, **brakuje wszystkiego między nim a stopem nogi** | (c) |
| **Moduł taktyczny** | ERIC +3,99 p.p. (W7), APOG/PENG +0,29 (W6); 20 % kapitału na pozycję poza NDX-100 | neutralne/plus; dodaje gross do 280 % przy 2 taktycznych | history |

**Rekonstrukcja ścieżki rachunku (w %):** wariant A (stałe 0,24, wejścia close D+1) daje za W1–W7 sumę +10,0 % i **max obsunięcie −23,9 %** — rachunek: −23,7 % od szczytu. Ale rachunek grał W1–W5 na ALLOC ~0,06–0,12 (12 % nominalnie, ~6,5 % faktycznie przez błąd stopy depozytu, audyt 28.09) i W6–W7 na 0,24: połowa (lub mniej) zysków z dobrych tygodni, pełna strata w złych. Ścieżka „B dla W1–W5 + A dla W6–W7” ≈ +17 % − 25 % ≈ −8 %; rachunek wobec `START_EQUITY` ≈ −17 % (szczyt +9 %, potem −23,7 %). **Różnica ok. −9 p.p. w 7 tygodni to drag wykonawczy**: stopy+reopen W7 (−2,3…−3,3), spready rotacji i wyrównań, finansowanie, LITE 15.09, REDUCE-y W4 — rząd 1–1,3 %/tyg., zgodny z (e).

---

## (e) Koszty CFD przy gross 240 % — roczny drag

Skrypt: `wyk_e_koszty.py` → `wyk_e_out.txt`. **Założenia** (parametry do podmiany przez właściciela; stawki Capital.com nie są w repo): spread round-trip 0,19 % (środek; pomiar audytu 28.09: AVGO 0,088 %, SBUX 0,328 %, CMCSA 0,312 % na parę), finansowanie overnight long 7,0 %/rok (stopa ref. USD ~4 % + marża ~3 %), short 1,0 %/rok (marża − stopa; może być ~0), dywidendy: short płaci 100 % (koszyk short defensyw ~2,8 %/rok), long dostaje 100 % (demo) / 70 % (live), rotacja 6,8 nóg/tyg. (W5–W8: 7/6/5/9 wymian), stopy+reopen 0,7 RT/tyg., wyrównania 1,0 %/mies. (audyt: 1,1 %/mies. przy gross ~90 % i pełnym churnie; po `REBALANCE_HOURS` i `MIN_REBALANCE_ACC` przyjęto połowę, przeskalowaną do gross 240 %).

| składnik | dolne | **środek** | górne |
|---|---|---|---|
| spread rotacji | 8,5 % | **16,1 %** | 25,5 % |
| spread stopów/reopen | 0,4 % | 1,7 % | 5,6 % |
| wyrównania 17:05 | 6,0 % | 12,0 % | 18,0 % |
| finansowanie overnight | 7,2 % | 9,6 % | 11,4 % |
| dywidendy netto (short płaci) | 2,9 % | 2,9 % | 3,0 % |
| **razem / rok** | **25 %** | **42 %** | **64 %** |
| na tydzień | 0,48 % | **0,81 %** | 1,22 % |
| w p.p. spreadu (÷1,2) | 0,40 | **0,68** | 1,02 |

Przy ALLOC 0,12 (gross 120 %): środek 21 %/rok. Skumulowany `spread_pp` W1–W7 = −3,67 p.p. (−0,52 p.p./tyg.); model musiałby dawać **+0,7 p.p./tyg. netto tylko na pokrycie kosztów** (środek), a przy sd ~7 p.p./tyg. wykazanie takiej przewagi wymaga ~400 tygodni. Dominują koszty **transakcyjne, nie finansowe** — rotacja 68 % koszyka co tydzień przy 10 nogach × 24 % to ~330 % obrotu kapitału tygodniowo.

---

## Krytyka PROPOZYCJI 3.1 (12.10) w świetle powyższego

- Zgadzam się: zamrożenie wag modelu, rejestr reguł, metryka 5-sesyjna, brak „oczywistych napraw” selekcji, 8–12 tygodni mierzy tylko wariancję.
- **Nie zgadzam się z ALLOC 0,20** (pkt 15): P(kill 52 tyg.) przy zerowej przewadze 92 % vs 97 % — to nie jest zmiana. Argument „REDUCE niewykonalny przy 0,12 dla MU/LITE” jest prawdziwy, ale rozwiązaniem jest `REDUCE_FALLBACK=close` i/lub nieobejmowanie nóg o cenie >½ celu, nie utrzymywanie dźwigni 2,0.
- **WEEK_LOSS_PCT 0,12** (pkt 12): sensowny, ale napisany przed końcem W7 („w W1–W7 nie wyzwoliłby się”). W W7 skumulowany wynik od zamknięcia D+1 (12.10): 13.10 −1,9 %, 14.10 −9,5 %, 15.10 −14,1 %, 16.10 −20,0 % (`wyk_common`, suma 10 nóg × 0,24) → próg −12 % przekroczony 15.10, REDUCE całości uratowałby ~½ z pozostałych −5,8 %, tj. ~+2,9 % kapitału. Podtrzymuję, ale jako składnik większej zmiany (niżej), bo to też reaguje po fakcie.
- Pominięte przez 3.1: (1) stop czyta poziom brokera, nie tezę; (2) reopen po stopie; (3) stopa depozytu w dniu rotacji; (4) tożsamość 1,2×; (5) koszty transakcyjne 25–64 %/rok — przy nich dyskusja o +1–2 p.p. przewagi jest drugorzędna.
- „Vol-managed per noga obalone (Cederburg)” — literatura dotyczy zwrotów czynnikowych, nie przetrwania rachunku z dźwignią 2,4 i kill switchem; tu celem skalowania nie jest Sharpe, lecz **P(przetrwania)**. Wariant C niżej obniża max obsunięcie z −24 % do −8,5 % kosztem części zysku W4 — to jest wybór właściciela, nie fakt do obalenia.

---

## Propozycje zmian (nazwy, wartości, pseudokod, skutek na W6–W7)

Skrypt kontrfaktyczny: `wyk_d_sizing.py` → `wyk_d_out.txt` (W1–W7, % kapitału, wejścia close D+1, bez kosztów):

| wariant | W6 | W7 | **W6+W7** | suma W1–W7 | sd | max obsunięcie |
|---|---|---|---|---|---|---|
| A — stałe 0,24 (dziś) | −4,9 | −20,0 | **−24,9** | +10,0 | 14,9 | **−23,9 %** |
| B — stałe 0,12 | −2,4 | −10,0 | −12,4 | +5,0 | 7,5 | −12,2 % |
| C — vol-target gross 1,5 %/d | −1,3 | −7,3 | **−8,6** | +0,7 | 4,4 | **−8,5 %** |
| D — drawdown-scale (1−2·dd) | −4,9 | −18,0 | −22,9 | +9,8 | 14,0 | −22,0 % |
| E — parytet σ per noga (2 % ryzyka/noga) | −2,0 | −11,0 | −12,9 | +7,4 | 7,8 | −12,7 % |
| F — C + stop 10 % od tezy bez reopen | −1,3 | −5,7 | **−7,1** | +2,3 | 4,0 | **−7,0 %** |

### 1. Rozmiar pozycji z budżetu zmienności, nie ze stałego procentu (największy efekt)
**Zmienne:** `VOL_TARGET_DAILY=0.015` (σ dzienna kapitału), `ALLOC_PCT_MAX=0.24` (sufit), `ALLOC_PCT_MIN=0.06` (podłoga — lot 0,1 akcji MU/LITE ≈ 10 % kapitału; poniżej noga wypada, patrz pkt 6). Źródło σ: rutyna tygodniowa liczy σ60 nóg i σ portfela z 60 sesji (PROPOZYCJA 3.1 pkt 7 już to proponuje jako pomiar) i zapisuje w **`d0.sigma_port`** oraz **`d0.sigma`** (słownik ticker→σ60) — `d0` jest już polem pisanym przez sobotę, więc walidator (`scripts/waliduj_signals.py`) wymaga tylko dopuszczenia podkluczy; `_sanity` nie odrzuca obcych kluczy w `d0`.
```
sig_port = (sig.get("d0") or {}).get("sigma_port")   # σ dzienna portfela przy ALLOC_PCT_MAX, ułamek
alloc_vol = ALLOC_PCT_MAX * min(1.0, VOL_TARGET_DAILY / sig_port) if sig_port else ALLOC_PCT_MAX
alloc = max(ALLOC_PCT_MIN, min(alloc, alloc_vol))     # przed limitem depozytowym i ogranicznikiem tempa
rep["alloc_vol"] = {"sigma_port": sig_port, "alloc_vol": alloc_vol}
```
Skutek: W6 alloc 0,064, W7 0,088 → **W6+W7 −8,6 % zamiast −24,9 %**; cena: W4 +7,1 zamiast +28,4. P(kill 4 tyg. od szczytu) przy σ 1,5 %/d ≈ 0,2 % (bootstrap dla 0,10–0,12). Dowód: poszlakowy (in-sample n = 7) + twardy co do wariancji (tożsamość σ).

### 2. Stop od ceny tezy, nie od poziomu brokera; po stopie noga wypada do rotacji
**Zmienne:** `STOP_ANCHOR=teza` (domyślnie; `broker` = dotychczas), `STOP_BLOCK_REOPEN=true`. Bot zapisuje stop w polu pisanym przez siebie `wykonanie.stopy = {"TICKER": {"data": …, "wersja": …, "poziom": …}}` (pole `wykonanie` już jest jego); `desired_book` pomija ticker z `wykonanie.stopy` o tej samej `wersja`; rotacja (zmiana `version`) czyści wpisy. CLAUDE.md i rutyny: `wykonanie.stopy` do listy „nie ruszaj”; Puls czyta je zamiast wnioskować ze zniknięcia fills.
```
# stopy_bezpieczenstwa():
wejscie = ((fills.get(t) or {}).get("cena") if STOP_ANCHOR == "teza" else None) or p.get("wejscie")
# sync(), po pętli stopów:
for epic in stopy: wykonanie["stopy"][epic2tic[epic]] = {"data": today, "wersja": sig["version"], "poziom": ...}
# desired_book(): 
zablokowane = {t for t, s in (sig.get("wykonanie") or {}).get("stopy", {}).items() if s.get("wersja") == sig["version"]} if STOP_BLOCK_REOPEN else set()
if ticker in closed or ticker in zablokowane: continue
```
Skutek W7 (faktyczne poziomy): reopen kosztował 2,3–3,3 % kapitału → z blokadą 4 nogi −9,6 % zamiast −11,9…−12,9 % kapitału. Kotwica od tezy: MU nie zostałby zamknięty 13.10 (teza 913,35, stop 822) — w W7 akurat gorzej o ~1 %, ale spójne z bramką i z pomiarem Pulsu; PANW stop 15.10 przy 370 zamiast 16.10 przy 361 (+2,6 % nogi). Dowód: twardy (księgowy) dla reopen; dla kotwicy — spójność, nie wynik.

### 3. Stop w jednostkach zmienności nogi zamiast stałych 10 %
**Zmienne:** `STOP_SIGMA_MULT=2.0`, `STOP_LOSS_PCT_MIN=0.06`, `STOP_LOSS_PCT_MAX=0.15`; próg_i = clamp(2,0 × σ60_i × √5, 6 %, 15 %) z `d0.sigma[t]`; brak σ → `STOP_LOSS_PCT`. Skutek: LITE próg 15 % (zamiast 0,8σ5), PEP/SBUX 6 % (zamiast 3,7σ5 — stop zaczyna chronić shorty, które w W7 straciły 7–9 % od wejścia bez żadnej reakcji). Dowód: teoretyczny (panel: po −10 % brak dryfu, więc wartość stopu jest wariancyjna i powinna być skalowana do σ).

### 4. Stopa depozytu w dniu rotacji
```
# sync(): mianownik stopy = ekspozycja brutto WSZYSTKICH pozycji z `wszystkie`, nie tylko `niesione`
brutto_wszystkie = sum(|size × mid / fx| for p in wszystkie if cena)
wyliczona = uzyty / brutto_wszystkie
```
plus `MARGIN_RATE_MAX=0.5` (odrzuca odczyt >50 %, co dla akcji USA jest zawsze błędem pomiaru) i w dniu rotacji (pierwszy bieg po zmianie `version`) `stopa = MARGIN_RATE_FALLBACK`. Skutek: nowe nogi wchodzą o 13:45 w pełnym rozmiarze, bez zamknij/otwórz o 17:05 (W7: 3 pary spreadów ≈ 0,15–0,2 % kapitału) i bez przestawiania kotwicy; PEP/TMUS wchodzą o 13:45 (W7: TMUS fill 152,79 vs close 12.10 151,87 → +0,6 % nogi). Dowód: poszlakowy (wymaga logu `/run`).

### 5. Schodek portfelowy między stopem nogi a kill switchem
**Zmienne:** `WEEK_LOSS_REDUCE_PCT=0.08`, `WEEK_LOSS_CLOSE_PCT=0.15` (od `equity_d0` zapisanego w `wykonanie.equity_d0` przy pierwszym biegu po zmianie `version`): −8 % → REDUCE wszystkich nóg koszyka (ścieżką `plan_redukcji`, `REDUCE_FALLBACK=close`), −15 % → zamknięcie koszyka do rotacji (bez zmiany `status`). W7 od zamknięcia D+1: −8 % przekroczone 14.10 (−9,5 %) → połowa ekspozycji na pozostałe −10,5 % = **+5,2 % kapitału**; −15 % dopiero 16.10 (−20,0 %; 15.10 było −14,1 %) → w W7 schodek CLOSE nie zadziałałby na czas. Razem w W7 rzędu +5 % kapitału (z pkt 1 skala maleje proporcjonalnie). Uwaga: reaguje po fakcie; w W1–W6 od D+1 nie wyzwoliłby się (najgorzej W6: −4,9 % na koniec tygodnia). Dowód: poszlakowy, jeden tydzień.

### 6. Ogranicznik tempa także dla nowych nóg po zmianie ALLOC
`MAX_EXPOSURE_STEP` liczyć wobec `cel_brutto` całej książki, gdy `ALLOC_PCT` różni się od `alloc_pct_deklarowany` zapisanego w `wykonanie` (zmiana parametru), a nie tylko dla niesionych; `ALLOC_PCT` zmieniać wyłącznie krokiem ≤ 0,04 na 4 tygodnie (INSTRUKCJA). Skutek: podwojenie 3.10 rozłożyłoby się na 3–4 rotacje; W6–W7 na ~0,15 → −15,5 zamiast −24,9. Dowód: księgowy.

### 7. Metryki raportu (rutyna, bez kodu)
`spread_konto_pp` od zamknięcia D+1 (lub od fills) do rotacji jako metryka główna; mnożnik 1,2 (nie 0,24) jawnie w stopce; `koszt_wykonania_pp` = (wynik rachunku w %) − 1,2·spread_konto_pp co tydzień — jedyna miara dragu, która nie wymaga cennika brokera.

### 8. Czego nie zmieniać
`KILL_LEVEL`/`KILL_TRAILING` (przesuwanie progu po stracie to nie zarządzanie ryzykiem), bramka 4/8 % i protokół Pulsu (po pkt 2–3 odzyskują sens), `HEDGE_EPIC=classic`, `REBALANCE_HOURS=17`, `MIN_REBALANCE_ACC` (działały zgodnie z zamiarem).

**Kolejność:** 1 i 2 (jeden PR, testy w `scripts/test_app.py`: alloc z σ, blokada reopen, kotwica), potem 4 (po odczycie logu), 5, 3, 6. Przy obecnym zapasie ≈ 1,7 % żadna z tych zmian nie usuwa ryzyka kill switcha w W8 (P ≈ 40–55 % w 4 tyg. nawet przy ALLOC 0,06) — to jest decyzja właściciela o kapitale/progu, której kod nie zastąpi.

---

## Czego nie da się stwierdzić z tych danych
- Faktycznych cen realizacji stopów i spreadów (brak eksportu transakcji po 28.09) — część (b) używa progu i zamknięcia jako widełek.
- Przyczyny otwarcia PEP/TMUS/LITE/AMAT/PAYX dopiero o 17:05 (brak logu `/run`; hipoteza w (a)/(d)).
- Rzeczywistych stawek overnight i traktowania dywidend na rachunku demo Capital.com — (e) to model parametryczny.
- Znaku przewagi modelu w jakimkolwiek oknie (t ≤ 1,0 wszędzie); dlatego propozycje dotyczą wyłącznie wariancji, kosztów i spójności, nie selekcji.
