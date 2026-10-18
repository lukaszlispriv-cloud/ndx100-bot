# Weryfikacja C5 — Wynik Modelu 3.0 nie ma mocy predykcyjnej na 5 sesji; jest momentum+betą; p skalibrowane odwrotnie

**Twierdzenie C5** (moc-predykcyjna-modelu.md, perspektywa-quant.md, audyt-regul.md): „Wynik Modelu 3.0 (TOP15/BOTTOM15, W1–W7) nie ma mocy predykcyjnej na 5 sesji (IC śr. −0,10, t −0,5; permutacja p=0,92), jest w ~75 % wyjaśniony momentum 6M/12M−1M i betą (Spearman 0,57–0,73), a p=50+0,5·(wynik−50) jest skalibrowane odwrotnie (p>55 % → 44,5 % trafień, p≥61 → 37,5 %)."

**Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM.** Rdzeń przeżył wszystkie próby obalenia: IC Wyniku jest ≤ 0 w każdej z czterech definicji okna (−0,04…−0,16), na 10 nogach koszyka (−0,09…−0,18), w obrębie strony (±0,02) i po usunięciu czynników (−0,05…−0,14); Wynik jest w przekroju w 67 % (R² rang) zdeterminowany przez momentum 6M/12M−1M i betę, a tygodniowy IC Wyniku jest w 97–99 % kopią IC proxy czynnikowego policzonego na tych samych 30 nazwach. Zastrzeżenia: **(1) „skalibrowane odwrotnie" jest przesadą** — po wyłączeniu W7 trafienia p>55 % rosną do 50,4 % (Wilson 42–59 %, przedział obejmuje deklarowane 58,7 %), Spearman(p, trafienie) = −0,02 (klastrowe 95 %: −0,12…+0,13); p jest *nieinformacyjne*, nie *odwrotne*; **(2) test nie ma mocy**: 95 % CI średniego IC to −0,57…+0,37, MDE 0,65, moc wykrycia IC 0,05 = 8 %; twierdzenie „nie ma mocy" wolno czytać wyłącznie jako „nie wykazano mocy", nie „wykazano jej brak"; **(3) „~75 %" zależy od definicji**: 67 % w przekroju 30 nazw, 97–99 % w dynamice IC, ale tylko 26–29 % w obrębie strony — czynniki decydują o przydziale LONG/SHORT, nie o kolejności w ramach strony; **(4) p permutacyjne 0,92 testuje złą hipotezę zerową** (sd śr. IC pod H0 bez struktury 0,07 vs realne se 0,19); **(5) trzy liczby kalibracji w twierdzeniu pochodzą z trzech różnych okien** (44,5 % z D0→D+5, 37,5 % z 70 nóg w oknie history).

Skrypt: `weryfikacja_C5.py` → `weryfikacja_C5_out.md`, `weryfikacja_C5_wyniki.json`, `weryfikacja_C5_nazwy.csv` (840 wierszy: 210 nazwo-tygodni × 4 okna), `weryfikacja_C5_T1_*.csv`. Dane: `mp_ranking.csv` (TOP15/BOTTOM15 W1–W8 z raportów), `mp_koszyki.json`, `closes_5y.csv` (dzisiejszy skład — survivorship bias dotyczy czynników, nie rankingu), `koszyki_historia.json` (fills → daty rotacji). Czynniki jak w `mp_ic_czynniki.py` (mom 6M = 126 sesji rel. ^NDX, mom 12M−1M = 231 sesji z pominięciem 21, beta 126d na log-zwrotach). Bez scipy: kwantyle t(6 df) wpisane ręcznie, Wilson z z = 1,96.

## 1. Testy wykonane i wyniki

### T1. IC na oknach „jak rachunek" (D+1 → rotacja) i w pozostałych definicjach okna

Kalendarz rachunku: wejście = pierwsza sesja po D0 (bieg 13:45 UTC ≈ zamknięcie tej sesji — przybliżenie), wyjście = sesja wejścia następnego koszyka wg fills (W5 29.09, W6 6.10, W7 12.10; W7 ucięte na 16.10). Dywidendy doliczone w oknach rachunek/history.

