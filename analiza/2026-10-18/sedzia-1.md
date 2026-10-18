# Sędzia 1 — perspektywa: dowody i statystyka (czy każdy element ma poparcie w danych; czy projekt nie jest dopasowany do W7)

Sesja 18.10.2026. Oceniam trzy projekty (A mechaniczny, B przeżywalność, C konstrukcja E) w świetle werdyktów weryfikacji C1–C9 i pełnych notatek projektów. Skala 1–10 w czterech kryteriach; total = suma. Wszystkie liczby pochodzą z notatek i wyjść skryptów w tym katalogu (ścieżki w nawiasach); bez liczb z rachunku.

Pliki, które przeczytałem w całości: `projekt-A-mechaniczny.md`, `projekt-B-przezywalnosc.md`, `projekt-C-konstrukcja.md`, `weryfikacja-C1…C9.md`, `_faza1_wyniki.txt`, `_faza2_wyniki.txt`; wyjścia skryptów projektów: `projektA_bt_out.md`, `projektA_boot_out.md`, `projekt_B_sim_out.md`, `projektC_bt_out.md`, `projektC_dod_out.md`.

---

## 0. Werdykt w trzech zdaniach

1. **Najlepszy: Projekt C** (konstrukcja E: 5 par w grupie TV z budżetem |b_SOX net| ≤ 0,5, stałe ALLOC 0,08). Jest jedynym projektem, którego rdzeń opiera się na **jedynym odpornym wyniku statystycznym całej analizy** — redukcji σ przez parowanie (σ-ratio 0,669, CI95 0,58–0,78, F p < 10⁻⁴, powtarzalna w 5/5 definicjach grupy i 11/11 klastrowaniach PIT z C2) — a nie na średniej momentum (C1: zero w CI) ani na wyborze poziomu ALLOC dla selekcji, której nie da się przetestować (B).
2. **Projekt B jest najlepiej uzasadnionym pojedynczym ruchem** (obniżka ALLOC = C4, jedyna zmiana klasy) i najłatwiejszy do wdrożenia, ale zostawia selekcję Modelu 3.0 — czyli zachowuje maszynę, która produkuje reguły po n = 1 (17/36) i koszyki o σ 3,3× losowego (χ²(6) = 66); jego własna symulacja pokazuje, że schodek FLAT prawie nie zmienia P(kill) w roku (27,3 → 25,5 %).
3. **Projekt A ma najlepszy proces** (ranking.py jako jedyne źródło, rejestr reguł z testem na PIT, cienie, metryki prerejestrowane), ale jego koszyk to czyste momentum z b_SOX +0,9–1,1 (dokładnie czynnik W6/W7), a jego sizing (vol-target z sufitem 0,12) jest wg własnych tabel GORSZY niż stałe 0,08 — cała redukcja P(kill) pochodzi z progu miękkiego. Do tego 22 zmiany w plikach, nowe pole `signals.json` i nakładka uznaniowa niemierzalna przez 52–144 tygodni.

---

## 1. Oceny

| projekt | evidence | implementability | risk-adjusted return | overfitting robustness | **total** |
|---|---|---|---|---|---|
| A — mechaniczny (A + vt+soft + σ-stop + nakładka) | 6 | 4 | 5 | 5 | **20** |
| B — przeżywalność (0,06 + FLAT + wznowienie + stop 15/10) | 7 | 8 | 4 | 6 | **25** |
| C — konstrukcja E (pary + budżet SOX, 0,08 + soft) | 7 | 6 | 7 | 6 | **26** |

### 1.1 Evidence (czy każdy element ma liczbę, która go niesie)

