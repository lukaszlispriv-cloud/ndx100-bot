# Symulacja warstwy wykonawczej bota (bt_symulacja-wykonania)

Dane: closes_5y.csv (zamknięcia dzienne 2021-10-18…2026-10-16, 103 spółki = DZISIEJSZY skład Nasdaq-100 → survivorship bias). Stop i kill switch sprawdzane WYŁĄCZNIE na zamknięciach dziennych (bot sprawdza o 13:45 i 17:05 UTC na mid brokera — w rzeczywistości więcej zadziałań, ale bliżej progu). Wejście = zamknięcie sesji po D0 (bieg 13:45 UTC w poniedziałek działa po otwarciu NYSE; zamknięcie poniedziałku to przybliżenie), wyjście = zamknięcie sesji po D5 (następna rotacja). Sizing 24% kapitału na nogę (gross 240%), kapitał 100, kill switch 25% od kroczącego szczytu (szczyt ≥ 100 jak `max(szczyt, START_EQUITY)` w app.py). Koszty: 0,10% nominału na każde otwarcie nogi (rotacja z turnoverem i każdy reopen) + 6%/rok finansowania od gross za dni kalendarzowe okna. Bez look-ahead: sygnał z danych do D0.

## Warianty

- **v1_D0_bez_stopow** — wejście D0 (piątek), wyjście D5; = 1,2 × spread_pp harnessu
- **v2_Pon_bez_stopow** — wejście D0+1 (poniedziałek), wyjście D5+1 (następna rotacja)
- **v3_stop10_bez_reopen** — stop 10% od wejścia na zamknięciu, bez ponownego otwarcia
- **v4_stop10_reopen** — stop 10% + reopen następnej sesji (app.py bez exclude)
- **v5_stop15_bez_reopen** — stop 15% bez reopen
- **v5b_stop15_reopen** — stop 15% z reopen
- **v6_stop2.5sig_bez_reopen** — stop 2,5σ60 dziennej nogi od wejścia, bez reopen
- **v6b_stop2.5sig_reopen** — stop 2,5σ60 z reopen
- **v7_reduce50_2sig** — REDUCE 50% po 2σ60 przeciw tezie, bez stopu
- **v8_inv_sigma_1.5pct** — bez stopów, wagi ∝ 1/σ, cel σ dz. kapitału 1,5%, gross ≤ 300%
- **v9_inv_sigma_stop10_reopen** — (8) + stop 10% z reopen
- **v10_alloc12_bez_stopow** — jak (2), ale ALLOC_PCT=0,12 (gross 120%) — dodatkowy wariant sizingowy
- **v11_alloc16_bez_stopow** — jak (2), ale ALLOC_PCT=0,16 (gross 160%)
- **v12_alloc12_stop10_reopen** — ALLOC_PCT=0,12 + obecny stop 10% z reopen

## (B) Momentum 6M tygodniowe, 234 okien (2022-04-22 → 2026-10-16)

Harness (spread_pp, wejście D0, bez kosztów): średnia 1.01 pp, σ 7.57, t 2.03, Sharpe 0.96, hit 56%, hit nóg 53%, maxDD skumulowanego spreadu 70.7 pp, najgorsze -25.8, najlepsze 31.8. (W jednostkach kapitału ×1,2 → wariant v1.)

**BASELINE** 2000 losowych koszyków 5/5 na okno: σ pojedynczego okna 3.44 pp spreadu (= 4.13 pp kapitału), 5–95% spreadu -5.47…5.49 pp; losowa STRATEGIA (losowy koszyk w każdym oknie): średnia 5–95% -0.36…0.37 pp/tydz., t-stat 5–95% -1.62…1.58 (97,5%: 1.90), σ strategii 5–95% 3.06…3.86 pp.

