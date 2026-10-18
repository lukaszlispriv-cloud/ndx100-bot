# Moc predykcyjna Modelu 3.0 i prostych czynników ilościowych na horyzoncie 5 sesji (NDX100, W1–W8)

Data analizy: 18.10.2026. Gałąź `claude/gifted-lamport-iwzpop`. Wszystkie liczby ze skryptów (pandas 3.0.6 / numpy 2.4.6; brak scipy — Spearman przez rangi + Pearson, t-staty i permutacje własne). Żadnych liczb z rachunku — wyłącznie p.p., % i korelacje.

Skrypty (katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):

| plik | co robi | wyjście |
|---|---|---|
| `mp_parse_raporty.py` | wyciąga z `reports/raport-2026-W1..W8.html` tabele TOP15/BOTTOM15 (ticker, Wynik, p, strona, status, podświetlenie) i koszyki TOP5/BOTTOM5 | `mp_ranking.csv` (240 wierszy = 8 tyg. × 30), `mp_koszyki.json` |
| `mp_lib.py` | wczytanie `closes_5y.csv` (wiersze świąt 2026-05-25 i 2026-09-07 odrzucone), zwroty forward rel. ^NDX, Spearman, t, dywidendy z raportów (PEP 1,48; NVDA 0,25; AVGO 0,65; CMCSA 0,33; MU 0,15) | — |
| `mp_ic_model.py` | IC Wyniku vs zwrot 5-sesyjny, hit rate grup, kalibracja p | `mp_ic_model_out.md`, `mp_model_nazwy.csv`, `mp_model_tygodnie.csv` |
| `mp_ic_czynniki.py` | IC 10 czynników ilościowych: W1–W7 i 208 okien 2022-10→2026-10; na co „patrzy” Wynik; koszyki czynnikowe w W1–W7 | `mp_ic_czynniki_out.md`, `mp_ic_czynniki_okna.csv`, `mp_ic_czynniki_summary.json` |
| `mp_dodatek.py` | IC modelu vs IC czynników, nadwyżka nad uniwersum, IC na resztach po becie/momentum, moc testu | `mp_dodatek_out.md` |
| `mp_spojnosc.py` | spójność Wyniku tydzień do tygodnia, rotacja tabel, nadpisania koszyka | `mp_spojnosc_out.md` |

Definicje: D0 z raportów (W1 26.08 śr., W2 28.08, W3 4.09, W4 11.09, W5 28.09 pon., W6 2.10, W7 9.10, W8 16.10). **Okno „5 sesji”** = zamknięcie D0 → zamknięcie 5. sesji po D0 (W3: 14.09, W4: 18.09, W5: 5.10 — inne niż okna faktycznie rozliczone 11.09 / 28.09 / 2.10). **Okno faktyczne** = jak w `history` (W1 2 sesje, W3 4, W4 11, W5 4). Zwrot relatywny = zwrot spółki − zwrot ^NDX; zwrot pozycji = rel dla LONG, −rel dla SHORT. Kontrola: spread z okien faktycznych z dywidendami odtwarza `history` co do 0,01 p.p. dla W1–W7 (−4,06; 6,19; 1,44; 13,85; 5,95; −5,89; −21,15) — liczby z `mp_ic_model_out.md`.

---

## 0. Wynik w sześciu zdaniach