**A = 6.** Dobrze poparte: konieczność skryptu zamiast scoringu (C5: IC Wyniku −0,10, CI −0,57…+0,37; 10/16 stron nadpisanych; 25 % wag mierzalnych), uchylenie K10 (C6: 0/148 wariantów za, 24 przeciw), usunięcie bramki 4/8 (C7), redukcja reżimu do P2 (C8), zawieszenie taktycznych (n = 4). Słabo poparte lub przeciwnie do dowodu:
- Momentum 6M skip 5 jako **teza koszyka**: PIT +0,60 brutto (t 1,37), netto +0,33 (t 0,74); CI obejmuje zero; wariant jest szczytem siatki 9×5 skorelowanych prób (C1 §e). A to przyznaje, ale i tak czyni z tego koszyk bota. C1 Implikacja 1 mówi wprost: „jeśli czynnik zostaje — ALLOC ≤ 12 %/nogę i rola tie-breakera, nie tezy koszyka”.
- Vol-target jako sizing: C4 §5 — przewaga VT nad stałym ALLOC jest nieistotna (90 % CI Sharpe [−0,12; +0,33]), a VT z capem 0,12 w spokojnych latach siedział na capie (38 % tygodni) i przegrał w 2024-08. **Własne tabele A to potwierdzają** (`projektA_boot_out.md`): vt (śr. ALLOC 0,104) P(kill 52, α0) 53,8 % vs stałe 0,08 → 33,3 %; `projektC_bt_out.md` dla A/PIT: vt 48,3 % vs fix 0,08 28,6 %. Dopiero próg miękki sprowadza to do 16,6–18,6 %. **Sizing A działa więc przez soft, nie przez VT** — a VT kosztuje nowe pole, walidator, `_sanity`.
- Nakładka Modelu 3.0 (≤ 1 wymiana/stronę): σ Δ 1,80 p.p./tydz. → wykrycie +0,3/+0,5 p.p. wymaga 144/52 tygodni; C5: warstwa uznaniowa dodaje +0,06 IC (t 1,2) — zero dowodu, mechanizm niemierzalny w horyzoncie projektu. Progi N5 są „decyzją, nie dowodem” (A przyznaje).
- σ-stop `clip(2·σ60·√5, 8 %, 20 %)`: PIT Δ −0,002 (t −0,06), 58 stopów/233 tyg. — neutralny, czyli bez dowodu korzyści; różni się od stałego 10 % (−0,037, t −0,30) o wielkość szumu. Jedyny argument to „nie szkodzi”.

**B = 7.** Rdzeń (ALLOC 0,24 → 0,06) stoi na C4, najmocniej zweryfikowanym twierdzeniu (bootstrap blokowy 5–60, GARCH, ścieżka historyczna — wszystkie zgodne). B uczciwie pokazuje, że wymaganie „P(kill) < 10 %/rok przy α0” jest nieosiągalne (25–27 % przy 0,06 z kosztami; 0,05 niewykonalne lotami). Stop asymetryczny 15/10 ma kierunkowe poparcie C3 (koszt stopu z nóg LONG −0,23, t −2,3; SHORT −0,05…+0,11). Brak reopen — zgodny z C3/wykonanie-bota. Co bez dowodu (B sam to oznacza): próg FLAT 12 % (decyzja), cooldown, ALLOC_RESTART; FLAT prawie nie zmienia P(kill 52) (`projekt_B_sim_out.md` A: 27,3 → 25,5 %). Co obniża ocenę: B **nie dotyka selekcji**, więc jego model σ (mieszanka W1–W8, σ jedn. 17,5 %/d, σ tyg. 7,2 p.p.) zakłada koszyki Modelu 3.0, których zrealizowana σ wyniosła 11,3 p.p. (pq_quant §A) — B podaje obie liczby, ale rekomendacja 0,06 jest kalibrowana do 7,2. Poziom 0,06 (nie 0,08/0,10 z C4) wymusza veto lotu wycinające MU/LITE/SNDK/MPWR/ASML/COST/MELI — koszt tego veta nie został policzony przekrojowo (B przyznaje: „mierzony co tydzień”).

**C = 7.** Rdzeń stoi na C2 i na własnym teście `projektC_bt.py` (209 okien, PIT): σ-ratio E/A 0,669 [0,58; 0,78], najgorszy tydzień −12,7 vs −23,9, b_SOX zrealizowane +0,31 vs +1,08, SOX−NDX < −3: −1,91 vs −5,14 (n 19). Redukcja σ jest odporna na definicję grupy (0,59–0,76 w 5 definicjach) i na skład (dziś 0,735). Co C uczciwie przyznaje i co obniża ocenę: średnia E jest nierozstrzygalna (Δ −0,21, CI −0,92…+0,50; C2 na klastrach PIT: mediana −0,86), definicja grupy base jest **jedyną** z Δ ≈ 0 w C2 i najlepszą w teście wrażliwości C (efekt wyboru definicji — C2 T4), taksonomia TV W8 jest narzucona wstecz nawet w „PIT” (korekta dotyczy członkostwa, nie etykiet branżowych), a dla 28 usuniętych spółek przypisana ręcznie. Mechanizm budżetu (8 par → 56 podzbiorów → cap 0,5) został zaprojektowany i przetestowany na tych samych danych; wybór cap 0,5 nad 1,0 to wybór z dwóch (mały zbiór, ale jednak). Veto cenowe > 1 280 USD: Δ +0,03…+0,04 (t ≤ 1,5), udział 2,1 % nóg — „≈ 0” poparte.

