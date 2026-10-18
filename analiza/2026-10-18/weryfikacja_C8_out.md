# Weryfikacja C8 — bramka reżimu w jednostkach kapitału (ALLOC 0,24, kill 0,75×szczyt)

Okna: 234 (D0 2022-04-22 → D5 2026-10-16), koszyki mom6M z fazy 2 (TOP5/BOTTOM5 6M skip 0, równe wagi). Dzienny zwrot kapitału = 0,24 × g × (Σ r_long − Σ r_short) − finansowanie 6%/rok × gross(2,4·g) − 0,10% × nominał za zmienioną nogę/zmianę gross. Kill switch: kapitał < 0,75 × kroczący szczyt (sprawdzany na zamknięciach), potem płasko. Kapitał startowy 100 (umowny).

Kontrola: korelacja tygodniowego zwrotu kapitału (brutto, bez kill) z 1,2×spread_pp = 0.9967; śr. 1.173 vs 1.206 pp kapitału.


## TEST 1–2. Pełna ścieżka: maxDD kapitału, czas odrobienia, Sharpe netto z finansowaniem ∝ gross

| wariant | śr. gross | kapitał końc. bez kill | maxDD kap. % (bez kill) | szczyt→dołek ses. | odrobienie ses. | CAGR % | Sharpe netto (tyg.) | t netto | śr. tyg. % | σ tyg. % | kapitał końc. Z KILL | kill (data) | koszt fin. łącznie | koszt rot. łącznie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bez bramki | 100% | 278.7 | 69.3 | 58 | nie odrobiono | 25.6 | 0.67 | 1.42 | 0.85 | 9.13 | 85.0 | 2022-06-23 | 87.9 | 15.9 |
| bramka z histerezą (odczyt D0, jak faza 2) | 74% | 236.4 | 69.5 | 58 | nie odrobiono | 21.1 | 0.61 | 1.30 | 0.69 | 8.13 | 95.8 | 2024-01-05 | 80.0 | 17.7 |
| bramka surowa (odczyt D0) | 76% | 285.3 | 69.3 | 58 | nie odrobiono | 26.2 | 0.68 | 1.45 | 0.78 | 8.17 | 101.6 | 2024-01-05 | 92.9 | 21.0 |
| tylko P2→0 (P1 pełny gross) | 79% | 318.2 | 69.3 | 58 | nie odrobiono | 29.3 | 0.72 | 1.52 | 0.84 | 8.45 | 90.3 | 2024-01-05 | 93.1 | 18.4 |
| bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji) | 74% | 250.8 | 71.7 | 58 | nie odrobiono | 22.7 | 0.64 | 1.35 | 0.72 | 8.20 | 105.5 | 2024-01-05 | 89.9 | 20.1 |
| bramka surowa DZIENNA | 77% | 345.4 | 71.7 | 58 | nie odrobiono | 31.7 | 0.75 | 1.60 | 0.87 | 8.33 | 107.7 | 2024-01-05 | 110.9 | 27.2 |

Epizody przebicia −25% od kroczącego szczytu na ścieżce BEZ kill (= ile razy kill switch strzeliłby, gdyby po każdym strzale wznawiać od bieżącego kapitału jako nowego szczytu — przybliżenie):

| wariant | liczba epizodów | daty pierwszej sesji |
|---|---|---|
| bez bramki | 4 | 2022-06-23, 2025-02-25, 2026-03-03, 2026-07-01 |
| bramka z histerezą (odczyt D0, jak faza 2) | 4 | 2024-01-05, 2025-02-25, 2026-03-03, 2026-07-01 |
| bramka surowa (odczyt D0) | 4 | 2024-01-05, 2025-02-25, 2026-03-03, 2026-07-01 |
| tylko P2→0 (P1 pełny gross) | 4 | 2024-01-05, 2025-02-25, 2026-03-03, 2026-07-01 |
| bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji) | 4 | 2024-01-05, 2025-02-25, 2026-03-03, 2026-07-01 |
| bramka surowa DZIENNA | 4 | 2024-01-05, 2025-02-25, 2026-03-03, 2026-07-01 |

