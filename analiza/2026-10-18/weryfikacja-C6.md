# Weryfikacja twierdzenia C6 — reguła „przegrana noga bez odzyskanej siły relatywnej = poza koszykiem"

**Twierdzenie C6:** „Reguła «przegrana noga bez odzyskanej siły relatywnej = poza koszykiem» (W3→W8) nie ma poparcia przekrojowego (przegrane bez odzyskania w top-kwintylu momentum: +0,66 p.p./tydz., n=1108, vs odzyskane +0,32, wygrane +0,59; t<0,5) i in-sample kosztowała (zamienniki gorsze o 0,84 p.p./nogę); analogicznie filtr siły relatywnej dla kandydatów spoza koszyka (W8) i sito Perf.W ≤ −8%."

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Część przekrojowa wytrzymała każdą próbę obalenia i jest w istocie **za słabo** sformułowana: w zbiorach kandydatów bliskich koszykowi (TOP5/TOP10 momentum 6M) nogi, które reguła wyrzuca, są **najlepszym** koszem (TOP5: +2,0 p.p./tydz. vs reszta koszyka, Δ +1,68, t 2,16), a symulacja portfela TOP5/BOTTOM5 z regułą traci −0,37 p.p./tydz. (t −1,61; P(reguła pomaga) = 5%), na uniwersum z 28 spółkami usuniętymi z NDX −0,70 (t −2,73). Żadna z 148 odmian definicji/warunków nie pokazała, że reguła pomaga z |t| ≥ 1,65; 24 pokazały, że kosztuje. Zastrzeżenia: (1) **in-sample „0,84 p.p./nogę" nie jest dowodem kosztu** — to średnia z 9 zamian, w której jedna (LITE W5: −18,09) przeważa; mediana +2,05, zamiennik lepszy w 6/9, bez LITE W5 średnia +1,32 — in-sample jest **nierozstrzygalne**, nie „kosztowało"; (2) sito Perf.W ≤ −8% jest „analogiczne" tylko po stronie LONG; po stronie SHORT (pierwotny sens D2: nie shortuj po kolapsie) działa kierunkowo w dobrą stronę (Δ −0,5, t −1,3) i nie wolno go uchylać w jednym pakiecie; (3) w holdoucie od 2025-07 w top-kwintylu reguła miała marginalną wartość (Δ −1,02, t −1,6), ale nie w TOP5/TOP10 ani w symulacji — szum przy 148 testach.

