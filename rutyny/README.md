# Rutyny — źródło prawdy dla treści zadań

Dwa zadania w schedulerze Claude, dwa pliki tutaj. **Zawsze zmieniaj najpierw
plik, potem wklejaj do zadania** — wtedy historia gita mówi, co i kiedy się
zmieniło, a nadpisanie zadania przez pomyłkę odtwarza się jednym kopiuj-wklej.

| Plik | Zadanie | Kiedy | Co pisze do `signals.json` | Co produkuje |
|---|---|---|---|---|
| `dzienna.md` | „Puls NDX100" | dni robocze ok. 12:30 UTC | tylko `status`, `exclude` (v2: nowe wpisy wyłącznie basis news), `tactical` (v2: `[]`), `last_daily` | `reports/puls-RRRR-MM-DD.html` |
| `tygodniowa.md` | „Ranking NDX100 — raport tygodniowy" | sobota ok. 07:30 UTC | `version`, `status`, `long`, `short`, `d0`, `generated`, `exclude=[]`, `tactical=[]`, wpis do `history` (obcięte do 26), `epics` tylko dopisanie | `reports/raport-2026-WX.html` |

Żadna z nich nie dotyka `fills`, `equity_peak` ani `wykonanie` — te pisze bot. `wykonanie` mówi, które REDUCE i pozycje taktyczne naprawdę zadziałały na rachunku; rozliczenie tygodniowe liczy wynik tylko z nich.

## Jak w 5 sekund poznać, która rutyna faktycznie się odpaliła

```
grep -o '"version": "[^"]*"' signals.json   # zmieniło się -> tygodniowa
ls reports/ | tail -3                        # puls-... = dzienna, raport-W... = tygodniowa
```

## Dlaczego ten katalog istnieje

Między 12.09 a 19.09.2026 treść zadania sobotniego została przypadkowo
nadpisana treścią dziennego. Skutek: dwie soboty (19.09, 26.09) wykonały puls
dzienny zamiast rotacji, koszyk `2026-W4` pracował 18 dni zamiast 5, pięć
reakcji z `exclude` wisiało zamrożonych, a w `history` brakuje dwóch wpisów.
Nikt tego nie zauważył, bo obie rutyny piszą po polsku, obie zapisują raport
i obie kończą się „AKTUALNA · REŻIM P0". Odtworzono z transkryptu biegu
z 12.09 (prompt rutyny jest pierwszą wiadomością każdego jej biegu).

## Zmiany wprowadzone 29.09.2026

### `tygodniowa.md` — względem wersji odtworzonej z 12.09

1. **KROK 0** — czyta też `fills` i `equity_peak` (tylko do odczytu) oraz
   sekcje KONTROLA BRAMKI z raportów dziennych, żeby wiedzieć, które reakcje
   bot faktycznie wykonał.
2. **ŹRÓDŁO KURSÓW** — nowa spółka z indeksu musi trafić do `epics` PRZED
   uruchomieniem `kursy.py` (skrypt czyta uniwersum z tej mapy). Jawnie
   zapisane, że rezerwy (Stooq, StockAnalysis, CBOE) i konektor FMP bywają
   zablokowane — wtedy odnotować, nie udawać drugiego źródła.
3. **KROK A** — trzy rzeczy:
   - poprawiony błąd zapisu: `[D+n/D0−1]` → `[D+n/D0−1]` (wyciekły
     sekwencje JSON) i usunięte zbłąkane cudzysłowy wokół całego kroku;
   - rozróżnienie **CZĘŚCIOWE** (n < 5) od **PRZETERMINOWANE** (n > 5)
     z polem `"sesje": n` we wpisie do `history` — inaczej rozliczenie W4 za
     trzy tygodnie wyglądałoby jak tygodniowe;
   - **druga seria `spread_fills_pp`** (od cen odniesienia z `fills`) obok
     `spread_pp` — puls dzienny od dawna raportuje obie i zakłada, że sobota
     je zapisuje, a stary prompt zapisywał tylko jedną;
   - przy `reaction_pp` obowiązkowa liczba **wykonanych** reakcji wg bramki
     bota; gdy 0 — napisać wprost, że wynik jest na papierze. W oknie W4
     bramka wykonała 0 z 5 (patrz `reports/audyt-2026-09-28.html`).
4. **B3** — gdy `tipranks.com` jest zablokowany: użyć ostatniego odczytu,
   odnotować brak weryfikacji na żywo, obniżyć wagę o stopień.
