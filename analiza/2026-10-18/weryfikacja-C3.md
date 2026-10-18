# Weryfikacja C3 — twardy stop 10% ma ujemną wartość oczekiwaną

**Twierdzenie C3** (bt_symulacja-wykonania.md, perspektywa-quant.md): „Twardy stop 10% od wejścia w W1–W7-podobnej konstrukcji ma ujemną wartość oczekiwaną: koszt −0,19…−0,30 p.p./tydz. (t −1,7…−2,7) wobec braku stopu, nie obniża σ ani maxDD; na losowych koszykach stop jest neutralny; ponowne otwarcie po stopie odrabia część, ale podwaja transakcje; po przebiciu −10% w 5 sesjach średnia dalsza zmiana ≈ 0."

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Rdzeń (ujemna EV rzędu −0,2…−0,3 p.p./tydz., brak redukcji σ/maxDD, neutralność na szumie, reopen odrabia część kosztu) przeżył wszystkie próby obalenia; cztery zastrzeżenia: (1) istotność jest słabsza, niż sugerują t-staty — koszt niesie kilkanaście okien z gwałtownym odbiciem po przebiciu, mediana efektu ≈ 0, test znaku p = 0,12; (2) koszt pochodzi z nóg LONG, na nogach SHORT stop jest ~darmowy; (3) stop ma mały, ale realny efekt ogonowy (kill 12-tyg. 41,3 % → 37,7 %, CVaR5 −18,6 → −17,8), którego twierdzenie nie wymienia; (4) zdanie „dalsza zmiana ≈ 0” jest za ostrożne — na nogach momentum po przebiciu kurs średnio ODBIJA w stronę tezy (+1,1 %, t 2,8), czyli stop ucina nogi, które się bronią.

Skrypty: `weryfikacja_C3.py` (wyniki `weryfikacja_C3_out.md`, `_wyniki.json`, `_serie.csv`), `weryfikacja_C3_dod.py` (`weryfikacja_C3_dod_out.md`, `_dod_wyniki.json`). Harness identyczny z fazą 2 (momentum 6M TOP5/BOTTOM5 vs ^NDX, 234 okien 2022-04-22 → 2026-10-16, wejście zamknięcie D0+1, wyjście zamknięcie D5+1, 24 %/noga, brutto). Jednostki: % kapitału na okno (= 1,2 × spread_pp). Dane: closes_5y.csv (dzisiejszy skład NDX-100 — survivorship bias, patrz zastrzeżenie 5).

## 1. Testy wykonane i wyniki

### T1. Stop na proxy intraday (brak OHLC): low/high = close × (1 ∓ k·σ60), k = 0,5 i 1,0

| wariant | Δ vs brak stopu (t) | Δ na 100 losowych strategiach | **Δ skorygowane o szum** | stopy | σ tyg. | p5 | kill 12-tyg. |
|---|---|---|---|---|---|---|---|
| zamknięcia, bez reopen (= v3 fazy 2) | −0,283 (−2,06) | −0,001 | **−0,282** | 285 | 9,87 | −13,5 | 37,7 % |
| zamknięcia + reopen (= v4, app.py) | −0,185 (−1,70) | −0,006 | **−0,179** | 293/145 | 9,98 | −12,8 | 40,4 % |
| proxy 0,5σ, realizacja NA PROGU | −0,132 (−0,71) | **+0,161** | **−0,294** | 434 | 9,13 | −11,6 | 30,0 % |
| proxy 0,5σ, na progu + reopen | −0,014 (−0,08) | **+0,191** | **−0,205** | 479/269 | 9,54 | −13,2 | 32,7 % |
| proxy 0,5σ, realizacja na zamknięciu | −0,431 (−2,32) | −0,012 | **−0,418** | 434 | 9,34 | −12,3 | — |
| proxy 0,5σ, na zamknięciu + reopen | −0,224 (−1,54) | +0,019 | **−0,242** | 479/269 | 9,68 | −13,4 | — |
| proxy 1,0σ, na progu | −1,839 (−6,41) | — | — | 622 | 9,10 | −13,2 | 52,5 % |

Źródło: weryfikacja_C3_out.md §1, §3; weryfikacja_C3_dod_out.md D1, D2.

