# Weryfikacja C8 — bramka reżimu P0/P1/P2 a momentum 6M

**Twierdzenie C8:** „Bramka reżimu P0/P1/P2 (NDX<MA200 / DD>10% / VIX>28 → gross 50%; DD>20% / VIX>40 / sesja ≤−5% → 0%) obniża średnią momentum 6M z 1,00 do 0,78 p.p./tydz. bez poprawy maxDD (71→72 pp), bo tygodnie P1 są dla momentum najlepsze (3,04 p.p., t 2,0) a P2 ≈ płaskie; była aktywna w 71/234 tyg. (36 w 2022)."

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Liczby twierdzenia się odtwarzają (stany bramki identyczne z serią fazy 2 — `assert` w skrypcie), a wniosek „bramka nie jest warta kosztu średniej" broni się także w jednostkach kapitału i wobec kontroli iso-gross. Zastrzeżenie: „bez poprawy maxDD" jest prawdą tylko dla maxDD pełnej ścieżki (zdominowanego przez epizod 2026 w P0); bramka **usuwa trafienie kill switcha w 2022 r.** (okna 12-tyg. z killem startujące w 2022: 20/37 → 0/37; P(kill 12 t.) ogółem 42% → 31%), czego miara w pp spreadu nie pokazuje. Ale ten sam efekt — i lepszy — daje zwykłe obniżenie ALLOC do tej samej średniej ekspozycji, więc bramka nie jest racjonalnym narzędziem ubezpieczeniowym.

## Pliki

| plik | zawartość |
|---|---|
| `weryfikacja_C8.py` → `weryfikacja_C8_out.md`, `weryfikacja_C8_wyniki.json`, `weryfikacja_C8_serie.csv`, `weryfikacja_C8_siatka.csv` | symulacja kapitału dzienna (ALLOC 0,24, kill 0,75×szczyt, finansowanie ∝ gross), P(kill) na oknach kroczących, siatka 576 wariantów progów, 500 losowych koszyków |
| `weryfikacja_C8_dod.py` → `weryfikacja_C8_dod_out.md`, `weryfikacja_C8_dod_wyniki.json` | kontrola iso-gross (stały ALLOC 0,178), epizody DD z datami i odrobieniem, tygodnie dodane przez histerezę, 200 losowych koszyków bramka vs iso-gross |

Wszystkie ścieżki w `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`. Dane: `../dane/closes_5y.csv` (1255 sesji, skład dzisiejszy — survivorship bias), koszyki mom6M (TOP5/BOTTOM5 6M, równe wagi) z `bt_rezim-i-zaklad-czynnikowy_serie.csv` (234 okna, D0 2022-04-22 → D5 2026-10-16).

**Konwencja kapitału:** dzienny zwrot = 0,24 × g × (Σ r_long − Σ r_short) − 6%/rok × gross(2,4·g) − 0,10% nominału nogi za zmienioną nazwę i za zmianę gross; g = 1 / 0,5 / 0 wg stanu bramki (odczyt D0 jak w fazie 2 albo DZIENNY jak w Pulsie — stan z zamknięcia poprzedniej sesji). Kill switch: kapitał < 0,75 × kroczący szczyt na zamknięciu, potem płasko. Kapitał startowy 100 (umowny). Kontrola: korelacja tygodniowego zwrotu kapitału z 1,2×spread_pp = 0,9967 (`weryfikacja_C8_out.md`).

## 1. Odtworzenie liczb twierdzenia

| element | twierdzenie | odtworzenie | źródło |
|---|---|---|---|
| aktywna tyg. | 71/234 (36 w 2022) | 71/234 (P1 21, P2 50); 2022: P2 **36 + P1 1 = 37/37** tygodni, śr. gross 2022 = 1% | `_dod_out.md` nagłówek |
| P1 najlepsze | 3,04 pp, t 2,0 | 3,65% kapitału = 3,04 pp, σ 8,16, n 21 → t 2,05; najgorszy tydzień P1 −4,5% | `_out.md` tabela „wg stanu" |
| P2 płaskie | ≈0 | 0,49% kap. (0,41 pp), n 50; w tym 42 tyg. zgodne z progami surowymi: −0,14% (t −0,12) | `_out.md`, `_dod_out.md` |
| średnia ↓ | 1,00 → 0,78 pp | netto w kapitale: 0,85 → 0,69 %/tydz. (hist. D0), 0,72 (hist. dzienna); Sharpe netto 0,668 → 0,613 / 0,636; t 1,42 → 1,30 / 1,35 | `_out.md` TEST 1–2 |
| maxDD bez zmian | 71 → 72 pp | kapitał, bez kill: 69,3% → 69,5% (D0) / 71,7% (dzienna); to epizod 2026-06-22 → 2026-09-14 (58 sesji, **P0**, nieodrobiony do 2026-10-16) | `_dod_out.md` epizody |

