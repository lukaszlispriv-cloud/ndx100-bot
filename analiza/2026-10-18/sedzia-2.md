# Sędzia 2 — wykonalność operacyjna (mały rachunek CFD, lot 0,1 akcji, Render/cron, rutyny Claude bez użytkownika, ryzyko błędu w `app.py`, zgodność z CLAUDE.md)

Sesja 18.10.2026. Oceniam projekty A (`projekt-A-mechaniczny.md`), B (`projekt-B-przezywalnosc.md`), C (`projekt-C-konstrukcja.md`)
w świetle werdyktów C1–C9 i wyników faz 1–2. Perspektywa: co da się wdrożyć do soboty 24.10 bez człowieka przy klawiaturze
w dni robocze, ile nowych ścieżek awarii powstaje w `app.py`, jak zachowuje się to przy locie 0,1 akcji i kapitale rzędu
`START_EQUITY`, czy rutyny zostają w granicach CLAUDE.md (pola `signals.json`, walidator, `/status` tylko do odczytu).
Bez liczb z rachunku — kapitał odniesienia 1 000 USD (`app.py:164`) i stosunek 0,83 z C9.

Własny skrypt tej notatki: `sedzia2_soft_loty.py` → `sedzia2_soft_loty_wyniki.json` (odtworzony `calc_size` z `app.py:871–898`,
krok 0,1, `MAX_OVERSHOOT` 1,6; kursy z ostatniego wiersza `dane/closes_5y.csv`). Sprawdzone w repo: `python3 scripts/test_app.py`
→ 151 OK, `scripts/test_ranking.py` → 17 OK (stan `b86ef1b`).

---

## 1. Oceny (1–10; total = suma)

| projekt | evidence | implementability | risk-adjusted return | overfitting robustness | **total** |
|---|---|---|---|---|---|
| **A — proces mechaniczny (ranking.py A + vol-target + σ-stop + nakładka)** | 8 | 4 | 6 | 7 | **25** |
| **B — przeżywalność (ALLOC 0,06 + FLAT + wznowienie + stop 15/10)** | 6 | 8 | 5 | 5 | **24** |
| **C — konstrukcja E (5 par z budżetem SOX, stałe 0,08 + próg miękki)** | 7 | 7 | 7 | 6 | **27** |

**Najlepszy: C**, pod warunkiem przeszczepienia rdzenia operacyjnego B (§4). Różnica jest mała i wynika z trzech rzeczy,
które widzi sędzia operacyjny, a nie quant: (1) C usuwa źródło zmienności w konstrukcji (σ-ratio 0,67, najgorszy tydzień
−12,7 vs −23,9 p.p.) **bez żadnego nowego pola w `signals.json` i bez zmiany walidatora**, czego A nie potrafi (pole `sizing`
+ `_sanity` + walidator + 22 zmiany plików w 5 dni); (2) B zostawia na stanowisku jedyny proces, którego ten audyt nie
obronił — uznaniową rutynę sobotnią Modelu 3.0 (IC −0,10, 10/16 stron nadpisanych, 36 reguł po n=1, 36 min TV) — i kalibruje
sizing 0,06 do jej 98. percentyla zmienności, co na tej skali rachunku wycina 7 nazw z uniwersum i blokuje połowienie
pozycji (§3.2); (3) przy stałym 0,08 próg miękki ×0,5 jest wykonalny dla 81/102 nazw (skrypt tej notatki), więc C nie
potrzebuje maszyny stanów FLAT z B.

---

## 2. Co werdykty C1–C9 robią z każdym projektem

