# Zatłoczenie momentum i momentum rezydualne — test KANDYDATÓW (08.11.2026)

Dane: closes_5y.csv — 1255 sesji 2021-11-08…2026-11-06, 103 kandydatów (skład dzisiejszy → survivorship bias). Okna tygodniowe: 260; z sygnałem (6M skip 5): 234; wspólne okna surowe/rezydualne: 234 (od D0 = 2022-05-13).

Harness: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; noga long = r − r_NDX, short = −(r − r_NDX); spread_pp = śr. 5 long + śr. 5 short (gross 2). Sygnały wyłącznie z cen ≤ D0. Brutto; koszty (rotacja 0,10 % × 0,2 nominału strony za zmienioną nogę + finansowanie 6 %/rok × gross) podane osobno w T2.

## T1. Zatłoczenie momentum (średnia korelacja parowa 20-sesyjna TOP10 momentum na D0) → spread 6M skip 5 w następnym tygodniu

Rozkład proxy: tercyle 0.291 / 0.438, p80 0.515; korelacja TOP10 vs całe uniwersum kandydatów: średnia 0.375 vs 0.263.

| wariant / kubełek | okna | średnia pp | mediana | σ | t | Sharpe | skośność | p5 | min | hit | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| wszystkie okna z proxy | 234 | 1.03 | 0.91 | 7.56 | 2.08 | 0.98 | 0.07 | -10.7 | -23.7 | 58% | 52.6 |
| korelacja TOP10 — tercyl niski | 78 | 1.22 | 0.70 | 7.02 | 1.54 | 1.25 | 0.83 | -8.3 | -22.1 | 58% | 47.7 |
| korelacja TOP10 — tercyl środkowy | 78 | -0.23 | -0.08 | 7.13 | -0.29 | -0.24 | -0.44 | -10.1 | -23.7 | 50% | 85.1 |
| korelacja TOP10 — tercyl wysoki | 78 | 2.10 | 1.97 | 8.36 | 2.22 | 1.81 | -0.16 | -13.0 | -21.7 | 65% | 46.3 |
| korelacja TOP10 — górne 20 % | 47 | 2.00 | 2.72 | 8.31 | 1.65 | 1.74 | -0.42 | -13.1 | -21.7 | 66% | 46.3 |
| korelacja TOP10 − uniwersum (relatywna) — tercyl niski | 78 | 0.60 | 0.97 | 5.94 | 0.89 | 0.73 | -0.54 | -8.5 | -19.8 | 60% | 36.3 |
| korelacja TOP10 − uniwersum (relatywna) — tercyl wysoki | 78 | 1.27 | 1.80 | 9.49 | 1.19 | 0.97 | -0.34 | -15.9 | -23.7 | 58% | 46.3 |
|   → strona LONG, tercyl wysoki korelacji | 78 | 1.76 | 1.47 | 5.71 | 2.72 | 2.22 | -0.05 | -6.9 | -14.6 | 63% | 29.7 |
|   → strona SHORT, tercyl wysoki korelacji | 78 | 0.34 | 1.00 | 4.45 | 0.68 | 0.55 | -0.55 | -8.3 | -12.5 | 59% | 21.5 |
|   → strona LONG, tercyl niski korelacji | 78 | 1.31 | 0.69 | 4.99 | 2.32 | 1.89 | 1.82 | -4.7 | -9.9 | 63% | 20.9 |

Różnica średnich wysoki − niski tercyl: +0.88 pp (Welch t = 0.71); relatywna: +0.67 pp (t = 0.53). OLS spread ~ korelacja TOP10: nachylenie 1.7 pp na 1,0 korelacji (t = 0.53, n = 234); ~ relatywna: 2.6 (t = 1.02); ~ korelacja uniwersum: -2.3 (t = -0.74).

Stabilność znaku po latach (średni spread w tercylu wysokim − niskim, lata wg D0):

| rok | okna wys./nis. | wysoki pp | niski pp | różnica |
|---|---|---|---|---|
| 2022 | 12/9 | 0.29 | 4.07 | -3.78 |
| 2023 | 14/20 | 1.74 | 0.34 | +1.39 |
| 2024 | 7/20 | 0.93 | 2.94 | -2.02 |
| 2025 | 18/20 | 2.08 | 0.33 | +1.75 |
| 2026 | 27/9 | 3.42 | -1.53 | +4.96 |