5. **B4** — dopisanie nowej spółki do `epics` „PRZED pobraniem kursów".
6. **KROK C** — rozliczenie pokazuje obie serie spreadu i liczbę wykonanych
   reakcji; stopka z kontekstem wielkości pozycji (12% / 10% od 29.09.2026).
7. **KROK D** — zdanie z `INSTRUKCJA.md` §5.6 (**`fills` i `equity_peak`
   nie ruszaj**), którego w odtworzonej wersji brakowało; informacja, że bot
   sam resetuje ceny odniesienia po zmianie `version`; `spread_fills_pp`
   i `sesje` we wpisie do `history`; lista kontrolna przed zapisem.
8. **KROK E** — `spread_fills_pp` i słowo CZĘŚCIOWE/PRZETERMINOWANE.

Nie zmieniono: Model 3.0 (B1/B2), panel fundamentów (B0b), reżim i histereza
(B0), zasady koszyków (B4), `tactical=[]` przy rotacji.

### `dzienna.md` — względem kopii w schedulerze

1. **KROK 0** — opis pola `fills`: dwa nowe pola `wersja` i `cena_brokera`
   (od poprawek z 28.09.2026 cena odniesienia przeżywa wyrównania).
2. **KROK 3, KONTEKST WIELKOŚCI POZYCJI** — „od 18.09.2026 … 26%" →
   „od 29.09.2026 … 12% (ALLOC_PCT=0.12)". Bez tej zmiany stopka każdego
   raportu dziennego zawyża przeliczenie punktów na dolary ponad dwukrotnie.

Poza tymi dwoma miejscami treść jest identyczna z zadaniem w schedulerze.

## Zmiany wprowadzone 12.10.2026 — kontrola rachunku przez `/status`

- `dzienna.md`: nowy **KROK 1b — KONTROLA RACHUNKU** (przed KROK 2) i
  **SEKCJA KONTROLA RACHUNKU** w KROK 3.
- `tygodniowa.md`: akapit **KONTROLA POKRYCIA RACHUNKU** na końcu KROK A.
- Obie rutyny czytają `curl -sS -m 120 "$NDX_BOT_URL/status"` (tylko
  odczyt; nagłówek `X-Run-Token` dokłada network secret środowiska). Zasady
  i znaczenie pól: `CLAUDE.md`. Po wklejeniu promptów do zadań sprawdź, że
  oba zadania wskazują środowisko, w którym jest `NDX_BOT_URL` i sekret
  (ikona chmury pod polem Instructions).

## Zmiany wprowadzone 12.10.2026 — konektor TradingView MCP, faza 1 (cień)

Plan: `WDROZENIE-TRADINGVIEW-2026-10-12.md`; zasady dla rutyn:
`rutyny/tradingview.md` (rutyny czytają go na starcie). Zgoda właściciela
12.10.2026. Po wklejeniu promptów włącz konektor TradingView w formularzu
KAŻDEGO zadania (ikona konektorów) — bez grantu sesja go nie widzi (lekcja FMP).

### `dzienna.md`

1. **Nagłówek** — harmonogram dni robocze ok. 12:30 UTC, blok TV do 13:15 UTC.
2. **KROK 0** — guard podwójnego biegu (precedens 12.10.2026).
3. **KROK 0b — KONEKTOR TRADINGVIEW MCP** — ładowanie narzędzi przez
   `select:`, allowlista, zakaz zapisu, budżet i twarda granica czasowa,
   429/401, symbole i kolumny tylko z plików, log, zasada cienia.
4. **ŹRÓDŁO KURSÓW** — martwy punkt „KONEKTOR MCP (FMP) = źródło nr 1"
   usunięty; `kursy.py` podstawowe; FMP tylko tam, gdzie działa; TV jako
   kontrola krzyżowa skryptem `tv_porownaj.py` i rezerwa poza sesją;
   kontrola wyceny brokera z `upl/size`.
5. **REŻIM** — usunięte zdanie o liczeniu reżimu z konektora; dodana rezerwa i
   kontrola serii 260 świec (`NASDAQ:NDX`, `CBOE:VIX`); licznik histerezy jako
   tabela 5 sesji.
6. **KROK 2, BLOKADA SEKTOROWA** — pomiar równoległy medianą branży TV
   (tylko cień; werdykt nadal z peers).
7. **KROK 3** — sekcja ŹRÓDŁA I PROBLEMY z linią STAN ŹRÓDEŁ i tabelą ZGODNOŚĆ.
8. **KROK 4** — walidator `waliduj_signals.py` przed commitem, zakaz nowych
   pól, lista plików dopuszczonych w commicie, bieg powtórny.

