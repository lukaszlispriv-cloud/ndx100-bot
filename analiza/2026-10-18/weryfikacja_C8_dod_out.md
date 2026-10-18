# Dodatek C8

Tygodnie 2022 (D0 w 2022): 37; z bramką hist. P1 1, P2 36 → aktywna w 37/37 tyg.; cała próba: aktywna 71/234 (P1 21, P2 50). Śr. gross 2022 = 1%.

## Tygodnie, w których histereza trzyma stan SUROWSZY niż progi (odczyt D0) — co robiło momentum

| przypadek | okna | śr. % kap. (gross 100%) | t | lata |
|---|---|---|---|---|
| hist. P2, surowa P1/P0 (po epizodzie P2, przed histerezą) | 8 | 3.84 | 1.75 | 2022:1, 2023:3, 2025:4 |
| hist. P1, surowa P0 (po P1, przed 3 sesjami powrotu) | 2 | 5.77 | 1.57 | 2026:2 |
| hist. łagodniejsza niż surowa (nie powinno być) | 0 | — | — | — |
| stan zgodny, P1 | 19 | 3.42 | 1.76 | 2022:1, 2023:6, 2024:3, 2025:5, 2026:4 |
| stan zgodny, P2 | 42 | -0.14 | -0.12 | 2022:35, 2023:6, 2025:1 |

## Epizody drawdownu ≥20% kapitału (ścieżka BEZ kill), ALLOC 0,24

**bez bramki** (ALLOC 0.240):

| szczyt | dołek | głębokość % | szczyt→dołek ses. | odrobienie ses. (od szczytu) | stan bramki w dołku |
|---|---|---|---|---|---|
| 2022-05-11 | 2024-09-03 | 63.4 | 580 | 689 | P0 |
| 2025-02-14 | 2025-03-10 | 43.3 | 15 | 141 | P1 |
| 2025-10-02 | 2025-10-22 | 22.1 | 14 | 19 | P0 |
| 2025-11-10 | 2025-11-20 | 21.9 | 8 | 30 | P0 |
| 2026-02-23 | 2026-03-06 | 39.4 | 9 | 32 | P1 |
| 2026-05-13 | 2026-05-18 | 20.1 | 3 | 8 | P0 |
| 2026-06-22 | 2026-09-14 | 69.3 | 58 | nie odrobiono do 2026-10-16 | P0 |

**bramka hist. D0** (ALLOC 0.240):

| szczyt | dołek | głębokość % | szczyt→dołek ses. | odrobienie ses. (od szczytu) | stan bramki w dołku |
|---|---|---|---|---|---|
| 2023-11-10 | 2024-09-03 | 50.4 | 202 | 255 | P0 |
| 2025-02-14 | 2025-03-10 | 39.0 | 15 | 177 | P1 |
| 2025-11-10 | 2025-11-20 | 21.9 | 8 | 30 | P0 |
| 2026-02-23 | 2026-03-06 | 39.4 | 9 | 54 | P1 |
| 2026-05-13 | 2026-05-18 | 20.1 | 3 | 8 | P0 |
| 2026-06-22 | 2026-09-14 | 69.5 | 58 | nie odrobiono do 2026-10-16 | P0 |

**bramka hist. dzienna** (ALLOC 0.240):

| szczyt | dołek | głębokość % | szczyt→dołek ses. | odrobienie ses. (od szczytu) | stan bramki w dołku |
|---|---|---|---|---|---|
| 2023-11-10 | 2024-09-03 | 50.3 | 202 | 253 | P0 |
| 2025-02-14 | 2025-03-10 | 38.7 | 15 | 177 | P1 |
| 2025-11-10 | 2025-11-20 | 21.9 | 8 | 30 | P0 |
| 2026-02-23 | 2026-03-06 | 39.4 | 9 | 54 | P1 |
| 2026-05-13 | 2026-05-18 | 20.1 | 3 | 8 | P0 |
| 2026-06-22 | 2026-09-14 | 71.7 | 58 | nie odrobiono do 2026-10-16 | P0 |

**stały ALLOC 0,178 (iso-gross)** (ALLOC 0.178):

