# IC Modelu 3.0 per tydzień (Spearman wynik vs zwrot rel. 5 sesji od D0; strona SHORT ma niski wynik, więc IC30 dodatni = model trafia kierunek)

| week | d0 | d5 | dF | ic30 | ic30_okno_fakt | ic_long15 | ic_short15 | spread5_pp | spreadF_div_pp | hit_top5 | hit_bot5 | hit_top5_fakt | hit_bot5_fakt | mean_rel_rest | share_rest_pos | n_rest |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-W1 | 2026-08-26 | 2026-09-02 | 2026-08-28 | -0.16 | -0.33 | 0.31 | -0.28 | -3.26 | -4.06 | 3 | 2 | 1 | 1 | -2.01 | 34.25 | 73 |
| 2026-W2 | 2026-08-28 | 2026-09-04 | 2026-09-04 | 0.33 | 0.33 | 0.46 | 0.18 | 6.40 | 6.19 | 4 | 3 | 4 | 3 | -1.27 | 38.89 | 72 |
| 2026-W3 | 2026-09-04 | 2026-09-14 | 2026-09-11 | -0.59 | -0.03 | -0.17 | 0.05 | -3.88 | 1.44 | 1 | 2 | 2 | 3 | -0.18 | 43.06 | 72 |
| 2026-W4 | 2026-09-11 | 2026-09-18 | 2026-09-28 | 0.58 | 0.61 | -0.15 | 0.09 | 7.29 | 13.85 | 3 | 4 | 3 | 5 | -1.56 | 30.56 | 72 |
| 2026-W5 | 2026-09-28 | 2026-10-05 | 2026-10-02 | 0.34 | 0.35 | -0.19 | 0.18 | 6.04 | 5.95 | 3 | 5 | 3 | 5 | -1.27 | 36.11 | 72 |
| 2026-W6 | 2026-10-02 | 2026-10-09 | 2026-10-09 | -0.54 | -0.54 | -0.20 | -0.18 | -5.59 | -5.89 | 1 | 2 | 1 | 2 | 0.99 | 66.67 | 72 |
| 2026-W7 | 2026-10-09 | 2026-10-16 | 2026-10-16 | -0.65 | -0.65 | -0.22 | 0.06 | -21.15 | -21.15 | 0 | 0 | 0 | 0 | 3.77 | 76.39 | 72 |

ic30: średnia -0.098, t=-0.51, n=7, dodatnich 3/7

ic30_okno_fakt: średnia -0.036, t=-0.20, n=7, dodatnich 3/7

ic_long15: średnia -0.021, t=-0.20, n=7, dodatnich 2/7

ic_short15: średnia 0.013, t=0.19, n=7, dodatnich 5/7

spread5_pp: średnia -2.021, t=-0.53, n=7, dodatnich 3/7

spreadF_div_pp: średnia -0.525, t=-0.12, n=7, dodatnich 4/7

kontrola spread okna faktycznego z dywidendami vs history spread_pp: W1 -4.06, W2 6.19, W3 1.44, W4 13.85, W5 5.95, W6 -5.89, W7 -21.15

Pooled Spearman (210 nazwo-tygodni, rel5 demeaned per tydzień): -0.133
Permutacja (5000): P(średni IC30 >= -0.098) = 0.916; 5-95% przy zerowej mocy: -0.117…0.112

# Hit rate i średni zwrot pozycji wg grupy (5 sesji od D0, równe wagi; "reszta" = uniwersum poza TOP15/BOTTOM15, kierunek long dla strony LONG i short dla SHORT — czyli to samo co losowa nazwa)
| side | grupa | n | hit | mean_pp | sd | t |
|---|---|---|---|---|---|---|
| LONG | koszyk5 | 35 | 42.86 | -1.98 | 6.55 | -1.79 |
| LONG | ranking6-15/wykl. | 70 | 40.00 | -1.94 | 6.89 | -2.35 |
| SHORT | koszyk5 | 35 | 51.43 | -0.04 | 6.13 | -0.04 |
| SHORT | ranking6-15/wykl. | 70 | 47.14 | -0.67 | 5.79 | -0.97 |

Średni zwrot pozycji grupy per tydzień (p.p.) — do t klastrowanego:
| side | grupa | 2026-W1 | 2026-W2 | 2026-W3 | 2026-W4 | 2026-W5 | 2026-W6 | 2026-W7 |
|---|---|---|---|---|---|---|---|---|
| LONG | koszyk5 | -1.03 | 4.18 | -3.20 | 2.12 | 0.37 | -4.87 | -11.46 |
| LONG | ranking6-15/wykl. | -2.31 | -2.42 | -6.93 | 4.14 | 3.92 | -2.10 | -7.87 |
| SHORT | koszyk5 | -2.24 | 2.22 | -0.68 | 5.18 | 5.67 | -0.72 | -9.69 |
| SHORT | ranking6-15/wykl. | -0.31 | 1.41 | -2.13 | 3.21 | 0.33 | -3.37 | -3.78 |
LONG koszyk5: śr -1.98 p.p./tydz., t(7 tyg.)=-1.01
LONG ranking6-15/wykl.: śr -1.94 p.p./tydz., t(7 tyg.)=-1.10
SHORT koszyk5: śr -0.04 p.p./tydz., t(7 tyg.)=-0.02
SHORT ranking6-15/wykl.: śr -0.66 p.p./tydz., t(7 tyg.)=-0.68

Baza losowa: udział nazw reszty uniwersum z rel5>0 per tydzień: 2026-W1: 34%, 2026-W2: 39%, 2026-W3: 43%, 2026-W4: 31%, 2026-W5: 36%, 2026-W6: 67%, 2026-W7: 76%

# Kalibracja p (p_win = deklarowane prawdopodobieństwo trafienia kierunku; w W1-W7 strona SHORT podawała p trafienia, w W8 p outperformance → znormalizowano)
p podane vs p ze wzoru B4 (50+0,5·(wynik−50), 38–62): zgodne co do 1 pkt w 97% wierszy (n=205); p jest funkcją wyniku, nie niezależną oceną
| p_win | n | trafien | hit_pct | p_sr | mean_pp |
|---|---|---|---|---|---|
| ≤54 | 22 | 11 | 50.00 | 53.50 | 0.35 |
| 55–56 | 52 | 23 | 44.23 | 55.63 | -1.14 |
| 57–58 | 55 | 24 | 43.64 | 57.53 | -1.53 |
| 59–60 | 37 | 16 | 43.24 | 59.62 | -1.52 |
| 61–62 | 39 | 16 | 41.03 | 61.64 | -1.73 |
p>55: 73/164 = 44.5% (±7.6 p.p. 95%), deklarowane śr. 58.7%; śr. zwrot pozycji -1.37 p.p.
p<=55: 17/41 = 41.5% (±15.1 p.p. 95%), deklarowane śr. 54.2%; śr. zwrot pozycji -0.86 p.p.
p>55 per tydzień: 2026-W1: 12/27, 2026-W2: 13/22, 2026-W3: 3/18, 2026-W4: 16/21, 2026-W5: 19/26, 2026-W6: 7/25, 2026-W7: 3/25

Siła sygnału |wynik−50| (tercyle) vs trafienie:
| sila | n | hit_pct | mean_pp | sila_min | sila_max |
|---|---|---|---|---|---|
| słaby | 82 | 46.34 | -0.79 | 5.00 | 13.00 |
| średni | 64 | 46.88 | -0.98 | 14.00 | 18.00 |
| silny | 64 | 40.62 | -1.97 | 19.00 | 33.00 |
