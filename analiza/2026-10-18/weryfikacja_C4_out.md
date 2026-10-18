# Weryfikacja C4 — skrypt weryfikacja_C4.py

Dane: /tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/../dane/closes_5y.csv; sesje 2021-10-18..2026-10-16; uniwersum 103 spolek (sklad dzisiejszy, survivorship bias).
Sciezka momentum 6M 5/5 (jak v2 w bt_symulacja-wykonania.py): 234 tygodni, 1124 sesji, 2022-04-26..2026-10-16.
Zwrot jednostkowy u = suma 5 long - suma 5 short; zwrot kapitalu = ALLOC x u. Srednia u +1.105%/d (= +1.10 p.p. spread/tydz.), sigma u 17.93%/d (x0,24 = 4.30%/d kapitalu).

## A. Czy tygodnie sa niezalezne? Autokorelacja zmiennosci sciezki momentum

| lag | ACF u | ACF |u| | ACF u^2 |
|---|---|---|---|
| 1 | -0.013 | +0.216 | +0.214 |
| 2 | -0.014 | +0.252 | +0.218 |
| 3 | +0.041 | +0.259 | +0.292 |
| 5 | -0.043 | +0.251 | +0.206 |
| 10 | -0.022 | +0.235 | +0.231 |
| 20 | -0.030 | +0.219 | +0.200 |

Sigma tygodniowa zrealizowana (RMS u w tygodniu, n=234): ACF lag1 +0.597, lag2 +0.496, lag4 +0.527, lag8 +0.415. Zwrot tygodniowy: ACF lag1 +0.007, lag2 +0.007, lag4 -0.033.
Blad std ACF ~ 1/sqrt(n): dzienny 0.030, tygodniowy 0.065. Ljung-Box-podobna suma kwadratow ACF(u^2) lag 1-20 x n = 924 (chi2(20) krytyczne 31,4).

## B. P(kill) na sciezce historycznej momentum 6M (okna kroczace, start od szczytu = kapital startowy)

| ALLOC | 12 tyg., alfa in-sample (+1,3 p.p./tyg) | 12 tyg., alfa 0 (wysrodkowane) | 52 tyg., alfa in-sample | 52 tyg., alfa 0 | DD p95 12 tyg. alfa 0 |
|---|---|---|---|---|---|
| 0.24 | 41.8% (n=213) | **51.2%** | 100.0% (n=173) | **100.0%** | -30.5% |
| 0.16 | 21.1% (n=213) | **32.4%** | 80.9% (n=173) | **100.0%** | -29.4% |
| 0.12 | 5.6% (n=213) | **8.0%** | 14.5% (n=173) | **64.7%** | -25.2% |
| 0.10 | 4.7% (n=213) | **5.6%** | 7.5% (n=173) | **44.5%** | -25.8% |
| 0.08 | 3.8% (n=213) | **3.8%** | 6.4% (n=173) | **22.0%** | -21.7% |

Uwaga: okna nakladajace sie (krok 5 sesji), wiec n to nie liczba niezaleznych prob. '37-41%' z C4 pochodzi z okien 12-tyg. Z alfa in-sample (sredni spread +1,0 p.p./tydz., kapital +1,3 p.p.); C4 przypisuje te liczbe 'zerowej alfie'.

## C. Bootstrap z wysrodkowanej sciezki momentum (alfa 0): zaleznosc P(kill) od struktury zaleznosci

GARCH(1,1) na u (wysrodkowane): omega 3.63e-04, alpha 0.085, beta 0.904, alpha+beta 0.989 (polowiczny czas zaniku szoku 61.0 sesji); sigma bezwarunkowa 17.93%/d; kurtoza reszt z 3.93 (u surowe 4.82).

