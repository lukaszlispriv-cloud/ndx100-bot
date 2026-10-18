Dane: 2021-10-18…2026-10-16, sesji 1255, spółek 102
Okien tygodniowych: 232 (2022-04-29…2026-10-02); dni w serii dziennej: 1115; sygnałów przekrojowych: 3194

## 1. Protokół 4/8 + druga sesja + bramka abs na koszykach momentum 6M (5/5), 2022-04…2026-10

Wariant | n | śr. pp/tydz | σ | t | p5 | p1 | min | maxDD (pp skum.) | hit | Δ vs baza (śr.) | t(Δ) | tyg. pomógł | tyg. zaszkodził | ΔmaxDD | Δp5
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---
od D0, bez reakcji (baza) | 232 | 1.09 | 7.25 | 2.29 | -10.63 | -18.52 | -25.83 | -49.76 | 0.56 | +0.000 | +nan | 0% | 0% | +0.0 | +0.00
od D0, protokół, cięcie na close sygnału | 232 | 0.95 | 7.16 | 2.01 | -10.66 | -19.89 | -21.06 | -52.70 | 0.55 | -0.145 | -1.61 | 32% | 35% | -2.9 | -0.03
od D0, protokół, cięcie na close dnia następnego | 232 | 1.07 | 7.11 | 2.29 | -11.04 | -18.83 | -23.13 | -49.80 | 0.55 | -0.022 | -0.40 | 29% | 24% | -0.0 | -0.41
od D0, jak audyt_regul (CLOSE luźniej) | 232 | 0.95 | 7.13 | 2.02 | -10.95 | -18.55 | -21.87 | -53.45 | 0.55 | -0.145 | -1.43 | 31% | 36% | -3.7 | -0.32
od D0, bez potwierdzenia 2. sesją | 232 | 0.90 | 6.81 | 2.01 | -9.31 | -16.23 | -18.89 | -44.64 | 0.53 | -0.190 | -1.42 | 38% | 49% | +5.1 | +1.32
od D+1 (pon.), bez reakcji (baza) | 232 | 1.13 | 7.66 | 2.24 | -10.27 | -17.30 | -18.76 | -53.47 | 0.53 | +0.000 | +nan | 0% | 0% | +0.0 | +0.00
od D+1, protokół, cięcie na close sygnału | 232 | 1.07 | 7.52 | 2.18 | -9.80 | -15.68 | -19.66 | -61.46 | 0.52 | -0.055 | -0.80 | 31% | 38% | -8.0 | +0.47
od D+1, protokół, cięcie na close dnia następnego | 232 | 1.14 | 7.47 | 2.33 | -9.56 | -15.62 | -18.15 | -55.29 | 0.53 | +0.016 | +0.32 | 25% | 25% | -1.8 | +0.71
od D+1, bez 2. sesji | 232 | 0.95 | 7.27 | 2.00 | -9.50 | -13.52 | -16.60 | -61.27 | 0.52 | -0.176 | -1.45 | 38% | 47% | -7.8 | +0.77
od D+1, stop 10 % + reopen (bot), bez protokołu | 232 | 1.01 | 7.73 | 1.98 | -10.30 | -16.78 | -20.00 | -60.09 | 0.52 | -0.122 | -1.77 | 46% | 52% | -6.6 | -0.03
od D+1, stop 10 % + reopen + protokół | 232 | 1.04 | 7.64 | 2.06 | -10.05 | -16.25 | -19.93 | -59.99 | 0.52 | +0.029 | +0.89 | 29% | 22% | +0.1 | +0.25

Liczba reakcji (D+1, lag 0): REDUCE 419, CLOSE 173 na 2320 nóg; tygodnie z ≥1 reakcją: 181/232; stopy 10 % (D+1): 294.
W tygodniach z reakcją (n=181): Δ śr. -0.07 pp, mediana +0.00, p10 -1.51, p90 +1.10; spread bazowy w tych tygodniach śr. -0.23 (vs +1.13 ogółem).
5 % najgorszych tygodni bazy (n=12, śr. -14.53 pp): z protokołem śr. -14.02 (lag0) / -13.38 (lag1) → Δ +0.51 / +1.16 pp.
5 % najlepszych tygodni bazy (n=12, śr. 20.17): z protokołem 19.73 → Δ -0.44 pp.

## 2. Losowe koszyki 5/5 (200 losowań/tydzień, te same okna, od D+1) — co bramka robi na SZUMIE