### 1.2 Implementability

**A = 4.** 22 zmiany w plikach (§11), w tym: nowe pole top-level `sizing` (KLUCZE walidatora, DOZWOLONE, `spojnosc`, `porownaj`), `_sanity` w `app.py` z blokadą handlu przy złym `sizing`, `sync()` z trzema warstwami alokacji, `stopy_bezpieczenstwa` czytające `data/ranking-<version>.json` z repo przez `gh_get_file` w każdym biegu (nowa zależność bota od pliku danych i od GitHuba w czasie biegu), kill-resume, `scripts/test_regula.py`, `koszyki_cienie.py` z 7 cieniami, trzy rutyny. Termin: kod do czwartku 23.10, rutyny piątek, pierwszy bieg sobota 24.10 — A sam przewiduje wariant przejściowy „ALLOC ręcznie z raportu”, który przenosi ryzyko na proces ręczny (ryzyko-i-sizing.md). Ryzyko §14.7: pole `sizing` bez zmiany `_sanity` = bot ignoruje sizing.

**B = 8.** Zero zmian w `signals.json` i walidatorze (cała pamięć w `wykonanie`, które jest polem bota), 7 zmiennych, ~120–150 linii, ~14 testów. Zmiana klasy (ALLOC) to jeden wpis w Renderze bez kodu. Punkty ryzyka, które B sam nazywa: `scal_wykonanie` gubi nowe podklucze (test obowiązkowy), zapis FLAT/kill musi być twardy (konflikt sha z zapisem pulsu), kolejność kill→FLAT. Veto lotu wymaga odczytu `konto.kapital` z `/status` w rutynie — to liczba z rachunku, która nie może trafić do repo (B tego nie zaznacza wprost; wynik veta w raporcie HTML jest w porządku, w `history` nie).

**C = 6.** `ranking.py` już ma `grupy`, `konstrukcja_pary`, `konstrukcja_budzet` — potrzebna jedna nowa funkcja (56 podzbiorów), dwa parametry, 6 testów; `app.py` tylko próg miękki (ten sam mechanizm co w A); walidator bez zmian merytorycznych (opcjonalne pola `history`). Jeśli kod `app.py` nie zdąży, E i tak wchodzi 24.10 (ranking.py niezależny) — to realna przewaga nad A. Co obniża: cotygodniowa zależność od snapshotu TV `run-screener` (429 → taksonomia sprzed tygodnia), od kalendarza wyników (veto EVENT może wyciąć grupy w sezonie wyników → `wybor:"min_b"` albo < 5 par → poprzedni koszyk zostaje), przepisanie obu rutyn. Harmonogram Pulsu 3×/tydz. to decyzja bez dowodu — nie wpływa na ocenę.

### 1.3 Risk-adjusted return (oczekiwanie ex ante przy α ≈ 0 z szeroką niepewnością, jak nakazuje C5 pkt 3)

Wspólny mianownik: przy α = 0 każdy projekt traci koszty (A −0,12 %/tydz., B −0,155 %, C −0,115 %); in-sample PIT A i C dają +0,04 %/tydz. Różnice są w ogonie i w P(kill), nie w średniej.

| | σ tyg. kapitału | P(kill 12 / 52 tyg., α0, koszty) | maxDD 52 tyg. med./p95 | tydzień typu W7 (SOX−NDX < −3) | koszty/tydz. |
|---|---|---|---|---|---|
| A (vt+soft, PIT) | 1,6–1,9 % | 0 % / 16,6 % (`projektA_boot`); 0,2 % / 18,6 % (`projektC_bt`) | −19 / −30 % | A −3,61…−5,14 p.p. → przy 0,08: −1,4…−2,1 % kap.; A sam pisze „−8…−10 %” dla tygodnia −21…−24 p.p. | 0,15–0,2 % |
| B (0,06 + FLAT, mieszanka W1–W8) | 2,1–3,4 % | 0,0 % / 25,5 % | p95 DD −25,9 % | W7 faktyczne przy 0,06: −6,7 % | 0,155 % |
| C (E, 0,08 + soft, PIT) | 1,84 % | 0,0 % / 0,2 % (soft) · 8,1 % (bez soft) | −14 / −25 % | E −1,91 p.p. → −0,8 % kap. | 0,115 % |

