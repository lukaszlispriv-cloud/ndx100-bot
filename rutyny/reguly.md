# Rejestr reguł systemu NDX100 (od 2026-W9)

Wersja 2026-10-18 (pierwsza). Plik czytają obie rutyny w KROKU 0. **Obowiązują wyłącznie
reguły z sekcji OBOWIĄZUJĄCE.** Falsyfikacja deklaracji D1–D3 albo lekcja z pojedynczego
tygodnia tworzy wyłącznie wpis KANDYDAT. Awans do OBOWIĄZUJĄCYCH tylko po teście
przekrojowym na 5 latach zamknięć (`analiza/2026-10-18/pobierz_closes_5y.py`): ≥ 30 zdarzeń
w ≥ 15 tygodniach, |t| ≥ 2 (klastrowane po dacie), ten sam znak w ≥ 4 z 5 lat, reguła musi
wiązać (zmieniać skład) — i po decyzji właściciela. Każda reguła ma datę retestu (12 tygodni)
i pole kosztu skumulowanego (zwrot wykluczonych − zamienników, liczony co sobotę przez
`scripts/koszyki_cienie.py`). Źródło audytu: `analiza/2026-10-18/audyt-regul.md` (36 reguł
W1–W8: 17 wprowadzonych po n = 1, 0 z retestem, ≥ 6 par sprzecznych).

Rutyny czytają ten plik w KROKU 0, ale go NIE edytują — każda zmiana rejestru to commit
właściciela (lub sesja na jego zlecenie) z datą. Stan wdrożenia: reguły oznaczone „app.py” albo
„Render” wymagają działania właściciela (PROPOZYCJA-2026-10-18-proces-v2.md §1–§3); do deployu
rutyny opisują stan faktyczny bota, nie docelowy.

Format wpisu: ID · treść operacyjna (pole, próg, kierunek) · zakres · wejście · wyzwalacz (n) ·
test przekrojowy (n, śr. p.p./tydz., t) · koszt skumulowany · retest/wygasa.

## OBOWIĄZUJĄCE

