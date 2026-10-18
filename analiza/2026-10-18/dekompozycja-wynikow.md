# Dekompozycja wyników W1–W7 systemu NDX100 — czynniki, selekcja, szum, wykonanie

Data analizy: 18.10.2026. Gałąź `claude/gifted-lamport-iwzpop`. Wszystkie liczby policzone skryptami
(czysty Python, bez numpy — pandas/numpy niedostępne w środowisku), ścieżki niżej. Liczby z rachunku (kapitał, pozycje)
NIE występują — wyłącznie p.p. i % kapitału. W8 (D0 16.10) rozliczenia nie ma; policzono tylko jej ekspozycję ex ante.

## 0. Wynik w pięciu zdaniach

1. **To, co widzimy, to w pierwszej kolejności zakład czynnikowy, nie dziesięć niezależnych prognoz.** Spread koszyka
   ma ładunek +1,1…+2,1 na czynnik ^SOX−^NDX w każdym tygodniu (z 250 sesji przed D0); dzienna seria spreadu w oknach
   W1–W7 jest w 74 % wyjaśniana przez ^NDX + (^SOX−^NDX) (n = 34 dni), a dla samej konstrukcji koszyków na 250 sesjach przed
   D0 — w 60–81 %. Znak tygodniowego spreadu zgadzał się ze znakiem (^SOX−^NDX) w 7 z 7 tygodni (corr 0,90, n = 7).
2. **Selekcja nazw (reszta po czynnikach) jest nieodróżnialna od zera:** +0,61 p.p./tydz., sd 5,98, t = 0,27 (n = 7);
   trafienie reszty 40/70 = 57 % (Wilson 45,5–68,1 %, p = 0,28). Strona LONG ma resztę −1,25 p.p./nogę, SHORT +1,86 p.p./nogę
   (t 1,99 przy zawyżonej niezależności nóg) — jedyny ślad przewagi, ale zbyt słaby, by na nim budować.
3. **Łączny wynik to szum wokół zera:** 7 tygodni, średnia −0,52 p.p., sd 11,3, t = −0,12; w oknach znormalizowanych
   do 5 sesji od D0: średnia −2,09 p.p., t = −0,55; hit rate 33/70 = 47,1 % (Wilson 35,9–58,7 %). Bez W7: +1,08 p.p./tydz., t = 0,44.
   Przy sd ≈ 6–10 p.p. wykrycie przewagi +1 p.p./tydz. na poziomie t = 2 wymaga 140–400 tygodni.
4. **W7 (−21,15 p.p.) to zdarzenie ogonowe tej konkretnej konstrukcji:** z = −3,8 wobec rozkładu 5-sesyjnych spreadów tego
   składu z 250 sesji przed D0 i gorsze od najgorszego okna z ~1000 sesji (−16,5 p.p.). Rozkłada się na −11,5 p.p. czynników
   (beta +1,0, ^SOX−^NDX −7,2, defensywy −5,3) i −9,7 p.p. reszty idiosynkratycznej (LITE −12,2, PANW −11,2, APP −6,6, SBUX −6,2).
   Dźwignia 2,4× brutto zamienia 5-sesyjne sd konstrukcji 6,5–9,8 p.p. na 8–12 % kapitału tygodniowo — przy zerowej
   przewadze kill switch (−25 % od szczytu) w 26 tygodni ma 78–90 % szans.
5. **Wykonanie NIE pogorszyło wyniku — poprawiło:** w W7 opóźnienie wejścia (poniedziałek 12.10) dało +1,41 p.p., a stopy
   10 % z ponownymi otwarciami +4,78 p.p. względem trzymania od wejścia; seria „jak rachunek” ≈ −14,96 p.p. (≈ −17,9 % kapitału)
   wobec −21,15 od D0. Każdy stop realizuje −2,4 % kapitału (10 % × ALLOC 0,24); cztery stopy W7 = −9,6 % zrealizowane.
   `spread_fills_pp` z history (W6 +3,88, W7 −12,36) nie jest serią rachunku i nie należy go tak czytać.

## 1. Dane, definicje, skrypty

- Kursy: `scratchpad/dane/closes_5y.csv` (1257 sesji, 2 puste wiersze świąt 2026-05-25 i 2026-09-07 odrzucone; CMCSA bez
  zamknięcia 2026-09-03 → 2 dni mniej w serii dziennej W2). Zamknięcia D0/D+n zgodne co do centa z tabelami raportów
  (sprawdzono 15 par, w tym ^NDX). Dywidendy w oknach (z raportów): PEP 1,48 (4.09), NVDA 0,25 (10.09), AVGO 0,65 (21.09),
  CMCSA 0,33 (7.10), MU 0,15 (14.10) — zwrot całkowity spółki = (P_end + div)/P_D0 − 1, symetrycznie dla L i S.
- Składy koszyków: W1–W3 z `reports/raport-2026-W2..W4.html` (tabele rozliczeń), W4–W8 z `scratchpad/analiza/koszyki_historia.json`.
  Okna faktyczne: W1 26.08→28.08 (2 sesje), W2 28.08→4.09 (5), W3 4.09→11.09 (4, Labor Day), W4 11.09→28.09 (11), W5 28.09→2.10 (4),
  W6 2.10→9.10 (5), W7 9.10→16.10 (5).
- Zwrot pozycji = [P_end/P_D0 − 1] − [NDX_end/NDX_D0 − 1], dla shortów ze znakiem ujemnym; spread = śr. L + śr. S
  (= śr. zwrot L − śr. zwrot S, bo ^NDX się skraca — więc spread jest też zwrotem dolarowo-neutralnej pary L/S).
- Czynniki dzienne: F1 = r(^NDX); F2 = r(^SOX) − r(^NDX); F3 = śr.[r(XLP), r(XLU), r(XLV)] − r(QQQ). Ładunki nogi z OLS
  na 250 sesjach dziennych kończących się na D0 (włącznie). Składowa pozycji: sgn·[(b_NDX − 1)·R_NDX + b_SOX·F2 + b_DEF·F3],
  reszta = pozycja − składowe. Składowa „beta netto” w modelu 3-czynnikowym jest mała, bo F2 pochłania większość bety semis;
  dla porównania podano wariant 1-czynnikowy (β1_net × R_NDX).