**A = 5.** Sharpe PIT 0,62–0,65 ≈ E, ale ogon 2× cięższy (najgorszy −23,9) i ekspozycja czynnikowa nienaruszona (b_SOX zreal. +0,91…+1,08). A broni tego liczbą „D − A = −0,54 (t −2,36)” — słusznie odrzuca D (budżet przez wymiany nóg), ale **nie testuje E** (budżet przez wybór par), który C pokazuje jako tańszy (Δ −0,21 za σ-ratio 0,67 vs D: −0,36…−0,54 za 0,80–0,84). Przy równej σ kapitału A musiałoby grać ALLOC ≈ 0,055 (6,9/4,6 × 0,08), co przy locie 0,1 akcji pomija 5+ nazw — A nie może zejść do ryzyka E bez utraty wykonalności.

**B = 4.** Sizing nie zmienia Sharpe'a (C4: 0,10 = 0,12 = 0,24 ≈ 0,95), więc ocena zależy od selekcji — Model 3.0 (IC ≈ 0, σ 3,3× losowego, 74 % wariancji = czynnik SOX). Przy α0 mediana roku −10 %, P(wynik < 0) 75 %, kill w 1 na 4 lata (B podaje). Próg opłacalności +0,52 p.p. spreadu/tydz. wobec oczekiwania 0…+0,5 netto. Jedyna rzecz, która chroni, to niska dźwignia.

**C = 7.** Sharpe PIT 0,60 (A 0,62), dziś 1,17 (A 0,99); p5 −7,0 vs −10,4; maxDD 52 tyg. p95 −25 % vs −28…−30 %; P(kill 52, α0) 8,1 % bez progu miękkiego vs A 28,6 % przy tym samym 0,08. Koszty najniższe (gross 80 %, obrót 2,8 nogi). Zastrzeżenie: w reżimie półprzewodników E oddaje 2/3 wyniku A (2026 PIT +0,81 vs +2,52) — to cena ubezpieczenia, nie błąd, ale przez wiele tygodni E będzie wyglądać gorzej od cienia A, co jest realnym ryzykiem behawioralnym (pokusa powrotu do A po „straconym” rajdzie).

### 1.4 Overfitting robustness (czy projekt nie jest dopasowany do W7 ani do próby)

**A = 5.** Proces (rejestr na PIT, moratorium, metryki prerejestrowane, „nigdy po złym tygodniu”) jest najlepszy z trzech — to zasługa. Ale: (i) wariant momentum skip 5 TOP5/BOTTOM5 piątek stoi na szczycie siatki skorelowanych prób (C1 §b, §e: mediana siatki PIT +0,3 brutto vs +0,71 wybranego); (ii) nakładka to furtka dla uznania z progami decyzyjnymi, których nie da się zwalidować przez rok; (iii) parametry VT (0,015, clip 0,04–0,12) i σ-stopu (2,0, 8–20 %) wybrane na tej samej próbie, σ-stop z 58 zadziałań; (iv) próg miękki −10 %/−5 % i cooldown 2/4 tyg. bez testu wrażliwości. W7-fit: A nie reaguje konstrukcją na W7 (nie neutralizuje SOX) — to paradoksalnie czyni go odpornym na zarzut „dopasowania do W7”, ale pozostawia ryzyko, które W7 ujawniło, a które backtest potwierdza na 19–23 tygodniach SOX−NDX < −3.

**B = 6.** Najmniej dopasowanych parametrów (0,06; 12 %; 15/10) i B oznacza, które są decyzją. FLAT −12 % nie zadziałałby w W1–W7 (maxDD −8,4 %), więc nie jest dopasowany do W7. Ale system pod B zachowuje selekcję uznaniową z 36 regułami (17 po n = 1), chronioną tylko moratorium w `reguly.md` — czyli zachowuje mechanizm, który generuje overfitting co tydzień; audyt-regul pokazuje, że reguły koszykowe K4–K17 istniały tylko w raportach HTML, poza rutyną. Moratorium bez skryptu jest obietnicą, nie bezpiecznikiem.

