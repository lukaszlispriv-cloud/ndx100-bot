# Audyt reguł procesu decyzyjnego NDX100 (W1–W8) — rejestr, test, werdykt

Agent: audytor procesu decyzyjnego · 18.10.2026 · repo `/home/user/ndx100-bot` (gałąź `claude/gifted-lamport-iwzpop`, HEAD 7b6b3e6).

Skrypt i wyniki: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/audyt_regul.py` →
`audyt_regul_wyniki.json`, `audyt_regul_wykluczenia.csv` (80 kontrfaktycznych nóg), `audyt_regul_nogi.csv` (70 nóg W1–W7 z p), `audyt_regul_stdout.txt`.
Dane: `scratchpad/dane/closes_5y.csv` (1257 sesji, zamknięcia **bez korekty o dywidendy** — stąd spread W2 6,40 vs 6,19 w raporcie, W6 −5,59 vs −5,89; różnice to PEP/NVDA/AVGO/CMCSA ex-date, bez wpływu na wnioski), raporty `reports/raport-2026-W1…W8.html` (teksty w `scratchpad/analiza/txt/`), `rutyny/tygodniowa.md`, `rutyny/dzienna.md`, `rutyny/tradingview.md`, `INSTRUKCJA.md §8`, `rutyny/README.md`, `reports/puls-2026-09-15…29.html`, `data/tv-screen-2026-W8.json` (kapitalizacja i sektor — statyczne proxy).

Konwencja: zwrot nogi = [D+n/D0−1] spółki − [D+n/D0−1] ^NDX w p.p.; SHORT ze znakiem minus (dodatni = short wygrał). „Wykluczona wygrałaby” = dodatni zwrot nogi, której reguła nie wpuściła. Testy przekrojowe: 103 spółki uniwersum, okna 5-sesyjne nienakładające się (224 okna, 2021-11 → 2026-10), t klastrowane po dacie (średnia w oknie, potem t po oknach). **Wszystko in-sample i przy n = 7 tygodni koszyków; to, co nie ma testu przekrojowego, jest anegdotą.**

---

## 0. Wynik w sześciu zdaniach

1. W raportach W1–W8 i obu rutynach naliczyłem **36 reguł/filtrów/konsekwencji** (tabela §1). **17 z nich powstało po jednej obserwacji** (jedna noga, jedna deklaracja, jeden tydzień), **żadna nie ma retestu** (jedyny zaplanowany test to D2-W8 „na papierze”), a **co najmniej 6 par jest wzajemnie sprzecznych** (§3).
2. Reguła o największym wpływie na skład koszyków — „**przegrana bez odzyskanej siły relatywnej = poza koszykiem**” (W3→W5→W6→W7→W8, zaostrzana po każdej falsyfikacji) — **nie ma żadnego poparcia w danych**: na 5 latach noga z top-kwintyla momentum, która przegrała tydzień i nie odzyskała siły ostatniej sesji, daje w kolejnym tygodniu **+0,66 p.p.** (n = 1108, t = 0,44) wobec +0,32 p.p. dla „odzyskanej siły” i +0,59 dla wygranych; przy przegranej < −4 p.p. nawet **+1,53 p.p.** (t = 1,26). In-sample (10 wykluczeń W2–W7) wykluczone nogi dały średnio −1,74 p.p., ale ich zamienniki były **gorsze o 0,84 p.p./nogę** (LITE W5: koszt 18,09 p.p. na nodze). W W8 ten filtr zdjął z TOP5 SNDK/STX/AVGO/AMAT/KLAC/FTNT (nierozstrzygnięte, dane kończą się 16.10).
3. Jedyna reguła koszykowa ze znakiem zgodnym z danymi to **zakaz shortowania po kolapsie** (D2-W4 >20%/10 sesji; od W7 >12%): in-sample INTU poza koszykiem W5–W7 oszczędziło **−20,8 p.p. na nodze** (INTU odbijał 3/3 tygodnie), a przekrojowo short po spadku 10-sesyjnym ≤ −20% traci **−1,64 p.p./tydz.** (n = 213, t = −2,42); ≤ −12%: −0,71 (t = −1,7). Efekt jest mały i słabnie przy progu 12%; wariant „luka 1-dniowa >10%” (D2-W7, TMUS) **nie ma poparcia** (−0,09…−1,01 p.p., t ≈ 0).
4. **Reguła DOJ/NVDA nic nie kosztowała**: NVDA poza koszykiem W4–W7 dała sumę −0,67 p.p. na nodze (3 z 4 okien NVDA przegrałaby z indeksem), a zamienniki (MRVL W4, AMD W5) były lepsze o +1,99 p.p./nogę. Koszt dla spreadu ≈ 0 (−0,1 p.p. łącznie). Problem nie jest w skutku, lecz w konstrukcji: reguła imienna bez daty wygaśnięcia, oparta na zdarzeniu bez związku z 5-sesyjnym zwrotem.
5. **Bramka 4%/8% + druga sesja** w symulacji od D0 (bez blokady sektorowej) poprawia sumę W1–W7 z −3,82 do **−1,04 p.p.** (+2,78), ale cały zysk to W7 (+5,55), a W4 kosztuje −3,13; przekrojowo sygnał REDUCE (rel ≤ −4 p.p. dwie sesje, abs ≤ −4%) nie przewiduje reszty okna: **+0,08 p.p.** (n = 3442, t = 0,03). Bramka obniża wariancję, nie podnosi oczekiwanego wyniku — i tak ma być opisana.
6. **Kalibracja p jest odwrotna**: nogi z p ≥ 61% trafiły 12/32 (37,5%, śr. −0,79 p.p.), nogi z p ≤ 58% — 15/25 (60%, +1,20 p.p.); corr(p, zwrot) = −0,16. Pasmo 38–62% nie niesie informacji; w W8 rutyna już sama je zawęziła (|p−50| śr. 6).

---

## 1. Rejestr reguł — wszystko, co znalazłem (36 pozycji)

Legenda kolumny „n”: liczba obserwacji, które uzasadniały wprowadzenie. „Skutek” — z `audyt_regul_wyniki.json` (sekcje `wykluczenia`, `reguly_agregat`, `testy_przekrojowe`, `symulacja_bramki`), o ile da się policzyć. „P/Z/0” = pomogła / zaszkodziła / nierozstrzygalne.

### 1A. Reguły koszykowe wprowadzone w raportach (nie ma ich w `tygodniowa.md`)

| # | Reguła | Wprowadzona | Wyzwalacz | n | Zastosowana później | Skutek in-sample (p.p. na nodze, vs ^NDX) | Test przekrojowy 5 lat | Werdykt |
|---|---|---|---|---|---|---|---|---|
| K1 | **Zasada świeżej luki**: spółka z luką po D0 poza koszykiem (NVDA, CRWD) | W1 (27.08) | uczciwość rozliczenia, nie prognoza | 0 | wygasła naturalnie w W2 | NVDA W1 +3,05, CRWD +14,73 — „koszt” 17,8 p.p., ale to artefakt księgowy (zysk fantomowy) | — | 0 (zasada księgowa, zasadna) |
| K2 | **Event w oknie → poza koszykiem / kara event-risk 0–10** | W1 (AVGO, MRVL), B4 | precedens AVGO −12,6% kwartał wcześniej | 1 | W2 (PANW, AVGO), W3 (ADBE, CPRT, AAPL), W5 (MU wpuszczony z karą 8), W6 (PEP, MRVL, COST), W8 (NFLX, TXN, LRCX, WDC, META) | 9 rozstrzygniętych: longi z raportem −5,8 śr. (AVGO W1 +3,0, MRVL W1 −12,3, AVGO W2 −3,3, PANW W2 −10,7) → **P**; shorty z eventem +3,2 śr. (ADBE W3 +4,8, CPRT +10,6, PEP W6 +0,2, COST −2,6) → **Z**. Wariant „bez nóg EVENT” (12.10): tylko MU W5 (+0,23). | niemożliwy (brak dat raportów w danych) | 0 — asymetria long/short, n = 9 |
| K3 | **Kara event: „15 zamiast 8”** jeśli D1-W5 padnie | W5 (29.09) | prerejestracja | 0 | nie uruchomiona (D1-W5 TAK) | — | — | archiwum |
| K4 | **Kara event pozytywny 6 → 3** | W7 (10.10), konsekwencja D3-W6 | MRVL +2,11 po Investor Day (n = 1) | 1 | W7: LITE kara 0 („3 skompensowane premią zbieżności”) → LITE −19,82; MRVL kara 1 → −11,75 | przyczyną W7 był sektor, nie OCP — skutek nierozstrzygalny; wada proceduralna: kara netowana premią | — | **do kosza** (n = 1, netowanie) |
| K5 | **Kryterium remisu „bez raportu w oknie”** (flaga `kryterium_event_remis`) | 12.10 (B4) | decyzja właściciela | 0 | W8 (wszystkie 10 nóg bez raportu D+1…D+5) | nierozstrzygnięte | — | 0 (nieszkodliwe) |
| K6 | **Nie shortuj żywego celu wykupu** (WDAY) + „fala M&A software” (ADBE W2) | W2 (29.08) | WDAY +7,3% w 2 sesje po doniesieniach Silver Lake (n = 1) | 1 | WDAY poza W2–W8; ADBE poza W2 | WDAY jako short wygrałby 5/6 okien: +4,74 / +4,56 / +1,53 / +3,06 / 0,00 / −7,75 = **+15,1**; ADBE W2 +8,96. Zamiennik PEP W2 +2,81 (Δ −1,9 / −6,1) → **Z** (−3…−5 p.p. spreadu łącznie) | — | **archiwum jako ryzyko ogonowe**, nie reguła skuteczności; limit czasowy |
| K7 | **Rozproszenie short-booka poza software, czynnik „ryzyko oferty”** | W2 | WDAY (n = 1) | 1 | W2–W8 (CMCSA/PEP/SBUX/NFLX/TMUS stale) | shorty defensywne 13/18 trafień, suma +10,1 (do W6 13/14; W7 0/4 = −46,9); software/inne 6/17, suma +29,2 (INTU, APP). | dolny kwintyl momentum: sektory defensywne −0,05 p.p./tydz. dla shorta (t −0,3) vs technologia +0,21 (t −0,9) — **brak przewagi defensywnych shortów** | 0 — „13/14” to seria, nie efekt |
| K8 | **Nie kupuj po jednodniowym skoku / pogoni** (CRWD +15% W2, SNDK +12% W3, ALNY −6% W6 jako short, ADSK −8% W3, TRI, AXON) | W2–W3 | CRWD W2, precedens „po +12% ujemna wartość 4-sesyjna” (n = 1) | 1 | W3 SNDK, W4 SNDK, W6 ALNY, W7 „pogoń” wielokrotnie | 7 przypadków: śr. −0,10, 4/7 wykluczonych wygrałoby (ADSK +1,9, TRI +3,1, AXON +6,5, SNDK W4 +1,8); pomogło: SNDK W3 −5,5, CRWD −2,8, ALNY −5,7 | top-kwintyl po skoku 1-dn ≥ +8%: **+0,79** (t 0,6); ≥ +12%: **+1,06** (t 2,21); 10 sesji ≥ +15%: **+1,13** (t 2,81) → kontynuacja, nie odwrócenie | **Z / do kosza** (znak przeciwny do danych) |
| K9 | **Koszyk long bez płatników capexu** (odbiorca bije płatnika; MSFT poza) | W3 (5.09) | MSFT −3,07 w W2 (n = 1) | 1 | MSFT poza W3–W7; W8 odwrócone (GOOGL, MSFT w koszyku) | MSFT: −0,22 / −0,35 / −0,12 / +3,15 / +4,37 = **+6,83** (2/5 wygrałby) → lekko **Z**; odwrócenie w W8 też po n = 1 (tydzień W7) | — | archiwum (etykieta opisowa, nie reguła) |
| K10 | **„Wraca po odzyskaniu siły relatywnej” → „przegrana bez odzyskanej siły = poza koszykiem”** | W3 LITE (warunek) → W5 (reguła) → W6 ALAB → W7 TER/AMAT/AMD/NFLX/PAYX → W8 bez wyjątku + rozszerzenie na kandydatów spoza koszyka | LITE −5,4 w W1 i −1,5 w W2 (n = 1 spółka) | 1 | W5, W6, W7, W8 (9 nóg W7 + 6 kandydatów) | 10 wykluczeń W2–W7: wykluczone śr. **−1,74** (3/10 wygrałyby), zamienniki **gorsze o 0,84/nogę** (LITE W5 +16,06 vs ALAB −2,03 = −18,1; AVGO W5 −0,16 vs STX −9,62; MRVL W5 +6,34 vs TER +10,14; W7 TER/AMAT/AMD −13,8/−13,8/−7,6 vs MRVL/PANW/CSCO −11,8/−12,8/−3,8). Łącznie dla spreadu ≈ **−1,5 p.p.** (zamienniki gorsze). MU W7 nadpisanie −9,09. | top-kwintyl: przegrana bez odzyskania **+0,66** (n 1108, t 0,44) = odzyskana +0,32 = wygrana +0,59; prev < −4: **+1,53** (t 1,26). Short-side lustro: +0,14 vs −0,24 — zero. **Brak sygnału**; jeśli coś, lekkie odwrócenie. | **Z / do kosza** — największy koszt proceduralny systemu (wymusza churn 5–9 nóg/tydz.) |
| K11 | **TSLA poza koszykiem po 3 przegranych** (konsekwencja D2-W3) | W4 (12.09) | 3 nogi TSLA −0,13 / −1,15 / −3,80 (jedna deklaracja) | 1 (3 nogi) | W4–W8 | short TSLA: W4 +5,28 (11 s; +1,26 na 5 s), W5 −1,92, W6 −3,02, W7 +1,82 = **+2,16**, 2/4 wygrałby. Zamiennik ADSK W4 +5,55 (Δ +0,27). Raporty piszą „reguła znów chroniła” (W6 tak, W7 nie). | — | 0 (szum; warunek powrotu „cięcie celu przez elitę” niefalsyfikowalny, bo elita nie pokrywa TSLA) |
| K12 | **NVDA poza koszykiem do domknięcia DOJ/Groq** | W4 (12.09) | DOJ 10.09 + REDUCE 11.09 + marża (n = 1) | 1 | W4–W8 (W8 mimo wyniku 73,1) | NVDA long: +1,75 (11 s; +0,88 na 5 s) / +0,47 / −2,24 / −1,12 = **−0,67**; zamienniki MRVL W4 +3,60, AMD W5 +2,53 → Δ **+1,99/nogę** → koszt dla spreadu ≈ 0 (reguła lekko pomogła, 3/4 okien NVDA przegrałaby) | — | 0 — **nie kosztowała**, ale bez daty wygaśnięcia; mechanizm (śledztwo) nie ma związku z 5-sesyjnym zwrotem |
| K13 | **Zakaz short po >20% spadku w 10 sesji przez 4 tyg.** (konsekwencja D2-W4) | W5 (29.09), do 16.10 | ADSK +1,20 przeciw w 5 sesjach (n = 1) | 1 | INTU poza W5–W7; PAYX W5 „w duchu” | INTU short: −2,58 / −7,47 / −12,89 = **−20,8** → **P** (3/3); zamiennik PEP W5 +3,79 (Δ +6,37). PAYX W5 +2,12 (koszt). | dolny kwintyl, r10 ≤ −20%: **−1,09** (n 126, t −1,54); całe uniwersum ≤ −20%: **−1,64** (n 213, **t −2,42**) | **P — jedyna reguła koszykowa ze znakiem zgodnym z danymi**; efekt mały (1–1,6 p.p./tydz. na nodze) |
| K14 | **Sito >12%/10 sesji wymaga twardego negatywu w oknie** (konsekwencja D2-W6) | W7 (10.10) | PAYX −4,85 (n = 1) | 1 | W7: PAYX poza (−12,85 → P); W8: MSTR, CRWV, RKLB, INTC, NBIS, AMAT, LRCX, TER, ARM, KLAC, SNDK, WDC, STX, MPWR jako shorty poza (nierozstrzygnięte) | W7 PAYX poza oszczędziło 12,85 na nodze; zamiennik TMUS −12,57 (Δ +0,28) | r10 ≤ −12%: dolny kwintyl **−0,66** (n 412, t −1,8); uniwersum −0,71 (t −1,7); pasmo (−20; −12]: −0,47 (t −1,59) | P słabo — to K13 z niższym progiem; **jedna reguła, jeden próg** (20%), wymóg „twardego negatywu” nietestowalny |
| K15 | **Nie shortuj w 1. oknie po jednodniowej luce >10% bez wyników** (konsekwencja D2-W7) | W8 (17.10), „retest 12 tyg.” | TMUS +12,57 przeciw (n = 1) | 1 | W8: brak kandydata | — | luka ≤ −10% w 3 sesjach: dolny kwintyl −0,09 (n 93, t 0,77); uniwersum −1,01 (n 246, t ≈ 0) → **brak poparcia** | **do kosza** (podzbiór K13 bez sygnału) |
| K16 | **MU wychodzi z W8 + „bez odzyskanej siły” bez wyjątku dla wyceny** (konsekwencja D1-W7) | W8 | MU −9,09 (n = 1) po jawnym nadpisaniu K10 | 1 | W8 (MU poza mimo elity 4/4 i wyceny) | nadpisanie K10 w W7 kosztowało −9,09; ale K10 sama nie ma sygnału (wyżej) — to reguła „karząca” za złamanie reguły bez wartości | j.w. K10 | **do kosza** razem z K10 |
| K17 | **Filtr siły relatywnej dla kandydatów SPOZA koszyka** (SNDK/STX/AVGO/AMAT/KLAC/FTNT poza TOP5) | W8 (17.10), test D2-W8 | W6–W7 (n = 2 tygodnie jednego czynnika) | 2 | W8 | **nierozstrzygnięte** (okno 16.10→23.10; dane do 16.10). Raport sam nazywa to „nadpisaniem wyniku modelu”. | K10 przekrojowo: brak sygnału; top-kwintyl po tygodniu < −4 p.p.: +1,53 (t 1,26) → oczekiwanie raczej przeciw filtrowi | **nie awansować**; D2-W8 to pierwszy prawdziwy test w historii systemu — zaliczyć wynik do rejestru |
| K18 | **Limit 2 nazwy na blok pamięć/WFE** | W5 (29.09) | koncentracja MU+SNDK+STX = 60% longów w W3 (n = 1) | 1 | W5 (LRCX/AMAT poza), W6 (LRCX/KLAC poza) | wykluczone +8,75 / +9,19 / −8,49 / −5,72; zamienniki lepsze o +1,49/nogę (TER W5 +10,14, AMAT W6 −6,36) → 0/P | dywersyfikacja — nie testuję predykcji | **zostaje** (konstrukcyjna, bezkosztowa) |
| K19 | **Rozproszenie longa po wąskich gardłach** (4–5 bloków) | W4 (12.09) | pamięć źródłem strat W3 (n = 1) | 1 | W4–W7 | W7: 5 „różnych” gardeł spadło razem (long śr. −11,46) — bloki nie były niezależne (`dekompozycja-wynikow.md`: SOX−NDX tłumaczy 70%+) | — | 0 — definicja „bloku” zła (wszystko AI-hardware); zastąpić pomiarem bety/korelacji |
| K20 | **Pre-mortem: „nowa podaż konkurenta” jako kontrargument nr 1 dla tez niedoboru** | W6 (3.10) | STX/Toshiba −9,62 (n = 1) | 1 | W7 pre-mortem MU (strajk, nie podaż — pominięte wg PROPOZYCJI) | nietestowalne | — | archiwum (checklista, nie reguła) |
| K21 | **„Momentum bez rewizji = pułapka” / „nie shortujemy pędu”** (SNPS W6/W7, INTC W5, CEG W7, PLTR W7) | B1(d), od W1 | zasada modelu | — | wielokrotnie | SNPS W6 +3,86 (koszt), W7 −5,36 (P); CEG W7 −3,47 (P); PLTR W7 −5,52 (P); INTC W5 short −1,09 (P) | j.w. K8: momentum po skoku kontynuuje (+1,1, t 2,2–2,8) → „pułapka” nie istnieje w danych | 0/Z — zbędna, momentum i tak jest czynnikiem (7%) |
| K22 | **„Nie shortujemy tego, czego nie rozumiemy”** (SHOP/BKNG W4, DASH W5–W6, FER W7) | W4 | brak katalizatora | — | W4–W7 | SHOP W4 −8,72 (P), BKNG +8,87 (Z), DASH W5 −4,28 / W6 −3,64 (P), FER W7 −4,01 (P), ARM W7 +8,96 (Z) → śr. −0,5, 2/6 | — | 0 (szum) |
| K23 | **Odbiorca vs płatnik: płatnicy w dolnym kwartylu czynnika 10** | W3 | lekcja W2 | 1 | W3–W7; W8 GOOGL/MSFT w koszyku = de facto zawieszenie | patrz K9 | — | j.w. K9 |
| K24 | **Czynnik cyklu pamięci 80→70→80**, koncentracja MU 55→35 | W4→W5 | TrendForce 4Q26 hamowanie → podniesienie (n = 1 każda) | 1 | — | nietestowalne (wagi jakościowe) | — | archiwum — zmiana wag po jednym komunikacie |
| K25 | **„W oknie ze zdarzeniem stopowym czynnik stóp z pełną wagą różnicuje wewnątrz bloków”** | W4 | stopy rozstrzygnęły W3 (n = 1); D3-W4 sfalsyfikowana (MU nie amortyzował) | 1 | W5 (ALAB mimo tego wpuszczony) | sfalsyfikowana własną deklaracją, nie wycofana | — | **do kosza** |
| K26 | **Taktyczne: odczekaj ≥1 sesję po luce wynikowej** | W6 (lekcja) | AKAM −3,26, ACN −7,32 (n = 2) | 2 | **nie wpisana** do `dzienna.md`; W7 ERIC wejście po +11,8% → +3,99 (kontrprzykład) | n = 3, 1 za / 2 przeciw | — | archiwum (kandydat) |
| K27 | **Nadpisania „°” (TTWO, MRNA poza shortami W8)** rozliczane na papierze | W8 | GTA VI, momentum MRNA | 0 | W8 | nierozstrzygnięte | — | 0 (dobra praktyka: nadpisanie oznaczone i mierzone) |

### 1B. Reguły w `rutyny/tygodniowa.md` i `rutyny/dzienna.md`

| # | Reguła | Wprowadzona | Wyzwalacz | n | Zastosowana | Skutek | Test | Werdykt |
|---|---|---|---|---|---|---|---|---|
| R1 | **Bramka 4%/8%** — trzy warunki (względny 4–8 / >8 p.p. od ceny wejścia; **potwierdzenie drugą sesją**; bezwzględny ≥4% / ≥8%) | 18–19.09 (pierwsze użycie: puls 19.09; `INSTRUKCJA.md §8`), formalnie `dzienna.md` 29.09 | LITE CLOSE 15.09 od D0 przy pozycji na plusie (−4,77 USD); 4 reakcje cenowe 27.08–18.09 = −17,43 USD, bramka wykonała 0/5 (audyt 28.09) | 5 wpisów (jedno zdarzenie 14–15.09) | po 29.09: STX REDUCE 2.10 (news; niewykonalny — 1 lot), LITE CLOSE 14.10 (cena od D0, bo stop bota skasował fills), PANW REDUCE 16.10 (stop i ponowne otwarcie) → **n = 2 wpisy cenowe, 1 „wykonany” przez nieotwieranie** | history: reaction_pp W1–W7 = 0 / −0,45 / +0,09 / −3,08 / 0 / 0 / +2,08 = **−1,36** (z czego −3,44 to stary protokół sprzed bramki). Symulacja protokołu od D0 (proxy wejścia, bez blokady sektorowej) W1–W7: bez reakcji −3,82 → **−1,04** (+2,78; W7 +5,55, W4 −3,13, W6 +0,36, reszta 0). Bez 2. sesji: −4,76 (W4 −7,2). Stary protokół (tylko względny, od D0): −3,47. | sygnał REDUCE (rel ≤ −4 dwie sesje, abs ≤ −4) → reszta okna **+0,08 p.p.** (n 3442, t 0,03); poziom CLOSE: +0,01; long top-q +0,19 (t −0,05); short bot-q **−0,22 (t −1,67)** | **zostaje** jako bezpiecznik wariancji, **nie** jako źródło wyniku; druga sesja zostaje (W4); opis „chroni oczekiwany wynik” — skreślić |
| R2 | **Blokada sektorowa 3%** (brak wpisu cenowego, gdy sektor spadł >3%) | 18–19.09 (puls 19.09), `dzienna.md` 29.09; pomiar równoległy TV 12.10 (`sektor_tv=false`) | 14.09 optyka (n = 1) | 1 | 13.10 (LITE, MU „obserwowane, blokada sektorowa”) → LITE 12.10→16.10 **−12,39 p.p.**, MU −6,33; bot i tak zamknął stopem 13.10 | W4 (14.09): blokada oszczędziłaby −3,08 (reakcje po sektorowym dniu były złe) → P; W7 (13.10): opóźniła cięcie → Z. **n = 2, znaki przeciwne** | PROPOZYCJA 3.1 (12.10): 4/5 longów ruszyło się z sektorem — blokada „nie łapie dnia, gdy każdy sektor spadł” | 0 — zostaje do czasu 5 rozbieżnych werdyktów TV (jak zapisano), ale **bez** tezy o skuteczności |
| R3 | **CLOSE tylko twarde (news), REDUCE miękkie (rekom/short/news); działają od razu bez bramki** | od startu; kejs TTD | — | — | TSLA REDUCE 1.09 (−0,45), NVDA REDUCE 11.09 (+0,09), STX REDUCE news 2.10 (+1,05 papier, 0 wykonane) | 3 reakcje, suma +0,69 na papierze, 0 wykonanych | — | zostaje (ryzyko ogonowe) |
| R4 | **Limity: 2 nowe wpisy/dzień; REDUCE→CLOSE nie odwrotnie; raz zredukowana zostaje do soboty** | od startu | — | — | W4: 5 wpisów przez 3 dni | „zostaje do soboty” kosztowało w W4: LITE CLOSE 15.09 → LITE +4,2% 18.09, odbicie bez pozycji; 5 wpisów wisiało 11 sesji | — | zostaje z wyjątkiem: wpis cenowy wygasa, gdy ruch względny wróci < 2 p.p. (histereza wpisu) — **propozycja, nie reguła** |
| R5 | **Reżim P0/P1/P2 + histereza powrotu + eskalacja o 1 za sygnały systemowe; poziom surowszy z 2 źródeł (12.10)** | od startu; 12.10 | prerejestrowane progi | — | **nigdy nie uruchomiony** (P0 przez 36 biegów; 16.10 drawdown −6,5%, VIX 20) | n = 0 | `bt_rezim-i-zaklad-czynnikowy.md §4` (inny agent) | zostaje (prerejestrowany, nietknięty) |
| R6 | **p = 50% + 0,5×(wynik−50), obcięte 38–62%** | Model 3.0 | — | — | 70 nóg | p ≥ 61: **12/32 (37,5%), −0,79 p.p.**; p ≤ 58: **15/25 (60%), +1,20**; corr(p, zwrot) = **−0,16**; p = 62 (n 21): 42,9% | — | **zmienić opis**: p nie jest prawdopodobieństwem; publikować jako „ranga wyniku”, bez %; kalibrację liczyć co 10 tygodni |
| R7 | **Limity bloków w scoringu** (rewizje+EPS+marże ≤31; AI+cykl+capex+cyber ≤25; wycena+stopy+FX ≤16) | Model 3.0 | — | — | co tydzień | nietestowalne z zewnątrz (wagi jakościowe) | — | zostaje zamrożone (z PROPOZYCJĄ: nie stroić) |
| R8 | **Veto −1 kwintyl** (governance, koncentracja klienta, krypto-beta, produkt pojedynczy) | Model 3.0 | — | — | MSTR i PDD poza każdym koszykiem; W8 PLTR, APP, TSLA, CRWV | MSTR jako short: −2,6 / −11,8 / +7,7 / −16,9 / −0,1 / +3,8 / +5,9 = **−14,05** (P, 3/7); PDD: +1,9 / +4,4 / +4,8 / +2,2 / +5,7 / −7,7 / −5,0 = **+6,37** (Z, 5/7); CRWV W7 short +19,7 (Z) | — | 0 — zostaje jako ryzyko ogonowe (zmienność MSTR 12–17 p.p./tydz. uzasadnia veto niezależnie od znaku) |
| R9 | **Elita: zbieżność ≥3 = premia; nie shortuj przy ≥3 Buy elity; sygnały spadkowe tylko Rasgon/Curtis/Malik-watch; waga −1 stopień bez weryfikacji na żywo** | Model 3.0; obniżenie wagi 29.09 | — | — | MU elita 4/4 W5–W7: +0,23 / −4,51 / −9,10; profile nieweryfikowane W4–W8 (zawsze −1 stopień) | MU z najsilniejszą zbieżnością w historii systemu dała 2 z 3 ostatnich tygodni ujemne; „−1 stopień” nigdy nie zmienił decyzji (raporty: „decyzji nie zmienia”) | nietestowalne (brak serii not) | zostaje jako czynnik 13 (rewizje), **skreślić** blokadę shortu przy ≥3 Buy (nigdy nie zaszła — elita nie pokrywa shortów) i „−1 stopień” (martwa) |
| R10 | **„Przy porównywalnych argumentach preferuj mniejszą wagę w indeksie”** | B4, od startu | koncentracja/próg pobicia NDX | — | W4 MRVL>NVDA, W5 TER>MRVL i AMD>NVDA, W6 LITE/TER>LRCX/MRVL, W7 CSCO/LITE/MRVL/TMUS>AMD/MSFT/NVDA, W8 ADP>ADI/AAPL/AMGN/FTNT, FER>PLTR | 8 rozstrzygniętych decyzji granicznych: wybrany gorszy od alternatywy śr. o **−1,31/nogę** (TER>MRVL W6 −11,4; AMD>PANW W6 −7,9; TMUS>NFLX W7 −6,8; CSCO>FTNT +3,9; CSCO>AMD +3,8; TER>MRVL W5 +3,8; AMD>NVDA +2,1; AMAT>LRCX +2,1) → szum | tercyl kapitalizacji (statyczne proxy z 16.10 — **obciążone look-ahead**): duże **+0,37 p.p./tydz. (t 4,86)**, średnie +0,06, małe −0,02 → kierunek **przeciw** regule, ale proxy niewiarygodne | 0 — zostaje wyłącznie jako tie-break (nie jako preferencja); zdjąć uzasadnienie „pełny efekt relatywny” |
| R11 | **Sygnał wyjścia z bloku pamięci** (pierwsza obniżka DRAM/NAND lub pierwszy miss) = CLOSE news | od startu | — | — | sprawdzany co tydzień, nigdy nie wystąpił | n = 0 | — | zostaje (twardy, prerejestrowany) |
| R12 | **Moduł taktyczny**: 1 nowa/dzień, 2 otwarte, SELL wymaga Rasgona/Curtisa, poszerzenie na S&P 500 (29.09), blokada EVENT (12.10), wykonalność decyduje bot (14.10) | 29.09 / 12.10 / 14.10 | GNRC 17.09 odrzucony; VICR/ACN blokowały sloty; UNH/GS/BLK odrzucone z powodu kursu | 1–3 | AKAM −3,26, VICR/ACN papier, APOG −4,19, PENG +4,48, ERIC +3,99 → tactical_pp skumulowane **+1,02** | 4 wykonane pozycje, 2/4 | — | zostaje; „odczekaj sesję” (K26) nie wpisywać |
| R13 | **Histereza wpisów REDUCE reżimowych; Puls nigdy nie przywraca AKTUALNA** | od startu | — | — | nigdy | n = 0 | — | zostaje |
| R14 | **Wariant „bez nóg EVENT” i benchmark „sort po samym momentum” na papierze; „żadnego wniosku przed 20 oknami”** | 12.10 | PROPOZYCJA 3.1 | — | W8 (benchmark retro W7: −13,64 vs model −21,15) | 1/20 | `bt_momentum.md` (inny agent) | **zostaje — to jedyny element pętli uczenia z prerejestrowanym n** |
| R15 | **B1 pkt (5) reguła D2: Perf.W ≤ −8% jako sito** (TV) | 12.10 | — | — | W8 (nie opisana w decyzjach) | nierozstrzygnięte | przekrojowo: top-kwintyl po tygodniu < −4 p.p. → +1,53 (t 1,26), czyli sito wycina kandydatów o lepszym oczekiwaniu | **nie awansować** (to K10 pod inną nazwą) |

### 1C. Reguły bota, które współdecydują o wyniku (poza zakresem rutyn, ale wymieniane w raportach)

| # | Reguła | Skutek | Uwaga |
|---|---|---|---|
| B1 | Stop 10% od poziomu brokera, **ponowne otwarcie w kolejnym biegu bez wpisu exclude** | W7: LITE, MU, MRVL, PANW zamknięte przy dołku i 3 otwarte niżej — główny składnik −23,7% kapitału (raport W8). Symulacja stopu −10% od D0 (close) **bez** ponownego otwarcia: W1–W7 suma −3,82 → **+1,10** (W7 −22,36 → −17,34; W6 −0,10) | konflikt z R1: bramka Pulsu liczy od `fills`, a stop kasuje `fills` → Puls liczy od D0 (LITE 14.10) albo od ceny ponownego otwarcia (MU 935,73) — protokół i bot mierzą inne rzeczy. Szczegóły: `wykonanie-bota.md` (inny agent) |
| B2 | ALLOC_PCT 0,12 → 0,24 (5.10) po W4–W5 | podwojenie po dwóch dobrych okresach (n = 2, jeden 11-sesyjny) — ta sama pętla „reguła po n = 1”, tylko w kodzie | PROPOZYCJA 3.1 T7 |

---

## 2. Deklaracje D1–D3 — bilans i to, co z nich zrobiono

Źródło: raporty W2–W8 (sekcje DEKLARACJE); `audyt_regul_wyniki.json["deklaracje"]`.

| Tydzień | D1 | D2 | D3 | Konsekwencja regułowa |
|---|---|---|---|---|
| W1 | NIE (MU −1,31, D+2) | NIE (software short +3,95 przeciw) | przeniesiona | K6/K7 (rozproszenie shortów, czynnik M&A) |
| W2 | TAK | TAK | TAK | — |
| W3 | NIE (STX) | NIE (TSLA) | TAK z zastrz. | **K11** TSLA poza koszykiem (do dziś) |
| W4 | TAK (MRVL) | NIE (ADSK +1,20) | NIE (MU nie amortyzował) | **K13** zakaz >20%/10 s; K25 nie wycofana |
| W5 | TAK (MU +0,23) | TAK (NFLX) | TAK (read-across) | K3 nie uruchomiona |
| W6 | TAK (LITE) | NIE (PAYX) | NIE (MRVL) | **K14** sito 12%; **K4** kara 6→3 |
| W7 | NIE (MU −9,09) | NIE (TMUS +12,57) | NIE (WFE) | **K16** MU poza + K10 bez wyjątku; **K15** luka >10% |
| W8 | otwarta | otwarta (test K17) | otwarta | kandydaci (poprawnie: „KANDYDAT, nie reguła”) |

**Bilans: 20 rozstrzygniętych, 9 TAK / 11 NIE (45%) — zgodne z losowością.** Z 11 falsyfikacji **6 wyprodukowało regułę** (K11, K13, K14, K4, K15, K16), **każda po n = 1**. Z 9 potwierdzeń żadne nie zbudowało reguły „pozytywnej” (poza utrzymaniem kary 8) — asymetria: porażki tworzą zakazy, sukcesy nic. Deklaracje testują pojedyncze nogi w 5 sesjach (σ nogi 5–10 p.p.), więc moc testu ≈ 0; mimo to w W4–W7 falsyfikacja była z góry związana z konsekwencją regułową („prerejestrowane”), co nadaje losowemu wynikowi moc prawodawczą. Jedyny poprawny wzorzec: W8 (konsekwencja = „KANDYDAT (n = 1), nie reguła”).

---

## 3. Ocena procesu uczenia

**Liczby.** 36 reguł/filtrów (27 koszykowych z raportów + 15 w rutynach, część się pokrywa; 42 wierszy w tabelach z dubletami). **17 powstało po n = 1** (K2, K4, K6, K7, K8, K9, K10, K11, K12, K13, K14, K15, K16, K18, K19, K20, K25; plus K17 po n = 2 i K26 po n = 2). **Retest: 0** — żadna reguła nie została sprawdzona na danych spoza tygodnia, w którym powstała; „retest po 12 tygodniach” zapisano raz (K15, W8). **Reguły, które raporty nazywają „prerejestrowanymi”**, to w 6 przypadkach konsekwencje deklaracji o n = 1. Reguły są zapisane **tylko w raportach HTML** — `tygodniowa.md` nie zawiera K4–K17 (grep: brak „odzyskanej siły”, „DOJ”, „TSLA”, „>12%”, „luka”), KROK 0 nie każe czytać poprzedniego raportu, więc każdy bieg musi je odtwarzać z pamięci poprzedniego raportu (W8: „reguła W4/W5” cytowana z drugiej ręki).

**Sprzeczności (co najmniej 6 par):**

1. **K8 (nie kupuj po skoku) ↔ K10 (wraca po odzyskaniu siły relatywnej)** — ten sam sygnał (świeża siła kursu) raz dyskwalifikuje (SNDK W3 po +12%), raz kwalifikuje (LITE W6 kupiona na ATH po +19% w miesiąc). Dane: siła kontynuuje (+1,1, t 2,2–2,8) — K8 ma znak przeciwny, K10 brak sygnału.
2. **K10 (przegrana longa = kontynuacja, poza) ↔ K13 (spadek kandydata short = odwrócenie, nie shortuj)** — dla tego samego zdarzenia (spółka spadła) jedna reguła zakłada kontynuację, druga odbicie. Dane wspierają tylko odbicie (K13) i tylko dla ekstremów (≤ −20%).
3. **K10 ↔ wycena/rewizje (Model 3.0)** — W7 rutyna jawnie nadpisała K10 dla MU „bo wycena i elita”, po czym W8 zaostrzyła K10 „bez wyjątku dla wyceny”, a jednocześnie zdjęła z TOP5 SNDK (78,4 — najwyższy wynik modelu w historii) — model i reguła dają przeciwne odpowiedzi co tydzień; rutyna sama nazywa to „nadpisaniem wyniku modelu”.
4. **K15 (nie shortuj po luce >10%: „poczekaj na cięcia prognoz”) ↔ uzasadnienie wejścia TMUS W7 („konsensus nie zdążył ciąć prognoz = czynnik nr 1 przed nami”)** — ten sam fakt jest argumentem ZA przed stratą i regułą PRZECIW po stracie.
5. **K4 (kara event 6→3 po jednym evencie) ↔ K3 (kara 15 zamiast 8, gdyby D1-W5 padło) ↔ K2** — trzy kalibracje tej samej kary w 3 tygodnie na n = 1 każda; w W7 kara LITE = 0 przez „premię zbieżności”, mimo że tygodniowa.md zakazuje netowania („kara PO wyliczeniu bazy”).
6. **R2 blokada sektorowa (ruch sektora ≠ sygnał o spółce, nie tnij) ↔ K19/W8 „koszyk = jeden zakład sektorowy” (ruch sektora JEST ryzykiem koszyka)** — w W7 blokada zatrzymała cięcia dokładnie wtedy, gdy czynnik sektorowy był całym ryzykiem.
7. **R10 (mniejsza waga) ↔ K12/K11 (NVDA/TSLA poza przez zdarzenia)** — tie-break „mniejsza waga” służył w W4/W5 jako drugie uzasadnienie wykluczeń imiennych, więc nigdy nie działał samodzielnie; dodatkowo dane (proxy) idą w przeciwną stronę.
8. **K9/K23 (płatnicy capexu poza) ↔ W8 (GOOGL, MSFT w koszyku jako „bilans i FCF”)** — odwrócenie po jednym tygodniu (W7), bez uchylenia K9.

**Mechanizm.** Pętla wygląda tak: strata → nazwanie przyczyny z nagłówków → reguła imienna lub progowa → zapis w raporcie → kolejny tydzień stosuje ją jako „prerejestrowaną” → falsyfikacja deklaracji zaostrza ją lub dodaje następną. Reguły nie mają: definicji wejścia w polu danych (co to „odzyskana siła” — raz „tydzień”, raz „jedna sesja”, raz „W −20,5%”), daty wygaśnięcia, licznika n_za/n_przeciw ani właściciela. Raporty za każdym razem zastrzegają „5-sesyjne zwroty są losowe”, a następnie z pięciu sesji wyprowadzają regułę. PROPOZYCJA 3.1 (12.10) opisała to poprawnie (T6) i zaproponowała rejestr — W8 go nie wdrożył, dodał za to K15, K16, K17.

**Co robi dobrze:** nadpisania w W8 są oznaczone („°”, „*”) i rozliczane na papierze; D2-W8 to pierwszy test kosztu filtra; benchmark momentum i wariant bez EVENT mają prerejestrowane n = 20; walidator `waliduj_signals.py` chroni plik; reżim i sygnał wyjścia z pamięci nigdy nie zostały ruszone.

---

## 4. Rejestr reguł — proponowany format (`rutyny/reguly.md`)

Jedna tabela, czytana przez KROK 0 obu rutyn; raport cytuje wyłącznie identyfikatory z sekcji OBOWIĄZUJĄCE. Pola:

```
| ID | Status | Treść operacyjna (pole danych, próg, kierunek) | Zakres (long/short/puls/sobota) | Data wejścia | Wyzwalacz (n obserwacji) | Test przekrojowy (n, śr. p.p., t, data) | n_za / n_przeciw od wejścia (nogi) | Koszt skumulowany p.p. (wykluczone − zamienniki) | Retest (data, co zdecyduje) | Wygasa |
```

Statusy: **OBOWIĄZUJĄCA** (tylko po teście przekrojowym: ≥30 zdarzeń, |t_klastrowane| ≥ 2, ten sam znak w ≥4 z 5 przesunięć okna, znak zgodny z intencją), **KANDYDAT** (z deklaracji/lekcji; liczona na papierze, nie zmienia koszyka), **WYJĄTEK IMIENNY** (ticker, powód, wygasa ≤ 4 tyg., bez przedłużenia bez nowego faktu), **UCHYLONA** (data, powód, link do testu), **KONSTRUKCYJNA** (dywersyfikacja/ryzyko ogonowe — nie podlega testowi skuteczności, podlega testowi kosztu). Zasady: jedna nowa pozycja na tydzień; falsyfikacja deklaracji tworzy wyłącznie KANDYDATA; nadpisanie wyniku modelu = wpis NADPISANIE z rozliczeniem po 5 sesjach (jak „°” w W8); każda reguła ma kolumnę „koszt” liczoną co sobotę (zwrot wykluczonych nóg − zwrot zamienników, w p.p. spreadu). Raport sobotni: sekcja „REGUŁY — kontrola” = rejestr × ticker × PASS/FAIL/NADPISANA.

---

## 5. Minimalny zestaw, który zostaje — i co do kosza

### Zostaje (10)

| ID | Reguła | Dlaczego |
|---|---|---|
| R5 | Reżim P0/P1/P2, histereza, eskalacja tylko o sygnały systemowe, poziom surowszy z 2 źródeł | prerejestrowana, nigdy nie strojona; jedyna warstwa ryzyka portfela poza kill switchem |
| R11 | Sygnał wyjścia z bloku pamięci (DRAM/NAND, pierwszy miss) = CLOSE news | twardy, falsyfikowalny, nietknięty |
| R3 | CLOSE/REDUCE o podstawie news/rekom/short — działają od razu | ryzyko ogonowe; 3 użycia, +0,69 na papierze |
| R1 | Bramka 4%/8% od `fills` + druga sesja + bezwzględny próg — **jako kontrola wariancji** | symulacja +2,78 (W7), przekrój 0,08 p.p. (t 0,03): nie szkodzi, ścina ogon; opis w rutynie zmienić („nie podnosi oczekiwanego wyniku”) |
| R2 | Blokada sektorowa — tylko do czasu 5 rozbieżnych werdyktów TV (jak zapisano) | n = 2 o przeciwnych znakach; zostaje przez prerejestrację, nie przez skuteczność |
| K13 | **Zakaz short po spadku ≤ −20% w 10 sesjach (jedna reguła, jeden próg)**; bez wyjątku „twardy negatyw” | jedyna z poparciem: in-sample INTU 3/3 (−20,8 na nodze), przekrój −1,64 p.p. (n 213, t −2,42); wariant 12% i „luka >10%” scalone/uchylone |
| K18 | Limit 2 nazwy na blok (zdefiniować blok betą do SOX−NDX, nie nazwą) | konstrukcyjna, bezkosztowa (zamienniki +1,49/nogę) |
| R8 | Veto −1 kwintyl (krypto-beta, governance, koncentracja klienta) | ryzyko ogonowe: MSTR 12–17 p.p./tydz.; znak nierozstrzygalny (MSTR P, PDD Z) |
| R4 | 2 wpisy/dzień, REDUCE→CLOSE jednokierunkowo, 1 taktyczna/dzień, 2 otwarte | higiena operacyjna |
| R14 | Benchmark momentum + wariant bez EVENT na papierze, n = 20 przed wnioskiem; walidator; nadpisania „°” rozliczane | jedyny działający element pętli uczenia |

Dodatkowo: **p (R6)** zostaje jako liczba, ale z opisem „ranga, nie prawdopodobieństwo”, a kalibracja p vs trafienia trafia do stałej tabeli raportu (obecnie odwrotna: 37,5% vs 60%).

### Do kosza / archiwum (z uzasadnieniem)

| ID | Reguła | Decyzja | Uzasadnienie liczbowe |
|---|---|---|---|
| **K10 + K16 + K17 + R15** | „Przegrana bez odzyskanej siły = poza koszykiem” (wszystkie warianty, w tym filtr kandydatów W8 i sito Perf.W ≤ −8%) | **UCHYLIĆ od W9** (po rozliczeniu D2-W8 na papierze) | brak sygnału przekrojowo (+0,66 vs +0,32 vs +0,59, t < 0,5; prev < −4: +1,53); zamienniki gorsze o 0,84/nogę; wymusza 5–9 wymian/tydz. (koszt wykonania W5: −10,61 p.p. różnicy serii); źródło sprzeczności 1–3 |
| **K8, K21** | „Nie kupuj po skoku / momentum bez rewizji = pułapka / nie shortuj pędu” | UCHYLIĆ | znak przeciwny do danych: +0,79…+1,13 (t 0,6–2,8); in-sample 4/7 wykluczonych wygrałoby; momentum jest już czynnikiem 7% |
| **K15** | Luka 1-dniowa >10% → nie shortuj | UCHYLIĆ (scalone w K13) | przekrój −0,09 / −1,01, t ≈ 0; n = 1 (TMUS) |
| **K14** | Sito >12% z wymogiem „twardego negatywu” | SCALIĆ w K13 (próg 20%) | 12% słabsze (t −1,6…−1,8), „twardy negatyw” nietestowalny; W8 wyciął 14 kandydatów na jednym tygodniu |
| **K4, K3** | Kara event 6→3 / 15 zamiast 8 | UCHYLIĆ; wrócić do jednej skali 0–10 bez netowania premią | n = 1 każda; LITE W7 kara 0 przez „premię” — złamanie własnej zasady „kara PO bazie” |
| **K12** | NVDA poza do zamknięcia DOJ | → WYJĄTEK IMIENNY, wygasa W9 bez nowego faktu | nic nie kosztowała (−0,67 na nodze; zamienniki +1,99), ale otwarta bezterminowo i bez związku mechanizmu z horyzontem |
| **K11** | TSLA poza po 3 przegranych | → WYJĄTEK IMIENNY, wygasa W9 | +2,16 na nodze (2/4 wygrałby); warunek powrotu niefalsyfikowalny (elita nie pokrywa TSLA) |
| **K6** | Nie shortuj celu wykupu | → KONSTRUKCYJNA z limitem: tylko przy ogłoszonej cenie/oficjalnym procesie, wygasa po 2 tyg. bez aktualizacji | WDAY +15,1 jako short przez 6 okien, ADBE W2 +8,96 — koszt ≈ 3–5 p.p. spreadu; ryzyko ogonowe realne, ale nie przez 7 tygodni |
| **K9/K23** | Płatnicy capexu poza longiem | ARCHIWUM (etykieta pozostaje czynnikiem 5%) | MSFT +6,83 kosztu; W8 i tak odwrócone bez uchylenia |
| **K7** | Shorty defensywne jako „jedyna strona z alfą” | ARCHIWUM | przekrój: defensywy −0,05 vs tech +0,21 dla shorta (t < 1); W7 0/4 = −46,9 |
| **K25, K24, K20, K26, K19** | wagi czynnika stóp/cyklu/koncentracji po jednym komunikacie; „nowa podaż konkurenta”; „odczekaj sesję”; „rozproszenie po gardłach” | ARCHIWUM (checklisty pre-mortem, nie reguły) | n = 1–2; K25 sfalsyfikowana własną D3-W4; K19 nie zadziałała w W7 (5 gardeł = 1 czynnik) |
| **R9 (części)** | blokada shortu przy ≥3 Buy elity; „−1 stopień bez weryfikacji” | SKREŚLIĆ martwe fragmenty | nigdy nie zaszły / nigdy nie zmieniły decyzji |
| **R10** | „mniejsza waga” jako preferencja | ZDEGRADOWAĆ do czystego tie-breaka bez uzasadnienia skuteczności | 8 decyzji: −1,31/nogę; proxy kapitalizacji idzie w drugą stronę (+0,37 dla dużych, t 4,9 — proxy obciążone) |
| **K22** | „nie shortujemy, czego nie rozumiemy” | ARCHIWUM | 2/6, śr. −0,5 — szum |

### Konsekwencja dla rutyn (treść, nie liczby z rachunku)

- `tygodniowa.md` KROK 0: „Reguły koszykowe = wyłącznie sekcja OBOWIĄZUJĄCE w `rutyny/reguly.md`; raport nie wprowadza reguł — falsyfikacja D1–D3 tworzy KANDYDATA. Nadpisanie wyniku modelu dozwolone 1×/tydz., oznaczone i rozliczane.”
- `tygodniowa.md` B4: usunąć wszystkie odwołania do „odzyskanej siły relatywnej” i „Perf.W ≤ −8% jako sito”; zostawić K13 (20%/10 sesji) jako jedyne sito short; limit 2/blok z definicją bloku przez β(SOX−NDX).
- `dzienna.md` KROK 2: zdanie „bramka chroni wynik” → „bramka ogranicza wariancję; oczekiwany wpływ ≈ 0 (test 5 lat)”; zapisać, że przy skasowaniu `fills` przez stop bota wyzwalacz liczy się od D0 i to ma być oznaczone jako awaria wykonania, nie decyzja Pulsu.
- Kalibracja p i koszt reguł — stałe tabele raportu (R14).

---

## 6. Czego nie da się stwierdzić (uczciwie)

- **Nic z 7 tygodni nie jest istotne**: σ spreadu tygodniowego ≈ 10 p.p. (W1–W7), więc nawet reguła o prawdziwym efekcie 1 p.p./tydz. potrzebuje ~400 tygodni, by dać t = 2. Wszystkie werdykty „P/Z” in-sample to opis, nie dowód; dowodem jest wyłącznie kolumna „test przekrojowy”, a i on jest in-sample na 5 latach jednej hossy AI (2023–2026 dominuje).
- **Test przekrojowy używa top/dolnego kwintyla momentum 6M jako proxy kandydatów** Modelu 3.0 — faktyczne koszyki są jakościowe (rewizje, elita), więc proxy jest przybliżeniem; wyniki dla całego uniwersum podaję obok.
- **Kara event i kryterium remisu** są nietestowalne bez kalendarza raportów w danych; 9 przypadków in-sample pokazuje asymetrię long/short (longi z raportem przegrywały, shorty wygrywały), ale to 9 obserwacji.
- **Bramka od D0 ≠ bramka od `fills`**: symulacja używa D0 jako ceny wejścia (rachunek wchodzi 1–3 sesje później, często wyżej/niżej o kilka %), nie modeluje blokady sektorowej ani minimalnego lotu (REDUCE niewykonalny na 0,1 akcji). Realny protokół wykonał 1 reakcję na 8 wpisów.
- **Proxy kapitalizacji** jest statyczne (16.10.2026) — wynik „duże spółki +0,37 p.p./tydz.” to w dużej mierze survivorship; nie wyciągam z niego reguły, tylko flagę, że R10 nie ma oparcia.
- **W8 nierozstrzygnięty**: filtr siły relatywnej (6 kandydatów), nadpisania TTWO/MRNA, K15 — dane kończą się 16.10; D2-W8 rozliczy to 24.10. To pierwszy test w historii systemu zaprojektowany przed wynikiem — jego wynik należy wpisać do rejestru niezależnie od znaku i **nie** zmieniać na jego podstawie nic poza statusem K17 (n = 1).
- Dywidendy pominięte w zwrotach (≤0,3 p.p. na nodze w 4 przypadkach); kursy Yahoo bez korekty — spójne z `closes_5y.csv`.

## 7. Źródła i ścieżki

- Skrypt: `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/audyt_regul.py` (uruchomienie: `python3 -I audyt_regul.py`, ~40 s; pandas 3.0.6).
- Wyniki: `audyt_regul_wyniki.json` (klucze: `spread_kontrola`, `kalibracja_p*`, `wykluczenia`, `reguly_agregat`, `deklaracje*`, `testy_przekrojowe`, `tie_break_waga_proxy`, `symulacja_bramki*`, `bramka_przekroj`, `shorty_defensywne*`, `W8_nierozstrzygniety`), `audyt_regul_wykluczenia.csv`, `audyt_regul_nogi.csv`, `audyt_regul_stdout.txt`.
- Repo: `rutyny/tygodniowa.md` (KROK 0, B1(5), B3, B4, KROK A), `rutyny/dzienna.md` (KROK 2: trzy warunki, blokada sektorowa, limity; KROK 1c), `rutyny/tradingview.md` §5.3, §6.3, §9–10, `INSTRUKCJA.md §8` (decyzja o koniunkcji progów, 4 reakcje = −17,43 USD), `rutyny/README.md` (daty 29.09, 12.10, 14.10), `rutyny/PROPOZYCJA-2026-10-12-model-3.1.md` (T6, T7; propozycja rejestru — zgodna z §4 tej notatki, ale jej „LUKA-SHORT ≤ −8%/3 sesje” **nie** potwierdza się w moim teście: t ≈ 0; potwierdza się tylko próg 10-sesyjny ≤ −20%), raporty W1–W8 i pulsy 15–29.09 (daty wprowadzenia bramki i blokady sektorowej: pierwsze użycie 19.09, formalizacja 29.09).
- Analizy równoległe (inni agenci, nie powtarzam): `dekompozycja-wynikow.md` (czynnik SOX−NDX), `wykonanie-bota.md` (stop + reopen), `bt_momentum.md`, `bt_odwrocenie.md`, `bt_neutralnosc.md`, `bt_rezim-i-zaklad-czynnikowy.md`.