Skrypty i wyniki (katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`): `weryfikacja_C6.py` → `weryfikacja_C6_out.md`, `weryfikacja_C6_wyniki.json`, `weryfikacja_C6_sim_A.csv`; `weryfikacja_C6_dod.py` → `weryfikacja_C6_dod_out.md`, `weryfikacja_C6_dod_wyniki.json`; `weryfikacja_C6_surv.py` → `weryfikacja_C6_surv_out.md`, `weryfikacja_C6_surv_wyniki.json`. Dane: `../dane/closes_5y.csv` (103 spółki, skład dzisiejszy), `../dane/dropped_closes.csv` (28 spółek usuniętych z NDX, wciąż notowanych), `audyt_regul_wykluczenia.csv` (in-sample W1–W7). Bez liczb z rachunku.

---

## 0. Co dokładnie testuję i jak (definicje)

Reguła z raportów W4–W8 (`reports/raport-2026-W6.html`, `-W7`, `-W8`): noga koszyka, której zwrot relatywny w tygodniu rozliczanym < 0 („przegrana"), zostaje poza koszykiem, dopóki nie pokaże **jednej sesji ze zwrotem relatywnym > 0** („odzyskana siła"); w W8 rozszerzona na kandydatów spoza koszyka (SNDK/STX/AVGO/AMAT/KLAC/FTNT poza TOP5 przy Perf.W −15…−21% i ostatniej sesji rel < 0) oraz jako sito Perf.W ≤ −8% w B1 pkt 5 (`rutyny/tygodniowa.md:48`).

Test przekrojowy (`weryfikacja_C6.py`): 230 tygodni kalendarzowych 2022-04-29…2026-09-18 (D0 = ostatnia sesja tygodnia, jak sobotnia rutyna; audyt używał okien co 5 sesji od stałej kotwicy), 22 075 obserwacji spółka-tydzień. Kandydaci LONG = top kwintyl momentum 6M relatywnego (jak audyt) **oraz** TOP10 i TOP5 (bliżej koszyka 5 nóg); SHORT = dolny kwintyl / BOTTOM10 symetrycznie (zysk shortu = −rel). Miary: (a) średni zwrot relatywny forward 1/2/4 tyg. grupy „przegrane bez odzyskania" vs „odzyskane" vs „wygrane" (t klastrowany po tygodniach); (b) **Δ = wykluczone − reszta kandydatów**, liczone tydzień po tygodniu (to jest właściwy koszt reguły: dodatnia Δ = reguła wyrzuca nogi lepsze od tych, które zostają), z t klastrowanym i CI90 bootstrapowym po tygodniach. Definicje „odzyskania": A ostatnia sesja rel > 0 (brzmienie reguły), B ≥ 2 z 3 ostatnich sesji rel > 0, C łączne 3 sesje rel > 0, D dwutygodniowa (przegrana w t−2, odzyskanie = cały tydzień t−1 rel > 0 — praktyka LITE W2→W3). Progi „przegranej": 0 / −2 / −4 / −8 p.p.

Symulacja portfela: co tydzień TOP5 LONG / BOTTOM5 SHORT z rankingu momentum 6M, równoważone; wariant z regułą: nogi z poprzedniego koszyka, które przegrały i nie odzyskały, poza koszykiem (z pamięcią: wracają po odzyskaniu), zamiennik = następna w rankingu. Mierzę Δ spread (reguła − bez), zmiany nóg/tydz., po latach i warunkowo.

## 1. Przekrój — próba obalenia definicjami i progami (LONG)

`weryfikacja_C6_out.md`, tabele „Top kwintyl / TOP10 / TOP5 … LONG, horyzont fwd1", Δ = wykluczone − reszta kandydatów, p.p./tydz.:

| kandydaci | przegrana < 0, def. A | < −2, def. A | < −4, def. A | < −8, def. A | najlepszy wynik DLA reguły (wszystkie 12 kombinacji) |
|---|---|---|---|---|---|
| top kwintyl (n wykl. 1130 / 707 / 406 / 164) | −0,16 (t −0,53) | +0,27 (t 0,69) | +0,46 (t 0,88) | +0,78 (t 1,09) | −0,16 (t −0,53), próg 0 def. A |
| TOP10 (537 / 352 / 230 / 107) | +0,19 (t 0,40) | +0,81 (t 1,42) | **+1,61 (t 2,13)** | **+2,46 (t 2,68)** | +0,07 (t 0,15), próg 0 def. C |
| TOP5 (240 / 174 / 122 / 65) | **+1,68 (t 2,16)** | **+2,64 (t 2,90)** | **+2,60 (t 2,21)** | **+3,20 (t 2,37)** | +0,73 (t 1,01), próg 0 def. C |

- Liczby C6 odtwarzają się (top kwintyl, def. A, próg 0): wykluczone **+0,60** (n=1130, t 1,2), odzyskane **+0,32** (n=649), wygrane **+0,63** — C6 podaje +0,66 / +0,32 / +0,59 z tekstu audytu; `audyt_regul_wyniki.json` ma +0,80 / +0,38 / +0,51 (n=1130). Rozstrzał to kotwica okna (5 przesunięć okien 5-sesyjnych: wykluczone +0,65…+1,12, Δ −0,15…+0,48, żadne t > 1,5 — `weryfikacja_C6_out.md` „Zależność od kotwicy"). Istota bez zmian: przegrane bez odzyskania **nie są gorsze** od odzyskanych ani wygranych.
- Im bliżej koszyka (TOP10, TOP5) i im większa przegrana, tym bardziej reguła wyrzuca najlepsze nogi: w TOP5 przegrane bez odzyskania zarabiają +2,0…+3,2 p.p./tydz. (t 2,6–3,6) wobec +1,1 dla wygranych. To wewnątrzkoszykowe odwrócenie tygodniowe wśród liderów 6M — spójne z `bt_odwrocenie.md` (po dużych tygodniach sygnał odwraca się) i `mp_ic_czynniki_out.md` (odwrócenie 1T IC ≈ 0 w całym przekroju, ale nie w ogonie rankingu).
- Definicje B/C (łagodniejsze kryterium odzyskania) i D (dwutygodniowa) nic nie zmieniają: top kwintyl Δ −0,32…+0,75, wszystkie |t| < 1,5; TOP5 Δ +0,73…+2,24 (t 1,0–2,6). Horyzont 2 i 4 tyg. (top kwintyl): Δ −0,23…+1,92, wszystkie |t| < 1,2 — nogi „poza koszykiem do odzyskania" nie tracą także w 2–4 tyg.

## 2. SHORT symetrycznie

`weryfikacja_C6_out.md` „Dolny kwintyl / BOTTOM10 — SHORT". „Przegrana shortu" = spółka rel > próg; „odzyskana słabość" = ostatnia sesja rel < 0.

- Dolny kwintyl, próg 0, def. A: wykluczone shorty +0,04 p.p. zysku/tydz. (n=1114) vs odzyskane −0,26 vs wygrane −0,09; Δ −0,18 (t −0,54). Jedyne miejsce, gdzie reguła kierunkowo pomaga: próg +2 z def. B/C, Δ −0,54/−0,56 (t −1,39/−1,57, CI90 obejmuje 0).
- Próg +8 (short po skoku spółki o 8 p.p. ponad indeks bez odzyskanej słabości) — reguła **kosztuje**: wykluczone shorty +0,86 (dolny kwintyl, Δ +1,21, t 1,87) / +1,96 (BOTTOM10, Δ +2,27, t 2,52); odzyskane −1,48 / −2,81. Zamknięcie shortu po skoku to oddanie zysku z późniejszego zgaśnięcia skoku.
- Symulacja tylko SHORT: Δ −0,04 p.p./tydz. (t −0,30) — neutralna. Dla shortów reguła ani nie chroni, ani nie boli; cały koszt siedzi po stronie LONG.

## 3. Warunkowo — czy reguła działa „po krachu" (kontynuacja)? Nie: działa odwrotnie

`weryfikacja_C6_out.md` „Warunkowo", top kwintyl, def. A, próg 0, Δ = wykluczone − reszta:

| warunek | n tyg. | wykluczone śr | reszta śr | Δ / t / CI90 |
|---|---|---|---|---|
| wszystkie | 230 | +0,60 | +0,57 | −0,16 / −0,53 / [−0,66; +0,35] |
| ^NDX tydzień < −3% | 32 | **+1,29** | −0,13 | **+1,40** / 1,21 / [−0,33; +3,35] |
| ^NDX tydzień < −2% | 51 | +0,67 | +0,04 | +0,81 / 0,97 |
| ^SOX−^NDX < −3 p.p. (jak W6/W7) | 21 | **+2,02** | −0,72 | **+2,92** / 1,76 / [+0,48; +5,68] |
| ^NDX w [−3%; +3%] | 158 | +0,36 | +0,72 | −0,47 / −1,34 / [−1,05; +0,09] |
| spółka r10 ≤ −12% | 79 | +2,56 | −0,60 | +2,28 / 1,03 |
| spółka Perf.W ≤ −8% | 96 | +1,75 | +0,74 | +0,83 / 0,44 |

- Po tygodniu ^NDX < −3% przegrane nogi bez odzyskania zarabiają +1,29 p.p./tydz. (hit 56%), wygrane −0,28 (hit 43%); indeks w następnym tygodniu średnio +1,56%, dodatni w 62,5% (n=32) (`weryfikacja_C6_dod_out.md` §F). To **odbicie, nie kontynuacja**. Po tygodniu SOX−NDX < −3 p.p. (dokładnie sytuacja W6/W7→W8) Δ +2,92 (t 1,76, CI90 nie obejmuje 0): reguła wyrzuca wtedy najlepsze nogi następnego tygodnia. Symulacja portfela potwierdza: w tygodniach ^NDX < −3% Δ spread −1,00 (t −1,35; 131 spółek: −1,92, t −2,55), po SOX−NDX < −3 p.p. −2,17 (t −1,91; 131 spółek: −3,62, t −3,04).
- Jedyny reżim, w którym reguła kierunkowo pomaga: spokojne tygodnie |^NDX| ≤ 3% (Δ −0,47, t −1,34) — przeciwnie do hipotezy „kontynuacja po krachu" i nieistotnie.
- Przy przegranej < −4 / < −8 i ^NDX < −3%: Δ +0,62 (t 0,57) / −0,46 (t −0,27, n=35) — szum.

## 4. Podokresy i holdout — najmocniejszy punkt NA RZECZ reguły

`weryfikacja_C6_out.md` „Warunkowo" (lata) i `weryfikacja_C6_dod_out.md` §A:

| zbiór | okres | Δ wykl.−reszta (def. A, próg 0) | próg −4 |
|---|---|---|---|
| top kwintyl | 2022 / 2023 / 2024 / 2025 / 2026 | +0,28 / −0,53 / +0,92 / −0,52 / −0,99 (wszystkie |t| ≤ 1,3) | — |
| top kwintyl | in-sample < 2025-07 (166 tyg.) | +0,18 (t 0,51) | +1,21 (t 1,88) |
| top kwintyl | **holdout ≥ 2025-07 (64 tyg.)** | **−1,02 (t −1,60, CI90 [−2,04; 0,00], hit 36,5% tyg.)** | −1,22 (t −1,45) |
| TOP10 | holdout | −0,13 (t −0,12) | +1,40 (t 0,89) |
| TOP5 | holdout | +0,75 (t 0,44) | +3,43 (t 1,25) |
| TOP15 | holdout | −0,59 (t −0,73) | −1,37 (t −1,31) |
| symulacja TOP5/BOTTOM5 | holdout | Δ spread −0,17 (t −0,37); 131 spółek: −0,74 (t −1,44) | −0,05 (t −0,11); 131 spółek: −0,71 (t −1,95) |

W ostatnich 64 tygodniach w szerokim top-kwintylu wykluczane nogi były o ~1 p.p./tydz. gorsze od reszty — to realny ślad na rzecz reguły, ale: znika w TOP5/TOP10 (tam, gdzie reguła faktycznie działa — koszyk ma 5 nóg), znika w symulacji portfela, ma CI90 dotykające zera i jest jednym z 148 testów (§6). Nie spełnia progu z `perspektywa-quant.md` (|t| ≥ 2, ten sam znak w ≥ 4/5 lat: tu 2/5 lat ujemne).

## 5. Symulacja portfela — koszt reguły w p.p./tydz.

`weryfikacja_C6_out.md` „Symulacja portfela" (103 spółki) i `weryfikacja_C6_surv_out.md` (131 spółek):

| wariant | spread bez reguły | z regułą | Δ (reguła − bez) | t | zmiany nóg/tydz. |
|---|---|---|---|---|---|
| obie strony, def. A, próg 0 (z pamięcią) | 1,10 (Sharpe 1,05) | 0,73 (0,74) | **−0,37** | −1,61 | 3,57 → 4,46 |
| def. B / def. C | 1,10 | 0,73 / 0,77 | −0,38 / −0,33 | −1,63 / −1,46 | → 4,87 / 5,14 |
| próg −2 / −4 / −8 | 1,10 | 0,82 / 0,89 / 1,05 | −0,29 / −0,22 / −0,06 | −1,38 / −1,17 / −0,41 | → 3,75 / 3,21 / 2,62 |
| tylko LONG / tylko SHORT | 1,10 | 0,78 / 1,06 | −0,33 / −0,04 | −1,87 / −0,30 | |
| bez pamięci (1 tydzień poza) | 1,10 | 0,66 | −0,45 | −2,62 | → 4,39 |
| + filtr W8 dla kandydatów | 1,10 | 0,79 | −0,31 | −1,34 | |
| horyzont 2 tyg. | 2,21 | 1,59 | −0,62 | −2,07 (LONG −0,82, t −3,71) | |
| koszyk 10/10 | 0,71 | 0,51 | −0,20 | −1,25 | 7,14 → 8,75 |
| ranking 6M z pominięciem 1M (mom6s), próg 0 / −4 | 0,95 | 0,71 / 0,66 | −0,24 / −0,29 | −1,05 / −1,48 | |
| **131 spółek (survivorship), próg 0 / −4** | 1,60 | 0,90 / 1,13 | **−0,70 / −0,47** | **−2,73 / −2,49** | 3,56 → 4,42 |

- Bootstrap tygodniowy (def. A, próg 0, 103 spółki; `weryfikacja_C6_dod_out.md` §C): Δ spread CI90 [−0,75; 0,00], **P(reguła pomaga) = 5,0%**; Δ LONG CI90 [−0,62; −0,04], P = 3,1%. Skumulowany koszt 2022-04…2026-09: −85 p.p. sumy tygodniowych spreadów (−16 p.p. w 2026 YTD). Reguła podnosi obrót o 0,9 nogi/tydz. (3,6 → 4,5) — koszt wykonania nieuwzględniony, działa w tę samą stronę.
- Po latach Δ ujemna w 5/5 lat (def. A, próg 0): −0,98 / −0,33 / −0,18 / −0,13 / −0,43 (131 spółek: −0,24 / −0,79 / −1,05 / −0,29 / −1,08). Żaden rok nie wyszedł na plus; jedyny dodatni rok to 2024 przy def. C (+0,11) i przy progu −4 (+0,09).
- Jedyny fragment, w którym symulacja z regułą była lepsza: 5 tygodni od W1 (21.08–18.09.2026) na koszykach momentum: +0,88 / +1,85 / +1,46 / +0,25 / 0,00 = +4,4 p.p. — n=5, to kontekst, w którym reguła powstała (LITE W1→W2). Reguła została dopisana po n=1–2 trafieniach.
- Survivorship: dodanie 28 spółek usuniętych z NDX (wciąż notowanych; nie obejmuje przejętych) **pogarsza** wynik reguły (Δ −0,37 → −0,70), bo spółki wypadające z indeksu to częste „przegrane bez odzyskania" w dolnym kwintylu, które reguła po stronie SHORT zamyka za wcześnie (SHORT Δ −0,17), a po stronie LONG przekrój TOP5 pozostaje +2,14 (t 2,47). Bias „skład dzisiejszy" nie ratuje reguły.

## 6. Kontrola wielokrotnych testów

`weryfikacja_C6_dod_out.md` §D: 148 wariantów przekrojowych (definicja × próg × zbiór × horyzont × warunek × strona). Δ < 0 (reguła pomaga kierunkowo) w 39, Δ > 0 w 109. **|t| ≥ 1,65: pomaga 0, kosztuje 24** (LONG: 122 wariantów, 0 vs 21). Najlepsze dla reguły: holdout top-kwintyl (t −1,6), SHORT próg +2 def. B/C (t −1,4/−1,6), spokojne tygodnie (t −1,3), sito r10 ≤ −12% po stronie SHORT (t −1,3). Przy 148 testach oczekiwane ~7 wyników |t| ≥ 1,65 przez przypadek w każdą stronę; 0 vs 24 to asymetria nie do pogodzenia z „reguła działa".

## 7. In-sample W2–W7: „zamienniki gorsze o 0,84 p.p./nogę" — liczba prawdziwa, wniosek nieuprawniony

`audyt_regul_wykluczenia.csv`, 10 wykluczeń (LITE W2/W3/W5, AVGO W5, MRVL W5, ALAB W6, TER/AMAT/AMD W7, NFLX W7), 9 z zamiennikiem:

| | wartość |
|---|---|
| Δ (zamiennik − wykluczona), średnia | −0,84 p.p. |
| **mediana** | **+2,05** |
| zamiennik lepszy od wykluczonej | **6 / 9** |
| średnia bez LITE W5 (+16,06 vs ALAB −2,03 = −18,09) | **+1,32** |
| wykluczona noga dodatnia | 3 / 10 (śr −1,74) |

Jedna obserwacja (LITE W5) odwraca znak średniej. W7 (TER/AMAT/AMD −13,8/−13,8/−7,6 vs zamienniki −11,8/−12,8/−3,8) to czynnik sektorowy, nie reguła — oba kosze straciły. In-sample przy n=9 nie mówi nic o koszcie reguły w żadną stronę; **ta część C6 jest nierozstrzygalna**, a nie „potwierdzona". Koszt reguły dowodzi przekrój (§5), nie in-sample.

## 8. Filtr W8 dla kandydatów spoza koszyka i sito Perf.W ≤ −8%

`weryfikacja_C6_out.md` „Sito Perf.W…", LONG, Δ = wykluczone − reszta kandydatów, fwd1:

| filtr | top kwintyl | TOP10 | TOP15 |
|---|---|---|---|
| Perf.W ≤ −8% (sito B1 pkt 5) | +0,89 (t 1,31; n 261) | **+2,14 (t 2,36; n 165)** | +1,04 (t 1,27) |
| Perf.W ≤ −8% i ostatnia sesja rel ≤ 0 (filtr W8) | +1,08 (t 1,40; n 198) | **+3,18 (t 3,02; n 124)** | +1,27 (t 1,35) |
| Perf.W ≤ −15% i ostatnia sesja ≤ 0 (jak SNDK/STX/AMAT W8) | −0,83 (t −0,54; n 38) | −0,39 (t −0,23; n 30) | −1,00 (t −0,62; n 35) |
| 131 spółek, Perf.W ≤ −8% | +0,74 (t 1,34) | +1,33 (t 1,67) | — |

- Sito Perf.W ≤ −8% i filtr W8 po stronie LONG wyrzucają kandydatów lepszych od reszty (TOP10: +2,1…+3,2 p.p./tydz., t 2,4–3,0; 2 tyg.: +1,5…+2,6). „Analogicznie" z C6 jest trafne.
- Wersja skrajna, taka jak decyzja W8 (Perf.W ≤ −15%): n=35 w 26 tygodniach, fwd1 śr −0,19 (mediana +1,82, hit 60%), fwd2 +0,33, fwd4 +1,18, wobec reszty TOP15 w tych samych tygodniach +1,28 / +2,51 (`weryfikacja_C6_dod_out.md` §E). Lista pokazuje, skąd ujemna średnia: klaster 26.06.2026 (WDC/STX/ARM/NBIS: −8,8/−9,6/−6,4/−11,0), CRWV 7.11.2025 (−25,4), APP 21.02.2025 (−18,2); kontrprzykłady SNDK 6.03.2026 +26,5, LITE 6.03.2026 +12,5, ARM 19.04.2024 +12,9. Nierozstrzygalne (t −0,2…−0,6), a nie „poparte" — i prerejestrowany test D2-W8 rozstrzygnie jeden przypadek, nie regułę.
- **Strona SHORT sita (pierwotny sens D2: nie shortuj po kolapsie):** dolny kwintyl, Perf.W ≤ −8% → Δ −0,01 (t −0,01); r10 ≤ −12% → Δ −0,50 (t −1,32); `audyt_regul_wyniki.json`: short po r10 ≤ −20% w całym uniwersum −1,14 (t −2,03). To osobna reguła o przeciwnym (pomocnym) znaku i nie należy jej uchylać wraz z K10.

## 9. Najmocniejszy kontrargument i dlaczego nie wystarcza

W holdoucie ≥ 2025-07 (64 tyg.) w top-kwintylu nogi „przegrane bez odzyskania" były o 1,02 p.p./tydz. gorsze od reszty kandydatów (t −1,60, CI90 [−2,04; 0,00], reguła lepsza w 36,5% tygodni), a przy progu −4 o 1,22 (t −1,45); skrajny filtr W8 (Perf.W ≤ −15%) wykluczał nazwy o fwd1 −0,19 wobec +1,28 reszty (n=35). Gdyby reżim 2025-26 był trwale inny („momentum crashuje w tydzień i nie wraca"), reguła miałaby sens. Nie wystarcza, bo: (a) w TOP5/TOP10 — tam, gdzie reguła realnie działa — holdout daje +0,75 / −0,13 (t 0,44 / −0,12), a przy progu −4 +3,43 / +1,40; (b) symulacja portfela w holdoucie: −0,17 (t −0,37), na 131 spółkach −0,74 (t −1,44) — reguła nadal kosztuje; (c) 2026 YTD w symulacji −0,43 (131 spółek: −1,08); (d) 0 ze 148 testów przechodzi |t| ≥ 1,65 na korzyść reguły wobec 24 przeciw; (e) po tygodniach SOX−NDX < −3 p.p. (W6/W7) wykluczone nogi biją resztę o +2,92 (CI90 [+0,48; +5,68]) — dokładnie przeciwnie do zastosowania w W8.

## 10. Co zostaje z C6 po weryfikacji

- **Potwierdzone i wzmocnione:** brak poparcia przekrojowego. Właściwa miara to nie „+0,66 vs +0,32 vs +0,59, t<0,5" (to porównanie grup w szerokim kwintylu), lecz Δ wykluczone − reszta koszyka: w TOP5 **+1,68 p.p./tydz. (t 2,16)**, w TOP10 przy przegranej < −4 **+1,61 (t 2,13)**; symulacja portfela **−0,37 p.p./tydz. (t −1,61, P(pomaga) 5%)**, na 131 spółkach **−0,70 (t −2,73)**; 0/148 wariantów za regułą przy |t| ≥ 1,65 vs 24 przeciw; po krachu indeksu/SOX reguła kosztuje najwięcej (odbicie, nie kontynuacja).
- **Zastrzeżenie 1 (in-sample):** „zamienniki gorsze o 0,84 p.p./nogę" to średnia zdominowana przez LITE W5; mediana +2,05, 6/9 zamienników lepszych, bez LITE +1,32. In-sample jest nierozstrzygalne — nie wolno go cytować jako dowodu kosztu (ani zysku).
- **Zastrzeżenie 2 (sito Perf.W):** analogia zachodzi tylko dla LONG. Po stronie SHORT sito/D2 ma kierunkowo pomocny znak (Δ −0,5, t −1,3; r10 ≤ −20% t −2,0) i wymaga osobnego testu, nie uchylenia w pakiecie.
- **Zastrzeżenie 3 (holdout):** marginalny ślad w top-kwintylu od 2025-07 (t −1,6) nieobecny w TOP5/TOP10 i w symulacji; nie spełnia progów awansu reguły.

## 11. Implikacja projektowa

1. Uchylić od W9 regułę „przegrana bez odzyskanej siły relatywnej" we wszystkich wariantach po stronie LONG i SHORT (K10, K16 „bez wyjątku dla wyceny", K17 filtr kandydatów spoza koszyka, sito Perf.W ≤ −8% w B1 pkt 5 **po stronie LONG**) — niezależnie od wyniku D2-W8 (jeden przypadek nie waży wobec 230 tygodni). Przegrana noga w TOP5 momentum jest przekrojowo najlepszą nogą następnego tygodnia; reguła działa jak anty-momentum wewnątrz koszyka i podnosi obrót o ~0,9 nogi/tydz.
2. **Nie** uchylać w tym samym ruchu sita po stronie SHORT (D2: nie shortuj po spadku r10 ≤ −12/−20%) — przenieść je do KANDYDATÓW z własnym testem (n=423, t −1,7…−2,1 w audycie; tu t −1,3).
3. W stałej tabeli raportu „KOSZT REGUŁ" podawać medianę i listę przypadków obok średniej (jedna zamiana LITE W5 odwróciła znak średniej z 9 obserwacji); żadna reguła nie wchodzi po n < 30 zdarzeń i bez |t| ≥ 2 klastrowanego po tygodniach, z tym samym znakiem w ≥ 4/5 lat i w TOP5/TOP10 (nie tylko w kwintylu).
4. Jeśli właściciel chce zachować jakąkolwiek reakcję na przegraną nogę: dane wskazują wyłącznie na tygodnie spokojne (|^NDX| ≤ 3%, Δ −0,47, t −1,34, nieistotnie) — i wprost zakazują stosowania jej po tygodniu ^NDX < −3% lub SOX−NDX < −3 p.p., gdzie wykluczane nogi są najlepsze (+1,4 / +2,9 p.p. nad resztą). Lepiej: brak reguły.

## 12. Ograniczenia

- Zamknięcia bez korekty o dywidendy; survivorship skorygowany tylko częściowo (28 nazw usuniętych z NDX, bez przejętych — SGEN, ATVI itp., które jako cele wykupu raczej sprzyjały longom). Korekta pogorszyła wynik reguły, więc kierunek błędu nie ratuje C6.
- Koszyki symulacji to ranking momentum 6M, nie Model 3.0 (20 czynników, scoring uznaniowy); reguła w rutynie działa na innych nogach. Jedyne dane o tych nogach to in-sample n=10 (§7) — nierozstrzygalne.
- Zwroty D0→D0 (piątek→piątek), bez poślizgu wejścia poniedziałkowego 13:45 UTC i kosztów; obrót z reguły (+0,9 nogi/tydz.) zwiększyłby koszt reguły, nie zmniejszył.
- 148 wariantów to także moje własne „polowanie" — dlatego raportuję asymetrię 0 vs 24, nie pojedyncze t.
