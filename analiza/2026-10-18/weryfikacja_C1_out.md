# Weryfikacja C1 — wyniki skryptu weryfikacja_C1.py

Dane: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv` — 1255 sesji 2021-10-18…2026-10-16, 103 kandydatów (skład dzisiejszy).


## 0. Reprodukcja twierdzenia (harness jak w fazie 2)

| wariant | n | brutto pp | σ | t | hit | netto pp | t netto | noga L | noga S | maxDD | najgorsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BAZA: 6M skip5, 5/5, piątek→piątek, pełne uniwersum | 233 | 1.01 | 7.42 | 2.09 | 58% | 0.74 | 1.53 | 1.32 | -0.31 | 50.6 | -25.9 |

Średnie uniwersum 96.0 spółek; obrót 2.01 nóg/tydz. (koszt rotacji 0.040 pp + finansowanie 0.230 pp).


Lata (brutto / netto, t):

| rok | n | brutto | t | netto | t netto |
|---|---|---|---|---|---|
| 2022 | 36 | -0.06 | -0.05 | -0.33 | -0.27 |
| 2023 | 52 | -0.13 | -0.25 | -0.41 | -0.74 |
| 2024 | 52 | 1.70 | 1.71 | 1.43 | 1.44 |
| 2025 | 52 | 1.33 | 1.56 | 1.06 | 1.24 |
| 2026 | 41 | 2.14 | 1.19 | 1.87 | 1.04 |

## (a) Usunięcie spółek krótkiej historii / dodanych po 2023

Lista krótka historia (pierwsza cena w danych > 2021-10-18): ALAB ARM CEG CRWV GEHC HONA NBIS SNDK SPCX WBD

Lista z podpowiedzi (18): ALAB ARM CRWV FER GEHC HONA NBIS SNDK SPCX MRNA PLTR MSTR AXON SHOP APP DASH TTWO WDAY

Lista szeroka (podpowiedź + przybliżone dodania 2022–2026): ALAB ALNY APP ARM AXON CCEP CEG CRWV DASH FER GEHC HONA LIN LITE MPWR MRNA MSTR NBIS PLTR RKLB ROP SHOP SNDK SPCX STX TRI TTWO WBD WDAY WDC WMT

| wariant | n | brutto pp | σ | t | hit | netto pp | t netto | noga L | noga S | maxDD | najgorsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BAZA: 6M skip5, 5/5, piątek→piątek, pełne uniwersum | 233 | 1.01 | 7.42 | 2.09 | 58% | 0.74 | 1.53 | 1.32 | -0.31 | 50.6 | -25.9 |
| bez krótkiej historii (dane) | 233 | 1.04 | 7.22 | 2.20 | 56% | 0.77 | 1.63 | 1.20 | -0.16 | 54.6 | -25.2 |
| bez listy z podpowiedzi (18) | 233 | 0.31 | 6.34 | 0.76 | 48% | 0.04 | 0.10 | 0.60 | -0.29 | 102.5 | -22.8 |
| bez listy szerokiej (31) | 233 | -0.09 | 5.47 | -0.26 | 48% | -0.37 | -1.03 | 0.16 | -0.26 | 117.8 | -19.7 |
| bez podpowiedzi + krótkiej historii | 233 | 0.32 | 6.39 | 0.75 | 48% | 0.04 | 0.10 | 0.59 | -0.28 | 107.6 | -22.8 |
| quasi point-in-time (przybliżone daty dołączenia) | 233 | 0.24 | 6.44 | 0.56 | 52% | -0.04 | -0.09 | 0.43 | -0.20 | 85.3 | -25.9 |

Lata (brutto) dla wariantów (a):

| wariant | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| bez krótkiej historii (dane) | nan | -0.09 | -0.17 | 1.51 | 1.71 | 2.11 |
| bez listy z podpowiedzi (18) | nan | -0.23 | -0.82 | 0.03 | 0.69 | 2.11 |
| bez listy szerokiej (31) | nan | -0.23 | -0.33 | -0.89 | -0.27 | 1.56 |
| bez podpowiedzi + krótkiej historii | nan | -0.33 | -0.78 | -0.09 | 0.79 | 2.18 |
| quasi point-in-time | nan | -0.06 | -0.55 | -0.62 | 0.57 | 2.14 |

### (a2) Koncentracja alfy w nazwach (baza)

Suma spreadu brutto = 236.3 pp na 233 okien. Najwięksi dawcy (pp skumulowane, liczba okien w koszyku):

| nazwa | wkład pp | okien | | nazwa | wkład pp | okien |
|---|---|---|---|---|---|---|
| APP | 67.3 | 149 | | ALAB | -34.5 | 40 |
| SNDK | 60.9 | 49 | | PDD | -14.3 | 62 |
| PLTR | 39.8 | 81 | | CRWV | -11.1 | 12 |
| LITE | 34.4 | 77 | | INTC | -10.5 | 56 |
| WDC | 33.8 | 52 | | AXON | -8.7 | 49 |
| MSTR | 29.1 | 129 | | TSLA | -8.3 | 64 |
| RKLB | 27.9 | 88 | | DASH | -7.9 | 27 |
| MRNA | 23.9 | 104 | | AMD | -7.9 | 37 |
| NVDA | 21.0 | 75 | | SHOP | -7.5 | 45 |
| NBIS | 15.2 | 30 | | PANW | -6.9 | 5 |

Leave-k-out: usuń k największych dawców z uniwersum i policz ponownie (test kruchości):

| wariant | n | brutto pp | σ | t | hit | netto pp | t netto | noga L | noga S | maxDD | najgorsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bez 1 największych dawców (APP) | 233 | 0.68 | 7.01 | 1.48 | 52% | 0.41 | 0.89 | 1.05 | -0.37 | 74.8 | -25.9 |
| bez 3 największych dawców (APP SNDK PLTR) | 233 | 0.35 | 6.67 | 0.81 | 50% | 0.08 | 0.19 | 0.75 | -0.39 | 90.6 | -25.2 |
| bez 5 największych dawców (APP SNDK PLTR LITE WDC) | 233 | 0.08 | 6.55 | 0.19 | 50% | -0.19 | -0.44 | 0.49 | -0.41 | 95.5 | -24.2 |
| bez 10 największych dawców (APP SNDK PLTR LITE WDC MSTR RKLB MRNA NVDA NBIS) | 233 | -0.43 | 6.09 | -1.07 | 46% | -0.71 | -1.77 | 0.06 | -0.49 | 165.1 | -23.9 |

Kontrola: usunięcie 5 LOSOWYCH nazw (200 powtórzeń) — rozkład średniej brutto:

średnia 0.97, 5–95% 0.66…1.13, min 0.38


## (b) Okna kotwiczone na innym dniu tygodnia (sygnał i wejście tego samego dnia)

| wariant | n | brutto pp | σ | t | hit | netto pp | t netto | noga L | noga S | maxDD | najgorsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| poniedziałek | 207 | 1.11 | 8.36 | 1.90 | 52% | 0.80 | 1.38 | 1.55 | -0.45 | 57.6 | -23.5 |
| wtorek | 233 | 1.07 | 8.23 | 1.99 | 59% | 0.80 | 1.48 | 1.44 | -0.37 | 63.6 | -31.8 |
| środa | 233 | 0.82 | 8.02 | 1.56 | 51% | 0.55 | 1.04 | 1.23 | -0.41 | 70.6 | -34.5 |
| czwartek | 233 | 0.83 | 7.55 | 1.68 | 56% | 0.56 | 1.13 | 1.21 | -0.38 | 72.3 | -32.2 |
| piątek (ostatnia sesja ≤ pt) | 233 | 1.01 | 7.42 | 2.09 | 58% | 0.74 | 1.53 | 1.32 | -0.31 | 50.6 | -25.9 |
| ostatnia sesja tygodnia (baza) | 233 | 1.01 | 7.42 | 2.09 | 58% | 0.74 | 1.53 | 1.32 | -0.31 | 50.6 | -25.9 |

Średnia po 5 kotwicach: brutto 0.97 pp (min 0.82, max 1.11), netto 0.69 pp (min 0.55), t brutto min 1.56 max 2.09.


## (c) Bootstrap blokowy (stacjonarny, 10 000 prób) — baza, brutto i netto

| seria | średnia | 95% CI średniej | SE boot | p jednostr. (H0: μ≤0) | 95% CI t |
|---|---|---|---|---|---|
| brutto, blok ~4 tyg. | 1.01 | 0.07 … 2.00 | 0.50 | 0.022 | 0.15 … 4.09 |
| brutto, blok ~8 tyg. | 1.01 | 0.08 … 2.02 | 0.50 | 0.024 | 0.18 … 3.97 |
| netto, blok ~4 tyg. | 0.74 | -0.20 … 1.73 | 0.50 | 0.072 | -0.43 … 3.53 |
| netto, blok ~8 tyg. | 0.74 | -0.19 … 1.75 | 0.50 | 0.073 | -0.42 … 3.42 |
| brutto bez listy 18, blok ~6 | 0.31 | -0.60 … 1.40 | 0.51 | 0.261 | -1.62 … 3.07 |
| netto bez listy 18, blok ~6 | 0.04 | -0.88 … 1.12 | 0.51 | 0.464 | -2.39 … 2.47 |

## (d) Podokresy 2022-04…2024-06 i 2024-07…2026-10 (baza i warianty (a))

| wariant | okres | n | brutto | σ | t | netto | t netto | noga L | noga S |
|---|---|---|---|---|---|---|---|---|---|
| baza | 2022-04…2024-06 | 114 | 0.09 | 5.57 | 0.18 | -0.18 | -0.34 | 0.50 | -0.41 |
| baza | 2024-07…2026-10 | 119 | 1.90 | 8.78 | 2.36 | 1.63 | 2.02 | 2.11 | -0.22 |
| baza | 2022-04…2023-12 | 88 | -0.11 | 5.61 | -0.18 | -0.38 | -0.63 | 0.50 | -0.60 |
| baza | 2024-01…2026-10 | 145 | 1.69 | 8.28 | 2.46 | 1.42 | 2.07 | 1.83 | -0.13 |
| bez listy 18 | 2022-04…2024-06 | 114 | -0.46 | 3.94 | -1.24 | -0.73 | -1.98 | -0.06 | -0.40 |
| bez listy 18 | 2024-07…2026-10 | 119 | 1.05 | 7.93 | 1.45 | 0.78 | 1.07 | 1.23 | -0.18 |
| bez listy 18 | 2022-04…2023-12 | 88 | -0.58 | 4.13 | -1.32 | -0.86 | -1.94 | 0.05 | -0.63 |
| bez listy 18 | 2024-01…2026-10 | 145 | 0.86 | 7.32 | 1.41 | 0.58 | 0.96 | 0.94 | -0.08 |
| quasi point-in-time | 2022-04…2024-06 | 114 | -0.27 | 4.23 | -0.69 | -0.55 | -1.39 | 0.00 | -0.28 |
| quasi point-in-time | 2024-07…2026-10 | 119 | 0.73 | 8.00 | 0.99 | 0.45 | 0.61 | 0.85 | -0.12 |
| quasi point-in-time | 2022-04…2023-12 | 88 | -0.35 | 4.12 | -0.79 | -0.62 | -1.42 | 0.08 | -0.43 |
| quasi point-in-time | 2024-01…2026-10 | 145 | 0.59 | 7.51 | 0.95 | 0.32 | 0.51 | 0.65 | -0.06 |
| bez listy szerokiej | 2022-04…2024-06 | 114 | -0.21 | 4.09 | -0.54 | -0.48 | -1.26 | 0.09 | -0.30 |
| bez listy szerokiej | 2024-07…2026-10 | 119 | 0.02 | 6.54 | 0.03 | -0.26 | -0.43 | 0.24 | -0.22 |
| bez listy szerokiej | 2022-04…2023-12 | 88 | -0.29 | 4.23 | -0.65 | -0.57 | -1.26 | 0.19 | -0.48 |
| bez listy szerokiej | 2024-01…2026-10 | 145 | 0.03 | 6.11 | 0.05 | -0.25 | -0.49 | 0.15 | -0.12 |

Welch t różnicy (2. okres − 1. okres) dla bazy: 1.88 (różnica 1.81 pp/tydz.).


## (e) Wrażliwość: skip 0/5/21 sesji × 4/4, 5/5, 7/7 nóg (piątek→piątek, pełne uniwersum)

| skip | nogi | n | brutto | σ | t | netto | t netto | 2022-04…2024-06 | 2024-07…2026-10 | bez listy 18: brutto / t / netto |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 4/4 | 234 | 1.16 | 8.27 | 2.14 | 0.88 | 1.64 | 0.03 | 2.25 | 0.35 / 0.79 / 0.07 |
| 0 | 5/5 | 234 | 1.01 | 7.57 | 2.03 | 0.73 | 1.48 | 0.09 | 1.89 | 0.28 / 0.68 / 0.01 |
| 0 | 7/7 | 234 | 0.90 | 6.88 | 1.99 | 0.63 | 1.40 | 0.14 | 1.63 | 0.36 / 0.95 / 0.09 |
| 5 | 4/4 | 233 | 1.29 | 7.97 | 2.47 | 1.02 | 1.95 | 0.28 | 2.26 | 0.48 / 1.12 / 0.21 |
| 5 | 5/5 | 233 | 1.01 | 7.42 | 2.09 | 0.74 | 1.53 | 0.09 | 1.90 | 0.31 / 0.76 / 0.04 |
| 5 | 7/7 | 233 | 0.71 | 6.68 | 1.62 | 0.44 | 1.01 | -0.06 | 1.45 | 0.31 / 0.82 / 0.03 |
| 21 | 4/4 | 230 | 1.05 | 7.58 | 2.10 | 0.78 | 1.56 | -0.06 | 2.09 | 0.45 / 1.04 / 0.17 |
| 21 | 5/5 | 230 | 1.02 | 7.09 | 2.19 | 0.75 | 1.61 | -0.13 | 2.10 | 0.37 / 0.89 / 0.09 |
| 21 | 7/7 | 230 | 0.66 | 6.43 | 1.56 | 0.40 | 0.93 | -0.24 | 1.51 | 0.37 / 0.98 / 0.10 |

Siatka 9 wariantów: t brutto 1.56…2.47 (mediana 2.09), netto 0.40…1.02 pp; bez listy 18: t brutto 0.68…1.12.


## (f) Dodatkowo: beta spreadu do ^NDX i warunkowo VIX (baza)

Regresja spread ~ ^NDX tyg.: alfa 0.93 pp, beta 0.22, r 0.09 (n=233).

- VIX>20: n=73, brutto 2.37 (t 2.60), netto 2.10.
- VIX≤20: n=160, brutto 0.40 (t 0.70), netto 0.13.
