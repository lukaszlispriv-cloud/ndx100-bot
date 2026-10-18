# Weryfikacja C7 — bramka reakcji Pulsu (REDUCE 4 %/CLOSE 8 %, druga sesja, blokada sektorowa)

**Twierdzenie C7:** bramka ma wartość oczekiwaną ≈ 0 (przekrój: po sygnale REDUCE reszta okna +0,08 p.p., n = 3442, t 0,03); po dniu ze spreadem koszyka ≤ −3 p.p. kolejne 3 sesje dają +1,43 p.p. (t 2,7) — cięcie po złym dniu ma ujemną wartość; in-sample W1–W7 symulacja protokołu +2,78 p.p. łącznie, wyłącznie z W7.

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Rdzeń (EV ≈ 0) przeżył próbę obalenia przez miary ogona, podział na reżimy, zmianę kotwicy (D0 → D+1) i interakcję ze stopem bota; bramka nie jest też skuteczną redukcją ogona (p5 lepsze o ≤ 0,7 p.p. na −10, maxDD w 4 z 5 wariantów gorsze, P(kill 12 tyg.) 32,6 % → 31,2 %). Trzy liczby twierdzenia są jednak zawyżone lub zależne od założeń: (1) „+1,43, t 2,7” mierzy odbicie wobec zera, a właściwy punkt odniesienia to bezwarunkowa suma 3 sesji koszyka +0,70 p.p. (t 3,8) — nadwyżka +0,5 p.p. ma t < 1, więc „ujemna wartość cięcia” jest kierunkowo prawdziwa, ale nieistotna (bezpośredni koszt protokołu po złym dniu −0,20 p.p./zdarzenie, t −1,55); (2) „+2,78 wyłącznie z W7” zależy od kotwicy D0 i cięcia na zamknięciu sesji sygnału — przy kotwicy D+1 (proxy fills) i cięciu dzień później Δ = +0,91 p.p., a zysk pochodzi z W6, nie z W7; (3) przekrój w ścisłej wersji reguły (CLOSE = 8 p.p. na dwóch sesjach) daje n = 3194, +0,16 p.p., t −0,28 — ten sam wniosek, inne liczby.