- Skrypty (wszystkie w `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):
  `lib_dekomp.py` (OLS, Wilson, t), `dekompozycja.py` → `dekompozycja_out.md`, `dekompozycja_wyniki.json`;
  `wykonanie_w6_w7.py` → `wykonanie_out.md`; `rozklad_historyczny.py` → `rozklad_out.md`; `panel_momentum.py` → `panel_out.md`;
  `w8_ekspozycja.py` → `w8_out.md`.

## 2. Rozliczenie per noga i dekompozycja tygodnia (od D0, okna faktyczne)

Kolumny: β(1f) = beta do ^NDX z 1 czynnika; b_* = ładunki 3-czynnikowe; skł. = wkład do pozycji vs ^NDX w p.p.; reszta = część
idiosynkratyczna. Wiersz „spread” porównuje z `history` (Δ = 0,00 we wszystkich 7 tygodniach — rozliczenia w raportach są poprawne).

### W1  D0=2026-08-26 → 2026-08-28 (n=2)  ^NDX +0.71%  SOX−NDX -1.93 p.p.  DEF−QQQ -2.08 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | -0.59% | -1.31 | 2.91 | 1.11 | 1.65 | -0.12 | 0.66 | +0.08 | -3.19 | +0.26 | +1.55 |
| LITE | L | SEMI | -4.69% | -5.40 | 2.37 | 0.57 | 1.83 | 0.06 | 0.38 | -0.31 | -3.54 | -0.12 | -1.44 |
| CEG | L | UTIL | -0.99% | -1.71 | 0.94 | 1.49 | 0.42 | 0.92 | 0.22 | +0.35 | -0.81 | -1.93 | +0.68 |
| AMD | L | SEMI | -3.19% | -3.91 | 2.55 | 1.39 | 1.04 | -0.11 | 0.57 | +0.28 | -2.01 | +0.23 | -2.41 |
| MSFT | L | MEGA | +3.46% | +2.74 | 0.56 | 0.85 | -0.79 | -0.48 | 0.37 | -0.11 | +1.53 | +1.00 | +0.32 |
| INTU | S | SOFT | +3.52% | -2.81 | 0.03 | 0.88 | -1.35 | -0.47 | 0.32 | +0.08 | -2.61 | -0.99 | +0.71 |
| WDAY | S | SOFT | +7.32% | -6.61 | -0.05 | 0.92 | -1.56 | -0.59 | 0.36 | +0.06 | -3.02 | -1.22 | -2.42 |
| APP | S | SOFT | +3.13% | -2.42 | 1.47 | 1.46 | -1.07 | -1.02 | 0.25 | -0.33 | -2.06 | -2.13 | +2.10 |
| TSLA | S | AUTO | +0.85% | -0.13 | 1.55 | 1.86 | -0.36 | -0.06 | 0.45 | -0.62 | -0.70 | -0.12 | +1.30 |
| CMCSA | S | DEF | -0.51% | +1.23 | -0.13 | 0.99 | -0.33 | 0.73 | 0.15 | +0.01 | -0.64 | +1.53 | +0.34 |

spread = -4.06 p.p. (history: -4.06; Δ -0.00)  hit 2/10  β_net(3f) -0.14  b_SOX_net +1.76  b_DEF_net +0.33
dekompozycja 3f: beta -0.10 + SOX -3.41 + DEF -0.70 + reszta +0.15
wariant 1f: β1_net +1.29 × ^NDX +0.71% = +0.92 p.p.; reszta po samej becie -4.99

### W2  D0=2026-08-28 → 2026-09-04 (n=5)  ^NDX +0.38%  SOX−NDX +1.94 p.p.  DEF−QQQ -0.36 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | +8.98% | +8.60 | 2.89 | 1.12 | 1.64 | -0.10 | 0.66 | +0.05 | +3.18 | +0.04 | +5.33 |
| NVDA | L | SEMI | +5.89% | +5.51 | 1.32 | 0.83 | 0.01 | -0.44 | 0.48 | -0.06 | +0.03 | +0.16 | +5.39 |
| MSFT | L | MEGA | -2.69% | -3.07 | 0.56 | 0.85 | -0.79 | -0.48 | 0.37 | -0.06 | -1.54 | +0.18 | -1.65 |
| AMD | L | SEMI | +2.58% | +2.20 | 2.53 | 1.40 | 1.04 | -0.08 | 0.57 | +0.15 | +2.02 | +0.03 | +0.00 |
| CEG | L | UTIL | +8.03% | +7.65 | 0.93 | 1.49 | 0.42 | 0.93 | 0.22 | +0.19 | +0.81 | -0.34 | +6.99 |
| INTU | S | SOFT | -7.08% | +7.46 | 0.02 | 0.88 | -1.35 | -0.47 | 0.33 | +0.04 | +2.62 | -0.17 | +4.96 |
| APP | S | SOFT | +0.88% | -0.50 | 1.46 | 1.47 | -1.06 | -0.99 | 0.24 | -0.18 | +2.05 | -0.36 | -2.01 |
| TSLA | S | AUTO | +1.53% | -1.15 | 1.55 | 1.86 | -0.36 | -0.06 | 0.45 | -0.32 | +0.70 | -0.02 | -1.51 |
| CMCSA | S | DEF | -2.11% | +2.48 | -0.14 | 0.99 | -0.34 | 0.74 | 0.15 | +0.00 | +0.66 | +0.27 | +1.55 |
| PEP | S | DEF | -1.39% | +1.77 | -0.31 | 0.84 | -0.11 | 0.98 | 0.38 | +0.06 | +0.21 | +0.35 | +1.14 |

spread = +6.19 p.p. (history: +6.19; Δ -0.00)  hit 7/10  β_net(3f) -0.07  b_SOX_net +1.11  b_DEF_net -0.07
dekompozycja 3f: beta -0.03 + SOX +2.15 + DEF +0.03 + reszta +4.04
wariant 1f: β1_net +1.13 × ^NDX +0.38% = +0.43 p.p.; reszta po samej becie +5.76

### W3  D0=2026-09-04 → 2026-09-11 (n=4)  ^NDX -0.59%  SOX−NDX +1.35 p.p.  DEF−QQQ -1.62 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | -4.07% | -3.47 | 2.89 | 1.11 | 1.64 | -0.11 | 0.66 | -0.07 | +2.21 | +0.18 | -5.80 |
| NVDA | L | SEMI | -5.13% | -4.54 | 1.32 | 0.83 | 0.02 | -0.44 | 0.48 | +0.10 | +0.02 | +0.71 | -5.37 |
| AMD | L | SEMI | +8.07% | +8.67 | 2.54 | 1.38 | 1.07 | -0.08 | 0.58 | -0.22 | +1.45 | +0.14 | +7.31 |
| AVGO | L | SEMI | +1.14% | +1.74 | 1.59 | 0.65 | 0.42 | -0.49 | 0.49 | +0.21 | +0.56 | +0.80 | +0.17 |
| STX | L | SEMI | -2.25% | -1.66 | 2.03 | 0.32 | 1.30 | -0.38 | 0.43 | +0.40 | +1.75 | +0.61 | -4.42 |
| TSLA | S | AUTO | +3.21% | -3.80 | 1.56 | 1.90 | -0.43 | -0.10 | 0.45 | +0.53 | +0.58 | -0.16 | -4.76 |
| INTU | S | SOFT | -3.35% | +2.75 | 0.03 | 0.87 | -1.36 | -0.50 | 0.33 | -0.08 | +1.83 | -0.81 | +1.80 |
| SBUX | S | DEF | -5.48% | +4.89 | 0.25 | 1.08 | -0.06 | 0.72 | 0.13 | +0.05 | +0.09 | +1.17 | +3.59 |
| APP | S | SOFT | +1.06% | -1.66 | 1.44 | 1.45 | -0.99 | -0.93 | 0.23 | +0.27 | +1.34 | -1.51 | -1.75 |
| CMCSA | S | DEF | -4.87% | +4.28 | -0.13 | 1.01 | -0.35 | 0.74 | 0.16 | +0.01 | +0.47 | +1.20 | +2.59 |

spread = +1.44 p.p. (history: +1.44; Δ +0.00)  hit 5/10  β_net(3f) -0.40  b_SOX_net +1.53  b_DEF_net -0.29
dekompozycja 3f: beta +0.24 + SOX +2.06 + DEF +0.47 + reszta -1.33
wariant 1f: β1_net +1.44 × ^NDX -0.59% = -0.86 p.p.; reszta po samej becie +2.30

### W4  D0=2026-09-11 → 2026-09-28 (n=11)  ^NDX +3.09%  SOX−NDX +2.33 p.p.  DEF−QQQ -4.75 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | +8.07% | +4.98 | 2.87 | 1.06 | 1.65 | -0.13 | 0.66 | +0.18 | +3.85 | +0.62 | +0.32 |
| AMD | L | SEMI | +17.77% | +14.68 | 2.54 | 1.34 | 1.09 | -0.10 | 0.59 | +1.04 | +2.54 | +0.48 | +10.62 |
| AVGO | L | SEMI | -3.25% | -6.34 | 1.60 | 0.72 | 0.37 | -0.48 | 0.51 | -0.88 | +0.86 | +2.28 | -8.61 |
| MRVL | L | SEMI | +6.69% | +3.60 | 2.47 | 0.81 | 1.59 | -0.05 | 0.55 | -0.58 | +3.70 | +0.23 | +0.24 |
| LITE | L | SEMI | -0.62% | -3.71 | 2.36 | 0.53 | 1.87 | 0.06 | 0.39 | -1.47 | +4.35 | -0.28 | -6.31 |
| INTU | S | SOFT | -16.22% | +19.32 | 0.04 | 0.91 | -1.38 | -0.49 | 0.33 | +0.27 | +3.21 | -2.32 | +18.16 |
| SBUX | S | DEF | -3.51% | +6.61 | 0.26 | 1.13 | -0.07 | 0.75 | 0.14 | -0.39 | +0.16 | +3.57 | +3.26 |
| CMCSA | S | DEF | -13.53% | +16.62 | -0.13 | 1.06 | -0.36 | 0.77 | 0.16 | -0.20 | +0.85 | +3.67 | +12.30 |
| APP | S | SOFT | -4.85% | +7.95 | 1.43 | 1.46 | -1.02 | -0.94 | 0.24 | -1.42 | +2.39 | -4.48 | +11.47 |
| ADSK | S | SOFT | -2.45% | +5.55 | 0.13 | 1.16 | -0.98 | 0.04 | 0.31 | -0.50 | +2.28 | +0.19 | +3.57 |

spread = +13.85 p.p. (history: +13.85; Δ -0.00)  hit 8/10  β_net(3f) -0.25  b_SOX_net +2.08  b_DEF_net -0.17
dekompozycja 3f: beta -0.79 + SOX +4.84 + DEF +0.79 + reszta +9.01
wariant 1f: β1_net +2.02 × ^NDX +3.09% = +6.26 p.p.; reszta po samej becie +7.59

### W5  D0=2026-09-28 → 2026-10-02 (n=4)  ^NDX +1.75%  SOX−NDX +3.63 p.p.  DEF−QQQ -2.98 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | +1.98% | +0.23 | 2.85 | 1.06 | 1.61 | -0.15 | 0.67 | +0.10 | +5.85 | +0.45 | -6.17 |
| AMD | L | SEMI | +4.28% | +2.53 | 2.58 | 1.39 | 1.05 | -0.13 | 0.59 | +0.68 | +3.80 | +0.38 | -2.33 |
| ALAB | L | SEMI | -0.28% | -2.03 | 3.00 | 0.54 | 1.40 | -0.97 | 0.48 | -0.80 | +5.09 | +2.89 | -9.22 |
| STX | L | SEMI | -7.87% | -9.62 | 1.98 | 0.27 | 1.33 | -0.34 | 0.43 | -1.29 | +4.84 | +1.02 | -14.20 |
| TER | L | SEMI | +11.90% | +10.14 | 2.51 | 1.16 | 1.76 | 0.41 | 0.65 | +0.29 | +6.38 | -1.23 | +4.70 |
| SBUX | S | DEF | -0.59% | +2.34 | 0.24 | 1.14 | -0.06 | 0.80 | 0.15 | -0.24 | +0.20 | +2.38 | +0.01 |
| NFLX | S | MEDIA | -3.13% | +4.89 | 0.11 | 1.27 | -0.70 | 0.43 | 0.21 | -0.48 | +2.54 | +1.28 | +1.55 |
| PEP | S | DEF | -2.03% | +3.79 | -0.28 | 0.84 | -0.11 | 0.96 | 0.38 | +0.28 | +0.41 | +2.85 | +0.25 |
| CMCSA | S | DEF | -1.01% | +2.76 | -0.13 | 1.02 | -0.35 | 0.75 | 0.15 | -0.04 | +1.27 | +2.23 | -0.70 |
| APP | S | SOFT | -12.98% | +14.74 | 1.40 | 1.42 | -1.03 | -0.97 | 0.24 | -0.74 | +3.73 | -2.89 | +14.64 |

spread = +5.95 p.p. (history: +5.95; Δ +0.00)  hit 8/10  β_net(3f) -0.26  b_SOX_net +1.88  b_DEF_net -0.63
dekompozycja 3f: beta -0.45 + SOX +6.82 + DEF +1.87 + reszta -2.29
wariant 1f: β1_net +2.32 × ^NDX +1.75% = +4.07 p.p.; reszta po samej becie +1.89

### W6  D0=2026-10-02 → 2026-10-09 (n=5)  ^NDX +0.24%  SOX−NDX -4.54 p.p.  DEF−QQQ +3.23 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | -4.27% | -4.51 | 2.84 | 0.96 | 1.59 | -0.25 | 0.66 | -0.01 | -7.22 | -0.80 | +3.51 |
| LITE | L | SEMI | +1.65% | +1.41 | 2.31 | 0.43 | 1.93 | 0.07 | 0.39 | -0.14 | -8.74 | +0.22 | +10.07 |
| TER | L | SEMI | -10.32% | -10.57 | 2.53 | 1.18 | 1.76 | 0.42 | 0.65 | +0.04 | -8.00 | +1.34 | -3.95 |
| AMAT | L | SEMI | -6.11% | -6.36 | 2.15 | 0.85 | 1.39 | 0.10 | 0.76 | -0.04 | -6.31 | +0.33 | -0.34 |
| AMD | L | SEMI | -4.07% | -4.32 | 2.58 | 1.42 | 1.04 | -0.09 | 0.59 | +0.10 | -4.74 | -0.30 | +0.62 |
| APP | S | SOFT | +3.29% | -3.04 | 1.39 | 1.44 | -1.02 | -0.94 | 0.23 | -0.11 | -4.62 | +3.02 | -1.34 |
| NFLX | S | MEDIA | +4.83% | -4.59 | 0.11 | 1.31 | -0.69 | 0.48 | 0.21 | -0.08 | -3.13 | -1.54 | +0.16 |
| PAYX | S | DEF | +5.09% | -4.85 | -0.18 | 0.70 | -0.69 | 0.17 | 0.27 | +0.07 | -3.13 | -0.54 | -1.26 |
| CMCSA | S | DEF | -2.69% | +2.93 | -0.12 | 1.03 | -0.35 | 0.75 | 0.15 | -0.01 | -1.57 | -2.42 | +6.93 |
| SBUX | S | DEF | -4.18% | +4.43 | 0.24 | 1.18 | -0.05 | 0.84 | 0.16 | -0.04 | -0.23 | -2.72 | +7.42 |

spread = -5.89 p.p. (history: -5.89; Δ -0.00)  hit 3/10  β_net(3f) -0.16  b_SOX_net +2.10  b_DEF_net -0.21
dekompozycja 3f: beta -0.04 + SOX -9.54 + DEF -0.68 + reszta +4.36
wariant 1f: β1_net +2.19 × ^NDX +0.24% = +0.54 p.p.; reszta po samej becie -6.43

### W7  D0=2026-10-09 → 2026-10-16 (n=5)  ^NDX -5.49%  SOX−NDX -5.92 p.p.  DEF−QQQ +8.99 p.p.
| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MU | L | SEMI | -14.58% | -9.09 | 2.85 | 0.98 | 1.59 | -0.25 | 0.66 | +0.11 | -9.43 | -2.22 | +2.46 |
| LITE | L | SEMI | -25.31% | -19.82 | 2.34 | 0.53 | 1.93 | 0.13 | 0.39 | +2.59 | -11.42 | +1.21 | -12.19 |
| MRVL | L | SEMI | -17.24% | -11.75 | 2.50 | 1.01 | 1.57 | 0.09 | 0.56 | -0.06 | -9.27 | +0.77 | -3.18 |
| PANW | L | CYBER | -18.33% | -12.84 | 0.83 | 0.72 | -0.85 | -0.92 | 0.27 | +1.52 | +5.04 | -8.24 | -11.17 |
| CSCO | L | SIECI | -9.29% | -3.80 | 0.71 | 0.56 | 0.12 | -0.03 | 0.16 | +2.44 | -0.71 | -0.25 | -5.29 |
| CMCSA | S | DEF | +6.00% | -11.49 | -0.16 | 0.94 | -0.34 | 0.70 | 0.14 | -0.36 | -2.00 | -6.33 | -2.81 |
| SBUX | S | DEF | +7.46% | -12.95 | 0.24 | 1.14 | -0.02 | 0.83 | 0.15 | +0.77 | -0.10 | -7.46 | -6.16 |
| PEP | S | DEF | +4.38% | -9.87 | -0.26 | 0.87 | -0.10 | 0.97 | 0.39 | -0.74 | -0.59 | -8.72 | +0.17 |
| TMUS | S | DEF | +7.08% | -12.57 | -0.36 | 0.38 | -0.28 | 0.43 | 0.11 | -3.41 | -1.68 | -3.83 | -3.64 |
| APP | S | SOFT | -3.94% | -1.55 | 1.43 | 1.40 | -0.97 | -0.95 | 0.24 | +2.22 | -5.74 | +8.56 | -6.59 |

spread = -21.15 p.p. (history: -21.15; Δ +0.00)  hit 0/10  β_net(3f) -0.19  b_SOX_net +1.21  b_DEF_net -0.59
dekompozycja 3f: beta +1.02 + SOX -7.18 + DEF -5.30 + reszta -9.68
wariant 1f: β1_net +1.67 × ^NDX -5.49% = -9.16 p.p.; reszta po samej becie -11.98



### Podsumowanie dekompozycji (p.p.)

| tydz. | n | spread | ^NDX | ^SOX−^NDX | DEF−QQQ | skł. beta (3f) | skł. SOX | skł. DEF | reszta | wariant 1f: β1_net × ^NDX | hit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 2 | −4,06 | +0,71 % | −1,93 | −2,08 | −0,10 | −3,41 | −0,70 | +0,15 | 1,29 × 0,71 = +0,92 | 2/10 |
| W2 | 5 | +6,19 | +0,38 % | +1,94 | −0,36 | −0,03 | +2,15 | +0,03 | +4,04 | +0,43 | 7/10 |
| W3 | 4 | +1,44 | −0,59 % | +1,35 | −1,62 | +0,24 | +2,06 | +0,47 | −1,33 | −0,86 | 5/10 |
| W4 | 11 | +13,85 | +3,09 % | +2,33 | −4,75 | −0,79 | +4,84 | +0,79 | +9,01 | +6,26 | 8/10 |
| W5 | 4 | +5,95 | +1,75 % | +3,63 | −2,98 | −0,45 | +6,82 | +1,87 | −2,29 | +4,07 | 8/10 |
| W6 | 5 | −5,89 | +0,24 % | −4,54 | +3,23 | −0,04 | −9,54 | −0,68 | +4,36 | +0,54 | 3/10 |
| W7 | 5 | −21,15 | −5,49 % | −5,92 | +8,99 | +1,02 | −7,18 | −5,30 | −9,68 | −9,16 | 0/10 |
| **suma** | | **−3,67** | | | | **−0,15** | **−6,26** | **−3,52** | **+4,25** | **+2,20** | **33/70** |

Odczyt: ładunek netto na ^SOX−^NDX wynosił +1,11 (W2) … +2,10 (W6); na defensywy −0,07 … −0,63 (short defensyw = ujemny ładunek,
co w W7 przy DEF−QQQ +8,99 p.p. kosztowało −5,3 p.p.). Suma części czynnikowej −7,93 p.p., reszty +4,25 p.p. W tygodniach
„dobrych” (W2, W4) reszta była dodatnia i duża (INTU, CMCSA, AMD, CEG); w W5 wynik +5,95 to w całości czynnik (reszta −2,29: STX −14,2,
ALAB −9,2); w W6 reszta +4,36 ratowała czynnik −9,54; w W7 oba składniki poszły w dół.

## 3. Normalizacja do 5 sesji i statystyki

| tydz. | D0 | okno faktyczne (n) i spread | D0→D+5 na papierze | per-sesja ×5 |
|---|---|---|---|---|
| W1 | D0 2026-08-26 | koniec faktyczny 2026-08-28 (n=2) -4.06 | D+5 2026-09-02 (n=5) -3.26 hit 5/10 | per-sesja×5 -10.16 |
| W2 | D0 2026-08-28 | koniec faktyczny 2026-09-04 (n=5) +6.19 | D+5 2026-09-04 (n=5) +6.19 hit 7/10 | per-sesja×5 +6.19 |
| W3 | D0 2026-09-04 | koniec faktyczny 2026-09-11 (n=4) +1.44 | D+5 2026-09-14 (n=5) -3.85 hit 3/10 | per-sesja×5 +1.80 |
| W4 | D0 2026-09-11 | koniec faktyczny 2026-09-28 (n=11) +13.85 | D+5 2026-09-18 (n=5) +7.29 hit 7/10 | per-sesja×5 +6.30 |
| W5 | D0 2026-09-28 | koniec faktyczny 2026-10-02 (n=4) +5.95 | D+5 2026-10-05 (n=5) +6.04 hit 8/10 | per-sesja×5 +7.44 |
| W6 | D0 2026-10-02 | koniec faktyczny 2026-10-09 (n=5) -5.89 | D+5 2026-10-09 (n=5) -5.89 hit 3/10 | per-sesja×5 -5.89 |
| W7 | D0 2026-10-09 | koniec faktyczny 2026-10-16 (n=5) -21.15 | D+5 2026-10-16 (n=5) -21.15 hit 0/10 | per-sesja×5 -21.15 |


Uwaga: W3 „D+5” = 14.09 to pierwsza sesja PO rotacji (dzień paniki po apelu liderów AI) — tylko na papierze. W4 D+5 = 18.09
(+7,29 p.p.) zgadza się z liczbą podaną w raporcie W5. W5 D+5 = 5.10 (+6,04) również na papierze.

| seria | n | średnia p.p. | sd | t | p (dwustr.) | suma |
|---|---|---|---|---|---|---|
| surowa (okna 2/5/4/11/4/5/5) | n=7 | śr. -0.52 | sd 11.28 | t = -0.12 | p ≈ 0.91 | suma -3.67 |
| D0→D+5 na papierze (wszystkie 7) | n=7 | śr. -2.09 | sd 10.04 | t = -0.55 | p ≈ 0.60 | suma -14.64 |
| tylko pełne 5-ses. okna faktyczne (W2,W6,W7) | n=3 | śr. -6.95 | sd 13.70 | t = -0.88 | p ≈ 0.47 | suma -20.85 |
| per-sesja ×5 (surowa/n×5) | n=7 | śr. -2.21 | sd 10.70 | t = -0.55 | p ≈ 0.60 | suma -15.47 |
| D0→D+5 bez W7 | n=6 | śr. +1.08 | sd 6.02 | t = 0.44 | p ≈ 0.68 | suma +6.51 |
| tylko strona LONG (śr. poz. L, okna faktyczne) | n=7 | śr. -1.58 | sd 5.26 | t = -0.79 | p ≈ 0.46 | suma -11.03 |
| tylko strona SHORT (śr. poz. S, okna faktyczne) | n=7 | śr. +1.05 | sd 6.53 | t = 0.43 | p ≈ 0.69 | suma +7.35 |
| reszta idiosynkratyczna spreadu (3f) | n=7 | śr. +0.61 | sd 5.98 | t = 0.27 | p ≈ 0.80 | suma +4.25 |
| część czynnikowa spreadu (beta+SOX+DEF) | n=7 | śr. -1.13 | sd 7.63 | t = -0.39 | p ≈ 0.71 | suma -7.93 |


### Hit rate (Wilson 95%)

| grupa | trafienia | Wilson 95% | p dwumianowy |
|---|---|---|---|
| wszystkie nogi | 33/70 = 47.1% | Wilson [35.9%, 58.7%] | p dwumianowy vs 50% = 0.72 |
| LONG | 14/35 = 40.0% | Wilson [25.6%, 56.4%] | p dwumianowy vs 50% = 0.31 |
| SHORT | 19/35 = 54.3% | Wilson [38.2%, 69.5%] | p dwumianowy vs 50% = 0.74 |
| bez W7 | 33/60 = 55.0% | Wilson [42.5%, 66.9%] | p dwumianowy vs 50% = 0.52 |
| W1–W6 LONG | 14/30 = 46.7% | Wilson [30.2%, 63.9%] | p dwumianowy vs 50% = 0.86 |
| W1–W6 SHORT | 19/30 = 63.3% | Wilson [45.5%, 78.1%] | p dwumianowy vs 50% = 0.20 |
| trafienie RESZTY (po odjęciu beta/SOX/DEF) | 40/70 = 57.1% | Wilson [45.5%, 68.1%] | p = 0.28 |

Tygodnie z dodatnim spreadem: 4/7; p(≥4 z 7 przy 50%) = 0.50


Interpretacja: żadna seria nie odbiega od zera. Hit rate 47 % z przedziałem 36–59 % obejmuje zarówno „brak umiejętności”, jak i cel
rutyny 55–60 %. Trafienie reszty (57 %) jest wyższe niż trafienie surowe, bo odjęcie czynnika SOX zmienia znak kilku nóg W6–W7 —
ale p = 0,28. Strona LONG: 14/35 (40 %) surowo i reszta −1,25 p.p./nogę; strona SHORT: 19/35 i reszta +1,86 p.p./nogę (bez W7 +2,80,
t 2,89 przy założeniu niezależności 30 nóg — zawyżone, nogi z jednego tygodnia są skorelowane). Hipoteza „przewaga po stronie short”
jest najlepiej umotywowanym z słabych sygnałów; do rejestru hipotez, nie do reguł.

## 4. Udział wariancji: czynniki vs selekcja

n=7 tygodni: var(spread)=127.3, var(czynniki)=58.2 (46%), var(reszta)=35.8 (28%), 2cov=33.4 (26%); corr(czynniki,spread)=0.87, corr(reszta,spread)=0.78
  składnik beta×NDX: śr. -0.02 p.p., sd 0.57, corr ze spreadem -0.90
  składnik SOX−NDX: śr. -0.61 p.p., sd 6.20, corr ze spreadem +0.82
  składnik DEF−QQQ: śr. -0.50 p.p., sd 2.30, corr ze spreadem +0.90
  regresja tygodniowa spread ~ NDX: R² 0.83 (adj 0.79), współczynniki [3.8] (n=7, k=2 — ilustracja, nie dowód)
  regresja tygodniowa spread ~ NDX+SOX−NDX: R² 0.95 (adj 0.93), współczynniki [2.25, 1.56] (n=7, k=3 — ilustracja, nie dowód)
  regresja tygodniowa spread ~ NDX+SOX−NDX+DEF: R² 0.95 (adj 0.91), współczynniki [2.74, 1.78, 0.45] (n=7, k=4 — ilustracja, nie dowód)


Wniosek z n = 7: wariancja części czynnikowej to 46 % wariancji spreadu, reszty 28 %, kowariancja 26 % (reszta jest DODATNIO
skorelowana z czynnikiem, 0,78 — gdy półprzewodniki spadają, wybrane nazwy spadają bardziej, niż mówi ich 250-sesyjny ładunek;
czyli ładunki „spokojnego roku” niedoszacowują ekspozycji w ruchu gwałtownym, a faktyczny udział czynnika jest raczej > 50 %).
Regresje tygodniowe (R² 0,83–0,95) przy n = 7 i k = 2–4 są ilustracją, nie dowodem. Twardsza miara to serie dzienne:

| koszyk | R² NDX (250 przed D0) | R² NDX+SOX | R² NDX+SOX+DEF | β_spread | b_SOX | b_DEF | σ_d spreadu | sd 5-ses. spreadu (√5) | w oknie: dni, R² 3f |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 0.21 | 0.65 | 0.65 | -0.15 | 1.78 | 0.34 | 3.46% | 7.73 p.p. | 2, 0.91 |
| W2 | 0.29 | 0.59 | 0.60 | -0.05 | 1.11 | -0.06 | 2.63% | 5.87 p.p. | 3, -31.43 |
| W3 | 0.31 | 0.71 | 0.72 | -0.39 | 1.53 | -0.28 | 3.22% | 7.20 p.p. | 4, 0.6 |
| W4 | 0.37 | 0.80 | 0.81 | -0.27 | 2.09 | -0.17 | 4.14% | 9.25 p.p. | 11, 0.86 |
| W5 | 0.45 | 0.80 | 0.81 | -0.26 | 1.88 | -0.63 | 4.35% | 9.72 p.p. | 4, -1.37 |
| W6 | 0.40 | 0.81 | 0.81 | -0.18 | 2.11 | -0.21 | 4.39% | 9.82 p.p. | 5, 0.29 |
| W7 | 0.39 | 0.66 | 0.67 | -0.19 | 1.21 | -0.59 | 3.31% | 7.40 p.p. | 5, -1.42 |

Pooled dni w oknach W1–W7 (n=34): R² NDX 0.36; NDX+SOX−NDX 0.74; +DEF 0.75; współcz. 3f: β -0.32 (SE 0.61), b_SOX 1.72 (SE 0.29), b_DEF -0.65 (SE 0.50); α dzienna +0.047% (t 0.15); σ reszty 1.81%
Pooled: średni dzienny spread -0.251% , sd 3.49%, t = -0.42 (n=34 dni)


Odczyt: (i) sama beta do ^NDX tłumaczy 21–45 % dziennej wariancji spreadu konstrukcji, dodanie ^SOX−^NDX podnosi R² do 59–81 %,
defensywy prawie nic nie dodają w dniu (ale liczą się w tygodniu W7); (ii) pooled w oknach R² 0,74 z b_SOX 1,72 ± 0,29 — ładunek jest
istotny statystycznie (t ≈ 6) w przeciwieństwie do alfy (t 0,15); (iii) σ 5-sesyjna konstrukcji 5,9–9,8 p.p. ⇒ przy ALLOC 0,24
(1,2 × spread) sd tygodnia rachunku 7–12 %. Zestawienie z R² okien 5-sesyjnych nienakładających się (sekcja 6): 0,41–0,72.

## 5. Koncentracja blokowa a wynik

Bloki (taksonomia własna, zgodna z `industry` w `data/tv-screen-2026-W8.json`): SEMI = MU, AMD, NVDA, AVGO, MRVL, LITE, ALAB, STX, TER, AMAT;
DEF = PEP, CMCSA, SBUX, TMUS, PAYX; MEDIA = NFLX; SOFT = INTU, WDAY, APP, ADSK; CYBER = PANW; SIECI = CSCO; AUTO = TSLA; UTIL = CEG; MEGA = MSFT.

| tydz. | longi SEMI | shorty DEF+MEDIA | shorty SOFT | β_net(3f) | b_SOX_net | spread | SOX−NDX w oknie | skł. SOX | skł. beta |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 3/5 | 1/5 | 3/5 | -0.14 | +1.76 | -4.06 | -1.93 | -3.41 | -0.10 |
| W2 | 3/5 | 2/5 | 2/5 | -0.07 | +1.11 | +6.19 | +1.94 | +2.15 | -0.03 |
| W3 | 5/5 | 2/5 | 2/5 | -0.40 | +1.53 | +1.44 | +1.35 | +2.06 | +0.24 |
| W4 | 5/5 | 2/5 | 3/5 | -0.25 | +2.08 | +13.85 | +2.33 | +4.84 | -0.79 |
| W5 | 5/5 | 4/5 | 1/5 | -0.26 | +1.88 | +5.95 | +3.63 | +6.82 | -0.45 |
| W6 | 5/5 | 4/5 | 1/5 | -0.16 | +2.10 | -5.89 | -4.54 | -9.54 | -0.04 |
| W7 | 3/5 | 4/5 | 1/5 | -0.19 | +1.21 | -21.15 | -5.92 | -7.18 | +1.02 |

Tygodnie z ≥4 longami SEMI: 4/7 (W3, W4, W5, W6); śr. spread +3.84 vs pozostałe -6.34
Tygodnie z ≥4 shortami DEF/MEDIA: 3/7 (W5, W6, W7); śr. spread -7.03 vs pozostałe +4.35
Oba naraz (≥4 SEMI long i ≥4 DEF short): 2/7 (W5, W6); śr. spread +0.03
corr(b_SOX_net, spread) = +0.37; corr(SOX−NDX w oknie, spread) = +0.90; corr(^NDX w oknie, spread) = +0.91; corr(DEF−QQQ, spread) = -0.92


Korelacje par (60 sesji przed D0) i efektywna liczba nóg:

| koszyk | śr. ρ par LONG (60 ses.) | śr. ρ par SHORT | ρ(śr. LONG, śr. SHORT) | efektywna liczba nóg LONG ≈ 5/(1+4ρ) |
|---|---|---|---|---|
| W1 | 0.37 | 0.29 | -0.12 | 2.0 |
| W2 | 0.34 | 0.21 | +0.01 | 2.1 |
| W3 | 0.56 | 0.14 | -0.09 | 1.5 |
| W4 | 0.64 | 0.25 | -0.45 | 1.4 |
| W5 | 0.75 | 0.22 | -0.27 | 1.3 |
| W6 | 0.75 | 0.19 | -0.35 | 1.2 |
| W7 | 0.29 | 0.23 | -0.32 | 2.3 |


Odczyt: (1) ≥ 4 longów SEMI w 4/7 tygodni (W3–W6), 5/5 w W3–W6; ≥ 4 shortów DEF/MEDIA w 3/7 (W5–W7); oba naraz W5 i W6.
(2) Tygodnie SEMI-koncentracji miały śr. +3,84 p.p., pozostałe −6,34 — ale to nie zasługa koncentracji, lecz tego, że W1 i W7 (najgorsze)
wypadły na ruchach ^SOX−^NDX −1,9 i −5,9 p.p. (corr spreadu z ^SOX−^NDX w oknie 0,90; z DEF−QQQ −0,92). W7 miał „tylko” 3/5 SEMI,
ale PANW i CSCO zachowały się jak SEMI (reszty −11,2 i −5,3). (3) Korelacja par w LONG 0,56–0,75 w W3–W6 → 1,2–1,5 efektywnej nogi
z pięciu; W7 ρ 0,29 (2,3 nogi) i mimo to 0/10 — dywersyfikacja „po tickerach” nie chroni, gdy wszystkie nogi mają ten sam znak ładunku SOX/DEF.

## 6. Rozkład historyczny konstrukcji: szum czy ogon?

| koszyk | wynik faktyczny (D+5 na papierze) | 250 sesji przed D0: śr. / sd 5-ses. spreadu | z | percentyl empiryczny (okna nakładające się) | min hist. | ~1000 sesji: sd / z / percentyl / min | R² 3f okien nienakł. (n) |
|---|---|---|---|---|---|---|---|
| W1 | -3.26 | +2.68 / 7.04 | -0.84 | 19.4% (n=248) | -20.79 | 5.17 / -0.75 / 19.8% / -20.79 | 0.47 (n=194; b_SOX 1.36, β -0.10) |
| W2 | +6.19 | +1.83 / 5.78 | +0.75 | 79.4% (n=248) | -13.17 | 4.78 / +1.15 / 89.6% / -22.77 | 0.41 (n=200; b_SOX 1.21, β -0.10) |
| W3 | -3.85 | +2.62 / 7.17 | -0.90 | 16.2% (n=247) | -16.94 | 5.39 / -0.89 / 14.9% / -23.66 | 0.55 (n=200; b_SOX 1.56, β -0.23) |
| W4 | +7.29 | +3.47 / 8.26 | +0.46 | 69.0% (n=248) | -28.22 | 5.98 / +1.06 / 87.9% / -28.22 | 0.65 (n=194; b_SOX 1.71, β -0.57) |
| W5 | +6.04 | +3.61 / 9.32 | +0.26 | 57.7% (n=248) | -22.79 | 7.29 / +0.62 / 75.7% / -22.79 | 0.72 (n=126; b_SOX 1.97, β -0.53) |
| W6 | -5.89 | +3.86 / 8.73 | -1.12 | 12.1% (n=248) | -25.34 | 6.04 / -1.12 / 9.5% / -25.34 | 0.67 (n=196; b_SOX 1.72, β -0.56) |
| W7 | -21.15 | +3.28 / 6.47 | -3.78 | 0.0% (n=248) | -16.30 | 5.05 / -4.37 / 0.0% / -16.51 | 0.51 (n=194; b_SOX 1.01, β -0.45) |


Odczyt: W1–W6 mieszczą się w |z| ≤ 1,2 (percentyle 10–90 %) — czysty szum wokół dodatniego dryfu konstrukcji. W7 to z = −3,8
(250 sesji) / −4,4 (1000 sesji), poniżej minimum z czterech lat tej konstrukcji (−16,5 p.p.). Przy sd 6,5 p.p. taki tydzień to
realizacja ryzyka ogonowego skoncentrowanego zakładu, nie „zwykła losowość 5 sesji”. Druga obserwacja: średni 5-sesyjny spread
tych konstrukcji w roku przed D0 wynosił +1,8…+3,9 p.p. — koszyki miały wbudowany dodatni dryf (hossa półprzewodników 2025–26),
więc dodatnie W2–W5 nie wymagają hipotezy umiejętności: są zgodne z kontynuacją dryfu czynnika.

Średnia historyczna 5-ses. spreadu konstrukcji (250 sesji przed D0, okna nakładające się) pokazuje, czy koszyk był „kupnem tego, co rosło”: 
- W1: śr. 5-ses. spread rok przed D0 +2.68 p.p.; ostatnie 20 sesji +0.55 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +21.87 p.p.; wynik faktyczny -4.06
- W2: śr. 5-ses. spread rok przed D0 +1.83 p.p.; ostatnie 20 sesji +1.79 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +3.14 p.p.; wynik faktyczny +6.19
- W3: śr. 5-ses. spread rok przed D0 +2.62 p.p.; ostatnie 20 sesji -0.42 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: -0.05 p.p.; wynik faktyczny +1.44
- W4: śr. 5-ses. spread rok przed D0 +3.47 p.p.; ostatnie 20 sesji +2.29 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +8.96 p.p.; wynik faktyczny +13.85
- W5: śr. 5-ses. spread rok przed D0 +3.61 p.p.; ostatnie 20 sesji +7.84 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +29.47 p.p.; wynik faktyczny +5.95
- W6: śr. 5-ses. spread rok przed D0 +3.86 p.p.; ostatnie 20 sesji +8.42 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +44.01 p.p.; wynik faktyczny -5.89
- W7: śr. 5-ses. spread rok przed D0 +3.28 p.p.; ostatnie 20 sesji +6.28 p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: +28.01 p.p.; wynik faktyczny -21.15

corr(momentum 20-ses. konstrukcji, spread faktyczny) = -0.51 (n=7)


Hipoteza „kupowano rozciągnięte nazwy i przyszło odwrócenie” (corr −0,51 przy n = 7) NIE przeżyła testu panelowego:

### (a1) Konstrukcje koszyków: spread 5-ses. forward vs zwrot L−S 20 sesji wstecz (okna nienakładające się co 5 sesji, ~1000 sesji przed D0)

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

### (a2) Uniwersum 103 spółek: 5-ses. zwrot relatywny vs ^NDX wg decyla 20-ses. zwrotu relatywnego (okna nienakładające się, 2022-10 → 2026-10)

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


Odczyt: dla tych samych konstrukcji wysokie momentum 20-sesyjne zapowiadało historycznie WYŻSZY (nie niższy) spread 5-sesyjny
(+3,5 vs +0,7 p.p.; w uniwersum decyl D10 +0,78 p.p. vs D1 +0,04). W6–W7 to nie kara za „pogoń”, lecz odwrócenie czynnika,
którego kierunku 5-sesyjny model nie przewiduje (i nie ma dowodu, że ktokolwiek przewiduje). To zgodne z literaturą cytowaną
w `rutyny/PROPOZYCJA-2026-10-12-model-3.1.md` (kontynuacja w dużych spółkach) — tu potwierdzone na własnych danych.

## 7. Reszty idiosynkratyczne per strona i blok

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

Odczyt: cała dodatnia reszta systemu siedzi po stronie SHORT, w szczególności w shortach software'u (INTU +25,6 p.p. w 4 tygodniach,
APP +16,5 w 7, ADSK +3,6): blok SOFT +3,3 p.p./nogę (n = 13). Shorty defensywne, chwalone 12.10 jako „jedyna powtarzalna przewaga”,
mają po W7 surową pozycję +0,14 p.p./nogę (13/19 trafień, ale TMUS −12,6, SBUX W7 −13,0, CMCSA W7 −11,5) — przewaga zniknęła
w jednym tygodniu, bo to też był zakład czynnikowy (ujemny ładunek DEF). Strona LONG SEMI: −1,5 p.p./nogę, 12/29.

## 8. Wkład per ticker

| ticker | kier. | blok | tygodni | suma pozycji p.p. | suma reszty p.p. | trafienia |
|---|---|---|---|---|---|---|
| INTU | S | SOFT | 4 | +26.72 | +25.64 | 3/4 |
| AMD | L | SEMI | 6 | +19.86 | +13.82 | 4/6 |
| CMCSA | S | DEF | 7 | +18.82 | +20.21 | 6/7 |
| APP | S | SOFT | 7 | +13.51 | +16.52 | 2/7 |
| CEG | L | UTIL | 2 | +5.94 | +7.67 | 1/2 |
| ADSK | S | SOFT | 1 | +5.55 | +3.57 | 1/1 |
| SBUX | S | DEF | 5 | +5.31 | +8.12 | 4/5 |
| NVDA | L | SEMI | 2 | +0.98 | +0.02 | 1/2 |
| NFLX | S | MEDIA | 2 | +0.30 | +1.70 | 1/2 |
| MSFT | L | MEGA | 2 | -0.33 | -1.32 | 1/2 |
| TER | L | SEMI | 2 | -0.43 | +0.75 | 1/2 |
| ALAB | L | SEMI | 1 | -2.03 | -9.22 | 0/1 |
| CSCO | L | SIECI | 1 | -3.80 | -5.29 | 0/1 |
| PEP | S | DEF | 3 | -4.32 | +1.55 | 2/3 |
| MU | L | SEMI | 7 | -4.57 | +1.20 | 3/7 |
| AVGO | L | SEMI | 2 | -4.61 | -8.44 | 1/2 |
| PAYX | S | DEF | 1 | -4.85 | -1.26 | 0/1 |
| TSLA | S | AUTO | 3 | -5.09 | -4.98 | 0/3 |
| AMAT | L | SEMI | 1 | -6.36 | -0.34 | 0/1 |
| WDAY | S | SOFT | 1 | -6.61 | -2.42 | 0/1 |
| MRVL | L | SEMI | 2 | -8.15 | -2.94 | 1/2 |
| STX | L | SEMI | 2 | -11.28 | -18.62 | 0/2 |
| TMUS | S | DEF | 1 | -12.57 | -3.64 | 0/1 |
| PANW | L | CYBER | 1 | -12.84 | -11.17 | 0/1 |
| LITE | L | SEMI | 4 | -27.52 | -9.87 | 1/4 |

MU był w koszyku 7/7 tygodni (−4,57 p.p. łącznie, reszta +1,20), APP i CMCSA 7/7. LITE 4 razy: −27,5 p.p. — najdroższa noga systemu
(σ dzienna 6 %, pre-mortem W7 nazwał „sprzedaj wiadomość” i zostawił karę 0).

## 9. Seria od D0 vs od wejść vs „jak rachunek” (W6–W7)

Rekonstrukcja z 39 stanów `fills` (koszyki_historia.json) i raportów dziennych 13–16.10. Założenia: wejście nogi odziedziczonej = D0
(pozycja była na rachunku); nowe nogi po cenach z `fills`; stop = dokładnie −10 % od poziomu brokera (fills; dla MRVL 267,53 z pulsu 15.10),
bot wykonuje po mid w biegu 13:45/17:05 UTC, więc faktyczna cena stopu mogła być NIŻSZA (zaniżam korzyść stopu LITE/PANW i zawyżam
MU/MRVL); PANW po ponownym otwarciu 16.10 na połowie wielkości (REDUCE). Każdy odcinek na pełną wielkość nogi, jak robi bot.

| tydz. | seria | LONG | SHORT | spread | ≈ rachunek |
|---|---|---|---|---|---|
| W6 | od D0 (prognoza) | LONG śr. -4.63 | SHORT śr. -1.27 | spread -5.89 p.p. | ≈ wynik rachunku -7.1% kapitału (×1,2) |
| W6 | od faktycznych wejść, bez stopów | LONG śr. -4.53 | SHORT śr. -1.28 | spread -5.81 p.p. | ≈ wynik rachunku -7.0% kapitału (×1,2) |
| W6 | jak rachunek (wejścia + stopy + ponowne otwarcia) | LONG śr. -4.53 | SHORT śr. -1.28 | spread -5.81 p.p. | ≈ wynik rachunku -7.0% kapitału (×1,2) |
| W7 | od D0 (prognoza) | LONG śr. -16.95 | SHORT śr. -4.20 | spread -21.15 p.p. | ≈ wynik rachunku -25.4% kapitału (×1,2) |
| W7 | od faktycznych wejść, bez stopów | LONG śr. -16.28 | SHORT śr. -3.45 | spread -19.74 p.p. | ≈ wynik rachunku -23.7% kapitału (×1,2) |
| W7 | jak rachunek (wejścia + stopy + ponowne otwarcia) | LONG śr. -11.50 | SHORT śr. -3.45 | spread -14.96 p.p. | ≈ wynik rachunku -17.9% kapitału (×1,2) |

### Nogi W7 — trzy serie (p.p. na nodze)

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

### Nogi W6 — trzy serie (p.p. na nodze)

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

### Bilans wykonania (p.p. spreadu)
- W6: opóźnienie wejścia +0.08 p.p.; stopy+ponowne otwarcia +0.00 p.p.; razem wykonanie vs prognoza +0.08 p.p. (history spread_fills_pp: W6 +3,88 / W7 −12,36 — te liczby NIE są serią rachunku)
- W7: opóźnienie wejścia +1.41 p.p.; stopy+ponowne otwarcia +4.78 p.p.; razem wykonanie vs prognoza +6.19 p.p. (history spread_fills_pp: W6 +3,88 / W7 −12,36 — te liczby NIE są serią rachunku)

Każdy stop realizuje −10 % × ALLOC 0.24 = -2.4 % kapitału; 4 stopy W7 (MU, LITE, MRVL, PANW) = -9.6 % kapitału zrealizowane (bez uwzględnienia, że MU i MRVL/PANW zostały odkupione niżej).

W6 od zamknięcia 6.10 do 9.10: spread -3.57 p.p. (≈ -4.3% kapitału); W7 jak rachunek -14.96 p.p. (≈ -17.9%); złożone ≈ -21.5% kapitału vs podane w zadaniu −23,7 % od szczytu 6.10→16.10 (różnica: taktyczne APOG/PENG/ERIC, koszty CFD, egzekucja stopów poniżej −10 %, wyrównania).

Odczyt: (1) W6 — wykonanie neutralne (+0,08). (2) W7 — poniedziałkowe wejście po niższych cenach longów i wyższych shortów dało +1,41 p.p.;
stopy: LITE (bez ponownego otwarcia dzięki wpisowi CLOSE 14.10) +14,1 p.p. na nodze, PANW +7,0 (odkupiony 7,8 % niżej),
MU +1,6, MRVL +1,3 (odkupione 2 % niżej). Łącznie stopy +4,78 p.p. spreadu. Ponowne otwarcie tego samego dnia było w W7 korzystne
tylko dlatego, że kurs do 17:05 UTC dalej spadał — to rzut monetą, nie mechanizm. (3) Złożony wynik 6.10→16.10 ≈ −21,5 % kapitału
wobec −23,7 % faktycznie: różnicę (−2 p.p.) tłumaczą taktyczne (APOG/PENG zamknięte przy rotacji, ERIC), koszty CFD (spready
z wyrównań, finansowanie, dywidendy po stronie short) i egzekucja stopów poniżej poziomu −10 %. (4) `spread_fills_pp` W6 (+3,88)
liczy MU od 913,35 z 27.08, W7 (−12,36) pomija zrealizowane straty na stopach — żadna z liczb w history nie mierzy rachunku.
W4 (+3,24) jest nieodtwarzalny (churn 63 par zamknij–otwórz), W5 (+7,76) zawiera MU od 27.08.

## 10. Ryzyko kill switcha przy obecnej konstrukcji (symulacja, zero przewagi)

Symulacja (zero przewagi, rozkład normalny, 20 000 ścieżek): P(obsunięcie od kroczącego szczytu ≥ 25 % w ciągu N tygodni)
- sd tygodnia spreadu 7 p.p. (rachunek 8.4%): N=13: 47%, N=26: 78%, N=52: 96%
- sd tygodnia spreadu 9 p.p. (rachunek 10.8%): N=13: 65%, N=26: 90%, N=52: 99%
- sd tygodnia spreadu 11 p.p. (rachunek 13.2%): N=13: 77%, N=26: 95%, N=52: 100%

Przy sd 5-sesyjnego spreadu 6,5–9,8 p.p. (sekcja 4b) i ALLOC 0,24 kill switch w ciągu pół roku jest bardziej prawdopodobny niż nie,
nawet gdyby przewaga wynosiła +1 p.p./tydz. (nieuwzględniona — przesuwa wynik o kilka punktów). To sedno: problem leży w kombinacji
ekspozycja czynnikowa × dźwignia, a nie w pojedynczych tezach.

## 11. Ekspozycja ex ante koszyka W8 (bez wyniku)

| noga | kier. | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | σ_d |
|---|---|---|---|---|---|---|---|
| GOOGL | L | 0.76 | 1.55 | -0.50 | 0.27 | 0.36 | 1.99% |
| GILD | L | 0.06 | 1.32 | -0.11 | 1.07 | 0.24 | 1.68% |
| MSFT | L | 0.57 | 0.88 | -0.83 | -0.49 | 0.39 | 2.08% |
| QCOM | L | 1.49 | 1.39 | 0.37 | 0.25 | 0.32 | 3.41% |
| ADP | L | -0.25 | 0.51 | -0.68 | 0.06 | 0.31 | 1.76% |
| AXON | S | 0.85 | 1.95 | -1.14 | -0.04 | 0.22 | 3.92% |
| DASH | S | 0.75 | 1.61 | -0.98 | -0.12 | 0.27 | 3.07% |
| ALNY | S | 0.06 | 1.61 | -0.29 | 1.17 | 0.11 | 3.05% |
| APP | S | 1.44 | 1.45 | -1.00 | -0.93 | 0.25 | 4.56% |
| FER | S | 0.57 | 1.03 | 0.19 | 0.61 | 0.29 | 1.60% |

W8 netto (L−S): β1 -0.21, b_NDX -0.40, b_SOX−NDX +0.29, b_DEF +0.10
spread dzienny konstrukcji W8, 250 sesji: σ_d 1.85% (5-ses. ≈ 4.15 p.p.), R² 3f 0.06, β -0.40, b_SOX +0.29, b_DEF +0.10; śr. 5-ses. historyczny +1.16 p.p.
śr. ρ par LONG (60 ses.) 0.10, SHORT 0.15

Odczyt: W8 jest pierwszym koszykiem o ładunku ^SOX−^NDX bliskim zera (+0,29 vs +1,1…+2,1), R² czynników 0,06, σ 5-sesyjna 4,2 p.p.
(połowa W4–W6), korelacja par 0,10. Czy to skutek reguły, czy przypadek rankingu — do sprawdzenia w sekcji KONSTRUKCJA raportu W8.
Jeśli ta cecha ma zostać, trzeba ją zapisać jako regułę (sekcja 13).

## 12. Krytyczna lektura `PROPOZYCJA-2026-10-12-model-3.1.md`

Zgodne z moimi liczbami: udział ^SOX−^NDX ~70–74 % (potwierdzone pooled 0,74 — ale ich wersja była z regresji n = 6, moja z dni),
β1 netto 1,1–2,7 (u mnie 1,13–2,32), kontynuacja momentum w panelu (potwierdzona), ostrzeżenie o P(kill) (potwierdzone, moje 78–90 %
w 26 tyg.), brak sensu w zmianie wag B2 przy n < 10. Niezgodne lub przedawnione: (a) „shorty defensywne to jedyna powtarzalna przewaga,
13/14 trafień” — po W7 13/19 i +0,14 p.p./nogę; przewaga była ekspozycją na czynnik DEF, nie selekcją; (b) „test betowy nieosiągalny 7/7”
— W8 pokazuje, że koszyk o b_SOX ≈ 0,3 jest osiągalny z tego samego rankingu; (c) propozycja ALLOC 0,20 jest kosmetyczna wobec sd
7–12 %/tydz. — ogranicznik lotu 0,1 akcji dla MU/LITE to argument za REDUCE_FALLBACK=close, nie za utrzymaniem 0,20;
(d) 29 agentów i 7 twierdzeń wyprodukowało 17 punktów zmian — przy n = 7 to więcej reguł niż obserwacji; z mojej analizy wynikają
trzy zmiany strukturalne (sekcja 13), reszta to pomiar.

## 13. Wnioski i rekomendacje (z siłą dowodu)

**Diagnoza:** zakład czynnikowy (długie półprzewodniki/AI-hardware kontra defensywy, ładunek 1,1–2,1 na ^SOX−^NDX) z dźwignią 2,4×,
bez wykrywalnej przewagi selekcyjnej (reszta +0,6 p.p./tydz., t 0,27), zakończony tygodniem z ogona rozkładu tej konstrukcji (z −3,8).
Nie da się stwierdzić, że selekcja NIE działa (przedział ufności obejmuje +3 p.p./tydz.) ani że działa; da się stwierdzić, że ponad
połowa (74 % dziennie) tego, co system przeżywa, to jeden czynnik, którego model nie prognozuje.

| # | zmiana | gdzie | oczekiwany efekt | dowód |
|---|---|---|---|---|
| 1 | Budżet czynnikowy w B4: policz b_SOX−NDX i b_DEF (250 sesji) dla TOP15/BOTTOM15; koszyk musi mieć abs(śr._L b_SOX − śr._S b_SOX) ≤ 0,5 i abs(b_DEF_net) ≤ 0,5 (wymiany w obrębie TOP15/BOTTOM15 albo parowanie: najsłabsza nazwa tego samego bloku po stronie short) | rutyna tygodniowa (B4) + `scripts/kursy.py --beta` | sd 5-ses. spreadu z 6,5–9,8 do ~4 p.p. (W8 ex ante 4,2); usuwa składnik, który dał −7,9 p.p. łącznie i −11,5 w W7 | twarda dla wariancji (R² 0,74; W8 pokazuje wykonalność); poszlakowa dla zwrotu (reszta +0,6/tydz.) |
| 2 | ALLOC_PCT 0,24 → ≤ 0,12 (i REDUCE_FALLBACK=close zamiast keep, bo przy lotach 0,1 akcji REDUCE na MU/LITE jest niewykonalny) | app.py (zmienne Render: ALLOC_PCT, REDUCE_FALLBACK) | sd tygodnia rachunku z 8–12 % do 2,5–5 %; P(kill 26 tyg., zero przewagi) z 78–90 % do rzędu 10–20 % przy jednoczesnym pkt 1 | twarda (symulacja na sd z danych; −23,7 % w 2 tygodnie przy ALLOC 0,24) |
| 3 | Po twardym stopie bot dopisuje sam wpis exclude CLOSE dla tej nogi do końca wersji (koniec ponownych otwarć w tym samym biegu/dniu) | app.py (`stopy_bezpieczenstwa` → zapis exclude) | eliminuje rzut monetą „odkup 2 h później”; W7: LITE bez ponownego otwarcia +14 p.p. na nodze, ponowne otwarcia MU/MRVL/PANW zyskały tylko dlatego, że kurs dalej spadał | poszlakowa (n = 4 stopy) / teoretyczna (ponowne otwarcie przywraca pełną ekspozycję czynnikową po −10 %) |
| 4 | Pomiar: w KROKU A obok spread_pp zapisywać spread_5s_pp (D0→D+5), dekompozycję 3f (beta/SOX/DEF/reszta) i serię „jak rachunek” (od faktycznych wejść, ze stopami, w tym straty zrealizowane na stopach); `spread_fills_pp` oznaczyć jako „cena odniesienia”, nie wynik rachunku; bot loguje stop (cena, czas, wielkość) w `wykonanie` | rutyna tygodniowa (KROK A) + app.py (log stopów w `wykonanie`) | przestaje się mylić czynnik z selekcją i prognozę z rachunkiem (W7: −21,15 vs −14,96 vs −12,36 to trzy różne rzeczy) | twarda (rekonstrukcja wymagała 39 stanów git i czytania raportów dziennych) |
| 5 | Nie zmieniać wag 20 czynników ani nie dopisywać reguł z pojedynczych tygodni; pętla uczenia tylko przez rejestr hipotez z testem panelowym (jak w sekcji 6) | proces | brak overfittingu przy n = 7; test panelowy w 2 minuty obala/potwierdza hipotezę (tu: „odwrócenie po pogoni” obalone) | teoretyczna (standard; przedziały w sekcji 3) |
| 6 | Hipoteza do śledzenia, nie reguła: shorty software'u (ofiary substytucji) reszta +3,3 p.p./nogę (n = 13); shorty defensywne +0,14 p.p./nogę surowo — nie traktować ich jako „przewagi” | rutyna tygodniowa (rejestr hipotez w raporcie) | po 30+ nogach widać, czy cokolwiek po stronie short jest selekcją, czy czynnikiem | poszlakowa |
| 7 | Limit koncentracji: maks. 3 nogi z jednego bloku na stronę i śr. ρ par ≤ 0,5 (60 sesji) — jako warunek konieczny obok pkt 1, nie zamiast | rutyna tygodniowa (B4) | efektywna liczba nóg z 1,2–1,5 do ≥ 3; mniejsze ogony | twarda dla wariancji, bez dowodu dla zwrotu (tygodnie SEMI 5/5 miały +3,84 śr. — bo czynnik rósł) |

Czego NIE robić: nie zmieniać horyzontu 5 sesji ani bramki 4/8 % na podstawie W7 (brak dowodu); nie wyłączać stopu 10 % (w W7 +4,8 p.p.);
nie czytać W2–W5 jako potwierdzenia modelu (dryf konstrukcji +1,8…+3,9 p.p./5 ses. historycznie tłumaczy je bez umiejętności).

## 14. Otwarte pytania

1. Faktyczne ceny egzekucji stopów (bot wykonuje po mid w biegu, nie na poziomie −10 %) — w `fills` ślad znika; potrzebny log z Capital.com/`wykonanie`.
2. Koszty CFD (spready z 63 par zamknij–otwórz we wrześniu, finansowanie 2,4× brutto, dywidendy po stronie short) — w żadnej serii; różnica ok. 2 p.p. między rekonstrukcją (−21,5 %) a faktem (−23,7 %) 6.10→16.10 to ich górne oszacowanie łącznie z taktycznymi.
3. Czy 250-sesyjne ładunki niedoszacowują ekspozycji w ruchach gwałtownych (reszta skorelowana +0,78 z czynnikiem)? Test: ładunki z 60 sesji lub z dni |^SOX−^NDX| > 2 %.
4. Czy reszta +0,6 p.p./tydz. (SHORT +1,9/nogę) to przewaga? Potrzeba ~100–150 tygodni przy sd reszty 6 p.p.; alternatywa: test przekrojowy TOP15/BOTTOM15 (nie tylko 5/5) z raportów.
5. W8 ma b_SOX +0,29 — z reguły czy z przypadku? Sprawdzić KONSTRUKCJĘ w raporcie W8; jeśli przypadek, pkt 1 i 7 trzeba zapisać.
6. Taktyczne (AKAM −3,3, VICR/ACN na papierze, APOG/PENG +0,3, ERIC +4,0) i reakcje pulsu (reaction_pp łącznie −0,36 wykonane) nie weszły do dekompozycji — mały wpływ, ale 20 % kapitału na nogę.
7. Czy strona SHORT powinna być bliższa indeksowi (hedge indeksowy) zamiast akcji? PROPOZYCJA podaje −0,40 p.p./tydz. in-sample — nie testowałem; po pkt 1 pytanie traci na wadze.
