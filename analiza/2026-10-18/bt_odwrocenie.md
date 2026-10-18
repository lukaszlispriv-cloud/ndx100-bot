# Backtest: krótkoterminowe odwrócenie w Nasdaq-100 (okna tygodniowe)

Dane: `dane/closes_5y.csv` (zamknięcia 2021-10-18…2026-10-16). Okna: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; pierwsze D0 2022-04-29, ostatnie D5 2026-10-16, 233 okien. Uniwersum wspólne = spółki z pełną historią 131 sesji na D0 (min 80, max 96 spółek); indeksy/ETF wyłączone. Zwroty względem ^NDX; spread = śr. 5 LONG + śr. 5 SHORT (= long−short). Koszty: 0.1% na slot na rotację (liczone po faktycznej rotacji składu) + 6.0%/rok na gross (= 0.231 pp/tydz.). MA200 ^NDX: dla pierwszych okien z <200 sesji użyto średniej z dostępnych (≥131).

## Warianty

| kod | definicja |
|---|---|
| a_rev5 | LONG 5 najgorszych rel. do NDX w 5 sesjach, SHORT 5 najlepszych |
| b_rev10 | jw., okno 10 sesji |
| c_rev21 | jw., okno 21 sesji |
| d_rev5_w_trendzie | LONG = najgorsze 1T wśród spółek z dodatnim rel. momentum 6M (126 sesji, bez ostatnich 5); SHORT = najlepsze 1T wśród spółek z ujemnym momentum 6M |
| e_rev5_bez_zdarzen | a_rev5 po wykluczeniu spółek z jakimkolwiek \|zwrotem dziennym\| > 8.0% w ostatnich 5 sesjach (proxy wyników) |
| f_kombo_mom6_rev5 | wynik = 0,5·percentyl(momentum 6M, wysoki=dobry) + 0,5·percentyl(−zwrot 1T, wysoki=wyprzedany); LONG top 5, SHORT dół 5 |
| ref_mom6 | odniesienie: czyste momentum 6M (skip 1T): LONG 5 najlepszych, SHORT 5 najgorszych |

## Baseline: 2000 losowych koszyków 5/5 na każdym oknie

- rozkład spreadu losowego (pooled, 233 okien × 2000): średnia -0.00 pp, σ **3.40 pp**, p5 -5.43 pp, p95 5.42 pp
- σ spreadu losowego w pojedynczym oknie: mediana 3.05 pp (p5 1.74, p95 5.07)
- 2000 losowych STRATEGII (losowy koszyk w każdym oknie): średnia tygodniowa p5 -0.362 / p95 0.360 pp (σ średniej 0.218 pp); t-stat p5 -1.63 / p95 1.61; σ Sharpe'a losowego 0.46

## Pełne metryki (cały okres)

| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit L | hit S | śr. L | śr. S | maxDD | najgorsze | najlepsze | rotacja | koszt/tydz | **netto śr.** | netto skum. | p(losowa ≥) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a_rev5 | 233 | -0.33 | -0.21 | 5.35 | -0.93 | -0.44 | 46% | 55% | 48% | 0.37 | -0.69 | -206.6 | -18.8 | 17.8 | 90% | 0.41 | **-0.74** | -171.5 | 0.931 |
| b_rev10 | 233 | -0.59 | -0.36 | 5.67 | -1.58 | -0.75 | 47% | 47% | 45% | 0.12 | -0.71 | -166.7 | -26.7 | 19.6 | 67% | 0.36 | **-0.95** | -221.7 | 0.996 |
| c_rev21 | 233 | -0.67 | -0.90 | 6.20 | -1.66 | -0.78 | 45% | 51% | 45% | 0.22 | -0.89 | -244.8 | -30.9 | 15.2 | 48% | 0.33 | **-1.00** | -232.9 | 1.000 |
| d_rev5_w_trendzie | 233 | 0.11 | 0.54 | 5.19 | 0.33 | 0.15 | 55% | 54% | 49% | 0.43 | -0.31 | -51.7 | -17.4 | 17.8 | 88% | 0.41 | **-0.30** | -69.0 | 0.309 |
| e_rev5_bez_zdarzen | 233 | 0.13 | 0.41 | 5.03 | 0.41 | 0.19 | 54% | 56% | 51% | 0.45 | -0.31 | -78.5 | -17.7 | 14.4 | 93% | 0.42 | **-0.28** | -65.7 | 0.273 |
| f_kombo_mom6_rev5 | 233 | 0.16 | 0.14 | 5.94 | 0.41 | 0.20 | 52% | 52% | 48% | 0.61 | -0.45 | -52.8 | -20.0 | 17.4 | 80% | 0.39 | **-0.23** | -53.8 | 0.235 |
| ref_mom6 | 233 | 0.96 | 0.77 | 7.29 | 2.02 | 0.95 | 57% | 58% | 51% | 1.25 | -0.29 | -49.2 | -23.7 | 31.8 | 20% | 0.27 | **0.69** | 161.6 | 0.000 |

