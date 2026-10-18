# Weryfikacja twierdzenia C1 — momentum 6M relatywne (skip 5) TOP5/BOTTOM5 w NDX-100

Recenzent: sceptyczny agent ilościowy, 18.10.2026. Zadanie: OBALIĆ C1 na danych.

**C1:** „Momentum 6M relatywne (skip 5 sesji) TOP5/BOTTOM5 w NDX-100 ma dodatnią, ale marginalną przewagę: ~+1,0 p.p./tydz. brutto (t≈2,0–2,1), +0,7–0,85 netto (t≈1,5–1,6), niestabilną (2022–2023 ≈0, cała alfa 2024–2026) i zawyżoną przez survivorship bias; realistyczne oczekiwanie ex ante +0,4…+0,8 p.p./tydz. netto przy σ 6–7,5 p.p."

## Werdykt: POTWIERDZONE Z ZASTRZEŻENIEM

Kierunek i charakter („dodatnia, marginalna, niestabilna, zawyżona przez survivorship") bronią się po korekcie survivorship na uniwersum point-in-time (PIT). **Nie bronią się liczby:** po korekcie przewaga przestaje być odróżnialna od zera (t 1,55 brutto / 0,95 netto; bootstrap 95% CI brutto −0,12…+1,61, netto −0,39…+1,34), dolna granica „ex ante +0,4…+0,8 netto" jest zawyżona (siatka wariantów na PIT: netto +0,09…+0,54), a wzorzec czasowy „2022–2023 ≈ 0, alfa 2024–2026" jest po części artefaktem składu (na PIT: 2022 +0,82, 2024 +0,12). Struktura nóg odwraca się: survivorship zawyżał nogę LONG (+1,32 → +0,30) i zaniżał SHORT (−0,31 → +0,41).

## Dane i narzędzia

- `dane/closes_5y.csv` — 1255 sesji 2021-10-18…2026-10-16, 103 kandydaci (skład dzisiejszy), Yahoo.
- **Nowe:** `dane/dropped_closes.csv` — 28 spółek USUNIĘTYCH z NDX-100 w okresie próby (ALGN BIDU BIIB CDW CHTR CSGP DLTR DOCU EBAY ENPH GFS ILMN JD LCID LULU MDB MTCH NTES OKTA ON SIRI SMCI SWKS TEAM TTD VRSK VRSN ZM), zamknięcia dzienne z TradingView `get-ohlcv` (odczyt), parser `analiza/parse_tv_dropped.py`. Niedostępne (delisting / symbol nieznany w TV): WBA, AZN, ANSS, SPLK, SGEN, ATVI (ATVI zwrócone, ale pominięte — 501 sesji do X.2023). Kontrola jakości: AAPL TV vs Yahoo — 1255 wspólnych sesji, mediana różnicy 0,000%, max |różnica| 0,019%, 0 sesji > 0,1% → źródła zgodne.
- Skrypty: `analiza/weryfikacja_C1.py` (harness identyczny z `bt_odwrocenie.py`/`bt_momentum.py`: okna D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego, sygnał z cen ≤ D0, uniwersum = pełna historia skip+126 sesji + cena na D0 i D5, noga = r_i − r_NDX, spread = śr. LONG + śr. SHORT, gross 2; koszty 0,10% × nominał nogi za zmienioną nazwę + 6%/rok × gross), `analiza/weryfikacja_C1_pit_robust.py` (wrażliwość PIT). Wyjścia: `weryfikacja_C1_out.md`, `weryfikacja_C1_wyniki.json`, `weryfikacja_C1_serie.csv`, `weryfikacja_C1_pit_robust.md/.json`.
- Daty członkostwa (point-in-time) zweryfikowane komunikatami Nasdaq (wyszukiwarka, 18.10.2026): rekonstytucje 19.12.2022 (out: VRSN SWKS SPLK BIDU MTCH DOCU NTES; in: CSGP RIVN WBD GFS BKR FANG), 18.12.2023 (in: CDW CCEP DASH MDB ROP SPLK TTWO; out: ALGN EBAY ENPH JD LCID ZM SGEN), 23.12.2024 (in: PLTR MSTR AXON; out: ILMN SMCI MRNA), 22.12.2025 (in: ALNY FER INSM MPWR STX WDC; out: BIIB CDW GFS LULU ON TTD), zmiany kwartalne 22.06.2026 (in: ALAB CRWV NBIS RKLB TER; out: CHTR CTSH INSM VRSK ZS); zamiany: ENPH za OKTA 21.11.2022, ARM za SIRI 24.06.2024, SMCI za WBA 22.07.2024, APP za DLTR 18.11.2024, SHOP za MDB 19.05.2025, TRI za ANSS 28.07.2025, WMT za AZN 20.01.2026, SNDK za TEAM 20.04.2026, LITE za CSGP 18.05.2026, MRNA za WBD 9.10.2026. Niezweryfikowane (małej wagi, oznaczone „?" w skrypcie): CEG, GEHC, LIN, HONA, SPCX, TER przed 2026, ON przed XII.2025, WDAY (przyjęty jako członek przez cały okres).
  Źródła: [Nasdaq 2025](https://www.nasdaq.com/press-release/annual-changes-nasdaq-100-indexr-2025-12-13), [Nasdaq 2024](https://www.nasdaq.com/press-release/annual-changes-nasdaq-100-indexr-2024-12-13), [Nasdaq 2023 (TipRanks)](https://www.tipranks.com/news/the-fly/nasdaq-announces-annual-changes-to-nasdaq-100-index), [2022 (StreetInsider)](https://www.streetinsider.com/Press+Releases/Annual+Changes+to+the+Nasdaq-100+Index/20954729.html), [VI.2026](https://ir.nasdaq.com/node/110541), [SNDK](https://finviz.com/news/352721/lumentum-holdings-inc-to-join-the-nasdaq-100-index-beginning-may-18-2026) / [SNDK IR](https://ir.nasdaq.com/node/110296/pdf), [LITE](https://finviz.com/news/352721/lumentum-holdings-inc-to-join-the-nasdaq-100-index-beginning-may-18-2026), [TRI](https://www.nasdaq.com/articles/thomson-reuters-replace-ansys-nasdaq-100-index), [APP](https://www.stocktitan.net/news/NDAQ/app-lovin-corporation-to-join-the-nasdaq-100-index-beginning-ni3mncagme3i.html), [ARM/SIRI](https://www.tipranks.com/news/the-fly/arm-to-join-nasdaq-100-index-replacing-sirius-xm), [SMCI/WBA](https://www.barchart.com/story/news/27392905/super-micro-computers-stock-is-being-added-to-nasdaq-100-index), [SHOP/MDB](https://ir.nasdaq.com/node/108996), [WMT/AZN](https://www.crowdfundinsider.com/?p=257287), [MRNA/WBD](https://www.quiverquant.com/news/Nasdaq+Announces+Moderna+to+Join+Nasdaq-100+Index,+Replacing+Warner+Bros.+Discovery).

## 0. Reprodukcja twierdzenia (uniwersum dzisiejsze, jak w fazie 2)

| wariant | n | brutto | σ | t | hit | netto | t netto | noga L | noga S | maxDD | najgorsze |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6M skip 5, 5/5, pt→pt | 233 | **1,01** | 7,42 | **2,09** | 58% | **0,74** | **1,53** | 1,32 | −0,31 | 50,6 | −25,9 |

Zgodne z `ref_mom6` (0,96/t 2,02 — inna wersja listy) i `mom6/none` (1,01/t 2,09) z fazy 2. Lata brutto: 2022 −0,06, 2023 −0,13, 2024 +1,70, 2025 +1,33, 2026 +2,14. Koszty: rotacja 0,040 pp (2,0 nogi/tydz.) + finansowanie 0,230 pp. Beta spreadu do ^NDX 0,22 (r 0,09); VIX>20: +2,37 (t 2,60, n 73), VIX≤20: +0,40 (t 0,70, n 160).

## Testy

### (a) Usunięcie spółek krótkiej historii / dodanych po 2023 — i dlaczego to za mało

| wariant (skip 5, 5/5) | brutto | t | netto | t netto | L | S |
|---|---|---|---|---|---|---|
| baza | 1,01 | 2,09 | 0,74 | 1,53 | 1,32 | −0,31 |
| bez krótkiej historii z danych (ALAB ARM CEG CRWV GEHC HONA NBIS SNDK SPCX WBD) | 1,04 | 2,20 | 0,77 | 1,63 | 1,20 | −0,16 |
| bez listy z podpowiedzi (18 nazw) | **0,31** | 0,76 | **0,04** | 0,10 | 0,60 | −0,29 |
| bez listy szerokiej (31) | −0,09 | −0,26 | −0,37 | −1,03 | 0,16 | −0,26 |
| quasi-PIT tylko dołączenia (bez spółek usuniętych) | 0,14 | 0,33 | −0,14 | −0,33 | 0,31 | −0,18 |

Samo wycinanie „zwycięzców dodanych po 2023" **kasuje wynik** (0,31 brutto, 0,04 netto), ale jest to nad-korekta: te spółki od daty dołączenia były legalnymi członkami, a jednocześnie w uniwersum brakuje przegranych, których indeks się pozbył — oni byliby naturalnymi shortami. Dlatego decydujący jest test (g), symetryczny.

Koncentracja (baza): suma spreadu 236 pp; APP 67, SNDK 61, PLTR 40, LITE 34, WDC 34, MSTR 29 pp. Bez 5 największych dawców: 0,08 brutto / −0,19 netto; usunięcie 5 LOSOWYCH nazw (200 prób): 0,66…1,13 (min 0,38). Test ex post, ale pokazuje, że alfa na uniwersum dzisiejszym siedzi w nazwach, których w większości tygodni NIE dało się handlować jako członków NDX-100 (APP dołączył 18.11.2024, PLTR/MSTR 23.12.2024, WDC 22.12.2025, SNDK 20.04.2026, LITE 18.05.2026).

### (g) Uniwersum point-in-time (dzisiejsze + 28 usuniętych, daty dołączeń i usunięć) — test główny

| wariant (skip 5, 5/5) | n | brutto | σ | t | hit | netto | t netto | L | S | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|
| baza (skład dzisiejszy) | 233 | 1,01 | 7,42 | 2,09 | 58% | 0,74 | 1,53 | 1,32 | −0,31 | 50,6 |
| dzisiejsze + usunięte, wszystkie zawsze (bez PIT) | 233 | 1,72 | 7,85 | 3,35 | 61% | 1,46 | 2,83 | 1,45 | 0,27 | 48,7 |
| **PIT: dołączenia + usunięcia** | 233 | **0,71** | 6,99 | **1,55** | 55% | **0,44** | **0,95** | 0,30 | 0,41 | 44,9 |
| PIT tylko usunięcia (dzisiejsze nazwy od początku) | 233 | 1,68 | 7,88 | 3,25 | | 1,41 | 2,73 | 1,42 | 0,25 | |
| PIT tylko dołączenia (usunięte zostają do końca) | 233 | 0,64 | 6,94 | 1,42 | | 0,37 | 0,82 | 0,26 | 0,38 | |

- Wariant „wszystkie zawsze" (1,72, t 3,35) to look-ahead w drugą stronę: shortuje LCID/ZM/ENPH/DOCU po usunięciu z indeksu, gdy spadały dalej — nie do handlu w systemie NDX-100. Jedynym uczciwym wariantem jest PIT.
- PIT: nogi SHORT ze spółek usuniętych = 622 z 1165 (53%), LONG = 86. Średnie uniwersum 94,7 spółek.
- PIT lata brutto: 2022 +0,82, 2023 −0,20, 2024 +0,12, 2025 +0,78, 2026 +2,42 → „2022–2023 ≈ 0, cała alfa 2024–2026" nie trzyma się: 2022 dodatni, 2024 ≈ 0; alfa to 2025–2026 (2026: 41 okien).
- Najwięksi dawcy PIT (165 pp razem): MU 27, WDC 22, NVDA 20, STX 20, MSTR 20, PLTR 18, LCID 17 (58 shortów), TEAM 14 (54 shorty), LRCX 13, SNDK 12; 5 największych = 66% sumy. Bez nich: 0,37 brutto / 0,09 netto (t 0,84 / 0,22).

### (c) Bootstrap blokowy (stacjonarny, 10 000 prób)

| seria | średnia | 95% CI | SE | p jednostr. (μ≤0) |
|---|---|---|---|---|
| baza brutto, blok ~4 / ~8 tyg. | 1,01 | 0,07…2,00 / 0,08…2,02 | 0,50 | 0,022 / 0,024 |
| baza netto, blok ~4 / ~8 | 0,74 | −0,20…1,73 / −0,19…1,75 | 0,50 | 0,072 / 0,073 |
| bez listy 18 brutto / netto, blok ~6 | 0,31 / 0,04 | −0,60…1,40 / −0,88…1,12 | 0,51 | 0,261 / 0,464 |
| **PIT brutto / netto, blok ~6** | 0,71 / 0,44 | **−0,12…1,61 / −0,39…1,34** | | **0,057 / 0,159** |

Na uniwersum PIT ani brutto, ani netto nie odrzuca H0 na 5%; netto nie odrzuca nawet na 15%.

### (d) Podokresy

| wariant | 2022-04…2024-06 (n 114) | 2024-07…2026-10 (n 119) |
|---|---|---|
| baza brutto / t / netto | 0,09 / 0,18 / −0,18 | 1,90 / 2,36 / 1,63 |
| bez listy 18 | −0,46 / −1,24 / −0,73 | 1,05 / 1,45 / 0,78 |
| **PIT** | **0,20 / 0,38 / −0,07** (L −0,01, S 0,22) | **1,19 / 1,61 / 0,92** (L 0,60, S 0,60) |

Welch t różnicy podokresów (baza): 1,88 (różnica 1,81 pp/tydz.). Przez 27 miesięcy strategia netto ≈ 0 także po korekcie; cała przewaga to ostatnie 2 lata i w PIT nie jest istotna (t 1,61).

### (b) Kotwica dnia tygodnia (sygnał i wejście tego samego dnia)

| kotwica | baza brutto / t / netto | PIT brutto / t / netto |
|---|---|---|
| pon (n 207) | 1,11 / 1,90 / 0,80 | 0,84 / 1,53 / 0,54 |
| wt | 1,07 / 1,99 / 0,80 | 0,83 / 1,70 / 0,56 |
| śr | 0,82 / 1,56 / 0,55 | 0,66 / 1,37 / 0,39 |
| czw | 0,83 / 1,68 / 0,56 | 0,68 / 1,43 / 0,41 |
| pt (ostatnia sesja tyg.) | 1,01 / 2,09 / 0,74 | 0,71 / 1,55 / 0,44 |

Znak stabilny po kotwicach (baza 0,82…1,11; PIT 0,66…0,84), ale t > 2 wyłącznie dla piątku na uniwersum dzisiejszym; na PIT żadna kotwica nie przebija t 1,7. Piątkowy wynik nie jest przypadkiem dnia, lecz najlepszą z 5 skorelowanych prób.

### (e) Wrażliwość skip × nogi (brutto / t / netto)

Uniwersum dzisiejsze:

| skip | 4/4 | 5/5 | 7/7 |
|---|---|---|---|
| 0 | 1,16 / 2,14 / 0,88 | 1,01 / 2,03 / 0,73 | 0,90 / 1,99 / 0,63 |
| 5 | 1,29 / 2,47 / 1,02 | 1,01 / 2,09 / 0,74 | 0,71 / 1,62 / 0,44 |
| 21 | 1,05 / 2,10 / 0,78 | 1,02 / 2,19 / 0,75 | 0,66 / 1,56 / 0,40 |

Uniwersum PIT:

| skip | 4/4 | 5/5 | 7/7 |
|---|---|---|---|
| 0 | 0,52 / 1,06 / 0,25 | 0,55 / 1,19 / 0,28 | 0,36 / 0,87 / 0,09 |
| 5 | 0,82 / 1,68 / 0,54 | 0,71 / 1,55 / 0,44 | 0,54 / 1,34 / 0,27 |
| 21 | 0,57 / 1,17 / 0,30 | 0,57 / 1,26 / 0,30 | 0,43 / 1,05 / 0,16 |

Siatka 9 wariantów na PIT: brutto 0,36…0,82, t 0,87…1,68, netto 0,09…0,54; skip 5 jest najlepszą z trzech wartości skip w każdej kolumnie → wariant z twierdzenia stoi na szczycie siatki (selekcja). Mniej nóg = wyższa średnia i σ (4/4: σ 7,97 na bazie), więcej nóg = dyfuzja.

### Wrażliwość PIT na daty członkostwa (±90 dni)

| przesunięcie | brutto | t | netto |
|---|---|---|---|
| join −90, leave −90 | 0,75 | 1,65 | 0,48 |
| join −90, leave +90 | 0,86 | 1,73 | 0,59 |
| join +90, leave −90 | 0,40 | 0,96 | 0,12 |
| join +90, leave +90 | 0,55 | 1,20 | 0,28 |

Przedział 0,40…0,86 brutto / 0,12…0,59 netto; w żadnym t ≥ 2. Przed weryfikacją dat (SNDK przyjęty na XII.2025 zamiast IV.2026) wynik PIT był 0,64/0,37 — korekta dat działa w obie strony o ±0,1 pp.

## Najsilniejszy kontrargument wobec C1

Po jedynej uczciwej korekcie survivorship (uniwersum point-in-time z 28 spółkami usuniętymi i zweryfikowanymi datami członkostwa) przewaga spada do +0,71 pp brutto (t 1,55) i **+0,44 pp netto (t 0,95)**, bootstrap blokowy daje 95% CI netto **−0,39…+1,34** (p jednostr. 0,16) — statystycznie nieodróżnialna od zera; w 2022-04…2024-06 netto −0,07; 66% skumulowanego P&L pochodzi z 5 nazw (bez nich netto +0,09); wariant „6M skip 5, 5/5, piątek" jest szczytem siatki 9×5 skorelowanych prób (t na PIT 0,87…1,70), więc t≈2 na uniwersum dzisiejszym to w połowie selekcja, w połowie skład ex post. Dolna granica „ex ante +0,4 netto" leży powyżej mediany siatki PIT (0,28–0,30).

## Zrewidowane twierdzenie

Momentum 6M relatywne (skip 5) TOP5/BOTTOM5 w NDX-100 miało w 2022-04…2026-10 na uniwersum point-in-time przewagę **+0,7 pp/tydz. brutto (t 1,55), +0,44 netto (t 0,95), σ 7,0 pp**, nieodróżnialną od zera (95% CI netto −0,4…+1,3; p 0,16); siatka skip/nogi: brutto +0,36…+0,82, netto +0,09…+0,54; podokresy: 2022-04…2024-06 netto −0,07, 2024-07…2026-10 +0,92 (t 1,61); 66% P&L z 5 nazw. Na składzie dzisiejszym liczby C1 (1,01/t 2,09; 0,74/t 1,53) reprodukują się co do setnych, ale są zawyżone w nodze LONG (+1,32 vs +0,30 PIT) i zaniżone w SHORT (−0,31 vs +0,41 PIT). Realistyczne oczekiwanie ex ante: **+0,1…+0,5 pp/tydz. netto przy σ 6,5–7,5 pp, z zerem wewnątrz przedziału ufności** (nie +0,4…+0,8).

## Implikacja dla projektu

1. Momentum 6M nie uzasadnia gross 240% ani sizingu z oczekiwaniem +0,7 netto: przy +0,1…+0,5 netto i σ 7 pp tygodniowy Sharpe 0,01–0,07 (roczny ~0,1–0,5), a kill switch 0,75× szczytu pozostaje realnym zagrożeniem (faza 2: 37% okien 12-tyg. przy 24%/nogę). Jeśli czynnik zostaje, to przy ALLOC ≤ 12%/nogę i jako jeden z czynników (tie-breaker), nie jako teza koszyka.
2. Noga SHORT ma na PIT wartość (+0,41 pp) wyłącznie dzięki shortowaniu nazw spadających KU wyjściu z indeksu (LCID 58 okien, TEAM 54, CHTR 44, LULU 44, ENPH 38, TTD 38) — czyli system musi mieć w uniwersum aktualnych członków z dołu rankingu kapitalizacji; koszyk W8 (short AXON DASH ALNY APP FER) nie jest tym profilem.
3. Nie używać t≈2 z uniwersum dzisiejszego jako argumentu w raportach/rutynach; do testów przyszłych wariantów stosować uniwersum PIT (`dane/dropped_closes.csv` + tabele dat w `weryfikacja_C1.py`) i próg t > 2 PO kosztach na PIT, prerejestrowany; pozostałe nazwy niedostępne (WBA, AZN, ANSS, SPLK, SGEN, ATVI) obniżają wynik shortów o nieznaną, prawdopodobnie dodatnią wielkość (wszystkie spadały przed usunięciem) — więc PIT jest tu raczej dolnym niż górnym oszacowaniem korekty.
4. Ocena żywej skuteczności: przy σ 7 pp i oczekiwaniu +0,3 netto potrzeba ~540 tygodni na t = 2; W1–W7 (7 tygodni) nie mówią nic o czynniku — mówią o koncentracji SOX (faza 2).

## Ograniczenia

- Daty członkostwa dla CEG, GEHC, LIN, HONA, SPCX, TER (przed 2026), ON (przed XII.2025), WDAY — niezweryfikowane; wrażliwość ±90 dni oszacowana wyżej (0,40…0,86 brutto).
- 6 usuniętych spółek bez danych (delisting): WBA, AZN, ANSS, SPLK, SGEN, ATVI; CTSH, ZS, INSM, RIVN, BKR niedodane (CTSH/ZS/INSM usunięte VI.2026 — 16 okien; RIVN/BKR: BKR jest w danych, RIVN brak — niezweryfikowane).
- TV i Yahoo: zamknięcia split-adjusted bez dywidend w obu źródłach (zgodność na AAPL 0,019% max) — dywidendy pomijane konsekwentnie, drobne zaniżenie nóg long na spółkach dywidendowych.
- Harness nie modeluje stopów 10%, bramki Pulsu ani poślizgu — jak w fazie 2 (symulacja wykonania pokazała, że stopy obniżają t do 1,05–1,33 na uniwersum dzisiejszym).