| ALLOC | horyzont | iid dzienny | blok 5 | blok 10 | blok 20 | blok 60 | tygodniowy iid | GARCH(1,1) | GARCH start h=sigma60 W7 |
|---|---|---|---|---|---|---|---|---|---|
| 0.24 | 12 tyg. | 65.3% | 61.9% | 59.8% | 57.0% | 51.1% | 63.3% | 60.3% | 61.8% |
| 0.12 | 12 tyg. | 13.5% | 12.1% | 11.3% | 12.3% | 8.2% | 11.7% | 15.7% | 16.0% |
| 0.10 | 12 tyg. | 5.9% | 5.2% | 4.8% | 6.3% | 5.4% | 4.3% | 8.6% | 9.0% |
| 0.08 | 12 tyg. | 1.5% | 1.2% | 1.2% | 1.6% | 4.0% | 0.9% | 3.7% | 3.9% |
| 0.24 | 52 tyg. | 99.6% | 99.4% | 99.5% | 99.0% | 98.5% | 99.4% | 97.8% | 98.0% |
| 0.12 | 52 tyg. | 75.6% | 74.2% | 72.0% | 73.0% | 71.9% | 74.9% | 71.3% | 71.3% |
| 0.10 | 52 tyg. | 61.3% | 58.1% | 56.4% | 57.8% | 57.6% | 59.1% | 58.1% | 58.3% |
| 0.08 | 52 tyg. | 41.1% | 37.8% | 35.6% | 37.3% | 38.9% | 39.2% | 40.7% | 41.3% |

Pula: sciezka momentum 6M (sigma u 18%/d, jak koszyki W1-W8: 17,5%). 'tygodniowy iid' = losowanie calych tygodni (zalozenie niezaleznych tygodni z C4). GARCH start h=sigma W7 = scenariusz 'zaczynamy w tygodniu o podwyzszonej zmiennosci'.

## D. Estymator sigma koszyka: sigma20 vs sigma60 vs EWMA(0,94) jako prognoza sigma w nastepnym tygodniu

Panel: 234 tygodni koszykow momentum (sigma koszyka wybranego w sobote liczona z jego wlasnej historii do D0; realizacja = RMS u w tygodniu po wejsciu).
| estymator | corr(log prognoza, log realizacja) | mediana realiz./prognoza | udzial tygodni realiz. > 1,5x prognoza | udzial > 2x | MAE log |
|---|---|---|---|---|---|
| sigma60 | 0.642 | 0.86 | 9.8% | 1.7% | 0.348 |
| sigma20 | 0.627 | 0.90 | 9.4% | 2.6% | 0.362 |
| EWMA 0,94 | 0.643 | 0.85 | 6.8% | 1.7% | 0.363 |
| max(sigma20,sigma60) | 0.638 | 0.82 | 5.6% | 0.9% | 0.374 |

- vol-target 1,5%/d z sigma60: sr. ALLOC 0.095; zrealizowana sigma_d kapitalu: mediana 1.22%, p90 2.09%, p99 2.88%, max 5.00%; udzial tygodni z sigma_d kapitalu > 3% (2x cel): 0.9%
- vol-target 1,5%/d z sigma20: sr. ALLOC 0.094; zrealizowana sigma_d kapitalu: mediana 1.21%, p90 2.05%, p99 3.45%, max 5.00%; udzial tygodni z sigma_d kapitalu > 3% (2x cel): 1.7%
- vol-target 1,5%/d z EWMA: sr. ALLOC 0.091; zrealizowana sigma_d kapitalu: mediana 1.17%, p90 2.07%, p99 2.83%, max 5.00%; udzial tygodni z sigma_d kapitalu > 3% (2x cel): 0.9%
- staly ALLOC 0,10: zrealizowana sigma_d kapitalu: mediana 1.35%, p90 2.80%, p99 4.28%, max 5.10%; udzial > 3%: 7.3%

Koszyki faktyczne W1-W8 na D0 (sobota): sigma jednostkowa z 60 vs 20 sesji i wynikajacy ALLOC (cel 1,5%/d, clip 0,04-0,12) oraz P&L tygodnia:

| W | sigma60 | sigma20 | sigma20/sigma60 | ALLOC(sigma60) | ALLOC(sigma20) | ALLOC(max) | spread_pp | P&L kap. 0,24 | P&L sigma60 | P&L sigma20 | P&L staly 0,10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 22.7% | 24.1% | 1.06 | 6.6% | 6.2% | 6.2% | -4.06 | -4.9% | -1.3% | -1.3% | -2.0% |
| W2 | 16.8% | 11.8% | 0.70 | 8.9% | 12.0% | 8.9% | 6.19 | +7.4% | +2.8% | +3.7% | +3.1% |
| W3 | 20.5% | 14.9% | 0.73 | 7.3% | 10.0% | 7.3% | 1.44 | +1.7% | +0.5% | +0.7% | +0.7% |
| W4 | 26.4% | 19.8% | 0.75 | 5.7% | 7.6% | 5.7% | 13.85 | +16.6% | +3.9% | +5.2% | +6.9% |
| W5 | 24.9% | 20.3% | 0.81 | 6.0% | 7.4% | 6.0% | 5.95 | +7.1% | +1.8% | +2.2% | +3.0% |
| W6 | 24.7% | 19.1% | 0.77 | 6.1% | 7.8% | 6.1% | -5.89 | -7.1% | -1.8% | -2.3% | -2.9% |
| W7 | 18.3% | 12.8% | 0.70 | 8.2% | 11.7% | 8.2% | -21.15 | -25.4% | -8.7% | -12.3% | -10.6% |
| W8 | 9.3% | 4.9% | 0.53 | 12.0% | 12.0% | 12.0% | - | - | - | - | - |
Suma W1-W7 (liniowo, bez kosztow): ALLOC 0,24 -4.4%, vol-target sigma60 -2.8%, sigma20 -4.0%, min(ALLOC60, ALLOC20) -2.7%, staly 0,10 -1.8%.

W7 (koszyk z 9.10, sesje 12-16.10): sigma20/sigma60 jednostkowa liczona na kazde zamkniecie, zwrot jednostkowy dnia i skumulowany:

| sesja | u dnia | sigma20 do tej sesji | sigma60 | |u|/sigma60 ex ante | skumulowany u |
|---|---|---|---|---|---|
| 2026-10-09 | +0.00% | 12.8% | 18.3% | 0.0 | +0.0% |
| 2026-10-12 | -25.58% | 14.1% | 18.7% | 1.4 | -25.6% |
| 2026-10-13 | -8.10% | 14.4% | 18.7% | 0.4 | -33.7% |
| 2026-10-14 | -31.54% | 16.3% | 18.9% | 1.7 | -65.2% |
| 2026-10-15 | -20.04% | 16.5% | 19.1% | 1.1 | -85.3% |
| 2026-10-16 | -26.57% | 17.3% | 19.3% | 1.5 | -111.8% |
Interpretacja: zwrot W7 jednostkowy -111.8% (x0,24 = -26.8% kapitalu, zgodne z -21,15 p.p. x 1,2 = -25,4%) przy sigma60 ex ante 18.3%/d -> -2.7 sigma tygodniowej.

## E. Polityki sizingu na sciezce historycznej momentum 6M 2022-2026 (tygodniowe przeskalowanie)

### alfa in-sample (+1,0 p.p. spread/tydz.)

