# Co masz zrobić — wdrożenie poprawek z audytu 28.09.2026

Kod jest gotowy i wypchnięty na `main`. Twoja część to **cztery kroki**.
Krok 1 i 2 zajmują po 2 minuty i są bezpieczne. Krok 3 to decyzja o ryzyku —
najpierw czytasz jedną liczbę, dopiero potem decydujesz. Krok 4 to rutyna
tygodniowa.

Kolejność ma znaczenie. **Nie rób kroku 3 przed krokiem 1.**

---

## KROK 1 — Wdróż nową wersję na Renderze ✅ ZROBIONE 29.09

Potwierdzone odczytem `/run`: cena odniesienia przeżywa wyrównanie (ADSK 211,55 przy poziomie brokera 206,80), okno `REBALANCE_HOURS` działa, `błędy: []`, ostrzeżenie o rotacji się zapala. Poniżej zostaje opis dla porządku.

### Co było do zrobienia

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

## KROK 2 — Diagnoza: ZROBIONA 29.09.2026 ✅

Odczyt `/run` z 29.09 o 08:57 UTC rozstrzygnął sprawę. **Nie musisz nic
sprawdzać** — poniżej wynik.

Bot liczył stopę depozytu z pola `deposit` zwracanego przez API. To pole
tego dnia było **co do grosza równe gotówce**, a nie depozytowi
zabezpieczającemu:

| | 29.09.2026 | 18.09.2026 |
|---|---|---|
| kapitał | 1 057,73 | 1 041,61 |
| dostępne do handlu | 820,42 | 864,15 |
| pole `deposit` z API | **1 053,62** | 177,45 |
| gotówka (`kapitał − wycena`) | **1 053,62** ← to samo | — |
| `kapitał − dostępne` | **237,31** | 177,46 |
| ekspozycja brutto | 1 184,43 | ~888 |
| **stopa z pola `deposit`** | **0,89** ❌ | 0,20 |
| **stopa z `kapitał − dostępne`** | **0,2004** ✅ | 0,1998 |

Różnica `kapitał − dostępne` daje **20,0% w obu odczytach** — podręcznikową
stopę dla akcji USA. Na odczycie z 18.09 oba źródła były zgodne i dlatego
błąd tak długo był niewidoczny.

**Wniosek: to nie jest kwestia dźwigni na Twoim rachunku, tylko czytania
złego pola.** Dodałem zmienną `MARGIN_FROM_AVAILABLE` — domyślnie `false`,
czyli nic się nie zmienia, dopóki sam nie zdecydujesz.

---

## KROK 3 — Decyzja o alokacji (SPROSTOWANIE 29.09, opcja A odpada)

### Co się zmieniło w tej analizie

Pisałem wcześniej, że opcja A (`ALLOC_PCT=0.07`) zatrzyma dzisiejsze cięcie
portfela. **To było błędne.** Po wiernym przeliczeniu według kodu:

limit depozytowy przycina `ALLOC_PCT` **proporcjonalnie**, żeby zmieścić się
w `ekspozycja_max`. Przy stopie 0,89 ten sufit wynosi **713 USD** i jest
sztywny — obniżanie `ALLOC_PCT` nie podnosi sufitu, tylko obniża cel jeszcze
bardziej. Dlatego A tnie **mocniej** niż nicnierobienie.

### Trzy scenariusze na bieg 17:05 UTC, policzone na danych z 29.09 08:57

| Scenariusz | Ustawienie | Transakcji dziś | Ekspozycja po biegu |
|---|---|---|---|
| Nic nie robię | `ALLOC_PCT=0.26` | **9** (cel 76 USD/poz.) | 1 184 → 789 USD (75%) |
| ~~Opcja A~~ | `ALLOC_PCT=0.07` | **9** (cel 68 USD/poz.) | 1 184 → 721 USD (68%) |
| **Opcja B** | `MARGIN_FROM_AVAILABLE=true`<br>`ALLOC_PCT=0.12` | **0** | 1 184 → **1 190 USD (113%)** |

**Opcja A jest zdominowana** — ta sama liczba spreadów co przy
nicnierobieniu, a portfel mniejszy. Nie ma powodu jej wybierać.

Kluczowa obserwacja: przy `ALLOC_PCT=0.12` i poprawnej stopie cel wynosi
**126,9 USD na pozycję**, a Twoje pozycje mają dziś 106–130 USD. Wszystkie
mieszczą się w paśmie tolerancji (±38 USD) — czyli **opcja B to zero
transakcji i zero spreadu**. To nie jest podniesienie ekspozycji, tylko
zatrzymanie jej tam, gdzie już jest.

### Co zrobić dziś — rekomendacja

