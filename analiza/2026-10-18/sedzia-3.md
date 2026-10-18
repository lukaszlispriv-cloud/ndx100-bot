# Sędzia 3 — stosunek zysku do ryzyka i przeżywalność (P(kill), drawdown, koszty, wynik netto przy alfie 0 / +0,5 / +1 p.p.)

Sesja 18.10.2026. Oceniane: projekt A (`projekt-A-mechaniczny.md`), projekt B (`projekt-B-przezywalnosc.md`),
projekt C (`projekt-C-konstrukcja.md`) w świetle werdyktów C1–C9. Bez liczb z rachunku (tylko % i p.p.;
kapitał odniesienia = `START_EQUITY` 1 000 USD z `app.py`).

Własne skrypty tego sędziego (katalog `/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/`):

| plik | co liczy |
|---|---|
| `sedzia3_harness.py` → `sedzia3_harness_out.md`, `sedzia3_harness_wyniki.json` | **jeden wspólny DZIENNY harness** dla polityk wszystkich trzech projektów na tych samych 209 oknach PIT 2022-10…2026-10 (nogi A i E z `projektC_bt_serie.csv`, ceny PIT z `projektA_bt.build(True)`), bootstrap blokowy 4 tyg., 3 000 ścieżek, koszty jak `projektA_bt.simulate` (0,10 % na zmienioną nogę i zmianę skali, 6 %/rok × gross), kill = kapitał < 0,75 × kroczący szczyt i płasko; alfa 0 / +0,5 / +1,0 p.p./tydz. dodana do wyśrodkowanej serii dziennej |
| `sedzia3_dod.py` → `sedzia3_dod_out.md` | alfy równoważne (E o 0,2–0,4 p.p. niżej niż A) i **udział dni z aktywnym progiem miękkim** |
| `sedzia3_pary.py` → `sedzia3_pary_out.md` | próg miękki **wykonalny lotami** dla E: zamknięcie 2 z 5 par (najwyższa σ60 pary) zamiast ×0,5 na locie |

Kontrola spójności harnessu z liczbami projektów: A vt+soft P(kill 52 t., alfa 0) 17,4 % (projektA_boot: 16,6 %); A vt bez progu 52,0 % (53,8 %); E 0,08+soft 0,1 % (projektC: 0,2 %); E 0,08 bez progu 8,0–9,2 % (8,1 %). Różnice ≤ 1,5 p.p. — porównania między projektami są na jednej skali.

---

## 0. Werdykt w sześciu zdaniach

1. **Wszystkie trzy projekty są projektami o przeżywalności, nie o zysku**: przy alfie 0 każda polityka kończy rok z oczekiwanym kapitałem 0,94–0,97 (koszty 3–7 %/rok) i P(strata) 60–74 %; przy +0,5 p.p./tydz. 1,02–1,05; przy +1 p.p. 1,11–1,16 (`sedzia3_harness_out.md`). Różnice między projektami w oczekiwanym wyniku mieszczą się w ±3 p.p. rocznie; różnice w ogonie są 10× większe.
2. **Najlepszy jako szkielet: projekt B** — jedna zmiana klasy (ALLOC 0,24 → 0,06) bez nowych pól `signals.json`, polityka wznowienia po kill w kodzie, stop bez reopen, Puls bez wyzwalaczy cenowych, uczciwe ramowanie P(kill) (horyzont + alfa). Jest jedynym projektem wdrażalnym przed poniedziałkiem 13:45 UTC i jedynym, którego mechanizmy są wykonalne przy locie 0,1 akcji.
3. **B jest niekompletny** (zostawia selekcję Modelu 3.0: IC −0,10, σ 3,3× losowego, b_SOX do 1,7) — stąd jego własne liczby przeżywalności są najgorsze (P(kill 52 t., alfa 0) 25 %, mediana −10 %/rok na mieszance W1–W8). Trzeba do niego przeszczepić mechaniczne źródło koszyka.
4. **Rdzeń sizingu projektu A (vol-target + próg miękki ×0,5) jest zdominowany przez stałe 0,06** na tej samej konstrukcji A: alfa 0 — E[kapitał] 0,936 vs 0,970, P(kill 52) 17,4 vs 13,4 %, μ tyg. −0,135 vs −0,063 %; alfa +0,5 — 1,023 vs 1,046; alfa +1 — 1,123 vs 1,125. Vol-target z sufitem 0,12 i próg miękki dokładają koszt zmian skali, a nie dokładają ochrony (zgodne z C4 §5).
5. **Próg miękki ×0,5 (A i C) nie jest hamulcem ogonowym, lecz stanem domyślnym**: aktywny w 42–62 % dni przy alfie 0 i 16–36 % przy alfie +1 (`sedzia3_dod_out.md`, `sedzia3_pary_out.md`); przy ~1 000 USD ALLOC 0,04/nogę pomija 9 nazw, a 5,6–5,9 % nóg A/E ma kurs > 640 USD — na parach E zamknięcie jednej nogi łamie budżet SOX. Wariant wykonalny — **zamknięcie 2 par o najwyższej σ** — daje ~80 % efektu: P(kill 52, alfa 0) 8,0 % → 0,5 % (×0,5: 0,1 %), p5 0,767 → 0,815 (0,839), maxDD p95 −25 → −21 % (−19 %).
6. **Konstrukcja E (C) jest jedyną, która spełnia warunek właściciela „P(kill) < 10 %/rok przy alfie 0" bez niewykonalnego hamulca** (E 0,08 bez progu: 8,0 %; A 0,06: 13,4 % tu / 27 % na σ Modelu 3.0; A 0,08+soft 6,1 %, ale soft niewykonalny) — za cenę oczekiwaną 3–5 p.p./rok, jeśli pary kosztują 0,3–0,5 p.p./tydz. średniej (C2). Rekomendacja: E do bota (0,08 + veto cenowe), A jako cień, decyzja o średniej po 52 oknach.

