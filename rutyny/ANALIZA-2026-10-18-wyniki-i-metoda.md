# Analiza wyników i metody doboru spółek — system NDX100 (stan 18.10.2026)

<!-- Dokument analityczny wygenerowany 18.10.2026 (sesja Claude Code na zlecenie właściciela: „przeanalizuj jeszcze raz wyniki i metodę dobierania spółek do portfela, udoskonal proces aby system osiągał zyski"). Trzy fazy pracy wieloagentowej: (1) sześć niezależnych analiz (dekompozycja wyników, wykonanie bota, audyt reguł, moc predykcyjna modelu, perspektywa quant, ryzyko/sizing); (2) pięć testów wstecznych na 5 latach danych dziennych (momentum, odwrócenie, neutralność branżowa/beta, zakład czynnikowy i bramka reżimu, symulacja wykonania); (3) adwersaryjna weryfikacja 9 twierdzeń, trzy niezależne projekty procesu i panel sędziów. Skrypty i notatki: analiza/2026-10-18/. Dane: zamknięcia Yahoo 2021-10-18…2026-10-16 (103 spółki dzisiejszego składu Nasdaq-100 + ^NDX, ^SOX, ^VIX, ETF-y czynnikowe) — survivorship bias zaznaczony przy każdym wyniku. Dokument nie zawiera liczb z rachunku (tylko % i p.p.). -->

## 0. Odpowiedź w sześciu zdaniach

1. **Wynik W1–W7 jest nieodróżnialny od zera** (średnia −0,52 p.p./tydz., t = −0,12; hit rate 33/70 = 47 %, Wilson 36–59 %), a jedyną statystycznie pewną cechą koszyków jest ich **zmienność: σ tygodniowego spreadu 11,3 p.p. = 3,3× losowego koszyka 5/5 z tego samego uniwersum** (3,4 p.p.; χ²(6) = 66).
2. **System nie dobierał spółek — grał jeden czynnik.** 74 % wariancji dziennego spreadu W1–W7 wyjaśnia ^NDX + (^SOX − ^NDX), znak tygodniowego spreadu = znak ^SOX − ^NDX w 7/7 tygodni; reszta „selekcyjna” to +0,6 p.p./tydz. przy sd 6 (t 0,27). W7 (−21,15 p.p.) to zdarzenie z = −3,8 wobec własnego rozkładu tej konstrukcji, nie pomyłka w typowaniu.
3. **Wynik Modelu 3.0 nie ma mocy predykcyjnej na 5 sesji** (IC −0,10, permutacja p = 0,92) i jest w ~75 % momentum 6–12M + betą; deklarowane p (38–62 %) jest **skalibrowane odwrotnie** (p > 55 % → 44,5 % trafień, p ≥ 61 % → 37,5 %). Tylko 25 % wag scoringu to czynniki mierzalne; koszyk odbiegał od własnego rankingu w 10 z 16 stron W2–W8.
4. **Na horyzoncie 5 sesji w NDX-100 (2022–2026) działa wyłącznie kontynuacja cenowa**: momentum 6M relatywne TOP5/BOTTOM5 +1,0 p.p./tydz. brutto (t ≈ 2,0–2,1), **+0,7–0,85 netto (t 1,5–1,6)** — marginalnie, niestabilnie (cała alfa 2024–2026) i z zawyżeniem przez survivorship bias; odwrócenie, sezonowość, low-vol i scoring fundamentalny nie działają albo mają znak przeciwny.
5. **Największym pojedynczym problemem jest sizing, nie typowanie**: 24 % kapitału na nogę (gross 240 %) przy σ konstrukcji 7–12 p.p./tydz. daje **P(kill switch −25 %) ≈ 51–65 % w 12 tygodni i 98–100 % w 52 tygodnie przy zerowej alfie** (weryfikacja C4; szacunek fazy 1: 37–41 % / 80–97 %); stop 10 % od poziomu brokera z ponownym otwarciem nogi w kolejnym biegu kosztuje (−0,19…−0,28 p.p./tydz., t −1,7…−2,1) i nie obniża ogona; pętla uczenia dopisała 36 reguł, 17 po n = 1, 0 z retestem, a najczęściej stosowana („przegrana bez odzyskanej siły relatywnej = poza koszykiem") ma znak przeciwny do danych.
6. **Co z tego wynika (szczegóły w §6–§7 i w PROPOZYCJA-2026-10-18-proces-v2.md):** koszyk jako deterministyczna funkcja danych — `scripts/ranking.py`, konstrukcja E (5 par branżowych, momentum 6M relatywne, budżet |b_SOX net| ≤ 0,5), nakładka uznaniowa wyłącznie jako mierzony cień; stały sizing ALLOC 0,08 (gross 80 %) zamiast 0,24, vol-target tylko diagnostycznie; stop 15 % LONG / 10 % SHORT bez ponownego otwierania w tej samej wersji (kotwica bez zmian — wariant z ceną tezy wypadł gorzej w weryfikacji C3); próg miękki i ślad kill switcha w bocie (specyfikacja do decyzji właściciela); reżim tylko jako wyłącznik P2; moduł taktyczny wyłączony; rejestr reguł z testem przekrojowym; koszyki cienie rozliczane co sobotę jednym skryptem; **decyzja właściciela na teraz** — kapitał ≈ 1,7 % nad progiem kill switcha: świadomy restart z nowym sizingiem (wariant B) zamiast losowego zatrzymania w tygodniu W8.

## 1. Co faktycznie się stało (W1–W7)

### 1.1 Rozliczenia są poprawne — problem nie leży w danych

Spready W1–W7 z `history` odtworzone z niezależnie pobranych zamknięć co do 0,00 p.p. (−4,06 / +6,19 / +1,44 / +13,85 / +5,95 / −5,89 / −21,15), z korektą o 5 dywidend w oknach; 15 par kontrolnych zamknięć D0/D+n zgodnych z tabelami raportów co do centa (`analiza/2026-10-18/dekompozycja.py`).

| Tydzień | Sesje | spread_pp | ^NDX w oknie | składowa czynnikowa (β·NDX + b·(SOX−NDX) + b·DEF) | reszta „selekcyjna” | ≥4 nogi z jednego bloku |
|---|---|---|---|---|---|---|
| W1 | 5 | −4,06 | | SOX −3,41 | | — |
| W2 | 5 | +6,19 | | SOX +2,15 | | — |
| W3 | 5 | +1,44 | | SOX +2,06 | | LONG 5/5 półprzewodniki |
| W4 | 11 | +13,85 | +4,2 % | SOX +4,84 | | LONG 5/5 półprzewodniki |
| W5 | 4 | +5,95 | +1,8 % | SOX +6,82 | | LONG 5/5, SHORT 4/5 defensywy |
| W6 | 5 | −5,89 | +0,2 % | SOX −9,54 | | LONG 5/5, SHORT 4/5 |
| W7 | 5 | −21,15 | −5,5 % | czynniki −11,5 (β +1,0; SOX −7,2; DEF −5,3) | −9,7 (LITE −12,2, PANW −11,2, APP −6,6, SBUX −6,2) | LONG 3/5, SHORT 4/5 |

Źródło: `dekompozycja-wynikow.md` §4–5 (ładunki z 250 sesji przed D0; udział wariancji tygodniowej: czynniki 46 %, reszta 28 %, kowariancja 26 %). Korelacja tygodniowego spreadu ze zwrotem ^SOX − ^NDX: 0,90; z czynnikiem defensywnym (XLP/XLU/XLV − QQQ): −0,92. Ładunek netto koszyka na ^SOX − ^NDX w każdym tygodniu +1,1…+2,1 (W8: +0,29 w regresji 3-czynnikowej z 250 sesji; +0,05 jako śr. b_SOX LONG − SHORT z ranking.py — miara używana w rozliczeniu A5 — pierwszy koszyk de facto neutralny czynnikowo).

### 1.2 Selekcja nazw: nie da się nic stwierdzić

Reszta po czynnikach: +0,61 p.p./tydz., sd 5,98, t = 0,27; trafienia reszty 40/70 = 57 % (Wilson 45–68 %). Łączny wynik: średnia −0,52 p.p. (t −0,12), bez W7 +1,08 (t 0,44). Przedział ufności dla przewagi selekcji obejmuje −2…+3 p.p./tydz.; wykrycie +1 p.p./tydz. przy sd 6–10 wymaga 140–400 tygodni. **Każda decyzja o wagach modelu podjęta na tej próbie jest data miningiem.**

Jedyny ślad przewagi: strona SHORT w software (INTU +25,6 p.p. w 4 tygodnie, APP +16,5, ADSK +3,6; blok +3,3 p.p./nogę, n = 13) — hipoteza do rejestru, nie reguła. Shorty defensywne, nazwane 12.10 „jedyną powtarzalną przewagą (13/14)", po W7 mają +0,14 p.p./nogę (13/19): to była ekspozycja na czynnik DEF, nie selekcja.

### 1.3 W7 jako ogon własnej konstrukcji

Rozkład 5-sesyjnych spreadów składu W7 z 250 sesji przed D0 ma sd 6,47 p.p.; −21,15 to z = −3,8 i gorzej niż najgorsze z ~1000 historycznych okien tego składu (−16,5). Przy gross 240 % sd 5-sesyjna konstrukcji 6,5–9,8 p.p. = 8–12 % kapitału tygodniowo. Koszyki W4–W6 były bardziej zmienne niż 100 % losowych koszyków 5/5 (W7: 98. percentyl, W8: 44.). Korelacja par LONG wzrosła z 0,35 (W1–W2) do 0,75 (W5–W6): efektywna liczba nóg z pięciu spadła do 1,2–1,5 (`ryzyko-i-sizing.md` §1, §4).

Test hipotezy „kupiono rozciągnięte nazwy, przyszło odwrócenie": **obalona** — w panelu 2021–2026 momentum 20-sesyjne > +20 p.p. zapowiadało WYŻSZY spread 5-sesyjny (+3,48 vs +0,69 p.p., n = 117/1180); decyl D10 momentum +0,78 vs D1 +0,04 p.p. (198 okien). W6–W7 to odwrócenie czynnika, nie kara za pogoń.

### 1.4 Trzy różne wielkości nazywane „wynikiem"

| Seria | W6 | W7 | Co mierzy |
|---|---|---|---|
| spread_pp od D0 (history) | −5,89 | −21,15 | jakość prognozy przy równych wagach i wejściu na zamknięciu D0 |
| spread_fills_pp (history) | +3,88 | −12,36 | od OSTATNIEJ ceny odniesienia — po stopach bota ceny odniesienia znikają, więc to NIE jest wynik rachunku |
| „jak rachunek" (rekonstrukcja: wejście D+1, stopy 10 % z ponownym otwarciem, straty zrealizowane) | ≈ −5,8 | −14,96 (≈ −17,9 % kapitału) | to, co grał rachunek, bez kosztów CFD |

Rekonstrukcja złożona 6.10→16.10: ≈ −21,5 % vs fakt −23,7 % (reszta: taktyczne, koszty CFD, egzekucja poniżej −10 %). **Mnożnik: 1 p.p. spreadu = 1,2 % kapitału** (ALLOC 0,24 × 5 nóg), nie 0,24 % — raporty dzienne pisały to mylnie dla spreadu (`wykonanie-bota.md` §0 p.1).

## 2. Czy metoda doboru ma moc predykcyjną

### 2.1 Wynik Modelu 3.0 vs realizacja

Spearman(Wynik, zwrot relatywny 5 sesji) dla 30 nazw TOP15+BOTTOM15, W1–W7: średni IC −0,10 (t −0,51); pooled 210 nazwo-tygodni −0,13; permutacja 5000×: P(IC ≥ obserwowany | brak mocy) = 0,92; pasmo zerowej mocy ±0,12. IC wewnątrz TOP15 −0,02, wewnątrz BOTTOM15 +0,01. Koszyk TOP5 trafiał 42,9 % vs pozycje 6–15 40,0 %; BOTTOM5 51,4 % vs 47,1 % (`moc-predykcyjna-modelu.md`, `mp_ic_model.py`).

### 2.2 p jest skalibrowane odwrotnie

p = 50 + 0,5·(wynik − 50) obcięte do 38–62 odtwarza tabele w 97 % wierszy (n = 205). p > 55 %: 73/164 = 44,5 % trafień (95 %: 37–52 %) przy deklarowanych śr. 58,7 %; p ≤ 55 %: 41,5 %. Tercyl najsilniejszych sygnałów (|wynik − 50| ≥ 19): hit 40,6 %, −1,97 p.p./pozycję; najsłabszych: 46,3 %, −0,79. Na 70 nogach koszyków: p ≥ 61 → 12/32 (37,5 %), p ≤ 58 → 15/25 (60 %); corr(p, zwrot) = −0,16. **p nie jest prawdopodobieństwem i nie powinno być publikowane jako takie.**

### 2.3 Model = momentum + beta

Spearman(Wynik, czynnik na D0) wśród 30 nazw, średnia z 8 tygodni: momentum 6M 0,73 (t 15), 12M−1M 0,72 (t 23), odległość od MA200 0,72, beta 126d 0,57 (t 6,9). Nogi LONG W4–W7: percentyle momentum 6M 84–91, bety 80–92. Korelacja tygodniowego IC modelu z IC bety 0,93, z IC momentum 0,95, ze zwrotem ^SOX − ^NDX 0,90 (n = 7). IC modelu na resztach po becie i momentum: −0,12 (t −1,5). **20 czynników fundamentalnych nie zmienia kolejności względem dwóch współrzędnych ilościowych.**

### 2.4 Koszt uznaniowości

W sekcji B2 tylko 26/104 wag (25 %) to czynniki mierzalne dla całego uniwersum w każdym biegu (wycena 14, momentum 7, buybacki 3, koncentracja 2); 42 % częściowo mierzalne (dane dla ≤ 8–20 spółek, reszta „50"); 33 % czysto uznaniowe (ekspozycja AI 9, cykl/pricing power 8, odbiorca vs płatnik 5, R&D 4, cyber 3, …). Sub-ocen nie ma w żadnym pliku — czynników nie można ani potwierdzić, ani wycofać z osobna. Wynik „goni kurs": corr(Δ Wyniku, zwrot kursu między D0) +0,53…+0,83 w 5 z 7 par tygodni; wymiana 15/30 nazw W2→W3 i 21/30 W7→W8; koszyk odbiegał od TOP5/BOTTOM5 własnego rankingu w 10 z 16 stron (W8: 7 z 10 nóg to nadpisania). Korelacja Wyniku z betą 0,53–0,73 (W1–W7) → 0,03 (W8): **model zmienił tożsamość po jednym złym tygodniu**, więc serii W1–W7 i W8+ nie wolno łączyć.

Baza hit rate: udział spółek uniwersum bijących kapitalizacyjny ^NDX w 5 sesji wynosił 31–43 % w tygodniach mega-capów i 67–76 % w rotacji (W6–W7) — „50 %" nie jest poprawną bazą; nadwyżka LONG nad medianą uniwersum −1,61 p.p./tydz. (t −0,66), SHORT −0,42 (t −0,25).

## 3. Co działa, a co nie na horyzoncie 5 sesji w NDX-100 (2022–2026)

Harness wspólny: okna piątek→piątek, 5L/5S równych wag, zwrot pozycji względem ^NDX, 208–234 okien, baseline 2000 losowych koszyków 5/5 na okno (σ 3,4 p.p.; losowa STRATEGIA: średnia 5–95 % = ±0,37 p.p., t 5–95 % = ±1,65, 97,5 % = 1,97). Koszty: 0,10 % na zmienioną nogę + 6 %/rok finansowania od gross. **Survivorship bias:** uniwersum = dzisiejszy skład, co faworyzuje momentum i zaniża wyniki shortowania liderów.

| Wariant | n | śr. p.p./tydz. | σ | t | Sharpe | hit | najgorszy tydz. | netto | Uwaga |
|---|---|---|---|---|---|---|---|---|---|
| momentum 6M (126 sesji, skip 5) TOP5/BOTTOM5 | 208–234 | +1,01…+1,11 | 7,4–7,7 | 2,0–2,1 | 1,0 | 55–57 % | −25,8 | +0,7…+0,85 (t 1,5–1,6) | 1. połowa próby t ≈ 0; 2023 ujemny; VIX > 20: +2,4 (t 2,8), VIX ≤ 20: +0,35 |
| momentum 12M−1M | 208 | +0,77 | 7,5 | 1,5 | 0,75 | 56 % | −25,5 | +0,51 | 2023: −1,18 (t −1,7) |
| momentum 3M / 1M | 208 | +0,95 / +0,76 | 7,5 / 6,4 | 1,8 / 1,7 | 0,9 / 0,85 | 56 % | −27,6 / −17,5 | +0,66 / +0,43 | obrót 1M 4,8 nóg/tydz. |
| odwrócenie 5 / 10 / 21 sesji | 233 | −0,33 / −0,59 / −0,67 | 5,4–6,2 | −0,9…−1,7 | <0 | 45–47 % | −19…−31 | −0,7…−1,0 | **nie działa**; strata z nogi SHORT (shortowanie liderów tygodnia) |
| 6M + 5 par wewnątrz branży TV | 233 | +1,01 | 5,67 | **2,72** | **1,29** | 56 % | **−14,4** | +0,74 (t 1,99) | ta sama średnia, σ −24 % (F p < 0,0001), maxDD −37 vs −51 |
| 6M + neutralność branżowa (≤1L+1S/grupa) | 233 | +0,76 | 5,93 | 1,95 | 0,92 | 54 % | −14,7 | +0,48 | σ −20 %; na 12M−1M podnosi też średnią (+0,40) |
| 6M + limit ≤2 semis/strona | 208–233 | +0,75…+0,88 | 6,7–7,2 | 1,6–1,9 | 0,8–0,9 | 52–58 % | −20…−26 | +0,47…+0,61 | limit prawie nie wiąże (skład = bez limitu w 77 % okien) |
| 6M + neutralność beta / risk parity 10 nóg ∝ 1/σ | 208–233 | +0,38…+0,82 | 6,5–7,6 | 0,8–1,7 | 0,4–0,8 | 51–52 % | −25…−32 | +0,11…+0,47 | **pogarsza**: przewaga dolarowa shortów = netto-short indeksu |
| proxy „AI-hardware long / defensywy short" (listy ex post) | 234 | +1,30 | 7,05 | 2,83 | 1,33 | 60 % | −21,9 | +1,05 (t 2,28) | to jest czynnik, który grał system; r = 0,78 z SMH − XLP; 2022 ujemny; listy zdefiniowane po fakcie |
| ETF long SMH / short XLP | 234 | +0,70 | 4,76 | 2,26 | 1,07 | 55 % | −15,6 | +0,47 | ten sam czynnik taniej i z połową drawdownu; W7: −15,6 vs koszyk −21,2 |
| 6M + bramka reżimu P0/P1/P2 (gross 100/50/0 %) | 234 | +0,78 | 6,8 | 1,8 | 0,83 | — | −25,8 | +0,57 | **pogarsza**: tygodnie P1 najlepsze dla momentum (+3,04, t 2,0); W7 był w P0 |
| 6M + stop 10 % (bez / z ponownym otwarciem jak app.py) | 234 | +1,02 / +1,12 | 9,9 (kapitał) | 1,6 / 1,7 | 0,75 / 0,81 | 51–53 % | −26 | +0,70 / +0,78 | koszt −0,28 / −0,19 p.p./tydz. (t −2,1 / −1,7) vs bez stopu; σ i maxDD bez zmian; na losowych koszykach stop neutralny |
| 6M + sizing 1/σ, cel σ dz. 1,5 % | 234 | +0,43 | 3,98 | 1,6 | 0,77 | 53 % | −10,2 | +0,24 | kill w 0,4 % okien 12-tyg. (vs 41 % przy 24 %/nogę); Sharpe −20 % |
| 6M + ALLOC 0,12 równe wagi | 234 | +0,65 | 4,93 | 2,0 | 0,95 | 54 % | −12,1 | +0,49 | identyczny Sharpe jak 0,24, kill w 5,8 % okien 12-tyg.; 0,16 → 19,3 % |

Wnioski z tabeli: (a) **żaden sygnał selekcji nie przebija baseline'u z t > 2 po kosztach**; najlepszy kandydat to momentum 6M w konstrukcji parowej (t netto 1,99); (b) odwrócenie krótkoterminowe w tym uniwersum nie istnieje (kontynuacja 1–4 tygodni, t −1,7…−2,1 dla kontrarian); (c) konstrukcje branżowe to jedyne, które statystycznie obniżają ryzyko bez utraty średniej; neutralizacja β/σ przez przesuwanie dolarów między stronami szkodzi (wymagałaby hedgu indeksowego); (d) bramka reżimu, stop per noga i cięcie po złym dniu mają ujemną lub zerową wartość oczekiwaną — redukcję ryzyka daje sizing całego koszyka; (e) finansowanie 6 %/rok od gross 240 % to 0,23–0,28 p.p./tydz., czyli 25–60 % brutto każdego sygnału.

Faktyczne koszyki W4–W7 to momentum 6M w skrajnej wersji (nogi long w percentylach 70–99, short 2–10; W4–W6 po 5/5 półprzewodników w long, gdzie mechaniczny TOP5 miał 3–4) i wypadły GORZEJ niż mechaniczny ranking w tych samych oknach (W6 −5,6 vs −4,0; W7 −21,1 vs −13,6). Retro konstrukcji z `scripts/ranking.py` (D0 z raportów, sesje jak w history): A czyste momentum +17,1 / +9,6 / −10,6 / −16,3; B pary branżowe +9,0 / +6,2 / −4,8 / −16,4; C neutralna +5,0 / +12,4 / −6,3 / −19,0; D budżet czynnikowy +7,1 / +10,7 / −3,1 / −12,2; FAKTYCZNY +16,0 / +5,95 / −5,6 / −21,15 (W4 na 10 sesjach). Cztery okna to anegdota: wszystkie konstrukcje straciły w W7, bo cały blok wysokiego momentum (także cyber) spadł razem; różnica jest w skali ogona, nie w znaku.

## 4. Wykonanie i ryzyko

### 4.1 Sizing i kill switch

| Sizing | σ dz. kapitału | P(kill −25 %, 4 tyg.) | P(kill, 12 tyg.) | P(kill, 52 tyg.) | Źródło |
|---|---|---|---|---|---|
| ALLOC 0,24 (dziś), koszyki W1–W8 | 3,7–5,6 % | 6–17 % | 37–70 % | 80–97 % | `ryzyko_sizing.py` §2 (bootstrap blokowy 20 000 ścieżek), `wyk_c_sigma.py`, `pq_quant.py` §F, `bt_symulacja-wykonania.py` |
| ALLOC 0,12 | ~2,2 % | — | 6 %* / ~30 % | ~31 % | *okna 12-tyg. w backteście momentum; 30 % z bootstrapu koszyków W1–W8 |
| ALLOC 0,08–0,10 | ~1,5–1,9 % | — | 2,7–4,9 % | ~9–18 % | kryterium „< 5 % w 12 tyg." spełnia stałe ALLOC ≤ 0,10 (pula W1–W8) / ≤ 0,08 (pula W4–W7) |
| vol-target: ALLOC = clip(0,015 / σ60_unit, 0,04, 0,12) (σ60_unit = σ dzienna Σ5L−Σ5S; w ranking.py `sigma60_unit_dzienna` to σ na parę, stąd tam czynnik 5) | 1,5 % (zrealizowane 1,7 %) | — | 0,3–0,5 % | ~10 % | średnie ALLOC ~0,08 (5,7–16 % per koszyk); z progiem ×0,5 przy DD < −10 %: 0,0 % |

Zdarzenie 6–16.10 (−23,7 % kapitału) leży w okolicach p90–p95 rozkładu 4-tygodniowego drawdownu przy obecnym sizingu — nie jest anomalią. ALLOC 0,24 to ≈ 1,6× pełny Kelly dla μ 0,75 / σ 7 p.p.; propozycja 3.1 (0,20) jest kosmetyczna (P(kill 52 tyg.) 92 % vs 97 %). Vol-target tnie symetrycznie zyski i straty (W7 −8,7 % zamiast −25,4 %, ale W4 +3,9 % zamiast +16,6 %); jego uzasadnieniem jest przeżywalność, nie wynik in-sample. Przy alfie +2 p.p./tydz. mediana wyniku 12 tyg. dla vol-targetu +9 %, dla 0,24 +20,8 % — ale z 60 % ruiny przy alfie 0.

Po trafieniu kill switcha bot zostaje wstrzymany bezterminowo (`app.py` ~1485–1503: każdy bieg kończy się na `equity < prog_kill`, a bez pozycji kapitał nie wraca nad próg) — brak polityki wznowienia.

### 4.2 Stop 10 % i ponowne otwarcie

* Stop czyta **poziom brokera** (`p["wejscie"]`) przed ceną tezy z `fills` — wbrew docstringowi i CLAUDE.md; każde wyrównanie wielkości przestawia kotwicę (MU zamknięty stopem 13.10 przy kursie +4,4 % nad ceną tezy 913,35; ten sam błąd co LITE 15.09).
* Po stopie `desired_book` otwiera nogę ponownie w kolejnym biegu, jeśli nie ma wpisu `exclude` (`app.py`: `book.pop` tylko w bieżącym biegu). W7: 4 stopy (LITE, MU, MRVL, PANW), 3 ponowne otwarcia; stop pomógł (−9,6 % kapitału zamiast −17,1 % bez stopu), reopen oddał 2,3–3,3 % — razem −11,9…−12,9 %.
* 10 % dla nóg o σ dziennej 4–6 % (LITE, SNDK, MU, MRVL) to 0,7–1,0 σ 5-sesyjnej: trafia „przez przypadek" w 9–18 % okien 5-sesyjnych w 5 latach (ostatni rok 15–24 %), a po trafieniu średni dalszy ruch ≈ 0 (+0,1…+2,7 p.p.); dla PEP 10 % = 3,6σ (martwy). Stop ma wartość wariancyjną, nie kierunkową; wniosek fazy 1 („próg w jednostkach σ”) skorygowała weryfikacja C3: **stały próg 15 % LONG / 10 % SHORT, bez ponownego otwarcia w tej samej wersji, kotwica bez zmian** (wariant σ bez przewagi nad stałym, kotwica w cenie tezy pogarsza).
* W backteście momentum stop 10 % kosztuje −0,28 p.p./tydz. (t −2,06) bez reopen i −0,19 (t −1,70) z reopen; 15 %: −0,19 (t −2,26); 2,5σ: −0,30 (t −2,71); REDUCE 50 % po 2σ: −0,13 (t −1,81). Żaden nie zmienia częstości kill switcha — zmienia ją tylko sizing.

### 4.3 Pozostałe mechanizmy

* **Opóźnienie wejścia** (rotacja w poniedziałek 13:45 UTC zamiast D0): +0,10 p.p./tydz., t 0,24 — nieistotne; w W4–W7 akurat pomogło (+15 p.p. łącznie). Harmonogramu nie zmieniać; zmienić METRYKĘ: rachunek gra od D+1/fills do rotacji.
* **Dzień rotacji**: nowe nogi weszły 12.10 o 13:45 na ok. połowie wielkości i zostały zamknięte/otwarte ponownie o 17:05 (PANW 411,82→400,95, MRVL 273,80→267,53, CSCO 116,47→115,53), PEP/TMUS weszły dopiero o 17:05 — prawdopodobnie stopa depozytu liczona z depozytu WSZYSTKICH pozycji na ekspozycję tylko nóg niesionych (zawyżona ~2,4× w dniu rotacji). Wymaga potwierdzenia logiem `/run` z 12.10 13:45.
* **Bramka 4 %/8 %** (Puls): przekrojowo po sygnale REDUCE reszta okna +0,08 p.p. (n = 3442, t 0,03); po dniu ze spreadem koszyka ≤ −3 p.p. kolejne 3 sesje +1,43 p.p. (t 2,7) — cięcie po złym dniu nie ma dodatniej wartości oczekiwanej (weryfikacja C7: EV bramki ≈ 0 w każdej mierze, ±0,15 p.p./tydz.); in-sample W1–W7 symulacja protokołu +2,78 p.p. łącznie, wyłącznie z W7. W praktyce stop bota (szybszy) zawsze wyprzedza bramkę (2 sesje + blokada sektorowa + bieg 12:30) — `reaction_pp ≈ 0` to artefakt, nie ocena Pulsu.
* **Bramka reżimu P0/P1/P2**: nigdy nie uruchomiona (36 biegów P0); w backteście byłaby aktywna 71/234 tygodni (36 w 2022) i obniża średnią momentum bez poprawy maxDD; straty W6–W7 (−26,7 p.p.) wystąpiły w P0 (^NDX +12 % nad MA200, VIX 15) — progi indeksowe nie widzą koncentracji czynnikowej.
* **Kontrola kapitału / ALLOC_PCT_SAFE / MAX_EXPOSURE_STEP**: bez wpływu w W6–W7; podwojenie ALLOC 3.10 (0,12→0,24 po dwóch dobrych okresach, jeden 11-sesyjny) weszło od razu na 100 % celu nowych nóg 5.10 — ta sama pętla „reguła po n = 1", tylko w kodzie. Rachunek grał W1–W5 na ~0,06–0,12 i W6–W7 na 0,24: połowa zysków, pełna strata.
* **Koszty CFD** (szacunek parametryczny): przy gross 240 % i obrocie ~330 % kapitału tygodniowo 25–64 % kapitału rocznie (środek 42 %: spread rotacji 16 %, wyrównania 12 %, finansowanie 9,6 %, dywidendy shortów 2,9 %) = ~0,7 p.p. spreadu tygodniowo tylko na pokrycie kosztów. Dominują koszty transakcyjne, nie finansowe. Faktyczne stawki Capital.com nieznane — do odczytu z rachunku.

## 5. Reguły i pętla uczenia

Rejestr (`audyt-regul.md` §1): **36 reguł/filtrów/konsekwencji**, z tego 17 wprowadzonych po jednej obserwacji, 0 z retestem, ≥ 6 par wzajemnie sprzecznych; reguły koszykowe K1–K27 istnieją wyłącznie w raportach HTML (brak w `tygodniowa.md`). Bilans deklaracji D1–D3: 20 rozstrzygniętych, 9 TAK / 11 NIE; 6 falsyfikacji wyprodukowało regułę (TSLA, zakaz > 20 %, sito 12 %, kara 6→3, luka > 10 %, MU/zaostrzenie) — każda po n = 1. Pętla: strata → nagłówek → reguła → zaostrzenie po następnej stracie.

| Reguła | Test przekrojowy 5 lat | In-sample | Werdykt |
|---|---|---|---|
| „Przegrana bez odzyskanej siły relatywnej = poza koszykiem" (K10/K16/K17, sito Perf.W ≤ −8 %) | top-kwintyl momentum: przegrana bez odzyskania **+0,66 p.p./tydz.** (n = 1108, t 0,44) vs odzyskana +0,32 vs wygrana +0,59 | 10 wykluczeń W2–W7: wykluczone śr. −1,74, zamienniki średnio gorsze o 0,84 p.p./nogę, ale mediana różnicy +2,05 — wynik zdominowany przez LITE W5 (+16,1 vs ALAB −2,0); in-sample nierozstrzygalne (C6) | **uchylić** — wymusza wymianę 5–9 nóg/tydz. bez sygnału |
| Zakaz short po spadku 10-sesyjnym ≤ −20 % (K13) | short po r10 ≤ −20 %: **−1,64 p.p./tydz.** (n = 213, t −2,42); wariant 12 %: −0,7 (t −1,7); luka 1-dniowa > 10 %: ≈ 0 | INTU poza W5–W7: −20,8 p.p. na nodze oszczędzone (3/3) | **zostaje** jako jedyna z poparciem; scalić sito 12 %, uchylić „lukę" |
| NVDA poza do zamknięcia DOJ/Groq (K12) | — | −0,67 p.p. na nodze, zamienniki +1,99 → koszt ≈ 0 | wyjątek imienny z wygaśnięciem |
| TSLA poza po 3 przegranych (K11) | — | short wygrałby 2/4, +2,16 na nodze | wyjątek imienny z wygaśnięciem; warunek powrotu niefalsyfikowalny |
| „Nie kupuj po skoku / momentum bez rewizji = pułapka" (K8/K21) | long po skoku ≥ +12 %: **+1,06 p.p.** (t 2,2); 10 sesji ≥ +15 %: +1,13 (t 2,8) | 4/7 wykluczonych wygrałoby | **uchylić** — znak przeciwny do danych |
| „Nie shortuj celu wykupu" (WDAY, K6) | — | WDAY jako short +15,1 p.p. w 6 oknach | ograniczyć do oficjalnej oferty, wygasa po 2 tyg. |
| Płatnicy capexu poza longiem (K9/K23) | — | MSFT +6,83 p.p. kosztu | archiwum (W8 i tak odwrócone) |
| Bramka 4 %/8 % + druga sesja (R1) | REDUCE → reszta okna +0,08 (t 0,03) | +2,78 p.p. (W7) | kontrola wariancji o zerowej wartości oczekiwanej — patrz §7 |
| Tie-break „mniejsza waga" (R10) | proxy kapitalizacji: duże +0,37 p.p./tydz. (t 4,9 — proxy obciążone) | 8 decyzji granicznych: wybrany gorszy o 1,31 p.p./nogę | zdegradować do czystego tie-breaka |
| Kalibracje kary event 6→3, „15 zamiast 8" (K3/K4) | nietestowalne bez kalendarza | n = 1 każda | uchylić, jedna skala 0–10 |

## 6. Weryfikacja adwersaryjna (faza 3)

Dziewięć twierdzeń z faz 1–2 dostało niezależnego sceptyka z zadaniem obalenia (skrypty i notatki `analiza/2026-10-18/weryfikacja-C*.md`). Wszystkie przeszły jako **POTWIERDZONE Z ZASTRZEŻENIEM** — zastrzeżenia zmieniły projekt w pięciu miejscach (kolumna „skutek").

| # | Twierdzenie | Werdykt i liczby po weryfikacji | Skutek dla procesu |
|---|---|---|---|
| C1 | Momentum 6M relatywne to jedyny działający sygnał | przewaga na uniwersum point-in-time: +0,7 p.p./tydz. brutto (t 1,55), **+0,44 netto (t 0,95)** — zero w przedziale ufności; survivorship bias zawyżał t 2,1 → 1,5 | momentum zostaje jako sygnał porządkujący, ale system v2 „ma przeżyć i mierzyć", nie obiecywać zysków (§6 PROPOZYCJI) |
| C2 | Pary branżowe obniżają σ bez utraty średniej | σ-ratio 0,67 (CI 0,58–0,78) odporne na definicję grupy (0,59–0,76) i uniwersum PIT; koszt średniej −0,21 (CI −0,92…+0,50), na klastrach PIT mediana −0,86 — **możliwy koszt 0,3–0,5 p.p./tydz.** | konstrukcja E przyjęta; w oczekiwaniach liczbowych koszt −0,3…−0,5 zapisany jawnie |
| C3 | Stop 10 % z ponownym otwarciem kosztuje | koszt z nóg LONG −0,23 p.p./tydz. (t −2,3), SHORT neutralny; **kotwica w cenie tezy pogarsza (−0,48 vs −0,28)**; stop σ-owy bez przewagi nad stałym | stop 15 % LONG / 10 % SHORT, bez reopen, kotwica bez zmian — zamiast „stopu w σ z kotwicą w cenie tezy" z fazy 2 |
| C4 | Sizing 0,24 jest głównym ryzykiem | P(kill, alfa 0): 0,24 → 51–65 %/12 tyg., 98–100 %/52; vol-target 0,0–0,4 %/12 i 20–49 %/52; **1/σ per noga niewykonalny lotami poniżej ~2 500 USD odniesienia**; vol-target vs stałe ALLOC: Sharpe +0,06…+0,12 (n.s.) | natychmiast ALLOC 0,08–0,10; vol-target tylko na papierze; bez inverse-vol per noga |
| C5 | Model 3.0 nie ma mocy predykcyjnej | IC Wyniku −0,10 (95 % CI −0,57…+0,37), p nieinformacyjne (corr −0,16), warstwa uznaniowa +0,06 IC (t 1,2) — **brak dowodu, nie dowód braku** (n = 7) | Model 3.0 poza selekcją; nakładka uznaniowa mierzona jako cień U |
| C6 | Reguła „przegrana bez odzyskanej siły" szkodzi | przekrój +0,66 vs +0,32 (t 0,44) — brak sygnału; symulacja kosztu −0,37…−0,70 p.p./tydz.; **in-sample nierozstrzygalne** (średnia −0,84, mediana +2,05, LITE W5 dominuje) | reguła uchylona; rejestr z moratorium i testem przekrojowym |
| C7 | Bramka cenowa Pulsu nie ma wartości | EV ≈ 0 w każdej mierze (±0,15 p.p./tydz.); po sygnale REDUCE reszta okna +0,08…+0,16 (t ≈ 0); stop bota zawsze szybszy | bramka = pomiar; `exclude` tylko basis news |
| C8 | Bramka reżimu P1 nie pomaga | P1 obniża momentum 1,00 → 0,78 bez poprawy maxDD; tygodnie P1 najlepsze (+3,04, t 2,0); W6–W7 w P0 | tylko P2 jako wyłącznik płynności; P1 flaga |
| C9 | „Jedyna opcja to restart" | P(kill) przy 0,24: 58/69/77 % w 5/10/20 sesji; przy 0,08: 39/48/58 % — ~21 % przypada na lukę poniedziałkową księgi W7 niezależnie od ALLOC; **sam reset `equity_peak` daje poduszkę 11 %, samo `START_EQUITY` — 0; pełne 25 % wymaga obu**; przy alfie 0 E[kapitał] restartu = E[czekania] | trzy spójne warianty A/B/C dla właściciela (PROPOZYCJA §1); restart = jawnie „przesunięcie progu po stracie", z obsunięciem od szczytu historycznego w każdym raporcie |

Panel projektowy: trzy niezależne projekty (A „mechaniczny" — ranking.py jako jedyne źródło + pętla pomiarowa; B „przeżywalność" — ALLOC 0,06, FLAT −12 %, polityka wznowienia, veto lotu; C „konstrukcja" — pary E z budżetem SOX, stałe 0,08, próg miękki) i trzech sędziów (`sedzia-1…3.md`: C 26/B 25/A 20; C 27/A 25/B 24; B 30/C 28/A 22). Konsensus: **konstrukcja E + stałe ALLOC 0,08** (C) z przeszczepami operacyjnymi z B (stop 15/10 bez reopen, ślad kill i wznowienie, `ALLOC_PCT_SAFE` 0,04, `REDUCE_FALLBACK=close`, obsunięcie od szczytu historycznego w raportach) i pętlą pomiarową z A (ranking.py jako jedyne źródło składu, rejestr, cienie, `data/ranking-<version>.json`). Odrzucone: vol-target jako pole sizingu bota, σ-stop czytany z pliku repo w biegu, Model 3.0 jako nakładka na żywo, FLAT −12 % (bez efektu w symulacji), 1/σ per noga, dwie transze.

## 7. Co z tego wynika dla procesu

Pełny opis decyzji, wariantów na poniedziałek 19.10 i specyfikacji bota: `rutyny/PROPOZYCJA-2026-10-18-proces-v2.md`. Skrót tego, co jest w repozytorium (gałąź `claude/gifted-lamport-iwzpop`, do scalenia przez właściciela):

1. **Skład koszyka** liczy `scripts/ranking.py` (konstrukcja E; parametry prerejestrowane w nagłówku skryptu, veto cenowe 1 280 USD jako stała — nie liczone z kapitału rachunku). Dla W8 plik `data/ranking-2026-W8.json` (D0 16.10, veto EVENT ze snapshotu TV) daje cienie do rozliczenia 24.10; E dla W8 to CRWD/APP (software), AMGN/ALNY (biotech), FTNT/PAYX (usługi IT), AMD/AVGO (półprzewodniki), DXCM/GEHC (sprzęt medyczny) — b_SOX net +0,26, σ60 tygodniowa 5,2 p.p. (percentyl 89 wobec losowych koszyków 5/5 z uniwersum po vetach; koszyk faktyczny W8: σ60 4,1 p.p., percentyl 61, b_SOX +0,05) wobec koszyka faktycznego W8 wybranego jeszcze Modelem 3.0.
2. **Rozliczenie** dostaje prerejestrowaną tabelę A1–A9 i `scripts/koszyki_cienie.py` → `data/koszyki-cienie.jsonl` (A, B, C, D, E, U, FAKTYCZNY); wnioski o wariancji po 12 oknach, o średniej nie przed 26; kryteria decyzji po 12/26/52 oknach zapisane w rutynie, decyduje właściciel.
3. **Rutyny v2** (`rutyny/tygodniowa.md`, `rutyny/dzienna.md`): sobota bez Modelu 3.0, elity, panelu fundamentów, p, pre-mortem i deklaracji; Puls jako raport kontrolny (bramka cenowa = pomiar, `exclude` tylko basis news z listy zamkniętej, `tactical=[]`, P1 flaga). Budżet TV ≤ 10 wywołań w obu.
4. **Rejestr reguł** `rutyny/reguly.md`: 14 OBOWIĄZUJĄCYCH (w tym K0 konstrukcja, S2 sizing 0,08, S3 stop 15/10, R5'' reżim P2, R1'' bramka-pomiar, T0 taktyczne wyłączone), KANDYDACI, WYJĄTKI IMIENNE z datą, UCHYLONE; moratorium do 26 okien.
5. **Bot (`app.py`) — zmiany WDROŻONE** (18.10.2026, na polecenie właściciela „wprowadź wszystkie niezbędne zmiany"): stop 15 % LONG / 10 % SHORT bez ponownego otwarcia w tej samej wersji (`wykonanie.stopy`), próg miękki od kroczącego szczytu (10 %/5 %, 2 pary; `wykonanie.soft`), ślad kill switcha i wznowienie po 14 dniach i zmianie wersji (`wykonanie.kill`, szczyt := kapitał bez podłogi START_EQUITY, ALLOC_RESTART 0,04), nowe domyślne ALLOC 0,08 / SAFE 0,04 / taktyczne wyłączone / REDUCE_FALLBACK close, `/status` z `kill_switch.zapas_pct`, `prog_miekki`, `wykonanie`. Aktywne po deployu na Renderze; zmienne ustawione tam jawnie (np. `ALLOC_PCT=0.24`) mają pierwszeństwo i trzeba je zmienić ręcznie. Do deployu rutyny czytają stan faktyczny z `/status`.
6. **Decyzja właściciela na poniedziałek 19.10 przed 13:45 UTC** (PROPOZYCJA §1): A płasko, **B restart z sizingiem 0,08** (Render `ALLOC_PCT=0.08`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`, `START_EQUITY=<kapitał>` + commit właściciela `equity_peak := kapitał`), C nic. Bez decyzji ~60 % szans, że bezpiecznik zamknie wszystko w tym tygodniu w losowym momencie.

Czego ten proces NIE obiecuje: zysku. Oczekiwanie przy alfie zero to −0,1 %/tydz. netto (koszty), przy in-sample +0,3 %; dowód przewagi na żywo wymaga setek tygodni. Zyskiem, który da się wykazać w horyzoncie roku, jest **niższa wariancja i przeżywalność** (P(kill 52 tyg.) 8 % zamiast 98–100 %), czyli szansa, żeby pomiar w ogóle trwał.

## 8. Czego nie da się stwierdzić (uczciwie)

* Czy selekcja ma jakąkolwiek przewagę: CI −2…+3 p.p./tydz.; potrzeba 140–400 tygodni przy obecnej σ, ~50 tygodni przy σ konstrukcji parowej z vol-targetem. Backtest przekrojowy to jedyne narzędzie, które rozstrzyga w horyzoncie życia projektu — o wariancji po 12–26 tygodniach, o średniej dopiero po 200+.
* O ile survivorship bias zawyża momentum (t 2,1) — wymaga historycznych składów Nasdaq-100; do tego czasu zakładać Sharpe 0,3–0,6, nie 1,0.
* Czy czynniki fundamentalne/rewizje mają moc na 5 sesjach — brak serii historycznych w repo (snapshoty TV od W8); testowalne po maszynowym zapisie sub-ocen.
* Faktyczne koszty CFD (spready per ticker, overnight long/short, korekty dywidendowe) i ceny realizacji stopów — tylko z eksportu transakcji brokera.
* Czy neutralizacja czynnikowa z 250-sesyjnych bet nie niedoszacowuje ekspozycji w ruchach gwałtownych (W7: cyber spadł z półprzewodnikami mimo niskiego b_SOX) — reszta skorelowana +0,78 z częścią czynnikową (n = 7).

## 9. Źródła

Notatki i skrypty faz 1–3: `analiza/2026-10-18/` (kopie z sesji; faza 3: `weryfikacja-C1…C9.md`, `projekt-A/B/C-*.md`, `sedzia-1…3.md`, `00-faza3-weryfikacja-i-projekty.txt`; dane `closes_5y.csv` do odtworzenia skryptem `analiza/2026-10-18/pobierz_closes_5y.py`). Raporty W1–W8: `reports/raport-2026-W*.html`; dzienne: `reports/puls-*.html`; `signals.json` (history, fills, wykonanie — 39 stanów w historii gita); `rutyny/PROPOZYCJA-2026-10-12-model-3.1.md` (analiza 12.10 — jej tezy T6/T7 potwierdzone; teza „shorty defensywne = jedyna alfa" obalona; reguła LUKA-SHORT słaba na pełnym uniwersum).
