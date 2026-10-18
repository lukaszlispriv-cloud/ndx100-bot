# Weryfikacja C2 — „5 par wewnątrz branży” zachowuje średnią i obniża σ o ~24 %

**Twierdzenie C2** (bt_neutralnosc.md): konstrukcja b_pary (long najlepsze / short najgorsze
momentum 6M w tej samej grupie TV) zachowuje średnią momentum (Δ≈0) i obniża σ spreadu o ~24 %
(F-test p<0,001), najgorszy tydzień z −26 do −14 p.p.; podobnie neutralność branżowa a_branza
(maks. 1L+1S z grupy).

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Część „obniża σ o ~24 %, najgorszy tydzień o połowę”
broni się w każdym teście, który miał ją obalić (losowa taksonomia, taksonomia point-in-time bez
look-ahead, połówki, lata, 6 definicji grupy, bez pary semis). Część „zachowuje średnią (Δ≈0)”
jest **nierozstrzygalna** na 233 oknach (CI95 Δ = ±0,57 p.p./tydz. przy średniej 1,01) i **nie
odtwarza się** w żadnej alternatywnej taksonomii: punktowe Δ jest ujemne we wszystkich 5 pozostałych
definicjach TV (−0,15…−0,55) i we wszystkich 11 klastrowaniach point-in-time (−0,38…−1,23,
mediana −0,86). Dla a_branza „zachowanie średniej” jest obalone punktowo (Δ −0,26…−0,45 w każdej
definicji). Mechanizm redukcji σ to w ~87 % niższa zmienność nóg (mniej skrajne rangi), a nie hedge
wewnątrz pary — korelacja L–S w parze TV wynosi 0,06, a 51 % par pochodzi z sektorowych zlepków
(SNDK/AXON, LITE/HON, PDD/AMZN).

Skrypty i wyniki (wszystkie liczby poniżej stamtąd):
- `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C2.py`
  → `weryfikacja_C2_out.txt`, `weryfikacja_C2_wyniki.json` (T1–T7)
- `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C2_dod.py`
  → `weryfikacja_C2_dod_out.txt`, `weryfikacja_C2_dod_wyniki.json` (klastry complete linkage, udział zlepków)
- `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C2_korel.py`
  (korelacja L–S w parze, dekompozycja σ spreadu)
- Harness, dane, sygnał, koszty: identyczne z `bt_neutralnosc.py` (import), mom6 = 126 sesji bez
  ostatnich 5, rel. do ^NDX, 233 okna tygodniowe 2022-04…2026-10, uniwersum 92–100 spółek/okno.

## T1 Reprodukcja i statystyka odporna

| wariant | śr. | σ | t | Sharpe | worst | 5 najgorszych | maxDD | netto t |
|---|---|---|---|---|---|---|---|---|
| none | 1,01 | 7,42 | 2,09 | 0,99 | −25,9 | −25,9 −20,9 −19,8 −17,5 −16,4 | −50,6 | 1,53 |
| b_pary | 1,01 | 5,67 | 2,72 | 1,29 | −14,4 | −14,4 −13,7 −13,1 −12,2 −11,1 | −37,4 | 1,99 |
| a_branza | 0,76 | 5,93 | 1,95 | 0,92 | −14,7 | −14,7 −14,3 −13,2 −13,1 −12,9 | −40,6 | 1,25 |

- b_pary vs none: Δśr −0,00 ± SE 0,30, **CI95 [−0,57; +0,57]** — „Δ≈0” znaczy tylko „nie
  wykryto różnicy”; przedział dopuszcza utratę 56 % średniej. σ-ratio 0,763, bootstrap CI95
  [0,70; 0,84]; test permutacyjny (zamiana parami w oknie) p = 0,000; F (log-F) p = 2e-5.
  Redukcja nie pochodzi z ogonów: MAD-ratio 0,80; σ-ratio po odcięciu 2/6/12 skrajnych okien
  0,78/0,79/0,80. Najgorszy tydzień: −14,4 vs −25,9 — i cała piątka najgorszych lepsza.
- a_branza vs none: Δ −0,26 (t −0,86, CI [−0,82; +0,31]); σ-ratio 0,80 [0,73; 0,88]; Sharpe
  **0,92 < 0,99 none** — „podobnie” w twierdzeniu nie dotyczy średniej ani Sharpe'a.
- b_pary ma zawsze 10 nóg (5 par) w 233 oknach; śr. 4,94/10 nóg wspólnych z none.