---

## 1. Wspólny harness — tabela porównawcza (52 tyg., 3 000 ścieżek, PIT, koszty wliczone)

Serie: A (konstrukcja A z wetami) 209 tyg., średnia in-sample **+0,66** p.p./tydz., σ dz. jednostkowa 3,35 %/d (σ tyg. ≈ 7,5 p.p.); E = B_cap05 średnia **+0,42**, σ 2,05 %/d (≈ 4,6 p.p.). „Alfa" = średnia spreadu po wyśrodkowaniu, **ta sama dla A i E** (patrz §3.5 o alfie równoważnej).

| polityka | alfa | P(kill 12) | P(kill 52) | E[kap.] | med | p5 | p95 | P(strata) | maxDD med / p95 | μ tyg. % | σ tyg. % | Sharpe | dni z progiem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A: A, vt [0,04;0,12] + soft** | 0 | 0,2 % | **17,4 %** | 0,936 | 0,912 | 0,753 | 1,200 | 74 % | −19 / −26 | −0,135 | 2,21 | −0,44 | 62 % |
| | +0,5 | 0,0 % | 8,2 % | 1,023 | 0,982 | 0,789 | 1,371 | 54 % | −17 / −25 | +0,045 | 2,38 | +0,14 | 56 % |
| | +1,0 | 0,0 % | 3,0 % | 1,123 | 1,073 | 0,839 | 1,568 | 35 % | −15 / −24 | +0,236 | 2,53 | +0,67 | — |
| **B (na konstrukcji A): 0,06 + FLAT −12 %** | 0 | 0,0 % | 13,8 % | 0,965 | 0,956 | 0,756 | 1,214 | 62 % | −16 / −26 | −0,074 | 2,08 | −0,26 | FLAT 1,0/rok |
| | +0,5 | 0,0 % | 7,2 % | 1,035 | 1,029 | 0,779 | 1,315 | 44 % | −14 / −25 | +0,070 | 2,13 | +0,24 | 0,8/rok |
| | +1,0 | 0,0 % | 3,5 % | 1,109 | 1,100 | 0,850 | 1,401 | 27 % | −12 / −23 | +0,217 | 2,14 | +0,73 | 0,6/rok |
| A, stałe 0,06 bez schodka | 0 | 0,0 % | 13,4 % | **0,970** | 0,961 | 0,757 | 1,224 | 61 % | −16 / −26 | −0,063 | 2,13 | −0,21 | — |
| | +0,5 | 0,0 % | 6,1 % | **1,046** | 1,039 | 0,799 | 1,318 | 41 % | −14 / −25 | +0,095 | 2,16 | +0,32 | — |
| | +1,0 | 0,0 % | 2,5 % | 1,125 | 1,116 | 0,870 | 1,406 | 23 % | −12 / −23 | +0,246 | 2,16 | +0,82 | — |
| A, stałe 0,08 + soft | 0 | 0,0 % | 6,1 % | 0,969 | 0,938 | 0,787 | 1,243 | 68 % | −16 / −25 | −0,063 | 2,15 | −0,21 | 53–68 % |
| **C: E, stałe 0,08 + soft** | 0 | 0,0 % | **0,1 %** | 0,958 | 0,938 | **0,836** | 1,135 | 72 % | **−13 / −19** | −0,089 | 1,51 | −0,42 | 42 % |
| | +0,5 | 0,0 % | 0,0 % | 1,040 | 1,018 | 0,881 | 1,269 | 44 % | −11 / −16 | +0,082 | 1,63 | +0,36 | 28 % |
| | +1,0 | 0,0 % | 0,0 % | **1,140** | 1,130 | 0,926 | 1,402 | 19 % | −9 / −14 | +0,271 | 1,73 | **+1,13** | 16 % |
| E, stałe 0,08 bez progu | 0 | 0,0 % | 8,0–9,2 % | 0,951 | 0,944 | 0,767 | 1,154 | 68 % | −15 / −25 | −0,104 | 1,82 | −0,41 | — |
| | +0,5 | 0,0 % | 1,3–1,7 % | 1,048 | 1,043 | 0,854 | 1,264 | 37 % | −11 / −21 | +0,100 | 1,82 | +0,40 | — |
| | +1,0 | 0,0 % | 0,3 % | 1,156 | 1,146 | 0,935 | 1,404 | 13 % | −9 / −17 | +0,302 | 1,84 | +1,18 | — |
| E, stałe 0,06 + FLAT −12 % | 0 | 0,0 % | 0,7 % | 0,964 | 0,961 | 0,825 | 1,116 | 68 % | −11 / −21 | −0,076 | 1,37 | −0,40 | 0,5/rok |
| E, stałe 0,06 + soft | 0 | 0,0 % | 0,0 % | 0,968 | 0,953 | 0,866 | 1,110 | 70 % | −11 / −16 | −0,067 | 1,24 | −0,40 | 26 % |
| E, stałe 0,10 + soft | 0 | 0,0 % | 1,4 % | 0,956 | 0,933 | 0,813 | 1,177 | 72 % | −14 / −22 | −0,091 | 1,78 | −0,37 | 54 % |
| A, vt bez progu | 0 | 2,8 % | 52,0 % | 0,921 | 0,865 | 0,741 | 1,258 | 71 % | −25 / −27 | −0,164 | 2,84 | −0,42 | — |

