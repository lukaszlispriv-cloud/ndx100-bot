# Wyniki skryptu ryzyko_sizing.py
dane: /tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/../dane/closes_5y.csv  sesje 2021-10-18..2026-10-16 n=1255; uniwersum 103 tickerow

## (1) sigma koszyka 5L/5S, 24% na noge (gross 240%)

| W | D0 | okno | sigma_d nogi long sr | sigma_d nogi short sr | sigma_d kapital | sigma_tyg (x sqrt5) | sigma_tyg empir. 5-ses. | rho par LONG | rho par SHORT | rho L-S | sigma gdyby nogi niezalezne |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 2026-08-26 | 60 (n=60) | 4.64% | 3.56% | **5.44%** | 12.2% | 13.1% | 0.37 | 0.29 | -0.05 | 3.32% |
| W1 | 2026-08-26 | 250 (n=248) | 4.17% | 3.20% | **4.15%** | 9.3% | 8.3% | 0.28 | 0.18 | 0.03 | 2.97% |
| W2 | 2026-08-28 | 60 (n=60) | 3.84% | 2.92% | **4.03%** | 9.0% | 8.5% | 0.34 | 0.21 | -0.05 | 2.80% |
| W2 | 2026-08-28 | 250 (n=248) | 3.42% | 2.80% | **3.15%** | 7.0% | 6.4% | 0.30 | 0.06 | 0.03 | 2.54% |
| W3 | 2026-09-04 | 60 (n=58) | 4.33% | 2.90% | **4.91%** | 11.0% | 11.6% | 0.57 | 0.14 | -0.07 | 2.96% |
| W3 | 2026-09-04 | 250 (n=246) | 3.96% | 2.89% | **3.86%** | 8.6% | 7.7% | 0.48 | 0.11 | 0.06 | 2.75% |
| W4 | 2026-09-11 | 60 (n=58) | 4.95% | 2.76% | **6.35%** | 14.2% | 11.8% | 0.64 | 0.25 | -0.26 | 3.16% |
| W4 | 2026-09-11 | 250 (n=248) | 4.75% | 2.76% | **4.97%** | 11.1% | 9.9% | 0.48 | 0.18 | -0.06 | 3.05% |
| W5 | 2026-09-28 | 60 (n=58) | 5.01% | 2.20% | **5.99%** | 13.4% | 12.2% | 0.74 | 0.23 | -0.21 | 3.01% |
| W5 | 2026-09-28 | 250 (n=248) | 5.13% | 2.42% | **5.21%** | 11.7% | 11.6% | 0.55 | 0.11 | -0.07 | 3.12% |
| W6 | 2026-10-02 | 60 (n=58) | 4.78% | 2.38% | **5.94%** | 13.3% | 12.9% | 0.75 | 0.20 | -0.21 | 2.93% |
| W6 | 2026-10-02 | 250 (n=248) | 4.92% | 2.52% | **5.27%** | 11.8% | 10.4% | 0.59 | 0.14 | -0.09 | 3.05% |
| W7 | 2026-10-09 | 60 (n=58) | 4.23% | 2.29% | **4.40%** | 9.8% | 9.8% | 0.29 | 0.23 | -0.15 | 2.72% |
| W7 | 2026-10-09 | 250 (n=248) | 4.31% | 2.34% | **3.97%** | 8.9% | 7.8% | 0.28 | 0.13 | -0.07 | 2.81% |
| W8 | 2026-10-16 | 60 (n=60) | 2.08% | 3.40% | **2.22%** | 5.0% | 2.9% | 0.10 | 0.15 | 0.16 | 2.25% |
| W8 | 2026-10-16 | 250 (n=250) | 2.18% | 3.24% | **2.23%** | 5.0% | 5.2% | 0.09 | 0.19 | 0.15 | 2.19% |

## (1b) losowe koszyki 5/5 z uniwersum (1000 losowan, okno 250 sesji, 24% na noge)

