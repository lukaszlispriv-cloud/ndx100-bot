# Zakład czynnikowy i reżimy (agent: rezim-i-zaklad-czynnikowy)

Dane: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv` — 1255 sesji 2021-10-18…2026-10-16, 103 kandydatów (skład dzisiejszy → survivorship bias). Okna tygodniowe: 260; wspólny zbiór okien (proxy, momentum 6M i odwrócenie 1T mają sygnał): 234 od D0 = 2022-04-22.

Harness: D0 = ostatnia sesja tygodnia ISO → D5 = ostatnia sesja następnego tygodnia; noga long = r − r_NDX, short = −(r − r_NDX); spread_pp = śr. 5 long + śr. 5 short. Sygnały tylko z cen ≤ D0; spółki bez pełnego okna 126 sesji wykluczone w danym oknie (ALAB wchodzi od 2024-09, SNDK od 2025-08 itd.). Koszty: 0,10% × nominał nogi (0,2 strony) za każdą zmienioną nazwę + finansowanie 6%/rok × gross (2 strony × udział) × dni/365; przy bramce dodatkowo 0,10% × 2 × |Δgross|.

**BASELINE** (2000 losowych koszyków 5/5 w każdym z 234 wspólnych okien): σ pojedynczego tygodnia (pooled) = **3.38 pp**, przedział 5–95% tygodniowego spreadu = **-5.4 … 5.4 pp**; rozkład średniej 2000 losowych STRATEGII: 5–95% = -0.36 … 0.37 pp/tydz., t-stat 5–95% = -1.65 … 1.66 (97,5% = 1.92), Sharpe 95% = 0.78.


## 1. Proxy zakładu czynnikowego: AI-hardware long (top 5 mom 6M z 14) vs defensywy short (5 najgorszych mom 6M z 14)

Listy: LONG z {MU, AMD, AVGO, MRVL, LITE, SNDK, STX, WDC, AMAT, LRCX, KLAC, TER, ALAB, NVDA}; SHORT z {PEP, CMCSA, SBUX, TMUS, KHC, MDLZ, KDP, CCEP, MNST, XEL, AEP, EXC, PAYX, ADP}. Spread liczony w harnessie (excess vs ^NDX po obu stronach).

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| proxy HW/DEF 6M | 234 | 1.30 | 1.34 | 7.05 | 2.83 | 1.33 | 60% | 55% | 68.4 | -21.9 | 20.8 |
| momentum 6M (uniwersum) | 234 | 1.01 | 0.97 | 7.57 | 2.03 | 0.96 | 56% | 53% | 70.7 | -25.8 | 31.8 |
| odwrócenie 1T (uniwersum) | 234 | -0.20 | -0.13 | 5.40 | -0.57 | -0.27 | 48% | 50% | 197.0 | -18.7 | 17.8 |
| BASELINE losowe 5/5 | 234 | 0.00 | — | 3.38 (pooled) | 5–95%: -1.65…1.66 | 95%: 0.78 | — | 50% | — | p5 -5.4 | p95 5.4 |

Po kosztach (wspólne okna):

| wariant | obrót nóg/tydz. | brutto pp | netto pp | t netto | Sharpe netto | pct wśród 2000 losowych strategii (brutto) |
|---|---|---|---|---|---|---|
| proxy AI-hardware L / defensywy S (6M) | 1.1 | 1.30 | 1.05 | 2.28 | 1.07 | 100.0% |
| momentum 6M top5/bottom5 (całe uniwersum) | 2.0 | 1.00 | 0.73 | 1.48 | 0.70 | 100.0% |
| odwrócenie 1T: long 5 najgorszych / short 5 najlepszych poprz. tygodnia | 9.1 | -0.20 | -0.61 | -1.75 | -0.82 | 17.5% |

### 1a. Korelacja tygodniowego spreadu proxy z czynnikami

| para | okna | r Pearsona | beta (OLS spread ~ czynnik) | R² | alfa pp/tydz. |
|---|---|---|---|---|---|
| proxy vs (^SOX−^NDX) | 234 | 0.73 | 1.92 | 0.53 | 0.72 |
| proxy vs (SMH−XLP) | 234 | 0.78 | 1.15 | 0.61 | 0.49 |
| momentum 6M vs (^SOX−^NDX) | 234 | 0.34 | 0.95 | 0.11 | 0.72 |
| momentum 6M vs (SMH−XLP) | 234 | 0.29 | 0.45 | 0.08 | 0.68 |
| momentum 6M vs proxy | 234 | 0.58 | 0.62 | 0.33 | 0.20 |
| odwrócenie 1T vs proxy | 234 | -0.06 | — | — | — |
| (^SOX−^NDX) vs (SMH−XLP) | 234 | 0.84 | — | — | — |

Korelacja proxy vs czynniki po latach:

| rok | okna | r(proxy, SOX−NDX) | r(proxy, SMH−XLP) | r(mom6M, SMH−XLP) | śr. proxy pp | śr. SMH−XLP pp | śr. SOX−NDX pp |
|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.73 | 0.78 | -0.44 | -0.49 | -0.06 | 0.24 |
| 2023 | 52 | 0.81 | 0.91 | 0.17 | 0.99 | 1.03 | 0.06 |
| 2024 | 52 | 0.76 | 0.89 | 0.29 | 1.16 | 0.75 | 0.09 |
| 2025 | 52 | 0.66 | 0.75 | 0.31 | 1.95 | 0.87 | 0.44 |
| 2026 | 41 | 0.77 | 0.74 | 0.60 | 2.66 | 0.72 | 0.78 |

Rozbicie proxy na lata i reżimy (brutto):

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | -0.49 | -0.50 | 4.27 | -0.70 | -0.83 | 46% | 46% | 28.9 | -11.0 | 6.9 |
| 2023 | 52 | 0.99 | 0.91 | 4.53 | 1.58 | 1.58 | 62% | 52% | 12.2 | -7.2 | 17.7 |
| 2024 | 52 | 1.16 | 1.59 | 6.39 | 1.31 | 1.31 | 63% | 54% | 39.9 | -14.5 | 13.9 |
| 2025 | 52 | 1.95 | 2.01 | 7.83 | 1.80 | 1.80 | 63% | 60% | 68.4 | -15.7 | 17.3 |
| 2026 | 41 | 2.66 | 4.75 | 10.55 | 1.62 | 1.82 | 63% | 58% | 47.6 | -21.9 | 20.8 |
| VIX>20 na D0 | 74 | 2.34 | 2.04 | 6.63 | 3.04 | 2.55 | 64% | 60% | 26.7 | -15.7 | 20.0 |
| VIX≤20 na D0 | 160 | 0.82 | 0.98 | 7.21 | 1.44 | 0.82 | 59% | 52% | 76.9 | -21.9 | 20.8 |
| NDX < MA200 | 39 | 1.16 | 1.12 | 7.15 | 1.02 | 1.17 | 56% | 55% | 28.4 | -15.7 | 18.7 |
| NDX > MA200 | 180 | 1.46 | 1.36 | 7.23 | 2.72 | 1.46 | 62% | 55% | 49.4 | -21.9 | 20.8 |

### 1b. Ile zakładu czynnikowego było w faktycznych koszykach W1–W7

| koszyk | long w liście HW | short w liście DEF | spread wg history pp | spread proxy w tym oknie pp | SMH−XLP pp | SOX−NDX pp |
|---|---|---|---|---|---|---|
| W1 (2026-08-26→2026-08-28) | 3/5 | 1/5 | -4.06 | -2.72 | 0.47 | -1.93 |
| W2 (2026-08-28→2026-09-04) | 3/5 | 2/5 | 6.19 | 8.50 | 3.53 | 1.94 |
| W3 (2026-09-04→2026-09-11) | 5/5 | 2/5 | 1.44 | 0.82 | 1.69 | 1.35 |
| W4 (2026-09-11→2026-09-28) | 5/5 | 2/5 | 13.85 | 19.35 | 6.86 | 2.33 |
| W5 (2026-09-28→2026-10-02) | 5/5 | 3/5 | 5.95 | 3.06 | 7.23 | 3.63 |
| W6 (2026-10-02→2026-10-09) | 5/5 | 3/5 | -5.89 | -2.02 | -7.93 | -4.54 |
| W7 (2026-10-09→2026-10-16) | 3/5 | 4/5 | -21.15 | -20.86 | -15.55 | -5.92 |

Uwaga: W4 rozliczano po 11 sesjach (do 2026-09-28); spready „history" liczone przez rutynę z cen d0 i cen rozliczenia (czasem Yahoo/TV, nie te same zamknięcia), więc mogą odbiegać o kilka dziesiątych pp od przeliczenia z closes_5y.csv.


## 2. Koszyki W4–W7: faktyczny skład vs ETF-y (SMH long / XLP short) i beta czynnikowa

Spread ETF w harnessie = (r_SMH − r_NDX) + (−(r_XLP − r_NDX)) = r_SMH − r_XLP. Beta koszyka: OLS tygodniowego spreadu KOSZYKA O STAŁYM SKŁADZIE (okna ISO sprzed D0, do 104 tygodni wstecz, bez look-ahead) na czynnik SMH−XLP oraz ^SOX−^NDX; „beta czynnikowa" = beta × zwrot czynnika w oknie koszyka; reszta = spread − beta czynnikowa.

| koszyk | okno | spread faktyczny pp (przeliczony) | history pp | ETF SMH−XLP pp | ETF ^SOX−XLP pp | beta(SMH−XLP) [R²] | beta czynnikowa pp | reszta pp | udział bety % | beta(SOX−NDX) [R²] | beta czynn. SOX pp | reszta SOX pp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W4 | 2026-09-11→2026-09-28 | 13.81 | 13.85 | 6.86 | 6.74 | 0.85 [0.42] (n=104) | 5.86 | 7.96 | 42% | 1.83 [0.71] | 4.26 | 9.56 |
| W5 | 2026-09-28→2026-10-02 | 5.95 | 5.95 | 7.23 | 7.51 | 0.93 [0.48] (n=104) | 6.74 | -0.79 | 113% | 1.82 [0.67] | 6.61 | -0.66 |
| W6 | 2026-10-02→2026-10-09 | -5.59 | -5.89 | -7.93 | -7.90 | 0.81 [0.37] (n=104) | -6.45 | 0.87 | 116% | 1.84 [0.69] | -8.36 | 2.77 |
| W7 | 2026-10-09→2026-10-16 | -21.15 | -21.15 | -15.55 | -16.44 | 0.59 [0.36] (n=104) | -9.20 | -11.95 | 43% | 1.10 [0.46] | -6.53 | -14.62 |

Suma W4–W7: spread faktyczny -7.0 pp; ETF SMH−XLP -9.4 pp; beta czynnikowa (SMH−XLP) -3.1 pp; reszta -3.9 pp. W6+W7: faktyczny -26.7 pp, ETF -23.5 pp, beta czynnikowa -15.6 pp.

Dla skali — czynnik jako „strategia" 2022–2026 (wspólne okna):

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ETF: long SMH / short XLP (= SMH−XLP) | 234 | 0.70 | 0.72 | 4.76 | 2.26 | 1.07 | 55% | —% | 37.8 | -15.6 | 13.8 |
| ^SOX − ^NDX | 234 | 0.30 | 0.31 | 2.69 | 1.74 | 0.82 | 54% | —% | 27.7 | -6.6 | 9.0 |

## 3. Reżimy warunkowe: momentum 6M vs odwrócenie 1T; kontynuacja czy odwrócenie po dużych tygodniach

Warunek sprawdzany na D0 (dane ≤ D0). „Poprzedni tydzień" = okno ISO zakończone na D0. Index: zwrot ^NDX i (^SOX−^NDX) w NASTĘPNYM tygodniu (D0→D5). Przekrój: `rev1W` = long 5 najgorszych / short 5 najlepszych poprzedniego tygodnia (dodatni = przegrani odbijają); `mom6M` = top5/bottom5 6M. Dodatkowo „przegrani-10": średni excess 10 najgorszych spółek poprzedniego tygodnia w tygodniu następnym (dodatni = odbicie).

| warunek na D0 | okna | ^NDX nast. tydz. śr. % [hit>0] | ^SOX−^NDX nast. tydz. śr. pp | mom6M śr. pp [t] hit | rev1W śr. pp [t] hit | przegrani-10 excess pp [t] | wygrani-10 excess pp [t] | proxy HW/DEF śr. pp [t] |
|---|---|---|---|---|---|---|---|---|
| wszystkie okna | 234 | 0.38 [57%] | 0.30 | 1.01 [2.0] 56% | -0.20 [-0.6] 48% | 0.29 [1.6] | 0.36 [1.9] | 1.30 [2.8] |
| VIX>20 na D0 | 74 | 0.79 [57%] | 0.79 | 2.42 [2.8] 64% | 0.17 [0.2] 46% | 0.89 [2.6] | 0.22 [0.7] | 2.34 [3.0] |
| VIX≤20 na D0 | 160 | 0.19 [57%] | 0.08 | 0.35 [0.6] 52% | -0.38 [-0.9] 49% | 0.01 [0.0] | 0.42 [1.8] | 0.82 [1.4] |
| ^NDX<MA50 | 71 | 0.52 [54%] | 0.58 | 0.82 [0.9] 58% | 0.43 [0.6] 54% | 0.76 [2.1] | 0.16 [0.5] | 1.17 [1.3] |
| ^NDX≥MA50 | 163 | 0.31 [59%] | 0.19 | 1.08 [1.8] 55% | -0.48 [-1.2] 46% | 0.08 [0.4] | 0.44 [1.9] | 1.36 [2.6] |
| ^NDX<MA200 | 39 | 0.30 [51%] | 0.48 | 1.91 [2.0] 64% | -0.39 [-0.4] 44% | 0.70 [1.5] | 0.56 [1.3] | 1.16 [1.0] |
| ^NDX≥MA200 | 195 | 0.39 [58%] | 0.27 | 0.82 [1.5] 54% | -0.17 [-0.4] 49% | 0.20 [1.0] | 0.32 [1.5] | 1.33 [2.6] |
| ^SOX 10 sesji < −8% | 15 | 0.59 [53%] | 0.33 | 1.27 [0.6] 60% | 2.95 [1.6] 67% | 2.04 [2.1] | -1.00 [-1.5] | 3.18 [1.3] |
| ^SOX 10 sesji ≥ −8% | 219 | 0.36 [58%] | 0.30 | 0.99 [1.9] 56% | -0.42 [-1.2] 47% | 0.17 [0.9] | 0.45 [2.3] | 1.17 [2.5] |
| po dużym tygodniu |^NDX|>4% | 38 | 1.15 [63%] | 0.48 | 1.12 [0.8] 63% | 2.02 [2.3] 63% | 0.93 [1.8] | -0.23 [-0.5] | 1.53 [1.6] |
| po dużym spadku ^NDX<−4% | 15 | 2.30 [67%] | 1.06 | -0.52 [-0.2] 60% | 3.00 [1.6] 67% | 1.34 [1.3] | -0.81 [-1.2] | 2.84 [1.4] |
| po dużym wzroście ^NDX>+4% | 23 | 0.39 [61%] | 0.10 | 2.18 [1.4] 65% | 1.39 [1.6] 61% | 0.66 [1.3] | 0.14 [0.2] | 0.68 [0.7] |
| „jak W7": ^NDX<−4% i ^SOX<−8% | 6 | 4.64 [83%] | 2.70 | 0.91 [0.2] 67% | 7.09 [2.8] 83% | 3.33 [1.9] | -2.47 [-2.4] | 7.51 [3.2] |
| po spokojnym tygodniu |^NDX|≤4% | 196 | 0.23 [56%] | 0.27 | 0.98 [1.9] 55% | -0.63 [-1.7] 45% | 0.16 [0.8] | 0.47 [2.3] | 1.26 [2.4] |

Tygodnie po dużym spadku ^NDX (<−4% w tygodniu zakończonym na D0) — co było w następnym tygodniu:

| D0 | ^NDX poprz. % | ^SOX poprz. % | VIX D0 | ^NDX nast. % | ^SOX−^NDX nast. pp | mom6M pp | rev1W pp | przegrani-10 pp | proxy pp |
|---|---|---|---|---|---|---|---|---|---|
| 2022-05-20 | -4.5 | -3.0 | 29.4 | 7.1 | 0.9 | 0.3 | 5.7 | 2.6 | 2.1 |
| 2022-06-10 | -5.7 | -7.5 | 27.8 | -4.8 | -4.2 | -4.3 | -7.6 | -5.6 | -5.3 |
| 2022-06-17 **(jak W7)** | -4.8 | -8.9 | 31.1 | 7.5 | -2.0 | -8.0 | -2.7 | -2.4 | -2.7 |
| 2022-07-01 **(jak W7)** | -4.3 | -9.6 | 26.7 | 4.7 | 1.8 | -14.6 | 13.5 | 5.5 | 5.6 |
| 2022-08-26 | -4.8 | -5.2 | 25.6 | -4.0 | -3.1 | 0.9 | -9.3 | -1.3 | -3.9 |
| 2022-09-02 | -4.0 | -7.1 | 25.5 | 4.0 | 0.7 | -8.0 | 8.0 | 3.8 | 3.3 |
| 2022-09-16 | -5.8 | -5.8 | 26.3 | -4.6 | -1.4 | 6.8 | -1.2 | -3.4 | -3.1 |
| 2022-09-23 | -4.6 | -6.0 | 29.9 | -3.0 | -1.2 | 2.4 | 3.3 | 2.2 | 1.9 |
| 2022-11-04 | -6.0 | -1.5 | 24.6 | 8.8 | 6.0 | -5.8 | 6.1 | 5.1 | 6.4 |
| 2024-04-19 **(jak W7)** | -5.4 | -9.2 | 18.7 | 4.0 | 6.0 | 7.0 | 10.9 | 6.6 | 11.0 |
| 2024-09-06 **(jak W7)** | -5.9 | -12.2 | 22.4 | 5.9 | 4.1 | 9.3 | 9.9 | 8.7 | 8.1 |
| 2025-04-04 **(jak W7)** | -9.8 | -16.0 | 45.3 | 7.4 | 3.5 | 5.1 | 1.9 | 0.0 | 13.8 |
| 2026-06-05 | -4.5 | -4.7 | 21.5 | 2.3 | 7.1 | 16.5 | 3.8 | 0.0 | 10.5 |
| 2026-06-26 | -4.2 | -7.9 | 18.4 | 0.7 | -5.1 | -22.1 | -6.4 | -3.1 | -14.4 |
| 2026-07-17 **(jak W7)** | -4.1 | -10.0 | 18.8 | -1.6 | 2.9 | 6.6 | 9.1 | 1.6 | 9.2 |

Sam tydzień W7 (D0 2026-10-09→2026-10-16): ^NDX -5.49%, ^SOX -11.41%, SMH−XLP -15.55 pp, mom6M -13.64 pp, rev1W -10.43 pp, proxy -20.86 pp. Następny tydzień (po W7) jeszcze nie istnieje w danych — tabela wyżej to jedyna statystyka ex ante dla tygodnia W8.


Pełne rozbicie momentum 6M i odwrócenia 1T (brutto, wspólne okna):


**momentum 6M**

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

**odwrócenie 1T**

| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.68 | -0.02 | 5.35 | 0.78 | 0.92 | 49% | 51% | 18.5 | -9.3 | 13.5 |
| 2023 | 52 | 1.09 | 1.20 | 4.37 | 1.80 | 1.80 | 62% | 53% | 17.5 | -9.2 | 11.3 |
| 2024 | 52 | -0.68 | -1.22 | 4.21 | -1.16 | -1.16 | 44% | 50% | 50.8 | -8.5 | 10.9 |
| 2025 | 52 | -1.23 | -0.56 | 4.63 | -1.92 | -1.92 | 40% | 48% | 73.8 | -12.8 | 10.6 |
| 2026 | 41 | -0.74 | -0.63 | 8.05 | -0.58 | -0.66 | 46% | 49% | 69.4 | -18.7 | 17.8 |
| VIX>20 na D0 | 74 | 0.17 | -0.32 | 6.03 | 0.24 | 0.20 | 46% | 50% | 41.7 | -18.7 | 17.8 |
| VIX≤20 na D0 | 160 | -0.38 | -0.08 | 5.09 | -0.93 | -0.53 | 49% | 50% | 165.4 | -15.2 | 17.1 |
| NDX < MA200 | 39 | -0.39 | -0.30 | 5.54 | -0.44 | -0.50 | 44% | 48% | 35.9 | -18.7 | 11.3 |
| NDX > MA200 | 180 | -0.20 | -0.08 | 5.33 | -0.52 | -0.28 | 49% | 50% | 170.2 | -15.2 | 17.8 |

## 4. Bramka reżimu P0/P1/P2 (progi z rutyny/tygodniowa.md KROK B0)

Dziennie: P1 = ^NDX<MA200 LUB drawdown od max 252 sesji >10% LUB VIX>28; P2 = drawdown>20% LUB VIX>40 LUB sesja ≤−5%. Wariant „surowy" = poziom z progów w dniu D0; wariant „z histerezą" = automat jak w rutynie (z P2 do handlu po 5 kolejnych sesjach VIX<25 i ^NDX>MA50 → P1; z P1 do P0 po 3 kolejnych sesjach VIX<22 i ^NDX>MA200). Gross: P0 = 100%, P1 = 50%, P2 = 0%. Reżim odczytany na D0 obowiązuje w oknie D0→D5.

Częstość (wspólne okna, odczyt na D0):

| rok | okna | P1 surowy | P2 surowy | P1 z histerezą | P2 z histerezą | ^NDX<MA200 | DD>10% | VIX>28 | DD>20% | VIX>40 | sesja D0 ≤−5% | śr. gross hist. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| razem | 234 | 27 | 42 | 21 | 50 | 39 | 63 | 16 | 42 | 1 | 1 | 74% |
| 2022 | 37 | 2 | 35 | 1 | 36 | 22 | 37 | 11 | 35 | 0 | 0 | 1% |
| 2023 | 52 | 9 | 6 | 6 | 9 | 4 | 15 | 0 | 6 | 0 | 0 | 77% |
| 2024 | 52 | 3 | 0 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 97% |
| 2025 | 52 | 9 | 1 | 5 | 5 | 10 | 7 | 3 | 1 | 1 | 1 | 86% |
| 2026 | 41 | 4 | 0 | 6 | 0 | 3 | 1 | 2 | 0 | 0 | 0 | 93% |

Sesje dzienne 2022–2026 w stanie P2 (z histerezą): 240 z 1202; P1: 171. Epizody P2 (pierwsza sesja): 2022-04-26, 2022-08-19, 2023-02-21, 2025-04-03.


Co bramka wycina — spread strategii w tygodniach wg stanu bramki (brutto, gross 100%):

| stan na D0 | okna | ^NDX nast. % [hit] | mom6M śr. pp [t] | rev1W śr. pp [t] | proxy śr. pp [t] | SMH−XLP pp |
|---|---|---|---|---|---|---|
| surowy P0 | 165 | 0.35 [59%] | 0.97 [1.6] | -0.61 [-1.5] | 1.34 [2.3] | 0.58 |
| surowy P1 | 27 | 0.44 [52%] | 2.96 [2.4] | 1.10 [0.8] | 2.36 [1.5] | 1.12 |
| surowy P2 | 42 | 0.46 [52%] | -0.12 [-0.1] | 0.56 [0.7] | 0.47 [0.6] | 0.94 |
| z histerezą P0 | 163 | 0.33 [60%] | 0.93 [1.5] | -0.59 [-1.5] | 1.33 [2.3] | 0.51 |
| z histerezą P1 | 21 | 0.66 [57%] | 3.04 [2.0] | 0.97 [0.6] | 2.63 [1.4] | 1.85 |
| z histerezą P2 | 50 | 0.41 [50%] | 0.41 [0.5] | 0.57 [0.8] | 0.67 [1.0] | 0.84 |

Strategie z bramką (gross × spread; tygodnie P2 = 0 pp; koszty: rotacja × gross + 0,10%×2×|Δgross| + finansowanie × gross):

| wariant | okna | brutto pp | σ | t | Sharpe | hit | maxDD | najgorsze | netto pp | t netto | Sharpe netto | śr. gross |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mom6M | bez bramki | 234 | 1.01 | 7.57 | 2.03 | 0.96 | 56% | 70.7 | -25.8 | 0.73 | 1.48 | 0.70 | 100% |
| mom6M | bramka surowa | 234 | 0.86 | 6.81 | 1.92 | 0.91 | 46% | 70.7 | -25.8 | 0.64 | 1.44 | 0.68 | 76% |
| mom6M | bramka z histerezą | 234 | 0.78 | 6.78 | 1.76 | 0.83 | 43% | 71.5 | -25.8 | 0.57 | 1.29 | 0.61 | 74% |
| mom6M | tylko P2→0 (P1 pełny gross), hist. | 234 | 0.92 | 7.02 | 2.00 | 0.94 | 43% | 70.7 | -25.8 | 0.70 | 1.52 | 0.72 | 79% |
| mom6M | odwrotna: P1/P2 → gross 150%/200% | 234 | 1.23 | 9.34 | 2.01 | 0.95 | 56% | 69.8 | -29.2 | 0.88 | 1.44 | 0.68 | 126% |
| rev1W | bez bramki | 234 | -0.20 | 5.40 | -0.57 | -0.27 | 48% | 197.0 | -18.7 | -0.62 | -1.74 | -0.82 | 100% |
| rev1W | bramka surowa | 234 | -0.37 | 4.47 | -1.25 | -0.59 | 40% | 195.8 | -15.2 | -0.69 | -2.36 | -1.11 | 76% |
| rev1W | bramka z histerezą | 234 | -0.37 | 4.44 | -1.27 | -0.60 | 38% | 190.7 | -15.2 | -0.68 | -2.35 | -1.11 | 74% |
| rev1W | tylko P2→0 (P1 pełny gross), hist. | 234 | -0.32 | 4.90 | -1.01 | -0.48 | 38% | 194.5 | -18.7 | -0.65 | -2.04 | -0.96 | 79% |
| rev1W | odwrotna: P1/P2 → gross 150%/200% | 234 | -0.04 | 7.17 | -0.08 | -0.04 | 48% | 203.4 | -28.0 | -0.56 | -1.21 | -0.57 | 126% |
| proxy | bez bramki | 234 | 1.30 | 7.05 | 2.83 | 1.33 | 60% | 68.4 | -21.9 | 1.05 | 2.28 | 1.07 | 100% |
| proxy | bramka surowa | 234 | 1.08 | 6.33 | 2.62 | 1.23 | 50% | 61.3 | -21.9 | 0.88 | 2.13 | 1.00 | 76% |
| proxy | bramka z histerezą | 234 | 1.04 | 6.30 | 2.53 | 1.19 | 49% | 58.9 | -21.9 | 0.85 | 2.06 | 0.97 | 74% |
| proxy | tylko P2→0 (P1 pełny gross), hist. | 234 | 1.16 | 6.71 | 2.65 | 1.25 | 49% | 68.4 | -21.9 | 0.96 | 2.18 | 1.03 | 79% |
| proxy | odwrotna: P1/P2 → gross 150%/200% | 234 | 1.56 | 8.57 | 2.79 | 1.31 | 60% | 77.9 | -23.5 | 1.24 | 2.21 | 1.04 | 126% |

Stan bramki na D0 koszyków systemu (dla porównania z `rezim` w history):

| koszyk | D0 | surowy | z histerezą | ^NDX vs MA200 % | DD od max 252 % | VIX |
|---|---|---|---|---|---|---|
| W1 | 2026-08-26 | P0 | P0 | 8.7 | -4.7 | 15.2 |
| W2 | 2026-08-28 | P0 | P0 | 9.3 | -4.0 | 14.4 |
| W3 | 2026-09-04 | P0 | P0 | 9.3 | -3.6 | 14.5 |
| W4 | 2026-09-11 | P0 | P0 | 8.3 | -4.2 | 15.8 |
| W5 | 2026-09-28 | P0 | P0 | 10.6 | -1.5 | 16.1 |
| W6 | 2026-10-02 | P0 | P0 | 12.1 | 0.0 | 15.3 |
| W7 | 2026-10-09 | P0 | P0 | 11.8 | -1.1 | 14.8 |
| W8 | 2026-10-16 | P0 | P0 | 5.2 | -6.5 | 20.0 |

## 5. Wnioski

1. Proxy „AI-hardware long / defensywy short”: średnia 1.30 pp/tydz., t = 2.83, netto 1.05 pp (t 2.28); σ 7.0 pp wobec 3.4 pp losowego koszyka — to zakład o 2.1× większej zmienności niż losowy 5/5. Korelacja z SMH−XLP r = 0.78 (R² 0.61), z ^SOX−^NDX r = 0.73.
2. Faktyczne koszyki W4–W7: 18/20 nóg long z listy hardware, 12/20 nóg short z listy defensyw. Beta na SMH−XLP koszyków: W4 0.85 (R² 0.42), W5 0.93 (R² 0.48), W6 0.81 (R² 0.37), W7 0.59 (R² 0.36). W6+W7 faktyczne -26.7 pp, z czego beta czynnikowa -15.6 pp (59%).
3. Po tygodniach ^NDX<−4% (n=15): ^NDX nast. tydz. 2.30% (hit 67%), ^SOX−^NDX 1.06 pp, mom6M -0.52 pp [t -0.2], rev1W 3.00 pp [t 1.6], przegrani-10 1.34 pp. Tygodnie „jak W7” (n=6): ^NDX 4.64%, mom6M 0.91 pp, rev1W 7.09 pp.
4. Bramka z histerezą: aktywna (P1 lub P2) w 71 z 234 tygodni (P2: 50); śr. gross 74%. Momentum 6M: bez bramki 1.00 pp (t 2.03, Sharpe 0.96, maxDD 71) → z bramką 0.78 pp (t 1.76, Sharpe 0.83, maxDD 72); netto 0.73 → 0.57 pp. Odwrócenie 1T: -0.20 → -0.37 pp.