1. **Wynik Modelu 3.0 nie przewiduje 5-sesyjnego zwrotu relatywnego.** Średni tygodniowy IC (Spearman Wyniku i zwrotu, 30 nazw TOP15+BOTTOM15) = **−0,10** w oknach 5-sesyjnych (t = −0,51) i **−0,04** w oknach faktycznych (t = −0,20); test permutacyjny: P(IC ≥ obserwowany | brak mocy) = 0,92; przedział 5–95 % przy zerowej mocy ±0,12. Pooled po 210 nazwo-tygodniach: −0,13. Ranking **w obrębie** strony (czy TOP1 bije TOP15) też nic nie niesie: IC_long15 −0,02, IC_short15 +0,01.
2. **p jest funkcją Wyniku, nie oceną** (wzór B4 `50+0,5·(wynik−50)`, obcięcie 38–62: zgodność z tabelami 97 % wierszy) **i jest skalibrowane odwrotnie:** nazwy z p > 55 % trafiły **73/164 = 44,5 %** (95 %: 37–52 %) przy deklarowanych średnio 58,7 %; tercyl najsilniejszych sygnałów (|wynik−50| ≥ 19) trafił 40,6 % i dał −1,97 p.p./pozycję, najsłabszych 46,3 % / −0,79.
3. **Tygodniowy sukces modelu to w całości zakład na betę / półprzewodniki:** korelacja tygodniowego IC modelu z tygodniowym IC bety w uniwersum 0,93, z IC momentum 12M−1M 0,95, ze spreadem ^SOX−^NDX 0,90 (n = 7). Wynik Modelu koreluje z momentum 6M na 0,73, z 12M−1M na 0,72, z odległością od MA200 na 0,72, z betą na 0,57 (średnie Spearmana z 8 tygodni, t 7–23). Po odjęciu bety i momentum 6M IC modelu na resztach = −0,12 (t = −1,5): poza czynnikami nie ma nic, a jeśli coś — to ze znakiem ujemnym.
4. **Z 10 prostych czynników w 208 oknach tygodniowych 2022–2026 żaden nie ma IC z |t| > 2 poza zmiennością 20d (IC +0,05, t 2,11) i betą (+0,05, t 1,93) — a te dwa to czyste zakłady na kierunek rynku**, nie selekcja: w tygodniach ^NDX ≤ −2 % ich IC wynosi −0,30/−0,39 (t −8/−9), w tygodniach ≥ +2 % +0,33/+0,44 (t +14/+16). Momentum 6M i 12M−1M mają IC +0,02/+0,03 (t 1,2/1,4; Q5−Q1 +0,5/+0,6 p.p./tydz., t 1,6/2,0), dodatnie w 4 z 5 lat (ujemne w 2023). Momentum 1T/1M/3M, odwrócenie 1T i odległość od szczytu 52-tyg.: IC ≈ 0.
5. **Przy sd tygodniowego IC 0,26–0,38 wykrycie IC 0,03 wymaga 300–650 tygodni; IC 0,05 — 110–230.** Siedem tygodni nie rozstrzyga niczego o Modelu (sd jego IC 0,51 → 400 tygodni dla IC 0,05) i nikt nie powinien udawać, że rozstrzyga.
6. **Koszt uznaniowości jest widoczny w danych:** (a) Wynik „goni kurs” — zmiana Wyniku tej samej spółki między sobotami koreluje z jej zwrotem relatywnym między D0 (0,53–0,83 w 5 z 7 par); (b) koszyk w 10 z 16 stron W2–W8 odbiega od TOP5/BOTTOM5 rankingu, w W8 7 z 10 nóg to nadpisania regułami/filtrami (13 z 30 wierszy W8 ma status wykluczenia); (c) po W7 model zmienił charakter: korelacja Wyniku z betą spadła z 0,53–0,73 do 0,03, ze zmiennością z +0,35…+0,67 do −0,32 (W8) — statystyka W1–W7 nie dotyczy już W8.

---

## 1. Moc predykcyjna Wyniku Modelu 3.0 (W1–W7)

### 1.1 IC per tydzień (`mp_ic_model_out.md`)

| tydz. | D0 | D+5 (5 sesji) | koniec faktyczny | IC30 (5 sesji) | IC30 (okno fakt.) | IC w TOP15 | IC w BOTTOM15 | spread 5 sesji p.p. | spread fakt. (=history) | hit TOP5 / BOT5 (5 sesji) | udział uniwersum > ^NDX |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 26.08 | 02.09 | 28.08 | −0,16 | −0,33 | +0,31 | −0,28 | −3,26 | −4,06 | 3/5, 2/5 | 34 % |
| W2 | 28.08 | 04.09 | 04.09 | +0,33 | +0,33 | +0,46 | +0,18 | +6,40 | +6,19 | 4/5, 3/5 | 39 % |
| W3 | 04.09 | 14.09 | 11.09 | −0,59 | −0,03 | −0,17 | +0,05 | −3,88 | +1,44 | 1/5, 2/5 | 43 % |
| W4 | 11.09 | 18.09 | 28.09 | +0,58 | +0,61 | −0,15 | +0,09 | +7,29 | +13,85 | 3/5, 4/5 | 31 % |
| W5 | 28.09 | 05.10 | 02.10 | +0,34 | +0,35 | −0,19 | +0,18 | +6,04 | +5,95 | 3/5, 5/5 | 36 % |
| W6 | 02.10 | 09.10 | 09.10 | −0,54 | −0,54 | −0,20 | −0,18 | −5,59 | −5,89 | 1/5, 2/5 | 67 % |
| W7 | 09.10 | 16.10 | 16.10 | −0,65 | −0,65 | −0,22 | +0,06 | −21,15 | −21,15 | 0/5, 0/5 | 76 % |
| **śr. / t** | | | | **−0,10 / −0,51** | **−0,04 / −0,20** | −0,02 / −0,20 | +0,01 / +0,19 | −2,02 / −0,53 | −0,52 / −0,12 | | |

- Permutacja (5000 losowań Wyniku w obrębie tygodnia): P(średni IC30 ≥ −0,098) = **0,916**; przy zerowej mocy średnia 7 IC mieści się w ±0,12 (5–95 %). Obserwowany model jest w dolnej połowie rozkładu „losowego”.
- W3 pokazuje kruchość: to samo rozliczenie liczone do 11.09 (4 sesje, jak w `history`) daje IC −0,03, a do 14.09 (5. sesja) −0,59. Jedna sesja zmienia IC 30 nazw o 0,56.
- **Ranking w obrębie strony nie działa**: IC w TOP15 dodatni tylko w 2 z 7 tygodni, w BOTTOM15 w 5 z 7, obie średnie ≈ 0. Czyli nie ma dowodu, że TOP1–5 jest lepsze od TOP6–15.

### 1.2 Hit rate: koszyk (TOP5/BOTTOM5) vs ranking 6–15 vs reszta uniwersum (okno 5 sesji, równe wagi)