| werdykt | A | B | C |
|---|---|---|---|
| C1 momentum netto +0,1…+0,5, zero w CI; ALLOC ≤ 12 %/nogę; nie powoływać się na t≈2 ze składu dzisiejszego | zgodny (sizing do alfy 0, sufit 0,12, liczby z PIT) — ale momentum zostaje **tezą koszyka**, nie tie-breakerem | nie dotyka selekcji; sizing 0,06 zgodny | zgodny (momentum wewnątrz par; liczby PIT 209 okien) |
| C2 pary = tylko redukcja ryzyka, koszt 0,3–0,5 p.p./tydz. średniej, zamrozić definicję; rozstrzygnięcie pary vs niższy ALLOC **tylko na koszyku-cieniu** | zgodny: pary jako cień, σ przez sizing | — | **wyprzedza werdykt**: E (= pary + budżet) wchodzi do bota od W9, nie jako cień; definicja grupy zamrożona na tej z Δ≈0 (najlepsza z 5 → efekt wyboru, C2 §) |
| C3 stop: EV −0,18…−0,42 przy 24 %/nogę, asymetria L/S, nie D0, reopen koszt ≈ 0; sizing 10× ważniejszy | σ-stop `clip(2σ60√5, 8 %, 20 %)` bez reopen — EV −0,002 na PIT, ale wymaga σ per noga z pliku repo w każdym biegu | **dokładnie C3**: 15 % LONG / 10 % SHORT, bez reopen, kotwica brokera; zmiana przez env | stop poza zakresem — zostaje 10 % + reopen „do czasu kodu A” |
| C4 ALLOC 0,24→0,10 natychmiast; vol-target **najpierw ≥12 tyg. na papierze**, potem pole; nie 0,12; polityka po kill obowiązkowa; P(kill) zawsze z horyzontem i alfą | **łamie staging**: pole `sizing` od W9; sufit 0,12; polityka wznowienia tak | zgodny: VT jako etap 2 po 12 tyg.; wznowienie w kodzie; P(kill) z horyzontem i alfą w stopce | stałe 0,08 (VT dla E martwy: 0,12 w 98 % tygodni); **brak polityki wznowienia** (odsyła do A) |
| C5 p usunąć; sizing do IC≈0; rozdzielić stronę/kolejność | zgodny (ranking JSON, nakładka księgowana) | p usuwa; reszta poza zakresem | zgodny (Model 3.0 skreślony) |
| C6 uchylić K10 i warianty od W9, zachować sito short po kolapsie | zgodny (reguly.md, K13 zostaje) | moratorium „bez zmian” — **nie uchyla K10 jawnie**, a selekcja zostaje uznaniowa | zgodny (ranking.py nie zna K10; K13 veto) |
| C7 bramka 4/8 EV≈0 — usunąć lub zostawić jako pomiar | pomiar | pomiar (KONTROLA STOPÓW) | pomiar |
| C8 reżim tylko P2 (DD>20 %), bez histerezy | zgodny | P2 jako wyłącznik; P1 nie opisany | zgodny |
| C9 restart = `equity_peak` **i** `START_EQUITY` razem; kill-resume potrzebuje własnej zmiennej, testu, INSTRUKCJA; `START_EQUITY` do `/status` | opcja (c) + `KILL_COOLDOWN_WEEKS` | opcja (c) + `KILL_RESUME_VERSIONS`, `start_equity` w `/status`, test, INSTRUKCJA §12 — **najpełniej** | opcja (c) jako „decyzja właściciela”; brak kodu wznowienia |

---

## 3. Analiza operacyjna projekt po projekcie

### 3.1 Projekt A — najlepiej udokumentowany, najcięższy do wdrożenia

Za: jedyny projekt z pełną pętlą dowodu (rejestr reguł z testem na PIT, cienie A0/A/B/C/D/ETF/FAKT, metryki prerejestrowane,
horyzonty 12/26/52), rutyna sobotnia staje się przepisywaniem wyniku skryptu, Puls dzienny jako raport kontrolny ≤ 8 wywołań TV.
Liczby spójne z C1/C4 (vt+soft P(kill 12/52 tyg., alfa 0) 0 %/17 %, `projektA_boot_out.md`).

Przeciw (wykonalność):

1. **Zakres kodu do 24.10**: 22 pozycje w §11, w tym `app.py` #9–#15 (sizing w `_sanity` i `sync()`, σ-stop z odczytem
   `data/ranking-<version>.json` przez `gh_get_file` w każdym biegu, brak reopen, kill-resume, soft, `MAX_EXPOSURE_STEP`
   wobec całej książki, `/status`), walidator (+6 testów), `ranking.py` (nakładka, sizing, hash), `koszyki_cienie.py`,
   nowy `test_regula.py`, 4 pliki rutyn, CLAUDE.md, INSTRUKCJA.md; cel 151 → ~175 testów. Bez człowieka-programisty
   w dni robocze to plan na 2–3 tygodnie, nie 5 dni. A sam to przyznaje (§12.4 „kod nie gotowy → ALLOC ręcznie z raportu”),
   ale wtedy pierwszy tydzień W9 gra na ręcznie przepisanym parametrze — ryzyko procesu ręcznego, które `ryzyko-i-sizing.md`
   wskazuje jako gorsze od kodu.