## TEST 4. P(kill) — okna kroczące 12 i 26 tygodni (start kapitału 100 = szczyt), ALLOC 0,24

| wariant | okna 12 tyg. z killem | % | 5. pct min. kapitału (12 t.) | mediana min. | okna 26 tyg. z killem | % |
|---|---|---|---|---|---|---|
| bez bramki | 94/223 | 42.2 | 73.8 | 88.8 | 150/209 | 71.8 |
| bramka z histerezą (odczyt D0, jak faza 2) | 70/223 | 31.4 | 74.7 | 93.9 | 112/209 | 53.6 |
| bramka surowa (odczyt D0) | 70/223 | 31.4 | 74.7 | 93.5 | 112/209 | 53.6 |
| tylko P2→0 (P1 pełny gross) | 71/223 | 31.8 | 74.5 | 92.5 | 113/209 | 54.1 |
| bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji) | 68/223 | 30.5 | 74.5 | 93.6 | 110/209 | 52.6 |
| bramka surowa DZIENNA | 70/223 | 31.4 | 74.6 | 92.4 | 112/209 | 53.6 |

Okna 12-tyg. z killem wg roku startu (bez bramki vs bramka z histerezą D0 vs dzienna):

| rok startu | okna | bez bramki | hist. D0 | hist. dzienna | tylko P2→0 |
|---|---|---|---|---|---|
| 2022 | 37 | 20 | 0 | 0 | 0 |
| 2023 | 52 | 13 | 10 | 10 | 10 |
| 2024 | 52 | 25 | 25 | 23 | 25 |
| 2025 | 52 | 11 | 10 | 10 | 11 |
| 2026 | 30 | 25 | 25 | 25 | 25 |

## Epizod 2022 (okna z D0 w 2022): kapitał z/bez bramki, start 100 na pierwszym D0 2022

| wariant | kapitał końc. 2022 bez kill | maxDD % | z kill: kapitał | kill |
|---|---|---|---|---|
| bez bramki | 91.9 | 47.2 | 85.0 | 2022-06-23 |
| bramka z histerezą (odczyt D0, jak faza 2) | 97.6 | 4.0 | 97.6 | — |
| bramka surowa (odczyt D0) | 105.4 | 4.0 | 105.4 | — |
| tylko P2→0 (P1 pełny gross) | 95.0 | 7.9 | 95.0 | — |
| bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji) | 106.1 | 1.3 | 106.1 | — |
| bramka surowa DZIENNA | 113.9 | 3.1 | 113.9 | — |

Zwrot kapitału (brutto, 1,2×spread) wg stanu bramki z histerezą na D0 — średnia, σ, najgorszy tydzień:

| stan | okna | śr. % kap. | σ % kap. | najgorszy % | 5. pct % | udział tyg. < −10% kap. |
|---|---|---|---|---|---|---|
| P0 | 163 | 1.11 | 9.63 | -30.9 | -14.3 | 9% |
| P1 | 21 | 3.65 | 8.16 | -4.5 | -4.5 | 0% |
| P2 | 50 | 0.49 | 7.45 | -17.5 | -10.8 | 6% |

## TEST 3. Warianty progów (bramka z histerezą, odczyt D0 i DZIENNY) — czy jakiś poprawia Sharpe netto kapitału?

Siatka: P1 VIX ∈ {25, 28, 30, 35}, P1 DD ∈ {10, 15, 100(=wył.)}, MA200 ∈ {tak, nie}; P2 DD ∈ {20, 25, 100(=wył.)}, P2 VIX ∈ {35, 40}; gross P1 ∈ {0,5; 0,75}. Metryki na pełnej ścieżce BEZ kill (Sharpe/maxDD) oraz P(kill 12 t.). Wielokrotne porównania — każdy "najlepszy" wariant jest in-sample.