| | baza | protokół lag0 | protokół lag1 |
|---|---|---|---|
| śr. pp/tydz. (śr. po 200 strategiach) | +0.008 | +0.012 (Δ +0.004, szkodzi w 47%) | +0.016 (Δ +0.008, szkodzi w 38%) |
| σ tyg. | 3.52 | 3.43 | 3.47 |
| p5 tyg. | -5.47 | -5.24 (Δ +0.22) | -5.35 (Δ +0.12) |
| maxDD skum. | -60.4 | -58.3 (Δ +2.1) | -58.6 (Δ +1.8) |
Pooled (n=46400): p5 -5.57 → -5.31; p1 -9.17 → -8.62; σ 3.54 → 3.44.

## 3. Protokół (od D+1, lag0) wg reżimu — czy w VIX>25 bramka pomaga?

reżim | n | baza śr. | protokół śr. | Δ śr. | t(Δ) | baza p5 | protokół p5 | baza min | protokół min | baza maxDD | protokół maxDD
---|---|---|---|---|---|---|---|---|---|---|---
VIX(D0) > 25 | 26 | +1.02 | +0.90 | -0.12 | -0.79 | -7.49 | -8.99 | -10.2 | -10.1 | -31.6 | -35.7
VIX(D0) 20–25 | 47 | +3.11 | +2.99 | -0.12 | -1.06 | -7.64 | -7.08 | -12.9 | -15.7 | -37.0 | -38.6
VIX(D0) ≤ 20 | 159 | +0.56 | +0.54 | -0.02 | -0.26 | -11.84 | -12.49 | -18.8 | -19.7 | -68.4 | -61.5
VIX(D0) > 20 | 73 | +2.37 | +2.24 | -0.12 | -1.33 | -7.65 | -7.56 | -12.9 | -15.7 | -61.7 | -64.8
rok 2022 | 36 | -0.06 | -0.29 | -0.23 | -1.58 | -8.46 | -9.65 | -12.9 | -15.7 | -53.5 | -56.5
rok 2023 | 52 | +0.10 | +0.02 | -0.07 | -1.35 | -5.94 | -5.69 | -8.2 | -9.4 | -22.7 | -25.4
rok 2024 | 52 | +1.55 | +1.49 | -0.05 | -0.36 | -6.42 | -6.83 | -9.5 | -7.7 | -31.0 | -28.4
rok 2025 | 52 | +1.32 | +1.46 | +0.14 | +0.90 | -8.98 | -8.12 | -18.8 | -15.7 | -48.9 | -39.8
rok 2026 | 40 | +2.75 | +2.62 | -0.13 | -0.52 | -16.84 | -14.75 | -18.1 | -19.7 | -49.4 | -61.5
^NDX w oknie ≤ −2 % | 50 | -1.06 | -0.97 | +0.09 | +0.57 | -13.54 | -13.52 | -18.8 | -15.7 | -87.7 | -81.7
^NDX w oknie > −2 % | 182 | +1.73 | +1.64 | -0.09 | -1.22 | -8.95 | -8.51 | -18.1 | -19.7 | -68.7 | -77.9
^NDX w oknie ≥ +2 % | 64 | +2.07 | +2.16 | +0.09 | +0.79 | -8.59 | -9.47 | -13.4 | -15.7 | -64.2 | -68.1

## 4. Ścieżka kapitału przy ALLOC 0,24 (1,2 × spread dzienny): P(kill switch −25 % od szczytu okna) z/bez protokołu

- okna 4 tyg. (n=229): P(kill) baza 10.5% → protokół 9.6%; DD p5 -36.7% → -33.6%; mediana DD -12.2% → -11.1%
- okna 12 tyg. (n=221): P(kill) baza 32.6% → protokół 31.2%; DD p5 -51.7% → -52.9%; mediana DD -19.3% → -17.6%
- okna 26 tyg. (n=207): P(kill) baza 57.5% → protokół 56.5%; DD p5 -58.0% → -60.4%; mediana DD -33.8% → -32.8%
σ dzienna spreadu: baza 3.58 pp → protokół 3.39 pp; σ dz. kapitału (×1,2): 4.29 % → 4.07 %; najgorszy dzień -13.98 → -13.98 pp.

## 5. Sygnał „dzień ze spreadem koszyka ≤ −3 pp” → suma kolejnych 3 sesji (seria dzienna koszyka momentum od D+1)

