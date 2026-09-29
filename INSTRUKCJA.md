# NDX100 BOT — instrukcja po poprawkach z 18.09.2026

Dokument opisuje, co zmieniło się w kodzie po rozliczeniu okresu
27.08–18.09.2026 (`reports/rozliczenie-2026-08-27_2026-09-18.html`),
co trzeba ustawić w Renderze i jak wygląda poprawiony prompt rutyny
dziennej.

---

## 1. Co naprawiono i dlaczego

| Usterka | Co kosztowała | Poprawka |
|---|---|---|
| Wyzwalacze liczone od kursu D0, a nie od ceny wejścia | LITE zamknięty 15.09 z zyskiem 0,37 USD zamiast 5,14 USD; łącznie cztery reakcje = **−17,43 USD** | Bramka wyzwalaczy cenowych + pole `fills` w `signals.json` |
| REDUCE dla drogich spółek po cichu się nie wykonywał | rozjazd sygnałów z portfelem, niewidoczny w logu | Jawne pominięcie w raporcie + `REDUCE_FALLBACK` |
| Weekend raportowany jako błąd | prawdziwa awaria wyglądała jak sobota | `rynek()` rozdziela pominięcie od błędu |
| Brak stopu od ceny wejścia | STX **−12,02 USD**, −13% w cztery sesje bez reakcji | `STOP_LOSS_PCT` |
| Kill switch od stałej 1000 USD | przy kapitale 1104 USD próg 750 = obsunięcie −32%, nie −25% | `KILL_TRAILING` + `equity_peak` |
| Kapitał z API nigdy nie weryfikowany | rozjazd 2,5× z historią transakcji, niezauważony | Kontrola kapitału + automatyczne zejście na `ALLOC_PCT_SAFE` |
| Moduł taktyczny bez czego wybierać | 10% kapitału bezczynne przez cały okres | Pozycja taktyczna może mieć własny `epic` |
| `scripts/kursy.py` wisiał przy HTTP 429 | brak kursów, ręczne obchodzenie źródła | Lista User-Agentów + budżet czasu |
| Nieużywana integracja z Telegramem | sugerowała, że alert dociera gdzieś poza log | Usunięta w v1.8.1 |
| **Podwójne liczenie wyceny pozycji w kapitale** | kapitał zawyżony o 6%, pozycje i próg kill switcha liczone od złej podstawy | Kapitałem jest samo `balance` (v1.9.0) |

### Przyczyna „limitu Yahoo" — to nie był limit

Pomiar z 18.09.2026, ten sam adres, ta sama sekunda:

```
User-Agent: Mozilla/5.0                                  -> HTTP 200 (3/3)
User-Agent: Mozilla/5.0 (X11; Linux x86_64) ... Chrome/126.0  -> HTTP 429 (3/3)
brak nagłówka User-Agent                                 -> HTTP 429
```

Stary kod wysyłał pełny łańcuch Chrome, dostawał 429 i traktował to jak
przeciążenie: spał 45/90/180 s i dostawał 429 znowu. Po poprawce skrypt
przechodzi całą listę User-Agentów bez spania i pobiera 104 symbole
w **12 sekund** zamiast wisieć kwadrans.

---

## 2. Zmienne środowiskowe w Renderze