| strona | grupa | n nóg | hit | śr. zwrot pozycji p.p. | sd | t (nogi) | t (7 tyg., klastrowane) | nadwyżka nad średnią uniwersum p.p./tydz. (t) |
|---|---|---|---|---|---|---|---|---|
| LONG | koszyk TOP5 | 35 | **42,9 %** | −1,98 | 6,55 | −1,79 | −1,01 | −1,61 (−0,66) |
| LONG | ranking 6–15 / wykluczone | 70 | 40,0 % | −1,94 | 6,89 | −2,35 | −1,10 | −1,56 (−0,75) |
| SHORT | koszyk BOTTOM5 | 35 | **51,4 %** | −0,04 | 6,13 | −0,04 | −0,02 | −0,42 (−0,25) |
| SHORT | ranking 6–15 / wykluczone | 70 | 47,1 % | −0,67 | 5,79 | −0,97 | −0,68 | −1,04 (−1,56) |
| reszta uniwersum (ok. 72 nazwy) | baza „losowa nazwa” | — | udział > ^NDX: 34–43 % w W1–W5, 67–76 % w W6–W7 | śr. rel: −2,0…−0,2 (W1–W5), +1,0/+3,8 (W6–W7) | | | | |

Wnioski: (i) koszyk nie różni się od miejsc 6–15 (LONG 42,9 vs 40,0 %, SHORT 51,4 vs 47,1 %; różnice zwrotów 0,04 i 0,63 p.p. przy sd ~6) — model nie odróżnia swoich najlepszych od przeciętnych; (ii) **baza dla strony LONG nie wynosi 50 %**: przez pięć tygodni tylko 31–43 % spółek biło kapitalizacyjny ^NDX (ciągnięty przez mega-capy), a w W6–W7 67–76 % — hit rate LONG liczony vs ^NDX mierzy głównie szerokość rynku; (iii) nadwyżka obu stron nad średnią równoważonego uniwersum jest ujemna (−1,6 i −0,4 p.p./tydz.) i nieistotna.

Okna faktyczne (jak `history`) dają 33/70 trafień koszyka — równie nieodróżnialne od losowości (Wilson 36–59 %; policzone w `dekompozycja-wynikow.md`, tu nie powtarzam).

### 1.3 Kalibracja p

p z tabel = `50 + 0,5·(Wynik − 50)` obcięte do 38–62 (dla SHORT w W1–W7 raportowano 100 − p jako „p trafienia”, w W8 surowe p outperformance — znormalizowano do p trafienia). Zgodność z wzorem 97 % wierszy → **p nie jest niezależną oceną prawdopodobieństwa, tylko przeskalowanym Wynikiem**; „kalibracja p” = kalibracja Wyniku.

| p trafienia (deklarowane) | n | trafień | hit | deklarowane śr. | śr. zwrot pozycji p.p. |
|---|---|---|---|---|---|
| ≤ 54 % | 22 | 11 | 50,0 % | 53,5 % | +0,35 |
| 55–56 % | 52 | 23 | 44,2 % | 55,6 % | −1,14 |
| 57–58 % | 55 | 24 | 43,6 % | 57,5 % | −1,53 |
| 59–60 % | 37 | 16 | 43,2 % | 59,6 % | −1,52 |
| 61–62 % | 39 | 16 | 41,0 % | 61,6 % | −1,73 |
| **p > 55 %** | **164** | **73** | **44,5 % (95 %: 37–52 %)** | 58,7 % | −1,37 |
| p ≤ 55 % | 41 | 17 | 41,5 % (26–57 %) | 54,2 % | −0,86 |

Per tydzień p > 55 %: W1 12/27, W2 13/22, W3 3/18, W4 16/21, W5 19/26, W6 7/25, W7 3/25 — kalibracja „działa” tylko w tygodniach, gdy półprzewodniki biją indeks. Monotoniczność jest **odwrotna**: im wyższe p, tym gorzej. Przy n = 164 górna granica 52 % wyklucza deklarowane 58,7 % — to jeden z niewielu twardych wyników tej analizy, choć in-sample i zdominowany przez W6–W7.

---

## 2. Proste czynniki ilościowe (closes_5y.csv) — IC do zwrotu 5-sesyjnego rel. ^NDX

Czynniki na D0 (tylko dane ≤ D0; spółki z pełnymi 252 sesjami historii, 75–91 na okno): momentum relatywne 1T (5 sesji), 1M (21), 3M (63), 6M (126), 12M−1M (231 sesji z pominięciem ostatnich 21); odwrócenie 1T = −mom 1T; odległość od MA200; zmienność 20d (sd log-zwrotów); beta 126d do ^NDX; dodatkowo odległość od szczytu 52-tyg. Okna całej próby: D0 = ostatnia sesja tygodnia ISO → ostatnia sesja następnego (3–6 sesji), 208 okien 21.10.2022 → 16.10.2026. **Uniwersum to dzisiejszy skład NDX-100 → survivorship bias** (faworyzuje momentum/betę: zwycięzcy, którzy weszli do indeksu, są w próbie od początku).

### 2.1 Cała próba (`mp_ic_czynniki_out.md` §b)