### `tygodniowa.md`

1. **Nagłówek** — wersja 12.10.
2. **KROK 0** — guard podwójnego biegu; **KROK 0b** jak w dziennej (budżet
   sobotni, snapshot do repo).
3. **ŹRÓDŁO KURSÓW** — `kursy.py` nr 1, FMP EOD-light dla 10 nóg, TV jako
   kontrola 21 kursów bez blokowania rotacji; `d0.prices` z TV tylko dla
   spółki bez kursu z Yahoo i FMP.
4. **KROK A** — dywidendy z `get-dividends-calendar` (korekta symetryczna),
   wariant „bez nóg EVENT" na papierze.
5. **KROK B0** — rezerwa i kontrola reżimu z serii TV.
6. **B1** — snapshot screenera (`rutyny/tv-zestaw-b1.json`) commitowany przed
   scoringiem, benchmark „sort po samym momentum", kontrola rang, konsensus
   przez `get-forecasts` jako kontekst (nie punktacja).
7. **B4** — lista „skład indeksu do weryfikacji", daty wyników z kolumny i
   kalendarza TV (pora dnia, `next_date_confirmed`), makro okna.
8. **KROK C** — sekcja PROBLEMY ze STAN ŹRÓDEŁ, tabelą ZGODNOŚĆ, kontrolą rang.
9. **KROK D** — walidator `--rutyna sobota`, pliki dopuszczone w commicie.

Nie zmieniono: Model 3.0 (wagi, limity bloków, kara event-risk, p=38–62%),
panel fundamentów (B0b), histereza, zasady koszyków, `tactical=[]` przy
rotacji. Pozycje N-P4, N-P5, N-R4 (newsy, pre-market, panel fundamentów ze
źródła) czekają na krok 8 planu — teksty w pliku PROPOZYCJA.

### 12.10.2026 (b) — faza 2 od startu (pełne użycie TV, decyzja właściciela)

- `data/tv-config.json`: `faza: 2`, budżety Puls ≤40 / 10 min, sobota ≤50 /
  20 min; flagi `b1_z_tv`, `rezim_surowszy`, `kryterium_event_remis`,
  `event_blokada_taktycznej` = `true`.
- `dzienna.md`: KROK 0b bez „fazy cienia"; REŻIM z poziomem surowszym; nowe
  KROK 1a (newsy, dokumenty, kalendarze z TV) i KROK 1c (pre-market, NQ,
  flaga EVENT, blokada taktycznej przy EVENT).
- `tygodniowa.md`: B0 poziom surowszy; B0b panel fundamentów ze źródła
  (`get-financial-history`, dokumenty, US10Y); B1 pkt (5) czynniki ilościowe
  z TV w scoringu, rewizje z `get-forecasts`, reguła D2; B4 kryterium remisu
  EVENT; KROK D pole `dane_b1` we wpisie `history`.
- Bramka licencyjna usunięta z planu (ryzyko przyjął właściciel).

## Zmiany wprowadzone 14.10.2026 — wykonalność pozycji taktycznych (`dzienna.md`)

Decyzja właściciela 14.10.2026 („zrób 1”). Przez cały wrzesień i październik
slot taktyczny stał pusty: zadanie kazało Pulsowi odrzucać kandydata, gdy
jego kurs przekraczał 1,6 × 20 % kapitału, zakładając minimalny lot
1 akcji. Bot liczy wykonalność inaczej (`app.py::calc_size`): minimalny lot
z brokera (`minDealSize`) × kurs ≤ `MAX_OVERSHOOT` × `TACTICAL_ALLOC_PCT` ×
kapitał, a lot dla większości dużych spółek USA to 0,1 akcji (historia
`fills`: MU, STX, AMD, AVGO 0,1; ADSK 0,3; INTU 0,26). Puls odrzucał więc
kandydatów, których bot otworzyłby bez trudu (13.10 UNH, GS; 14.10 BLK).

1. **KROK 2, MODUŁ TAKTYCZNY, akapit WYKONALNOŚĆ** — Puls wpisuje kandydata
   z twardym wyzwalaczem niezależnie od kursu akcji; o wykonalności decyduje
   bot, który zapisuje `wykonanie.taktyczne` („nieotwarta — min. wielkość N
   = X USD > tolerancja”); Puls usuwa taki wpis następnego dnia (jak dotąd)
   i nie wpisuje tej spółki ponownie w tym tygodniu. W raporcie limit w USD
   i wartość lotu w dwóch wariantach (0,1 akcji i 1 akcja).