## T2 Kontrola: losowa taksonomia (300 permutacji etykiet industry/sector między spółkami)

Czy sama struktura „best/worst w grupie” obniża σ bez treści branżowej?

| | σ mediana [p5; p95] | σ-ratio mediana | śr. mediana [p5; p95] | worst mediana |
|---|---|---|---|---|
| pairs, losowe grupy | 6,80 [6,31; 7,30] | 0,916 | 0,95 [0,60; 1,29] | −21,1 |
| **pairs, grupy TV** | **5,67** | **0,763** | 1,01 | −14,4 |
| neutral, losowe grupy | 6,90 [6,36; 7,39] | 0,929 | 0,95 [0,58; 1,28] | −21,3 |
| **neutral, grupy TV** | **5,93** | **0,799** | 0,76 | −14,7 |

- Udział permutacji z σ ≤ realnej: **0,000** (obie konstrukcje); z worst ≤ realnego: 0,000.
  Struktura sama daje ~8 p.p. redukcji σ (0,92), treść grup TV dodaje kolejne ~16 p.p.
  → redukcja σ **nie** jest artefaktem struktury parowej. Twierdzenie obronione w tym punkcie.
- Średnia: udział permutacji ze śr. ≥ 1,01 = 0,39; t ≥ 2,72 = 0,067. Średnia b_pary jest
  zwyczajna (39. percentyl losowych taksonomii); wyjątkowy jest tylko t przez niższe σ.

## T3 Taksonomia point-in-time (look-ahead usunięty)

Grupy = klastry korelacyjne residuów dziennych (vs ^NDX) z 252 sesji ≤ D0, liczone na nowo
w każdym oknie (average i complete linkage, K = 8…40; grupy <3 → „Pozostałe”).

| klastrowanie | grup ≥3 | pairs: śr. | σ | Sharpe | Δ vs none (t) | σ-ratio | neutral: Δ (t) | σ-ratio |
|---|---|---|---|---|---|---|---|---|
| avg K=10 | 5,4 | 0,35 | 5,27 | 0,48 | −0,84 (−1,96) | 0,714 | −0,57 (−1,36) | 0,846 |
| avg K=15 | 6,4 | 0,81 | 4,59 | 1,27 | −0,38 (−0,96) | 0,622 | −0,37 (−0,95) | 0,701 |
| avg K=20 | 6,7 | 0,31 | 4,32 | 0,51 | −0,88 (−2,08) | 0,585 | −0,76 (−1,81) | 0,674 |
| compl K=8 | 7,0 | 0,75 | 4,90 | 1,10 | −0,44 (−1,12) | 0,664 | −0,27 (−0,76) | 0,822 |
| compl K=12 | 9,1 | 0,63 | 4,43 | 1,03 | −0,56 (−1,39) | 0,600 | −0,16 (−0,41) | 0,771 |
| compl K=15 | 9,9 | 0,76 | 4,31 | 1,27 | −0,43 (−1,08) | 0,584 | −0,39 (−1,00) | 0,689 |
| compl K=20 | 10,4 | 0,23 | 4,23 | 0,39 | −0,96 (−2,41) | 0,573 | −0,66 (−1,70) | 0,667 |
| compl K=25 | 10,2 | 0,34 | 3,88 | 0,62 | −0,86 (−2,02) | 0,526 | −0,76 (−1,83) | 0,665 |
| avg K=25/30/40 | 6,3/6,0/4,9 | 0,12/−0,04/0,06 | 3,63/3,63/3,45 | 0,24/−0,07/0,13 | −1,07/−1,23/−1,13 (t −2,5…−2,7) | 0,49/0,49/0,47 | −0,88/−0,97/−0,78 | 0,63/0,62/0,68 |

- σ-ratio pairs: mediana **0,584** [0,47; 0,71] — redukcja σ bez look-ahead jest **większa**
  niż z TV (klastry korelacyjne hedgują naprawdę: korelacja L–S w parze 0,22 vs 0,06 dla TV).
- Δśr pairs: mediana **−0,86** [−1,23; −0,38], w 6/11 wariantów t(Δ) ≤ −1,96. Sharpe > none
  (0,99) tylko w **4/11** wariantów (mediana 0,51). Neutral: Δ mediana −0,66, σ-ratio 0,683.
