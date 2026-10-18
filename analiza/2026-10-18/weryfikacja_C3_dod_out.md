# weryfikacja_C3 — dodatek

## D1. Koszt stopu z korektą o artefakt na szumie (Δ_momentum − Δ_losowe; pp/tydz., brutto)

Δ_losowe = średnia po 100 losowych strategiach 5/5 (te same okna) różnicy wariant − v2; przy realizacji „na progu” proxy intraday jest dodatni (realizacja lepsza niż zamknięcie, gdy zamknięcie < próg).

| wariant | Δ momentum (t) | Δ losowe (5–95%) | Δ skorygowane | σ tyg. mom. | σ tyg. los. (v2: 4.17) | p5 mom. | p5 los. (v2: -6.50) | min mom. | CVaR5 mom. | CVaR5 los. (v2: -9.24) | maxDD mom. | maxDD los. śr. (v2: 52.5) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v3_stop10_close | -0.283 (-2.06) | -0.001 (-0.11…+0.11) | **-0.282** | 9.87 | 4.07 | -13.5 | -6.24 | -26.3 | -17.8 | -8.56 | 74.5 | 51.5 |
| v4_stop10_close_reopen | -0.185 (-1.70) | -0.006 (-0.08…+0.08) | **-0.179** | 9.98 | 4.12 | -12.8 | -6.42 | -26.3 | -19.0 | -8.91 | 72.2 | 52.1 |
| t1_intra05_thr | -0.132 (-0.71) | +0.161 (-0.01…+0.34) | **-0.294** | 9.13 | 3.83 | -11.6 | -5.61 | -21.1 | -15.8 | -7.24 | 73.0 | 42.1 |
| t1_intra05_thr_reopen | -0.014 (-0.08) | +0.191 (+0.06…+0.35) | **-0.205** | 9.54 | 3.90 | -13.2 | -5.75 | -25.3 | -18.8 | -7.64 | 77.3 | 41.5 |
| t1_intra05_close | -0.431 (-2.32) | -0.012 (-0.16…+0.13) | **-0.418** | 9.34 | 4.03 | -12.3 | -6.20 | -22.0 | -16.0 | -8.40 | 70.7 | 51.3 |
| t1_intra05_close_reopen | -0.224 (-1.54) | +0.019 (-0.09…+0.15) | **-0.242** | 9.68 | 4.10 | -13.4 | -6.33 | -28.1 | -18.1 | -8.78 | 66.4 | 50.7 |
| t3_stop10_anchor_d0 | -0.476 (-2.56) | -0.058 (-0.19…+0.09) | **-0.418** | 9.50 | 4.05 | -12.9 | -6.24 | -26.7 | -17.5 | -8.57 | 70.0 | 53.2 |
| t_stop15_close | -0.189 (-2.26) | +0.010 (-0.07…+0.09) | **-0.199** | 9.90 | 4.12 | -13.6 | -6.38 | -26.8 | -18.2 | -8.79 | 73.9 | 51.2 |
| t_stop15_intra05_thr | -0.103 (-0.85) | +0.105 (-0.01…+0.23) | **-0.208** | 9.80 | 3.95 | -13.3 | -6.00 | -26.5 | -18.3 | -7.91 | 76.0 | 45.7 |
| t_stop20_close | -0.118 (-2.13) | +0.009 (-0.05…+0.07) | **-0.127** | 9.91 | 4.14 | -13.0 | -6.45 | -24.2 | -18.2 | -8.91 | 70.0 | 51.4 |
| t_stop07_close | -0.371 (-1.88) | -0.024 (-0.15…+0.10) | **-0.347** | 9.30 | 4.03 | -12.2 | -6.21 | -22.0 | -15.7 | -8.36 | 70.8 | 52.2 |
| t_stop07_close_reopen | -0.135 (-0.87) | +0.010 (-0.09…+0.14) | **-0.145** | 9.69 | 4.11 | -13.5 | -6.34 | -29.5 | -18.2 | -8.83 | 65.9 | 51.3 |
| t_stop05_close | -0.565 (-2.12) | -0.019 (-0.19…+0.16) | **-0.546** | 8.88 | 3.98 | -11.5 | -6.07 | -18.8 | -14.1 | -8.10 | 66.5 | 51.0 |
| t_stop07_intra05_thr | -0.181 (-0.63) | +0.239 (+0.03…+0.48) | **-0.420** | 8.43 | 3.72 | -9.9 | -5.20 | -15.7 | -12.8 | -6.61 | 62.0 | 38.2 |
| t2_stop10_long_only | -0.231 (-2.34) | -0.030 (-0.09…+0.02) | **-0.201** | 9.93 | 4.17 | -14.1 | -6.57 | -27.0 | -18.7 | -9.29 | 75.3 | 54.1 |
| t2_stop10_short_only | -0.052 (-0.56) | +0.029 (-0.05…+0.13) | **-0.081** | 9.79 | 4.07 | -12.4 | -6.19 | -23.5 | -17.7 | -8.52 | 67.6 | 49.9 |
| t2_stop07_long_only | -0.272 (-1.92) | -0.042 (-0.13…+0.04) | **-0.230** | 9.51 | 4.16 | -12.3 | -6.56 | -23.9 | -17.0 | -9.22 | 71.0 | 54.6 |
| t2_stop07_short_only | -0.100 (-0.74) | +0.017 (-0.09…+0.12) | **-0.117** | 9.65 | 4.06 | -12.9 | -6.21 | -22.2 | -17.6 | -8.47 | 68.4 | 49.9 |