Odniesienie bez bramki: Sharpe netto 0.668, maxDD 69.3%, kapitał końc. 278.7.

Wariantów w siatce: 576; z Sharpe > odniesienia: 326 (57%); z maxDD niższym o >5 pkt: 0; z OBYDWOMA (Sharpe wyżej i maxDD niżej o >5 pkt): 0.

Top 10 wg Sharpe:

| P1 VIX | P1 DD | MA200 | P2 DD | P2 VIX | gross P1 | tryb | aktywna tyg. | śr. gross | Sharpe | t | śr. tyg. % | σ | maxDD % | kapitał końc. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 35 | 15% | nie | 20% | 40 | 0.75 | dzienna | 57 | 78% | 0.773 | 1.64 | 0.91 | 8.46 | 69.3 | 369.2 |
| 35 | 15% | nie | 20% | 40 | 0.5 | dzienna | 57 | 77% | 0.773 | 1.64 | 0.91 | 8.45 | 69.3 | 368.9 |
| 35 | 15% | nie | 20% | 35 | 0.5 | dzienna | 59 | 76% | 0.772 | 1.64 | 0.90 | 8.44 | 69.3 | 367.5 |
| 35 | 15% | nie | 20% | 35 | 0.75 | dzienna | 59 | 77% | 0.770 | 1.63 | 0.90 | 8.46 | 69.3 | 366.3 |
| 35 | wył. | nie | 20% | 40 | 0.75 | dzienna | 54 | 78% | 0.770 | 1.63 | 0.90 | 8.47 | 69.3 | 366.1 |
| 35 | wył. | nie | 20% | 35 | 0.75 | dzienna | 56 | 77% | 0.767 | 1.63 | 0.90 | 8.46 | 69.3 | 363.2 |
| 35 | wył. | nie | 20% | 40 | 0.5 | dzienna | 54 | 78% | 0.767 | 1.63 | 0.90 | 8.45 | 69.3 | 362.9 |
| 35 | wył. | nie | 20% | 35 | 0.5 | dzienna | 56 | 77% | 0.765 | 1.62 | 0.90 | 8.45 | 69.3 | 361.5 |
| 35 | 15% | nie | 25% | 35 | 0.5 | D0 | 59 | 79% | 0.757 | 1.61 | 0.89 | 8.45 | 69.3 | 353.5 |
| 35 | 15% | nie | wył. | 35 | 0.5 | D0 | 59 | 81% | 0.757 | 1.61 | 0.89 | 8.49 | 69.3 | 353.7 |

Warianty z pytania (VIX 25 / VIX 30 / DD 15%), reszta progów jak w rutynie, gross P1 0,5:

| wariant | tryb | aktywna tyg. | śr. gross | Sharpe | t | maxDD % | kapitał końc. | ΔSharpe | ΔmaxDD |
|---|---|---|---|---|---|---|---|---|---|
| P1 VIX>25 | D0 | 74 | 74% | 0.577 | 1.22 | 69.5 | 215.0 | -0.091 | +0.2 |
| P1 VIX>25 | dzienna | 74 | 74% | 0.616 | 1.31 | 71.7 | 238.0 | -0.052 | +2.4 |
| P1 VIX>30 | D0 | 69 | 75% | 0.666 | 1.41 | 69.5 | 273.3 | -0.002 | +0.2 |
| P1 VIX>30 | dzienna | 69 | 75% | 0.688 | 1.46 | 71.7 | 289.9 | +0.020 | +2.4 |
| P1 DD>15% | D0 | 66 | 75% | 0.621 | 1.32 | 69.3 | 241.7 | -0.047 | +0.0 |
| P1 DD>15% | dzienna | 66 | 75% | 0.655 | 1.39 | 69.3 | 264.4 | -0.013 | -0.0 |
| P2 DD>25% | D0 | 71 | 76% | 0.625 | 1.33 | 69.5 | 244.2 | -0.043 | +0.2 |
| P2 DD>25% | dzienna | 71 | 77% | 0.594 | 1.26 | 71.7 | 224.6 | -0.074 | +2.4 |
| bez MA200 w P1 | D0 | 70 | 74% | 0.619 | 1.31 | 69.5 | 240.5 | -0.049 | +0.2 |
| bez MA200 w P1 | dzienna | 70 | 75% | 0.605 | 1.28 | 71.7 | 231.4 | -0.063 | +2.4 |
| tylko VIX (P1>28, P2>40), bez DD i MA | D0 | 53 | 83% | 0.641 | 1.36 | 69.3 | 255.4 | -0.027 | +0.0 |
| tylko VIX (P1>28, P2>40), bez DD i MA | dzienna | 53 | 83% | 0.626 | 1.33 | 69.3 | 245.3 | -0.042 | -0.0 |

