# PROJEKT A — proces mechaniczny: koszyk jako deterministyczna funkcja danych, Model 3.0 jako mierzona nakładka

Autor: projektant procesu (sesja 18.10.2026). Priorytet: **odtwarzalność i dowód**. Każdy element ma
liczbę z faz 1–2 (`_faza1_wyniki.txt`, `_faza2_wyniki.txt`), z weryfikacji adwersaryjnej C1–C9
(`weryfikacja-C*.md`) albo z dwóch nowych skryptów tej notatki — albo jest oznaczony
**„bez dowodu — decyzja”**. Bez liczb z rachunku (tylko % i p.p.).

Nowe skrypty (katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):

| plik | co liczy |
|---|---|
| `projektA_bt.py` → `projektA_bt_out.md`, `projektA_bt_wyniki.json`, `projektA_bt_serie.csv` | konstrukcje A0/A_S1/A_K13/A/D na uniwersum **point-in-time** (harness C1, 233 okna 2022-04…2026-10) i na składzie dzisiejszym; ekspozycja czynnikowa zrealizowana; ścieżka dzienna kapitału dla 5 polityk sizingu; koszt nakładki „1 wymiana nogi na stronę”; stopy 10/15/20 % i w jednostkach σ |
| `projektA_boot.py` → `projektA_boot_out.md`, `projektA_boot_wyniki.json` | bootstrap blokowy (blok 4 tyg., 2000 ścieżek) P(kill −25 %) 12/52 tyg. dla polityk sizingu przy alfie 0 / +0,3 / in-sample; start z poduszką ≈ 1,7 % |
| `projektA_ranking_W8.json/.md` | `scripts/ranking.py` na D0 = 2026-10-16 z konstrukcją D (koszyki cienie dla W8) |

---

## 0. Streszczenie decyzji

| element | decyzja | liczba, która ją uzasadnia | źródło |
|---|---|---|---|
| **Źródło koszyka** | `scripts/ranking.py`: momentum 6M relatywne (126 sesji, skip 5) → TOP5/BOTTOM5 po wetach; **konstrukcja A**, nie D/B/C | Wynik Modelu 3.0: IC −0,10 (95 % CI −0,57…+0,37), w 67 % zdeterminowany przez momentum+betę; koszyk odbiegał od własnego rankingu w 10/16 stron. Momentum 6M na PIT: +0,71 p.p./tydz. brutto (t 1,55), +0,44 netto (t 0,95) — jedyny sygnał cenowy z dodatnim znakiem w 5 latach; odwrócenie −0,33 (t −0,93) | moc-predykcyjna-modelu.md; C5; C1 §(g); bt_odwrocenie.md |
| **Dlaczego nie budżet czynnikowy (D)** | D zostaje koszykiem **cieniem**, nie koszykiem bota | PIT: D − A = **−0,54 p.p./tydz. (t −2,36)**, Sharpe 0,09 vs 0,65; σ_D/σ_A 0,76, ale netto −0,23. Dziś: −0,34 (t −1,41). Spójne z f/g/h (bt_momentum) i klastrami PIT (C2: Δ mediana −0,86) | projektA_bt_out.md; bt_momentum.md; C2 T3 |
| **Dlaczego nie pary branżowe (B)** | cień | σ −24 % trzyma się, ale Δ średniej nierozstrzygalna (CI ±0,57) i ujemna w 5/6 definicji TV oraz 11/11 klastrowań PIT (−0,38…−1,23) | C2 |
| **Veta w rankingu** | K13 (nie shortuj po r10 ≤ −20 %), S1 (σ60 > 3× mediany), K2' (raport w D+1…D+5) | K13: short po r10 ≤ −20 %: −1,64 p.p./tydz. (n 213, t −2,42); w konstrukcji koszt ≈ 0 (A_K13 vs A0: −0,02). S1: koszt −0,04 p.p. PIT (−0,15 dziś), σ −3 %, p5 +1,0 p.p. — **konstrukcyjna**. K2': nietestowalne bez kalendarza — **bez dowodu — decyzja o ogonie** | audyt-regul.md; projektA_bt_out.md; reguly.md K2' |
| **Model 3.0** | nakładka: **≤ 1 wymiana nogi na stronę**, tylko z rang 6–15 tej samej strony, z zapisem i tygodniowym rozliczeniem Δ = FAKT − A | σ Δ losowej wymiany 1,80 p.p./tydz.; wykrycie prawdziwej przewagi +0,3 / +0,5 / +1,0 p.p. przy t = 2 wymaga **144 / 52 / 13 tygodni**; IC modelu nierozstrzygalne (420–570 tyg. dla IC 0,05) | projektA_bt_out.md; C5 |
| **Sizing** | vol-target całego koszyka + próg miękki: `ALLOC = clip(0,015/(5·σ60_unit), 0,04, 0,12)`, przy DD < −10 % od szczytu ×0,5 do powrotu nad −5 %; `ALLOC_PCT` w Renderze = 0,12 jako twardy sufit | bootstrap PIT, alfa 0: P(kill 12/52 tyg.) stałe 0,24: 48 %/98 %; 0,12: 8 %/68 %; 0,08: 1 %/33 %; vt: 4 %/54 %; **vt+soft: 0 %/17 %** (in-sample 0 %/6 %); maxDD p95 −30 % vs −79 % | projektA_boot_out.md; C4 |
| **Stop** | stop w jednostkach σ: `clip(2·σ60_i·√5, 8 %, 20 %)`, **bez ponownego otwarcia** w tej samej `version`, kotwica = `fills.cena` | σ-stop: Δ −0,002 p.p./tydz. (t −0,06), σ 6,66→6,59, p5 −10,4→−9,9 (58 stopów/233 tyg.); stały 10 %: −0,04 (PIT) … −0,28 (dziś, C3); reopen = drugi spread, netto ≈ 0 | projektA_bt_out.md; C3; wykonanie-bota.md |
| **Bramka Pulsu 4 %/8 %** | **usunięta jako wyzwalacz**; zostaje pomiar diagnostyczny | EV ≈ 0 (±0,15 p.p./tydz.), ogon ≤ 1 p.p. w 5 % najgorszych tygodni, P(kill) 32,6→31,2 %; w W6–W7 zawsze wyprzedzona przez stop | C7; audyt-regul.md |
| **Bramka reżimu** | P1 → tylko flaga; P2 = **wyłącznie** DD ^NDX > 20 % od maks. 252 sesji (sobota) → `status NIEAKTUALNA`; bez histerezy; Puls: sesja ≤ −5 % lub VIX > 40 → NIEAKTUALNA do najbliższej soboty (**bez dowodu — decyzja o płynności**) | bramka P0/P1/P2 obniża średnią 1,00→0,78 bez poprawy maxDD; P1 najlepsze tygodnie (+3,04, t 2,0); „tylko P2→0” najtańsze (Sharpe 0,72 vs 0,67) i usuwa kill 2022 (20/37→0/37 okien); histereza kosztuje 10 tyg. odbić | bt_rezim…md; C8 |
| **Moduł taktyczny** | **zawieszony** (`tactical=[]`, `TACTICAL_ENABLED=false`) do testu przekrojowego H2 na PIT | n = 4 pozycje, 20 % kapitału/noga bez testu; H2 (long po dniu ≥ +12 %, 10 sesji): fwd10 +3,5 p.p. (t 2,2, n 307), ale 2022 i 2026 ujemne dla ≥ +8 % — nie przechodzi kryterium znaku w ≥ 4/5 lat | perspektywa-quant.md §D; reguly.md H2 |
| **Deklaracje D1–D3** | zastąpione: jedyną deklaracją tygodnia jest **wpis nakładki** („Y zamiast X, oczekiwanie: Y > X”); falsyfikacja nigdy nie tworzy reguły | 20 rozstrzygniętych deklaracji: 9 TAK/11 NIE; 6 falsyfikacji → 6 reguł po n = 1; 17/36 reguł po n = 1, 0 retestów | audyt-regul.md |
| **Rejestr reguł** | `rutyny/reguly.md` — awans tylko po teście przekrojowym **na uniwersum PIT**: ≥ 30 zdarzeń w ≥ 15 tyg., \|t\| ≥ 2 klastrowane, znak w ≥ 4/5 lat, reguła wiąże; moratorium do 26 okien cieni | K10 („przegrana bez odzyskanej siły”): w TOP5 wyrzucane nogi są najlepsze (+1,68, t 2,16) — reguła anty-momentum; 148 wariantów: 0 za, 24 przeciw | C6; audyt-regul.md |
| **Pomiar** | koszyki cienie co sobotę jednym skryptem; metryki prerejestrowane; wnioski o wariancji po 12, o nakładce po 26, o czynniku nigdy przed 52 (i tylko jako CI) | σ losowego koszyka 3,4 p.p. vs faktyczne 11,3 (χ²(6) = 66); przy σ 7 p.p. +1 p.p./tydz. wymaga ~200 tyg., +0,3 — ~540 | perspektywa-quant.md; C1 |
| **Migracja teraz** | przed poniedziałkiem 13:45 UTC: `ALLOC_PCT` 0,24 → 0,08, `TACTICAL_ENABLED=false`, **reset `equity_peak` do bieżącego kapitału + `START_EQUITY` ≤ kapitał** (decyzja właściciela); W8 zostaje ostatnim koszykiem Modelu 3.0 i pierwszym tygodniem cieni | z poduszką ≈ 1,7 %: P(kill w 4 tyg., alfa 0) 68–85 % **dla każdej polityki** (bootstrap), P(kill pon. 13:45 na książce W7) 21 %; po resecie (opcja c C9) 0 %/0 %/0 %/0 % przy 0,08 | projektA_boot_out.md; C9 §2, §5 |