| okno | IC30 śr. (t) | dodatnich | IC10 nóg śr. (t) | IC w LONG15 / SHORT15 | spread 10 nóg p.p./tydz. (t) | trafienia 10 nóg | trafienia 30 nazw vs ^NDX / vs mediana uniwersum | bootstrap tyg.: P(IC30>0), 95 % |
|---|---|---|---|---|---|---|---|---|
| D0→D+5 (faza 1) | **−0,098 (−0,51)** | 3/7 | −0,087 (−0,38) | −0,02 / +0,01 | −2,02 (−0,53) | 33/70 = 47,1 % [36–59] | 44,8 % / 41,0 % | 0,29; −0,44…+0,24 |
| D+1→D+6 (5 sesji od wejścia) | −0,118 (−0,56) | 3/7 | −0,126 (−0,53) | +0,01 / +0,11 | −0,69 (−0,15) | 38/70 = 54,3 % [43–65] | 45,7 % / 43,3 % | 0,27; −0,48…+0,27 |
| rachunek: wejście→rotacja (2–11 sesji) | −0,156 (−0,69) | 3/7 | −0,179 (−0,72) | −0,01 / +0,06 | +0,46 (+0,09) | 34/70 = 48,6 % [37–60] | 43,8 % / 43,3 % | 0,23; −0,53…+0,25 |
| history: D0→DEND | −0,042 (−0,23) | 3/7 | −0,093 (−0,36) | −0,11 / −0,05 | −0,53 (−0,12) | 33/70 = 47,1 % [36–59] | 50,0 % / 48,1 % | 0,40; −0,36…+0,28 |

Źródło: weryfikacja_C5_out.md §T1. IC30 per tydzień w oknie rachunku: −0,45 / +0,39 / −0,61 / +0,79 / +0,14 / −0,72 / −0,64 — znak identyczny z D0→D+5 w 7/7 tygodni. Pooled Spearman po 210 nazwo-tygodniach (zwrot demeaned per tydzień): −0,13 (D0→D+5), −0,12 (D+1→D+6), −0,10 (rachunek), −0,03 (history); klastrowe 95 % po tygodniach odpowiednio −0,46…+0,21, −0,52…+0,29, −0,55…+0,33, −0,38…+0,33 — naiwne iid ±0,135 zaniża przedział ~2,5×.

Wniosek: zmiana okna na „jak rachunek" **nie ratuje** Wyniku — IC jest ujemne we wszystkich czterech definicjach, 3/7 tygodni dodatnich w każdej. Jedyny ślad na korzyść modelu: trafienia 10 nóg w oknie D+1→D+6 54,3 % — ale Wilson 43–65 % obejmuje 50 % i każdą inną hipotezę; spread 10 nóg w oknie rachunku +0,46 p.p./tydz. (t 0,09) powstaje z jednego 11-sesyjnego okna W4 (+27,2 p.p.), bez niego jest ujemny.

### T2. 10 nóg koszyka zamiast 30 nazw

IC10 (Spearman Wyniku i zwrotu na 10 nogach): −0,09 / −0,13 / −0,18 / −0,09 w czterech oknach, 3/7 tygodni dodatnich. W obrębie 5 nóg LONG: −0,09…−0,16 (t do −1,97 w oknie rachunku, 1/7 dodatnich) — ranga 1 w koszyku nie bije rangi 5; w obrębie 5 nóg SHORT: −0,03…−0,26 (t do −1,76). Koszyk faktyczny vs czysty TOP5/BOTTOM5 Wyniku: spread 10 nóg −2,02 vs −3,61 p.p./tydz. (D0→D+5); nadpisania reguł nie pogorszyły (to domena weryfikacji C-reguł, tu tylko kontrola). Źródło: §T1 kolumny ic10, icL5, icS5, spread_top5bot5.

### T3. Kalibracja p — czy „odwrotna" znika bez W7

