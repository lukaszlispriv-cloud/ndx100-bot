# ndx100-bot — zasady dla sesji Claude (rutyny „Puls NDX100" i „Raport NDX100")

Repozytorium jest źródłem prawdy dla sygnałów (`signals.json`), raportów
(`reports/`) i treści rutyn (`rutyny/dzienna.md`, `rutyny/tygodniowa.md`).
Egzekucję robi usługa na Renderze (`app.py`, endpoint `/run`), odpalana przez
cron-job.org w dni robocze o **13:45 i 17:05 UTC**. Rutyny nigdy nie składają
zleceń i nie dotykają pól pisanych przez bota (`fills`, `equity_peak`,
`wykonanie`).

## Co wolno, czego nie wolno

- Puls pisze w `signals.json` tylko `status`, `exclude`, `tactical`,
  `last_daily`; raport tygodniowy — `version`, `status`, `long`, `short`,
  `d0`, `generated`, `exclude=[]`, `tactical=[]`, wpis do `history`
  (+ `epics`: wyłącznie dopisanie nowej spółki z indeksu). Nic więcej:
  bot waliduje plik przed każdym biegiem i przy złym pliku wstrzymuje handel.
- Zmiany treści rutyn: najpierw plik w `rutyny/`, potem wklejenie do zadania
  na claude.ai/code/routines (historia gita mówi, co się zmieniło).
- Testy: `python3 scripts/test_app.py` (bez sieci; wymaga `flask`, `requests`).
- Commity i dokumenty nie zawierają liczb z rachunku (kapitał, pozycje) —
  one należą do raportów HTML, nie do repo z kodem.

## Kontrola rachunku przez `/status` (od 12.10.2026 — rutyny mają dostęp)

Środowisko rutyn ma zmienną `NDX_BOT_URL` (adres bota NDX100 na Renderze,
`https://<nazwa-ndx>.onrender.com`) oraz network secret, który dokłada
nagłówek `X-Run-Token` do żądań na ten host — token NIE jest w zmiennych
sesji i nie wolno go szukać, wypisywać ani prosić o niego. Wywołuj WYŁĄCZNIE
endpoint tylko do odczytu:

```bash
curl -sS -m 120 "$NDX_BOT_URL/status"
```

- NIGDY nie wołaj `/run` (bieg bota ZE ZLECENIAMI), `/generate`, `/close_all`
  ani `/search`. `/health` nie wymaga tokena i nadaje się na test dostępu.
- Autoryzacja (`auth_ok()` w `app.py`): nagłówek `X-Run-Token` albo `?token=`
  dla zgodności wstecz; rutyny używają wyłącznie nagłówka przez sekret.
- Brak `NDX_BOT_URL` w sesji = brak dostępu: napisz to w sekcji problemów
  raportu i pomiń kontrolę (nie wymyślaj liczb). Zmienna `BOT_URL` bez
  przedrostka `NDX_` należy do bota WIG20 (`wig20-bot.onrender.com`) — nie
  używaj jej dla NDX100.
- Pierwsza odpowiedź po przerwie może trwać do minuty (Render usypia
  serwis). `{"error":"zły token"}` = sekret nie dokłada nagłówka; 403/407
  z proxy = host nie jest na liście dozwolonych — oba zgłoś w problemach.
- Gdy `NDX_BOT_URL` nie jest ustawione, właściciel ustawia w claude.ai:
  Edit environment → Environment variables `NDX_BOT_URL=https://<nazwa-ndx>.onrender.com`;
  Network secrets → Add secret: Allowed websites `<nazwa-ndx>.onrender.com`,
  Custom headers: Name `X-Run-Token`, Prefix pusty, Value = `RUN_TOKEN`
  z Rendera. Obie rutyny muszą wskazywać to środowisko (ikona chmury pod
  polem Instructions).

### Pola odpowiedzi `/status` i jak je czytać