**C = 6.** Zamrożone parametry z datą, metryki i progi prerejestrowane (12/26/52 okien), jedyna dopuszczona korekta (PAIR_POOL 10 po 12 oknach) nazwana z góry — dobrze. Słabości: definicja grupy base jest ex post najlepsza z 5 dla średniej w obu składach (C2 T4: „efekt wyboru definicji”; sąsiednie definicje −0,12…−0,56 przy tej samej redukcji σ); taksonomia z jednego snapshotu narzucona wstecz (C2 T3: klastry liczone na żywo dają σ-ratio 0,47–0,71, ale Δ mediana −0,86 — wniosek o σ przeżywa, o średniej nie); budżet SOX prerejestrowany dopiero teraz. Czy to dopasowanie do W7? Nie: redukcja σ i b_SOX mierzona jest na 209–233 oknach, a ładunek SOX koszyków momentum rósł od 2023 (bt_momentum: −0,75 w 2022 → 2,03 w 2026). W7 jest ilustracją, nie źródłem parametrów.

---

## 2. Dlaczego C, a nie B (najbliższy rywal)

B i C nie są sprzeczne: B to sizing + siatka, C to konstrukcja + sizing. Gdyby trzeba było wybrać **jeden** rdzeń, decyduje pytanie: co dane rozstrzygają? Rozstrzygają **wariancję** (test F o σ-ratio: moc 47 % po 26 tyg., 74 % po 52) i **nie rozstrzygają średniej** (t = 2 dla Δ 0,3 po 1 204 tyg.). Projekt, którego wartość leży w wariancji (C), jest więc falsyfikowalny w horyzoncie życia rachunku; projekt, którego wartość leży w „alfa Modelu 3.0 przy niskiej dźwigni” (B), nie jest — po 26 tygodniach t ≈ 0,7 przy +1 p.p. (B przyznaje). Dodatkowo C przy ALLOC 0,08 ma P(kill 52, α0) 8,1 % **bez** progu miękkiego, B przy 0,06 — 27,3 %; C osiąga to konstrukcją, nie poziomem dźwigni, więc nie płaci kosztu veta lotu (7 nazw) ani niewykonalności przy 0,06.

Dlaczego C, a nie A: ten sam skrypt, ta sama mechanizacja, ten sam próg miękki — ale A zostawia b_SOX ≈ 1 i dokłada VT (n.s.), nowe pole `signals.json`, σ-stop z zależnością bota od pliku w repo i nakładkę niemierzalną. C robi mniej i opiera się na mocniejszym wyniku.

---

## 3. Elementy do przeszczepienia do C (z uzasadnieniem liczbowym)

Z **B**:
1. **Stop stały asymetryczny 15 % LONG / 10 % SHORT, bez reopen** zamiast σ-stopu z A (C odsyła do A §6). C3: koszt stopu z nóg LONG (−0,23, t −2,3), 15 % −0,19 vs 10 % −0,28; SHORT neutralny (tam squeeze: AXON +22,8 %). Wymaga tylko `STOP_LOSS_PCT_SHORT` i `STOP_REOPEN=false` — bez czytania `ranking-<version>.json` przez bota. Na PIT A: 15 % −0,085 (t −1,53), σ-stop −0,002 (t −0,06), 10 % −0,037 — różnice są szumem, więc rozstrzyga prostota.
2. **Polityka wznowienia po kill w kodzie** (`wykonanie.kill`, 2 rotacje płasko, szczyt := kapitał, start od ALLOC_RESTART) — C4 pkt 5 i C9 pkt 2: obowiązkowa przed zmianą sizingu; C jej nie specyfikuje (odsyła do A §5.2). Wersja B jest kompletna (testy, `/status`, `scal_wykonanie`).
3. **Obowiązkowa linia o obsunięciu od szczytu HISTORYCZNEGO** w każdym raporcie obok szczytu po resecie (B §7) — bez tego reset `equity_peak` 19.10 staje się ukrywaniem straty (C9 §5).
4. **`START_EQUITY` w `/status.ustawienia`** i `P(kill)` zawsze z horyzontem i alfą (C4 pkt 4) — C ma to drugie, pierwszego nie.
5. **Hipoteza B o zniknięciu podwójnego wejścia 13:45/17:05 przy gross ≤ 80 %** (limit depozytowy przestaje wiązać) — potwierdzić logiem `/run` 19.10 i 26.10 (A §12.3 ma ten sam punkt kontrolny).