- Wniosek: im lepszy hedge wewnątrz pary, tym mniej momentum zostaje — „σ w dół przy Δ≈0” to
  własność konkretnej taksonomii TV W8, nie konstrukcji parowej jako takiej. Zastrzeżenie: klastry
  korelacyjne są inną taksonomią niż branżowa (mniej grup, 5–10 vs 15), więc test nie dowodzi, że
  branże TV z 2022 r. dałyby inny wynik — dowodzi, że wynik Δ≈0 nie przenosi się na taksonomię
  liczoną uczciwie z danych dostępnych w D0.

## T4 Wrażliwość na definicję grupy (taksonomia TV W8, pairs)

| definicja grupy | grup | śr. | σ | Sharpe | Δ (t) | σ-ratio | netto t |
|---|---|---|---|---|---|---|---|
| **base: industry ≥4 \| sector, grupa ≥3** | 14,7 | 1,01 | 5,67 | **1,29** | −0,00 (−0,01) | 0,763 | 1,99 |
| sector-only | 10,0 | 0,71 | 5,30 | 0,97 | −0,30 (−0,89) | 0,714 | 1,27 |
| industry-only (≥3) | 11,3 | 0,57 | 4,91 | 0,83 | −0,45 (−1,17) | 0,661 | 0,92 |
| industry ≥6 \| sector (= ≥10) | 12,0 | 0,87 | 5,74 | 1,09 | −0,15 (−0,49) | 0,773 | 1,58 |
| industry ≥2 \| sector | 13,3 | 0,47 | 4,87 | 0,69 | −0,55 (−1,48) | 0,656 | 0,60 |
| MIN_GROUP 2/4/5/6 (base) | — | 1,01/0,96/1,02/1,00 | 5,67/5,55/5,65/5,28 | — | −0,00/−0,06/+0,01/−0,02 | 0,76/0,75/0,76/0,71 | — |

- σ-ratio 0,66–0,77 w każdej definicji → redukcja σ odporna. Δ: base jest **jedyną** z 6
  definicji z Δ≈0; pozostałe −0,15…−0,55. Sharpe > none w 3/6 (base, ≥6, ≥10 — dwie ostatnie to
  ta sama taksonomia). Dla a_branza Δ −0,26…−0,45 we **wszystkich** 6, Sharpe > none w 0/6
  (0,71–0,96).
- To wygląda na efekt wyboru definicji: nawet jeśli base była ustalona a priori, jej przewaga nad
  sąsiednimi definicjami (±0,3–0,5 p.p./tydz.) mieści się w szumie (SE Δ = 0,30).

## T5 Stabilność w czasie (b_pary vs none)

| okres | n | none σ / śr. | b_pary σ / śr. | Δ (t) | σ-ratio [CI95] | worst b_pary / none |
|---|---|---|---|---|---|---|
| połowa 1 (2022-04…2024-07) | 116 | 5,53 / 0,06 | 4,06 / 0,17 | +0,11 (0,32) | 0,735 [0,64; 0,85] | −11,1 / −19,8 |
| połowa 2 (2024-07…2026-10) | 117 | 8,84 / 1,96 | 6,82 / 1,85 | −0,11 (−0,23) | 0,771 [0,70; 0,87] | −14,4 / −25,9 |
| 2022 | 36 | 7,46 / −0,06 | 4,69 / +0,63 | +0,69 (0,95) | 0,629 | −11,1 / −19,8 |
| 2023 | 52 | 3,95 / −0,13 | 2,93 / −0,11 | +0,03 (0,07) | 0,741 | −7,1 / −8,3 |
| 2024 | 52 | 7,17 / +1,70 | 5,40 / +1,47 | −0,23 (−0,40) | 0,753 | −10,8 / −12,3 |
| 2025 | 52 | 6,18 / +1,33 | 5,81 / +1,31 | −0,03 (−0,05) | **0,941** | −12,2 / −16,4 |
| 2026 | 41 | 11,49 / +2,14 | 8,55 / +1,82 | −0,33 (−0,28) | 0,744 | −14,4 / −25,9 |
| VIX>20 / VIX≤20 | 73 / 160 | — | — | −0,08 / +0,03 | 0,725 / 0,778 | — |

