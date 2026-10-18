# PROJEKT C — konstrukcja koszyka i horyzont: 5 par branżowych z budżetem SOX, 1 tydzień, 5/5 nóg

> Nota 18.10.2026 (po przeglądzie): składy „E dla W8” w tej notatce liczono bez veta EVENT — historyczne. Obowiązuje `data/ranking-2026-W8.json` (CRWD/APP, AMGN/ALNY, FTNT/PAYX, AMD/AVGO, DXCM/GEHC).

Autor: projektant procesu inwestycyjnego (sesja 18.10.2026). Priorytet: **konstrukcja koszyka i horyzont**
przy wykonalności (lot 0,1 akcji, kursy > 600 USD, kapitał odniesienia rzędu `START_EQUITY` = 1 000 USD
z `app.py:164`; bez liczb z rachunku). Każdy element ma liczbę z faz 1–2 (`_faza1_wyniki.txt`,
`_faza2_wyniki.txt`), z weryfikacji C1–C9 albo z dwóch nowych skryptów tej notatki — albo jest oznaczony
**„bez dowodu — decyzja”**.

Nowe skrypty (katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):

| plik | co liczy |
|---|---|
| `projektC_bt.py` → `projektC_bt_out.md`, `projektC_bt_wyniki.json`, `projektC_bt_serie.csv` | 11 konstrukcji 5L/5S na 209 oknach tygodniowych 2022-10…2026-10 (okna z pełnym 250-sesyjnym oknem bety), na składzie **dzisiejszym** i **point-in-time** (JOIN/LEAVE z `weryfikacja_C1.py` + `dane/dropped_closes.csv`, 28 spółek usuniętych z taksonomią przypisaną ręcznie); różnice sparowane wobec A, σ-ratio z bootstrapem i testem F; ekspozycja SOX ex ante (b_SOX 250 sesji) i zrealizowana (regresja tygodniowa); veto cenowe; loty 0,1 akcji dla 10 i 20 pozycji; bootstrap blokowy kapitału P(kill −25 %) 12/52 tyg.; koszyki na D0 2026-10-16 |
| `projektC_dod.py` → `projektC_dod_out.md`, `projektC_dod_wyniki.json` | P(kill) dla polityk 0,10 / 0,08 + próg miękki / vol-target 1,0 %; **moc testu F** na koszykach cieniach (ile tygodni, by potwierdzić σ-ratio); wrażliwość konstrukcji E na definicję grupy (5 definicji × 2 składy) |

Oznaczenia: **A** = TOP5/BOTTOM5 momentum 6M rel. (126 sesji, skip 5) z wetami S1/K13 (koszyk bota w projekcie A);
**B** = 5 par wewnątrz grupy TV; **E = B_cap05** = 5 par z budżetem |b_SOX net| ≤ 0,5 (konstrukcja tej notatki);
`_stag` = 2 transze z 5 nogami/stronę (noga trzymana 2 tygodnie, wymiana 2/3 na przemian); `_2x5` = 2 transze po 5
(10 nazw/stronę, pół wagi); **D_lo / D_05** = A + budżet |b_SOX net| ≤ 1,0 / ≤ 0,5 przez wymiany nóg (jak `ranking.py::konstrukcja_budzet`).

---

## 0. Streszczenie decyzji

| element | decyzja | liczba, która ją uzasadnia | źródło |
|---|---|---|---|
| **Konstrukcja koszyka bota** | **E: 5 par „long najlepsze / short najgorsze momentum 6M w tej samej grupie TV”, dobranych spośród 8 najlepszych par tak, by \|b_SOX net\| ≤ 0,5** | PIT: σ 4,61 vs 6,89 p.p. (σ-ratio **0,669**, CI95 0,58–0,78, F p < 10⁻⁴), najgorszy tydzień **−12,7 vs −23,9**, p5 −7,0 vs −10,4, maxDD −41 vs −57; b_SOX zrealizowane **+0,31 vs +1,08**; w 19 tygodniach SOX−NDX < −3 p.p.: **−1,91 vs −5,14**. Koszt: Δ średniej −0,21 p.p./tydz. (t −0,58, CI −0,92…+0,50) PIT, −0,12 (t −0,35) dziś. Dziś: Sharpe 1,17 vs 0,99 | projektC_bt §1 |
| **Dlaczego pary, nie budżet czynnikowy na A (D)** | D obniża σ mniej i kosztuje więcej średniej | PIT: D_05 Δ −0,38 (t −1,65), σ-ratio 0,805; D_lo (cap 1,0) Δ −0,36 (t −1,89), σ-ratio 0,844. E: Δ −0,21, σ-ratio 0,669. Zgodne z projektem A (D − A −0,54, t −2,36 na 233 oknach) | projektC_bt §1b; projekt-A §2.2 |
| **Dlaczego pary z budżetem (E), nie same pary (B)** | B tylko połowicznie usuwa zakład SOX; E usuwa go w ~70 % przy tym samym koszcie średniej | b_SOX zreal.: A 1,08 → B 0,53 → **E 0,31** (PIT); ex ante \|b_SOX net\| 0,71 → 0,44 → **0,29**; SOX<−3: −5,14 → −4,08 → **−1,91**; Δ vs A: B −0,24, E −0,21 (PIT); dziś B +0,04, E −0,12. Na D0 09.10.2026 same pary dały b_SOX **+1,40** (ALAB/AVGO w jednej grupie) | projektC_bt §1, §5 |
| **Horyzont** | **1 tydzień, pełna rotacja co sobotę** — bez 2 transz | A_stag vs A: Δ +0,18 (t +1,60) dziś, **−0,10 (t −0,85) PIT**; B_stag vs B: −0,26 (t −1,42) dziś, −0,09 PIT; σ-ratio 0,95–1,01; oszczędność obrotu 0,4–0,7 nogi/tydz. ≈ 0,005 % kapitału/tydz. — **brak dowodu korzyści**. 2×5 nakładające się (pq_quant: Sharpe 1,12 vs 0,99) na PIT: Sharpe 0,51 vs 0,62, Δ −0,01 | projektC_bt §1b |
| **Liczba nóg** | **5/5** (jak dziś) | N=10 h=1w Sharpe 0,66 vs 0,99 dla N=5 (sygnał w ogonach rankingu); 20 pozycji przy 1 000 USD i ALLOC 0,04/pozycję: **9 nazw pomijanych** (ASML COST LITE MELI META MPWR MU REGN SNDK), 10 w przestrzale | pq_quant §B; projektC_bt §3 |
| **Veto cenowe (wykonalność)** | nazwy o kursie > 1 280 USD poza koszykiem (`MAX_PRICE_USD`, = 1,6 × 0,08 × 1 000 / 0,1) | przy 10 pozycjach i ALLOC 0,08: pomijane ASML, MELI, SNDK; koszt veta: Δ +0,03…+0,04 p.p./tydz. (t 0,7–1,5), udział tych nazw w nogach 2,1–2,2 % — **≈ 0** | projektC_bt §2–3 |
| **Sizing** | **stałe ALLOC 0,08 + próg miękki −10 %/−5 % (×0,5)**; **bez** vol-targetu i bez pola `sizing` | dla E vol-target 1,5 %/d daje ALLOC 0,12 w **98 %** tygodni (σ60_unit E ≈ 1,9–2,0 %/d) — reguła martwa; P(kill 52 tyg., alfa 0, PIT): 0,08 → **8,1 %**, 0,10 → 19,1 %, 0,12 → 33,0 %; 0,08 + soft → **0,2 %**; 12 tyg.: 0,0 % przy każdym z nich | projektC_bt §4; projektC_dod §A |
| **Pola `signals.json`** | **żadnego nowego pola top-level**; opcjonalnie podklucz `konstrukcja: "E"` w nowym wpisie `history` (walidator już go przepuszcza) | E ma 5/5 nóg, równe wagi, ALLOC stałe w Renderze → `_sanity` i walidator bez zmian merytorycznych; próg miękki to pole bota `wykonanie.soft` | CLAUDE.md; `waliduj_signals.py` |
| **Puls dzienny** | w obecnej formie (bramka 4 %/8 %, protokół cenowy) **niepotrzebny**; zostaje jako raport kontrolny (pokrycie `/status`, wyzwalacze newsowe z listy zamkniętej, wyłącznik płynności); częstotliwość 3×/tydz. (pon./śr./pt.) = **bez dowodu — decyzja** | REDUCE przewiduje resztę okna na +0,08 p.p. (n 3442, t 0,03); autokorelacja dziennego spreadu lag1 −0,01; po dniu ≤ −3 p.p. kolejne 3 sesje **+1,43 p.p. (t 2,7)**; EV bramki ±0,15, P(kill) 32,6 → 31,2 %; w W6–W7 zawsze wyprzedzona przez stop; przy E σ dz. kapitału ≈ 0,8 % → ruch 4 % nogi ≈ 0,3 % kapitału | audyt-regul.md; perspektywa-quant.md §E; C7 |
| **Migracja** | 18–19.10: ALLOC 0,24 → 0,08, taktyczne off, decyzja o resecie szczytu (C9/projekt A); W8 bez zmian; **W9 (24.10) = pierwszy koszyk E**; koszyki cienie od W8 | z poduszką ≈ 1,7 % żadna polityka nie ratuje W8 (P(kill 4 tyg.) 68–85 %); E na D0 16.10: CRWD AMD FTNT TRI ABNB / APP AVGO PAYX NFLX CMCSA, σ60_unit 1,94 %/d, b_SOX +0,18 | C9; projektA_boot; projektC_bt §5 |
| **Pomiar** | koszyki cienie A/A0/B/E/D/ETF co sobotę; **wniosek o σ po 26 tyg. (moc 47 %) / 52 tyg. (74 %)**; o średniej nigdy przed 52 tyg. i tylko jako CI | σ sparowanej Δ(E−A) 5,21 p.p. → t = 2 dla Δ 0,3 / 0,5 / 1,0 p.p. po **1 204 / 433 / 108** tygodniach | projektC_dod §B |

**Oczekiwane metryki (E, PIT, ALLOC 0,08 + soft):** μ spreadu +0,38 p.p./tydz. brutto (CI95 −0,25…+1,01; dziś +0,82), σ 4,6 p.p.; kapitał: σ tyg. 1,84 %, σ dz. ≈ 0,8 %, μ tyg. −0,11 % (alfa 0, same koszty) … +0,04 % (in-sample PIT) … +0,26 % (in-sample dziś); P(kill 12 tyg.) 0 %, 52 tyg. 0,2 % (alfa 0); maxDD 52 tyg. mediana −14 %, p95 −25 %; koszty ≈ 0,115 % kapitału/tydz. **To projekt o połowie mniejszym ogonie i przeżywalności, nie o zysku** — oczekiwany wynik netto jest w granicach ±0,1 %/tydz. i zera w CI.