## TEST 4b. Bramka jako ubezpieczenie przy zerowej alfie: losowe koszyki 5/5 (te same okna), ALLOC 0,24

500 losowych strategii (losowy TOP5/BOTTOM5 z uniwersum ważnego na D0 — spółki z pełnym 126-sesyjnym oknem). Dla każdej: P(kill 12 t.) bez bramki vs z bramką (hist. D0 i dzienna), maxDD pełnej ścieżki, Sharpe netto. Finansowanie ∝ gross jest tu kosztem netto ujemnym dla obu wariantów.

| wariant | P(kill 12 t.) śr. | mediana | maxDD śr. % | mediana | Sharpe netto śr. | śr. tyg. % | σ tyg. % | kapitał końc. mediana | udział strategii z kill w pełnej ścieżce |
|---|---|---|---|---|---|---|---|---|---|
| bez bramki | 11.8% | 12.5% | 78.4 | 80.5 | -0.92 | -0.506 | 4.00 | 25.4 | 100% |
| bramka hist. D0 | 8.1% | 7.1% | 69.4 | 71.5 | -0.81 | -0.382 | 3.45 | 35.5 | 100% |
| bramka hist. dzienna | 8.3% | 7.1% | 69.6 | 72.0 | -0.81 | -0.385 | 3.47 | 35.1 | 100% |
| tylko P2→0 | 9.4% | 8.9% | 71.2 | 73.3 | -0.80 | -0.398 | 3.61 | 33.6 | 100% |

Sparowane różnice (hist. D0 − bez bramki) na 500 losowych strategiach: ΔP(kill 12 t.) = -3.7 pkt (udział strategii, gdzie bramka obniża P(kill): 75%); ΔmaxDD = -9.0 pkt (obniża w 97%); ΔSharpe = +0.113 (podnosi w 69%).

σ tygodniowego zwrotu kapitału LOSOWEGO koszyka (brutto, 1,2×spread) wg stanu bramki (pooled z 200 losowań):

| stan | σ % kap. | 5. pct | 1. pct |
|---|---|---|---|
| P0 | 4.10 | -6.6 | -10.8 |
| P1 | 4.24 | -6.8 | -11.3 |
| P2 | 3.72 | -5.9 | -9.7 |

## Dodatek: ta sama bramka przy ALLOC 0,12 (gross 120%) — momentum 6M

| wariant | kapitał końc. bez kill | maxDD % | Sharpe netto | P(kill 12 t.) | kapitał z kill |
|---|---|---|---|---|---|
| bez bramki | 217.1 | 41.9 | 0.69 | 6.7% | 80.6 |
| bramka z histerezą (odczyt D0, jak faza 2) | 187.5 | 42.2 | 0.62 | 5.8% | 85.0 |
| bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji) | 193.0 | 44.4 | 0.64 | 6.3% | 89.2 |
| tylko P2→0 (P1 pełny gross) | 221.6 | 41.9 | 0.74 | 5.8% | 80.7 |