| szczyt | dołek | głębokość % | szczyt→dołek ses. | odrobienie ses. (od szczytu) | stan bramki w dołku |
|---|---|---|---|---|---|
| 2022-05-11 | 2024-09-03 | 49.7 | 580 | 645 | P0 |
| 2025-02-14 | 2025-03-10 | 34.0 | 15 | 141 | P1 |
| 2026-02-23 | 2026-03-06 | 30.7 | 9 | 31 | P1 |
| 2026-06-22 | 2026-09-14 | 56.8 | 58 | nie odrobiono do 2026-10-16 | P0 |

## Kontrola iso-gross: bramka (śr. gross 74%) vs stały ALLOC 0,24×0,74 = 0,178 (gross 178%) vs bramka — momentum 6M

| wariant | ALLOC | śr. gross (×240%) | kapitał końc. bez kill | maxDD % | Sharpe netto | t | P(kill 12 t.) | P(kill 26 t.) | kill 12 t. 2022 | kill 12 t. 2023–26 | kapitał Z KILL | kill (data) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bez bramki | 0.240 | 100% | 278.7 | 69.3 | 0.668 | 1.42 | 42.2% | 71.8% | 20/37 | 74/186 | 85.0 | 2022-06-23 |
| bramka hist. D0 | 0.240 | 74% | 236.4 | 69.5 | 0.613 | 1.30 | 31.4% | 53.6% | 0/37 | 70/186 | 95.8 | 2024-01-05 |
| bramka hist. dzienna | 0.240 | 74% | 250.8 | 71.7 | 0.636 | 1.35 | 30.5% | 52.6% | 0/37 | 68/186 | 105.5 | 2024-01-05 |
| stały iso-gross | 0.178 | 74% | 261.6 | 56.8 | 0.679 | 1.44 | 27.8% | 60.3% | 17/37 | 45/186 | 81.4 | 2022-07-18 |
| stały ALLOC 0,16 | 0.160 | 67% | 250.2 | 52.5 | 0.682 | 1.45 | 23.3% | 56.5% | 11/37 | 41/186 | 81.5 | 2022-07-19 |
| stały ALLOC 0,12 | 0.120 | 50% | 217.1 | 41.9 | 0.690 | 1.46 | 6.7% | 8.6% | 2/37 | 13/186 | 80.6 | 2022-07-21 |
| bramka hist. D0 + ALLOC 0,16 (gross P0 160%) | 0.160 | 49% | 211.7 | 52.8 | 0.621 | 1.32 | 16.1% | 43.5% | 0/37 | 36/186 | 88.1 | 2024-02-21 |

## Losowe koszyki 5/5 (zerowa alfa), 200 strategii: bramka hist. D0 vs stały iso-gross ALLOC 0,178 — sparowane

| wariant | P(kill 12 t.) śr. | maxDD śr. % | Sharpe netto śr. | śr. liczba okien 12-t. z killem startujących w 2022 (z ~10 badanych) |
|---|---|---|---|---|
| bez bramki, ALLOC 0,24 | 11.7% | 78.9 | -0.93 | 0.88 |
| bramka hist. D0, ALLOC 0,24 | 8.5% | 70.7 | -0.83 | 0.00 |
| stały ALLOC 0,178 (iso-gross) | 3.0% | 68.4 | -0.93 | 0.17 |

Sparowane (bramka − iso-gross): ΔP(kill 12 t.) +5.5 pkt (bramka niżej w 3%, równe 12%); ΔmaxDD +2.3 pkt (bramka niżej w 32%); ΔSharpe +0.100 (bramka wyżej w 66%).


## σ tygodniowa zwrotu kapitału mom6M (1,2×spread) wg roku i stanu — gdzie jest ryzyko kill

| rok | okna | śr. % | σ % | najgorszy % | tyg. P0 | σ w P0 | tyg. P1/P2 | σ w P1/P2 |
|---|---|---|---|---|---|---|---|---|
| 2022 | 37 | 0.61 | 7.96 | -17.5 | 0 | nan | 37 | 7.96 |
| 2023 | 52 | -0.23 | 4.74 | -9.5 | 37 | 4.66 | 15 | 4.64 |
| 2024 | 52 | 1.68 | 8.85 | -15.4 | 49 | 8.97 | 3 | 8.20 |
| 2025 | 52 | 1.90 | 7.80 | -19.3 | 42 | 8.46 | 10 | 3.79 |
| 2026 | 41 | 2.09 | 14.59 | -30.9 | 35 | 14.75 | 6 | 10.60 |