| czynnik | IC śr. | sd IC | **t** | udział IC > 0 | Q5−Q1 p.p./tydz. | t(Q5−Q1) |
|---|---|---|---|---|---|---|
| mom 1T | −0,00 | 0,22 | −0,25 | 50 % | +0,20 | 0,77 |
| mom 1M | −0,01 | 0,22 | −0,58 | 49 % | +0,22 | 0,87 |
| mom 3M | −0,00 | 0,26 | −0,12 | 52 % | +0,17 | 0,53 |
| mom 6M | +0,02 | 0,26 | 1,19 | 55 % | +0,50 | 1,57 |
| **mom 12M−1M** | +0,03 | 0,28 | **1,43** | 58 % | +0,64 | **1,96** |
| odwrócenie 1T | +0,00 | 0,22 | 0,25 | 50 % | −0,18 | −0,69 |
| odległość od MA200 | +0,01 | 0,27 | 0,75 | 54 % | +0,35 | 1,11 |
| **zmienność 20d** | +0,05 | 0,31 | **2,11** | 58 % | +1,12 | **3,43** |
| **beta 126d** | +0,05 | 0,38 | **1,93** | 57 % | +1,07 | **2,71** |
| odl. od szczytu 52-tyg. | −0,02 | 0,25 | −0,88 | 50 % | −0,30 | −1,13 |

**Żaden czynnik nie przekracza |t| = 2 na IC** (zmienność 2,11 na granicy). Q5−Q1 zmienności/bety ma t 2,7–3,4 — ale to nie jest alfa:

| czynnik | ^NDX w oknie ≤ −2 % (n 39) | −2…+2 % (n 114) | ≥ +2 % (n 55) |
|---|---|---|---|
| zmienność 20d | **−0,30 (t −8,0)** | +0,02 (1,1) | **+0,33 (t 13,7)** |
| beta 126d | **−0,39 (t −9,4)** | +0,02 (0,6) | **+0,44 (t 16,4)** |
| mom 6M | −0,09 (−2,2) | +0,01 (0,6) | +0,12 (3,4) |
| mom 12M−1M | −0,08 (−1,8) | +0,02 (0,8) | +0,12 (3,2) |
| odl. od MA200 | −0,10 (−2,1) | +0,01 (0,2) | +0,11 (3,0) |
| odl. od szczytu 52-tyg. | +0,10 (2,6) | −0,02 (−0,9) | −0,09 (−2,4) |

Dodatni IC zmienności/bety w całej próbie to premia za trzymanie ryzyka rynkowego w okresie 2022-10→2026-10 (hossa) — czysty zakład kierunkowy, który w tygodniu spadkowym kosztuje tyle, ile w wzrostowym daje. Momentum 6M/12M−1M też ma ten składnik (IC rośnie z ^NDX), ale słabszy: w tygodniach płaskich pozostaje +0,01/+0,02.

Lata (IC śr., t): mom 12M−1M 2022 +0,08 (0,8; n 11), 2023 −0,03 (−0,8), 2024 +0,06 (1,5), 2025 +0,02 (0,7), 2026 +0,05 (1,1). Mom 6M odpowiednio +0,04 / −0,03 / +0,02 / +0,05 / +0,05. **2023 był ujemny dla wszystkiego, co momentum-podobne** (mom 1M t −2,5, mom 3M −2,3, odl. od szczytu −2,7). Ostatnie 26 okien (IV–X 2026): wszystkie |t| < 0,7.

Korelacje rang między czynnikami (ostatnie 52 okna): mom 6M ~ odl. MA200 0,96, ~ 12M−1M 0,73, ~ mom 3M 0,71; zmienność ~ beta 0,75; mom 1T ~ mom 1M 0,45. Faktycznie są trzy niezależne „sygnały”: krótkie (1T/1M), średnie/długie momentum (3M–12M, MA200, szczyt 52-tyg.) i ryzyko (zmienność/beta).

### 2.2 Te same czynniki w tygodniach W1–W7 (`mp_ic_czynniki_out.md` §a)

| tydz. | mom 1T | mom 1M | mom 3M | mom 6M | mom 12M−1M | odl. MA200 | zmienność 20d | beta | odl. szczytu |
|---|---|---|---|---|---|---|---|---|---|
| W1 | −0,10 | −0,05 | −0,11 | −0,28 | −0,25 | −0,29 | −0,11 | −0,28 | −0,01 |
| W2 | −0,34 | −0,05 | −0,42 | +0,05 | +0,28 | −0,01 | +0,26 | +0,40 | −0,41 |
| W3 | −0,28 | −0,15 | −0,13 | −0,15 | −0,17 | −0,16 | −0,16 | −0,28 | +0,12 |
| W4 | +0,15 | +0,09 | +0,04 | +0,36 | +0,39 | +0,40 | +0,29 | +0,36 | +0,11 |
| W5 | +0,01 | +0,05 | −0,03 | +0,37 | +0,21 | +0,26 | +0,41 | +0,45 | −0,07 |
| W6 | −0,17 | −0,38 | +0,16 | −0,32 | −0,40 | −0,26 | −0,29 | −0,55 | +0,03 |
| W7 | +0,33 | −0,39 | −0,12 | −0,52 | −0,41 | −0,51 | −0,69 | **−0,87** | +0,05 |
| śr. (t) | −0,06 (−0,6) | −0,13 (−1,7) | −0,09 (−1,3) | −0,07 (−0,5) | −0,05 (−0,4) | −0,08 (−0,7) | −0,04 (−0,3) | −0,11 (−0,6) | −0,03 (−0,4) |

