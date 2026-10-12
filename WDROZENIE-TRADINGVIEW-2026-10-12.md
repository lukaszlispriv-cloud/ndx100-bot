# Wdrożenie TradingView MCP w czterech rutynach — plan po inwentaryzacji na żywo

Stan na 12.10.2026, 13:47–14:20 UTC. Dokument dla właściciela systemu.
Punkt wyjścia: „TradingView MCP Server w czterech rutynach — propozycja
wdrożenia po przeglądzie sceptyków" (dalej: PROPOZYCJA; numeracja pozycji
A-1…A-3, N-P1…N-P5, N-R1…N-R4, W-P1…W-P2, W-R1…W-R3 jak tam).
Ten plan NIE powtarza PROPOZYCJI — mówi, co inwentaryzacja na żywo zmieniła,
co z tego wynika dla każdej rutyny, w jakiej kolejności to wdrażamy i jakie
decyzje właściciel musi podjąć przed startem.

Liczby z rachunku: brak (zgodnie z CLAUDE.md). Kursy w tym dokumencie to
dane rynkowe użyte wyłącznie do testów zgodności źródeł.

---

## 0. Streszczenie

1. **Konektor TradingView JEST widoczny w tej sesji** (w sesji, z której
   pochodzi PROPOZYCJA, nie był). 35 narzędzi pod nazwami
   `mcp__TradingView__mcp-tv-<nazwa>` (27) i `mcp__TradingView__mcp-watchlist-<nazwa>` (8).
   Przeprowadziłem inwentaryzację na żywo: **32 wywołania wyłącznie do
   odczytu**, bez watchlist i alertów, poza oknem biegów (po 13:45 UTC),
   zero błędów 429 — także przy dwóch równoległych wywołaniach narzędzi
   screenera.
2. **Kluczowe założenia PROPOZYCJI potwierdzone**: `symbolset
   SYML:NASDAQ;NDX` działa (101 nazw = `epics` minus KHC i WBD),
   `run_screener(market='poland', symbolset=['SYML:GPW;WIG20'])` zwraca
   20/20 spółek zgodnych z mapą `epics` wig20-bot, `get_symbol_data_batch`
   rozwiązuje symbole GPW bez `missing`, kolumny `premarket_*`, `Perf.*`,
   `SMA50/200`, `update_mode`, `earnings_release_next_date` istnieją,
   serie `get_ohlcv` dla GPW:LPP są identyczne z `data/kursy-cache.json`
   w 11/11 sesjach, w tym przez ex-date 8.10 (brak korekty dywidendowej —
   backfill cache dopuszczalny), `NASDAQ:NDX` zamknięcie 9.10 = `d0.ndx`
   co do grosza, MA50/MA200 z TV vs `kursy.py` różnią się o 0,09–0,17%
   (różnica wyjaśniona niedokończoną świecą 12.10).
3. **Założenia obalone (zmieniają plan)**: (a) `get_ohlcv` MA `date_from`
   / `date_to` i stronicowanie — backfill może prosić o dokładne okno;
   (b) w katalogu kolumn screenera **nie ma** `recommendation_*`,
   `price_target_*` ani forward P/E — konsensus tylko przez
   `get_forecasts` (1 wywołanie / spółka), metoda równoległa forward P/E
   z N-R4 jest martwa; (c) `get_earnings_calendar` i
   `get_dividends_calendar(symbols=[...])` **nie obsługują GPW**, ale daty
   wyników GPW są w kolumnie screenera `earnings_release_next_date`, a
   dywidendy GPW działają w trybie `market='poland'` + okno dat (LPP 500 zł
   ex 8.10, PZU 4,80 zł ex 16.09 — zgodne z korektami ręcznymi z W5 i W9);
   (d) `get_news` dla GPW (lang=pl) zwraca 0 nagłówków — gałąź newsowa WIG20
   odpada; (e) kalendarz makro PL działa (GUS, NBP, RPP 4.11 14:00 UTC,
   święta GPW), ale prawie wszystko ma `importance = -1` — W-P2/W-R2 muszą
   wołać `min_importance=-1` i filtrować lokalnie; (f) `get_forecasts` dla
   `GPW:PKO` zwraca cele cenowe ok. 30 zł przy kursie 115,68 zł — konsensus
   GPW z TV wymaga kontroli skali, cele = b.d. do wyjaśnienia; (g) w
   odpowiedzi `get_earnings_calendar` JEST pora dnia (`release_next_at`,
   `release_next_time_flag`) i flaga `next_date_confirmed`.
4. Kolejność bez zmian wobec PROPOZYCJI: decyzje właściciela → grant
   konektora w 4 rutynach → skrypty i walidator (A-3) → blok KROK 0 (A-1)
   → pliki `data/tv-*.json` z faktami poniżej → prompty (plik, commit,
   wklejenie) → 2 tygodnie fazy cienia → kryteria → faza 2.
5. Rekomendacje do sześciu pytań PROPOZYCJI: sekcja 4. Najważniejsza:
   **bez decyzji licencyjnej TV zostaje w fazie 1** (kontrola, rezerwa,
   kalendarze, dokumenty) — i faza 1 sama w sobie zamyka realne dziury:
   brak rezerwy serii rocznej ^NDX, brak świecy D0 dla WIG20 od 29.09,
   KALENDARZ_NIEPOTWIERDZONY i DYWIDENDA_KOREKTA bez źródła maszynowego.
6. Dwa repozytoria = dwa zestawy commitów. Ten plan leży w ndx100-bot;
   zmiany w wig20-bot (sekcja 6.3, 6.4, 7) wymagają osobnej sesji z prawem
   zapisu do `lukaszlispriv-cloud/wig20-bot` (w tej sesji repo było
   dostępne tylko do odczytu).

---

## 1. Co inwentaryzacja zmienia w PROPOZYCJI

