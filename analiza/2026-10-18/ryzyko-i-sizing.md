# Ryzyko i sizing koszyka NDX100 — notatka risk managera (18.10.2026)

Skrypty i wyniki (wszystko w `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):

| plik | co liczy |
|---|---|
| `ryzyko_sizing.py` → `ryzyko_sizing_out.md`, `ryzyko_sizing_wyniki.json`, `ryzyko_sizing_stdout.txt` | punkty 1–5: σ koszyków, losowe koszyki, bootstrap kill switcha, stopy, korelacja, polityki |
| `ryzyko_extra.py` → `ryzyko_extra_out.md` | wykonalność lotów, ryzyko kill w bieżącym tygodniu (W8), jakość estymatora σ, przeliczenie reguły na W1–W8 |
| dane: `../dane/closes_5y.csv` (1 255 sesji po usunięciu dwóch pustych wierszy świąt 2026‑05‑25 i 2026‑09‑07), `mp_koszyki.json` (składy W1–W7), W8 z `reports/raport-2026-W8.html` |

Konwencje: zwroty proste close/close; „jednostka koszyka” = suma zwrotów 5 nóg long − suma 5 nóg short (po 1,0 na nogę); zwrot kapitału = ALLOC × jednostka (ALLOC 0,24 → gross 240 %). `spread_pp` z `history` = jednostka/5, więc **P&L tygodnia ≈ 5 × ALLOC × spread_pp** (0,24 → 1,2×; 0,08 → 0,4×). Bootstrap blokowy (blok 5 sesji), 20 000 ścieżek, zwroty wyśrodkowane per koszyk (= zerowa alfa). Kill switch jak w `app.py`: kapitał < 0,75 × kroczącego szczytu, sprawdzany na zamknięciach (bot sprawdza dwa razy dziennie, więc prawdopodobieństwa niżej są lekko zaniżone). Bez kosztów, stopów ani REDUCE (osobno w pkt 3).

Ograniczenie zasadnicze: **n = 7 tygodni rozliczonych**; wszystko, co dotyczy alfy, jest nieodróżnialne od zera (śr. spread W1–W7 −0,52 p.p., W1–W6 +2,91 p.p., t ≈ 0,97). Ryzyko natomiast da się policzyć z 5 lat historii nóg — i to jest treść tej notatki.

---

## 1. σ koszyka 5L/5S przy 24 % na nogę

### 1a. Koszyki faktyczne (kowariancja z okna przed D0; `ryzyko_sizing_out.md` §1)

| W | D0 | σ_d nogi long (śr.) | σ_d nogi short (śr.) | **σ_d kapitału, okno 60** | okno 250 | σ_tyg (60, ×√5) | σ_tyg empiryczna 5‑ses. (60) | ρ par LONG 60 | ρ L‑S 60 | σ_d gdyby nogi niezależne |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 08‑26 | 4,64 % | 3,56 % | **5,44 %** | 4,15 % | 12,2 % | 13,1 % | 0,37 | −0,05 | 3,32 % |
| W2 | 08‑28 | 3,84 % | 2,92 % | **4,03 %** | 3,14 % | 9,0 % | 8,5 % | 0,34 | −0,05 | 2,80 % |
| W3 | 09‑04 | 4,33 % | 2,90 % | **4,91 %** | 3,85 % | 11,0 % | 11,6 % | 0,57 | −0,07 | 2,96 % |
| W4 | 09‑11 | 4,97 % | 2,71 % | **6,29 %** | 4,97 % | 14,1 % | 11,2 % | 0,65 | −0,24 | 3,16 % |
| W5 | 09‑28 | 5,01 % | 2,21 % | **6,03 %** | 5,21 % | 13,5 % | 10,5 % | 0,76 | −0,20 | 3,01 % |
| W6 | 10‑02 | 4,80 % | 2,39 % | **5,95 %** | 5,21 % | 13,3 % | 9,7 % | 0,76 | −0,20 | 2,94 % |
| W7 | 10‑09 | 4,27 % | 2,30 % | **4,44 %** | 3,98 % | 9,9 % | 6,4 % | 0,29 | −0,15 | 2,74 % |
| W8 | 10‑16 | 2,06 % | 3,43 % | **2,25 %** | 2,24 % | 5,0 % | 2,9 % | 0,11 | +0,16 | 2,26 % |

Fakty:
- W4–W7 ex ante σ dzienna kapitału **4,4–6,3 %** (okno 60) / 4,0–5,2 % (okno 250); tygodniowa **9–14 %**. Przy takiej σ ruch −25 % w 4 tygodnie to ≈ 1 σ 4‑tygodniowej (6 %·√20 ≈ 27 %).
- Koszyk L/S **nie był neutralny**: σ przy ρ = 0 byłaby ~3 %, faktyczna 6 % — połowa zmienności to koncentracja czynnikowa (ρ par LONG 0,65–0,76 w W4–W6), a ujemna korelacja L‑S (−0,2) oznacza, że shorty defensywne (SBUX/PEP/CMCSA) poruszały się *przeciwnie* do longów półprzewodnikowych — czyli short nie hedżował, lecz dokładał ekspozycji na ten sam czynnik (SOX − defensywy).
- Kontrola modelu (`§2f`): ścieżka W1→W7 z równymi wagami 0,24, bez stopów i kosztów, od close D0 do close następnego D0: wynik −7,7 %, **max DD −29,3 %** (szczyt 2.10), σ_d zrealizowana 4,19 % — zgodna z ex ante. Rachunek pokazał −23,7 % od szczytu 6.10: mniej niż model, bo bot nie niósł pełnych 240 % (limit depozytowy, REDUCE, stopy, min. loty). W7: pięć ujemnych sesji po −6,1/−1,9/−7,6/−4,8/−6,4 %, suma −26,8 % = **−2,7 σ tygodniowej ex ante** — zdarzenie rzadkie (ok. 0,4 % przy normalności), ale przy ogonach akcji półprzewodnikowych raczej 1–2 %.
- W8 (GOOGL/GILD/MSFT/QCOM/ADP vs AXON/DASH/ALNY/APP/FER) ma σ_d 2,25 % — 2,7× mniej niż W4–W6 przy tym samym ALLOC. Stałe ALLOC znaczy, że ryzyko kapitału skacze 2–3× z tygodnia na tydzień zależnie od tego, co wybrała rutyna.

### 1b. Losowe koszyki 5/5 z uniwersum (1 000 losowań, okno 250, `§1b`)

| D0 | mediana σ_d kapitału | p10 | p90 | p99 | ρ par LONG (losowe) | σ koszyka faktycznego | **percentyl faktycznego** |
|---|---|---|---|---|---|---|---|
| 2026‑09‑11 (W4) | 2,25 % | 1,72 % | 3,46 % | 4,17 % | 0,11 | 4,97 % | **100** |
| 2026‑09‑28 (W5) | 2,23 % | 1,69 % | 3,45 % | 4,14 % | 0,11 | 5,21 % | **100** |
| 2026‑10‑02 (W6) | 2,32 % | 1,74 % | 3,47 % | 4,18 % | 0,12 | 5,27 % | **100** |
| 2026‑10‑09 (W7) | 2,27 % | 1,72 % | 3,46 % | 4,19 % | 0,11 | 3,97 % | 98 |
| 2026‑10‑16 (W8) | 2,32 % | 1,74 % | 3,43 % | 4,28 % | 0,11 | 2,23 % | 44 |

Fakt: **koszyki W4–W6 były bardziej zmienne niż 100 % losowych koszyków 5/5 z tego samego uniwersum**, W7 — niż 98 %. Metoda doboru (B1 momentum/rewizje, „sprzęt AI” po stronie long, defensywy po stronie short) systematycznie wybiera najbardziej zmienne i najbardziej skorelowane nazwy. Nie jest to pech, to własność selekcji. W8 jest pierwszym koszykiem o zmienności typowej dla uniwersum.

---

## 2. Rozkład drawdownu i P(kill switch) — zerowa alfa

### 2a. Stała alokacja, pula W1–W8 (σ jednostkowa 17,5 %/d; `§2a`)

| ALLOC/nogę | gross | σ_d kap. | 4 tyg.: DD mediana | DD p90 | DD p95 | DD p99 | P(kill) 4 tyg. | **P(kill) 12 tyg.** | P(kill) 12 tyg. ze startu −21 % | ze startu −23,7 % |
|---|---|---|---|---|---|---|---|---|---|---|
| **0,24 (obecne)** | 240 % | 4,21 % | −15,0 % | −26,3 % | −27,9 % | −30,9 % | **16,5 %** | **60 %** | 86 % | 93 % |
| 0,20 | 200 % | 3,51 % | −12,6 % | −24,4 % | −26,3 % | −29,3 % | 9,1 % | 46 % | 82 % | 91 % |
| 0,16 | 160 % | 2,81 % | −10,1 % | −19,9 % | −23,3 % | −26,8 % | 3,3 % | 28 % | 77 % | 89 % |
| 0,12 | 120 % | 2,10 % | −7,6 % | −15,2 % | −17,8 % | −22,6 % | 0,5 % | 11 % | 70 % | 86 % |
| 0,10 | 100 % | 1,75 % | −6,4 % | −12,8 % | −15,0 % | −19,2 % | 0,1 % | **4,9 %** | 65 % | 84 % |
| 0,08 | 80 % | 1,40 % | −5,1 % | −10,3 % | −12,2 % | −15,6 % | 0,0 % | **1,2 %** | 57 % | 81 % |
| 0,06 | 60 % | 1,05 % | −3,8 % | −7,8 % | −9,2 % | −11,9 % | 0,0 % | 0,1 % | 47 % | 77 % |

Pula tylko W4–W7 (σ jedn. 20,3 %/d, `§2b`): 0,24 → P(kill 12 t.) **70 %**, 4 tyg. 24 %; 0,12 → 18 %; 0,08 → 2,7 %; 0,06 → 0,2 %.
Proces „co tydzień losowy koszyk z uniwersum” (`§2c`, σ jedn. 8,2 %/d): 0,24 → 8,6 %; 0,12 → 0,1 %. Czyli przy *losowym* doborze obecny sizing byłby znośny; nieznośny czyni go selekcja z pkt 1b.

Wnioski (fakty z symulacji):
- Przy zerowej alfie i obecnych koszykach obecny sizing kończy się kill switchem w 12 tygodniach z prawdopodobieństwem 60–70 %; mediana czasu do kill wśród zabitych ścieżek = 31. sesja. To, co stało się 6–16.10 (−23,7 % w 8 sesji), to zdarzenie z okolic p90–p95 rozkładu 4‑tygodniowego DD — nie anomalia.
- Próg „< 5 % w 12 tygodniach” spełnia stałe **ALLOC ≤ 0,10** (4,9 %) na puli W1–W8, a na puli W4–W7 dopiero **≤ 0,08** (2,7 %). Rekomendacja robocza: 0,08 (σ_d ≈ 1,4–1,6 %).
- **Ze stanu bieżącego nic nie jest bezpieczne**: przy kapitale ≈ 1,7 % nad progiem każde ALLOC daje 50–90 % szans na kill w 12 tygodniach, bo próg jest 0,8 σ dziennej (0,24) albo 2,3 σ (0,08) poniżej. Patrz §5c.

### 2d. Skalowanie do celu σ kapitału (vol‑target na poziomie koszyka, `§2d`)

Metoda: co tydzień losowy koszyk z W1–W8 z własną 250‑sesyjną historią (wyśrodkowaną) i własną σ60 ex ante (z 60 sesji do D0, dostępną w sobotę); ALLOC_b = min(cap, cel/σ60_jedn.(b)).

σ60 jednostkowa per koszyk: W1 22,7 %, W2 16,8 %, W3 20,5 %, W4 26,4 %, W5 24,9 %, W6 24,7 %, W7 18,3 %, **W8 9,3 %**.

| cel σ_d | śr. ALLOC/nogę | zakres ALLOC W1…W8 | P(kill) 4 tyg. | **P(kill) 12 tyg.** | DD p95 4 tyg. | DD p95 12 tyg. | stały ALLOC o tej samej średniej → P(kill 12 t.) |
|---|---|---|---|---|---|---|---|
| 1,0 % | 0,054 | 0,038–0,108 | 0,0 % | **0,0 %** | −7,5 % | −12,8 % | 0,0 % |
| 1,5 % | 0,081 | 0,057–0,162 | 0,0 % | **0,5 %** | −11,1 % | −18,7 % | 1,3 % |
| 2,0 % | 0,108 | 0,076–0,216 | 0,0 % | **4,2 %** | −14,6 % | −24,2 % | 7,2 % |

ALLOC z celu 1,5 %/d per koszyk: W1 6,6 %, W2 8,9 %, W3 7,3 %, W4 5,7 %, W5 6,0 %, W6 6,1 %, W7 8,2 %, W8 16,2 %.

Fakt: vol‑target obniża P(kill) o ok. 40 % względem stałego ALLOC o tej samej średniej (0,5 % vs 1,3 %; 4,2 % vs 7,2 %), bo tnie ekspozycję właśnie wtedy, gdy rutyna wybrała koszyk „na 100. percentylu”. Cel 1,5 %/d daje średnie gross ~80 % i mieści się w kryterium < 5 %; cel 2,0 % jest na granicy.

### 2e. Wagi odwrotnie do σ nogi (inverse‑vol per noga, `§2e`) — wykonalne tylko przy większym rachunku

Przy celu 1,5 %/d i kowariancji 60 sesji wagi inverse‑vol wychodzą np. W7: MU 6,1 %, LITE 4,8 %, MRVL 6,0 %, PANW 7,5 %, CSCO 13,5 %, CMCSA 12,8 %, SBUX 22,0 %, PEP 23,7 %, TMUS 9,6 %, APP 7,5 % (gross 114 %); W4: MU 4,0 %, LITE 3,8 %, SBUX 16,9 % (gross 75 %). Problem praktyczny (`ryzyko_extra_out.md`, tabela lotów): przy kroku 0,1 akcji i kapitale rzędu `START_EQUITY` (1 000 USD) 0,1 MU = 88 USD, 0,1 LITE = 82 USD — waga 4–6 % (40–60 USD) jest **poniżej minimalnego lotu**; `calc_size` otworzy min. lot (przestrzał do 1,6× celu) albo pominie nogę. Inverse‑vol per noga na tej skali rachunku degeneruje się do „równych lotów”. Dlatego rekomendacja to **skalowanie gross całego koszyka** (jedna liczba ALLOC na tydzień) z równymi wagami, a inverse‑vol per noga dopiero od ok. 5 000 USD kapitału (wtedy 4 % = 200 USD > 0,1 akcji każdej spółki poza ASML/MELI).

Wykonalność lotów przy równych wagach (kursy 16.10, krok 0,1, kapitał 1 000 USD):

| ALLOC | cel/nogę | pomijane (0,1 akcji > 1,6 × cel) | min. lot z przestrzałem (cel; 1,6 cel] |
|---|---|---|---|
| 0,12 | 120 USD | — | ASML, MELI, MPWR, SNDK |
| 0,10 | 100 USD | ASML, MELI | MPWR, SNDK |
| 0,08 | 80 USD | ASML, MELI, SNDK | COST, LITE, MPWR, MU |
| 0,06 | 60 USD | ASML, COST, MELI, MPWR, SNDK | LITE, META, MU, REGN, STX |

Przy ALLOC 0,08 MU i LITE wchodzą jako min. lot (ok. 8,8 %/8,2 % kapitału zamiast 8 %) — akceptowalne; SNDK/ASML/MELI wypadają (SNDK przy σ_d 7 % i tak nie powinien wchodzić po 24 %). REDUCE 50 % przestaje działać dla MU/LITE/COST/META (cel 40 USD < min. lot) — argument, by zastąpić REDUCE per noga skalowaniem całego koszyka.

---

## 3. Twardy stop 10 % od wejścia na nogach o σ_d 4–6 %

Empirycznie z zamknięć (dolna granica — bot sprawdza `mid` w dwu biegach dziennie, intraday trafia częściej), okna 5 sesji od każdego dnia wejścia, `§3`:

| ticker | kier. | σ_d 250 | **P(stop 10 % w ≤ 5 ses.) 5 lat** | ost. 250 ses. | ost. 60 ses. | 10 % w σ_5 (stan 16.10) | śr. ruch po stopie do końca okna | „whipsaw” (na koniec okna strata < 10 %) | P(stop 15 %) | P(stop 20 %) |
|---|---|---|---|---|---|---|---|---|---|---|
| LITE | BUY | 6,24 % | **9,5 %** | 22,4 % | 26,7 % | 0,74 σ | +2,73 p.p. | 35 % | 3,9 % | 2,0 % |
| SNDK | BUY | 7,17 % | **18,3 %** (n = 416) | 24,0 % | 28,3 % | 0,67 σ | +0,60 p.p. | 33 % | 9,6 % | 5,5 % |
| MU | BUY | 5,13 % | **9,0 %** | 19,2 % | 16,7 % | 1,00 σ | +0,60 p.p. | 20 % | 3,4 % | 0,6 % |
| MRVL | BUY | 5,03 % | **10,9 %** | 14,8 % | 18,3 % | 0,92 σ | +0,13 p.p. | 24 % | 4,1 % | 1,5 % |
| AMD | BUY | 4,29 % | 8,6 % | 10,8 % | 11,7 % | | +0,30 p.p. | 19 % | 2,6 % | 0,6 % |
| TER | BUY | 4,87 % | 7,5 % | 16,4 % | 25,0 % | | +1,34 p.p. | 23 % | 2,7 % | 1,1 % |
| APP | SELL | 4,56 % | 20,6 % | 17,2 % | 0,0 % | | −0,62 p.p. | 21 % | 10,2 % | 5,3 % |
| PANW | BUY | 3,10 % | 4,3 % | 6,4 % | 8,3 % | | +1,15 p.p. | 30 % | 1,1 % | 0,4 % |
| CSCO | BUY | 2,22 % | 1,3 % | 2,0 % | 1,7 % | | +1,93 p.p. | 38 % | 0,2 % | 0,0 % |
| PEP | SELL | 1,32 % | 0,2 % | 1,2 % | 0,0 % | 3,6 σ | −0,30 p.p. | 0 % | 0,0 % | 0,0 % |
| CMCSA | SELL | 2,05 % | 0,6 % | 1,6 % | 3,3 % | 2,0 σ | +0,76 p.p. | 38 % | 0,0 % | 0,0 % |
| SBUX | SELL | 1,74 % | 1,5 % | 0,0 % | 0,0 % | | +0,92 p.p. | 21 % | 0,4 % | 0,4 % |

Symetria (stop na SHORT, ruch +10 % w 5 ses., 5 lat): LITE 17,5 %, SNDK 43,3 %, MU 16,0 %, MRVL 15,6 % — shortowanie tych nazw z 10 % stopem to rzut monetą.

Stop + ponowne otwarcie następnego dnia (tak robi bot, bo stop nie dodaje `exclude`) vs trzymaj, 5 lat, long: LITE −1,32 p.p./trafienie (≈ −6 p.p. nogi rocznie), MRVL −0,36, MU +0,35, SNDK +1,19. Znak zależy od nazwy, średnio ~0 — **stop nie ma przewagi**, kosztuje spread.

Fakty i interpretacja:
- Dla LITE/SNDK/MU/MRVL stop 10 % leży **0,67–1,0 σ 5‑sesyjnej** od wejścia; w ostatnim roku trafia w 15–24 % tygodni, w ostatnich 60 sesjach w 17–28 %. Dla PEP to 3,6 σ, dla CMCSA 2,0 σ. Ten sam procent to zupełnie inna reguła dla różnych nóg.
- Po trafieniu stopu średni ruch do końca okna jest **dodatni** (+0,1 do +2,7 p.p. nogi), tzn. w 5‑sesyjnym horyzoncie nie ma kontynuacji, którą stop miałby odcinać; 20–35 % trafień to „whipsaw” (na koniec okna strata mniejsza niż stop). Stop 10 % na tych nazwach realizuje szum, nie zmianę tezy — jest to zgodne z literaturą cytowaną w propozycji 3.1 (Kaminski‑Lo), ale tu policzone wprost na tych nogach.
- Stop nie chroni kapitału w sensie portfela: w W7 cztery stopy zadziałały (MU, LITE, MRVL, PANW), a bot i tak stracił −12 do −13 % kapitału na tych nogach, bo trzy z czterech otworzył ponownie (`wykonanie-bota.md`, cz. 1). Ochroną jest sizing, nie stop.

Hipoteza (nie dowód): stop w jednostkach σ (np. 2,0 × σ_5, czyli LITE ~27 %, MU ~20 %, CMCSA ~10 %, PEP ~5,5 %) z zakazem ponownego otwarcia w tej samej `version` byłby spójny między nogami; różnica wyniku in‑sample jest w szumie (cz. 2 `wykonanie-bota.md`: wszystkie warianty stopów W1–W7 w przedziale 9,8–10,9 % sumy). Przy ALLOC 0,08 strata 20 % na nodze = 1,6 % kapitału, czyli stop przestaje być krytyczny.

---

## 4. Korelacja między nogami long — weryfikacja tezy 3.1 „0,35 → 0,75”

| W | ρ60 LONG | ρ250 LONG | ρ60 SHORT | ρ60 L‑S | σ60 strony LONG (5 × 24 %) | gdyby ρ = 0 | N_eff LONG |
|---|---|---|---|---|---|---|---|
| W1 | 0,37 | 0,28 | 0,29 | −0,05 | 4,31 % | 2,68 % | 1,7 |
| W2 | 0,34 | 0,30 | 0,21 | −0,05 | 3,44 % | 2,25 % | 1,8 |
| W3 | 0,57 | 0,48 | 0,14 | −0,07 | 4,30 % | 2,43 % | 1,4 |
| W4 | 0,64 | 0,48 | 0,25 | −0,26 | 5,10 % | 2,73 % | 1,3 |
| W5 | **0,74** | 0,55 | 0,23 | −0,21 | 5,35 % | 2,71 % | 1,3 |
| W6 | **0,75** | 0,59 | 0,20 | −0,21 | 5,09 % | 2,57 % | 1,2 |
| W7 | 0,29 | 0,28 | 0,23 | −0,15 | 3,53 % | 2,35 % | 2,0 |
| W8 | 0,10 | 0,09 | 0,15 | +0,16 | 1,32 % | 1,15 % | 3,6 |

**Teza 3.1 potwierdzona**: ρ60 par LONG 0,34–0,37 (W1–W2) → 0,74–0,75 (W5–W6); na oknie 250 sesji 0,28 → 0,59. W7 spadła do 0,29 (CSCO, PANW), W8 do 0,10. N_eff = (Σσ)²/σ²_strony: strona long W5–W6 to **1,2–1,3 niezależnych zakładów** przy 120 % kapitału — jeden zakład „sprzęt AI” z dźwignią.

Wrażliwość teoretyczna (5 nóg po 24 %, σ_d nogi 4,5 %, jednakowa ρ): ρ 0 → 2,41 %; 0,35 → 3,74 % (×1,55); 0,50 → 4,18 %; 0,75 → 4,83 % (×2,00); 0,90 → 5,18 %. Przejście 0,35 → 0,75 podnosi σ strony long o **29 %** (3,74 → 4,83 %), a σ całego koszyka W6 (z ujemną ρ L‑S) o podobny rząd: 5,95 % vs 2,94 % przy niezależności.

Dwie uwagi do planu 3.1: (i) „limit bloków ρ ≤ 0,55” słusznie uznano za martwy jako bramkę selekcji — ale ρ działa doskonale jako *wejście do sizingu*: zamiast zakazywać koszyka, skaluje się jego gross (§2d robi to implicite przez σ60 jednostkową, która zawiera korelacje). (ii) Z ujemnej ρ L‑S wynika, że strona short *dodaje* ryzyka czynnikowego, więc „beta‑neutralność” liczona tylko do ^NDX nie wystarczy; miarą jest σ60 jednostkowa całego koszyka.

---

## 5. Propozycja: sizing, stopy, kill switch

### 5a. Porównanie polityk (mieszanka koszyków W1–W8, 12 tygodni, `§5`)

| polityka | śr. ALLOC | σ_d kap. | **P(kill 12 t.) alfa 0** | P(kill) ze startu −21 % | DD p95 12 t. | mediana wyniku 12 t., alfa +1 p.p./t | **alfa +2 p.p./t** | P(wynik > 0) przy +2 | mediana przy alfie −1 p.p./t |
|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0,24 stały (obecne) | 0,240 | 4,23 % | **60,7 %** | 87 % | −30,4 % | +2,9 % | +20,8 % | 68 % | −17,9 % |
| ALLOC 0,16 | 0,160 | 2,82 % | 28,7 % | 78 % | −27,8 % | +7,2 % | +18,2 % | 78 % | −12,6 % |
| ALLOC 0,12 | 0,120 | 2,12 % | 11,3 % | 70 % | −26,0 % | +6,1 % | +14,0 % | 81 % | −8,2 % |
| ALLOC 0,10 | 0,100 | 1,76 % | **4,9 %** | 65 % | −24,9 % | +5,3 % | +11,8 % | 81 % | −6,6 % |
| ALLOC 0,08 | 0,080 | 1,41 % | **1,2 %** | 58 % | −20,4 % | +4,3 % | +9,5 % | 82 % | −5,2 % |
| ALLOC 0,06 | 0,060 | 1,06 % | 0,1 % | 47 % | −15,6 % | +3,4 % | +7,1 % | 82 % | −3,8 % |
| ALLOC 0,12 + ×0,5 przy DD < −10 % | 0,120 | 2,12 % | 1,0 % | 47 % | −21,4 % | +3,6 % | +11,9 % | 76 % | −8,7 % |
| ALLOC 0,24 + ×0,5 przy DD < −10 % | 0,240 | 4,23 % | 33,9 % | 73 % | −27,2 % | +2,2 % | +15,7 % | 70 % | −14,2 % |
| vol‑target 1,0 %/d (cap 0,24) | 0,054 | 0,96 % | 0,0 % | 38 % | −12,8 % | +3,0 % | +6,4 % | 84 % | −3,4 % |
| **vol‑target 1,5 %/d (cap 0,12)** | 0,076 | 1,34 % | **0,3 %** | 53 % | −17,9 % | +4,2 % | **+9,0 %** | 83 % | −4,9 % |
| vol‑target 2,0 %/d (cap 0,12) | 0,096 | 1,70 % | 2,7 % | 63 % | −22,8 % | +5,1 % | +11,3 % | 82 % | −6,4 % |
| **vol‑target 1,5 %/d + ×0,5 przy DD < −10 %** | 0,081 | 1,43 % | **0,0 %** | **25 %** | −15,2 % | +4,2 % | +9,5 % | 82 % | −6,0 % |
| vol‑target 2,0 %/d + ×0,5 przy DD < −10 % | 0,108 | 1,91 % | 0,1 % | 38 % | −18,3 % | +4,5 % | +11,9 % | 79 % | −7,9 % |

Odczyt: mediana wyniku przy alfie +1 p.p./tyg jest **wyższa** przy ALLOC 0,10–0,16 niż przy 0,24 (+5–7 % vs +2,9 %), bo kill switch i geometria strat zjadają przewagę przy dużej dźwigni; przy +2 p.p./tyg 0,24 daje więcej (+21 %), ale z 60 % szansą ruiny przy zerowej alfie i 32 % szansą straty nawet przy alfie. Przy obecnej wiedzy o alfie (nieodróżnialna od zera) racjonalny jest sizing, który przy alfie 0 przeżywa, a przy +1…+2 p.p. zarabia 4–10 % na kwartał: **vol‑target 1,5 %/d, cap 0,12, floor 0,04**.

Kill switch stały vs kroczący (`§5b`, 52 tyg.): przy ALLOC 0,08 i alfie 0 kroczący 33 % vs stały 18 %; przy alfie +2 p.p. 2,9 % vs 0,6 %, mediany wyniku identyczne (+48 %). Kroczący jest surowszy, ale skoro alfa nie jest dowiedziona, surowość jest pożądana; **zostawić kroczący** i rozwiązać problem „co po trafieniu” (obecnie: nic — `app.py:1498` zamyka wszystko i każdy kolejny bieg kończy się na tym samym `if equity < prog_kill`, bo bez pozycji kapitał nie wraca nad próg; wznowienie wymaga ręcznej zmiany `equity_peak` albo `START_EQUITY`).

### 5b. Reguła do wdrożenia w `app.py` (zmienne środowiskowe + jedno pole w `signals.json`)

**Sizing (poziom koszyka, równe wagi):**

```
sigma60_unit  = odchylenie standardowe dziennych zwrotów (Σ 5 long − Σ 5 short), 60 sesji do D0
ALLOC_t       = clip(VOL_TARGET / sigma60_unit, ALLOC_MIN, ALLOC_MAX)
VOL_TARGET=0.015   ALLOC_MIN=0.04   ALLOC_MAX=0.12   (ALLOC_PCT w Renderze = 0.12 jako twardy sufit)
```

- Kto liczy: rutyna sobotnia, z zamknięć `scripts/kursy.py` (zakres 1y, 60 ostatnich sesji) lub TradingView `get-ohlcv` jako drugie źródło; różnica > 20 % między źródłami → adnotacja, bierzemy wyższą σ (surowszą). Zapis do `signals.json` jako nowe pole `sizing: {"sigma60_unit": 0.183, "alloc_pct": 0.082, "d0": "2026-10-09", "zrodlo": "yahoo"}`. Wymaga: (a) dopisania pola do allowlisty w `scripts/waliduj_signals.py --rutyna sobota` z kontrolą zakresu 0,04–0,12 i zgodności `alloc_pct` z formułą; (b) w `app.py` po `alloc = ALLOC_PCT if zgodne else ALLOC_PCT_SAFE` dodać `alloc = min(alloc, float(sig.get("sizing", {}).get("alloc_pct", alloc)))` — bot **nigdy nie przekracza** ALLOC_PCT z Rendera, pole może tylko obniżyć; brak/niepoprawne pole → `ALLOC_PCT_SAFE` (zmienić na 0,06). Prostszy wariant przejściowy bez zmiany pliku: właściciel wpisuje `ALLOC_PCT` w Renderze z tabeli raportu sobotniego (kolumna „ALLOC z celu 1,5 %”).
- Przeliczenie na historię (`ryzyko_extra_out.md`): ALLOC z celu 1,5 % = W1 6,6 %, W2 8,9 %, W3 7,3 %, W4 5,7 %, W5 6,0 %, W6 6,1 %, W7 8,2 %, **W8 16,0 % → cap 12 %**. Liniowy P&L W1–W7 przy faktycznych spreadach: −2,8 % kapitału (vs −4,4 % przy 0,24 liczonym tak samo; W7 −8,7 % zamiast −25 %, W4 +3,9 % zamiast +16,6 %). Reguła tnie zarówno straty, jak i zyski — to zamierzone: płacimy ~⅓ zysku W4 za przeżycie W7.
- Estymator σ: σ60, σ20 i EWMA(0,94) mają niemal tę samą moc prognostyczną 5‑sesyjnej σ realizowanej (korelacja log‑σ 0,60/0,60/0,61 na panelu 9 049 okien); wybór σ60 dla stabilności (mniej skoków ALLOC tydzień do tygodnia). Mediana realizowana/prognoza 0,83 — σ60 lekko zawyża, co jest po bezpiecznej stronie.
- Per‑noga inverse‑vol: **nie teraz** (§2e, loty). Zamiast tego twardy filtr selekcji: noga o σ60 > 2× mediany uniwersum (dziś ~6 % vs ~2,3 %: SNDK, LITE) wymaga uzasadnienia w raporcie — nie zakaz, adnotacja.

**Stopy:**

```
STOP_LOSS_SIGMA=2.0   STOP_LOSS_MIN=0.08   STOP_LOSS_MAX=0.20
stop_i = clip(STOP_LOSS_SIGMA × sigma60_i × √5, STOP_LOSS_MIN, STOP_LOSS_MAX)
```

σ60 nogi z tego samego sobotniego odczytu (pole `sizing.sigma60_nogi` lub tabela w raporcie); bez odczytu → dziś‑jak‑dziś 10 %. Po trafieniu stopu **brak ponownego otwarcia w tej samej `version`**: bot zapisuje `wykonanie.stopy[ticker] = version` i `desired_book` pomija nogę, dopóki `version` się nie zmieni (to pole już jest własnością bota, więc rutyny go nie dotykają). Dowód na poprawę wyniku: brak (różnice in‑sample w szumie); dowód na spójność i oszczędność spreadu: tak (§3).

**Kill switch — trzy progi, wszystkie od kroczącego szczytu:**

| próg DD od szczytu | działanie | zmienna |
|---|---|---|
| −10 % | ALLOC × 0,5 do czasu, gdy DD wróci nad −5 % (wyrównanie w biegu 17:05, jak REBALANCE) | `DD_SOFT=0.10`, `DD_SOFT_FACTOR=0.5`, `DD_SOFT_RESET=0.05` |
| −18 % | zamknij wszystko, płasko do najbliższej zmiany `version`; nowy koszyk startuje z ALLOC_MIN | `DD_FLAT=0.18` |
| −25 % (`KILL_LEVEL=0.75`) | jak dziś: zamknij, wstrzymaj. **Nowe:** wznowienie automatyczne po `KILL_COOLDOWN_WEEKS=4` zmianach `version`, z `equity_peak` przepisanym na bieżący kapitał i ALLOC_MIN przez kolejne 4 tygodnie; każde wznowienie liczone w `wykonanie.kill_count`, trzecie wymaga ręcznej zgody (zmienna `KILL_MANUAL_RESUME=true`) | `KILL_COOLDOWN_WEEKS`, `KILL_MANUAL_RESUME` |

Efekt policzony (§5a): vol‑target 1,5 % + próg −10 % → P(kill 12 t.) 0,0 % przy alfie 0, a ze startu −21 %: 25 % (vs 55 % bez progu i 87 % dziś). Mediana wyniku przy alfie +2 p.p.: +9,5 % na 12 tygodni (bez progu +9,6 % — próg prawie nic nie kosztuje). Progu −18 % nie symulowałem osobno (działa między −10 % i −25 %, wynik mieści się między wierszami tabeli).

### 5c. Stan bieżący (kapitał ≈ 1,7 % nad progiem, koszyk W8 σ_d 2,22 %/d przy 0,24)

| ALLOC | σ_d kap. | P(kill w 5 ses.) | w 10 ses. | w 20 ses. | odległość do progu |
|---|---|---|---|---|---|
| 0,24 | 2,22 % | **53 %** | 65 % | 76 % | 0,8 σ |
| 0,12 | 1,11 % | 31 % | 47 % | 62 % | 1,5 σ |
| 0,08 | 0,74 % | 18 % | 33 % | 49 % | 2,3 σ |
| 0,06 | 0,56 % | 12 % | 25 % | 40 % | 3,0 σ |

Odrobienie −23,7 % wymaga +31 %; przy alfie +2 p.p./tyg (niedowiedzionej) to 11 tygodni przy 0,24 albo 34 tygodnie przy 0,08 — bez szumu. Decyzja należy do właściciela i jest binarna: albo (A) świadomie pozwolić, by kill switch zadziałał / uznać, że zadziałał — przepisać `equity_peak` na bieżący kapitał (commit ręczny, pole bota), wdrożyć sizing z §5b i startować z ALLOC_MIN; albo (B) grać dalej na 0,24 z 53 % szansą zamknięcia wszystkiego w tym tygodniu przez ruch 0,8 σ. Wariant „zmniejszyć do 0,08 i czekać ≈ 1,7 % nad progiem” jest gorszy od (A): to samo ryzyko kill (49 % w 4 tygodnie) bez zdolności odrabiania.

---

## Czego nie da się stwierdzić (n = 7)

1. Czy istnieje alfa. Śr. spread W1–W7 −0,52 p.p. (sd ≈ 11), W1–W6 +2,91 p.p. (t ≈ 0,97). Przy sd 11 p.p./tydz. potrzeba ~50 tygodni, by odróżnić +1,5 p.p. od zera na poziomie t = 2. Sizing z §5b daje te 50 tygodni szansę się wydarzyć (P(kill 52 t.) przy alfie 0 i ALLOC ~0,08: 33 % kroczący) — przy 0,24 jest to 99 %.
2. Czy stop w jednostkach σ poprawia wynik (wszystkie warianty in‑sample w przedziale ±1 p.p. kapitału). Pewne jest tylko, że 10 % na LITE/SNDK to 0,7 σ i trafia co 4–5 tygodni bez związku z tezą.
3. Czy vol‑target zjada alfę momentum (Cederburg i in. 2020 ostrzegają dla per‑noga; dla poziomu portfela Moreira‑Muir 2017 pokazują poprawę Sharpe’a). Tu mamy jeden tydzień W4 jako „koszt” (+3,9 % zamiast +16,6 %) i jeden W7 jako „zysk” (−8,7 % zamiast −25 %); to anegdota, nie test.
4. Rozkład ogonów: bootstrap z 250 sesji historii nóg zawiera 2025–2026, ale nie zawiera krachu rzędu 2022 dla półprzewodników w tym składzie; P(kill) niżej traktować jako dolne oszacowanie dla koszyków typu W4–W6.
5. Zrealizowane −23,7 % vs model −29,3 %: różnica to realna, niższa od deklarowanej ekspozycja bota (limit depozytowy, min. loty, REDUCE, stopy) — nie policzyłem jej dokładnie, bo liczby z rachunku nie trafiają do notatki; `kontrola_kapitalu`/`limit_depozytowy` z `/run` są właściwym źródłem.