---

## 1. Co bierzemy z faz 1–2 (liczby, które decydują o konstrukcji)

| twierdzenie | liczba | źródło | skutek dla projektu |
|---|---|---|---|
| Spread W1–W7 to zakład na półprzewodniki, nie selekcja | 74 % wariancji dziennego spreadu = ^NDX + (SOX−NDX), b_SOX 1,72 ± 0,29; znak tygodnia = znak SOX−NDX 7/7; składowa SOX W7 −7,2 p.p.; reszta selekcyjna +0,61 p.p./tydz. (t 0,27) | dekompozycja-wynikow.md | konstrukcja musi mierzyć i ograniczać b_SOX, nie „trafność” |
| Koncentracja to własność metody, nie pech | ρ par LONG 0,56–0,75 (W3–W6) → 1,2–1,5 efektywnej nogi z pięciu; koszyki W4–W6 bardziej zmienne niż 100 % losowych 5/5; σ faktyczna 11,3 p.p. vs 3,4 losowego (χ²(6) = 66) | dekompozycja; ryzyko-i-sizing.md; perspektywa-quant.md | limit koncentracji konieczny, ale sam nie wystarcza (W7: ρ 0,29, 3/5 SEMI) |
| Jedyny sygnał z dodatnim znakiem: momentum 6M | dziś +1,01 (t 2,09), PIT +0,71 (t 1,55), netto +0,44 (t 0,95); odwrócenie −0,33 (t −0,93); low-vol −1,58 (t −3,1) | bt_momentum; C1; bt_odwrocenie; pq_quant §C | sygnał w parach = momentum 6M; żadnych komponentów kontrariańskich |
| Pary branżowe obniżają σ odporne na każdy test, średnia nierozstrzygalna | σ-ratio 0,763 (CI 0,70–0,84), losowa taksonomia 0,92 (p = 0,000), klastry PIT 0,47–0,71; Δ: TV W8 −0,00 ± 0,30, inne definicje −0,15…−0,55, klastry PIT mediana −0,86; 87 % redukcji σ = mniej skrajne nogi, 13 % hedge; 51 % par to zlepki sektorowe | bt_neutralnosc; C2 | pary planować z kosztem 0,2–0,5 p.p./tydz. średniej; definicję grupy **zamrozić**; same pary nie hedgują SOX |
| Budżet czynnikowy na A tnie przewagę | D − A −0,54 (t −2,36), Sharpe 0,09 vs 0,65 (PIT); f beta-neutral 0,38 (t 0,84) | projekt-A §2.2; bt_momentum | budżet jako **wybór między parami**, nie wymiana nóg w A |
| 2 transze nakładające się | N=5 h=2w nakł.: 1,14 vs 1,01, Sharpe 1,12 vs 0,99, obrót 0,10 vs 0,20 (skład dzisiejszy, 231 okien) | pq_quant §B | do sprawdzenia na PIT i w wersji wykonalnej (5 nóg) — §2.3 |
| Neutralność β/σ przez przewagę dolarową shortów szkodzi | e_beta Δ −0,45 (6M) / −0,90 (12M−1M, t −3,2); d_rp W_S 1,6–1,75 → net-short NDX | bt_neutralnosc | równe wagi i równe strony; neutralizacja czynnika tylko przez dobór składu |
| Sizing to dźwignia nr 1 | 0,24: P(kill 12 tyg., alfa 0) 51–65 %, 52 tyg. 98–100 %; 0,08: 1–4 % / 33–41 %; vol-target + soft 0 %/17 % | C4; projektA_boot | ALLOC ≤ 0,08; próg miękki |
| Inverse-vol per noga i REDUCE per noga niewykonalne na tej skali | 0,1 MU = 88 USD, 0,1 LITE = 82 USD > waga 4–6 %; REDUCE martwy dla MU/LITE/COST/META przy ALLOC ≤ 0,10 | ryzyko-i-sizing.md; ryzyko_extra_out.md | równe wagi, jedna liczba ALLOC, skalowanie całego koszyka |
| Bramka Pulsu i protokół cenowy | REDUCE → reszta okna +0,08 (t 0,03); EV ±0,15; po dniu ≤ −3 p.p. +1,43 w 3 sesje (t 2,7); stop zawsze pierwszy | audyt-regul; pq_quant §E; C7 | Puls bez decyzji cenowych (§9) |
| Stan 18.10 | ≈ 1,7 % nad progiem; P(kill 5 ses.) 52 % przy 0,24, 18 % przy 0,08; pon. 13:45 na księdze W7: 21 % | C9 | konstrukcja nie ratuje W8; migracja §12 |

---

## 2. Nowe liczby tej notatki

### 2.1 Konstrukcje na 209 oknach (`projektC_bt.py` §1)

Okna: ISO D0 → D5 (zamknięcie piątku → piątku), od 2022-10-21 (pierwsze okno z 250 sesjami bety). Sygnał: momentum 6M rel. (126 sesji, skip 5). Veta wspólne poza A0: S1 (σ60 > 3× mediany uniwersum), K13 (r10 ≤ −20 % → nie short). Koszty: 0,10 % nominału na zmienioną nogę + 6 %/rok od gross 2. Spread w p.p. (równe wagi, gross 2).

**Skład point-in-time** (uniwersum 103 dzisiejsze + 28 usuniętych, z datami JOIN/LEAVE; śr. 13,7 grup ≥ 3):

| konstrukcja | śr. | σ | t | Sharpe | hit | p5 | najgorszy | maxDD | netto | t netto | obrót nóg/tydz. | σ60_unit %/d | \|b_SOX net\| ex ante | b_SOX zreal. | R² czynn. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 (bez wet) | +0,69 | 7,18 | 1,40 | 0,70 | 54 % | −11,9 | −23,9 | −45 | +0,38 | 0,76 | 2,10 | 3,04 | 0,71 | +1,16 | 0,17 |
| **A** | +0,59 | 6,89 | 1,25 | 0,62 | 56 % | −10,4 | −23,9 | −57 | +0,27 | 0,57 | 2,33 | 2,87 | 0,71 | +1,08 | 0,17 |
| B (5 par) | +0,35 | 5,15 | 0,99 | 0,50 | 54 % | −7,5 | −17,8 | −50 | +0,02 | 0,06 | 2,59 | 2,12 | 0,44 | +0,53 | 0,15 |
| **E = B_cap05** | **+0,38** | **4,61** | 1,20 | 0,60 | 53 % | **−7,0** | **−12,7** | **−41** | +0,04 | 0,13 | 2,79 | 1,89 | **0,29** | **+0,31** | **0,06** |
| B_cap10 | +0,46 | 5,03 | 1,34 | 0,67 | 55 % | −7,3 | −15,7 | −39 | +0,13 | 0,38 | 2,60 | 2,06 | 0,41 | +0,51 | 0,13 |
| A_stag | +0,56 | 6,98 | 1,14 | 0,58 | 53 % | −10,2 | −21,7 | −54 | +0,26 | 0,52 | 1,83 | 2,87 | 0,70 | +1,05 | 0,18 |
| B_stag | +0,26 | 4,95 | 0,74 | 0,37 | 55 % | −8,5 | −16,4 | −42 | −0,05 | −0,14 | 1,90 | 2,11 | 0,44 | +0,57 | 0,15 |
| A_2x5 | +0,49 | 6,88 | 0,97 | 0,51 | 57 % | −11,1 | −22,2 | −53 | +0,19 | 0,37 | 1,75 | 2,70 | 0,67 | +1,14 | 0,19 |
| B_2x5 | +0,44 | 5,05 | 1,21 | 0,63 | 56 % | −8,1 | −15,6 | −40 | +0,14 | 0,38 | 1,84 | 1,96 | 0,42 | +0,65 | 0,18 |
| D_lo (A, cap 1,0) | +0,24 | 5,82 | 0,59 | 0,29 | 55 % | −9,8 | −19,2 | −58 | −0,10 | −0,24 | 2,62 | 2,54 | 0,51 | +0,63 | 0,09 |
| D_05 (A, cap 0,5) | +0,21 | 5,54 | 0,56 | 0,28 | 52 % | −9,8 | −17,9 | −50 | −0,13 | −0,34 | 2,83 | 2,40 | 0,32 | +0,45 | 0,05 |

**Skład dzisiejszy** (survivorship bias zawyża średnie wszystkich wariantów; różnice między wariantami są mniej obciążone):

| konstrukcja | śr. | σ | t | Sharpe | p5 | najgorszy | maxDD | netto | \|b_SOX net\| ex ante | b_SOX zreal. |
|---|---|---|---|---|---|---|---|---|---|---|
| A0 | +1,17 | 7,36 | 2,31 | 1,15 | −10,9 | −25,9 | −45 | +0,86 | 0,78 | +1,00 |
| **A** | +0,95 | 6,88 | 1,99 | 0,99 | −9,0 | −25,2 | −42 | +0,62 | 0,77 | +0,94 |
| B | +0,99 | 5,64 | 2,53 | 1,26 | −6,8 | −16,4 | −35 | +0,66 | 0,50 | +0,56 |
| **E = B_cap05** | **+0,82** | **5,05** | 2,35 | **1,17** | **−6,2** | **−13,4** | **−26** | +0,49 | **0,32** | **+0,27** |
| B_cap10 | +0,95 | 5,53 | 2,48 | 1,24 | −6,8 | −14,7 | −28 | +0,62 | 0,44 | +0,47 |
| A_stag | +1,13 | 6,95 | 2,34 | 1,17 | −8,8 | −23,0 | −47 | +0,83 | 0,76 | +1,00 |
| B_stag | +0,72 | 5,50 | 1,90 | 0,95 | −7,1 | −14,4 | −48 | +0,42 | 0,48 | +0,55 |
| D_lo | +0,81 | 6,26 | 1,87 | 0,93 | −8,6 | −20,8 | −38 | +0,47 | 0,57 | +0,54 |
| D_05 | +0,68 | 5,91 | 1,67 | 0,83 | −7,9 | −17,0 | −38 | +0,34 | 0,36 | +0,32 |

### 2.2 Różnice sparowane wobec A (`projektC_bt.py` §1b)