- bezwarunkowo (wszystkie dni): n=1112, śr. sumy 3 sesji +0.70 pp (σ 6.13, t 3.82) — to jest właściwy punkt odniesienia, nie 0
- po dniu ≤ −3 pp: n=168 (nienakł. 111), śr. +1.23 pp (mediana +2.03, hit 61%), σ 7.35, t naiwne 2.16, t HAC(3) 1.92, nienakł. śr. +0.88 t 1.33
- po dniu ≥ +3 pp: n=190 (nienakł. 111), śr. +0.66 pp (mediana +0.63, hit 54%), σ 7.62, t naiwne 1.20, t HAC(3) 0.98, nienakł. śr. +0.85 t 1.24
- po dniu ≤ −3 pp, bez 2022: n=137 (nienakł. 93), śr. +1.45 pp (mediana +2.07, hit 63%), σ 7.21, t naiwne 2.36, t HAC(3) 2.07, nienakł. śr. +1.05 t 1.47
- po dniu ≤ −3 pp, rok 2022: n=31 (nienakł. 18), śr. +0.23 pp (mediana +1.58, hit 55%), σ 8.01, t naiwne 0.16, t HAC(3) 0.15, nienakł. śr. +0.01 t 0.01
- po dniu ≤ −3 pp, rok 2023: n=18 (nienakł. 16), śr. +1.22 pp (mediana +0.79, hit 56%), σ 3.10, t naiwne 1.66, t HAC(3) 1.97, nienakł. śr. +1.27 t 1.54
- po dniu ≤ −3 pp, rok 2024: n=32 (nienakł. 24), śr. +2.26 pp (mediana +2.59, hit 72%), σ 4.62, t naiwne 2.77, t HAC(3) 2.74, nienakł. śr. +2.90 t 3.11
- po dniu ≤ −3 pp, rok 2025: n=38 (nienakł. 27), śr. +1.00 pp (mediana +1.65, hit 66%), σ 6.02, t naiwne 1.03, t HAC(3) 0.79, nienakł. śr. -0.01 t -0.01
- po dniu ≤ −3 pp, rok 2026: n=49 (nienakł. 26), śr. +1.36 pp (mediana +3.07, hit 57%), σ 10.07, t naiwne 0.94, t HAC(3) 0.87, nienakł. śr. +0.31 t 0.15
- po dniu ≤ −3 pp, gdy ^NDX tego dnia ≤ −2 %: n=21 (nienakł. 19), śr. +3.38 pp (mediana +3.06, hit 67%), σ 5.94, t naiwne 2.61, t HAC(3) 3.36, nienakł. śr. +2.78 t 2.05
- po dniu ≤ −3 pp, gdy ^NDX tego dnia > −2 %: n=147 (nienakł. 104), śr. +0.92 pp (mediana +1.67, hit 61%), σ 7.50, t naiwne 1.48, t HAC(3) 1.34, nienakł. śr. +1.21 t 1.76
- po dniu ≤ −3 pp, gdy |^NDX| tego dnia < 1 % (spread własny, nie indeks): n=70 (nienakł. 58), śr. +1.86 pp (mediana +2.04, hit 67%), σ 6.92, t naiwne 2.24, t HAC(3) 2.39, nienakł. śr. +1.69 t 1.93
- po dniu ≤ −3 pp, VIX > 25: n=27 (nienakł. 18), śr. +3.04 pp (mediana +3.29, hit 67%), σ 8.57, t naiwne 1.84, t HAC(3) 1.71, nienakł. śr. +2.88 t 1.30
- po dniu ≤ −3 pp, VIX ≤ 25: n=141 (nienakł. 97), śr. +0.88 pp (mediana +1.62, hit 60%), σ 7.08, t naiwne 1.47, t HAC(3) 1.30, nienakł. śr. +0.66 t 0.96
- po dniu ≤ −5 pp: n=68 (nienakł. 53), śr. +2.16 pp (mediana +2.45, hit 66%), σ 8.17, t naiwne 2.18, t HAC(3) 2.29, nienakł. śr. +1.00 t 0.93
- po DWÓCH sesjach o sumie ≤ −4 pp (analog potwierdzenia 2. sesją): n=167 (nienakł. 93), śr. +1.85 pp (mediana +2.15, hit 63%), σ 7.63, t naiwne 3.13, t HAC(3) 2.79, nienakł. śr. +1.50 t 1.96
- po dwóch sesjach ≤ −2 pp każda: n=62 (nienakł. 39), śr. +2.59 pp (mediana +3.11, hit 68%), σ 8.05, t naiwne 2.54, t HAC(3) 2.13, nienakł. śr. +1.92 t 1.81
- po dniu ≤ −3 pp: ^NDX w kolejnych 3 sesjach śr. +0.27 % (bezwar. +0.26 %); β spreadu(3 ses.) na ^NDX(3 ses.) = 0.39, stała +1.12 pp — część odbicia niezależna od indeksu
- po dniu ≤ −3 pp: kolejne 3 sesje bez reakcji +1.23 pp vs z protokołem (wagi po reakcjach) +1.03 pp → koszt protokołu po złym dniu -0.20 pp (t sparowane -1.55)