Z **A**:
6. **`scripts/test_regula.py` — harness PIT w repo** (closes_5y + dropped_closes + tabele JOIN/LEAVE z `weryfikacja_C1.py`) i kryterium awansu reguły z testem w TOP5/TOP10, nie tylko w kwintylu (C6: znak K10 odwraca się między kwintylem −0,16 a TOP5 +1,68). C ma rejestr, nie ma harnessu.
7. **Statusy w `reguly.md` po tej analizie** (A §8 pkt 3): S2/S3 z poprawionymi liczbami (stare „37–70 %”/„20 % Sharpe'a” obalone przez C4 jako pomylenie wariantów), H5 jako cień, K10 uchylona po obu stronach **z wyjątkiem** sita SHORT r10 ≤ −12/−20 % (C6 zastrzeżenie 2 — osobny KANDYDAT), K13 OBOWIĄZUJĄCA, kalibracja kary event po n = 1 uchylona.
8. **Cień ETF SMH/XLP i „A bez EVENT”** w `koszyki_cienie.py` (A §10.1): pierwszy mierzy, czy cokolwiek bije czysty czynnik (bt_rezim: ETF +0,70, σ 4,76, maxDD 38), drugi koszt veta K2' bez dowodu.
9. **Sufit `ALLOC_PCT` w Renderze jako zabezpieczenie niezależne od kodu** — w C: 0,08 (nie 0,12).
10. **Tabela „REGUŁY — kontrola” z medianą i listą przypadków obok średniej** (C6 §7: jedna zamiana LITE W5 odwróciła znak średniej z 9 obserwacji).

---

## 4. Elementy do odrzucenia (z powodem)

| element | z | powód |
|---|---|---|
| Vol-target całego koszyka jako sizing bota (pole `signals.json["sizing"]`, formuła w walidatorze i `_sanity`) | A | C4 §5: przewaga nad stałym ALLOC n.s. (Sharpe 90 % CI [−0,12; +0,33]); VT z capem 0,12 ma w spokojnych latach WYŻSZĄ ekspozycję niż 0,10 (38–57 % tygodni na capie) — własne tabele A: vt 48–54 % P(kill 52) vs fix 0,08 29–33 %; dla E martwy (0,12 w 98 % tygodni). C4 pkt 2: najpierw ≥ 12 tyg. na papierze. Zostawić jako kolumnę diagnostyczną w raporcie. |
| Sufit `ALLOC_PCT = 0,12` | A | C4 §9 pkt 1: „nie 0,12 (8–16 % / 65–76 % w 52 t.)”. Dla E sufit 0,08 (C §9 to przyznaje). |
| Nakładka Modelu 3.0 na żywo (≤ 1 wymiana/stronę) | A | Niemierzalna: σ Δ 1,8 p.p./tydz. → 52–144 tyg. do t = 2; C5: warstwa uznaniowa +0,06 IC (t 1,2); progi N5 „decyzja, nie dowód”. Zamiast tego: wyłącznie na papierze jako cień FAKT_hipotetyczny przez 26 okien; wejście na żywo tylko po t ≥ 2 na cieniu i na PIT (własne kryterium A §10.1 dla cieni). |
| σ-stop czytany przez bota z `data/ranking-<version>.json` (`gh_get_file` w biegu) | A | EV ≈ stały stop (PIT −0,002 vs −0,037 vs −0,085 — szum); nowa zależność bota od pliku danych w repo i od GitHuba w czasie biegu = nowy tryb awarii bez korzyści. Stop 15/10 stały z B. |
| Kotwica stopu `fills.cena` przed `p["wejscie"]` jako zmiana kodu teraz | A | C3 T3: kotwica D0 −0,48 vs −0,28 (t −2,6); A przyznaje „EV nieustalone”. Przy gross ≤ 80 % kotwica rzadko się przestawia (brak podwójnego wejścia) — zmiana bez przedmiotu; odłożyć do potwierdzenia logiem. |
| Momentum 6M TOP5/BOTTOM5 jako koszyk bota (konstrukcja A w bocie) | A | C1: netto +0,33–0,44, t 0,74–0,95, CI z zerem, szczyt siatki; b_SOX zreal. +0,91–1,08; SOX−NDX < −3: −3,6…−5,1 p.p. Zostaje jako cień i benchmark kosztu konstrukcji E. |
| Selekcja Modelu 3.0 pozostawiona jako źródło koszyka | B | C5: IC −0,10 (CI −0,57…+0,37), 67 % Wyniku = momentum+beta, procedura nieodtwarzalna (10/16 stron nadpisanych); σ koszyków 11,3 p.p. = 3,3× losowego; 36 reguł, 17 po n = 1. Moratorium bez skryptu nie zatrzymuje produkcji reguł. |
| ALLOC 0,06 jako poziom docelowy | B | Wymusza veto lotu 7 nazw (ASML COST LITE MELI MPWR MU SNDK) o niezmierzonym koszcie; C4 rekomenduje 0,10, C pokazuje że przy E 0,08 daje P(kill 52, α0) 8,1 % bez soft — lepsze niż 0,06 z koszykiem o σ 7,2–11,3. Poziom 0,06 ma sens tylko, jeśli selekcja zostaje uznaniowa (wtedy B jest spójny). |
| Schodek FLAT −12 % od szczytu CYKLU jako główna ochrona ogona | B | Własna symulacja B: P(kill 52, α0) 27,3 → 25,5 %; na ścieżce hist. 19 → 14,5 %. Wartość tylko w ogonie 12/26 tyg. Próg miękki od kroczącego szczytu (A/C) daje 8,1 → 0,2 % — ale patrz §5 o wykonalności ×0,5. |
| Puls 3×/tydz. (pon./śr./pt.) | C | Bez dowodu (C przyznaje). Wyzwalacze newsowe R3 i wyłącznik płynności nie mają innego nośnika; koszt codziennej wersji kontrolnej ≤ 8 wywołań TV/10 min (A) jest mały. Zostawić codziennie w wersji kontrolnej; decyzja właściciela, nie statystyki. |
| `KILL_LEVEL` 0,70/0,65 jako forma restartu | wszystkie odradzają | C9 §4: przesuwanie progu po stracie; poduszka 8,9–17 % zamiast 33 %. |
| Reset `equity_peak` BEZ `START_EQUITY ≤ kapitał` (albo odwrotnie) | — | C9 §4: osobno dają 11 % albo 0 poduszki; tylko oba naraz dają 33 %. Wszystkie trzy projekty mają to poprawnie — odnotowuję, bo to najczęstszy błąd wykonania. |

---

## 5. Zastrzeżenie wspólne dla A i C, którego żaden z nich nie rozwiązał: wykonalność progu miękkiego ×0,5

Próg miękki (`equity/equity_peak < 0,90 → alloc × 0,5`) daje w A i C największą część redukcji P(kill 52): A vt 48–54 % → 17–19 %, E 0,08: 8,1 → 0,2 %. Ale przy ALLOC 0,08 × 0,5 = 0,04 na nogę i kapitale rzędu START_EQUITY tabela lotów (`projektC_bt_out.md` §3, `projekt_B_sim_out.md` E) pokazuje **9 nazw pomijanych** (ASML COST LITE MELI META MPWR MU REGN SNDK) i 10 w przestrzale — koszyk E z 16.10 (CRWD AMD FTNT TRI ABNB / APP AVGO PAYX NFLX CMCSA) traci AMD i ma AVGO w przestrzale. B wskazał dokładnie ten problem („połowienie lotu 0,1 niewykonalne; `plan_redukcji` → niewykonalna; stąd płasko”). Konsekwencje:
- Liczby „+soft” dla A i C są **górnym oszacowaniem** korzyści; faktyczny mechanizm po −10 % to `REDUCE_FALLBACK=close` dla nóg niewykonalnych → koszyk nierówny (strony nie są równe → netto-short/long indeksu, czego bt_neutralnosc ostrzega przy nierównych stronach).
- Rozwiązanie do wyboru przed wdrożeniem (decyzja, nie dowód): (a) soft = „zamknij wszystko do powrotu nad −5 %” (semantyka FLAT z B, ale od kroczącego szczytu, nie od szczytu cyklu — wtedy liczby P(kill) z A/C są bliskie prawdy, bo płasko ≤ ×0,5); (b) soft ×0,5 z `REDUCE_FALLBACK=close` i pomiarem nierówności stron w Pulsie; (c) próg wykonalności kapitału ~1 600–2 500 USD (C4 §6) jako warunek użycia ×0,5. Rekomenduję (a): jest wykonalna lotami, zachowuje równość stron i jej P(kill) jest policzalne tą samą symulacją (zamiast ×0,5 wstawić ×0).
- Kryterium 12 okien w C („σ zreal. w [0,7; 1,4] × 1,84 %”) powinno osobno raportować tygodnie w trybie soft, bo w nich σ i pokrycie będą inne.

---

## 6. Co trzy projekty mają wspólnego i co jest dobrze poparte (nie wymaga dalszego sporu)

- `ALLOC_PCT` 0,24 → ≤ 0,08 przed 19.10 13:45 UTC; `TACTICAL_ENABLED=false` (C4, n = 4 pozycje).
- Decyzja o resecie szczytu: opcja (c) z C9 (oba pola naraz) albo płasko; sam ALLOC zostawia 39 %/48 %/58 % (C9 §2). To decyzja właściciela; dane mówią, że E[kapitał] czekania ≈ restartu (0,765 vs 0,761), więc nie ma „jedynej sensownej opcji”.
- Puls bez wyzwalaczy cenowych 4/8 (C7: EV ±0,15, ogon ≤ 1 p.p., P(kill) −1,4 pkt); KONTROLA BRAMKI jako pomiar; wyzwalacze newsowe z listy zamkniętej z dokumentem (bez dowodu — decyzja o ogonie).
- Reżim: P1 flaga, P2 tylko DD ^NDX > 20 % bez histerezy (C8: histereza = 10 tyg. odbić po +3,8…+5,8 %).
- K10 i warianty uchylone (C6) z wyjątkiem sita SHORT po kolapsie (osobny test).
- Brak reopen po stopie w tej samej `version` (wykonanie-bota, C3: netto ≈ 0, księgowo pewny spread).
- `p` usunięte z tabel (C5: nieinformacyjne, |Spearman| ≤ 0,05).
- Metryka główna od fills (D+1), nie od D0 (C7 §7: kotwica zmienia wnioski o W4 i W7; wykonanie-bota: różnica ±4–10 p.p./tydz.).
- Koszyki cienie co sobotę jednym skryptem; decyzje o wariancji po 12–26 oknach, o średniej nigdy przed 52 i tylko jako CI.
- Żadna zmiana parametrów po złym tygodniu.

---

## 7. Kontrole spójności liczb, które wykonałem (żeby ocena nie opierała się na streszczeniach)

1. A §2.2 „vt+soft 0 %/17 %” = `projektA_boot_out.md` 0,0 %/16,6 % — zgodne; ale A §0 pisze „vt: 4 %/54 %” i nie wyciąga wniosku, że VT bez soft jest gorszy od stałego 0,08 (1,0 %/33,3 %). Wniosek wyciągam ja (§1.1).
2. A „stałe 0,08 PIT in-sample P(kill 52) 15,6 %” (boot) vs `projektA_bt_out.md` ścieżka historyczna 0,0 % — różne metody (bootstrap vs jedna ścieżka); nie błąd, ale A cytuje korzystniejszą z dwu tam, gdzie wygodnie (§13 „P(kill 12 tyg.) 0 % przy każdej alfie” — z bootstrapu 0,0 %, ścieżka 0,0 %; ok).
3. B „P(kill 52, α0 z kosztami) 25,5 %” = `projekt_B_sim_out.md` A P3c — zgodne; „FLAT 1,4/rok” = 1,39 — zgodne; „W1–W7 przy 0,06: −2,5 %, maxDD −8,4 %” = sekcja C — zgodne.
4. C „σ-ratio 0,669 [0,58; 0,78]” = `projektC_bt_out.md` 1b PIT B_cap05 — zgodne; „0,08 + soft 0,2 %” = `projektC_dod_out.md` A — zgodne; „vol-target 0,12 w 98 % tygodni” = §4b — zgodne; „9 nazw pomijanych przy 0,04” = §3 — zgodne.
5. C9 „P(kill 5 ses.) przy 0,08 = 39 %” (z luką W7) vs projekty cytujące „18 %” (bez luki): A §12.1 podaje 35 %/54 % (c = 0), C §11.1 39 %/58 % (c = 0,3) — oba poprawnie uwzględniają księgę W7. B §7 „≈ 30 %/40 %” dla 0,06 — spójne kierunkowo.
6. C1 PIT „+0,71 brutto / +0,44 netto” (233 okna, bez wet) vs A „A0 +0,71/+0,44” — zgodne; A z wetami S1+K13 +0,60/+0,33 (koszt wet −0,11 p.p., nieistotny). C na 209 oknach A +0,59 — zgodne z A po skróceniu okna.

---

## 8. Ścieżki

- Ta notatka: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/sedzia-1.md`
- Projekty: `projekt-A-mechaniczny.md`, `projekt-B-przezywalnosc.md`, `projekt-C-konstrukcja.md` (ten sam katalog)
- Wyjścia skryptów użyte do kontroli: `projektA_bt_out.md`, `projektA_boot_out.md`, `projekt_B_sim_out.md`, `projektC_bt_out.md`, `projektC_dod_out.md`
- Weryfikacje: `weryfikacja-C1.md` … `weryfikacja-C9.md`