| data D0 | mediana sigma_d kapital | p10 | p90 | p99 | sr rho par LONG (losowe) | sigma faktycznego koszyka | percentyl faktycznego |
|---|---|---|---|---|---|---|---|
| 2026-09-11 (W4, n_univ=91) | 2.25% | 1.72% | 3.46% | 4.17% | 0.11 | 4.97% | 100 |
| 2026-09-28 (W5, n_univ=89) | 2.23% | 1.69% | 3.45% | 4.14% | 0.11 | 5.21% | 100 |
| 2026-10-02 (W6, n_univ=88) | 2.32% | 1.74% | 3.47% | 4.18% | 0.12 | 5.27% | 100 |
| 2026-10-09 (W7, n_univ=88) | 2.27% | 1.72% | 3.46% | 4.19% | 0.11 | 3.97% | 98 |
| 2026-10-16 (W8, n_univ=88) | 2.32% | 1.74% | 3.43% | 4.28% | 0.11 | 2.23% | 44 |

## (2) Rozklad drawdownu i P(kill switch 25% od szczytu)

pula bootstrapu: koszyki W1-W8 x 250 sesji do D0, wysrodkowane; n=1984, sigma jednostkowa 17.54%/d  (x0,24 = 4.21%/d kapitalu)
pula W4-W7: n=992, sigma jednostkowa 20.30%/d (x0,24 = 4.87%/d)

### (2a) stala alokacja na noge, zerowa alfa, bootstrap blokowy (blok 5) z puli W1-W8; start od szczytu

| ALLOC/noge | gross | sigma_d kap. | 4 tyg: DD mediana | DD p90 | DD p95 | DD p99 | P(kill) 4 tyg | P(kill) 12 tyg | P(kill) 12 tyg, start -21% | P(kill) 12 tyg, start -23,7% |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.24 | 240% | 4.21% | -15.0% | -26.3% | -27.9% | -30.9% | 16.5% | **60.4%** | 86% | 93% |
| 0.20 | 200% | 3.51% | -12.6% | -24.4% | -26.3% | -29.3% | 9.1% | **45.9%** | 82% | 91% |
| 0.16 | 160% | 2.81% | -10.1% | -19.9% | -23.3% | -26.8% | 3.3% | **28.4%** | 77% | 89% |
| 0.12 | 120% | 2.10% | -7.6% | -15.2% | -17.8% | -22.6% | 0.5% | **11.1%** | 70% | 86% |
| 0.10 | 100% | 1.75% | -6.4% | -12.8% | -15.0% | -19.2% | 0.1% | **4.9%** | 65% | 84% |
| 0.08 | 80% | 1.40% | -5.1% | -10.3% | -12.2% | -15.6% | 0.0% | **1.1%** | 57% | 81% |
| 0.06 | 60% | 1.05% | -3.8% | -7.8% | -9.2% | -11.9% | 0.0% | **0.1%** | 47% | 77% |
| 0.04 | 40% | 0.70% | -2.6% | -5.2% | -6.2% | -8.0% | 0.0% | **0.0%** | 29% | 68% |

### (2b) to samo, pula tylko W4-W7 (koszyki o najwyzszej zmiennosci)

| ALLOC | sigma_d kap. | P(kill) 4 tyg | P(kill) 12 tyg | DD p95 4 tyg |
|---|---|---|---|---|
| 0.24 | 4.87% | 24.2% | 70.3% | -29.0% |
| 0.12 | 2.44% | 1.2% | 17.6% | -20.1% |
| 0.08 | 1.62% | 0.0% | 2.7% | -13.8% |
| 0.06 | 1.22% | 0.0% | 0.2% | -10.5% |

### (2c) proces 'co tydzien nowy losowy koszyk 5/5 z uniwersum' (losowy blok 5 sesji z 5 lat, zwroty wysrodkowane), 12 tygodni

sigma jednostkowa losowych koszykow: 8.20%/d
| ALLOC | sigma_d kap. | P(kill) 12 tyg | DD p95 12 tyg |
|---|---|---|---|
| 0.24 | 1.97% | 8.6% | -25.7% |
| 0.12 | 0.98% | 0.1% | -14.7% |
| 0.08 | 0.66% | 0.0% | -10.0% |
| 0.06 | 0.49% | 0.0% | -7.6% |

