# Backtest: neutralizacja ryzyka czynnikowego na momentum (Nasdaq-100, okna tygodniowe)

Dane: `dane/closes_5y.csv` (zamknięcia 2021-10-18…2026-10-16, dzisiejszy skład NDX-100 → survivorship bias). Okna: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia. Sygnał 6M: 2022-04-29…, 233 okien; sygnał 12M−1M: 2022-11-18…, 204 okien. Uniwersum = spółki z pełną historią sygnału (i 121 sesji do β) na D0; indeksy/ETF wyłączone; pojedyncze braki odczytu (≤2 sesje) uzupełnione poprzednim zamknięciem. Branże: `data/tv-screen-2026-W8.json` (industry/sector TV; brak w screenie: KHC, WBD → przypisane ręcznie). Grupa branżowa = industry o ≥4 spółkach w uniwersum, inaczej sector; grupy <3 → „Pozostałe” (nie biorą udziału w rankingu wewnątrz grupy); liczba grup na oknie: 15–16.

Konwencje: spread_pp = Σ wᵢ·rᵢ (wagi ze znakiem, long +, short −) = long_pp + short_pp + (W_L − W_S)·r_NDX; dla równych wag 5/5 to dokładnie „śr. 5 long − śr. 5 short” względem ^NDX. Kolumna „śr. NDX-skł.” = średni składnik (W_L − W_S)·r_NDX (≠0 tylko przy stronach nierównych dolarowo: d_rp, e_beta, cd, cde, ade). Koszty: 0.1% × Σ|Δw|/2 na rotację (pełna rotacja równych wag = 0,20 pp) + 6.0%/rok na gross (0.231 pp/tydz. przy gross 200%, 0.277 przy 240%). σ60 = odchylenie dziennych zwrotów z 60 sesji do D0; β = OLS 120 sesji vs ^NDX (przycięta do [0,2; 3]). t = śr./σ·√n; Sharpe = śr./σ·√52 (brutto); „netto t” liczone na serii po kosztach.

## Warianty

| kod | definicja |
|---|---|
| none | TOP5/BOTTOM5 wg momentum relatywnego (bez neutralizacji; = ref_mom6 z bt_odwrocenie.py) |
| a_branza | (a) ranking WEWNĄTRZ grupy branżowej (momentum − średnia grupy); maks. 1 long i 1 short z grupy; równe wagi |
| b_pary | (b) 5 par z tej samej grupy (≥3 spółki): grupy o największej różnicy najlepsza−najgorsza; long = najlepsza, short = najgorsza |
| c_blok | (c) TOP5/BOTTOM5 z limitem ≤2 long z bloku SEMI = industry {Computer Peripherals, Electronic Production Equipment, Semiconductors} i ≤2 short z bloku DEF = sector {Communications, Consumer Non-Durables, Utilities}; nadmiar zastępuje następna spółka z rankingu |
| c2_blok_roz | jak c, blok SEMI rozszerzony o AMAT, LITE, LRCX (semicap w TV = Industrial Machinery, LITE = Electrical Products) |
| d_rp | (d) skład none, wagi 10 nóg ∝ 1/σ60, Σ\|w\| = 240% (dosłownie wg zadania: strony NIE są równe dolarowo) |
| d2_rp_strony | (d′) wagi ∝ 1/σ60 osobno w każdej stronie, każda strona = 120% (dolarowo neutralny) |
| e_beta | (e) skład none, równe wagi w stronie, strony przeskalowane tak, by Σβ_L = Σβ_S, gross 200% |
| cd | skład c_blok + wagi d_rp |
| cde | skład c_blok, wagi ∝ 1/σ, strony przeskalowane do Σwβ_L = Σwβ_S, gross 240% |
| ade | skład a_branza, wagi ∝ 1/σ, Σwβ równe, gross 240% |

## Sygnał: momentum 6M (126 sesji, bez ostatnich 5)

**Baseline (2000 losowych koszyków 5/5 równych wag na każdym z 233 okien):** σ spreadu losowego **3.37 pp**, p5 -5.39 / p95 5.41 pp, średnia 0.00; σ w pojedynczym oknie (mediana) 3.04 pp. 2000 losowych STRATEGII: średnia tygodniowa p5 -0.365 / p95 0.360 pp, t-stat p5 -1.65 / p95 1.65, σ Sharpe'a 0.48. Dla gross 240% (warianty d/cd/cde/ade) baseline σ skaluje się ×1,2 → 4.05 pp.

### Cały okres

| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit nóg | śr. L | śr. S | śr. NDX-skł. | maxDD | najgorsze (D0) | najlepsze | gross | rotacja | koszt/tydz | **netto śr.** | netto t | netto maxDD | p(losowa ≥) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 233 | 1.01 | 0.72 | 7.42 | 2.09 | 0.99 | 58% | 53% | 1.32 | -0.31 | 0.00 | -50.6 | -25.9 (2026-02-27) | 31.8 | 200% | 20% | 0.27 | **0.74** | 1.53 | -56.1 | 0.000 |
| a_branza | 233 | 0.76 | 0.58 | 5.93 | 1.95 | 0.92 | 54% | 52% | 1.08 | -0.32 | 0.00 | -40.6 | -14.7 (2026-06-26) | 24.7 | 200% | 21% | 0.27 | **0.48** | 1.25 | -42.9 | 0.002 |
| b_pary | 233 | 1.01 | 0.74 | 5.67 | 2.72 | 1.29 | 56% | 52% | 1.10 | -0.08 | 0.00 | -37.4 | -14.4 (2026-06-26) | 20.3 | 200% | 20% | 0.27 | **0.74** | 1.99 | -39.4 | 0.000 |
| c_blok | 233 | 0.88 | 0.72 | 7.17 | 1.87 | 0.88 | 58% | 53% | 1.18 | -0.30 | 0.00 | -50.6 | -26.5 (2026-02-27) | 31.8 | 200% | 20% | 0.27 | **0.61** | 1.29 | -56.1 | 0.001 |
| c2_blok_roz | 233 | 0.67 | 0.62 | 6.84 | 1.49 | 0.70 | 57% | 52% | 0.97 | -0.30 | 0.00 | -50.6 | -19.8 (2022-07-15) | 31.8 | 200% | 20% | 0.27 | **0.40** | 0.89 | -56.1 | 0.002 |
| d_rp | 233 | 0.82 | 0.29 | 7.56 | 1.65 | 0.78 | 52% | 53% | 1.07 | -0.22 | -0.03 | -52.6 | -31.5 (2026-02-27) | 34.2 | 240% | 27% | 0.34 | **0.47** | 0.96 | -80.3 | 0.001 |
| d2_rp_strony | 233 | 1.06 | 0.84 | 8.67 | 1.87 | 0.88 | 57% | 53% | 1.34 | -0.28 | -0.00 | -54.8 | -32.0 (2026-02-27) | 37.4 | 240% | 26% | 0.34 | **0.73** | 1.28 | -69.3 | 0.000 |
| e_beta | 233 | 0.57 | 0.46 | 6.51 | 1.33 | 0.63 | 54% | 53% | 1.02 | -0.30 | -0.15 | -58.3 | -24.5 (2026-02-27) | 31.9 | 200% | 24% | 0.28 | **0.29** | 0.67 | -91.4 | 0.007 |
| cd | 233 | 0.69 | 0.35 | 7.29 | 1.45 | 0.69 | 52% | 53% | 0.92 | -0.21 | -0.02 | -51.5 | -32.1 (2026-02-27) | 34.2 | 240% | 27% | 0.34 | **0.35** | 0.74 | -81.2 | 0.002 |
| cde | 233 | 0.48 | 0.53 | 7.36 | 1.00 | 0.47 | 55% | 53% | 0.87 | -0.25 | -0.14 | -74.9 | -31.1 (2026-02-27) | 38.7 | 240% | 28% | 0.35 | **0.14** | 0.28 | -115.9 | 0.016 |
| ade | 233 | 0.23 | -0.20 | 5.34 | 0.67 | 0.31 | 48% | 52% | 0.73 | -0.38 | -0.11 | -53.3 | -13.5 (2026-06-26) | 24.6 | 240% | 26% | 0.34 | **-0.11** | -0.31 | -73.3 | 0.150 |

