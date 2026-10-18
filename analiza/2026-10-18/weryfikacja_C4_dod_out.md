# Dodatek C4 (weryfikacja_C4_dod.py)

## Rozklad ALLOC z vol-targetu sigma60 1,5%/d clip [0,04;0,12] na 234 tygodniach momentum 6M
- udzial tygodni na capie 0,12: 38%; na floorze 0,04: 0%; mediana 0.100; p10 0.055; p90 0.120; srednia 0.095
- to samo z sigma20: cap 35%, floor 3%, mediana 0.102
- sigma60 jednostkowa koszykow momentum: mediana 15.0%/d, p10 9.6%, p90 27.2%; lata: 2022 17.9%, 2023 10.0%, 2024 13.5%, 2025 17.3%, 2026 27.8%

## Istotnosc roznicy Sharpe'a: VT sigma60 [0,04;0,12] vs staly 0,10 vs staly 0,12 (bootstrap blokowy tygodni, blok 4, 5000 prob)

| scenariusz alfy | Sharpe VT | Sharpe 0,10 | roznica | 90% CI roznicy (bootstrap) | P(roznica>0) | sr. tyg. VT | sr. tyg. 0,10 | stosunek zyskow VT/0,10 |
|---|---|---|---|---|---|---|---|---|
| in-sample | 1.07 | 0.95 | +0.12 | [-0.12; +0.33] | 76% | +0.506% | +0.534% | 0.95 |
| alfa 0 | 0.00 | 0.00 | +0.00 | [-0.30; +0.21] | 41% | +0.002% | +0.002% | 0.88 |
| alfa +1 p.p. | 0.97 | 0.86 | +0.11 | [-0.13; +0.32] | 74% | +0.458% | +0.484% | 0.95 |
| alfa +0,5 p.p. | 0.49 | 0.43 | +0.06 | [-0.20; +0.27] | 58% | +0.230% | +0.243% | 0.95 |

Uwaga: Sharpe stalego ALLOC nie zalezy od poziomu ALLOC (0,10 = 0,12 = 0,24 co do Sharpe'a przy zwrotach liniowych), wiec roznica dotyczy KSZTALTU skalowania, nie poziomu.

## W7: zrealizowana zmiennosc vs prognoza
- RMS u w W7: 23.8%/d; odchylenie wokol wlasnej sredniej: 9.0%/d; sigma60 ex ante 18.3%, sigma20 12.8%; srednia dzienna W7 -22.4%/d = -1.22 sigma60 dziennie, 5 dni z rzedu ujemnych (P przy symetrii = 1/32 = 3,1%).
- Wniosek: W7 to nie 'wybuch zmiennosci' (RMS/prognoza 1.30x), lecz seria 5 ujemnych dni o przecietnej skali 1,2 sigma; zaden estymator sigma z danych do D0 (ani sigma20 ani sigma60) nie przewidzialby tego — sigma20 byla NIZSZA od sigma60 i dalaby wyzszy ALLOC.

## Rowna srednia ALLOC: VT sigma60 przeskalowany do sredniej 0,10 vs staly 0,10 (sciezka historyczna, okna kroczace co 5 sesji)

| scenariusz | polityka | sr. ALLOC | max ALLOC | okna 12t kill | okna 52t kill | DD p95 12t |
|---|---|---|---|---|---|---|
| alfa 0 | staly 0,10 | 0.100 | 0.100 | 5.6% | 44.5% | -26.6% |
| alfa 0 | VT sigma60 x (0,10/sr.) | 0.100 | 0.127 | 0.9% | 56.6% | -22.7% |
| alfa 0 | VT sigma60 [0,04;0,12] | 0.095 | 0.120 | 0.0% | 48.6% | -21.6% |
| alfa +1 p.p. | staly 0,10 | 0.100 | 0.100 | 4.7% | 7.5% | -23.2% |
| alfa +1 p.p. | VT sigma60 x (0,10/sr.) | 0.100 | 0.127 | 0.0% | 11.0% | -19.3% |
| alfa +1 p.p. | VT sigma60 [0,04;0,12] | 0.095 | 0.120 | 0.0% | 6.9% | -18.3% |