| Pole | Znaczenie dla rutyny |
|---|---|
| `konto.kapital`, `konto.waluta` | equity rachunku (USD) — kapitał do sekcji kontroli rachunku; `konto.gotowka` to saldo bez wyceny, `konto.wycena_pozycji` otwarty wynik wszystkich pozycji, `konto.depozyt_zabezpieczajacy` zamrożony depozyt, `konto.dostepne_do_handlu` wolne środki. |
| `equity_peak` | kroczący szczyt kapitału z `signals.json`. Porównaj z plikiem — rozjazd oznacza, że bot zapisał nowy szczyt po ostatnim commicie. Próg kill switcha NIE jest po prostu `kill_level` × szczyt: bot v2 zwraca gotowe `kill_switch` (`odniesienie` = max(szczyt, podłoga `START_EQUITY`; po wznowieniu bez podłogi), `prog`, `zapas_pct`, `dd_od_szczytu_pct`, `zatrzask`, `wznowienie_oczekuje_w_najblizszym_biegu`, `restart_reczny_od_kapitalu`, `slad`) — próg i zapas bierz stamtąd. |
| `konta_wszystkie[]` | wszystkie rachunki Capital.com; `aktywne_dla_bota = true` wskazuje ten, na którym bot handluje; `blad_przelaczenia_rachunku ≠ null` = handel wstrzymany. |
| `sygnaly` | `version`, `status`, `long`, `short`, `exclude`, `tactical` — wersja sygnałów, którą bot widzi (po rotacji sobotniej jest nowsza niż pozycje na rachunku do poniedziałku 13:45 UTC). |
| `pozycje[]` | pozycje z epikami z mapy `epics` (+ hedge indeksowy): `epic`, `direction`, `size`, `upl` (otwarty wynik), `wejscie` (poziom otwarcia u brokera), `otwarta`. UWAGA: taktyczne spoza NDX-100 (własny `epic`) tu NIE są — patrz `pokrycie_koszyka.pozycje_taktyczne`. |
| `ceny_wejscia` | = `fills` z `signals.json` (ceny odniesienia tezy, pole `cena`); do zwrotów OD CENY WEJŚCIA zgodnie z KROK 1 Pulsu. `cena_brokera` to tylko bieżący poziom u brokera. Wpis przeżywa wyrównania wielkości; przy zmianie `version` resetuje się do poziomu brokera TYLKO dla spółki, która wypadła z koszyka albo zmieniła kierunek — noga kontynuowana (ten sam ticker w `long`/`short`/`tactical` w tym samym kierunku) zachowuje `cena` i `data`, a dostaje nową `wersja` (bot od 12.10.2026; wcześniej sobotni bieg po zmianie `version` kasował wszystkie odniesienia, jak 10.10.2026). |
| `kontrola_kapitalu` | `zgodne`, `roznica` wobec `tolerancja`, `pozycje_spoza_ksiazki`, `pozycje_bez_wyceny`, `suma_upl_pozycji_bota`, `wycena_z_api`. |
| `pokrycie_koszyka` | (bot od 12.10.2026) `nogi_koszyka`, `nogi_na_rachunku`, `brakujace[]`, `wykluczone_przez_puls[]`, `zredukowane_przez_puls[]` dla LONG; `short` z tą samą strukturą (tryb classic) albo `null`; `pozycje_taktyczne[]`, `pozycje_spoza_koszyka[]`, `hedge_mode`, `wersja_sygnalow`. Starszy bot nie ma tego pola — wtedy policz pokrycie sam (niżej). |
| `hedge_mode` | `classic` (short koszykowy jako SELL na akcjach — tryb w użyciu: `fills` ma wpisy `SELL`), `index` (syntetyczny short przez `HEDGE_EPIC`) albo `off` (long-only). Wynika ze zmiennej `HEDGE_EPIC` w Renderze. |
| `ustawienia` | `alloc_pct`, `tactical_alloc_pct`, `reduce_factor`, `react_reduce_pct`, `react_close_pct`, `stop_loss_pct`, `kill_level`, `margin_budget`… — stąd bierz wartości do stopki raportu zamiast zgadywać. |
| `dry_run` | `true` = bot nie składa zleceń. |

