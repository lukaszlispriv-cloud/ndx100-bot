# Dodatki (ryzyko_extra.py)

## Wykonalnosc lotow (krok 0,1 akcji, kapital odniesienia = START_EQUITY 1 000 USD z app.py)

| ALLOC/noge | cel USD | nazwy, dla ktorych 0,1 akcji > cel x 1,6 (noga POMIJANA) | nazwy z 0,1 akcji w (cel; 1,6 cel] (otwierany min. lot = przestrzal) |
|---|---|---|---|
| 0.24 | 240 | 0: - | 0: - |
| 0.12 | 120 | 0: - | 4: ASML (164), MELI (183), MPWR (121), SNDK (130) |
| 0.10 | 100 | 2: ASML (164), MELI (183) | 2: MPWR (121), SNDK (130) |
| 0.08 | 80 | 3: ASML (164), MELI (183), SNDK (130) | 4: COST (99), LITE (82), MPWR (121), MU (88) |
| 0.06 | 60 | 5: ASML (164), COST (99), MELI (183), MPWR (121), SNDK (130) | 5: LITE (82), META (71), MU (88), REGN (79), STX (64) |

Kursy 2026-10-16 (USD): MU 879, LITE 824, NFLX 71, AVGO 329, MSFT 529, META 709, COST 989, ASML 1642, MELI 1834, BKNG 163, NVDA 214, AMD 529, MRVL 228, SNDK 1299

## Biezacy tydzien (W8): P(przebicia kill switcha) przy kapitale ≈ 1,7 % nad progiem

koszyk W8 sigma jednostkowa 250 ses.: 9.25%/d; 60 ses.: 9.18%/d
| ALLOC | sigma_d kap. | P(kill w 5 ses.) | P(kill w 10 ses.) | P(kill w 20 ses.) |
|---|---|---|---|---|
| 0.24 | 2.22% | 53% | 65% | 76% |
| 0.12 | 1.11% | 31% | 47% | 62% |
| 0.08 | 0.74% | 18% | 33% | 49% |
| 0.06 | 0.56% | 12% | 25% | 40% |
| 0.04 | 0.37% | 5% | 13% | 26% |

Odleglosc do progu w sigmach dziennych kapitalu (≈ 1,7 %/sigma_d): ALLOC 0.24: 0.8 sigma, ALLOC 0.12: 1.5 sigma, ALLOC 0.08: 2.3 sigma, ALLOC 0.06: 3.0 sigma

## Estymator sigma nogi: korelacja prognozy (sigma20 / sigma60 / EWMA lambda 0,94) z sigma realizowana w nastepnych 5 sesjach

- sigma20: korelacja log-sigma prognoza vs realizacja 0.597; mediana (realizowana/prognoza) 0.89; n=9049
- sigma60: korelacja log-sigma prognoza vs realizacja 0.601; mediana (realizowana/prognoza) 0.83; n=9049
- EWMA(0,94): korelacja log-sigma prognoza vs realizacja 0.614; mediana (realizowana/prognoza) 0.83; n=9049

## Arytmetyka odrabiania

- obsuniecie -10.0% wymaga +11.1% do szczytu; przy alfie +2 p.p./tyg: ALLOC 0,24 -> 4 tyg (bez szumu), ALLOC 0,08 -> 13 tyg
- obsuniecie -20.0% wymaga +25.0% do szczytu; przy alfie +2 p.p./tyg: ALLOC 0,24 -> 9 tyg (bez szumu), ALLOC 0,08 -> 28 tyg
- obsuniecie -23.7% wymaga +31.1% do szczytu; przy alfie +2 p.p./tyg: ALLOC 0,24 -> 11 tyg (bez szumu), ALLOC 0,08 -> 34 tyg
- obsuniecie -25.0% wymaga +33.3% do szczytu; przy alfie +2 p.p./tyg: ALLOC 0,24 -> 12 tyg (bez szumu), ALLOC 0,08 -> 36 tyg

## Regula: ALLOC_t = clip(VOL_TARGET / sigma60_unit(koszyk), ALLOC_MIN, ALLOC_MAX); sigma60_unit = odchylenie dzienne sumy 5 long - 5 short z 60 sesji do D0

| W | sigma60_unit | ALLOC przy celu 1,0% | 1,25% | 1,5% | 2,0% | wariant uproszczony: sr. sigma60 nog x sqrt(10) x (1+rho) ... pominiety | P&L tygodnia przy spread_pp faktycznym (cel 1,5%) vs ALLOC 0,24 |
|---|---|---|---|---|---|---|---|
| W1 | 22.7% | 4.4% | 5.5% | 6.6% | 8.8% | | -1.3% vs -4.9% |
| W2 | 16.8% | 5.9% | 7.4% | 8.9% | 11.9% | | +2.8% vs +7.4% |
| W3 | 20.5% | 4.9% | 6.1% | 7.3% | 9.8% | | +0.5% vs +1.7% |
| W4 | 26.4% | 4.0% | 4.7% | 5.7% | 7.6% | | +3.9% vs +16.6% |
| W5 | 24.9% | 4.0% | 5.0% | 6.0% | 8.0% | | +1.8% vs +7.1% |
| W6 | 24.7% | 4.0% | 5.1% | 6.1% | 8.1% | | -1.8% vs -7.1% |
| W7 | 18.3% | 5.5% | 6.8% | 8.2% | 10.9% | | -8.7% vs -25.4% |
| W8 | 9.3% | 10.8% | 13.5% | 16.0% | 16.0% | | - |
suma W1-W7 (liniowo, bez kosztow): cel 1,5% -> -2.8% kapitalu; ALLOC 0,24 -> -4.4% (spread_pp x 5 x ALLOC; W4 liczony jak 1 tydzien)