| polityka | sr. ALLOC | sigma_d kap. | sr. tyg. | sigma tyg. | Sharpe (52) | najgorszy tydz. | maxDD | kapital konc. bez kill (100=start) | z kill | data kill | okna 12 tyg. z kill | okna 52 tyg. z kill |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0,24 staly | 0.240 | 4.30% | +1.30% | 10.04% | 0.93 | -23.5% | -68.5% | 692 | 90 | 2022-06-23 | 41.8% | 100.0% |
| ALLOC 0,12 staly | 0.120 | 2.15% | +0.64% | 4.90% | 0.95 | -11.8% | -41.1% | 342 | 90 | 2024-09-03 | 5.6% | 14.5% |
| ALLOC 0,10 staly | 0.100 | 1.79% | +0.53% | 4.06% | 0.95 | -9.8% | -35.3% | 289 | 309 | 2026-07-16 | 4.7% | 7.5% |
| ALLOC 0,08 staly | 0.080 | 1.43% | +0.43% | 3.24% | 0.95 | -7.9% | -29.0% | 241 | 238 | 2026-07-29 | 3.8% | 6.4% |
| VT sigma60 1,5% [0,04;0,12] | 0.095 | 1.45% | +0.51% | 3.41% | 1.07 | -7.5% | -24.1% | 286 | 286 | - | 0.0% | 0.0% |
| VT sigma20 1,5% [0,04;0,12] | 0.094 | 1.45% | +0.47% | 3.45% | 0.98 | -8.6% | -25.2% | 262 | 91 | 2024-09-03 | 0.0% | 6.9% |
| VT EWMA 1,5% [0,04;0,12] | 0.091 | 1.39% | +0.48% | 3.33% | 1.04 | -8.0% | -23.4% | 272 | 272 | - | 0.0% | 0.0% |
| VT min(s60,s20) 1,5% [0,04;0,12] | 0.090 | 1.37% | +0.47% | 3.29% | 1.02 | -7.5% | -24.3% | 264 | 264 | - | 0.0% | 0.0% |
| VT sigma60 1,5% [0,04;0,24] | 0.106 | 1.58% | +0.56% | 3.90% | 1.03 | -10.2% | -29.8% | 311 | 99 | 2024-02-21 | 0.9% | 24.9% |
| VT sigma60 2,0% [0,04;0,16] | 0.126 | 1.94% | +0.68% | 4.60% | 1.06 | -9.9% | -31.4% | 386 | 98 | 2024-02-21 | 0.0% | 25.4% |
| VT sigma60 1,0% [0,03;0,10] | 0.068 | 1.03% | +0.37% | 2.50% | 1.06 | -5.6% | -18.3% | 220 | 220 | - | 0.0% | 0.0% |

### alfa 0 (wysrodkowane)

| polityka | sr. ALLOC | sigma_d kap. | sr. tyg. | sigma tyg. | Sharpe (52) | najgorszy tydz. | maxDD | kapital konc. bez kill (100=start) | z kill | data kill | okna 12 tyg. z kill | okna 52 tyg. z kill |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0,24 staly | 0.240 | 4.30% | +0.02% | 9.92% | 0.01 | -24.4% | -87.7% | 35 | 86 | 2022-05-31 | 51.2% | 100.0% |
| ALLOC 0,12 staly | 0.120 | 2.15% | +0.00% | 4.86% | 0.01 | -12.3% | -62.2% | 77 | 81 | 2022-07-20 | 8.0% | 64.7% |
| ALLOC 0,10 staly | 0.100 | 1.79% | +0.00% | 4.04% | 0.00 | -10.2% | -55.1% | 83 | 80 | 2023-02-01 | 5.6% | 44.5% |
| ALLOC 0,08 staly | 0.080 | 1.43% | +0.00% | 3.22% | 0.00 | -8.2% | -46.9% | 89 | 79 | 2023-02-15 | 3.8% | 22.0% |
| VT sigma60 1,5% [0,04;0,12] | 0.095 | 1.45% | +0.00% | 3.39% | 0.00 | -7.9% | -55.1% | 88 | 77 | 2023-02-09 | 0.0% | 48.6% |
| VT sigma20 1,5% [0,04;0,12] | 0.094 | 1.45% | -0.03% | 3.43% | -0.07 | -9.0% | -57.1% | 81 | 79 | 2023-02-02 | 0.0% | 44.5% |
| VT EWMA 1,5% [0,04;0,12] | 0.091 | 1.39% | -0.00% | 3.31% | -0.01 | -8.4% | -54.0% | 88 | 77 | 2023-02-09 | 0.0% | 42.8% |
| VT min(s60,s20) 1,5% [0,04;0,12] | 0.090 | 1.37% | -0.01% | 3.27% | -0.03 | -7.9% | -54.9% | 86 | 77 | 2023-02-09 | 0.0% | 42.8% |
| VT sigma60 1,5% [0,04;0,24] | 0.106 | 1.58% | -0.01% | 3.87% | -0.02 | -11.1% | -60.1% | 83 | 76 | 2023-02-09 | 5.2% | 56.6% |
| VT sigma60 2,0% [0,04;0,16] | 0.126 | 1.94% | +0.00% | 4.56% | 0.01 | -10.4% | -66.4% | 80 | 79 | 2023-01-31 | 12.2% | 66.5% |
| VT sigma60 1,0% [0,03;0,10] | 0.068 | 1.03% | +0.00% | 2.48% | 0.01 | -6.1% | -43.2% | 94 | 75 | 2023-12-22 | 0.0% | 17.9% |