Nowe (wszystkie mają sensowne domyślne — ustaw tylko to, co chcesz zmienić):

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `REACT_GATE` | `true` | Weryfikuj wyzwalacze cenowe wobec ceny wejścia. `false` = zachowanie sprzed poprawki. |
| `REACT_REDUCE_PCT` | `0.04` | Próg REDUCE liczony od ceny wejścia. |
| `REACT_CLOSE_PCT` | `0.08` | Próg CLOSE liczony od ceny wejścia. |
| `STOP_LOSS_PCT` | `0.10` | Twardy stop od ceny wejścia. `0` wyłącza. |
| `REDUCE_FALLBACK` | `keep` | Gdy minimalna wielkość > cel po redukcji: `keep` zostawia pełną pozycję, `close` zamyka całość. |
| `KILL_TRAILING` | `true` | Kill switch od kroczącego szczytu kapitału. |
| `EQUITY_TOL` | `0.02` | Tolerancja kontroli kapitału (ułamek equity). |
| `ALLOC_PCT_SAFE` | `0.10` | Wielkość pozycji, gdy kontrola kapitału nie przechodzi. |
| `WRITE_FILLS` | `true` | Zapis cen wejścia do `signals.json`. |
| `MAX_EXPOSURE_STEP` | `0.25` | O ile najwyżej mogą urosnąć w JEDNYM biegu pozycje już niesione. `0` wyłącza. |
| `MARGIN_BUDGET` | `0.60` | Jaka część kapitału może być najwyżej zamrożona w depozycie zabezpieczającym. |
| `MARGIN_RATE_FALLBACK` | `0.20` | Stopa depozytu przyjmowana, gdy nie da się jej wyliczyć z rachunku. |
| `REBALANCE_TOL_MIN` | `0.30` | Dolna granica pasma tolerancji wielkości pozycji. **Podniesione z `0.12` po audycie 28.09.2026** — patrz rozdział 10. |
| `MIN_REBALANCE_ACC` | `25` | Minimalna wartość korekty wielkości (w walucie rachunku). Poniżej progu bot nie rusza pozycji, bo spread za wyrównanie jest droższy niż korekta. |
| `REBALANCE_HOURS` | `17` | Godziny UTC, w których bot wyrównuje wielkości pozycji (lista po przecinku; puste = w każdym biegu). Otwarcia, zamknięcia, reakcje i stopy działają w każdym biegu niezależnie od tego ustawienia. |
| `MARGIN_RATE_MAX` | `1.0` | Górna granica wiarygodności stopy depozytu wyliczonej z rachunku. `1.0` = zachowanie sprzed audytu. Niższa wartość (np. `0.5`) każe odrzucić niewiarygodny odczyt i zejść na `MARGIN_RATE_FALLBACK`. **Zwiększa ekspozycję kilkukrotnie — zmieniaj dopiero po odczytaniu diagnozy z `/run`.** |
| `MARGIN_FROM_AVAILABLE` | `false` | Skąd brać użyty depozyt: `false` = pole `deposit` z API (zachowanie sprzed poprawki), `true` = `kapitał − dostępne`. **`true` to wartość poprawna** (patrz 10.3), ale podnosi ekspozycję ok. czterokrotnie — włączaj razem z docelowym `ALLOC_PCT`. |
| `ROTATION_MAX_DNI` | `9` | Po ilu dniach od `d0` bot ostrzega, że rutyna tygodniowa nie wystartowała. `0` wyłącza ostrzeżenie. |
| `KURSY_LIMIT_CZASU` | `600` | Budżet czasu dla `scripts/kursy.py` (sekundy). |
| `KURSY_UA` | — | Własny User-Agent dla Yahoo, próbowany jako pierwszy. |

Zmienione domyślne: **`ALLOC_PCT` z `0.10` na `0.26`** oraz
**`TACTICAL_ALLOC_PCT` z `0.05` na `0.10`** — podwojenie wielkości pozycji
na życzenie właściciela rachunku (18.09.2026). Co to znaczy w liczbach,
przy kapitale 1041,61 USD i stopie depozytu 20%:

| | Przed | Po |
|---|---|---|
| Wielkość jednej pozycji koszykowej | ~99 USD | ~271 USD |
| Ekspozycja brutto (9 pozycji) | 888 USD | ~2 350 USD |
| Depozyt zabezpieczający | 177 USD | ~470 USD |
| Dostępne do handlu | 864 USD | ~570 USD |
| Poziom depozytu | 587% | ~222% |
| Dźwignia brutto wobec kapitału | 0,85× | ~2,26× |

Dojście do nowego poziomu zajmuje **pięć biegów** — tyle wynika
z `MAX_EXPOSURE_STEP`. Ekspozycja rośnie kolejno: 888, 1060, 1301, 1638,
1976, 2351 USD.