Jednostki: p.p. na tydzień; maxDD/najgorsze/najlepsze/skum. w p.p. (suma prosta spreadów). t = śr./σ·√n. Sharpe = śr./σ·√52 (brutto). p(losowa ≥) = odsetek z 2000 losowych strategii o średniej ≥ średniej wariantu.

## Lata (po dacie D0; brutto, pp/tydz.)

| wariant | 2022 (n / śr. / t / hit) | 2023 (n / śr. / t / hit) | 2024 (n / śr. / t / hit) | 2025 (n / śr. / t / hit) | 2026 (n / śr. / t / hit) |
|---|---|---|---|---|---|
| a_rev5 | 36 / 0.80 / 1.0 / 53% | 52 / 0.74 / 1.4 / 62% | 52 / -0.97 / -1.6 / 37% | 52 / -1.34 / -2.1 / 37% | 41 / -0.57 / -0.4 / 44% |
| b_rev10 | 36 / -0.85 / -0.9 / 39% | 52 / 0.56 / 1.0 / 62% | 52 / -1.20 / -1.4 / 37% | 52 / -0.92 / -1.4 / 46% | 41 / -0.61 / -0.5 / 51% |
| c_rev21 | 36 / 0.05 / 0.1 / 44% | 52 / 0.75 / 1.8 / 62% | 52 / -2.24 / -2.2 / 31% | 52 / -1.12 / -1.4 / 38% | 41 / -0.56 / -0.4 / 49% |
| d_rev5_w_trendzie | 36 / -0.28 / -0.4 / 53% | 52 / 0.60 / 1.1 / 65% | 52 / 0.03 / 0.1 / 52% | 52 / -0.24 / -0.3 / 54% | 41 / 0.39 / 0.4 / 49% |
| e_rev5_bez_zdarzen | 36 / 1.00 / 1.3 / 64% | 52 / 0.45 / 0.8 / 62% | 52 / 0.27 / 0.4 / 46% | 52 / -0.45 / -0.8 / 50% | 41 / -0.46 / -0.4 / 49% |
| f_kombo_mom6_rev5 | 36 / 0.13 / 0.2 / 50% | 52 / -0.06 / -0.1 / 46% | 52 / -0.14 / -0.2 / 50% | 52 / 0.78 / 0.9 / 60% | 41 / 0.07 / 0.1 / 51% |
| ref_mom6 | 36 / 0.03 / 0.0 / 64% | 52 / -0.24 / -0.5 / 44% | 52 / 1.53 / 1.5 / 54% | 52 / 1.35 / 1.6 / 58% | 41 / 2.10 / 1.2 / 68% |

## Reżimy na D0 (brutto, pp/tydz.)

| wariant | VIX>20 (n / śr. / t) | VIX≤20 (n / śr. / t) | NDX<MA200 (n / śr. / t) | NDX>MA200 (n / śr. / t) | 1. połowa (n / śr. / t) | 2. połowa (n / śr. / t) |
|---|---|---|---|---|---|---|
| a_rev5 | 73 / 0.24 / 0.3 | 160 / -0.59 / -1.5 | 53 / -0.05 / -0.1 | 180 / -0.41 / -1.0 | 116 / 0.40 / 1.0 | 117 / -1.05 / -1.9 |
| b_rev10 | 73 / -0.78 / -1.1 | 160 / -0.50 / -1.2 | 53 / -0.91 / -1.1 | 180 / -0.49 / -1.2 | 116 / 0.01 / 0.0 | 117 / -1.18 / -2.0 |
| c_rev21 | 73 / -0.83 / -1.1 | 160 / -0.60 / -1.2 | 53 / 0.36 / 0.5 | 180 / -0.98 / -2.1 | 116 / 0.07 / 0.2 | 117 / -1.42 / -2.0 |
| d_rev5_w_trendzie | 73 / 1.01 / 1.5 | 160 / -0.30 / -0.8 | 53 / -0.08 / -0.1 | 180 / 0.17 / 0.4 | 116 / 0.30 / 0.8 | 117 / -0.08 / -0.1 |
| e_rev5_bez_zdarzen | 73 / 1.08 / 1.8 | 160 / -0.30 / -0.8 | 53 / 0.53 / 0.8 | 180 / 0.02 / 0.0 | 116 / 0.57 / 1.5 | 117 / -0.30 / -0.6 |
| f_kombo_mom6_rev5 | 73 / 1.55 / 2.3 | 160 / -0.47 / -1.0 | 53 / 0.04 / 0.1 | 180 / 0.20 / 0.4 | 116 / -0.09 / -0.2 | 117 / 0.40 / 0.6 |
| ref_mom6 | 73 / 2.23 / 2.5 | 160 / 0.39 / 0.7 | 53 / 0.61 / 0.7 | 180 / 1.07 / 1.9 | 116 / -0.03 / -0.1 | 117 / 1.95 / 2.4 |