Drobna nieścisłość w twierdzeniu: „36 w 2022" to liczba tygodni P2; bramka była aktywna we **wszystkich 37** tygodniach 2022 (P1 w jednym).

## 2. Próby obalenia

### 2a. maxDD w kapitale i czas odrobienia (ALLOC 0,24, bez kill)

Epizody DD ≥20% (`_dod_out.md`):

| wariant | epizod 2022–24 | odrobienie | epizod 2026 | odrobienie |
|---|---|---|---|---|
| bez bramki | szczyt 2022-05-11 → dołek 2024-09-03, **63,4%** (580 sesji) | 689 sesji (~2,7 roku) | 2026-06-22 → 2026-09-14, 69,3% | nie |
| bramka hist. D0 | szczyt 2023-11-10 → 2024-09-03, 50,4% (202 sesje) | 255 sesji | 69,5% | nie |
| stały ALLOC 0,178 (iso-gross) | 2022-05-11 → 2024-09-03, 49,7% | 645 sesji | 56,8% | nie |

Pozostałe epizody (2025-02 39–43%, 2025-10/11 22%, 2026-02 39%, 2026-05 20%) są identyczne lub niemal identyczne z bramką i bez — wszystkie poza 2025-02 i 2026-02 (dołek w P1) wypadają w P0. Wniosek: w kapitale maxDD pełnej ścieżki rzeczywiście nie zmienia się (69→70%), ale **bramka usuwa 2022 z historii strat**: DD w roku 2022 bez bramki 47,2%, z bramką 4,0% (D0) / 1,3% (dzienna) — `_out.md` „Epizod 2022". To, co twierdzenie opisuje jako brak poprawy, jest brakiem poprawy *najgłębszego* epizodu, nie brakiem poprawy ryzyka w ogóle.

### 2b. Sharpe kapitału z finansowaniem ∝ gross

Finansowanie 6%/rok od gross 240% = 14,4%/rok (łączny koszt na ścieżce 87,9 pkt bez bramki vs 80,0 z bramką hist.) — obniżenie gross tnie koszt proporcjonalnie, ale nie ratuje Sharpe'a: 0,668 → 0,613 (hist. D0), 0,636 (hist. dzienna). Warianty bez histerezy są neutralne lub lepsze: surowa D0 0,68, tylko P2→0 0,72, surowa dzienna 0,75 (`_out.md` TEST 1–2). Źródło szkody to histereza: 8 tygodni, w których trzyma P2, gdy progi mówią P1/P0 (powrót po epizodzie), dały momentum **+3,84% kapitału/tydz. (t 1,75)**, a 2 tygodnie P1-po-progach +5,77%; tygodnie P2 zgodne z progami (42) to −0,14% (`_dod_out.md`). Czyli bramka w kształcie z rutyny (z histerezą) wycina właśnie odbicia po kryzysie, w których momentum zarabia najwięcej — to potwierdza mechanizm z twierdzenia i go precyzuje.

### 2c. Warianty progów — czy istnieje wariant poprawiający Sharpe?

Siatka 576 wariantów (P1 VIX ∈ {25,28,30,35}, P1 DD ∈ {10%,15%,wył.}, MA200 tak/nie, P2 DD ∈ {20%,25%,wył.}, P2 VIX ∈ {35,40}, gross P1 ∈ {0,5; 0,75}, odczyt D0/dzienny; `weryfikacja_C8_siatka.csv`):