### alfa +1 p.p./tydz. (wysrodkowane + 0,01/d)

| polityka | sr. ALLOC | sigma_d kap. | sr. tyg. | sigma tyg. | Sharpe (52) | najgorszy tydz. | maxDD | kapital konc. bez kill (100=start) | z kill | data kill | okna 12 tyg. z kill | okna 52 tyg. z kill |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0,24 staly | 0.240 | 4.30% | +1.18% | 10.03% | 0.85 | -23.6% | -69.0% | 522 | 89 | 2022-06-23 | 41.8% | 100.0% |
| ALLOC 0,12 staly | 0.120 | 2.15% | +0.58% | 4.89% | 0.86 | -11.9% | -41.6% | 297 | 85 | 2024-08-07 | 6.1% | 18.5% |
| ALLOC 0,10 staly | 0.100 | 1.79% | +0.48% | 4.06% | 0.86 | -9.9% | -35.7% | 257 | 277 | 2026-07-16 | 4.7% | 7.5% |
| ALLOC 0,08 staly | 0.080 | 1.43% | +0.39% | 3.24% | 0.86 | -7.9% | -29.4% | 219 | 218 | 2026-07-29 | 3.8% | 6.4% |
| VT sigma60 1,5% [0,04;0,12] | 0.095 | 1.45% | +0.46% | 3.41% | 0.97 | -7.6% | -25.8% | 256 | 89 | 2024-09-03 | 0.0% | 6.9% |
| VT sigma20 1,5% [0,04;0,12] | 0.094 | 1.45% | +0.42% | 3.45% | 0.88 | -8.6% | -26.9% | 234 | 85 | 2024-09-03 | 0.0% | 8.7% |
| VT EWMA 1,5% [0,04;0,12] | 0.091 | 1.39% | +0.44% | 3.33% | 0.94 | -8.1% | -25.1% | 244 | 90 | 2024-09-03 | 0.0% | 6.9% |
| VT min(s60,s20) 1,5% [0,04;0,12] | 0.090 | 1.37% | +0.42% | 3.28% | 0.92 | -7.6% | -25.9% | 237 | 87 | 2024-09-03 | 0.0% | 6.9% |
| VT sigma60 1,5% [0,04;0,24] | 0.106 | 1.58% | +0.50% | 3.90% | 0.93 | -10.3% | -31.7% | 274 | 93 | 2024-02-21 | 0.9% | 24.9% |
| VT sigma60 2,0% [0,04;0,16] | 0.126 | 1.94% | +0.61% | 4.59% | 0.96 | -10.0% | -33.5% | 332 | 92 | 2024-02-21 | 0.0% | 32.9% |
| VT sigma60 1,0% [0,03;0,10] | 0.068 | 1.03% | +0.33% | 2.49% | 0.96 | -5.6% | -19.7% | 203 | 203 | - | 0.0% | 0.0% |

### alfa +0,5 p.p./tydz.