**Oczekiwane metryki projektu (konstrukcja A, PIT, vt+soft):** μ spreadu +0,60 p.p./tydz. brutto (CI obejmuje zero; ex ante +0,1…+0,5 netto), σ spreadu 6,7 p.p.; kapitał: σ tyg. 1,6–1,9 %, σ dz. 0,8–0,9 %, μ tyg. −0,12 % (alfa 0, same koszty) … +0,04 % (in-sample); P(kill 12 tyg.) 0 %, 52 tyg. 6–17 %; maxDD p95 −26…−30 %; koszty ≈ 0,15–0,2 % kapitału/tydz. (finansowanie 6 %/rok × gross ~100 % + rotacja 2,3 nogi/tydz.). **To projekt o przeżywalności i mierzalności, nie o zysku** — zysk, jeśli jest, zmieści się w 0,1–0,5 p.p./tydz. i będzie widoczny dopiero po 50–200 tygodniach.

---

## 1. Zasada projektu: co jest dowodem

1. **Koszyk = f(dane, parametry zamrożone w `scripts/ranking.py`).** Każdy może odtworzyć sobotni koszyk z `data/ranking-cache.csv` (albo `closes`), `data/tv-screen-<version>.json` i kalendarza wyników. Rutyna nie wybiera — przepisuje.
2. **Jedyna warstwa uznaniowa jest skwantowana i księgowana**: ≤ 1 wymiana nogi na stronę, z rang 6–15, z zapisem w `data/ranking-<version>.json` (`nakladka`) i rozliczana co sobotę jako `delta_nakladki_pp`.
3. **Reguła istnieje tylko wtedy, gdy ma rejestr i test przekrojowy** (`rutyny/reguly.md`). Reguła bez testu nie wiąże składu — może najwyżej być cieniem.
4. **Horyzont dowodu jest jawny w każdym raporcie**: przy σ 6,7 p.p./tydz. tygodnie W1–Wn nie dowodzą przewagi; dowodem przewagi jest wyłącznie backtest przekrojowy na PIT (C1 §Implikacja pkt 3). Żywy rachunek rozstrzyga o **wariancji, kosztach i wykonaniu** (test F po 12 oknach), nie o średniej.
5. **Sizing zakłada alfę 0.** Ekspozycja jest funkcją σ konstrukcji, nie „pewności tezy” (p skalibrowane nieinformacyjnie: Spearman(p, trafienie) −0,02, C5).

---

## 2. Stan dowodu, na którym stoi projekt

### 2.1 Co wiemy z faz 1–2 i weryfikacji (liczby, które decydują)

| twierdzenie | liczba | źródło | skutek dla projektu |
|---|---|---|---|
| System grał jeden czynnik, nie selekcję | 74 % wariancji dziennego spreadu W1–W7 = ^NDX + (SOX−NDX); znak tygodnia = znak SOX−NDX 7/7; reszta „selekcyjna” +0,61 p.p./tydz. (t 0,27) | dekompozycja-wynikow.md | ryzyko trzeba mierzyć ekspozycją, nie „trafnością” |
| Wynik Modelu 3.0 bez mocy na 5 sesji | IC −0,10 (t −0,5), 95 % CI −0,57…+0,37; 67 % R² rang = momentum 6M/12M−1M + beta; p: p ≥ 61 → 37,5 % trafień, Spearman(p, hit) −0,02 | moc-predykcyjna-modelu.md; C5 | Model 3.0 nie może decydować o składzie; może być nakładką z budżetem |
| Tylko 25 % wag scoringu mierzalne; koszyk odbiegał od rankingu w 10/16 stron; W8 7/10 nóg to nadpisania | moc-predykcyjna-modelu.md | procedura nieodtwarzalna → wymóg skryptu |
| Momentum 6M to jedyny dodatni sygnał cenowy | PIT: +0,71 brutto (t 1,55), +0,44 netto (t 0,95), 95 % CI netto −0,39…+1,34; dziś +1,01 (t 2,09) — t≈2 to w połowie selekcja wariantu, w połowie skład ex post | C1 | sygnał zostaje jako jedyny, ale sizing i oczekiwania do alfy ≈ 0 |
| Odwrócenie nie istnieje; low-vol ujemne | rev5 −0,33 (t −0,93), rev21 −0,67 (t −1,66); long low-σ/short high-σ −1,58 (t −3,1) | bt_odwrocenie.md; perspektywa-quant.md | żadnych komponentów kontrariańskich |
| Konstrukcje neutralizujące tną zwrot | f beta-neutral 0,38 (t 0,84); g ≤2 semis 0,75; h neutral branżowo 0,77; pary: Δ −0,86 mediana na klastrach PIT | bt_momentum.md; C2 | konstrukcja A; redukcję ryzyka robi sizing |
| Sizing jest dźwignią nr 1 | 0,24: P(kill 12 tyg., alfa 0) 51–65 %, 52 tyg. 98–100 %; 0,12 → 8–16 %/65–76 %; vol-target → 0–0,4 %/20–49 %; soft −10 % → 0 % (12 tyg.) | C4; ryzyko-i-sizing.md | vol-target + próg miękki |
| Stop 10 % per noga: EV ujemna lub ≈ 0, ogon mały | −0,28 (t −2,06) dziś / −0,04 (t −0,3) PIT; kill 41,3→37,7 %; reopen +0,10 za drugi spread | C3; projektA_bt | stop w σ, bez reopen |
| Bramka Pulsu | REDUCE → reszta okna +0,08 (n 3442, t 0,03); EV ±0,15; p5 ≤ 0,7 p.p. | C7 | usunąć jako wyzwalacz |
| Bramka reżimu | 1,00→0,78 p.p./tydz. bez poprawy maxDD; tylko P2→0 tanie i usuwa kill 2022 | C8 | zredukować do P2 |
| Reguła K10 | w TOP5: wyrzucane nogi +1,68 p.p. nad resztą (t 2,16); 0/148 wariantów za | C6 | uchylona |
| K13 | short po r10 ≤ −20 %: −1,64 (t −2,42) | audyt-regul.md | jedyna reguła koszykowa z poparciem |
| Pętla uczenia | 36 reguł, 17 po n = 1, 0 retestów, ≥ 6 par sprzecznych | audyt-regul.md | rejestr + moratorium |
| Koszty CFD | 25–64 % kapitału/rok przy gross 240 % i obrocie ~330 %/tydz. (środek 42 %) | wykonanie-bota.md | gross ~100 %, obrót 2,3 nogi/tydz. → ~8–10 %/rok |
| Stan 18.10 | ≈ 1,7 % nad progiem; P(kill 5/10/20 sesji) przy 0,24: 52/65/76 %; przy 0,08: 18/34/50 %; pon. 13:45 na książce W7: 21 % | C9 | reset szczytu albo akceptacja losowego zamknięcia |

### 2.2 Nowe liczby tej notatki (projektA_bt / projektA_boot)

**Konstrukcje na uniwersum PIT** (233 okna, śr. 94,7 spółek; veto σ 0,50 nazwy/tydz., veto K13 0,84/tydz.; D: śr. 1,91 wymian, D = A w 25 % okien; |b_SOX net| ex ante A 0,68 → D 0,29):

| konstrukcja | brutto | σ | t | Sharpe | hit | p5 | najgorszy | netto | t netto | obrót | b_SOX zreal. | R² czynn. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 (TOP5/BOTTOM5 bez wet) | +0,71 | 6,99 | 1,55 | 0,73 | 55 % | −11,3 | −23,9 | +0,44 | 0,95 | 2,10 | +0,97 | 0,12 |
| A_S1 (tylko veto σ) | +0,67 | 6,79 | 1,50 | 0,71 | 55 % | −10,3 | −23,9 | +0,40 | 0,89 | 2,16 | +0,93 | 0,12 |
| A_K13 (tylko veto short) | +0,69 | 6,77 | 1,54 | 0,73 | 55 % | −10,9 | −23,9 | +0,41 | 0,92 | 2,29 | +0,97 | 0,13 |
| **A (S1 + K13) — koszyk bota** | **+0,60** | **6,70** | **1,37** | **0,65** | 56 % | −10,3 | −23,9 | **+0,33** | 0,74 | 2,33 | +0,91 | 0,12 |
| D (A + budżet czynnikowy) | +0,06 | 5,09 | 0,19 | 0,09 | 53 % | −8,4 | −17,2 | −0,23 | −0,69 | 3,18 | +0,34 | 0,02 |

D − A sparowane: −0,54 p.p./tydz. (t −2,36); w 23 tygodniach SOX−NDX < −3 p.p.: A −3,61, D −1,35 — D kupuje ochronę ogona za 0,54 p.p./tydz., czyli za całą przewagę. Lata PIT (A brutto): 2022 +0,60, 2023 −0,45, 2024 −0,04, 2025 +0,79, 2026 +2,52 — dwa lata z pięciu ujemne.

**Sizing (ścieżka dzienna, A, PIT, koszty wliczone)** — bootstrap blokowy 2000 ścieżek:

