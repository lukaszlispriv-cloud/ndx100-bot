# (a1) Konstrukcje koszyków: spread 5-ses. forward vs zwrot L−S 20 sesji wstecz (okna nienakładające się co 5 sesji, ~1000 sesji przed D0)

| koszyk | n okien | corr(mom20, fwd5) | slope (p.p. fwd na 10 p.p. mom) | t | śr. fwd5 gdy mom20 > +20 p.p. (n) | śr. fwd5 pozostałe |
|---|---|---|---|---|---|---|
| W1 | 197 | +0.07 | +0.33 | +0.93 | +1.16 (14) | +0.68 |
| W2 | 200 | +0.10 | +0.42 | +1.36 | +3.42 (9) | +0.56 |
| W3 | 200 | +0.15 | +0.64 | +2.11 | +2.84 (17) | +0.80 |
| W4 | 192 | +0.07 | +0.32 | +0.91 | +3.53 (21) | +0.66 |
| W5 | 122 | +0.16 | +0.73 | +1.78 | +4.10 (18) | +1.19 |
| W6 | 195 | +0.14 | +0.63 | +1.89 | +4.78 (23) | +0.39 |
| W7 | 191 | +0.08 | +0.39 | +1.17 | +3.58 (15) | +0.76 |

Pooled 7 konstrukcji (n=1297; obserwacje skorelowane między koszykami — t zawyżony): corr +0.11, slope +0.52 p.p./10 p.p., t +4.11; fwd5 przy mom20>+20 p.p.: +3.48 (n=117) vs +0.69 (n=1180)

# (a2) Uniwersum 103 spółek: 5-ses. zwrot relatywny vs ^NDX wg decyla 20-ses. zwrotu relatywnego (okna nienakładające się, 2022-10 → 2026-10)

okien: 198; średni 5-ses. zwrot relatywny wg decyla momentum 20-ses. (D1 = najsłabsze, D10 = najmocniejsze):
  D1: +0.04 p.p. (n=1993, sd 6.3)
  D2: +0.10 p.p. (n=1906, sd 5.1)
  D3: -0.08 p.p. (n=1950, sd 5.0)
  D4: -0.02 p.p. (n=1904, sd 5.6)
  D5: -0.17 p.p. (n=1902, sd 5.0)
  D6: +0.07 p.p. (n=1951, sd 5.0)
  D7: +0.06 p.p. (n=1923, sd 5.1)
  D8: -0.06 p.p. (n=1931, sd 5.3)
  D9: +0.35 p.p. (n=1925, sd 5.8)
  D10: +0.78 p.p. (n=1851, sd 7.9)
TOP5−BOTTOM5 wg momentum 20-ses. (naiwny „koszyk pogoni”): śr. +0.88 p.p./5 ses., sd 6.40, t +1.94 (n=198)
  ostatnie 52 okna: śr. +1.29, t +1.05

# (b) Reszty idiosynkratyczne nóg (3f) — per strona i blok

| grupa | nóg | śr. reszta p.p. | sd | t (nogi traktowane jako niezależne — zawyżone) | reszta > 0 |
|---|---|---|---|---|---|
| wszystkie nogi | 70 | +0.30 | 5.94 | +0.43 | 40/70 |
| LONG | 35 | -1.25 | 6.01 | -1.23 | 17/35 |
| SHORT | 35 | +1.86 | 5.52 | +1.99 | 23/35 |
| LONG bez W7 | 30 | -0.48 | 5.75 | -0.46 | 16/30 |
| SHORT bez W7 | 30 | +2.80 | 5.32 | +2.89 | 22/30 |
| blok SEMI | 29 | -1.16 | 6.09 | -1.03 | 14/29 |
| blok SOFT | 13 | +3.33 | 7.28 | +1.65 | 8/13 |
| blok DEF | 17 | +1.47 | 4.42 | +1.37 | 12/17 |
| blok MEDIA | 2 | +0.85 | 0.98 | +1.22 | 2/2 |
| blok CYBER | 1 | -11.17 | nan | +nan | 0/1 |
| blok SIECI | 1 | -5.29 | nan | +nan | 0/1 |
| blok AUTO | 3 | -1.66 | 3.03 | -0.95 | 1/3 |
| blok UTIL | 2 | +3.83 | 4.46 | +1.22 | 2/2 |
| blok MEGA | 2 | -0.66 | 1.39 | -0.67 | 1/2 |

Surowe pozycje (vs NDX) per strona:
| grupa | nóg | śr. pozycja p.p. | sd | t | trafienia |
|---|---|---|---|---|---|
| LONG pozycja | 35 | -1.58 | 7.19 | -1.30 | 14/35 |
| SHORT pozycja | 35 | +1.05 | 7.37 | +0.84 | 19/35 |
| SHORT DEF+MEDIA pozycja | 19 | +0.14 | 7.64 | +0.08 | 13/19 |
| SHORT SOFT pozycja | 13 | +3.01 | 7.65 | +1.42 | 6/13 |
| LONG SEMI pozycja | 29 | -1.52 | 7.37 | -1.11 | 12/29 |
