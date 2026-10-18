# Weryfikacja C9 — kill switch ≈ 1,7 % pod kapitałem, koszyk W8, „jedyna sensowna opcja to restart"

**Twierdzenie C9:** „Stan bieżący: kapitał ≈ 1,7 % nad kill switchem; przy koszyku W8 (σ dzienna kapitału ~2,2% przy ALLOC 0,24) P(przebicia progu) ≈ 50% w 5 sesji, 65% w 10 sesji; przy ALLOC 0,08 ≈ 18%/33%; po przebiciu bot zostaje wstrzymany bezterminowo (equity nie wraca nad próg bez pozycji) — jedyna sensowna opcja to świadomy restart (reset equity_peak lub START_EQUITY) z nowym sizingiem."

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Liczby rdzenia odtwarzają się niezależnie (52%/65% przy 0,24; 18%/34% przy 0,08) i są odporne na okno, długość bloku i rozkład; mechanizm „wstrzymany bezterminowo" potwierdza kod. Cztery rzeczy w twierdzeniu są jednak błędne lub niekompletne: (1) poniedziałkowe sprawdzenie o 13:45 UTC wykonuje się na **księdze W7, która wciąż jest na rachunku** (9 pozycji, gross ~218%) — to ~21% szans na kill, zanim W8 w ogóle wejdzie, i tej części żadne ALLOC nie zmienia, więc „przy ALLOC 0,08 ≈ 18%/33%" zaniża realne ~39%/48%; (2) „reset equity_peak **lub** START_EQUITY" jest mechanicznie fałszywe: sam reset `equity_peak` daje poduszkę 11% (podłoga `max(szczyt, START_EQUITY)`), samo START_EQUITY nie daje nic — 25% wymaga **obu** zmian; (3) σ W8 z ostatnich 20 sesji to połowa σ z 250 (4,9% vs 9,3% jednostkowo), więc uczciwy przedział dla 5 sesji przy 0,24 to 32–58%, nie punktowe 50%; (4) „jedyna sensowna opcja" to sąd, nie wynik: przy zerowej alfie E[kapitał] czekania ≈ E[kapitał] restartu (0,765 vs 0,761 szczytu), kill jest obcięciem rozkładu, a przepisanie szczytu przed jego zadziałaniem to dokładnie „przesuwanie progu po stracie", przed którym ostrzega `wykonanie-bota.md` i INSTRUKCJA.md.