### B1. Warianty wykonania — BRUTTO (% kapitału na okno; bez kill switcha, żeby porównać same reguły)

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | maxDD kap. % | najgorsze | najlepsze | kapitał końc. % | stopy | reopen | REDUCE | śr. gross | σ dz. kapitału % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v1_D0_bez_stopow | 234 | 1.21 | 1.16 | 9.08 | 2.03 | 0.96 | 56% | 62.3 | -30.9 | 38.2 | 544.6 | 0 | 0 | 0 | 2.40 | 4.34 |
| v2_Pon_bez_stopow | 234 | 1.31 | 0.80 | 9.86 | 2.03 | 0.95 | 54% | 68.6 | -24.2 | 54.5 | 615.6 | 0 | 0 | 0 | 2.40 | 4.31 |
| v3_stop10_bez_reopen | 234 | 1.02 | 0.22 | 9.87 | 1.58 | 0.75 | 51% | 74.5 | -26.3 | 54.5 | 270.8 | 285 | 0 | 0 | 2.40 | 4.02 |
| v4_stop10_reopen | 234 | 1.12 | 0.57 | 9.98 | 1.72 | 0.81 | 53% | 72.2 | -26.3 | 55.6 | 351.5 | 293 | 145 | 0 | 2.40 | 4.19 |
| v5_stop15_bez_reopen | 234 | 1.12 | 0.66 | 9.90 | 1.72 | 0.81 | 53% | 73.9 | -26.8 | 53.3 | 355.6 | 117 | 0 | 0 | 2.40 | 4.15 |
| v5b_stop15_reopen | 234 | 1.19 | 0.73 | 9.94 | 1.83 | 0.86 | 54% | 74.8 | -26.8 | 54.3 | 430.3 | 118 | 51 | 0 | 2.40 | 4.21 |
| v6_stop2.5sig_bez_reopen | 234 | 1.01 | 0.38 | 9.99 | 1.54 | 0.73 | 53% | 74.3 | -26.1 | 54.5 | 248.3 | 341 | 0 | 0 | 2.40 | 4.10 |
| v6b_stop2.5sig_reopen | 234 | 1.12 | 0.72 | 10.02 | 1.72 | 0.81 | 53% | 75.9 | -28.6 | 55.6 | 351.6 | 349 | 160 | 0 | 2.40 | 4.19 |
| v7_reduce50_2sig | 234 | 1.18 | 0.45 | 9.83 | 1.83 | 0.86 | 52% | 71.6 | -24.7 | 54.5 | 436.4 | 0 | 0 | 486 | 2.40 | 4.12 |
| v8_inv_sigma_1.5pct | 234 | 0.43 | 0.21 | 3.98 | 1.64 | 0.77 | 53% | 38.9 | -10.2 | 33.3 | 127.9 | 0 | 0 | 0 | 1.35 | 1.68 |
| v9_inv_sigma_stop10_reopen | 234 | 0.37 | 0.19 | 4.03 | 1.40 | 0.66 | 53% | 37.3 | -9.1 | 34.0 | 98.7 | 293 | 145 | 0 | 1.35 | 1.66 |
| v10_alloc12_bez_stopow | 234 | 0.65 | 0.40 | 4.93 | 2.03 | 0.95 | 54% | 42.1 | -12.1 | 27.3 | 248.7 | 0 | 0 | 0 | 1.20 | 2.15 |
| v11_alloc16_bez_stopow | 234 | 0.87 | 0.53 | 6.57 | 2.03 | 0.95 | 54% | 52.4 | -16.1 | 36.3 | 369.5 | 0 | 0 | 0 | 1.60 | 2.87 |
| v12_alloc12_stop10_reopen | 234 | 0.56 | 0.29 | 4.99 | 1.72 | 0.81 | 53% | 45.2 | -13.2 | 27.8 | 179.1 | 293 | 145 | 0 | 1.20 | 2.10 |