| podzbiór (okno D0→D+5, trafienie vs ^NDX) | n | p>55: trafienia [Wilson] vs deklarowane | p≥61 | p≤58 | Spearman(p, trafienie) | Spearman(p, zwrot pozycji) |
|---|---|---|---|---|---|---|
| W1–W7 | 210 | **73/164 = 44,5 % [37–52]** vs 58,7 | 16/39 = 41,0 % [27–57] | 58/129 = 45,0 % | −0,018 | −0,048 |
| **bez W7** | 180 | **70/139 = 50,4 % [42–59]** vs 58,8 | 16/37 = 43,2 % [29–59] | 55/104 = 52,9 % | −0,040 | −0,086 |
| bez W6+W7 | 150 | 63/114 = 55,3 % [46–64] vs 59,1 | 15/35 = 42,9 % | 47/80 = 58,8 % | −0,049 | −0,101 |
| leave-one-week-out, zakres | 180 | 39,1 % (bez W5) … 50,4 % (bez W7) | 36,4 % … 50,0 % (bez W3) | 38,4 % … 52,9 % | −0,070 … +0,016 | −0,093 … +0,006 |

Okno rachunku: W1–W7 p>55 → 43,3 % [36–51]; bez W7 → 48,9 % [41–57]; bez W6+W7 → 56,1 % [47–65]. Baza „vs mediana uniwersum" (uczciwsza niż ^NDX przy szerokości rynku 31–67 %): W1–W7 40,9 %, bez W7 46,0 %, bez W6+W7 51,8 %. Klastrowy bootstrap po tygodniach (3000): Spearman(p, trafienie) −0,018 [−0,123…+0,128], Spearman(p, zwrot pozycji) −0,048 [−0,188…+0,090], P(<0) = 0,76; okno rachunku −0,045 [−0,156…+0,102] i −0,051 [−0,177…+0,054], P(<0) = 0,85. Spearman(p, zwrot) w obrębie tygodnia: śr. −0,07 (t −0,88), dodatni w 2/7 (W1, W2); bez W7 −0,06 (t −0,64). Źródło: §T3.

Reprodukcja liczb z twierdzenia: 44,5 % = 73/164 (D0→D+5, 30 nazw); 37,5 % = 12/32 **tylko** na 70 nogach w oknie history D0→DEND (jak audyt-regul); w oknie D0→D+5 te same nogi dają 14/32 = 43,8 % [28–61], w oknie rachunku 13/32 = 40,6 % [26–58]. Przedziały Wilsona dla p≥61 (n 30–39) mają szerokość ~30 p.p. i w każdym podzbiorze obejmują 50 %.

Wniosek: **„odwrotna kalibracja" nie jest cechą próby, lecz W6–W7** (p>55: 7/25 i 3/25 trafień przy 66–76 % uniwersum bijącym ^NDX). Co przeżywa: p>55 w pełnej próbie trafia poniżej deklaracji (Wilson 37–52 % wyklucza 58,7 %) oraz p jest **nieinformacyjne** — korelacja p z trafieniem i ze zwrotem jest ≈ 0 w każdym podzbiorze i oknie (|Spearman| ≤ 0,10, wszystkie przedziały klastrowe obejmują 0). Słowo „odwrotnie" trzeba zastąpić „bez związku z wynikiem"; bez W7 nie da się nawet odrzucić, że p jest skalibrowane poprawnie.

### T4. IC na resztach po becie i momentum — ranking w obrębie kwintyli, rangowa OLS, model vs proxy

| statystyka (Spearman Wyniku z…) | D0→D+5: śr. (t), dodatnich | rachunek: śr. (t), dodatnich |
|---|---|---|
| zwrot surowy | −0,10 (−0,51), 3/7 | −0,16 (−0,69), 3/7 |
| percentyl zwrotu W OBRĘBIE kwintyla bety 126d (uniwersum ~90) | −0,06 (−0,56), 3/7 | −0,05 (−0,62), 1/7 |
| … kwintyla mom 6M | −0,05 (−0,44), 4/7 | −0,05 (−0,39), 2/7 |
| … kwintyla mom 12M−1M | −0,10 (−1,12), 3/7 | −0,08 (−0,89), 2/7 |
| … tercyl bety × tercyl mom 6M | −0,08 (−0,73), 2/7 | −0,08 (−0,77), 2/7 |
| reszta rangowej OLS zwrotu na rangach (beta, mom 6M, mom 12M−1M) w uniwersum | −0,14 (−1,52), 3/7 | −0,08 (−0,69), 2/7 |
| **IC proxy czynnikowego** (śr. rang mom 6M, mom 12M−1M, bety) na TYCH SAMYCH 30 nazwach | −0,18 (−0,82) | −0,20 (−0,78) |
| **IC modelu − IC proxy** (parowane) | **+0,06 (+1,23), 5/7** | **+0,04 (+0,98), 5/7** |
| IC modelu na reszcie po proxy w obrębie 30 nazw | +0,02 (+0,66) | −0,01 (−0,33) |
| corr(IC modelu, IC proxy) po tygodniach | **0,99 (R² 0,97)** | **1,00 (R² 0,99)** |