Źródło: `sedzia3_harness_out.md`, `sedzia3_dod_out.md`, `sedzia3_pary_out.md` (dwie wartości = dwa biegi z innym ziarnem).

---

## 2. Co z tego wynika dla stosunku zysku do ryzyka

### 2.1 Sizing jest dźwignią klasy; reszta to drugi rząd — ale koszt sizingu też się liczy
Zgodnie z C4 i wszystkimi trzema projektami: 0,24 → ≤ 0,08 to jedyna zmiana, która zmienia los systemu (P(kill 52, alfa 0) 98 % → 0–17 %). **Nowe:** polityki różnią się kosztem własnym. Przy alfie 0 μ tygodniowa kapitału: A stałe 0,06 −0,063 %, E 0,08 −0,104 % (gross 80 %), A vt+soft **−0,135 %** — vol-target płaci za zmiany skali (|Δa|·10·0,10 % co tydzień + przełączenia progu) i za finansowanie przy suficie 0,12 (mediana ALLOC z reguły na PIT = 0,12, 55–57 % tygodni na suficie — `projektA_bt_out.md`). Przy sygnale rzędu 0,1–0,5 p.p./tydz. netto (C1) 0,07 %/tydz. różnicy kosztu to 3,6 %/rok, czyli tyle, ile cała oczekiwana przewaga.

### 2.2 Vol-target + próg miękki (A) nie dominuje stałego ALLOC — jest zdominowany
Na tej samej konstrukcji A: stałe 0,06 ma wyższy E[kapitał] przy każdej alfie (0,970/1,046/1,125 vs 0,936/1,023/1,123), niższe P(kill 52) (13,4/6,1/2,5 % vs 17,4/8,2/3,0 %), ten sam maxDD p95 (−26 %), lepszy Sharpe (−0,21/+0,32/+0,82 vs −0,44/+0,14/+0,67) i zero nowych pól `signals.json`. To potwierdza C4 §5 (vt z sufitem 0,12 przy równej średniej ekspozycji przegrywa w 52 tyg. przy alfie 0) i obala streszczenie projektu A „vt+soft: 0 %/17 % vs 0,08: 1 %/33 %" — porównanie A było z stałym 0,08 **bez** progu, a właściwe porównanie (stałe 0,06, ta sama średnia ekspozycja) nie zostało w A policzone. Wniosek: pole `sizing`, walidator, `_sanity` i `ranking_hash` w A kupują złożoność, nie ochronę.

### 2.3 Próg miękki ×0,5 jest stanem domyślnym, nie bezpiecznikiem — i jest niewykonalny lotami
Udział dni z aktywnym progiem (DD od szczytu w (−10 %, −5 %)): A vt+soft 62 % (alfa 0) / 56 % (+0,5); E 0,08+soft 42 % / 28 % / 16 % (alfa 0 / +0,5 / +1); E 0,10+soft 53 % (`sedzia3_dod_out.md`, `sedzia3_pary_out.md`). Przy kosztach i alfie ≈ 0 kapitał większość czasu spędza 5–15 % pod szczytem, więc „×0,5" to faktyczny ALLOC 0,04 (E) albo 0,02–0,06 (A vt) przez jedną trzecią do dwóch trzecich roku. Przy kapitale rzędu START_EQUITY: 0,04/nogę → **9 nazw pomijanych, 10 w przestrzale** (`projektC_bt_out.md` §3); 5,9 % nóg E i 5,6 % nóg A ma kurs > 640 USD na D0 (wynik tej notatki); `REDUCE_FALLBACK=close` zamknie wtedy jedną nogę pary i złamie budżet SOX. Projekt B ma rację („połowienie lotu 0,1 jest niewykonalne"), ale jego odpowiedź (FLAT) nie działa statystycznie (§2.4). **Wykonalna odpowiedź** (`sedzia3_pary_out.md`): przy DD < −10 % zamknąć 2 z 5 par o najwyższej σ60 pary (gross ×0,6), wrócić do 5 par przy DD > −5 %:

| E 0,08, alfa 0 | P(kill 52) | E[kap.] | p5 | maxDD p95 | μ tyg. | Sharpe |
|---|---|---|---|---|---|---|
| bez progu | 8,0 % | 0,951 | 0,767 | −25 % | −0,104 | −0,41 |
| ×0,5 na locie (A/C — niewykonalny) | 0,1 % | 0,961 | 0,839 | −19 % | −0,082 | −0,39 |
| **zamknij 2 pary o najwyższej σ** | **0,5 %** | 0,954 | 0,815 | −21 % | −0,098 | −0,45 |

Przy alfie +1: 0,3 / 0,0 / 0,0 %; E[kap.] 1,154 / 1,142 / 1,140. Zamknięcie par daje ~80 % redukcji ogona ×0,5 (w P(kill), p5, maxDD) i jest wykonalne jako zamknięcie całych pozycji; koszt średniej przy alfie 0 to ok. 0,016 %/tydz. wobec ×0,5 (pary o najwyższej σ miały in-sample wyższą średnią — to półprzewodniki). Wybór „najwyższa σ" vs „najmniejszy rozstęp momentum" — do testu przed wdrożeniem.

### 2.4 Schodek FLAT −12 % (B) nic nie daje statystycznie
Na konstrukcji A: 0,06+FLAT vs 0,06 bez schodka — P(kill 52, alfa 0) 13,8 vs 13,4 %, E[kap.] 0,965 vs 0,970, Sharpe −0,26 vs −0,21; przy +1: 3,5 vs 2,5 %, 1,109 vs 1,125. Na E: 0,06+FLAT 0,7 % vs 0,06+soft 0,0 %. Powód (B sam go podaje): szczyt cyklu resetuje się po wznowieniu, a wszechczasowy nie — kolejne −12 % od −12,5 % daje −23,5 %, czyli pod próg kill prawie bez hamulca; ×0,5 (albo zamknięcie par) działa, bo **trzyma** niższą ekspozycję przez całą strefę DD (−10 %…−25 %). FLAT dokłada stan do pilnowania (`wykonanie.plasko`, twardy zapis, cooldown w `version`) i ok. 1 epizod/rok płasko. Odrzucić w tej postaci; zachować z B wyłącznie **logikę wykonalności** (redukcja = zamknięcie całych pozycji) i politykę wznowienia po kill.

### 2.5 E vs A: σ pewna, średnia nie — i to decyduje o Sharpe'ie
Przy **tej samej** alfie E ma Sharpe 1,13–1,18 vs A 0,67–0,82 (+1 p.p.), 0,36–0,40 vs 0,14–0,32 (+0,5). Ale E ma średnią in-sample o 0,24 p.p./tydz. niższą (+0,42 vs +0,66 na tych oknach), a C2 każe planować z kosztem 0,3–0,5 (klastry PIT mediana −0,86). Próg równowagi Sharpe'a: c* = α·(1 − σ_E/σ_A) = 0,39·α → przy α_A = +0,5 koszt par ≥ 0,2 p.p. zeruje przewagę Sharpe'a E; przy α_A = +1,0 próg to 0,39. Alfy równoważne (`sedzia3_dod_out.md`):

| para | E[kap. 52] | P(kill 52) | p5 | maxDD p95 | Sharpe |
|---|---|---|---|---|---|
| A 0,06 (B) przy +0,5 vs **E 0,08+soft przy +0,2** (koszt par 0,3) | 1,046 vs 0,989 | 6,1 vs 0,1 % | 0,799 vs 0,855 | −25 vs −18 % | +0,32 vs −0,10 |
| A 0,06 przy +0,5 vs E przy +0,0 (koszt 0,5) | 1,046 vs 0,959 | 6,1 vs 0,1 % | 0,799 vs 0,838 | −25 vs −19 % | +0,32 vs −0,40 |
| A vt+soft przy +0,3 (C1 środek) vs E przy +0,0 | 0,982 vs 0,959 | 10,7 vs 0,1 % | 0,775 vs 0,838 | −25 vs −19 % | −0,12 vs −0,40 |
| A 0,06 przy +0,0 vs E przy −0,4 | 0,970 vs 0,909 | 13,4 vs 0,9 % | 0,757 vs 0,806 | −26 vs −21 % | −0,21 vs −1,00 |

Odczyt: jeśli koszt par jest taki, jak każe planować C2 (0,3–0,5), **E oddaje 3–6 p.p. rocznie oczekiwanego wyniku i cały Sharpe** w zamian za P(kill) niższe o 6–13 p.p., p5 lepsze o 5–8 p.p. i maxDD p95 o 6–7 p.p. płytsze. Jeśli koszt par ≈ 0 (C2 definicja TV W8: Δ −0,00 ± 0,30), E dominuje na każdej osi. **Dane tego nie rozstrzygają** (CI Δ −0,92…+0,50; t = 2 dla Δ 0,3 po 1 204 tyg.) i nie rozstrzygną w życiu projektu — decyzja jest o preferencji: tail vs średnia.