## a_rev5: 8 najgorszych i 5 najlepszych okien

| D0 | D5 | spread | long | short | LONG | SHORT |
|---|---|---|---|---|---|---|
| 2026-04-02 | 2026-04-10 | -18.8 | -5.1 | -13.7 | MSTR AXON MRNA CEG TMUS | LITE SNDK INTC STX MRVL |
| 2026-01-30 | 2026-02-06 | -15.2 | -4.4 | -10.9 | AXON PLTR INTU ALAB TTWO | SNDK STX LITE TXN META |
| 2025-11-07 | 2025-11-14 | -12.8 | -13.6 | 0.8 | CRWV DASH RKLB AXON NBIS | SNDK LITE DDOG IDXX MAR |
| 2025-03-28 | 2025-04-04 | -12.2 | -7.2 | -5.0 | ALAB APP MRVL AVGO ARM | CTAS TSLA PAYX ORLY MDLZ |
| 2025-08-01 | 2025-08-08 | -11.0 | -4.8 | -6.2 | MRNA ARM ODFL PANW PYPL | ALNY TER WDC MPWR ALAB |
| 2026-05-22 | 2026-05-29 | -10.6 | -4.1 | -6.5 | INTU MSTR WMT REGN TTWO | ARM ALAB QCOM CRWD MRVL |
| 2026-10-09 | 2026-10-16 | -10.4 | -7.7 | -2.7 | ARM INTC TER TMUS NBIS | MRNA CEG SHOP MELI ADSK |
| 2026-05-01 | 2026-05-08 | -10.2 | 1.9 | -12.2 | TER GEHC KLAC MRNA ARM | STX NXPI INTC SNDK QCOM |
| 2026-03-06 | 2026-03-13 | 17.8 | 12.5 | 5.3 | LITE SNDK LRCX TER STX | INTU TRI APP CRWD PLTR |
| 2026-08-14 | 2026-08-21 | 17.1 | 7.0 | 10.1 | APP AVGO CSCO PDD MSTR | NBIS SNDK STX WDC CRWV |
| 2024-09-06 | 2024-09-13 | 13.5 | 9.2 | 4.3 | ASML ALNY MSTR MPWR AVGO | MDLZ MNST PEP XEL AEP |
| 2022-07-01 | 2022-07-08 | 13.5 | 9.6 | 3.9 | MSTR SHOP AMD NVDA MPWR | EXC XEL AEP MRNA BKR |
| 2026-07-02 | 2026-07-10 | 13.0 | 3.6 | 9.3 | SNDK TER WDC STX MU | AXON MRNA RKLB PLTR WDAY |

## a_rev5: ostatnie 12 okien

| D0 | D5 | spread | long | short | LONG | SHORT |
|---|---|---|---|---|---|---|
| 2026-07-24 | 2026-07-31 | 3.0 | 1.6 | 1.4 | TSLA MRNA CRWD PANW SHOP | WDC CEG TER MU STX |
| 2026-07-31 | 2026-08-07 | 1.6 | 1.5 | 0.1 | ALNY SNDK NXPI KLAC QCOM | MSFT WDAY AMZN DXCM REGN |
| 2026-08-07 | 2026-08-14 | 1.7 | 4.6 | -2.9 | WDC DDOG APP FANG MNST | PLTR SHOP RKLB CRWV LITE |
| 2026-08-14 | 2026-08-21 | 17.1 | 7.0 | 10.1 | APP AVGO CSCO PDD MSTR | NBIS SNDK STX WDC CRWV |
| 2026-08-21 | 2026-08-28 | -0.6 | -3.1 | 2.5 | NBIS CRWV ARM STX INTC | MRNA MSTR VRTX CPRT MRVL |
| 2026-08-28 | 2026-09-04 | 8.5 | 3.9 | 4.6 | PYPL RKLB MRVL SNDK FER | CRWD SNPS FTNT MSTR CDNS |
| 2026-09-04 | 2026-09-11 | 2.3 | -2.3 | 4.6 | ADSK AXON CDNS SNPS DASH | SNDK ALNY MSTR MU NBIS |
| 2026-09-11 | 2026-09-18 | -4.9 | -2.7 | -2.2 | AMGN TRI ADBE SHOP AXON | AMD MRVL INTC TER LITE |
| 2026-09-18 | 2026-09-25 | -1.8 | -2.3 | 0.5 | CEG CRWV TMUS NFLX AXON | MSTR CRWD PANW SNDK FTNT |
| 2026-09-25 | 2026-10-02 | -0.1 | -0.2 | 0.1 | PAYX INTU CPRT ADBE ABNB | MRNA ALAB DDOG CDNS RKLB |
| 2026-10-02 | 2026-10-09 | 2.2 | -1.8 | 4.0 | ALNY APP WDC QCOM STX | LITE SNPS TER AMAT LRCX |
| 2026-10-09 | 2026-10-16 | -10.4 | -7.7 | -2.7 | ARM INTC TER TMUS NBIS | MRNA CEG SHOP MELI ADSK |