Źródło: §T4. R² rangowej OLS zwrotu na trzech czynnikach w uniwersum: 0,07–0,76 (śr. 0,27 D0→D+5; 0,40 rachunek) — w W6–W7 beta i momentum wyjaśniają 36–76 % przekroju zwrotów, stąd te tygodnie „robią" IC.

Wniosek: po usunięciu czynników IC nadal ≤ 0, ale bliżej zera i nigdzie istotne — warstwa uznaniowa **nic nie dodaje i nic nie psuje**: model wobec własnego proxy czynnikowego ma +0,06 IC (t 1,2), czyli 20 czynników fundamentalnych + narracja = momentum i beta ± szum. Ujemny surowy IC jest w całości ujemnym IC proxy (−0,18) w tygodniach, gdy półprzewodniki/beta przegrywały.

### T5. Moc testu — jakiego IC nie można wykluczyć

| okno | sd tygodniowego IC30 | se (n=7) | 95 % CI średniego IC (t, 6 df) | MDE (80 % mocy, α 5 %) | moc wykrycia IC 0,05 / 0,10 / 0,30 (jednostr.) | tygodni do t=2 dla IC 0,03 / 0,05 / 0,10 |
|---|---|---|---|---|---|---|
| D0→D+5 | 0,511 | 0,193 | **−0,57 … +0,37** | 0,65 | 8 % / 12 % / 39 % | 1163 / 419 / 105 |
| D+1→D+6 | 0,561 | 0,212 | −0,64 … +0,40 | 0,71 | 8 % / 11 % / 34 % | 1400 / 504 / 126 |
| rachunek | 0,596 | 0,225 | −0,71 … +0,40 | 0,76 | 8 % / 11 % / 32 % | 1580 / 569 / 143 |