| wariant | Δ śr. PIT (t) | CI95 Δ PIT | σ-ratio PIT [CI95] | F p | Δ śr. dziś (t) | σ-ratio dziś | nóg wspólnych z A (na 10) |
|---|---|---|---|---|---|---|---|
| B | −0,24 (−0,81) | −0,82…+0,34 | 0,747 [0,67; 0,83] | < 10⁻⁴ | +0,04 (+0,13) | 0,821 | 5,0 |
| **E** | **−0,21 (−0,58)** | **−0,92…+0,50** | **0,669 [0,58; 0,78]** | **< 10⁻⁴** | **−0,12 (−0,35)** | **0,735** | 4,8 |
| B_cap10 | −0,13 (−0,42) | −0,74…+0,48 | 0,730 [0,65; 0,83] | < 10⁻⁴ | +0,00 (+0,01) | 0,804 | 5,0 |
| D_lo | −0,36 (−1,89) | −0,72…+0,01 | 0,844 [0,77; 0,92] | 0,015 | −0,14 (−0,88) | 0,910 | 9,4 |
| D_05 | −0,38 (−1,65) | −0,83…+0,07 | 0,805 [0,73; 0,89] | 0,002 | −0,26 (−1,11) | 0,860 | 8,7 |
| A_stag | −0,10 (−0,85) | −0,33…+0,13 | 1,003 | 0,97 | +0,18 (+1,60) | 1,011 | 9,0 |
| B_stag (vs B) | −0,09 (−0,87) | — | 0,954 | — | −0,26 (−1,42) | 0,975 | — |
| A_2x5 | −0,01 (−0,14) | −0,21…+0,18 | 0,999 | 0,99 | +0,11 (+1,07) | 0,981 | 10,0 |
| B_2x5 | −0,20 (−0,66) | −0,79…+0,40 | 0,715 | < 10⁻⁴ | −0,10 (−0,35) | 0,770 | 5,4 |

Odczyt: **redukcja σ jest jedyną różnicą, którą dane rozstrzygają** (CI σ-ratio E nie zawiera 1 w żadnym składzie); różnice średnich wszystkich wariantów mieszczą się w ±0,6 p.p. i w CI zawierają zero. Budżet czynnikowy przez wymianę nóg w A (D) kupuje mniej redukcji σ (0,80–0,84) za większy koszt średniej (−0,36…−0,38, t do −1,9) niż wybór par (E: 0,67 za −0,21). To rozstrzyga pytanie zadania „parowanie czy budżet b_SOX”: **parowanie z budżetem jako kryterium wyboru par**.

### 2.3 Lata i reżimy (`projektC_bt.py` §1c; średnia p.p./tydz., w nawiasie σ)

| konstrukcja (PIT) | 2022 | 2023 | 2024 | 2025 | 2026 | VIX > 20 (n 50) | VIX ≤ 20 (n 159) | SOX−NDX < −3 (n 19) | SOX−NDX > +3 (n 32) | poł. 1 | poł. 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | +0,45 (6,2) | −0,45 (5,8) | −0,04 (4,4) | +0,79 (5,0) | +2,52 (11,4) | +2,52 (7,0) | −0,01 (6,8) | **−5,14 (9,4)** | +4,97 (8,4) | −0,29 (5,3) | +1,47 (8,1) |
| B | −0,94 (4,9) | +0,26 (3,7) | −0,11 (3,7) | +1,21 (5,4) | +0,35 (7,6) | +1,79 (5,5) | −0,10 (5,0) | −4,08 (6,7) | +3,18 (5,6) | −0,15 (3,9) | +0,85 (6,1) |
| **E** | −0,94 (4,9) | +0,18 (3,6) | −0,13 (3,8) | +1,07 (5,3) | +0,81 (5,6) | +1,20 (5,1) | +0,13 (4,4) | **−1,91 (4,6)** | +2,39 (5,3) | −0,18 (3,9) | +0,94 (5,1) |
| D_lo | +0,45 (6,2) | −0,45 (5,8) | −0,06 (4,4) | +0,61 (5,0) | +0,96 (8,0) | +1,95 (5,9) | −0,30 (5,7) | −3,06 (7,6) | +2,72 (6,0) | −0,30 (5,3) | +0,77 (6,2) |

| konstrukcja (dziś) | 2022 | 2023 | 2024 | 2025 | 2026 | SOX−NDX < −3 (n 19) | SOX−NDX > +3 (n 32) |
|---|---|---|---|---|---|---|---|
| A | +0,40 (6,2) | −0,19 (3,9) | +1,18 (6,6) | +1,52 (6,2) | +1,53 (10,4) | **−5,55 (10,0)** | +5,31 (6,5) |
| B | +1,86 (3,8) | −0,12 (2,9) | +1,15 (5,4) | +1,49 (6,0) | +1,29 (8,1) | −3,46 (7,2) | +4,40 (5,4) |
| **E** | +1,86 (3,8) | −0,12 (2,9) | +1,36 (5,3) | +0,83 (5,6) | +1,03 (6,3) | **−0,80 (5,7)** | +3,08 (5,0) |

Co E oddaje: tygodnie, w których SOX bije NDX o > 3 p.p. (+2,4…+3,1 zamiast +5,0…+5,3), i rok 2026 na PIT (+0,81 vs +2,52 — rok trendu półprzewodników). Co E dostaje: w tygodniach typu W6/W7 (SOX−NDX < −3) strata **−0,8…−1,9 zamiast −5,1…−5,6 p.p.**, czyli przy ALLOC 0,08 ok. −0,4…−0,8 % kapitału zamiast −2,1…−2,2 %. To jest dokładnie wymiana, o którą prosi zadanie („usuń zakład czynnikowy”) — jej cena to ok. 0,1–0,2 p.p./tydz. średniej in-sample i do 0,5 p.p. w pesymistycznym końcu CI.

### 2.4 Dwie transze i liczba nóg — dlaczego NIE

| wariant | mechanizm | dziś: Δ (t) vs baza | PIT: Δ (t) | σ-ratio | obrót nóg/tydz. (baza) | wykonalność |
|---|---|---|---|---|---|---|
| A_stag (5 nóg, każda 2 tyg., wymiana 3/2) | wygładza datę sygnału | +0,18 (+1,60) | −0,10 (−0,85) | 1,00–1,01 | 1,73–1,83 (2,33) | tak (10 pozycji) |
| B_stag (5 par, każda 2 tyg.) | j.w. dla par | −0,26 (−1,42) | −0,09 (−0,87) | 0,95–0,98 | 1,73–1,90 (2,33–2,59) | tak |
| A_2x5 (10 nazw/stronę, pół wagi) | 2 pełne transze (pq_quant „nakł.”) | +0,11 (+1,07) | −0,01 (−0,14) | 0,98–1,00 | 1,54–1,75 | **nie**: 20 pozycji przy 0,04 → 9 nazw pomijanych |
| B_2x5 | j.w. dla par | −0,10 (−0,35) | −0,20 (−0,66) | 0,72–0,77 (vs A) | 1,66–1,84 | **nie** |

Wynik pq_quant (Sharpe 1,12 vs 0,99 dla 2×5 nakładających się) **nie przeżywa składu PIT** (0,51 vs 0,62) i nie przenosi się na wariant z 5 nogami. Oszczędność obrotu 0,4–0,7 nogi/tydz. to przy ALLOC 0,08 ok. 0,005 % kapitału tygodniowo. Transze dodają stan do pilnowania przez rutynę (która para jest w drugim tygodniu) i rozmywają rozliczenie „od D0” — **decyzja: 1 tydzień, pełna rotacja**. Liczba nóg: N = 10/stronę obniża Sharpe (0,66 vs 0,99, pq_quant §B), bo sygnał momentum siedzi w ogonach rankingu; 5/5 zostaje.

### 2.5 Veto cenowe i loty (`projektC_bt.py` §2–3; kursy 2026-10-16, kapitał odniesienia 1 000 USD, krok 0,1 akcji, `MAX_OVERSHOOT` 1,6)

| pozycji | ALLOC/pozycję | cel USD | pomijane (0,1 akcji > 1,6 × cel) | przestrzał (lot w (cel; 1,6 cel]) |
|---|---|---|---|---|
| 10 | 0,12 | 120 | 0 | ASML MELI MPWR SNDK |
| 10 | 0,10 | 100 | ASML MELI | MPWR SNDK |
| **10** | **0,08** | **80** | **ASML MELI SNDK** | **COST LITE MPWR MU** |
| 10 | 0,06 | 60 | ASML COST MELI MPWR SNDK | LITE META MU REGN STX |
| 20 | 0,05 | 50 | ASML COST LITE MELI MPWR MU SNDK | AMD IDXX META MSFT REGN STX |
| 20 | 0,04 | 40 | ASML COST LITE MELI META MPWR MU REGN SNDK (9) | 10 nazw |

| konstrukcja | veto | Δ vs bez veta (t) | udział nóg wyciętych nazw |
|---|---|---|---|
| A | > 1 280 USD (ASML MELI SNDK) | +0,04 (+1,50) | 2,2 % |
| B | > 1 280 USD | +0,03 (+0,66) | 2,1 % |
| B | > 960 USD (+ COST MPWR) | +0,01 (+0,15) | 2,4 % |

Veto cenowe **nic nie kosztuje** (Δ ≥ 0, t ≤ 1,5) i zamienia „noga pominięta przez bota z komunikatem” na „noga nigdy nie wybrana” — koszyk na rachunku = koszyk w `signals.json`. Nazwy w przestrzale (COST LITE MPWR MU przy 0,08) wchodzą jako jeden lot 0,1 akcji = 99–121 USD zamiast 80 USD (przestrzał 1,2–1,5×) — to pozostaje, bo veto do 960 USD (wyciąłoby COST i MPWR) nie ma mierzalnego kosztu, ale i zysku; **decyzja: próg 1 280 USD** (dopasowany do ALLOC 0,08; przy zmianie ALLOC przeliczyć: `MAX_PRICE_USD = 1,6 × ALLOC × START_EQUITY / 0,1`).

### 2.6 Wrażliwość E na definicję grupy (`projektC_dod.py` §C)

| definicja grupy | PIT: śr. / σ / Sharpe / Δ vs A (t) / σ-ratio / b_SOX | dziś: śr. / σ / Sharpe / Δ (t) / σ-ratio / b_SOX |
|---|---|---|---|
| **base: industry ≥ 4 \| sector, grupa ≥ 3** | +0,38 / 4,61 / 0,60 / −0,21 (−0,58) / **0,669** / +0,31 | +0,82 / 5,05 / 1,17 / −0,12 (−0,35) / **0,735** / +0,27 |
| industry ≥ 2 \| sector | +0,27 / 4,23 / 0,46 / −0,33 (−0,86) / 0,614 / +0,20 | +0,39 / 4,50 / 0,62 / −0,56 (−1,38) / 0,654 / +0,16 |
| industry ≥ 6 \| sector | +0,41 / 4,67 / 0,63 / −0,19 (−0,52) / 0,679 / +0,34 | +0,54 / 4,78 / 0,82 / −0,40 (−1,18) / 0,695 / +0,23 |
| grupa ≥ 5 | +0,30 / 4,08 / 0,54 / −0,29 (−0,76) / 0,592 / +0,15 | +0,77 / 5,24 / 1,06 / −0,18 (−0,47) / 0,762 / +0,05 |
| sector-only | +0,23 / 4,36 / 0,37 / −0,37 (−1,03) / 0,633 / +0,23 | +0,55 / 4,58 / 0,86 / −0,40 (−1,14) / 0,667 / +0,21 |