## 6. Przekrój: pierwszy sygnał REDUCE (rel ≤ −4 dwie sesje, abs ≤ −4) w sesjach 2..K−1 od D0 → reszta okna (pp rel.)

podzbiór | n | okien | śr. reszta pp | σ | t (klastr. po d0) | hit>0
---|---|---|---|---|---|---
wszystkie | 3194 | 232 | +0.16 | 5.24 | -0.28 | 51.8%
long | 1479 | 221 | +0.34 | 4.37 | +1.00 | 51.2%
short | 1715 | 220 | +0.02 | 5.88 | -0.25 | 52.3%
poziom CLOSE (rel/abs ≤ −8 dwie sesje) | 494 | 182 | +0.18 | 7.07 | -0.69 | 49.2%
tylko REDUCE | 2700 | 232 | +0.16 | 4.83 | -0.21 | 52.3%
long top-kwintyl mom6M (jak koszyk) | 429 | 168 | +0.75 | 5.23 | +0.92 | 53.6%
short dolny kwintyl mom6M | 405 | 155 | +0.14 | 5.29 | +0.12 | 53.6%
koszykowe (top-L + bot-S) | 834 | 209 | +0.45 | 5.27 | +0.54 | 53.6%
VIX(sygnał) > 25 | 364 | 36 | +0.22 | 5.21 | -0.09 | 50.3%
VIX(sygnał) 20–25 | 507 | 58 | +0.35 | 5.12 | +0.41 | 52.1%
VIX(sygnał) ≤ 20 | 2323 | 177 | +0.11 | 5.27 | -0.42 | 52.0%
VIX > 25, koszykowe | 83 | 28 | +0.63 | 5.81 | +0.76 | 53.0%
rok 2022 | 432 | 36 | +0.06 | 4.93 | -0.06 | 51.4%
rok 2023 | 441 | 52 | -0.05 | 3.97 | -0.47 | 50.1%
rok 2024 | 546 | 52 | -0.53 | 5.28 | -1.49 | 47.8%
rok 2025 | 748 | 52 | +0.12 | 4.96 | +0.80 | 50.3%
rok 2026 | 1027 | 40 | +0.70 | 5.93 | +0.78 | 55.9%
sygnał w sesji 2 | 914 | 216 | +0.27 | 7.22 | -1.04 | 51.2%
sygnał w sesji 3 | 1167 | 222 | +0.37 | 4.86 | +0.10 | 53.0%
sygnał w sesji 4 | 1113 | 184 | -0.13 | 3.32 | -1.04 | 50.9%
^NDX od D0 do sygnału ≤ −3 % | 207 | 25 | +1.04 | 5.48 | -0.32 | 52.7%
^NDX od D0 do sygnału > −3 % | 2987 | 227 | +0.10 | 5.21 | -0.17 | 51.7%

Rozkład reszty po sygnale REDUCE: p5 -7.65, p95 8.07, σ 5.24 pp (asymetria -0.27); poziom CLOSE: p5 -11.64, p95 10.94.

## 7. In-sample W1–W7: protokół od D0 (jak audyt) vs od D+1 (pon., proxy fills), cięcie lag 0/1

tydzień | baza D0 | protokół D0 lag0 (audyt-CLOSE) | protokół D0 lag0 (ścisły CLOSE) | protokół D0 lag1 | baza D+1 | protokół D+1 lag0 | protokół D+1 lag1 | D+1 bez 2. sesji
---|---|---|---|---|---|---|---|---
W1 | -4.04 | -4.04 | -4.04 | -4.04 | -3.02 | -3.02 | -3.02 | -3.59
W2 | +6.28 | +6.28 | +6.28 | +6.28 | +6.77 | +6.77 | +6.77 | +6.77
W3 | +1.43 | +1.43 | +1.43 | +1.43 | -7.42 | -7.42 | -7.42 | -7.20
W4 | +14.36 | +11.23 | +11.23 | +13.83 | +27.14 | +27.14 | +27.14 | +27.14
W5 | +6.08 | +6.08 | +6.08 | +6.08 | +5.68 | +5.68 | +5.68 | +5.32
W6 | -5.57 | -5.21 | -5.39 | -5.67 | -8.66 | -7.49 | -7.75 | -7.64
W7 | -22.36 | -16.81 | -17.75 | -19.71 | -17.25 | -15.57 | -17.25 | -14.56
SUMA | -3.83 | -1.05 (Δ +2.78) | -2.17 (Δ +1.66) | -1.80 (Δ +2.03) | +3.26 | +6.09 (Δ +2.84) | +4.17 (Δ +0.91) | +6.24 (Δ +2.98)
Uwaga: okno D+1 dla W7 kończy się 16.10 (brak sesji D5+1 w danych) — W7 od D+1 to 12.10→16.10.