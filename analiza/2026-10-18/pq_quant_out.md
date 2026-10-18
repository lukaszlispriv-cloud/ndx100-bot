Dane: 2021-10-18…2026-10-16, sesji 1255, spółek 102

## A. Baseline: losowe koszyki, σ tygodniowego spreadu (p.p., gross = 2)
| nogi na stronę | horyzont | okien | σ pooled | p5 | p95 | σ/σ(5,1w) |
|---|---|---|---|---|---|---|
| 5 | 1 tyg. | 260 | 3.42 | -5.5 | 5.5 | 1.00 |
| 10 | 1 tyg. | 260 | 2.43 | -3.9 | 3.9 | 0.71 |
| 15 | 1 tyg. | 260 | 1.98 | -3.2 | 3.2 | 0.58 |
| 5 | 2 tyg. | 130 | 4.90 | -7.8 | 7.9 | 1.43 |
| 10 | 2 tyg. | 130 | 3.47 | -5.5 | 5.6 | 1.02 |
| 15 | 2 tyg. | 130 | 2.82 | -4.5 | 4.5 | 0.82 |
| 5 | 4 tyg. | 65 | 7.25 | -11.4 | 11.3 | 2.12 |
| 10 | 4 tyg. | 65 | 5.16 | -8.3 | 8.3 | 1.51 |
| 15 | 4 tyg. | 65 | 4.21 | -6.8 | 6.8 | 1.23 |

σ pojedynczej nogi (zwrot rel. vs ^NDX, 1 tydz., pooled): 5.49 p.p.; teoretyczna σ spreadu 5/5 przy niezależności = σ_nogi·√(2/5) = 3.47 p.p.
σ dzienna (60 ses., %, przekrój na 2026-10-16): mediana 2.48, p90 4.71, max 23.54 (MRNA)

## B. Momentum 6M (126 sesji, bez ostatnich 5) — liczba nóg i horyzont
Koszty: round-trip 0,20% nominału nogi na każdą wymienioną nazwę (CFD spread ~0,1% × 2), finansowanie 6%/rok od gross 2 (= 0,115 pp/tydz./stronę → 0,23 pp/tydz.).
| wariant | okien | śr. pp/okno | σ/okno | t | Sharpe | hit | maxDD | najgorsze | obrót/okno | koszt pp/okno | netto pp/okno | t netto | Sharpe netto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom6M N=5 h=1w | 233 | 1.01 | 7.42 | 2.09 | 0.99 | 58% | -51 | -25.9 | 0.20 | 0.20 | 0.82 | 1.68 | 0.79 |
| mom6M N=5 h=2w | 116 | 1.90 | 11.26 | 1.81 | 0.86 | 62% | -52 | -36.9 | 0.28 | 0.34 | 1.55 | 1.49 | 0.70 |
| mom6M N=5 h=4w | 57 | 4.08 | 18.26 | 1.69 | 0.80 | 63% | -64 | -50.0 | 0.40 | 0.62 | 3.46 | 1.43 | 0.68 |
| mom6M N=5 h=2w nakł. | 231 | 1.14 | 7.30 | 2.37 | 1.12 | 57% | -51 | -24.7 | 0.10 | 0.15 | 0.98 | 2.05 | 0.97 |
| mom6M N=5 h=4w nakł. | 227 | 1.05 | 7.29 | 2.16 | 1.03 | 54% | -52 | -24.2 | 0.08 | 0.15 | 0.90 | 1.85 | 0.89 |
| mom6M N=10 h=1w | 233 | 0.55 | 6.00 | 1.41 | 0.66 | 57% | -49 | -20.9 | 0.18 | 0.19 | 0.36 | 0.93 | 0.44 |
| mom6M N=10 h=2w | 116 | 1.18 | 8.85 | 1.43 | 0.68 | 59% | -43 | -28.5 | 0.25 | 0.33 | 0.84 | 1.03 | 0.49 |
| mom6M N=10 h=4w | 57 | 2.58 | 13.92 | 1.40 | 0.67 | 56% | -47 | -33.1 | 0.35 | 0.60 | 1.98 | 1.08 | 0.51 |
| mom6M N=10 h=2w nakł. | 231 | 0.65 | 5.82 | 1.69 | 0.80 | 58% | -50 | -20.4 | 0.09 | 0.15 | 0.50 | 1.30 | 0.62 |
| mom6M N=10 h=4w nakł. | 227 | 0.62 | 5.79 | 1.62 | 0.77 | 58% | -53 | -20.1 | 0.07 | 0.15 | 0.48 | 1.24 | 0.59 |
| mom6M N=15 h=1w | 233 | 0.43 | 5.21 | 1.27 | 0.60 | 57% | -41 | -18.3 | 0.17 | 0.18 | 0.25 | 0.74 | 0.35 |
| mom6M N=15 h=2w | 116 | 0.87 | 7.29 | 1.28 | 0.61 | 54% | -33 | -22.3 | 0.23 | 0.32 | 0.54 | 0.80 | 0.38 |
| mom6M N=15 h=4w | 57 | 1.96 | 10.90 | 1.36 | 0.65 | 60% | -39 | -24.8 | 0.33 | 0.59 | 1.37 | 0.95 | 0.45 |
| mom6M N=15 h=2w nakł. | 231 | 0.50 | 4.98 | 1.51 | 0.72 | 57% | -41 | -16.9 | 0.08 | 0.15 | 0.35 | 1.06 | 0.50 |
| mom6M N=15 h=4w nakł. | 227 | 0.50 | 4.92 | 1.52 | 0.73 | 59% | -45 | -16.5 | 0.07 | 0.14 | 0.35 | 1.08 | 0.52 |