Redukcja σ (0,59–0,76) i b_SOX (0,05–0,34) są odporne na definicję; średnia **nie** (Δ −0,12…−0,56). Definicja base jest najlepsza dla średniej w obu składach, co jest też jej słabością (C2: „efekt wyboru definicji”). **Decyzja: zamrozić base** (ta sama, która jest już w `ranking.py`: `MIN_IND 4, MIN_GROUP 3`) i planować z kosztem średniej do −0,5 p.p./tydz.

### 2.7 Koszyki na D0 2026-10-16 (`projektC_bt.py` §5; zgodne z `projektA_ranking_W8.json`)

| koszyk | LONG | SHORT | σ60_unit %/d | b_SOX net | grupy |
|---|---|---|---|---|---|
| A | CRWD DDOG PANW FTNT AMD | NFLX FER APP ALNY CMCSA | 3,59 | +0,40 | — |
| B | CRWD AMD FTNT SNDK TRI | APP AVGO PAYX AXON NFLX | 2,66 | +0,70 | Packaged Software, Semiconductors, Technology Services, Electronic Technology, Internet Soft. |
| **E** | **CRWD AMD FTNT TRI ABNB** | **APP AVGO PAYX NFLX CMCSA** | **1,94** | **+0,18** | Packaged Software, Semiconductors, Technology Services, Internet Soft., Consumer Services |
| FAKT W8 (Model 3.0) | GOOGL GILD MSFT QCOM ADP | AXON DASH ALNY APP FER | 1,85 | +0,05 | — |

Uwaga: W8 faktyczny ma dziś (przypadkiem albo przez niejawną zmianę scoringu — moc-predykcyjna-modelu.md) ryzyko podobne do E. Tydzień wcześniej (D0 09.10) same pary B miały b_SOX **+1,40** (ALAB long / AVGO short w jednej grupie) — to jest powód, dla którego budżet SOX jest częścią konstrukcji, a nie adnotacją.

---

## 3. Konstrukcja E — definicja operacyjna (parametry zamrożone 18.10.2026)

| krok | definicja | parametr (`scripts/ranking.py`) | uzasadnienie |
|---|---|---|---|
| 1. uniwersum | klucze `signals.json["epics"]` z ≥ 132 sesjami historii; lista „do weryfikacji” z TV tylko sygnalizuje różnice składu | `MIN_HISTORY` | CLAUDE.md: epics = uniwersum |
| 2. dane | zamknięcia dzienne z `kursy.py` (zakres `1y` → ok. 251 sesji; beta 250 liczona z dostępnych par ≥ 125) + ^NDX, ^SOX, XLP, XLU, XLV, QQQ; cache `data/ranking-cache.csv` | `--fetch` | kursy.py źródłem nr 1 (bez zmian); **zalecenie (bez dowodu)**: zakres `2y`, żeby beta zawsze miała pełne 250 sesji |
| 3. sygnał | `mom6_rel = P[d0−5]/P[d0−131] − 1 − (^NDX analogicznie)` | `MOM_WIN 126, MOM_SKIP 5` | C1 (szczyt siatki → optymistyczne) |
| 4. veta | S1: σ60 > 3× mediany → poza obu stronami; K13: r10 ≤ −20 % → poza SHORT; **EVENT**: raport w D+1…D+5 (kalendarz FMP → TV; data niepotwierdzona = veto) → poza obu stronami; **cena**: `close > MAX_PRICE_USD` → poza obu stronami; wyjątki imienne z `reguly.md` | `SIGMA_VETO_MULT 3.0`, `SHORT_VETO_R10 −0.20`, `EVENT_WINDOW_DAYS 7`, **nowy `MAX_PRICE_USD 1280`** | S1/K13: projekt A §3.1 (koszt ≈ 0, K13 t −2,42); EVENT: **bez dowodu — decyzja o ogonie**; cena: §2.5 (Δ ≥ 0) |
| 5. grupy | industry TV, jeśli ≥ 4 spółek uniwersum ma tę industry; inaczej sector; grupa < 3 → „Pozostałe” (bez par); taksonomia ze **snapshotu tej soboty** `data/tv-screen-<version>.json`; brak snapshotu → poprzedni (adnotacja) | `MIN_IND 4, MIN_GROUP 3` (`grupy()`) | §2.6: jedyna definicja z Δ ≈ 0 w C2 i najlepsza tu; każda inna zmienia średnią o −0,1…−0,4 |
| 6. kandydaci par | w każdej grupie: long = najwyższe mom6 wśród kandydatów LONG, short = najniższe wśród kandydatów SHORT (long ≠ short); rozstęp = mom6(long) − mom6(short); **8 par o największym rozstępie** | `konstrukcja_pary` (istnieje), **nowy `PAIR_POOL 8`** | top-8 = pula testowana w §2 (56 podzbiorów) |
| 7. budżet SOX | spośród C(8,5) = 56 piątek wybierz tę o **największej sumie rozstępów**, dla której \|śr. b_SOX(L) − śr. b_SOX(S)\| ≤ 0,5 (b_SOX = beta dziennych zwrotów spółki na SOX−NDX, 250 sesji); gdy żadna nie spełnia → piątka o najmniejszym \|b_SOX net\| | **nowa `konstrukcja_pary_budzet`**, `FACTOR_BUDGET 0.5` (istnieje), `PAIR_POOL 8` | §2.1–2.3: b_SOX zreal. 0,27–0,31, SOX<−3: −0,8…−1,9; cap 1,0 słabiej (0,47–0,51) |
| 8. wagi i horyzont | 5 LONG + 5 SHORT, równe wagi, 1 tydzień; pełna rotacja co sobotę (noga kontynuowana zachowuje `fills.cena` — bot od 12.10) | — | §2.4; bt_neutralnosc (nierówne strony = net-short NDX) |
| 9. b_DEF | **tylko adnotacja** (\|b_DEF net\| w raporcie), bez budżetu | — | nie testowano jako kryterium wyboru par; D z budżetem DEF kosztował średnią (projekt A) |
| 10. wyjście | `data/ranking-<version>.json["konstrukcje"]["E_pary_budzet_sox"] = {long, short, pary[], b_sox_net, pula_par[], wybor:"budzet"|"min_b"}` + `ryzyko` jak dla A–D; tabela MD; **skrypt nie dotyka `signals.json`**; rutyna przepisuje E do `long/short` | `--out`, `--md` | odtwarzalność (hash pliku w raporcie) |

**Czego E nie robi (świadomie):** nie neutralizuje β do ^NDX (zwroty rozliczane względem ^NDX, strony równe → β net ≈ 0 strukturalnie; przewaga dolarowa shortów szkodzi: e_beta Δ −0,45…−0,90); nie waży nóg 1/σ (loty); nie robi hedge'u indeksowego (osobna decyzja o finansowaniu trzeciej nogi; przy b_SOX 0,3 traci na wadze); nie stosuje żadnej reguły spoza `reguly.md` OBOWIĄZUJĄCE.

**Nakładka uznaniowa:** w projekcie C **domyślnie brak** (koszyk = E). Jeżeli właściciel przyjmie nakładkę z projektu A (N1–N5: ≤ 1 wymiana/stronę z rang 6–15), musi ona respektować pary: wymiana nogi = wymiana **całej pary** na kolejną z puli 8 spełniającą budżet — inaczej budżet SOX i parowanie przestają istnieć. Koszt mierzalny jak Δ(FAKT − E).

---

## 4. Sizing i ryzyko kapitału dla E

### 4.1 Dlaczego stałe ALLOC, nie vol-target

Vol-target `ALLOC = clip(0,015/(5·σ60_unit), 0,04, 0,12)` ma sens dla A (σ60_unit mediana 2,9 %/d, w 2026 do 4,6 %: ALLOC mediana 0,12, w 2026 0,058, p5 0,052). Dla E σ60_unit ≈ 1,9 %/d, więc reguła daje **0,12 w 98 % tygodni** (projektC_bt §4b) — to stała 0,12 z dodatkową złożonością (nowe pole, walidator, `_sanity`). Zamiast tego: **stałe ALLOC 0,08** (parametr Rendera, bez pola w `signals.json`) i próg miękki.

| polityka (E, PIT, koszty wliczone) | alfa | P(kill 12) | P(kill 26) | P(kill 52) | maxDD 52: mediana / p95 | kapitał po 52: p5 / med / p95 |
|---|---|---|---|---|---|---|
| stałe 0,08 | 0 | 0,0 % | — | **8,1 %** | −14 % / −25 % | 0,76 / 0,94 / 1,16 |
| stałe 0,08 | in-sample (+0,38) | 0,0 % | — | 2,2 % | −11 % / −22 % | 0,83 / 1,02 / 1,25 |
| **stałe 0,08 + soft −10 %/−5 % (×0,5)** | 0 | **0,0 %** | **0,0 %** | **0,2 %** | — | — |
| stałe 0,08 + soft | in-sample | 0,0 % | 0,0 % | 0,0 % | — | — |
| stałe 0,10 | 0 | 0,1 % | 3,1 % | 19,1 % | — | — |
| stałe 0,10 + soft | 0 | 0,0 % | 0,1 % | 2,1 % | — | — |
| stałe 0,12 | 0 | 0,5 % | — | 33,0 % | −21 % / −28 % | 0,74 / 0,90 / 1,23 |
| vol-target 1,5 %/d (≈ 0,12) | 0 | 0,2 % | — | 32,8 % | −21 % / −28 % | — |
| vol-target 1,5 %/d + soft | 0 | 0,0 % | — | 6,1 % | −16 % / −25 % | — |
| vol-target 1,0 %/d | 0 | 0,0 % | 2,5 % | 21,8 % | — | — |
| dla porównania A stałe 0,08 | 0 | 0,8 % | — | 30,2 % | −20 % / −28 % | 0,74 / 0,94 / 1,31 |
| dla porównania A vt + soft | 0 | 0,0 % | — | 17,2 % | −18 % / −26 % | 0,75 / 0,91 / 1,24 |