Koszyk 5/5 „z samego czynnika” (TOP5/BOTTOM5 percentyla w uniwersum) w tych siedmiu oknach, suma p.p.: mom 6M −22,0; mom 3M −21,5; beta −20,1; odl. MA200 −12,9; 12M−1M −8,3; mom 1M −4,8; mom 1T −4,7; zmienność +3,8; odwrócenie 1T +4,7 — wszystkie |t| ≤ 1,5. W7 koszyk czystego momentum 6M dał −13,9 p.p. (raport W8 podaje dla swojego benchmarku −13,64 — zgodne), koszyk bety −20,8 — Model (−21,15) zachował się jak **koszyk najwyższej bety**, nie jak koszyk momentum.

### 2.3 Na co „patrzy” Wynik Modelu 3.0 (`mp_ic_czynniki_out.md` §c)

Spearman(Wynik, czynnik na D0) wśród 30 nazw TOP15+BOTTOM15:

| tydz. | mom 1T | mom 1M | mom 3M | mom 6M | mom 12M−1M | odl. MA200 | zmienność 20d | beta | odl. szczytu |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 0,21 | 0,29 | 0,09 | 0,66 | 0,63 | 0,66 | 0,44 | 0,59 | 0,18 |
| W2 | 0,14 | −0,05 | −0,01 | 0,70 | 0,62 | 0,64 | 0,28 | 0,53 | 0,27 |
| W3 | 0,63 | 0,18 | 0,18 | 0,82 | 0,77 | 0,81 | 0,43 | 0,71 | 0,18 |
| W4 | 0,72 | 0,17 | −0,04 | 0,81 | 0,78 | 0,81 | 0,54 | 0,73 | 0,44 |
| W5 | 0,57 | 0,70 | −0,16 | 0,84 | 0,76 | 0,81 | 0,67 | 0,73 | 0,29 |
| W6 | 0,61 | 0,83 | 0,60 | 0,80 | 0,85 | 0,85 | 0,65 | 0,70 | 0,62 |
| W7 | 0,11 | 0,76 | 0,72 | 0,79 | 0,74 | 0,81 | 0,35 | 0,53 | 0,67 |
| **W8** | 0,14 | 0,08 | 0,08 | **0,43** | 0,61 | **0,33** | **−0,32** | **0,03** | 0,32 |
| śr. W1–W8 (t) | 0,39 (4,2) | 0,37 (3,1) | 0,18 (1,7) | **0,73 (15,3)** | **0,72 (23,0)** | **0,72 (11,8)** | 0,38 (3,4) | **0,57 (6,9)** | 0,37 (5,6) |

Percentyle (0–100) nóg koszyka w uniwersum, W4–W7: LONG mom 6M 84–91, beta 80–92, zmienność 74–84; SHORT mom 6M 10–22, beta 28–33. W W8: LONG mom 6M 74, beta **42**, zmienność **30**; SHORT beta 44. **Model 3.0 w W1–W7 to w praktyce „długie momentum 6–12M i wysoka beta vs niskie momentum i niska beta”; w W8 — po jednym złym tygodniu — zmienił się w coś innego (niska zmienność, neutralna beta).** 20 czynników fundamentalnych nie wnosi do rankingu nic, co dałoby się odróżnić od tych dwóch współrzędnych, a ich wkład na resztach ma znak ujemny (IC reszt −0,12, t −1,5; `mp_dodatek_out.md` §3).

### 2.4 IC modelu vs IC czynników (`mp_dodatek_out.md` §1)

Korelacja Pearsona tygodniowego IC modelu (7 pkt.) z tygodniowym IC: bety 0,93, mom 12M−1M 0,95, mom 6M 0,90, zmienności 0,90, ^SOX−^NDX 0,90, ^NDX 0,71. Przy n = 7 to ilustracja, nie test — ale razem z §2.3 mówi to samo: wynik tygodnia zależy od tego, czy w danym tygodniu wysoka beta/półprzewodniki biją ^NDX, a nie od tego, które nazwy wybrano.

### 2.5 Moc testu (`mp_dodatek_out.md` §4)

| czynnik | sd IC | tygodni dla t = 2 przy IC 0,02 | 0,03 | 0,05 | 0,10 |
|---|---|---|---|---|---|
| mom 6M | 0,26 | 693 | 308 | 111 | 28 |
| mom 12M−1M | 0,28 | 772 | 343 | 124 | 31 |
| zmienność 20d | 0,31 | 960 | 427 | 154 | 39 |
| beta | 0,38 | 1455 | 647 | 233 | 59 |
| Model 3.0 (sd 0,51, n = 7) | 0,51 | — | — | 419 | 105 |

---

## 3. Które czynniki mogą działać na 5 sesjach w tym uniwersum, a które są szumem