### (2d) skalowanie do celu sigma_d kapitalu: co tydzien losowy koszyk z W1-W8 z wlasna historia i wlasna sigma60 ex ante

Metoda: tydzien = losowy koszyk b z {W1..W8}; zwroty = losowy blok 5 sesji z jego 250-sesyjnej, wysrodkowanej historii do D0; ALLOC_b = min(cap, cel / sigma60_unit(b)), sigma60 z 60 sesji do D0 (znane w sobote).

sigma60 jednostkowa (suma 10 nog) per koszyk: W1 22.7%, W2 16.8%, W3 20.5%, W4 26.4%, W5 24.9%, W6 24.7%, W7 18.3%, W8 9.3%
sigma jednostkowa mieszanki: 17.63%/d

| cel sigma_d | sr. ALLOC/noge | min-max ALLOC (W1..W8) | P(kill) 4 tyg | P(kill) 12 tyg | DD p95 4 tyg | DD p95 12 tyg | dla porownania: staly ALLOC o tej samej sredniej -> P(kill 12t) |
|---|---|---|---|---|---|---|---|
| 1.0% | 0.054 | 0.038-0.108 | 0.0% | **0.0%** | -7.5% | -12.8% | 0.0% |
| 1.5% | 0.081 | 0.057-0.162 | 0.0% | **0.5%** | -11.1% | -18.7% | 1.3% |
| 2.0% | 0.108 | 0.076-0.216 | 0.0% | **4.2%** | -14.6% | -24.2% | 7.2% |

ALLOC na noge z vol-targetu per koszyk (cel 1,5%/d): W1 6.6%, W2 8.9%, W3 7.3%, W4 5.7%, W5 6.0%, W6 6.1%, W7 8.2%, W8 16.2%


- **W4** (sigma60 nog %: MU 5.9, AMD 4.4, AVGO 2.7, MRVL 5.6, LITE 6.2, INTU 2.9, SBUX 1.4, CMCSA 2.3, APP 4.4, ADSK 2.7)
  - cel 1,5%/d: wagi inv-vol = MU 4.0%, AMD 5.4%, AVGO 8.7%, MRVL 4.2%, LITE 3.8%, INTU 8.1%, SBUX 16.9%, CMCSA 10.0%, APP 5.3%, ADSK 8.7%; gross 75%
  - cel 1,5%/d przy rownych wagach: 5.7% na noge, gross 57%; (cel 1,0%: 3.8%/noge; cel 2,0%: 7.6%/noge)
- **W5** (sigma60 nog %: MU 4.9, AMD 4.3, ALAB 6.3, STX 4.7, TER 4.9, SBUX 1.3, NFLX 2.2, PEP 1.2, CMCSA 2.3, APP 4.0)
  - cel 1,5%/d: wagi inv-vol = MU 4.9%, AMD 5.5%, ALAB 3.8%, STX 5.1%, TER 4.9%, SBUX 17.6%, NFLX 11.0%, PEP 19.1%, CMCSA 10.5%, APP 5.9%; gross 88%
  - cel 1,5%/d przy rownych wagach: 6.0% na noge, gross 60%; (cel 1,0%: 4.0%/noge; cel 2,0%: 8.0%/noge)
- **W6** (sigma60 nog %: MU 4.8, LITE 6.1, TER 4.8, AMAT 4.1, AMD 4.1, APP 4.0, NFLX 2.2, PAYX 2.2, CMCSA 2.2, SBUX 1.3)
  - cel 1,5%/d: wagi inv-vol = MU 5.0%, LITE 3.9%, TER 5.0%, AMAT 5.9%, AMD 5.8%, APP 5.9%, NFLX 11.0%, PAYX 11.0%, CMCSA 10.7%, SBUX 18.7%; gross 83%
  - cel 1,5%/d przy rownych wagach: 6.1% na noge, gross 61%; (cel 1,0%: 4.0%/noge; cel 2,0%: 8.1%/noge)