Pod H0 niezależnych 30 nazw sd IC byłoby 1/√29 = 0,19; obserwowane 0,51–0,60 jest **2,8–3,2× większe**, bo Wynik ładuje czynniki, a zwroty czynników huśtają IC całego przekroju. Permutacja (Wynik tasowany w tygodniu, 5000×): sd śr. IC 0,070, pasmo 5–95 % −0,117…+0,112, P(≥ obs) = 0,916 — reprodukuje fazę 1, ale: (a) IC 0,05 leży w paśmie zerowej mocy, więc test z 7×30 nie odróżnia IC 0,05 od zera; (b) H0 permutacji („Wynik nie ma żadnej struktury") nie jest hipotezą, którą ktoś broni — Wynik ma strukturę czynnikową, więc właściwe se jest 2,7× większe niż permutacyjne. Źródło: §T5.

Wniosek: 210 obserwacji **nie daje** mocy wykrycia IC 0,05 (8 %, czyli poziom α); nie można wykluczyć IC aż do **+0,37…+0,40** ani ujemnego do **−0,57…−0,71**. Dla porównania: IC 0,05 to już dobry sygnał tygodniowy, IC 0,37 byłby nieprawdopodobny. Twierdzenie w formie „model NIE MA mocy" jest nieuprawnione; w formie „model nie wykazał mocy, a dane nie pozwalają jej wykryć" — tak.

### T6. „~75 % wyjaśnione momentum i betą" — pomiar

R² regresji rang Wyniku na rangach czynników (30 nazw, per tydzień, śr. W1–W7): mom 6M sam **0,60**; beta sama 0,42; mom 6M + mom 12M−1M 0,66; **trzy czynniki 0,67** (zakres 0,55–0,75); z vol 20d 0,69. **W obrębie strony**: LONG15 **0,29**, SHORT15 **0,26** (zakres 0,06–0,45). Spearman przydziału strony (LONG=1) z mom 6M: 0,62–0,87 (śr. 0,79). W8: R² trzech czynników 0,41 (beta 0,00) — potwierdza zmianę tożsamości modelu z fazy 1. Źródło: §T6. Spearmany 0,57 (beta) i 0,73 (mom 6M) z twierdzenia reprodukują się w mp_ic_czynniki_out.md §(c).

Wniosek: „~75 %" jest **prawdziwe dla jednej definicji i fałszywe dla dwóch innych**: 67 % Wyniku w przekroju 30 nazw (blisko), 97–99 % jego IC w czasie (więcej), ale 26–29 % kolejności w obrębie strony (dużo mniej). Czynniki decydują, kto jest LONG a kto SHORT; kolejność w ramach strony to „coś innego" — tyle że to coś innego ma IC ≈ 0 (LONG15 −0,02, SHORT15 +0,01).

### Dodatek: horyzont 10 i 15 sesji (poza twierdzeniem)

IC Wyniku na 10 sesjach od D0: +0,09 (t 0,39, n=6); na 15 sesjach **+0,49 (t 4,75, n=4, W1–W4)**. Nie traktować jako dowodu: cztery okna 15-sesyjne W1–W4 (26.08→17.09 … 11.09→2.10) nakładają się na jeden epizod rajdu półprzewodników, efektywne n ≈ 1; W5–W7 nie mają jeszcze 15 sesji. Zapisane jako pytanie: Wynik może być proxy momentum o horyzoncie 3–4 tygodni, a nie 5 sesji — testowalne po W8–W10. Źródło: §Dodatek.

## 2. Najsilniejszy kontrargument

Cała „odwrotna kalibracja" i większość ujemnego IC to dwa tygodnie (W6–W7), w których 63–76 % uniwersum biło ^NDX, a beta/półprzewodniki przegrały: bez W7 trafienia p>55 % wynoszą 50,4 % (Wilson 42–59 %, deklarowane 58,7 % w przedziale), bez W6+W7 55–56 %; korelacja p z trafieniem jest ≈ 0 w każdym podzbiorze (−0,07…+0,02), a nie ujemna. Jednocześnie test IC ma 8 % mocy na IC 0,05 i nie wyklucza IC +0,37 — więc dane nie pokazują ani odwrotnej kalibracji, ani braku mocy; pokazują **nic**, co jest słabszym, ale jedynym uprawnionym wnioskiem. Kontrargument nie obala rdzenia (model = proxy czynnikowe ± szum, R² IC 0,97–0,99, IC modelu − IC proxy +0,06 nieistotne), bo ten rdzeń nie zależy od W7 (corr IC modelu z proxy bez W7 nadal 0,99 — proxy i model to te same rangi), ale obala przymiotnik „odwrotnie" i przeformułowuje „nie ma mocy" na „nie wykazano mocy".

## 3. Twierdzenie po weryfikacji

„Wynik Modelu 3.0 (TOP15/BOTTOM15, W1–W7) **nie wykazał** mocy predykcyjnej na 5 sesji: IC śr. −0,10 (t −0,5) w oknie D0→D+5 i −0,16 (t −0,7) w oknie „jak rachunek", 3/7 tygodni dodatnich w każdej z 4 definicji okna, na 10 nogach −0,09…−0,18, w obrębie strony ±0,02; 95 % CI średniego IC −0,57…+0,37 (MDE 0,65, moc na IC 0,05 = 8 %), więc nie da się wykluczyć ani przewagi IC +0,37, ani szkody −0,57. Wynik jest w przekroju w 67 % (R² rang, 0,55–0,75) funkcją momentum 6M/12M−1M i bety (Spearman 0,73/0,72/0,57), które decydują o przydziale strony (R² w obrębie strony tylko 0,26–0,29); tygodniowy IC Wyniku jest w 97–99 % IC proxy czynnikowego na tych samych 30 nazwach, a nadwyżka modelu nad proxy wynosi +0,06 (t 1,2) — warstwa uznaniowa nic nie dodaje ani nie odejmuje. p=50+0,5·(wynik−50) jest **nieinformacyjne**, nie odwrotne: Spearman(p, trafienie) −0,02 (klastrowe 95 %: −0,12…+0,13); trafienia p>55 % w pełnej próbie 44,5 % (Wilson 37–52 %) leżą poniżej deklarowanych 58,7 %, ale bez W7 wynoszą 50,4 % (42–59 %), a bez W6+W7 55,3 % — rozjazd z deklaracją jest skutkiem dwóch tygodni o szerokości rynku 63–76 %, nie cechą p; liczba 37,5 % (p≥61) dotyczy 32 nóg w oknie history i ma Wilson 23–55 %."

## 4. Implikacja projektowa

1. **p usunąć z tabel albo publikować jako rangę** — nie dlatego, że jest odwrotne (tego dane nie pokazują), ale dlatego, że nie niesie informacji (|Spearman| ≤ 0,05 z trafieniem przy 210 obs.) i udaje prawdopodobieństwo. Zastąpić zdaniem: „IC Wyniku −0,10, 95 % CI −0,57…+0,37, n = 7 — moc nieustalona".
2. **Nie uzasadniać decyzji o Modelu samym W1–W7** — ani „model szkodzi" (CI sięga +0,37), ani „model działa" (sięga −0,57). Przy sd IC 0,5–0,6 potrzeba 420–570 tygodni, by rozstrzygnąć o IC 0,05; żaden realny okres handlu tego nie da. Zamiast rozstrzygać o IC Wyniku, mierzyć co tydzień **IC modelu − IC proxy czynnikowego** (mom 6M, mom 12M−1M, beta na tych samych 30 nazwach) — to jedyna statystyka, której sd nie jest napędzane zwrotami czynników (tu +0,06 ± 0,13) i która mierzy warstwę uznaniową osobno; po ~30 tygodniach odpowie, czy uznanie coś wnosi.
3. **Sizing i ryzyko kalibrować do IC ≈ 0 z szeroką niepewnością**, czyli do konstrukcji (ekspozycja na SOX−NDX, beta netto, σ koszyka), nie do „trafności modelu" — to zgodne z fazą 1/2 i z weryfikacją C-sizing; C5 dodaje, że dowód trafności jest niemożliwy w horyzoncie życia rachunku.
4. **Rozdzielić przydział strony (czynnikowy, 67 % Wyniku) od kolejności w stronie (uznaniowa, 26–29 %)** i zapisywać oba maszynowo (ranking-<version>.json), bo dzisiejsze tabele HTML nie pozwalają odróżnić, które z nich zawiodło w danym tygodniu.
5. Otwarte: IC na 15 sesjach +0,49 (n=4, jeden epizod) — jeśli po W8–W10 utrzyma się na niezależnych oknach, Model 3.0 jest sygnałem 3–4-tygodniowym grany na 5 sesjach, co zmienia rotację, nie scoring.

## 5. Zastrzeżenia metodyczne

- Wejście „13:45 UTC" przybliżone zamknięciem sesji wejścia; brak OHLC. Zmiana na otwarcie przesunęłaby zwroty o ruch intraday jednej sesji; kierunek IC nie zależał od tego w 7/7 tygodni (D0→D+5 vs rachunek).
- Czynniki liczone na dzisiejszym składzie NDX-100 (survivorship) — dotyczy kwintyli i proxy w T4/T6, nie samego IC Wyniku.
- Ranking W1–W7 z HTML (mp_ranking.csv, 97 % zgodności p ze wzorem); 2–4 nazwy na tydzień bez pełnej historii 253 sesji wypadają z testów czynnikowych (n 26–28 zamiast 30).
- 7 tygodni to 7 obserwacji czynnikowych; wszystkie t-staty tygodniowe mają 6 df, a przedziały Wilsona dla podzbiorów n 25–39 mają szerokość 28–36 p.p.