**Fakty (z danych):**
- Jedyne czynniki z konsekwentnie dodatnim znakiem (4 z 5 lat, 55–58 % okien): **momentum 6M i 12M−1M** (IC +0,02/+0,03, Q5−Q1 +0,5/+0,6 p.p./tydz., t 1,2–2,0). To zgadza się z backtestem portfelowym innego agenta (`bt_momentum.md`: a_6M +1,11 p.p./tydz. brutto, t 2,1; +0,84 netto, t 1,6). Efekt jest **słaby, zależny od reżimu** (ujemny w tygodniach spadkowych, ujemny w 2023) i obciążony survivorship bias — nie uzasadnia koszyka 5/5 przy gross 240 %.
- **Zmienność/beta** mają najwyższy IC, ale są czystym zakładem na kierunek ^NDX — na horyzoncie 5 sesji to timing, nie selekcja. Koszyk, który z nich korzysta (jak Model 3.0 w W1–W7), ma sd tygodnia 6–10 p.p. i kill switch w zasięgu jednego złego tygodnia.
- **Szum na 5 sesjach:** momentum 1T/1M/3M, odwrócenie 1T (IC 0,00, t 0,25 — w tym uniwersum tygodniowe odwrócenie nie istnieje, co zgadza się z `bt_odwrocenie.md`), odległość od szczytu 52-tyg. (ujemna), odległość od MA200 poza składnikiem wspólnym z mom 6M.

**Hipotezy (nie da się przetestować tymi danymi):**
- Czynniki fundamentalne (wzrost EPS/FCF, marże, ROIC, bilans, wycena) i rewizje: brak serii historycznej w repo, więc nic nie policzyłem. Argument pośredni: w rankingach W1–W8 te czynniki nie zmieniają kolejności względem samego momentum (§2.3), a na resztach po czynnikach model ma IC ≤ 0. Literatura (nieweryfikowana tu) lokuje efekt rewizji i wyceny na horyzontach 1–12 miesięcy; w 5 sesjach ich sygnał jest o rząd mniejszy niż sd zwrotu (6 p.p.). Traktuję je jako **nieudowodnione i prawdopodobnie nieistotne na tym horyzoncie**, nie jako „obalone”.
- „Typ ekspozycji AI” [0]–[4], „fala wąskich gardeł”, „odbiorca vs płatnik capexu”: to taksonomie sektorowe. W danych działają jako proxy bety do ^SOX−^NDX (ładunek spreadu 1,1–2,1 wg `dekompozycja-wynikow.md`). Na 5 sesjach to **ekspozycja czynnikowa, nie prognoza**.

---

## 4. Sekcja B2 rutyny tygodniowej: mierzalność 20 czynników i koszt uznaniowości

Źródło: `rutyny/tygodniowa.md` wiersz 49 (B2) i 48 (B1: lista imienna (c), veto-flagi, typ ekspozycji AI), kolumny TV w `data/tv-kolumny.json`. Wagi po przełączeniu wyceny na 14 sumują się do 104 („resztę przeskaluj proporcjonalnie”). Klasyfikacja moja, oparta na tym, czy czynnik ma zdefiniowaną liczbę, źródło dla całego uniwersum i próg — odróżniam „mierzalne dla ~100 spółek w każdym biegu” od „mierzalne, ale rutyna dostaje dane dla ≤ 8–20 spółek na bieg” (`get-financial-history` ≤ 8, `get-forecasts` ≤ 20; dla reszty „brak danych = 50 z obniżonym confidence” — czyli de facto uznanie):

| # | czynnik (waga) | status | źródło w rutynie | uwaga |
|---|---|---|---|---|
| 1 | rewizje prognoz i luka oczekiwań (13) | **częściowo** | get-forecasts ≤ 20 spółek; „luka oczekiwań” — tekst | poziom konsensusu ≠ rewizja; zmiany dopiero od drugiego snapshotu; elita B3 — tekstowo |
| 2 | wzrost EPS/FCF (10) | częściowo | kolumny YoYTTM w snapshocie (całe uniwersum), FCF tylko z financial-history (≤ 8) | EPS r/r mierzalne; FCF nie |
| 3 | wycena początkowa (14) | **mierzalne** | P/E ttm, P/FCF, EV/EBITDA, P/S w snapshocie | ale „REŻIMOWO 14 vs 6” — decyzja uznaniowa o wadze |
| 4 | ekspozycja na deficytową infrastrukturę AI (9) | **uznaniowe** | lista imienna B1(c) | taksonomia; proxy ^SOX |
| 5 | marże i dźwignia operacyjna (8) | częściowo | financial-history ≤ 8 | reszta uniwersum: 50/uznanie |
| 6 | cykl podaż–popyt i pricing power (8) | **uznaniowe** | prasa/TrendForce | brak liczby i progu |
| 7 | momentum relatywne „oczyszczone” (7) | **mierzalne** | Perf.6M/Perf.Y − indeks, percentyle | „oczyszczone” (z rewizji) — niezdefiniowane |
| 8 | ROIC / jakość zysku / konwersja FCF (6) | częściowo | financial-history ≤ 8 | |
| 9 | wrażliwość na realne stopy (5) | mierzalne w zasadzie, **niezaimplementowane** | brak (można liczyć betę do US10Y/TIPS z cen) | dziś uznanie |
| 10 | odbiorca vs płatnik capexu (5) | **uznaniowe** | taksonomia | |
| 11 | monetyzacja R&D / cykl produktowy (4) | **uznaniowe** | | |
| 12 | buybacki vs rozwodnienie (3) | **mierzalne** | buyback_yield | |
| 13 | strukturalny popyt cyber/observability (3) | **uznaniowe** | lista imienna | |
| 14 | bilans (2) | częściowo | brak kolumny długu w snapshocie | |
| 15 | koncentracja / próg pobicia NDX (2) | **mierzalne** | market_cap_basic | |
| 16 | geopolityka / export controls (1) | uznaniowe | | |
| 17 | pasywne przepływy / zdarzenia indeksowe (1) | uznaniowe (daty mierzalne) | | |
| 18 | inflacja / FX (1) | uznaniowe | | |
| 19 | regulacje / polityka przemysłowa (1) | uznaniowe | | |
| 20 | M&A / integracja (1) | uznaniowe | | |