- 326/576 (57%) ma Sharpe netto > 0,668, ale maksimum to **0,773** (+0,105; t 1,64 vs 1,42) — przy P1 VIX>35 bez MA200, czyli bramka, która praktycznie nie wchodzi w P1 i sprowadza się do „P2 przy DD>20%".
- **0/576** obniża maxDD kapitału o >5 pkt; 0/576 poprawia jednocześnie Sharpe i maxDD.
- Warianty z pytania (reszta jak w rutynie): VIX>25: ΔSharpe −0,091 (D0) / −0,052 (dzienna); VIX>30: −0,002 / +0,020; DD>15%: −0,047 / −0,013; P2 DD>25%: −0,043 / −0,074; tylko VIX: −0,027 / −0,042. ΔmaxDD w każdym przypadku +0,0…+2,4 pkt (`_out.md` TEST 3).

Różnice ±0,1 Sharpe przy t≈1,4 całej strategii są szumem i in-sample (wiele porównań). Nie istnieje wariant progów, który czyni z bramki narzędzie poprawy ryzyka.

### 2d. Bramka jako ubezpieczenie od bessy 2022 — P(kill)

Okna kroczące, start kapitału 100 = szczyt (`_out.md` TEST 4, `_dod_out.md` iso-gross):

| wariant | ALLOC | śr. gross | P(kill 12 t.) | P(kill 26 t.) | kill 12 t. start 2022 | kill 12 t. start 2023–26 | Sharpe netto | maxDD % | pełna ścieżka z kill |
|---|---|---|---|---|---|---|---|---|---|
| bez bramki | 0,24 | 240% | **42,2%** (94/223) | 71,8% | 20/37 | 74/186 | 0,668 | 69,3 | kill 2022-06-23, końc. 85,0 |
| bramka hist. D0 | 0,24 | 178% | **31,4%** | 53,6% | **0/37** | 70/186 | 0,613 | 69,5 | kill 2024-01-05, końc. 95,8 |
| bramka hist. dzienna | 0,24 | 178% | 30,5% | 52,6% | 0/37 | 68/186 | 0,636 | 71,7 | kill 2024-01-05, końc. 105,5 |
| **stały ALLOC 0,178 (iso-gross)** | 0,178 | 178% | **27,8%** | 60,3% | 17/37 | **45/186** | **0,679** | **56,8** | kill 2022-07-18, końc. 81,4 |
| stały ALLOC 0,16 | 0,16 | 160% | 23,3% | 56,5% | 11/37 | 41/186 | 0,682 | 52,5 | kill 2022-07-19 |
| stały ALLOC 0,12 | 0,12 | 120% | **6,7%** | **8,6%** | 2/37 | 13/186 | **0,690** | **41,9** | kill 2022-07-21, końc. 80,6 |
| bramka + ALLOC 0,16 | 0,16 | 119% | 16,1% | 43,5% | 0/37 | 36/186 | 0,621 | 52,8 | kill 2024-02-21 |

Odczyt: cała redukcja P(kill) przez bramkę pochodzi z 2022 (20→0 okien); w 2023–2026 bramka prawie nic nie zmienia (74→70), bo ryzyko kill siedzi w P0 — σ tygodniowa kapitału mom6M: 2026 w P0 14,75% (najgorszy tydzień −30,9%), 2024 w P0 8,97%, wobec 2022 (cały rok P2) 7,96% (`_dod_out.md` ostatnia tabela). Tygodnie P2 **nie są** wysokozmienne dla spreadu L/S: σ losowego koszyka 5/5 w P2 3,72% kapitału vs 4,10% w P0 (`_out.md` TEST 4b); bramka adresuje ryzyko indeksu, a strategia jest (nominalnie) neutralna indeksowo.

**Kontrola iso-gross** rozstrzyga pytanie ubezpieczeniowe: stały ALLOC 0,178 (ta sama średnia ekspozycja co bramka) ma niższy P(kill 12 t.) (27,8 vs 31,4%), niższy maxDD (56,8 vs 69,5%) i wyższy Sharpe (0,679 vs 0,613); przegrywa tylko w 2022 (17 vs 0 okien) i w horyzoncie 26 t. (60 vs 54%). Przy **zerowej alfie** (200 losowych koszyków, sparowane): P(kill 12 t.) bramka 8,5% vs iso-gross 3,0% — iso-gross niżej w 97% strategii (bramka niżej w 3%); maxDD 70,7 vs 68,4 (`_dod_out.md`). Bramka wobec braku bramki na 500 losowych koszykach: ΔP(kill) −3,7 pkt, ΔmaxDD −9,0 pkt (`_out.md` TEST 4b) — ale to efekt samego obniżenia gross o 26%, nie trafności momentu, bo stały ALLOC o tej samej średniej daje więcej.