### B2. Warianty wykonania — NETTO (po 0,10%/nogę/otwarcie + 6%/rok od gross)

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | maxDD kap. % | najgorsze | najlepsze | kapitał końc. % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v1_D0_bez_stopow | 234 | 0.88 | 0.84 | 9.09 | 1.48 | 0.70 | 54% | 64.0 | -31.2 | 37.9 | 201.9 |
| v2_Pon_bez_stopow | 234 | 0.98 | 0.49 | 9.86 | 1.52 | 0.72 | 52% | 70.1 | -24.5 | 54.2 | 235.7 |
| v3_stop10_bez_reopen | 234 | 0.70 | -0.12 | 9.87 | 1.08 | 0.51 | 50% | 75.7 | -26.6 | 54.2 | 73.6 |
| v4_stop10_reopen | 234 | 0.78 | 0.26 | 9.99 | 1.20 | 0.56 | 50% | 73.7 | -26.7 | 55.3 | 103.7 |
| v5_stop15_bez_reopen | 234 | 0.79 | 0.31 | 9.90 | 1.22 | 0.58 | 51% | 75.1 | -27.1 | 53.0 | 113.4 |
| v5b_stop15_reopen | 234 | 0.86 | 0.36 | 9.94 | 1.32 | 0.62 | 52% | 76.1 | -27.1 | 54.0 | 145.3 |
| v6_stop2.5sig_bez_reopen | 234 | 0.68 | 0.05 | 9.99 | 1.05 | 0.49 | 50% | 75.5 | -26.4 | 54.2 | 63.0 |
| v6b_stop2.5sig_reopen | 234 | 0.78 | 0.34 | 10.03 | 1.19 | 0.56 | 51% | 77.1 | -28.9 | 55.3 | 103.1 |
| v7_reduce50_2sig | 234 | 0.85 | 0.14 | 9.83 | 1.33 | 0.63 | 51% | 72.9 | -25.0 | 54.2 | 151.4 |
| v8_inv_sigma_1.5pct | 234 | 0.24 | 0.03 | 3.98 | 0.92 | 0.43 | 51% | 44.7 | -10.5 | 33.1 | 47.2 |
| v9_inv_sigma_stop10_reopen | 234 | 0.18 | 0.01 | 4.03 | 0.67 | 0.32 | 50% | 43.8 | -9.4 | 33.8 | 26.6 |
| v10_alloc12_bez_stopow | 234 | 0.49 | 0.24 | 4.93 | 1.52 | 0.72 | 52% | 43.4 | -12.3 | 27.1 | 138.9 |
| v11_alloc16_bez_stopow | 234 | 0.65 | 0.32 | 6.57 | 1.52 | 0.72 | 52% | 53.8 | -16.3 | 36.2 | 183.6 |
| v12_alloc12_stop10_reopen | 234 | 0.39 | 0.13 | 5.00 | 1.20 | 0.56 | 50% | 46.6 | -13.3 | 27.7 | 87.8 |

### B3. Kill switch 25% od kroczącego szczytu

| wariant | kapitał końc. bez kill (brutto) | kapitał końc. z kill (brutto) | kill na pełnej ścieżce | okna 12-tyg. z killem | 5. pct min. kapitału w oknie 12-tyg. | mediana min. |
|---|---|---|---|---|---|---|
| v1_D0_bez_stopow | 644.6 | 85.2 | TAK — 2022-07-18 | 83/223 = 37.2% | 73.4 | 89.9 |
| v2_Pon_bez_stopow | 715.6 | 87.2 | TAK — 2022-07-19 | 92/223 = 41.3% | 73.4 | 90.6 |
| v3_stop10_bez_reopen | 370.8 | 86.9 | TAK — 2022-06-23 | 84/223 = 37.7% | 74.0 | 91.0 |
| v4_stop10_reopen | 451.5 | 89.5 | TAK — 2022-06-22 | 90/223 = 40.4% | 73.5 | 91.0 |
| v5_stop15_bez_reopen | 455.6 | 86.1 | TAK — 2022-06-24 | 88/223 = 39.5% | 74.0 | 90.6 |
| v5b_stop15_reopen | 530.3 | 87.3 | TAK — 2022-06-24 | 89/223 = 39.9% | 74.1 | 90.6 |
| v6_stop2.5sig_bez_reopen | 348.3 | 89.2 | TAK — 2022-06-24 | 88/223 = 39.5% | 74.0 | 89.9 |
| v6b_stop2.5sig_reopen | 451.6 | 88.3 | TAK — 2022-07-19 | 89/223 = 39.9% | 73.2 | 90.2 |
| v7_reduce50_2sig | 536.4 | 89.9 | TAK — 2022-06-24 | 87/223 = 39.0% | 73.8 | 90.3 |
| v8_inv_sigma_1.5pct | 227.9 | 92.1 | TAK — 2024-02-21 | 1/223 = 0.4% | 81.6 | 94.0 |
| v9_inv_sigma_stop10_reopen | 198.7 | 87.3 | TAK — 2024-02-21 | 1/223 = 0.4% | 82.4 | 94.1 |
| v10_alloc12_bez_stopow | 348.7 | 92.2 | TAK — 2024-09-03 | 13/223 = 5.8% | 81.4 | 94.6 |
| v11_alloc16_bez_stopow | 469.5 | 83.1 | TAK — 2022-07-21 | 43/223 = 19.3% | 77.0 | 93.4 |
| v12_alloc12_stop10_reopen | 279.1 | 85.2 | TAK — 2024-08-07 | 14/223 = 6.3% | 81.0 | 94.8 |

