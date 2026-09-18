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

## Szybki start

```bash
pip install -r requirements.txt
python3 scripts/test_app.py     # musi przejść 46/46
python3 scripts/kursy.py        # kursy + sekcja REŻIM
```

Materiał badawczo-edukacyjny. Nie jest poradą inwestycyjną.
