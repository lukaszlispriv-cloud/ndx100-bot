# Seria od D0 vs od wejść vs „jak rachunek” (W6, W7)

| tydz. | seria | LONG | SHORT | spread | ≈ rachunek |
|---|---|---|---|---|---|
| W6 | od D0 (prognoza) | LONG śr. -4.63 | SHORT śr. -1.27 | spread -5.89 p.p. | ≈ wynik rachunku -7.1% kapitału (×1,2) |
| W6 | od faktycznych wejść, bez stopów | LONG śr. -4.53 | SHORT śr. -1.28 | spread -5.81 p.p. | ≈ wynik rachunku -7.0% kapitału (×1,2) |
| W6 | jak rachunek (wejścia + stopy + ponowne otwarcia) | LONG śr. -4.53 | SHORT śr. -1.28 | spread -5.81 p.p. | ≈ wynik rachunku -7.0% kapitału (×1,2) |
| W7 | od D0 (prognoza) | LONG śr. -16.95 | SHORT śr. -4.20 | spread -21.15 p.p. | ≈ wynik rachunku -25.4% kapitału (×1,2) |
| W7 | od faktycznych wejść, bez stopów | LONG śr. -16.28 | SHORT śr. -3.45 | spread -19.74 p.p. | ≈ wynik rachunku -23.7% kapitału (×1,2) |
| W7 | jak rachunek (wejścia + stopy + ponowne otwarcia) | LONG śr. -11.50 | SHORT śr. -3.45 | spread -14.96 p.p. | ≈ wynik rachunku -17.9% kapitału (×1,2) |

## Nogi W7 — trzy serie (p.p. na nodze)

| noga | kier. | od D0 | od wejścia bez stopu | jak rachunek | efekt stopu+ponownego otwarcia (rachunek − hold) | efekt opóźnienia wejścia (hold − D0) |
|---|---|---|---|---|---|---|
| MU | L | -14.58 | -14.58 | -13.03 | +1.55 | +0.00 |
| LITE | L | -25.31 | -25.31 | -11.25 | +14.06 | +0.00 |
| MRVL | L | -17.24 | -16.79 | -15.49 | +1.30 | +0.45 |
| PANW | L | -18.33 | -16.95 | -9.96 | +7.00 | +1.38 |
| CSCO | L | -9.29 | -7.80 | -7.80 | +0.00 | +1.50 |
| CMCSA | S | -6.00 | -6.00 | -6.00 | +0.00 | +0.00 |
| SBUX | S | -7.46 | -7.46 | -7.46 | +0.00 | +0.00 |
| PEP | S | -4.38 | -3.61 | -3.61 | +0.00 | +0.77 |
| TMUS | S | -7.08 | -4.13 | -4.13 | +0.00 | +2.95 |
| APP | S | +3.94 | +3.94 | +3.94 | +0.00 | +0.00 |

## Nogi W6 — trzy serie (p.p. na nodze)

| noga | kier. | od D0 | od wejścia | efekt opóźnienia wejścia |
|---|---|---|---|---|
| MU | L | -4.27 | -4.27 | +0.00 |
| LITE | L | +1.65 | +1.40 | -0.25 |
| TER | L | -10.32 | -10.32 | +0.00 |
| AMAT | L | -6.11 | -5.37 | +0.74 |
| AMD | L | -4.07 | -4.07 | +0.00 |
| APP | S | -3.29 | -3.29 | +0.00 |
| NFLX | S | -4.83 | -4.83 | +0.00 |
| PAYX | S | -5.09 | -5.17 | -0.07 |
| CMCSA | S | +2.69 | +2.69 | +0.00 |
| SBUX | S | +4.18 | +4.18 | +0.00 |

## Bilans wykonania (p.p. spreadu)
- W6: opóźnienie wejścia +0.08 p.p.; stopy+ponowne otwarcia +0.00 p.p.; razem wykonanie vs prognoza +0.08 p.p. (history spread_fills_pp: W6 +3,88 / W7 −12,36 — te liczby NIE są serią rachunku)
- W7: opóźnienie wejścia +1.41 p.p.; stopy+ponowne otwarcia +4.78 p.p.; razem wykonanie vs prognoza +6.19 p.p. (history spread_fills_pp: W6 +3,88 / W7 −12,36 — te liczby NIE są serią rachunku)

Każdy stop realizuje −10 % × ALLOC 0.24 = -2.4 % kapitału; 4 stopy W7 (MU, LITE, MRVL, PANW) = -9.6 % kapitału zrealizowane (bez uwzględnienia, że MU i MRVL/PANW zostały odkupione niżej).

W6 od zamknięcia 6.10 do 9.10: spread -3.57 p.p. (≈ -4.3% kapitału); W7 jak rachunek -14.96 p.p. (≈ -17.9%); złożone ≈ -21.5% kapitału vs podane w zadaniu −23,7 % od szczytu 6.10→16.10 (różnica: taktyczne APOG/PENG/ERIC, koszty CFD, egzekucja stopów poniżej −10 %, wyrównania).