### B4. Dekompozycja: co kosztuje ile (różnice średnich brutto, pp kapitału/tydzień; t różnicy = sparowany)

| element | Δ średnia pp/tydz | Δ łącznie pp (suma) | t (sparowany) | Δ σ tyg. | Δ Sharpe | Δ kapitał końc. (bez kill) | Δ maxDD |
|---|---|---|---|---|---|---|---|
| opóźnienie wejścia pt→pon (v2 − v1) | +0.099 | +23.1 | +0.24 | +0.78 | -0.00 | +71.0 | +6.4 |
| stop 10% bez reopen (v3 − v2) | -0.283 | -66.3 | -2.06 | +0.01 | -0.21 | -344.7 | +5.8 |
| reopen po stopie (v4 − v3) | +0.098 | +23.0 | +1.10 | +0.11 | +0.06 | +80.6 | -2.2 |
| stop 10% + reopen = app.py (v4 − v2) | -0.185 | -43.3 | -1.70 | +0.12 | -0.15 | -264.1 | +3.6 |
| stop 15% bez reopen (v5 − v2) | -0.189 | -44.3 | -2.26 | +0.04 | -0.14 | -260.0 | +5.3 |
| stop 2,5σ bez reopen (v6 − v2) | -0.298 | -69.7 | -2.71 | +0.13 | -0.23 | -367.2 | +5.6 |
| REDUCE 50% po 2σ (v7 − v2) | -0.128 | -30.1 | -1.81 | -0.03 | -0.09 | -179.2 | +2.9 |
| sizing 1/σ cel 1,5% (v8 − v2) | -0.878 | -205.5 | -2.00 | -5.88 | -0.18 | -487.6 | -29.7 |
| (8) + stop10 reopen (v9 − v8) | -0.057 | -13.4 | -1.32 | +0.05 | -0.11 | -29.2 | -1.6 |
| ALLOC 0,12 zamiast 0,24 (v10 − v2) | -0.653 | -152.7 | -2.03 | -4.93 | +0.00 | -366.8 | -26.6 |
| ALLOC 0,16 zamiast 0,24 (v11 − v2) | -0.435 | -101.8 | -2.03 | -3.29 | +0.00 | -246.1 | -16.2 |

Okna z ≥1 stopem 10% (v3): 145/234 (62%). W tych oknach stop bez reopen vs brak stopu: śr -0.46 pp (udział okien, gdzie stop pomógł: 42%); reopen vs bez reopen: śr +0.16 pp (udział okien, gdzie reopen pomógł: 46%).

### B5. Baseline przez warstwę wykonania (200 losowych strategii 5/5, bez kill, brutto) — koszt reguł na SZUMIE

| wariant | śr. pp/tydz (5–95%) | σ tyg. śr. | kapitał końc. śr. (brutto) | kapitał końc. śr. (netto) | stopy śr. | maxDD śr. |
|---|---|---|---|---|---|---|
| v2_Pon_bez_stopow | +0.004 (-0.45…+0.43) | 4.20 | 101.5 | 31.2 | 0 | 53.8 |
| v3_stop10_bez_reopen | +0.007 (-0.42…+0.42) | 4.08 | 103.3 | 31.7 | 126 | 52.4 |
| v4_stop10_reopen | -0.001 (-0.43…+0.42) | 4.15 | 100.3 | 30.4 | 130 | 53.5 |
| v8_inv_sigma_1.5pct | -0.000 (-0.43…+0.40) | 3.53 | 100.5 | 26.9 | 0 | 48.2 |

