# Weryfikacja C9 — wyniki skryptu weryfikacja_C9.py

Stan: kapital/szczyt ~0.76, prog 0.75 -> poduszka ~1.7% kapitalu; alloc per noga x 10 nog = gross.

## 1. Replikacja (W8, 250 sesji, demean, blok 5, 20 000 sciezek) i wrazliwosc

sigma jednostkowa W8: 250 ses. 9.31%/d; 60 ses. 9.28%/d; 125 ses. 9.72%/d; 500 ses. 9.30%/d; 1250 ses. 9.02%/d

| ALLOC | gross | sigma_d kap. | P(kill 5) | P(kill 10) | P(kill 20) | poduszka w sigma_d |
|---|---|---|---|---|---|---|
| 0.24 | 240% | 2.23% | 52% | 65% | 76% | 0.7 |
| 0.12 | 120% | 1.12% | 31% | 47% | 61% | 1.5 |
| 0.08 | 80% | 0.74% | 18% | 34% | 50% | 2.2 |
| 0.06 | 60% | 0.56% | 11% | 24% | 40% | 3.0 |
| 0.04 | 40% | 0.37% | 5% | 12% | 25% | 4.5 |

Wrazliwosc (ALLOC 0,24 / 0,08; P(kill 5) / P(kill 10)):

| wariant | sigma_d (0,24) | 0,24: 5 ses. | 0,24: 10 ses. | 0,08: 5 ses. | 0,08: 10 ses. |
|---|---|---|---|---|---|
| okno 60, blok 5 | 2.23% | 48% | 64% | 11% | 23% |
| okno 125, blok 5 | 2.33% | 49% | 63% | 20% | 35% |
| okno 250, blok 1 | 2.23% | 56% | 69% | 21% | 38% |
| okno 250, blok 10 | 2.23% | 53% | 63% | 18% | 33% |
| okno 250, blok 20 | 2.23% | 55% | 66% | 19% | 34% |
| okno 250, SUROWE (z dryfem hist.) | 2.23% | 44% | 54% | 15% | 25% |
| okno 500, blok 5 | 2.23% | 51% | 65% | 19% | 35% |
| okno 1250, blok 5 | 2.17% | 49% | 63% | 17% | 32% |
| Gauss iid, sigma 250 ses., ALLOC 0.24 | 2.23% | 57% | 68% | - | - |
| Gauss iid, sigma 250 ses., ALLOC 0.08 | 0.74% | 22% | 38% | - | - |
| odbicie (ciagly monitoring, Gauss), ALLOC 0.24 | 2.23% | 74% | 81% | - | - |
| odbicie (ciagly monitoring, Gauss), ALLOC 0.08 | 0.74% | 32% | 48% | - | - |

## 2. Poniedzialek 13:45 UTC: kill sprawdzany na KSIAZCE W7 (przed rotacja)

ksiazka W7 (9 pozycji z /status, wagi = ekspozycja/kapital, gross 218%, bez ERIC): sigma dzienna kapitalu 250 ses. 3.08%, 500 ses. 2.69%; ostatnie 5 sesji (13–16.10 + 12.10) zrealizowane: -3.5%, -1.6%, -4.9%, -4.3%, -4.3%

Luka pt. zamkniecie -> pon. 13:45 UTC to ~1 sesja zwrotu (weekend) z udzialem wariancji f (overnight/doba). P(strata > poduszka) z bootstrapu 1-dniowego:

| f (udzial wariancji luki) | P(kill 13:45 pon., 250 ses.) | 500 ses. | Gauss |
|---|---|---|---|
| 0.3 | 16% | 10% | 17% |
| 0.5 | 21% | 15% | 23% |
| 0.7 | 25% | 19% | 26% |
| 1.0 | 29% | 22% | 30% |

Uwaga: poduszka liczona od kapitalu = ≈ 1,7 % kapitalu = 1,64% w ujeciu 'strata/kapital' (0,0167/1,0167). W7 na rachunku to realny stan 18.10 (pokrycie_koszyka: 9 pozycji spoza koszyka W8, APP SELL kontynuowany).

## 3. Laczna sciezka: pon. 13:45 na W7 (f=0,5) -> rotacja z kosztem c -> W8 od 17:05 (ALLOC a)

Koszt rotacji c = spread polowkowy ~0,05–0,15% x (9 zamkniec + 10 otwarc) x ~24% nominalu = ok. 0,2–0,7% kapitalu (audyt 28.09: AVGO 0,088%, SBUX 0,328%, CMCSA 0,312% na pare; wykonanie-bota.md: podwojny spread w dniu rotacji).