Wniosek: surowy koszt przy realizacji „na progu" spada do −0,13 (t −0,7) i wygląda na obalenie — ale ta sama reguła na LOSOWYCH koszykach daje **+0,16 p.p./tydz.** (5–95 %: −0,01…+0,34), bo realizacja na progu jest lepsza niż zamknięcie zawsze, gdy sesja kończy się głębiej niż −10 % (luki po wynikach). Po odjęciu artefaktu koszt wraca do −0,29 (bez reopen) / −0,21 (z reopen). Wariant pesymistyczny (wyzwalacz intraday, realizacja na zamknięciu, bez artefaktu: Δ_losowe −0,012) kosztuje −0,42 (t −2,3). Zatem przy intraday stop zadziała częściej (434 vs 285 razy) i każde dodatkowe zadziałanie ucina nogę z dodatnim dryfem — koszt rośnie, nie maleje. Proxy 1,0σ (szerszy zakres dnia) jest absurdalnie drogi (−1,8), bo wyzwala 622 stopy; pokazuje kierunek: im więcej zadziałań, tym gorzej. Przedział z twierdzenia (−0,19…−0,30) jest raczej dolną granicą kosztu.

### T2. LONG vs SHORT, VIX > 20 / ≤ 20

| wariant | Δ nogi LONG (t) | Δ nogi SHORT (t) | Δ VIX>20, n=74 (t) | Δ VIX≤20, n=160 (t) |
|---|---|---|---|---|
| stop 10 % zamknięcia | −0,231 (−2,3) | −0,052 (−0,6) | −0,440 (−1,8) | −0,211 (−1,3) |
| stop 10 % + reopen | −0,176 (−2,6) | −0,009 (−0,1) | −0,362 (−1,5) | −0,103 (−0,9) |
| proxy 0,5σ na progu | −0,246 (−1,8) | +0,113 (+0,8) | −0,461 (−1,3) | +0,020 (+0,1) |
| stop tylko LONG (zamkn.) | −0,231 (−2,3); test znaku 22/59, p 0,067 | — | −0,125 | −0,280 (−2,1) |
| stop tylko SHORT (zamkn.) | — | −0,052 (−0,6); test znaku 36/73, p 1,0 | −0,315 (−1,7) | +0,069 (+0,7) |
| stop tylko LONG, proxy intraday | −0,246 (−1,84); test znaku 39/106, **p 0,008** | — | | |
| stop tylko SHORT, proxy intraday | — | +0,113 (+0,84); test znaku 59/114, p 0,78 | | |

Źródło: weryfikacja_C3_out.md §1–2. Liczba stopów: 146 LONG vs 139 SHORT (na 1170 nóg każdej strony) — częstość zadziałania podobna, koszt różny. Skorygowane o szum (dod D1): tylko LONG −0,20, tylko SHORT −0,08.

Wniosek: koszt stopu to zjawisko nóg LONG (po −10 % w tygodniu długa noga momentum odbija: +1,88 %, t 3,0 do wyjścia — §T6). Na nogach SHORT stop jest w granicach szumu (−0,05…+0,11). W reżimie VIX>20 koszt jest ~2× większy (−0,44 vs −0,21) — stop jest najdroższy wtedy, gdy intuicyjnie ma „chronić”. Nie obala twierdzenia; precyzuje je.

### T3. Kotwica D0 (cena tezy) vs D+1 (poziom brokera, jak app.py); wejście D0

| wariant | Δ (t) | boot 95 % | stopy |
|---|---|---|---|
| kotwica D0, zamknięcia, bez reopen | **−0,476 (−2,56)** | −0,84…−0,12 | 337 |
| kotwica D0 + reopen | −0,180 (−1,41) | −0,44…+0,07 | 347/208 |
| kotwica D0, proxy intraday na progu | −0,095 (−0,40) [skoryg. ≈ −0,26] | | 478 |
| wejście D0 (pt), stop 10 % zamkn. − v1 bez stopu | −0,232 (−1,57) | −0,53…+0,05 | 276 |
| wejście D0 + reopen − v1 | −0,165 (−1,51) | −0,39…+0,04 | 286 |

Źródło: weryfikacja_C3_out.md §1; dod_out.md (akapit „Wejście D0”). Kotwica w cenie tezy (rekomendacja STOP_ANCHOR=teza z wykonanie-bota.md) jest DROŻSZA niż kotwica brokera: więcej zadziałań (337 vs 285), bo ruch pt→pon już zużywa część progu. Na koszykach faktycznych W1–W7 kotwica D0 wygląda świetnie (+18,11 vs +9,97 % kapitału; W7 −11,63 zamiast −19,98 — tabela §6 out.md) — to anegdota jednego tygodnia (poniedziałek 12.10 był już głęboko pod D0), panel 234 okien mówi odwrotnie. Wejście w piątek nie zmienia obrazu (−0,23).

