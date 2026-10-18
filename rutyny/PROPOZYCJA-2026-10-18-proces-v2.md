# Proces v2 systemu NDX100 — decyzje, wdrożenie, migracja (18.10.2026)

Dokument wynikowy analizy `rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md` (fazy 1–3: 6 analiz, 5 testów
wstecznych, 9 weryfikacji adwersaryjnych, 3 projekty, 3 sędziów). Wygrał projekt C (konstrukcja E) z
przeszczepami operacyjnymi z projektu B i pętlą pomiarową z projektu A. Nic poniżej nie zawiera kwot z rachunku ani wielkości
pozycji — stan rachunku wyłącznie jako zaokrąglone wskaźniki względne (% i p.p.).

## 0. Co zmieniamy i dlaczego (jedna tabela)

| Element | Dotąd (W1–W8) | Proces v2 (od 2026-W9) | Dowód |
|---|---|---|---|
| **Źródło koszyka** | Model 3.0: 20 czynników, 33 % wag uznaniowych, scoring w głowie, 10/16 stron koszyków nadpisanych względem własnego rankingu | `scripts/ranking.py`: deterministyczny ranking momentum 6M relatywnego (skip 5 sesji) + veta (K13, EVENT, σ, cena) — zero uznania w składzie; Model 3.0, elita, panel fundamentów, p, pre-mortem i deklaracje D1–D3 wychodzą z selekcji | IC Wyniku −0,10 (95 % CI −0,57…+0,37), 67 % Wyniku = momentum + beta, warstwa uznaniowa +0,06 IC (t 1,2); p nieinformacyjne (C5) |
| **Konstrukcja** | TOP5/BOTTOM5 wg Wyniku; de facto 5/5 półprzewodników vs defensywy (b_SOX +1,1…+2,1) | **E = 5 par w grupie branżowej** (long najlepsze / short najgorsze momentum w tej samej grupie TV) z puli 8 par, wybór piątki o największej sumie rozstępów przy **budżecie \|b_SOX net\| ≤ 0,5**; równe wagi, 1 tydzień | σ spreadu 4,6 vs 6,9 p.p. (σ-ratio 0,67, CI 0,58–0,78, odporne na definicję grupy i uniwersum PIT), najgorszy tydzień −12,7 vs −23,9, w tygodniach SOX−NDX < −3: −1,9 vs −5,1; koszt średniej Δ −0,21 (nierozstrzygalny; planować −0,3…−0,5) (C2, projekt C) |
| **Sizing** | ALLOC_PCT 0,24 (gross 240 %) | **ALLOC_PCT 0,08** (gross 80 %), ALLOC_PCT_SAFE 0,04; zmiana krokiem ≤ 0,02 na 4 tygodnie; vol-target TYLKO jako kolumna diagnostyczna (≥ 12 tyg. na papierze) | P(kill −25 %, alfa 0): 0,24 → 51–65 %/12 tyg., 98–100 %/52 tyg.; E przy 0,08 → 0,0 %/12 tyg., 8 %/52 tyg. (C4, projekt C); vol-target zdominowany przez stałe ALLOC na tej samej konstrukcji (sędzia 3) |
| **Stop bota** | 10 % od poziomu brokera, po stopie ponowne otwarcie w kolejnym biegu | **15 % LONG / 10 % SHORT, bez ponownego otwarcia w tej samej wersji** (wpis `wykonanie.stopy`); kotwica bez zmian | koszt stopu z nóg LONG (−0,23 p.p./tydz., t −2,3), SHORT neutralny; reopen = drugi spread bez sygnału; kotwica w cenie tezy pogarsza (−0,48 vs −0,28) (C3) |
| **Próg pośredni** | brak (między stopem nogi 10 % a kill 25 % nie ma nic) | **próg miękki**: obsunięcie > 10 % od kroczącego szczytu → bot zamyka 2 pary o najwyższej σ (pierwsze 2 nogi każdej listy), wraca poniżej 5 %; stan `wykonanie.soft` | P(kill 52 tyg., alfa 0) 8,0 → 0,5 % (sędzia 3, symulacja par); wykonalny lotami (zamyka całe pozycje, nie połowi) |
| **Kill switch** | 0,75 × kroczący szczyt; po trafieniu bot stoi bezterminowo, bez śladu w pliku | bez zmiany progu; **ślad `wykonanie.kill` + polityka wznowienia** (po KILL_RESUME_DAYS i zmianie version szczyt := kapitał, pierwszy koszyk z ALLOC_RESTART) | app.py:1497–1503 return bez zapisu; wznowienie dziś = ręczna edycja pola bota (C9) |
| **Bramka cenowa Pulsu 4 %/8 %** | wpis REDUCE/CLOSE od ceny wejścia, potwierdzenie drugą sesją, blokada sektorowa | **tylko pomiar** („co zrobiłby protokół”, od fills), bez wpisów; exclude wyłącznie basis news z listy zamkniętej | EV ≈ 0 w każdej mierze (±0,15 p.p./tydz.; po sygnale REDUCE reszta okna +0,16, t ≈ 0); stop bota zawsze pierwszy (C7) |
| **Bramka reżimu P0/P1/P2** | P1 → REDUCE wszystkich (gross 50 %), P2 → płasko, histereza | **tylko P2 jako wyłącznik płynności** (drawdown ^NDX > 20 % od maks. 252 sesji, sesja ≤ −5 % lub VIX > 40 → status NIEAKTUALNA do powrotu); P1 = flaga w raporcie | bramka obniża momentum 1,00 → 0,78 bez poprawy maxDD; tygodnie P1 najlepsze (+3,04, t 2,0); W6–W7 w P0 (C8) |
| **Moduł taktyczny** | 1 nowa/dzień, 20 % kapitału na nogę | **wyłączony** (`tactical=[]`, TACTICAL_ENABLED=false) do czasu testu przekrojowego reguły „long po dniu ≥ +12 % rel., 10 sesji” (KANDYDAT H2) | n = 4 pozycje, 20 % kapitału bez dowodu; σ ≈ 1 % kapitału dziennie z jednej nogi |
| **Reguły** | 36 reguł, 17 po n = 1, 0 retestów, ≥ 6 par sprzecznych, w HTML | `rutyny/reguly.md`: OBOWIĄZUJĄCE / KANDYDACI / WYJĄTKI IMIENNE / UCHYLONE; awans tylko po teście przekrojowym (jak w nagłówku reguly.md: ≥ 30 zdarzeń w ≥ 15 tygodniach, \|t\| ≥ 2 klastrowane po dacie, ten sam znak w ≥ 4 z 5 lat, reguła musi wiązać) i decyzji właściciela; moratorium do 26 okien cieni | audyt-regul.md; K10 kosztowała −0,37…−0,70 p.p./tydz. (C6) |
| **Pomiar** | spread_pp od D0; p; hit rate vs 50 % | prerejestrowana tabela w stałej kolejności: spread od D0 i od fills (do rotacji), σ zreal. vs ex ante, b_SOX zreal., koszyki cienie (A, B, C, D, E, E_bez_exclude, U, FAKT, ETF SMH−XLP, bez EVENT; `koszyki_cienie.py --podsumowanie`: CI, σ-ratio, test F), KOSZT REGUŁ I NADPISAŃ (E_bez_exclude, veta imienne, NADPISANIE = FAKT − E), zdanie o mocy („nieodróżnialne od losowości, t, n”) | o wariancji rozstrzyga test F po 12–26 tyg. (moc 22–47 %), o średniej praktycznie nigdy (t = 2 dla Δ 0,3 po ~1 200 tyg.) |
| **Budżet TV** | sobota do 50 wywołań / 20 min (W8: 29 / 36 min) | sobota ≤ 10 wywołań (zwykle 7: screener, ≤2× earnings-calendar, dividends, 2× ohlcv NDX/VIX, economic); Puls ≤ 10 (zwykle 7) — limity w `data/tv-config.json` | research per spółka nie wchodzi do selekcji |