| ALLOC W8 | c | P(kill pon. 13:45) | P(kill w 5 ses.) | P(kill w 10 ses.) | P(kill w 20 ses.) |
|---|---|---|---|---|---|
| 0.24 | 0.0% | 21% | 55% | 66% | 76% |
| 0.24 | 0.3% | 21% | 58% | 69% | 77% |
| 0.24 | 0.6% | 22% | 61% | 71% | 79% |
| 0.12 | 0.0% | 21% | 41% | 52% | 62% |
| 0.12 | 0.3% | 21% | 45% | 56% | 66% |
| 0.12 | 0.6% | 21% | 49% | 60% | 69% |
| 0.08 | 0.0% | 21% | 35% | 43% | 54% |
| 0.08 | 0.3% | 21% | 39% | 48% | 58% |
| 0.08 | 0.6% | 21% | 43% | 53% | 62% |
| 0.04 | 0.0% | 21% | 27% | 32% | 38% |
| 0.04 | 0.3% | 21% | 31% | 37% | 43% |
| 0.04 | 0.6% | 21% | 36% | 42% | 48% |

## 4. Dwa sprawdzenia dziennie (13:45 i 17:05 UTC) zamiast jednego na zamknieciu — Gauss, ta sama sigma dzienna

| ALLOC | 1 sprawdzenie/d: 5 ses. | 2 sprawdzenia/d (f=0,5): 5 ses. | 10 ses.: 1 | 10 ses.: 2 |
|---|---|---|---|---|
| 0.24 | 56% | 62% | 68% | 73% |
| 0.08 | 22% | 25% | 38% | 41% |

## 5. Mechanika restartu wg app.py:1488-1492: odniesienie = max(equity_peak or START_EQUITY, START_EQUITY); prog = odniesienie x KILL_LEVEL

kapital/START_EQUITY(1000) ~ 0.83 (equity_peak/1000 ~ 1.09; wartosci zaokraglone celowo; START_EQUITY na Renderze NIE jest w /status.ustawienia — zalozono domyslne 1000 z app.py:164).

| opcja | poduszka nad progiem | 0,24: P(kill 5/10/20/60 ses.) | 0,08: P(kill 5/10/20/60) |
|---|---|---|---|
| (0) nic nie robic | 1.7% | 52%/65%/75%/86% | 18%/33%/49%/70% |
| (a) equity_peak := kapital, START_EQUITY 1000 bez zmian -> odniesienie = START_EQUITY | 11.0% | 4%/11%/24%/50% | 0%/0%/0%/6% |
| (b) tylko START_EQUITY := kapital (equity_peak w pliku bez zmian) -> odniesienie = equity_peak | 1.7% | 52%/64%/74%/86% | 19%/34%/50%/70% |
| (c) equity_peak := kapital ORAZ START_EQUITY <= kapital (albo usunac equity_peak + START_EQUITY := kapital) | 33.3% | 0%/0%/1%/15% | 0%/0%/0%/0% |
| (d) KILL_LEVEL 0,70, szczyt bez zmian | 8.9% | 8%/17%/32%/57% | 0%/0%/1%/12% |
| (e) KILL_LEVEL 0,65, szczyt bez zmian | 17.3% | 0%/2%/9%/34% | 0%/0%/0%/1% |

Uwaga do (c): po restarcie bot przy pierwszym zapisie fills nadpisze equity_peak = max(zapisany, kapital) (app.py:1960-1961), wiec reset trzyma sie tylko, gdy START_EQUITY <= nowy equity_peak; przy START_EQUITY > kapital odniesienie i tak = START_EQUITY (opcja a).

## 6. Koszt czekania na automatyczny kill vs restart teraz (W8, 20 sesji, zero alfy)

| ALLOC | P(kill 20) | E[przestrzal pod progiem | kill] | mediana sesji do kill | kapital/szczyt po 20 ses.: p5 / mediana / p95 | E[kapital/szczyt] |
|---|---|---|---|---|---|
| 0.24 | 75% | 1.19% | 3 | 0.727 / 0.746 / 0.876 | 0.7648 |
| 0.12 | 61% | 0.63% | 6 | 0.739 / 0.749 / 0.822 | 0.7640 |
| 0.08 | 49% | 0.43% | 7 | 0.743 / 0.752 / 0.802 | 0.7634 |
| 0.04 | 25% | 0.21% | 11 | 0.747 / 0.763 / 0.782 | 0.7627 |

Restart teraz (zamkniecie W7 na poziomie ~0.76 szczytu, koszt zamkniecia ~0,2–0,3%) = kapital/szczyt ~0.761 pewny; czekanie: ten sam E[kapital] minus koszty, ale rozklad dwumodalny (kill ~0,74 albo W8 w grze).