### Pokrycie koszyka (gdy liczysz sam)

Noga koszyka = ticker z `sygnaly.long` (kierunek BUY) albo `sygnaly.short`
(kierunek SELL, tylko w `hedge_mode = classic`). Epic nogi = `signals.json["epics"][ticker]`
(dla akcji USA zwykle równy tickerowi). Noga jest **na rachunku**, gdy w
`pozycje` jest wpis o tym `epic` i tym kierunku. Noga z `exclude` o
`action = CLOSE` jest **wykluczona przez protokół**, nie brakująca; noga po
`REDUCE` jest obecna z mniejszym celem (`alloc_pct × reduce_factor`).
**Pozycje spoza koszyka** = wpisy z `pozycje`, których epic nie należy do
żadnej nogi ani do `sygnaly.tactical` — między sobotnią rotacją sygnałów
a poniedziałkowym biegiem `/run` są to nazwy poprzedniego tygodnia (stan
SPRZED rotacji), później to sygnał do opisania w problemach.

### `kontrola_kapitalu.zgodne = false`

Kapitał z API nie daje się odtworzyć z książki bota: `roznica` (wycena
z API minus suma `upl` znanych pozycji) przekracza `tolerancja`
(`EQUITY_TOL` × equity), są `pozycje_spoza_ksiazki` albo `pozycje_bez_wyceny`.
W `/run` bot wtedy ogranicza wielkość pozycji do `ALLOC_PCT_SAFE` (blokuje
skalowanie). **Zastrzeżenie dla `/status`:** ten endpoint liczy kontrolę
z książki zawężonej do uniwersum `epics` (+ hedge) — inaczej niż `/run`,
który dolicza epiki taktyczne i ledger `fills`. Otwarta pozycja taktyczna
spoza NDX-100 (np. APOG, PENG) pojawia się więc w `pozycje_spoza_ksiazki`,
podnosi `roznica` i przełącza `zgodne` na `false`, choć `/run` uznaje ją za
własną. Alarmem jest dopiero: epic w `pozycje_spoza_ksiazki`, którego nie ma
ani w `sygnaly.tactical`, ani w `ceny_wejscia`; niepuste `pozycje_bez_wyceny`;
albo |`roznica`| > `tolerancja` po odjęciu `upl` pozycji taktycznych.

### Kod `EKSPOZYCJA_NIEPELNA`

