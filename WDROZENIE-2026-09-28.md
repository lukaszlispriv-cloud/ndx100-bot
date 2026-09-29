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

## KROK 3 — Decyzja o alokacji (to jedyna decyzja, jaką masz podjąć)

Co się stanie przy każdym ustawieniu, policzone na Twoich danych z 29.09:

| Ustawienie | Stopa | Pozycja koszykowa | Ekspozycja docelowa |
|---|---|---|---|
| **dziś** (`MARGIN_FROM_AVAILABLE=false`) | 0,89 | 69 USD (6,5%) | 713 USD = 67% kapitału |
| **po włączeniu** (`=true`) | 0,20 | **275 USD (26%)** | **2 856 USD = 270% kapitału** |

### ⏰ Najpierw rzecz pilna — bieg 17:05 UTC dzisiaj

Niezależnie od decyzji: **przy obecnym ustawieniu dzisiejszy bieg 17:05
zetnie portfel.** Pozycje mają dziś po ok. 120–130 USD, a cel wynosi 76 USD,
więc bot utnie **~400 USD ekspozycji i zapłaci 9 spreadów**:

```
MRVL 127 → 76 · SBUX 124 → 76 · APP 123 → 76 · INTU 121 → 76
CMCSA 130 → 76 · AMD 123 → 76 · AVGO 106 → 76 · ADSK 124 → 76 · MU 107 → 76
```

Jeśli i tak zamierzasz podnosić alokację, ścinanie dziś i odbudowa jutro to
czysta strata na spreadzie. **Decyzja przed 17:05 UTC oszczędza ten koszt.**

### Twoje trzy opcje

**A — zostaw ryzyko jak jest, popraw tylko deklarację** *(najbezpieczniejsza)*
W panelu Rendera ustaw:
```
ALLOC_PCT = 0.07
```
Nic więcej. Ekspozycja bez zmian, ale przestajesz deklarować 26% tam, gdzie
naprawdę jest 7% — i bieg 17:05 nie zetnie portfela, bo cel zrówna się z tym,
co już masz. Stopka raportów przestaje kłamać czterokrotnie.

**B — podnieś dwukrotnie** *(zalecana, jeśli chcesz iść w stronę projektu)*
```
MARGIN_FROM_AVAILABLE = true
ALLOC_PCT             = 0.12
```
Ekspozycja rośnie z ~113% do ~130% kapitału. `MAX_EXPOSURE_STEP=0.25`
rozłoży dojście na kilka biegów. Po tygodniu obserwacji ewentualnie `0.19`,
potem `0.26`.

**C — pełna alokacja projektowa**
```
MARGIN_FROM_AVAILABLE = true
```
`ALLOC_PCT` zostaje `0.26`. Ekspozycja **270% kapitału**. Dołek z 14.09
(−4,6%) zrobiłby się ok. **−18%**, a próg kill switcha (−25%, czyli 810 USD)
byłby w zasięgu jednej złej sesji. Tylko jeśli to akceptujesz.

> Jak ustawić: Render → `ndx100-bot` → **Environment** → **Add Environment
> Variable** → klucz i wartość → **Save Changes**. Zapis sam wywoła deploy.
> Po pierwszym biegu sprawdź w `/run` blok `limit_depozytowy`: pole
> `zrodlo_depozytu` ma pokazać `kapitał − dostępne`, a `alloc_pct_faktyczny`
> ma się zgadzać z tym, co ustawiłeś.

---

## KROK 4 — Rutyna tygodniowa (nadal niezrobione, koszyk ma już 18 dni)

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
