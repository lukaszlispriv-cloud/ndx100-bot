# Rutyny — źródło prawdy dla treści zadań

Dwa zadania w schedulerze Claude, dwa pliki tutaj. **Zawsze zmieniaj najpierw
plik, potem wklejaj do zadania** — wtedy historia gita mówi, co i kiedy się
zmieniło, a nadpisanie zadania przez pomyłkę odtwarza się jednym kopiuj-wklej.

| Plik | Zadanie | Kiedy | Co pisze do `signals.json` | Co produkuje |
|---|---|---|---|---|
| `dzienna.md` | „Puls NDX100" | codziennie ok. 12:40 UTC | tylko `status`, `exclude`, `tactical`, `last_daily` | `reports/puls-RRRR-MM-DD.html` |
| `tygodniowa.md` | „Ranking NDX100 — raport tygodniowy" | sobota ok. 07:30 UTC | `version`, `long`, `short`, `d0`, `generated`, `exclude=[]`, `tactical=[]`, wpis do `history` | `reports/raport-2026-WX.html` |

Żadna z nich nie dotyka `fills` ani `equity_peak` — te pisze bot.

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