| polityka | alfa | P(kill 12 tyg.) | P(kill 52 tyg.) | kapitał po 52 tyg.: p5 / mediana / p95 | maxDD mediana / p95 (52 tyg.) |
|---|---|---|---|---|---|
| stałe 0,24 | 0 | 48,4 % | 98,2 % | 0,27 / 0,72 / 1,80 | −55 % / −79 % |
| stałe 0,12 | 0 | 8,4 % | 68,1 % | 0,55 / 0,88 / 1,45 | −30 % / −52 % |
| stałe 0,08 | 0 | 1,0 % | 33,3 % | 0,68 / 0,94 / 1,30 | −21 % / −38 % |
| vol-target (śr. ALLOC 0,104) | 0 | 3,7 % | 53,8 % | 0,59 / 0,89 / 1,27 | −26 % / −46 % |
| **vol-target + soft −10 %** | **0** | **0,0 %** | **16,6 %** | 0,75 / 0,91 / 1,19 | −19 % / −30 % |
| vol-target + soft | +0,3 | 0,0 % | 10,3 % | 0,78 / 0,96 / 1,34 | −17 % / −28 % |
| vol-target + soft | in-sample (+0,65) | 0,0 % | 6,0 % | 0,82 / 1,01 / 1,44 | −16 % / −26 % |
| stałe 0,08 | in-sample | 0,4 % | 15,6 % | 0,79 / 1,07 / 1,47 | −17 % / −32 % |

Rozkład ALLOC z vol-targetu na PIT (A): p5 0,053, mediana 0,12 (sufit w 55 % tygodni), σ60_unit tyg. mediana 5,45 p.p.; w reżimie 2026 (σ60 koszyków 2,8× wyższa niż 2023, C4) ALLOC wypada 0,05–0,08. Próg miękki kosztuje in-sample ~0,08 %/tydz. kapitału (1,17 → 1,06 na ścieżce historycznej), ale zbija P(kill 52 tyg.) z 54 % do 17 % przy alfie 0 i maxDD p95 z −46 % do −30 %.

**Start z poduszką ≈ 1,7 % (kapitał = 76,25 % szczytu), alfa 0, 4 tygodnie:** P(kill) 0,24: 85 %, 0,12: 78 %, 0,08: 68 %, 0,04: 42 %, vt: 76 %, vt+soft: 75 %. **Żadna polityka sizingu nie ratuje W8 z tego punktu startu** — potwierdzenie C9.

**Nakładka (losowa wymiana nogi 5. na kandydata z rang 6–15, jedna na stronę, A, PIT):** Δ śr. +0,02 p.p./tydz., σ Δ 1,80 p.p.; tygodni do t = 2 przy prawdziwej przewadze nakładki +0,3 / +0,5 / +1,0 p.p.: **144 / 52 / 13**. Po 26 tygodniach test wykrywa tylko |Δ| ≥ 0,71 p.p./tydz.

**Stopy (A, PIT, od wejścia D0, na zamknięciach, bez reopen):**

| próg | stopów / 233 tyg. | Δ vs brak stopu | t | σ bez / ze | p5 bez / ze | najgorszy |
|---|---|---|---|---|---|---|
| 10 % | 215 | −0,037 | −0,30 | 6,66 / 6,32 | −10,4 / −8,8 | −24,0 / −24,2 |
| 15 % | 71 | −0,085 | −1,53 | 6,66 / 6,63 | −10,4 / −10,4 | bez zmian |
| 20 % | 22 | −0,033 | −1,49 | bez zmian | bez zmian | bez zmian |
| **σ: clip(2·σ60·√5, 8 %, 20 %)** | **58** | **−0,002** | **−0,06** | 6,66 / 6,59 | −10,4 / −9,9 | bez zmian |

Stop 20 % jest martwy (22 zadziałania, zero efektu ogona). Stop σ jest jedynym wariantem o EV ≈ 0 z mierzalnym, choć małym, cięciem p5. Rozbieżność z C3 (−0,28 na składzie dzisiejszym) wynika z nogi LONG: na PIT dryf longów to +0,30 zamiast +1,32 p.p., więc stop mniej „ścina” — **EV stopu zależy od dryfu, który jest nieznany; stop ma być neutralny, nie ochronny.**

### 2.3 Czego nie wiemy (i co projekt z tym robi)

