# Weryfikacja twierdzenia C4 — sizing, P(kill switch), vol-target

**Twierdzenie C4:** „Sizing jest głównym problemem: przy ALLOC 0,24 (gross 240%) P(kill switch −25% od kroczącego szczytu) ≈ 37–41% w 12 tyg. i 80–97% w 52 tyg. przy zerowej alfie; ALLOC 0,10–0,12 → 6–30%; vol-target całego koszyka (σ60 jednostkowa, cel 1,5%/d, ALLOC 0,04–0,12) → <1% przy koszcie ~20% Sharpe'a; inverse-vol per noga niewykonalny przy locie 0,1 akcji na obecnej skali.”

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Kierunek tezy (sizing jest dźwignią nr 1, 0,24 jest nieprzeżywalne, per-noga 1/σ odpada) wytrzymuje wszystkie próby obalenia — w tym bootstrap blokowy 10–60 sesji i GARCH(1,1). Ale cztery liczby w C4 są błędne albo mieszają horyzonty i scenariusze alfy: (1) „37–41% w 12 tyg. przy zerowej alfie” to liczba Z alfą in-sample; przy alfie 0 jest to 51–65%; (2) „80–97% w 52 tyg.” to także scenariusz z alfą +0,75…+1 p.p.; przy alfie 0 jest 98–100%; (3) „0,10–0,12 → 6–30%” i „vol-target → <1%” są prawdziwe tylko w horyzoncie 12 tyg. (albo 52 tyg. przy alfie +1 p.p.); w 52 tyg. przy alfie 0 to odpowiednio 45–76% i 20–49%; (4) „koszt ~20% Sharpe'a” dotyczy wag 1/σ **per noga** (v8), nie vol-targetu całego koszyka — ten przy równych wagach ma Sharpe'a o +0,06…+0,12 **wyższy** od stałego ALLOC (nieistotnie, 90% CI [−0,12; +0,33]).

