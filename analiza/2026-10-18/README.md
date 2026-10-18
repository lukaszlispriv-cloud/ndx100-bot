# Analiza 18.10.2026 — materiały źródłowe

Dokument główny: `rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md`; proces: `rutyny/PROPOZYCJA-2026-10-18-proces-v2.md`.

Zawartość (kopie z sesji wieloagentowej; ścieżki w tekstach wskazują na katalog roboczy sesji — podmień na ten katalog):

* `00-faza1-wnioski.txt`, `00-faza2-backtesty.txt` — ustrukturyzowane wnioski agentów (faza 1: 6 analiz, faza 2: 5 testów wstecznych).
* Faza 1: `dekompozycja-wynikow.md` (+ `dekompozycja.py`, `lib_dekomp.py`, `panel_momentum.py`, `rozklad_historyczny.py`, `w8_ekspozycja.py`), `wykonanie-bota.md` (+ `wyk_*.py`), `audyt-regul.md` (+ `audyt_regul.py`), `moc-predykcyjna-modelu.md` (+ `mp_*.py`), `perspektywa-quant.md` (+ `pq_quant.py`), `ryzyko-i-sizing.md` (+ `ryzyko_sizing.py`, `ryzyko_extra.py`).
* Faza 2: `bt_momentum`, `bt_odwrocenie`, `bt_neutralnosc`, `bt_rezim-i-zaklad-czynnikowy`, `bt_symulacja-wykonania` (`.md` + `.py`).
* Faza 3: `00-faza3-weryfikacja-i-projekty.txt` (ustrukturyzowane wnioski), `weryfikacja-C1…C9.md` (sceptycy; + `weryfikacja_C*.py`, `*_out.md`), `projekt-A-mechaniczny.md`, `projekt-B-przezywalnosc.md`, `projekt-C-konstrukcja.md` (+ `projektA_*`, `projekt_B_sim.py`, `projektC_*`), `sedzia-1…3.md` (panel; + `sedzia2_soft_loty.py`, `sedzia3_*`). Konsensus panelu: konstrukcja E + stałe ALLOC 0,08 — patrz `rutyny/ANALIZA-…` §6.
* Dane: zamknięcia dzienne 2021-10-18…2026-10-16 odtwarza `pobierz_closes_5y.py` (Yahoo; survivorship bias — skład dzisiejszy). Serie tygodniowe i JSON-y wyników nie są w repo (duże) — generują je skrypty.

Żaden plik nie zawiera liczb z rachunku (kapitał, pozycje) — wyłącznie %, p.p. i stosunki do `START_EQUITY` (stała domyślna `app.py`) lub do szczytu; dwa wpisy z fazy 3 zostały z tego powodu zanonimizowane przy kopiowaniu (18.10.2026).

UWAGA do składów „E dla W8” w notatkach fazy 3 (projekt C, sędziowie, `projektA_ranking_W8.md`, `ranking_test_W8.md`): liczone bez veta EVENT i przed poprawkami skryptu — są HISTORYCZNE. Obowiązuje `data/ranking-2026-W8.json` (veto EVENT ze snapshotu TV, konstrukcja FAKTYCZNY = koszyk W8 z signals.json): E = CRWD/APP, AMGN/ALNY, FTNT/PAYX, AMD/AVGO, DXCM/GEHC.