- **W7** (sigma60 nog %: MU 4.6, LITE 5.9, MRVL 4.7, PANW 3.8, CSCO 2.1, CMCSA 2.2, SBUX 1.3, PEP 1.2, TMUS 3.0, APP 3.8)
  - cel 1,5%/d: wagi inv-vol = MU 6.1%, LITE 4.8%, MRVL 6.0%, PANW 7.5%, CSCO 13.5%, CMCSA 12.8%, SBUX 22.0%, PEP 23.7%, TMUS 9.6%, APP 7.5%; gross 114%
  - cel 1,5%/d przy rownych wagach: 8.2% na noge, gross 82%; (cel 1,0%: 5.5%/noge; cel 2,0%: 10.9%/noge)
- **W8** (sigma60 nog %: GOOGL 1.8, GILD 1.6, MSFT 2.5, QCOM 2.9, ADP 1.6, AXON 4.3, DASH 2.7, ALNY 4.7, APP 3.9, FER 1.5)
  - cel 1,5%/d: wagi inv-vol = GOOGL 31.2%, GILD 36.1%, MSFT 23.0%, QCOM 19.7%, ADP 36.0%, AXON 13.4%, DASH 21.6%, ALNY 12.1%, APP 14.8%, FER 37.7%; gross 246%
  - cel 1,5%/d przy rownych wagach: 16.2% na noge, gross 162%; (cel 1,0%: 10.8%/noge; cel 2,0%: 21.6%/noge)

### (2f) kontrola modelu: zrealizowane dzienne zwroty kapitalu (0,24, rowne wagi, bez stopow/kosztow, wejscie close D0, do kolejnego D0)

sciezka W1..W7 rozliczana do D0 nastepnego tygodnia (D0 W1 = 2026-08-26 -> 2026-10-16), 36 sesji: wynik -7.7%, max DD -29.3%, szczyt 2026-10-02; sigma_d zrealizowana 4.19%
W7 (12-16.10): dzienne zwroty kapitalu x0,24: -6.14%, -1.94%, -7.57%, -4.81%, -6.38%; suma -26.84%; sigma_d jednostkowa koszyka W7 ex ante (60 ses.) 4.40%/d -> tydzien -2.7 sigma (ex ante)

## (3) Twardy stop 10% od wejscia na nogach o sigma_d 4-6%: czestosc trafienia w <=5 sesjach (zamkniecia, dolna granica wobec intraday)