Na losowych koszykach stop 10% + reopen zmienia średnią o -0.005 pp/tydz. (5–95% -0.08…+0.07; udział strategii, gdzie szkodzi: 55%), stop bez reopen o +0.003 pp/tydz. — to koszt wykonania NIEZALEŻNY od sygnału.

### B6. Rozbicie na lata i reżimy (brutto, pp kapitału/tydz., t w nawiasie; lata i reżim wg D0)

| wariant | 2022 (n=37) | 2023 (n=52) | 2024 (n=52) | 2025 (n=52) | 2026 (n=41) | VIX>20 (n=74) | VIX≤20 (n=160) | NDX<MA200 (n=39) | NDX>MA200 (n=180) |
|---|---|---|---|---|---|---|---|---|---|
| v1_D0_bez_stopow | 0.61 (t 0.5) | -0.23 (t -0.3) | 1.68 (t 1.4) | 1.90 (t 1.8) | 2.09 (t 0.9) | 2.90 (t 2.8) | 0.42 (t 0.6) | 2.29 (t 2.0) | 1.18 (t 1.7) |
| v2_Pon_bez_stopow | 0.73 (t 0.6) | -0.16 (t -0.2) | 1.70 (t 1.3) | 2.15 (t 1.7) | 2.11 (t 0.8) | 3.38 (t 2.9) | 0.35 (t 0.5) | 2.87 (t 2.3) | 1.15 (t 1.5) |
| v3_stop10_bez_reopen | 0.15 (t 0.1) | -0.27 (t -0.4) | 1.54 (t 1.1) | 1.78 (t 1.5) | 1.82 (t 0.7) | 2.94 (t 2.5) | 0.14 (t 0.2) | 2.52 (t 2.0) | 0.95 (t 1.2) |
| v4_stop10_reopen | 0.42 (t 0.3) | -0.25 (t -0.4) | 1.72 (t 1.3) | 1.90 (t 1.5) | 1.73 (t 0.7) | 3.01 (t 2.6) | 0.24 (t 0.3) | 2.52 (t 2.0) | 1.05 (t 1.3) |
| v6_stop2.5sig_bez_reopen | 0.28 (t 0.2) | -0.44 (t -0.6) | 1.53 (t 1.1) | 1.74 (t 1.4) | 1.90 (t 0.8) | 3.15 (t 2.7) | 0.02 (t 0.0) | 2.44 (t 1.9) | 0.87 (t 1.1) |
| v8_inv_sigma_1.5pct | 0.24 (t 0.6) | -0.11 (t -0.2) | 0.65 (t 0.9) | 0.85 (t 1.9) | 0.46 (t 0.7) | 1.32 (t 2.5) | 0.01 (t 0.0) | 0.94 (t 2.2) | 0.39 (t 1.2) |
| v10_alloc12_bez_stopow | 0.36 (t 0.6) | -0.08 (t -0.2) | 0.85 (t 1.3) | 1.08 (t 1.7) | 1.06 (t 0.8) | 1.69 (t 2.9) | 0.17 (t 0.5) | 1.43 (t 2.3) | 0.58 (t 1.5) |

## (A) Faktyczne koszyki 2026-W4…W7 (koszyki_historia.json)

