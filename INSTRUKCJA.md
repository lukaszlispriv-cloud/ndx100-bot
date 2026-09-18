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

---

## 6. Testy

```bash
python3 scripts/test_app.py     # 52 testy logiki decyzyjnej, bez sieci
python3 scripts/kursy.py        # kursy + sekcja REŻIM
```

`test_app.py` (52 testy) pokrywa bramkę wyzwalaczy, kontrolę kapitału,
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

## 8. Czego poprawki NIE zmieniają

- Metody budowania koszyków i rankingu tygodniowego.
- Kierunków pozycji — bramka tylko łagodzi reakcje, nigdy nie odwraca tezy.
- Zachowania przy `status: NIEAKTUALNA` i przy reżimie P2 — nadal zamykają
  wszystko.
- Zachowania bez pola `fills` w `signals.json`: dopóki bot nie zapisze cen
  wejścia, bramka przepuszcza wpisy pulsu bez zmian, czyli system działa
  dokładnie jak przed poprawką.
