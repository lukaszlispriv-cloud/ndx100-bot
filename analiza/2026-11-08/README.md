# Analiza 08.11.2026 — zatłoczenie momentum i momentum rezydualne (KANDYDACI, na papierze)

Kontekst: po tygodniu 2026-W10 (spread −13,6 pp, wyprzedaż półprzewodników/AI, wyłącznik P2)
właściciel zapytał, czy „boty grające podobnie” tłumaczą takie obsuwy i czy da się to
wykorzystać. Test dwóch pomysłów z rozmowy na 5 latach zamknięć (harness jak w
`analiza/2026-10-18/bt_momentum.py`, uniwersum = dzisiejsze `epics`, survivorship bias).

Pliki: `zatloczenie_momentum.py` (czysty Python, bez numpy; wejście: closes_5y.csv z
`analiza/2026-10-18/pobierz_closes_5y.py`), `zatloczenie-momentum.md` (wynik skryptu).
Bez liczb z rachunku. Nic nie zmienia ranking.py, signals.json ani bota.

## Wnioski (234 okna tygodniowe, 2022-05 … 2026-11)

1. **T1 — zatłoczenie momentum (korelacja parowa 20-sesyjna TOP10): FALSYFIKACJA jako wyłącznik.**
   Tygodnie o wysokiej korelacji liderów momentum NIE były gorsze: tercyl wysoki +2,10 pp/tydz.
   vs niski +1,22 (różnica +0,88, Welch t 0,71); OLS t 0,53; znak różnicy zmienia się
   z roku na rok (2022 −3,8, 2023 +1,4, 2024 −2,0, 2025 +1,8, 2026 +5,0). Z 10 najgorszych
   tygodni tylko 4 miały proxy w górnym kwintylu; najgorszy (27.02.2026, −23,7) i W10
   (30.10.2026, −22,1) miały korelację przeciętną lub niską. Proxy z cen nie zapowiada załamań.
   Kryteria awansu (|t| ≥ 2, ten sam znak w 4 z 5 lat) — nie spełnione.
2. **T2 — momentum rezydualne (reszty wobec ^NDX i ^SOX, suma/σ): FALSYFIKACJA.**
   Średnia −0,28 pp/tydz. vs +1,03 surowe (różnica −1,31, t par −2,10), hit 48 %, skośność −1,08,
   najgorszy tydzień −33,4 pp (W10 — gorzej niż surowe −22,1), obrót 8,8 nóg/tydz. (4× większy),
   netto −0,69 pp/tydz. Wariancja niższa (0,53× surowego), ale za cenę ujemnej średniej
   i grubszego lewego ogona. Składy prawie rozłączne z surowym (0,5/10 wspólnych nóg).
   Na tym uniwersum i horyzoncie efekt z literatury (Blitz–Huij–Martens 2011) nie występuje.
3. **T3 — reżim „po korekcie” (dd > 10 % i VIX > 25 na D0): n = 5, bez wniosku.**
   Pięć okien, wszystkie dodatnie dla surowego momentum (śr. +4,4 pp) — kierunek odwrotny do
   intuicji „momentum crash”, ale 5 obserwacji to nie dowód. Zgodne z wynikiem z 18.10
   (bramka P1 kosztowała). Nie uzasadnia zmiany zachowania po powrocie z P2.

**Konsekwencje:** żaden z pomysłów nie trafia do `rutyny/reguly.md` nawet jako KANDYDAT
z rekomendacją; zostają tu jako wynik ujemny (żeby nie wracać do nich po kolejnym złym
tygodniu). Teza o zatłoczeniu może być prawdziwa, ale nie da się jej zoperacjonalizować
z cen — co najwyżej mierzyłaby ją korelacja pozycji funduszy (13F), do których nie mamy
dostępu. Niezmienione: koszyk E, sizing 0,08, stopy 15/10, wyłącznik P2 z histerezą.
Nieprzetestowany pomysł nr 4 z rozmowy (przesunięcie biegu rotacji z 13:45 na późniejszą
godzinę UTC) wymaga porównania `fills` z kursami zamknięcia na kilku tygodniach, nie backtestu.

## Dodatek — pomysł nr 4: godzina wejścia (bieg 13:45 UTC) — `godzina_wejscia.py`, `godzina-wejscia.md`

126 wpisów `fills` z historii gita (27.08–02.11.2026) porównanych z zamknięciem dnia wejścia
i z poprzednim zamknięciem. Koszt wejścia vs zamknięcie dnia: śr. +0,13 % na nogę (mediana
+0,08 %, t 1,16; bez odstającego FER 19.10); poniedziałki rotacji +0,27 % (t 1,34), BUY ≈ 0,
SELL +0,25 % (t 1,8). W przeliczeniu na koszyk ≈ 0,1 % kapitału na rotację, czyli rząd kosztów
transakcyjnych (0,27 pp/tydz. w analizie 18.10), a nie luki wykonania z W10 (≈ 2 pp kapitału,
która wynikła ze stopów i wyłącznika P2). **Wniosek: brak podstaw do przesuwania godziny
biegu** — efekt nieodróżnialny od zera przy n = 126, a koszt zmiany (bieg bliżej 17:05 skraca
okno między rotacją a wyrównaniem) nie jest zerowy. Jedyna sugestia warta obserwacji: strona
SELL wchodzi średnio 0,5 % poniżej poprzedniego zamknięcia (t 2,25) — shorty otwierane po
porannym spadku; przy 70 obserwacjach to kandydat do ponownego policzenia za ~3 miesiące,
nie do działania.