Co bramka robi lepiej niż stały ALLOC: wyłącznie epizod 2022 (35 z 36 tygodni P2 pochodzi z jednego kryterium DD>20% od maksimum 252 sesji — faza 2, §4). Ocena bramki jako ubezpieczenia jest więc oceną jednego epizodu, a jej cena to −0,16 %/tydz. netto (0,85 → 0,69) i wycięte odbicia po kryzysie.

## 3. Najsilniejszy kontrargument

Bez bramki rachunek przy ALLOC 0,24 **ginie 2022-06-23** (kill switch; kapitał 85, płasko do końca próby), a z bramką przechodzi przez 2022 z DD 1–4% i gra do 2024-01-05 — 20 z 37 okien 12-tygodniowych startujących w 2022 kończy się killem bez bramki, 0 z bramką. Metryka „maxDD w pp spreadu 71→72" tego nie widzi, bo sumuje spready bez dźwigni i bez kill switcha. Jest to realny, duży pay-off ubezpieczeniowy — i zarazem jedyny: w 2023–2026 bramka nie zmienia P(kill) (74 vs 70 okien), a ten sam kapitał da się ochronić taniej stałym ALLOC 0,178 (P(kill) 27,8%, Sharpe 0,679) albo 0,12 (6,7%, 0,690, maxDD 41,9%). Argument „bramka = ubezpieczenie od 2022" broni istnienia **jakiejś** redukcji ekspozycji w bessie, nie tej bramki.

## 4. Zastrzeżenia

- Jedna próba, jeden epizod bessy (2022) i jedna hossa AI; P2 w 2022 to jeden wyzwalacz (DD>20%), więc „wartość ubezpieczenia" ma n=1. Survivorship bias składu (dzisiejsze 103 spółki) zawyża momentum w P0 2023–2026 i tym samym koszt bramki.
- Siatka progów: 576 wariantów in-sample; każdy „najlepszy" to selekcja po fakcie. Progi wrażliwe na definicję DD (max 252 sesji) i MA200 z dokładnie 200 zamknięć.
- Symulacja: wejścia po zamknięciu D0 (bot wchodzi w poniedziałek 13:45 UTC), stałe wagi w oknie bez wyrównywania, bez stopów 10% i bez REDUCE pulsowego (bramka dzienna przybliża REDUCE na wszystkich pozycjach jako g=0,5 od następnej sesji). Kill sprawdzany tylko na zamknięciach (bot dwa razy dziennie — P(kill) lekko zaniżone). Koszty założone (0,10%/noga, 6%/rok), nie taryfa Capital.com.
- Hit rate z bramką nie jest porównywalny (tygodnie gross 0 = 0%) — porównywałem średnią, σ, Sharpe, P(kill).
- Liczby w % kapitału umownego 100; żadnych liczb z rachunku.

## 5. Implikacja projektowa

Bramka P0/P1/P2 w obecnym kształcie nie jest narzędziem zarządzania ryzykiem koszyka L/S — mierzy ryzyko indeksu, podczas gdy ryzyko kill (2024, 2026, W6/W7) siedzi w P0 i w koncentracji czynnikowej. Jeśli ma zostać: usunąć histerezę (to ona kosztuje — 10 tygodni odbić po +3,8…+5,8% kapitału) i zredukować do jednego progu P2 (DD ^NDX >20% od maks. 252 sesji → status NIEAKTUALNA), który jest tani (tylko P2→0: Sharpe 0,72 vs 0,67) i chroni przed powtórką 2022. Właściwa dźwignia ochrony kapitału to ALLOC: 0,12 daje P(kill 12 t.) 6,7% zamiast 42% przy tym samym Sharpe, czego żadna wersja bramki przy 0,24 nie osiąga (najlepsza: 30,5%).