Skrypty: `weryfikacja_C7.py` (główny, 13 s), `weryfikacja_C7_dod.py` (kwartyle σ ex ante). Wyjścia: `weryfikacja_C7_out.md`, `weryfikacja_C7_wyniki.json`, `weryfikacja_C7_serie.csv` (232 tygodnie × warianty), `weryfikacja_C7_dzienne.csv` (1115 dni), `weryfikacja_C7_przekroj.csv` (3194 sygnałów), `weryfikacja_C7_dod_out.md`. Katalog: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`.

## 0. Konstrukcja testu

- Dane: `closes_5y.csv` (2021-10-18…2026-10-16, 1255 sesji, 102 spółki po usunięciu GOOG; skład dzisiejszy — survivorship bias). Zamknięcia bez korekty o dywidendy.
- Koszyk-proxy systemu: momentum 6M (126 sesji, bez ostatnich 5) TOP5/BOTTOM5 rel. do ^NDX, równe wagi, okna D0 = ostatnia sesja tygodnia ISO → następne D0; 232 okna 2022-04-29…2026-10-02 (jak `pq_quant.py`/`bt_momentum.py`). Zwrot nogi = r − r_NDX (long) / −(r − r_NDX) (short) w p.p.; spread = śr. L + śr. S (gross 2).
- Protokół (rutyny/dzienna.md KROK 2): REDUCE (waga 0,5), gdy ruch względny od kotwicy ≤ −4 p.p. na dwóch kolejnych zamknięciach I ruch bezwzględny ≤ −4 %; CLOSE (waga 0), gdy ≤ −8 p.p. na dwóch zamknięciach I abs ≤ −8 % („ścisły CLOSE”); wariant „jak audyt_regul” (CLOSE, gdy drugi dzień ≤ −8 po pierwszym ≤ −4) do odtworzenia +2,78. Cięcie: lag 0 = na zamknięciu sesji sygnału (≈ bieg bota 13:45 UTC dnia następnego bez luki otwarcia — optymistycznie), lag 1 = na zamknięciu sesji następnej (pesymistycznie). Prawda leży między.
- Kotwica: D0 (jak audyt; zwroty od piątkowego zamknięcia) albo D+1 (zamknięcie poniedziałku — proxy fills bota; okno D+1 → D5+1).
- Stop bota: −10 % abs od kotwicy na zamknięciu, płasko jedną sesję, ponowne otwarcie na zamknięciu następnej z nową kotwicą (także dla bramki — fills resetuje się po stopie).
- Kapitał przy ALLOC 0,24: dzienny zwrot = 1,2 × spread dzienny/100 (tożsamość z wykonanie-bota.md); kill = −25 % od kroczącego szczytu okna.
- Blokada sektorowa NIE jest symulowana (brak dziennej taksonomii; in-sample n = 2 o przeciwnych znakach wg audyt-regul.md) — ta część C7 pozostaje nieprzetestowana.

## 1. Test ogona: średnia vs p5/p1/min/maxDD (koszyki momentum, 232 tygodnie)

| wariant | śr. pp/tydz | σ | p5 | p1 | min | maxDD skum. | Δ śr. vs baza | t(Δ) | tyg. pomógł/zaszkodził | Δp5 | ΔmaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| od D0, baza | 1,09 | 7,25 | −10,63 | −18,52 | −25,83 | −49,8 | — | — | — | — | — |
| od D0, protokół lag 0 | 0,95 | 7,16 | −10,66 | −19,89 | −21,06 | −52,7 | −0,145 | −1,61 | 32 %/35 % | −0,03 | −2,9 |
| od D0, protokół lag 1 | 1,07 | 7,11 | −11,04 | −18,83 | −23,13 | −49,8 | −0,022 | −0,40 | 29 %/24 % | −0,41 | 0,0 |
| od D0, bez 2. sesji | 0,90 | 6,81 | −9,31 | −16,23 | −18,89 | −44,6 | −0,190 | −1,42 | 38 %/49 % | +1,32 | +5,1 |
| od D+1, baza | 1,13 | 7,66 | −10,27 | −17,30 | −18,76 | −53,5 | — | — | — | — | — |
| od D+1, protokół lag 0 | 1,07 | 7,52 | −9,80 | −15,68 | −19,66 | −61,5 | −0,055 | −0,80 | 31 %/38 % | +0,47 | −8,0 |
| od D+1, protokół lag 1 | 1,14 | 7,47 | −9,56 | −15,62 | −18,15 | −55,3 | +0,016 | +0,32 | 25 %/25 % | +0,71 | −1,8 |
| od D+1, stop 10 % + reopen (bot) | 1,01 | 7,73 | −10,30 | −16,78 | −20,00 | −60,1 | −0,122 | −1,77 | 46 %/52 % | −0,03 | −6,6 |
| od D+1, stop + reopen + protokół (vs stop) | 1,04 | 7,64 | −10,05 | −16,25 | −19,93 | −60,0 | +0,029 | +0,89 | 29 %/22 % | +0,25 | +0,1 |

Źródło: `weryfikacja_C7_out.md` §1. Reakcje (D+1, lag 0): 419 REDUCE + 173 CLOSE na 2320 nóg, 181/232 tygodni z ≥ 1 reakcją; stopy 10 %: 294.

- Średnia: Δ od −0,15 do +0,02 p.p./tydz. zależnie od kotwicy i lagu, |t| ≤ 1,6 → **EV ≈ 0 potwierdzone**, z lekkim ujemnym znakiem przy cięciu natychmiastowym od D0.
- Ogon: p5 poprawia się o 0…+0,7 p.p. (na poziomie −10), p1 o do +1,7; **min i maxDD nie poprawiają się systematycznie** (maxDD gorsze w 4 z 5 wariantów protokołu, do −8 p.p. skumulowanych). W 5 % najgorszych tygodni bazy (n = 12, śr. −14,53 p.p.) protokół daje −14,02 (lag 0) / −13,38 (lag 1): **odjęte 3–8 % straty ogona**. W 5 % najlepszych (śr. +20,17) koszt −0,44.
- Rozkład Δ jest symetryczny: Δ > +2 p.p. w 8 tygodniach, Δ < −2 p.p. w 9 (max +3,52 2026-05-08, min −5,92 2026-07-24) — `weryfikacja_C7_dod_out.md`.
- Na stopie bota (realny stan: stop czyta poziom brokera i strzela pierwszy) protokół dodaje +0,03 p.p./tydz. (t 0,89), p5 +0,25, maxDD 0 — **marginalnie nic**.

## 2. Szum (200 losowych koszyków 5/5 na tydzień, od D+1)

Baza śr. +0,008 → protokół +0,012 (lag 0; Δ +0,004, szkodzi w 47 % strategii) / +0,016 (lag 1); σ tyg. 3,52 → 3,43 (−2,6 %); p5 −5,47 → −5,24 (+0,22); maxDD skum. −60,4 → −58,3 (+2,1); pooled n = 46 400: p1 −9,17 → −8,62. Bramka na szumie to mechaniczna redukcja wariancji o 2–3 % przy zerowej średniej — zgodne z opisem „kontrola wariancji, EV ≈ 0”, ale skala jest kosmetyczna.

## 3. Reżimy: VIX > 25, lata, ruch indeksu (od D+1, lag 0)

| reżim | n | baza śr. | Δ śr. | t(Δ) | p5 baza → protokół | maxDD baza → protokół |
|---|---|---|---|---|---|---|
| VIX(D0) > 25 | 26 | +1,02 | −0,12 | −0,79 | −7,49 → −8,99 | −31,6 → −35,7 |
| VIX(D0) 20–25 | 47 | +3,11 | −0,12 | −1,06 | −7,64 → −7,08 | −37,0 → −38,6 |
| VIX(D0) ≤ 20 | 159 | +0,56 | −0,02 | −0,26 | −11,84 → −12,49 | −68,4 → −61,5 |
| 2022 | 36 | −0,06 | −0,23 | −1,58 | −8,46 → −9,65 | −53,5 → −56,5 |
| 2023 | 52 | +0,10 | −0,07 | −1,35 | −5,94 → −5,69 | −22,7 → −25,4 |
| 2024 | 52 | +1,55 | −0,05 | −0,36 | −6,42 → −6,83 | −31,0 → −28,4 |
| 2025 | 52 | +1,32 | +0,14 | +0,90 | −8,98 → −8,12 | −48,9 → −39,8 |
| 2026 | 40 | +2,75 | −0,13 | −0,52 | −16,84 → −14,75 | −49,4 → −61,5 |
| ^NDX w oknie ≤ −2 % | 50 | −1,06 | +0,09 | +0,57 | −13,54 → −13,52 | −87,7 → −81,7 |
| ^NDX w oknie ≥ +2 % | 64 | +2,07 | +0,09 | +0,79 | −8,59 → −9,47 | −64,2 → −68,1 |

**W reżimie VIX > 25 bramka NIE pomaga**: Δ −0,12 (t −0,79), p5 i maxDD gorsze. Jedyny rok z dodatnim Δ to 2025 (+0,14, t 0,9). W tygodniach spadku indeksu ≤ −2 % Δ +0,09 (t 0,57), min lepsze (−18,8 → −15,7). Żaden podzbiór nie ma |t| ≥ 2.

Kwartyle σ60 ex ante koszyka (`weryfikacja_C7_dod_out.md`; koszyki systemu W4–W7 ≈ 3,7–5,2 p.p./dz. spreadu = Q4): Q4 (σ60 4,07–7,31, σ tyg. zreal. 10,9 — jak system) Δ lag 0 −0,19 (t −1,09), lag 1 +0,17 (t +1,33); p5 −15,3 → −14,2/−13,9 (+1,1…+1,4 p.p., ≈ 8 %); maxDD −49,4 → −61,5 (lag 0) / −42,6 (lag 1). **Znak efektu w koszykach wysokiej σ zależy od tego, czy cięcie zdąży na zamknięcie sesji sygnału — a bot tnie dopiero 13:45 UTC dnia następnego.** Tygodnie z bazą ≤ −10 p.p. (n = 13, śr. −14,20): Δ +0,48 (pomógł w 62 %) / +1,11.

## 4. Kapitał przy ALLOC 0,24: P(kill −25 %) z/bez protokołu

| okna | n | P(kill) baza → protokół | DD p5 | mediana DD |
|---|---|---|---|---|
| 4 tyg. | 229 | 10,5 % → 9,6 % | −36,7 % → −33,6 % | −12,2 % → −11,1 % |
| 12 tyg. | 221 | 32,6 % → 31,2 % | −51,7 % → −52,9 % | −19,3 % → −17,6 % |
| 26 tyg. | 207 | 57,5 % → 56,5 % | −58,0 % → −60,4 % | −33,8 % → −32,8 % |

σ dzienna kapitału 4,29 % → 4,07 % (−5 %); najgorszy dzień bez zmian (−13,98 p.p. spreadu). Bramka obniża P(kill) o ~1 p.p. — wobec 32,6 % w kwartale to szum; sizing (ALLOC 0,12 → 5,8 %, bt_symulacja-wykonania.md) robi 25 p.p. Źródło: `weryfikacja_C7_out.md` §4.

## 5. Sygnał „dzień ≤ −3 p.p.” — stabilność, 2022, indeks, HAC

Seria dzienna spreadu koszyka momentum (od D+1, n = 1112 dni z 3-sesyjną kontynuacją).

| warunek | n (nienakł.) | śr. sumy 3 sesji | mediana | hit | t naiwne | t HAC(3) | nienakł. śr. (t) |
|---|---|---|---|---|---|---|---|
| **bezwarunkowo (punkt odniesienia)** | 1112 | **+0,70** | — | — | 3,82 | — | — |
| po dniu ≤ −3 | 168 (111) | +1,23 | +2,03 | 61 % | 2,16 | 1,92 | +0,88 (1,33) |
| po dniu ≥ +3 | 190 (111) | +0,66 | +0,63 | 54 % | 1,20 | 0,98 | +0,85 (1,24) |
| ≤ −3, bez 2022 | 137 (93) | +1,45 | +2,07 | 63 % | 2,36 | 2,07 | +1,05 (1,47) |
| ≤ −3, 2022 / 2023 / 2024 / 2025 / 2026 | 31/18/32/38/49 | +0,23 / +1,22 / +2,26 / +1,00 / +1,36 | | | 0,16 / 1,66 / 2,77 / 1,03 / 0,94 | 0,15 / 1,97 / 2,74 / 0,79 / 0,87 | |
| ≤ −3 i ^NDX tego dnia ≤ −2 % | 21 (19) | +3,38 | +3,06 | 67 % | 2,61 | 3,36 | +2,78 (2,05) |
| ≤ −3 i \|^NDX\| < 1 % (ruch własny koszyka) | 70 (58) | +1,86 | +2,04 | 67 % | 2,24 | 2,39 | +1,69 (1,93) |
| ≤ −3, VIX > 25 / ≤ 25 | 27 / 141 | +3,04 / +0,88 | | 67 % / 60 % | 1,84 / 1,47 | 1,71 / 1,30 | +2,88 (1,30) / +0,66 (0,96) |
| ≤ −5 | 68 (53) | +2,16 | +2,45 | 66 % | 2,18 | 2,29 | +1,00 (0,93) |
| dwie sesje o sumie ≤ −4 (analog 2. sesji) | 167 (93) | +1,85 | +2,15 | 63 % | 3,13 | 2,79 | +1,50 (1,96) |

Źródło: `weryfikacja_C7_out.md` §5. Wnioski:
- Liczba „+1,43 (t 2,7)” odtwarza się jako +1,23 (t naiwne 2,16; różnica: moja seria od D+1 i ffill 2) — ale **mierzona wobec zera, podczas gdy koszyk ma bezwarunkowy dryf +0,70 p.p./3 sesje (t 3,8)**. Nadwyżka odbicia +0,53 p.p. ma t ≈ 0,9; po usunięciu nakładania okien t 1,33; HAC(3) 1,92. Po dniu ≥ +3 suma wynosi +0,66 ≈ bezwarunkowa — asymetria istnieje, ale słaba.
- **Nie jest zdominowane przez 2022** — przeciwnie, 2022 jest najsłabsze (+0,23); znak dodatni we wszystkich 5 latach, istotny tylko w 2024 (t 2,7).
- **Nie jest artefaktem ruchu indeksu**: po dniach ≤ −3 przy |^NDX| < 1 % odbicie +1,86 (t HAC 2,4); ^NDX w kolejnych 3 sesjach +0,27 % (bezwar. +0,26 %); regresja sumy 3 sesji spreadu na ^NDX: β 0,39, stała +1,12 p.p. Silniejsze po dniach z dużym spadkiem indeksu (+3,38, n = 21) i przy VIX > 25 (+3,04, n = 27) — małe próby.
- **Bezpośredni koszt protokołu po złym dniu**: po dniach ≤ −3 kolejne 3 sesje bez reakcji +1,23 vs z wagami po reakcjach +1,03 → **−0,20 p.p./zdarzenie, t sparowane −1,55**. To jest właściwa liczba za zdanie „cięcie po złym dniu ma ujemną wartość”: kierunek ujemny, wielkość 0,2 p.p., nieistotne.
- Analog potwierdzenia drugą sesją (dwie sesje o sumie ≤ −4) wybiera momenty o najsilniejszym odbiciu (+1,85, HAC 2,8; nienakł. +1,50, t 1,96) — warunek drugiej sesji nie filtruje „kontynuacji”, bo jej w danych nie ma (autokorelacja lag1 −0,01 wg pq_quant).

## 6. Przekrój: pierwszy sygnał REDUCE → reszta okna (ścisła reguła, kotwica D0)

| podzbiór | n | okien | śr. reszta p.p. | t (klastr. po d0) | hit > 0 |
|---|---|---|---|---|---|
| wszystkie | 3194 | 232 | +0,16 | −0,28 | 51,8 % |
| long / short | 1479 / 1715 | | +0,34 / +0,02 | +1,00 / −0,25 | |
| poziom CLOSE (≤ −8 dwie sesje) / tylko REDUCE | 494 / 2700 | | +0,18 / +0,16 | −0,69 / −0,21 | |
| koszykowe (long top-kwintyl + short dolny kwintyl mom6M) | 834 | 209 | +0,45 | +0,54 | 53,6 % |
| VIX(sygnał) > 25 / 20–25 / ≤ 20 | 364 / 507 / 2323 | 36 / 58 / 177 | +0,22 / +0,35 / +0,11 | −0,09 / +0,41 / −0,42 | |
| VIX > 25, koszykowe | 83 | 28 | +0,63 | +0,76 | 53,0 % |
| 2022 / 2023 / 2024 / 2025 / 2026 | 432 / 441 / 546 / 748 / 1027 | | +0,06 / −0,05 / −0,53 / +0,12 / +0,70 | −0,06 / −0,47 / −1,49 / +0,80 / +0,78 | |
| sygnał w sesji 2 / 3 / 4 | 914 / 1167 / 1113 | | +0,27 / +0,37 / −0,13 | −1,04 / +0,10 / −1,04 | |
| ^NDX od D0 do sygnału ≤ −3 % | 207 | 25 | +1,04 | −0,32 | 52,7 % |

Rozkład reszty: p5 −7,65, p95 +8,07, σ 5,24, asymetria −0,27; na poziomie CLOSE p5 −11,64 / p95 +10,94 — symetryczny. Źródło: `weryfikacja_C7_out.md` §6. Liczby twierdzenia (n = 3442, +0,08, t 0,03; w bieżącym `audyt_regul_wyniki.json` n = 3447, −0,01, t −0,45) odtwarzają się co do wniosku: **żaden podzbiór (strona, poziom, VIX, rok, sesja sygnału, ruch indeksu) nie ma |t| ≥ 1,5; po sygnale nie ma ani kontynuacji, ani istotnego odbicia**. W VIX > 25 reszta jest dodatnia (+0,22; koszykowe +0,63) — cięcie nie pomaga także tam.

## 7. In-sample W1–W7: zależność od kotwicy i czasu cięcia

| tydzień | baza D0 | protokół D0 lag 0 (CLOSE jak audyt) | D0 lag 0 (ścisły CLOSE) | D0 lag 1 | baza D+1 | protokół D+1 lag 0 | D+1 lag 1 | D+1 bez 2. sesji |
|---|---|---|---|---|---|---|---|---|
| W1 | −4,04 | −4,04 | −4,04 | −4,04 | −3,02 | −3,02 | −3,02 | −3,59 |
| W2 | +6,28 | +6,28 | +6,28 | +6,28 | +6,77 | +6,77 | +6,77 | +6,77 |
| W3 | +1,43 | +1,43 | +1,43 | +1,43 | −7,42 | −7,42 | −7,42 | −7,20 |
| W4 | +14,36 | +11,23 | +11,23 | +13,83 | +27,14 | +27,14 | +27,14 | +27,14 |
| W5 | +6,08 | +6,08 | +6,08 | +6,08 | +5,68 | +5,68 | +5,68 | +5,32 |
| W6 | −5,57 | −5,21 | −5,39 | −5,67 | −8,66 | −7,49 | −7,75 | −7,64 |
| W7 | −22,36 | −16,81 | −17,75 | −19,71 | −17,25 | −15,57 | −17,25 | −14,56 |
| **SUMA** | −3,83 | −1,05 (**Δ +2,78**) | −2,17 (Δ +1,66) | −1,80 (Δ +2,03) | +3,26 | +6,09 (Δ +2,84) | +4,17 (**Δ +0,91**) | +6,24 (Δ +2,98) |

Źródło: `weryfikacja_C7_out.md` §7 (okno D+1 dla W7 = 12.10→16.10, brak D5+1 w danych). **+2,78 odtworzone co do setnej** (kotwica D0, lag 0, CLOSE jak audyt: W4 −3,13, W6 +0,36, W7 +5,55). Ale: ścisły CLOSE +1,66; cięcie dzień później +2,03; od D+1 (proxy fills) W4 nie generuje reakcji (kurs odjechał od poniedziałkowego wejścia inaczej niż od D0), a W7 daje tylko +1,68 (lag 0) / 0,00 (lag 1) — zysk przy D+1 lag 1 to **W6 +0,91, nie W7**. „Wyłącznie z W7” jest prawdą tylko dla kotwicy D0. Wariant bez drugiej sesji od D+1 jest LEPSZY (+2,98) niż z nią (+2,84) — przeciwnie niż od D0 (−4,76 wg audytu) — kolejny dowód, że 7 tygodni to szum.

## 8. Najmocniejszy kontrargument i odpowiedź

**Kontrargument:** bramka nie ma być źródłem wyniku, lecz ubezpieczeniem ogona przy dźwigni 2,4 i kill switchu ≈ 1,7 % pod kapitałem; w jedynym zdarzeniu z ogona (W7) odjęła 5,55 p.p. z −22,36 (25 %); koszyki systemu mają σ 11 p.p./tydz. (nie 7 jak proxy), więc test 5-letni może niedoszacować jej wartości; blokada sektorowa i wyzwalacze newsowe nie były symulowane.

**Odpowiedź z danych:** (a) w 12 najgorszych tygodniach 5 lat (śr. −14,5 p.p., porównywalne z W6/W7 proxy) protokół odjął 0,5–1,2 p.p. (3–8 %), a W7 przy kotwicy D+1 (jak rachunek) kurczy się do +1,68/0,00; (b) w kwartyle σ ex ante jak system (Q4, σ tyg. 10,9) p5 lepsze o 1,1–1,4 p.p. na −15,3, ale znak Δ średniej i maxDD zależy od tego, czy cięcie trafi na zamknięcie sesji sygnału (lag 0: maxDD −49 → −61; lag 1: −49 → −43) — bot tnie dopiero 13:45 UTC dnia następnego, a stop 10 % od poziomu brokera zwykle strzela wcześniej (1 z 8 wpisów Pulsu wykonany, audyt-regul.md); (c) P(kill 12 tyg.) 32,6 → 31,2 % przy ALLOC 0,24 — bramka nie zmienia losu systemu; (d) blokada sektorowa (n = 2) i wyzwalacze newsowe pozostają nieprzetestowane — ale ich zadaniem nie jest cenowe cięcie, więc nie ratują tezy o bramce 4/8. Kontrargument obniża pewność co do skali efektu ogona (0–8 % straty ogona), nie co do wniosku EV ≈ 0.

## 9. Twierdzenie po weryfikacji

Bramka cenowa Pulsu (REDUCE 4 %/CLOSE 8 % od ceny wejścia, druga sesja) ma wartość oczekiwaną ≈ 0: na 232 tygodniach koszyków momentum 6M Δ od −0,15 do +0,02 p.p./tydz. (|t| ≤ 1,6) zależnie od kotwicy (D0/D+1) i chwili cięcia; na 200 losowych koszykach Δ +0,004; przekrojowo po sygnale REDUCE reszta okna +0,16 p.p. (n = 3194, t −0,28), w VIX > 25 +0,22 (t −0,09). Nie jest też skuteczną redukcją ogona: p5 tygodnia lepsze o 0–0,7 p.p. (na −10), w 5 % najgorszych tygodni odjęte 0,5–1,2 p.p. z −14,5, maxDD gorsze w 4 z 5 wariantów, P(kill 12 tyg. przy ALLOC 0,24) 32,6 → 31,2 %, σ dzienna kapitału −5 %. Odbicie po dniu ≤ −3 p.p. (+1,23…+1,43 p.p./3 sesje) jest tylko o +0,5 p.p. wyższe od bezwarunkowego dryfu koszyka (+0,70, t 3,8) — t < 1 (HAC 1,9; nienakładające się 1,3); znak dodatni w 5/5 lat, 2022 najsłabsze, nie wynika z indeksu (β 0,39, stała +1,12). Bezpośredni koszt protokołu po złym dniu −0,20 p.p./zdarzenie (t −1,55): cięcie po złym dniu ma wartość ≈ 0, nie udowodnioną ujemną. In-sample W1–W7 Δ +2,78 odtworzone dokładnie, ale zależy od kotwicy D0 i cięcia na zamknięciu sesji sygnału: ścisły CLOSE +1,66, lag 1 +2,03, od D+1 (fills) +2,84/+0,91, z czego przy D+1 lag 1 całość z W6, nie z W7.

## 10. Implikacja projektowa

Nie opierać kontroli ryzyka na bramce 4/8 ani jej nie „naprawiać” — w każdej mierze (średnia, p5, maxDD, P(kill), σ) jest neutralna w granicach ±1 p.p., a jej realny efekt na rachunku jest jeszcze mniejszy, bo stop 10 % strzela pierwszy. Decyzja „usunąć czy zostawić” jest kosmetyczna; jeśli zostaje, opis w `rutyny/dzienna.md` KROK 2 ma brzmieć: „kontrola wariancji, EV ≈ 0 (±0,15 p.p./tydz.), efekt ogona ≤ 1 p.p. w 5 % najgorszych tygodni, nie zastępuje sizingu”, bez zdania o „ujemnej wartości cięcia po złym dniu” (nieudowodnione) i bez odwoływania się do +2,78 in-sample jako dowodu (zależne od kotwicy). Jedyną dźwignią ogona pozostaje sizing/vol-target (ALLOC 0,12 → P(kill 12 tyg.) 5,8 % wg bt_symulacja-wykonania.md vs 31–33 % tu). Rozliczać bramkę w KONTROLI BRAMKI od fills (D+1), nie od D0 — różnica zmienia znak wniosku o W4 i W7. Blokada sektorowa i wyzwalacze newsowe: brak testu, zostawić jako regułę zdarzeniową, nie cenową.

## 11. Zastrzeżenia

- Koszyk-proxy (momentum 6M) nie jest koszykiem Modelu 3.0; wyniki per-reguła (Δ) są mniej wrażliwe na to niż poziomy, ale koszyki systemu były bardziej skoncentrowane (ρ par 0,56–0,75) — kwartyl Q4 to najbliższe przybliżenie.
- Survivorship bias (skład dzisiejszy) zawyża dryf strony long (+0,70/3 sesje) i tym samym „odbicie”; dla różnic protokół–baza wpływ jest drugorzędny.
- Cięcie na zamknięciach (lag 0/1) zamiast o 13:45 UTC z luką otwarcia; stop na zamknięciach zamiast na mid 13:45/17:05; brak kosztów transakcyjnych reakcji (każdy REDUCE/CLOSE to spread CFD — pogarsza protokół o ~0,1–0,3 % nominału nogi).
- Test „dzień ≤ −3” liczy nakładające się 3-sesyjne sumy; podane t HAC(3) i wersja nienakładająca się. n w podgrupach (VIX > 25: 27, ^NDX ≤ −2 %: 21) za małe na wnioski.
- Blokada sektorowa i wyzwalacze newsowe/rekomendacyjne nie symulowane. Bez liczb z rachunku — wyłącznie p.p. i %.