- Redukcja σ stabilna w obu połówkach (0,74/0,77) i reżimach VIX; w 2025 niemal zanikła (0,94).
- Δ stabilnie ≈0 w połówkach, ale uwaga: połowa 1 to okres, w którym samo momentum nie działało
  (none śr. 0,06) — tam „zachowanie średniej” nic nie kosztuje. W latach 2024–2026, gdy momentum
  dawało 1,3–2,1 p.p./tydz., Δ jest ujemna (−0,23/−0,03/−0,33). a_branza: Δ −0,63/−0,37/−0,67
  w 2024/2025/2026.

## T6 Skład par: semis, zlepki sektorowe, GOOG/GOOGL

- Udział grup w parach b_pary: Packaged Software 0,19, Semiconductors 0,16, **Electronic
  Technology (sector-zlepek) 0,16**, Health Technology (zlepek) 0,13, Internet Soft. 0,07,
  Producer Manufacturing 0,07, … Para z Semiconductors w 82 % okien, Packaged Software w 93 %.
- **51 % par pochodzi z grup = sector** (industry <4 spółek spada do sektora); tylko 62 % par ma
  oba końce w tej samej industry TV. Najczęstsze pary: SNDK/AXON (42×; Computer Peripherals vs
  Aerospace & Defense), LITE/HON (38×; Electrical Products vs Industrial Machinery), MRNA/ALNY,
  RKLB/TER, CTAS/SHOP, PDD/AMZN. Etykieta „wewnątrz branży” jest w połowie przypadków nominalna.
- Korelacja residuów L–S wewnątrz pary (252 sesje ≤ D0): **b_pary 0,06**, a_branza 0,00,
  none −0,06, klastry PIT 0,22. Pary TV prawie nie hedgują siebie nawzajem.
- Dekompozycja σ² spreadu (σ_L, σ_S, corr(L,S) zwrotów stron): none 5,32 / 3,97 / −0,26 → σ² 55,1;
  b_pary 4,32 / 3,08 / −0,15 → σ² 32,1. Gdyby b_pary zachowała corr none (−0,26): σ² 35,1, σ 5,92
  (ratio 0,80). **~87 % redukcji wariancji (20,0 z 23,0) pochodzi z niższej zmienności nóg, ~13 %
  z korelacji** — czyli z tego, że pary biorą mniej skrajne spółki (śr. ranga long 6,4 / short
  12,5 vs 2,0 / 2,0 w none; ekstremalność mom L−S 137 vs 173 p.p.).
- Para Semiconductors: wkład śr. +0,05 p.p./okno, σ wkładu 1,81. Bez pary semis: śr. 0,91, σ 5,75
  (ratio 0,774), Sharpe 1,14 — **semis nie są źródłem redukcji σ**. Bez semis i software: śr.
  0,57, σ 4,87, Sharpe 0,84 — tech-pary niosą średnią. GOOG/GOOGL: 0 par na 1165 (brak
  degeneracji).

## T7 Kontrola ekstremalności (none z rang k…k+4, bez taksonomii)

| rangi | śr. | σ | σ-ratio | worst |
|---|---|---|---|---|
| 1–5 (none) | 1,01 | 7,42 | 1,000 | −25,9 |
| 4–8 | −0,07 | 6,14 | 0,828 | −19,1 |
| 7–11 | 0,03 | 5,79 | 0,780 | −21,5 |
| 11–15 | 0,17 | 4,98 | 0,671 | −21,0 |
| 16–20 | 0,01 | 3,77 | 0,508 | −14,7 |

Mniej skrajne rangi dają podobną redukcję σ (0,78 przy rangach 7–11, zbliżonych do śr. rang
b_pary), ale zerową średnią. Treść b_pary polega więc na tym, że **wybiera mniej skrajne nogi
i w próbie nie traci przy tym średniej** — i właśnie ta druga część nie jest odporna (T3, T4).
Najgorszy tydzień b_pary (−14,4) jest jednak lepszy niż każdej kontroli rang do 11–15 (−21) —
to realna poprawa ogona, nie tylko skutek mniejszej ekstremalności.

## Najsilniejszy kontrargument

Δ≈0 jest własnością jednej taksonomii (TV W8, definicja industry≥4|sector) narzuconej wstecz; we
wszystkich 5 innych definicjach TV i 11 taksonomiach point-in-time punktowa średnia spada
o 0,15–1,23 p.p./tydz. (mediana PIT −0,86, t do −2,7), Sharpe przebija none tylko w 3/6 (TV)
i 4/11 (PIT); a 233 okna dają SE Δ = 0,30, więc rozstrzygnięcie „zachowuje średnią” przy różnicy
rzędu 0,3–0,5 wymagałoby ~900–2500 tygodni. Jednocześnie mechanizm redukcji σ to głównie mniej
skrajne, mniej zmienne nogi (87 % wariancji), nie hedge branżowy (corr w parze 0,06; 51 % par
to zlepki sektorowe) — czyli to, co daje też zwykłe przesunięcie rang (T7), tyle że bez utraty
średniej **w próbie**.