### Porównanie parami z `none` (te same okna)

| wariant | n | Δśr. pp (wariant − none) | t(Δ) | σ wariantu / σ none | to samo przy gross 200% | korelacja z none | p (σ wariantu < σ none, F) | wspólne nogi z none (na 10) | okna z identycznym składem |
|---|---|---|---|---|---|---|---|---|---|
| a_branza | 233 | -0.26 | -0.86 | 0.80 | 0.80 | 0.79 | 0.0003 | 5.2 | 0% |
| b_pary | 233 | -0.00 | -0.01 | 0.76 | 0.76 | 0.79 | 0.0000 | 4.9 | 0% |
| c_blok | 233 | -0.14 | -1.61 | 0.97 | 0.97 | 0.98 | 0.2996 | 9.6 | 77% |
| c2_blok_roz | 233 | -0.35 | -2.18 | 0.92 | 0.92 | 0.95 | 0.1070 | 9.4 | 74% |
| d_rp | 233 | -0.20 | -1.07 | 1.02 | 0.85 | 0.93 | 0.6073 | 10.0 | 100% |
| d2_rp_strony | 233 | 0.05 | 0.38 | 1.17 | 0.97 | 0.98 | 0.9911 | 10.0 | 100% |
| e_beta | 233 | -0.45 | -1.73 | 0.88 | 0.88 | 0.85 | 0.0230 | 10.0 | 100% |
| cd | 233 | -0.32 | -1.53 | 0.98 | 0.82 | 0.91 | 0.3897 | 9.6 | 77% |
| cde | 233 | -0.53 | -1.82 | 0.99 | 0.83 | 0.82 | 0.4470 | 9.6 | 77% |
| ade | 233 | -0.78 | -2.02 | 0.72 | 0.60 | 0.62 | 0.0000 | 5.2 | 0% |

### Wspólny okres z sygnałem 12M−1M (D0 ≥ 2022-11-18)

| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit nóg | śr. L | śr. S | śr. NDX-skł. | maxDD | najgorsze (D0) | najlepsze | gross | rotacja | koszt/tydz | **netto śr.** | netto t | netto maxDD | p(losowa ≥) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 204 | 1.26 | 0.56 | 7.33 | 2.46 | 1.24 | 57% | 53% | 1.50 | -0.24 | 0.00 | -44.9 | -25.9 (2026-02-27) | 31.8 | 200% | 20% | 0.27 | **0.99** | 1.93 | -46.6 | – |
| a_branza | 204 | 0.86 | 0.59 | 6.01 | 2.05 | 1.03 | 54% | 52% | 1.20 | -0.34 | 0.00 | -40.6 | -14.7 (2026-06-26) | 24.7 | 200% | 20% | 0.27 | **0.59** | 1.40 | -42.9 | – |
| b_pary | 204 | 1.07 | 0.67 | 5.76 | 2.66 | 1.34 | 56% | 52% | 1.21 | -0.13 | 0.00 | -37.4 | -14.4 (2026-06-26) | 20.3 | 200% | 20% | 0.27 | **0.80** | 1.99 | -39.4 | – |
| c_blok | 204 | 1.10 | 0.58 | 7.04 | 2.24 | 1.13 | 57% | 52% | 1.33 | -0.23 | 0.00 | -39.0 | -26.5 (2026-02-27) | 31.8 | 200% | 20% | 0.27 | **0.83** | 1.69 | -40.6 | – |
| c2_blok_roz | 204 | 0.87 | 0.50 | 6.66 | 1.86 | 0.94 | 56% | 51% | 1.09 | -0.23 | 0.00 | -40.2 | -19.4 (2026-02-27) | 31.8 | 200% | 20% | 0.27 | **0.60** | 1.28 | -42.2 | – |
| d_rp | 204 | 1.03 | 0.39 | 7.66 | 1.92 | 0.97 | 54% | 53% | 1.20 | -0.16 | -0.01 | -52.6 | -31.5 (2026-02-27) | 34.2 | 240% | 26% | 0.34 | **0.69** | 1.29 | -58.6 | – |
| d2_rp_strony | 204 | 1.33 | 0.83 | 8.66 | 2.19 | 1.10 | 57% | 53% | 1.51 | -0.19 | -0.00 | -54.8 | -32.0 (2026-02-27) | 37.4 | 240% | 26% | 0.34 | **0.99** | 1.63 | -58.8 | – |
| e_beta | 204 | 0.74 | 0.49 | 6.53 | 1.63 | 0.82 | 54% | 53% | 1.14 | -0.27 | -0.12 | -42.5 | -24.5 (2026-02-27) | 31.9 | 200% | 24% | 0.28 | **0.46** | 1.02 | -66.9 | – |
| cd | 204 | 0.89 | 0.43 | 7.36 | 1.73 | 0.87 | 54% | 52% | 1.04 | -0.14 | 0.00 | -51.5 | -32.1 (2026-02-27) | 34.2 | 240% | 27% | 0.34 | **0.55** | 1.07 | -59.4 | – |
| cde | 204 | 0.64 | 0.52 | 7.43 | 1.23 | 0.62 | 55% | 52% | 0.97 | -0.22 | -0.12 | -61.7 | -31.1 (2026-02-27) | 38.7 | 240% | 28% | 0.35 | **0.30** | 0.57 | -91.9 | – |
| ade | 204 | 0.31 | -0.09 | 5.43 | 0.82 | 0.41 | 50% | 52% | 0.78 | -0.39 | -0.08 | -53.3 | -13.5 (2026-06-26) | 24.6 | 240% | 26% | 0.34 | **-0.03** | -0.07 | -64.1 | – |

### Lata (po dacie D0; brutto, pp/tydz.: n / śr. / t / hit)

