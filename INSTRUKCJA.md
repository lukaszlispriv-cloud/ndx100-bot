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
| `MAX_EXPOSURE_STEP` | `0.25` | O ile najwyżej może urosnąć łączna ekspozycja brutto w JEDNYM biegu. `0` wyłącza. |
| `KURSY_LIMIT_CZASU` | `600` | Budżet czasu dla `scripts/kursy.py` (sekundy). |
| `KURSY_UA` | — | Własny User-Agent dla Yahoo, próbowany jako pierwszy. |

Zmieniona domyślna: **`ALLOC_PCT` z `0.10` na `0.13`**.

Podniesienie wielkości pozycji jest obwarowane dwoma bezpiecznikami, które
działają automatycznie:

1. **Kontrola kapitału** — dopóki equity z API nie daje się odtworzyć
   z pozycji, które bot zna, obowiązuje `ALLOC_PCT_SAFE` (0,10).
2. **Ogranicznik tempa** — ekspozycja brutto nie urośnie w jednym biegu
   o więcej niż `MAX_EXPOSURE_STEP`. Symulacja na stanie z 18.09.2026:
   bez ogranicznika książka skoczyłaby z 709 do 1292 USD w jednym biegu,
   z ogranicznikiem rośnie do 886 USD i dochodzi do celu przez kilka
   biegów.

> Jeżeli masz `ALLOC_PCT` ustawione jawnie w panelu Rendera, zmiana
> domyślnej w kodzie **nic nie da** — trzeba poprawić zmienną w panelu.
> Chcesz zostać przy dotychczasowej wielkości? Ustaw `ALLOC_PCT=0.10`.

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

## 4. Co zrobić ręcznie, zanim podniesiesz wielkość pozycji

Rozliczenie wykazało rozjazd: kapitał w logu rósł ok. 2,5× szybciej, niż
wynikało z historii transakcji (17.09: log +47,1 USD wobec +21,8 USD
z odtworzonych pozycji). Kolejność działań:

1. Otwórz `/status` — jest tam nowa sekcja `kontrola_kapitalu`.
2. Jeśli `zgodne: false`, przeczytaj `powod`:
   - **`pozycje spoza książki bota`** — na rachunku są pozycje, których bot
     nie otwierał. To najprostsze wyjaśnienie rozjazdu. Zamknij je ręcznie
     albo dopisz ich instrumenty do mapy `epics`.
   - **`wycena z API vs suma upl`** — API liczy coś, czego bot nie widzi.
     Sprawdź historię operacji gotówkowych na Capital.com (wpłata lub
     korekta na rachunku demo eksportu transakcji **nie** zawiera).
3. Dopóki `zgodne: false`, bot sam trzyma `ALLOC_PCT_SAFE` — nie musisz
   nic wyłączać, ale nie zobaczysz też efektu podniesienia wielkości.
4. Gdy `zgodne: true`, ekspozycja dojdzie do nowego celu w kilku biegach,
   pilnowana przez `MAX_EXPOSURE_STEP`.

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

---

## 6. Testy

```bash
python3 scripts/test_app.py     # 46 testów logiki decyzyjnej, bez sieci
python3 scripts/kursy.py        # kursy + sekcja REŻIM
```

`test_app.py` (52 testy) pokrywa bramkę wyzwalaczy, kontrolę kapitału,
stopy, klasyfikację stanu rynku, budowę książki, ogranicznik tempa i
kontrolę spójności `signals.json`. Uruchom go po każdej zmianie w
`app.py`.

## 7. Czego poprawki NIE zmieniają

- Metody budowania koszyków i rankingu tygodniowego.
- Kierunków pozycji — bramka tylko łagodzi reakcje, nigdy nie odwraca tezy.
- Zachowania przy `status: NIEAKTUALNA` i przy reżimie P2 — nadal zamykają
  wszystko.
- Zachowania bez pola `fills` w `signals.json`: dopóki bot nie zapisze cen
  wejścia, bramka przepuszcza wpisy pulsu bez zmian, czyli system działa
  dokładnie jak przed poprawką.