10 najgorszych tygodni surowego momentum i wartość proxy na D0 (percentyl korelacji TOP10 wśród okien):

| D0 | spread pp | kor. TOP10 | percentyl | kor. uniwersum | VIX D0 | dd ^NDX D0 |
|---|---|---|---|---|---|---|
| 2026-02-27 | -23.7 | 0.39 | 58 | 0.12 | 19.9 | -4.4 % |
| 2026-10-30 | -22.1 | 0.26 | 24 | 0.06 | 19.4 | -9.1 % |
| 2026-07-10 | -21.7 | 0.72 | 99 | 0.08 | 15.0 | -2.7 % |
| 2022-07-15 | -19.8 | 0.36 | 47 | 0.50 | 24.2 | nan % |
| 2026-06-26 | -16.4 | 0.62 | 94 | 0.10 | 18.4 | -5.0 % |
| 2025-02-14 | -15.8 | 0.31 | 35 | 0.10 | 14.8 | 0.0 % |
| 2022-07-01 | -15.1 | 0.49 | 74 | 0.63 | 26.7 | nan % |
| 2024-04-12 | -13.3 | 0.38 | 54 | 0.29 | 17.3 | -1.8 % |
| 2026-06-18 | -13.1 | 0.53 | 83 | 0.11 | 16.4 | -0.8 % |
| 2026-04-10 | -13.0 | 0.65 | 95 | 0.29 | 19.2 | -3.8 % |

## T2. Momentum rezydualne (reszty wobec ^NDX i ^SOX, 126 sesji, skip 5, suma reszt / σ reszt) vs surowe momentum relatywne

| wariant / kubełek | okna | średnia pp | mediana | σ | t | Sharpe | skośność | p5 | min | hit | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a) surowe 6M rel. skip 5 (produkcyjne) | 234 | 1.03 | 0.91 | 7.56 | 2.08 | 0.98 | 0.07 | -10.7 | -23.7 | 58% | 52.6 | obrót 2.1 nóg/tydz.
| b) rezydualne NDX+SOX | 234 | -0.28 | -0.21 | 5.52 | -0.79 | -0.37 | -1.08 | -8.5 | -33.4 | 48% | 77.1 | obrót 8.8 nóg/tydz.
|   a) strona LONG | 234 | 1.24 | 0.85 | 5.29 | 3.59 | 1.69 | 0.40 | -6.9 | -14.6 | 62% | 29.7 |
|   b) strona LONG | 234 | 0.23 | 0.14 | 3.40 | 1.03 | 0.48 | 0.68 | -4.5 | -9.1 | 53% | 47.2 |
|   a) strona SHORT | 234 | -0.21 | -0.14 | 4.07 | -0.80 | -0.38 | -0.51 | -7.3 | -17.1 | 49% | 65.0 |
|   b) strona SHORT | 234 | -0.51 | -0.30 | 3.63 | -2.17 | -1.02 | -1.66 | -5.6 | -24.3 | 45% | 120.1 |

Pokrycie składów a/b: średnio 0.5 z 10 nóg wspólnych; korelacja tygodniowych spreadów a/b: -0.05. Koszty (rotacja + finansowanie): a) 0.27 pp/tydz., b) 0.41 pp/tydz. → netto a) 0.76, b) -0.69 pp/tydz. Stosunek wariancji b/a: 0.534 (df 233); różnica średnich b − a = -1.31 pp (t par = -2.10).

Po latach (lata wg D0, wspólne okna):

| rok | okna | a) surowe pp | b) rezydualne pp | a) min | b) min | a) σ | b) σ |
|---|---|---|---|---|---|---|---|
| 2022 | 34 | 0.34 | -0.26 | -19.8 | -10.9 | 7.48 | 3.97 |
| 2023 | 52 | -0.16 | -0.71 | -9.5 | -8.3 | 4.10 | 3.44 |
| 2024 | 52 | 1.39 | -0.29 | -13.3 | -23.6 | 7.32 | 5.80 |
| 2025 | 52 | 1.70 | 0.37 | -15.8 | -10.5 | 6.17 | 4.33 |
| 2026 | 44 | 1.74 | -0.58 | -23.7 | -33.4 | 11.60 | 8.73 |