Źródło: projektC_bt §4, projektC_dod §A (bootstrap blokowy, blok 4 tyg., 3 000–5 000 ścieżek). Na składzie dzisiejszym liczby są o 1–4 p.p. wyższe (0,08: 9,5 %; 0,10: 23,1 %; 0,08 + soft: 0,2 %).

### 4.2 Przekład na kapitał (E, PIT)

| ALLOC | gross | σ tyg. kapitału | σ dz. (≈ σ tyg./√5) | μ tyg. brutto in-sample | koszt tyg. (finansowanie + rotacja) | μ tyg. netto in-sample / alfa 0 |
|---|---|---|---|---|---|---|
| **0,08** | **80 %** | **1,84 %** | **0,82 %** | +0,153 % | 0,115 % (0,092 + 0,022) | **+0,04 % / −0,115 %** |
| 0,10 | 100 % | 2,30 % | 1,03 % | +0,191 % | 0,143 % | +0,05 % / −0,14 % |
| 0,12 | 120 % | 2,77 % | 1,24 % | +0,230 % | 0,172 % | +0,06 % / −0,17 % |

Jednostki: 1 p.p. spreadu = 5 × ALLOC % kapitału (0,08 → 0,4 %). Obrót E 2,79 nogi/tydz. (A 2,33) — koszt rotacji 0,022 %/tydz., finansowanie dominuje (6 %/rok × gross; stawka parametryczna — faktyczne stawki Capital.com nieodczytane, perspektywa-quant.md). **Wniosek o zysku:** przy alfie 0 system traci ~6 %/rok w kosztach; in-sample PIT zarabia ~2 %/rok; in-sample na składzie dzisiejszym ~13 %/rok (+0,26 %/tydz.). Żadnej z tych liczb nie da się odróżnić od pozostałych wcześniej niż po setkach tygodni (σ tyg. 1,84 % → t = 2 dla +0,1 %/tydz. po ~1 350 tygodniach).

### 4.3 Próg miękki (`DD_SOFT`) — jedyna zmiana w `app.py` wymagana przez projekt C

`soft_factor = 0,5`, gdy `equity/equity_peak < 0,90`, aż `equity/equity_peak > 0,95` (wyrównanie w biegu 17:05, stan w `wykonanie.soft = {"aktywny": bool, "od": "RRRR-MM-DD"}` — pole bota). Liczba: P(kill 52 tyg., alfa 0) 8,1 % → 0,2 %; koszt in-sample: brak osobnej liczby dla E (dla A: ~0,08 %/tydz. kapitału, projektA_boot) — **bez dowodu co do kosztu, z dowodem co do P(kill)**. Zgodne z projektem A §5 (ten sam mechanizm), więc wdrożenie jest wspólne.

### 4.4 Stop i reopen

Niezmienione wobec rekomendacji wspólnych faz 1–2 (stop w σ, bez reopen, kotwica `fills.cena` — projekt A §6, C3): przy E nogi są mniej skrajne (σ60 nóg niższa), więc stały stop 10 % zadziała rzadziej niż na A; nie jest to element konstrukcji. Do czasu zmiany kodu: `STOP_LOSS_PCT 0.10` zostaje (koszt −0,04 p.p./tydz. na PIT, C3/projekt A).

---

## 5. Jak rutyna sobotnia liczy E (KROK B po zmianie)