| wariant | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| none | 36 / -0.06 / -0.1 / 64% | 52 / -0.13 / -0.2 / 44% | 52 / 1.70 / 1.7 / 60% | 52 / 1.33 / 1.6 / 58% | 41 / 2.14 / 1.2 / 66% |
| a_branza | 36 / 0.27 / 0.3 / 53% | 52 / 0.01 / 0.0 / 54% | 52 / 1.07 / 1.5 / 54% | 52 / 0.97 / 1.1 / 54% | 41 / 1.47 / 1.0 / 56% |
| b_pary | 36 / 0.63 / 0.8 / 58% | 52 / -0.11 / -0.3 / 46% | 52 / 1.47 / 2.0 / 62% | 52 / 1.31 / 1.6 / 58% | 41 / 1.82 / 1.4 / 59% |
| c_blok | 36 / -0.06 / -0.1 / 64% | 52 / -0.10 / -0.2 / 46% | 52 / 1.66 / 1.7 / 60% | 52 / 1.08 / 1.3 / 58% | 41 / 1.69 / 1.0 / 66% |
| c2_blok_roz | 36 / -0.06 / -0.1 / 64% | 52 / -0.11 / -0.2 / 46% | 52 / 1.66 / 1.7 / 60% | 52 / 0.75 / 0.9 / 58% | 41 / 0.94 / 0.6 / 59% |
| d_rp | 36 / -0.08 / -0.1 / 47% | 52 / -0.27 / -0.4 / 44% | 52 / 1.27 / 1.3 / 52% | 52 / 1.56 / 1.9 / 56% | 41 / 1.45 / 0.7 / 63% |
| d2_rp_strony | 36 / -0.12 / -0.1 / 61% | 52 / -0.07 / -0.1 / 42% | 52 / 1.50 / 1.4 / 54% | 52 / 1.64 / 1.6 / 63% | 41 / 2.26 / 1.0 / 66% |
| e_beta | 36 / -0.07 / -0.1 / 56% | 52 / -0.65 / -1.1 / 48% | 52 / 1.35 / 1.5 / 52% | 52 / 1.18 / 1.6 / 56% | 41 / 0.89 / 0.6 / 61% |
| cd | 36 / -0.08 / -0.1 / 47% | 52 / -0.23 / -0.4 / 46% | 52 / 1.22 / 1.3 / 52% | 52 / 1.34 / 1.7 / 54% | 41 / 1.05 / 0.6 / 63% |
| cde | 36 / -0.06 / -0.1 / 58% | 52 / -0.73 / -1.1 / 48% | 52 / 1.22 / 1.2 / 48% | 52 / 1.32 / 1.6 / 60% | 41 / 0.50 / 0.3 / 61% |
| ade | 36 / -0.09 / -0.1 / 47% | 52 / -0.15 / -0.3 / 48% | 52 / 0.69 / 1.0 / 50% | 52 / 0.88 / 1.1 / 54% | 41 / -0.40 / -0.3 / 41% |

### Reżimy na D0 (brutto: n / śr. / σ / t)

| wariant | VIX>20 | VIX≤20 | NDX<MA200 | NDX>MA200 | 1. połowa | 2. połowa |
|---|---|---|---|---|---|---|
| none | 73 / 2.37 / 7.8 / 2.6 | 160 / 0.40 / 7.2 / 0.7 | 53 / 0.69 / 6.9 / 0.7 | 180 / 1.11 / 7.6 / 2.0 | 116 / 0.06 / 5.5 / 0.1 | 117 / 1.96 / 8.8 / 2.4 |
| a_branza | 73 / 2.03 / 6.2 / 2.8 | 160 / 0.18 / 5.7 / 0.4 | 53 / 0.41 / 5.1 / 0.6 | 180 / 0.86 / 6.2 / 1.9 | 116 / 0.02 / 4.1 / 0.1 | 117 / 1.48 / 7.3 / 2.2 |
| b_pary | 73 / 2.29 / 5.6 / 3.5 | 160 / 0.43 / 5.6 / 1.0 | 53 / 0.91 / 4.6 / 1.4 | 180 / 1.04 / 5.9 / 2.3 | 116 / 0.17 / 4.1 / 0.4 | 117 / 1.85 / 6.8 / 2.9 |
| c_blok | 73 / 2.25 / 7.6 / 2.5 | 160 / 0.25 / 6.9 / 0.5 | 53 / 0.63 / 6.8 / 0.7 | 180 / 0.95 / 7.3 / 1.7 | 116 / 0.06 / 5.5 / 0.1 | 117 / 1.69 / 8.5 / 2.2 |
| c2_blok_roz | 73 / 1.93 / 7.3 / 2.3 | 160 / 0.09 / 6.6 / 0.2 | 53 / 0.53 / 6.7 / 0.6 | 180 / 0.71 / 6.9 / 1.4 | 116 / 0.06 / 5.5 / 0.1 | 117 / 1.28 / 7.9 / 1.7 |
| d_rp | 73 / 2.69 / 7.9 / 2.9 | 160 / -0.04 / 7.3 / -0.1 | 53 / 1.02 / 6.6 / 1.1 | 180 / 0.76 / 7.8 / 1.3 | 116 / -0.21 / 5.2 / -0.4 | 117 / 1.83 / 9.3 / 2.1 |
| d2_rp_strony | 73 / 2.94 / 8.9 / 2.8 | 160 / 0.21 / 8.5 / 0.3 | 53 / 0.85 / 7.8 / 0.8 | 180 / 1.13 / 8.9 / 1.7 | 116 / -0.02 / 6.2 / -0.0 | 117 / 2.14 / 10.5 / 2.2 |
| e_beta | 73 / 1.78 / 7.1 / 2.1 | 160 / 0.01 / 6.1 / 0.0 | 53 / 0.72 / 6.0 / 0.9 | 180 / 0.52 / 6.7 / 1.0 | 116 / -0.36 / 4.8 / -0.8 | 117 / 1.49 / 7.7 / 2.1 |
| cd | 73 / 2.59 / 7.7 / 2.9 | 160 / -0.17 / 6.9 / -0.3 | 53 / 0.96 / 6.5 / 1.1 | 180 / 0.62 / 7.5 / 1.1 | 116 / -0.22 / 5.1 / -0.5 | 117 / 1.60 / 8.9 / 2.0 |
| cde | 73 / 2.24 / 8.2 / 2.3 | 160 / -0.32 / 6.8 / -0.6 | 53 / 0.94 / 6.8 / 1.0 | 180 / 0.35 / 7.5 / 0.6 | 116 / -0.52 / 5.2 / -1.1 | 117 / 1.47 / 8.9 / 1.8 |
| ade | 73 / 1.48 / 5.8 / 2.2 | 160 / -0.34 / 5.1 / -0.8 | 53 / 0.04 / 4.7 / 0.1 | 180 / 0.29 / 5.5 / 0.7 | 116 / -0.23 / 3.9 / -0.6 | 117 / 0.70 / 6.4 / 1.2 |

## Sygnał: momentum 12M−1M (252 sesje, bez ostatnich 21)