Tygodnie, gdy surowe momentum straciło ≥ 10 pp — co zrobiło rezydualne:

| D0 | a) surowe | b) rezydualne | SOX−NDX pp |
|---|---|---|---|
| 2022-07-01 | -15.1 | 3.0 | 1.8 |
| 2022-07-15 | -19.8 | -9.2 | 2.1 |
| 2024-04-12 | -13.3 | 11.2 | -3.9 |
| 2025-02-14 | -15.8 | -0.4 | 1.8 |
| 2026-02-20 | -12.5 | -3.3 | -1.8 |
| 2026-02-27 | -23.7 | 10.5 | -5.9 |
| 2026-04-10 | -13.0 | -7.4 | 1.3 |
| 2026-06-18 | -13.1 | 7.8 | -3.7 |
| 2026-06-26 | -16.4 | 5.3 | -5.1 |
| 2026-07-10 | -21.7 | 16.3 | -5.8 |
| 2026-10-09 | -12.3 | -17.9 | -5.9 |
| 2026-10-30 | -22.1 | -33.4 | -7.2 |

Skład rezydualny na ostatnim D0 harnessu (2026-10-30, informacyjnie, NIE do signals.json): LONG ASML, LRCX, MRVL, ADBE, KLAC · SHORT NFLX, APP, TTWO, PEP, AMZN; surowe: LONG MRNA, CRWD, PANW, FTNT, DDOG · SHORT CRWV, APP, RKLB, NFLX, FER.

## T3 (informacyjnie). Reżim „po korekcie”: obsunięcie ^NDX od maks. 252 sesji > 10 % i VIX > 25 na D0

| wariant / kubełek | okna | średnia pp | mediana | σ | t | Sharpe | skośność | p5 | min | hit | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| surowe momentum — reżim po korekcie | 5 | 4.41 | 5.05 | 2.92 | 3.38 | 10.89 | -0.18 | 0.9 | 0.6 | 100% | 0.0 |
| surowe momentum — pozostałe okna | 229 | 0.96 | 0.83 | 7.61 | 1.90 | 0.91 | 0.09 | -11.4 | -23.7 | 57% | 52.6 |
|   strona LONG — po korekcie | 5 | 4.54 | 5.25 | 2.89 | 3.51 | 11.31 | -0.39 | 0.8 | 0.1 | 100% | 0.0 |
|   strona SHORT — po korekcie | 5 | -0.13 | 1.17 | 3.17 | -0.09 | -0.29 | -0.99 | -4.5 | -5.7 | 80% | 5.7 |
| rezydualne — po korekcie | 5 | 0.91 | -0.10 | 4.56 | 0.45 | 1.44 | 0.74 | -3.0 | -3.6 | 40% | 3.6 |
| rezydualne — pozostałe okna | 229 | -0.31 | -0.25 | 5.55 | -0.85 | -0.40 | -1.09 | -8.7 | -33.4 | 48% | 77.1 |

Okna „po korekcie”: 5 (lata: 2023: 1, 2025: 3, 2026: 1). Welch t różnicy średnich (po korekcie − pozostałe): 2.47.

## Uwagi metodyczne
- Skład dzisiejszy uniwersum (survivorship bias) — jak w analizie 18.10; spółki bez pełnego okna formacji wypadają z selekcji w danym tygodniu.
- Proxy zatłoczenia T1 jest liczone z cen (korelacja), nie z pozycji funduszy — mierzy współbieżność ruchów liderów momentum, nie faktyczne zatłoczenie.
- Kryteria awansu z nagłówka rutyny/reguly.md: ≥ 30 zdarzeń w ≥ 15 tygodniach, |t| ≥ 2 (klastrowane), ten sam znak w ≥ 4 z 5 lat, reguła musi wiązać. Moratorium na nowe reguły koszykowe do końca 26 okien cieni.
- „nan %” w kolumnie dd ^NDX = brak 252 sesji historii przed D0 (pierwszy rok danych).
- Nic z tego pliku nie zmienia ranking.py, signals.json ani bota.

