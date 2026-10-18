# Weryfikacja C6 — dodatek

## A. Holdout od 2025-07 (64 tyg.) vs in-sample do 2025-06 — Δ (wykluczone − reszta kandydatów), def. A, horyzont 1 tyg.

| kandydaci | próg przegranej | okres | n wykl. | śr. wykluczonych | śr. reszty | Δ / t / CI90 / hit tyg. |
|---|---|---|---|---|---|---|
| top kwintyl | 0 | holdout ≥2025-07 | 318 | 1.13 | 1.58 | -1.02 / -1.6 / [-2.04, -0.0] / 0.365 |
| top kwintyl | 0 | in-sample <2025-07 | 812 | 0.4 | 0.16 | 0.18 / 0.51 / [-0.38, 0.75] / 0.478 |
| top kwintyl | 0 | 2026 | 202 | 1.02 | 1.72 | -0.99 / -1.09 / [-2.47, 0.47] / 0.368 |
| top kwintyl | -4 | holdout ≥2025-07 | 153 | 1.66 | 1.44 | -1.22 / -1.45 / [-2.57, 0.17] / 0.412 |
| top kwintyl | -4 | in-sample <2025-07 | 253 | 0.99 | 0.15 | 1.21 / 1.88 / [0.2, 2.3] / 0.544 |
| top kwintyl | -4 | 2026 | 108 | 1.81 | 1.49 | -0.72 / -0.63 / [-2.5, 1.17] / 0.455 |
| TOP10 | 0 | holdout ≥2025-07 | 145 | 1.29 | 2.17 | -0.13 / -0.12 / [-1.88, 1.7] / 0.396 |
| TOP10 | 0 | in-sample <2025-07 | 392 | 0.6 | 0.33 | 0.3 / 0.58 / [-0.54, 1.15] / 0.493 |
| TOP10 | 0 | 2026 | 94 | 0.6 | 2.22 | 0.3 / 0.2 / [-2.19, 2.9] / 0.517 |
| TOP10 | -4 | holdout ≥2025-07 | 81 | 2.59 | 1.88 | 1.4 / 0.89 / [-1.0, 4.12] / 0.538 |
| TOP10 | -4 | in-sample <2025-07 | 149 | 1.22 | 0.31 | 1.7 / 2.01 / [0.38, 3.08] / 0.517 |
| TOP10 | -4 | 2026 | 56 | 2.6 | 1.68 | 2.69 / 1.25 / [-0.38, 6.35] / 0.68 |
| TOP5 | 0 | holdout ≥2025-07 | 59 | 2.83 | 2.54 | 0.75 / 0.44 / [-1.93, 3.7] / 0.5 |
| TOP5 | 0 | in-sample <2025-07 | 181 | 1.73 | 0.6 | 1.97 / 2.26 / [0.55, 3.52] / 0.573 |
| TOP5 | 0 | 2026 | 40 | 2.6 | 2.68 | 1.85 / 0.83 / [-1.5, 5.49] / 0.526 |
| TOP5 | -4 | holdout ≥2025-07 | 37 | 5.57 | 2.2 | 3.43 / 1.25 / [-0.71, 8.16] / 0.609 |
| TOP5 | -4 | in-sample <2025-07 | 85 | 1.7 | 0.75 | 2.3 / 1.81 / [0.33, 4.38] / 0.565 |
| TOP5 | -4 | 2026 | 26 | 6.08 | 2.12 | 4.41 / 1.1 / [-1.2, 11.13] / 0.692 |
| TOP15 | 0 | holdout ≥2025-07 | 234 | 1.73 | 1.79 | -0.59 / -0.73 / [-1.91, 0.68] / 0.448 |
| TOP15 | 0 | in-sample <2025-07 | 605 | 0.59 | 0.2 | 0.37 / 0.92 / [-0.26, 1.06] / 0.494 |
| TOP15 | 0 | 2026 | 153 | 1.42 | 1.82 | -0.59 / -0.52 / [-2.42, 1.31] / 0.472 |
| TOP15 | -4 | holdout ≥2025-07 | 122 | 2.09 | 1.73 | -1.37 / -1.31 / [-3.01, 0.3] / 0.4 |
| TOP15 | -4 | in-sample <2025-07 | 202 | 1.32 | 0.2 | 1.46 / 1.95 / [0.28, 2.66] / 0.562 |
| TOP15 | -4 | 2026 | 83 | 2.33 | 1.61 | -0.63 / -0.43 / [-2.92, 1.72] / 0.429 |

## B. Symulacja portfela z innym rankingiem: momentum 6M z pominięciem ostatniego miesiąca (mom6s), def. A


### ranking mom6s, przegrana < 0.0