2. **Nagłówek** — wersja 14.10.2026 (c).

Nie zmieniono: twardy wyzwalacz z 24 h, wsparcie elity dla SELL, limit
1 nowa/dzień i 2 otwarte, blokada EVENT, zawieszenie przy P1/P2, ustawienia
bota (`MAX_OVERSHOOT`, `TACTICAL_ALLOC_PCT`), kod bota. Po zmianie pliku
wklej do zadania „Puls NDX100” cały tekst poniżej linii — albo tylko akapit
WYKONALNOŚĆ (jedyna różnica względem kopii z 12.10.2026 (b)).

## Zmiany wprowadzone 18.10.2026 — proces v2 (`tygodniowa.md` (d), `dzienna.md` (d))

Podstawa: `rutyny/ANALIZA-2026-10-18-wyniki-i-metoda.md` (sześć analiz, pięć
testów wstecznych na 5 latach, dziewięć weryfikacji adwersaryjnych, trzy
projekty, trzech sędziów) i `rutyny/PROPOZYCJA-2026-10-18-proces-v2.md`.
Wniosek analizy: wynik W1–W7 był zakładem czynnikowym (półprzewodniki) przy
sizingu 240 %, scoring Modelu 3.0 nie miał mocy predykcyjnej, a pętla reguł
dopisywała reguły po n = 1. Proces v2 zamienia typowanie na pomiar.

### `tygodniowa.md`

1. **Zasada nadrzędna** — skład koszyka = `scripts/ranking.py`, konstrukcja E
   (5 par branżowych z budżetem |b_SOX net| ≤ 0,5); rutyna nie zmienia składu.
2. **KROK 0** — czyta `rutyny/reguly.md` (OBOWIĄZUJĄCE / WYJĄTKI z datą /
   KANDYDACI) i `data/ranking-<rozliczana version>.json`.
3. **KROK 0b** — TV zawężone do 7–10 wywołań (screener, kalendarze, ohlcv
   reżimu); bez `get-forecasts`, `get-financial-history`, newsów.
4. **KROK A** — prerejestrowana tabela A1–A9: obie serie spreadu, taktyczne
   i reakcje z wykonanych, **koszyki cienie** (`scripts/koszyki_cienie.py`,
   log `data/koszyki-cienie.jsonl`), dekompozycja czynnikowa i kalibracja σ,
   **KOSZT REGUŁ I NADPISAŃ**, zdanie o mocy (t, n), kandydaci na papierze,
   kontrola rachunku z zapasem do kill w σ i obsunięciem od szczytu
   historycznego.
5. **KROK B0** — reżim tylko jako wyłącznik P2; P1 = flaga; bez eskalacji
   uznaniowej.
6. **KROK B** — snapshot B1 → lista `--exclude` z zamkniętych źródeł →
   weryfikacja dat wyników → `ranking.py` → koszyk = `konstrukcje.E_pary_budzet_sox`;
   opcjonalny cień uznaniowy U w pliku ranking (nigdy w `signals.json`).
   Usunięte: Model 3.0 (B1/B2), elita (B3), panel fundamentów (B0b), p,
   pre-mortem, deklaracje D1–D3.
7. **KROK C** — stała kolejność sekcji; kryteria decyzji po 12/26/52 oknach
   od 12. okna.
8. **KROK D** — te same pola `signals.json`; `dane_b1: "yahoo"`; dodatkowe
   pliki `data/ranking-<version>.json`, `data/koszyki-cienie.jsonl`.

### `dzienna.md`

1. **Zasada nadrzędna** — Puls = raport kontrolny; bramka cenowa 4 %/8 % jest
   POMIAREM (sekcja BRAMKA — POMIAR), nie tworzy wpisów.
2. **KROK 0b** — TV ≤ 10 wywołań (3 batche, 2 ohlcv, 2 kalendarze; rezerwa
   ≤ 2 po dokument źródłowy).
3. **KROK 1** — research tylko w kategoriach listy zamkniętej R3/R11 oraz
   kalendarz; bez elity, FINRA, makro-narracji; pre-market informacyjnie.
4. **KROK 1b** — kontrola rachunku rozszerzona: `wykonanie.stopy/soft/kill`
   (bot v2), zapas do kill w σ dziennej, obsunięcie od szczytu historycznego,
   przestrzały lotów, parametry wyłącznie z `/status.ustawienia`.
5. **REŻIM** — P1 flaga (bez REDUCE), P2 `NIEAKTUALNA`; bez eskalacji.
6. **KROK 2** — `exclude` tylko `basis="news"` z dokumentem; `tactical=[]`;
   zakaz wpisów cena/rekom/short/rezim; moduł taktyczny i blokada sektorowa
   usunięte.
