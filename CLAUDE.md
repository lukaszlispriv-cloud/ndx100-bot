# ndx100-bot — zasady dla sesji Claude (rutyny „Puls NDX100" i „Raport NDX100")

Repozytorium jest źródłem prawdy dla sygnałów (`signals.json`), raportów
(`reports/`) i treści rutyn (`rutyny/dzienna.md`, `rutyny/tygodniowa.md`).
Egzekucję robi usługa na Renderze (`app.py`, endpoint `/run`), odpalana przez
cron-job.org o **13:45 i 17:05 UTC** (zlecenia tylko w dni robocze; zadanie
13:45 odpala się też w weekendy — patrz „Biegi weekendowe" niżej). Rutyny
nigdy nie składają zleceń i nie dotykają pól pisanych przez bota (`fills`,
`equity_peak`, `wykonanie`).

## Co wolno, czego nie wolno

- Puls pisze w `signals.json` tylko `status`, `exclude`, `tactical`,
  `last_daily`; raport tygodniowy — `version`, `long`, `short`, `d0`,
  `generated`, `exclude=[]`, `tactical=[]`, wpis do `history`. Nic więcej:
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
| `equity_peak` | kroczący szczyt kapitału z `signals.json` (kill switch = `ustawienia.kill_level` × szczyt). Porównaj z plikiem — rozjazd oznacza, że bot zapisał nowy szczyt po ostatnim commicie. |
| `konta_wszystkie[]` | wszystkie rachunki Capital.com; `aktywne_dla_bota = true` wskazuje ten, na którym bot handluje; `blad_przelaczenia_rachunku ≠ null` = handel wstrzymany. |
| `sygnaly` | `version`, `status`, `long`, `short`, `exclude`, `tactical` — wersja sygnałów, którą bot widzi (po rotacji sobotniej jest nowsza niż pozycje na rachunku do poniedziałku 13:45 UTC). |
| `pozycje[]` | pozycje z epikami z mapy `epics` (+ hedge indeksowy): `epic`, `direction`, `size`, `upl` (otwarty wynik), `wejscie` (poziom otwarcia u brokera), `otwarta`. UWAGA: taktyczne spoza NDX-100 (własny `epic`) tu NIE są — patrz `pokrycie_koszyka.pozycje_taktyczne`. |
| `ceny_wejscia` | = `fills` z `signals.json` (ceny odniesienia tezy, pole `cena`); do zwrotów OD CENY WEJŚCIA zgodnie z KROK 1 Pulsu. `cena_brokera` to tylko bieżący poziom u brokera. Noga kontynuowana w nowym koszyku w tym samym kierunku ZACHOWUJE `cena` i `data` z pierwszego wejścia w tezę (bot od 12.10.2026; `wersja` dostaje nową wartość w pierwszym biegu po zmianie `version`, także weekendowym). Wpis ze STARĄ `wersja` = noga poprzedniego koszyka, która czeka na rotację (zamknięcie w poniedziałek 13:45 UTC) — nie „cena sprzed rotacji". Reset do poziomu brokera dotyczy tylko nóg nowych, o zmienionym kierunku albo takich, które wypadły z koszyka i wróciły. Do 10.10.2026 każdy bieg między sobotnim raportem a poniedziałkową rotacją resetował ceny WSZYSTKICH nóg (stąd `fills` z 10.10 ma dla MU, APP, SBUX, CMCSA poziomy brokera z 06.10, nie ceny tezy). |
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
  wielkości tylko w biegu 17:05 — `REBALANCE_HOURS=17`). Rotacja POZYCJI
  (zamknięcie nóg poprzedniego koszyka, otwarcie nowych) wykonuje się
  w pierwszym biegu po zmianie `version` przy OTWARTYM rynku, czyli
  w poniedziałek o 13:45 UTC; sama zmiana `version` w sobotę rotacją nie jest.
- Puls NDX100: dni robocze ok. 12:30 UTC (14:30 Warszawy, przed otwarciem
  NYSE) — widzi stan **po biegu 17:05 UTC z poprzedniego dnia**, a
  w poniedziałek stan **SPRZED rotacji** (pozycje poprzedniego tygodnia przy
  nowych `sygnaly.long/short`). Napisz w raporcie, który to przypadek;
  wskazówką są wpisy `ceny_wejscia` ze starą `wersja` (nogi poprzedniego
  koszyka czekające na zamknięcie) oraz nogi nowego koszyka nieobecne
  w `pozycje`. Noga kontynuowana ma już nową `wersja`, ale `data` sprzed
  rotacji — to poprawne, nie błąd ledgera.
- Biegi weekendowe: historia gita pokazuje commity bota z soboty 3.10,
  niedzieli 4.10 i soboty 10.10.2026, zawsze o 13:45 UTC, nigdy o 17:05 —
  zadanie 13:45 w cron-job.org jest ustawione na codziennie, zadanie 17:05
  na dni robocze (konfiguracja leży w cron-job.org, nie w repo;
  `WDROZENIE-2026-09-28.md`, krok 5, pozostawia weekendy jako opcję). Przy
  zamkniętym rynku bieg nic nie składa (`rynek()` → „pominięte"), ale
  zapisuje ledger `fills` i `wykonanie` — po poprawce z 12.10.2026 taki
  zapis jest dla cen tezy nieszkodliwy (podnosi tylko `wersja` nóg
  kontynuowanych). Jeśli w `fills` pojawi się commit z weekendu zmieniający
  `cena` nogi kontynuowanej, to regresja — zgłoś w problemach.
- Raport tygodniowy (sobota ok. 07:30 UTC): widzi pozycje ROZLICZANEGO
  tygodnia — porównuj je z koszykiem rozliczanym, nie z nowym.
- Stan rachunku nie opuszcza raportów: kapitał i wynik w USD tylko w sekcji
  kontroli rachunku / problemów, nigdy w powiadomieniu push ani w commicie.