- spread bez reguły 0.95 p.p./tydz. (Sharpe 0.94), z regułą 0.71 (Sharpe 0.76); Δ(reguła − bez) = **-0.24** p.p./tydz., t -1.05; LONG Δ -0.31 (t -1.77), SHORT Δ 0.07 (t 0.51); tygodnie z różnicą 215/230, reguła lepsza w 0.439 tyg.; zmiany nóg/tydz. 4.13 → 4.98; wykluczeń/tydz. 3.03
- po latach Δ spread: 2022: -0.25 (t -0.42, n 36), 2023: -0.2 (t -0.61, n 52), 2024: -0.23 (t -0.49, n 52), 2025: -0.2 (t -0.43, n 52), 2026: -0.35 (t -0.44, n 38)
- warunkowo: ^NDX tydzień < −3%: Δ -1.52 (t -2.97, n 32, LONG Δ -0.99); ^SOX−^NDX < −3 p.p.: Δ -2.38 (t -2.57, n 21, LONG Δ -2.02); holdout od 2025-07: Δ -0.24 (t -0.45, n 64, LONG Δ -0.36)

### ranking mom6s, przegrana < -4.0

- spread bez reguły 0.95 p.p./tydz. (Sharpe 0.94), z regułą 0.66 (Sharpe 0.68); Δ(reguła − bez) = **-0.29** p.p./tydz., t -1.48; LONG Δ -0.19 (t -1.24), SHORT Δ -0.1 (t -0.86); tygodnie z różnicą 192/230, reguła lepsza w 0.357 tyg.; zmiany nóg/tydz. 3.4 → 3.78; wykluczeń/tydz. 1.91
- po latach Δ spread: 2022: 0.09 (t 0.17, n 36), 2023: -0.22 (t -0.84, n 52), 2024: -0.37 (t -0.97, n 52), 2025: -0.33 (t -0.84, n 52), 2026: -0.56 (t -0.8, n 38)
- warunkowo: ^NDX tydzień < −3%: Δ -0.63 (t -1.67, n 32, LONG Δ -0.32); ^SOX−^NDX < −3 p.p.: Δ -1.33 (t -1.66, n 21, LONG Δ -1.2); holdout od 2025-07: Δ -0.42 (t -0.9, n 64, LONG Δ -0.22)

## C. Bootstrap tygodniowy Δ spread (reguła − bez), def. A, próg 0, obie strony

- d_spread: średnia -0.37 p.p./tydz., CI90 [-0.75, 0.0], CI95 [-0.83, 0.08], P(Δ>0 — reguła pomaga) = 0.05
- d_long: średnia -0.33 p.p./tydz., CI90 [-0.62, -0.04], CI95 [-0.68, 0.02], P(Δ>0 — reguła pomaga) = 0.031
- d_short: średnia -0.04 p.p./tydz., CI90 [-0.26, 0.18], CI95 [-0.3, 0.22], P(Δ>0 — reguła pomaga) = 0.379
- skumulowany Δ spread 2022-04…2026-09: -85.1 p.p. (suma tygodni); 2026 YTD: -16.2 p.p.; od W1 (21.08.2026): 4.4 p.p. w 5 tyg.
- tygodnie od W1 (ranking momentum TOP5/BOTTOM5, nie koszyki Modelu 3.0): 2026-08-21: Δ +0.88; 2026-08-28: Δ +1.85; 2026-09-04: Δ +1.46; 2026-09-11: Δ +0.25; 2026-09-18: Δ +0.00

## D. Ile wariantów przekrojowych wskazuje, że reguła POMAGA (Δ wykl.−reszta < 0, t ≤ −1,65) vs KOSZTUJE (Δ > 0, t ≥ 1,65)?

- wszystkich wariantów z t: 148; Δ<0 (reguła pomaga kierunkowo): 39, Δ>0 (kosztuje): 109; |t|≥1,65: pomaga 0, kosztuje 24
- tylko LONG: 122 wariantów, pomaga istotnie 0, kosztuje istotnie 21
- warianty, gdzie reguła pomaga z t ≤ −1,3: /short_botq/thr2|B_2z3_sesji<0 Δ -0.54 t -1.39 n 805; /short_botq/thr2|C_3sesje_lacznie<0 Δ -0.56 t -1.57 n 901; /warunkowo/^NDX tydzień w [−3%, +3%] Δ -0.47 t -1.34 n 761; /warunkowo/holdout od 2025-07 Δ -1.02 t -1.6 n 318; /warunkowo_duza/-4|holdout od 2025-07 Δ -1.22 t -1.45 n 153; /sito/SHORT|r10 ≤ −12% Δ -0.5 t -1.32 n 413
- warianty, gdzie reguła kosztuje z t ≥ 2,0: /long_top10/thr-4|A_ostatnia_sesja>0 Δ 1.61 t 2.13 n 230; /long_top10/thr-8|A_ostatnia_sesja>0 Δ 2.46 t 2.68 n 107; /long_top5/thr0|A_ostatnia_sesja>0 Δ 1.68 t 2.16 n 240; /long_top5/thr-2|A_ostatnia_sesja>0 Δ 2.64 t 2.9 n 174; /long_top5/thr-2|B_2z3_sesji>0 Δ 1.96 t 2.18 n 218; /long_top5/thr-2|C_3sesje_lacznie>0 Δ 2.24 t 2.61 n 227; /long_top5/thr-4|A_ostatnia_sesja>0 Δ 2.6 t 2.21 n 122; /long_top5/thr-8|A_ostatnia_sesja>0 Δ 3.2 t 2.37 n 65; /short_bot10/thr8|A_ostatnia_sesja<0 Δ 2.27 t 2.52 n 82; /warunkowo_duza/-8|^NDX tydzień > +2% Δ 3.24 t 2.1 n 37; /sito/TOP10|Perf.W ≤ −8%|fwd1 Δ 2.14 t 2.36 n 165; /sito/TOP10|Perf.W ≤ −8% i ostatnia sesja rel ≤ 0 (filtr W8)|fwd1 Δ 3.18 t 3.02 n 124; /sito/TOP10|rel tydzień ≤ −8 p.p. i ostatnia sesja rel ≤ 0|fwd1 Δ 2.46 t 2.68 n 107