## Wnioski

- Odwrócenie 5-sesyjne (a_rev5): średnia -0.33 pp/tydz., t = -0.93, Sharpe -0.44, hit 46%; po kosztach (ok. 0.41 pp/tydz. przy rotacji 90%) średnia **-0.74 pp/tydz.**, skumulowane netto -171.5 pp w 233 tygodni.
- Baseline: σ spreadu losowego koszyka 5/5 = 3.40 pp/tydz.; losowa strategia ma średnią w przedziale [-0.36; 0.36] pp i |t| zwykle < 1.6. Wariant o najwyższym t: ref_mom6 (t = 2.02, p(losowa ≥) = 0.000).
- Warianty z t > 2 **i** dodatnią średnią po kosztach: ref_mom6.
- Asymetria nóg (a_rev5): noga LONG (kupno 1T przegranych) średnio 0.37 pp/tydz., hit 55%; noga SHORT (sprzedaż 1T wygranych) średnio **-0.69 pp/tydz.**, hit 48% — straty generuje przede wszystkim shortowanie tygodniowych liderów (krótkoterminowa KONTYNUACJA, nie odwrócenie).
- Dryf w czasie (a_rev5, brutto): 2022: 0.80 pp (hit 53%); 2023: 0.74 pp (hit 62%); 2024: -0.97 pp (hit 37%); 2025: -1.34 pp (hit 37%); 2026: -0.57 pp (hit 44%). Odwrócenie działało słabo dodatnio w 2022–2023, a od 2024 (era momentum AI/półprzewodniki) jest ujemne — pierwsza i druga połowa próby mają przeciwne znaki, więc nie ma stabilnego efektu.
- Lustro a_rev5 (kupuj 1T/1M liderów, sprzedawaj maruderów): średnia 0.33 pp, t = 0.93, netto -0.08 pp/tydz. — też NIE przebija progu t > 2 (i jest wynikiem in-sample, odczytanym z tego samego testu).
- Lustro c_rev21 (kupuj 1T/1M liderów, sprzedawaj maruderów): średnia 0.67 pp, t = 1.66, netto 0.35 pp/tydz. — też NIE przebija progu t > 2 (i jest wynikiem in-sample, odczytanym z tego samego testu).
- Filtry (d) trend, (e) bez zdarzeń i (f) kombinacja z momentum 6M poprawiają odwrócenie do ok. 0 brutto (t 0,3–0,4; p(losowa ≥) 0,24–0,31 — nieodróżnialne od losowego koszyka) i do ok. −0,25 pp/tydz. netto, bo rotacja 80–93% tygodniowo kosztuje ok. 0,4 pp/tydz. Cała poprawa względem (a) pochodzi z komponentu momentum, nie z odwrócenia.
- Odniesienie ref_mom6 (czyste momentum 6M, skip 1T): t = 2.02, netto 0.69 pp/tydz., rotacja 20% — jedyny wariant z t ≈ 2 i dodatnim wynikiem po kosztach, ale w 2022–2023 ≈ 0 (zysk skoncentrowany w 2024–2026, survivorship bias sprzyja momentum).
- **Odpowiedź wprost: odwrócenie 5-sesyjne w Nasdaq-100 2022–2026 NIE działa — brutto jest ujemne (−0,33 pp/tydz., t = −0,93, gorsze niż 93% losowych koszyków), a po koszcie spreadu i finansowania traci ok. 0,74 pp/tydz. (≈ −38 pp/rok). Żaden wariant odwrócenia (a–f) nie przebija baseline z t > 2 ani nie jest dodatni po kosztach.**