Skrypt: `weryfikacja_C9.py` (1,6 s; 20 000 ścieżek na komórkę). Wyjścia: `weryfikacja_C9_out.md`, `weryfikacja_C9_wyniki.json`; odczyt `/status` 18.10 użyty tylko jako stosunki (plik odpowiedzi usunięty — zawierał kwoty). Katalog: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`.

## 0. Stan wejściowy (zweryfikowany)

- `/status` 18.10 (odczyt tylko-do-odczytu zgodnie z CLAUDE.md): `kapital/equity_peak ≈ 0,76` → poduszka nad progiem 0,75 ≈ **1,7 %** kapitału (zgodnie z twierdzeniem). `ustawienia`: alloc_pct 0,24, kill_level 0,75, kill_trailing true, stop_loss_pct 0,10, dry_run false, hedge_mode classic.
- Na rachunku **9 pozycji z W7** (CSCO, MU, MRVL BUY; PANW BUY po REDUCE ~½; APP, SBUX, PEP, TMUS, CMCSA SELL) + taktyczna ERIC BUY; gross ≈ 2,2 (ALLOC 0,24 × 9 nóg; bez ERIC). `pokrycie_koszyka`: nogi W8 na rachunku 0/5 LONG, 1/5 SHORT (APP kontynuowany), `brakujace` = 5 LONG + 4 SHORT — stan SPRZED rotacji, rotacja w poniedziałek 19.10 13:45 UTC.
- `signals.json`: `kapital/START_EQUITY ≈ 0,83` (stosunek wyprowadzony z `equity_peak` w pliku i z `kapital/equity_peak`; kwoty pominięte zgodnie z CLAUDE.md) (START_EQUITY domyślne 1000 wg app.py:164; wartość na Renderze NIE jest w `/status.ustawienia` — niezweryfikowana).
- Dane: `closes_5y.csv`, zamknięcia 2021-10-18…2026-10-16 (1257 sesji), skład dzisiejszy (survivorship bias); ERIC nie ma w pliku (pominięty w księdze W7 → σ księgi zaniżona o kilka %).

## 1. Replikacja i wrażliwość (W8: GOOGL GILD MSFT QCOM ADP / AXON DASH ALNY APP FER)

Metoda jak w `ryzyko_extra.py`: seria jednostkowa = Σ5 long − Σ5 short dziennych zwrotów, wyśrodkowana (zero alfy), bootstrap blokowy (blok 5) z 250 sesji, kapitał_t = kapitał_{t−1}·(1 + ALLOC·u_t), start ≈ 0,76 szczytu, szczyt kroczący, kill gdy kapitał < 0,75·szczyt na zamknięciu.

σ jednostkowa W8: 250 ses. 9,31%/d (60: 9,28; 125: 9,72; 500: 9,30; 1250: 9,02).

| ALLOC | gross | σ_d kapitału | P(kill 5) | P(kill 10) | P(kill 20) | poduszka w σ_d |
|---|---|---|---|---|---|---|
| 0,24 | 240% | 2,23% | **52%** | **65%** | 76% | 0,7 |
| 0,12 | 120% | 1,12% | 31% | 47% | 61% | 1,5 |
| 0,08 | 80% | 0,74% | **18%** | **34%** | 50% | 2,2 |
| 0,06 | 60% | 0,56% | 11% | 24% | 40% | 3,0 |
| 0,04 | 40% | 0,37% | 5% | 12% | 25% | 4,5 |

Wrażliwość (P(kill 5)/P(kill 10)): okno 60 → 48%/64% (0,24), 11%/23% (0,08); okno 1250 → 49%/63%; blok 1 → 56%/69%; blok 20 → 55%/66%; surowe z dryfem historycznym (W8 miało +1,16 p.p./5 ses. in-sample) → 44%/54%; Gauss iid tej samej σ → 57%/68%; ciągły monitoring (odbicie, górna granica) → 74%/81%. **Liczby twierdzenia leżą w środku przedziału 44–57% / 54–69% i są odporne na metodę.** Źródło: `weryfikacja_C9_out.md` §1.

**Zastrzeżenie reżimu σ:** σ jednostkowa W8 z ostatnich 20 sesji = 4,88%/d, z 10 = 5,13%, z 5 = 6,26% — wobec 9,3% z 250 sesji (stosunek 0,53). Bootstrap z 250 sesji przeskalowany do σ20 daje P(kill 5/10) = **32%/48%** przy 0,24 i **7%/15%** przy 0,08. Estymatory σ20/σ60 mają zbliżoną moc prognostyczną (`ryzyko_extra.py`: korelacja log-σ 0,60/0,60, mediana realizowana/prognoza 0,83–0,89), więc nie da się wskazać, który jest właściwy; VIX 16.10 = 20,0 (mediana 250 ses. 17,1), σ20 ^NDX 1,17% vs 250 ses. 1,25% — rynek nie jest w reżimie podwyższonej zmienności. Uczciwy przedział dla 5 sesji przy 0,24: **32–58%**.

## 2. Czego twierdzenie nie liczy: poniedziałek 13:45 UTC to kill na księdze W7

`app.py:1397-1425` buduje `positions` z `managed` (uniwersum + epiki z `tactical` + epiki z `fills`), potem `1485-1503` sprawdza kill — **przed** `NIEAKTUALNA` (1506), bramką, stopami i rotacją. O 13:45 UTC w poniedziałek na rachunku jest jeszcze księga W7 (powyżej), więc pierwsze sprawdzenie dotyczy jej luki piątek→poniedziałek, nie koszyka W8.

Księga W7 (wagi = ekspozycja/kapitał z `/status`, bez ERIC): σ dzienna kapitału 3,08% (250 ses.) / 2,69% (500 ses.); zrealizowane 12–16.10: −3,5 / −1,6 / −4,9 / −4,3 / −4,3% kapitału. P(strata w luce > 1,64% kapitału) z bootstrapu 1-dniowego, dla udziału wariancji luki f w wariancji dobowej:

| f | 250 ses. | 500 ses. | Gauss |
|---|---|---|---|
| 0,3 | 16% | 10% | 17% |
| 0,5 | **21%** | 15% | 23% |
| 1,0 | 29% | 22% | 30% |

Łączna ścieżka (pon. 13:45 na W7 z f=0,5 → rotacja z kosztem c → W8 od 17:05; c = spread połówkowy × 19 transakcji × ~24% nominału ≈ 0,2–0,7% kapitału wg audytu 28.09 i `wykonanie-bota.md`):

| ALLOC W8 | c | P(kill pon. 13:45) | P(kill 5 ses.) | P(kill 10) | P(kill 20) |
|---|---|---|---|---|---|
| 0,24 | 0,0% | 21% | 55% | 66% | 76% |
| 0,24 | 0,3% | 21% | **58%** | **69%** | 77% |
| 0,08 | 0,0% | 21% | 35% | 43% | 54% |
| 0,08 | 0,3% | 21% | **39%** | **48%** | 58% |
| 0,04 | 0,3% | 21% | 31% | 37% | 43% |

Wniosek: dla ALLOC 0,24 korekta jest mała (52→58%), bo W8 i tak dominuje; dla ALLOC 0,08 twierdzenie **zaniża ryzyko dwukrotnie** (18%→39% w 5 sesji), bo zmiana ALLOC w Renderze nie dotyka luki na W7 — ta ekspozycja istnieje niezależnie od decyzji o sizingu. Dwa sprawdzenia dziennie (13:45 i 17:05 UTC) zamiast jednego na zamknięciu podnoszą P(kill) o dalsze 3–6 p.p. (Gauss: 56→62% przy 0,24, 22→25% przy 0,08; §4 wyjścia).

## 3. „Wstrzymany bezterminowo" — potwierdzone w kodzie, z jedną ukrytą ścieżką

- `app.py:1488-1503`: `szczyt = equity_peak or START_EQUITY`; `odniesienie = max(szczyt, START_EQUITY)`; `prog = odniesienie × KILL_LEVEL`; gdy `equity < prog`: `do_close` dla WSZYSTKICH `positions` (w `/run` obejmuje epiki z `fills`, więc także ERIC — inaczej niż w `/status`, który liczy książkę bez taktycznych), powiadomienie i `return rep` — bieg kończy się przed bramką, stopami, rotacją i zapisem `fills`/`equity_peak` (1912-1970 nie wykonują się).
- Bez pozycji kapitał jest stały (gotówka, brak odsetek), szczyt w pliku się nie zmienia → warunek `equity < prog` jest prawdziwy w każdym kolejnym biegu. Brak w kodzie licznika, cooldownu, pola „wznowienie" ani zmiennej odblokowującej. `DRY_RUN` nie omija sprawdzenia. **Potwierdzone.**
- Ścieżki wznowienia (wszystkie ręczne): (i) `equity_peak` w `signals.json`; (ii) `START_EQUITY`; (iii) `KILL_LEVEL`; (iv) **`KILL_TRAILING=false`** — pominięta w twierdzeniu: `odniesienie = START_EQUITY` → próg 0,75·1000, a kapitał po kill ≈ 0,74 × szczyt ≈ 0,81 × START_EQUITY > próg → handel rusza od razu z poduszką ~7% (to przypadkowa, nie projektowana furtka — do odnotowania, nie do użycia).
- Test `scripts/test_app.py` sprawdza walidator (`equity_peak nie wolno ruszać sobocie`, l. 878-880), ale nie ma testu „kill → każdy kolejny bieg bez handlu" — wniosek pochodzi z czytania kodu, nie z testu.

## 4. Mechanika restartu — „reset equity_peak LUB START_EQUITY" jest błędne

Przy `kapital/START_EQUITY ≈ 0,83` (zaokrąglone celowo; START_EQUITY = 1000 domyślne, niezweryfikowane na Renderze):

| opcja | poduszka | 0,24: P(kill 5/10/20/60) | 0,08: P(kill 5/10/20/60) |
|---|---|---|---|
| (0) nic | 1,7% | 52/65/75/86% | 18/33/49/70% |
| (a) `equity_peak := kapitał`, START_EQUITY 1000 → odniesienie = START_EQUITY | **11,0%** | 4/11/24/50% | 0/0/0/6% |
| (b) tylko `START_EQUITY := kapitał` (plik bez zmian) → odniesienie = equity_peak | **1,7%** (bez efektu) | 52/64/74/86% | 19/34/50/70% |
| (c) `equity_peak := kapitał` **oraz** `START_EQUITY ≤ kapitał` | 33,3% (= pełne 25% DD) | 0/0/1/15% | 0/0/0/0% |
| (d) KILL_LEVEL 0,70, szczyt bez zmian | 8,9% | 8/17/32/57% | 0/0/1/12% |

- Sam reset `equity_peak` (jak sugeruje „lub") daje próg 0,75·START_EQUITY, czyli poduszkę 11%, nie 25%; samo START_EQUITY nie działa, bo `max(szczyt, START_EQUITY)` bierze szczyt z pliku. Prawidłowy restart z pełną poduszką = **obie** zmiany na raz, albo `START_EQUITY := kapitał` **i** `equity_peak := ta sama wartość`.
- **Nie usuwać klucza `equity_peak`:** `scripts/waliduj_signals.py` wymaga zestawu kluczy top-level DOKŁADNIE równego `KLUCZE` (15 kluczy, docstring l. 25-26, `KLUCZE` l. 35) — brak klucza unieważnia każdy kolejny bieg obu rutyn (FALLBACK). Wartość trzeba nadpisać, nie skasować. Przy 0,24 opcja (a) i tak daje 24% w 20 sesji — restart bez obniżenia ALLOC nie ma sensu, co twierdzenie słusznie mówi.
- Kto może to zrobić: wyłącznie **właściciel ręcznym commitem**. `equity_peak` jest w `POLA_BOTA` walidatora (l. 38, 125-127) i na liście „NIE RUSZAJ" CLAUDE.md oraz obu rutyn; rutyna, która to zmieni, dostaje kod wyjścia ≠ 0 i FALLBACK. `app.py::_sanity` (l. 350-375) nie sprawdza `equity_peak` w ogóle, więc bot przyjmie każdą liczbę; kolejna rutyna waliduje `--diff HEAD`, a HEAD zawiera już commit właściciela → przechodzi. Kolejność: (1) Render: `ALLOC_PCT` (docelowy) i `START_EQUITY := kapitał` (zmiana env restartuje serwis), (2) commit `equity_peak := kapitał` przed 13:45 UTC poniedziałku; po pierwszym zapisie bot i tak nadpisze `equity_peak = max(zapisany, equity)` (1960-1961) — to pożądane. CLAUDE.md: w treści commita bez kwoty (bot sam pisze kwoty w swoich commitach, ale reguła dla ludzi i rutyn stoi).

## 5. Czy restart to „jedyna sensowna opcja"? — koszt czekania w liczbach

W8, 20 sesji, zero alfy (§6 wyjścia):

| ALLOC | P(kill 20) | E[przestrzał pod progiem \| kill] | mediana sesji do kill | kapitał/szczyt po 20 ses.: p5 / med / p95 | E[kapitał/szczyt] |
|---|---|---|---|---|---|
| 0,24 | 75% | 1,19% | 3 | 0,727 / 0,746 / 0,876 | 0,7648 |
| 0,08 | 49% | 0,43% | 7 | 0,743 / 0,752 / 0,802 | 0,7634 |
| 0,04 | 25% | 0,21% | 11 | 0,747 / 0,763 / 0,782 | 0,7627 |

Restart teraz (zamknięcie W7 ręcznie lub przez `status=NIEAKTUALNA`) = kapitał ≈ 0,761 szczytu pewny (po koszcie zamknięcia ~0,2%). Czekanie ma tę samą wartość oczekiwaną (0,763–0,765 minus koszty) — kill switch nie kosztuje w średniej, on **obcina** rozkład: w 75% ścieżek (0,24) kończy się na ~0,74 (poduszka ≈ 1,7 % + przestrzał 1,2% = ok. 2,9 p.p. kapitału poniżej restartu teraz), w 25% zostaje otwarta droga do p95 0,876. Decyzja jest więc o wariancji i o tym, kto wybiera moment zamknięcia — nie o pieniądzach w średniej. Twierdzenie ma rację, że moment zamknięcia przez kill jest losowy, ale „jedyna" przecenia: (i) zamknięcie bez restartu (zostać płasko do zmiany metody) jest równie spójne z danymi faz 1–2 (alfa selekcji t ≈ −0,12 za W1–W7, zakład czynnikowy SOX wyjaśnia 74% spreadu) — restart z nowym sizingiem zakłada, że problemem był sizing, a nie brak przewagi; (ii) przepisanie szczytu *zanim* kill zadziała to dokładnie „przesuwanie progu po stracie", które `wykonanie-bota.md` rekomenduje nie robić („Nie zmieniać KILL_LEVEL/KILL_TRAILING … unika przesuwania progu po stracie") — różnica między „świadomy restart" a „zadziałanie kill i restart tydzień później" to ≤ 2,9 p.p. kapitału i tydzień czasu, a nie zmiana jakościowa; (iii) w wariancie restartu bez obniżenia ALLOC (opcja (a), 0,24) kill w 20 sesji wraca do 24% — bez sizingu restart nic nie załatwia.

Alternatywa „`status=NIEAKTUALNA` przed poniedziałkiem": bot zamyka wszystko o 13:45 (po sprawdzeniu kill — więc 21% luki W7 i tak obowiązuje; oba wyjścia kończą się tak samo: płasko), ale nie zmienia progu: poduszka zostaje ≈ 1,7 % i każdy późniejszy `AKTUALNA` wraca do tego samego stanu. Zaletą jest, że pole `status` należy do rutyn (rutyna tygodniowa może je ustawić w sobotę przy P2, puls przy zdarzeniu unieważniającym; właściciel ręcznie zawsze), a rozstrzygnięcie o progu i sizingu zostaje jawną, osobną decyzją właściciela. NIEAKTUALNA odracza, nie rozwiązuje — zgodnie z twierdzeniem.

## 6. Najsilniejszy kontrargument

Twierdzenie mierzy ryzyko koszyka, którego jeszcze nie ma na rachunku, i pomija ten, który jest: pierwsze sprawdzenie kill (pon. 13:45 UTC) dotyczy księgi W7 (σ_d 2,7–3,1% kapitału, 9 pozycji, gross ~218%) i daje ~21% (15–29%) szans na zamknięcie niezależnie od ALLOC. Przez to porównanie „0,24 → 50%, 0,08 → 18%" sugeruje, że obniżenie ALLOC zmniejsza ryzyko tygodnia 2,8×, a faktycznie (39% vs 58%) 1,5×. Drugi kontrargument: zalecany „reset equity_peak lub START_EQUITY" nie daje 25% poduszki w żadnym z dwóch wariantów osobno (11% albo 0 zmiany), a usunięcie klucza wywraca walidator rutyn.

## 7. Zrewidowane twierdzenie

Kapitał ≈ 1,7 % nad progiem (≈ 0,76 szczytu, `/status` 18.10). Koszyk W8 przy ALLOC 0,24 (σ_d kapitału 2,2% z 250 sesji; 1,2% z 20 sesji): P(kill) 44–58% w 5 sesji i 54–69% w 10 (środek 52%/65%), do tego ~21% (15–29%) na samej luce poniedziałkowej księgi W7, która istnieje niezależnie od ALLOC; łącznie z kosztem rotacji 0,3%: 58%/69% przy 0,24 i **39%/48%** przy 0,08 (nie 18%/33%). Po kill bot jest płasko bezterminowo (app.py:1497-1503, brak ścieżki automatycznego wznowienia; ręczne: equity_peak, START_EQUITY, KILL_LEVEL, KILL_TRAILING=false). Restart z pełną poduszką 25% wymaga **jednocześnie** `equity_peak := kapitał` (nadpisać, nie usuwać; commit właściciela, nie rutyny) i `START_EQUITY ≤ kapitał` na Renderze; sam reset `equity_peak` daje 11%, samo START_EQUITY — 0. Przy zerowej alfie restart teraz i czekanie mają tę samą wartość oczekiwaną (0,761 vs 0,765 szczytu); restart kupuje pewność kosztem p95 i jest tożsamy z przesunięciem progu po stracie — jego sens zależy od tego, czy właściciel wierzy w alfę po zmianie sizingu, czego dane W1–W7 nie rozstrzygają.

## 8. Implikacja projektowa

1. Decyzja przed pon. 13:45 UTC ma trzy spójne warianty, nie jeden: (A) zostać płasko (ręczne zamknięcie / `NIEAKTUALNA`) i nie restartować do zmiany metody; (B) świadomy restart = `START_EQUITY := kapitał` + `equity_peak := kapitał` + `ALLOC_PCT ≤ 0,08` naraz, zanim bot otworzy W8; (C) nic nie robić i przyjąć ~60% szans zamknięcia w tym tygodniu jako zaprojektowane działanie bezpiecznika. Półśrodek „tylko ALLOC 0,08" zostawia 39%/48%/58% (5/10/20 sesji).
2. W kodzie brakuje polityki wznowienia po kill (licznik, cooldown w `version`, start od ALLOC_MIN) — dziś wznowienie to zawsze ręczna edycja pola bota, niewidoczna dla walidatora i testów. Jeśli reset ma być procedurą, powinien mieć własne pole/zmienną (np. `KILL_RESET_AT=<version>`), test w `test_app.py` i wpis w INSTRUKCJA.md, zamiast edycji `equity_peak`.
3. Raport tygodniowy/puls powinny podawać poduszkę w σ dziennej **bieżącej księgi** (tej na rachunku), nie tylko nowego koszyka — w poniedziałek to inny koszyk.

## 9. Zastrzeżenia

- Symulacja na zamknięciach; bot sprawdza mid o 13:45 i 17:05 UTC (korekta +3–6 p.p., §4). Luka weekendowa modelowana jako 1 sesja z udziałem wariancji f (0,3–1,0) — bez danych OHLC to przedział, nie estymata.
- ERIC (taktyczna, ~20% kapitału nominalnie, poza NDX-100) pominięty w księdze W7 — P(kill pon.) jest dolnym oszacowaniem o kilka punktów.
- Zero alfy przez wyśrodkowanie 250 sesji; wariant surowy (z dryfem W8 in-sample +1,16 p.p./5 ses.) obniża P(kill 5) o ~8 p.p.
- START_EQUITY na Renderze przyjęto jako domyślne 1000 — jeśli zostało zmienione, poduszka opcji (a) jest inna (wzór: 1 − 0,75·START_EQUITY/kapitał).
- Survivorship bias danych (skład dzisiejszy); nie wpływa na W8/W7 (nazwy obecne), wpływa na „typowy koszyk".
- Bez liczb z rachunku w USD: wyłącznie stosunki do szczytu i do START_EQUITY.
