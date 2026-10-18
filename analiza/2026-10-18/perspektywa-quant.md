# Perspektywa quant: czego realistycznie można oczekiwać od koszyka 5L/5S z Nasdaq-100 na 5 sesji — i jak przebudować proces

Data: 18.10.2026. Gałąź `claude/gifted-lamport-iwzpop`. Autor: agent „perspektywa-quant" (portfolio manager, strategie statystyczne).
Wszystkie liczby ze skryptów (pandas 3.0.6 / numpy 2.4.6); każda ma źródło w nawiasie. Żadnych liczb z rachunku — wyłącznie p.p., % kapitału i prawdopodobieństwa.

Skrypt własny: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/pq_quant.py`
→ `pq_quant_out.md` (tabele surowe), `pq_quant_summary.json`.
Korzystam też (z podaniem pliku) z backtestów siostrzanych w tym samym katalogu: `bt_momentum.md`, `bt_odwrocenie.md`, `bt_neutralnosc.md`, `bt_rezim-i-zaklad-czynnikowy.md`, `bt_symulacja-wykonania.md`, `dekompozycja-wynikow.md`, `moc-predykcyjna-modelu.md`, `audyt-regul.md`, `wykonanie-bota.md`. Tam, gdzie moje liczby i ich liczby dotyczą tego samego, podaję obie.

Konwencje: D0 = ostatnia sesja tygodnia ISO; zwrot pozycji = r_spółki − r_^NDX (LONG) / −(r − r_^NDX) (SHORT); spread_pp = śr. LONG + śr. SHORT = P&L w % nominału jednej strony (gross = 2). Przy ALLOC 0,24 i 5 nogach 1 p.p. spreadu = 1,2 % kapitału (`wykonanie-bota.md` §0). Dane: `closes_5y.csv` (2021-10-18…2026-10-16, 1257 sesji, 102 spółki po scaleniu GOOG/GOOGL; skład DZISIEJSZY → survivorship bias zawyża wszystko, co jest „long zwycięzców").

---

## 0. Odpowiedź w ośmiu zdaniach

1. **Realistyczny sufit dla mechanicznego koszyka 5/5 z NDX-100 rotowanego co tydzień to Sharpe brutto ≈ 1,0 (netto 0,7–0,8), czyli ≈ +1,0 p.p./tydz. przy σ ≈ 7 p.p.** (momentum 6M, 233 okna 2022–2026, t = 2,1 brutto / 1,7 netto — `pq_quant_out.md` §B, zgodnie z `bt_momentum.md`). To jest wynik najlepszego znanego, prostego sygnału na danych z survivorship bias — rozsądna wartość oczekiwana ex ante to **+0,3…+0,7 p.p./tydz. netto przy σ 6–7 p.p.**, czyli Sharpe 0,3–0,6. Hit rate takiej strategii to 55–58 % tygodni i 52–53 % nóg — pojedyncza noga jest rzutem monetą, wynik robi asymetria wielkości ruchów.
2. **Losowy koszyk 5/5 o równych wagach ma σ tygodniowego spreadu 3,4 p.p.; faktyczne koszyki W1–W7 miały σ 11,3 p.p. (χ²(6) = 66, p ≈ 0)** — system brał 3,3× ryzyko losowego koszyka, a przy ALLOC 0,24 zamieniał to na σ ≈ 13 % kapitału tygodniowo. W7 (−21,15 p.p.) to −6,2σ wobec losowego koszyka, ale tylko −1,7σ wobec koszyków momentum 6M z 2026 (σ ≈ 12 p.p., `bt_momentum.md` §9). Nie była to „pomyłka", tylko realizacja znanego ryzyka konstrukcji.
3. **Horyzont 5 sesji + scoring fundamentalny (rewizje, FCF, „ekspozycja AI") to niedopasowanie horyzontu do sygnału.** Informacja fundamentalna ma horyzont miesięcy–kwartałów; w oknie 5 sesji jej IC jest nieodróżnialny od zera, a Wynik Modelu 3.0 po odjęciu bety i momentum 6M ma IC −0,12 (t −1,5; `moc-predykcyjna-modelu.md` §0 p.3). Co tygodniowo „działa" w tym uniwersum, to kontynuacja (momentum 6M, Medhat–Schmeling) i dryf po dużych ruchach — nie odwrócenie (Jegadeesh/Lehmann: w NDX-100 −0,33 p.p./tydz. brutto, −0,74 netto; `bt_odwrocenie.md`).
4. **Dotychczasowy „zysk" strony short (defensywy) i strony long (sprzęt AI) to w ~60–75 % jeden czynnik (SOX−NDX / SMH−XLP) i beta, nie selekcja.** Long high-σ / short low-σ w NDX-100 dawało +1,58 p.p./tydz. w 2023–2026 z korelacją −0,61 do ^NDX i β −1,6 (`pq_quant_out.md` §C) — czyli premia za zmienność była tu UJEMNA (zarabiał ten, kto brał zmienność) wyłącznie dlatego, że indeks rósł. W 2022 ten sam zakład tracił. Nazywanie tego „jedyną stroną z dodatnią alfą" (PROPOZYCJA 3.1 §4) jest błędem atrybucji.
5. **Konstrukcje, które statystycznie poprawiają stabilność:** (a) 2 nakładające się transze tygodniowe (horyzont 2 tyg.) — ta sama σ, t 2,37 vs 2,09, obrót ×½, Sharpe netto 0,97 vs 0,79 (`pq_quant_out.md` §B); (b) neutralność branżowa / parowanie wewnątrz branży — σ −20–24 % przy tej samej średniej, najgorszy tydzień −14…−18 vs −26 p.p. (`bt_neutralnosc.md`); (c) vol targeting całego koszyka (σ dz. kapitału 1,5 %) — maxDD 39 % vs 69 %, P(kill) 0,4 % vs 41 % okien 12-tyg. (`bt_symulacja-wykonania.md` v8). Neutralność beta przez przewagę dolarową shortów i risk parity „10 nóg ∝ 1/σ" POGARSZAJĄ wynik (net-short indeksu). Więcej nóg (10/10, 15/15) obniża σ do 6,0/5,2, ale średnią do 0,55/0,43 — Sharpe spada, bo sygnał momentum siedzi w ogonach rankingu.
6. **Przy σ 7 p.p. wykrycie +1 p.p./tydz. na poziomie t = 2 wymaga ≈ 200 tygodni; +0,5 p.p. — 780.** Siedem tygodni, a nawet 52, nie rozstrzygną niczego o przewadze. Pętla uczenia musi więc rozstrzygać regułami przekrojowymi na 5 latach (n ≥ 30 zdarzeń, |t| ≥ 2, ten sam znak w ≥ 4 z 5 lat), a tygodniowe wyniki mierzyć wyłącznie jako wariancję, koszt reguł i zgodność wykonania — nigdy jako dowód skuteczności.
7. **Największym pojedynczym problemem nie jest selekcja, lecz wielkość pozycji wobec σ konstrukcji:** przy μ 0,75 / σ 7 p.p. ALLOC 0,24 daje P(kill switch w 52 tyg.) ≈ 83 %, ALLOC 0,12 ≈ 31 %, ALLOC 0,08 ≈ 9 % (symulacja t(4), `pq_quant_out.md` §F). Pół-Kelly dla tych parametrów to ALLOC ≈ 0,15 przy ZNANYCH parametrach; przy niepewności parametrów (t ≈ 1,5) ćwierć-Kelly ≈ 0,08 jest właściwą skalą. Propozycja 3.1 (ALLOC 0,20) jest kosmetyczna.
8. **Zostawić:** horyzont tygodniowy, ale jako 2 transze; zwroty relatywne vs ^NDX; shorty na akcjach (tryb classic); zamknięte okna rozliczeń od cen wejścia; kill switch; prerejestrację i benchmark momentum „na papierze". **Skasować lub zdegradować:** uznaniowy scoring 20 czynników jako źródło koszyka (zostaje jako nakładka co najwyżej ±1 nogi z mierzonym kosztem), bramkę reakcji 4 %/8 % z drugą sesją (autokorelacja dziennego spreadu −0,01; po dniu ≤ −3 p.p. kolejne 3 sesje dają +1,43 p.p., t 2,7 — cięcie po złym dniu ma ujemną wartość oczekiwaną), deklaracje D1–D3 jako źródło reguł, regime gate w obecnej formie (obniża średnią 1,00 → 0,78 p.p. przy maxDD bez zmian, `bt_rezim-i-zaklad-czynnikowy.md` §5 p.4), stop 10 % z reopen (−0,19 p.p./tydz., t −1,7, `bt_symulacja-wykonania.md`).

---

## 1. Punkt odniesienia: ile da się zarobić i z jaką σ (pytanie 1)

### 1.1 Co mówi literatura o horyzoncie 5 sesji w dużych spółkach

| efekt | źródło | co mówi | co widać w NDX-100 2022–2026 |
|---|---|---|---|
| krótkoterminowe odwrócenie (1 tydz.–1 mies.) | Jegadeesh 1990, Lehmann 1990 | ujemna autokorelacja zwrotów na 1 tyg./1 mies.; w nowszych próbach silnie osłabione, skoncentrowane w małych/niepłynnych spółkach, pochłaniane przez koszty (Avramov–Chordia–Goyal 2006; Hameed–Mian 2015: efekt wewnątrzbranżowy) | **ujemne**: long 5 najgorszych / short 5 najlepszych z poprzedniego tygodnia: −0,33 p.p./tydz. brutto, −0,74 netto, t −0,9; 2024–2025 t −1,6/−2,1 (`bt_odwrocenie.md` a_rev5). Odwrócenie 10- i 21-sesyjne jeszcze gorsze (−0,59/−0,67). |
| kontynuacja w dużych, płynnych spółkach | Medhat–Schmeling 2022 (RFS) | w spółkach o wysokim obrocie krótki zwrot KONTYNUUJE, odwrócenie dotyczy niskiego obrotu | spójne: momentum 1M daje +0,76 p.p. (t 1,7), kontrariańskie 1M −0,76 (`bt_momentum.md` d_1M / d_rev); po skoku ≥ +12 % rel. fwd5 +1,08 (t 2,2), fwd10 +3,5 p.p. (`pq_quant_out.md` §D) |
| momentum branżowe | Moskowitz–Grinblatt 1999 | większość momentum indywidualnego to momentum branż; horyzont 1–12 mies. | koszyk momentum 6M w 2026 = 4,4 półprzewodnika w TOP5, ekspozycja na SOX−NDX 2,0 (`bt_momentum.md` §6); spread faktycznych koszyków wyjaśniony w 70–74 % przez ^NDX + (^SOX−^NDX) (`dekompozycja-wynikow.md` §0) |
| dryf po wynikach (PEAD) | Bernard–Thomas 1989; w dużych spółkach słabnie (Chordia i in. 2009) | dryf w kierunku niespodzianki przez 60 dni, największy w pierwszych dniach | proxy: po ruchu rel. ≥ +12 % fwd10 +3,5 p.p.; po ≤ −12 % fwd5 **+2,56** (t 2,8), fwd10 +2,6 — czyli po dużych SPADKACH w tym uniwersum jest odbicie, nie dryf (`pq_quant_out.md` §D). Niestabilne w latach: po ≤ −8 % 2022–2024 ≈ 0, 2025–2026 +1,4/+1,9. |
| sezonowość tygodniowa | French 1980 (poniedziałek), efekt weekendu | współcześnie ≈ 0 w indeksach USA | dzienny spread koszyka momentum wg dnia tygodnia: 0,09–0,28 p.p., wszystkie t < 1,3 (`pq_quant_out.md` §E) — **brak** |
| premia za zmienność / low-vol | Ang i in. 2006; Frazzini–Pedersen 2014 (BAB) | niska zmienność/beta daje wyższą alfę (po korekcie o betę); w surowych zwrotach zależy od kierunku rynku | **surowo ujemna** w NDX-100 2023–2026: long low-σ / short high-σ −1,58 p.p./tydz. (t −3,1), corr z ^NDX −0,61, β −1,6; 2022 +0,52 (`pq_quant_out.md` §C). To jest lustrzane odbicie zakładu systemu (long semis high-σ / short staples low-σ). |
| koszty CFD | — | spread ~0,1–0,2 % nominału na transakcję (akcje USA, Capital.com), finansowanie overnight (benchmark + marża) od nominału obu stron, korekty dywidendowe na shortach | przyjęte: 0,20 % round-trip/nogę, 6 %/rok od gross — przy gross 2 to 0,23 p.p./tydz. (≈ 12 p.p./rok), przy gross 2,4 0,28 p.p./tydz.; to 25–30 % brutto najlepszego sygnału i > 100 % sygnałów o średniej < 0,3 p.p. |

**Wniosek 1.1:** w tym uniwersum i horyzoncie jedynym sygnałem z t > 2 brutto jest momentum relatywne 6M (i jego wariant: dryf po dużych ruchach w górę). Odwrócenie, sezonowość, low-vol — nie istnieją albo mają znak przeciwny do klasycznej literatury, co jest zgodne z Medhat–Schmeling (duże, płynne spółki) i z tym, że NDX-100 to uniwersum ~100 nazw o wysokiej korelacji z jednym czynnikiem.

### 1.2 Sharpe → tygodniowy spread

| σ tyg. spreadu (p.p.) | Sharpe 0,5 → μ | Sharpe 1,0 → μ | Sharpe 1,5 → μ | tygodni do t = 2 przy S = 1,0 |
|---|---|---|---|---|
| 3,4 (losowy 5/5) | 0,24 | 0,47 | 0,71 | 208 |
| 5,0 (branżowo neutralny) | 0,35 | 0,69 | 1,04 | 208 |
| 7,0 (momentum 5/5) | 0,49 | 0,97 | 1,46 | 208 |
| 10,0 (koszyki W4–W7) | 0,69 | 1,39 | 2,08 | 208 |

(`pq_quant_out.md` §F). Liczba tygodni do t = 2 zależy tylko od Sharpe'a: n = (2/S·√52)² ≈ 208/S². Przy Sharpe 0,5 to 830 tygodni.

**Realistyczne oczekiwanie dla najlepszych znanych sygnałów** (mechaniczne momentum 6M, 5/5, gross 2, po kosztach, z poprawką na survivorship bias ≈ −0,2…−0,3 p.p.): **μ ≈ +0,4…+0,8 p.p./tydz., σ ≈ 6–7,5 p.p., Sharpe netto 0,3–0,6, hit 53–57 %.** Rocznie: +20…+40 p.p. spreadu brutto nominału strony, czyli przy ALLOC 0,12 (gross 1,2) **+12…+24 % kapitału/rok przy σ ≈ 30 %/rok i maxDD 30–45 %**. Oczekiwanie „+2 p.p./tydz." (W1–W6 sugerowały +2,9) odpowiada Sharpe'owi 2 w uniwersum 100 nazw z jednym sygnałem — a priori nieprawdopodobne; wszystkie 2000 losowych strategii mają średnią w paśmie ±0,37 p.p. (`bt_momentum.md` baseline), a najlepszy sygnał 1,0.

### 1.3 Faktyczne W1–W7 wobec odniesienia

| miara | W1–W7 faktyczne | losowy 5/5 | momentum 6M 5/5 (2022–26) | źródło |
|---|---|---|---|---|
| średnia p.p./okno | −0,52 (okna 2–11 sesji); −2,09 w oknach znormalizowanych do 5 sesji | 0,00 | +1,01 | history; `dekompozycja-wynikow.md` §0 |
| σ | 11,3 | 3,4 | 7,4 (2026: 12,2) | `pq_quant_out.md` §G; `bt_momentum.md` |
| t | −0,12 | — | 2,09 | |
| hit nóg | 33/70 = 47 % (Wilson 36–59 %) | 50 % | 53 % | |
| udział czynników (^NDX, SOX−NDX, defensywy) | 60–81 % wariancji konstrukcji | — | R² na SOX−NDX 0,11 cały okres, 0,59 w 2026 | `dekompozycja-wynikow.md`; `bt_momentum.md` §6 |

χ²(6) = 6·11,3²/3,4² = 66 (krytyczne 12,6): **σ W1–W7 jest istotnie wyższa niż losowego koszyka** — to jedyny statystycznie pewny fakt o W1–W7. O średniej nie da się powiedzieć nic (t = −0,12; przedział ufności 95 % dla μ: ≈ −11…+10 p.p.).

---

## 2. Horyzont 5 sesji a sygnał fundamentalny (pytanie 2)

**Teza: to niedopasowanie, i to w obie strony.**

1. **Sygnały fundamentalne mają horyzont miesięcy.** Rewizje konsensusu (Chan–Jegadeesh–Lakonishok 1996), jakość/FCF (Novy-Marx 2013), wycena — ich IC ujawnia się w oknach 1–12 miesięcy, a w oknie 5 sesji jest zdominowany szumem o σ_nogi 5,5 p.p. (`pq_quant_out.md` §A). Rotując co tydzień koszyk oparty na takich czynnikach, płacimy koszt obrotu za sygnał, który w tym oknie nie zdążył zadziałać; żeby „wyciągnąć" fundamenty, trzeba trzymać 4–13 tygodni.
2. **Empirycznie Wynik Modelu 3.0 nie ma mocy w oknie 5 sesji poza tym, co pochodzi z bety i momentum:** IC Wyniku vs zwrot 5-sesyjny koreluje z IC bety 0,93 i z IC momentum 12M−1M 0,95 (n = 7 tyg.), a na resztach po becie i momentum IC = −0,12 (t −1,5); nogi o najwyższej pewności (|wynik−50| ≥ 19) trafiły 40,6 % i dały −1,97 p.p./pozycję; kalibracja p odwrotna (p ≥ 61 % → 37,5 % trafień) (`moc-predykcyjna-modelu.md` §0, `audyt-regul.md` §0 p.6). Model zachowywał się jak nieprecyzyjny proxy momentum/bety z dodatkowym szumem uznaniowym — i w W8 zmienił charakter (corr z betą 0,53–0,73 → 0,03), więc W1–W7 nic nie mówi o W8.
3. **Uznaniowość jest niereprodukowalna, więc nietestowalna.** Wynik tej samej spółki między sobotami koreluje z jej zwrotem relatywnym 0,53–0,83 („goni kurs"), a 10 z 16 stron koszyków W2–W8 odbiega od TOP5/BOTTOM5 własnego rankingu (`moc-predykcyjna-modelu.md` §0 p.6). Nie da się zbacktestować procedury, której wynik zależy od tego, co model językowy przeczytał tego dnia. To wyklucza pętlę uczenia w sensie statystycznym — można uczyć się tylko o regułach, które da się policzyć z zapisanych wejść.
4. **„Ekspozycja AI" to etykieta czynnika, nie sygnału.** Lista B1(c) (optyka, pamięć, WFE, cyber) wyprodukowała 24/35 nóg long i ekspozycję na SOX−NDX 1,1–2,7 w każdym tygodniu — to decyzja o CZYNNIKU podjęta raz, przebrana za 5 niezależnych tez. Zwrot takiego koszyka w tygodniu to w 60–80 % zwrot czynnika, więc pre-mortem per spółka jest teatrem: właściwe pytanie brzmiało „czy chcę mieć β 2 na SOX−NDX w tym tygodniu", a na nie nikt nie odpowiadał.
5. **Co pasuje do 5 sesji:** momentum relatywne 6M z pominięciem ostatniego tygodnia (t 2,1), ewentualnie 1M (t 1,7, obrót ×2,4), dryf po dużych ruchach w górę (≥ +12 %: fwd10 +3,5 p.p., t 2,2) i unikanie shortów po dużych spadkach (≤ −12 %: fwd5 +2,56, t 2,8; wśród spółek z wysokim momentum 6M po ≤ −8 % fwd5 **+2,79**, n = 272, wśród niskiego momentum −0,98, n = 174 — `pq_quant_out.md` §D). Wszystko to są sygnały CENOWE, policzalne z `closes`, odtwarzalne co sobotę skryptem.

**Praktyczny wniosek:** albo horyzont do 4–13 tygodni z fundamentami (wtedy to inny system — mniej rotacji, inny bot, inny rachunek), albo horyzont tygodniowy z sygnałami cenowymi i fundamentami wyłącznie jako VETO (event w oknie, wezwanie, zawieszenie). Hybryda „fundamenty na 5 sesji" płaci koszty obu i nie zbiera premii żadnego.

---

## 3. Konstrukcje dające stabilny wynik (pytanie 3)

### 3.1 Liczba nóg i horyzont (moje liczby, momentum 6M, 2022-04-22…2026-10-16, koszty 0,20 % RT/nogę + 6 %/rok gross 2)

| wariant | okien | śr. p.p./okno | σ/okno | t | Sharpe | hit | maxDD | najgorsze | obrót/okno | netto p.p. | t netto | Sharpe netto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5/5, 1 tydz. | 233 | 1,01 | 7,42 | 2,09 | 0,99 | 58 % | −51 | −25,9 | 0,20 | 0,82 | 1,68 | 0,79 |
| **5/5, 2 transze nakł. (hor. 2 tyg.)** | 231 | 1,14 | 7,30 | **2,37** | 1,12 | 57 % | −51 | −24,7 | 0,10 | 0,98 | **2,05** | **0,97** |
| 5/5, 4 transze nakł. (hor. 4 tyg.) | 227 | 1,05 | 7,29 | 2,16 | 1,03 | 54 % | −52 | −24,2 | 0,08 | 0,90 | 1,85 | 0,89 |
| 5/5, 2 tyg. bez nakładania | 116 | 1,90 (0,95/tydz.) | 11,26 (7,96/tydz.) | 1,81 | 0,86 | 62 % | −52 | −36,9 | 0,28 | 1,55 | 1,49 | 0,70 |
| 5/5, 4 tyg. bez nakładania | 57 | 4,08 (1,02/tydz.) | 18,26 (9,13/tydz.) | 1,69 | 0,80 | 63 % | −64 | −50,0 | 0,40 | 3,46 | 1,43 | 0,68 |
| 10/10, 1 tydz. | 233 | 0,55 | 6,00 | 1,41 | 0,66 | 57 % | −49 | −20,9 | 0,18 | 0,36 | 0,93 | 0,44 |
| 10/10, 2 transze nakł. | 231 | 0,65 | 5,82 | 1,69 | 0,80 | 58 % | −50 | −20,4 | 0,09 | 0,50 | 1,30 | 0,62 |
| 15/15, 1 tydz. | 233 | 0,43 | 5,21 | 1,27 | 0,60 | 57 % | −41 | −18,3 | 0,17 | 0,25 | 0,74 | 0,35 |
| 15/15, 2 transze nakł. | 231 | 0,50 | 4,98 | 1,51 | 0,72 | 57 % | −41 | −16,9 | 0,08 | 0,35 | 1,06 | 0,50 |
| losowy 5/5 / 10/10 / 15/15, 1 tydz. (σ) | 260 | 0 | 3,42 / 2,43 / 1,98 | — | — | 50 % | — | p5 −5,5 / −3,9 / −3,2 | — | — | — | — |

(`pq_quant_out.md` §A–B.) Odczyt:

- **Więcej nóg obniża σ (7,4 → 6,0 → 5,2), ale średnią szybciej (1,01 → 0,55 → 0,43)** — Sharpe spada 0,99 → 0,66 → 0,60. Sygnał momentum siedzi w skrajnych decylach; rozmycie na 15 nazw na stronę to w połowie losowy koszyk. Koszyki momentum są 2,2–2,6× bardziej zmienne niż losowe o tej samej liczbie nóg (7,42/3,42; 6,00/2,43; 5,21/1,98) — to cena za koncentrację sektorową, której sam dobór liczby nóg nie usuwa.
- **Dłuższy horyzont bez nakładania nic nie daje** (średnia na tydzień taka sama, σ na tydzień wyższa, mniej obserwacji). **Nakładanie 2 transz jest jedyną zmianą horyzontu, która poprawia t i Sharpe'a**: ta sama σ tygodniowa, wyższa średnia (1,14), obrót o połowę mniejszy (0,10 nominału strony/tydz. zamiast 0,20), Sharpe netto 0,97 vs 0,79. Mechanizm: dywersyfikacja w czasie (dwa D0, dwie wersje rankingu) bez rozmywania sygnału; każda transza trzyma 2 tygodnie. Operacyjnie: 10 nazw na stronę po 1/10 strony każda, co sobotę wymienia się połowa.
- Dla bota: 2 transze = `long`/`short` po 10 nazw z wagą 0,5 każda (albo polem `weights`) i rotacja 5+5 co tydzień. Przy kroku 0,1 akcji i kursach > 600 USD wymaga to ALLOC ≥ 2 × wartość lotu / kapitał — przy małym rachunku 10 nóg po stronie może być niewykonalne; wtedy 5/5 i 1 tydz. z vol targetingiem (niżej) jest drugim wyborem.

### 3.2 Neutralizacje (z `bt_neutralnosc.md`, momentum 6M, 233 okna; moja ocena)

| konstrukcja | śr. p.p. | σ | t | Sharpe | najgorsze | netto | werdykt |
|---|---|---|---|---|---|---|---|
| bez neutralizacji (none) | 1,01 | 7,42 | 2,09 | 0,99 | −25,9 | 0,74 | odniesienie |
| ranking wewnątrz branży, ≤ 1 L i 1 S z grupy | 0,76 | 5,93 | 1,95 | 0,92 | −14,7 | 0,48 | σ −20 %, średnia −25 %: Sharpe ≈, ogon o połowę krótszy |
| **5 par wewnątrz branży** (long najlepsza, short najgorsza z tej samej grupy) | 1,01 | 5,67 | **2,72** | **1,29** | −14,4 | 0,74 (t 1,99) | **ta sama średnia, σ −24 %, F-test p < 0,001; najlepsza konstrukcja w danych** |
| limit ≤ 2 semis long / ≤ 2 defensywy short | 0,88 | 7,17 | 1,87 | 0,88 | −26,5 | 0,61 | prawie nie wiąże; nic nie zmienia |
| wagi 10 nóg ∝ 1/σ60 (risk parity dosłownie) | 0,82 | 7,56 | 1,65 | 0,78 | −31,5 | 0,47 | **gorsze**: przenosi dolary na shorty niskiej σ → net-short indeksu 80–100 % kapitału |
| wagi ∝ 1/σ osobno w stronie (dolarowo neutralne) | 1,06 | 8,67 (gross 2,4) | 1,87 | 0,88 | −32,0 | 0,73 | ≈ none w skali; bez poprawy |
| neutralność beta (Σβ_L = Σβ_S przez skalowanie stron) | 0,57 | 6,51 | 1,33 | 0,65 | −24,8 | 0,30 | **gorsze**: ten sam zakład w mniejszej skali minus zwrot indeksu |

Dlaczego beta-neutral przegrywa: zwroty liczone względem ^NDX przy równych stronach dolarowych są już neutralne w sensie „spread = L − S"; dodatkowa neutralizacja β bez hedgu indeksowego oznacza systematyczną przewagę dolarową shortów (β_L > β_S zawsze przy momentum), czyli short indeksu w rynku, który w próbie rósł. Jeżeli ktoś chce neutralności β bez tracenia średniej, jedyną czystą drogą jest **hedge indeksem** (tryb `HEDGE_EPIC = index` dla różnicy β·nominału, NIE zamiana shortów akcyjnych na indeks) — ale to kosztuje finansowanie trzeciej nogi i w próbie 2023–2026 (indeks w górę) musiałoby stracić; ex ante jest to ubezpieczenie od tygodnia takiego jak W7 (^NDX −5,5 % → ~7–9 % kapitału z samej bety netto, `wykonanie-bota.md` §0).

### 3.3 Vol targeting całego koszyka i sizing (z `bt_symulacja-wykonania.md` + moje symulacje)

| wariant (momentum 6M, 234 okna) | śr. % kap./tydz. | σ | Sharpe | maxDD kap. | P(kill 25 % w oknie 12 tyg.) | śr. gross |
|---|---|---|---|---|---|---|
| ALLOC 0,24, bez stopów (jak bot bez bramki) | 1,31 | 9,86 | 0,95 | 69 % | 41 % | 2,40 |
| ALLOC 0,24 + stop 10 % z reopen (app.py) | 1,12 | 9,98 | 0,81 | 72 % | 40 % | 2,40 |
| ALLOC 0,12, bez stopów | 0,65 | 4,93 | 0,95 | 42 % | 5,8 % | 1,20 |
| **wagi ∝ 1/σ, cel σ dz. kapitału 1,5 %, gross ≤ 3** | 0,43 | 3,98 | 0,77 | **39 %** | **0,4 %** | 1,35 |

Moja symulacja ruiny (zwroty t(4), 20 000 ścieżek, kill = −25 % od kroczącego szczytu; `pq_quant_out.md` §F):

| μ p.p./tydz. | σ p.p./tydz. | ALLOC 0,24 — 26 / 52 tyg. | ALLOC 0,12 | ALLOC 0,08 |
|---|---|---|---|---|
| 0,00 | 7,0 | 71 % / 93 % | 25 % / 53 % | 6 % / 23 % |
| 0,75 | 7,0 | 56 % / 83 % | 12 % / 31 % | 3 % / 9 % |
| 1,00 | 7,0 | 50 % / 78 % | 10 % / 25 % | 2 % / 7 % |
| 0,75 | 5,0 (neutralność branżowa) | 27 % / 51 % | 2 % / 8 % | 0 % / 1 % |
| 0,50 | 3,4 (losowy / bardzo zdywersyfikowany) | 9 % / 23 % | 0 % / 1 % | 0 % / 0 % |

Kelly: f* = μ/σ² w jednostkach nominału strony; przy μ 0,75 / σ 7 p.p. f* = 1,53 × strona → pełny Kelly ALLOC 0,31, pół-Kelly 0,15, ćwierć-Kelly 0,08. Ponieważ μ jest znane z t ≈ 1,5–2 (a nie dokładnie), a ogony są grube (t(4)), **standard branżowy to ćwierć–pół Kelly'ego: ALLOC 0,08–0,15**, przy czym P(kill) w tabeli wyżej pokazuje, że 0,12 jest górną granicą, jeżeli kill switch 25 % ma być bezpiecznikiem, a nie oczekiwanym zdarzeniem. **ALLOC 0,24 to 1,6× pełny Kelly** dla optymistycznych parametrów — to nie jest agresywny sizing, to ujemna wartość oczekiwana logarytmu kapitału.

**Vol targeting** (gross = min(gross_max, cel_σ / σ̂ koszyka), σ̂ z 60 sesji dziennych spreadu koszyka o danym składzie) jest lepszy od stałego ALLOC, bo σ konstrukcji zmienia się 2–3× między tygodniami (semis vs staples) i w czasie (2023 σ 4,5 → 2026 σ 10,6 dla proxy HW/DEF, `bt_rezim-i-zaklad-czynnikowy.md` §1). Cel: σ tygodniowa kapitału 3–4 % (≈ 20–28 % rocznie), czyli przy σ spreadu 7 p.p. gross ≈ 1,0–1,2 (ALLOC 0,10–0,12), przy σ 5 p.p. gross 1,4–1,6.

### 3.4 Rekomendowana konstrukcja (w kolejności wpływu na stabilność)

1. **Sizing: vol targeting koszyka do σ_tyg. kapitału ≈ 3,5 %, gross_max 1,6, ALLOC_PCT jako sufit 0,12** (zmienne `ALLOC_PCT`, nowa `TARGET_WEEKLY_VOL`; σ̂ liczy skrypt sobotni z `closes`, zapisuje w nowym, prerejestrowanym polu `d0.sigma_koszyka` albo bot liczy sam). To jedna zmiana, która przy identycznej selekcji przesuwa P(kill 52 tyg.) z ~80 % do ~10–30 %.
2. **Sygnał: ranking ilościowy, odtwarzalny skryptem**: momentum 6M rel. (skip 5 sesji) jako kręgosłup; veto cenowe: nie short po spadku 10-sesyjnym ≤ −12 % lub dniu ≤ −8 % (fwd5 po takich zdarzeniach +0,9…+2,6 p.p. przeciw shortowi); veto zdarzeniowe: raport w oknie D+1…D+5 (jedyny element fundamentalny, który na 5 sesji ma sens — niespodzianka to loteria o σ 8–10 p.p.).
3. **Konstrukcja: 5 par wewnątrz branży** (grupy z `tv-screen` industry ≥ 4 spółek, inaczej sector) — σ −24 % przy tej samej średniej; **albo** TOP5/BOTTOM5 z 2 nakładającymi się transzami, jeśli parowanie okaże się niewykonalne przy wielkości rachunku. Oba warianty prowadzić NA PAPIERZE równolegle od W9 z prerejestrowanymi definicjami.
4. **Horyzont: 1 tydzień wejścia, 2 tygodnie trzymania (2 transze)** — jedyna zmiana horyzontu poprawiająca t (2,09 → 2,37) i tnąca obrót o połowę.
5. **Model 3.0 jako nakładka, nie źródło**: co najwyżej 1 wymiana nogi na stronę względem rankingu ilościowego, z zapisem „noga rankingowa vs noga nadpisana" i rozliczeniem różnicy co tydzień (to jest jedyny sposób, żeby kiedykolwiek zmierzyć, czy uznaniowość coś dodaje; dziś koszt nadpisań jest nieznany, a 10/16 stron było nadpisanych).

---

## 4. Pętla uczenia, która nie dopisuje reguł po n = 1 (pytanie 4)

Stan: 36 reguł w raportach, 17 po jednej obserwacji, 0 retestów, ≥ 6 par sprzecznych; reguła o największym wpływie na skład („przegrana bez odzyskanej siły") ma w danych znak przeciwny (+0,66 p.p. dla wykluczanych, n = 1108) (`audyt-regul.md` §0). Deklaracje D1–D3 produkują regułę po każdej falsyfikacji (n = 1). To nie jest pętla uczenia, to pętla dopasowania do ostatniego tygodnia.

### 4.1 Zasady (do `rutyny/reguly.md`, czytane przez obie rutyny)

1. **Dwa rejestry:** OBOWIĄZUJĄCE (tylko reguły z przekrojowym testem) i KANDYDACI (wszystko, co wyszło z tygodnia, deklaracji, pre-mortem). Kandydat nie zmienia koszyka. Nigdy.
2. **Awans kandydata → obowiązująca wyłącznie po teście przekrojowym na `closes_5y.csv` (albo dłuższym):** okna 5-sesyjne nienakładające się (233), zwrot relatywny vs ^NDX, **n ≥ 30 zdarzeń w ≥ 15 różnych tygodniach**, **|t| ≥ 2 z klastrowaniem po dacie**, **ten sam znak w ≥ 4 z 5 lat kalendarzowych**, efekt po kosztach > 0, oraz sprawdzenie, że reguła zmienia skład (reguła, która nie wiąże, nie jest regułą). Dla reguły z p < 0,05 przy 36 testowanych regułach oczekiwane ~2 fałszywe pozytywy — stąd wymóg stabilności znaku w latach (Harvey–Liu–Zhu 2016: t > 3 dla nowego czynnika; tu kompromis t ≥ 2 + stabilność, bo próba jest krótka).
3. **Holdout czasowy:** test na 2022-04…2025-06, potwierdzenie na 2025-07…dziś (bez modyfikacji po zobaczeniu holdoutu). Reguła dopasowana na całości wchodzi tylko jako kandydat.
4. **Prerejestracja metryk** (stała tabela, ta sama kolejność co tydzień, od W9): spread_5s_pp (zawsze 5 sesji od D0), spread_konto_pp (od zamknięcia D+1 do rotacji), σ obu serii narastająco, najgorszy dzień/tydzień, β_spread(250) i ładunek na SOX−NDX, udział czynnika w wyniku tygodnia, KOSZT NADPISAŃ (koszyk rankingowy vs faktyczny, Δ p.p.), KOSZT REGUŁ (nogi pominięte przez reguły), zgodność wykonania (ile nóg weszło w 13:45, ile w 17:05, stopy, reopeny), koszty (finansowanie + spread szacunkowo). **Żadnej z tych metryk nie wolno interpretować jako dowodu przewagi przed n_pełnych ≥ 52 i |t| ≥ 2** — zdanie obowiązkowe w raporcie.
5. **Koszyki cienie na papierze (prerejestrowane definicje, rozliczane tym samym kodem):** (i) momentum 6M 5/5 mechaniczne, (ii) 5 par branżowych, (iii) ranking Modelu 3.0 bez nadpisań, (iv) faktyczny. Decyzja o zmianie trybu bota dopiero po 26 tygodniach sparowanej różnicy z |t| ≥ 2 — albo wcześniej, jeśli faktyczny ma σ > 1,5× cienia (i) przy nie wyższej średniej (to kryterium wariancji, nie średniej, i jest osiągalne w 12–20 tygodni).
6. **Deklaracje D1–D3:** zostają jako dyscyplina myślenia, ale **ich falsyfikacja NIE ma konsekwencji w składzie**; zamiast tego wpis KANDYDAT z liczbą obserwacji. Zapis prerejestrowanej konsekwencji „MU wychodzi z koszyka bez względu na wynik modelu" (raport W8) to dokładnie mechanizm, który trzeba usunąć.
7. **Reguły imienne (TSLA, NVDA/DOJ, WDAY, MSFT „płatnik capexu")** — wyłącznie w sekcji WYJĄTKI z datą wygaśnięcia ≤ 4 tygodnie i rozliczeniem kosztu (WDAY jako short wygrałby 5/6 okien, +15 p.p.; MSFT poza koszykiem kosztował +6,8 p.p. — `audyt-regul.md` K6, K9).
8. **Minimalne n dla zmian parametrów bota** (ALLOC, stop, bramka): nigdy na podstawie serii tygodniowej (potrzeba 200–800 tygodni); wyłącznie na podstawie symulacji na 233 oknach z tym samym harnessem (`bt_symulacja-wykonania.py` jest gotowym narzędziem) + test na losowych koszykach (czy reguła „pomaga" także na szumie — wtedy to redukcja wariancji, nie przewaga).
9. **Jeden właściciel reguł i jedno miejsce:** `rutyny/reguly.md` w repo; raport tygodniowy nie może wprowadzić reguły — może tylko dopisać kandydata. Grep: dziś `tygodniowa.md` nie zawiera żadnej z 17 reguł koszykowych z raportów.

### 4.2 Moc testu — ile trzeba danych

| co chcemy wykryć | σ | n tygodni do t = 2 |
|---|---|---|
| μ = +1,0 p.p./tydz. | 3,4 / 7,0 / 11,3 | 46 / 196 / 511 |
| μ = +0,5 p.p./tydz. | 3,4 / 7,0 / 11,3 | 185 / 784 / 2043 |
| μ = +2,0 p.p./tydz. | 3,4 / 7,0 / 11,3 | 12 / 49 / 128 |
| różnica dwóch wariantów Δ = 1 p.p. przy σ_Δ ≈ 3 p.p. | — | 36 |
| różnica σ (F-test, σ₁ = 1,5σ₂) | — | ≈ 25–30 okien na wariant |

(`pq_quant_out.md` §G.) Praktycznie: **po 12–26 tygodniach da się rozstrzygać tylko o wariancji, kosztach i wykonaniu; o średniej — nigdy w horyzoncie życia tego projektu.** Dlatego decyzje o przewadze muszą pochodzić z backtestu przekrojowego, a tygodnie służą do kontroli, czy system robi to, co zbacktestowano (zgodność składu z rankingiem, zgodność σ z oczekiwaną, zgodność kosztów).

---

## 5. PROPOZYCJA 3.1 (12.10) — co jest poparte danymi, co nie

| element propozycji | ocena | dlaczego |
|---|---|---|
| T7: ekspozycję podwojono po wyniku nieodróżnialnym od zera; P(kill) 0,92–0,97 w 52 tyg. przy zerowej przewadze | **poparte** | moja symulacja: 93 % (μ 0, σ 7, ALLOC 0,24); przy μ 0,75 nadal 83 % |
| T6: pętla uczenia dopisuje reguły po n = 1, trzyma je poza rutyną | **poparte** | `audyt-regul.md`: 17/36 po n = 1, 0 retestów |
| pkt 1–2: seria 5-sesyjna + seria „jak rachunek", dekompozycja na betę/SOX | **poparte, za mało** | słusznie, ale seria „od D+1/fills" powinna być GŁÓWNA (różnica W4 +9,8, W7 +4,5 p.p.; `wykonanie-bota.md` (a)) |
| pkt 4: reguła LUKA-SHORT (brak shorta po dniu ≤ −8 % lub 10 sesji ≤ −12 %) jako pierwsza OBOWIĄZUJĄCA, „n = 234, t 2,47" | **słabo poparte; kierunek tak, status nie** | na pełnym uniwersum: po dniu ≤ −8 % fwd5 **+0,88 p.p. (t 0,82 klastrowane)**; po ≤ −12 % +2,56 (t 2,8); wg lat 2022–2024 ≈ 0, 2025–2026 +1,4/+1,9 → **nie przechodzi własnego kryterium propozycji (znak w ≥ 4 z 5 lat)**. Wariant 10 sesji ≤ −20 %: −1,64 p.p. dla shorta, t −2,4 (`audyt-regul.md` p.3) — ten przechodzi lepiej niż 12 %. Jako veto o niskim koszcie — tak; jako „reguła z dowodem" — nie. Zależy od momentum spółki: po ≤ −8 % w górnym tercylu momentum +2,79, w dolnym −0,98 (`pq_quant_out.md` §D) — to argument, by veto dotyczyło tylko shortów na spółkach z dodatnim momentum, czyli dokładnie tych, których mechaniczny ranking i tak nie shortuje. |
| §4 „Nie zmieniać: selekcja fundamentalna (wagi B2) — zamrozić" | **błędna konkluzja z dobrej przesłanki** | słuszne, że zmiana wag przy n = 6 to data mining; ale „zamrozić" oznacza dalej grać koszykiem, którego IC ≈ 0 po becie/momentum i którego nie da się odtworzyć. Właściwy wniosek: zdegradować do nakładki, mierzyć koszt. |
| §4 „Nie zmieniać: horyzont 5 sesji" (Medhat–Schmeling, Novy-Marx) | **połowicznie** | kontynuacja tak; ale 2 transze nakładające się (horyzont 2 tyg.) są lepsze in-sample (t 2,37 vs 2,09, obrót ×½) — czego propozycja nie testowała |
| §4 „Nie zmieniać: bramka 4/8 % + druga sesja + blokada sektorowa (Kaminski–Lo)" | **nie poparte** | przekrojowo sygnał REDUCE przewiduje resztę okna na +0,08 p.p. (t 0,03; `audyt-regul.md` p.5); autokorelacja dziennego spreadu −0,01/−0,02; po dniu ≤ −3 p.p. kolejne 3 sesje +1,43 p.p. (t 2,7) — cięcie po złym dniu ma znak ujemny. Kaminski–Lo mówią o stop-lossach przy DODATNIEJ autokorelacji (momentum w czasie); tu jej nie ma. Bramka to redukcja wariancji o losowym koszcie, nie przewaga — tak ma być opisana i w tej roli lepszy jest vol targeting. |
| §4 „HEDGE_EPIC = classic i shorty defensywne — jedyna strona z dodatnią alfą" | **błąd atrybucji** | shorty defensywne = short low-σ/low-β w rosnącym rynku; przekrojowo dolny kwintyl momentum w sektorach defensywnych daje shortowi −0,05 p.p./tydz. (t −0,3) vs technologia +0,21 (`audyt-regul.md` K7); long high-σ/short low-σ w NDX 2023–26 +1,58 p.p./tydz. z β −1,6 do indeksu (`pq_quant_out.md` §C) — to beta, nie alfa; w 2022 znak przeciwny. Tryb classic zostaje z innego powodu: short akcyjny jest potrzebny, by spread był L − S; ale „defensywy jako short" nie jest przewagą. |
| pkt 5: diagnostyka β/SOX, flaga KONCENTRACJA, maks. 1 wymiana | **poparte jako pomiar**, za słabe jako ingerencja | 1 wymiana przy 5 nogach semis nie zmienia ekspozycji 2,0 na SOX−NDX; parowanie branżowe (σ −24 %) robi to strukturalnie |
| pkt 7: σ60 per noga, bez filtra; „wagi per noga obalone (Cederburg)" | **częściowo** | Cederburg i in. 2020 dotyczą vol-managed CZYNNIKÓW; vol targeting całego koszyka na 234 oknach obniża maxDD 69 → 39 % i P(kill) 41 → 0,4 % przy Sharpe 0,95 → 0,77 (`bt_symulacja-wykonania.md`) — to inny wniosek niż „obalone" |
| pkt 12: WEEK_LOSS_PCT 12 % w kodzie | **sensowne jako bezpiecznik**, nie rozwiązanie | ogranicza ogon realizowany, nie zmienia σ ex ante; przy σ 13 % kapitału/tydz. (ALLOC 0,24) zadziała co ~5–6 tygodni i każdorazowo zrealizuje −12 %; przy ALLOC 0,12 praktycznie nie zadziała — czyli to sizing jest zmienną sterującą |
| pkt 15: ALLOC 0,24 → 0,20 | **kosmetyczne** | P(kill 52 tyg.) przy μ 0,75/σ 7: 0,24 → 83 %, 0,20 → ~75 % (interpolacja), 0,12 → 31 %, 0,08 → 9 %. Argument o locie 0,1 akcji (REDUCE niewykonalny) jest realny, ale rozwiązuje go `REDUCE_FALLBACK=close` albo wykluczenie nazw o kursie > X z koszyka (koszt tej reguły do zmierzenia), nie utrzymywanie 1,6× pełnego Kelly'ego |
| §7 „hit rate 52–58 % to cel", „σ tygodnia 6 p.p." | **poparte** | zgodne z backtestem (hit 55–58 %, σ 7,4) |
| plan testu „8 tygodni 3.0 vs 3.1" | **za krótki i źle skierowany** | 8 tygodni rozstrzyga o niczym poza wariancją; test ma być przekrojowy na 233 oknach (gotowe harnessy w katalogu `analiza/`) |

Ogólnie: propozycja dobrze diagnozuje (T6, T7, czynnik SOX), ale w części normatywnej konserwuje elementy bez dowodu (scoring, bramka, defensywne shorty jako alfa) i wprowadza jedną regułę na bazie panelu 44 spółek, która na 102 spółkach i 5 latach nie przechodzi kryterium stabilności w latach. Jej autorzy mieli 1 rok danych (`closes_1y.csv`); dziś jest 5 lat i wnioski trzeba uaktualnić.

---

## 6. Co zostawić, co skasować (pytanie 5)

| element | decyzja | uzasadnienie liczbowe |
|---|---|---|
| zwroty relatywne vs ^NDX, spread = śr. L + śr. S, równe strony dolarowe | **zostaje** | to jest poprawna miara L/S; neutralizacje β/σ bez hedgu indeksowego ją psują (`bt_neutralnosc.md`) |
| horyzont tygodniowy rotacji | **zostaje, w 2 transzach** (trzymanie 2 tyg.) | t 2,37 vs 2,09, obrót ×½, Sharpe netto 0,97 vs 0,79 |
| 5 nóg na stronę (na transzę) | **zostaje** | 10/10 i 15/15 obniżają Sharpe'a (0,66/0,60) |
| shorty akcyjne (`HEDGE_EPIC = classic`) | **zostaje** | L − S wymaga shortów na akcjach; tryb index to inny zakład (`PROPOZYCJA` pkt 16: −0,40 p.p./tydz.) |
| Model 3.0: scoring 20 czynników jako źródło koszyka | **do kosza jako źródło; zostaje jako nakładka ≤ 1 wymiana/stronę z mierzonym kosztem** | IC po becie/momentum −0,12; „goni kurs" 0,53–0,83; 10/16 stron nadpisanych; niereprodukowalny |
| lista B1(c) „ekspozycja AI" | **do kosza** jako czynnik selekcji; zostaje jako etykieta do pomiaru koncentracji | wyprodukowała ekspozycję 1,1–2,7 na SOX−NDX i 24/35 nóg long; to decyzja czynnikowa, nie selekcja |
| p = 38–62 % | **do kosza** | kalibracja odwrotna (p ≥ 61 % → 37,5 % trafień) |
| bramka reakcji 4 %/8 % + druga sesja + blokada sektorowa, REDUCE/CLOSE basis="cena" | **do kosza** (zastąpić vol targetingiem) | przekrojowo +0,08 p.p. (t 0,03); autokorelacja dzienna ≈ 0; po dniu ≤ −3 p.p. kolejne 3 sesje +1,43 (t 2,7); in-sample reakcje W1–W4 −3,44 p.p. |
| REDUCE/CLOSE basis="news" (twarde zdarzenia: wezwanie, zawieszenie, delisting, szokowy raport) | **zostaje**, ale tylko lista zamknięta | nie testowalne cenowo; to zarządzanie ryzykiem ogonowym, nie sygnał; koszt zerowy, gdy zdarzeń brak |
| moduł taktyczny (1–2 pozycje po newsie, 20 % kapitału) | **zawiesić do czasu testu** | n = 4 pozycje, suma +1,0 p.p. (history); 20 % kapitału na jedną nogę o σ dz. 4–6 % to σ ≈ 1 % kapitału dziennie z pojedynczej pozycji — największe skupienie ryzyka w systemie bez żadnego dowodu; dryf po skoku ≥ +12 % istnieje (fwd10 +3,5, t 2,2), więc kandydat na regułę mechaniczną, ale po teście, nie z newsów |
| stop 10 % z reopen | **do kosza** (z vol targetingiem stop jest zbędny; jeśli zostaje — bez reopen i 15 %) | v4 − v2 = −0,19 p.p./tydz. (t −1,7); 15 % bez reopen −0,19 → −0,12; na szumie ≈ 0 (`bt_symulacja-wykonania.md` B4) |
| kill switch 0,75 × szczyt | **zostaje**, ale ma być zdarzeniem o P ≤ 10 %/rok — co wymaga ALLOC ≤ 0,12 albo vol targetingu | tabela §3.3 |
| ALLOC 0,24 | **do kosza → 0,08–0,12 albo vol targeting 3,5 %/tydz.** | 1,6× pełny Kelly; P(kill 52 tyg.) 78–93 % |
| regime gate P0/P1/P2 (MA200/VIX/drawdown; P1 → REDUCE wszystkich, P2 → płasko) | **zdegradować do vol targetingu**; zostawić tylko P2 jako wyłącznik płynności (sesja ≤ −5 %, VIX > 40) | bramka aktywna 71/234 tyg., średnia 1,00 → 0,78 p.p., maxDD 71 → 72 (bez poprawy; `bt_rezim-i-zaklad-czynnikowy.md` §5 p.4); momentum w VIX > 20 miało WYŻSZĄ średnią (proxy 2,34 vs 0,82) — gate ucina dobre tygodnie |
| deklaracje falsyfikowalne D1–D3 | **zostają jako notatka**, bez konsekwencji w składzie | każda falsyfikacja → reguła po n = 1 (`audyt-regul.md` §2) |
| pre-mortem per noga | **zastąpić pre-mortem per CZYNNIK** (β_spread, ładunek SOX−NDX, udział grup branżowych, σ̂ koszyka) | 60–80 % wariancji to czynniki; pre-mortem LITE nazwał ryzyko i nic z tego nie wynikło |
| benchmark „sort po samym momentum" na papierze | **zostaje i awansuje do cienia (i)** | to jest kandydat na system właściwy |
| rozliczenie od D0 (`spread_pp`) jako główna miara | **zdegradować**; główna = od cen wejścia / od D+1 | różnice W4 +9,8, W7 +4,5 p.p.; rachunek gra inne okna |
| TradingView / FMP / newsy / elita analityków w rutynie sobotniej | **ograniczyć do: snapshot screenera (industry, close), kalendarz wyników, dywidendy** | reszta zasila scoring, który ma IC ≈ 0; budżet 36 min TV w W8 przekroczony o 80 % (raport W8) |
| walidator `waliduj_signals.py`, guard podwójnego biegu, `fills` od bota, `wykonanie` | **zostają** | higiena danych; bez nich żadna miara nie jest wiarygodna |

---

## 7. Konkretne rekomendacje (z liczbami i miejscem)

1. **`app.py` / panel Render — sizing.** `ALLOC_PCT` 0,24 → **0,10** natychmiast (gross 1,0; σ tyg. kapitału przy σ spreadu 7 p.p. ≈ 3,5 %; P(kill 52 tyg.) przy μ 0,75 ≈ 20 %). Docelowo zmienna `TARGET_WEEKLY_VOL = 0.035` i `GROSS_MAX = 1.6`: alokacja na nogę = min(ALLOC_PCT, TARGET_WEEKLY_VOL / σ̂_koszyka × 0,2), gdzie σ̂_koszyka (p.p./tydz.) jest liczona w sobotę z 60 dziennych spreadów składu i zapisywana w prerejestrowanym polu (np. `d0.sigma_koszyka` — jedno nowe pole, dopisane do walidatora i do listy pól w CLAUDE.md). Dowód: `bt_symulacja-wykonania.md` v8/v10, `pq_quant_out.md` §F. Siła dowodu: twarda (symulacja na 234 oknach + analityka Kelly'ego).
2. **`rutyny/tygodniowa.md` KROK B — źródło koszyka = ranking ilościowy ze skryptu** (`scripts/ranking.py`, deterministyczny, wejście: `closes` z Yahoo za 1 rok, snapshot TV industry, kalendarz wyników): momentum 6M rel. (skip 5 sesji) → TOP/BOTTOM; veto: raport w D+1…D+5; veto short: dzień ≤ −8 % w 3 sesjach albo 10 sesji ≤ −20 %; parowanie branżowe (5 par) jako konstrukcja A, TOP5/BOTTOM5 jako konstrukcja B. Model 3.0 może nadpisać ≤ 1 nogę na stronę; raport zapisuje obie wersje i rozlicza Δ. Siła: twarda dla momentum (t 2,1 brutto, 233 okna; 100 % percentyl wśród losowych), twarda dla parowania (F-test p < 0,001, ta sama średnia), poszlakowa dla veto short (t 0,8–2,8, niestabilne w latach).
3. **`rutyny/tygodniowa.md` — 2 transze.** `long`/`short` po 10 nazw (5 z bieżącej soboty + 5 z poprzedniej), wagi równe 1/10 strony; bot rotuje tylko nazwy, które wypadły. Jeśli lot 0,1 akcji × kurs > 0,5 × alokacja nogi dla ≥ 2 nazw — wariant B (5/5, 1 tydz.) i adnotacja. Siła: poszlakowa-twarda (t 2,37 vs 2,09 in-sample, mechanizm dywersyfikacji w czasie jest teoretycznie oczywisty, obrót ×½ jest pewny).
4. **`rutyny/dzienna.md` KROK 2 — skasować wyzwalacze basis="cena" (REDUCE/CLOSE 4 %/8 %, druga sesja, blokada sektorowa); zostawić basis="news" z listą zamkniętą (wezwanie, delisting, zawieszenie, raport/guidance w trybie szoku ≥ |8 %| pre-market z dokumentem źródłowym) oraz REDUCE przy P2.** Puls staje się raportem kontrolnym (pokrycie rachunku, zgodność wykonania, σ̂ bieżąca, kalendarz jutra). Siła: twarda (przekrojowo +0,08 p.p., t 0,03; autokorelacja ≈ 0; po złym dniu +1,43, t 2,7).
5. **`rutyny/tygodniowa.md` KROK A — metryka główna: spread od cen wejścia (fills) do następnej rotacji; obok 5-sesyjna od D0.** Tabela prerejestrowanych metryk (§4.1 p.4) w stałej kolejności; obowiązkowe zdanie o t i n. Siła: twarda (różnice okien W4 +9,8, W7 +4,5 p.p.).
6. **Nowy plik `rutyny/reguly.md`** z sekcjami OBOWIĄZUJĄCE / KANDYDACI / WYJĄTKI (≤ 4 tyg.) / UCHYLONE i kryterium awansu z §4.1 p.2; przeniesienie 36 reguł z `audyt-regul.md` §1: wszystkie koszykowe → KANDYDACI lub UCHYLONE; „zakaz shorta po spadku 10-ses. ≤ −20 %" → OBOWIĄZUJĄCA po potwierdzeniu holdoutem (dziś t −2,4 na całości). Siła: proces — twarda w sensie higieny, nie wyniku.
7. **Cztery koszyki cienie na papierze od W9** (§4.1 p.5), rozliczane jednym skryptem; decyzja o trybie bota po 26 tygodniach; wcześniejsza decyzja dopuszczalna wyłącznie o wariancji (σ faktycznego > 1,5× cienia przy nie wyższej średniej, test F). Siła: proces.
8. **Moduł taktyczny: zawiesić** (`tactical=[]`, `TACTICAL_ALLOC_PCT` 0) do czasu testu przekrojowego reguły „long po dniu ≥ +12 % rel., trzymanie 10 sesji" (fwd10 +3,5 p.p., t 2,2, n = 307) — kandydat, nie reguła; 20 % kapitału na jedną nogę σ 4–6 %/d to σ ≈ 1 % kapitału/dzień bez dowodu. Siła: poszlakowa (dryf istnieje, ale niestabilny w latach: 2022 −0,9, 2026 −0,35 dla ≥ +8 %).
9. **Regime gate**: P1 bez działań (tylko flaga), P2 wyłącznie dla płynności (sesja ≤ −5 % lub VIX > 40 → płasko do histerezy); redukcję ekspozycji w podwyższonej zmienności robi vol targeting automatycznie (σ̂ rośnie → gross spada). Siła: poszlakowa (gate obniżał średnią bez poprawy maxDD; momentum lepsze przy VIX > 20 na D0 — t 3,0 dla proxy).
10. **Rutyna sobotnia — budżet poznawczy.** Ograniczyć TV/FMP/elitę do danych wejściowych skryptu (industry, close, kalendarz wyników, dywidendy): przy IC scoringu ≈ 0 każda minuta researchu per spółka to koszt bez zwrotu, a budżet czasu już jest przekraczany (36 min vs 20). Siła: poszlakowa (wynika z braku IC, nie z bezpośredniego testu kosztu czasu).

---

## 8. Czego nie da się stwierdzić z tych danych (uczciwie)

- **Czy Model 3.0 ma jakąkolwiek przewagę** — 7 tygodni przy σ 11 p.p. daje przedział ufności dla μ ≈ ±10 p.p.; nie da się odróżnić +2 od −2 p.p./tydz. Jedyne, co da się powiedzieć: jego Wynik jest w ~90 % proxy bety/momentum, a reszta ma IC ujemny przy t −1,5 (też nieistotne).
- **Czy momentum 6M zadziała out-of-sample** — t 2,1 na danych z survivorship bias (skład dzisiejszy: zwycięzcy w uniwersum), w okresie 2023–2026 zdominowanym przez jeden motyw (AI/semis). Po korekcie o bias rozsądnie zakładać Sharpe 0,3–0,6, a nie 1,0. W 2023 momentum 6M było ujemne (−0,24 p.p./tydz.).
- **Czy parowanie branżowe utrzyma średnią** — przy taksonomii z jednego snapshotu TV (2026-W8) narzuconej wstecz na 5 lat; grupy zmieniały skład. Redukcja σ jest mechanicznie pewna, równość średniej — nie.
- **Koszty rzeczywiste CFD** — 6 %/rok i 0,20 % RT to założenia; brak danych o faktycznych stawkach overnight i spreadach brokera dla tych nazw. Jeśli finansowanie wynosi 8–9 % (benchmark 4 % + marża 2,5 % obie strony), netto spada o kolejne 0,1 p.p./tydz., co przy sygnale 0,5–0,8 p.p. jest istotne.
- **Dryf po zdarzeniach jako proxy PEAD** — bez dat raportów nie odróżnię niespodzianki wynikowej od innych ruchów; wyniki §D są o „dużych ruchach", nie o wynikach.
- **Czy wejście w poniedziałek po luce systematycznie pomaga** — W4–W7 +15,4 p.p., ale t 1,0 i rozkład dwumodalny; na 234 oknach v2 − v1 = +0,10 p.p. (t 0,24) — czyli nic.
- **Jakakolwiek sezonowość tygodniowa** — t < 1,3 dla każdego dnia; brak efektu to też wynik.

---

## 9. Źródła i ścieżki

- Dane: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv`.
- Skrypt własny: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/pq_quant.py` → `pq_quant_out.md`, `pq_quant_summary.json` (baseline N×h, momentum N×h z nakładaniem, premia za zmienność/betę, dryf po ruchach, dzień tygodnia, autokorelacja, symulacja kill switcha, Kelly, W1–W7 vs baseline).
- Backtesty siostrzane (ten sam katalog): `bt_momentum.md/.py`, `bt_odwrocenie.md/.py`, `bt_neutralnosc.md/.py`, `bt_rezim-i-zaklad-czynnikowy.md/.py`, `bt_symulacja-wykonania.md/.py`, `dekompozycja-wynikow.md`, `moc-predykcyjna-modelu.md` (+ `mp_*.py`), `audyt-regul.md` (+ `audyt_regul.py`), `wykonanie-bota.md` (+ `wyk_*.py`).
- Repo: `signals.json` (history W1–W7), `rutyny/tygodniowa.md`, `rutyny/dzienna.md`, `rutyny/PROPOZYCJA-2026-10-12-model-3.1.md`, `reports/raport-2026-W8.html` (deklaracje, benchmark momentum, konsekwencje D1-W7), `app.py` (ALLOC_PCT, STOP_LOSS_PCT, kill switch), `CLAUDE.md`.
- Literatura (z pamięci, do weryfikacji abstraktów): Jegadeesh 1990 JF; Lehmann 1990 QJE; Moskowitz–Grinblatt 1999 JF; Bernard–Thomas 1989 JAR; Chordia–Goyal–Sadka–Sadka–Shivakumar 2009 JFE; Avramov–Chordia–Goyal 2006 JF; Hameed–Mian 2015 JFQA; Medhat–Schmeling 2022 RFS; Ang–Hodrick–Xing–Zhang 2006 JF; Frazzini–Pedersen 2014 JFE; Novy-Marx 2012/2013 JFE; Chan–Jegadeesh–Lakonishok 1996 JF; Harvey–Liu–Zhu 2016 RFS; Cederburg–O'Doherty–Wang–Yan 2020 JFE; Kaminski–Lo 2014 JFM; French 1980 JFE; Kelly 1956; Thorp 2006 (fractional Kelly).