## D2. Kill switch 25% w oknach 12-tyg. — momentum vs losowe strategie (30 losowań)

| wariant | kill12 momentum | kill12 losowe śr. (5–95%) | 5. pct min kapitału mom. | 5. pct min kapitału los. śr. |
|---|---|---|---|---|
| v2_bez_stopu | 41.3% | 8.8% (1.1…19.1) | 73.4 | 77.6 |
| v3_stop10_close | 37.7% | 8.4% (2.4…16.5) | 74.0 | 77.7 |
| t1_intra05_thr | 30.0% | 3.8% (0.0…11.1) | 74.8 | 79.7 |
| t_stop07_close | 36.3% | 6.9% (0.0…15.7) | 73.7 | 77.9 |

## D3. Koszt stopu wg tercyli zmienności koszyka ex ante (śr. σ60 dzienna nóg na sesji wejścia; 10% w jednostkach σ5 = 0,10/(σ60·√5))

| tercyl | n | śr. σ60 nogi | 10% w σ5 | śr. v2 | Δ v3 (t) | Δ v4 (t) | Δ intra05_thr (t) | Δ stop07_close (t) | Δ stop15_close (t) | stopy v3 | p5 v2 | p5 v3 | p5 stop07 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 78 | 3.00% | 1.49σ | +1.20 | -0.193 (-1.2) | -0.051 (-0.5) | -0.092 (-0.4) | -0.365 (-1.4) | -0.143 (-1.3) | 63 | -6.8 | -8.2 | -8.1 |
| 2 | 78 | 3.91% | 1.14σ | +1.22 | -0.309 (-1.3) | -0.087 (-0.5) | -0.046 (-0.2) | -0.489 (-1.5) | -0.113 (-0.8) | 102 | -11.2 | -11.4 | -10.2 |
| 3 | 78 | 4.82% | 0.93σ | +1.50 | -0.348 (-1.2) | -0.417 (-1.6) | -0.259 (-0.6) | -0.260 (-0.6) | -0.312 (-1.8) | 120 | -18.8 | -16.7 | -15.0 |

Odniesienie koszyków faktycznych: W4: σ60 nóg 3.87% (long 4.97%, short 2.77%) = percentyl 47 rozkładu okien momentum; W7: σ60 nóg 3.25% (long 4.24%, short 2.26%) = percentyl 24 rozkładu okien momentum; W8: σ60 nóg 2.74% (long 2.08%, short 3.40%) = percentyl 9 rozkładu okien momentum.

## D4. Okna z największym |Δ| (v3 − v2) — co stop uciął

