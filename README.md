# ndx100-bot

Automat koszykowy long/short na uniwersum Nasdaq-100, prowadzony na
rachunku DEMO Capital.com. Sygnały i raporty żyją w tym repozytorium,
egzekucję robi usługa na Renderze (`app.py`, endpoint `/run`).

- **`signals.json`** — stan systemu: koszyki, status, reakcje dzienne,
  pozycje taktyczne, faktyczne ceny wejścia (`fills`), szczyt kapitału.
- **`app.py`** — synchronizacja portfela z sygnałami, bramka wyzwalaczy,
  kontrola kapitału, stopy, kill switch.
- **`scripts/kursy.py`** — kursy zamknięcia i wyliczenie reżimu rynkowego.
- **`scripts/test_app.py`** — testy logiki decyzyjnej (bez sieci).
- **`reports/`** — raporty dzienne, tygodniowe i rozliczenia okresów.
- **`INSTRUKCJA.md`** — co zmieniono, jak skonfigurować Render, poprawiony
  prompt rutyny dziennej.
- **`CLAUDE.md`** — zasady dla rutyn Claude, m.in. kontrola rachunku przez
  endpoint tylko do odczytu `/status`.
- **`rutyny/`** — źródło prawdy dla treści zadań „Puls NDX100" i „Raport
  NDX100"; `rutyny/tradingview.md` — zasady konektora TradingView MCP.
- **`data/`** — konfiguracja i log konektora TradingView (`tv-config.json`,
  `tv-symbole.json`, `tv-kolumny.json`, `tv-log.jsonl`, snapshoty
  `tv-screen-<version>.json`); bez liczb z rachunku.
- **`scripts/waliduj_signals.py`** — bramka przed commitem `signals.json`
  (obce klucze, pola bota, zmiany poza rutyną); **`scripts/tv_porownaj.py`**
  — porównanie kursów TradingView vs Yahoo vs FMP.
- **`scripts/ranking.py`** — (proces v2 od 2026-W9) deterministyczny ranking
  momentum i konstrukcja koszyka 5 par branżowych z budżetem czynnikowym;
  **`scripts/koszyki_cienie.py`** — rozliczenie koszyków cieni
  (`data/koszyki-cienie.jsonl`); **`scripts/test_ranking.py`** — testy obu.
- **`rutyny/reguly.md`** — rejestr reguł (obowiązujące / kandydaci / wyjątki /
  uchylone); **`rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md`** i
  **`rutyny/PROPOZYCJA-2026-10-18-proces-v2.md`** — analiza i decyzje procesu
  v2; **`analiza/2026-10-18/`** — skrypty i notatki dowodowe.

## Szybki start

```bash
pip install -r requirements.txt
python3 scripts/test_app.py     # musi przejść 151/151
python3 scripts/test_ranking.py # 23/23, bez sieci
python3 scripts/kursy.py        # kursy + sekcja REŻIM
```

Materiał badawczo-edukacyjny. Nie jest poradą inwestycyjną.