Okna: D0 → D0 następnego koszyka (W4 11 sesji od 2026-09-14, W5 4, W6 5, W7 4 — W7 kończy się 2026-10-16, ostatnia sesja danych; wariant „poniedziałek" wychodzi też 2026-10-16). Bez wpisów exclude/tactical z pulsu (czysta warstwa wykonawcza).

| tydzień | D0 | wyjście | LONG | SHORT | spread_pp (D0→D0+5, vs ^NDX) | hit nóg | history.spread_pp | history.spread_fills_pp |
|---|---|---|---|---|---|---|---|---|
| 2026-W4 | 2026-09-11 | 2026-09-28 | MU AMD AVGO MRVL LITE | INTU SBUX CMCSA APP ADSK | +13.81 | 8/10 | 13.85 | 3.24 |
| 2026-W5 | 2026-09-28 | 2026-10-02 | MU AMD ALAB STX TER | SBUX NFLX PEP CMCSA APP | +5.95 | 8/10 | 5.95 | 7.76 |
| 2026-W6 | 2026-10-02 | 2026-10-09 | MU LITE TER AMAT AMD | APP NFLX PAYX CMCSA SBUX | -5.59 | 3/10 | -5.89 | 3.88 |
| 2026-W7 | 2026-10-09 | 2026-10-16 | MU LITE MRVL PANW CSCO | CMCSA SBUX PEP TMUS APP | -21.15 | 0/10 | -21.15 | -12.36 |

### A1. Zwrot kapitału na okno (brutto, % kapitału na starcie okna; w nawiasie liczba stopów/reopen) i kapitał końcowy

| wariant | 2026-W4 | 2026-W5 | 2026-W6 | 2026-W7 | suma pp | kapitał końc. brutto | kapitał końc. netto | kill | koszty łącznie pp |
|---|---|---|---|---|---|---|---|---|---|
| v1_D0_bez_stopow | +16.58 | +7.14 | -6.71 | -19.77 | -2.76 | 93.48 | 91.71 | TAK 2026-10-15 | 1.93 |
| v2_Pon_bez_stopow | +32.62 | +6.68 | -10.28 | -19.98 | +9.04 | 101.58 | 99.86 | TAK 2026-10-16 | 1.81 |
| v3_stop10_bez_reopen | +32.62 | +6.68 | -9.48 (1s/0r) | -18.88 (4s/0r) | +10.94 | 103.89 | 102.14 | TAK 2026-10-16 | 1.81 |
| v4_stop10_reopen | +32.62 | +6.68 | -10.60 (1s/1r) | -18.88 (4s/0r) | +9.82 | 102.60 | 100.85 | TAK 2026-10-16 | 1.84 |
| v5_stop15_bez_reopen | +32.62 | +6.68 | -10.28 | -19.98 (2s/0r) | +9.04 | 101.58 | 99.86 | TAK 2026-10-16 | 1.81 |
| v5b_stop15_reopen | +32.62 | +6.68 | -10.28 | -19.98 (2s/0r) | +9.04 | 101.58 | 99.86 | TAK 2026-10-16 | 1.81 |
| v6_stop2.5sig_bez_reopen | +32.62 | +6.68 | -10.62 (2s/0r) | -19.81 (7s/0r) | +8.87 | 101.40 | 99.69 | TAK 2026-10-16 | 1.81 |
| v6b_stop2.5sig_reopen | +32.62 | +6.68 | -10.73 (2s/1r) | -19.81 (7s/0r) | +8.76 | 101.28 | 99.54 | TAK 2026-10-16 | 1.84 |
| v7_reduce50_2sig | +32.62 | +6.68 | -10.03 (0s/0r/4R) | -18.17 (0s/0r/8R) | +11.10 | 104.16 | 102.41 | TAK 2026-10-16 | 1.81 |
| v8_inv_sigma_1.5pct | +8.66 | +2.17 | -2.14 | -7.64 | +1.05 | 100.34 | 99.70 | nie | 0.64 |
| v9_inv_sigma_stop10_reopen | +8.66 | +2.17 | -2.21 (1s/1r) | -7.43 (4s/0r) | +1.19 | 100.50 | 99.86 | nie | 0.65 |
| v10_alloc12_bez_stopow | +16.31 | +3.34 | -5.14 | -9.99 | +4.52 | 102.63 | 101.74 | nie | 0.91 |
| v11_alloc16_bez_stopow | +21.75 | +4.45 | -6.86 | -13.32 | +6.03 | 102.68 | 101.51 | nie | 1.21 |
| v12_alloc12_stop10_reopen | +16.31 | +3.34 | -5.30 (1s/1r) | -9.44 (4s/0r) | +4.91 | 103.08 | 102.17 | nie | 0.92 |

### A2. Dekompozycja na koszykach faktycznych (Δ kapitału końcowego brutto wobec v2)

- v1_D0_bez_stopow: -8.09 pkt kapitału (v2 = 101.58)
- v3_stop10_bez_reopen: +2.31 pkt kapitału (v2 = 101.58)
- v4_stop10_reopen: +1.02 pkt kapitału (v2 = 101.58)
- v5_stop15_bez_reopen: +0.00 pkt kapitału (v2 = 101.58)
- v5b_stop15_reopen: +0.00 pkt kapitału (v2 = 101.58)
- v6_stop2.5sig_bez_reopen: -0.18 pkt kapitału (v2 = 101.58)
- v6b_stop2.5sig_reopen: -0.30 pkt kapitału (v2 = 101.58)
- v7_reduce50_2sig: +2.58 pkt kapitału (v2 = 101.58)
- v8_inv_sigma_1.5pct: -1.24 pkt kapitału (v2 = 101.58)
- v9_inv_sigma_stop10_reopen: -1.08 pkt kapitału (v2 = 101.58)
- v10_alloc12_bez_stopow: +1.05 pkt kapitału (v2 = 101.58)
- v11_alloc16_bez_stopow: +1.10 pkt kapitału (v2 = 101.58)
- v12_alloc12_stop10_reopen: +1.50 pkt kapitału (v2 = 101.58)

### A3. Ścieżka dzienna kapitału w W7 (wejście 2026-10-12) — v2 / v3 / v4 / v6

| sesja | v2 bez stopu | v3 stop10 | v4 stop10+reopen | v6 2,5σ |
|---|---|---|---|---|
| 2026-10-13 | -1.94% | -1.94% | -1.94% | -1.94% |
| 2026-10-14 | -9.47% | -9.47% | -9.47% | -9.47% |
| 2026-10-15 | -14.14% | -14.14% | -14.14% | -14.14% |
| 2026-10-16 | -19.98% | -18.88% | -18.88% | -19.81% |

## Wnioski

1. Sygnał (v1, D0→D5): 1.21 pp kapitału/tydz., t 2.03 brutto, netto 0.88 pp (t 1.48); baseline t 97,5% = 1.90. NIE przebija baseline z t>2 po kosztach.
2. Opóźnienie wejścia pt→pon (v2 − v1): +0.099 pp/tydz. (t +0.24).
3. Stop 10% bez reopen (v3 − v2): -0.283 pp/tydz. (t -2.06); reopen (v4 − v3): +0.098 (t +1.10); razem app.py (v4 − v2): -0.185 pp/tydz. (t -1.70). Na szumie (losowe koszyki) v4 − v2 = -0.005 pp/tydz.
4. Sizing 1/σ z celem 1,5% σ dziennej (v8): średnia 0.43 pp, σ 3.98, Sharpe 0.77, maxDD 38.9% vs v2 Sharpe 0.95, maxDD 68.6%; śr. gross 1.35; σ dz. kapitału v2 = 4.31% (cel 1,5%).
5. Kill switch 25%: v2 trafia w 41.3% okien 12-tyg., v4 w 40.4%, v8 w 0.4%.
6. ALLOC_PCT 0,12 (v10): średnia 0.65 pp, σ 4.93, maxDD 42.1%, kill w 5.8% okien 12-tyg.; kapitał końc. z kill 92.2 vs 87.2 dla 0,24; netto 0.49 pp (t 1.52).

## Co zmienić w app.py (nazwy zmiennych)

Ranking kosztu elementów wykonania (B, brutto, pp kapitału/tydz.; ujemne = kosztuje). Warianty sizingu (v8/v10/v11) obniżają średnią przez samo zmniejszenie gross — to NIE koszt (t-stat i Sharpe bez zmian przy równych wagach), dlatego są wypisane osobno:

- stop 2,5σ bez reopen (v6 − v2): -0.298 pp/tydz. (t -2.71)
- stop 10% bez reopen (v3 − v2): -0.283 pp/tydz. (t -2.06)
- stop 15% bez reopen (v5 − v2): -0.189 pp/tydz. (t -2.26)
- stop 10% + reopen = app.py (v4 − v2): -0.185 pp/tydz. (t -1.70)
- REDUCE 50% po 2σ (v7 − v2): -0.128 pp/tydz. (t -1.81)
- (8) + stop10 reopen (v9 − v8): -0.057 pp/tydz. (t -1.32)
- reopen po stopie (v4 − v3): +0.098 pp/tydz. (t +1.10)
- opóźnienie wejścia pt→pon (v2 − v1): +0.099 pp/tydz. (t +0.24)

Sizing (zmiana skali, nie koszt): sizing 1/σ cel 1,5% (v8 − v2): -0.878 pp/tydz., t-stat wariantu 1.64 vs 2.03; ALLOC 0,12 zamiast 0,24 (v10 − v2): -0.653 pp/tydz., t-stat wariantu 2.03 vs 2.03; ALLOC 0,16 zamiast 0,24 (v11 − v2): -0.435 pp/tydz., t-stat wariantu 2.03 vs 2.03

Interpretacja i rekomendacje:

- **Największy koszt to nie reguła per noga, tylko para `ALLOC_PCT=0.24` × `KILL_LEVEL=0.75`**: przy gross 240% tygodniowa σ kapitału wynosi ~10 pp (dzienna 4.3%), więc obsunięcie 25% od szczytu to ~2,5σ tygodniowej i wypada w 41% okien 12-tygodniowych; po trafieniu strategia z dodatnią oczekiwaną (kapitał 716 bez kill) kończy na 87. Żaden stop per noga tego nie zmienia (B3: 37–41% dla v1–v7). Działa tylko sizing: `ALLOC_PCT=0.12` daje 5.8% okien z killem, sizing 1/σ z celem 1,5% (gross śr. 1.35) 0.4%. Alternatywa, jeśli właściciel chce gross 240%: `KILL_LEVEL` musiałby zejść do ok. 0,50 — co jest sprzeczne z celem kill switcha.
- **`STOP_LOSS_PCT=0.10` (twardy stop od ceny wejścia) obniża oczekiwaną o -0.28 pp/tydz. (t -2.1) i NIE zmniejsza σ ani maxDD** (B1: σ 9.87 vs 9.86, maxDD 74% vs 69%); na losowych koszykach jest neutralny (+0.003), czyli ścina właśnie noga po spadku, w której sygnał momentum ma dodatni dryf do końca tygodnia. Stop 15% (`STOP_LOSS_PCT=0.15`) kosztuje mniej (-0.19), stop 2,5σ więcej (-0.30). Rekomendacja: `STOP_LOSS_PCT=0` (wyłączyć) albo podnieść do 0,15–0,20 i traktować wyłącznie jako siatkę awaryjną; ryzykiem całości steruje sizing, nie stop per noga.
- **Reopen po stopie** (brak wpisu `exclude` po STOP → `desired_book` otwiera nogę w następnym biegu) odrabia część kosztu stopu (+0.10 pp/tydz., t 1.1) za cenę drugiego spreadu (145 reopenów na 293 stopów). To nie jest błąd kosztowy, lecz logiczny: stop bez pamięci jest sprzeczny sam ze sobą. Jeśli stop zostaje, po STOP bot powinien dopisywać do `signals.json` wpis `exclude` {ticker, action: CLOSE, basis: 'stop'} (ścieżka już istnieje dla pulsu; `bramka_reakcji` przepuszcza basis spoza ('cena','price') bez sprawdzania), żeby `desired_book` nie otwierał nogi do soboty — wariant v3. Alternatywnie zaakceptować v4 jako świadomy wybór (mniej kosztuje niż v3 brutto, ale netto różnica maleje).
- **REDUCE 50% po 2σ zamiast stopu** (`REACT_REDUCE_PCT`/`REDUCE_FACTOR` jako siatka automatyczna) kosztuje -0.13 pp/tydz. — mniej niż stop, ale nadal ujemnie; nie rozwiązuje problemu kill switcha.
- **Opóźnienie wejścia** (rotacja w poniedziałek 13:45 UTC zamiast D0) jest statystycznie nieistotne (+0.10 pp/tydz., t 0.2); W4–W7 akurat sprzyjało (+8 pkt kapitału w (A)). Nie warto zmieniać harmonogramu cron-job.org z tego powodu.
- **Koszty**: finansowanie 6%/rok od gross 240% = 0,28 pp/tydz., spread z turnoverem ~0,05 pp — razem ~0.32 pp/tydz. z 1.31 brutto. Netto t-stat v2 = 1.52 (brutto 2.03; baseline 97,5% = 1.90): po kosztach żaden wariant nie przebija baseline z t>2. Obniżenie gross (ALLOC_PCT 0,12) tnie finansowanie proporcjonalnie, ale nie poprawia t-stat (koszt i zwrot skalują się razem).