Bilans wag: **mierzalne dla całego uniwersum w każdym biegu: 26/104 = 25 %** (wycena 14, momentum 7, buybacki 3, koncentracja 2); **częściowo mierzalne (dane dla części spółek, reszta „50”): 44/104 = 42 %** (rewizje 13, EPS/FCF 10, marże 8, ROIC 6, stopy 5, bilans 2); **uznaniowe/taksonomiczne: 34/104 = 33 %**. Na to nakładają się trzy kolejne warstwy uznania poza 20 czynnikami: veto-flagi (−1 kwintyl), kara event-risk 0–10 pkt, nakładka elity B3, oraz reguły spoza rutyny (W8: „reguła W4”, „filtr siły relatywnej”, „sito D2”, „veto krypto-beta”, „nadpisanie rutyny °” — 13 z 30 wierszy).

**Koszt uznaniowości — co widać w liczbach (`mp_spojnosc_out.md`):**

| para | nazw wspólnych (z 30) | Spearman Wyniku dla wspólnych | śr. |Δ Wyniku| | max |Δ| | corr(Δ Wyniku, zwrot rel. kursu D0→D0) |
|---|---|---|---|---|---|
| W1→W2 | 27 | 0,96 | 1,7 | 12 | +0,53 |
| W2→W3 | 15 | 0,86 | 6,2 | 13 | −0,12 |
| W3→W4 | 23 | 0,88 | 2,9 | 10 | +0,65 |
| W4→W5 | 23 | 0,85 | 4,0 | 9 | −0,22 |
| W5→W6 | 25 | 0,86 | 2,5 | 10 | +0,32 |
| W6→W7 | 20 | 0,86 | 2,8 | 9 | +0,83 |
| W7→W8 | 9 | 0,75 | 5,5 | 14 | +0,83 |

1. **Ranking jest sztywny tam, gdzie powinien być zmienny, i zmienny tam, gdzie powinien być sztywny.** Dla nazw obecnych w dwóch kolejnych tabelach Wynik prawie się nie rusza (ρ 0,85–0,96) — a to, co się rusza, idzie za kursem (corr Δ Wyniku z zwrotem relatywnym +0,53…+0,83 w 5 z 7 par). Czynniki „fundamentalne” (33 % wag uznaniowych + 42 % częściowych) zachowują się jak stała per spółka; zmienną częścią Wyniku jest wbudowane momentum. Stąd 15 spółek obecnych w ≥ 6 z 8 tabel (MU, NVDA, AMD, LITE, TER, APP, TSLA, INTU, CMCSA, PEP, SBUX…) i 69 unikalnych nazw na 240 wierszy.
2. **Rotacja tabel jest skokowa, nie ciągła:** W2→W3 i W7→W8 wymieniono 15 i 21 z 30 nazw przy ρ dla pozostałych 0,86/0,75 — to nie przeliczenie czynników, lecz zmiana zbioru kandydatów z B1 (ok. 20+20 z ~100, bez zapisanego kryterium progu).
3. **Koszyk nie jest funkcją Wyniku.** W 10 z 16 stron W2–W8 koszyk odbiega od TOP5/BOTTOM5: W5 i W6 SHORT po 2 nadpisania, W8 LONG 3 (GILD, QCOM, ADP za SNDK, NVDA, STX) i SHORT 4 (DASH, ALNY, APP, FER za MSTR, CRWV, TSLA, RKLB). Rozliczenie `history` mierzy więc nie Model 3.0, lecz Model 3.0 + zmienny zestaw reguł — co uniemożliwia przypisanie wyniku czemukolwiek.
4. **Model zmienia tożsamość po jednym tygodniu** (§2.3, wiersz W8): korelacja Wyniku z betą 0,53–0,73 → 0,03, ze zmiennością +0,35…+0,67 → −0,32, format Wyniku z liczb całkowitych na dziesiętne (dane_b1 = tv). To właśnie „pętla uczenia po n = 1” opisana w `PROPOZYCJA-2026-10-12-model-3.1.md` §3 T6 — tu widoczna w samym scoringu, nie tylko w regułach. Konsekwencja statystyczna: serii W1–W7 i W8+ nie wolno łączyć; licznik dowodu zaczyna się od zera.
5. Czego **nie** potwierdzam z PROPOZYCJI 3.1: zdanie „selekcja fundamentalna — zamrozić, nie naprawiać” zakłada, że w Wyniku jest coś fundamentalnego do zamrożenia; §2.3 pokazuje, że Wynik W1–W7 był w ~3/4 wyjaśniony przez momentum 6–12M i betę, więc „zamrożenie Modelu 3.0” = zamrożenie zakładu na betę półprzewodników. Zgadzam się natomiast z jej diagnozą T6/T7 i z tym, że żadna reguła nie powinna wejść bez testu przekrojowego — ten dokument jest takim testem dla samego Wyniku i p.