7. **KROK 3** — sekcje w stałej kolejności, stopka z parametrami z `/status`.

Bez zmian w obu: pola `signals.json`, które wolno pisać, walidator, guard
podwójnego biegu, harmonogram, `kursy.py` jako źródło nr 1, kontrola przez
`/status`. Pliki towarzyszące: `rutyny/reguly.md` (rejestr), `rutyny/tradingview.md`
§0a, `data/tv-config.json` 2026-10-18d, `CLAUDE.md` sekcja „Proces v2".
Po scaleniu do `main` wklej oba teksty poniżej linii do zadań na
claude.ai/code/routines; `app.py` wymaga osobnej decyzji właściciela
(PROPOZYCJA §3).

### 18.10.2026 — poprawki po przeglądzie adwersaryjnym (6 recenzentów, 98 ustaleń)

Najważniejsze zmiany względem pierwszej wersji v2 z tego samego dnia:

- `scripts/waliduj_signals.py`: usunięte zakleszczenie przy 26 wpisach
  `history` (oczekiwane = stare + nowy, obcięte do 26 ostatnich — jak w bocie);
  reguły v2 dla Pulsu (nowy wpis `exclude` tylko `basis="news"`, `tactical=[]`;
  `--v1` dla starszej rutyny). Testy w `scripts/test_app.py`.
- `scripts/ranking.py`: dopełnianie par przy < 5 grupach (`+dopelnione`),
  tryb `bez_czynnika` (brak bety SOX), percentyl σ wobec losowych koszyków
  z uniwersum PO vetach, `--exclude TICKER=POWÓD` + cień `E_bez_exclude`,
  `--faktyczny-long/-short` → konstrukcja `FAKTYCZNY` z ryzykiem, pole
  `earnings_date` i liczniki dat, ostrzeżenie przy D0 spoza danych, SMH w
  cache; `data/ranking-2026-W8.json` przeliczony (FAKTYCZNY = koszyk W8).
- `scripts/koszyki_cienie.py`: σ zrealizowana i ex ante w wierszu logu,
  cień `ETF_SMH_XLP`, pomijanie konstrukcji bez list (U „pominięty”),
  ostrzeżenie i brak logu przy sesji spoza cache, `--pokrycie`,
  `--podsumowanie` (CI, σ-ratio, test F bez scipy, E netto, kalibracja).
- `tygodniowa.md`: linia KOLEJNOŚĆ WYKONANIA; bieg 1 z `--fetch` do
  scratchpadu i bieg końcowy z `--closes`; `za_malo_par` → FALLBACK (nie
  „koszyk nadal E”); bez snapshotu → E bez taksonomii + daty z FMP/TV;
  kontrole wyjścia (d0, czynniki, liczniki dat); A5 jednoczynnikowa; A6
  z definicjami operacyjnymi; A7/A9 pełne ścieżki pól; guard po nazwie
  raportu NOWEJ wersji; `dane_b1` „tv” za W8 / „yahoo” od W9; history
  obcięte do 26; komenda na szczyt historyczny z `git log -p`; `--faza 2`;
  cień U obowiązkowy albo jawnie pominięty.
- `dzienna.md`: σ ex ante tylko z konstrukcji pasującej do `signals.json`
  (W8 = FAKTYCZNY), REDUCE basis news zamknięte do dwu przypadków, wpisy tylko
  dla aktualnych nóg, budżet WebSearch i czas (13:20/13:35 UTC), ROZJAZD
  ŹRÓDEŁ vs NIEZGODNOŚĆ D0 (wyjątek split/ex-date), `--faza 2`, MAX_OVERSHOOT 1,6.
- `tradingview.md`: nagłówek (3) w brzmieniu v2, §0a doprecyzowany, markery
  [v2: ZAWIESZONE] na §5.3–5.5, §6.2, §6.4, lista plików §8; `tv-zestaw-b1.json`
  pole konsensus; `tv-config.json` opisy.
- Dokumenty: budżet TV ujednolicony do ≤ 10 (zwykle 7); stan rachunku w
  dokumentach wyłącznie jako zaokrąglone wskaźniki (CLAUDE.md —
  doprecyzowanie reguły); `PROPOZYCJA` §0/§1/§4 i `ANALIZA` §0/§1.1/§4.2/§6/§7
  spójne z kodem; `reguly.md` K2'/R3/K0/R8 doprecyzowane.