**Baseline (2000 losowych koszyków 5/5 równych wag na każdym z 204 okien):** σ spreadu losowego **3.32 pp**, p5 -5.29 / p95 5.27 pp, średnia -0.01; σ w pojedynczym oknie (mediana) 2.95 pp. 2000 losowych STRATEGII: średnia tygodniowa p5 -0.388 / p95 0.347 pp, t-stat p5 -1.71 / p95 1.52, σ Sharpe'a 0.50. Dla gross 240% (warianty d/cd/cde/ade) baseline σ skaluje się ×1,2 → 3.99 pp.

### Cały okres

| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit nóg | śr. L | śr. S | śr. NDX-skł. | maxDD | najgorsze (D0) | najlepsze | gross | rotacja | koszt/tydz | **netto śr.** | netto t | netto maxDD | p(losowa ≥) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 204 | 0.58 | 0.59 | 7.27 | 1.14 | 0.58 | 55% | 53% | 1.13 | -0.55 | 0.00 | -99.3 | -25.5 (2026-06-26) | 20.6 | 200% | 14% | 0.26 | **0.32** | 0.63 | -108.3 | 0.004 |
| a_branza | 204 | 0.98 | 0.85 | 5.85 | 2.39 | 1.21 | 56% | 53% | 1.21 | -0.23 | 0.00 | -56.6 | -17.6 (2026-10-09) | 20.5 | 200% | 15% | 0.26 | **0.72** | 1.75 | -68.6 | 0.000 |
| b_pary | 204 | 0.91 | 0.67 | 5.77 | 2.24 | 1.13 | 55% | 52% | 1.11 | -0.20 | 0.00 | -46.9 | -17.6 (2026-10-09) | 20.9 | 200% | 17% | 0.26 | **0.64** | 1.59 | -56.1 | 0.000 |
| c_blok | 204 | 0.56 | 0.59 | 7.20 | 1.10 | 0.56 | 56% | 52% | 1.11 | -0.55 | 0.00 | -99.3 | -25.1 (2026-07-10) | 21.3 | 200% | 14% | 0.26 | **0.30** | 0.59 | -108.3 | 0.006 |
| c2_blok_roz | 204 | 0.60 | 0.58 | 6.83 | 1.26 | 0.64 | 57% | 52% | 1.16 | -0.55 | 0.00 | -99.3 | -23.2 (2026-07-10) | 20.6 | 200% | 14% | 0.26 | **0.34** | 0.72 | -108.3 | 0.002 |
| d_rp | 204 | 0.16 | 0.33 | 7.75 | 0.29 | 0.15 | 52% | 53% | 0.84 | -0.57 | -0.12 | -94.1 | -30.1 (2026-07-10) | 21.2 | 240% | 20% | 0.32 | **-0.17** | -0.31 | -122.7 | 0.247 |
| d2_rp_strony | 204 | 0.67 | 0.92 | 8.78 | 1.09 | 0.55 | 57% | 53% | 1.28 | -0.60 | 0.00 | -108.3 | -31.8 (2026-07-10) | 23.2 | 240% | 19% | 0.32 | **0.35** | 0.57 | -119.6 | 0.001 |
| e_beta | 204 | -0.32 | -0.39 | 6.37 | -0.71 | -0.36 | 48% | 53% | 0.50 | -0.60 | -0.22 | -112.9 | -26.7 (2026-06-26) | 18.2 | 200% | 18% | 0.27 | **-0.58** | -1.31 | -137.8 | 0.910 |
| cd | 204 | 0.14 | 0.45 | 7.64 | 0.26 | 0.13 | 52% | 52% | 0.83 | -0.57 | -0.13 | -92.3 | -30.3 (2026-07-10) | 22.8 | 240% | 20% | 0.33 | **-0.19** | -0.35 | -120.8 | 0.278 |
| cde | 204 | -0.46 | -0.15 | 7.34 | -0.90 | -0.45 | 49% | 52% | 0.47 | -0.64 | -0.29 | -121.7 | -28.1 (2026-06-26) | 21.5 | 240% | 22% | 0.33 | **-0.79** | -1.53 | -168.4 | 0.975 |
| ade | 204 | 0.25 | -0.12 | 4.91 | 0.73 | 0.37 | 49% | 53% | 0.74 | -0.26 | -0.23 | -48.3 | -11.6 (2026-01-02) | 14.9 | 240% | 21% | 0.33 | **-0.08** | -0.22 | -76.3 | 0.127 |

### Porównanie parami z `none` (te same okna)

| wariant | n | Δśr. pp (wariant − none) | t(Δ) | σ wariantu / σ none | to samo przy gross 200% | korelacja z none | p (σ wariantu < σ none, F) | wspólne nogi z none (na 10) | okna z identycznym składem |
|---|---|---|---|---|---|---|---|---|---|
| a_branza | 204 | 0.40 | 1.31 | 0.80 | 0.80 | 0.80 | 0.0010 | 5.4 | 0% |
| b_pary | 204 | 0.32 | 1.05 | 0.79 | 0.79 | 0.80 | 0.0005 | 5.0 | 0% |
| c_blok | 204 | -0.02 | -0.29 | 0.99 | 0.99 | 0.99 | 0.4429 | 9.7 | 80% |
| c2_blok_roz | 204 | 0.02 | 0.13 | 0.94 | 0.94 | 0.94 | 0.1831 | 9.5 | 77% |
| d_rp | 204 | -0.42 | -2.40 | 1.07 | 0.89 | 0.95 | 0.8194 | 10.0 | 100% |
| d2_rp_strony | 204 | 0.09 | 0.64 | 1.21 | 1.01 | 0.98 | 0.9963 | 10.0 | 100% |
| e_beta | 204 | -0.90 | -3.21 | 0.88 | 0.88 | 0.84 | 0.0300 | 10.0 | 100% |
| cd | 204 | -0.44 | -2.41 | 1.05 | 0.87 | 0.94 | 0.7558 | 9.7 | 80% |
| cde | 204 | -1.04 | -3.49 | 1.01 | 0.84 | 0.83 | 0.5515 | 9.7 | 80% |
| ade | 204 | -0.33 | -0.79 | 0.68 | 0.56 | 0.58 | 0.0000 | 5.4 | 0% |

### Lata (po dacie D0; brutto, pp/tydz.: n / śr. / t / hit)