| # | Założenie w PROPOZYCJI | Fakt z 12.10 (narzędzie) | Skutek dla planu |
|---|---|---|---|
| 1 | Konektor niewidoczny; nazwy „prawdopodobne" | Widoczny; `mcp__TradingView__mcp-tv-*` / `mcp-watchlist-*`; ToolSearch `select:<pełna nazwa>` ładuje schemat | A-1 pkt (1): szukaj najpierw `select:` po pełnych nazwach z `rutyny/tradingview.md`, słowne „tradingview" jako zapas |
| 2 | `get_ohlcv` bez okna dat i stronicowania | Ma `date_from`, `date_to`, `has_more`, `next_date_to`, `format=columns`, `count` do 5000 | `tv_merge.py` prosi o dokładne okno brakujących sesji; brak potrzeby „count=40 i filtr" |
| 3 | `symbolset SYML:NASDAQ;NDX` niezweryfikowany | Działa, `totalCount=101`, GOOG+GOOGL; odpowiedź zawiera też kolumny domyślne (EMA50/200, High.3M, `days_to_earnings`, `earnings_release_next_date`…) — ok. 60 kB | N-R2 snapshot GO; N-R3 skład indeksu GO; wynik ZAWSZE do pliku i przez skrypt |
| 4 | GPW przez MCP niezweryfikowane | Batch 5 symboli (w tym GPW:PKO, GPW:WIG20) bez `missing`; screener `market='poland'` + `SYML:GPW;WIG20` = 20/20; `update_mode=delayed_streaming_900` | W-P1/W-R1 GO (bramka „20/20" spełniona) |
| 5 | Korekta serii o dywidendy niezweryfikowana | GPW:LPP 25.09–09.10: 11/11 zamknięć identycznych z cache, w tym 7.10→8.10 (24 800 → 24 400) przez ex-date 500 zł | Bramka ex-date OK; backfill cache dopuszczalny po walidacji D0 |
| 6 | Symbol VIX nierozstrzygnięty | `CBOE:VIX` zamknięcie 9.10 = 14,84 (Yahoo 14,84); `TVC:VIX` 14,85 | Mapa: `CBOE:VIX`; N-P2 VIX z TV GO |
| 7 | Konsensus (`recommendation_mark`, `price_target_average`) jako kolumny screenera | Brak w katalogu (`get_screener_columns` search „recommend"/„target" = no match; grupa `earnings_estimates` ma tylko prognozy EPS/przychodów) | N-R2 REWIZJE i W-R3 tylko przez `get_forecasts` per spółka (≤20 wywołań, sekwencyjnie); zestaw B1 bez tych kolumn |
| 8 | Forward P/E ze składników (kolumna `price_earnings_fwd`) | Brak kolumny (grupa `valuation`: `price_earnings_ttm`, `price_book_fq`, `enterprise_value_ebitda_ttm`, `price_free_cash_flow_ttm`…; „forward" tylko `dividends_yield`) | N-R4 pkt (3) metoda równoległa SKREŚLONA; flaga `fpe_z_tv` bezprzedmiotowa; WSJ zostaje, brak = b.d. |
| 9 | `get_earnings_calendar` dla GPW | Brak danych dla GPW:PKO, GPW:LPP; dla NASDAQ:MU jest `release_next_at` (z godziną), `release_next_time_flag`, `next_date_confirmed=false` | W-P2(b)/W-R2(2): daty wyników GPW z kolumny `earnings_release_next_date` (jest dla 20/20 w screenerze), nie z kalendarza; NDX: pora dnia JEST — do flagi EVENT |
| 10 | `get_dividends_calendar(symbols)` dla GPW | Puste; tryb `market='poland'` + okno dat działa (42 wiersze, w tym LPP i PZU; także zagraniczne spółki notowane na GPW) | W-P2(c)/W-R2(1): jedno wywołanie z oknem, filtr lokalny po mapie symboli |
| 11 | Kalendarz makro PL niezweryfikowany; `min_importance=0/1` | Działa (GUS 07:30 UTC, NBP, RPP 04.11 14:00 UTC, święta 1.11 i 11.11 jako „Holidays"); importance PL = −1 dla prawie wszystkiego, 0 dla CPI flash/stopy; US: 1 dla CPI/PPI/sprzedaży | W-P2(a)/W-R2(3): `min_importance=-1`, filtr lokalny po `source`/`indicator`; święta GPW z tego samego wywołania |
| 12 | Newsy GPW | `get_news('GPW:PGE', lang='pl')` = 0 | Gałąź newsowa WIG20 odpada (także z „zachowanego elementu" W-P3) |
| 13 | `get_forecasts` dla GPW „prawdopodobne" | GPW:PKO: 15 analityków, rozkład 6/8/1 — ale `price_targets.average` 30,08 przy kursie 115,68 (upside −74%) i `eps_ttm` 2,30 — skala niezgodna z kursem | W-R3: dla GPW tylko `total_analysts` i rozkład; cele i EPS = b.d. do wyjaśnienia przez właściciela (test skali: cel/kurs w przedziale 0,5–2,0) |
| 14 | `premarket_time`, `postmarket_*` | Katalog: `premarket_change`, `_change_abs`, `_close`, `_gap`, `_volume`; brak `premarket_time` i `postmarket_*` | N-P5: znacznik czasu = godzina odczytu; post-market b.d. |
| 15 | Opóźnienie „15–20 min" | `update_mode=delayed_streaming_900` (900 s) na NASDAQ i GPW w trakcie sesji; `get_ohlcv` ostrzega, że ostatnia świeca się formuje | Reguła mapowania świec: sekcja 2.4 |
| 16 | 429 przy równoległych wywołaniach scannera | 0 × 429 w 32 wywołaniach, w tym tury z 2 narzędziami scannera naraz | W rutynach nadal sekwencyjnie (zasada bez zmian), ale budżety z PROPOZYCJI są realistyczne |
| 17 | Newsy USA: pokrycie dostawców nieznane | NASDAQ:MU: GuruFocus, Seeking Alpha (pełny tekst), Dow Jones Newswires (`paywall=true`, `permission=headline`) | N-P4(a): nagłówek DJ bez treści = tylko nagłówek, b.d. |
| 18 | Dokumenty | NASDAQ:MU: 10-K (pdf + summary), transkrypt, slajdy — dostawca Quartr, `views[].id` jako URN | N-R4(2), N-P4(b) GO; `get_document_view` nietestowany (długość treści nieznana) |

---

## 2. Fakty z inwentaryzacji (do przepisania do plików `data/tv-*.json`)

### 2.1 Narzędzia

Pełne nazwy w tej sesji (prefiks konektora `mcp__TradingView__`):

- Odczyt, dozwolone w rutynach (allowlista): `mcp-tv-get-ohlcv`,
  `mcp-tv-get-symbol-data`, `mcp-tv-get-symbol-data-batch`,
  `mcp-tv-run-screener`, `mcp-tv-get-screener-columns`,
  `mcp-tv-search-symbols`, `mcp-tv-get-technicals-rating`,
  `mcp-tv-get-news`, `mcp-tv-get-news-story`, `mcp-tv-get-documents`,
  `mcp-tv-get-document-view`, `mcp-tv-get-financials`,
  `mcp-tv-get-financial-history`, `mcp-tv-get-forecasts`,
  `mcp-tv-get-earnings-calendar`, `mcp-tv-get-economic-calendar`,
  `mcp-tv-get-dividends-calendar`, `mcp-tv-get-economic-data`,
  `mcp-tv-get-economic-symbols`.
- Odczyt, NIEUŻYWANE w rutynach: `mcp-tv-get-alerts`, `mcp-tv-list-alerts`,
  `mcp-tv-get-alerts-log`, `mcp-watchlist-list-watchlists`,
  `mcp-watchlist-get-watchlist`.
- ZAKAZ (zapis w koncie TV): `mcp-tv-create-alert`, `mcp-tv-update-alert`,
  `mcp-tv-delete-alert`, `mcp-tv-stop-alerts`, `mcp-tv-restart-alerts`,
  `mcp-watchlist-create-watchlist`, `mcp-watchlist-delete-watchlist`,
  `mcp-watchlist-add-to-watchlist`, `mcp-watchlist-remove-from-watchlist`,
  `mcp-watchlist-update-watchlist` oraz `mcp-watchlist-get-active-watchlist`
  (skutek uboczny: tworzy watchlistę).

Ładowanie schematów: `ToolSearch` z zapytaniem
`select:mcp__TradingView__mcp-tv-get-ohlcv,mcp__TradingView__mcp-tv-get-symbol-data-batch`
(pełne nazwy, po przecinku) — sprawdzone. Zapytanie słowne („tradingview
ohlcv") też działa, ale zwraca obok `get-ohlcv` również `create-alert`
(narzędzie zapisu) — dlatego w rutynach wyłącznie `select:` z allowlisty,
słowne tylko jako test obecności konektora. Rutyna loguje pełną nazwę
pierwszego załadowanego narzędzia w `data/tv-log.jsonl`.

### 2.2 Mapa symboli (`data/tv-symbole.json`)

NDX100 (ndx100-bot): każdy klucz `epics` → `NASDAQ:<ticker>` (101/103
rozwiązane przez screener; KHC i WBD nie są już w indeksie — reguła
„usuniętych nie wybieraj, `epics` zostaw" bez zmian). Indeks `NASDAQ:NDX`.
VIX `CBOE:VIX`. Taktyczne spoza `epics`: rozwiązywać przez
`search_symbols('<ticker>', type_filter='stock')` i dopisywać do mapy
(giełda NYSE/NASDAQ z odpowiedzi, nigdy epic Capital.com).

WIG20 (wig20-bot), ticker systemowy → symbol TV: ALIOR `GPW:ALR`, ALLEGRO
`GPW:ALE`, BUDIMEX `GPW:BDX`, CDPROJEKT `GPW:CDR`, DINOPL `GPW:DNP`, ERSTEPL
`GPW:EBP`, KETY `GPW:KTY`, KGHM `GPW:KGH`, KRUK `GPW:KRU`, LPP `GPW:LPP`,
MBANK `GPW:MBK`, MODIVO `GPW:MDV`, PEKAO `GPW:PEO`, PEPCO `GPW:PCO`, PGE
`GPW:PGE`, PKNORLEN `GPW:PKN`, PKOBP `GPW:PKO`, PZU `GPW:PZU`, TAURONPE
`GPW:TPE`, ZABKA `GPW:ZAB`; indeks `GPW:WIG20`. (Wszystkie 20 potwierdzone
screenerem i batchem.)

NIEROZSTRZYGNIĘTE (dopełnienie inwentaryzacji, ~10 wywołań, krok 3 planu):
`NQ1!` (futures), SOX, US10Y, miedź/srebro/Brent (futures ciągłe), USDPLN,
EURPLN, `GPW:WIG_BANKI` / `WIG_ENERG` / `WIG_PALIWA`, seria FW20, tickery
`ECONOMICS:PL*` (`get_economic_symbols(country='PL')`). Do czasu
rozstrzygnięcia: b.d.

### 2.3 Kolumny (`data/tv-kolumny.json`)

Potwierdzone (zwrócone z wartościami lub w katalogu):

- cena/zmiana: `name`, `exchange`, `close`, `change`, `change_abs`,
  `volume`, `market_cap_basic`, `update_mode`
- pre-market (stock/etf): `premarket_change`, `premarket_change_abs`,
  `premarket_close`, `premarket_gap`, `premarket_volume`
- momentum: `Perf.W`, `Perf.1M`, `Perf.3M`, `Perf.6M`, `Perf.YTD`,
  `Perf.Y` (grupa `performance`); działają też dla indeksu NASDAQ:NDX
- średnie i zakres: `SMA50`, `SMA200`, `EMA50`, `EMA200`,
  `price_52_week_high`, `High.3M`, `Low.3M`, `pct_from_high_3m`,
  `pct_from_low_3m`, `price_vs_ema50_pct`, `price_vs_ema200_pct`
- wolumen: `average_volume_10d_calc`, `vol_ratio_10d`
- wyniki: `earnings_release_next_date`, `days_to_earnings`
- klasyfikacja: `sector`, `industry` (np. Electronic Technology /
  Semiconductors; Finance / Major Banks)
- wycena (grupa `valuation`): `price_earnings_ttm`, `price_book_fq`,
  `enterprise_value_ebitda_ttm`, `price_free_cash_flow_ttm`,
  `price_sales_current`, `earnings_yield`, `buyback_yield`
- dywidenda: `dividends_yield` (forward)
- prognozy (grupa `earnings_estimates`): `earnings_per_share_forecast_next_fq`
  (`_fh`, `_fy`), `revenue_forecast_next_fq` (`_fh`, `_fy`)

BRAK w katalogu (ustalone): `recommendation_*`, `price_target_*`,
`Recommend.All` jako kolumna screenera (rating techniczny tylko przez
`get_technicals_rating`), forward P/E, `premarket_time`, `postmarket_*`,
short interest, `eps_surprise_*`, `earnings_per_share_diluted_yoy_growth_ttm`
i `total_revenue_yoy_growth_fq` (nie szukane w tej turze — do dopełnienia,
grupy `income_statement`/`profitability`).

Grupy katalogu: balance_sheet, bonds, cash_flow, crypto, dividends,
earnings_estimates, etf, identity, income_statement, misc, ownership_shares,
performance, price, profitability, technicals, valuation, volume_liquidity.
`search` to podciąg nazwy/opisu — „recommend" nie trafia, bo takich kolumn
nie ma.

### 2.4 Semantyka świec `get_ohlcv` (reguła mapowania — do `rutyny/tradingview.md`)

- `t` = otwarcie sesji regularnej w UTC: NASDAQ 13:30 UTC, CBOE (VIX) 13:15
  UTC, GPW 07:00 UTC. **Data sesji = data UTC z `t`.**
- Ostatnia świeca to bieżąca, niedokończona sesja, gdy data(`t`) = dziś i
  zegar nie minął 16:10 Nowego Jorku (NASDAQ/CBOE) lub 17:10 Warszawy (GPW)
  — odrzucić (wolumen `NASDAQ:NDX` o 13:49 UTC: 52 mln vs ~1 mld dla sesji
  zakończonych). To ta sama granica, którą stosuje `kursy.py`.
- Tylko sesja regularna, korekta tylko o splity (ostrzeżenie w
  odpowiedzi; test LPP potwierdza brak korekty dywidendowej).
- `SMA50`/`SMA200` z `get_symbol_data` ZAWIERAJĄ bieżącą świecę — tylko
  orientacyjnie; MA do reżimu liczyć z `get_ohlcv` po odrzuceniu ostatniej
  świecy, dokładnie 200/50 zamknięć (różnica 12.10: MA200 27 651,7 TV
  z niedokończoną świecą vs 27 625,8 `kursy.py`; MA50 29 824,4 vs 29 774,7).
- `close` w batchu w trakcie sesji = kurs opóźniony o 15 min, nie
  zamknięcie (MU 13:49 UTC: 985,2 przy zamknięciu 9.10 = 1 029,0).

### 2.5 Kalendarze, newsy, dokumenty, konsensus — pokrycie

| Narzędzie | USA | GPW/PL | Uwagi |
|---|---|---|---|
| `get_economic_calendar` | TAK, `importance` 0/1, data z godziną UTC | TAK (GUS, NBP, RPP), `importance` −1/0 | zawsze `min_importance=-1` dla PL; święta jako `indicator=Holidays` |
| `get_earnings_calendar` | TAK: `release_next_at` z godziną, `release_next_time_flag`, `next_date_confirmed`, konsensus EPS/przychodów | NIE | GPW: kolumna `earnings_release_next_date` ze screenera (20/20) |
| `get_dividends_calendar` | TAK (symbols): PEP 1,48 ex 4.09 | tryb `symbols` NIE; tryb `market='poland'` + okno TAK (LPP 500 ex 8.10, PZU 4,80 ex 16.09) | filtr lokalny po mapie (w wynikach także NVDA, MSFT notowane na GPW) |
| `get_news` | TAK (GuruFocus, Seeking Alpha, DJ z paywall) | NIE (PGE, pl: 0) | |
| `get_documents` | TAK (Quartr: 10-K, transkrypt, slajdy; `views[].id` URN) | nietestowane | |
| `get_forecasts` | TAK (MU: 55 analityków, cel 1 599, EPS) | DANE PODEJRZANE (PKO: cele ~30 przy kursie 115,68) | GPW: tylko liczba analityków i rozkład |
| `get_technicals_rating` | nietestowane | nietestowane | |

### 2.6 Koszt i limity

32 wywołania w 33 minuty, maks. 8 w jednej turze (w tym 2 scannera
równolegle), 0 × 429, 0 × 401. Największa odpowiedź: screener NDX 101
wierszy z kolumnami domyślnymi (ok. 60 kB) — w rutynie zawsze do pliku i
skryptem, nigdy do kontekstu.

---

## 3. GO / NO-GO per pozycja PROPOZYCJI

| Pozycja | Werdykt | Uzasadnienie / zmiana |
|---|---|---|
| A-1 blok KONEKTOR | GO | tekst bez zmian poza pkt (1) (ToolSearch `select:`) i pkt (5) (symbole z mapy — mapa gotowa) |
| A-2 inwentaryzacja | WYKONANA w 80% | pozostało: symbole z 2.2 „nierozstrzygnięte", `get_document_view` (długość), `get_technicals_rating`, kolumny r/r, `update_mode` poza sesją, pomiar czasu 3 batchy |
| A-3 walidator + guard + skrypty | GO, PIERWSZY | niezależne od TV; `_sanity` w `app.py` nie odrzuca obcych kluczy (potwierdzone w kodzie, l. 349–) |
| N-P1 kursy NDX | GO (F1) | `update_mode` do batcha TAK; FMP EOD-light dla 10 nóg — osobny test (nie TV) |
| N-P2 reżim | GO (F1) | symbole `NASDAQ:NDX`, `CBOE:VIX` rozstrzygnięte; zgodność MA ≤0,2% potwierdzona |
| N-P3 blokada sektorowa (cień) | GO (F1) | `symbolset SYML:SP;SPX` nietestowany — pierwszy bieg z fallbackiem `filters={'index':'S&P 500'}`; taksonomia potwierdzona |
| N-P4 newsy/dokumenty/kalendarze | GO (krok 8) | DJ = tylko nagłówek; pora dnia raportu JEST (`release_next_at`) — do flagi EVENT |
| N-P5 pre-market | GO warunkowo (krok 8) | kolumny są; bez `premarket_time`; `NQ1!` po dopełnieniu |
| N-R1 kontrola d0/B0 | GO (F1) | bez zmian |
| N-R2 snapshot B1/benchmark/kontrola rang | GO z ZMIANĄ | zestaw B1 bez kolumn konsensusu; REWIZJE przez `get_forecasts` ≤20/sobotę (10 rozliczanych + 10 nowych), sekwencyjnie; F2 nadal za licencją |
| N-R3 skład/zdarzenia/dywidendy | GO (F1) | skład: 101 = `epics` − {KHC, WBD}; daty wyników z `earnings_release_next_date` (0 wywołań) + `get_earnings_calendar` dla pory dnia |
| N-R4 panel fundamentów | GO bez pkt (3) | forward P/E ze składników SKREŚLONY (brak kolumny); reszta po sezonie wyników |
| W-P1 kursy WIG20 + backfill | GO (F1) | bramki: 20/20 TAK, ex-date TAK, D0 ≤0,5% — do potwierdzenia w pierwszym biegu; `date_from/date_to` upraszcza backfill |
| W-P2 kalendarze WIG20 | GO ze ZMIANĄ | makro: `min_importance=-1`; wyniki: kolumna screenera; dywidendy: `market='poland'` + okno; newsy GPW: NIE |
| W-R1 sobota WIG20 | GO (F1) | `market='poland'` + `symbolset` działa; sanity rel5/rel20 z `Perf.W` orientacyjnie |
| W-R2 dywidendy/kalendarze/sektorówka | GO ze ZMIANĄ | jak W-P2; surowce/FX po dopełnieniu mapy |
| W-R3 wycena/konsensus | GO CZĘŚCIOWO | wycena (`price_earnings_ttm`, `price_book_fq`, `enterprise_value_ebitda_ttm`, `dividends_yield`) z screenera TAK; konsensus GPW: tylko liczba analityków i rozkład, cele b.d. (skala) |
| Gałąź newsowa WIG20 | NO-GO | 0 nagłówków GPW |
| Flaga `fpe_z_tv` | BEZPRZEDMIOTOWA | brak kolumny forward P/E |

---

## 4. Decyzje właściciela przed startem (odpowiedzi na pytania §11 PROPOZYCJI)

1. **Licencja (§3 regulaminu TV).** Rekomendacja: zapytać support TV o
   użycie danych w automacie, który składa zlecenia na podstawie
   częściowo zasilanych nimi sygnałów; termin 31.10.2026. Do odpowiedzi:
   tylko faza 1 (kontrola, rezerwa, kalendarze, dokumenty, snapshot bez
   użycia w scoringu). Faza 1 nie narusza „display-only" bardziej niż
   dzisiejsze ręczne odczyty z serwisów.
2. **Plan i grant.** Plan Essential+ jest potwierdzony pośrednio: narzędzia
   działają w tej sesji. Do zrobienia przez właściciela: w formularzu
   każdej z 4 rutyn (claude.ai/code/routines) włączyć konektor TradingView
   (lekcja FMP: bez grantu sesja go nie widzi); usunąć Google Drive z
   grantów rutyn. Rekomendacja: zrobić to dopiero po kroku 2 (A-3 i A-1 w
   repo), żeby pierwszy bieg z konektorem już miał blok KROK 0.
3. **Godzina Pulsu WIG20.** Rekomendacja: zostawić 8:15 Warszawy. Przed
   otwarciem `close` z batcha = zamknięcie wczorajsze (1 wywołanie na 21
   symboli), a świeca D0 i tak idzie z `get_ohlcv`. Po 10:01 batch jest
   bezużyteczny. Osobno do sprawdzenia w cron-job.org: podwójny bieg
   12.10 i bieg bota NDX w sobotę 10.10 — to nie dotyczy TV.
4. **Metoda WIG20 przy backfillu.** Rekomendacja: v1.1 + kod
   `KURS_ZRODLO_TV` w `data_quality`. Backfill dopisuje wyłącznie brakujące
   sesje nieskorygowane (test LPP), więc nie zmienia definicji momentum,
   tylko kompletność (znika `BRAK_20S`/`METRYKI_Nk_Z_20`). Korekta ex-div w
   momentum: NIE (zostaje kod + zdanie w PROBLEMY; ewentualnie v1.2 później).
5. **NDX w fazie 2.** Rekomendacja: wariant A (`kursy.py` nr 1, TV
   kontrola i rezerwa). Yahoo działa (35 raportów bez rozjazdu D0,
   12.10: 105/105 symboli, walidacja OK), TV dodaje miejsce błędu, nie
   informację.
6. **Flagi.** Start: wszystkie `false`. Kandydatki po fazie 1:
   `rezim_surowszy` (najtańsza i najbezpieczniejsza — tylko zaostrza),
   `sektor_tv` (po ≥5 rozbieżnych werdyktach). `kryterium_event_remis`,
   `event_blokada_taktycznej`, `wstrzymanie_przy_rozjezdzie` — dopiero po
   zaobserwowanym przypadku. `fpe_z_tv` — usunąć z listy. `b1_z_tv` — tylko
   po licencji.

Zapis decyzji: sekcja „TradingView" w CLAUDE.md obu repo z datą (krok 4).

---

## 5. Harmonogram i podział pracy

| Krok | Kiedy | Kto | Co | Repo |
|---|---|---|---|---|
| 1 | 12–14.10 | właściciel | decyzje z sekcji 4; pytanie do supportu TV | — |
| 2 | 13–15.10 | sesja Claude (NDX) + sesja Claude (WIG20) | **A-3**: `scripts/waliduj_signals.py` (listy kluczy per repo), guard podwójnego biegu, `scripts/tv_porownaj.py` (z FMP EOD lub `kursy.py --json` jako drugim źródłem — działa bez TV), `scripts/tv_merge.py` (wig20); testy bez sieci w `scripts/test_app.py` (NDX) / `tests/` (WIG20). **A-1**: `rutyny/tradingview.md` (NDX), `docs/tradingview.md` (WIG20) z treścią sekcji 2 i 9; katalog `data/` w ndx100-bot; `data/tv-config.json`, `data/tv-symbole.json`, `data/tv-kolumny.json` z sekcji 7 | oba |
| 3 | 15–16.10, poza oknami 12:00–13:45 UTC i 08:00–10:30 Warszawy, nie w sobotę | sesja interaktywna | dopełnienie inwentaryzacji (sekcja 2.2 „nierozstrzygnięte", `get_document_view`, `get_technicals_rating`, kolumny r/r, `update_mode` poza sesją, czas 3 batchy, `symbolset SYML:SP;SPX`); ~10–15 wywołań; wynik do plików z kroku 2 | oba |
| 4 | 16–17.10 | sesje Claude, potem właściciel wkleja | prompty: najpierw plik, commit, dopiero wklejenie; grant konektora w 4 rutynach; CLAUDE.md obu repo (sekcja TradingView, FMP wg stanu, „rotacja 9:15" → 10:01 w wig20) | oba |
| 5 | sobota 17.10 (pierwszy bieg sobotni) → 30.10 | rutyny | **FAZA CIENIA**: NDX Puls A-1, N-P1, N-P2, N-P3; NDX sobota N-R1, N-R2 (snapshot + benchmark + kontrola rang), N-R3; WIG20 Puls W-P1, W-P2 (bez newsów); WIG20 sobota W-R1, W-R2. Żaden werdykt nie zależy od TV. Każdy bieg: wiersz w `data/tv-log.jsonl` + linia STAN ŹRÓDEŁ | oba |
| 6 | 31.10 | sesja Claude | raport cienia `reports/tv-cien-2026-10.html` w każdym repo ze skryptu nad logiem; kryteria z sekcji 8 | oba |
| 7 | od 2.11 (po decyzjach) | właściciel + sesje | **FAZA 2**: WIG20 TV nr 1 kursów (W-P1/W-R1) z `kursy.py` jako drugim torem; NDX wariant A; `rezim_surowszy` jako pierwsza flaga; `b1_z_tv` tylko po licencji | oba |
| 8 | 9–20.11 | sesje | N-P4, N-P5, N-R4, W-R3 — każda osobnym commitem i licznikiem `werdykt_zmieniony` | oba |
| 9 | ciągle | właściciel | raz w tygodniu: status konektora w claude.ai, wpisy „brak/401" w logu (dwa kolejne = ponowna autoryzacja); po komunikacie TV o zmianie narzędzi — powtórka inwentaryzacji; `enabled:false` w obu configach wyłącza TV | oba |

Twarde granice czasowe bez zmian: Puls NDX kończy blok TV o 13:15 UTC
(bot 13:45 UTC); Puls WIG20 przed 10:01 Warszawy.

---

## 6. Co dokładnie zmienia się w każdej rutynie

Teksty „gotowe do wklejenia" są w PROPOZYCJI (§4). Poniżej wyłącznie
różnice wynikające z inwentaryzacji oraz zakres F1/F2.

### 6.1 Puls NDX100 (`rutyny/dzienna.md`)

- **KROK 0 — KONEKTOR TRADINGVIEW** (A-1): tekst z PROPOZYCJI z poprawkami:
  pkt (1) „ToolSearch: `select:` po pełnych nazwach z allowlisty w
  `rutyny/tradingview.md`; słowne 'tradingview' tylko jako test obecności
  (zwraca też narzędzia zapisu — nie ładuj ich)"; pkt (5) „symbole
  z `data/tv-symbole.json` — taktyczne spoza mapy przez `search_symbols`
  i dopisanie do mapy w commicie".
- **Linia 18 ŹRÓDŁO KURSÓW** → N-P1. Dodatkowo: `update_mode` w batchu
  (potwierdzony); w trakcie sesji `close` to kurs opóźniony, nie
  zamknięcie — do tabeli wyłącznie kolumna „TV (opóźnione, HH:MM UTC)".
- **REŻIM** → N-P2 z symbolami `NASDAQ:NDX` i `CBOE:VIX`; MA z
  `get_ohlcv(count=260)` po odrzuceniu niedokończonej świecy; progi
  zgodności ≤0,5% MA / ≤0,2 pkt VIX (12.10: 0,09% / 0,17% / 0,00).
- **Blokada sektorowa** → N-P3 w cieniu; pierwszy bieg testuje
  `symbolset SYML:SP;SPX`, przy błędzie `filters={'index':'S&P 500'}`;
  wynik do pliku.
- **KROK 1** → N-P4 dopiero w kroku 8; do flagi EVENT używać
  `release_next_at` i `next_date_confirmed` (data estymowana = „niepotwierdzona").
- **Tabela** → N-P5 w kroku 8 (kolumny bez `premarket_time`).
- **KROK 4** → dopuszczenie plików `data/tv-log.jsonl`,
  `data/tv-symbole.json` w commicie; walidator i guard (A-3) PRZED commitem.
- Budżet F1: ≤20 wywołań / 8 min (3 batche + 2–3 ohlcv + 1–2 screener);
  F2: ≤40 / 10 min.

### 6.2 Raport tygodniowy NDX100 (`rutyny/tygodniowa.md`)

- **KROK 0** (A-1) jak wyżej.
- **ŹRÓDŁO KURSÓW + KROK D** → N-R1 (bez zmian; `symbolset` potwierdzony,
  więc 1 screener zamiast 3 batchy daje te same 101 zamknięć plus
  `earnings_release_next_date` — ale `close` w sobotę rano to piątkowe
  zamknięcie tylko poza sesją; potwierdzić w pierwszym biegu).
- **B1/B2** → N-R2 ze zmianą: `rutyny/tv-zestaw-b1.json` = `name`,
  `exchange`, `close`, `change`, `Perf.W`, `Perf.1M`, `Perf.3M`, `Perf.6M`,
  `Perf.YTD`, `Perf.Y`, `SMA50`, `SMA200`, `price_52_week_high`, `High.3M`,
  `market_cap_basic`, `sector`, `industry`, `earnings_release_next_date`,
  `days_to_earnings`, `average_volume_10d_calc`, `price_earnings_ttm`,
  `price_free_cash_flow_ttm`, `earnings_per_share_forecast_next_fq`,
  `revenue_forecast_next_fq` (+ kolumny r/r po dopełnieniu katalogu).
  REWIZJE: `get_forecasts` dla 10 nóg rozliczanych + 10 nowych (≤20,
  sekwencyjnie, 429 → wartości sprzed tygodnia); snapshot `data/tv-screen-<version>.json`
  commitowany PRZED scoringiem; benchmark „sort po samym momentum" z Yahoo
  od pierwszej soboty; kontrola rang TV vs Yahoo. F2 (`b1_z_tv`) tylko po
  licencji.
- **B4/A** → N-R3: skład indeksu = lista `name` ze screenera vs `epics`
  (12.10: 0 nowych, 2 usunięte — KHC, WBD); daty wyników z kolumny (0
  wywołań) + `get_earnings_calendar` dla pory dnia i konsensusu (1–2
  wywołania); dywidendy `get_dividends_calendar(symbols=20)` (USA działa).
- **B0/B0b** → N-R4 bez pkt (3); panel tylko po publikacji wyników.
- Budżet F1: ≤20 (1 screener + 1 indeks + 2 ohlcv + ≤10 forecasts + 2–3
  kalendarze); F2: ≤50 / 20 min.

### 6.3 Puls WIG20 (`docs/routine-puls-wig20-prompt.txt`, wig20-bot)

- **KROK 0** (A-1) z `docs/tradingview.md` i `data/tv-config.json` wig20.
- **ŹRÓDŁO KURSÓW** → W-P1: FMP skreślone (`FMP_PLAN_BLOKADA` przestaje być
  dopisywane); `kursy.py` ZAWSZE i RAZ; batch 21 symboli z mapy
  (`columns=['name','close','change','update_mode']`); świeca D0 z
  `get_ohlcv(symbol, date_from=D0, date_to=D0)` lub `count=3`; backfill
  `tv_merge.py --tylko-brakujace` z dokładnym oknem brakujących sesji
  (12.10: ALIOR, ERSTEPL, KETY, LPP, PZU, ZABKA mają 33 sesje przy 35 dla
  WIG20 — skrypt policzy luki). F1 (min. 10 biegów): tabele i progi
  4%/8% nadal z `kursy.py`; F2: TV → `kursy.py` jako kontrola; bankier
  wygrywa przy rozjeździe >0,5%.
- **KROK 1** → W-P2 ze zmianami: (a) `get_economic_calendar(countries='PL,US,EU',
  min_importance=-1, okno dziś…+7)` + filtr lokalny (GUS, NBP/RPP, Fed, EBC,
  BLS; święta GPW z `indicator=Holidays`); (b) daty wyników: kolumna
  `earnings_release_next_date` z batcha/screenera (0 dodatkowych wywołań),
  nie `get_earnings_calendar`; (c) dywidendy:
  `get_dividends_calendar(market='poland', date_from=D0−30 dni, date_to=+15 dni, limit=200)`
  + filtr po mapie (1 wywołanie). Zdanie o „datowanym źródle" wchodzi
  dopiero po dopisku do `docs/metoda.md` §9. Newsy GPW z TV: nie ma.
- **KROK 4** → pliki TV w commicie, walidator (klucze wig20: `_instrukcja`,
  `d0`, `epics`, `exclude`, `generated`, `history`, `last_daily`, `long`,
  `short`, `status`, `tactical`, `version`), guard.
- Budżet F1: ≤20 (1 batch + 0–3 ohlcv zwykle, do 21 po przerwie + 2
  kalendarze) / 8 min, przed 10:01 Warszawy.

### 6.4 Raport tygodniowy WIG20 (`docs/routine-raport-tygodniowy-prompt.txt`)

- **KROK 0** (A-1).
- **ŹRÓDŁO KURSÓW / B0 / A2** → W-R1: `run_screener(market='poland',
  symbolset=['SYML:GPW;WIG20'], columns=<zestaw W-R1+W-R3>, limit=30)` +
  `get_symbol_data('GPW:WIG20', columns=['close','change','Perf.W','Perf.1M'])`;
  `totalCount=20` i lista `name` = 20 dozwolonych tickerów po mapie
  (12.10: zgodne); zamknięcia piątkowe D+5 jako drugie źródło; backfill
  luk; metryki WYŁĄCZNIE `metryki.py`; sanity rel5/rel20 orientacyjnie.
- **KROK A/B2/B4** → W-R2 z parametrami jak w 6.3 (makro `-1`, dywidendy
  `market='poland'`, daty wyników z kolumny); surowce/FX/subindeksy po
  dopełnieniu mapy (krok 3), do tego czasu b.d.
- **B5/B7** → W-R3 (krok 8): wycena z tych samych kolumn screenera
  (`price_earnings_ttm`, `price_book_fq`, `enterprise_value_ebitda_ttm`,
  `dividends_yield`, `average_volume_10d_calc`) z JEDNĄ datą odczytu;
  konsensus: `get_forecasts` dla 20 spółek sekwencyjnie TYLKO
  `total_analysts` i rozkład buy/hold/sell (test skali celu: cel/kurs
  w 0,5–2,0; poza → cele b.d. i wpis w PROBLEMY; 12.10 PKO: 0,26 →
  b.d.); n<5 → „niska próba"; punktacja bez zmian do decyzji §4 metody.
- `docs/metoda.md`: §8 kody `KURS_ZRODLO_TV`, `TV_MCP_NIEDOSTEPNY`,
  `TV_DANE_ROZBIEZNE` + poprawka `KURS_ZRODLO_REZERWA` (= bankier/cache);
  §9 kalendarz TV jako datowane źródło warunkowo (data + godzina;
  organizator wygrywa); §7b/§8 decyzja o `metoda`; §4 konsensus TV ≠ PAP
  (tylko po decyzji).
- `CLAUDE.md` wig20: „Źródło kursów" bez FMP jako nr 1 (sekcja 1 FMP do
  usunięcia), „rotacja 9:15" → 10:01, sekcja TradingView.
- Budżet F1: ≤25 (1–2 screener + 0–21 backfill + 2 kalendarze) / 15 min.

---

## 7. Pliki do utworzenia (szkice)

### 7.1 `data/tv-config.json` (oba repo, osobne commity)

```json
{
  "enabled": true,
  "faza": 1,
  "wersja_konfiguracji": "2026-10-12",
  "narzedzia_prefix": "mcp__TradingView__mcp-tv-",
  "budzet": {
    "puls":   {"wywolania": 20, "czas_s": 480, "twarda_granica_utc": "13:15"},
    "sobota": {"wywolania": 20, "czas_s": 1200, "twarda_granica_utc": null}
  },
  "flagi": {
    "sektor_tv": false,
    "kryterium_event_remis": false,
    "event_blokada_taktycznej": false,
    "wstrzymanie_przy_rozjezdzie": false,
    "rezim_surowszy": false,
    "b1_z_tv": false
  },
  "tolerancje": {"kurs_pct": 0.5, "ma_pct": 0.5, "vix_pkt": 0.2, "rozjazd_adnotacja_pct": 0.1}
}
```

Dla wig20-bot: `budzet.puls` 20 / 480 s / granica `08:01` UTC (10:01
Warszawy), `budzet.sobota` 25 / 900 s; flagi `sektor_tv`,
`kryterium_event_remis`, `b1_z_tv` nie dotyczą WIG20 — pominąć.

### 7.2 `data/tv-symbole.json`

Sekcja 2.2 w formacie `{"ticker_systemowy": "EXCHANGE:TICKER"}` plus
`"_indeks": "NASDAQ:NDX"`, `"_vix": "CBOE:VIX"` (NDX) /
`"_indeks": "GPW:WIG20"` (WIG20), `"_nierozstrzygniete": [...]`,
`"_data": "2026-10-12"`. Dla NDX generowany skryptem z kluczy `epics`
(`NASDAQ:` + ticker) z wyjątkami wpisanymi ręcznie po dopełnieniu.

### 7.3 `data/tv-kolumny.json`

Sekcja 2.3 w formacie `{"nazwa": {"opis": "...", "warianty": [...],
"potwierdzono": "2026-10-12"}}` + klucze: `"premarket_dostepne": true`,
`"konsensus_w_screenerze": false`, `"forward_pe": false`,
`"short_interest_sprawdzone": true` (brak), `"documents_gpw": null`,
`"news_gpw": false` (wig20), `"earnings_gpw_kalendarz": false`,
`"earnings_gpw_kolumna": true`, `"dividends_gpw_symbols": false`,
`"dividends_gpw_market": true`, `"kalendarz_pl": true` (importance −1).

### 7.4 `rutyny/tv-zestaw-b1.json` (NDX)

Lista z 6.2 z datą zamrożenia; zmiana zestawu = edycja pliku z datą.

### 7.5 `data/tv-log.jsonl` — wiersz na bieg

```json
{"data":"2026-10-19","rutyna":"puls-ndx","narzedzia_prefix":"mcp__TradingView__mcp-tv-","stan":"OK","wywolania":14,"czas_s":210,"max_delta_pct":0.08,"rozjazdy_gt_0_5":[],"missing":[],"faza":1,"werdykt_zmieniony":"nie","depesze_agencyjne":"nie","blok_przerwany_czasem":false}
```

Bez liczb z rachunku. Ta sama treść jako linia STAN ŹRÓDEŁ w problemach raportu.

### 7.6 Skrypty (krok 2)

- `scripts/waliduj_signals.py --diff HEAD --rutyna puls|sobota` — dokładny
  zestaw kluczy top-level (NDX: `_instrukcja, d0, epics, equity_peak,
  exclude, fills, generated, history, last_daily, long, short, status,
  tactical, version, wykonanie`; WIG20: bez `equity_peak`, `fills`,
  `wykonanie`), zmienione pola wobec HEAD tylko z listy per rutyna, zakaz
  zmian w `fills`/`equity_peak`/`wykonanie`; kod wyjścia ≠ 0 = nie commituj.
- `scripts/tv_porownaj.py --tv <plik> --kursy <kursy.py --json> [--fmp]
  [--screener] --d0 signals.json` — tabela ZGODNOŚĆ, rozjazdy >0,1% /
  >0,5% z datą świecy obu źródeł, mediana `change` po `industry`, wiersz
  logu.
- `scripts/tv_merge.py --ohlcv <pliki> --cache data/kursy-cache.json --d0
  signals.json --tylko-brakujace` (wig20) — dopisuje brakujące sesje po
  walidacji D0 (0,5%) i teście ex-date, nie nadpisuje istniejących.
- Guard podwójnego biegu w promptach (A-3 pkt 3) — bez skryptu.
- Testy bez sieci: fixture z odpowiedziami z 12.10 (NDX ohlcv 5 świec,
  LPP 12 świec, batch 5 symboli) w `scripts/test_app.py` (NDX) i
  `tests/test_tv.py` (WIG20).

---

## 8. Kryteria awansu do fazy 2 i wycofania (prerejestrowane, jak §7 krok 6 PROPOZYCJI)

Awans po 10 biegach Pulsów (ok. 31.10): ≥9/10 biegów `stan=OK`; mediana
|Δ| ≤0,1% dla nóg i indeksu; zero niewyjaśnionych rozjazdów >0,5% dla nóg
(wyjaśnione = ex-date, split, niedokończona świeca, święto); blok TV w
budżecie czasu w każdym biegu; WIG20 dodatkowo: ≥8/10 biegów z kompletem
21/21 zamknięć z dwóch źródeł i zero serii odrzuconych kodem
`TV_DANE_ROZBIEZNE`.

Wycofanie do F1 (lub `enabled:false`): ≥3 biegi z 401/brak w 10; ≥2
niewyjaśnione rozjazdy >0,5% dla nóg; bieg Pulsu NDX, który nie
scommitował `signals.json` przed 13:45 UTC z powodu TV; dwa kolejne biegi z
429 na kursach koszyka.

Metryki do raportu cienia: jak §8 PROPOZYCJI (dostępność, zgodność,
odporność, jakość danych, werdykty, warianty na papierze) — liczone
skryptem nad `data/tv-log.jsonl`, bez liczb z rachunku.

---

## 9. Czego nie robić — uzupełnienia po inwentaryzacji

Wszystkie punkty §9 PROPOZYCJI obowiązują. Dodatkowo:

- Nie wołać `mcp-watchlist-get-active-watchlist` (tworzy watchlistę) ani
  żadnego narzędzia z listy ZAKAZ w 2.1 — rutyna nie dostaje pytania o zgodę.
- Nie używać `get_earnings_calendar` ani `get_dividends_calendar(symbols)`
  dla GPW — puste; daty wyników GPW z kolumny screenera, dywidendy z trybu
  `market='poland'`.
- Nie wołać kalendarza makro PL z `min_importance ≥ 0` — zniknie prawie
  wszystko (GUS i NBP mają −1).
- Nie brać celów cenowych ani EPS z `get_forecasts` dla GPW bez testu skali
  (PKO 12.10: cel 30 przy kursie 115,68); nie punktować na ich podstawie.
- Nie szukać kolumn `recommendation_*`, `price_target_*`, forward P/E,
  `premarket_time`, `postmarket_*` — nie ma ich w katalogu; nie iterować po
  wariantach nazw.
- Nie liczyć MA do reżimu z kolumn `SMA50`/`SMA200` (zawierają bieżącą
  świecę); tylko z `get_ohlcv` po odrzuceniu ostatniej świecy.
- Nie wczytywać odpowiedzi screenera (≈60 kB dla NDX) do kontekstu —
  plik + skrypt.
- Nie traktować `close` z batcha w trakcie sesji jako zamknięcia
  (opóźnienie 900 s, `update_mode=delayed_streaming_900`).
- Nie dopisywać do mapy symboli z wyników `market='poland'` spółek
  zagranicznych notowanych na GPW (NVDA, MSFT, META…) — filtrować po
  20 tickerach.
- Nie uruchamiać dopełnienia inwentaryzacji (krok 3) w oknach biegów ani
  w sobotę; nie w rutynie.

---

## 10. Otwarte ryzyka

1. **Licencja** — jedyne ryzyko, którego faza 1 nie zamyka; termin 31.10.
2. **Grant konektora w rutynach** — do pierwszego biegu rutyny nie wiadomo,
   czy ruch idzie przez Anthropic bez allowlisty środowiska (w tej sesji
   działał bez wpisu `tradingview.com` w allowliście sieci).
3. **Odnawianie OAuth** — zgłoszenia o wygasaniu po ~24 h dotyczą innych
   konektorów; log `401` i krok 9 to jedyna ochrona.
4. **Toolset w becie** — nazwy mogą się zmienić; blok KROK 0 kończy bieg
   fallbackiem, nie halucynacją.
5. **`get_forecasts` dla GPW** — dane o niezgodnej skali; nie wiadomo, czy
   dotyczy wszystkich spółek GPW (test 1 spółki).
6. **`symbolset SYML:SP;SPX`** (N-P3) i `get_document_view` (długość
   transkryptów) — nietestowane; pierwszy bieg z fallbackiem i limitem 2
   widoków.
7. **Limit dzienny bety** — nieznany; log sumuje wywołania dzienne 4 rutyn
   (szczyt: sobota, Raport WIG20 ~06:30 + Raport NDX ~07:30 UTC ≤ 45 łącznie
   w F1).