2. **Nowe pole `sizing` wbrew stagingowi C4** (najpierw ≥12 tyg. na papierze). Rozszerza kontrakt z CLAUDE.md (rutyna
   sobotnia pisze nowe pole, walidator jest jedyną ochroną) i tworzy nową ścieżkę zatrzymania handlu: `_sanity` ma odrzucać
   `|alloc − clip(formuła)| > 1e-4` — `ranking.py` zaokrągla do 4 miejsc (`round(alloc, 4)`, `ranking.py:367`), więc
   tolerancja jest na granicy błędu zaokrąglenia; każdy rozjazd = bot stoi do interwencji właściciela.
3. **σ-stop z pliku repo w każdym biegu** = nowa zależność sieciowa w ścieżce zleceń (GitHub API 2×/dzień poza
   `signals.json`); fallback 10 % istnieje, ale C3 mówi wprost, że stop obniża kill 12-tyg. o 3,6 pkt, sizing o ~32 — to
   najdroższy kodowo element o najmniejszym efekcie.
4. **Sufit 0,12 = gross 120 %** przy hipotezie zawyżonej stopy depozytu w dniu rotacji (2,4× — `wykonanie-bota.md`):
   `MARGIN_BUDGET` 0,60 / (0,20·2,4) = 125 % kapitału (`app.py:135, 1603`) — gross 120 % siedzi na limicie, czyli podwójne
   wejście 13:45→17:05 z 12.10 wraca; przy 80 % (C) i 60 % (B) limit nie wiąże. C4: „nie 0,12”.
5. **Nakładka Model 3.0 (≤1 wymiana/stronę)**: uczciwie księgowana, ale niemierzalna (|Δ| ≥ 0,71 po 26 tyg.) i utrzymuje
   w rutynie research per spółka, który przekraczał budżet TV (36 vs 20 min). Z parami (C) łamie budżet SOX, chyba że
   wymiana całej pary.
6. Ekspozycja czynnikowa zostaje (b_SOX zreal. +0,91): tydzień typu W7 przy 0,08 ≈ −8…−10 % kapitału; próg miękki działa
   po nim (A §14 p.2). Dla rachunku ≈ 1,7 % nad progiem, który właśnie przeżył W7, to najsłabszy punkt A.
7. Drobne: A nie wymienia `scal_wykonanie` (patrz §3.3 p.2) — jego `wykonanie.soft/stopy/kill` zostałyby zgubione tak samo
   jak w C.

### 3.2 Projekt B — najlepszy rdzeń operacyjny, niepełny jako projekt

Za: jedyny projekt, który **przeczytał kod do końca**: `scal_wykonanie` (`app.py:900–929`) buduje wynik od zera i zgubi
podklucze `stopy/plasko/kill`; kill (`app.py:1497–1503`) robi `return rep` przed zapisem, więc nie zostawia śladu w pliku;
zapis `fills` jest `try/except` („udogodnienie, nie warunek handlu”, `app.py:1969–1971`) → stan FLAT/kill musi być zapisany
twardo; `ALLOC_PCT_SAFE` 0,10 > nowy `ALLOC_PCT` (awaryjna większa od normalnej — `app.py:129, 1430`) → 0,04;
`START_EQUITY` do `/status.ustawienia` (C9). Zero nowych pól `signals.json`, zero zmian walidatora, ~120–150 linii,
~14 testów, każda nowa zmienna z domyślną = dzisiejsze zachowanie (`STOP_REOPEN` true, `DD_FLAT_PCT` 0, `KILL_RESUME_VERSIONS`
0) — wdrożenie odwracalne z panelu Rendera. Asymetryczny stop 15/10 bez reopen = dosłownie C3. Zgodność z CLAUDE.md najwyższa
(wszystko w `wykonanie`, polu bota).

Przeciw:

1. **Selekcja zostaje Modelem 3.0**. B pisze „zakres A/C”, ale to oznacza, że od W9 rutyna sobotnia nadal: 20 czynników
   (33 % czysto uznaniowych), elita, panel fundamentów, nadpisania 7/10 nóg (W8), reguły K4–K17 istniejące tylko w HTML.
   Z perspektywy „rutyny Claude bez użytkownika” to największe ryzyko operacyjne systemu — nieodtwarzalny wynik, przekroczony
   budżet TV, produkcja reguł po n=1 — i B go nie dotyka. Kalibracja sizingu do σ 7–11 p.p. (koszyki Modelu 3.0) wymusza
   0,06, podczas gdy A/E mają σ 4,6–6,7 p.p.
2. **0,06 na tej skali rachunku psuje koszyk** (`projekt_B_sim_out.md` E; `sedzia2_soft_loty.py`): przy 0,83×START_EQUITY
   7 nazw pomijanych (ASML COST LITE MELI MPWR MU SNDK), 14 kolejnych na minimalnym locie bez możliwości redukcji, 12 z
   niewykonalnym połowieniem; veto lotu > ~650 USD wycina sprzęt AI, gdzie siedzi sygnał momentum. Przy 0,08 pomijane są 3–4
   nazwy, a veto cenowe 1 280 USD kosztuje Δ +0,03…+0,04 (t ≤ 1,5; `projektC_bt_out.md` §2) — 0,08 jest praktyczną podłogą
   tego rachunku, 0,06 kupuje P(kill 52 tyg., alfa 0) 27 % zamiast 53 % **tylko dla koszyków o σ Modelu 3.0**.
3. **FLAT −12 % od szczytu cyklu** to druga maszyna stanów obok kill-resume (cooldown liczony w numerach `version` —
   arytmetyka ISO-tygodni przez granicę roku W52/W53→W1 do napisania i przetestowania). B sam liczy: P(kill 52 tyg.) 27,3 → 25,5 %,
   wartość to „kształt ogona i przewidywalność”. Argument B, że ×0,5 jest niewykonalne, jest prawdziwy przy 0,06 (26/102 nazw
   bez redukcji lub niewykonalnych), ale przy 0,08 próg miękki redukuje ≥40 % w 81/102 nazw, w koszyku E 9/10 nóg
   (tylko AMD zostaje na 0,1 akcji) — FLAT staje się zbędny, jeśli ALLOC = 0,08.
4. Puls zachowuje basis `rekom`/`short` (nieweryfikowalne z środowiska, 1/8 wpisów wykonany — A §7.1), nie uchyla K10 jawnie.
5. Automatyczne wznowienie po kill z resetem `equity_peak` przez bota jest przesunięciem progu po stracie (C9 §5); B to wie
   i nakłada obowiązek linii „obsunięcie od szczytu historycznego” — warunek konieczny, nie opcja.

### 3.3 Projekt C — najlżejszy kodowo i najlepszy ogon, z trzema dziurami do zasypania

Za: adresuje zdiagnozowaną przyczynę (74 % wariancji spreadu W1–W7 = czynnik, `dekompozycja-wynikow.md`) w konstrukcji,
nie w sizingu: σ-ratio E/A 0,669 [0,58; 0,78] i b_SOX zreal. +0,31 vs +1,08 na PIT, tygodnie SOX−NDX<−3: −1,9 vs −5,1 p.p.;
redukcja σ odporna na wszystkie 5 definicji grupy (0,59–0,76). Przy 0,08: gross 80 %, σ dz. kapitału ≈ 0,8 %, P(kill 12 tyg.)
0,0 %, 52 tyg. 8,1 % bez progu / 0,2 % z progiem (alfa 0). **Zero nowych pól top-level**, `_sanity` bez zmian, ALLOC w
Renderze; `ranking.py` ma już `grupy`, `konstrukcja_pary`, bety — dopisek to jedna funkcja (56 podzbiorów) + 6 testów,
offline. Kluczowe operacyjnie: „jeśli kod `app.py` nie zdąży, E i tak wchodzi 24.10” — selekcja odsprzęgnięta od bota.
Puls wyłącznie kontrolny, exclude tylko basis news z dokumentem.

Przeciw:

1. **„Jedyna zmiana w `app.py` to próg miękki” jest nieprawdą**: `wykonanie.soft` zginie w `scal_wykonanie` (`app.py:900–929`,
   wynik budowany z `{"reakcje","taktyczne"}`), a `zmiana_wyk` (`app.py:1952–1953`) porównuje tylko te dwa klucze — stan `soft`
   ani nie przetrwa, ani nie wymusi commita. To samo dotyczy A. Poprawka jest mała (B #9), ale bez niej histereza progu
   (×0,5 do powrotu nad −5 %) nie działa: każdy bieg liczy od nowa i przy DD między −5 % a −10 % bot przełącza się
   tam i z powrotem co bieg (spread za każde wyrównanie).
2. **Brak polityki wznowienia po kill** (C4 pkt 5 „obowiązkowa przed zmianą sizingu”, C9 pkt 2) i **brak zmiany stopu**
   (10 % + reopen zostaje „do czasu kodu A”). C odsyła do projektu A, którego nie da się wdrożyć w tym terminie — w praktyce
   C bez B nie ma siatki poniżej kill.
3. **`ALLOC_PCT_SAFE` nieruszone** → przy `kontrola_kapitalu.zgodne=false` bot gra 0,10 > 0,08 (B to łapie).
4. **Fallback „< 5 par → koszyk poprzedni zostaje”** trafia w sezon wyników: W9 (D0 23.10) to szczyt publikacji za Q3,
   veto EVENT (D+1…D+5) może wyciąć 20–30 % uniwersum (C §11.4). „Koszyk poprzedni” = W8 Modelu 3.0 na drugi tydzień ze
   starymi `fills` i bez D0 — gorsze niż zdefiniowany fallback mechaniczny (konstrukcja A z wetami albo B bez budżetu,
   z adnotacją w raporcie).
5. **Puls 3×/tydz.** sprzeczny z CLAUDE.md (kontrola rachunku w dni robocze; `EKSPOZYCJA_NIEPELNA`; 12.10 podwójne
   wejście wykryte tylko dzięki raportom — C sam to pisze w §8) i z własnym wyzwalaczem R3 (news bez innego nośnika).
   Codzienny Puls kontrolny ≤ 8 wywołań / 10 min (A §9.2) kosztuje tyle samo co trzy biegi i zamyka lukę 48 h.
6. Zależność od snapshotu TV co sobotę (429 → taksonomia sprzed tygodnia) i od taksonomii w ogóle (C2: 51 % par to zlepki
   sektorowe; etykiety industry się zmieniają). E prerejestrowane dopiero teraz; C2 chciało je najpierw jako cień. Koszt
   średniej do −0,5 p.p./tydz. (0,2 % kapitału przy 0,08) ≈ roczne koszty; przy alfie 0 system traci ~6 %/rok.
7. Veto cenowe 1 280 USD policzone z `START_EQUITY` 1 000 — po restarcie B′ (`START_EQUITY := kapitał`) próg trzeba
   przeliczyć (C to zaznacza; rutyna musi to robić z `/status.ustawienia.start_equity`, które dziś nie istnieje → B #10).

### 3.4 Wspólne dla wszystkich (werdykt C9, decyzja właściciela przed pon. 19.10 13:45 UTC)

Wszystkie trzy rekomendują wariant (c)/B′: Render `ALLOC_PCT` ↓, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`,
`START_EQUITY := kapitał` **razem z** commitem właściciela `equity_peak := ta sama wartość` (nadpisać klucz, nie usuwać —
walidator wymaga 15 kluczy). Operacyjnie: zmiana env restartuje serwis Rendera — sprawdzić `/status.ustawienia.alloc_pct`
przed 13:45 UTC; kill na księdze W7 (21 %) nie zależy od ALLOC. Bez resetu żadna polityka nie ratuje W8 (68–85 % w 4 tyg.).
To jest jawne uznanie kill switcha za zadziałany — każdy raport musi odtąd pokazywać obsunięcie od szczytu historycznego.

---

## 4. Co przeszczepić do C

Z B (rdzeń operacyjny, wszystko w `wykonanie` i w zmiennych Rendera, bez pól rutyn):
1. Polityka wznowienia po kill: `wykonanie.kill` zapisywany **w ścieżce kill** (dziś `return rep` przed zapisem),
   `KILL_RESUME_VERSIONS=2`, `ALLOC_RESTART`/`RESTART_VERSIONS`; test w `test_app.py`; INSTRUKCJA §12.
2. Stop asymetryczny 15 % LONG / 10 % SHORT (`STOP_LOSS_PCT_SHORT`), `STOP_REOPEN=false` przez `wykonanie.stopy`,
   `desired_book` pomija nogę ze stopem w bieżącej `version`, kotwica bez zmian. Zamiast σ-stopu A (brak odczytu pliku
   w biegu). Po ≥ 30 stopach ledger L/S rozstrzyga o `STOP_LOSS_PCT=0` dla LONG.
3. `scal_wykonanie` przenosi `soft/stopy/kill`; `zmiana_wyk` porównuje te podklucze; zapis FLAT/kill/soft **twardy**
   (ponowienie po konflikcie sha) — warunek działania progu miękkiego C.
4. `ALLOC_PCT_SAFE=0.04` (≤ `ALLOC_PCT`); `REDUCE_FALLBACK=close` (A i C to mają).
5. `/status`: `start_equity`, `soft`, `alloc_efektywny`, `stopy`, `kill`, odległość do progu miękkiego i kill w σ dziennej
   **bieżącej księgi**, `pokrycie_koszyka.zatrzymane_stopem[]` (noga po stopie ≠ `EKSPOZYCJA_NIEPELNA`).
6. Stopka każdego raportu: obsunięcie od szczytu historycznego obok cyklu; P(kill) zawsze z horyzontem i alfą
   (12/52 tyg. × alfa 0/+1); mnożnik „1 p.p. spreadu = 5·ALLOC % kapitału”.
7. Kryterium twardego wyjścia po 26 tyg.: śr. `spread_konto_pp` (od fills do rotacji) < −1,0 p.p./tydz. (t < −1) →
   papier/zamknięcie; ALLOC w górę tylko krokiem ≤ 0,02 po spełnieniu wszystkich kryteriów.

Z A (proces i pomiar, bez kodu w ścieżce zleceń):
8. `rutyny/reguly.md` z testem na uniwersum PIT (`scripts/test_regula.py` z harnessu `weryfikacja_C1.py` +
   `dane/dropped_closes.csv`), kryterium awansu (≥30 zdarzeń, |t| ≥ 2 klastrowane, znak w ≥4/5 lat, także w TOP5/TOP10),
   jawne uchylenie K10/K16/K17/sita Perf.W LONG od W9 (C6), moratorium do 26 okien; tabela „REGUŁY — kontrola” z medianą
   i listą przypadków.
9. Zestaw cieni rozszerzony o A0, ETF SMH/XLP, „E bez EVENT”, „E bez ceny”, FAKT; hash `data/ranking-<version>.json`
   w raporcie i commicie; `koszt_wykonania_pp` (tylko raport).
10. Vol-target **na papierze** (C4 staging): co sobotę w raporcie σ60_unit, ALLOC z reguły, percentyl vs losowe — bez pola
    `sizing`; dla E będzie zwykle 0,12 (sufit), co samo w sobie dokumentuje, dlaczego pole jest zbędne.
11. Puls codzienny w wersji kontrolnej (≤ 8 wywołań TV, 10 min): `/status`, pokrycie 10/10, przestrzały lotów, stan soft/stopy,
    kursy od fills i od D0, kalendarz, exclude tylko basis news z listy zamkniętej i dokumentem; wyłącznik płynności
    (sesja ≤ −5 % / VIX > 40 → NIEAKTUALNA do soboty) — zamiast 3×/tydz. z C.
12. Fallback mechaniczny dla soboty: gdy E ma < 5 par → konstrukcja A z wetami S1/K13/EVENT (lub B bez budżetu) z adnotacją
    i wpisem `konstrukcja` w `history` — nie „koszyk poprzedni”.
13. Kontrola hipotezy stopy depozytu logiem `/run` 19.10 i 26.10 (`limit_depozytowy.realizacja_celu`); poprawka mianownika
    osobno — przy gross 80 % limit nie wiąże, więc nie blokuje W9.

---

## 5. Co odrzucić (z powodem)

| element | z | powód |
|---|---|---|
| Pole `signals.json["sizing"]` + kontrola w `_sanity` od W9 | A | C4: VT najpierw ≥12 tyg. na papierze; rozszerza kontrakt rutyn z CLAUDE.md; nowa ścieżka zatrzymania handlu przy rozjeździe formuły (tolerancja 1e-4 vs `round(…,4)`); dla E martwe (0,12 w 98 % tygodni) |
| σ-stop per noga z `data/ranking-<version>.json` czytany w biegu | A | zależność sieciowa w ścieżce zleceń; C3: stop obniża kill 12-tyg. o 3,6 pkt vs sizing ~32 — najwięcej kodu za najmniejszy efekt; B daje 90 % tego samego dwiema zmiennymi env |
| Sufit `ALLOC_PCT=0.12` (gross 120 %) | A | C4 „nie 0,12”; przy hipotezie stopy 2,4× limit depozytowy = 125 % kapitału → powrót podwójnego wejścia 13:45→17:05 |
| Nakładka Model 3.0 w koszyku bota (≤1 wymiana/stronę) | A | niemierzalna (|Δ| ≥ 0,71 po 26 tyg.), utrzymuje research per spółka i budżet TV; z parami łamie budżet SOX; dopuszczalna wyłącznie jako cień FAKT na papierze |
| Big-bang 22 zmian plików do 23.10 | A | nierealne bez programisty w dni robocze; wariant przejściowy „ALLOC ręcznie z raportu” przenosi ryzyko na proces ręczny |
| Selekcja = Model 3.0 bez zmian | B | IC −0,10 (CI −0,57…+0,37), 10/16 stron nadpisanych, 36 reguł po n=1, 36 min TV — nieodtwarzalny proces jako jedyne źródło koszyka; C5/C6 wymagają zmiany |
| `ALLOC_PCT=0.06` + veto lotu > ~650 USD | B | na 0,83×START_EQUITY 7 nazw pomijanych, 14 bez możliwości redukcji, 12 z niewykonalnym połowieniem; veto wycina sprzęt AI; 0,08 + veto 1 280 USD (koszt Δ +0,03, t ≤ 1,5) jest podłogą wykonalności; 0,06 zasadne tylko przy σ koszyków Modelu 3.0 |
| Schodek FLAT −12 % jako druga maszyna stanów | B | przy 0,08 próg miękki ×0,5 wykonalny w 81/102 nazw (E: 9/10 nóg); FLAT zmienia P(kill 52 tyg.) 27,3 → 25,5 %; dodatkowa arytmetyka `version` przez granicę roku; wrócić do niego tylko, jeśli ALLOC spadnie ≤ 0,06 |
| Basis `rekom`/`short` w Pulsie | B | nieweryfikowalne z środowiska rutyn, 1/8 wpisów wykonany; lista zamknięta tylko `news` z dokumentem |
| Puls 3×/tydz. | C | CLAUDE.md: kontrola rachunku w dni robocze; R3 i wyłącznik płynności bez nośnika przez 48 h; koszt codziennej wersji kontrolnej taki sam |
| „< 5 par → koszyk poprzedni zostaje” | C | w sezonie wyników (W9!) prawdopodobne; stary koszyk Modelu 3.0 bez D0 i z nieaktualnymi `fills` — zastąpić fallbackiem mechanicznym (A z wetami) |
| Stop 10 % + reopen „do czasu kodu A” | C | kod A nie zdąży; `STOP_REOPEN=false` + 15/10 z B to ~40 linii i test |
| Interpretacja E jako „pary wewnątrz branży” i jakiekolwiek wnioski o średniej przed 52 oknami | C | C2: 51 % par to zlepki sektorowe; σ Δ(E−A) 5,21 p.p. → t=2 dla Δ 0,3 po 1 204 tyg. |
| Zmiana `KILL_LEVEL`/`KILL_TRAILING`, kotwica stopu w D0, 1/σ per noga, REDUCE per noga, moduł taktyczny 20 % | wszystkie | C3 (D0 −0,48), C4 (1/σ −19 % Sharpe, 2/10 nóg pomijanych), `ryzyko-i-sizing.md` (REDUCE martwy przy ≤0,10), n=4 bez testu; przesuwanie progu po stracie |

---

## 6. Kolejność wdrożenia pakietu „C + rdzeń B” (ocena wykonalności w czasie)

| kiedy | co | ryzyko |
|---|---|---|
| niedziela 19.10 (przed 13:45 UTC pon.) | Render: `ALLOC_PCT=0.08`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`, `REDUCE_FALLBACK=close`, `START_EQUITY := kapitał`; commit właściciela `equity_peak := kapitał`; `curl $NDX_BOT_URL/status` → `ustawienia.alloc_pct == 0.08` | zero kodu; decyzja właściciela (C9); W8 wchodzi na 0,08 — wszystkie 10 nóg wykonalne (skrypt: 53–78 USD/nogę) |
| 19–22.10 | `ranking.py`: `konstrukcja_pary_budzet`, `PAIR_POOL`, `MAX_PRICE_USD`, `E_bez_event/E_bez_ceny`; `test_ranking.py` +6; `koszyki_cienie.py` E + σ-ratio; `reguly.md` (K10 uchylone, S4 E, S5 veto cenowe); `tygodniowa.md` KROK B/A/C/D; `dzienna.md` kontrolna | offline, testowalne; największa praca to tekst rutyn i wklejenie do zadań (właściciel) |
| 19–23.10 (gałąź, testy, deploy) | `app.py`: soft (`DD_SOFT*`), `scal_wykonanie` + `zmiana_wyk`, stop per kierunek + `STOP_REOPEN`, `wykonanie.kill` + `KILL_RESUME_VERSIONS`, `/status` pola, twardy zapis; ~150 linii, ~20 testów | jeśli nie zdąży: E wchodzi 24.10 i tak (P(kill 52 tyg., alfa 0) 8,1 % zamiast 0,2 %; 12 tyg. 0,0 %); stop 10 % + reopen przez 1–2 tyg. (koszt ≈ 0, C3) |
| piątek 23.10 po deployu | Render: `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `DD_SOFT_FACTOR=0.5`, `STOP_LOSS_PCT=0.15`, `STOP_LOSS_PCT_SHORT=0.10`, `STOP_REOPEN=false`, `KILL_RESUME_VERSIONS=2` | zmiany env z domyślnymi = dzisiejsze zachowanie → odwracalne |
| sobota 24.10 (W9) | pierwszy koszyk E (fallback A z wetami, gdy < 5 par); cienie od W8; `MAX_PRICE_USD` przeliczone z `start_equity` z `/status` | sezon wyników → częstość `wybor:"min_b"`/fallbacku mierzyć |
| 12 / 26 / 52 okien | wyłącznie wykonanie i σ; σ-ratio E/A (moc 47 % po 26, 74 % po 52); `spread_konto_pp` < −1 → papier; nic po złym tygodniu | — |

---

## 7. Źródła

Projekty: `projekt-A-mechaniczny.md` (§2.2, §5, §6, §11, §12, §14), `projekt-B-przezywalnosc.md` (§2.1–2.6, §6, §7, §8, §12),
`projekt-C-konstrukcja.md` (§2, §4, §6, §8, §9, §10, §13); ich skrypty `projektA_bt/boot`, `projekt_B_sim_out.md` (A, B, C, E),
`projektC_bt_out.md`, `projektC_dod_out.md`. Werdykty: `weryfikacja-C1…C9.md` (streszczenia w zadaniu; C9 §3–4 odczytane).
Fazy 1–2: `_faza1_wyniki.txt` (dekompozycja, wykonanie-bota, moc-predykcyjna, audyt-regul, ryzyko-i-sizing, perspektywa-quant),
`_faza2_wyniki.txt` (bt_momentum, bt_odwrocenie, bt_neutralnosc). Kod: `app.py` (`_sanity` 349–389, `calc_size` 871–898,
`scal_wykonanie` 900–929, `stopy_bezpieczenstwa` 1290, `desired_book` 1315, alloc 1430, kill 1485–1503, wyrównanie 1776–1830,
zapis `fills/equity_peak/wykonanie` 1945–1971, `MARGIN_BUDGET` 135, `ALLOC_PCT_SAFE` 129, `START_EQUITY` 164),
`scripts/waliduj_signals.py` (`KLUCZE` 35, `POLA_BOTA` 38), `scripts/ranking.py` (parametry 51–63, `alloc` 356–367),
`scripts/test_app.py` (151 OK), `scripts/test_ranking.py` (17 OK). Własne: `sedzia2_soft_loty.py`, `sedzia2_soft_loty_wyniki.json`.