| wariant | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| none | 7 / 1.22 / 0.9 / 57% | 52 / -1.58 / -2.4 / 37% | 52 / 1.64 / 1.9 / 69% | 52 / 0.66 / 0.7 / 58% | 41 / 1.77 / 1.0 / 59% |
| a_branza | 7 / 1.49 / 1.3 / 57% | 52 / -1.04 / -2.1 / 40% | 52 / 1.99 / 3.0 / 63% | 52 / 1.17 / 1.6 / 58% | 41 / 1.91 / 1.3 / 63% |
| b_pary | 7 / 1.44 / 1.1 / 71% | 52 / -0.75 / -1.6 / 40% | 52 / 1.65 / 2.6 / 60% | 52 / 0.79 / 1.1 / 58% | 41 / 2.12 / 1.5 / 63% |
| c_blok | 7 / 1.22 / 0.9 / 57% | 52 / -1.58 / -2.4 / 37% | 52 / 1.64 / 1.9 / 69% | 52 / 0.66 / 0.7 / 58% | 41 / 1.65 / 1.0 / 61% |
| c2_blok_roz | 7 / 1.22 / 0.9 / 57% | 52 / -1.58 / -2.4 / 37% | 52 / 1.64 / 1.9 / 69% | 52 / 0.67 / 0.7 / 58% | 41 / 1.88 / 1.3 / 66% |
| d_rp | 7 / 0.37 / 0.6 / 71% | 52 / -1.30 / -2.1 / 38% | 52 / 0.94 / 1.0 / 62% | 52 / 0.21 / 0.2 / 48% | 41 / 0.91 / 0.5 / 59% |
| d2_rp_strony | 7 / 1.65 / 1.1 / 71% | 52 / -1.70 / -2.2 / 38% | 52 / 1.92 / 1.8 / 67% | 52 / 0.64 / 0.6 / 60% | 41 / 1.98 / 0.9 / 61% |
| e_beta | 7 / -0.18 / -0.3 / 57% | 52 / -1.26 / -2.1 / 35% | 52 / 0.06 / 0.1 / 52% | 52 / 0.01 / 0.0 / 50% | 41 / -0.04 / -0.0 / 56% |
| cd | 7 / 0.37 / 0.6 / 71% | 52 / -1.30 / -2.1 / 38% | 52 / 0.97 / 1.0 / 60% | 52 / 0.21 / 0.2 / 48% | 41 / 0.77 / 0.4 / 63% |
| cde | 7 / -0.12 / -0.1 / 43% | 52 / -1.30 / -2.1 / 40% | 52 / -0.13 / -0.2 / 56% | 52 / -0.09 / -0.1 / 46% | 41 / -0.33 / -0.2 / 54% |
| ade | 7 / 0.39 / 0.5 / 29% | 52 / -0.80 / -1.7 / 44% | 52 / 1.05 / 1.8 / 52% | 52 / 0.78 / 1.1 / 52% | 41 / -0.14 / -0.1 / 51% |

### Reżimy na D0 (brutto: n / śr. / σ / t)

| wariant | VIX>20 | VIX≤20 | NDX<MA200 | NDX>MA200 | 1. połowa | 2. połowa |
|---|---|---|---|---|---|---|
| none | 45 / 3.19 / 6.5 / 3.3 | 159 / -0.16 / 7.3 / -0.3 | 24 / 1.32 / 6.3 / 1.0 | 180 / 0.48 / 7.4 / 0.9 | 102 / -0.39 / 5.4 / -0.7 | 102 / 1.55 / 8.7 / 1.8 |
| a_branza | 45 / 3.27 / 6.4 / 3.4 | 159 / 0.33 / 5.5 / 0.7 | 24 / 1.37 / 5.8 / 1.2 | 180 / 0.93 / 5.9 / 2.1 | 102 / 0.19 / 3.9 / 0.5 | 102 / 1.77 / 7.2 / 2.5 |
| b_pary | 45 / 3.37 / 6.1 / 3.7 | 159 / 0.21 / 5.5 / 0.5 | 24 / 1.17 / 6.0 / 1.0 | 180 / 0.87 / 5.8 / 2.0 | 102 / 0.20 / 3.8 / 0.5 | 102 / 1.61 / 7.2 / 2.3 |
| c_blok | 45 / 3.17 / 6.5 / 3.3 | 159 / -0.19 / 7.2 / -0.3 | 24 / 1.56 / 6.7 / 1.1 | 180 / 0.42 / 7.3 / 0.8 | 102 / -0.39 / 5.4 / -0.7 | 102 / 1.50 / 8.6 / 1.8 |
| c2_blok_roz | 45 / 2.94 / 6.3 / 3.1 | 159 / -0.06 / 6.8 / -0.1 | 24 / 1.38 / 6.5 / 1.0 | 180 / 0.50 / 6.9 / 1.0 | 102 / -0.39 / 5.4 / -0.7 | 102 / 1.60 / 7.9 / 2.0 |
| d_rp | 45 / 3.00 / 6.7 / 3.0 | 159 / -0.65 / 7.9 / -1.0 | 24 / 1.64 / 6.3 / 1.3 | 180 / -0.04 / 7.9 / -0.1 | 102 / -0.59 / 5.4 / -1.1 | 102 / 0.90 / 9.5 / 1.0 |
| d2_rp_strony | 45 / 3.90 / 7.8 / 3.3 | 159 / -0.24 / 8.8 / -0.3 | 24 / 1.42 / 7.7 / 0.9 | 180 / 0.57 / 8.9 / 0.9 | 102 / -0.33 / 6.4 / -0.5 | 102 / 1.68 / 10.6 / 1.6 |
| e_beta | 45 / 1.65 / 5.6 / 2.0 | 159 / -0.88 / 6.5 / -1.7 | 24 / 1.63 / 5.0 / 1.6 | 180 / -0.58 / 6.5 / -1.2 | 102 / -0.96 / 4.5 / -2.1 | 102 / 0.32 / 7.8 / 0.4 |
| cd | 45 / 3.01 / 6.7 / 3.0 | 159 / -0.67 / 7.7 / -1.1 | 24 / 1.79 / 6.6 / 1.3 | 180 / -0.08 / 7.8 / -0.1 | 102 / -0.57 / 5.5 / -1.1 | 102 / 0.84 / 9.3 / 0.9 |
| cde | 45 / 1.95 / 6.5 / 2.0 | 159 / -1.14 / 7.4 / -1.9 | 24 / 1.89 / 6.5 / 1.4 | 180 / -0.77 / 7.4 / -1.4 | 102 / -1.07 / 5.0 / -2.2 | 102 / 0.15 / 9.1 / 0.2 |
| ade | 45 / 1.89 / 4.8 / 2.6 | 159 / -0.21 / 4.9 / -0.6 | 24 / 0.52 / 3.7 / 0.7 | 180 / 0.21 / 5.1 / 0.6 | 102 / -0.11 / 3.7 / -0.3 | 102 / 0.61 / 5.9 / 1.0 |

## Ostatnie 8 okien: składy none / b_pary (6M) i a_branza (12M−1M)

