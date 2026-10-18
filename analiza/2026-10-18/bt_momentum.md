# Backtest koszyków momentum 5L/5S w uniwersum Nasdaq-100 (agent: momentum)

Dane: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv` — 1255 sesji 2021-10-18…2026-10-16, 103 kandydatów (skład dzisiejszy → survivorship bias). Okna tygodniowe: 260. Wspólny zbiór okien (wszystkie warianty mają sygnał, od D0 = 2022-10-21): 208 okien.

Harness: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; noga long = r_spółki − r_NDX, short = −(r_spółki − r_NDX); spread_pp = średnia 5 long + średnia 5 short (= P&L w % nominału jednej strony, gross = 2). Sygnały wyłącznie z cen ≤ D0. Spółki bez pełnego okna sygnału wykluczone (ALAB, ARM, CRWV, GEHC, HONA, NBIS, SNDK, SPCX, WBD, CEG do czasu uzupełnienia historii).

Koszty: rotacja 0,10% × nominał nogi (0,2 strony) za każdą ZMIENIONĄ nazwę (obrót liczony z serii), finansowanie 6%/rok × gross 2 × dni/365. Pełna rotacja 10 nóg = 0,20 pp/tydz.; finansowanie ≈ 0,23 pp/tydz.


## 1. Wyniki na wspólnym zbiorze okien (brutto)

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a_6M | 208 | 1.11 | 0.93 | 7.65 | 2.10 | 1.05 | 55% | 53% | 70.7 | -25.8 | 31.8 |
| b_12M-1M | 208 | 0.77 | 0.59 | 7.49 | 1.49 | 0.75 | 56% | 53% | 75.8 | -25.5 | 28.7 |
| c_3M | 208 | 0.95 | 0.71 | 7.51 | 1.81 | 0.91 | 56% | 51% | 70.9 | -27.6 | 39.6 |
| d_1M | 208 | 0.76 | 0.69 | 6.41 | 1.71 | 0.85 | 56% | 52% | 60.6 | -17.5 | 32.2 |
| e_6M_winsor_sigma | 208 | 0.65 | 0.32 | 5.93 | 1.57 | 0.79 | 52% | 51% | 49.1 | -24.5 | 32.0 |
| f_6M_beta_neutral | 208 | 0.38 | 0.23 | 6.47 | 0.84 | 0.42 | 51% | 53% | 73.5 | -24.8 | 23.6 |
| g_6M_max2semi | 208 | 0.75 | 0.51 | 6.69 | 1.61 | 0.81 | 52% | 52% | 62.0 | -20.4 | 31.6 |
| h_6M_industry_neutral | 208 | 0.77 | 0.88 | 6.36 | 1.75 | 0.88 | 57% | 52% | 60.2 | -18.3 | 32.6 |
| d_rev_1M_contrarian | 208 | -0.76 | -0.69 | 6.41 | -1.71 | -0.85 | 44% | 48% | 247.3 | -32.2 | 17.5 |
| a_rev_6M_contrarian | 208 | -1.11 | -0.93 | 7.65 | -2.10 | -1.05 | 45% | 47% | 307.7 | -31.8 | 25.8 |
| BASELINE losowe 5/5 (2000 koszyków/okno) | 208 | -0.00 | — | 3.40 (pooled) | 5–95% t: -1.64…1.65 | 95% Sharpe: 0.83 | — | 50% | — | p5 -5.4 | p95 5.4 |

Baseline: σ pojedynczego tygodnia losowego koszyka 5/5 (pooled) = **3.40 pp**, przedział 5–95% tygodniowego spreadu = **-5.4 … 5.4 pp**; rozkład średniej 2000 losowych STRATEGII (losowy koszyk w każdym oknie): 5–95% = -0.39 … 0.39 pp/tydz., t-stat 5–95% = -1.64 … 1.65 (97,5% = 1.97); σ tygodniowa losowej strategii 5–95% = 3.00 … 3.85 pp.


## 2. Po kosztach (wspólne okna)

| wariant | obrót nóg/tydz. | koszt rotacji pp/tydz. | finansowanie pp/tydz. | brutto pp | netto pp | t netto | Sharpe netto | hit netto | pct wśród losowych (brutto) |
|---|---|---|---|---|---|---|---|---|---|
| a_6M | 2.0 | 0.04 | 0.23 | 1.11 | 0.84 | 1.59 | 0.79 | 53% | 100.0% |
| b_12M-1M | 1.5 | 0.03 | 0.23 | 0.77 | 0.51 | 0.99 | 0.49 | 53% | 100.0% |
| c_3M | 2.8 | 0.06 | 0.23 | 0.95 | 0.66 | 1.27 | 0.63 | 53% | 100.0% |
| d_1M | 4.8 | 0.10 | 0.23 | 0.76 | 0.43 | 0.97 | 0.49 | 53% | 100.0% |
| e_6M_winsor_sigma | 3.1 | 0.06 | 0.23 | 0.65 | 0.36 | 0.86 | 0.43 | 50% | 99.7% |
| f_6M_beta_neutral | 2.1 | 0.04 | 0.23 | 0.38 | 0.11 | 0.24 | 0.12 | 50% | 94.5% |
| g_6M_max2semi | 2.1 | 0.04 | 0.23 | 0.75 | 0.47 | 1.02 | 0.51 | 51% | 100.0% |
| h_6M_industry_neutral | 2.1 | 0.04 | 0.23 | 0.77 | 0.50 | 1.13 | 0.57 | 54% | 100.0% |
| d_rev_1M_contrarian | 4.8 | 0.10 | 0.23 | -0.76 | -1.09 | -2.44 | -1.22 | 42% | 0.1% |
| a_rev_6M_contrarian | 2.0 | 0.04 | 0.23 | -1.11 | -1.38 | -2.61 | -1.30 | 44% | 0.0% |

## 3. Każdy wariant na wszystkich swoich oknach (brutto; różne okresy — nieporównywalne wprost)

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a_6M | 234 | 1.01 | 0.97 | 7.57 | 2.03 | 0.96 | 56% | 53% | 70.7 | -25.8 | 31.8 | od 2022-04-22
| b_12M-1M | 208 | 0.77 | 0.59 | 7.49 | 1.49 | 0.75 | 56% | 53% | 75.8 | -25.5 | 28.7 | od 2022-10-21
| c_3M | 247 | 0.76 | 0.70 | 7.62 | 1.56 | 0.72 | 55% | 52% | 78.4 | -30.5 | 39.6 | od 2022-01-21
| d_1M | 256 | 0.52 | 0.69 | 6.34 | 1.30 | 0.59 | 55% | 52% | 96.0 | -24.7 | 32.2 | od 2021-11-19
| e_6M_winsor_sigma | 234 | 0.61 | 0.34 | 5.90 | 1.58 | 0.74 | 53% | 52% | 49.1 | -24.5 | 32.0 | od 2022-04-22
| f_6M_beta_neutral | 209 | 0.39 | 0.29 | 6.46 | 0.86 | 0.43 | 52% | 53% | 73.5 | -24.8 | 23.6 | od 2022-10-14
| g_6M_max2semi | 234 | 0.68 | 0.63 | 6.71 | 1.55 | 0.73 | 53% | 52% | 62.0 | -20.4 | 31.6 | od 2022-04-22
| h_6M_industry_neutral | 234 | 0.73 | 0.91 | 6.39 | 1.75 | 0.83 | 58% | 52% | 60.2 | -18.3 | 32.6 | od 2022-04-22
| d_rev_1M_contrarian | 256 | -0.52 | -0.69 | 6.34 | -1.30 | -0.59 | 45% | 48% | 247.3 | -32.2 | 24.7 | od 2021-11-19
| a_rev_6M_contrarian | 234 | -1.01 | -0.97 | 7.57 | -2.03 | -0.96 | 44% | 47% | 318.6 | -31.8 | 25.8 | od 2022-04-22
| BASELINE (okna wariantu a) | 234 | -0.00 | — | 3.38 | t 5–95%: -1.65…1.66 | — | — | 50% | — | p5 -5.4 | p95 5.4 |

## 4. Rozbicie na lata i reżimy (brutto; lata wg D0; wariant na swoich wszystkich oknach)


### a_6M

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.51 | 1.33 | 6.63 | 0.47 | 0.56 | 62% | 58% | 31.8 | -14.6 | 12.5 |
| 2023 | 52 | -0.19 | -0.58 | 3.95 | -0.35 | -0.35 | 46% | 50% | 26.1 | -7.9 | 9.4 |
| 2024 | 52 | 1.40 | -0.04 | 7.38 | 1.37 | 1.37 | 50% | 51% | 34.4 | -12.8 | 31.8 |
| 2025 | 52 | 1.58 | 1.32 | 6.50 | 1.75 | 1.75 | 63% | 56% | 32.7 | -16.1 | 19.9 |
| 2026 | 41 | 1.74 | 3.46 | 12.16 | 0.92 | 1.03 | 61% | 54% | 70.7 | -25.8 | 23.2 |
| VIX>20 na D0 | 74 | 2.42 | 1.55 | 7.33 | 2.83 | 2.38 | 64% | 60% | 37.5 | -14.6 | 31.8 |
| VIX≤20 na D0 | 160 | 0.35 | 0.35 | 7.61 | 0.59 | 0.33 | 52% | 50% | 73.4 | -25.8 | 23.2 |
| NDX < MA200 | 39 | 1.91 | 1.35 | 6.05 | 1.97 | 2.28 | 64% | 61% | 18.0 | -9.9 | 21.0 |
| NDX > MA200 | 180 | 0.98 | 0.72 | 7.86 | 1.68 | 0.90 | 54% | 52% | 70.7 | -25.8 | 31.8 |

### b_12M-1M

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 11 | 1.06 | 0.55 | 5.04 | 0.70 | 1.52 | 64% | 58% | 6.7 | -6.7 | 11.2 |
| 2023 | 52 | -1.18 | -1.26 | 4.95 | -1.71 | -1.71 | 42% | 46% | 60.2 | -13.2 | 10.6 |
| 2024 | 52 | 1.58 | 1.08 | 6.83 | 1.67 | 1.67 | 58% | 55% | 51.9 | -12.8 | 28.7 |
| 2025 | 52 | 0.65 | 1.44 | 6.25 | 0.75 | 0.75 | 60% | 53% | 30.5 | -15.7 | 16.5 |
| 2026 | 41 | 2.31 | 4.09 | 11.63 | 1.27 | 1.43 | 63% | 58% | 57.4 | -25.5 | 20.9 |
| VIX>20 na D0 | 49 | 3.32 | 2.19 | 7.89 | 2.94 | 3.03 | 65% | 62% | 29.7 | -13.2 | 28.7 |
| VIX≤20 na D0 | 159 | -0.01 | 0.41 | 7.21 | -0.02 | -0.01 | 53% | 50% | 57.4 | -25.5 | 19.3 |
| NDX < MA200 | 28 | 1.15 | 1.89 | 6.90 | 0.88 | 1.21 | 64% | 57% | 38.9 | -13.2 | 20.9 |
| NDX > MA200 | 180 | 0.72 | 0.50 | 7.60 | 1.26 | 0.68 | 54% | 52% | 57.4 | -25.5 | 28.7 |

### c_3M

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 50 | 0.00 | 0.18 | 7.62 | 0.00 | 0.00 | 52% | 55% | 54.3 | -30.5 | 11.9 |
| 2023 | 52 | -0.62 | -0.51 | 4.68 | -0.95 | -0.95 | 40% | 47% | 32.0 | -13.9 | 9.1 |
| 2024 | 52 | 2.70 | 1.80 | 7.84 | 2.48 | 2.48 | 69% | 54% | 24.0 | -11.0 | 39.6 |
| 2025 | 52 | 0.54 | 0.16 | 7.60 | 0.52 | 0.52 | 54% | 50% | 66.1 | -18.4 | 23.7 |
| 2026 | 41 | 1.23 | 2.51 | 9.89 | 0.80 | 0.90 | 61% | 54% | 70.9 | -27.6 | 21.9 |
| VIX>20 na D0 | 86 | 1.50 | 0.68 | 9.06 | 1.54 | 1.20 | 57% | 55% | 58.6 | -30.5 | 39.6 |
| VIX≤20 na D0 | 161 | 0.36 | 0.70 | 6.73 | 0.68 | 0.38 | 54% | 50% | 70.9 | -27.6 | 20.9 |
| NDX < MA200 | 39 | -0.30 | 0.19 | 6.92 | -0.27 | -0.31 | 54% | 52% | 40.8 | -13.9 | 21.9 |
| NDX > MA200 | 180 | 1.12 | 0.86 | 7.52 | 1.99 | 1.07 | 56% | 52% | 70.9 | -27.6 | 39.6 |

### d_1M

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 7 | 0.37 | -1.10 | 3.67 | 0.27 | 0.73 | 43% | 54% | 5.3 | -4.1 | 5.0 |
| 2022 | 52 | -0.44 | 0.93 | 6.07 | -0.52 | -0.52 | 56% | 52% | 54.8 | -24.7 | 10.0 |
| 2023 | 52 | -0.98 | -0.48 | 3.13 | -2.25 | -2.25 | 44% | 47% | 43.0 | -11.0 | 4.9 |
| 2024 | 52 | 2.32 | 1.61 | 7.43 | 2.25 | 2.25 | 65% | 54% | 18.0 | -12.0 | 32.2 |
| 2025 | 52 | 1.06 | 1.45 | 5.94 | 1.28 | 1.28 | 62% | 55% | 28.9 | -13.8 | 16.7 |
| 2026 | 41 | 0.67 | 0.84 | 8.41 | 0.51 | 0.57 | 51% | 53% | 53.0 | -17.5 | 16.3 |
| VIX>20 na D0 | 89 | 0.16 | 0.73 | 6.60 | 0.23 | 0.18 | 53% | 52% | 74.4 | -24.7 | 32.2 |
| VIX≤20 na D0 | 167 | 0.70 | 0.67 | 6.22 | 1.46 | 0.82 | 57% | 53% | 53.0 | -17.5 | 22.6 |
| NDX < MA200 | 39 | -0.75 | 0.37 | 5.34 | -0.88 | -1.02 | 51% | 52% | 45.2 | -11.0 | 13.2 |
| NDX > MA200 | 180 | 0.98 | 0.72 | 6.52 | 2.01 | 1.08 | 57% | 53% | 53.0 | -17.5 | 32.2 |

### e_6M_winsor_sigma

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.50 | 2.29 | 5.31 | 0.58 | 0.69 | 57% | 58% | 35.0 | -11.4 | 8.1 |
| 2023 | 52 | 0.21 | -0.22 | 4.01 | 0.37 | 0.37 | 44% | 51% | 21.4 | -10.3 | 10.0 |
| 2024 | 52 | 0.17 | -0.72 | 6.01 | 0.21 | 0.21 | 44% | 46% | 49.1 | -10.6 | 32.0 |
| 2025 | 52 | 1.00 | 0.81 | 5.19 | 1.39 | 1.39 | 62% | 54% | 23.5 | -16.4 | 12.8 |
| 2026 | 41 | 1.26 | 2.89 | 8.69 | 0.93 | 1.05 | 59% | 53% | 36.7 | -24.5 | 18.0 |
| VIX>20 na D0 | 74 | 1.62 | 1.25 | 6.69 | 2.08 | 1.74 | 58% | 57% | 38.7 | -11.4 | 32.0 |
| VIX≤20 na D0 | 160 | 0.14 | -0.02 | 5.46 | 0.33 | 0.19 | 50% | 50% | 63.5 | -24.5 | 15.0 |
| NDX < MA200 | 39 | 1.08 | 1.02 | 4.74 | 1.43 | 1.65 | 59% | 58% | 16.3 | -7.4 | 14.6 |
| NDX > MA200 | 180 | 0.62 | 0.23 | 6.12 | 1.35 | 0.73 | 52% | 51% | 49.1 | -24.5 | 32.0 |

### f_6M_beta_neutral

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 12 | 1.82 | 1.90 | 5.09 | 1.24 | 2.57 | 75% | 59% | 10.6 | -7.5 | 11.1 |
| 2023 | 52 | -0.53 | -0.29 | 3.80 | -1.00 | -1.00 | 44% | 50% | 27.4 | -9.1 | 8.0 |
| 2024 | 52 | 0.38 | -0.51 | 5.37 | 0.51 | 0.51 | 42% | 50% | 47.1 | -10.1 | 18.5 |
| 2025 | 52 | 0.82 | 1.38 | 5.08 | 1.16 | 1.16 | 62% | 57% | 29.6 | -15.5 | 9.6 |
| 2026 | 41 | 0.59 | 1.39 | 10.93 | 0.35 | 0.39 | 54% | 54% | 73.5 | -24.8 | 23.6 |
| VIX>20 na D0 | 50 | 3.02 | 2.52 | 6.36 | 3.35 | 3.42 | 70% | 62% | 15.7 | -8.5 | 22.0 |
| VIX≤20 na D0 | 159 | -0.44 | -0.29 | 6.28 | -0.89 | -0.51 | 46% | 50% | 105.9 | -24.8 | 23.6 |
| NDX < MA200 | 29 | 2.10 | 1.72 | 5.87 | 1.93 | 2.58 | 66% | 58% | 15.6 | -7.5 | 22.0 |
| NDX > MA200 | 180 | 0.11 | -0.12 | 6.52 | 0.23 | 0.12 | 49% | 52% | 73.5 | -24.8 | 23.6 |

### g_6M_max2semi

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.49 | 1.33 | 6.71 | 0.45 | 0.53 | 62% | 58% | 31.8 | -14.6 | 12.5 |
| 2023 | 52 | -0.26 | -0.74 | 3.96 | -0.48 | -0.48 | 44% | 50% | 27.2 | -7.3 | 9.4 |
| 2024 | 52 | 1.54 | 0.29 | 7.36 | 1.51 | 1.51 | 52% | 51% | 32.0 | -11.1 | 31.6 |
| 2025 | 52 | 1.26 | 1.15 | 6.21 | 1.46 | 1.46 | 60% | 55% | 33.4 | -16.1 | 21.1 |
| 2026 | 41 | 0.22 | -0.25 | 8.97 | 0.15 | 0.17 | 49% | 48% | 62.0 | -20.4 | 14.9 |
| VIX>20 na D0 | 74 | 1.92 | 1.42 | 6.86 | 2.41 | 2.02 | 62% | 58% | 37.5 | -14.6 | 31.6 |
| VIX≤20 na D0 | 160 | 0.10 | -0.22 | 6.58 | 0.20 | 0.11 | 49% | 50% | 78.6 | -20.4 | 22.0 |
| NDX < MA200 | 39 | 1.53 | 1.35 | 5.46 | 1.75 | 2.02 | 67% | 59% | 18.0 | -9.9 | 12.8 |
| NDX > MA200 | 180 | 0.64 | -0.04 | 6.88 | 1.25 | 0.67 | 50% | 51% | 62.0 | -20.4 | 31.6 |

### h_6M_industry_neutral

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.67 | 1.62 | 6.67 | 0.61 | 0.72 | 65% | 58% | 33.0 | -15.8 | 12.3 |
| 2023 | 52 | -0.17 | -0.06 | 3.88 | -0.32 | -0.32 | 48% | 51% | 25.4 | -8.2 | 8.7 |
| 2024 | 52 | 1.64 | 1.17 | 7.65 | 1.55 | 1.55 | 62% | 52% | 26.9 | -11.6 | 32.6 |
| 2025 | 52 | 1.09 | 1.44 | 5.77 | 1.36 | 1.36 | 60% | 54% | 34.8 | -15.6 | 13.0 |
| 2026 | 41 | 0.32 | 1.03 | 7.69 | 0.27 | 0.30 | 56% | 49% | 60.2 | -18.3 | 14.0 |
| VIX>20 na D0 | 74 | 1.86 | 2.50 | 6.72 | 2.38 | 2.00 | 65% | 57% | 41.1 | -15.8 | 32.6 |
| VIX≤20 na D0 | 160 | 0.21 | 0.44 | 6.19 | 0.43 | 0.25 | 54% | 51% | 73.7 | -18.3 | 23.2 |
| NDX < MA200 | 39 | 1.48 | 2.72 | 5.48 | 1.68 | 1.94 | 67% | 57% | 18.9 | -12.2 | 12.3 |
| NDX > MA200 | 180 | 0.66 | 0.72 | 6.50 | 1.37 | 0.73 | 56% | 51% | 60.2 | -18.3 | 32.6 |

### BASELINE w reżimach (średnia losowego koszyka, σ pooled) — dla porównania z tabelami wyżej

| reżim | okna | średnia losowych pp | σ pooled | p5 | p95 |
|---|---|---|---|---|---|
| wszystkie (okna a) | 234 | -0.00 | 3.38 | -5.4 | 5.4 |
| 2022 | 37 | 0.01 | 3.24 | -5.3 | 5.3 |
| 2023 | 52 | 0.00 | 2.65 | -4.3 | 4.3 |
| 2024 | 52 | 0.00 | 3.25 | -5.1 | 5.1 |
| 2025 | 52 | -0.01 | 3.28 | -5.4 | 5.4 |
| 2026 | 41 | -0.01 | 4.44 | -7.0 | 7.0 |
| VIX>20 | 74 | 0.00 | 3.41 | -5.5 | 5.5 |
| VIX≤20 | 160 | -0.00 | 3.36 | -5.4 | 5.4 |
| NDX<MA200 | 39 | 0.01 | 3.30 | -5.3 | 5.4 |
| NDX>MA200 | 180 | -0.00 | 3.40 | -5.4 | 5.4 |

## 5. Wariant (f) — szczegóły konstrukcji beta-neutral

Średni nominał strony long = 0.70, short = 1.30 (gross 2). Średnia beta strony long = short = 0.90. Spread 'excess vs NDX' (harness literalnie, czyli z dodatkowym shortem NDX o nominał long−short): średnia 0.59 pp, t = 1.24; spread beta-neutral (bez NDX): średnia 0.38 pp, t = 0.84.

Dla porównania koszyk (a) równych wag: średnia beta 250d strony long = 1.60, short = 0.97 → koszyk (a) ma strukturalnie dodatnią betę netto ≈ 0.63 (long wysokiej bety, short niskiej).

Regresja spreadu (a) na tygodniowym zwrocie ^NDX: alfa = 0.88 pp/tydz., beta = 0.33, r = 0.13 (n=234). Czyli 2% wariancji spreadu (a) to kierunek rynku.


## 6. Strategia (a) a półprzewodniki (^SOX − ^NDX)

| podzbiór tygodni | okna | średni spread (a) pp | σ | t | hit | najgorsze | średni SOX−NDX pp |
|---|---|---|---|---|---|---|---|
| SOX−NDX < −3 pp (jak W6/W7) | 23 | -4.40 | 10.84 | -1.95 | 35% | -25.8 | -4.8 |
| |SOX−NDX| ≤ 3 pp | 177 | 0.84 | 6.66 | 1.68 | 54% | -16.1 | 0.1 |
| SOX−NDX > +3 pp | 34 | 5.51 | 6.96 | 4.62 | 82% | -7.9 | 4.6 |
| wszystkie | 234 | 1.01 | 7.57 | 2.03 | 56% | -25.8 | 0.3 |

To samo dla wariantów bez zakładu na półprzewodniki (g: max 2 semis/strona, h: ranking neutralny branżowo), wspólne okna:

| wariant | SOX−NDX < −3: n / średnia / hit | pozostałe: n / średnia | wszystkie wspólne: średnia / t / σ | beta na SOX−NDX | r |
|---|---|---|---|---|---|
| a_6M | 19 / -5.83 / 26% | 189 / 1.81 | 1.11 / 2.10 / 7.65 | 1.11 | 0.39 |
| g_6M_max2semi | 19 / -4.28 / 26% | 189 / 1.25 | 0.75 / 1.61 / 6.69 | 0.77 | 0.31 |
| h_6M_industry_neutral | 19 / -3.79 / 32% | 189 / 1.23 | 0.77 / 1.75 / 6.36 | 0.70 | 0.30 |
| e_6M_winsor_sigma | 19 / -2.48 / 47% | 189 / 0.96 | 0.65 / 1.57 / 5.93 | 0.64 | 0.29 |
| f_6M_beta_neutral | 19 / -3.54 / 37% | 189 / 0.77 | 0.38 / 0.84 / 6.47 | 0.72 | 0.30 |

Regresja tygodniowego spreadu (a) na (SOX−NDX): alfa = 0.72 pp, **beta = 0.95**, r = 0.34, R² = 0.11 (n=234). Co 1 pp przegranej SOX z NDX kosztuje koszyk ≈ 0.95 pp.


### Ekspozycja koszyka (a) na SOX−NDX w czasie (beta nóg z 126 sesji; long − short) i liczba półprzewodników

| okres | okna | śr. ekspozycja beta(SOX−NDX) | min | max | śr. liczba semis LONG | śr. semis SHORT | % tygodni z ≥3 semis w long | % tygodni ekspozycja>0,5 |
|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | -0.75 | -1.45 | -0.06 | 0.1 | 0.9 | 0% | 0% |
| 2023 | 52 | 0.38 | -0.37 | 1.07 | 1.0 | 0.7 | 2% | 42% |
| 2024 | 52 | 0.36 | -0.58 | 1.26 | 1.2 | 1.2 | 8% | 46% |
| 2025 | 52 | 0.42 | -0.55 | 1.45 | 1.9 | 1.7 | 31% | 38% |
| 2026 | 41 | 2.03 | 0.08 | 2.76 | 4.4 | 0.2 | 95% | 98% |
| wszystkie | 234 | 0.49 | -1.45 | 2.76 | 1.7 | 1.0 | 26% | 45% |

Ostatnie 26 okien (D0, ekspozycja beta SOX−NDX, semis long/short, spread a, SOX−NDX):

| D0 | ekspozycja | semis L/S | spread (a) pp | SOX−NDX pp | skład long (a) |
|---|---|---|---|---|---|
| 2026-04-17 | 2.68 | 5/0 | 7.3 | 7.7 | SNDK LITE WDC TER STX |
| 2026-04-24 | 2.60 | 5/0 | 4.8 | -0.7 | SNDK LITE WDC TER STX |
| 2026-05-01 | 2.67 | 5/0 | 14.5 | 5.6 | SNDK LITE WDC STX INTC |
| 2026-05-08 | 2.74 | 5/0 | 0.2 | -1.2 | SNDK LITE INTC MU WDC |
| 2026-05-15 | 2.76 | 5/0 | 4.6 | 4.1 | SNDK LITE MU WDC INTC |
| 2026-05-22 | 2.73 | 5/0 | 0.9 | 2.2 | SNDK LITE INTC MU WDC |
| 2026-05-29 | 2.52 | 4/0 | -7.9 | -0.2 | SNDK MU WDC RKLB STX |
| 2026-06-05 | 2.16 | 5/0 | 16.5 | 7.1 | SNDK MU WDC STX LITE |
| 2026-06-12 | 2.54 | 5/0 | 20.5 | 4.7 | SNDK MU STX WDC INTC |
| 2026-06-18 | 2.52 | 5/0 | -14.8 | -3.7 | SNDK MU WDC STX MRVL |
| 2026-06-26 | 2.29 | 5/0 | -22.1 | -5.1 | SNDK MU INTC WDC STX |
| 2026-07-02 | 2.20 | 5/0 | 3.5 | 1.0 | SNDK MU INTC WDC STX |
| 2026-07-10 | 2.23 | 5/0 | -18.6 | -5.8 | SNDK STX WDC MU ARM |
| 2026-07-17 | 2.06 | 5/0 | 6.6 | 2.9 | SNDK MU ARM STX MRVL |
| 2026-07-24 | 2.00 | 5/0 | -10.7 | -4.8 | SNDK STX MRVL MU ARM |
| 2026-07-31 | 1.69 | 3/0 | 1.7 | 4.1 | MRVL SNDK ARM DDOG NBIS |
| 2026-08-07 | 1.86 | 3/0 | 7.1 | -0.6 | MRVL ARM NBIS AMD PANW |
| 2026-08-14 | 2.03 | 4/0 | -14.5 | -3.0 | NBIS MRVL SNDK ALAB AMD |
| 2026-08-21 | 1.32 | 3/0 | -4.6 | -2.7 | MRVL MRNA SNDK PANW AMD |
| 2026-08-28 | 0.94 | 2/0 | -2.2 | 1.9 | MRVL MRNA PANW ALAB CRWD |
| 2026-09-04 | 1.94 | 3/0 | -2.0 | 1.4 | SNDK MRNA MU ALAB NBIS |
| 2026-09-11 | 1.93 | 4/0 | 7.8 | -0.1 | MRNA MRVL SNDK AMD ALAB |
| 2026-09-18 | 1.90 | 4/0 | 17.7 | 3.0 | MRNA MRVL AMD ALAB INTC |
| 2026-09-25 | 1.98 | 4/0 | 2.1 | 3.0 | MRNA ALAB AMD MU SNDK |
| 2026-10-02 | 1.48 | 3/0 | -4.0 | -4.5 | MRNA ALAB MU AMD CRWD |
| 2026-10-09 | 0.08 | 0/0 | -13.6 | -5.9 | MRNA CRWD DDOG PANW FTNT |

Spread (a) gdy ekspozycja SOX powyżej mediany (0.45): średnia 1.30 pp, σ 8.26, t 1.70 (n=117); poniżej mediany: średnia 0.71 pp, σ 6.83, t 1.13 (n=117).


Korelacja spreadu (a) z (SOX−NDX) wg lat: 2022: r=-0.26, 2023: r=0.06, 2024: r=0.17, 2025: r=0.18, 2026: r=0.77


## 7. Faktyczne koszyki W4–W8 a momentum 6M

Percentyl momentum 6M relatywnego (100 = najsilniejsza spółka) przy D0 koszyka; overlap = ile nazw pokrywa się z TOP5/BOTTOM5 (a).

| tydzień | D0 koszyka | okno harnessu | long (pct mom) | short (pct mom) | overlap L/S | semis w long | spread (a) w oknie | spread faktyczny w oknie | SOX−NDX pp | TOP5 (a) | BOTTOM5 (a) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-W4 | 2026-09-11 | 2026-09-11→2026-09-18 | MU(95) AMD(97) AVGO(46) MRVL(99) LITE(85) | INTU(2) SBUX(31) CMCSA(8) APP(1) ADSK(9) | 2/2 | 5 | 7.8 | 7.3 | -0.1 | ALAB AMD MRNA MRVL SNDK | ALNY APP INTU ISRG PDD |
| 2026-W5 | 2026-09-28 | 2026-09-28→(brak okna) | MU(97) AMD(98) ALAB(99) STX(91) TER(74) | SBUX(40) NFLX(2) PEP(10) CMCSA(3) APP(7) | 3/2 | 5 | — | — | — | ALAB AMD CRWD MRNA MU | CMCSA INTU NFLX PDD TMUS |
| 2026-W6 | 2026-10-02 | 2026-10-02→2026-10-09 | MU(98) LITE(72) TER(82) AMAT(85) AMD(97) | APP(4) NFLX(2) PAYX(41) CMCSA(6) SBUX(40) | 2/2 | 5 | -4.0 | -5.6 | -4.5 | ALAB AMD CRWD MRNA MU | ALNY APP INTU NFLX PDD |
| 2026-W7 | 2026-10-09 | 2026-10-09→2026-10-16 | MU(94) LITE(70) MRVL(92) PANW(97) CSCO(82) | CMCSA(5) SBUX(24) PEP(7) TMUS(6) APP(3) | 1/2 | 3 | -13.6 | -21.1 | -5.9 | CRWD DDOG FTNT MRNA PANW | ALNY APP CMCSA FER NFLX |
| 2026-W8 | 2026-10-16 | 2026-10-16→(brak okna) | GOOGL(44) GILD(69) MSFT(80) QCOM(81) ADP(90) | AXON(37) DASH(51) ALNY(7) APP(2) FER(4) | 0/2 | 1 | — | — | — | CRWD DDOG FTNT MRNA PANW | APP CRWV FER NFLX RKLB |

History (zapisane w signals): 2026-W1: -4.06 pp, 2026-W2: 6.19 pp, 2026-W3: 1.44 pp, 2026-W4: 13.85 pp, 2026-W5: 5.95 pp, 2026-W6: -5.89 pp, 2026-W7: -21.15 pp


## 7b. Stabilność: pierwsza vs druga połowa wspólnych okien (brutto)

| wariant | 1. połowa: n / średnia / t | 2. połowa: n / średnia / t |
|---|---|---|
| a_6M | 104 / 0.05 / 0.10 | 104 / 2.18 / 2.31 |
| b_12M-1M | 104 / -0.22 / -0.42 | 104 / 1.77 / 2.00 |
| c_3M | 104 / 0.29 / 0.58 | 104 / 1.60 / 1.76 |
| d_1M | 104 / 0.04 / 0.09 | 104 / 1.48 / 1.93 |
| e_6M_winsor_sigma | 104 / 0.01 / 0.04 | 104 / 1.28 / 1.79 |
| f_6M_beta_neutral | 104 / -0.25 / -0.60 | 104 / 1.01 / 1.28 |
| g_6M_max2semi | 104 / 0.08 / 0.16 | 104 / 1.42 / 1.78 |
| h_6M_industry_neutral | 104 / 0.16 / 0.33 | 104 / 1.38 / 1.88 |

## 8. Wnioski (automatyczne z liczb — interpretacja w odpowiedzi agenta)

- a_6M: brutto 1.11 pp/tydz. (t 2.10), netto 0.84 pp (t 1.59); t>2 brutto; średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- b_12M-1M: brutto 0.77 pp/tydz. (t 1.49), netto 0.51 pp (t 0.99); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- c_3M: brutto 0.95 pp/tydz. (t 1.81), netto 0.66 pp (t 1.27); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- d_1M: brutto 0.76 pp/tydz. (t 1.71), netto 0.43 pp (t 0.97); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- e_6M_winsor_sigma: brutto 0.65 pp/tydz. (t 1.57), netto 0.36 pp (t 0.86); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- f_6M_beta_neutral: brutto 0.38 pp/tydz. (t 0.84), netto 0.11 pp (t 0.24); σ > p95 losowych strategii (koncentracja ryzyka).
- g_6M_max2semi: brutto 0.75 pp/tydz. (t 1.61), netto 0.47 pp (t 1.02); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- h_6M_industry_neutral: brutto 0.77 pp/tydz. (t 1.75), netto 0.50 pp (t 1.13); średnia > p95 losowych; σ > p95 losowych strategii (koncentracja ryzyka).
- d_rev_1M_contrarian: brutto -0.76 pp/tydz. (t -1.71), netto -1.09 pp (t -2.44); σ > p95 losowych strategii (koncentracja ryzyka).
- a_rev_6M_contrarian: brutto -1.11 pp/tydz. (t -2.10), netto -1.38 pp (t -2.61); σ > p95 losowych strategii (koncentracja ryzyka).
- Najlepszy t netto wśród wariantów a–f: a_6M (t = 1.59).

## 9. Interpretacja (agent momentum)

1. **Nic nie przebija baseline'u z t > 2 po kosztach.** Jedyny wariant z t > 2 brutto to (a) 6M: 1,11 pp/tydz., t = 2,10 na 208 wspólnych oknach — ale 97,5. percentyl t-statu 2000 losowych strategii wynosi 1,97, a testowanych wariantów jest 8 (skorelowanych), więc to wynik na granicy szumu po poprawce na wielokrotne testowanie. Netto (0,04 pp rotacji + 0,23 pp finansowania) t spada do 1,59, Sharpe 0,79. Pozostałe warianty: t brutto 0,84–1,81, netto 0,24–1,27.
2. **Ryzyko koszyków momentum jest 2× większe niż losowych.** σ tygodniowa 5,9–7,7 pp wobec 3,4 pp dla losowego 5/5 (p95 losowych strategii = 3,85). W 2026 σ (a) = 12,2 pp wobec 4,4 pp losowych; najgorszy tydzień −25,8 pp, maxDD skumulowanego spreadu 71 pp. Hit rate 52–57 %, hit nóg 51–53 % — pojedyncza noga jest niemal rzutem monetą; wynik robi asymetria wielkości ruchów, nie trafność.
3. **Alfa jest niestabilna w czasie:** pierwsza połowa próby (X.2022–X.2024) daje t ≈ 0 dla wszystkich wariantów, cała alfa pochodzi z drugiej połowy (2024–2026, t 1,3–2,3). 2023 był ujemny dla każdego sygnału momentum (1M: −0,98 pp/tydz., t −2,25). Reżim VIX > 20 na D0 wygląda najlepiej (a: 2,42 pp, t 2,83; f: 3,02 pp, t 3,35; b: 3,32 pp, t 2,94), przy VIX ≤ 20 momentum nie zarabia (a: 0,35 pp, t 0,59; f: −0,44 pp) — ale to podział ex post (2 reżimy × 8 wariantów) i trzeba go traktować jako hipotezę, nie regułę.
4. **Momentum L/S w tym uniwersum to w ostatnich 12 miesiącach zakład na półprzewodniki.** Beta spreadu (a) na (SOX−NDX) = 0,95–1,11; r = 0,34 w całej próbie, ale 0,77 w 2026. Ekspozycja koszyka (a) na SOX−NDX (beta nóg long − short) rosła z −0,75 (2022, long defensywy) przez 0,4 (2023–2025) do **2,03 w 2026**, gdy TOP5 to średnio 4,4 półprzewodnika i 0,2 w BOTTOM5 (95 % tygodni ≥ 3 semis w long). W 23 tygodniach, gdy SOX przegrał z NDX o > 3 pp (jak W6/W7), (a) traci średnio **−4,4 pp** (wspólne okna: −5,8 pp, hit 26 %, najgorsze −25,8), a w 34 tygodniach SOX > NDX + 3 pp zarabia +5,5 pp (hit 82 %). Czyli wynik koszyka momentum to w praktyce ~1:1 zakład na względną siłę SOX.
5. **Usunięcie zakładu usuwa też większość alfy.** Limit 2 semis/strona (g) albo ranking neutralny branżowo (h) tnie betę na SOX−NDX do 0,7 i stratę w złych tygodniach do −3,8…−4,3 pp, ale średnia spada do 0,75–0,77 pp (t 1,6–1,75; netto 0,47–0,50, t 1,0–1,1). Różnica (a) − (g/h) ≈ 0,35 pp/tydz. to premia za trend półprzewodników 2025–26, nie ogólny efekt momentum. Winsoryzacja + filtr σ (e) obniża σ do 5,9 pp i maxDD do 49 pp, lecz średnia 0,65 pp (t 1,57). Beta-neutralizacja (f) prawie zeruje wynik (0,38 pp, t 0,84): koszyk (a) ma strukturalną betę netto ≈ +0,63 (long beta 1,60 vs short 0,97) i część jego zwrotu to po prostu ekspozycja na rynek i na beta-momentum.
6. **Faktyczne koszyki W4–W7 to momentum 6M w skrajnej wersji.** Nogi long miały percentyl momentum 70–99, short 2–10 (SBUX/PAYX wyjątki, 24–41); w W4–W6 **5/5 nóg long to półprzewodniki** (TOP5 (a) miał 3–4), overlap z czystym (a) 1–3 nazw/stronę. W tych samych oknach faktyczne koszyki wypadły gorzej niż (a): W6 −5,6 vs −4,0, W7 −21,1 vs −13,6 pp — bo zrobiono zakład na SOX jeszcze bardziej skoncentrowany niż daje mechaniczny ranking. W8 (GOOGL GILD MSFT QCOM ADP / AXON DASH ALNY APP FER) to odejście od momentum (overlap 0/2, long w percentylach 44–90) — brak wyników, więc nie wiadomo, czy to poprawa czy dryf metody.
7. **Koszty:** przy obrocie 1,5–4,8 nóg/tydz. rotacja kosztuje 0,03–0,10 pp, finansowanie 6 % na gross 2 to stałe 0,23 pp/tydz. (≈ 12 pp rocznie), czyli ~25 % brutto (a) i > 60 % brutto (f). Finansowanie jest głównym kosztem i argumentem przeciw utrzymywaniu gross 2 przy słabym sygnale.

Rekomendacja robocza dla procesu: traktować momentum 6M wyłącznie jako jeden z czynników, a nie uzasadnienie 5/5 półprzewodników; limit koncentracji branżowej (≤ 2 nogi z jednej branży na stronę) lub ranking neutralny branżowo obniża najgorsze tygodnie z −26 do −18/−20 pp przy utracie ~0,35 pp/tydz. oczekiwanej wartości, której istotność statystyczna i tak jest wątpliwa; rozważyć redukcję gross (albo wstrzymanie) przy VIX ≤ 20, gdzie żaden wariant nie wykazał dodatniej alfy; monitorować ekspozycję koszyka na SOX−NDX (kolumna `expo_sox_beta` w serii) jako jawne ryzyko, zamiast odkrywać ją po tygodniu −21 pp.

## 10. Zastrzeżenia

- Survivorship bias: uniwersum = dzisiejsze epics Nasdaq-100; spółki, które wypadły z indeksu (często po słabym momentum), nie są w short-bookach, a zwycięzcy 2025–26 (SNDK, ALAB, NBIS, MRNA, CRWV) są — zawyża to wynik strony long w ostatnich latach.
- Jedna próba ~4,5 lat (208–256 okien), jeden cykl rynkowy z dominacją AI/półprzewodników; wyniki per rok oparte na 37–52 oknach.
- Wielokrotne testowanie: 8 wariantów + rozbicia reżimowe; „najlepszy” t = 2,10 nie przeżywa poprawki.
- Egzekucja po cenie zamknięcia D0/D5, bez poślizgu i luk; koszt 0,10 % na nogę i 6 % finansowania na gross to założenia, nie taryfa brokera (finansowanie shortów u Capital.com bywa inne).
- Reżimy (VIX, MA200) i podział półprzewodników (branże TV + lista uzupełniająca AMAT/LRCX/TER/ASML/SNDK/WDC/STX/LITE/ALAB/ARM) zdefiniowane ex post.
- Wariant (f) używa innych nominałów stron (long 0,70 / short 1,30), więc jego spread nie jest wprost porównywalny z harnessem równych wag; wersja „excess” podana w §5.
