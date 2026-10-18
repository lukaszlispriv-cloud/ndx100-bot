# Spójność wyniku tydzień do tygodnia (tabele TOP15+BOTTOM15, 30 nazw/tydz.)

| para | wspolne | nowe_w_tabeli | spearman_wynik | sr_abs_zmiana_wyniku | max_abs_zmiana | corr_zmiana_wyniku_vs_rel_kursu | zmiana_strony |
|---|---|---|---|---|---|---|---|
| W1→W2 | 27 | 3 | 0.96 | 1.67 | 12.00 | 0.53 | 0 |
| W2→W3 | 15 | 15 | 0.86 | 6.20 | 13.00 | -0.12 | 0 |
| W3→W4 | 23 | 7 | 0.88 | 2.87 | 10.00 | 0.65 | 0 |
| W4→W5 | 23 | 7 | 0.85 | 4.00 | 9.00 | -0.22 | 0 |
| W5→W6 | 25 | 5 | 0.86 | 2.48 | 10.00 | 0.32 | 0 |
| W6→W7 | 20 | 10 | 0.86 | 2.75 | 9.00 | 0.83 | 0 |
| W7→W8 | 9 | 21 | 0.75 | 5.52 | 14.40 | 0.83 | 0 |

Interpretacja: spearman_wynik ~1 = ranking stabilny; corr(zmiana wyniku, zwrot rel. kursu) > 0 = wynik „goni” kurs (momentum wbudowane w ocenę).

Unikalnych spółek w tabelach W1–W8: 69 (z ~101); w ≥6 z 8 tygodni: 15; tylko raz: 18

Spółki obecne ≥5 razy — rozstęp wyniku:
| ticker | n | strony | wynik_min | wynik_max | wynik_sd |
|---|---|---|---|---|---|
| APP | 8 | SHORT | 27.00 | 41.60 | 5.38 |
| TSLA | 8 | SHORT | 20.00 | 32.30 | 3.91 |
| NVDA | 8 | LONG | 63.00 | 78.00 | 5.14 |
| INTU | 7 | SHORT | 22.00 | 41.00 | 6.85 |
| CMCSA | 7 | SHORT | 30.00 | 42.00 | 4.46 |
| AMD | 7 | LONG | 65.00 | 78.00 | 4.20 |
| PEP | 7 | SHORT | 33.00 | 44.00 | 4.50 |
| SBUX | 7 | SHORT | 35.00 | 39.00 | 1.72 |
| MU | 7 | LONG | 74.00 | 83.00 | 3.73 |
| LITE | 7 | LONG | 66.00 | 78.00 | 3.64 |
| TER | 7 | LONG | 61.00 | 70.00 | 3.26 |
| KLAC | 6 | LONG | 60.30 | 71.00 | 3.92 |
| AMAT | 6 | LONG | 61.10 | 69.00 | 2.91 |
| AVGO | 6 | LONG | 62.20 | 74.00 | 4.35 |
| STX | 6 | LONG | 63.00 | 74.00 | 4.20 |
| CRWD | 5 | LONG | 64.00 | 68.00 | 1.79 |
| LRCX | 5 | LONG | 62.00 | 72.00 | 4.27 |
| DASH | 5 | SHORT | 40.00 | 43.00 | 1.31 |
| MSFT | 5 | LONG | 63.00 | 73.00 | 4.69 |
| MRVL | 5 | LONG | 67.00 | 73.00 | 2.61 |
| NFLX | 5 | SHORT | 35.00 | 45.00 | 4.15 |
| SNDK | 5 | LONG | 63.00 | 78.40 | 6.34 |

Format wyniku: W1–W7 liczby całkowite; W8 jedno miejsce po przecinku (78,4) — zmiana generatora/metody (dane_b1=tv od 12.10).
Liczba wierszy z gwiazdką/statusem wykluczenia (reguła/filtr poza modelem) w W8: 13 z 30

Nogi koszyka spoza pierwszej piątki rankingu (nadpisania regułami/filtrami):
  2026-W2 SHORT: w koszyku spoza TOP5: ['PEP']; z TOP5 pominięte: ['ADBE']
  2026-W3 LONG: w koszyku spoza TOP5: ['AVGO']; z TOP5 pominięte: ['SNDK']
  2026-W3 SHORT: w koszyku spoza TOP5: ['CMCSA']; z TOP5 pominięte: ['TTWO']
  2026-W4 SHORT: w koszyku spoza TOP5: ['CMCSA']; z TOP5 pominięte: ['TSLA']
  2026-W5 LONG: w koszyku spoza TOP5: ['TER']; z TOP5 pominięte: ['NVDA']
  2026-W5 SHORT: w koszyku spoza TOP5: ['CMCSA', 'APP']; z TOP5 pominięte: ['TSLA', 'INTU']
  2026-W6 SHORT: w koszyku spoza TOP5: ['CMCSA', 'SBUX']; z TOP5 pominięte: ['TSLA', 'INTU']
  2026-W7 SHORT: w koszyku spoza TOP5: ['PEP']; z TOP5 pominięte: ['TSLA']
  2026-W8 LONG: w koszyku spoza TOP5: ['GILD', 'QCOM', 'ADP']; z TOP5 pominięte: ['SNDK', 'NVDA', 'STX']
  2026-W8 SHORT: w koszyku spoza TOP5: ['DASH', 'ALNY', 'APP', 'FER']; z TOP5 pominięte: ['MSTR', 'CRWV', 'TSLA', 'RKLB']