### 2.6 Dlaczego mimo to E do bota: warunek właściciela i natura dominującego ryzyka
(i) Jedyny twardy warunek właściciela w zadaniu dla B („P(kill) < 10 %/rok przy zerowej alfie") spełnia **tylko E** z wykonalnymi mechanizmami: E 0,08 bez progu 8,0–9,2 %, E 0,08 + zamknięcie par 0,5 %, E 0,06 ~0–1 %; A 0,06 daje 13,4 % na PIT (27 % na σ Modelu 3.0 — `projekt_B_sim_out.md` A), A 0,08+soft 6,1 % tylko z niewykonalnym ×0,5. (ii) Ryzyko, które system faktycznie zrealizował (74 % wariancji spreadu = czynnik SOX; W7 −21 p.p.) E tnie z −5,1 do −1,9 p.p. w tygodniach SOX−NDX < −3 (PIT, `projektC_bt_out.md` §1c) — to jedyne ryzyko o udowodnionym mechanizmie, a jego redukcja jest jedynym wynikiem całej analizy, którego CI nie zawiera zera (σ-ratio 0,67 [0,58; 0,78]). (iii) Z polityką wznowienia po kill (A S5 / B §2.3) kill nie jest ruiną, lecz kosztem (2 rotacje płasko + reset) — to osłabia argument „P(kill)" na rzecz E[kapitał]; ale kill przy A 0,06 trafia po maxDD ≥ 25 %, a przy E maxDD p95 wynosi −19…−21 % — różnica w głębokości DD zostaje. (iv) Cena E (3–6 p.p./rok oczekiwanego) jest mniejsza od niepewności samej alfy (CI netto A −0,4…+1,3 p.p./tydz. = ±25 p.p./rok przy gross 60–80 %) — czyli wybór E vs A nie zmienia znaku oczekiwania, zmienia tylko kształt rozkładu. Przy niedowiedzionej alfie kształt jest tym, co wolno wybierać.

### 2.7 Koszty i wykonalność ALLOC
Finansowanie 6 %/rok × gross jest parametrem, nie taryfą (wszyscy to zaznaczają); przy μ netto ≈ 0 to on decyduje o znaku. Argument za 0,08 (C) przeciw 0,06 (B) przy ~1 000 USD: przy 0,06 pomijane są ASML COST MELI MPWR SNDK (5; przy 0,83 × START_EQUITY 7) i 5 w przestrzale — veto lotu B „wycina sprzęt AI", gdzie C1 lokuje alfę momentum; przy 0,08 + veto cenowe 1 280 USD pomijane 0, w przestrzale ≤ 4 (`projektC_bt_out.md` §2–3, koszt veta Δ +0,03…+0,04, t ≤ 1,5). Dla E 0,08 ma σ tyg. kapitału 1,8 % ≈ A 0,05 — równoważne ryzyko przy wykonalnych lotach. Dla A 0,08 bez progu P(kill 52, alfa 0) ≈ 28–33 % (`projektC_bt_out.md` §4, `projektA_boot_out.md`) — za dużo; A wymaga 0,06 i akceptacji veta lotu. To drugi argument za E jako konstrukcją bota na tej skali rachunku.

### 2.8 Migracja 18–19.10 — trzy projekty mówią to samo
Wszystkie: ALLOC 0,24 → 0,06–0,08, taktyczne off, reset `equity_peak` **oraz** `START_EQUITY ≤ kapitał` (C9 opcja c), W8 bez zmian, cienie od W8. P(kill o 13:45 na księdze W7) 21 % niezależnie od ALLOC; z poduszką ≈ 1,7 % P(kill w 4 tyg.) 68–85 % dla każdej polityki (`projektA_boot_out.md`). Sędzia: restart = przesunięcie progu po stracie (C9 §5), ale sprzężony ze zmianą metody (gross 240 → 60–80 %, selekcja mechaniczna) jest jedynym wariantem, w którym nowe reguły w ogóle zostaną zmierzone; warunek B (linia „obsunięcie od szczytu historycznego" w każdym raporcie) jest obowiązkowy. Wariant A z B (NIEAKTUALNA, start z W9) równie spójny i tańszy o 21 % ryzyka poniedziałkowego — jeśli kod wznowienia nie zdąży, jest bezpieczniejszy.

---

## 3. Oceny (1–10)

| projekt | evidence | implementability | risk_adjusted_return | overfitting_robustness | **total** |
|---|---|---|---|---|---|
| A — proces mechaniczny (A + vt + soft + σ-stop + nakładka) | 7 | 4 | 5 | 6 | **22** |
| B — przeżywalność (0,06 + FLAT + wznowienie + stop 15/10) | 7 | 9 | 6 | 8 | **30** |
| C — konstrukcja E (5 par, budżet SOX, 0,08 + soft) | 8 | 6 | 8 | 6 | **28** |

**A.** Evidence 7: najwięcej liczb (PIT, bootstrap, nakładka, stopy), uczciwe CI — ale kluczowe porównanie sizingu (vt+soft vs stałe o tej samej średniej ekspozycji) nie zostało zrobione, a wynik jest odwrotny do tezy (§2.2); nakładka jawnie niemierzalna (|Δ| ≥ 0,71 po 26 tyg.). Implementability 4: 22 zmiany w 5 dni, nowe pole + walidator + `_sanity`, bot czytający `ranking-<version>.json` z GitHuba w biegu (nowy tryb awarii dla stopów), kill-resume, soft, nakładka, cienie; próg miękki niewykonalny lotami; sufit 0,12 w Renderze jako „zabezpieczenie" oznacza gross 120 % w 55 % tygodni PIT. Risk-adjusted 5: najwyższa oczekiwana średnia konstrukcji, ale polityka sizingu ma najgorsze E[kap.], P(kill) i Sharpe z trzech przy każdej alfie (tabela §1); b_SOX zrealizowane +0,91 zostaje. Robustness 6: skip 5 = szczyt siatki (C1), VOL_TARGET/clip/soft/σ-stop — wiele parametrów prerejestrowanych in-sample; mocny proces (PIT-test reguł, moratorium, cienie).

**B.** Evidence 7: sizing zgodny z C4 i z tym harnessem; FLAT uczciwie opisany jako „ogon kwartału", ale w harnessie nie daje nic (§2.4); stop 15/10 z jednego harnessu (C3, rozkład ogonowy, 5 okien = 68 % kosztu). Implementability 9: zmiana ALLOC to edycja panelu; zero nowych pól; 120–150 linii z testami; każdy mechanizm wykonalny lotami (zamknięcie całych pozycji); jedyny projekt gotowy na 19.10. Risk-adjusted 6: jako zaproponowany (selekcja Modelu 3.0) P(kill 52, alfa 0) 25 %, mediana −10 %/rok, próg opłacalności +0,52 p.p./tydz. — najgorsze liczby z trzech, bo nie rusza σ selekcji (3,3× losowego); na konstrukcji mechanicznej jego sizing jest najlepszy w E[kap.] (§2.2). Robustness 8: cztery liczby (0,06; −12 %; 15/10; 2 rotacje), wszystkie oznaczone jako decyzje; nic do przeuczenia.

**C.** Evidence 8: σ-ratio 0,67 z CI poza 1 w każdej definicji i w PIT — najtwardszy wynik całego panelu; 209 okien; wrażliwość na taksonomię policzona; vol-target dla E słusznie odrzucony (0,12 w 98 % tygodni). Zastrzeżenia: bootstrap kapitału sprawdza kill na tygodniach, nie dniach (`projektC_bt.boot_capital`) — tu potwierdzony dziennie; koszt progu miękkiego „bez osobnej liczby"; „P(kill 52) 0,2 %" opiera się na mechanizmie niewykonalnym lotami (§2.3) — bez niego 8–9 %. Implementability 6: brak nowych pól top-level, `app.py` tylko soft; ale `ranking.py` z 56 podzbiorami + testy, zależność od cotygodniowego snapshotu TV (429 → taksonomia sprzed tygodnia), < 5 par po wetach w sezonie wyników → „poprzedni koszyk zostaje" (decyzja bez dowodu), Puls 3×/tydz. (decyzja). Risk-adjusted 8: najlepszy Sharpe przy równej alfie, najpłytsze DD, P(kill) < 10 % bez hamulca; obniżone za nierozstrzygalny koszt średniej 0,3–0,5 p.p. i gross 80 % (koszt 0,115 %/tydz. > B). Robustness 6: definicja grupy = najlepsza z 5 w obu składach (C2 „efekt wyboru definicji"), PAIR_POOL 8 / cap 0,5 z siatki, 2026 in-sample E oddaje 2/3 wyniku A; zamrożenie + cienie łagodzą.

---

## 4. Najlepszy: **B** jako szkielet, z przeszczepem źródła koszyka

Uzasadnienie: B jest jedynym projektem, którego każdy element przeżywa jednocześnie test statystyczny (sizing), test wykonalności (loty, zero pól) i test czasu (wdrażalny przed 13:45 UTC 19.10). Jego błąd (FLAT) jest tani i usuwalny; jego luka (selekcja) jest jawnie zadeklarowana jako zakres A/C i daje się domknąć przeszczepem bez zmiany jego własnych decyzji. A ma najgorszy stosunek złożoności do ochrony; C ma najlepszą konstrukcję, ale jej liczby przeżywalności stoją na niewykonalnym ×0,5 i brak w nim polityki wznowienia po kill.

## 5. Przeszczepy do B (z A i C)

1. **Z A: `scripts/ranking.py` jako jedyne źródło koszyka** (uniwersum = epics, mom6_rel skip 5, veta S1/K13/EVENT, wyjątki z `reguly.md` z datą wygaśnięcia, `data/ranking-<version>.json` + hash w commicie; Model 3.0, elita, panel fundamentów, p, D1–D3 — skreślone). Powód: IC Wyniku −0,10 (CI −0,57…+0,37), 10/16 stron nadpisanych, σ Modelu 3.0 3,3× losowego — B na tej selekcji ma P(kill 52) 25 %, na mechanicznej 0,5–13 % (§1). Nakładkę A (N1–N6) **nie** przeszczepiać na start (niemierzalna; na parach wymaga wymiany całej pary) — ewentualnie po 26 oknach cieni.
2. **Z C: konstrukcja E (5 par, budżet |b_SOX| ≤ 0,5 z puli 8) jako koszyk bota, stałe ALLOC 0,08 + veto cenowe 1 280 USD**, A jako główny cień z testem F (moc 47 % po 26, 74 % po 52 tyg.). Powody: §2.5–2.7. Kryteria C §6.4 bez zmian (σ-ratio > 1,03 po 26 → powrót do A przy 0,06).
3. **Z C (zmodyfikowany): próg miękki jako zamknięcie 2 par o najwyższej σ60** przy DD < −10 % od kroczącego szczytu, powrót przy DD > −5 % (P(kill 52, alfa 0) 8,0 → 0,5 %, p5 0,767 → 0,815; `sedzia3_pary_out.md`), zamiast ×0,5 na locie (niewykonalne) i zamiast FLAT (bezskuteczne). Stan w `wykonanie.soft` (pole bota), bez pól rutyn. Wymaga: wyboru kryterium par (σ vs rozstęp) testem na PIT przed wdrożeniem i obsługi w `desired_book` („para zamknięta progiem" ≠ brakująca).
4. **Z A: kotwica stopu `fills.cena` przed poziomem brokera** — nie z powodu EV (C3: nieustalone), lecz spójności pomiaru (MU 13.10 zamknięty +4,4 % nad ceną tezy; bramka i stop mierzyły od różnych punktów). B zostawia poziom brokera z argumentu C3 T3, ale ten test dotyczył kotwicy D0, nie `fills` (A §6). Stop bez reopen — wspólne (B §2.4 = A §6).
5. **Z A/C: metryki prerejestrowane w stałej kolejności** (spread od D0 i od fills, σ zreal. vs ex ante, b_SOX zreal., koszt_wykonania_pp, REGUŁY — kontrola z medianą i listą, zdanie o mocy) i koszyki cienie jednym skryptem (`koszyki_cienie.py` → `data/koszyki-cienie.jsonl`): A0/A/E/B/D/ETF/„bez EVENT"/FAKT.
6. **Z A: `scripts/test_regula.py` na uniwersum PIT** (`dane/dropped_closes.csv` + tabele dat) i kryterium awansu z testem w TOP5/TOP10 (C6: znak reguły odwraca się między kwintylem a TOP5).
7. **Z A: reżim tylko P2 = DD ^NDX > 20 % od maks. 252 sesji → NIEAKTUALNA, bez histerezy**; P1 flaga (C8). B zostawia „wyłącznik P2" bez tej redukcji — doprecyzować.
8. **Z A/C: Puls bez basis `rekom`/`short`** (B je zostawia z listy R3): nieweryfikowalne, 1/8 wpisów wykonany; zostaje `news` z dokumentem i wyłącznik płynności (sesja ≤ −5 %, VIX > 40 — decyzja).

## 6. Elementy do odrzucenia (z powodem)

| element | projekt | powód |
|---|---|---|
| Vol-target `clip(0,015/(5·σ60), 0,04, 0,12)` + pole `signals.json["sizing"]` + zmiany walidatora/`_sanity`/`ranking_hash` | A | zdominowany przez stałe 0,06 na tej samej konstrukcji przy każdej alfie (E[kap.] 0,936 vs 0,970 przy 0; P(kill 52) 17,4 vs 13,4 %; Sharpe −0,44 vs −0,21; `sedzia3_harness_out.md`); sufit 0,12 = gross 120 % w 55 % tygodni; dla E reguła martwa (0,12 w 98 % tygodni); koszt zmian skali ~0,02–0,04 %/tydz.; C4 §5 |
| Próg miękki ×0,5 **na locie** | A, C | aktywny 42–62 % dni przy alfie 0 (stan domyślny, nie bezpiecznik); ALLOC 0,04/nogę → 9 nazw pomijanych, 10 w przestrzale przy ~1 000 USD; 5,6–5,9 % nóg > 640 USD → `REDUCE_FALLBACK=close` łamie pary i budżet SOX; zastąpić zamknięciem 2 par (§2.3) |
| Schodek FLAT −12 % od szczytu cyklu z cooldownem | B | brak efektu: P(kill 52, alfa 0) 13,8 vs 13,4 % bez schodka, E[kap.] 0,965 vs 0,970, Sharpe −0,26 vs −0,21; przy +1: 3,5 vs 2,5 %; B sam: 25,5 vs 27,3 %; dodaje stan `wykonanie.plasko`, twardy zapis, 1 epizod/rok płasko |
| Nakładka Modelu 3.0 (≤ 1 wymiana/stronę) od W9 | A | σ Δ 1,80 p.p./tydz. → |Δ| ≥ 0,71 wykrywalne po 26 tyg., +0,3 po 144 tyg.; na parach E wymiana nogi łamie budżet; progi N5 to decyzja; zostawić jako opcję po 26 oknach cieni |
| Bot czytający `data/ranking-<version>.json` z GitHuba w biegu dla progów σ-stopu | A | nowy tryb awarii w `/run` (brak pliku/limit API → fallback 10 %) za EV stopu −0,002 vs −0,04 p.p./tydz. (PIT) — różnica niemierzalna; stały próg per kierunek (B: 15/10) daje to samo bez zależności sieciowej |
| Selekcja Modelu 3.0 bez zmian (zakres B) | B | IC −0,10 (CI ±0,5), σ 3,3× losowego, b_SOX do 1,7, 36 min TV; na niej B ma P(kill 52, alfa 0) 25 % i medianę −10 %/rok — fundament B wymaga koszyka mechanicznego |
| Veto lotu S4 `0,1 × kurs > 1,3 × ALLOC × kapitał` przy ALLOC 0,06 | B | wycina 5–7 nazw sprzętu AI (C1: tam alfa momentum); przy 0,08 + veto cenowe 1 280 USD pomijane 0 (koszt Δ +0,03…+0,04, t ≤ 1,5) — wybrać 0,08 + veto cenowe |
| Kotwica stopu = poziom brokera | B | C3 T3 testował kotwicę D0, nie `fills.cena`; poziom brokera przestawia się przy każdym wyrównaniu (MU 13.10 +4,4 % nad tezą), bramka i stop mierzą od różnych punktów |
| Puls 3×/tydz. (pon./śr./pt.) | C | bez dowodu — decyzja; wyzwalacz newsowy R3 i wyłącznik płynności nie mają innego nośnika; koszt Pulsu kontrolnego to ≤ 8 wywołań TV/10 min (A) — zostawić codziennie, skrócić zakres |
| Basis `rekom`/`short` w Pulsie | B | nieweryfikowalne ze środowiska, brak testu, 1 z 8 wpisów Pulsu wykonany (A §7.1) |
| „P(kill 52) 0,2 %" jako metryka oczekiwana E | C | zależy od ×0,5 na locie; wykonalna wersja: 0,5 % (zamknięcie par) albo 8–9 % (bez progu) — tak raportować |
| Hipoteza stopy depozytu w dniu rotacji — poprawka `sync()` | A, C | wymaga logu `/run` 19.10 i 26.10; nie wdrażać przed potwierdzeniem (wspólne stanowisko — podtrzymane) |

## 7. Zastrzeżenia do metody sędziego

- Harness na zamknięciach dziennych (kill sprawdzany raz dziennie; bot sprawdza mid o 13:45 i 17:05 UTC — P(kill) lekko zaniżone, równo dla wszystkich polityk); wejścia na zamknięciu D0, nie w poniedziałek 13:45 (C3/C7: ±0,1 p.p./tydz.).
- „Ta sama alfa dla A i E" to założenie; §2.5 pokazuje korekty o 0,2–0,4 p.p. — wynik porównania E vs A zależy od nieznanego kosztu par i nie jest rozstrzygalny danymi (C2).
- Koszty parametryczne (6 %/rok × gross, 0,10 % na nogę; bez poślizgu, dywidend shortów, FX); przy μ ≈ 0 każde 2 %/rok przesuwa znak. Zmiana skali kosztowana jako |Δa|·10·0,10 % — obciąża vt i soft, nie stałe ALLOC; bez tego kosztu różnica A vt+soft vs stałe 0,06 maleje o ~0,02–0,04 %/tydz., ale znak się nie zmienia (P(kill) i p5 są bez kosztu zmian skali).
- Bootstrap blokowy 4 tyg. nie modeluje reżimów dłuższych niż miesiąc; C4: klastrowanie zmienności nie podnosi P(kill) (blok 60/GARCH ≈ blok 5).
- PIT koryguje 28 nazw, 6 niedostępnych (C1) — średnie zawyżone, σ-ratio i P(kill) przy alfie 0 praktycznie nie.
- Zamknięcie par: kryterium „najwyższa σ60 pary" wybrane a priori (jedno), bez siatki; pary z `grupy` dopasowane w 209/209 tygodni; FLAT z cooldownem przybliżony (płasko do startu tygodnia k+2).
- Liczby P(kill) przy alfie 0 dla ALLOC 0,06 na konstrukcji A różnią się między harnessami 2× (13,4 % tu na PIT A vs 27 % w `projekt_B_sim` na mieszance W1–W8 o σ Modelu 3.0) — to miara niepewności modelu, nie błąd; dla decyzji liczy się kolejność polityk, która jest w obu ta sama.

## 8. Źródła

Projekty: `projekt-A-mechaniczny.md` (+ `projektA_bt_out.md`, `projektA_boot_out.md`), `projekt-B-przezywalnosc.md` (+ `projekt_B_sim_out.md`), `projekt-C-konstrukcja.md` (+ `projektC_bt_out.md`, `projektC_dod_out.md`). Weryfikacje: `weryfikacja-C1.md`…`weryfikacja-C9.md` (werdykty w zadaniu). Fazy 1–2: `_faza1_wyniki.txt`, `_faza2_wyniki.txt`. Własne: `sedzia3_harness.py/_out.md/_wyniki.json`, `sedzia3_dod.py/_out.md/_wyniki.json`, `sedzia3_pary.py/_out.md/_wyniki.json`. Dane: `dane/closes_5y.csv`, `dane/dropped_closes.csv`, `data/tv-screen-2026-W8.json` (taksonomia przez `projektC_bt.IND`).