### T4. Ogon rozkładu i kill switch (brutto, bez artefaktu — realizacja na zamknięciu)

| wariant | śr. | σ | p1 | p5 | min | CVaR5 | najgorsze 4 tyg. | maxDD | kill 12-tyg. | 5. pct min kapitału |
|---|---|---|---|---|---|---|---|---|---|---|
| bez stopu | +1,31 | 9,86 | −20,5 | −13,4 | −24,2 | −18,6 | −65,4 | 68,6 | 41,3 % | 73,4 |
| stop 10 % | +1,02 | 9,87 | −21,0 | −13,5 | −26,3 | −17,8 | −73,6 | 74,5 | 37,7 % | 74,0 |
| stop 10 % + reopen | +1,12 | 9,98 | −22,5 | −12,8 | −26,3 | −19,0 | −71,3 | 72,2 | 40,4 % | 73,5 |
| stop 7 % | +0,93 | 9,30 | — | −12,2 | −22,0 | −15,7 | — | 70,8 | 36,3 % | 73,7 |
| stop 5 % | +0,74 | 8,88 | — | −11,5 | −18,8 | −14,1 | — | 66,5 | — | — |
| stop 15 % | +1,12 | 9,90 | — | −13,6 | −26,8 | −18,2 | — | 73,9 | 39,5 % (faza 2) | 74,0 |
| stop 20 % | +1,19 | 9,91 | −21,4 | −13,0 | −24,2 | −18,2 | −65,4 | 70,0 | 39,9 % | 72,6 |
| losowe strategie, bez stopu (100) | +0,00 | 4,17 | | −6,50 | | −9,24 | | 52,5 | 8,8 % (30 los.) | 77,6 |
| losowe, stop 10 % | +0,00 | 4,07 | | −6,24 | | −8,56 | | 51,5 | 8,4 % | 77,7 |

Źródło: weryfikacja_C3_out.md §3; dod_out.md D1, D2. W 10 % najgorszych okien bazy stop 10 % daje +0,96 p.p./okno (reopen: +0,18); w 10 % najlepszych −0,02.

Wniosek: p1/p5/min/maxDD stop 10 % NIE poprawia (min i maxDD pogarsza, bo realizuje na zamknięciu głębiej niż −10 % i traci odbicie). Poprawia marginalnie CVaR5 (+0,8 p.p.) i częstość kill switcha (41,3 → 37,7 %, −3,6 p.p. bezwzgl., −9 % wzgl.); 5. percentyl minimum kapitału +0,6 pkt. Ciaśniejszy stop 7 % obniża CVaR5 o 2,9 p.p. i kill do 36,3 % za koszt −0,35 p.p./tydz. (skoryg.), stop 5 % obniża min z −24 do −19 za −0,55 p.p./tydz. Ubezpieczenie ogonowe istnieje, ale jest słabe i drogie: ten sam efekt na kill (41 → 9 %) daje sizing (losowa strategia o σ 4,2 vs 9,9). Twierdzenie „nie obniża σ ani maxDD” — potwierdzone; „nie ma wartości ogonowej” byłoby za mocne — ma małą.

### T5. Istotność: bootstrap, test znaku, obcięcie, podokresy

- v3 − v2: −0,283; boot 95 % CI −0,56…−0,02, P(Δ>0) 1,8 %; **test znaku 51/120 okien ze stopem pomogło, p 0,12**; **po usunięciu 5 największych |Δ| koszt −0,09** p.p./tydz.; lata: 2022 −0,58, 2023 −0,11, 2024 −0,16, 2025 −0,37, 2026 −0,29 (5/5 lat ujemne). Mediana Δ w oknach ze stopem −0,43.
- v4 − v2: −0,185; CI −0,41…+0,02, P(Δ>0) 3,6 %; test znaku 57/121, p 0,59; obcięcie 5 → −0,12; 2024 +0,02, pozostałe lata ujemne.
- Struktura (dod D5): v3 Δ>+2 p.p. w 17 oknach (+65 p.p.), Δ<−2 p.p. w 28 (−119 p.p.), |Δ|≤2 w 189 (−13 p.p.). 5 najgorszych okien = −45 p.p. z −66 łącznie; 10 najgorszych = −70 (więcej niż suma).
- Okna niosące koszt (dod D4): 2025-04-04 (MSTR L −11,3 % → +30,9 % do wyjścia; shorty AMD/MPWR/MCHP +15…18 % → dalej +2…13 %), 2026-07-24 (SNDK/MRVL/MU/ARM L −14…−18 % → +6…+19 %), 2024-03-01 (MSTR L −21 % → +41 %), 2025-11-14 (SNDK L −26 % → +16 %). Okna, gdzie stop pomógł: 2026-02-20 (shorty AXON/TRI +11…23 % → dalej −10 %), 2024-07-26 (MSTR/ARM L dalej −9…−13 %).