| D0 | D5 | NDX pp | none 6M (spread) | b_pary 6M (spread) | a_branza 12M−1M (spread) |
|---|---|---|---|---|---|
| 2026-08-21 | 2026-08-28 | 0.4 | L NBIS MRVL SNDK ALAB AMD / S ALNY MSTR TSLA CMCSA ISRG (**-4.5**) | L NBIS MRVL SNDK MRNA ABNB / S APP NXPI AAPL ALNY CMCSA (**-6.3**) | L SNDK MU LITE NBIS ROST / S AXON HON MCHP INTU TRI (**-1.3**) |
| 2026-08-28 | 2026-09-04 | 0.4 | L MRVL MRNA SNDK PANW AMD / S ALNY APP ISRG META PDD (**0.8**) | L MRNA MRVL PANW SNDK ABNB / S ALNY NXPI APP RKLB CMCSA (**-0.2**) | L SNDK MU LITE NBIS ROST / S AXON HON QCOM INTU ALNY (**8.7**) |
| 2026-09-04 | 2026-09-11 | -0.6 | L MRVL MRNA PANW ALAB CRWD / S ALNY APP ISRG FER WMT (**0.5**) | L MRNA PANW MRVL SNDK FTNT / S ALNY APP MCHP RKLB PAYX (**2.0**) | L SNDK MU LITE NBIS GOOGL / S AXON HON QCOM INTU ALNY (**1.4**) |
| 2026-09-11 | 2026-09-18 | 0.9 | L MRNA MRVL SNDK MU ALAB / S APP INTU ISRG PDD ALNY (**7.0**) | L MRNA SNDK MRVL NBIS FTNT / S ALNY RKLB NXPI APP PAYX (**7.6**) | L SNDK MU LITE NBIS MRNA / S AXON HON QCOM ALNY INTU (**7.4**) |
| 2026-09-18 | 2026-09-25 | 3.3 | L MRNA MRVL SNDK AMD ALAB / S APP INTU PDD ISRG ALNY (**13.7**) | L MRNA SNDK MRVL NBIS LITE / S ALNY RKLB AVGO APP HON (**3.8**) | L SNDK MU MRNA LITE NBIS / S AXON HON ALNY NXPI INTU (**8.2**) |
| 2026-09-25 | 2026-10-02 | 0.7 | L MRNA MRVL AMD ALAB INTC / S INTU APP ALNY NFLX CMCSA (**5.3**) | L MRNA MRVL CRWD SNDK FTNT / S ALNY MPWR INTU AXON PAYX (**4.2**) | L SNDK MU LITE MRNA NBIS / S AXON HON ALNY NXPI INTU (**4.5**) |
| 2026-10-02 | 2026-10-09 | 0.2 | L MRNA ALAB AMD MU SNDK / S INTU NFLX CMCSA PDD ALNY (**-4.5**) | L MRNA ALAB SNDK CRWD FTNT / S ALNY AVGO AXON INTU PAYX (**-1.1**) | L SNDK MU MRNA LITE NBIS / S AXON HON ALNY NXPI INTU (**-1.5**) |
| 2026-10-09 | 2026-10-16 | -5.5 | L MRNA ALAB MU AMD CRWD / S INTU NFLX ALNY APP PDD (**-13.5**) | L MRNA CRWD ALAB SNDK FTNT / S ALNY INTU AVGO AXON PAYX (**-13.1**) | L SNDK MU MRNA LITE NBIS / S AXON HON ALNY NXPI INTU (**-17.6**) |

## Faktyczne koszyki W4–W7 po narzuceniu (c) i (d)

Okno = D0 koszyka → sesja rozliczenia z raportu (W4: 11 sesji — rotacja przeterminowana; pozostałe 4–5 sesji). Zamiana nadmiarowych nóg: kolejne spółki z TOP15/BOTTOM15 danego raportu (w kolejności rankingu), z pominięciem oznaczonych „*” (poza koszykiem wg prerejestrowanej reguły: TSLA, INTU do 16.10, NVDA od W6) i spółek już w koszyku; limit bloku sprawdzany także dla zamienników. Wagi (d) z σ60 na D0 danego koszyka; gross 240% (dla porównania podano też równe wagi ×1,2 = gross 240%).

| tydzień | okno | sesje | NDX pp | nogi w bloku SEMI (spec / rozsz.) | nogi w bloku DEF | zamiany (c) | zamiany (c2) |
|---|---|---|---|---|---|---|---|
| 2026-W4 | 2026-09-11→2026-09-28 | 11 | 3.09 | MU AMD AVGO MRVL (4) / MU AMD AVGO MRVL LITE (5) | — (0) | L: AVGO MRVL → PANW AMAT | L: AVGO MRVL LITE → PANW CRWD META |
| 2026-W5 | 2026-09-28→2026-10-02 | 4 | 1.75 | MU AMD ALAB STX TER (5) / MU AMD ALAB STX TER (5) | PEP (1) | L: ALAB STX TER → LRCX AMAT LITE | L: ALAB STX TER → PANW |
| 2026-W6 | 2026-10-02→2026-10-09 | 5 | 0.24 | MU TER AMD (3) / MU LITE TER AMAT AMD (5) | — (0) | L: AMD → PANW | L: TER AMAT AMD → PANW CRWD SNPS |
| 2026-W7 | 2026-10-09→2026-10-16 | 5 | -5.49 | MU MRVL (2) / MU LITE MRVL (3) | PEP TMUS (2) | brak | L: MRVL → FTNT |

Wyniki (pp spreadu w oknie; „nogi+” = liczba nóg z dodatnim wkładem na 10):

| tydzień | fakt_rowne | fakt_rowne_240 | fakt_d_rp | fakt_d2_rp_strony | c_blok_rowne | c_blok_d_rp | c2_blok_roz_rowne | c2_blok_roz_d_rp |
|---|---|---|---|---|---|---|---|---|
| 2026-W4 | 13.81 (8/10) | 16.58 (8/10) | 15.94 (8/10) | 14.89 (8/10) | 18.20 (9/10) | 21.37 (9/10) | 24.17 (10/10) | 25.95 (10/10) |
| 2026-W5 | 5.95 (8/10) | 7.14 (8/10) | 6.02 (8/10) | 5.71 (8/10) | 13.05 (10/10) | 10.55 (10/10) | 6.99 (8/10) | 6.60 (8/10) |
| 2026-W6 | -5.59 (3/10) | -6.71 (3/10) | -3.75 (3/10) | -5.96 (3/10) | -4.00 (4/10) | -2.33 (4/10) | 0.48 (6/10) | 1.26 (6/10) |
| 2026-W7 | -21.15 (0/10) | -25.38 (0/10) | -20.31 (0/10) | -24.34 (0/10) | -21.15 (0/10) | -20.31 (0/10) | -20.33 (0/10) | -20.22 (0/10) |
| **suma** | **-6.97** | **-8.37** | **-2.10** | **-9.71** | **6.11** | **9.27** | **11.29** | **13.59** |

Składy po (c) i wagi (d):

- **2026-W4**: fakt L MU AMD AVGO MRVL LITE / S INTU SBUX CMCSA APP ADSK; σ60: MU 5.85, AMD 4.34, AVGO 2.66, MRVL 5.57, LITE 6.16, INTU 2.91, SBUX 1.38, CMCSA 2.32, APP 4.36, ADSK 2.88.
  - wagi d_rp (fakt): MU +0.13, AMD +0.17, AVGO +0.28, MRVL +0.14, LITE +0.12, INTU -0.26, SBUX -0.54, CMCSA -0.32, APP -0.17, ADSK -0.26 (W_L 0.84, W_S 1.56; składnik NDX -2.22 pp)
  - po (c): L MU AMD LITE PANW AMAT / S INTU SBUX CMCSA APP ADSK → 18.20 pp (fakt 13.81 pp)
  - po (c)+(d): 21.37 pp; wagi MU +0.13, AMD +0.18, LITE +0.12, PANW +0.21, AMAT +0.15, INTU -0.27, SBUX -0.56, CMCSA -0.33, APP -0.18, ADSK -0.27
