# Projekt B — „Przeżywalność” (minimalny zestaw zmian: sizing, stop, schodek FLAT, wznowienie)

Projektant: proces inwestycyjny, priorytet = przeżywalność rachunku i prostota operacyjna
(mały rachunek, lot 0,1 akcji, Render, cron 13:45/17:05 UTC). Stan 18.10.2026.
Skrypt tego projektu: `projekt_B_sim.py` → `projekt_B_sim_out.md`, `projekt_B_sim_wyniki.json`
(katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`).
Źródła liczb z faz 1–3: `ryzyko-i-sizing.md`, `wykonanie-bota.md`, `bt_symulacja-wykonania.md`,
`weryfikacja-C3.md` (stop), `weryfikacja-C4.md` (sizing), `weryfikacja-C7.md` (bramka Pulsu),
`weryfikacja-C9.md` (stan na 19.10), `dekompozycja-wynikow.md`, `perspektywa-quant.md`.
Bez liczb z rachunku: tylko %, p.p. i stosunki do `START_EQUITY` / szczytu.

---

## 0. Odpowiedź w ośmiu zdaniach

1. **Jedna zmiana klasy: `ALLOC_PCT` 0,24 → 0,06** (gross 240 % → 60 %). To jedyny element, który
   zmienia los systemu; wszystko inne jest siatką awaryjną albo porządkiem procesu.
2. **Wymaganie „P(kill) < 10 %/rok przy zerowej alfie” jest przy tym rachunku nieosiągalne w sensie
   dosłownym**: przy zerowej alfie *brutto* system traci koszty (≈ 0,16 %/tydz. ≈ 8 %/rok przy 0,06),
   więc kroczący próg −25 % trafia w 24–27 % lat nawet przy 0,06 + schodku; ALLOC 0,05 (14 %) jest
   niewykonalny przy locie 0,1 akcji (9 nazw pomijanych). **Osiągalne**: ≈ 13 % przy zerowej alfie
   *netto* (po kosztach), **6–7 % przy +1 p.p./tydz. brutto**, ≈ 1 % przy +2 p.p. (tabela §5).
3. **Przy alfie +1 p.p./tydz. system zarabia**: mediana +4,9 %/rok po kosztach (0,06 + FLAT), przy
   +2 p.p. +22,7 %; 0,08 daje przy +1 p.p. prawie to samo (+4,7 %), ale P(kill 52 tyg.) 19 % zamiast 7 %.
4. **Schodek FLAT −12 % od szczytu cyklu** (zamknij wszystko, płasko do kolejnej rotacji, wznowienie
   automatyczne) nie obniża znacząco P(kill) w skali roku (25 % vs 27 % przy 0,06), ale ścina ogon
   kwartału (P(kill 12 tyg.) 0,1 % → 0,0 %; 26 tyg. 4,6 % → 3,3 %), ogranicza stratę jednego cyklu do
   ≈ −12…−14 % i na ścieżce historycznej momentum 2022–2026 obniża P(kill 52 tyg.) z 51 % do 23–39 %
   (przy 0,08). Jest tani (90–94 % sesji w rynku) — „decyzja o kształcie ogona, nie o średniej”.
5. **Wznowienie po kill przestaje być ręczną edycją pola bota**: polityka w kodzie (płasko 2 rotacje,
   szczyt := kapitał, start od ALLOC_RESTART na 4 rotacje, wpis w `wykonanie.kill`). Dziś kill = płasko
   bezterminowo (`app.py` 1497–1503), a ręczny reset ma dwa pułapkowe warianty (C9 §4).
6. **Stop: asymetryczny 15 % LONG / 10 % SHORT, bez ponownego otwarcia w tej samej wersji**, kotwica
   bez zmian (poziom brokera). Koszt stopu to zjawisko nóg LONG (−0,23 p.p./tydz. przy 24 %/nogę, C3 T2);
   przy 0,06 cały mechanizm waży ≈ −0,05 %/tydz. i nie decyduje o niczym — jest tylko siatką.
7. **Puls traci wyzwalacze cenowe (REDUCE/CLOSE basis=cena), moduł taktyczny zostaje wyłączony**:
   EV bramki ≈ 0 (C7), stop bota zawsze ją wyprzedza, REDUCE na jednym locie jest niewykonalny;
   taktyczne 20 % kapitału na jednej nodze bez dowodu (n = 4) to największe pojedyncze ryzyko po sizingu.
8. **Zero nowych pól w `signals.json`, zero zmian w walidatorze** w etapie 1: wszystko, co bot
   zapamiętuje (stopy, FLAT, kill), ląduje w podkluczach pola `wykonanie`, które już jest polem bota.
   Vol-target (pole `sizing`) to etap 2 po 12 tygodniach na papierze — specyfikacja walidatora w §9.

---

## 1. Diagnoza w liczbach, do których projekt się odnosi

| Fakt | Liczba | Źródło |
|---|---|---|
| σ tygodniowa spreadu koszyków W1–W7 | 11,3 p.p. (3,3× losowego 5/5 = 3,4 p.p.) | `perspektywa-quant.md` §A |
| σ tygodniowa spreadu mieszanki koszyków W1–W8 (bootstrap) | 7,2 p.p.; σ jedn. 17,5 %/d | `projekt_B_sim_out.md` A |
| P(kill 52 tyg.) przy ALLOC 0,24, alfa 0, bez kosztów | 99,2 % (bootstrap); 100 % (ścieżka hist.) | tu A, C4 §B |
| P(kill 12 tyg.) przy 0,24, alfa 0 | 61 % (bootstrap), 51–65 % (C4) | tu A, C4 §1 |
| Mnożnik wyniku | 1 p.p. spreadu = 5 × ALLOC % kapitału (0,24 → 1,2 %; 0,06 → 0,30 %) | `wykonanie-bota.md` §0 p.1 |
| Stop 10 % + reopen vs bez stopu (24 %/nogę) | −0,18…−0,42 p.p. kapitału/tydz.; LONG −0,23 (t −2,3), SHORT −0,05…+0,11 | C3 §5 |
| Bramka 4 %/8 % Pulsu, EV | +0,08 p.p. (n = 3442, t 0,03); P(kill 12t) 32,6 → 31,2 % | C7 |
| Po kill bot płasko bezterminowo | `app.py:1488–1503`, brak ścieżki wznowienia | C9 §3 |
| Loty: 0,1 akcji przy kapitale 0,83×START_EQUITY, ALLOC 0,06 | 7 nazw pomijanych (ASML COST LITE MELI MPWR MU SNDK), 8 na min. locie | tu E |
| Stan 18.10 | kapitał ≈ 0,76 szczytu (poduszka ≈ 1,7 %), księga W7 na rachunku (gross ≈ 218 %), W8 wchodzi 19.10 13:45 UTC | C9 §0 |

---

## 2. Projekt — składniki, parametry, dowód

Oznaczenia dowodu: **[D]** = uzasadnienie liczbowe z faz 1–3 lub z `projekt_B_sim.py`;
**[bez dowodu — decyzja]** = wybór projektowy, liczby pokazują tylko, że nie szkodzi.

### 2.1 Sizing: stały `ALLOC_PCT = 0,06` (gross 60 %) — [D]

| ALLOC | P(kill 12t) α0 | P(kill 52t) α0, bez kosztów | α0, z kosztami | α +1 p.p., z kosztami | α +2 p.p. | mediana 52t, α +1 | mediana α +2 | najgorszy tydz. W1–W7 (W7) |
|---|---|---|---|---|---|---|---|---|
| 0,24 (dziś) | 61 % | 99,2 % | 99,7 % | 98,3 % | 93,8 % | −9,5 % | +7,5 % | −19,4 % |
| 0,10 | 4,8 % | 55,5 % | 70,9 % | 41,3 % | 17,8 % | +3,6 % | +38,1 % | −11,0 % |
| 0,08 | 1,2 % | 35,3 % | 52,6 % | 22,8 % | 7,0 % | +6,0 % | +31,2 % | −8,8 % |
| **0,06** | **0,1 %** | **14,8 %** | **27,3 %** | **7,5 %** | **1,2 %** | **+5,5 %** | **+23,3 %** | **−6,7 %** |
| 0,05 (loty: 9 nazw poza) | 0,0 % | 6,3 % | 14,4 % | 2,5 % | 0,3 % | +4,7 % | +19,3 % | −5,5 % |
| VT σ60 1,5 % [0,04; 0,12] (śr. 0,076) | 0,3 % | 24,9 % | 42,3 % | 13,7 % | 2,6 % | +7,0 % | +30,4 % | — |

Źródło: `projekt_B_sim_out.md` A (mieszanka W1–W8, 20 000 ścieżek, 260 sesji, kill 0,75 × szczyt kroczący,
koszty = 6 %/rok od gross + 0,2 % × 7 nóg/tydz. × ALLOC). Zgodne z C4 §1–3 (0,08: 22–41 % / 52 tyg. α0).

Dlaczego 0,06, nie 0,08 ani 0,10:
- Przy +1 p.p./tydz. zysk niemal nie zależy od ALLOC w tym zakresie (mediana +5,5 % vs +6,0 % vs +3,6 %),
  bo koszty i alfa skalują się razem, a obcięcie przez kill rośnie z ALLOC. Różnica jest w P(kill): 7,5 % vs 23 % vs 41 %.
- Przy 0,06 koszyk W8 ma σ dzienną kapitału 0,56 % (C9 tab. 1), koszyk W4 (najbardziej zmienny) 1,5 %;
  σ tygodniowa kapitału 2,1 % (σ spreadu 7,2) do 3,4 % (σ spreadu 11,3) — kill −25 % to 7–12 σ tygodniowych.
- 0,05 byłoby lepsze statystycznie, ale przy locie 0,1 akcji i kapitale ≈ 0,83 × START_EQUITY cel ≈ 5 % START_EQUITY
  na nogę pomija 9 nazw i stawia 9 kolejnych na minimalnym locie (tabela E) — koszyk przestaje być
  równoważony. 0,06 pomija 7 nazw (wszystkie o kursie > ~650 USD) — stąd **veto lotu** w rutynie (§2.6).
- Dlaczego nie vol-target od razu: C4 §5 — przy równej średniej ekspozycji VT nie jest lepszy w 52 tyg.,
  jego przewaga to ogon 12-tyg. i maxDD; kosztem jest nowe pole `signals.json`, walidator i proces sobotni.
  Tu ogon 12-tyg. załatwia schodek FLAT. VT = etap 2 (§9).

### 2.2 Schodek FLAT: `DD_FLAT_PCT = 0,12` od szczytu CYKLU — [D dla ogona 12/26 tyg.; bez dowodu — decyzja dla progu 12 %]

Mechanika: w każdym biegu, po kontroli kill, bot liczy `dd_cyklu = kapitał / szczyt_cyklu − 1`.
`szczyt_cyklu` = maksimum kapitału od ostatniego wznowienia (pole `wykonanie.plasko.szczyt_cyklu`,
inicjowane kapitałem przy pierwszym biegu po wdrożeniu). Gdy `dd_cyklu < −DD_FLAT_PCT`: zamknij wszystkie
pozycje, zapisz `wykonanie.plasko = {od, wersja, szczyt_cyklu, kapital_pct: dd, do_wersji: version+FLAT_COOLDOWN_VERSIONS}`,
powiadom. Kolejne biegi: płasko, dopóki `version` nie zmieni się `FLAT_COOLDOWN_VERSIONS` (= 1) razy ponad
wersję wyzwolenia, czyli: FLAT w W9 → płasko do końca W9 i przez całe W10 → wznowienie z rotacją W11.
Przy wznowieniu: `szczyt_cyklu := kapitał`, ALLOC = `ALLOC_RESTART` (domyślnie = ALLOC_PCT, czyli bez
redukcji — P3b vs P3c różnią się o < 1 p.p. P(kill), tabela niżej) przez `RESTART_VERSIONS` = 4.
Kill 0,75 × szczyt WSZECHCZASOWY (`equity_peak`) zostaje bez zmian jako drugi, twardy bezpiecznik.

| polityka (koszty TAK) | α0: P(kill 12/26/52t) | α0: P(≥1 FLAT/rok), śr. FLAT | % sesji w rynku | α +1: P(kill 52t) | α +1: mediana | hist. momentum 2022–26, α0: P(kill 52t okna) | hist. α +1 |
|---|---|---|---|---|---|---|---|
| 0,06 bez schodka | 0,1 / 4,6 / 27,3 % | — | 92 % | 7,5 % | +5,5 % | 19,1 % | 0,0 % |
| **0,06 + FLAT −12 %, cooldown 1, restart 0,06** | **0,0 / 3,3 / 25,5 %** | 87 %, 1,4 | 89 % | **7,0 %** | **+4,9 %** | **14,5 %** | 0,0 % |
| 0,06 + FLAT −12 %, restart 0,05 | 0,0 / 2,5 / 23,7 % | 87 %, 1,4 | 90 % | 6,1 % | +4,8 % | 14,5 % | 0,0 % |
| 0,06 + FLAT −10 % | 0,0 / 3,3 / 24,7 % | 94 %, 1,9 | 88 % | 6,9 % | +4,8 % | 17,3 % | 3,5 % |
| 0,08 bez schodka | 1,9 / 18,1 / 52,6 % | — | 79 % | 22,8 % | +6,0 % | 51,4 % | 13,3 % |
| 0,08 + FLAT −12 %, cooldown 1 | 0,3 / 11,2 / 47,0 % | 97 %, 1,9 | 79 % | 19,1 % | +4,7 % | 39,3 % | 4,6 % |
| 0,08 + FLAT −12 %, cooldown 2 | 0,1 / 8,9 / 43,9 % | 97 %, 1,8 | 78 % | 17,5 % | +4,5 % | 23,1 % | 2,3 % |
| 0,08 + FLAT −15 % | 0,9 / 14,1 / 48,7 %* | 90 %, 1,1* | — | 20,0 %* | +5,5 %* | 39,3 % | 15,0 % |

Źródło: `projekt_B_sim_out.md` A i B (\* z biegu 2 000 ścieżek, reszta 20 000). Uwaga: „% sesji w rynku” obejmuje
ścieżki zabite (po kill płasko), stąd niskie wartości przy 0,08/0,10.

Co schodek robi, a czego nie: w roku przy zerowej alfie trafia średnio 1,4 razy (ok. 2 tygodnie płasko na
epizod); **nie** ratuje przed killem w skali roku (25,5 vs 27,3 %), bo po wznowieniu szczyt cyklu resetuje się,
a szczyt wszechczasowy nie — kolejne −12 % od −12,5 % to −23,5 %; **ścina** ogon kwartału/półrocza
i zamienia „losowy moment zamknięcia przez kill” na „przewidywalny koniec cyklu po −12 %”. Próg 12 % =
ok. 4–6 σ tygodniowych kapitału przy 0,06 (3,5 σ przy koszyku typu W4); 10 % daje 1,9 FLAT/rok (za często),
15 % traci ochronę 26-tyg. (14 % vs 11 % przy 0,08). **Wybór 12 % jest decyzją**, nie wynikiem optymalizacji.

Dlaczego „płasko”, a nie „ALLOC × 0,5”: przy locie 0,1 akcji połowienie pozycji 0,1 jest niewykonalne
(`plan_redukcji` → „niewykonalna”, `REDUCE_FALLBACK=keep`), a halving per noga robiłby koszyk netto-short
(C4 §6). Zamknięcie wszystkiego jest jedyną wykonalną redukcją na tej skali rachunku.

### 2.3 Wznowienie po kill: `KILL_RESUME_VERSIONS = 2` — [bez dowodu — decyzja; mechanika z C9]

Dziś: po kill każdy bieg kończy się na `equity < prog_kill` (bez pozycji kapitał nie wraca), a ręczne
wznowienie ma pułapki: sam reset `equity_peak` daje poduszkę 11 % (podłoga `max(szczyt, START_EQUITY)`),
samo `START_EQUITY` — 0; usunięcie klucza wywraca walidator rutyn (C9 §4). Projekt: po kill bot zapisuje
`wykonanie.kill = {data, wersja, szczyt, do_wersji: version + KILL_RESUME_VERSIONS, licznik}`; po dwu zmianach
`version` (dwie soboty) pierwszy bieg wznawia handel: `equity_peak := kapitał` (pole bota — bot ma do niego
prawo), `szczyt_cyklu := kapitał`, ALLOC = `ALLOC_RESTART` przez `RESTART_VERSIONS`. Właściciel może
zatrzymać wznowienie `status=NIEAKTUALNA` (pole rutyn) albo `KILL_RESUME_VERSIONS=0` (= dzisiejsze zachowanie).

Skutek w liczbach (A2, koszty TAK): przy 0,06 + FLAT, α0: P(≥ 1 kill/rok) 25 %, śr. 0,26 killa/rok,
P(kapitał < 0,75 start po roku) **10 %**, P(< 0,60) 0,3 %; przy α +1: 7 %, 0,07/rok, 1,5 %, 0,0 %.
Dla porównania 0,24 dziś: 3,8 killa/rok, P(< 0,60) 50 %. Kill przestaje być stanem terminalnym, a jego
częstość zostaje jawną metryką rocznej walidacji (§8).

Zastrzeżenie uczciwości (C9 §5): automatyczny reset szczytu po kill to przesunięcie progu po stracie; różnica
wobec dzisiejszego „ręcznie, kiedyś” jest w jawności, cooldownie i zmniejszonym starcie, nie w wartości
oczekiwanej. Raporty muszą dalej pokazywać obsunięcie od szczytu HISTORYCZNEGO (§7), żeby reset nie ukrywał straty.

### 2.4 Stop: `STOP_LOSS_PCT = 0,15` (LONG), `STOP_LOSS_PCT_SHORT = 0,10`, `STOP_REOPEN = false` — [D dla asymetrii i progu; decyzja dla blokady reopen]

- Próg 15 % na LONG: C3 T4 — stop 15 % kosztuje −0,19 p.p./tydz. (t −2,3) wobec −0,28 dla 10 %, przy tej
  samej częstości kill (39,5 vs 37,7 %); koszt stopu to nogi LONG (po −10 % długa noga momentum odbija +1,9 %,
  t 3,0 — C3 T6). Przy 0,06 koszt ≈ −0,05 %/tydz. — stop nie jest już narzędziem ryzyka (strata 15 % na nodze
  = 0,9 % kapitału; 20 % = 1,2 %), tylko siatką na luki.
- 10 % na SHORT zostaje: na nogach SHORT stop jest neutralny (−0,05…+0,11, C3 T2), a tam leży ryzyko
  squeeze'u (AXON +22,8 % w jednym oknie); W8 ma shorty AXON/DASH/APP o σ60 3–4,6 %/d.
- Bez reopen w tej samej `version`: EV reopenu ≈ +0,10 brutto − drugi spread ≈ 0 (C3 §5) — **decyzja o
  spójności**, nie o wyniku: reopen kasował cenę odniesienia, rozjeżdżał bramkę Pulsu z wykonaniem (audyt reguł)
  i w W7 kosztował 2,3–3,3 % kapitału (anegdota). Mechanika: po stopie bot zapisuje
  `wykonanie.stopy[ticker] = {data, wersja, poziom, kierunek}`; `desired_book` pomija nogę z wpisem o bieżącej
  `version`; rotacja (zmiana `version`) czyści wpisy. Pole `wykonanie` jest polem bota — walidator rutyn nie
  wymaga zmian (`POLA_BOTA` identyczne z bazą), `_sanity` nie sprawdza `wykonanie`.
- Kotwica: **bez zmian** (`p["wejscie"]` przed `fills.cena`). Rekomendacja „kotwica = cena tezy” z fazy 1
  nie przeżyła weryfikacji: na panelu 234 okien kotwica D0 kosztuje −0,48 vs −0,28 (C3 T3); W7 to anegdota.
  Efekt uboczny niskiego ALLOC: przy gross 60 % limit depozytowy (0,60/0,20 = 300 %) nie wiąże nawet przy
  zawyżonej 2,4× stopie depozytu w dniu rotacji (125 % > 60 %), więc znika „wejście na pół + zamknij/otwórz
  o 17:05” z 12.10 i kotwica nie przestawia się tego samego dnia bez zmian w `sync()`.

### 2.5 Puls i taktyczne — [D]

- **Wyzwalacze cenowe (basis=cena, 4 %/8 %, druga sesja, blokada sektorowa) usunięte z protokołu**: EV ≈ 0
  (C7: +0,08 p.p., t 0,03; P(kill 12t) 32,6 → 31,2 %), stop bota zawsze wyprzedza (2 sesje + bieg 12:30),
  REDUCE na jednym locie niewykonalny. Zostają: basis `news`/`rekom`/`short` z listy zamkniętej (R3 w
  `rutyny/reguly.md`) i wyłącznik P2 (`status=NIEAKTUALNA`). Puls staje się raportem kontrolnym: pokrycie,
  zgodność wykonania, odległość do FLAT i KILL w σ dziennej **bieżącej księgi**, stopy z `wykonanie.stopy`.
- **`TACTICAL_ENABLED=false`** (lub `TACTICAL_ALLOC_PCT=0`): 20 % kapitału na jednej nodze o σ 4–6 %/d
  = σ ≈ 1 %/d kapitału bez dowodu (n = 4: AKAM −3,3, APOG/PENG +0,3, ERIC +4,0 p.p.; `dekompozycja-wynikow.md`
  pytania). Przy ALLOC 0,06 taktyczna 0,20 byłaby 3,3× większa od nogi koszykowej — niespójne z projektem.
  Powrót: wyłącznie jako hipoteza H2 z `reguly.md` po teście przekrojowym i z `TACTICAL_ALLOC_PCT = ALLOC_PCT`.

### 2.6 Rutyna tygodniowa — tylko to, czego wymaga sizing — [D dla veta lotu i σ; selekcja poza zakresem B]

Projekt B nie przeprojektowuje selekcji (zakres projektów A/C). Trzy obowiązkowe dodatki w KROKU B4/C:
1. **Veto lotu (S4)**: noga, dla której `0,1 × kurs > 1,3 × ALLOC_PCT × konto.kapital` (z `/status`),
   wypada z koszyka na rzecz następnej w rankingu; raport wypisuje ją w tabeli „REGUŁY — kontrola” jako
   „pominięta: lot” z wartością lotu. Przy 0,06 i kapitale ≈ 0,83 × START_EQUITY to kurs > ~650 USD
   (dziś ASML, COST, LITE, MELI, MPWR, MU, SNDK; tabela E). Bez veta `calc_size` i tak pominie nogę
   (> 1,6 × cel) albo otworzy ją z przestrzałem do 1,6× — koszyk nierówny, σ wyżej. **Koszt**: wypadają nazwy
   sprzętu AI, w których siedziała historyczna alfa momentum (`bt_momentum.md`) — jawnie zapisany w rejestrze.
2. **Diagnostyka ryzyka ex ante** (już liczy `scripts/ranking.py`: σ60_unit, percentyl vs 1 000 losowych,
   ρ60 par, N_eff, b_SOX/b_DEF): w raporcie obok koszyka zdanie „σ tygodniowa kapitału przy ALLOC 0,06 ≈ X %;
   FLAT −12 % = Y σ; kill = Z σ”. Bez bramki — pomiar do decyzji o VT po 12 tygodniach (§8).
3. **Metryka główna = `spread_konto_pp`** (od fills do rotacji) z mnożnikiem 5 × ALLOC jawnie w stopce
   („1 p.p. = 0,30 % kapitału”) i `koszt_wykonania_pp = wynik rachunku % − 5·ALLOC·spread_konto_pp`
   (`wykonanie-bota.md` rekomendacja). `spread_pp` od D0 zostaje jako jakość prognozy.

---

## 3. Skutki na W1–W7 (ścieżka faktyczna, dzienne zwroty D0+1 → następne D0, koszty TAK, bez stopów)

| polityka | W1 | W2 | W3 | W4 (11 ses.) | W5 | W6 | W7 | **W1–W7 złożone** | maxDD | FLAT | kill |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,24 (dziś) | −5,1 % | +6,7 % | +1,0 % | +15,6 % | +6,9 % | −7,3 % | −19,4 % | **−5,6 %** | **−25,3 %** | — | **TAK (16.10)** |
| 0,10 | −2,1 | +2,8 | +0,4 | +6,5 | +2,9 | −3,1 | −10,9 | −4,3 % | −13,7 % | — | nie |
| 0,08 | −1,7 | +2,2 | +0,4 | +5,3 | +2,3 | −2,4 | −8,8 | −3,4 % | −11,1 % | — | nie |
| 0,08 + FLAT −10 % | j.w. | | | | | | FLAT w W7 | −3,4 % | −11,1 % | W7 | nie |
| **0,06 (+ FLAT −12 %)** | −1,3 | +1,7 | +0,3 | +3,9 | +1,7 | −1,8 | **−6,7 %** | **−2,5 %** | **−8,4 %** | brak | nie |

Źródło: `projekt_B_sim_out.md` C. Ścieżka 0,24 odtwarza rachunek (kill 16.10; rachunek −23,7 % od szczytu).
Przy 0,06 ten sam ciąg prognoz kosztuje W6+W7 −8,4 % zamiast −25 %, a W4 daje +3,9 % zamiast +15,6 %:
reguła tnie symetrycznie (zgodnie z `ryzyko-i-sizing.md` §0 p.8). FLAT −12 % nie zadziałałby w W1–W7
(maxDD −8,4 %); −10 % przy 0,08 zadziałałby 16.10, czyli ostatniego dnia (po fakcie — zero korzyści,
zero szkody). Lekcja z C4 §4 stoi: W7 to 5 ujemnych dni × 1,2 σ przy σ zgodnej z prognozą — chroni
wyłącznie ekspozycja ustalona przed tygodniem.

---

## 4. Skutki na backteście (momentum 6M 2022–2026, 234 tyg., wejście D0+1, koszty TAK, okna kroczące)

| polityka | α in-sample (+1,1 p.p.): P(kill 12t / 52t) | α0: 12t / 52t | α +1: 12t / 52t | α0: P(≥1 FLAT 52t), śr. | α0: mediana 52t | α +1: mediana 52t | pełna ścieżka α in-sample: kapitał z kill (100), maxDD |
|---|---|---|---|---|---|---|---|
| 0,24 | 49 / 100 % | 55 / 100 % | 49 / 100 % | — | −22 % | −15 % | 85, −27,8 % |
| 0,10 | 4,7 / 19 % | 6,1 / 65 % | 4,7 / 20 % | — | −22 % | +7,4 % | 77, −28,7 % |
| 0,08 | 3,8 / 6,4 % | 3,8 / 51 % | 3,8 / 13 % | — | −20 % | +6,5 % | 79, −25,3 % |
| 0,08 + FLAT −12 % (cd 1) | 1,9 / 5,8 % | 3,8 / 39 % | 0,9 / 4,6 % | 100 %, 1,6 | −17 % | +5,6 % | 79, −25,8 % |
| 0,08 + FLAT −12 % (cd 2) | 0,0 / 2,3 % | 0,0 / 23 % | 0,0 / 2,3 % | 100 %, 1,6 | −11 % | +5,6 % | 79, −25,2 % |
| **0,06** | 0,0 / 0,0 % | 0,9 / 19 % | 0,0 / 0,0 % | — | −10 % | +5,2 % | **139**, −23,8 % |
| **0,06 + FLAT −12 % (cd 1)** | **0,0 / 0,0 %** | **0,0 / 14,5 %** | **0,0 / 0,0 %** | 100 %, 1,5 | −11,5 % | +2,8 % | 78, −25,7 % |
| 0,05 | 0,0 / 0,0 % | 0,0 / 1,2 % | 0,0 / 0,0 % | — | −8 % | +4,5 % | 133, −20,1 % |

Źródło: `projekt_B_sim_out.md` B. Uwaga o „pełnej ścieżce”: kill liczony od szczytu wszechczasowego bez
wznowienia — 0,06 bez schodka przeżywa cały 2022 (139), 0,06 + FLAT trafia kill raz (78) i zostaje płasko do
końca symulacji; z polityką wznowienia (§2.3) to porównanie przestaje mieć sens, dlatego miarodajne są
okna kroczące. Survivorship bias zawyża średnią (+1,1 p.p.), nie σ (C4 §10) — kolumny α0 są właściwym testem
przeżywalności, kolumny α +1 — testem „czy zarabia”.

---

## 5. Oczekiwane metryki projektu (ALLOC 0,06 + FLAT −12 %, stop 15/10 bez reopen, bez taktycznych)

| metryka | wartość | źródło |
|---|---|---|
| μ spreadu (prognoza) | nieznane; CI W1–W7 −2…+3 p.p./tydz.; realistyczne ex ante 0…+0,5 p.p. netto (C1: PIT +0,09…+0,54) | `dekompozycja`, C1 |
| σ tygodniowa spreadu | 7,2 p.p. (mieszanka W1–W8), 11,3 p.p. (W1–W7 zrealizowane), 5,7–7,4 p.p. (momentum / pary) | tu A, pq_quant, bt_neutralnosc |
| 1 p.p. spreadu → kapitał | 0,30 % (5 × 0,06) | tożsamość |
| σ tygodniowa kapitału | 2,1 % (σ 7,2) … 3,4 % (σ 11,3); σ dzienna 0,56 % (W8) … 1,5 % (W4) | tu D, C9 |
| Koszty modelowe | 0,155 %/tydz. ≈ 8 %/rok (finansowanie 3,6 % + rotacja 4,4 %); próg opłacalności **+0,52 p.p. spreadu/tydz.** | tu D; stawki = założenia (`wykonanie-bota.md` §0 p.9) |
| P(kill 12 / 26 / 52 tyg.) przy α0 brutto, z kosztami | 0,0 % / 3,3 % / 25,5 % | tu A |
| P(kill 52 tyg.) przy α0 netto (bez kosztów) | 13,8 % | tu A |
| P(kill 52 tyg.) przy α +1 / +2 p.p. brutto | 7,0 % / 1,1 % | tu A |
| P(≥ 1 FLAT w roku), śr. liczba | 87 %, 1,4 (α0); 66 %, 0,9 (α +1) | tu A |
| Mediana wyniku 52 tyg.: α0 / +1 / +2 | −10,0 % / **+4,9 %** / +22,7 %; p5: −25 / −21 / −6 % | tu A |
| P(wynik roku < 0): α0 / +1 / +2 | 75 % / 38 % / 10 % | tu A |
| Po kill z wznowieniem: P(kapitał < 0,75 po roku) α0 / +1 | 10 % / 1,5 % | tu A2 |
| Kiedy test alfy rozstrzyga | przy σ_w kapitału 2,1 % i μ 0,30 %/tydz. (= +1 p.p.) t = 2 po ≈ 200 tyg.; po 26 tyg. t ≈ 0,7 — **26 tygodni rozstrzyga o wariancji, kosztach i wykonaniu, nie o średniej** | pq_quant §G |

Wniosek dla właściciela: wymaganie „< 10 %/rok przy zerowej alfie” jest spełnione tylko w sensie *netto*
(≈ 13–14 %) albo przy alfie ≥ +1 p.p. brutto (7 %); przy alfie zerowej brutto system z kosztami traci
mediano −10 %/rok i kill w ciągu roku jest w 1 na 4 lata — to **właściwe** zachowanie bezpiecznika wobec
procesu, który nie zarabia. Każda polityka o niższym P(kill) przy α0 (0,05, 0,04) jest na tym rachunku
niewykonalna lotami.

---

## 6. Zmiany w kodzie (`app.py`) — specyfikacja

### 6.1 Zmienne środowiskowe (panel Render)

| zmienna | dziś | projekt | właściciel | uwagi |
|---|---|---|---|---|
| `ALLOC_PCT` | 0,24 | **0,06** | panel Render | zmiana klasy; bez kodu |
| `TACTICAL_ENABLED` | true | **false** | panel Render | alternatywnie `TACTICAL_ALLOC_PCT=0` |
| `STOP_LOSS_PCT` | 0,10 | **0,15** (LONG) | panel Render | do czasu wdrożenia 6.2 obowiązuje dla obu stron — zmienić dopiero RAZEM z kodem |
| `STOP_LOSS_PCT_SHORT` | — | **0,10** (nowa; domyślnie = STOP_LOSS_PCT) | kod + panel | |
| `STOP_REOPEN` | — (zachowanie: reopen) | **false** (nowa; domyślnie true = zachowanie dziś) | kod + panel | |
| `DD_FLAT_PCT` | — | **0,12** (nowa; 0 = wyłączony) | kod + panel | |
| `FLAT_COOLDOWN_VERSIONS` | — | **1** (nowa) | kod + panel | |
| `KILL_RESUME_VERSIONS` | — | **2** (nowa; 0 = dzisiejsze „płasko bezterminowo”) | kod + panel | |
| `ALLOC_RESTART` | — | **0** = ALLOC_PCT (nowa; opcjonalnie 0,05) | kod + panel | |
| `RESTART_VERSIONS` | — | **4** (nowa) | kod | |
| `START_EQUITY` | 1000 (domyślne) | := kapitał w dniu restartu (jednorazowo, §7) | panel Render | wymagane razem z `equity_peak` |
| `ALLOC_PCT_SAFE` | 0,10 | **0,04** | panel Render | nie może być > ALLOC_PCT (dziś „awaryjna” byłaby większa od normalnej) |
| `REACT_GATE`, `REACT_*`, `REDUCE_*`, `KILL_LEVEL`, `KILL_TRAILING`, `MARGIN_*`, `REBALANCE_*`, `MAX_EXPOSURE_STEP`, `HEDGE_EPIC` | — | **bez zmian** | — | przy gross 60 % limit depozytowy i MAX_EXPOSURE_STEP nie wiążą |

### 6.2 Logika (kolejność w `sync()`)

1. **Kill switch (1488–1503)**: po `do_close` dla wszystkich pozycji dopisać zapis `wykonanie.kill`
   (`data`, `wersja`, `szczyt`, `do_wersji`, `licznik += 1`) i `save_signals` (dziś `return rep` wykonuje się
   przed zapisem — kill nie zostawia śladu w pliku). Przed sprawdzeniem `equity < prog_kill`: jeżeli
   `wykonanie.kill` istnieje i `version` ≥ `do_wersji` (porównanie numerów tygodni) → wznowienie: `sig["equity_peak"] = equity`,
   `wykonanie.plasko = {szczyt_cyklu: equity, restart_do_wersji: version + RESTART_VERSIONS}`, usuń `wykonanie.kill`,
   zapisz, powiadom „WZNOWIENIE po kill”. Jeżeli `wykonanie.kill` istnieje i wersja za młoda → `return rep`
   z akcją „KILL: płasko do wersji X” (bez ponownego zamykania — pozycji nie ma).
2. **Schodek FLAT (nowy blok po kill, przed `NIEAKTUALNA`)**: `szczyt_cyklu = max(wykonanie.plasko.szczyt_cyklu or equity, equity)`;
   jeżeli `wykonanie.plasko.do_wersji` istnieje i `version < do_wersji` → `do_close` wszystkiego, `return rep`
   („FLAT: płasko do wersji X”). Jeżeli `version ≥ do_wersji` (wznowienie) → `szczyt_cyklu := equity`,
   `restart_do_wersji := version + RESTART_VERSIONS`, usuń `do_wersji`. Jeżeli `DD_FLAT_PCT > 0` i
   `equity < (1 − DD_FLAT_PCT) × szczyt_cyklu` → `do_close` wszystkiego, zapis `wykonanie.plasko = {od, wersja, szczyt_cyklu, dd, do_wersji: version + FLAT_COOLDOWN_VERSIONS}`,
   powiadomienie, `return rep`. Zapis `szczyt_cyklu` przy zmianie > 0,5 % (jak `equity_peak`).
3. **ALLOC**: `alloc = ALLOC_PCT if zgodne else ALLOC_PCT_SAFE`; jeżeli `wykonanie.plasko.restart_do_wersji` > `version`
   i `ALLOC_RESTART > 0` → `alloc = min(alloc, ALLOC_RESTART)`. `rep["alloc_pct"]` i `rep["tryb"]` („normalny” / „restart” / „flat” / „kill”).
4. **Stopy** (`stopy_bezpieczenstwa`): próg = `STOP_LOSS_PCT_SHORT` dla `direction == "SELL"`, inaczej
   `STOP_LOSS_PCT`; po trafieniu: `wykonanie.stopy[ticker] = {data, wersja, poziom: ruch, kierunek, cena_stopu: mid}`.
   `desired_book(sig, …)`: gdy `not STOP_REOPEN`, pomiń ticker z wpisem `wykonanie.stopy[ticker].wersja == version`
   (do `skipped` „zatrzymana stopem w tej wersji”). `scal_wykonanie`: przenosić podklucze `stopy` (tylko wpisy
   o bieżącej `version`), `plasko`, `kill` — dziś funkcja buduje wynik od zera z `reakcje`/`taktyczne`/`aktualizacja`
   i zgubiłaby nowe klucze.
5. **`/status`**: dodać `plasko`, `kill`, `stopy` (z `wykonanie`), `szczyt_cyklu`, `odleglosc_flat_pct`,
   `odleglosc_kill_pct`, oraz w `ustawienia`: `stop_loss_pct_short`, `stop_reopen`, `dd_flat_pct`,
   `flat_cooldown_versions`, `kill_resume_versions`, `alloc_restart`, `tactical_enabled`, `start_equity`
   (C9: `START_EQUITY` nie było w `/status`). W `pokrycie_koszyka`: lista `zatrzymane_stopem[]` —
   noga ze stopem w tej wersji NIE jest „brakująca”.
6. **Powiadomienia**: FLAT, WZNOWIENIE, KILL z numerem cyklu; w stopce `/run` mnożnik „1 p.p. = {5·alloc} % kapitału”.

Rozmiar: ok. 120–150 linii zmian; żadnych zmian w `_sanity` (nie sprawdza `wykonanie`), żadnych w `waliduj_signals.py`
(`wykonanie` ∈ `POLA_BOTA`, musi być identyczne z bazą — rutyny go nie dotykają).

### 6.3 Testy (`scripts/test_app.py`, bez sieci, `FakeCap`)

- kill → `wykonanie.kill` zapisany; kolejny bieg z tą samą `version` → płasko, bez zleceń; bieg z `version + 2` →
  `equity_peak == equity`, `alloc == ALLOC_RESTART`, pozycje otwierane; `KILL_RESUME_VERSIONS=0` → stare zachowanie.
- FLAT: equity 0,879 × `szczyt_cyklu` → wszystko zamknięte, `plasko.do_wersji == version + 1`; `version + 1` → płasko;
  `version + 2` → handel, `szczyt_cyklu == equity`; `DD_FLAT_PCT=0` → brak zmian wobec dziś.
- Stopy: SELL −12 % od wejścia przy `STOP_LOSS_PCT_SHORT=0.10` → stop; BUY −12 % przy `STOP_LOSS_PCT=0.15` → brak;
  po stopie `desired_book` bez nogi przy `STOP_REOPEN=false`, z nogą przy `true`; po zmianie `version` wpis znika.
- `scal_wykonanie` zachowuje `stopy`/`plasko`/`kill`.
- `test_app.py` dziś: 151 OK — po zmianie oczekiwane ≈ 165.

---

## 7. Migracja z obecnego stanu — co zrobić PRZED poniedziałkiem 19.10, 13:45 UTC

Stan (C9 §0): kapitał ≈ 0,76 szczytu (poduszka ≈ 1,7 %), 9 pozycji W7 na rachunku (gross ≈ 218 %) + ERIC;
pierwsze sprawdzenie kill w poniedziałek 13:45 dotyczy **księgi W7** (luka pt→pon: ~21 %, przedział 15–29 %
szans na kill niezależnie od `ALLOC_PCT`), potem rotacja na W8.

| wariant | co zrobić | P(kill) 19–23.10 | ocena |
|---|---|---|---|
| (0) nic | — | 58 % w 5 ses., 69 % w 10 (0,24, z kosztem rotacji) | losowy moment zamknięcia; odrzucić |
| (½) tylko `ALLOC_PCT=0,06` | panel Render | ≈ 21 % luka W7 + 11 %/24 % (5/10 ses. na W8 przy 0,06) ≈ 30 %/40 % | półśrodek: poduszka ≈ 1,7 % zostaje, każdy AKTUALNA wraca do tego stanu |
| **(B′) świadomy restart = pierwsze zastosowanie polityki wznowienia** | sobota/niedziela: Render `ALLOC_PCT=0.06`, `TACTICAL_ENABLED=false`, `ALLOC_PCT_SAFE=0.04`, **`START_EQUITY := bieżący kapitał`** (restart serwisu); **commit właściciela `equity_peak := bieżący kapitał`** (nadpisać, NIE usuwać klucza — walidator wymaga 15 kluczy; C9 §4) przed 13:45 UTC; `STOP_LOSS_PCT` zostaje 0,10 do wdrożenia kodu | poduszka 33 %: **0 % w 5/10/20 ses., 15 % w 60 ses. przy 0,24; 0 % przy 0,06** (C9 tab. §4, opcja c); luka W7 bez znaczenia (σ_d księgi W7 ≈ 3 %) | **rekomendowany**; warunek: w raportach stale „obsunięcie od szczytu historycznego” (−23,7 % od 6.10) obok cyklu — reset nie może ukryć straty |
| (A) płasko do zmiany metody | właściciel ustawia `status=NIEAKTUALNA` (pole rutyn) w sobotę; bot 13:45 zamyka W7 (po sprawdzeniu kill — 21 % zostaje); kod z §6 wdrażany w tygodniu; start z W9 (26.10) pod polityką | 21 % (luka W7), potem 0 | spójny z faktem, że alfa nie jest dowiedziona (C9 §5); koszt: tydzień bez rynku, W8 nie wejdzie; wymaga, by rutyna sobotnia 24.10 ustawiła AKTUALNA |

Uzasadnienie wyboru B′ (bez dowodu — decyzja; liczby z C9 §5): przy zerowej alfie E[kapitał] czekania i
restartu są równe (0,765 vs 0,761 szczytu) — decyzja jest o wariancji i o tym, kto wybiera moment zamknięcia.
Projekt B zmienia proces (gross 240 → 60 %, stop, Puls, taktyczne), więc stary próg mierzył inny proces;
reset z jednoczesną zmianą sizingu to jedno zdarzenie w dzienniku, nie „przesuwanie progu, żeby grać dalej tym
samym”. Wariant A jest równie uczciwy i tańszy w ryzyku poniedziałkowym; wybór należy do właściciela.

Kolejność techniczna B′ (sobota 18.10 wieczorem lub niedziela):
1. Render → Environment: `ALLOC_PCT=0.06`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`, `START_EQUITY=<kapitał z /status>`;
   deploy (restart serwisu); `curl $NDX_BOT_URL/status` → `ustawienia.alloc_pct == 0.06`.
2. Commit właściciela w `signals.json`: `equity_peak` := ta sama wartość (wiadomość commita bez kwoty, np.
   „bot/właściciel: reset szczytu kapitału — restart pod projektem B (gross 60 %)”); `python3 -I scripts/waliduj_signals.py --diff HEAD~1 --rutyna sobota`
   **zgłosi** „zmienione pole pisane przez bota: equity_peak” — to oczekiwane dla commita właściciela
   (walidator chroni rutyny, nie właściciela); następna rutyna waliduje `--diff HEAD`, więc przechodzi.
3. `tactical` w `signals.json` jest już `[]` po rotacji W8; ERIC zostanie zamknięty przez bota 13:45 jako
   „poza aktualnymi sygnałami” (jest w `fills` → `managed`).
4. Poniedziałek 13:45 UTC: rotacja W7 → W8 na 0,06 (10 nóg × 6 % = 60 % gross; W8: 0,1 akcji 5–53 USD —
   wszystkie nogi wykonalne; MSFT na minimalnym locie z przestrzałem 1,06×). 17:05: wyrównanie.
5. W tygodniu 19–23.10: kod §6 na gałęzi, testy, deploy; `STOP_LOSS_PCT=0.15`, `STOP_LOSS_PCT_SHORT=0.10`,
   `STOP_REOPEN=false`, `DD_FLAT_PCT=0.12`, `FLAT_COOLDOWN_VERSIONS=1`, `KILL_RESUME_VERSIONS=2` w panelu.
   Pierwszy bieg po deployu inicjuje `wykonanie.plasko.szczyt_cyklu = kapitał`.
6. Sobota 24.10: rutyna tygodniowa wg zmienionej `tygodniowa.md` (veto lotu, σ ex ante, metryka od fills);
   Puls od 19.10 wg zmienionej `dzienna.md` (bez wyzwalaczy cenowych) — wklejenie do claude.ai/code/routines
   PO commicie plików w `rutyny/` (zasada CLAUDE.md).

---

## 8. Plan walidacji (prerejestrowany 18.10.2026)

**Koszyki cienie** (R14 w `rutyny/reguly.md`, `scripts/koszyki_cienie.py`, `data/koszyki-cienie.jsonl`):
A momentum, B pary, C neutralna, D budżet czynnikowy, FAKTYCZNY — bez zmian. Dodatkowo dla projektu B
rozliczane co sobotę w raporcie (nie w `history`):

| metryka | definicja | kryterium po 12 tyg. (W9–W20, ok. 9.01.2027) | kryterium po 26 tyg. (ok. 17.04.2027) |
|---|---|---|---|
| `spread_konto_pp` | od fills do rotacji, śr. i σ narastająco, t | tylko raport | kontynuacja, jeśli śr. > −0,5 p.p./tydz.; **śr. < −1,0 p.p. (t < −1) → zamknąć system albo przejść na papier** |
| σ tyg. kapitału zrealizowana vs ex ante | z /status (kapitał dzień po dniu) vs 5·ALLOC·σ60_unit·√5 | **≤ 1,5× ex ante** w ≥ 10/12 tyg.; inaczej błąd modelu σ — raport problemu | j.w.; corr(log σ ex ante, log σ realizowanej) > 0,5 w 26 tyg. = **warunek wejścia VT (etap 2)** |
| `koszt_wykonania_pp` | wynik rachunku % − 5·ALLOC·spread_konto_pp | **≤ 0,3 %/tydz.** średnio; powyżej → audyt spreadów/wyrównań | ≤ 0,25 %/tydz. |
| liczba FLAT, kill | z `wykonanie.plasko/kill` | **0 kill; ≤ 1 FLAT**; 2 FLAT w 12 tyg. → przegląd (oczekiwane 1,4/rok przy α0) | ≤ 2 FLAT, 0 kill (P ≈ 3 % przy α0 — kill w 26 tyg. = sygnał, że α < 0 albo σ niedoszacowana) |
| ledger stopów | zwrot nogi od stopu do rotacji, LONG/SHORT osobno (C3 §6) | tylko zbieranie | po ≥ 30 stopach: jeżeli LONG odbija (t > 2) → `STOP_LOSS_PCT=0`; jeżeli SHORT nie → 0,10 zostaje |
| veto lotu — koszt | zwrot pominiętych vs zamienników (jak „KOSZT REGUŁ”) | raport | po 26 tyg.: jeżeli koszt > 1 p.p./tydz. (t > 1,5) → decyzja o kapitale (próg wykonalności 0,06 bez veta ≈ 1 600 USD = 1,6 × START_EQUITY) |
| P(kill) raportowane | zawsze z horyzontem i alfą (C4 §9 p.4) | w stopce raportu: „P(kill 12/52 tyg.) przy α0: 0,0 %/25 %; przy +1: 0,0 %/7 %” | — |

**Czego 12 i 26 tygodni NIE rozstrzyga**: średniej (potrzeba ≈ 200 tyg. dla +1 p.p. przy σ 7 p.p.). Decyzje
o zmianie ALLOC w górę dozwolone wyłącznie: po 26 tyg. bez kill, ≤ 2 FLAT, σ zrealizowana ≤ 1,2× ex ante,
koszt ≤ 0,25 %/tydz., śr. `spread_konto_pp` > +0,5 p.p. — i tylko krokiem 0,06 → 0,08 (INSTRUKCJA: „krok
≤ 0,02 na 26 tygodni, nigdy ×2” — lekcja z 3.10, `wykonanie-bota.md`).

**Moratorium reguł** (reguly.md pkt 5): bez zmian; projekt B nie dodaje reguł koszykowych poza vetem lotu
(S4, konstrukcyjne, nie prognostyczne) i nie zmienia progów prerejestrowanych.

---

## 9. Etap 2 (po 12 tyg., warunkowo): vol-target przez pole `signals.json["sizing"]` — jak zmienić walidator i `_sanity`

Tylko jeżeli po 12 tygodniach corr(σ ex ante, σ realizowana) > 0,5 i rozpiętość σ60_unit koszyków > 2×
(W1–W8: 9,3–26,4 %, czyli 2,8×). Reguła: `ALLOC_t = clip(0,015 / σ60_unit, 0,04, 0,08)` (cap 0,08, nie 0,12 —
C4 §5: VT z capem 0,12 siedział na capie 38 % tygodni i w 2024-08 przegrał ze stałym 0,10).

- **`signals.json`**: nowy klucz top-level `sizing = {"sigma60_unit": float>0, "alloc_pct": 0,04–0,08, "d0": "RRRR-MM-DD" (= d0.date), "zrodlo": "ranking.py"}`
  pisany WYŁĄCZNIE przez rutynę sobotnią.
- **`scripts/waliduj_signals.py`**: `KLUCZE |= {"sizing"}`; `DOZWOLONE["sobota"] |= {"sizing"}` (puls — nie);
  w `spojnosc()`: typy i zakresy jak wyżej, `sizing.d0 == d0.date`, `|alloc_pct − clip(0.015/sigma60_unit, 0.04, 0.08)| ≤ 1e-4`
  (formuła zamrożona w walidatorze = brak dyskrecji); w `porownaj()`: `"sizing"` zmienione bez zmiany `version` → problem.
- **`app.py::_sanity`**: jeżeli `"sizing" in sig`: wymagaj dict z `alloc_pct` ∈ [0,04; 0,08] i `d0` == `sig["d0"]["date"]`,
  inaczej `ValueError` (handel wstrzymany — jak dla złego koszyka). `sync()`: `alloc = min(alloc, sig["sizing"]["alloc_pct"])`
  tylko gdy `sizing.d0 == d0.date` (stare `sizing` ignorowane z wpisem w `pominiete`). Bot nigdy nie zwiększa
  ALLOC ponad `ALLOC_PCT` z panelu — pole może tylko obniżać.
- **`rutyny/tygodniowa.md` KROK D(a)**: dopisać `sizing` do listy pól; wartość z `scripts/ranking.py`
  (`alloc_pct_proponowany`, już liczony; zmienić `ALLOC_MAX` 0,12 → 0,08). **CLAUDE.md**: tabela pól.
- Test: `test_app.py` — `_sanity` odrzuca `sizing` poza zakresem / ze starym `d0`; `waliduj_signals` odrzuca `sizing` od pulsu.

---

## 10. Pełna lista zmian w plikach (z właścicielem)

| # | plik / miejsce | zmiana | właściciel | kiedy |
|---|---|---|---|---|
| 1 | panel Render | `ALLOC_PCT=0.06`, `ALLOC_PCT_SAFE=0.04`, `TACTICAL_ENABLED=false`, `START_EQUITY=<kapitał>` | właściciel (Render/decyzja) | przed pon. 19.10 13:45 UTC |
| 2 | `signals.json` → `equity_peak` | := bieżący kapitał (commit właściciela, klucz zostaje) | właściciel (Render/decyzja) | przed pon. 13:45 UTC |
| 3 | `app.py` KONFIGURACJA | nowe zmienne `STOP_LOSS_PCT_SHORT`, `STOP_REOPEN`, `DD_FLAT_PCT`, `FLAT_COOLDOWN_VERSIONS`, `KILL_RESUME_VERSIONS`, `ALLOC_RESTART`, `RESTART_VERSIONS`; komentarz o decyzji 18.10 (gross 60 %) | kod app.py | tydzień 19–23.10 |
| 4 | `app.py::sync()` 1488–1503 | kill: zapis `wykonanie.kill`, wznowienie po `KILL_RESUME_VERSIONS` (reset `equity_peak`, `szczyt_cyklu`, restart ALLOC) | kod app.py | j.w. |
| 5 | `app.py::sync()` nowy blok po kill | schodek FLAT od `szczyt_cyklu`, `wykonanie.plasko`, płasko do `do_wersji`, wznowienie | kod app.py | j.w. |
| 6 | `app.py::sync()` 1430 | `alloc = min(alloc, ALLOC_RESTART)` w oknie restartu; `rep["tryb"]` | kod app.py | j.w. |
| 7 | `app.py::stopy_bezpieczenstwa` 1290 | próg per kierunek; zapis `wykonanie.stopy[ticker]` | kod app.py | j.w. |
| 8 | `app.py::desired_book` 1315 | pomijanie nóg z `wykonanie.stopy` o bieżącej `version` gdy `STOP_REOPEN=false` | kod app.py | j.w. |
| 9 | `app.py::scal_wykonanie` 900 | przenoszenie podkluczy `stopy` (bieżąca wersja), `plasko`, `kill` | kod app.py | j.w. |
| 10 | `app.py::status_ep` 2125 i `pokrycie_koszyka` 1131 | `plasko`, `kill`, `stopy`, `szczyt_cyklu`, odległości do FLAT/KILL, nowe `ustawienia`, `zatrzymane_stopem[]` | kod app.py | j.w. |
| 11 | `app.py` powiadomienia (`notify`) | FLAT / WZNOWIENIE / KILL z numerem cyklu; mnożnik 5·ALLOC w stopce | kod app.py | j.w. |
| 12 | `scripts/test_app.py` | testy z §6.3 (kill-resume, FLAT, stop per kierunek, brak reopen, scal_wykonanie) | kod app.py | j.w. |
| 13 | panel Render (po deployu) | `STOP_LOSS_PCT=0.15`, `STOP_LOSS_PCT_SHORT=0.10`, `STOP_REOPEN=false`, `DD_FLAT_PCT=0.12`, `FLAT_COOLDOWN_VERSIONS=1`, `KILL_RESUME_VERSIONS=2` | właściciel (Render/decyzja) | po zielonych testach |
| 14 | `rutyny/dzienna.md` KROK 2 | usunąć „TRZY WARUNKI DLA WYZWALACZY CZYSTO CENOWYCH”, blokadę sektorową i `basis=cena` z protokołu; zostawić `news`/`rekom`/`short`/`rezim` z listą zamkniętą; MODUŁ TAKTYCZNY → „ZAWIESZONY (TACTICAL_ENABLED=false) — tactical zawsze []” | rutyna | commit przed wklejeniem, 19.10 |
| 15 | `rutyny/dzienna.md` KROK 1b / KROK 3 | KONTROLA RACHUNKU: czytać `wykonanie.stopy/plasko/kill` z `/status`; noga zatrzymana stopem ≠ brakująca (bez `EKSPOZYCJA_NIEPELNA`); podać odległość do FLAT i KILL w σ dziennej bieżącej księgi; obsunięcie od szczytu HISTORYCZNEGO i od szczytu cyklu; mnożnik „1 p.p. = 0,30 % kapitału” | rutyna | j.w. |
| 16 | `rutyny/dzienna.md` KROK 3 SEKCJA KONTROLA BRAMKI | zastąpić „KONTROLA STOPÓW” (wpisy `wykonanie.stopy`: ticker, kierunek, poziom, zwrot od stopu do dziś) | rutyna | j.w. |
| 17 | `rutyny/tygodniowa.md` KROK A | metryka główna `spread_konto_pp` (fills → rotacja), `koszt_wykonania_pp`, ledger stopów LONG/SHORT; `spread_pp` od D0 jako jakość prognozy | rutyna | przed sobotą 24.10 |
| 18 | `rutyny/tygodniowa.md` B4 | veto lotu S4 (`0,1 × kurs > 1,3 × alloc_pct × konto.kapital` → następna w rankingu; tabela „pominięta: lot”); usunąć p (R6 uchylone) | rutyna | j.w. |
| 19 | `rutyny/tygodniowa.md` KROK C | sekcja RYZYKO EX ANTE (σ60_unit, σ tyg. kapitału przy ALLOC z `/status`, FLAT i KILL w σ, percentyl vs losowe, N_eff, b_SOX/b_DEF z `ranking.py`); stopka: „pozycja koszykowa = ALLOC_PCT z /status (od 19.10.2026: 6 %; taktyczne wyłączone)”; P(kill) zawsze z horyzontem i alfą | rutyna | j.w. |
| 20 | `rutyny/tygodniowa.md` KROK E | wiadomość końcowa: `spread_konto_pp`, tryb bota (normalny/restart/FLAT), liczba stopów | rutyna | j.w. |
| 21 | `rutyny/reguly.md` | S2 → „etap 2 (warunkowo po 12 tyg., cap 0,08)”; S3 → „próg 15 % LONG / 10 % SHORT, bez reopen, kotwica = poziom brokera (C3 T3)”; dopisać S4 veto lotu, S5 schodek FLAT −12 %, S6 polityka wznowienia; R1'/R2 pozostają UCHYLONE | rutyna | j.w. |
| 22 | `CLAUDE.md` | „Co wolno”: `wykonanie` ma podklucze `reakcje`, `taktyczne`, `stopy`, `plasko`, `kill` (bot); tabela `/status`: nowe pola; „Kod EKSPOZYCJA_NIEPELNA”: noga w `zatrzymane_stopem` i tryb FLAT/KILL nie są awarią; akapit o `equity_peak`: reset wyłącznie przez politykę bota albo jednorazowy commit właściciela z datą | rutyna (dokument) | z PR kodu |
| 23 | `INSTRUKCJA.md` §2 tabela | nowe zmienne z domyślnymi; `ALLOC_PCT` 0,06 z datą i uzasadnieniem (P(kill)); zasada „ALLOC krokiem ≤ 0,02 na 26 tyg., nigdy ×2”; §12 „Decyzja 18.10.2026: gross 60 %, schodek FLAT, wznowienie po kill, procedura restartu 19.10” (bez kwot) | kod app.py (dokument) | z PR kodu |
| 24 | `scripts/ranking.py` | `ALLOC_MAX` 0,12 → 0,08; opcjonalny `--alloc` i `--kapital` do tabeli veta lotu (wartość 0,1 akcji vs 1,3 × cel) | rutyna / kod | przed 24.10 |
| 25 | `scripts/waliduj_signals.py`, `app.py::_sanity` | **etap 1: bez zmian**; etap 2 wg §9 (`sizing`) | walidator | po 12 tyg., warunkowo |
| 26 | claude.ai/code/routines | wklejenie zmienionych `dzienna.md` (19.10) i `tygodniowa.md` (do 24.10) — po commitach | właściciel (Render/decyzja) | 19.10 / 24.10 |

---

## 11. Czego projekt B świadomie NIE robi (i dlaczego)

- Nie zmienia `KILL_LEVEL`/`KILL_TRAILING` (próg po stracie nie rusza się; reset tylko przez politykę z §2.3).
- Nie wdraża vol-targetu ani inverse-vol per noga w etapie 1 (C4 §5–6: brak przewagi w 52 tyg. przy równej
  średniej; per noga −19 % Sharpe'a i niewykonalne lotami).
- Nie przestawia kotwicy stopu na cenę tezy (C3 T3: −0,48 vs −0,28).
- Nie zmienia harmonogramu cron (opóźnienie wejścia +0,10 p.p./tydz., t 0,24 — `bt_symulacja-wykonania.md`).
- Nie dotyka selekcji (Model 3.0 / ranking.py / konstrukcje) poza vetem lotu — to zakres projektów A/C;
  sizing 0,06 działa dla dowolnej selekcji o σ spreadu 5–11 p.p.
- Nie dodaje reguł koszykowych ani nie zmienia progów prerejestrowanych (moratorium `reguly.md` pkt 5).
- Nie obiecuje P(kill) < 10 %/rok przy zerowej alfie brutto: tego na tym rachunku nie daje żadna wykonalna
  polityka; daje 25 % (brutto α0), 13 % (netto α0), 7 % (+1 p.p.), 1 % (+2 p.p.).

## 12. Główne ryzyka projektu

1. **Alfa ≤ 0 brutto**: system traci ≈ 8–10 %/rok kosztów przy medianie −10 %; po 26 tygodniach nie da się
   tego odróżnić od pecha (t ≈ 0,7) — kryterium „śr. < −1 p.p./tydz.” z §8 jest jedynym twardym wyjściem.
2. **Veto lotu wycina sprzęt AI** (MU, LITE, SNDK, MPWR, ASML, COST, MELI) — tam siedziała historyczna
   alfa momentum (`bt_momentum.md`); koszt mierzony co tydzień, próg wykonalności bez veta ≈ 1,6 × START_EQUITY.
3. **Szok jednodniowy > 12 %** przy 0,06 wymaga ruchu jednostkowego −200 % (σ 17,5 %/d → 11 σ) — praktycznie
   tylko luka wielu nóg naraz; FLAT i kill mogą wtedy zadziałać tego samego dnia (kolejność: kill pierwszy).
4. **Operacyjne**: `scal_wykonanie` gubiący nowe podklucze (test obowiązkowy); konflikt sha przy zapisie
   `wykonanie.kill`/`plasko` w biegu z zapisem pulsu (jak dziś dla `fills`: zapis to udogodnienie — ale FLAT
   bez zapisu oznacza brak pamięci płasko w kolejnym biegu → **zapis FLAT/kill musi być twardy**, z ponowieniem
   po odczycie świeżego sha).
5. **Reset szczytu 19.10 jako precedens**: bez zdania o szczycie historycznym w każdym raporcie reset staje
   się mechanizmem ukrywania strat; stąd obowiązkowa linia w KROKU 1b/C.
6. Koszty CFD są założeniem (6 %/rok, 0,1 %/noga); faktyczne stawki Capital.com nieznane — `koszt_wykonania_pp`
   z §8 jest jedyną miarą niewymagającą cennika.