Wniosek: ujemny znak jest stabilny (5/5 lat, obie strony VIX, oba sposoby realizacji), ale WIELKOŚĆ jest ogonowa: połowa okien ze stopem wygrywa, połowa przegrywa; EV robi kilkanaście tygodni z brutalnym odbiciem po przebiciu (MSTR, SNDK, MU, MRVL — nazwy o σ60 4–8 %/d). t −2,06 przy skośnym rozkładzie z kurtozą 4 jest optymistyczne; test znaku nie odrzuca zera. To nie obala kierunku, ale zdanie „t −1,7…−2,7” należy czytać jako „ok. 2σ przy ciężkich ogonach”, nie jako dowód.

### T6. Co stop ucina: zwrot od sesji przebicia −10 % (zamknięcie) do wyjścia, w kierunku tezy

| zbiór | n (udział nóg) | śr. | mediana | t | udział dalszych strat |
|---|---|---|---|---|---|
| nogi momentum 6M, wszystkie | 285 (12,2 %) | **+1,12 %** | 0,00 | **+2,80** | 34 % |
| — LONG | 146 | **+1,88 %** | 0,00 | +3,03 | 31 % |
| — SHORT | 139 | +0,33 % | 0,00 | +0,66 | 37 % |
| — VIX>20 / ≤20 | 82 / 203 | +1,57 / +0,94 | | +2,29 / +1,92 | |
| nogi losowe 5/5 | 111 (4,7 %) | −0,61 % | 0,00 | −0,84 | 37 % |
| — LONG / SHORT losowe | 46 / 65 | +0,64 / −1,50 | | +0,56 / −1,59 | |

Źródło: weryfikacja_C3_out.md §4. Dzień przebicia: sesje 1–5 → 24/63/77/79/42 (większość w 3–4 sesji, więc odbicie ma 1–2 sesje czasu). Nogi momentum przebijają −10 % 2,6× częściej niż losowe (12,2 % vs 4,7 %) — to koszt wyboru nazw o wysokiej σ.

Wniosek: dla uniwersum losowego „≈ 0” zgadza się (−0,6 %, t −0,8; wyk_b_stopy.py część 3: +0,5 %, mediana 0, n = 443). Dla nóg wybranych momentum po przebiciu kurs średnio wraca w stronę tezy o +1,1 % (long +1,9 %, t 3,0), więc stop zabiera nogę w najgorszym momencie. To mechanizm asymetrii „neutralny na szumie, kosztowny na sygnale” — twierdzenie jest tu nawet za słabe.

### T7. Koszyki faktyczne W1–W7 (% kapitału, 24 %/noga, zamknięcia; dod. proxy intraday)

| wariant | W1 | W2 | W3 | W4 | W5 | W6 | W7 | suma | stopy |
|---|---|---|---|---|---|---|---|---|---|
| bez stopu | −4,89 | +7,20 | −2,44 | +28,37 | +6,59 | −4,89 | −19,98 | +9,97 | 0 |
| stop 10 % zamkn. (± reopen) | | | | | | −5,10 | −18,88 | +10,85 | 5 |
| proxy 0,5σ na progu | | | −2,87 | | | −5,03 | −15,66 | +13,71 | 6 |
| proxy 0,5σ na progu + reopen | | | −2,87 | | | −5,03 | −16,92 | +12,46 | 6/1 |
| kotwica D0, zamkn. | | | | | | −5,10 | −11,63 | +18,11 | 5 |
| stop 15 % proxy | | | | | | | −19,54 | +10,41 | 3 |