Największe obsunięcie wyniku zanotowane w okresie 27.08–18.09 to −4,9%
kapitału przy wielkości pozycji ok. 10%. Przy 26% ta sama seria zdarzeń
dałaby ok. −12,7%, a kill switch stoi na −25% od kroczącego szczytu.

Podniesienie wielkości pozycji jest obwarowane dwoma bezpiecznikami, które
działają automatycznie:

1. **Kontrola kapitału** — dopóki equity z API nie daje się odtworzyć
   z pozycji, które bot zna, obowiązuje `ALLOC_PCT_SAFE` (0,10).
2. **Limit depozytowy** — bot wylicza stopę depozytu na żywo (depozyt
   zabezpieczający podzielony przez bieżącą ekspozycję) i nie pozwala,
   by depozyt przekroczył `MARGIN_BUDGET` kapitału. Bez tego broker
   zacząłby odrzucać zlecenia, a bieg raportowałby serię błędów otwarcia
   zamiast powiedzieć wprost, że zabrakło wolnego depozytu.
3. **Ogranicznik tempa** — pozycje już niesione nie urosną w jednym biegu
   o więcej niż `MAX_EXPOSURE_STEP`. Nowo otwierane idą od razu w pełnym
   rozmiarze, inaczej sobotnia rotacja koszyków byłaby zduszona.

> Jeżeli masz `ALLOC_PCT` ustawione jawnie w panelu Rendera, zmiana
> domyślnej w kodzie **nic nie da** — trzeba poprawić zmienną w panelu.
> Efektywną wielkość widać teraz w każdej linii `NOTIFY:` jako `poz. X%`.
>
> Chcesz dokładnie dwukrotność DZISIEJSZYCH pozycji (~196 USD zamiast
> ~271 USD)? Ustaw `ALLOC_PCT=0.19`. Różnica bierze się stąd, że książka
> nie zdążyła dojść do poprzedniego celu 13% — dzisiejsze ~99 USD na
> pozycję to nie jest to samo co ustawione 13%.

---

## 3. Nowe pola w `signals.json`

Wszystkie są **opcjonalne** — plik bez nich działa jak dotąd.

```jsonc
{
  "fills": {                      // pisze BOT po każdym biegu, nie ruszaj ręcznie
    "MU": {"cena": 913.35, "kierunek": "BUY", "wielkosc": 0.1, "data": "2026-08-27"}
  },
  "equity_peak": 1104.12,         // pisze BOT — odniesienie kill switcha
  "exclude": [
    {"ticker": "LITE", "action": "CLOSE", "reason": "...",
     "basis": "cena"}             // cena | news | rekom | short | rezim
  ],
  "tactical": [
    {"ticker": "GNRC", "direction": "BUY", "epic": "GNRC",
     "entry_date": "2026-09-18"}  // epic pozwala wyjść poza uniwersum NDX-100
  ]
}
```