## E. Filtr W8 w wersji skrajnej (TOP15, Perf.W ≤ −15%, ostatnia sesja rel ≤ 0): wszystkie obserwacje

- n=35 obserwacji w 26 tygodniach; fwd1 śr -0.19, mediana 1.82, hit 0.6; fwd2 śr 0.33, fwd4 śr 1.18; po latach {'2022': 2, '2023': 2, '2024': 7, '2025': 11, '2026': 13}
- lista: 2022-06-17 FANG W -21.4% last -9.76 → fwd1 -9.57; 2022-10-14 PDD W -16.7% last -1.33 → fwd1 5.65; 2023-05-12 MSTR W -17.1% last -5.33 → fwd1 2.9; 2023-10-20 TSLA W -15.6% last -2.19 → fwd1 0.4; 2024-04-05 MSTR W -15.6% last -12.21 → fwd1 3.4; 2024-04-19 ARM W -31.0% last -14.85 → fwd1 12.93; 2024-04-19 MSTR W -20.6% last -0.77 → fwd1 5.23; 2024-08-02 MSTR W -17.4% last -1.84 → fwd1 -6.9; 2024-08-02 ARM W -23.9% last -4.25 → fwd1 2.74; 2024-11-15 ALNY W -15.1% last -6.26 → fwd1 2.09; 2024-12-13 APP W -19.2% last -1.3 → fwd1 7.35; 2025-02-21 APP W -18.6% last -5.65 → fwd1 -18.19; 2025-02-21 AXON W -24.9% last -3.22 → fwd1 6.34; 2025-02-21 RKLB W -16.0% last -4.71 → fwd1 -9.62; 2025-02-28 PLTR W -16.2% last -1.45 → fwd1 3.26; 2025-04-04 APP W -19.5% last -10.2 → fwd1 6.51; 2025-09-26 ALAB W -19.3% last -1.86 → fwd1 0.35; 2025-10-10 APP W -16.5% last -1.58 → fwd1 2.7; 2025-10-17 ALAB W -22.5% last -2.94 → fwd1 1.06; 2025-11-07 CRWV W -22.2% last -2.45 → fwd1 -25.42; 2025-11-14 NBIS W -24.9% last -5.8 → fwd1 2.74; 2025-11-21 AMD W -17.4% last -1.86 → fwd1 1.82; 2026-03-06 LITE W -20.3% last -12.69 → fwd1 12.54; 2026-03-06 SNDK W -17.0% last -5.26 → fwd1 26.53; 2026-05-01 TER W -17.4% last -0.37 → fwd1 -1.35; 2026-06-05 RKLB W -23.3% last -3.46 → fwd1 -9.33; 2026-06-26 WDC W -21.4% last -12.07 → fwd1 -8.82; 2026-06-26 STX W -15.9% last -11.14 → fwd1 -9.59; 2026-06-26 ARM W -23.9% last -2.77 → fwd1 -6.41; 2026-06-26 NBIS W -16.2% last -5.27 → fwd1 -11.0; 2026-07-02 SNDK W -16.5% last -12.52 → fwd1 8.1; 2026-07-17 ALAB W -26.5% last -3.55 → fwd1 -2.34; 2026-07-17 SNDK W -29.3% last -2.49 → fwd1 7.66; 2026-07-31 SNDK W -15.4% last -5.69 → fwd1 -5.34; 2026-08-21 NBIS W -21.1% last -0.77 → fwd1 -4.97
- reszta TOP15 w tych samych tygodniach: n=355, fwd1 śr 1.28, fwd2 śr 2.51

## F. Kontynuacja po krachu? Top kwintyl, tygodnie ^NDX < −3%: przegrane (<0) vs wygrane nogi, forward 1 tyg.

- przegrane < 0 bez odzyskania: n=148, fwd1 śr 1.29, t 1.06, hit 0.561
- przegrane < 0 z odzyskaniem: n=96, fwd1 śr 0.45, t -0.2, hit 0.583
- wygrane ≥ 0: n=374, fwd1 śr -0.28, t -0.95, hit 0.433
- przegrane < −8 bez odzyskania: n=35, fwd1 śr -0.4, t -0.02, hit 0.514
- indeks ^NDX po tygodniu < −3% (n=32): następny tydzień śr 1.56%, dodatni w 0.625