## C. Premia za zmienność (σ60) i zakład systemu (long high-σ semis / short low-σ staples)
- long low-σ / short high-σ (5/5): n=234, śr. -1.58 pp/tydz., σ 7.71, t -3.14, Sharpe -1.48, hit 44%; corr z r(^NDX) = -0.61, β na ^NDX = -1.59 (pp spreadu na 1 pp indeksu); netto -1.75 pp/tydz.
  lata: 2022: n=37 śr. 0.52 σ 8.02; 2023: n=52 śr. -1.70 σ 5.61; 2024: n=52 śr. -1.90 σ 7.23; 2025: n=52 śr. -2.23 σ 8.30; 2026: n=41 śr. -2.09 σ 9.40
- long low-β / short high-β (5/5): n=234, śr. -1.44 pp/tydz., σ 8.04, t -2.74, Sharpe -1.29, hit 43%; corr z r(^NDX) = -0.68, β na ^NDX = -1.85 (pp spreadu na 1 pp indeksu); netto -1.60 pp/tydz.
  lata: 2022: n=37 śr. 0.45 σ 7.84; 2023: n=52 śr. -2.52 σ 6.45; 2024: n=52 śr. -1.29 σ 7.84; 2025: n=52 śr. -1.36 σ 7.53; 2026: n=41 śr. -2.08 σ 10.58

## D. Dryf po dużym ruchu dziennym (proxy wyników): zwrot rel. w kolejnych 5 i 10 sesjach
| zdarzenie (ruch rel. dnia) | n | fwd 1 ses. śr. | fwd 5 ses. śr. | σ5 | t5 (klastr. po dacie) | hit5 (kontynuacja) | fwd 10 ses. śr. |
|---|---|---|---|---|---|---|---|
| ≥ +8% | 959 (554 dni) | 0.23 | 0.45 | 10.4 | 0.96 | 50% | 2.92 |
| +5…+8% | 1926 (797 dni) | 0.07 | 0.36 | 8.7 | 1.79 | 47% | 1.02 |
| ≤ −8% | 669 (423 dni) | 0.05 | 0.88 | 9.6 | 0.82 | 52% | 1.06 |
| −8…−5% | 1745 (756 dni) | 0.03 | 1.12 | 9.0 | 2.41 | 49% | 1.61 |
| ≥ +12% | 307 (244 dni) | 0.49 | 1.08 | 11.0 | 2.21 | 51% | 3.53 |
| ≤ −12% | 186 (149 dni) | 0.65 | 2.56 | 10.6 | 2.84 | 46% | 2.61 |
Po ≤ −8% (fwd5 rel.) wg lat: 2021: n=19 śr. -2.56; 2022: n=122 śr. 0.11; 2023: n=52 śr. -0.01; 2024: n=107 śr. 0.00; 2025: n=173 śr. 1.41; 2026: n=196 śr. 1.93
Po ≥ +8% (fwd5 rel.) wg lat: 2021: n=22 śr. 0.81; 2022: n=127 śr. -0.92; 2023: n=100 śr. 0.48; 2024: n=174 śr. 2.10; 2025: n=214 śr. 1.08; 2026: n=322 śr. -0.35
Po ≤ −8%: spółki z momentum 6M w górnych 30% → fwd5 śr. 2.79 (n=272); dolne 30% → -0.98 (n=174)
Po ≥ +8%: spółki z momentum 6M w górnych 30% → fwd5 śr. 1.32 (n=457); dolne 30% → -0.02 (n=234)

## E. Dzień tygodnia: dzienny spread koszyka momentum 6M (5/5, skład z ostatniego D0) wg dnia tygodnia
| dzień | n | śr. spread pp | σ | t | śr. r(^NDX) % |
|---|---|---|---|---|---|
| pon | 208 | 0.283 | 3.42 | 1.20 | 0.191 |
| wt | 232 | 0.274 | 3.86 | 1.08 | 0.022 |
| śr | 230 | 0.175 | 3.59 | 0.74 | 0.125 |
| czw | 224 | 0.247 | 3.84 | 0.96 | 0.027 |
| pt | 226 | 0.091 | 3.10 | 0.44 | 0.060 |
Autokorelacja dziennego spreadu momentum: lag1 -0.014, lag2 -0.024 (n=1120); wartość |ρ|<0,05 = brak podstaw dla bramki reagującej na dwie sesje w jednym kierunku.
Po dniu ze spreadem ≤ −3 pp (n=173): suma kolejnych 3 sesji śr. 1.43 pp (σ 7.05, t 2.67); po dniu ≥ +3 pp (n=188): 0.46 pp.