## 1. Decyzja właściciela na poniedziałek 19.10.2026 (przed 13:45 UTC)

Stan: kapitał **≈ 1,7 % nad progiem kill switcha** (0,76 × szczyt z 6.10); na rachunku 9 nóg W7 + ERIC do biegu 13:45 UTC, potem rotacja na W8 (GOOGL GILD MSFT QCOM ADP / AXON DASH ALNY APP FER). Z symulacji (weryfikacja C9; bootstrap blokowy 250 sesji koszyka W8, koszt rotacji 0,3 %): przy ALLOC 0,24 **P(kill) ≈ 58 % w 5 sesji, 69 % w 10, 77 % w 20**; przy 0,08: 39 % / 48 % / 58 %; ~21 % przypada na samą lukę poniedziałkową księgi W7 (niezależnie od ALLOC). Trzy spójne warianty:

| Wariant | Co zrobić | Skutek | Uwaga |
|---|---|---|---|
| **A. Płasko bez restartu** | przed 13:45 UTC commit `status: "NIEAKTUALNA"` (pole rutyn, ale tutaj commit ręczny właściciela — Puls wg KROKU 2 nie zmienia statusu z powodu kill switcha) → bot zamyka wszystko i stoi do zmiany statusu | zatrzymanie w kontrolowanym momencie; próg kill bez zmian (0,75 × stary szczyt), więc powrót do handlu wymaga i tak resetu szczytu | kill-check jest PRZED sprawdzeniem statusu — przy luce poniedziałkowej > 1,7 % bot i tak zamknie przez kill; różnica tylko we fladze |
| **B. Świadomy restart z nowym sizingiem** (rekomendacja analizy) | JEDNOCZEŚNIE: (1) Render `ALLOC_PCT=0.08`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`, `REDUCE_FALLBACK=close`, `START_EQUITY=<bieżący kapitał>`; (2) commit właściciela `equity_peak := <bieżący kapitał>` w signals.json (nadpisanie wartości, nie usunięcie klucza — walidator wymaga 15 kluczy; to pole bota, więc commit ręczny właściciela, nie rutyny) | poduszka do kill 25 % zamiast ≈ 1,7 %; P(kill 5/20 sesji) ≈ 0 %/1 % przy 0,08; W8 gra dalej (konstrukcja W8 ma ex ante b_SOX +0,05 (śr. b_SOX LONG − SHORT z ranking.py; w regresji 3-czynnikowej z 250 sesji +0,29), σ60 1,85 %/d — profil ryzyka jak E) | sam reset equity_peak daje poduszkę 11 %; samo START_EQUITY — zero zmiany; samo ALLOC 0,08 — 39 %/58 %. Restart = przesunięcie progu po stracie: obsunięcie od szczytu HISTORYCZNEGO (−23,7 %) musi być w każdym raporcie obok cyklu |
| **C. Nic nie robić** | — | ~60 % szans, że bezpiecznik zamknie wszystko w tym tygodniu w losowym momencie; po tym bot stoi bezterminowo | przy zerowej alfie wartość oczekiwana B i C jest ta sama; B kupuje kontrolę momentu i wybór sizingu |

Niezależnie od wariantu: od soboty 24.10 (W9) koszyk powstaje z `ranking.py` (konstrukcja E), W8 jest rozliczany cieniami A/B/C/D/E.

## 2. Co jest już w repo (ta gałąź) i co wymaga działania właściciela

### 2.1 Gotowe (gałąź `claude/gifted-lamport-iwzpop`)

* `scripts/ranking.py` — ranking + konstrukcje A/B/C/D/**E**, veta, ekspozycje, σ koszyka, proponowany ALLOC (diagnostyka); `--fetch` pobiera 1y z Yahoo; `--exclude TICKER=POWÓD` (cień E_bez_exclude), `--faktyczny-long/-short` (konstrukcja FAKTYCZNY z ryzykiem), dopełnianie par i tryb bez czynnika SOX, liczniki dat raportów i ostrzeżenia (po przeglądzie 18.10); wynik do `data/ranking-<version>.json` + markdown. Testy: `scripts/test_ranking.py` (23 testy, bez sieci). Veto cenowe 1 280 USD jest STAŁĄ skryptu (nie liczy się go z kapitału rachunku — plik `data/ranking-<version>.json` trafia do repo).
* `scripts/koszyki_cienie.py` — rozliczenie cieni, koszyka faktycznego i ETF SMH−XLP (σ zrealizowana, ex ante), log `data/koszyki-cienie.jsonl`; `--podsumowanie`: n, średnia, σ, CI 95 %, σ-ratio, test F (bez scipy), E netto po koszcie 0,3 p.p./tydz., kalibracja, pokrycie — liczby do KRYTERIÓW DECYZJI.
* `data/ranking-2026-W8.json` — cienie dla W8 (D0 16.10, veto EVENT ze snapshotu TV, bez `--exclude`): E = CRWD/APP, AMGN/ALNY, FTNT/PAYX, AMD/AVGO, DXCM/GEHC (b_SOX net +0,26, σ60 tyg. 5,2 p.p., percentyl 89 wobec losowych po vetach) + konstrukcja FAKTYCZNY (koszyk W8 z signals.json: σ60 4,1 p.p., b_SOX +0,05) — do rozliczenia 24.10.
* `rutyny/reguly.md` — rejestr reguł; `rutyny/tygodniowa.md`, `rutyny/dzienna.md` — treści rutyn v2 (do wklejenia do zadań na claude.ai/code/routines po scaleniu); `CLAUDE.md` zaktualizowany.
* `rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md`, `analiza/2026-10-18/` — materiał dowodowy.

### 2.2 Wymaga decyzji i działania właściciela

1. **Panel Render (natychmiast, przed 19.10 13:45 UTC)** — patrz §1: `ALLOC_PCT`, `ALLOC_PCT_SAFE`, `TACTICAL_ENABLED`, `TACTICAL_ALLOC_PCT`, `START_EQUITY`; `REDUCE_FALLBACK=close` (REDUCE per noga przy 0,08 i locie 0,1 akcji jest martwy dla nazw > ~600 USD).
2. **Scalenie gałęzi do `main`** (rutyny czytają `main`) i wklejenie treści `rutyny/tygodniowa.md` i `rutyny/dzienna.md` do zadań na claude.ai (zasada z CLAUDE.md: najpierw plik, potem wklejenie).
3. **Zmiany w `app.py` (§3) — WDROŻONE w tej gałęzi** (18.10.2026, po Twoim poleceniu „wprowadź wszystkie niezbędne zmiany, aby zwiększyć skuteczność"), z testami w `scripts/test_app.py` (184 przechodzą). Aktywują się po scaleniu do `main` i deployu na Renderze. UWAGA do domyślnych: nowe zmienne (`STOP_LOSS_PCT_LONG=0.15`, `STOP_LOSS_PCT_SHORT=0.10`, `STOP_REOPEN=false`, `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `SOFT_PARY=2`, `KILL_RESUME_DAYS=14`, `ALLOC_RESTART=0.04`) mają domyślnie wartości v2, a stare domyślne zmieniono na v2 (`ALLOC_PCT` 0,08, `ALLOC_PCT_SAFE` 0,04, `TACTICAL_ENABLED` false, `REDUCE_FALLBACK` close) — zmienna ustawiona jawnie w Renderze (dziś `ALLOC_PCT=0.24`, `TACTICAL_ALLOC_PCT=0.20`) ma pierwszeństwo, więc pkt 1 pozostaje do zrobienia ręcznie. Po deployu BEZ restartu z §1 próg miękki włączy się od razu (obsunięcie od szczytu > 10 %) i bot będzie trzymał 3 pary z 5 do czasu restartu albo powrotu kapitału poniżej 5 % od szczytu — to zamierzone (mniejsza ekspozycja przy ≈ 1,7 % zapasu do kill), ale trzeba o tym wiedzieć.