**Ustaw opcję B już dziś**, przed 17:05 UTC:

```
MARGIN_FROM_AVAILABLE = true
ALLOC_PCT             = 0.12      (zmiana z 0.26)
```

Uzasadnienie, które stoi za pierwotnym „A dziś, B po weekendzie", brzmiało:
nie podnoś ekspozycji na przeterminowanej prognozie. **B przy 0,12 niczego
nie podnosi** — zostawia 113% kapitału, czyli dokładnie to, co już masz —
a przy okazji oszczędza 9 spreadów i naprawia odczyt stopy depozytu.

### Jedyny powód, żeby zrobić inaczej

Jeśli świadomie chcesz **mniejszej** ekspozycji na 18-dniowym koszyku, zwłaszcza
przed wynikami Microna w środę 30.09 po sesji — wtedy **nie rób nic dziś**,
pozwól biegowi 17:05 ściąć portfel do 75% kapitału i ustaw opcję B dopiero
w poniedziałek. Kosztuje to 9 spreadów dziś plus 9 w poniedziałek, czyli ok.
**4 USD (0,4% kapitału)** za cztery sesje niższego ryzyka.

To jedyny realny wybór, jaki tu jest. Obie drogi są sensowne; A nie jest.

### Po weekendzie (poniedziałek 5.10)

Jeżeli dziś wybrałeś B, w poniedziałek **nie musisz nic robić** — chyba że
po rotacji koszyka chcesz iść dalej w stronę projektowych 26%. Wtedy
`ALLOC_PCT = 0.19`, a po kolejnym tygodniu `0.26`. Za każdym razem sprawdź
w `/run`, czy `alloc_pct_faktyczny` zgadza się z tym, co ustawiłeś — jeśli
nie, znowu coś przycina i trzeba to obejrzeć, zanim pójdziesz wyżej.

> **Tego kroku nie mogę wykonać za Ciebie** — to zmienne środowiskowe
> w Twoim panelu Render, do którego nie mam dostępu.
> Render → `ndx100-bot` → **Environment** → przy `ALLOC_PCT` wpisz nową
> wartość, potem **Add Environment Variable** → `MARGIN_FROM_AVAILABLE` =
> `true` → **Save Changes**. Zapis sam uruchomi deploy. Zajmuje 30 sekund.

---

## KROK 4 — Rutyna tygodniowa: ODTWORZONA 29.09 ✅ — teraz wklej poprawioną wersję

Ustalone: między 12.09 a 19.09 treść zadania sobotniego została nadpisana
treścią dziennego (soboty 19.09 i 26.09 odpaliły puls o 07:1x, w slocie
tygodniowym). Odtworzona wersja to stan sprzed `INSTRUKCJA.md` §5.6.

**Poprawiona treść jest w repo: `rutyny/tygodniowa.md`** (lista zmian:
`rutyny/README.md`). Od teraz to jest źródło prawdy — najpierw plik, potem
wklejenie do zadania.

1. Otwórz `rutyny/tygodniowa.md`, skopiuj **wszystko poniżej linii `---`**.
2. Wklej do zadania „Ranking NDX100 — raport tygodniowy", zastępując treść.
3. **Odpal ręcznie teraz** — najlepiej przed **13:45 UTC (15:45 czasu
   polskiego)**, żeby bieg bota 13:45 wykonał rotację jednym ruchem.
   Prompt sam rozpozna, że to bieg w środku tygodnia (n = 12 sesji od D0),
   i oznaczy rozliczenie W4 jako PRZETERMINOWANE z polem `sesje: 12`.
4. Po biegu sprawdź:
   ```
   grep -o '"version": "[^"]*"' signals.json     # 2026-W5
   ls reports/raport-2026-W*.html                 # przybyło W5
   ```
   W `history` ma być wpis `2026-W4` z obiema seriami (`spread_pp`,
   `spread_fills_pp`) i `sesje: 12`.

Czego się spodziewać po rotacji: bot o 13:45 zamknie nazwy spoza nowego
koszyka i otworzy nowe od razu po ok. 127 USD; `exclude` i `tactical` zostaną
wyczyszczone (AKAM zamknięty — tak działa rotacja z założenia); ceny odniesienia
zresetują się dla wszystkich nazw (nowa `version`); ostrzeżenie `⏳ koszyk 18
dni` zniknie.

**Zadanie dzienne — jedna zmiana, kiedy będziesz miał chwilę.** Kopia z dwiema
poprawkami: `rutyny/dzienna.md`. Najważniejsza: stopka raportu mówi jeszcze
„26% kapitału", a prawda to 12%. Skopiuj treść poniżej `---` i wklej do
zadania „Puls NDX100". To nie jest pilne — nie blokuje niczego.

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