---

## 5. Zalecenia (ranga: twarda / poszlakowa / teoretyczna)

1. **Przestać publikować p jako prawdopodobieństwo** (B4: `p = 50 + 0,5·(wynik−50)`). p > 55 % trafia 44,5 % (95 %: 37–52 %) — deklaracja 55–62 % jest falsyfikowana przez własne dane. Zastąpić zdaniem: „Wynik nie ma potwierdzonej mocy predykcyjnej na 5 sesjach (IC −0,10 ± 0,19, n = 7)”. [twarda, in-sample]
2. **Zapisywać ranking maszynowo** — `data/ranking-<version>.json`: ticker, Wynik, 20 sub-ocen, kara event, veto, percentyle czynników ilościowych, status reguł — żeby IC każdego czynnika dało się liczyć kumulatywnie. Dziś z HTML da się wyciągnąć tylko sumę; 20 czynników jest **niesprawdzalnych z osobna**. [proces; bezkosztowe]
3. **Co sobotę liczyć i publikować w KROKU A IC Wyniku (30 nazw) oraz IC bety i momentum 6M w uniwersum za rozliczony tydzień**, obok spread_pp; w LEKCJI porównać: „IC modelu −0,65 przy IC bety −0,87 — tydzień wyjaśniony betą”. To rozdziela selekcję od zakładu czynnikowego, czego `history` nie potrafi. [proces; skrypt `mp_ic_model.py` można zaadaptować do `scripts/`]
4. **Zdefiniować Model jako to, czym jest:** część ilościowa (momentum 6M/12M−1M, wycena, buybacki, waga — 25 % wag) liczona skryptem z percentyli TV/Yahoo i nienaruszalna; część uznaniowa ograniczona do korekty ±1 kwintyla z obowiązkowym wpisem „czynnik → liczba → źródło”. Każda spółka bez danych dostaje medianę, **nie** „50 z obniżonym confidence” plus narrację. [poszlakowa: §2.3 i §4 pkt 1 — uznanie dziś nie zmienia kolejności względem momentum, a kosztuje spójność]
5. **Nie zmieniać charakteru scoringu po jednym tygodniu** (W8: beta 0,73 → 0,03). Jeżeli właściciel chce ograniczyć betę koszyka, powinno to być jawne (reguła budowy koszyka: dobór par w kwintylach bety / sektorach), a nie przeprowadzone niejawnie przez zmianę ocen. Ryzyko: backtest innego agenta pokazuje, że beta-neutralność obniża średni spread momentum (0,38 vs 1,11 p.p./tydz.) — ale obniża też wariancję, co przy kill switchu ≈ 1,7 % pod kapitałem jest ważniejsze. [poszlakowa]
6. **Horyzont 5 sesji vs czynniki:** jedyny czynnik z dodatnim znakiem to momentum 6–12M (IC 0,02–0,03) — za słaby, by przy gross 240 % pokryć koszty (finansowanie ~0,23 p.p./tydz. wg `bt_momentum.md`) z marginesem. Jeżeli system ma „osiągać zyski”, dźwignia musi wynikać z udowodnionej przewagi, a tej nie ma; decyzja o ALLOC_PCT należy do właściciela i wykracza poza ten dokument (patrz `wykonanie-bota.md`). [teoretyczna w części dotyczącej kosztów; twarda co do braku przewagi]
7. **Reguły spoza rutyny** (W8: 13/30 wierszy) wyłącznie przez rejestr z testem przekrojowym (jak w PROPOZYCJI 3.1 pkt 3) — bo dziś rozliczenie mierzy „Model + reguły tygodnia”, czyli nic. [proces]

## 6. Czego nie da się stwierdzić (otwarte)

- Czy czynniki fundamentalne/rewizje mają jakąkolwiek moc na 5 sesjach w tym uniwersum: brak danych historycznych w repo (snapshoty TV dopiero od W8). Da się to zacząć mierzyć tylko po wdrożeniu pkt 2.
- Czy ujemny IC Wyniku (−0,10) to pech 7 tygodni, czy systematyczna cecha (np. „kupowanie rozciągniętych liderów” — Wynik ~ beta 0,57) — n = 7, permutacja 0,92 mówi tylko „brak dowodu mocy”, nie „dowód szkody”.
- Survivorship bias próby 2022–2026 (dzisiejszy skład): zawyża IC momentum/bety o nieznaną wielkość; właściwy test wymaga historycznych składów NDX-100.
- Wrażliwość na definicję okna: W3 IC −0,03 (4 sesje) vs −0,59 (5 sesji). Rozliczanie tygodni o 2–11 sesjach pod jedną etykietą (jak `history`) zwiększa szum.
- Czy W8 (ładunki czynnikowe inne niż W1–W7) jest nowym modelem czy jednorazowym odchyleniem — rozstrzygnie się dopiero, gdy ranking będzie zapisywany maszynowo.