| polityka | sr. ALLOC | sigma_d kap. | sr. tyg. | sigma tyg. | Sharpe (52) | najgorszy tydz. | maxDD | kapital konc. bez kill (100=start) | z kill | data kill | okna 12 tyg. z kill | okna 52 tyg. z kill |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0,24 staly | 0.240 | 4.30% | +0.60% | 9.97% | 0.43 | -24.0% | -75.3% | 135 | 88 | 2022-06-02 | 49.3% | 100.0% |
| ALLOC 0,12 staly | 0.120 | 2.15% | +0.29% | 4.88% | 0.43 | -12.1% | -46.4% | 151 | 81 | 2023-02-08 | 6.1% | 40.5% |
| ALLOC 0,10 staly | 0.100 | 1.79% | +0.24% | 4.05% | 0.43 | -10.1% | -39.9% | 146 | 80 | 2024-01-02 | 4.7% | 20.2% |
| ALLOC 0,08 staly | 0.080 | 1.43% | +0.19% | 3.23% | 0.43 | -8.1% | -32.9% | 140 | 79 | 2024-02-21 | 3.8% | 6.4% |
| VT sigma60 1,5% [0,04;0,12] | 0.095 | 1.45% | +0.23% | 3.40% | 0.49 | -7.7% | -38.5% | 150 | 79 | 2024-01-30 | 0.0% | 13.9% |
| VT sigma20 1,5% [0,04;0,12] | 0.094 | 1.45% | +0.19% | 3.44% | 0.41 | -8.8% | -41.3% | 138 | 79 | 2024-01-03 | 0.0% | 19.7% |
| VT EWMA 1,5% [0,04;0,12] | 0.091 | 1.39% | +0.22% | 3.31% | 0.47 | -8.2% | -37.4% | 146 | 75 | 2024-02-21 | 0.0% | 13.9% |
| VT min(s60,s20) 1,5% [0,04;0,12] | 0.090 | 1.37% | +0.20% | 3.27% | 0.45 | -7.7% | -38.9% | 143 | 78 | 2024-01-30 | 0.0% | 13.9% |
| VT sigma60 1,5% [0,04;0,24] | 0.106 | 1.58% | +0.25% | 3.88% | 0.46 | -10.7% | -43.3% | 151 | 80 | 2023-12-26 | 3.8% | 30.6% |
| VT sigma60 2,0% [0,04;0,16] | 0.126 | 1.94% | +0.31% | 4.57% | 0.49 | -10.2% | -48.9% | 164 | 80 | 2023-02-09 | 6.6% | 64.7% |
| VT sigma60 1,0% [0,03;0,10] | 0.068 | 1.03% | +0.17% | 2.49% | 0.48 | -5.9% | -29.2% | 138 | 78 | 2024-07-30 | 0.0% | 6.9% |

## F. Bootstrap mieszanki koszykow W1-W8 (jak ryzyko_sizing.py §2d) — blok 5/10/20, sigma60 vs sigma20, staly 0,10 vs vol-target

| blok | polityka | sr. ALLOC | P(kill 12t) alfa 0 | P(kill 52t) alfa 0 | DD p95 12t | mediana 12t alfa +1 | srednia 12t alfa +1 | mediana 52t alfa +1 | P(kill 52t) alfa +1 | Sharpe tyg. (52) alfa +1 |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | ALLOC 0,24 | 0.240 | **60.5%** | 99.2% | -30.3% | +3.1% | +10.7% | -3.9% | 96.9% | 0.91 |
| 5 | ALLOC 0,12 | 0.120 | **11.4%** | 71.5% | -26.0% | +5.8% | +6.5% | +17.7% | 45.2% | 0.95 |
| 5 | ALLOC 0,10 | 0.100 | **5.0%** | 56.4% | -25.0% | +5.0% | +5.5% | +20.5% | 28.0% | 0.95 |
| 5 | ALLOC 0,08 | 0.080 | **1.2%** | 36.2% | -20.4% | +4.2% | +4.4% | +18.5% | 13.2% | 0.96 |
| 5 | VT sigma60 1,5% [0,04;0,12] | 0.076 | **0.4%** | 25.6% | -17.9% | +4.0% | +4.3% | +18.3% | 6.6% | 1.04 |
| 5 | VT sigma20 1,5% [0,04;0,12] | 0.093 | **2.2%** | 45.5% | -22.1% | +4.7% | +5.2% | +21.4% | 17.9% | 1.00 |
| 5 | VT sigma60 1,5% [0,04;0,24] | 0.081 | **0.5%** | 29.2% | -18.6% | +4.3% | +4.5% | +19.7% | 7.8% | 1.06 |
| 10 | ALLOC 0,24 | 0.240 | **60.6%** | 99.3% | -30.4% | +1.8% | +8.5% | -4.4% | 96.0% | 0.90 |
| 10 | ALLOC 0,12 | 0.120 | **8.4%** | 66.7% | -25.6% | +5.9% | +6.4% | +21.1% | 37.0% | 0.94 |
| 10 | ALLOC 0,10 | 0.100 | **3.0%** | 50.6% | -23.2% | +5.1% | +5.4% | +21.4% | 21.2% | 0.95 |
| 10 | ALLOC 0,08 | 0.080 | **0.6%** | 30.3% | -18.9% | +4.2% | +4.4% | +18.2% | 8.4% | 0.96 |
| 10 | VT sigma60 1,5% [0,04;0,12] | 0.076 | **0.1%** | 21.0% | -16.8% | +4.1% | +4.3% | +18.2% | 3.8% | 1.04 |
| 10 | VT sigma20 1,5% [0,04;0,12] | 0.093 | **1.1%** | 39.3% | -20.8% | +4.9% | +5.3% | +21.9% | 12.3% | 1.01 |
| 10 | VT sigma60 1,5% [0,04;0,24] | 0.081 | **0.3%** | 25.1% | -17.7% | +4.3% | +4.7% | +19.7% | 5.2% | 1.06 |
| 20 | ALLOC 0,24 | 0.240 | **59.9%** | 98.9% | -30.5% | +1.6% | +8.1% | -3.3% | 95.8% | 0.92 |
| 20 | ALLOC 0,12 | 0.120 | **8.5%** | 66.3% | -25.7% | +5.9% | +6.3% | +21.8% | 35.6% | 0.96 |
| 20 | ALLOC 0,10 | 0.100 | **3.1%** | 49.6% | -23.4% | +5.1% | +5.4% | +22.1% | 19.9% | 0.96 |
| 20 | ALLOC 0,08 | 0.080 | **0.6%** | 28.8% | -19.0% | +4.2% | +4.4% | +18.7% | 7.6% | 0.97 |
| 20 | VT sigma60 1,5% [0,04;0,12] | 0.076 | **0.1%** | 20.2% | -16.8% | +4.1% | +4.2% | +18.1% | 2.9% | 1.04 |
| 20 | VT sigma20 1,5% [0,04;0,12] | 0.093 | **1.2%** | 38.4% | -20.7% | +4.9% | +5.2% | +21.5% | 11.2% | 1.01 |
| 20 | VT sigma60 1,5% [0,04;0,24] | 0.081 | **0.3%** | 24.6% | -17.9% | +4.3% | +4.5% | +19.1% | 4.3% | 1.05 |