| okno D0 | Δ v3 | Δ v4 | v2 | stopy v3 | nogi ze stopem (kierunek, zwrot od stopu do wyjścia %) |
|---|---|---|---|---|---|
| 2025-04-04 | -12.17 | -15.29 | +5.42 | 4 | MSTR L d1 close -11.3% → +30.9%; AMD S d2 close +15.8% → +2.4%; MPWR S d2 close +15.0% → +4.1%; MCHP S d2 close +17.9% → +13.4% |
| 2026-07-24 | -11.15 | -4.83 | -5.27 | 4 | SNDK L d1 close -14.2% → +17.5%; MRVL L d2 close -13.6% → +18.6%; MU L d2 close -17.9% → +12.2%; ARM L d2 close -15.6% → +6.3% |
| 2024-03-01 | -7.79 | -3.21 | -2.71 | 2 | MSTR L d1 close -21.2% → +41.2%; MRNA S d5 close +16.6% → -0.0% |
| 2022-09-30 | -7.39 | -1.85 | +3.65 | 2 | MSTR S d1 close +10.8% → +11.3%; SHOP S d1 close +13.6% → +16.1% |
| 2025-11-14 | -6.62 | +0.52 | +0.77 | 3 | SNDK L d3 close -26.3% → +15.8%; WDC L d3 close -13.7% → +7.6%; MU L d3 close -16.8% → +11.2% |
| 2025-01-03 | -5.55 | -1.87 | -7.87 | 6 | RKLB L d4 close -17.0% → +0.0%; APP L d3 close -10.3% → -0.9%; PLTR L d2 close -10.1% → -4.8%; MSTR L d2 close -12.5% → -1.0%; ALAB L d4 close -11.5% → +0.0%; MRNA S d1 close +11.7% → +26.0% |
| 2022-05-06 | -5.46 | -4.19 | -2.81 | 3 | DASH S d4 close +14.8% → +10.7%; APP S d3 close +21.7% → -1.7%; SHOP S d4 close +18.4% → +10.6% |
| 2026-06-18 | -4.62 | -4.16 | -18.75 | 5 | SNDK L d1 close -13.6% → +4.4%; MU L d1 close -13.2% → +8.9%; WDC L d2 close -12.1% → +1.3%; STX L d4 close -17.7% → +7.6%; MRVL L d2 close -10.1% → +0.4% |
| 2024-07-26 | +5.26 | +2.32 | -6.16 | 4 | MSTR L d3 close -10.3% → -13.4%; ARM L d3 close -14.1% → -9.1%; APP L d4 close -10.6% → -2.3%; PLTR L d5 close -11.0% → +0.0% |
| 2024-04-19 | +5.39 | +2.03 | -3.14 | 1 | TSLA S d2 close +14.1% → -19.7% |
| 2026-04-10 | +5.55 | +2.88 | -15.49 | 3 | DASH S d2 close +12.7% → -5.5%; AXON S d2 close +11.8% → -0.4%; MSTR S d3 close +12.5% → -14.7% |
| 2026-02-20 | +6.40 | +5.42 | -20.17 | 4 | AXON S d2 close +22.8% → -10.0%; INTU S d4 close +13.8% → -2.5%; TRI S d1 close +11.4% → -10.4%; MSTR S d5 close +11.3% → -0.0% |

Suma Δ v3: -66.3 pp; udział 5 najgorszych okien: -45.1 pp; 10 najgorszych: -69.6 pp; suma dodatnich Δ: +88.5 pp (n=51), suma ujemnych: -154.8 pp (n=69); mediana Δ w oknach ze stopem: -0.43.

Wejście D0: d0_stop10_close − v1 = -0.232 pp/tydz. (t -1.57; boot 95% -0.528…+0.048); stopy 276.
Wejście D0: d0_stop10_close_reopen − v1 = -0.165 pp/tydz. (t -1.51; boot 95% -0.391…+0.037); stopy 286.
Wejście D0: d0_intra05_thr − v1 = -0.003 pp/tydz. (t -0.02; boot 95% -0.424…+0.404); stopy 411.

## D5. Rozkład Δ (v3 − v2) i (stop07 − v2)

- v3_stop10_close: Δ>+2 pp w 17 oknach (suma +65.2), Δ<−2 pp w 28 (suma -118.7); |Δ|≤2: 189 (suma -12.9); p99 Δ +5.3, p1 Δ -7.7
- v4_stop10_close_reopen: Δ>+2 pp w 13 oknach (suma +39.1), Δ<−2 pp w 18 (suma -70.1); |Δ|≤2: 203 (suma -12.3); p99 Δ +4.0, p1 Δ -4.6
- t_stop07_close: Δ>+2 pp w 25 oknach (suma +124.0), Δ<−2 pp w 44 (suma -214.4); |Δ|≤2: 165 (suma +3.6); p99 Δ +7.0, p1 Δ -10.1
- t1_intra05_close: Δ>+2 pp w 23 oknach (suma +109.6), Δ<−2 pp w 44 (suma -203.4); |Δ|≤2: 167 (suma -6.9); p99 Δ +7.5, p1 Δ -8.9