## F. Przekład Sharpe'a na tygodniowy spread i ryzyko kill switcha (symulacja)
| σ tyg. spreadu | Sharpe 0,5 → μ pp/tydz. | Sharpe 1,0 | Sharpe 1,5 | tygodni do t=2 przy S=1,0 |
|---|---|---|---|---|
| 3.4 | 0.24 | 0.47 | 0.71 | 208 |
| 5.0 | 0.35 | 0.69 | 1.04 | 208 |
| 7.0 | 0.49 | 0.97 | 1.46 | 208 |
| 10.0 | 0.69 | 1.39 | 2.08 | 208 |

P(kill switch −25% od szczytu) — zwroty t(4), tygodniowe; mnożnik kapitał/spread = gross/2 (ALLOC 0,24 → 1,2; 0,12 → 0,6):
| μ pp/tydz. | σ pp/tydz. | ALLOC | 26 tyg. | 52 tyg. |
|---|---|---|---|---|
| 0.00 | 7.0 | 0.24 | 71% | 93% |
| 0.00 | 7.0 | 0.12 | 25% | 53% |
| 0.00 | 7.0 | 0.08 | 6% | 23% |
| 0.75 | 7.0 | 0.24 | 56% | 83% |
| 0.75 | 7.0 | 0.12 | 12% | 31% |
| 0.75 | 7.0 | 0.08 | 3% | 9% |
| 0.75 | 5.0 | 0.24 | 27% | 51% |
| 0.75 | 5.0 | 0.12 | 2% | 8% |
| 0.75 | 5.0 | 0.08 | 0% | 1% |
| 1.00 | 7.0 | 0.24 | 50% | 78% |
| 1.00 | 7.0 | 0.12 | 10% | 25% |
| 1.00 | 7.0 | 0.08 | 2% | 7% |
| 0.00 | 3.4 | 0.24 | 22% | 51% |
| 0.00 | 3.4 | 0.12 | 1% | 8% |
| 0.00 | 3.4 | 0.08 | 0% | 1% |
| 0.50 | 3.4 | 0.24 | 9% | 23% |
| 0.50 | 3.4 | 0.12 | 0% | 1% |
| 0.50 | 3.4 | 0.08 | 0% | 0% |

Ułamek Kelly'ego (f* = μ/σ², w jednostkach nominału jednej strony/kapitał; 1,0 = ALLOC 0,20 przy 5 nogach):
- μ 0.5 pp, σ 3.4 pp → f* = 4.33 × strona (pełny Kelly = ALLOC 0.87; pół-Kelly = ALLOC 0.43)
- μ 0.75 pp, σ 7.0 pp → f* = 1.53 × strona (pełny Kelly = ALLOC 0.31; pół-Kelly = ALLOC 0.15)
- μ 1.0 pp, σ 7.0 pp → f* = 2.04 × strona (pełny Kelly = ALLOC 0.41; pół-Kelly = ALLOC 0.20)
- μ 1.0 pp, σ 5.0 pp → f* = 4.00 × strona (pełny Kelly = ALLOC 0.80; pół-Kelly = ALLOC 0.40)

## G. Faktyczne wyniki W1–W7 vs baseline
W1–W7: śr. -0.52, σ 11.29, t -0.12; σ faktyczna / σ losowego 5-5 (3,4) = 3.3×; W7 jako z wobec losowego koszyka: -6.2σ, wobec σ koszyków momentum 6M w 2026 (~12 pp wg bt_momentum): -1.7σ.
χ²(6) = 66 dla H0: σ = 3,4 pp → p ≈ 0 (wartość krytyczna 12,6): koszyki są istotnie bardziej ryzykowne niż losowe o równych wagach.
- μ=0.5 pp, σ=3.4 pp: n tygodni do t=2: 185
- μ=0.5 pp, σ=7.0 pp: n tygodni do t=2: 784
- μ=0.5 pp, σ=11.3 pp: n tygodni do t=2: 2043
- μ=1.0 pp, σ=3.4 pp: n tygodni do t=2: 46
- μ=1.0 pp, σ=7.0 pp: n tygodni do t=2: 196
- μ=1.0 pp, σ=11.3 pp: n tygodni do t=2: 511
- μ=2.0 pp, σ=3.4 pp: n tygodni do t=2: 12
- μ=2.0 pp, σ=7.0 pp: n tygodni do t=2: 49
- μ=2.0 pp, σ=11.3 pp: n tygodni do t=2: 128