sigma60 / sigma20 jednostkowa koszykow na D0: W1 22.7/24.1%; W2 16.8/11.8%; W3 20.5/14.9%; W4 26.4/19.8%; W5 24.9/20.3%; W6 24.7/19.1%; W7 18.3/12.8%; W8 9.3/4.9%

## G. Inverse-vol per noga przy kroku 0,1 akcji (logika calc_size z app.py: krok otwierany, gdy min_acc <= cel x MAX_OVERSHOOT=1,6)

| kapital odniesienia (USD) | koszyk | cel sigma_d | wagi inv-vol (min / max, % kapitalu) | nogi POMIJANE (0,1 akcji > 1,6 x cel) | nogi jako min. lot (przestrzal >1x) | faktyczny gross po lotach vs zamierzony |
|---|---|---|---|---|---|---|
| 1000 | W7 | 1,5%/d | 4.8% / 23.7% | 2: MU, LITE | 0: - | 103% vs 114% |
| 1000 | W8 | 1,5%/d | 12.1% / 37.7% | 0: - | 0: - | 239% vs 246% |
| 2500 | W7 | 1,5%/d | 4.8% / 23.7% | 0: - | 0: - | 112% vs 114% |
| 2500 | W8 | 1,5%/d | 12.1% / 37.7% | 0: - | 0: - | 247% vs 246% |
| 5000 | W7 | 1,5%/d | 4.8% / 23.7% | 0: - | 0: - | 113% vs 114% |
| 5000 | W8 | 1,5%/d | 12.1% / 37.7% | 0: - | 0: - | 245% vs 246% |
| 10000 | W7 | 1,5%/d | 4.8% / 23.7% | 0: - | 0: - | 113% vs 114% |
| 10000 | W8 | 1,5%/d | 12.1% / 37.7% | 0: - | 0: - | 246% vs 246% |

Kursy z D0 koszyka (W7: 9.10.2026, W8: 16.10.2026). Krok 0,1 akcji = zalozenie z ryzyko_extra.py (Capital.com, akcje USA); app.py bierze krok z minDealSize brokera.