| niewiadoma | skutek | w projekcie |
|---|---|---|
| Czy momentum 6M ma dodatnią alfę ex ante (CI −0,4…+1,3 netto) | sizing i oczekiwania | alfa = 0 w sizingu; cień ETF SMH/XLP jako alternatywa (0,70 p.p., σ 4,76, maxDD 38) |
| Faktyczne koszty CFD (spready, overnight long/short, dywidendy shortów) | drag 0,15–0,2 %/tydz. to szacunek | tygodniowy `koszt_wykonania_pp` = wynik rachunku − 5·ALLOC·spread_fills; po 12 tyg. mediana |
| Kalendarz wyników historycznie (veto K2') | reguła nietestowalna | status KONSTRUKCYJNA; koszt mierzony cieniem „A bez veta EVENT” |
| Czy σ-stop na mid 13:45/17:05 zachowuje się jak na zamknięciach | test na zamknięciach = dolna granica zadziałań | log stopów w `wykonanie.stopy`; po 30 stopach ocena |
| Ekspozycja czynnikowa koszyka A (b_SOX zreal. +0,91) | tygodnie typu W7 wracają (A w SOX−NDX < −3: −3,61 p.p.) | nie neutralizujemy (D traci 0,54); ogon tnie sizing: 5·ALLOC·(−10,3 p5) ≈ −4…−6 % kapitału w 5 % tygodni |

---

## 3. Selekcja: `scripts/ranking.py` jako jedyne źródło koszyka

### 3.1 Definicja (parametry zamrożone 18.10.2026; zmiana = commit z datą w nagłówku skryptu)

| krok | definicja | parametr | uzasadnienie |
|---|---|---|---|
| uniwersum | klucze `signals.json["epics"]` należące dziś do Nasdaq-100 (lista „do weryfikacji” z TV tylko sygnalizuje różnice) | — | CLAUDE.md: epics = uniwersum |
| dane | zamknięcia dzienne 1 rok: `kursy.py --json` / `ranking.py --fetch` → `data/ranking-cache.csv`; ^NDX, ^SOX, XLP, XLU, XLV, QQQ | — | kursy.py źródło nr 1 (bez zmian) |
| sygnał | `mom6_rel = P[d0−5]/P[d0−131] − 1 − (NDX analogicznie)` | `MOM_WIN 126, MOM_SKIP 5` | C1 siatka: skip 5 najlepsze w każdej kolumnie na PIT (brutto 0,71 vs 0,55 skip 0, 0,57 skip 21) — **uwaga: to szczyt siatki, więc liczby są optymistyczne** |
| veto σ (S1) | `σ60_i > 3 × mediana σ60 uniwersum` → poza obu stronami | `SIGMA_VETO_MULT 3.0` | konstrukcyjna: koszt −0,04 p.p. PIT, σ −3 %, p5 +1 p.p.; MRNA 16.10 σ60 23,5 %/d = ~70 % wariancji koszyka równych wag |
| veto short (K13) | `r10 ≤ −20 %` → poza SHORT | `SHORT_VETO_R10 −0.20` | audyt: −1,64 p.p./tydz. (t −2,42); koszt w konstrukcji −0,02 |
| veto event (K2') | raport wyników w D+1…D+5 (FMP earnings-calendar → TV get-earnings-calendar; data niepotwierdzona = veto) → poza obu stronami | `EVENT_WINDOW_DAYS 7` | **bez dowodu — decyzja** o ryzyku ogonowym pojedynczej nogi (gap po wynikach); koszt mierzony cieniem „A bez veta EVENT” |
| wyjątki imienne | tylko z `reguly.md` sekcja WYJĄTKI z datą wygaśnięcia (K12 NVDA, K11 TSLA wygasają W9; K6' oferta przejęcia 2 tyg.) | `--exclude` | audyt: koszt ≈ 0 (NVDA −0,67/nogę, TSLA +2,16); likwidacja bezterminowości |
| konstrukcja | **A**: 5 najwyższych mom6 z kandydatów LONG; 5 najniższych z kandydatów SHORT; równe wagi | — | tabela §2.2: A Sharpe 0,65 vs D 0,09, B/C — C2 |
| wyjście | `data/ranking-<version>.json` (pełny ranking: czynniki, percentyle, veta, 4 konstrukcje z ryzykiem, `sizing`) + tabela MD do raportu; **skrypt nie dotyka `signals.json`** | `--out`, `--md` | odtwarzalność: hash pliku w raporcie i w commicie |

Stan skryptu w repo (`b86ef1b`): konstrukcje A/B/C/D, veta S1/K13/EVENT/exclude, ryzyko koszyka (σ60_unit, percentyl vs 1000 losowych, ρ60, N_eff, b_SOX/b_DEF/β net, `alloc_pct_proponowany`), testy `scripts/test_ranking.py` (17 OK). **Do dopisania** (§11): blok `nakladka` w JSON, blok `sizing` w formacie z §5.3, pole `hash_closes`, opcjonalnie `--pit` do testów.

### 3.2 Dlaczego A, a nie konstrukcja „bezpieczniejsza”

| konstrukcja | argument za | liczba przeciw | decyzja |
|---|---|---|---|
| D (budżet czynnikowy \|b_SOX\|, \|b_DEF\| ≤ 0,5) | tnie ogon: SOX−NDX < −3 → −1,35 vs −3,61; W4–W7 retro +7,1/+10,7/−3,1/−12,2 (anegdota) | PIT Δ −0,54 (t −2,36); Sharpe 0,09; netto −0,23; obrót 3,18 nóg/tydz. | cień H5; nie w bocie |
| B (5 par wewnątrz grupy TV) | σ −24 %, najgorszy tydzień −14 vs −26 | Δ średniej zależna od taksonomii: −0,15…−0,55 w 5/6 definicji TV, mediana −0,86 na klastrach PIT; 51 % par to zlepki sektorowe | cień H4 |
| C (≤ 1 L + 1 S na grupę) | σ −20 % | Δ −0,26…−0,45 w 6/6 definicji | cień |
| **A + vol-target** | ten sam efekt σ na kapitale co B/D, ale bez utraty średniej: skala koszyka zamiast składu | C2 pkt 3: „tańszy odpowiednik ~80 % efektu σ: vol-targeting” | **koszyk bota** |

---

## 4. Nakładka Model 3.0 — jawnie mierzona warstwa uznaniowa

### 4.1 Reguły

| reguła | treść | uzasadnienie |
|---|---|---|
| N1 budżet | ≤ 1 wymiana nogi na stronę (≤ 2 na tydzień); wymiana = zastąpienie **dowolnej** nogi z A kandydatem z rang 6–15 tej samej strony bez veta | σ Δ 1,80 p.p./tydz. przy 2 wymianach — więcej wymian = nakładka niemierzalna |
| N2 zapis | w `data/ranking-<version>.json["nakladka"]`: `{strona, z, na, ranga_z, ranga_na, czynnik, liczba, zrodlo, data_odczytu}` — jeden czynnik, jedna liczba, jedno źródło; brak liczby = brak wymiany | moc-predykcyjna: sub-ocen nie ma w żadnym pliku → czynników nie da się ocenić |
| N3 zakaz | nakładka nie może: przywrócić nogi z vetem, zmienić kierunku, sięgnąć poza rangi 6–15, zmienić parametrów rankingu | koszyk odbiegał od rankingu w 10/16 stron |
| N4 rozliczenie | co sobotę `koszyki_cienie.py`: `delta_nakladki_pp = spread(FAKT) − spread(A)` (D0→D+5 i od fills), kumulatywnie: suma, t, n; tabela w raporcie | jedyna statystyka warstwy uznaniowej, której σ nie napędzają zwroty czynników (C5 pkt 2) |
| N5 kryteria | po 26 oknach: t(Δ) ≤ −1,0 → nakładka wyłączona (koszyk = A) do 52 okien; po 52 oknach: t ≤ 0 → wyłączona na stałe; t ≥ 2 → budżet może wzrosnąć do 2 wymian/stronę (nigdy więcej) | asymetria: ciężar dowodu na nakładce; po 26 tyg. wykrywalne tylko \|Δ\| ≥ 0,71 — **progi decyzyjne to decyzja, nie dowód** |
| N6 to jest deklaracja | wpis nakładki zastępuje D1–D3: „oczekuję, że `na` pobije `z` w oknie”; rozliczany N4; **nie tworzy reguł** | audyt: 6 falsyfikacji → 6 reguł n = 1 |

### 4.2 Co z Modelem 3.0 jako procedurą

Scoring 20 czynników, elita analityków (B3), panel fundamentów (B0b), research per spółka — **skreślone z rutyny sobotniej jako wejścia do selekcji**; mogą służyć wyłącznie do uzasadnienia ≤ 2 wymian (N2). Powody liczbowe: IC ≈ 0 z CI ±0,5; 33 % wag czysto uznaniowych; budżet TV już przekraczany (36 min vs 20 w W8, perspektywa-quant). `p` znika z raportu (R6 uchylona). W raporcie zostaje zdanie: „IC Wyniku −0,10, 95 % CI −0,57…+0,37, n = 7 — moc nieustalona”.

---

## 5. Sizing i ryzyko kapitału

### 5.1 Reguła

```
σ60_unit  = odchylenie dzienne (śr. zwrotów 5 LONG − śr. zwrotów 5 SHORT) z 60 sesji do D0  [ranking.py]
ALLOC_t   = clip(0,015 / (5 · σ60_unit), 0,04, 0,12)                                           [ranking.py → signals.json["sizing"]]
alloc_bot = min(ALLOC_PCT=0,12 [Render], sizing.alloc_pct) × soft_factor                        [app.py]
soft_factor: 1,0; gdy equity/equity_peak < 0,90 → 0,5 aż equity/equity_peak > 0,95 (wyrównanie w biegu 17:05)
kill      : equity < 0,75 × equity_peak (bez zmian) → zamknij wszystko; wznowienie wg 5.4
```

| element | liczba | źródło |
|---|---|---|
| cel 1,5 %/d σ kapitału (≈ 3,35 %/tydz.) | przy μ 0 i σ_tyg 3,35 %: P(kill 12 tyg.) 3,7 %, soft → 0 %; przy 0,24 σ_tyg 8,6 % → 48 % | projektA_boot; C4 |
| sufit 0,12 | 0,12 stałe: P(kill 12) 8 %; 0,16: 19 % (bt_symulacja v10); C4: „nie 0,12 bez vol-targetu” — stąd sufit, nie wartość | bt_symulacja-wykonania.md; C4 §9 |
| podłoga 0,04 | lot 0,1 akcji: przy ALLOC 0,08 MU/LITE wykonalne z przestrzałem ≤ 1,6×; poniżej 0,04 pomijane nazwy > 600 USD | ryzyko-i-sizing.md (loty) — **wykonalność, nie EV** |
| σ60 (nie σ20) | estymatory σ20/σ60/EWMA mają niemal identyczną moc (korelacja log-σ 0,60/0,60/0,61, n 9049); σ20 dałaby W7 11,7 % vs 8,2 % → strata −12,3 vs −8,7 % | ryzyko-i-sizing.md; C4 |
| próg miękki −10 %/−5 % | P(kill 52 tyg., alfa 0) 54 % → 17 %; koszt in-sample ~0,08 %/tydz. | projektA_boot |
| **bez** 1/σ per noga | Sharpe −19 %, 2/10 nóg pomijane przy 1000 USD | C4; bt_symulacja v8 |
| **bez** REDUCE 50 % per noga | martwy dla MU/LITE/COST/META przy ALLOC ≤ 0,10 (REDUCE_FALLBACK=keep) | ryzyko-i-sizing.md |

### 5.2 Kill switch i polityka wznowienia (**bez dowodu — decyzja**, poza liczbą P(kill))

Dziś po trafieniu bot stoi bezterminowo (app.py ~1485–1503: każdy bieg kończy się na `equity < prog_kill`). Projekt: po KILL bot zapisuje `wykonanie.kill = {data, kapital_pct_szczytu, version}`; handel wraca przy **pierwszej zmianie `version` po ≥ 2 kolejnych sobotach** (cooldown 2 tyg.), z `equity_peak := equity` i `alloc_bot = ALLOC_MIN` przez 4 tygodnie (`KILL_COOLDOWN_WEEKS=2`, `KILL_RESTART_WEEKS_MIN=4`). Przy alfie 0 kill w ciągu roku ma P 6–17 % — polityka wznowienia jest częścią systemu, nie wyjątkiem (C4 §9 pkt 5).

### 5.3 Nowe pole `signals.json["sizing"]` — dokładnie, co zmienić

Pole pisze **rutyna sobotnia** (z `ranking.py`), czyta bot. Format:

```json
"sizing": {"d0": "2026-10-23", "wersja": "2026-W9", "sigma60_unit": 0.0211, "alloc_pct": 0.12,
           "formula": "clip(0.015/(5*sigma60_unit),0.04,0.12)", "zrodlo": "ranking.py 2026-10-18", "ranking_hash": "sha256:…"}
```

**`scripts/waliduj_signals.py`:**
1. `KLUCZE` += `"sizing"`; `DOZWOLONE["sobota"]` += `"sizing"` (Puls nie ma do niego prawa — zmiana przez puls = błąd).
2. W `spojnosc()`: jeśli `sizing` istnieje: `d0 == sig["d0"]["date"]`, `wersja == sig["version"]`, `0 < sigma60_unit < 0.2`, `0.04 ≤ alloc_pct ≤ 0.12`, `|alloc_pct − clip(0.015/(5·sigma60_unit), 0.04, 0.12)| ≤ 1e-4`, `ranking_hash` niepuste.
3. W `porownaj()` dla soboty: `sizing` zmienione **tylko** razem z `version`; brak pola przy zmianie `version` = problem („nowa version bez sizing”) — od W9.
4. Testy: 6 przypadków (brak pola / złe d0 / alloc poza zakresem / alloc niezgodny z formułą / zmiana przez puls / zmiana bez version) w `scripts/test_app.py` (sekcja walidatora) lub nowym `scripts/test_waliduj.py`.

**`app.py::_sanity`:** jeżeli `"sizing" in sig`: te same kontrole zakresu i formuły; błąd → `problemy.append(...)` → **handel wstrzymany** (jak przy złym koszyku — zły parametr ryzyka jest groźniejszy niż zły ticker). Brak pola → dozwolony (zgodność wstecz), bot używa `SIZING_FALLBACK_PCT=0.06`.

**`app.py::sync()`** (po `rep["kontrola_kapitalu"]`): `alloc = min(ALLOC_PCT, sizing.alloc_pct if sizing valid and sizing.d0 == sig["d0"]["date"] else SIZING_FALLBACK_PCT)`; `if not zgodne: alloc = min(alloc, ALLOC_PCT_SAFE)`; `alloc *= soft_factor` (stan w `wykonanie.soft = {"aktywny": bool, "od": data}`); `rep["alloc_pct"]`, `rep["alloc_zrodlo"]`. `/status.ustawienia` dodaje `sizing`, `soft`, `alloc_efektywny`.

**CLAUDE.md:** w „Co wolno”: raport tygodniowy pisze także `sizing`; `wykonanie` zyskuje podklucze `stopy`, `soft`, `kill` (pisze bot); tabela `/status`: wiersz `sizing`.

### 5.4 MAX_EXPOSURE_STEP i zmiana skali

`MAX_EXPOSURE_STEP` liczony wobec całej książki, gdy `alloc_bot` różni się od `wykonanie.alloc_ostatni` o > 0,02 (zmiana skali rozkłada się na biegi 17:05); zasada w INSTRUKCJA: `ALLOC_PCT` (sufit) zmienia się krokiem ≤ 0,04 na 4 tygodnie. Liczba: podwojenie 3.10 (0,12 → 0,24) weszło od razu na 100 % celu nowych nóg i dało W6–W7 −24,9 % zamiast ~−15,5 % przy 0,15 (wykonanie-bota.md).

---

## 6. Stopy

| element | projekt | liczba |
|---|---|---|
| próg | `stop_i = clip(2 · σ60_i · √5, 0,08, 0,20)` z `data/ranking-<version>.json["ranking"][i].sigma60` (bot czyta plik z repo przez `gh_get_file`; brak → `STOP_LOSS_PCT=0.10`) | σ-stop Δ −0,002 (t −0,06), σ −1 %, p5 +0,5 p.p.; 10 % trafia „przez przypadek” w 15–24 % tygodni dla σ 4–6 %/d, dla PEP = 3,6σ (martwy) |
| kotwica | `fills[t]["cena"]` **przed** `p["wejscie"]` (zgodnie z docstringiem i CLAUDE.md) | MU 13.10 zamknięty stopem +4,4 % nad ceną tezy przez kotwicę brokera po wyrównaniu; C3 ostrzega tylko przed kotwicą D0 (nie dotyczy fills) — **decyzja o spójności z pomiarem Pulsu, EV nieustalone** |
| reopen | **brak**: po stopie bot zapisuje `wykonanie.stopy[ticker] = {wersja, data, poziom, kierunek}`; `desired_book` pomija ticker z wpisem o bieżącej `version`; rotacja czyści | reopen W7: oddał 2,3–3,3 % kapitału; v4 vs v3 +0,10 brutto minus drugi spread ≈ 0; księgowo pewny zysk ze spreadu |
| asymetria L/S | nie wprowadzamy (jeden wzór) | C3: koszt stopu z nóg LONG, na SHORT ≈ 0 — ale σ-stop i tak daje szerszy próg nogom o wysokiej σ (LITE 20 %) i ciasny defensywom (PEP 8 %) |
| pomiar | w `wykonanie.stopy` bot loguje poziom i czas; sobota liczy „zwrot nogi od stopu do rotacji” osobno L/S; ocena po 30 stopach | C3 §6 |

---

## 7. Puls, reżim, taktyczne, deklaracje — decyzje

### 7.1 Puls dzienny = raport kontrolny, nie decydent

| funkcja Pulsu | decyzja | liczba |
|---|---|---|
| wyzwalacze cenowe 4 %/8 % (basis `cena`) | **usunięte**; sekcja KONTROLA BRAMKI zostaje jako pomiar ex post (co by zrobiła) | C7: EV ±0,15, ogon ≤ 1 p.p., P(kill) −1,4 pkt; w W6–W7 0 wykonanych reakcji (stop pierwszy) |
| basis `rekom` (elita), `short` (short interest) | **usunięte** | nieweryfikowalne z środowiska (R9), brak jakiegokolwiek testu; 1 z 8 wpisów Pulsu wykonany |
| basis `news` — lista zamknięta: wezwanie/oferta z ceną, delisting/zawieszenie, raport/guidance z dokumentem źródłowym, decyzja regulatora | **zostaje** (R3) | **bez dowodu — decyzja o ogonie**; 3 użycia, +0,69 p.p. na papierze |
| blokada sektorowa | bez przedmiotu (nie ma wyzwalaczy cenowych) → usunięta | n = 2 o przeciwnych znakach |
| wyłącznik płynności | sesja ^NDX ≤ −5 % lub VIX > 40 → `status NIEAKTUALNA` do najbliższej soboty | **bez dowodu — decyzja**; C8: ryzyko kill siedzi w P0, więc to ubezpieczenie od zdarzeń typu 2020, nie od W7 |
| kontrola rachunku `/status` | bez zmian + nowe pola `sizing`, `soft`, `stopy` | CLAUDE.md |
| pomiar diagnostyczny | spread od fills i od D0; σ zrealizowana tygodnia vs σ60 ex ante; alloc efektywny vs `sizing.alloc_pct`; stopy; pokrycie | KROK A soboty czyta te sekcje |

Puls pisze w `signals.json` wyłącznie `status` (P2/płynność), `exclude` (tylko basis `news`), `tactical=[]`, `last_daily`. Zwykle zmienia tylko `last_daily`.

### 7.2 Reżim

P1 (NDX < MA200 ∨ DD > 10 % ∨ VIX > 28): **flaga w raporcie, bez REDUCE** (R5' uchylona: tygodnie P1 najlepsze dla momentum +3,04, t 2,0; bramka 1,00 → 0,78). P2 (sobota): DD ^NDX > 20 % od maks. 252 sesji → `status NIEAKTUALNA` i koszyk na papierze; powrót w pierwszą sobotę z DD ≤ 20 % (bez histerezy: C8 — histereza kosztuje 10 tyg. odbić po +3,8…+5,8 %). VIX > 40 / sesja ≤ −5 % tylko jako wyłącznik Pulsu (7.1). Redukcję ekspozycji w podwyższonej zmienności robi σ60 w sizingu.

### 7.3 Moduł taktyczny — zawieszony

`tactical=[]`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`. Liczby: 4 pozycje (AKAM −3,3, APOG/PENG +0,3, ERIC +4,0 p.p.), 20 % kapitału/noga = σ ≈ 1 % kapitału dziennie bez dowodu; H2 w KANDYDATACH z wymaganym testem na PIT (fwd10 +3,5, t 2,2, n 307; 2022/2026 ujemne dla ≥ +8 % → nie spełnia „znak w ≥ 4/5 lat”). Powrót modułu wyłącznie jako reguła mechaniczna z własnym sizingiem.

### 7.4 Deklaracje D1–D3

Zastąpione wpisem nakładki (N6). D1-W8/D2-W8/D3-W8 rozliczyć 24.10 na papierze i zamknąć serię. Powód: 20 deklaracji → 9/11, 6 reguł po n = 1; „falsyfikacja = KANDYDAT” w reguly.md i tak odbiera im moc zmiany składu, więc jako osobny mechanizm są kosztem czasu bez funkcji.

---

## 8. Rejestr reguł i test przekrojowy

`rutyny/reguly.md` (stan z `b86ef1b`) jest dobrym szkieletem; projekt zmienia **cztery rzeczy**:

1. **Uniwersum testu = PIT** (`dane/closes_5y.csv` + `dane/dropped_closes.csv` + tabele dat z `weryfikacja_C1.py`), nie skład dzisiejszy: różnica dla momentum 1,01 → 0,71 (t 2,09 → 1,55); dla K10 na PIT koszt rośnie (−0,70, t −2,73). Skrypt testu trafia do repo jako `scripts/test_regula.py --regula <ID>` z zapisanym wynikiem w rejestrze.
2. **Kryterium awansu** bez zmian (≥ 30 zdarzeń w ≥ 15 tyg., |t| ≥ 2 klastrowane, znak w ≥ 4/5 lat, reguła wiąże) **plus**: test w zbiorze kandydatów bliskim koszykowi (TOP5/TOP10 i BOTTOM5/BOTTOM10, nie tylko kwintyl) — C6 pokazał, że znak reguły odwraca się między kwintylem (−0,16) a TOP5 (+1,68).
3. **Statusy wpisów po tej notatce**: S2 (sizing) i S3 (stop σ) → OBOWIĄZUJĄCE z liczbami z §2.2 (dotąd miały liczby „37–70 %”/„koszt 20 % Sharpe’a”, które C4 obaliła jako pomylenie wariantów); H5 (budżet czynnikowy) → KANDYDAT z adnotacją „PIT: −0,54 (t −2,36) — odrzucony jako koszyk bota, zostaje cieniem”; R3 (news) i K2' (event) → status KONSTRUKCYJNA/„bez dowodu — decyzja”; R8 (veto krypto-beta/governance) → KONSTRUKCYJNA, test po 30 zdarzeniach; nowe: N1–N6 (nakładka), S4 (próg miękki −10 %), S5 (polityka wznowienia), P2' (reżim tylko DD > 20 %).
4. **Stała tabela raportu „REGUŁY — kontrola”**: które veta wiązały (nazwy), zwrot wykluczonych vs zamienników (mediana i lista, nie tylko średnia — C6 §7), koszt skumulowany; żaden wpis bez tej tabeli.

Moratorium: do 26 okien cieni (ok. kwiecień 2027) żadna nowa reguła koszykowa nie wchodzi do OBOWIĄZUJĄCYCH; jedyny ruch dozwolony to **uchylenie** reguły, której test PIT daje |t| ≥ 2 przeciw.

---

## 9. Rutyny po zmianie

### 9.1 Sobota (`rutyny/tygodniowa.md`) — nowy przebieg (ok. 25 min, ≤ 12 wywołań TV)

| krok | treść | zmiana wobec dziś |
|---|---|---|
| 0 | `signals.json`, `fills`, `wykonanie` (stopy, soft, kill), `reguly.md` sekcja OBOWIĄZUJĄCE + WYJĄTKI; guard podwójnego biegu | + `wykonanie.stopy/soft/kill`; reguły z pliku, nie z pamięci |
| 0b | TV: **tylko** run-screener (snapshot `data/tv-screen-<version>.json` — taksonomia dla cieni B/C), get-earnings-calendar (TOP15/BOTTOM15, ≤ 2 wywołania), get-dividends-calendar (20 nóg), get-ohlcv NDX/VIX (reżim, 2 wywołania); **skreślone**: get-forecasts, get-financial-history, get-documents, newsy, panel fundamentów | budżet 50 → 12 wywołań; TV = dane wejściowe skryptu |
| A | rozliczenie: `koszyki_cienie.py --ranking data/ranking-<stara version>.json --closes … --do <piątek> --faktyczny-long … --log data/koszyki-cienie.jsonl` → spread_pp A0/A/B/C/D/ETF/FAKT od D0 i od fills; `delta_nakladki_pp`; σ zrealizowana vs σ60 ex ante; stopy (zwrot od stopu do rotacji); `koszt_wykonania_pp = wynik rachunku % − 5·alloc·spread_fills_pp` (z `/status`, tylko w raporcie); wpis `history` jak dziś + `nakladka_pp` (pole dodatkowe; walidator wymaga tylko zestawu HISTORY_POLA) | zastępuje managed/reaction (= 0 bez wyzwalaczy); hit rate liczony vs **mediana uniwersum** (baza 31–76 % vs ^NDX) |
| A2 | kontrola pokrycia `/status` (bez zmian) + `alloc efektywny` vs `sizing.alloc_pct`, stan `soft` | — |
| B0 | reżim: tylko DD > 20 % → P2 (status NIEAKTUALNA); P1 flaga | 7.2 |
| B | `python3 scripts/ranking.py --fetch --tv data/tv-screen-<version>.json --earnings <scratch>/earnings.json --exclude <WYJĄTKI z reguly.md> --out data/ranking-<version>.json --md <scratch>/ranking.md` → koszyk A, `sizing`, cienie | zastępuje B1–B4 w całości |
| B+ | NAKŁADKA (opcjonalna): ≤ 1 wymiana/stronę z rang 6–15 wg N1–N3; wpis do `ranking-<version>.json["nakladka"]` z liczbą i źródłem; **domyślnie brak wymiany** | zastępuje Model 3.0 |
| C | raport HTML: rozliczenie (tabela cieni + Δ nakładki kumulatywnie z t i n), REGUŁY — kontrola, ranking TOP15/BOTTOM15 z czynnikami i wetami (z MD skryptu), koszyk A + nakładka, `sizing` (σ60_unit, percentyl vs losowe, ALLOC, σ dz. kapitału przy ALLOC), ekspozycje b_SOX/b_DEF/β (**adnotacja, nie bramka**), stopka: „ALLOC z pola sizing = X; sufit 0,12; 1 p.p. spreadu = 5·ALLOC % kapitału”; zdanie o horyzoncie dowodu („n = k tygodni; przy σ 6,7 p.p. test wykrywa |μ| ≥ 2·6,7/√k”) | bez p, bez elity, bez pre-mortemu |
| D | `signals.json`: version, status, long, short (= A + nakładka), d0, generated, exclude=[], tactical=[], history (+1), **sizing**; `python3 -I scripts/waliduj_signals.py --diff HEAD --rutyna sobota`; commit z hashem `ranking-<version>.json`; w commicie dozwolone dodatkowo: `data/ranking-<version>.json`, `data/ranking-cache.csv`, `data/koszyki-cienie.jsonl`, `data/tv-screen-<version>.json`, `data/tv-log.jsonl` | + sizing, + ranking, + cienie |
| E | wiadomość: spread A/FAKT rozliczonego tygodnia, Δ nakładki, nowy koszyk, ALLOC, ścieżka raportu | — |

### 9.2 Puls (`rutyny/dzienna.md`) — nowy przebieg (ok. 10 min, ≤ 8 wywołań TV)

KROK 0 (stan + `wykonanie.stopy/soft`), 0b (TV: batch kursów ≤ 3, get-ohlcv NDX/VIX 2, get-earnings-calendar 1, get-news tylko dla nogi z ruchem ≥ 5 % przeciw tezie ≤ 2), 1 (kursy i zwroty od fills i od D0; kalendarz dnia; **bez** researchu elity, FINRA, makro-narracji), 1b (`/status` bez zmian), 2 (werdykt: `status` = NIEAKTUALNA tylko przy wyłączniku płynności lub przeniesionym P2; `exclude` tylko basis `news` z listy zamkniętej **z dokumentem źródłowym**; `tactical=[]`), 3 (raport: tabele koszyków, pasek spread ×2, KONTROLA BRAMKI jako **pomiar** „co zrobiłby protokół 4/8” bez wpisu, KILL SWITCH z `soft`, KONTROLA RACHUNKU, ŹRÓDŁA), 4 (walidator `--rutyna puls`, commit), 5 (wiadomość).

Skreślone akapity dzienna.md: ELITA ANALITYKÓW, TRZY WARUNKI DLA WYZWALACZY CENOWYCH, BLOKADA SEKTOROWA (jako warunek), MODUŁ TAKTYCZNY, WYKONALNOŚĆ, LICZNIK HISTEREZY, działania P1 (REDUCE wszystkich).

---

## 10. Pętla uczenia: koszyki cienie i prerejestrowane metryki

### 10.1 Koszyki cienie (co sobotę, jeden skrypt, `data/koszyki-cienie.jsonl`)

| cień | po co | metryka decyzyjna |
|---|---|---|
| A0 (bez wet) | koszt wet S1/K13/EVENT | Δ(A − A0): po 26 oknach jeśli t ≤ −1,5 → veto konstrukcyjne (S1/EVENT) do przeglądu (K13 zostaje — ma własny test) |
| **A** (koszyk rankingowy) | baza | σ zreal. vs σ60 ex ante (kalibracja sizingu: mediana zrealizowana/prognoza 0,83 w panelu) |
| FAKT (A + nakładka) | nakładka | Δ(FAKT − A): N5 |
| B, C, D | hipotezy H4/H5 | test F wariancji po 12 oknach (σ_D/σ_A oczekiwane 0,76); średnia tylko jako CI; żadna nie wchodzi do bota przed 52 oknami i t(Δ) ≥ 2 **na PIT** (nie na cieniach) |
| ETF SMH/XLP | czynnik taniej | czy A bije czysty czynnik: Δ(A − ETF) — po 52 oknach |
| „A bez veta EVENT” | koszt K2' | Δ po 26 oknach |

### 10.2 Metryki prerejestrowane (stała kolejność w raporcie; nic nie dopisujemy w trakcie)

1. `spread_pp` od D0 i `spread_fills_pp` od wejścia (A i FAKT), narastająco: suma, średnia, σ, t, n.
2. `delta_nakladki_pp`, narastająco z t.
3. σ zrealizowana tygodnia kapitału vs cel 3,35 %; `alloc` użyty; stan `soft`; DD od szczytu.
4. Ekspozycja: b_SOX, b_DEF, β net ex ante (adnotacja) i zrealizowany udział czynnika w wyniku tygodnia.
5. Stopy: liczba, zwrot od stopu do rotacji (L/S).
6. `koszt_wykonania_pp` (rachunek vs model) — mediana krocząca 12 tyg.
7. REGUŁY — kontrola (które wiązały, koszt).
8. Zdanie o mocy: „po n tygodniach test wykrywa |μ| ≥ 2·σ̂/√n p.p./tydz.; obecnie: …”.

### 10.3 Kryteria decyzji

| horyzont | wolno rozstrzygnąć | kryterium | działanie |
|---|---|---|---|
| 12 okien (ok. 16.01.2027) | wariancja i wykonanie | σ zreal. kapitału w [0,7; 1,4] × cel; test F σ_FAKT vs σ_A; mediana `koszt_wykonania_pp`; liczba stopów vs oczekiwane 0,25/tydz. | kalibracja celu σ (nie progów); jeśli koszt wykonania > 0,3 %/tydz. → audyt wykonania (nie zmiana selekcji) |
| 26 okien (ok. kwiecień 2027) | nakładka, veta konstrukcyjne | N5 (t(Δ) ≤ −1 → nakładka off); Δ(A − A0) t ≤ −1,5 → przegląd S1/EVENT; test F dla B/C/D | moratorium reguł kończy się; możliwe uchylenia |
| 52 okna (ok. październik 2027) | czynnik (tylko jako CI), cienie B/C/D/ETF | CI 95 % średniej A netto; jeśli górna granica < 0 → system na papier / decyzja właściciela o ETF; cień z t(Δ) ≥ 2 na cieniach **i** t ≥ 2 na PIT → może zastąpić A | zmiana konstrukcji bota wyłącznie tu |

Nigdy: zmiana parametrów rankingu, progów sizingu czy stopu „po złym tygodniu”; zmiana wag wg wyniku W_k.

---

## 11. Pełna lista zmian w plikach (z właścicielem)

| # | plik | zmiana | właściciel |
|---|---|---|---|
| 1 | `rutyny/tygodniowa.md` | nowy przebieg §9.1: KROK B = `ranking.py`, B+ nakładka N1–N6, KROK A = `koszyki_cienie.py` + metryki §10.2, KROK C bez p/elity/pre-mortemu, KROK D + `sizing` i pliki `data/ranking-*`, `koszyki-cienie.jsonl`; skreślone B0b, B1–B4, elita, deklaracje D1–D3, benchmark liczony ręcznie | rutyna |
| 2 | `rutyny/dzienna.md` | §9.2: usunięte wyzwalacze cenowe/rekom/short, blokada sektorowa jako warunek, moduł taktyczny, licznik histerezy, działania P1; KONTROLA BRAMKI jako pomiar; wyłącznik płynności; odczyt `wykonanie.stopy/soft/kill`; `exclude` tylko basis news z dokumentem | rutyna |
| 3 | `rutyny/reguly.md` | §8 pkt 3: statusy S2/S3 z liczbami §2.2, H5 odrzucony jako koszyk (cień), nowe N1–N6, S4, S5, P2'; test na PIT; tabela „REGUŁY — kontrola” | rutyna |
| 4 | `rutyny/tradingview.md` | budżety: sobota 12 wywołań/10 min, puls 8/5 min; allowlista bez get-forecasts/get-financial-history/get-documents w sobocie; `data/tv-config.json` flagi `b1_z_tv`, `kryterium_event_remis`, `event_blokada_taktycznej`, `rezim_surowszy` → bez przedmiotu (opis) | rutyna |
| 5 | `scripts/ranking.py` | blok `nakladka` w JSON (schemat N2, walidacja rang 6–15 i braku veta), blok `sizing` wg §5.3 (+ `ranking_hash` = sha256 pliku cache), `--pit` (opcjonalnie), zapis `sigma60` per ticker już jest; testy w `scripts/test_ranking.py` (+5) | kod app.py |
| 6 | `scripts/koszyki_cienie.py` | cienie A0, ETF (SMH/XLP z cache), „A bez EVENT”; `delta_nakladki_pp`; seria od `fills` (odczyt `signals.json`); zwrot od stopu do rotacji z `wykonanie.stopy`; kumulacje (suma, t, n) z `data/koszyki-cienie.jsonl` | kod app.py |
| 7 | `scripts/test_regula.py` (nowy) | harness PIT (z `weryfikacja_C1.py`: `build`, `windows`, tabele JOIN/LEAVE) + `dane/dropped_closes.csv` w `data/`; test reguły wg kryterium §8 z wynikiem do rejestru | kod app.py |
| 8 | `scripts/waliduj_signals.py` | §5.3 pkt 1–3: `sizing` (KLUCZE, DOZWOLONE sobota, spójność, zmiana tylko z version); `BASIS` zawęża się do `{"news", "rezim", "reżim"}` dla **nowych** wpisów (stare basis `cena` w bazie tolerowane); testy (+6) | walidator |
| 9 | `app.py` — `_sanity` | kontrola `sizing` (zakres, formuła, d0) → błąd = handel wstrzymany; brak pola dozwolony | kod app.py |
| 10 | `app.py` — `sync()` alokacja | `alloc = min(ALLOC_PCT, sizing.alloc_pct lub SIZING_FALLBACK_PCT) × soft_factor`, potem `ALLOC_PCT_SAFE`; `wykonanie.soft`; `MAX_EXPOSURE_STEP` wobec całej książki przy zmianie skali > 0,02 | kod app.py |
| 11 | `app.py` — `stopy_bezpieczenstwa` | próg per noga z `ranking-<version>.json["ranking"][t].sigma60` (`gh_get_file`, cache w biegu): `clip(STOP_SIGMA_MULT·σ60·√5, STOP_LOSS_MIN, STOP_LOSS_MAX)`; kotwica `fills[t]["cena"]` przed `p["wejscie"]`; po stopie `wykonanie.stopy[t] = {wersja, data, poziom, kierunek, cena_stopu}`; `desired_book` pomija ticker z wpisem o bieżącej `version` | kod app.py |
| 12 | `app.py` — kill switch | `wykonanie.kill`; wznowienie: po `KILL_COOLDOWN_WEEKS=2` i zmianie `version` → `equity_peak := equity`, `alloc = ALLOC_MIN` przez `KILL_RESTART_WEEKS_MIN=4` | kod app.py |
| 13 | `app.py` — `/status` | `ustawienia.sizing`, `soft`, `alloc_efektywny`, `stopy` (lista), `kill` | kod app.py |
| 14 | `app.py` — zmienne | nowe: `SIZING_FALLBACK_PCT=0.06`, `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `DD_SOFT_FACTOR=0.5`, `STOP_SIGMA_MULT=2.0`, `STOP_LOSS_MIN=0.08`, `STOP_LOSS_MAX=0.20`, `STOP_REOPEN=false`, `KILL_COOLDOWN_WEEKS=2`, `KILL_RESTART_WEEKS_MIN=4`; `REACT_GATE` bez przedmiotu (zostaje dla zgodności) | kod app.py |
| 15 | `scripts/test_app.py` | testy: alokacja z `sizing` (brak/zły/zgodny, sufit, soft on/off, SAFE), σ-stop (próg per noga, kotwica fills, brak reopen przez `wykonanie.stopy`, czyszczenie po rotacji), kill-resume, `_sanity(sizing)`; cel 151 → ~175 OK | kod app.py |
| 16 | `CLAUDE.md` | pola soboty + `sizing`; `wykonanie` z podkluczami bota `stopy/soft/kill`; tabela `/status` + `sizing`; sekcja „Koszyk = ranking.py; nakładka ≤ 1/stronę”; `data/ranking-*.json`, `koszyki-cienie.jsonl` bez liczb z rachunku; `dane/dropped_closes.csv` jako część uniwersum testowego | rutyna |
| 17 | `INSTRUKCJA.md` | §2 nowe zmienne (tabela z #14), §3 pole `sizing` i podklucze `wykonanie`, §8 rewizja („dwa progi” → „bramka Pulsu wycofana, pomiar zostaje”), nowy § „Polityka wznowienia po kill switchu” i „ALLOC_PCT krokiem ≤ 0,04/4 tyg.” | kod app.py |
| 18 | panel Render — natychmiast (przed pon. 19.10 13:45 UTC) | `ALLOC_PCT=0.08`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`, `START_EQUITY` ≤ bieżący kapitał (razem z resetem `equity_peak`, §12) | właściciel (Render/decyzja) |
| 19 | panel Render — po wdrożeniu kodu (przed sobotą 24.10) | `ALLOC_PCT=0.12` (sufit), `SIZING_FALLBACK_PCT=0.06`, `STOP_LOSS_PCT=0.10` (fallback), `STOP_SIGMA_MULT=2.0`, `STOP_LOSS_MIN=0.08`, `STOP_LOSS_MAX=0.20`, `STOP_REOPEN=false`, `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `KILL_COOLDOWN_WEEKS=2`, `KILL_RESTART_WEEKS_MIN=4`, `REDUCE_FALLBACK=close` | właściciel (Render/decyzja) |
| 20 | `signals.json` — `equity_peak` | ręczny commit właściciela: `equity_peak := bieżący kapitał` (pole bota; rutyny nie dotykają) — **decyzja** | właściciel (Render/decyzja) |
| 21 | `data/` | `data/ranking-cache.csv`, `data/ranking-<version>.json`, `data/koszyki-cienie.jsonl`, `data/dropped_closes.csv`; `data/tv-config.json` budżety | rutyna |
| 22 | zadania claude.ai/code/routines | wklejenie nowych treści obu rutyn po commicie (zasada: plik → zadanie) | właściciel (Render/decyzja) |

Kolejność wdrożenia: #18 + #20 (niedziela 19.10) → #5, #6, #8, #9–#15 z testami (do czwartku 23.10) → #16, #17, #3, #4 → #1, #2 + #22 (piątek 23.10) → #19 (piątek po deployu) → pierwszy bieg mechaniczny sobota 24.10 (W9). Jeśli kod nie zdąży do 24.10: sobota biegnie według nowej rutyny, `sizing` liczy skrypt, a `ALLOC_PCT` ustawia właściciel ręcznie z raportu (wariant przejściowy z ryzykiem błędu ręcznego — ryzyko-i-sizing.md).

---

## 12. Plan migracji

### 12.1 Teraz: 18–19.10 (kapitał ≈ 1,7 % nad progiem; W8 rusza 19.10 13:45 UTC)

| opcja | poduszka | P(kill): pon. 13:45 na książce W7 / 5 ses. / 20 ses. (ALLOC W8 0,08) | ocena |
|---|---|---|---|
| (0) nic | 1,7 % | 21 % / 35 % / 54 % (przy 0,24: 21 % / 55 % / 76 %) | bootstrap tej notatki: 68–85 % w 4 tyg. dla **każdej** polityki |
| (a) `equity_peak := kapitał`, `START_EQUITY` 1000 bez zmian → odniesienie = START_EQUITY | 11,0 % | 0 % / 0 % / 0 % (0,08); 4 / 11 / 24 % (0,24) | połowiczne: odniesienie to stała z Rendera |
| **(c) `equity_peak := kapitał` ORAZ `START_EQUITY` ≤ kapitał** | 33 % | **0 % / 0 % / 1 %** (0,08) | zalecane; wymaga `START_EQUITY ≤ nowy equity_peak`, inaczej bot nadpisze szczyt (app.py:1960) |
| (d)/(e) `KILL_LEVEL` 0,70 / 0,65 | 8,9 / 17,3 % | 0 % / 0 % / 1 % (0,08, e) | przesuwanie progu po stracie — odradzane (wykonanie-bota.md) |

Źródła: C9 §2–§6; projektA_boot „start ≈ 1,7 %”. **Rekomendacja (decyzja właściciela, nie dowód):** opcja (c) + `ALLOC_PCT=0.08` + `TACTICAL_ENABLED=false` przed 19.10 13:45 UTC. Uzasadnienie liczbowe: restart teraz = kapitał/szczyt ≈ 0,761 pewny vs rozkład dwumodalny przy czekaniu (kill ~0,74 albo gra; E[kapitał] identyczny, C9 §6). Reset szczytu jest jawnym uznaniem kill switcha za zadziałany (ryzyko-i-sizing.md).

W8 zostaje koszykiem Modelu 3.0 (już scommitowany, D0 16.10): to **pierwszy tydzień pomiaru cieni**. Cienie dla W8 (`projektA_ranking_W8.json`, D0 2026-10-16, ranking z vetem S1 — MRNA σ60 23,5 % poza):

| koszyk | LONG | SHORT | σ60 tyg. (p.p.) | percentyl vs losowe | b_SOX net | ALLOC z reguły |
|---|---|---|---|---|---|---|
| A | CRWD DDOG PANW FTNT AMD | NFLX FER APP ALNY CMCSA | 8,06 | 88,9 | +0,40 | 0,083 |
| D | CRWD DDOG PANW FTNT WDAY | NFLX FER APP ALNY CMCSA | 7,37 | 89,2 | −0,12 | 0,091 |
| B | CRWD AMD FTNT SNDK TRI | APP AVGO PAYX AXON NFLX | 5,91 | 84,1 | +0,70 | 0,114 |
| FAKT (W8, Model 3.0) | GOOGL GILD MSFT QCOM ADP | AXON DASH ALNY APP FER | σ_d 2,22 % przy 0,24 → ~4,2 p.p. | 44 | +0,29 | cap 0,12 |

Uwaga do W8: shorty AXON (pct mom6 67,7) i DASH (73,7) to shortowanie liderów momentum — przekrój: noga SHORT odwrócenia −0,69 p.p./tydz. (hit 48 %). Nie zmieniamy W8 (zmiana koszyka poza sobotą łamie konwencję pól i rozliczeń); zapisujemy to jako pierwszą obserwację Δ(FAKT − A).

### 12.2 W9 (sobota 24.10) — pierwszy bieg mechaniczny

Kolejność z §11. Oczekiwane dla W9 przy σ60_unit podobnej do A-W8 (8,06 p.p. tyg. → σ_unit 1,6 %/d): ALLOC ≈ 0,08, gross ≈ 80 %, σ dz. kapitału ≈ 1,5 %. Nakładka: domyślnie brak wymiany; jeżeli rutyna zrobi wymianę — z liczbą i źródłem.

### 12.3 Tygodnie 1–12 (do 16.01.2027)

- Bez zmian parametrów. Raport co sobotę z metrykami §10.2.
- Kontrola wykonania: nowe nogi wchodzą o 13:45 w pełnym rozmiarze? (hipoteza stopy depozytu z wykonanie-bota.md — potwierdzić logiem `/run` z 19.10 i 26.10; jeśli potwierdzona: poprawka `sync()` mianownika stopy depozytu, osobne wdrożenie).
- Po 12 oknach: decyzje z §10.3 (tylko wariancja/wykonanie).

### 12.4 Co może przerwać migrację

| ryzyko | reakcja |
|---|---|
| kod nie gotowy na 24.10 | sobota liczy `sizing` skryptem, właściciel ustawia `ALLOC_PCT` ręcznie z raportu; stop zostaje 10 % z reopen (koszt −0,19 p.p./tydz. wg C3) — tydzień do dwóch |
| `ranking.py --fetch` bez danych (Yahoo) | TV get-ohlcv jako rezerwa 1y dla brakujących nazw (allowlista), adnotacja; brak > 10 % uniwersum → koszyk poprzedni zostaje (`version` bez zmiany, raport z PROBLEMY) |
| kill w W8 mimo resetu | polityka wznowienia §5.2 (do czasu kodu: ręczna wg tej samej reguły) |

---

## 13. Oczekiwane metryki (prerejestrowane; konstrukcja A, PIT, vt+soft)

| metryka | wartość oczekiwana | przedział / warunek | źródło |
|---|---|---|---|
| μ spreadu tyg. (brutto, równe wagi) | +0,60 p.p. | 95 % CI ≈ −0,26…+1,46 (σ 6,70, n 233); ex ante netto +0,1…+0,5 z zerem w CI | projektA_bt; C1 |
| σ spreadu tyg. | 6,7 p.p. | p5 −10,3; najgorszy −23,9; 2026: ~11 (reżim) | projektA_bt; bt_momentum |
| hit tygodni / nóg | 56 % / ~53 % | baza losowa 50 % | projektA_bt; bt_momentum |
| ALLOC z reguły | mediana 0,12 (PIT), w reżimie 2026: 0,05–0,08 | p5 0,053 | projektA_bt |
| σ dz. / tyg. kapitału | 0,8–0,9 % / 1,6–1,9 % | cel 1,5 %/d przed progiem miękkim; zrealizowane/prognoza 0,83 (panel) | projektA_bt; ryzyko-i-sizing |
| μ tyg. kapitału | −0,12 % (alfa 0) … +0,04 % (in-sample) | koszty ≈ 0,15–0,2 %/tydz. (finansowanie 6 % × gross ~1,0 + rotacja 2,3 nogi) | projektA_bt |
| P(kill −25 %, 12 tyg.) | 0 % | bootstrap, każde alfa | projektA_boot |
| P(kill, 52 tyg.) | 17 % (alfa 0) / 10 % (+0,3) / 6 % (in-sample) | vs 98 % przy 0,24 | projektA_boot |
| maxDD 52 tyg. | mediana −19 %, p95 −30 % | vs −55 % / −79 % przy 0,24 | projektA_boot |
| stopy | ~0,25/tydz.; Δ EV −0,002 p.p./tydz. | kotwica fills, bez reopen | projektA_bt |
| Δ nakładki | 0 ± 1,8 p.p./tydz. | po 26 tyg. wykrywalne |Δ| ≥ 0,71 | projektA_bt |
| obrót | 2,3 nogi/tydz. (+ zmiana skali) | vs 5–9 nóg/tydz. z K10 | projektA_bt; audyt-regul |
| koszty roczne | ~8–10 % kapitału | vs 25–64 % przy gross 240 % | wykonanie-bota.md (parametryczne) |

---

## 14. Główne ryzyka projektu

1. **Alfa może być zerem lub ujemna** (PIT netto CI −0,39…+1,34; 2023 i 2024 ujemne) — projekt przeżyje (P(kill 52) 17 %), ale będzie tracił ~0,12 %/tydz. na kosztach; kryterium 52 okien (§10.3) musi być egzekwowane.
2. **Ekspozycja czynnikowa pozostaje** (b_SOX zreal. +0,91): tydzień typu W7 przy ALLOC 0,08 to ≈ −8…−10 % kapitału (5·0,08·(−21…−24 p.p.)); próg miękki zadziała dopiero po nim.
3. **Momentum 6M skip 5 jest szczytem siatki** (C1 §e): realny wynik może być bliżej mediany siatki PIT (+0,3 brutto).
4. **Nakładka jest niemierzalna w horyzoncie roku** poza katastrofą (|Δ| ≥ 0,5 wymaga 52 tyg.); jej jedyną ochroną jest budżet N1 i zakazy N3.
5. **Wykonalność przy małym kapitale**: ALLOC 0,04–0,06 × nazwy > 600 USD → pomijane nogi (ASML, MELI, SNDK) — koszyk 9/10; rozwiązanie wymaga kapitału ~2 500 USD (C4) albo veta kursowego (koszt do zmierzenia).
6. **Zależność od danych Yahoo** (`--fetch`) i snapshotu TV dla cieni; brak snapshotu = cienie B/C bez taksonomii (adnotacja, nie blokada).
7. **Ryzyko procesu**: trzy pliki rutyn i walidator muszą zmienić się razem; pole `sizing` bez zmiany `_sanity` = bot ignoruje sizing i gra `ALLOC_PCT` — stąd sufit 0,12 w Renderze jako zabezpieczenie niezależne od kodu.
8. **Survivorship w cieniach i testach**: PIT koryguje 28 nazw, 6 niedostępnych (WBA, AZN, ANSS, SPLK, SGEN, ATVI) — PIT to raczej dolne oszacowanie korekty dla shortów (C1 §Implikacja 3).

---

## 15. Źródła

Fazy 1–2: `_faza1_wyniki.txt` (dekompozycja-wynikow.md, wykonanie-bota.md, moc-predykcyjna-modelu.md, audyt-regul.md, perspektywa-quant.md, ryzyko-i-sizing.md), `_faza2_wyniki.txt` (bt_momentum.md, bt_odwrocenie.md, bt_neutralnosc.md, bt_rezim-i-zaklad-czynnikowy.md, bt_symulacja-wykonania.md). Weryfikacje: `weryfikacja-C1.md` … `weryfikacja-C8.md`, `weryfikacja_C9_out.md`. Nowe: `projektA_bt.py`, `projektA_boot.py`, `projektA_ranking_W8.json`. Repo: `scripts/ranking.py`, `scripts/koszyki_cienie.py`, `rutyny/reguly.md`, `rutyny/tygodniowa.md`, `rutyny/dzienna.md`, `scripts/waliduj_signals.py`, `app.py` (`_sanity` 349–388, `bramka_reakcji` 1218, `stopy_bezpieczenstwa` 1290, `desired_book` 1315, kill 1485–1503, `equity_peak` 1945–1961), `CLAUDE.md`, `INSTRUKCJA.md` §2–3, §8. Dane: `dane/closes_5y.csv`, `dane/dropped_closes.csv` (PIT), `data/tv-screen-2026-W8.json`.