| krok | treść | wejście | wyjście |
|---|---|---|---|
| B-0 | snapshot screenera `run-screener` wg `rutyny/tv-zestaw-b1.json` → `data/tv-screen-<version>.json` (commit PRZED rankingiem); brak/429 → poprzedni snapshot + adnotacja „taksonomia z <version−1>” | TV (1 wywołanie) | plik snapshotu |
| B-1 | kalendarz wyników: FMP `earnings-calendar` dla całego uniwersum (lub TOP/BOTTOM 30 wg wstępnego rankingu); TV `get-earnings-calendar` drugie (≤ 2 wywołania); `next_date_confirmed=false` → data = veto | FMP/TV | `<scratch>/earnings.json` `{ticker: "RRRR-MM-DD"}` |
| B-2 | `python3 scripts/ranking.py --fetch --tv data/tv-screen-<version>.json --earnings <scratch>/earnings.json --exclude <WYJĄTKI z reguly.md> --out data/ranking-<version>.json --md <scratch>/ranking.md` | kursy.py 1y (cache), snapshot, kalendarz | JSON z konstrukcjami A/B/C/D/**E**, `sizing` informacyjnie, ryzyko (σ60_unit, percentyl vs 1000 losowych, ρ60, b_SOX/b_DEF/β net) |
| B-3 | **koszyk bota = `konstrukcje.E_pary_budzet_sox`**: `long`, `short` do `signals.json`; `d0.prices` z `kursy.py` dla tych 10 nazw (walidacja 0,5 % jak dziś); `status` wg B0 | JSON | pola soboty |
| B-4 | kontrola: 5 par (każda z inną grupą), \|b_SOX net\| ≤ 0,5 albo `wybor:"min_b"` z adnotacją; brak spółki > `MAX_PRICE_USD`; brak nogi z vetem; gdy skrypt zwróci < 5 par (za mało grup po wetach) → **koszyk poprzedniej soboty zostaje** (`version` bez zmiany, raport z PROBLEMY) — **bez dowodu — decyzja o bezpieczeństwie** | JSON | lista kontrolna w raporcie |
| B-5 | raport: tabela par (grupa, long, short, mom6 obu, rozstęp, b_SOX obu), b_SOX net / b_DEF net / β net koszyka (adnotacja), σ60_unit i percentyl vs losowe, σ dz. kapitału przy ALLOC z Rendera (`/status.ustawienia.alloc_pct`), pula 8 par z zaznaczeniem wybranych, veta które wiązały (S1/K13/EVENT/cena) z nazwami | JSON | HTML |

Czas: ranking.py ~10 s; TV ≤ 4 wywołania (screener, 2× earnings, ohlcv NDX/VIX do reżimu jak dziś). Skreślone z KROKU B: B1 scoring/benchmark ręczny, B2 (20 czynników), B3 (elita), B4 (p, pre-mortem) — zgodnie z projektem A; tu dodatkowo: kryterium remisu „bez raportu w oknie” staje się vetem EVENT (jak projekt A).

**Rutyna nie liczy nic ręcznie**: cała arytmetyka par i budżetu jest w skrypcie (testy w `scripts/test_ranking.py`), rutyna przepisuje i kontroluje.

---

## 6. Test na papierze obok faktycznego koszyka

### 6.1 Koszyki cienie (co sobotę, `scripts/koszyki_cienie.py`, `data/koszyki-cienie.jsonl`)

| cień | po co | metryka |
|---|---|---|
| **E** (koszyk bota) | baza rachunku | spread od D0 i od `fills`; σ zreal. vs σ60_unit ex ante |
| **A** (TOP5/BOTTOM5 z wetami) | koszt konstrukcji E = Δ(E − A) i **σ-ratio E/A** | test F po 26/52 oknach; Δ tylko jako CI |
| A0 (bez wet) | koszt wet S1/K13 | Δ(A − A0) po 26 |
| **B** (pary bez budżetu) | wkład budżetu SOX = Δ(E − B), b_SOX_E vs b_SOX_B | regresja zrealizowana po 26 oknach |
| D (A + budżet) | H5 z `reguly.md` | σ-ratio D/A vs oczekiwane 0,80–0,84 |
| ETF SMH/XLP | czynnik taniej | Δ(E − ETF) po 52 |
| E bez veta EVENT; E bez veta cenowego | koszt wet konstrukcyjnych | Δ po 26 |
| FAKT (jeśli nakładka) | nakładka | Δ(FAKT − E) |

`koszyki_cienie.py` już rozlicza wszystkie `konstrukcje` z JSON-u — dopisanie E do `policz()` wystarcza; warianty „bez veta” wymagają dwóch dodatkowych kluczy w JSON (`E_bez_event`, `E_bez_ceny`) liczonych przez `ranking.py` z flagami.

### 6.2 Moc testów (`projektC_dod.py` §B; bootstrap par tygodni A/E na PIT, blok 4)

| tygodni cieni | P(F-test σ_E < σ_A, p < 0,05) | P(σ-ratio < 0,85) | mediana σ-ratio | p5–p95 σ-ratio | P(t(Δ) < −2 przy prawdziwej Δ −0,21) |
|---|---|---|---|---|---|
| 12 | 22 % | 68 % | 0,72 | 0,40–1,24 | 3,5 % |
| 26 | 47 % | 80 % | 0,69 | 0,47–1,03 | 3,7 % |
| 52 | 74 % | 90 % | 0,68 | 0,52–0,91 | 4,1 % |

σ sparowanej różnicy Δ(E − A) = 5,21 p.p./tydz. → tygodni do t = 2 przy prawdziwej Δ 0,3 / 0,5 / 1,0 p.p.: **1 204 / 433 / 108**. Wniosek: o średniej **nie rozstrzygamy nigdy** w horyzoncie projektu; o σ — z 47 % mocy po 26 i 74 % po 52 tygodniach.

### 6.3 Prerejestrowane metryki (stała kolejność w raporcie, nic nie dopisujemy)

1. `spread_pp` od D0 i `spread_fills_pp` od wejścia dla E; narastająco: suma, średnia, σ, t, n.
2. σ-ratio E/A narastająco (z F p) i Δ(E − A) z CI95 — **bez interpretacji średniej przed 52 oknami**.
3. b_SOX zrealizowane E i A (regresja tygodniowa narastająco od ≥ 12 okien) oraz ex ante b_SOX net koszyka tygodnia; udział czynnika w wyniku tygodnia (dekompozycja 3f).
4. Najgorszy tydzień i p5 narastająco vs oczekiwane (E: −12,7 / −7,0; A: −23,9 / −10,4).
5. σ zrealizowana tyg. kapitału vs oczekiwane 1,84 % (przy 0,08); DD od szczytu; stan `soft`.
6. Pokrycie rachunku: nogi E na rachunku 10/10? (`/status.pokrycie_koszyka`), nogi w przestrzale lotu, `koszt_wykonania_pp = wynik rachunku % − 5·ALLOC·spread_fills_pp` (tylko w raporcie, nigdy w repo).
7. Veta, które wiązały (S1/K13/EVENT/cena, nazwy) i `wybor` budżetu (budzet / min_b) z \|b_SOX net\|.
8. Zdanie o mocy: „po n tygodniach test F wykrywa σ-ratio ≤ …; test średniej wykrywa \|Δ\| ≥ 2·5,21/√n”.

### 6.4 Kryteria decyzji

| horyzont | wolno rozstrzygnąć | kryterium | działanie |
|---|---|---|---|
| **12 okien** (ok. 16.01.2027) | wykonanie i kalibracja | σ zreal. kapitału w [0,7; 1,4] × 1,84 %; pokrycie 10/10 w ≥ 10/12 tygodni; mediana `koszt_wykonania_pp`; `wybor:"min_b"` ≤ 3/12 | tylko korekty wykonania (np. `MAX_PRICE_USD`, zakres danych); **żadnej zmiany konstrukcji** |
| **26 okien** (kwiecień 2027) | σ i czynnik | σ-ratio E/A ≤ 0,85 (oczekiwane 0,69; p95 1,03) **i** b_SOX_E < b_SOX_A; koszt wet konstrukcyjnych Δ(E − E_bez_EVENT) t ≤ −1,5 → przegląd EVENT | σ-ratio > 1,03 (poza p95) → E nie robi tego, co ma robić → powrót do A z ALLOC 0,06 (**decyzja**) |
| **52 okna** (październik 2027) | σ (moc 74 %), średnia tylko jako CI | σ-ratio ≤ 0,91 (p95) potwierdza; CI95 Δ(E − A); CI95 średniej E netto | górna granica CI średniej E < 0 → system na papier / ETF (decyzja właściciela); Δ(E − A) z t ≤ −2 (możliwe tylko przy Δ ≤ −1,4) → A z niższym ALLOC |

Nigdy: zmiana `MIN_IND/MIN_GROUP/PAIR_POOL/FACTOR_BUDGET` po złym tygodniu; zmiana ALLOC o > 0,02 na 4 tygodnie; wprowadzenie reguły poza `reguly.md`.

---

## 7. Dlaczego nie inne konstrukcje (krótko)

| konstrukcja | argument za | liczba przeciw | decyzja |
|---|---|---|---|
| A (czyste momentum) + vol-target | najwyższa średnia (PIT +0,59, dziś +0,95) | b_SOX 0,94–1,08, najgorszy −24…−25, SOX<−3: −5,1…−5,6; ALLOC z vt w 2026 0,058 (gross 58 %) — niższa ekspozycja na lepszy sygnał | cień (projekt A ma ją jako koszyk; różnica między projektami to wybór σ vs średnia) |
| B (pary bez budżetu) | Δ ≈ 0 dziś, Sharpe 1,26 | b_SOX 0,53–0,56; na D0 09.10 b_SOX **+1,40**; PIT Δ −0,24 przy σ-ratio 0,75 (gorszy stosunek niż E) | cień |
| B_cap10 (budżet 1,0) | Δ 0,00 dziś, −0,13 PIT | b_SOX 0,47–0,51, SOX<−3 −2,4…−3,6 — połowa efektu E | odrzucona (wariant pośredni bez własnej zalety) |
| D (budżet na A) | ten sam cel co E | σ-ratio 0,80–0,84 za Δ −0,36…−0,54 (t do −2,36) | cień (H5) |
| C (≤ 1 L + 1 S z grupy) | σ −20 % | Δ −0,26…−0,45 w 6/6 definicji (C2) | cień |
| transze / 2×5 / N = 10 | obrót, wygładzenie | §2.4 | odrzucone |
| risk parity, beta-neutral przez wagi | — | net-short NDX, Δ −0,45…−0,90 | odrzucone |
| hedge indeksowy (HEDGE_EPIC) | ubezpieczenie ogona | nietestowany; przy b_SOX 0,3 i β net ≈ 0 koszt finansowania trzeciej nogi bez przedmiotu | nie w C |

---

## 8. Puls dzienny — ocena

**Czy obecny Puls jest potrzebny? Jako decydent — nie. Jako kontrola — tak, w mniejszej dawce.**

| funkcja Pulsu dziś | dowód | decyzja |
|---|---|---|
| wyzwalacze cenowe 4 %/8 % (REDUCE/CLOSE basis `cena`, 2 sesje, blokada sektorowa) | REDUCE → reszta okna +0,08 p.p. (n 3442, t 0,03); autokorelacja dziennego spreadu lag1 −0,01, lag2 −0,02; po dniu ≤ −3 p.p. kolejne 3 sesje **+1,43 (t 2,7)**; EV ±0,15; P(kill) 32,6 → 31,2 %; w W6–W7 stop bota zawsze pierwszy; in-sample W1–W4 −3,44 p.p. | **usunięte** jako wyzwalacz; zostaje **pomiar** „co zrobiłby protokół” w KONTROLI BRAMKI (seria do raportu cieni) |
| REDUCE przy P1 | bramka P0/P1/P2 obniża średnią 1,00 → 0,78 bez poprawy maxDD; P1 to najlepsze tygodnie (+3,04, t 2,0) | usunięte; P1 = flaga |
| wyzwalacze newsowe (lista zamknięta R3) | ryzyko ogonowe; 3 użycia +0,69 na papierze; przy E pojedyncza noga = 8 % kapitału → szok −30 % nogi = −2,4 % kapitału | **zostaje** (basis `news` z dokumentem źródłowym) |
| wyłącznik płynności (sesja ≤ −5 %, VIX > 40) | bez dowodu — decyzja o płynności (projekt A §7.2) | zostaje |
| moduł taktyczny | n = 4, 20 % kapitału/noga bez testu (perspektywa-quant) | zawieszony (`tactical=[]`) — jak projekt A |
| kontrola rachunku `/status` (pokrycie 10/10, `kontrola_kapitalu`, `EKSPOZYCJA_NIEPELNA`) | 12.10: podwójne wejście 13:45/17:05, PEP/TMUS dopiero o 17:05 (wykonanie-bota.md) — wykryte tylko dzięki raportom | **zostaje — główna racja Pulsu** |
| flaga EVENT, kalendarz, pre-market | wejście do veta EVENT w sobotę (data niepotwierdzona) | zostaje w wersji minimalnej (1 wywołanie TV) |
| research elity, FINRA, makro, panel fundamentów | IC scoringu ≈ 0; budżet TV przekraczany (36 vs 20 min) | skreślone |

Skala ryzyka, na którą Puls miałby reagować, przy E i ALLOC 0,08: σ dz. kapitału ≈ 0,8 %; ruch 4 % jednej nogi = 0,32 % kapitału; 8 % = 0,64 %. Decyzja dzienna o takiej skali nie ma czego chronić, a jej EV ≈ 0.

**Częstotliwość (bez dowodu — decyzja):** 3 biegi/tydz. — **poniedziałek** (obowiązkowy: stan sprzed/po rotacji, pokrycie nowych 10 nóg, przestrzały lotów), **środa** i **piątek** (pokrycie, newsy z listy zamkniętej, EVENT na sobotę). Alternatywa: codziennie w wersji kontrolnej (≈ 8 wywołań TV, 10 min) — projekt A. Argument za 3×: bot i tak biega 2× dziennie i wysyła powiadomienia; Puls nie składa zleceń; koszt pominięcia dnia = opóźnienie wyzwalacza newsowego o ≤ 48 h (3 użycia w 8 tygodni). Argument za codziennie: wyzwalacz newsowy R3 i wyłącznik płynności nie mają innego nośnika niż Puls. **Rekomendacja: 3×/tydz. z możliwością biegu ręcznego przy zdarzeniu z listy R3.**

---

## 9. `signals.json`, walidator, `_sanity` — dokładnie

**Zasada projektu C: zero nowych pól top-level.** E ma 5/5 nóg o równych wagach, ALLOC jest stałe w Renderze, próg miękki to stan bota w `wykonanie`. Dzięki temu:

| plik | zmiana | czy konieczna |
|---|---|---|
| `scripts/waliduj_signals.py` | (1) **opcjonalnie** wpis `history` z polem `"konstrukcja": "E"` (i `"b_sox_net": liczba`) — walidator już przepuszcza dodatkowe pola wpisu (`brak = HISTORY_POLA − keys`), ale dla jawności dodać `HISTORY_POLA_OPCJONALNE = {"dane_b1", "sesje", "konstrukcja", "b_sox_net"}` i kontrolę: `set(h1[-1]) − HISTORY_POLA − HISTORY_POLA_OPCJONALNE == ∅`, `konstrukcja ∈ {"A","E","FAKT"}`, `−3 ≤ b_sox_net ≤ 3`; (2) `BASIS` dla **nowych** wpisów `exclude` zawężone do `{"news", "rezim", "reżim"}` (stare `cena` w bazie tolerowane) — jak projekt A #8; (3) testy +3 | (1) zalecana, (2) spójna z §8 |
| `app.py::_sanity` | **bez zmian** (nie czyta `history`; 5/5, epics, status, exclude, tactical, fills jak dziś) | — |
| `app.py::sync()` | **próg miękki**: po `alloc = ALLOC_PCT if zgodne else ALLOC_PCT_SAFE` → `soft = (equity/odniesienie < 1 − DD_SOFT) or (wykonanie.soft.aktywny and equity/odniesienie < 1 − DD_SOFT_RESET)`; `alloc *= DD_SOFT_FACTOR if soft`; `wykonanie["soft"] = {"aktywny": soft, "od": data}` zapisywane razem z `fills` (ten sam commit bota); `/status.ustawienia` + `soft`, `alloc_efektywny`. Zmienne: `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `DD_SOFT_FACTOR=0.5`. Wyrównanie w dół natychmiast (13:45 lub 17:05), w górę tylko w biegu 17:05 (REBALANCE_HOURS) | tak (P(kill 52) 8,1 → 0,2 %) |
| `scripts/test_app.py` | testy: soft on/off/reset, zapis `wykonanie.soft`, `_sanity` bez zmian przechodzi plik z `history[-1].konstrukcja` | tak |
| CLAUDE.md | „Co wolno”: wpis `history` może mieć `konstrukcja`, `b_sox_net`; `wykonanie` ma podklucz bota `soft`; tabela `/status`: `soft`, `alloc_efektywny`; akapit „Koszyk = `ranking.py` konstrukcja E; `data/ranking-*.json`, `koszyki-cienie.jsonl` bez liczb z rachunku” | tak |

Jeżeli właściciel mimo wszystko wybierze vol-target (projekt A, pole `sizing`), projekt C jest z nim zgodny: dla E pole będzie niemal zawsze równe sufitowi, więc sufit `ALLOC_PCT` w Renderze należy wtedy ustawić na 0,08, nie 0,12.

---

## 10. Pełna lista zmian w plikach (z właścicielem)

| # | plik | zmiana | właściciel |
|---|---|---|---|
| 1 | `scripts/ranking.py` | nowa `konstrukcja_pary_budzet(score, grupa, kandyd_l, kandyd_s, bety, n=5, pula=PAIR_POOL, cap=FACTOR_BUDGET)` (algorytm §3 krok 6–7: 8 par → 56 podzbiorów → max suma rozstępów przy \|b_SOX net\| ≤ 0,5, inaczej min \|b\|); parametry `PAIR_POOL = 8`, `MAX_PRICE_USD = 1280.0` (veto obu stron, `--max-price` nadpisuje; `0` wyłącza); `policz()` dopisuje `konstrukcje["E_pary_budzet_sox"]` = `{long, short, pary[{grupa, long, short, mom_long, mom_short, roznica_mom, b_sox_long, b_sox_short}], b_sox_net, b_def_net, pula_par[8], wybor, ryzyko}` oraz `E_bez_event`, `E_bez_ceny` (dla cieni); `veto_long/veto_short` dostają wpis „cena > 1280 USD”; `tabela_md` sekcja par; opcjonalnie `--zakres 2y` w `pobierz_1y` | kod app.py |
| 2 | `scripts/test_ranking.py` | +6 testów: budżet spełniony → wybór o maks. sumie rozstępów; budżet niespełnialny → `wybor:"min_b"`; każda para z inną grupą; long ≠ short; veto cenowe wiąże; < 5 par → pusta konstrukcja z `status` | kod app.py |
| 3 | `scripts/koszyki_cienie.py` | bez zmian logiki (rozlicza wszystkie `konstrukcje`); dopisać do wiersza logu `b_sox_net` ex ante każdej konstrukcji z JSON-u i kumulację σ-ratio E/A + F p z `data/koszyki-cienie.jsonl` (sekcja „narastająco”) | kod app.py |
| 4 | `scripts/waliduj_signals.py` | §9: `HISTORY_POLA_OPCJONALNE`, kontrola `konstrukcja`/`b_sox_net`; `BASIS` nowych wpisów bez `cena/price/rekom/short`; +3 testy w `scripts/test_app.py` | walidator |
| 5 | `app.py` — `sync()` | próg miękki `DD_SOFT/DD_SOFT_RESET/DD_SOFT_FACTOR`, `wykonanie.soft`, `/status.ustawienia.soft`, `alloc_efektywny` | kod app.py |
| 6 | `app.py` — zmienne | `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `DD_SOFT_FACTOR=0.5` (domyślne `DD_SOFT=0` = wyłączony do czasu ustawienia w Renderze — zgodność wstecz) | kod app.py |
| 7 | `scripts/test_app.py` | testy soft (3), `_sanity` z `history.konstrukcja` (1), walidator (3) — cel 151 → ~158 OK | kod app.py |
| 8 | `rutyny/tygodniowa.md` | KROK B = §5 tej notatki (B-0…B-5); KROK A = `koszyki_cienie.py` + metryki §6.3 (σ-ratio E/A, b_SOX zreal., najgorszy tydzień, pokrycie, `koszt_wykonania_pp` tylko w raporcie); KROK C: tabela par, b_SOX/b_DEF/β net (adnotacja), pula 8 par, veta, zdanie o mocy; KROK D: `history` +`konstrukcja:"E"`, `b_sox_net`; w commicie dozwolone dodatkowo `data/ranking-<version>.json`, `data/ranking-cache.csv`, `data/koszyki-cienie.jsonl`; skreślone B1–B4 (scoring, elita, p, pre-mortem, deklaracje D1–D3), benchmark ręczny; stopka: „ALLOC_PCT = 0,08; 1 p.p. spreadu = 0,4 % kapitału; próg miękki: stan z /status” | rutyna |
| 9 | `rutyny/dzienna.md` | §8: usunięte TRZY WARUNKI, BLOKADA SEKTOROWA jako warunek, ELITA, MODUŁ TAKTYCZNY, WYKONALNOŚĆ, LICZNIK HISTEREZY, działania P1; KROK 2: `exclude` tylko basis `news` z listy R3 + dokument, `status` NIEAKTUALNA tylko wyłącznik płynności/P2; KROK 3: KONTROLA BRAMKI jako pomiar; KROK 1b bez zmian + odczyt `wykonanie.soft`; sekcja pokrycia: nogi E 10/10, przestrzały lotów, `wybor` budżetu; harmonogram: pon./śr./pt. (decyzja) | rutyna |
| 10 | `rutyny/reguly.md` | OBOWIĄZUJĄCE: **S4 „Konstrukcja E”** (treść §3, liczby §2.1–2.3, retest 26 okien), **S5 veto cenowe** (`MAX_PRICE_USD`, koszt Δ +0,03…+0,04, t ≤ 1,5), S2 (sizing) przeredagowana: „stałe ALLOC 0,08 + próg miękki; vol-target bez przedmiotu dla E (ALLOC 0,12 w 98 % tygodni)”; H4 → status „W BOCIE (E)” z kryteriami §6.4; H5 (budżet na A) → cień D; nowy KANDYDAT H6 „transze 2-tyg. nie poprawiają wyniku (Δ −0,10…+0,18, t ≤ 1,6)” — zamknięty; H7 „b_DEF jako drugi budżet” — do testu | rutyna |
| 11 | `rutyny/tradingview.md` | budżet soboty: screener 1, earnings ≤ 2, ohlcv 2 (≤ 6 wywołań, 10 min); pulsu: batch kursów ≤ 3, ohlcv 2, earnings 1, news ≤ 2 (≤ 8); allowlista soboty bez `get-forecasts`, `get-financial-history`, `get-documents`; flagi `b1_z_tv`, `kryterium_event_remis`, `event_blokada_taktycznej` → bez przedmiotu (opis) | rutyna |
| 12 | `data/tv-config.json` | budżety jak #11; flaga `taksonomia_z_poprzedniego_snapshotu_ok: true` (pozwolenie na użycie snapshotu sprzed tygodnia przy 429) | rutyna |
| 13 | `CLAUDE.md` | §9: `history.konstrukcja/b_sox_net`, `wykonanie.soft`, `/status` + `soft`/`alloc_efektywny`; akapit „Koszyk = ranking.py konstrukcja E (5 par, budżet SOX); rutyna nie wybiera spółek”; pliki `data/ranking-*`, `koszyki-cienie.jsonl` bez liczb z rachunku; `MAX_PRICE_USD` przeliczać przy zmianie `ALLOC_PCT`/`START_EQUITY` | rutyna |
| 14 | `INSTRUKCJA.md` | §2: `DD_SOFT*`, zasada „`ALLOC_PCT` krokiem ≤ 0,02 na 4 tygodnie”; §3: `wykonanie.soft`, `history.konstrukcja`; §8 rewizja („dwa progi” → „bramka wycofana, pomiar zostaje”); nowy §: „Konstrukcja E i veto cenowe — co zrobić, gdy `/run` pomija nogę z powodu lotu” | kod app.py |
| 15 | panel Render — **natychmiast (przed pon. 19.10 13:45 UTC)** | `ALLOC_PCT=0.08`, `TACTICAL_ENABLED=false`, `TACTICAL_ALLOC_PCT=0`; decyzja o `equity_peak`/`START_EQUITY` (§11) | właściciel (Render/decyzja) |
| 16 | panel Render — po deployu kodu (przed sobotą 24.10) | `DD_SOFT=0.10`, `DD_SOFT_RESET=0.05`, `DD_SOFT_FACTOR=0.5`; `REDUCE_FALLBACK=close`; (z innych projektów, zgodne: `STOP_REOPEN=false` jeśli wdrożone) | właściciel (Render/decyzja) |
| 17 | `signals.json` — `equity_peak` | ręczny commit właściciela (pole bota) **tylko** jeśli wybrana opcja (c) z C9 (reset szczytu + `START_EQUITY` ≤ kapitał) | właściciel (Render/decyzja) |
| 18 | zadania claude.ai/code/routines | wklejenie nowych treści obu rutyn po commicie; harmonogram Pulsu pon./śr./pt. (decyzja) | właściciel (Render/decyzja) |

Kolejność: #15 (+#17 decyzja) niedziela 19.10 → #1–#7 z testami do czwartku 23.10 → #10–#14 → #8, #9 + #18 piątek 23.10 → #16 piątek po deployu → **pierwszy koszyk E: sobota 24.10 (W9)**. Jeśli kod (#5–#7) nie zdąży: E i tak wchodzi 24.10 (ranking.py #1 jest niezależny od app.py); próg miękki czeka na deploy — ryzyko mierzalne: P(kill 52, alfa 0) 8,1 % zamiast 0,2 %, w 12 tyg. 0,0 % w obu.

---

## 11. Plan migracji

### 11.1 Teraz: 18–19.10 (kapitał ≈ 1,7 % nad progiem; W8 rusza 19.10 13:45 UTC)

Konstrukcja nie zmienia nic w W8 (koszyk Modelu 3.0 jest scommitowany; zmiana poza sobotą łamie konwencję pól i rozliczeń). Decyzje z C9 / projektu A obowiązują:

| opcja | poduszka | P(kill): pon. 13:45 na księdze W7 / 5 ses. / 20 ses. przy ALLOC 0,08 | ocena |
|---|---|---|---|
| (0) nic, ALLOC 0,24 | 1,7 % | 21 % / 58 % / 77 % | — |
| (a) ALLOC 0,08, bez resetu | 1,7 % | 21 % / 39 % / 58 % | 4 tyg.: 68–85 % dla każdej polityki (projektA_boot) |
| **(c) ALLOC 0,08 + `equity_peak := kapitał` + `START_EQUITY` ≤ kapitał** | 33 % | 0 % / 0 % / 1 % | zalecane w C9/projekcie A — **decyzja właściciela** (jawne uznanie kill switcha za zadziałany; E[kapitał] czekania ≈ restartu, C9 §6) |

W8 faktyczny ma ex ante σ60_unit 1,85 %/d i b_SOX +0,05 — ryzykowo przypomina E; przy ALLOC 0,08 σ dz. kapitału ≈ 0,74 %. Od soboty 24.10 W8 jest rozliczany cieniami (A/B/E/D z `projektA_ranking_W8.json` + E z tej notatki: CRWD AMD FTNT TRI ABNB / APP AVGO PAYX NFLX CMCSA).

### 11.2 W9 (sobota 24.10) — pierwszy koszyk E

Kolejność z §10. Oczekiwane: 5 par, \|b_SOX net\| ≤ 0,5 (na 16.10 wyszło +0,18), σ60_unit ≈ 1,9–2,7 %/d, przy 0,08: σ dz. kapitału 0,8–1,1 %, gross 80 %. Poniedziałek 26.10: Puls kontroluje pokrycie 10/10 i przestrzały (COST/LITE/MPWR/MU, jeśli w koszyku). Nowe nogi wchodzą o 13:45 — jeśli znów o 17:05 (hipoteza stopy depozytu z wykonanie-bota.md), potwierdzić logiem `/run` i wdrożyć osobno.

### 11.3 Tygodnie 1–12 (do 16.01.2027)

- Bez zmian parametrów (`PAIR_POOL`, `FACTOR_BUDGET`, `MIN_IND/MIN_GROUP`, `MAX_PRICE_USD`, ALLOC).
- Co sobotę: cienie, metryki §6.3, tabela par; co Puls: pokrycie i `soft`.
- Po 12 oknach: tylko wykonanie i kalibracja (§6.4). Jeśli `wybor:"min_b"` ≥ 4/12 (budżet często niespełnialny) → rozważyć `PAIR_POOL 10` od W22 — zmiana prerejestrowana tu, nie „po złym tygodniu”.

### 11.4 Co może przerwać migrację

| ryzyko | reakcja |
|---|---|
| `ranking.py --fetch` bez danych (Yahoo) | TV `get-ohlcv` jako rezerwa 1y dla brakujących nazw (allowlista), adnotacja; brak > 10 % uniwersum → koszyk poprzedni zostaje |
| snapshot TV 429 w sobotę | taksonomia z poprzedniego snapshotu (grupy zmieniają się rzadko), adnotacja; dwie soboty z rzędu bez snapshotu → PROBLEMY |
| < 5 par po wetach (EVENT w sezonie wyników może wyciąć 20–30 % uniwersum) | `PAIR_POOL` szuka dalej w rankingu grup; gdy nadal < 5 → poprzedni koszyk zostaje (`version` bez zmiany) — **decyzja**; sezon wyników (koniec X–XI, I–II, IV–V, VII–VIII) jest przewidywalny — w raporcie liczyć, ile grup wypadło |
| kill w W8 mimo decyzji (a) | polityka wznowienia z projektu A §5.2 (ręcznie do czasu kodu); E wchodzi przy wznowieniu |
| kod `DD_SOFT` nie gotowy 24.10 | E bez progu miękkiego: P(kill 52, alfa 0) 8,1 % — akceptowalne na tygodnie, nie na kwartał |

---

## 12. Oczekiwane metryki (prerejestrowane; konstrukcja E, PIT, ALLOC 0,08 + soft)

| metryka | wartość oczekiwana | przedział / warunek | źródło |
|---|---|---|---|
| μ spreadu tyg. (brutto, równe wagi) | **+0,38 p.p.** (PIT) | 95 % CI ≈ −0,25…+1,01 (σ 4,61, n 209); dziś +0,82; netto PIT +0,04, dziś +0,49; **zero w CI** | projektC_bt §1 |
| σ spreadu tyg. | **4,6 p.p.** (PIT) / 5,1 (dziś) | σ-ratio vs A 0,67 [0,58; 0,78]; 2026 (PIT) 5,6 vs A 11,4 | projektC_bt §1, §1c |
| hit tygodni | 53–55 % | baza losowa 50 % | projektC_bt §1 |
| p5 / najgorszy tydzień | −7,0 / −12,7 p.p. (PIT); −6,2 / −13,4 (dziś) | A: −10,4 / −23,9 | projektC_bt §1 |
| b_SOX zrealizowane | +0,31 (PIT) / +0,27 (dziś) | A: +1,08 / +0,94; ex ante \|b_SOX net\| koszyka ≤ 0,5 (śr. 0,29–0,32) | projektC_bt §1 |
| tygodnie SOX−NDX < −3 p.p. | −1,9 (PIT) / −0,8 (dziś) p.p. | A: −5,1 / −5,6 | projektC_bt §1c |
| obrót | 2,8 nogi/tydz. | A 2,3; koszt rotacji 0,022 %/tydz. przy 0,08 | projektC_bt §4b |
| σ tyg. / dz. kapitału | **1,84 % / ≈ 0,8 %** | przy 0,08; 0,10 → 2,30 %; 0,12 → 2,77 % | projektC_bt §4b |
| μ tyg. kapitału | −0,11 % (alfa 0) … +0,04 % (in-sample PIT) … +0,26 % (in-sample dziś) | koszty 0,115 %/tydz. (finansowanie 0,092 + rotacja 0,022; stawka 6 % parametryczna) | projektC_bt §4b |
| P(kill −25 %, 12 tyg.) | **0,0 %** | każde alfa, każda z polityk 0,08/0,10 | projektC_bt §4; projektC_dod §A |
| P(kill, 26 tyg.) | 0,0 % (0,08 + soft) | 0,10 + soft 0,1 %; 0,10 bez soft 3,1 % | projektC_dod §A |
| P(kill, 52 tyg.) | **0,2 %** (0,08 + soft, alfa 0); 8,1 % bez soft | dziś 0,2 % / 9,5 %; A: 17 % (vt + soft) / 30 % (0,08) | projektC_bt §4; projektC_dod §A |
| maxDD 52 tyg. (0,08) | mediana −14 %, p95 −25 % | A: −20 % / −28 % | projektC_bt §4 |
| loty | 3 nazwy pomijane przez veto (ASML MELI SNDK), do 4 w przestrzale ≤ 1,5× | kapitał odniesienia 1 000 USD | projektC_bt §3 |
| moc testu σ po 26 / 52 tyg. | 47 % / 74 % | σ-ratio p95 1,03 / 0,91 | projektC_dod §B |

---

## 13. Główne ryzyka projektu

1. **Średnia może być niższa niż A o do 0,5–0,9 p.p./tydz.** (CI95 Δ −0,92…+0,50; klastry PIT w C2 mediana −0,86 dla par bez budżetu) — czyli E może oddać całą przewagę momentum i grać na zero po kosztach; nierozstrzygalne w horyzoncie projektu (1 204 tyg. dla Δ 0,3). Zabezpieczenie: niska dźwignia (koszty 6 %/rok), kryteria §6.4.
2. **Zależność od taksonomii TV**: Δ −0,12…−0,56 między definicjami; etykiety industry zmieniają się w czasie; 51 % par to zlepki sektorowe (C2); taksonomia spółek usuniętych w PIT przypisana ręcznie (przybliżenie). Zabezpieczenie: definicja zamrożona, snapshot co sobotę w repo, cień B/A.
3. **Survivorship bias**: dziś +0,82 vs PIT +0,38; w 2026 E oddaje 2/3 wyniku A (+0,81 vs +2,52) — jeśli reżim półprzewodników trwa, E będzie wyglądać gorzej niż A przez wiele tygodni (to jest cena ubezpieczenia, nie błąd).
4. **Budżet SOX z 56 podzbiorów** — mechanizm prerejestrowany dopiero teraz; `wybor:"min_b"` może być częsty w sezonach wyników (veto EVENT tnie grupy). Mierzyć częstość; `PAIR_POOL 10` jako jedyna dopuszczona zmiana (po 12 oknach).
5. **Koszty CFD nieznane** (overnight long/short, dywidendy shortów): przy μ netto ≈ 0 każde dodatkowe 2–3 %/rok przesuwa oczekiwanie pod zero. Pomiar `koszt_wykonania_pp` co tydzień.
6. **Stan 18.10**: żadna konstrukcja nie zmienia P(kill) w W8 (68–85 % w 4 tyg. z poduszką ≈ 1,7 %); E zaczyna dopiero od W9.
7. **Veto EVENT bez dowodu** (brak historycznego kalendarza) — może kosztować dryf po wynikach (pq_quant §D: po ≥ +12 % fwd10 +3,5 p.p.). Cień „E bez EVENT”.
8. **Wykonanie**: podwójne wejście 13:45/17:05 i kotwica stopu po poziomie brokera (wykonanie-bota.md) są niezależne od konstrukcji; przy E nogi w przestrzale (jeden lot) nie dają się wyrównać — `REDUCE_FALLBACK=close`.
9. **Pokusa poprawiania**: 36 reguł po n = 1 w W1–W8 (audyt-regul). Każdy parametr E jest w `ranking.py` z datą; zmiana = commit z liczbą z testu przekrojowego na PIT, nigdy z tygodnia.

---

## 14. Źródła

- Fazy 1–2: `_faza1_wyniki.txt` (dekompozycja-wynikow, wykonanie-bota, moc-predykcyjna-modelu, audyt-regul, ryzyko-i-sizing, perspektywa-quant), `_faza2_wyniki.txt` (bt_momentum, bt_odwrocenie, bt_neutralnosc, bt_rezim-i-zaklad-czynnikowy, bt_symulacja-wykonania); `pq_quant_out.md`, `ryzyko_extra_out.md`.
- Weryfikacje: `weryfikacja-C1.md` (PIT, tabele JOIN/LEAVE), `weryfikacja-C2.md` (pary), `weryfikacja-C4.md` (sizing), `weryfikacja-C9.md` (stan 18.10).
- Projekt A: `projekt-A-mechaniczny.md`, `projektA_bt_out.md`, `projektA_boot_out.md`, `projektA_ranking_W8.json`; projekt B: `projekt_B_sim_out.md`.
- Tej notatki: `projektC_bt.py` → `projektC_bt_out.md`, `projektC_bt_wyniki.json`, `projektC_bt_serie.csv`; `projektC_dod.py` → `projektC_dod_out.md`, `projektC_dod_wyniki.json`.
- Repo: `app.py` (`_sanity` 349–389, `calc_size` 871–898, `desired_book` 1315–1358, `sync()` 1361–, kill 1485–1503, zapis `fills/equity_peak/wykonanie` 1930–1970), `scripts/waliduj_signals.py`, `scripts/ranking.py` (`grupy`, `konstrukcja_pary`, `konstrukcja_budzet`, `policz`), `scripts/koszyki_cienie.py`, `rutyny/tygodniowa.md`, `rutyny/dzienna.md`, `rutyny/reguly.md`, `data/tv-screen-2026-W8.json`, `data/tv-config.json`, CLAUDE.md.
- Dane: `dane/closes_5y.csv` (2021-10-18…2026-10-16, skład dzisiejszy), `dane/dropped_closes.csv` (28 spółek usuniętych).

Zastrzeżenia metodyczne: okna od 2022-10-21 (209, nie 233 — wymóg 250 sesji bety); zamknięcia bez korekty o dywidendy; koszty parametryczne; brak poślizgu i luk poniedziałkowych (bot wchodzi 13:45 UTC w poniedziałek, harness na zamknięciach piątkowych — C1/C3: różnica ±0,1 p.p./tydz., nieistotna); taksonomia TV z jednego snapshotu (2026-W8) narzucona wstecz, dla spółek usuniętych ręcznie; wielokrotne testowanie (11 konstrukcji × 2 składy + 5 definicji) — wnioski o σ są na to odporne (wszystkie σ-ratio E < 0,8), wnioski o średniej są przez to „nierozstrzygalne”, nie „obalone”. Bez liczb z rachunku.