Dopisz go w nagłówku sekcji kontroli rachunku raportu HTML i w wiadomości
końcowej, gdy: brakuje nogi LONG (lub SHORT w trybie classic), której nie
wykluczył protokół (`exclude`), albo `kontrola_kapitalu` jest naprawdę
niezgodna w sensie powyżej. `signals.json` NIE ma pola `data_quality`
i nic do niego nie dopisujesz — bot waliduje plik i przy obcym polu może
wstrzymać handel. Nogę, której bot nie otworzył z powodu minimalnej
transakcji (patrz `wykonanie.taktyczne` „nieotwarta — …"), opisz jako
ograniczenie wielkości rachunku, nie awarię.

### Godzina biegu `/run` a godzina rutyn

- `/run`: dni robocze 13:45 i 17:05 UTC (cron-job.org; wyrównywanie
  wielkości tylko w biegu 17:05 — `REBALANCE_HOURS=17`). Rotacja koszyka
  wykonuje się w PIERWSZYM biegu po zmianie `version`, czyli w poniedziałek
  o 13:45 UTC.
- Puls NDX100: dni robocze ok. 12:30 UTC (14:30 Warszawy, przed otwarciem
  NYSE) — widzi stan **po biegu 17:05 UTC z poprzedniego dnia**, a
  w poniedziałek stan **SPRZED rotacji** (pozycje poprzedniego tygodnia przy
  nowych `sygnaly.long/short`). Napisz w raporcie, który to przypadek;
  wskazówką jest `wersja` we wpisach `ceny_wejscia` wobec `sygnaly.version`.
- Raport tygodniowy (sobota ok. 07:30 UTC): widzi pozycje ROZLICZANEGO
  tygodnia — porównuj je z koszykiem rozliczanym, nie z nowym.
- Stan rachunku nie opuszcza raportów: kapitał i wynik w USD tylko w sekcji
  kontroli rachunku / problemów, nigdy w powiadomieniu push ani w commicie.

## TradingView MCP (od 12.10.2026 — FAZA 2; OD 18.10.2026 ZAWĘŻONE przez proces v2 — sekcja „Proces v2” niżej i `rutyny/tradingview.md` §0a; punkty o pełnym użyciu, flagach b1_z_tv/kryterium_event_remis/event_blokada_taktycznej i budżetach 40/50 są HISTORYCZNE)

Właściciel 12.10.2026 wyraził zgodę na wdrożenie wg
`WDROZENIE-TRADINGVIEW-2026-10-12.md` (plan po inwentaryzacji na żywo;
propozycja wyjściowa: `WDROZENIE-TRADINGVIEW-2026-10-12-PROPOZYCJA.md`).
Pełne zasady dla rutyn: **`rutyny/tradingview.md`** — rutyny czytają go na
starcie. Skrót:

- Konektor: narzędzia `mcp__TradingView__mcp-tv-*` (27, odczyt + alerty) i
  `mcp__TradingView__mcp-watchlist-*` (8). Schematy ładuje `ToolSearch`
  zapytaniem `select:<pełna nazwa>`. W rutynach WYŁĄCZNIE allowlista odczytu;
  ZAKAZ wszystkich narzędzi zapisu (alerty, watchlisty) i
  `get-active-watchlist` — rutyna nie dostaje pytania o zgodę.
- Pliki: `data/tv-config.json` (`enabled`, `faza`, budżety, flagi — brak pliku
  lub `enabled:false` wyłącza TV), `data/tv-symbole.json` (jedyne źródło
  symboli), `data/tv-kolumny.json` (jedyne źródło nazw kolumn),
  `rutyny/tv-zestaw-b1.json` (zamrożony zestaw snapshotu), `data/tv-log.jsonl`
  (wiersz na bieg), `data/tv-screen-<version>.json` (snapshot sobotni).
  Żaden z nich nie zawiera liczb z rachunku.
- Skrypty: `scripts/waliduj_signals.py --diff HEAD --rutyna puls|sobota`
  (obowiązkowy PRZED każdym commitem `signals.json` — `app.py::_sanity` NIE
  odrzuca obcych kluczy ani zmian w `fills`/`equity_peak`/`wykonanie`, ten
  walidator jest jedyną ochroną), `scripts/tv_porownaj.py` (porównanie
  TV vs Yahoo vs FMP, mediana branży, wiersz logu). Testy obu w
  `scripts/test_app.py`.
- Faza 2 od startu (decyzja właściciela 12.10.2026, po południu): TV w pełnym
  użyciu — drugie źródło kursów i rezerwa poza sesją, reżim z poziomem
  SUROWSZYM z dwóch źródeł, czynniki ilościowe B1/B2 i rewizje ze snapshotu
  i `get-forecasts`, panel fundamentów z `get-financial-history`/dokumentów,
  newsy i 8-K, pre-market, futures NQ, kalendarze, dywidendy. Niezmienne:
  `kursy.py` nr 1 dla zamknięć i `d0.prices` (wariant A), rozjazd = adnotacja
  (nigdy FALLBACK ani uśrednianie), prerejestrowane progi i wagi bez zmian.
  Raport cienia (`reports/tv-cien-2026-10.html`, ok. 31.10) mierzy, nie bramkuje;
  progi WYCOFANIA: `rutyny/tradingview.md` §9.
- Flagi (stan 12.10.2026): `b1_z_tv`, `rezim_surowszy`, `kryterium_event_remis`,
  `event_blokada_taktycznej` = `true`; `sektor_tv` (taksonomia bez dowodu ex
  post), `wstrzymanie_przy_rozjezdzie` (łagodzi wyzwalacze) = `false`;
  `fpe_z_tv` usunięta (brak kolumny forward P/E). **Licencja (regulamin TV
  §3)**: właściciel 12.10.2026 zdecydował, że nie jest bramką — ryzyko przyjmuje
  właściciel; bramka wycofana z planu.
- Nowe pole wpisu `history` (sobota): `dane_b1` = `"tv"` albo `"yahoo"`.
- Konektor FMP wg stanu: na obecnym planie działa `^VIX` EOD,
  earnings-calendar i historical-price-eod-light (wyrywkowo); quote, chart,
  indexes, news odmawiają — nie wołać. Nie jest już „źródłem nr 1”.
- Czego nie robić: `rutyny/tradingview.md` §10 (w szczególności: nie zmieniać
  progów ani pól `signals.json` na podstawie TV, nie blokować rotacji przy
  rozjeździe źródeł, nie uśredniać kursów, nie wołać narzędzi zapisu, nie
  robić inwentaryzacji w rutynie ani w oknach biegów).

## Proces v2 (decyzja 18.10.2026 — gałąź `claude/gifted-lamport-iwzpop`, obowiązuje po scaleniu do `main`)

Źródła: `rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md` (dlaczego),
`rutyny/PROPOZYCJA-2026-10-18-proces-v2.md` (co i jak, warianty decyzji na
19.10, specyfikacja bota), `rutyny/reguly.md` (rejestr reguł — czytany przez
obie rutyny, edytowany tylko commitem właściciela). Materiał dowodowy:
`analiza/2026-10-18/`.

- **Skład koszyka** liczy `scripts/ranking.py` (konstrukcja
  `E_pary_budzet_sox`: 5 par branżowych, momentum 6M relatywne, budżet
  |b_SOX net| ≤ 0,5; veta: exclude, EVENT, σ, cena 1 280 USD, K13). Parametry
  są prerejestrowane w nagłówku skryptu — rutyna ich nie nadpisuje, nie liczy
  progu cenowego z kapitału rachunku i nie zmienia składu „ręcznie". Wynik:
  `data/ranking-<version>.json` (+ opcjonalny cień `U_uznaniowy`), serie
  roczne w scratchpadzie (`data/ranking-cache.csv` jest w `.gitignore`).
- **Pomiar**: `scripts/koszyki_cienie.py` → `data/koszyki-cienie.jsonl`
  (A, B, C, D, E, U, FAKTYCZNY), prerejestrowana tabela A1–A9 w rutynie
  sobotniej; wnioski o wariancji po 12 oknach, o średniej nie przed 26;
  kryteria decyzji po 12/26/52 oknach — decyduje właściciel.
- **Pola `signals.json` pisane przez rutyny — bez zmian** (patrz „Co wolno").
  Nowe w praktyce: Puls pisze w `exclude` wyłącznie wpisy `basis="news"`
  z listy zamkniętej R3/R11 (bramka cenowa 4 %/8 % jest tylko POMIAREM
  w raporcie), `tactical` jest zawsze `[]` (moduł wyłączony), reżim P1 to
  flaga, P2 nadal `NIEAKTUALNA`. Wpis `history` ma `dane_b1: "yahoo"`.
  Walidator (`waliduj_signals.py`) obowiązuje jak dotąd.
- **Pliki dopuszczone w commitach rutyn** (uzupełnienie): sobota — także
  `data/ranking-<version>.json` i `data/koszyki-cienie.jsonl`; żaden plik
  w `data/` nie zawiera liczb z rachunku.
- **Bot (`app.py`) — zmiany v2 WDROŻONE w tej gałęzi (18.10.2026, polecenie
  właściciela „wprowadź wszystkie niezbędne zmiany")**, aktywne po deployu
  na Renderze: stop 15 % LONG / 10 % SHORT (`STOP_LOSS_PCT_LONG/SHORT`) bez
  ponownego otwarcia w tej samej wersji (`STOP_REOPEN=false`, pamięć w
  `wykonanie.stopy`), próg miękki od kroczącego szczytu (`DD_SOFT=0.10`,
  `DD_SOFT_RESET=0.05`, `SOFT_PARY=2` — zamyka pierwsze 2 pary list, stan
  w `wykonanie.soft`), ślad kill switcha (`wykonanie.kill` = data, wersja,
  `dd_pct`, `kill_level` — bez kwot) działający jak ZATRZASK (po kill bot
  trzyma rachunek płasko) i wznowienie: automatyczne po `KILL_RESUME_DAYS=14`
  dniach i zmianie `version` (szczyt := kapitał bez podłogi START_EQUITY,
  zapis do pliku przed otwarciami, koszyk wznowienia z `ALLOC_RESTART=0.04`)
  albo ręczne po dopłacie do ≥ próg × (1 + `KILL_REARM_PCT=0.10`); nowe
  domyślne: `ALLOC_PCT=0.08`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`,
  `REDUCE_FALLBACK=close`. Zmienne w Renderze mają pierwszeństwo — jeśli
  `ALLOC_PCT=0.24` jest tam ustawione jawnie, trzeba je zmienić ręcznie.
  Podklucze `wykonanie.stopy/soft/kill` są POLAMI BOTA — rutyny ich nie
  piszą, tylko czytają; `_sanity` sprawdza ich kształt i przy obcym
  wstrzymuje handel. `/status` zwraca dodatkowo `kill_switch` (próg,
  `zapas_pct`, `dd_od_szczytu_pct`, `zatrzask`, `restart_reczny_od_kapitalu`,
  ślad), `prog_miekki` (stan zapisany `aktywny` i przewidywany
  `wlaczy_sie_w_najblizszym_biegu`), `wykonanie`, `pokrycie_koszyka` z
  `nogi_sygnalu`/`zatrzymane_stopem`/`zamkniete_progiem_miekkim` i nowe pola
  `ustawienia` (m.in. `max_overshoot`, `kill_rearm_pct`). Kod po przeglądzie
  adwersaryjnym diffu (4 recenzentów, 18.10 wieczór) — poprawki w
  `INSTRUKCJA.md` §12. Do deployu rutyny czytają stan faktyczny bota z
  `/status` (`ustawienia`), nie z pamięci.
- **Zmienne Rendera z decyzji 18.10** (ustawia właściciel; rutyny ich nie
  dotykają): `ALLOC_PCT=0.08`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`,
  `TACTICAL_ALLOC_PCT=0`, `REDUCE_FALLBACK=close`, `START_EQUITY=<kapitał>`
  (razem z commitem właściciela `equity_peak := kapitał` — wariant B z
  PROPOZYCJI §1).
- **TradingView w v2**: ≤ 10 wywołań na bieg, tylko kursy/taksonomia/daty
  wyników ze snapshotu B1, reżim i kalendarze (`rutyny/tradingview.md` §0a);
  `get-forecasts`, `get-financial-history`, newsy per spółka — zawieszone.
- **Liczby z rachunku — doprecyzowanie (18.10.2026)**: zakaz obejmuje kwoty
  w walucie, wielkości pozycji ORAZ stosunki do `equity_peak`/`START_EQUITY`
  z precyzją większą niż 2 cyfry znaczące (z nich odtwarza się kwotę).
  Dozwolone w dokumentach: zaokrąglone wskaźniki względne (%, p.p., „≈ 0,8 ×
  START_EQUITY”). Pełne liczby tylko w raportach HTML.
- **Walidator w v2** (`waliduj_signals.py`): dla Pulsu każdy NOWY wpis
  `exclude` musi mieć `basis="news"`, a `tactical` musi być `[]` (starsza
  rutyna → `--v1`); `history` = stare wpisy + dokładnie jeden nowy, lista
  obcięta do 26 OSTATNICH (jak w bocie). `data/koszyki-cienie.jsonl` powstaje
  przy pierwszym biegu v2 (`--log` tworzy plik; wcześniej n = 0).
- **Testy**: `python3 scripts/test_app.py` (walidator włącznie) i
  `python3 scripts/test_ranking.py` (bez sieci).