- **2026-W5**: fakt L MU AMD ALAB STX TER / S SBUX NFLX PEP CMCSA APP; σ60: MU 4.86, AMD 4.3, ALAB 6.32, STX 4.67, TER 4.86, SBUX 1.34, NFLX 2.22, PEP 1.24, CMCSA 2.22, APP 3.96.
  - wagi d_rp (fakt): MU +0.13, AMD +0.15, ALAB +0.10, STX +0.14, TER +0.13, SBUX -0.48, NFLX -0.29, PEP -0.52, CMCSA -0.29, APP -0.16 (W_L 0.66, W_S 1.75; składnik NDX -1.91 pp)
  - po (c): L MU AMD LRCX AMAT LITE / S SBUX NFLX PEP CMCSA APP → 13.05 pp (fakt 5.95 pp)
  - po (c)+(d): 10.55 pp; wagi MU +0.13, AMD +0.15, LRCX +0.14, AMAT +0.16, LITE +0.10, SBUX -0.47, NFLX -0.28, PEP -0.51, CMCSA -0.29, APP -0.16
- **2026-W6**: fakt L MU LITE TER AMAT AMD / S APP NFLX PAYX CMCSA SBUX; σ60: MU 4.81, LITE 6.02, TER 4.78, AMAT 4.02, AMD 4.08, APP 3.99, NFLX 2.25, PAYX 2.16, CMCSA 2.21, SBUX 1.27.
  - wagi d_rp (fakt): MU +0.14, LITE +0.12, TER +0.14, AMAT +0.17, AMD +0.17, APP -0.17, NFLX -0.31, PAYX -0.32, CMCSA -0.31, SBUX -0.54 (W_L 0.75, W_S 1.66; składnik NDX -0.22 pp)
  - po (c): L MU LITE TER AMAT PANW / S APP NFLX PAYX CMCSA SBUX → -4.00 pp (fakt -5.59 pp)
  - po (c)+(d): -2.33 pp; wagi MU +0.14, LITE +0.11, TER +0.14, AMAT +0.17, PANW +0.18, APP -0.17, NFLX -0.31, PAYX -0.32, CMCSA -0.31, SBUX -0.54
- **2026-W7**: fakt L MU LITE MRVL PANW CSCO / S CMCSA SBUX PEP TMUS APP; σ60: MU 4.62, LITE 5.88, MRVL 4.69, PANW 3.7, CSCO 2.07, CMCSA 2.18, SBUX 1.28, PEP 1.2, TMUS 2.93, APP 3.73.
  - wagi d_rp (fakt): MU +0.13, LITE +0.10, MRVL +0.13, PANW +0.16, CSCO +0.29, CMCSA -0.27, SBUX -0.47, PEP -0.50, TMUS -0.20, APP -0.16 (W_L 0.80, W_S 1.60; składnik NDX 4.35 pp)
  - po (c): L MU LITE MRVL PANW CSCO / S CMCSA SBUX PEP TMUS APP → -21.15 pp (fakt -21.15 pp)
  - po (c)+(d): -20.31 pp; wagi MU +0.13, LITE +0.10, MRVL +0.13, PANW +0.16, CSCO +0.29, CMCSA -0.27, SBUX -0.47, PEP -0.50, TMUS -0.20, APP -0.16

## Wnioski

- **momentum 6M (126 sesji, bez ostatnich 5)**, bez neutralizacji (none): śr. 1.01 pp/tydz., σ 7.42, t 2.09, Sharpe 0.99, maxDD -50.6 pp, najgorsze okno -25.9 pp (2026-02-27); netto 0.74 pp/tydz. (netto t 1.53). Baseline σ losowego koszyka 3.37 pp — momentum ma σ ok. 2.2× wyższą niż losowy koszyk 5/5 (koncentracja czynnikowa).
  - a_branza: σ 5.93 (80% σ none przy tym samym gross), śr. 0.76, t 1.95, Sharpe 0.92, maxDD -40.6, najgorsze -14.7 (2026-06-26), hit 54%, netto śr. 0.48 (netto t 1.25), p(losowa ≥) 0.002.
  - b_pary: σ 5.67 (76% σ none przy tym samym gross), śr. 1.01, t 2.72, Sharpe 1.29, maxDD -37.4, najgorsze -14.4 (2026-06-26), hit 56%, netto śr. 0.74 (netto t 1.99), p(losowa ≥) 0.000.
  - c_blok: σ 7.17 (97% σ none przy tym samym gross), śr. 0.88, t 1.87, Sharpe 0.88, maxDD -50.6, najgorsze -26.5 (2026-02-27), hit 58%, netto śr. 0.61 (netto t 1.29), p(losowa ≥) 0.001.
  - c2_blok_roz: σ 6.84 (92% σ none przy tym samym gross), śr. 0.67, t 1.49, Sharpe 0.70, maxDD -50.6, najgorsze -19.8 (2022-07-15), hit 57%, netto śr. 0.40 (netto t 0.89), p(losowa ≥) 0.002.
  - d_rp: σ 7.56 (85% σ none przy tym samym gross), śr. 0.82, t 1.65, Sharpe 0.78, maxDD -52.6, najgorsze -31.5 (2026-02-27), hit 52%, netto śr. 0.47 (netto t 0.96), p(losowa ≥) 0.001.
  - d2_rp_strony: σ 8.67 (97% σ none przy tym samym gross), śr. 1.06, t 1.87, Sharpe 0.88, maxDD -54.8, najgorsze -32.0 (2026-02-27), hit 57%, netto śr. 0.73 (netto t 1.28), p(losowa ≥) 0.000.
  - e_beta: σ 6.51 (88% σ none przy tym samym gross), śr. 0.57, t 1.33, Sharpe 0.63, maxDD -58.3, najgorsze -24.5 (2026-02-27), hit 54%, netto śr. 0.29 (netto t 0.67), p(losowa ≥) 0.007.
  - cd: σ 7.29 (82% σ none przy tym samym gross), śr. 0.69, t 1.45, Sharpe 0.69, maxDD -51.5, najgorsze -32.1 (2026-02-27), hit 52%, netto śr. 0.35 (netto t 0.74), p(losowa ≥) 0.002.
  - cde: σ 7.36 (83% σ none przy tym samym gross), śr. 0.48, t 1.00, Sharpe 0.47, maxDD -74.9, najgorsze -31.1 (2026-02-27), hit 55%, netto śr. 0.14 (netto t 0.28), p(losowa ≥) 0.016.
  - ade: σ 5.34 (60% σ none przy tym samym gross), śr. 0.23, t 0.67, Sharpe 0.31, maxDD -53.3, najgorsze -13.5 (2026-06-26), hit 48%, netto śr. -0.11 (netto t -0.31), p(losowa ≥) 0.150.
  - Warianty z t > 2 **i** netto > 0 **i** netto t > 2: **żaden**; t > 2 i netto > 0, ale netto t ≤ 2: none, b_pary.