| ticker | kierunek | sigma_d 250 | n okien (5 lat) | P(stop 10% w <=5 ses.) 5 lat | ostatnie 250 ses. | ostatnie 60 ses. | mediana dnia trafienia | sr. ruch po stopie do konca okna | udzial 'whipsaw' (na koniec okna strata <10%) | P(stop 15%) 5 lat | P(stop 20%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LITE | BUY | 6.24% | 1250 | **9.5%** | 22.4% | 26.7% | 3.0 | +2.73 p.p. | 35% | 3.9% | 2.0% |
| SNDK | BUY | 7.17% | 416 | **18.3%** | 24.0% | 28.3% | 3.0 | +0.60 p.p. | 33% | 9.6% | 5.5% |
| MU | BUY | 5.13% | 1249 | **9.0%** | 19.2% | 16.7% | 4.0 | +0.60 p.p. | 20% | 3.4% | 0.6% |
| MRVL | BUY | 5.03% | 1249 | **10.9%** | 14.8% | 18.3% | 3.0 | +0.13 p.p. | 24% | 4.1% | 1.5% |
| AMD | BUY | 4.29% | 1250 | **8.6%** | 10.8% | 11.7% | 4.0 | +0.30 p.p. | 19% | 2.6% | 0.6% |
| TER | BUY | 4.87% | 1250 | **7.5%** | 16.4% | 25.0% | 4.0 | +1.34 p.p. | 23% | 2.7% | 1.1% |
| APP | SELL | 4.56% | 1249 | **20.6%** | 17.2% | 0.0% | 3.0 | -0.62 p.p. | 21% | 10.2% | 5.3% |
| PANW | BUY | 3.10% | 1249 | **4.3%** | 6.4% | 8.3% | 4.0 | +1.15 p.p. | 30% | 1.1% | 0.4% |
| CSCO | BUY | 2.22% | 1245 | **1.3%** | 2.0% | 1.7% | 3.0 | +1.93 p.p. | 38% | 0.2% | 0.0% |
| PEP | SELL | 1.32% | 1250 | **0.2%** | 1.2% | 0.0% | 5.0 | -0.30 p.p. | 0% | 0.0% | 0.0% |
| CMCSA | SELL | 2.05% | 1248 | **0.6%** | 1.6% | 3.3% | 3.0 | +0.76 p.p. | 38% | 0.0% | 0.0% |
| SBUX | SELL | 1.74% | 1250 | **1.5%** | 0.0% | 0.0% | 4.0 | +0.92 p.p. | 21% | 0.4% | 0.4% |

Symetria: czestosc ruchu +10% w 5 sesjach (stop na SHORT) dla tych samych nazw, 5 lat:
- LITE: 17.5% (n=1250)
- SNDK: 43.3% (n=416)
- MU: 16.0% (n=1249)
- MRVL: 15.6% (n=1249)

Stop 10% w jednostkach sigma 5-sesyjnej (sigma_d60 x sqrt5), stan na 2026-10-16:
- LITE: sigma_d60 6.08%, sigma_5 13.6%, 10% = 0.74 sigma_5; 2 sigma_5 = 27.2%
- SNDK: sigma_d60 6.64%, sigma_5 14.8%, 10% = 0.67 sigma_5; 2 sigma_5 = 29.7%
- MU: sigma_d60 4.49%, sigma_5 10.0%, 10% = 1.00 sigma_5; 2 sigma_5 = 20.1%
- MRVL: sigma_d60 4.85%, sigma_5 10.9%, 10% = 0.92 sigma_5; 2 sigma_5 = 21.7%
- PEP: sigma_d60 1.24%, sigma_5 2.8%, 10% = 3.62 sigma_5; 2 sigma_5 = 5.5%
- CMCSA: sigma_d60 2.23%, sigma_5 5.0%, 10% = 2.00 sigma_5; 2 sigma_5 = 10.0%

Stop 10% + ponowne otwarcie nastepnego dnia (jak bot) vs trzymaj, okna 5 sesji, 5 lat, long:
- LITE: trafien 118/1249 (9.4%), sr. roznica (stop+reopen - trzymaj) w oknie z trafieniem -1.32 p.p. nogi; oczekiwany koszt na ~50 okien/rok: -6.24 p.p. nogi
- SNDK: trafien 75/415 (18.1%), sr. roznica (stop+reopen - trzymaj) w oknie z trafieniem +1.19 p.p. nogi; oczekiwany koszt na ~50 okien/rok: +10.74 p.p. nogi
- MU: trafien 112/1248 (9.0%), sr. roznica (stop+reopen - trzymaj) w oknie z trafieniem +0.35 p.p. nogi; oczekiwany koszt na ~50 okien/rok: +1.58 p.p. nogi
- MRVL: trafien 135/1248 (10.8%), sr. roznica (stop+reopen - trzymaj) w oknie z trafieniem -0.36 p.p. nogi; oczekiwany koszt na ~50 okien/rok: -1.94 p.p. nogi

## (4) Korelacja par w LONG a sigma koszyka

| W | rho60 LONG | rho250 LONG | rho60 SHORT | rho60 L-S (cross) | sigma60 strony LONG (5 nog po 24%) | gdyby rho=0 | N_eff LONG |
|---|---|---|---|---|---|---|---|
| W1 | 0.37 | 0.28 | 0.29 | -0.05 | 4.31% | 2.68% | 1.7 |
| W2 | 0.34 | 0.30 | 0.21 | -0.05 | 3.44% | 2.25% | 1.8 |
| W3 | 0.57 | 0.48 | 0.14 | -0.07 | 4.30% | 2.43% | 1.4 |
| W4 | 0.64 | 0.48 | 0.25 | -0.26 | 5.10% | 2.73% | 1.3 |
| W5 | 0.74 | 0.55 | 0.23 | -0.21 | 5.35% | 2.71% | 1.3 |
| W6 | 0.75 | 0.59 | 0.20 | -0.21 | 5.09% | 2.57% | 1.2 |
| W7 | 0.29 | 0.28 | 0.23 | -0.15 | 3.53% | 2.35% | 2.0 |
| W8 | 0.10 | 0.09 | 0.15 | 0.16 | 1.32% | 1.15% | 3.6 |

Wrazliwosc teoretyczna: 5 nog long po 24%, sigma_d nogi 4,5% (sr. W4-W7), jednakowa rho par:

| rho | sigma_d strony LONG | mnoznik vs rho=0 | N_eff |
|---|---|---|---|
| 0.00 | 2.41% | x1.00 | 5.0 |
| 0.20 | 3.24% | x1.34 | 2.8 |
| 0.35 | 3.74% | x1.55 | 2.1 |
| 0.50 | 4.18% | x1.73 | 1.7 |
| 0.60 | 4.45% | x1.84 | 1.5 |
| 0.75 | 4.83% | x2.00 | 1.2 |
| 0.90 | 5.18% | x2.14 | 1.1 |

## (5) Polityki sizingu i kill switcha: P(kill 12 tyg) przy zerowej alfie oraz wynik przy alfie

Alfa: 'spread_pp' tygodniowy koszyka jednostkowego (sr. zwrot 5 long + sr. 5 short, w p.p.) => zwrot jednostkowy sumy 10 nog = 10 x spread/100/... UWAGA: jednostka tu = SUMA 5 long - SUMA 5 short, czyli spread_pp x 5 / 100 na tydzien = spread_pp x 1,0 pp/d.
Alfa_d jednostkowa = spread_tyg(pp) x 5 / 100 / 5 = spread_tyg/100 na dzien. Scenariusze: 0; +1 p.p./tyg; +2 p.p./tyg (sr. W1-W7 = -0,52 p.p.; sr. W1-W6 +2,91 p.p.).

| polityka | sr. ALLOC | sigma_d kap. (sr.) | P(kill 12t) alfa 0 | P(kill 12t) alfa 0, start -21% | DD p95 12t alfa 0 | mediana wyniku 12t alfa +1pp/t | alfa +2pp/t | P(wynik>0) 12t alfa +2 | mediana 12t alfa -1pp/t | sr. 12t alfa +2 |
|---|---|---|---|---|---|---|---|---|---|---|
| ALLOC 0.24 staly | 0.240 | 4.23% | **60.7%** | 87% | -30.4% | +2.9% | +20.8% | 68% | -17.9% | +26.3% |
| ALLOC 0.16 staly | 0.160 | 2.82% | **28.7%** | 78% | -27.8% | +7.2% | +18.2% | 78% | -12.6% | +19.3% |
| ALLOC 0.12 staly | 0.120 | 2.12% | **11.3%** | 70% | -26.0% | +6.1% | +14.0% | 81% | -8.2% | +14.7% |
| ALLOC 0.10 staly | 0.100 | 1.76% | **4.9%** | 65% | -24.9% | +5.3% | +11.8% | 81% | -6.6% | +12.2% |
| ALLOC 0.08 staly | 0.080 | 1.41% | **1.2%** | 58% | -20.4% | +4.3% | +9.5% | 82% | -5.2% | +9.7% |
| ALLOC 0.06 staly | 0.060 | 1.06% | **0.1%** | 47% | -15.6% | +3.4% | +7.1% | 82% | -3.8% | +7.2% |
| ALLOC 0.12 + x0.5 przy DD<-10% | 0.120 | 2.12% | **1.0%** | 47% | -21.4% | +3.6% | +11.9% | 76% | -8.7% | +13.4% |
| ALLOC 0.10 + x0.5 przy DD<-10% | 0.100 | 1.76% | **0.2%** | 39% | -18.8% | +3.9% | +10.7% | 77% | -7.6% | +11.4% |
| ALLOC 0.24 + x0.5 przy DD<-10% | 0.240 | 4.23% | **33.9%** | 73% | -27.2% | +2.2% | +15.7% | 70% | -14.2% | +23.2% |
| vol-target 1.0%/d (cap 0.24) | 0.054 | 0.96% | **0.0%** | 38% | -12.8% | +3.0% | +6.4% | 84% | -3.4% | +6.5% |
| vol-target 1.5%/d (cap 0.24) | 0.081 | 1.43% | **0.5%** | 55% | -18.7% | +4.4% | +9.6% | 84% | -5.2% | +9.9% |
| vol-target 2.0%/d (cap 0.24) | 0.108 | 1.91% | **4.2%** | 65% | -24.2% | +5.7% | +12.8% | 83% | -7.1% | +13.4% |
| vol-target 1.5%/d (cap 0.12) | 0.076 | 1.34% | **0.3%** | 53% | -17.9% | +4.2% | +9.0% | 83% | -4.9% | +9.3% |
| vol-target 2.0%/d (cap 0.12) | 0.096 | 1.70% | **2.7%** | 63% | -22.8% | +5.1% | +11.3% | 82% | -6.4% | +11.8% |
| vol-target 1.5%/d (cap 0.12, floor 0.06) | 0.076 | 1.35% | **0.4%** | 54% | -18.0% | +4.2% | +9.1% | 83% | -5.0% | +9.3% |
| vol-target 1.5%/d + x0.5 przy DD<-10% | 0.081 | 1.43% | **0.0%** | 25% | -15.2% | +4.2% | +9.5% | 82% | -6.0% | +9.7% |
| vol-target 2.0%/d + x0.5 przy DD<-10% | 0.108 | 1.91% | **0.1%** | 38% | -18.3% | +4.5% | +11.9% | 79% | -7.9% | +12.6% |
| vol-target 1.0%/d + x0.5 przy DD<-10% | 0.054 | 0.96% | **0.0%** | 9% | -11.9% | +3.0% | +6.4% | 84% | -3.5% | +6.5% |

Uwaga: alfa +2 p.p./tyg to srednia W1-W6 (t=0,97, nieistotna); W1-W7 srednia -0,52 p.p. Mnoznik P&L: tydzien = 5 x ALLOC x spread_pp (0,24 -> 1,2x; 0,08 -> 0,4x).

### (5b) kill switch staly (od startu) vs kroczacy (od szczytu), 52 tyg, bootstrap

| ALLOC | alfa/tyg | P(kill 52t) kroczacy | P(kill 52t) staly | mediana wyniku kroczacy | mediana staly |
|---|---|---|---|---|---|
| 0.24 | +0 p.p. | 99.0% | 72.3% | -13.5% | -25.9% |
| 0.24 | +1 p.p. | 95.8% | 42.8% | -1.0% | +19.5% |
| 0.24 | +2 p.p. | 88.9% | 20.9% | +26.8% | +162.6% |
| 0.12 | +0 p.p. | 68.6% | 39.5% | -10.4% | -8.4% |
| 0.12 | +1 p.p. | 41.8% | 13.6% | +22.4% | +29.2% |
| 0.12 | +2 p.p. | 20.8% | 3.4% | +73.7% | +77.1% |
| 0.08 | +0 p.p. | 33.4% | 18.4% | -3.2% | -2.3% |
| 0.08 | +1 p.p. | 11.4% | 3.7% | +20.3% | +20.4% |
| 0.08 | +2 p.p. | 2.9% | 0.6% | +48.2% | +48.3% |

ALLOC 0,24, alfa 0: mediana dnia trafienia kill (sposrod sciezek zabitych w 60 ses.) = 31. sesja; 25% zabitych przed 19. sesja