Źródło: weryfikacja_C3_out.md §6. W W1–W7 stop pomógł (+0,9…+4,3 p.p. kapitału), wyłącznie przez W7 — zgodne z fazą 1 (wykonanie-bota.md: 4 stopy W7 −9,6 % zamiast −17,1 % kapitału). Siedem tygodni to jedno zdarzenie; panel 234 okien jest właściwym sędzią.

## 2. Tercyle zmienności (czy „W1–W7-podobna konstrukcja” zmienia wynik)

| tercyl σ60 nóg | n | śr. σ60 | 10 % w σ5 | Δ stop 10 % (t) | Δ +reopen (t) | Δ stop 7 % (t) | p5 bez / ze stopem 10 % / 7 % |
|---|---|---|---|---|---|---|---|
| 1 (niska) | 78 | 3,00 % | 1,49σ | −0,19 (−1,2) | −0,05 (−0,5) | −0,37 (−1,4) | −6,8 / −8,2 / −8,1 |
| 2 | 78 | 3,91 % | 1,14σ | −0,31 (−1,3) | −0,09 (−0,5) | −0,49 (−1,5) | −11,2 / −11,4 / −10,2 |
| 3 (wysoka) | 78 | 4,82 % | 0,93σ | −0,35 (−1,2) | −0,42 (−1,6) | −0,26 (−0,6) | −18,8 / −16,7 / −15,0 |

Źródło: dod_out.md D3. Koszyki faktyczne: W4 σ60 nóg 3,87 % (47. percentyl okien momentum), W7 3,25 % (24.), **W8 2,74 % (9. percentyl; long 2,08 %, short 3,40 %)**. Koszt stopu rośnie ze zmiennością koszyka (−0,19 → −0,35); w tercylu wysokiej σ stop 10 % poprawia p5 o 2 p.p. (−18,8 → −16,7) — tam wartość ogonowa jest największa, ale kosztuje najwięcej. W8 leży w tercylu niskiej σ: stop 10 % = ~1,6σ5, zadziała rzadko, koszt ≈ −0,05…−0,19 i prawie wyłącznie na shortach (AXON/DASH/APP/FER), gdzie EV stopu ≈ 0.

## 3. Najsilniejszy kontrargument wobec C3

Koszt stopu nie jest systematycznym „dragiem”, lecz sumą kilkunastu okien, w których noga po przebiciu −10 % odbiła o +10…+40 % (MSTR ×3, SNDK ×3, MU, MRVL, ARM): 5 okien = −45 z −66 p.p. łącznego kosztu, mediana Δ ≈ 0, test znaku p 0,12, po obcięciu 5 okien koszt −0,09 p.p./tydz. Te nazwy są jednocześnie najbardziej podatne na survivorship bias (dzisiejszy skład NDX-100: spółki, które po −20 % nie wróciły, w danych nie istnieją) — odbicie po przebiciu, a więc i koszt stopu, jest prawdopodobnie przeszacowane. Jeśli przyjąć, że „prawdziwy” koszt leży między wariantem obciętym (−0,09) a pełnym (−0,28), to przy zrealizowanej redukcji kill 12-tyg. o 3,6 p.p. i CVaR5 o 0,8 p.p. stop 10 % jest tanim, choć słabym, ubezpieczeniem — nie „reguły o ujemnej EV do wyłączenia”, lecz „reguły o EV ≈ −0,1…−0,3 i małym plusie ogonowym”. Kontrargument NIE wystarcza do obalenia: znak jest ujemny w 5/5 lat, w obu reżimach VIX, przy obu kotwicach, przy wejściu pt i pon, przy realizacji na zamknięciu i (po korekcie artefaktu) na progu; wariant pesymistyczny intraday daje −0,42 (t −2,3); mechanizm (odbicie nóg momentum po przebiciu, +1,1 %, t 2,8) jest spójny z całością.

## 4. Zastrzeżenia metodyczne