Skrypty: `weryfikacja_C4.py` → `weryfikacja_C4_out.md`, `weryfikacja_C4_wyniki.json`; `weryfikacja_C4_dod.py` → `weryfikacja_C4_dod_out.md`. Katalog: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`. Dane: `../dane/closes_5y.csv` (skład dzisiejszy — survivorship bias dotyczy średniej, nie σ). Bez liczb z rachunku; kapitał odniesienia w §G to `START_EQUITY=1000` z `app.py:164`.

---

## 0. Skąd pochodzą liczby C4 (rekonstrukcja źródeł)

| fragment C4 | źródło w fazach 1–2 | co naprawdę mierzy |
|---|---|---|
| 37–41% w 12 tyg. | `bt_symulacja-wykonania.md` B3 (v1–v7, 223 okna 12-tyg. nakładające się) | ścieżka historyczna momentum 6M 2022–2026 **z alfą in-sample** (+1,0 p.p. spread/tydz., +1,3 p.p. kapitału) |
| 80–97% w 52 tyg. | `wykonanie-bota.md` §0 p.3 (80–97%), `perspektywa-quant.md` §F (93% przy μ 0; 83% przy μ 0,75), `ryzyko_sizing_out.md` §5b (99% przy alfie 0) | rozstrzał to różne alfy: 0 → 93–99%, +0,75…+1 p.p. → 78–83% |
| 0,10–0,12 → 6–30% | `bt_symulacja` v10 (5,8% okien 12-tyg., alfa in-sample), `ryzyko_sizing` §2a (0,10: 4,9%, 0,12: 11,1%, 12 tyg., alfa 0), `pq_quant` §F (0,12: 25–31% w 52 tyg. przy μ 0,75–1,0) | mieszanka horyzontów 12/52 tyg. i alf |
| vol-target <1%, koszt ~20% Sharpe | `bt_symulacja` v8 (kill 0,4%, Sharpe 0,95→0,77 = −19%) + `ryzyko_sizing` §2d (0,3–0,5%) | v8 to **1/σ per noga** (wagi ∝ 1/σ_i); §2d to koszyk równoważony — dwie różne reguły zlane w jedną |
| inverse-vol niewykonalny przy locie 0,1 | `ryzyko_extra.py` tabela lotów | przy START_EQUITY 1000 USD |

## 1. Czy symulacje zakładają niezależne tygodnie? (test: ACF, bootstrap blokowy 10–60, GARCH)

**Zależność jest silna, ale nie podnosi P(kill).** Dzienna seria jednostkowa koszyka momentum 6M (234 tyg., 1124 sesje, σ 17,9%/d — tyle samo co pula koszyków W1–W8: 17,5%):

- ACF |u|: +0,22 / +0,25 / +0,26 / +0,25 / +0,24 / +0,22 dla lagów 1/2/3/5/10/20 (błąd std 0,03); ACF u² lag 1–20 suma kwadratów × n = 924 vs χ²(20) krytyczne 31,4. ACF σ tygodniowej (RMS u w tygodniu, n=234): lag1 **+0,60**, lag4 +0,53, lag8 +0,42. Zwrot tygodniowy: ACF lag1 +0,01 — brak autokorelacji znaku, pełna autokorelacja skali. (`weryfikacja_C4_out.md` §A)
- GARCH(1,1): α 0,085, β 0,904, α+β 0,989 (połowiczny zanik szoku 61 sesji); kurtoza reszt 3,9 vs 4,8 surowych. (§C)

P(kill) przy alfie 0 (wyśrodkowana ścieżka momentum, 20 000 ścieżek; `weryfikacja_C4_out.md` §C):

| ALLOC | horyzont | iid dzienny | blok 5 | blok 10 | blok 20 | blok 60 | tygodniowy iid | GARCH(1,1) | GARCH start σ W7 |
|---|---|---|---|---|---|---|---|---|---|
| 0,24 | 12 tyg. | 65,3% | 61,9% | 59,8% | 57,0% | 51,1% | 63,3% | 60,3% | 61,8% |
| 0,12 | 12 tyg. | 13,5% | 12,1% | 11,3% | 12,3% | 8,2% | 11,7% | 15,7% | 16,0% |
| 0,10 | 12 tyg. | 5,9% | 5,2% | 4,8% | 6,3% | 5,4% | 4,3% | 8,6% | 9,0% |
| 0,08 | 12 tyg. | 1,5% | 1,2% | 1,2% | 1,6% | 4,0% | 0,9% | 3,7% | 3,9% |
| 0,24 | 52 tyg. | 99,6% | 99,4% | 99,5% | 99,0% | 98,5% | 99,4% | 97,8% | 98,0% |
| 0,12 | 52 tyg. | 75,6% | 74,2% | 72,0% | 73,0% | 71,9% | 74,9% | 71,3% | 71,3% |
| 0,10 | 52 tyg. | 61,3% | 58,1% | 56,4% | 57,8% | 57,6% | 59,1% | 58,1% | 58,3% |
| 0,08 | 52 tyg. | 41,1% | 37,8% | 35,6% | 37,3% | 38,9% | 39,2% | 40,7% | 41,3% |

Wniosek: klastrowanie zmienności **obniża** P(kill 12 tyg.) przy 0,24 z 65% (iid) do 51–60% (blok 60 / GARCH) — ścieżki rozdzielają się na spokojne i burzliwe przy tej samej σ bezwarunkowej, a ogon 12-tygodniowy nie rośnie. Dla 0,08–0,12 GARCH podnosi P(kill 12 tyg.) o 2–4 p.p. (0,10: 5,2% → 8,6%). W 52 tyg. wszystkie metody zbiegają (0,24: 98–100%). Zarzut „niezależne tygodnie zaniżają ryzyko” **nie obala** tezy; bootstrap blokowy 5 z faz 1–2 jest wręcz po konserwatywnej stronie. Start w tygodniu o σ koszyka W7 (18,3%) nic nie zmienia, bo σ60 W7 ≈ σ bezwarunkowej (17,9%) — W7 nie był koszykiem o podwyższonej zmienności ex ante.

Pula mieszanki W1–W8 (`ryzyko_sizing.py` §2d) z blokiem 10 i 20 zamiast 5 (`weryfikacja_C4_out.md` §F): 0,24 → 60,5 / 60,6 / 59,9% (blok 5/10/20); 0,12 → 11,4 / 8,4 / 8,5%; 0,10 → 5,0 / 3,0 / 3,1%; VT σ60 → 0,4 / 0,1 / 0,1%. Dłuższy blok obniża P(kill) dla małych ALLOC, bo przy bloku 20 cztery tygodnie dzielą jeden koszyk (mniej przełączeń między koszykami o różnej σ).

## 2. Korekta liczb C4 dla ALLOC 0,24 (test: ścieżka historyczna, okna kroczące)

`weryfikacja_C4_out.md` §B (okna kroczące co 5 sesji, nakładające się):

| ALLOC | 12 tyg. alfa in-sample | 12 tyg. alfa 0 | 52 tyg. alfa in-sample | 52 tyg. alfa 0 |
|---|---|---|---|---|
| 0,24 | 41,8% | **51,2%** | 100,0% | **100,0%** |
| 0,16 | 21,1% | 32,4% | 80,9% | 100,0% |
| 0,12 | 5,6% | **8,0%** | 14,5% | **64,7%** |
| 0,10 | 4,7% | **5,6%** | 7,5% | **44,5%** |
| 0,08 | 3,8% | 3,8% | 6,4% | 22,0% |

- „37–41% w 12 tyg. przy zerowej alfie” → poprawnie: **41,8% z alfą in-sample +1,0 p.p./tydz.; 51% (historia) / 57–65% (bootstrap, GARCH) przy alfie 0**. C4 zaniża o 10–25 p.p.
- „80–97% w 52 tyg. przy zerowej alfie” → poprawnie: **98–100% przy alfie 0; 96–97% przy alfie +1 p.p. (mieszanka W1–W8, §F); 100% na ścieżce historycznej nawet z alfą in-sample**. Rozstrzał 80–97% z faz 1–2 to scenariusze z alfą +0,75…+1 p.p. (pq_quant §F: 83%/78%) zmieszane z alfą 0 (93–99%).

## 3. Korekta liczb dla ALLOC 0,10–0,12 i vol-targetu: horyzont rozstrzyga

| polityka | 12 tyg., alfa 0 | 52 tyg., alfa 0 | 52 tyg., alfa +1 p.p. | źródło |
|---|---|---|---|---|
| 0,12 | 8,0% hist.; 8,4–16% boot./GARCH | **64,7% hist.; 66–76% boot.** | 18,5% hist.; 36–45% boot. | §B, §C, §E, §F |
| 0,10 | 5,6% hist.; 3,0–9,0% | **44,5% hist.; 50–61%** | 7,5% hist.; 20–28% boot. | §B, §C, §E, §F |
| 0,08 | 3,8%; 0,6–4,0% | 22,0%; 29–41% | 6,4%; 7,6–13% | §B, §C, §E, §F |
| VT σ60 1,5% [0,04;0,12] | **0,0% hist.; 0,1–0,4% boot.** | **48,6% hist.; 20–26% boot.** | 6,9% hist.; 2,9–6,6% boot. | §E, §F |

- „0,10–0,12 → 6–30%”: prawdziwe dla 12 tyg. przy alfie 0 (3–16%) i dla 52 tyg. przy alfie +1 p.p. na ścieżce historycznej (7,5–18,5%); **fałszywe dla 52 tyg. przy alfie 0 (45–76%)**.
- „vol-target → <1%”: prawdziwe **wyłącznie w 12 tyg.**; w 52 tyg. przy alfie 0 to 20–49%. Przy zerowej alfie żaden ALLOC ≥0,08 nie czyni kill switcha rzadkim zdarzeniem w skali roku — kroczący próg −25% przy błądzeniu losowym o σ_d 1,4–2,2% zostanie trafiony w 22–76% lat. Sizing kupuje czas (mediana sesji trafienia), nie nieśmiertelność; to alfa decyduje o przeżyciu w 52 tyg. (0,10: 44,5% → 7,5% przy +1 p.p.).

## 4. Czy σ60 reaguje za późno? Czy σ20 byłaby lepsza? (test: panel 234 tyg. + W1–W8 + W7 dzień po dniu)

**Nie — σ20 pogorszyłaby wynik, a W7 nie był zdarzeniem zmienności.** (`weryfikacja_C4_out.md` §D, `weryfikacja_C4_dod_out.md`)

- Panel 234 koszyków momentum (σ koszyka z własnej historii do D0 vs RMS u w tygodniu po wejściu): corr(log) σ60 0,642, σ20 0,627, EWMA 0,643; udział tygodni z realizacją >2× prognozy: σ60 1,7%, σ20 2,6%; mediana realizacja/prognoza 0,86 / 0,90. Zrealizowana σ_d kapitału przy VT 1,5%: p99 σ60 2,88% vs σ20 3,45%; tygodnie >3% (2× cel): 0,9% vs 1,7%. Dla porównania stały 0,10: p99 4,28%, >3% w 7,3% tygodni.
- Koszyki faktyczne W1–W8 na D0: σ20/σ60 = 1,06 / 0,70 / 0,73 / 0,75 / 0,81 / 0,77 / **0,70** / 0,53 — zmienność **spadała** przed każdym D0 od W2, więc σ20 dawałaby WYŻSZY ALLOC: W7 11,7% zamiast 8,2% i stratę −12,3% zamiast −8,7% kapitału (0,24: −25,4%). Suma W1–W7 liniowo: 0,24 −4,4%; VT σ60 −2,8%; VT σ20 −4,0%; stały 0,10 −1,8%; min(ALLOC60, ALLOC20) −2,7%.
- W7 dzień po dniu (koszyk z 9.10, sesje 12–16.10): u dnia −25,6 / −8,1 / −31,5 / −20,0 / −26,6% jednostkowo = 1,4 / 0,4 / 1,7 / 1,1 / 1,5 σ60 ex ante; σ20 rosła w trakcie tygodnia z 12,8% do 17,3% (wciąż poniżej σ60 19,3%). RMS u w W7 23,8%/d = **1,30× prognozy σ60** (nie wybuch zmienności); odchylenie wokół własnej średniej tygodnia tylko 9,0%/d. Strata to **5 ujemnych dni z rzędu o skali 1,2σ każdy** (−2,7σ tygodniowej; P(5 tych samych znaków) = 3,1% przy symetrii), czyli ruch kierunkowy, nie σ. Żaden estymator σ z danych do D0 by go nie przewidział; tygodniowe przeskalowanie nie mogło zareagować w trakcie tygodnia. Jedyną obroną był poziom ALLOC przed tygodniem.

## 5. Czy stały ALLOC 0,10 jest równoważny vol-targetowi? (test: ścieżka historyczna, bootstrap mieszanki, istotność Sharpe'a)

**Prawie — różnica jest realna w ogonie 12-tygodniowym i w maxDD, nieistotna w Sharpe'ie, zerowa w 52 tyg. przy alfie 0.** (`weryfikacja_C4_out.md` §E–F, `weryfikacja_C4_dod_out.md`)

Ścieżka historyczna momentum 6M 2022–2026 (tygodniowe przeskalowanie):

| scenariusz | polityka | śr. ALLOC | σ tyg. | Sharpe | najgorszy tydz. | maxDD | kapitał końc. bez kill (100) | okna 12t kill | okna 52t kill |
|---|---|---|---|---|---|---|---|---|---|
| in-sample | 0,24 | 0,240 | 10,0% | 0,93 | −23,5% | −68,5% | 692 | 41,8% | 100% |
| in-sample | 0,10 | 0,100 | 4,1% | 0,95 | −9,8% | −35,3% | 289 | 4,7% | 7,5% |
| in-sample | VT σ60 1,5% [0,04;0,12] | 0,095 | 3,4% | **1,07** | −7,5% | **−24,1%** | 286 | **0,0%** | 0,0% |
| alfa 0 | 0,10 | 0,100 | 4,0% | 0,00 | −10,2% | −55,1% | 83 | 5,6% | 44,5% |
| alfa 0 | VT σ60 | 0,095 | 3,4% | 0,00 | −7,9% | −55,1% | 88 | 0,0% | 48,6% |
| +1 p.p. | 0,10 | 0,100 | 4,1% | 0,86 | −9,9% | −35,7% | 257 | 4,7% | 7,5% |
| +1 p.p. | VT σ60 | 0,095 | 3,4% | 0,97 | −7,6% | −25,8% | 256 | 0,0% | 6,9% |
| +1 p.p. | VT σ20 | 0,094 | 3,5% | 0,88 | −8,6% | −26,9% | 234 | 0,0% | 8,7% |

- Sharpe: VT − stały = +0,12 (in-sample), +0,11 (+1 p.p.), +0,06 (+0,5 p.p.); 90% CI z bootstrapu blokowego tygodni (blok 4, 5000 prób) **[−0,12; +0,33]**, P(różnica>0) 74–76% — poprawa jest prawdopodobna, nie dowiedziona. Koszt „~20% Sharpe'a” z C4 ma **znak przeciwny** dla vol-targetu koszyka; −19% dotyczy v8 (1/σ per noga: Sharpe 0,95→0,77, bo 1/σ przenosi wagi z półprzewodników, w których siedzi sygnał). Sharpe stałego ALLOC nie zależy od poziomu (0,10 = 0,12 = 0,24 ≈ 0,95).
- Zysk przy alfie +1 p.p./tydz.: VT traci wobec stałego 0,10 **5% zysku** na ścieżce historycznej (śr. tyg. +0,458% vs +0,484%; kapitał 256 vs 257) przy maxDD −25,8% vs −35,7%. Na mieszance W1–W8 (śr. ALLOC VT 0,076 vs 0,10) mediana 12 tyg. +4,0…4,1% vs +5,0…5,1% (−20%), 52 tyg. +18,1…18,3% vs +20,5…22,1% (−10…−17%) — ale P(kill 52t) 2,9–6,6% vs 20–28%. Ta różnica to w większości niższa średnia ekspozycja, nie kształt reguły.
- Równa średnia ekspozycja (VT przeskalowany do śr. 0,10, max 0,127 vs stały 0,10, `weryfikacja_C4_dod_out.md`): alfa 0 — okna 12t 0,9% vs 5,6%, okna 52t **56,6% vs 44,5%** (VT gorszy!), DD p95 12t −22,7% vs −26,6%; alfa +1 — 12t 0,0% vs 4,7%, 52t 11,0% vs 7,5%. Na mieszance W1–W8 przy równej średniej (VT 0,076 vs stały 0,08): 12t 0,1–0,4% vs 0,6–1,2%, 52t 20–26% vs 29–36% — tam VT lepszy o ~30%. Rozbieżność bierze się z 2024-08/09: VT siedział na capie 0,12 (38% tygodni na capie, mediana 0,100, p10 0,055) w spokojnym 2023–2024 (mediana σ60 koszyków 10,0% w 2023 vs 27,8% w 2026) i oberwał w sierpniu 2024 — cap 0,12 > 0,10.
- Werdykt cząstkowy: stały 0,10 daje ~90% korzyści (P(kill 12t, alfa 0) 51–65% → 3–9%); VT dokłada: ogon 12-tyg. 5% → 0%, najgorszy tydzień −10% → −7,5…−8%, maxDD in-sample −35% → −24%, Sharpe +0,1 (n.s.), za cenę 5% zysku i nowego pola w `signals.json` (walidator + `app.py` + rutyna). Nie jest to zmiana klasy „0,24 → 0,10”.

## 6. Inverse-vol per noga przy kroku 0,1 akcji (test: logika `calc_size`, `app.py:871–897`, MAX_OVERSHOOT 1,6)

Krok 0,1 akcji potwierdzony w raportach (`reports/*.html`: „0,1 akcji = jeden minimalny lot, REDUCE_FALLBACK=keep”). `weryfikacja_C4_out.md` §G, wagi 1/σ60 do celu 1,5%/d:

| kapitał odniesienia | koszyk | wagi min/max | nogi pomijane | gross faktyczny vs zamierzony |
|---|---|---|---|---|
| 1 000 USD (START_EQUITY) | W7 | 4,8% / 23,7% | **2: MU, LITE** (0,1 akcji = 82–88 USD vs cel 48 USD → 1,7–1,8× > 1,6) | 103% vs 114% |
| 1 000 USD | W8 | 12,1% / 37,7% | 0 | 239% vs 246% |
| 2 500 USD | W7 | 4,8% / 23,7% | 0 | 112% vs 114% |
| 5 000 USD | W7 | — | 0 | 113% vs 114% |

Potwierdzone z doprecyzowaniem: niewykonalność dotyczy koszyków typu W4–W7 (półprzewodniki o kursie 800–1 300 USD z wagą ~5%) przy kapitale rzędu START_EQUITY; próg wykonalności to ok. 2 500 USD, nie 5 000 jak w `ryzyko-i-sizing.md`. Pominięcie 2 z 5 nóg long zmienia koszyk w netto-short — gorsze niż brak reguły. Niezależnie od lotów, 1/σ per noga kosztuje −19% Sharpe'a (v8) — argument przeciw jest podwójny.

## 7. Najsilniejszy kontrargument wobec C4

Przy zerowej alfie **żaden** poziom ALLOC ≥0,08 ani vol-target nie czyni kill switcha rzadkim zdarzeniem w horyzoncie roku: 0,08 → 22–41%, 0,10 → 45–61%, 0,12 → 65–76%, VT σ60 → 20–49% (§C, §E, §F). Liczby „<1%” i „6–30%” z C4 to wyłącznie horyzont 12-tygodniowy. Sizing kupuje czas na test alfy (przy 0,10 mediana trafienia przesuwa się z 31. sesji na drugi rok), ale „przeżywalność” w C4 jest tezą o kwartale, nie o roku; w skali roku o przeżyciu decyduje alfa (0,10: 44,5% → 7,5% przy +1 p.p.). Drugi kontrargument: stały 0,10 jest nieodróżnialny od vol-targetu w Sharpe'ie (CI obejmuje 0) i w P(kill 52t) na ścieżce historycznej, a VT z capem 0,12 w spokojnych latach ma WYŻSZĄ ekspozycję niż 0,10 (38% tygodni na capie) — jego przewaga to ogon 12-tygodniowy i maxDD, okupione nowym polem w `signals.json` i procesem sobotnim.

## 8. Twierdzenie po weryfikacji

„Sizing jest główną dźwignią ryzyka: przy ALLOC 0,24 P(kill −25% od kroczącego szczytu) przy zerowej alfie = 51% (ścieżka historyczna) / 57–65% (bootstrap blokowy 5–60, GARCH) w 12 tyg. i 98–100% w 52 tyg.; z alfą +1 p.p./tydz. 42% i 96–100%. ALLOC 0,10–0,12 → 3–16% w 12 tyg. (alfa 0), ale 45–76% w 52 tyg. przy alfie 0 i 7,5–45% przy +1 p.p. Vol-target koszyka σ60 1,5%/d [0,04;0,12] (śr. ALLOC 0,076–0,095) → 0,0–0,4% w 12 tyg., 20–49% w 52 tyg. przy alfie 0, 3–7% przy +1 p.p.; Sharpe +0,06…+0,12 wobec stałego ALLOC (n.s.), zysk −5% wobec stałego 0,10 przy +1 p.p.; koszt −19% Sharpe'a dotyczy 1/σ per noga, nie vol-targetu koszyka. σ20 dawałaby wyższy ALLOC w W2–W8 (W7: 11,7% vs 8,2%, strata −12,3% vs −8,7%). Klastrowanie zmienności (ACF |u| 0,22–0,26, ACF σ tyg. 0,60) nie podnosi P(kill). 1/σ per noga niewykonalny przy START_EQUITY 1 000 USD dla koszyków półprzewodnikowych (2/10 nóg pomijane), wykonalny od ~2 500 USD.”

## 9. Implikacja projektowa

1. **Natychmiast `ALLOC_PCT` 0,24 → 0,10** (Render). To jedyna zmiana klasy: P(kill 12 tyg., alfa 0) 51–65% → 3–9%, najgorszy tydzień −24% → −10%, bez wpływu na Sharpe'a. Nie 0,12 (8–16% / 65–76%) i nie 0,16 (32%).
2. **Vol-target koszyka jako krok drugi, nie pierwszy**: σ60 jednostkowa (nie σ20, nie max/min z obu), cel 1,5%/d, clip [0,04; 0,12]; przez ≥12 tygodni na papierze w raporcie sobotnim (σ60_unit, ALLOC z reguły, percentyl wobec losowych 5/5), zanim dojdzie pole `sizing` do `signals.json`/walidatora/`app.py`. Zysk z wdrożenia: ogon 12-tyg. 5% → 0%, maxDD −35% → −24% in-sample; koszt: 5% zysku i proces.
3. **Nie wdrażać** 1/σ per noga (−19% Sharpe'a, 2/10 nóg pomijanych przy START_EQUITY) ani σ20 jako estymatora.
4. **Raportować P(kill) zawsze z horyzontem i alfą** (12/52 tyg. × alfa 0 / +1 p.p.) — C4 pokazuje, jak mieszanie daje liczby od 6% do 76% dla tej samej reguły.
5. **Polityka po trafieniu kill switcha jest obowiązkowa, nie opcjonalna**: przy zerowej alfie kill w ciągu roku jest oczekiwany dla każdego ALLOC ≥0,08 (22–76%); `app.py` po trafieniu zostaje wstrzymany bezterminowo (`ryzyko-i-sizing.md`). Reset `equity_peak` + cooldown + restart od ALLOC_MIN musi być zdefiniowany przed zmianą sizingu, inaczej sizing tylko odwleka ten sam stan.
6. W7 jako lekcja: 5 ujemnych dni × 1,2σ przy σ zgodnej z prognozą — reguły reagujące na σ w trakcie tygodnia (Puls, σ20) nie mają tu czego wykryć; chroni wyłącznie ekspozycja ustalona przed tygodniem.

## 10. Ograniczenia

- Jedna ścieżka historyczna (2022–2026, jeden cykl AI/półprzewodników); okna 12/52 tyg. nakładają się (n efektywne ≪ 213/173). Survivorship bias dotyczy średniej (alfa in-sample +1,0 p.p. zawyżona), nie σ i klastrowania.
- Kill i stopy liczone na zamknięciach; bot sprawdza o 13:45/17:05 UTC na mid — P(kill) lekko zaniżone (tak samo w fazach 1–2).
- Pula W1–W8 to tylko 8 koszyków z 250-sesyjną historią każdy; w 2026 σ60 koszyków momentum (mediana 27,8%) jest 2,8× wyższa niż w 2023 (10,0%) — vol-target w bieżącym reżimie dawałby ALLOC 0,04–0,06, nie 0,095.
- GARCH dopasowany siatką (bez scipy); parametry typowe (α+β 0,99), kurtoza reszt 3,9 — reszty bootstrapowane, więc ogony zachowane.
- Koszty transakcyjne i finansowanie pominięte (jak w `ryzyko_sizing.py`); przy gross 100% finansowanie 6%/rok ≈ 0,12 p.p./tydz., dotyczy wszystkich polityk proporcjonalnie do ALLOC.