- **momentum 12M−1M (252 sesje, bez ostatnich 21)**, bez neutralizacji (none): śr. 0.58 pp/tydz., σ 7.27, t 1.14, Sharpe 0.58, maxDD -99.3 pp, najgorsze okno -25.5 pp (2026-06-26); netto 0.32 pp/tydz. (netto t 0.63). Baseline σ losowego koszyka 3.32 pp — momentum ma σ ok. 2.2× wyższą niż losowy koszyk 5/5 (koncentracja czynnikowa).
  - a_branza: σ 5.85 (80% σ none przy tym samym gross), śr. 0.98, t 2.39, Sharpe 1.21, maxDD -56.6, najgorsze -17.6 (2026-10-09), hit 56%, netto śr. 0.72 (netto t 1.75), p(losowa ≥) 0.000.
  - b_pary: σ 5.77 (79% σ none przy tym samym gross), śr. 0.91, t 2.24, Sharpe 1.13, maxDD -46.9, najgorsze -17.6 (2026-10-09), hit 55%, netto śr. 0.64 (netto t 1.59), p(losowa ≥) 0.000.
  - c_blok: σ 7.20 (99% σ none przy tym samym gross), śr. 0.56, t 1.10, Sharpe 0.56, maxDD -99.3, najgorsze -25.1 (2026-07-10), hit 56%, netto śr. 0.30 (netto t 0.59), p(losowa ≥) 0.006.
  - c2_blok_roz: σ 6.83 (94% σ none przy tym samym gross), śr. 0.60, t 1.26, Sharpe 0.64, maxDD -99.3, najgorsze -23.2 (2026-07-10), hit 57%, netto śr. 0.34 (netto t 0.72), p(losowa ≥) 0.002.
  - d_rp: σ 7.75 (89% σ none przy tym samym gross), śr. 0.16, t 0.29, Sharpe 0.15, maxDD -94.1, najgorsze -30.1 (2026-07-10), hit 52%, netto śr. -0.17 (netto t -0.31), p(losowa ≥) 0.247.
  - d2_rp_strony: σ 8.78 (101% σ none przy tym samym gross), śr. 0.67, t 1.09, Sharpe 0.55, maxDD -108.3, najgorsze -31.8 (2026-07-10), hit 57%, netto śr. 0.35 (netto t 0.57), p(losowa ≥) 0.001.
  - e_beta: σ 6.37 (88% σ none przy tym samym gross), śr. -0.32, t -0.71, Sharpe -0.36, maxDD -112.9, najgorsze -26.7 (2026-06-26), hit 48%, netto śr. -0.58 (netto t -1.31), p(losowa ≥) 0.910.
  - cd: σ 7.64 (87% σ none przy tym samym gross), śr. 0.14, t 0.26, Sharpe 0.13, maxDD -92.3, najgorsze -30.3 (2026-07-10), hit 52%, netto śr. -0.19 (netto t -0.35), p(losowa ≥) 0.278.
  - cde: σ 7.34 (84% σ none przy tym samym gross), śr. -0.46, t -0.90, Sharpe -0.45, maxDD -121.7, najgorsze -28.1 (2026-06-26), hit 49%, netto śr. -0.79 (netto t -1.53), p(losowa ≥) 0.975.
  - ade: σ 4.91 (56% σ none przy tym samym gross), śr. 0.25, t 0.73, Sharpe 0.37, maxDD -48.3, najgorsze -11.6 (2026-01-02), hit 49%, netto śr. -0.08 (netto t -0.22), p(losowa ≥) 0.127.
  - Warianty z t > 2 **i** netto > 0 **i** netto t > 2: **żaden**; t > 2 i netto > 0, ale netto t ≤ 2: a_branza, b_pary.
- **Interpretacja.** (1) Neutralność branżowa (a) i parowanie (b) obniżają σ spreadu o ok. 20–24% przy tym samym gross i tej samej (6M) lub wyższej (12M−1M) średniej — to jedyne konstrukcje, które statystycznie zmniejszają ryzyko (F-test p < 0,001) bez kosztu w średniej; maxDD spada z ok. −50 do −37…−41 pp, najgorsze okno z −26 do −14…−18 pp. Sharpe rośnie z ~1,0 do ~1,3 (6M) i z ~0,6 do ~1,2 (12M−1M). Ale: w obu przypadkach t brutto ≈ 2,2–2,7 i t netto 1,6–2,0 — po kosztach żaden wariant nie przekracza t > 2, a σ Sharpe'a losowej strategii to ~0,5, więc przewaga nad losowym koszykiem o Sharpe 1,3 jest ok. 2,5σ, nie więcej. (2) Limit bloku (c) w wersji z zadania prawie nie wiąże (skład identyczny z none w większości okien, korelacja 0,98) i nic nie zmienia; rozszerzony blok (c2) obniża σ o 6–8%, ale kosztem średniej (6M: Δ = −0,35 pp/tydz., t(Δ) = −2,2) — momentum w tym uniwersum to w dużej mierze blok sprzętu AI i jego ograniczanie ucina źródło zwrotu. (3) Równy udział ryzyka (d) w wersji dosłownej (10 nóg ∝ 1/σ) przenosi dolary z longów o wysokiej σ (semis) na shorty o niskiej σ (staples) → W_S ≈ 1,6–1,75 vs W_L ≈ 0,7–0,85, czyli koszyk jest netto short indeksu o 80–100% kapitału; w rynku rosnącym to ujemny składnik (W_L − W_S)·r_NDX i wyższa σ, nie niższa. Wersja po stronach (d2) nie zmienia nic poza skalą (σ/gross 0,97–1,01 σ none). (4) Neutralność beta (e) jest tym samym zakładem w innej skali: longi momentum mają β > shorty, więc wyrównanie Σβ wymaga przewagi dolarowej shortów — średnia spada o 0,45 (6M) i 0,90 pp/tydz. (12M−1M, t(Δ) = −3,2); maxDD rośnie. Kombinacje cde/ade dziedziczą tę wadę. Wniosek: przy zwrotach liczonych względem ^NDX i równych stronach koszyk jest już „neutralny” w sensie, który ma znaczenie dla tego harnessu; jawna neutralizacja β/σ bez hedgu indeksowego pogarsza wynik.
- **Faktyczne koszyki W4–W7** (suma 4 okien): równe wagi -6.97 pp (×1,2 przy gross 240%: -8.37); (d) risk parity 240%: -2.10; (c) limit bloku (spec): 6.11; (c)+(d): 9.27; (c) blok rozszerzony: 11.29; (c2)+(d): 13.59. Poprawa z (c) w W4–W6 pochodzi z zamienników (PANW, AMAT, LRCX, LITE), które akurat pobiły indeks — to cztery okna, anegdota, nie test; w W7 limit nie wiąże (2 nogi SEMI, 2 nogi DEF) i strata −21 pp zostaje. (d) na faktycznych koszykach daje +0,8…+1,8 pp w W4/W6/W7 głównie przez składnik netto-short NDX (W7: +4,35 pp przy NDX −5,5%), a nie przez trafniejsze nogi (nogi+ bez zmian).