## 3. Specyfikacja zmian w `app.py` — STAN: WDROŻONE 18.10.2026 (gałąź), aktywne po deployu

Zasada po zmianie decyzji właściciela: każda zmiana za zmienną środowiskową z domyślną wartością = zalecenie v2 (nie „dzisiejsze zachowanie" — właściciel polecił wprowadzić wszystkie zmiany); dawne zachowanie przywraca się zmiennymi (`STOP_LOSS_PCT_LONG=0.10`, `STOP_REOPEN=true`, `DD_SOFT=0`, `KILL_RESUME_DAYS=0`). Każda z testem w `scripts/test_app.py` (184 testy po zmianie; funkcje czyste: `stopy_bezpieczenstwa`, `desired_book(stopped, soft)`, `scal_wykonanie`, `stan_progu_miekkiego`, `decyzja_wznowienia`, `pokrycie_koszyka`). Różnice wobec pierwotnej specyfikacji niżej: wznowienie zdejmuje podłogę `START_EQUITY` z odniesienia kill switcha (bez tego reset szczytu dawałby poduszkę 11 %, nie 25 % — weryfikacja C9); `/status` zwraca `kill_switch.zapas_pct` w %, a zapas w σ dziennej liczą rutyny z pliku ranking (bot nie ma σ koszyka).

### 3.1 Stop asymetryczny i pamięć stopu

```
STOP_LOSS_PCT_LONG  = float(os.environ.get("STOP_LOSS_PCT_LONG", str(STOP_LOSS_PCT)))   # zalecane 0.15
STOP_LOSS_PCT_SHORT = float(os.environ.get("STOP_LOSS_PCT_SHORT", str(STOP_LOSS_PCT)))  # 0.10
STOP_REOPEN         = os.environ.get("STOP_REOPEN", "true").lower() == "true"           # zalecane false
```
* `stopy_bezpieczenstwa()`: próg = `STOP_LOSS_PCT_LONG` dla BUY, `STOP_LOSS_PCT_SHORT` dla SELL (kotwica bez zmian: `p["wejscie"]`, potem `fills[t]["cena"]`).
* W pętli zamknięć w `sync()`: po stopie, gdy `STOP_REOPEN=false`, zapis `wykonanie["stopy"][ticker] = {"wersja", "data", "kierunek", "opis"}`; `desired_book(sig, closed, reduced, stopped=…)` pomija tickery z wpisem o bieżącej `version` (rotacja czyści). `scal_wykonanie()` przenosi `stopy` tylko dla bieżącej wersji; porównanie `zmiana_wyk` obejmuje klucze `stopy`, `soft`, `kill`.
* `pokrycie_koszyka()`: noga z `wykonanie.stopy` nie jest „brakująca” — nowe pole `zatrzymane_stopem`.
* Testy: BUY −12 % przy 0,15 nie zamyka, SELL +12 % przy 0,10 zamyka; po stopie `desired_book` pomija nogę w tej wersji i wraca po zmianie `version`; `scal_wykonanie` kasuje wpisy innej wersji.

### 3.2 Próg miękki od kroczącego szczytu

```
DD_SOFT = 0 (wył.) → zalecane 0.10; DD_SOFT_RESET = 0.05; SOFT_PARY = 2
```
* Po bloku kill switcha: `dd = 1 − equity/odniesienie`; stan `wykonanie.soft = {aktywny, od, dd_start}` z histerezą (włącz > DD_SOFT, wyłącz < DD_SOFT_RESET).
* Gdy aktywny: `desired_book` pomija pierwsze `SOFT_PARY` tickery z `long` i pierwsze `SOFT_PARY` z `short` (rutyna porządkuje listy od pary o najwyższej σ60 — `ranking.py` konstrukcja E to robi). Zamyka całe pozycje (wykonalne lotami), nie połowi.
* Testy: przejścia stanu przy obsunięciu 9 %/11 %/4 %; książka bez 2+2 nóg przy aktywnym progu; taktyczne nietknięte.

### 3.3 Ślad kill switcha i polityka wznowienia

```
KILL_RESUME_DAYS = 0 (wył.) → zalecane 14; ALLOC_RESTART = 0 → zalecane 0.04
```
* W ścieżce kill (dziś `return rep` bez zapisu): zapis `wykonanie.kill = {data, wersja, szczyt, prog, kapital}` przez `save_signals` (raz; kolejne biegi nie nadpisują).
* Przed liczeniem progu: jeśli `wykonanie.kill` bez `wznowiono`, minęło ≥ KILL_RESUME_DAYS i `version` ≠ `kill.wersja` → `equity_peak := equity`, `kill.wznowiono = dziś`, `kill.wersja_wznowienia = version`; dla tej wersji `alloc = min(alloc, ALLOC_RESTART)`.
* `/status`: `ustawienia.start_equity`, `stop_loss_pct_long/short`, `stop_reopen`, `dd_soft*`, `kill_resume_days`, `alloc_restart`; pola `wykonanie` i `kill_switch.zapas_pct` (zapas w % do progu) — rutyny podają zapas w σ dziennej bieżącej księgi.
* Testy: brak wznowienia przed terminem / bez zmiany wersji; wznowienie przepisuje szczyt; ALLOC_RESTART tylko dla wersji wznowienia.

### 3.4 Nie zmieniać

KILL_LEVEL 0,75 / KILL_TRAILING true; REBALANCE_HOURS 17; HEDGE_MODE classic; MIN_REBALANCE_ACC; bramka reakcji w kodzie (zostaje, bo Puls nie będzie już pisał wpisów cenowych — basis news przechodzi bez bramki); kotwica stopu. Nie wdrażać: inverse-vol per noga, pola `sizing` w signals.json, σ-stopu czytanego z pliku repo w biegu, FLAT −12 % z cooldownem (bez efektu w symulacji).

## 4. Rutyna tygodniowa v2 — przebieg (szczegóły w `rutyny/tygodniowa.md`)

1. KROK 0 — guard biegu, `signals.json`, `rutyny/reguly.md` (tylko OBOWIĄZUJĄCE + WYJĄTKI z datą), `/status`.
2. KROK A — prerejestrowana tabela A1–A9: spread od D0 i od fills; taktyczne/reakcje z wykonanych; cienie (`koszyki_cienie.py --ranking data/ranking-<poprzednia>.json … --log` i `--podsumowanie`); dekompozycja jednoczynnikowa SOX i kalibracja σ zreal./ex ante; KOSZT REGUŁ I NADPISAŃ (E_bez_exclude, veta imienne, NADPISANIE); zdanie o mocy (t, n); kandydaci na papierze; kontrola rachunku z zapasem do kill w σ. Wpis `history` bez nowych pól (`dane_b1`: "tv" za W8, "yahoo" od W9).
3. KROK B0 — reżim: tylko P2 (wyłącznik płynności) → NIEAKTUALNA; P1 flaga.
4. KROK B — `python3 -I scripts/ranking.py --fetch --cache <scratch>/closes-1y.csv --tv data/tv-screen-<version>.json --earnings-from-tv [--earnings <plik z weryfikacji dat>] --exclude <lista zamknięta: wyjątki imienne, R8, usunięte z indeksu, K6'> --version <version> --out data/ranking-<version>.json --md …` (veto cenowe = stała 1 280 USD w skrypcie; żadnych nadpisań parametrów) → koszyk = `konstrukcje.E_pary_budzet_sox` (long/short w kolejności par od najwyższej σ). Bez nakładki uznaniowej (dopuszczalna wyłącznie jako cień na papierze).
5. KROK C — raport HTML z prerejestrowaną tabelą metryk, tabelą REGUŁY — kontrola, sekcją ryzyka (σ60 koszyka, percentyl vs losowe, b_SOX/b_DEF net, ALLOC diagnostyczny, zapas do kill w σ dziennej) i ryzyk operacyjnych (loty, przestrzały).
6. KROK D — `signals.json`: version, status, long, short, d0, generated, exclude=[], tactical=[], history +1; walidator; commit snapshotu TV i `data/ranking-<version>.json`, `data/koszyki-cienie.jsonl`.
7. Kryteria decyzji (prerejestrowane): po 12 oknach tylko kalibracja wykonania (σ zreal. w [0,7; 1,4] × ex ante, pokrycie ≥ 10/12); po 26 oknach: σ-ratio E/A ≤ 0,85 i średnie |b_sox_net_ex_ante| E < A → E zostaje; σ-ratio > 1,03 → powrót do A z ALLOC 0,06 (decyzja właściciela); 0,85–1,03 → bez zmian do 52 okien; po 52: górna granica CI średniej E netto < 0 → papier/ETF. Nigdy: zmiana MIN_IND/MIN_GROUP/PAIR_POOL/FACTOR_BUDGET po złym tygodniu.

## 5. Rutyna dzienna v2 — przebieg (szczegóły w `rutyny/dzienna.md`)

Puls staje się **raportem kontrolnym**: `/status` (pokrycie 10/10 nóg, kontrola kapitału, stan `wykonanie` — stopy/soft/kill, zapas do progów w σ dziennej, przestrzały lotów, EKSPOZYCJA_NIEPELNA), kursy i spread od fills/D0, kalendarz (wyniki w 2 sesjach — flaga EVENT), reżim (tylko P2 zmienia status), **KONTROLA BRAMKI jako pomiar** („co zrobiłby protokół 4 %/8 %” — bez wpisu), exclude wyłącznie `basis="news"` z listy zamkniętej (R3) i dokumentem źródłowym, `tactical=[]`. Bez elity, FINRA, makro-narracji, bramki sektorowej jako warunku. Harmonogram bez zmian (dni robocze 12:30 UTC); budżet TV ≤ 10 wywołań (zwykle 7). Opcja do decyzji: 3 biegi/tydz. (pon./śr./pt.).

## 6. Oczekiwania liczbowe (żeby nikt nie mylił planu z obietnicą)

* Konstrukcja E przy ALLOC 0,08: σ tygodniowa kapitału ≈ 1,8 %, gross 80 %, koszty ≈ 0,12 %/tydz. (finansowanie + rotacja 2,8 nogi), **μ netto −0,1 % (alfa 0) … +0,3 % (in-sample dzisiejszy skład)**, 1 p.p. spreadu = 0,4 % kapitału; P(kill 52 tyg., alfa 0) ≈ 8 % (z progiem miękkim < 1 %); maxDD 52 tyg. mediana −14 %, p95 −25 %.
* Momentum na uniwersum point-in-time: +0,7 p.p./tydz. brutto (t 1,55), +0,44 netto (t 0,95) — zero w przedziale ufności. System v2 ma **przeżyć i mierzyć**, nie „osiągać zyski” z definicji; dowód przewagi na żywo wymaga ~540 tygodni, dowód o wariancji 12–26.
* Alternatywa tańsza o połowę drawdownu: czynnik SMH/XLP ETF-ami (Sharpe 1,07 in-sample, bez kosztów rotacji) — do rozważenia przez właściciela, gdy po 52 oknach E nie pokaże przewagi nad ETF.

## 7. Co zostaje poza systemem (świadomie)

Model 3.0 jako źródło koszyka; p; elita analityków; panel fundamentów jako wejście do selekcji; reguła „przegrana bez odzyskanej siły relatywnej”; filtry pogoni; bramka cenowa Pulsu jako wyzwalacz; REDUCE przy P1; moduł taktyczny; inverse-vol per noga; dwie transze; neutralność beta przez wagi; vol-target jako sizing bota (na razie).