| ID | Treść operacyjna | Zakres | Wejście | Test przekrojowy | Retest |
|---|---|---|---|---|---|
| K13 | **Nie shortuj spółki po spadku 10-sesyjnym ≤ −20 %** (`r10` z ranking.py); bez wyjątku „twardy negatyw”. Scalone: sito 12 % (K14), luka 1-dniowa > 10 % (K15) — uchylone. | sobota, strona SHORT | W5 (29.09), potwierdzona 18.10 | short po r10 ≤ −20 %: −1,64 p.p./tydz. (n = 213, t −2,42); 12 %: −0,7 (t −1,7); luka: ≈ 0. In-sample INTU W5–W7: −20,8 p.p./nogę oszczędzone (3/3) | 2027-01-10 |
| R11 | Sygnał wyjścia z bloku pamięci (pierwsza obniżka cen kontraktowych DRAM/NAND wg TrendForce albo pierwszy miss guidance MU/SNDK/STX/WDC) = CLOSE o podstawie news dla nóg pamięciowych | puls i sobota | od startu | twardy, prerejestrowany, nigdy nie wystąpił (n = 0) | — |
| R3 | CLOSE o podstawie **news** (lista zamknięta: ogłoszona oferta przejęcia/wezwanie z ceną (noga SHORT), delisting/zawieszenie notowań, szokowy raport lub cięcie guidance z dokumentem źródłowym, decyzja regulatora o bezpośrednim skutku dla przychodu, R11 dla nóg pamięciowych); REDUCE WYŁĄCZNIE przy obniżce guidance bez missu (z dokumentem) albo wszczęciu postępowania regulatora bez decyzji (dokument) — nic innego („istotny negatyw” nie jest kategorią); działają od razu, bez bramki cenowej | puls | od startu | ryzyko ogonowe; 3 użycia, +0,69 p.p. na papierze | 2027-01-10 |
| R4 | Higiena: ≤ 2 nowe wpisy exclude/dzień; REDUCE → CLOSE jednokierunkowo; raz zredukowana zostaje do rotacji | puls | od startu | operacyjna | — |
| R8 | **Lista imienna do `--exclude` ranking.py (obie strony)**: dziś MSTR (krypto-beta); governance z raportem audytora/short-sellera albo koncentracja klienta > 30 % wchodzą tylko jako WYJĄTEK IMIENNY z datą i faktem (commit właściciela), nie z oceny rutyny | sobota | Model 3.0 → 18.10 | ryzyko ogonowe (MSTR 12–17 p.p./tydz.); znak nierozstrzygalny | 2027-01-10 |
| R14 | Koszyki cienie (A momentum, B pary branżowe, C neutralna, D budżet czynnikowy, **E koszyk bota**, U nakładka uznaniowa opcjonalnie, FAKTYCZNY; na papierze „bez nóg EVENT” i ETF SMH−XLP) rozliczane co sobotę `scripts/koszyki_cienie.py` z `data/ranking-<version>.json` do `data/koszyki-cienie.jsonl`; **żadnego wniosku o średniej przed 26 oknami, o wariancji (test F) po 12**; kryteria decyzji po 12/26/52 oknach prerejestrowane w `rutyny/tygodniowa.md` KROK C | sobota | 12.10 / 18.10 | jedyny działający element pętli uczenia; moc testu F dla σ-ratio 0,67: 22–47 % po 12–26 oknach | — |
| K2' | Raport wyników w oknie D0+1…D0+7 dni kalendarzowych (≈ sesje D+1…D+5; `EVENT_WINDOW_DAYS` w ranking.py; chroni okno pomiaru — raport w poniedziałek rotacji D0+10 NIE jest wetowany, to ryzyko rachunku opisywane w raporcie) = **veto** dla nogi (nie kara punktowa); kalendarz: FMP earnings-calendar pierwszy, TradingView drugi; data niepotwierdzona = veto | sobota | W1 (kara), 18.10 (veto) | nietestowalne bez historycznego kalendarza (asymetria in-sample: longi z raportem przegrywały, shorty wygrywały); decyzja konstrukcyjna o ryzyku ogonowym | 2027-01-10 |
| S1 | **Veto zmienności**: noga o σ60 > 3× mediany uniwersum poza koszykiem (ranking.py `SIGMA_VETO_MULT`) | sobota | 18.10 | konstrukcyjna: przy równych wagach jedna noga o σ 20 %/d ≈ 70 % wariancji koszyka (MRNA 16.10: σ60 23,5 %) — nie prognoza | 2027-01-10 |
| S2 | **Stały sizing koszyka: ALLOC_PCT 0,08 (gross 80 %), ALLOC_PCT_SAFE 0,04** — zmienne Rendera ustawia właściciel; zmiana krokiem ≤ 0,02 na 4 tygodnie, nigdy po jednym tygodniu; vol-target (ALLOC = clip(0,015/(5 × σ60_unit), 0,04, 0,12)) WYŁĄCZNIE jako kolumna diagnostyczna raportu (`alloc_pct_proponowany` z ranking.py), ≥ 12 tygodni na papierze; pole `sizing` w signals.json NIE powstaje. Od 18.10.2026 wartości 0,08 / 0,04 są też DOMYŚLNYMI w `app.py` (zmienna w Renderze ma pierwszeństwo). Próg miękki (S2'): obsunięcie > 10 % od szczytu kill switcha → bot zamyka pierwsze 2 pary list long/short do powrotu poniżej 5 % (`DD_SOFT`, `DD_SOFT_RESET`, `SOFT_PARY`; stan `wykonanie.soft`) — WDROŻONE | Render + sobota + app.py | 18.10 (panel sędziów: stałe ALLOC zdominowało vol-target na tej samej konstrukcji) | P(kill −25 %, alfa 0): 0,24 → 51–65 %/12 tyg., 98–100 %/52 tyg.; E przy 0,08 → ≈ 0 %/12 tyg., 8 %/52 tyg. (< 1 % z progiem miękkim) (C4, projekt C, sędzia 3) | 2027-01-10 |
| K0 | **Koszyk bota = `konstrukcje.E_pary_budzet_sox` z `scripts/ranking.py`** (momentum 6M rel., skip 5; 5 par w grupie branżowej TV z puli 8 par o największym rozstępie; piątka o największej sumie rozstępów przy \|b_SOX net\| ≤ 0,5, inaczej min \|b\|; równe wagi; listy w kolejności od pary o najwyższej σ60); veta: exclude, EVENT (raport D0+1…+7 dni), σ60 > 3× mediany, cena > 1 280 USD, K13 (short). Żadnej nakładki uznaniowej w signals.json (cień U na papierze obowiązkowy albo jawnie pominięty). Degradacje z adnotacją w raporcie i wiadomości: bez snapshotu TV → E bez taksonomii (jedna grupa); < 5 par branżowych → skrypt dopełnia parami bez grupy (`+dopelnione`); brak bety SOX → wybór po rozstępie (`bez_czynnika`); `za_malo_par` → FALLBACK bez rotacji | sobota | 18.10 | σ-ratio E/A 0,67 (CI 0,58–0,78) na 209 oknach PIT, najgorszy tydzień −12,7 vs −23,9 p.p., Δ średniej −0,21 (nierozstrzygalna); retro W4–W7: E +11,8 / +6,4 / −2,2 / −9,3 vs FAKT +13,8 / +6,0 / −5,6 / −21,2 (anegdota) (C2, projekt C) | 2027-01-10 |
| R5'' | **Reżim = wyłącznie wyłącznik płynności P2** (drawdown ^NDX > 20 % od maks. 252 sesji LUB sesja ≤ −5 % LUB VIX > 40 → `status` NIEAKTUALNA; powrót po 5 sesjach VIX < 25 ∧ ^NDX > MA50 decyzją soboty); P1 = flaga w raporcie, bez REDUCE; bez eskalacji uznaniowej | puls i sobota | 18.10 | bramka P1 obniżała momentum 1,00 → 0,78 p.p./tydz. bez poprawy maxDD; tygodnie P1 najlepsze (+3,04, t 2,0); W6–W7 w P0 (C8) | 2027-01-10 |
| R1'' | **Bramka cenowa Pulsu 4 %/8 % = pomiar** (sekcja BRAMKA — POMIAR, bez wpisów); `exclude` wyłącznie R3/R11 z dokumentem źródłowym | puls | 18.10 | EV ≈ 0 (±0,15 p.p./tydz.; po sygnale REDUCE reszta okna +0,08…+0,16, t ≈ 0); stop bota zawsze pierwszy (C7) | 2027-01-10 |
| T0 | **Moduł taktyczny wyłączony**: `tactical = []` w obu rutynach, Render `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0` — do testu przekrojowego H2 | puls, sobota, Render | 18.10 | n = 4 pozycje, 20 % kapitału na nogę bez dowodu; σ ≈ 1 % kapitału dziennie z jednej nogi | po teście H2 |
| S3 | **Stop bota 15 % LONG / 10 % SHORT od poziomu brokera (kotwica bez zmian), bez ponownego otwarcia w tej samej wersji** (`wykonanie.stopy[ticker]` blokuje nogę do zmiany `version`) — WDROŻONE w `app.py` 18.10.2026 (gałąź; domyślne `STOP_LOSS_PCT_LONG=0.15`, `STOP_LOSS_PCT_SHORT=0.10`, `STOP_REOPEN=false`), aktywne po deployu na Renderze; do deployu rutyny czytają stan faktyczny z `/status.ustawienia`. Wariant „stop w jednostkach σ z kotwicą w cenie tezy” odrzucony w weryfikacji (C3) | app.py (Render: STOP_LOSS_PCT_LONG/SHORT, STOP_REOPEN) | 18.10 | stop 10 % kosztuje na nogach LONG −0,23 p.p./tydz. (t −2,3), SHORT neutralny; ponowne otwarcie = drugi spread bez sygnału; kotwica w cenie tezy pogarsza (−0,48 vs −0,28) (C3) | 2027-01-10 |

## KANDYDACI (rozliczane na papierze, nie zmieniają składu)

| ID | Treść | Źródło | Co trzeba pokazać |
|---|---|---|---|
| H1 | Shorty software/„ofiary substytucji” mają dodatnią resztę po czynnikach (+3,3 p.p./nogę, n = 13 in-sample) | dekompozycja-wynikow.md §6 | przekrój ≥ 30 zdarzeń; dotąd brak definicji operacyjnej „ofiary” |
| H2 | Long po dniu ≥ +12 % relatywnie, trzymanie 10 sesji (fwd10 +3,5 p.p., t 2,2, n = 307; 2022 i 2026 ujemne dla ≥ +8 %) — ewentualna mechaniczna reguła taktyczna | perspektywa-quant.md §D | holdout 2025-07…, stabilność znaku w latach, sizing |
| H3 | Momentum 6M działa tylko przy VIX > 20 na D0 (+2,4 p.p., t 2,8 vs +0,35 przy VIX ≤ 20) | bt_momentum.md | podział ex post; potrzebny holdout — do czasu testu NIE sterować gross wg VIX |
| H4 | Konstrukcja parowa (B) ma σ o 24 % niższą od czystego momentum przy tej samej średniej | bt_neutralnosc.md | potwierdzenie na taksonomii liczonej per data (od W9 snapshoty TV co tydzień) i test F na ≥ 12 oknach cieni |
| H5 | Budżet czynnikowy (D: \|b_SOX net\| ≤ 0,5, \|b_DEF net\| ≤ 0,5) obniża ogon bez utraty średniej | dekompozycja-wynikow.md, ranking.py | retro W4–W7 (okna 5 sesji od D0, z vetem cenowym 1 280 USD): D +8,2 / +10,9 / −2,1 / −12,2; E +11,8 / +6,4 / −2,2 / −9,3; FAKT +13,8 / +6,0 / −5,6 / −21,2 (anegdota) — ≥ 12 okien cieni |
| D1-W8 | GOOGL pobije ^NDX relatywnie 16.10→23.10 | raport W8 | rozliczyć 24.10 na papierze; bez konsekwencji w składzie |
| D2-W8 | SNDK (poza koszykiem przez filtr siły relatywnej) nie pobije ^NDX w oknie | raport W8 | rozliczyć 24.10; **niezależnie od wyniku filtr K17 jest uchylony** (patrz UCHYLONE) |
| D3-W8 | warunkowa: po NFLX ≤ −5 % 21.10 APP i DASH przegrają z ^NDX w sesji 21.10 | raport W8 | rozliczyć 24.10 na papierze |

## WYJĄTKI IMIENNE (wygasają bez nowego faktu)

| ID | Treść | Wygasa | Koszt dotąd |
|---|---|---|---|
| K12 | NVDA poza koszykiem long do zamknięcia śledztwa DOJ/Groq | **wygasł z końcem W8** — od rotacji 24.10.2026 (W9) NIE wchodzi do `--exclude`; przedłużenie tylko z nowym faktem z datą (commit właściciela) | −0,67 p.p./nogę (zamienniki +1,99) ≈ 0 |
| K11 | TSLA poza koszykiem short („wraca po cięciu celu przez elitę”) | **wygasł z końcem W8** — od 24.10.2026 NIE wchodzi do `--exclude`; warunek powrotu skreślony | short wygrałby 2/4 (+2,16/nogę) — szum |
| K6' | Nie shortuj spółki z OGŁOSZONĄ ofertą przejęcia (cena/proces); doniesienia prasowe bez oferty nie liczą się. Operacyjnie (sobota, KROK B2): jedno zapytanie WebSearch dla każdej z 5 nóg SHORT konstrukcji E; trafienie → `--exclude` i ponowny bieg ranking.py | 2 tygodnie od ostatniej aktualizacji oferty | WDAY poza shortem 6 okien na doniesieniach: +15,1 p.p./nogę kosztu |

## UCHYLONE (archiwum — nie stosować)

| ID | Treść | Powód uchylenia (liczby) |
|---|---|---|
| K10 / K16 / K17 / R15 | „Przegrana noga bez odzyskanej siły relatywnej = poza koszykiem”, warianty: bez wyjątku dla wyceny, filtr kandydatów spoza koszyka (W8), sito Perf.W ≤ −8 % | przekrój: przegrane bez odzyskania +0,66 p.p./tydz. (n = 1108, t 0,44) vs odzyskane +0,32 vs wygrane +0,59; in-sample 10 wykluczeń: zamienniki średnio gorsze o 0,84 p.p./nogę, ale mediana różnicy +2,05 — wynik zdominowany przez LITE W5 (+16,1), in-sample nierozstrzygalne (C6); koszt reguły w symulacji −0,37…−0,70 p.p./tydz. (C6); wymuszała wymianę 5–9 nóg/tydz. |
| K8 / K21 | „Nie kupuj po jednodniowym skoku / pogoń”, „momentum bez rewizji = pułapka”, „nie shortuj pędu” jako filtry | znak przeciwny do danych: long po skoku ≥ +12 % +1,06 p.p. (t 2,2), 10 sesji ≥ +15 % +1,13 (t 2,8); 4/7 wykluczonych wygrałoby |
| K14 / K15 | Sito > 12 %/10 sesji z „twardym negatywem”; luka 1-dniowa > 10 % → nie shortuj | słabsze niż K13 (t −1,7) / brak sygnału (t ≈ 0); n = 1 (PAYX / TMUS) |
| K3 / K4 | Kalibracje kary event („15 zamiast 8”, 6→3 dla pozytywnego eventu) | n = 1 każda; LITE W7 kara 0 przez „premię” złamała zasadę „kara PO bazie”; zastąpione vetem K2' |
| K9 / K23 | Płatnicy capexu poza longiem / dolny kwartyl czynnika 10 | MSFT +6,83 p.p. kosztu; W8 i tak odwrócone |
| K7 | Shorty defensywne jako „jedyna strona z alfą” | przekrój: defensywy −0,05 vs tech +0,21 dla shorta (t < 1); W7 0/4 = −46,9 p.p. — ekspozycja czynnikowa, nie selekcja |
| K18 / K19 | Limit 2 nazwy na blok nazwany (pamięć/WFE) / rozproszenie po „wąskich gardłach” | W7: 5 „różnych gardeł” spadło razem; blok definiuje beta do SOX−NDX (ranking.py), nie nazwa |
| K20 / K24 / K25 / K26 | Checklisty pre-mortem i zmiany wag po jednym komunikacie | n = 1–2; K25 sfalsyfikowana własną deklaracją |
| K22 | „Nie shortujemy tego, czego nie rozumiemy” | 2/6, śr. −0,5 p.p. — szum |
| R6 | p = 50 % + 0,5 × (wynik − 50), 38–62 % jako „prawdopodobieństwo” | skalibrowane odwrotnie: p ≥ 61 → 37,5 % trafień, p ≤ 58 → 60 %; corr(p, zwrot) −0,16 |
| R9 (części) | Blokada shortu przy ≥ 3 Buy elity; „−1 stopień bez weryfikacji na żywo” | nigdy nie zmieniły decyzji; elita nieweryfikowalna z tego środowiska |
| R10 | „Przy porównywalnych argumentach mniejsza waga” jako preferencja skuteczności | 8 decyzji granicznych: wybrany gorszy o 1,31 p.p./nogę; zostaje tylko jako tie-break bez uzasadnienia |
| R1' / R2 | Bramka cenowa Pulsu 4 %/8 % od `fills` z potwierdzeniem drugą sesją i blokadą sektorową **jako wyzwalacz REDUCE/CLOSE** | przekrój: po sygnale REDUCE reszta okna +0,08 p.p. (n = 3442, t 0,03); po dniu spreadu ≤ −3 p.p. kolejne 3 sesje +1,43 p.p. (t 2,7); in-sample +2,78 p.p. (tylko W7); zawsze wyprzedzana przez stop bota. Redukcję wariancji przejmują S2 (sizing 0,08), K0 (konstrukcja E) i S3 (stop 15/10 bez reopen). Puls zachowuje pomiar bramki jako DIAGNOSTYKĘ (R1'', bez wpisu) do oceny ex post. |
| R5' | Bramka reżimu P1 → REDUCE wszystkich nóg (gross 50 %) | backtest: obniża średnią momentum 1,00 → 0,78 p.p./tydz. bez poprawy maxDD; tygodnie P1 najlepsze dla momentum (+3,04, t 2,0). **P1 zostaje flagą w raporcie; P2 zostaje jako wyłącznik płynności** (sesja ≤ −5 % lub VIX > 40 → status NIEAKTUALNA do histerezy). |

## Zasady prowadzenia rejestru

1. Nowy wpis wyłącznie w KANDYDATACH, z definicją operacyjną (pole danych, próg, kierunek) i skryptem testu.
2. Awans: test przekrojowy jak w nagłówku + decyzja właściciela zapisana w commicie; retest co 12 tygodni — reguła bez retestu wraca do KANDYDATÓW.
3. Jedno zdarzenie cenowe ma jedną interpretację kierunkową (koniec par sprzecznych: „nie kupuj po skoku” vs „momentum”).
4. Raport sobotni ma stałą tabelę „REGUŁY — kontrola”: które reguły wiązały w tym tygodniu, które nogi wykluczyły i jaki był zwrot wykluczonych vs zamienników.
5. Moratorium: do zakończenia 26 okien koszyków cieni (ok. kwiecień 2027) żadna nowa reguła koszykowa nie wchodzi do OBOWIĄZUJĄCYCH.