## Brzmienie po weryfikacji

b_pary (taksonomia TV W8, industry≥4|sector, grupa≥3) obniża σ tygodniową spreadu z 7,42 do
5,67 p.p. (σ-ratio 0,763, bootstrap CI95 0,70–0,84; permutacyjnie p<0,001; stabilnie w obu
połówkach 0,74/0,77; w losowej taksonomii σ-ratio tylko 0,92, p=0,000), najgorszy tydzień
z −25,9 do −14,4 p.p. i maxDD z −50,6 do −37,4 p.p. Redukcja σ powtarza się w każdej definicji
grupy (0,66–0,77) i w klastrach point-in-time (0,47–0,71). Średnia: Δ −0,00 ± 0,30 (CI95 ±0,57)
tylko w tej definicji; w pozostałych definicjach TV Δ −0,15…−0,55, w taksonomiach PIT −0,38…−1,23
(mediana −0,86) — „zachowuje średnią” jest nierozstrzygalne i nieodporne. Dla a_branza Δ
−0,26…−0,45 w każdej definicji, Sharpe 0,71–0,96 < 0,99 none — nie „podobnie”. 87 % redukcji
wariancji to niższa zmienność nóg (mniej skrajne rangi), 13 % hedge wewnątrz pary.

## Implikacja projektowa

1. Parowanie branżowe traktować jako narzędzie **redukcji ryzyka** (σ −20…−30 %, ogon o połowę),
   nie jako darmowy obiad: planować z założeniem, że kosztuje 0,3–0,5 p.p./tydz. średniej
   (ok. 30–50 % przewagi momentum brutto) — wtedy Sharpe ≈ none, zysk tylko w maxDD i odległości
   od kill switcha. To nadal ma sens przy ≈ 1,7 % nad kill switchem, bo kill switch karze σ, nie
   średnią.
2. Jeśli wdrażać, zamrozić dokładnie testowaną definicję (industry ≥4 w uniwersum → industry,
   inaczej sector; grupa ≥3; 5 par wg największego rozstępu) — każda inna definicja zmieniła znak
   Δ. I nie nazywać tego „parami wewnątrz branży”: 51 % par to pary wewnątrz sektora-zlepka.
3. Tańszy odpowiednik ~80 % efektu σ: vol-targeting / mniejsza alokacja na nogę albo wybór z rang
   dalszych niż 1–5 (T7) — bez zależności od taksonomii TV. Decyzję między „pary” a „niższy ALLOC”
   podjąć na koszyku-cieniu z taksonomią liczoną na żywo (pytanie z perspektywa-quant.md pkt ?
   pozostaje otwarte); test F o wariancji rozstrzygalny w 12–26 tygodni, o średniej nie.
4. Nie wdrażać a_branza w celu zachowania średniej — w danych punktowo obniża średnią i Sharpe'a
   w każdej definicji; jej jedyny zysk to σ/ogon, który b_pary daje taniej.

## Zastrzeżenia

- Taksonomia TV z jednego snapshotu (2026-W8) narzucona wstecz — test T3 zastępuje ją klastrami
  korelacyjnymi, nie historycznymi branżami; klastry mają 5–10 grup ≥3 (TV: 15), więc porównanie
  Δ nie jest w pełni symetryczne. Survivorship bias uniwersum wspólny dla none i wariantów.
- KHC, WBD przypisane ręcznie (jak w bt_neutralnosc.py); WBD ma 1 obserwację — bez znaczenia.
- Testy wielokrotne: 6 definicji TV × 2 konstrukcje + 11 klastrowań × 2 — wartości t
  nieskorygowane; wniosek o σ jest odporny na to (wszystkie σ-ratio <0,85), wniosek o Δ jest
  właśnie przez to „nierozstrzygalny”, nie „obalony”.
- Koszty i gross jak w bt_neutralnosc.py (0,10 %/noga rotacji + 6 %/rok na gross 200 %); brak
  korekty o dywidendy; wyniki w p.p. spreadu, nie w USD rachunku.