`basis` decyduje, czy wpis przechodzi przez bramkę. **Brak pola = `cena`**,
czyli wpis jest weryfikowany. Wpisy reżimowe (`reason` zaczyna się od
„REŻIM") nigdy nie są łagodzone.

---

## 4. Rozjazd kapitału — rozstrzygnięty

Rozliczenie wykazało, że kapitał w logu rósł ok. 2,5× szybciej, niż
wynikało z historii transakcji. **Przyczyna została ustalona 18.09.2026
i naprawiona w v1.9.0: to był błąd w kodzie, nie w rachunku.**

Bot liczył kapitał jako `balance + profitLoss`, a Capital.com podaje
w polu `balance` **już kapitał z wyceną otwartych pozycji**
(`balance = deposit + profitLoss`). Wycena była doliczana drugi raz.

Wykluczone po drodze, w tej kolejności:

1. **Wpłata na rachunek** — właściciel sprawdził historię operacji
   gotówkowych, między 15 a 18 września nic nie wpłynęło.
2. **Niekompletny eksport transakcji** — broker dopisuje wiersz `SWAP` dla
   każdej otwartej pozycji codziennie o 21:00 UTC; porównanie dzień po dniu
   dało zgodność **22 na 22 dni**, co do czwartego miejsca po przecinku.
3. Zostało podwójne liczenie, potwierdzone dopasowaniem wzoru
   `1000 + zrealizowany + 2 × niezrealizowany` do sześciu odczytów z logu
   ze średnim odchyleniem **3,90 USD**.

**Co to zmienia w liczbach.** Rzeczywisty kapitał na 18.09 to ok. **1 041
USD**, nie 1 104 USD. Zysk okresu to **+4,1%**, nie +10,4%. Wynik liczony
z historii transakcji (**+33,47 USD**) był prawidłowy przez cały czas —
pochodzi z eksportu, a nie z API rachunku.

**Co zrobiono w kodzie.** Kapitałem jest teraz samo `balance`. Gdy API poda
pole `deposit`, bot sprawdza tożsamość `balance = deposit + profitLoss`;
złamanie tej tożsamości zapala kontrolę kapitału i obniża wielkość pozycji
do `ALLOC_PCT_SAFE`. Pole `equity_peak` w `signals.json` zostało
wyzerowane, bo zapisana wartość 1104,36 pochodziła z zawyżonego kapitału —
bot zasieje je ponownie przy najbliższym biegu.

**Czego pilnować dalej.** W `/status` sekcja `kontrola_kapitalu` powinna
pokazywać `zgodne: true`. Jeśli pokaże `false`, przeczytaj `powod`:

- **`pozycje spoza książki bota`** — na rachunku są pozycje, których bot nie
  otwierał. Zamknij je albo dopisz ich instrumenty do mapy `epics`.
- **`API łamie tożsamość balance = deposit + profitLoss`** — broker zmienił
  semantykę pól; napisz, sprawdzimy ponownie.
- Dopóki `zgodne: false`, bot sam trzyma `ALLOC_PCT_SAFE`.

---

## 5. Poprawiony prompt rutyny dziennej

Prompt żyje w harmonogramie Cowork, nie w repozytorium — trzeba go
podmienić ręcznie. Poniżej fragmenty, które się zmieniają.

### 5.1. W KROKU 0 (wczytanie stanu)

> Wyciągnij dodatkowo: **`fills`** (faktyczne ceny wejścia zapisane przez
> bota) i `equity_peak`. Jeżeli `fills` jest puste, pracuj jak dotąd na
> `d0.prices` i **zaznacz to w raporcie**.

### 5.2. W KROKU 2 (werdykt) — zamiast dotychczasowego akapitu o `exclude`

> **exclude — reakcje per spółka koszykowa, DWA szczeble.**
> Każdy wpis MUSI mieć pole `basis` o wartości `cena`, `news`, `rekom`,
> `short` albo `rezim` — opisuje, co jest podstawą reakcji.
>
> **Wyzwalacze cenowe (`basis: "cena"`) liczy się od ceny z `fills`**, a nie
> od `d0.prices`. Gdy dla spółki nie ma wpisu w `fills`, użyj `d0.prices`
> i dopisz w `reason`: „brak ceny wejścia, mierzone od D0".
>
> Wyzwalacz czysto cenowy uzbraja się dopiero po spełnieniu **obu**
> warunków:
> 1. **ruch względny**, czyli ruch spółki minus ruch ^NDX w tym samym
>    oknie, mieści się w paśmie 4–8 p.p. (REDUCE) albo przekracza 8 p.p.
>    (CLOSE) przeciw tezie;
> 2. **potwierdzenie drugą sesją** — próg jest przekroczony na zamknięciu
>    dwóch kolejnych sesji. Po pierwszej sesji odnotuj spółkę w sekcji
>    „Najważniejsze zmiany" jako obserwowaną, ale NIE twórz wpisu.
>
> Oba warunki **nie obowiązują**, gdy wpis ma podstawę inną niż cenowa
> (`news`, `rekom`, `short`) albo jest wpisem reżimowym — te działają od
> razu, tak jak dotąd.
>
> **Nie twórz wpisu cenowego w dniu, w którym cały sektor spółki spadł
> o ponad 3%** — to nie jest sygnał o spółce. Odnotuj to w raporcie.

### 5.3. W KROKU 2 (moduł taktyczny)

> Skanuj **S&P 500 i Nasdaq Composite**, nie tylko NDX-100. Koszyki
> pozostają bez zmian — poszerzenie dotyczy wyłącznie modułu taktycznego.
> Dla spółki spoza mapy `epics` **podaj pole `epic`** (symbol z Capital.com,
> zwykle ten sam co ticker; sprawdź endpointem `/search?q=...`). Bez tego
> pola bot pominie pozycję.

### 5.4. W KROKU 3 (raport)

> W tabelach koszyków dodaj kolumnę **„kurs wejścia"** z `fills` i licz
> „zwrot pozycji" od niej. Zwrot od D0 zostaw jako osobną kolumnę — mierzy
> jakość prognozy, a nie wynik rachunku. Gdy obie liczby różnią się o
> ponad 2 p.p., zaznacz to wyraźnie.

### 5.5. W KROKU 4 (zapis)

> Podmieniaj TYLKO: `status`, `exclude`, `tactical`, `last_daily`.
> Pól **`fills` i `equity_peak` nie ruszaj** — pisze je bot i nadpisanie
> ich zepsuje bramkę wyzwalaczy oraz kill switch.

### 5.6. Rutyna TYGODNIOWA (sobota) — jedno zdanie do dopisania

Rutyna sobotnia przebudowuje `signals.json` mocniej niż dzienna (nowa
`version`, nowe koszyki, nowe `d0`, wpis do `history`). Dopisz jej w kroku
zapisu to samo zabezpieczenie:

> Pól **`fills` i `equity_peak` nie ruszaj** — pisze je bot. `fills` po
> rotacji koszyków i tak przestaje pasować do nowych nazw; bot odtworzy je
> sam przy pierwszym poniedziałkowym biegu, ale kasowanie ich ręcznie nic
> nie daje, a skasowanie `equity_peak` cofa kill switch do `START_EQUITY`.

Gdyby rutyna mimo to wyczyściła te pola, **nic się nie psuje**: bramka
wyzwalaczy przepuszcza wtedy wpisy pulsu bez zmian (czyli zachowanie
sprzed poprawek), a `equity_peak` zasiewa się ponownie od bieżącego
kapitału przy najbliższym biegu.

---

## 6. Testy

```bash
python3 scripts/test_app.py     # 52 testy logiki decyzyjnej, bez sieci
python3 scripts/kursy.py        # kursy + sekcja REŻIM
```

`test_app.py` (77 testów) pokrywa bramkę wyzwalaczy, kontrolę kapitału,
stopy, klasyfikację stanu rynku, budowę książki, ogranicznik tempa i
kontrolę spójności `signals.json`. Uruchom go po każdej zmianie w
`app.py`.

## 7. Gdzie szukać powiadomień

Integracja z Telegramem została usunięta — nie była używana. Podsumowanie
każdego biegu trafia w dwa miejsca:

1. **Log usługi w Renderze** (zakładka Logs) — szukaj linii zaczynających
   się od `NOTIFY:`. Wyglądają tak:

   ```
   NOTIFY: 🤖 NDX100 BOT /run v2026-W4 | kapitał 1104.12 USD | akcje: 3 |
   pominięte: 5 | błędy: 0 | DEMO | ↓ bramka x4
   ```

2. **Odpowiedź endpointu `/run`** — pełny JSON z listami `akcje`,
   `pominiete`, `błędy`, `reakcje`, `kontrola_kapitalu`, `stopy`
   i `ogranicznik_tempa`. To samo widać w `/status` bez wykonywania
   transakcji.

Znaczenie dopisków na końcu linii `NOTIFY:`:

| Dopisek | Znaczenie |
|---|---|
| `↓ bramka xN` | Bot odrzucił N reakcji pulsu, bo licząc od ceny wejścia nie przekraczają progów. |
| `⚠ KONTROLA KAPITAŁU` | Kapitał z API nie zgadza się z pozycjami bota — wielkość pozycji zeszła na `ALLOC_PCT_SAFE`. |
| `⛔ STOP xN` | N pozycji zamkniętych twardym stopem od ceny wejścia. |

## 8. Decyzja projektowa: dwa różne progi, celowo

System mierzy ruch kursu DWOMA sposobami i to nie jest niedopatrzenie.

| Kto | Co mierzy | Próg |
|---|---|---|
| Rutyna dzienna (puls) | ruch spółki **względem ^NDX** od ceny wejścia | 4–8 p.p. REDUCE, >8 p.p. CLOSE |
| Bramka w `app.py` | ruch **bezwzględny** od ceny wejścia | 4% REDUCE, 8% CLOSE |

Reakcja wykonuje się tylko wtedy, gdy **oba** testy wypadną na tak. Puls
odpowiada na pytanie „czy teza się psuje", bramka na pytanie „czy pozycja
realnie traci pieniądze". Do cięcia potrzebne są obie odpowiedzi.

**Dlaczego tak, a nie bramka też względna.** Rozliczenie okresu
27.08–18.09.2026 pokazało, że wszystkie cztery reakcje czysto cenowe
trafiły w lokalny dołek i kosztowały **17,43 USD**, a cały zysk okresu
siedział w pozycjach, których nikt nie ruszył. Przy takim rozkładzie
błędów pomyłka w stronę „nie tnij" jest tańsza od pomyłki w stronę „tnij",
więc koniunkcja dwóch progów jest właściwym ustawieniem. Dodanie bramce
odniesienia do indeksu wymagałoby pobierania serii ^NDX z Capital.com
przy każdym biegu i powiększyłoby liczbę rzeczy, które mogą zawieść,
w zamian za częstsze cięcia — czyli dokładnie to, co okazało się kosztowne.

**Konsekwencja dla rutyny dziennej.** Wpis, którego ruch bezwzględny nie
sięga progu, nie zostanie wykonany, więc puls ma go w ogóle nie tworzyć,
tylko oznaczyć spółkę jako OBSERWOWANĄ. Wpis, którego bot nie wykona,
zaśmieca `signals.json` i fałszuje sobotnie rozliczenie reakcji.

**Kiedy tę decyzję odwrócić.** Gdy sobotnie rozliczenie przez kilka tygodni
z rzędu pokaże dodatnie `reaction_cena_pp` — czyli że reakcje cenowe
zaczęły zarabiać — progi bramki są za luźne i wtedy warto wrócić do tematu.
Testy `scripts/test_app.py` w sekcji „KONIUNKCJA PROGÓW" pilnują, żeby
zachowanie nie zmieniło się przypadkiem.

## 9. Czego poprawki NIE zmieniają

- Metody budowania koszyków i rankingu tygodniowego.
- Kierunków pozycji — bramka tylko łagodzi reakcje, nigdy nie odwraca tezy.
- Zachowania przy `status: NIEAKTUALNA` i przy reżimie P2 — nadal zamykają
  wszystko.
- Zachowania bez pola `fills` w `signals.json`: dopóki bot nie zapisze cen
  wejścia, bramka przepuszcza wpisy pulsu bez zmian, czyli system działa
  dokładnie jak przed poprawką.

---

## 10. Audyt miesiąca (28.09.2026) — cztery poprawki w kodzie

Pełny raport: `reports/audyt-2026-09-28.html`. Wynik okresu 29.08–25.09.2026:
kapitał 1 000 → 1 072,32 USD (**+7,23%**) wobec ^NDX **+3,99%**, przewaga
**+3,24 p.p.** przy becie 0,51. Poniżej to, co audyt wykrył i co zostało
zmienione w kodzie.

### 10.1. Churn — bot zamykał i otwierał tę samą pozycję

W eksporcie transakcji jest **63 par „CLOSED + OPENED tego samego
instrumentu w tej samej sekundzie"**; od 21.09 działo się to w każdym biegu.
To nie była rotacja koszyka, tylko wyrównywanie wielkości: Capital.com nie
zmienia wielkości pozycji w miejscu, więc kod ją zamyka i otwiera na nowo.

Koszt zmierzony wprost z cen (różnica między ceną zamknięcia a ceną
ponownego otwarcia): **11,82 USD = 1,1% kapitału w miesiąc**, a w fazie
pełnego churnu **0,21% kapitału na sesję**, czyli ok. **4,4% miesięcznie**
przy wyniku +7,2%. Obrót księgi: 14 754 USD przy kapitale 1 070 USD.
Najdroższe są tanie spółki — SBUX 0,328% i CMCSA 0,312% na parę, wobec
AVGO 0,088%; SBUX i CMCSA to 49% rachunku.

**Zmiana:** `REBALANCE_TOL_MIN` z `0.12` na `0.30`, nowy próg
`MIN_REBALANCE_ACC` = 25 (nie ruszamy pozycji dla korekty wartej mniej niż
25 USD) i nowe okno `REBALANCE_HOURS` = `17` (wyrównywanie tylko w biegu
17:05 UTC). Otwarcia, zamknięcia, reakcje i stopy działają w każdym biegu.

### 10.2. Churn kasował cenę wejścia — bramka i stop-loss były martwe

To skutek uboczny 10.1 i realnie ważniejszy od samego kosztu.
`ceny_wejscia()` bezwarunkowo nadpisywała cenę z `signals.json` poziomem
otwarcia u brokera. Skoro pozycja była otwierana na nowo w każdym biegu,
„cena wejścia" miała kilka godzin. Skutki:

- bramka reakcji (4% / 8%) zawsze widziała ruch bliski zeru i zwracała
  „BRAK" — w logu **`↓ bramka x4` w dwudziestu biegach z rzędu**, a pięć
  reakcji postawionych 15–17.09 **nie wykonało się ani razu**;
- `STOP_LOSS_PCT` = 10% mógł zadziałać wyłącznie przy luce >10% między
  biegami, czyli praktycznie nigdy;
- kolumna „zwrot od wejścia" w raporcie dziennym i pole `spread_fills_pp`
  mierzyły godziny, nie tydzień.

**Zmiana:** `signals.json` → `fills` niesie teraz **cenę odniesienia tezy**,
a nie poziom otwarcia u brokera. Cena przeżywa wyrównanie i kasuje się tylko
przy: zmianie kierunku pozycji, rotacji koszyka (poznawanej po zmianie
`version`, zapisywanej w nowym polu `fills[TICKER].wersja`) albo pierwszym
otwarciu pozycji. Bieżący poziom brokera idzie do nowego pola
`fills[TICKER].cena_brokera` — do rachunku P/L i diagnostyki. Wpis bez pola
`wersja` (sprzed tej zmiany) jest uznawany za ważny, więc migracja niczego
nie gubi. Osiem testów w sekcji „CENA ODNIESIENIA TEZY".

### 10.3. Alokacja 6,5% zamiast deklarowanych 26%

Ekspozycja brutto wynosiła 765 USD wobec celu 2 890 USD (10 × 26% + 10%
taktyczna). Osiągnięta ekspozycja była praktycznie równa budżetowi depozytu
(0,60 × 1 070 = 642 USD), co znaczy, że bot wyliczał stopę depozytu bliską
**1,0** — „dolar ekspozycji wymaga dolara depozytu". Warunek w kodzie
(`0.01 <= wyliczona <= 1.0`) taki odczyt przepuszczał, a limit przycinał
`ALLOC_PCT` proporcjonalnie: z 0,26 do ok. 0,06. W powiadomieniach widać to
jako `poz. 6.7%` i `poz. 12.5%` zamiast 26%.

**Zmiana — celowo bez wpływu na zachowanie.** Nowa zmienna
`MARGIN_RATE_MAX` (domyślnie `1.0`, czyli dokładnie jak dotąd) pozwala
odrzucić niewiarygodny odczyt. Bot **diagnozuje** problem sam: blok
`limit_depozytowy` w odpowiedzi `/run` ma teraz pola `stopa_wyliczona`,
`stopa_odrzucona`, `realizacja_celu` i `alloc_pct_faktyczny`, a gdy cel jest
osiągalny w mniej niż 90%, do „pominiętych" trafia linia `UWAGA ALOKACJA`,
a do powiadomienia znacznik `↘ alokacja X%/26%`.

**ROZSTRZYGNIĘTE 29.09.2026 — to nie jest kwestia dźwigni, tylko złego pola.**
Odczyt `/run` pokazał `stopa_wyliczona: 0.8896`, ale zestawienie całego bloku
`konto` wyjaśnia dlaczego:

| | 29.09.2026 | 18.09.2026 |
|---|---|---|
| kapitał | 1 057,73 | 1 041,61 |
| dostępne do handlu | 820,42 | 864,15 |
| pole `deposit` z API | **1 053,62** | 177,45 |
| `kapitał − wycena` (gotówka) | **1 053,62** | — |
| `kapitał − dostępne` | **237,31** | 177,46 |
| ekspozycja brutto | 1 184,43 | ~888 |
| stopa z pola `deposit` | **0,8896** | 0,1998 |
| stopa z `kapitał − dostępne` | **0,2004** | 0,1998 |

29.09 pole `deposit` jest co do grosza równe **gotówce**, a nie depozytowi
zabezpieczającemu — stąd stopa 89%. Różnica `kapitał − dostępne` daje **20,0%
w obu odczytach**, czyli podręcznikową stopę dla akcji USA. Na odczycie
z 18.09 oba źródła były zgodne i właśnie dlatego błąd tak długo pozostawał
niewidoczny.

**Zmiana:** nowa zmienna `MARGIN_FROM_AVAILABLE`. Domyślnie `false`, czyli
zachowanie bez zmian. Niezależnie od ustawienia blok `limit_depozytowy`
zawiera teraz `depozyt_z_pola`, `depozyt_z_dostepnych`, `zrodlo_depozytu`
oraz `gdyby_drugie_zrodlo` — symulację tego, co zrobiłoby drugie źródło.
Decyzja o włączeniu jest decyzją o ryzyku, nie o poprawności odczytu.

Podniesienie alokacji **czterokrotnie zwiększa też obsunięcia** — dołek
14.09 (−4,56%) zrobiłby się ok. −18%, a próg kill switcha −25% byłby
w zasięgu jednej złej sesji. Dlatego domyślna wartość niczego nie zmienia
i decyzja należy do właściciela rachunku (patrz instrukcja wdrożenia).

### 10.4. Rutyna tygodniowa nie wystartowała — bot o tym nie mówił

Soboty 19.09 i 26.09 nie zrobiły rotacji: w repo są raporty `W1`–`W4`
i nic więcej, `signals.json` nadal ma `version: 2026-W4` i `d0: 2026-09-11`,
a `history` kończy się na `2026-W3`. Koszyk pracował 17. dzień zamiast 5.,
a reguła „raz zredukowana zostaje do soboty" zamieniła się w „do odwołania".

**Zmiana:** nowa zmienna `ROTATION_MAX_DNI` (domyślnie 9). Po przekroczeniu
bot dopisuje `UWAGA ROTACJA` do „pominiętych", wystawia blok `wiek_koszyka`
w odpowiedzi `/run` i znacznik `⏳ koszyk N dni` w powiadomieniu. Bot nie
umie rotacji wymusić — ma o niej przypominać.

### 10.5. Weekendowe biegi kończyły się błędem

Trzy z czterech biegów weekendowych raportowały `błędy: 1` przy
`akcje: 0`. Ta sama sytuacja — brak wyceny rynku — raz kończyła się statusem
(POMINIĘCIE), a raz wyjątkiem `requests.HTTPError` (BŁĄD). **Zmiana:** brak
wyceny rynku w pętli otwarć jest teraz zawsze pominięciem; kanał „błędy"
zostaje dla rzeczy, które wymagają reakcji człowieka.