1. Brak OHLC: proxy close × (1 ∓ 0,5σ60) nie widzi luk na otwarciu (wyniki kwartalne — MSTR, SNDK, ARM w D4); bot przy luce realizuje przy mid o 13:45 UTC, czyli bliżej zamknięcia niż progu. Realne wykonanie leży między „na progu” (−0,29 skoryg.) a „na zamknięciu” (−0,42).
2. Korekta o szum zakłada, że artefakt realizacji na progu jest taki sam dla nóg momentum i losowych; nogi momentum mają wyższą σ i częściej kończą sesję głęboko pod progiem, więc artefakt na nich jest raczej większy — korekta jest konserwatywna (zaniża koszt).
3. Survivorship bias zawyża odbicia po −10 % (głównie LONG), czyli zawyża koszt stopu; nie dotyczy porównań między wariantami w tym samym stopniu, ale dotyczy ich kierunku.
4. Kill 12-tyg. liczony na zamknięciach; bot sprawdza 2× dziennie na mid — częstości lekko zaniżone dla wszystkich wariantów.
5. Brak kosztów transakcyjnych w tabelach powyżej (faza 2: reopen = drugi spread; 0,10 %/nogę/otwarcie zjada ~0,03 p.p./tydz. przy 145 reopenach) — netto wariant z reopen jest bliżej −0,21 niż −0,18.

## 5. Twierdzenie po weryfikacji

Twardy stop 10 % od wejścia w konstrukcji momentum 5/5 (24 %/noga) ma ujemną wartość oczekiwaną rzędu **−0,18…−0,42 p.p. kapitału/tydz.** wobec braku stopu (zamknięcia: −0,28 bez reopen / −0,18 z reopen; wyzwalacz intraday: −0,29 po korekcie artefaktu / −0,42 przy realizacji na zamknięciu); znak ujemny w 5/5 lat i obu reżimach VIX, ale rozkład jest ogonowy (test znaku p 0,12; 5 okien = 68 % kosztu; po ich obcięciu −0,09). Koszt pochodzi z nóg LONG (−0,23, t −2,3; po −10 % długa noga momentum odbija +1,9 %, t 3,0); na nogach SHORT stop jest neutralny (−0,05…+0,11). Stop nie obniża σ (9,87 vs 9,86) ani maxDD (74,5 vs 68,6 %), nie poprawia p1/p5/min; obniża kill 12-tyg. z 41,3 do 37,7 % i CVaR5 z −18,6 do −17,8 — mały efekt ogonowy, 10× słabszy niż sizing (losowa strategia o σ 4,2: kill 8,8 %). Na losowych koszykach stop jest neutralny (−0,001…−0,006). Reopen odrabia +0,10 p.p./tydz. za 145 dodatkowych otwarć na 293 stopy. Kotwica w cenie tezy (D0) pogarsza EV (−0,48, t −2,6). Koszt rośnie ze zmiennością koszyka (−0,19 w tercylu niskiej σ → −0,35 w wysokiej); W8 (σ60 nóg 2,74 %, 9. percentyl) leży w tercylu niskiej σ.

## 6. Implikacja projektowa

- Stop 10 % nie jest narzędziem EV i słabym narzędziem ogona — ryzykiem kapitału ma sterować ALLOC_PCT/vol-target (zgodnie z C1/C2), nie stop per noga. Jeśli stop zostaje jako siatka awaryjna: **asymetrycznie** — na nogach SHORT bez zmian lub ciaśniej (EV ≈ 0, a tam leży ryzyko squeeze’u: W2026-02-20 AXON +22,8 %), na nogach LONG szerszy próg (15–20 %: koszt −0,13…−0,20 przy niemal tej samej częstości kill) albo w jednostkach σ z capem; wymaga w app.py rozdzielenia STOP_LOSS_PCT na STOP_LOSS_PCT_LONG / STOP_LOSS_PCT_SHORT.
- NIE przestawiać kotwicy na cenę tezy (D0): panel mówi −0,48 vs −0,28; W7 to anegdota.
- Reopen: zostawić decyzję kosztową (netto ≈ 0 wobec braku reopen: +0,10 brutto minus drugi spread); logicznie czystsze jest exclude po stopie, ale EV tego nie wymaga.
- Nie liczyć na stop przy kill switchu w W8: koszyk o σ60 nóg 2,74 % przebije 10 % na pojedynczej nodze rzadko (10 % ≈ 1,6σ5), a problem W8 to odległość ≈ 1,7 % od progu kill przy σ dziennej kapitału ~2,2 % (ryzyko-i-sizing.md) — stop per noga tego nie adresuje.
- Do pomiaru w KROKU A raportu tygodniowego: po każdym stopie zapisywać zwrot nogi od stopu do rotacji (to, co stop „oddał”), osobno LONG/SHORT — po ~30 stopach rozstrzygnie, czy asymetria LONG/SHORT jest realna poza próbą.
