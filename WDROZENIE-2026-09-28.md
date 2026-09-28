# Co masz zrobić — wdrożenie poprawek z audytu 28.09.2026

Kod jest gotowy i wypchnięty na `main`. Twoja część to **cztery kroki**.
Krok 1 i 2 zajmują po 2 minuty i są bezpieczne. Krok 3 to decyzja o ryzyku —
najpierw czytasz jedną liczbę, dopiero potem decydujesz. Krok 4 to rutyna
tygodniowa.

Kolejność ma znaczenie. **Nie rób kroku 3 przed krokiem 1.**

---

## KROK 1 — Wdróż nową wersję na Renderze (2 min, bezpieczne)

Nic nie musisz ustawiać. Wszystkie nowe wartości domyślne są już w kodzie.

1. Wejdź na **Render → usługa `ndx100-bot` → Manual Deploy → Deploy latest commit**.
2. Poczekaj na `==> Your service is live 🎉` w logu.
3. Sprawdź, czy w panelu **Environment** **NIE MASZ** ustawionych ręcznie:
   `REBALANCE_TOL_MIN`, `MIN_REBALANCE_ACC`, `REBALANCE_HOURS`.
   Jeśli któraś tam jest — **usuń ją**, bo przesłania nową wartość domyślną.

**Co się zmieni od razu:**

| | Przed | Po |
|---|---|---|
| Wyrównywanie wielkości pozycji | w każdym biegu (13:45 i 17:05 UTC) | tylko 17:05 UTC |
| Minimalna korekta wielkości | brak progu | 25 USD |
| Dolne pasmo tolerancji | 12% | 30% |
| Cena wejścia po wyrównaniu | kasowana | **zachowywana** |
| Weekendowe `błędy: 1` | jest | znika |

**Czego oczekiwać w powiadomieniu po pierwszym biegu:** `akcje` spadnie
(mniej wyrównań), `pominięte` wzrośnie (bot mówi teraz, czego świadomie nie
robi). To jest poprawne zachowanie, nie usterka.

> **Ważne o cenach wejścia.** Od tego wdrożenia ceny w `signals.json → fills`
> przestają się kasować. Ale te, które są tam **teraz**, pochodzą z ostatniego
> churnu (np. SBUX i MRVL mają datę `2026-09-28`, bo dzisiejszy bieg 13:45 je
> nadpisał). Czyli: od teraz są stabilne, ale w pełni sensowne staną się
> dopiero od najbliższej rotacji koszyka (krok 4). Wyjątek: **MU ma prawdziwą
> cenę 913,35 z 27.08** i ona zostaje.

---

## KROK 2 — Odczytaj diagnozę alokacji (3 min, tylko czytanie)

Po pierwszym biegu na nowej wersji otwórz w przeglądarce:

```
https://ndx100-bot.onrender.com/run?token=TWÓJ_TOKEN
```

(token masz w adresie, którego używa cron-job.org — skopiuj go stamtąd)

W zwróconym JSON-ie znajdź blok **`limit_depozytowy`**. Interesują Cię
cztery pola:

```json
"limit_depozytowy": {
  "stopa_wyliczona":      <-- TO JEST NAJWAŻNIEJSZA LICZBA
  "stopa_depozytu":       <-- ta, której bot faktycznie użył
  "realizacja_celu":      <-- 1.0 = alokacja pełna, 0.25 = ćwiartka
  "alloc_pct_faktyczny":  <-- ile NAPRAWDĘ wynosi pozycja koszykowa
}
```

**Zapisz sobie te cztery liczby** — bez nich krok 3 jest zgadywaniem.

Jak to czytać:

| `stopa_wyliczona` | Co to znaczy | Co robić |
|---|---|---|
| **ok. 0,20** | Wszystko w porządku, dźwignia 5:1 jak na akcjach USA | Krok 3 **niepotrzebny** — alokacja jest zdrowa |
| **0,90–1,00** | Rachunek raportuje depozyt = pełna wartość pozycji. To hipoteza z audytu | Przejdź do kroku 3 |
| **coś innego** | Nie zgaduj — **napisz mi, jaka to liczba**, i ustalimy razem | — |

---

## KROK 3 — Decyzja o alokacji (tylko jeśli krok 2 pokazał stopę ≈ 1,0)

**Przeczytaj to, zanim cokolwiek zmienisz.**

Dziś pozycja koszykowa to ok. **6,5% kapitału**, choć deklarujemy 26%.
Ustawienie `MARGIN_RATE_MAX=0.5` sprawi, że bot odrzuci niewiarygodny odczyt
i zejdzie na `MARGIN_RATE_FALLBACK` (0,20) — i **ekspozycja wzrośnie około
czterokrotnie**.

Co to znaczy w liczbach, na Twoich własnych danych z ostatniego miesiąca:

| | Dziś (~6,5%) | Po zmianie (~26%) |
|---|---|---|
| Wynik z koszyka W4 | +5,2% kapitału | +20,8% kapitału |
| Obsunięcie z 14.09 | −4,6% | **ok. −18%** |
| Odległość do kill switcha (−25%) | daleko | **jedna zła sesja** |

To nie jest „naprawa buga" — to **zmiana profilu ryzyka**, na którą musisz
świadomie się zgodzić. Masz trzy opcje:

### Opcja A — zostaw jak jest, popraw tylko deklarację (zalecana na start)
Nic nie ustawiasz na Renderze. Zamiast tego powiedz mi, żebym zmienił
`ALLOC_PCT` na `0.065`, czyli na to, co system naprawdę robi. Zyskujesz to,
że stopka raportu („1 p.p. zwrotu pozycji = 0,26 p.p. kapitału") przestaje
kłamać czterokrotnie. Ryzyko bez zmian.

### Opcja B — podnieś stopniowo
Ustaw na Renderze:
```
MARGIN_RATE_MAX = 0.5
ALLOC_PCT       = 0.12
```
To daje ok. dwukrotny wzrost zamiast czterokrotnego. Ogranicznik
`MAX_EXPOSURE_STEP=0.25` i tak rozłoży dojście do celu na kilka biegów.
Obserwuj tydzień, potem ewentualnie `ALLOC_PCT = 0.19`, a na końcu `0.26`.

### Opcja C — pełna alokacja od razu
```
MARGIN_RATE_MAX = 0.5
```
`ALLOC_PCT` zostaje `0.26`. **Tylko jeśli akceptujesz obsunięcia rzędu −18%
na rachunku DEMO.**

> Cokolwiek wybierzesz — **napisz mi, którą opcję**, a dopiszę to do
> `INSTRUKCJA.md` i poprawię stopkę raportów dziennych, żeby przeliczenia
> punktów na dolary się zgadzały.

---

## KROK 4 — Rutyna tygodniowa (najpilniejsze po kroku 1)

Rutyna sobotnia **nie wystartowała 19.09 ani 26.09**. To dlatego koszyk
`2026-W4` pracuje 17. dzień zamiast 5., a pięć reakcji z 15–17.09 wisi
zamrożonych, bo miały obowiązywać „do soboty".

Sprawdź w kolejności:

1. **Czy zadanie w ogóle istnieje?** Wejdź w listę swoich zaplanowanych
   rutyn (tam, gdzie zdefiniowana jest rutyna dzienna „Puls NDX100”)
   i sprawdź, czy obok niej jest rutyna sobotnia.
2. **Czy ma poprawny harmonogram?** Powinna odpalać w sobotę, po zamknięciu
   piątkowej sesji.
3. **Czy się nie wywraca po cichu?** Jeśli jest i ma harmonogram, odpal ją
   ręcznie raz i zobacz, czy dojdzie do końca.

**Po naprawie rutyna sobotnia powinna, tak jak dotąd:** nadpisać `long`,
`short`, `version`, `d0`, dopisać wpis do `history` (`spread_pp`,
`spread_fills_pp`, `reaction_pp`), wyczyścić `exclude` i wygenerować
`reports/raport-2026-WX.html`.

**Jeśli rutyny nie da się szybko przywrócić** — napisz mi, a przygotuję
rotację jako zadanie do odpalenia ręcznie w tej samej sesji co puls dzienny.

> Od teraz bot sam o tym przypomina: po 9 dniach od `d0` w powiadomieniu
> pojawia się `⏳ koszyk N dni`, a w „pominiętych" linia `UWAGA ROTACJA`.

---

## KROK 5 (opcjonalny, 1 min) — cron w weekendy

Biegi w sobotę i niedzielę nic nie robią (giełda zamknięta). Po kroku 1 nie
zgłaszają już błędu, więc możesz je spokojnie zostawić. Jeśli wolisz czysty
log, w cron-job.org ustaw harmonogram na **poniedziałek–piątek**.

---

## Jak sprawdzić, że zadziałało

Po **trzech sesjach** na nowej wersji:

| Co sprawdzić | Gdzie | Ma być |
|---|---|---|
| Liczba par „zamknij i otwórz" | eksport transakcji | **blisko zera**; dziś 63/mies. |
| `↓ bramka x4` w powiadomieniu | log Render | znika albo maleje — bramka zaczyna widzieć prawdziwe ruchy |
| `błędy:` w biegach weekendowych | log Render | `0` |
| `fills[TICKER].cena` | `signals.json` | **nie zmienia się** między biegami |
| `fills[TICKER].cena_brokera` | `signals.json` | nowe pole, może się zmieniać |
| `⏳ koszyk N dni` | powiadomienie | znika po naprawie rutyny tygodniowej |

Jeśli którakolwiek pozycja z tej tabeli nie wyjdzie — wklej mi log z Rendera
albo świeży eksport transakcji i zdiagnozuję.
