#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testy logiki decyzyjnej bota — bez sieci, bez brokera, bez GitHuba.

Uruchomienie:  python3 scripts/test_app.py
Kod wyjścia 0 = wszystko przeszło.

Zakres: bramka wyzwalaczy cenowych, kontrola kapitału, kill switch od
kroczącego szczytu, dobór wielkości pozycji przy grubym kroku, budowa
książki (w tym pozycje taktyczne z własnym epic) i kontrola spójności
signals.json. To są dokładnie te miejsca, w których system tracił
pieniądze albo po cichu nie robił tego, co zapisano w sygnałach.
"""
import os
import sys

os.environ.setdefault("GITHUB_REPO", "test/test")
os.environ.setdefault("RUN_TOKEN", "test")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app  # noqa: E402

ZIELONY, CZERWONY, KONIEC = "\033[32m", "\033[31m", "\033[0m"
_wynik = {"ok": 0, "zle": 0}


def sprawdz(nazwa, warunek, detal=""):
    if warunek:
        _wynik["ok"] += 1
        print(f"  {ZIELONY}OK{KONIEC}  {nazwa}")
    else:
        _wynik["zle"] += 1
        print(f"  {CZERWONY}ŹLE{KONIEC} {nazwa}" + (f" — {detal}" if detal else ""))


class FakeCap:
    """Minimalna atrapa Capital.com: tylko to, czego dotyka logika decyzji."""

    def __init__(self, ceny, status="TRADEABLE", minimum=0.1, waluta="USD"):
        self.ceny = ceny
        self.status = status
        self.minimum = minimum
        self.waluta = waluta
        self.zapytania = 0
        self._rynki = {}

    def market(self, epic, odswiez=False):
        self.zapytania += 1
        if epic not in self.ceny:
            raise app.requests.HTTPError(f"brak rynku {epic}")
        return {"epic": epic, "name": epic, "currency": self.waluta,
                "status": self.status, "mid": self.ceny[epic],
                "min": self.minimum}

    def fx_rate(self, a, b):
        return 1.0


def pusty_rep():
    return {"akcje": [], "pominiete": [], "błędy": []}


BAZA = {
    "version": "2026-W4", "status": "AKTUALNA",
    "long": ["MU", "AMD", "AVGO", "MRVL", "LITE"],
    "short": ["INTU", "SBUX", "CMCSA", "APP", "ADSK"],
    "epics": {t: t for t in ["MU", "AMD", "AVGO", "MRVL", "LITE",
                             "INTU", "SBUX", "CMCSA", "APP", "ADSK"]},
    "exclude": [], "tactical": [],
}


def sig(**kw):
    s = {k: (list(v) if isinstance(v, list) else
             dict(v) if isinstance(v, dict) else v)
         for k, v in BAZA.items()}
    s.update(kw)
    return s


# ---------------------------------------------------------------- bramka ----
print("\nBRAMKA WYZWALACZY CENOWYCH")

# Przypadek z 15.09.2026: LITE dostał CLOSE za "ruch -9,92% od D0" (927,03),
# ale bot wszedł po 842,25 i wobec własnego wejścia był NA PLUSIE.
s = sig(exclude=[{"ticker": "LITE", "action": "CLOSE",
                  "reason": "ruch -9,92% od D0", "basis": "cena"}])
cap = FakeCap({"LITE": 845.95})
fills = {"LITE": {"cena": 842.25}}
rep = pusty_rep()
closed, reduced, slad = app.bramka_reakcji(s, cap, fills, rep)
sprawdz("LITE: CLOSE od D0 nie zamyka pozycji będącej na plusie od wejścia",
        "LITE" not in closed and "LITE" not in reduced, f"closed={closed}")
sprawdz("złagodzenie trafia do listy pominiętych", len(rep["pominiete"]) == 1)

# Pozycja naprawdę pod wodą wobec wejścia — CLOSE ma przejść.
s = sig(exclude=[{"ticker": "AVGO", "action": "CLOSE", "reason": "ruch -9% od D0"}])
cap = FakeCap({"AVGO": 330.0})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"AVGO": {"cena": 364.64}},
                                        pusty_rep())
sprawdz("AVGO: realna strata 9,5% od wejścia — CLOSE przechodzi",
        "AVGO" in closed, f"closed={closed}")

# Strata w paśmie miękkim: CLOSE ma zejść do REDUCE, nie zniknąć.
cap = FakeCap({"AVGO": 345.0})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"AVGO": {"cena": 364.64}},
                                        pusty_rep())
sprawdz("AVGO: strata 5,4% od wejścia — CLOSE złagodzony do REDUCE",
        "AVGO" in reduced and "AVGO" not in closed, f"r={reduced} c={closed}")

# Krótka pozycja: stratą jest WZROST kursu.
s = sig(exclude=[{"ticker": "ADSK", "action": "REDUCE", "reason": "ruch +7,8% od D0"}])
cap = FakeCap({"ADSK": 230.82})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"ADSK": {"cena": 228.56}},
                                        pusty_rep())
sprawdz("ADSK short: wzrost o 1,0% od wejścia — REDUCE pominięty",
        "ADSK" not in reduced and "ADSK" not in closed)
cap = FakeCap({"ADSK": 245.0})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"ADSK": {"cena": 228.56}},
                                        pusty_rep())
sprawdz("ADSK short: wzrost o 7,2% od wejścia — REDUCE przechodzi",
        "ADSK" in reduced)

# Wpis reżimowy nie jest wyzwalaczem cenowym — bramka go nie dotyka.
s = sig(exclude=[{"ticker": "MU", "action": "REDUCE", "reason": "REŻIM P1"}])
cap = FakeCap({"MU": 977.5})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"MU": {"cena": 913.35}},
                                        pusty_rep())
sprawdz("wpis REŻIM P1 przechodzi bez weryfikacji ceny", "MU" in reduced)

# Wpis oparty na newsie też przechodzi bez bramki.
s = sig(exclude=[{"ticker": "CMCSA", "action": "REDUCE",
                  "reason": "ostrzeżenie CFO", "basis": "news"}])
cap = FakeCap({"CMCSA": 22.91})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"CMCSA": {"cena": 26.57}},
                                        pusty_rep())
sprawdz("wpis o podstawie 'news' przechodzi bez weryfikacji ceny",
        "CMCSA" in reduced)

# Brak ceny wejścia = brak podstawy do łagodzenia; wpis wykonujemy.
s = sig(exclude=[{"ticker": "APP", "action": "CLOSE", "reason": "ruch od D0"}])
cap = FakeCap({"APP": 300.0})
closed, reduced, slad = app.bramka_reakcji(s, cap, {}, pusty_rep())
sprawdz("brak ceny wejścia — wpis pulsu wykonany bez zmian", "APP" in closed)
sprawdz("ślad decyzji odnotowuje brak danych",
        any("brak danych" in (x.get("uwaga") or "") for x in slad))

# Bramka nigdy nie zaostrza: REDUCE przy stracie 12% zostaje REDUCE.
s = sig(exclude=[{"ticker": "LITE", "action": "REDUCE", "reason": "ruch od D0"}])
cap = FakeCap({"LITE": 800.0})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"LITE": {"cena": 927.03}},
                                        pusty_rep())
sprawdz("bramka nie awansuje REDUCE do CLOSE",
        "LITE" in reduced and "LITE" not in closed)

# Wyłączona bramka = zachowanie sprzed poprawki.
app.REACT_GATE = False
s = sig(exclude=[{"ticker": "LITE", "action": "CLOSE", "reason": "ruch od D0"}])
closed, _, _ = app.bramka_reakcji(s, FakeCap({"LITE": 845.95}),
                                  {"LITE": {"cena": 842.25}}, pusty_rep())
sprawdz("REACT_GATE=false przywraca stare zachowanie", "LITE" in closed)
app.REACT_GATE = True

# ------------------------------------------------------- kontrola kapitału ---
print("\nKONTROLA KAPITAŁU")

snap = {"equity": 1041.32, "gotowka": 986.14, "wycena": 55.18, "ccy": "USD"}
poz = [{"epic": "MU", "direction": "BUY", "size": 0.1, "upl": 6.41},
       {"epic": "AMD", "direction": "BUY", "size": 0.2, "upl": 14.65},
       {"epic": "CMCSA", "direction": "SELL", "size": 4, "upl": 34.12}]
rep = pusty_rep()
k = app.kontrola_kapitalu(snap, poz, {"MU", "AMD", "CMCSA"}, rep)
sprawdz("zgodna wycena przechodzi kontrolę", k["zgodne"], k)

# Pozycja spoza książki bota — dokładnie ten scenariusz tłumaczyłby
# rozjazd kapitału z historią transakcji.
poz2 = poz + [{"epic": "TSLA", "direction": "BUY", "size": 1, "upl": 40.0}]
rep = pusty_rep()
k = app.kontrola_kapitalu(snap, poz2, {"MU", "AMD", "CMCSA"}, rep)
sprawdz("pozycja spoza książki zapala kontrolę", not k["zgodne"])
sprawdz("powód trafia do błędów biegu",
        any("KONTROLA KAPITAŁU" in b for b in rep["błędy"]))

# Rozjazd samej wyceny (bez obcych pozycji).
rep = pusty_rep()
k = app.kontrola_kapitalu({"equity": 1104.12, "gotowka": 1000.0,
                           "wycena": 104.12, "ccy": "USD"},
                          poz, {"MU", "AMD", "CMCSA"}, rep)
sprawdz("wycena z API niezgodna z sumą upl zapala kontrolę", not k["zgodne"])

# Pozycja bez wyceny z API.
rep = pusty_rep()
k = app.kontrola_kapitalu(snap, [{"epic": "MU", "direction": "BUY",
                                  "size": 0.1, "upl": None}], {"MU"}, rep)
sprawdz("pozycja bez upl zapala kontrolę", not k["zgodne"])

# ------------------------------------------------------- ruch przeciw tezie --
print("\nPOMIAR RUCHU")
sprawdz("long pod wodą daje liczbę dodatnią",
        abs(app.ruch_przeciw_tezie("BUY", 100, 90) - 0.10) < 1e-9)
sprawdz("long na plusie daje liczbę ujemną",
        app.ruch_przeciw_tezie("BUY", 100, 110) < 0)
sprawdz("short pod wodą daje liczbę dodatnią",
        abs(app.ruch_przeciw_tezie("SELL", 100, 110) - 0.10) < 1e-9)
sprawdz("brak ceny wejścia daje None",
        app.ruch_przeciw_tezie("BUY", None, 90) is None)
sprawdz("zerowa cena wejścia nie wywala się",
        app.ruch_przeciw_tezie("BUY", 0, 90) is None)

# ------------------------------------------------------------------ stopy ----
print("\nTWARDY STOP OD CENY WEJŚCIA")
poz = [{"epic": "STX", "direction": "BUY", "size": 0.1, "wejscie": 909.52},
       {"epic": "MU", "direction": "BUY", "size": 0.1, "wejscie": 913.35}]
cap = FakeCap({"STX": 790.55, "MU": 977.5})
trafione = app.stopy_bezpieczenstwa(poz, {}, {"STX": "STX", "MU": "MU"},
                                    cap, pusty_rep())
sprawdz("STX -13% od wejścia przebija stop", "STX" in trafione, trafione)
sprawdz("MU na plusie nie przebija stopu", "MU" not in trafione)

stary = app.STOP_LOSS_PCT
app.STOP_LOSS_PCT = 0
sprawdz("STOP_LOSS_PCT=0 wyłącza stopy",
        app.stopy_bezpieczenstwa(poz, {}, {"STX": "STX"}, cap, pusty_rep()) == {})
app.STOP_LOSS_PCT = stary

# Rynek zamknięty nie generuje stopu na starej cenie.
cap = FakeCap({"STX": 790.55}, status="CLOSED")
sprawdz("stop nie działa przy zamkniętym rynku",
        app.stopy_bezpieczenstwa([poz[0]], {}, {"STX": "STX"}, cap,
                                 pusty_rep()) == {})

# ------------------------------------------------------------ rynek() --------
print("\nKLASYFIKACJA STANU RYNKU")
rep = pusty_rep()
sprawdz("otwarty rynek zwraca migawkę",
        app.rynek(FakeCap({"MU": 977.5}), "MU", rep, "MU") is not None)
rep = pusty_rep()
app.rynek(FakeCap({"MU": 977.5}, status="CLOSED"), "MU", rep, "MU")
sprawdz("zamknięty rynek to pominięcie, nie błąd",
        len(rep["pominiete"]) == 1 and not rep["błędy"], rep)
rep = pusty_rep()
app.rynek(FakeCap({}), "MU", rep, "MU")
sprawdz("brak rynku w API to błąd", len(rep["błędy"]) == 1 and not rep["pominiete"])

# -------------------------------------------------------------- książka -----
print("\nBUDOWA KSIĄŻKI")
book, skipped, closed = app.desired_book(sig(), set(), set())
sprawdz("pełna książka to 10 pozycji", len(book) == 10, len(book))
book, _, closed = app.desired_book(sig(), {"LITE"}, {"MU"})
sprawdz("CLOSE usuwa pozycję z książki", "LITE" not in book)
sprawdz("REDUCE zostawia pozycję z flagą", book["MU"]["reduced"] is True)

s = sig(tactical=[{"ticker": "GNRC", "direction": "BUY", "epic": "GNRC"}])
book, skipped, _ = app.desired_book(s, set(), set())
sprawdz("taktyczna z własnym epic wchodzi do książki spoza uniwersum",
        "GNRC" in book and book["GNRC"].get("tactical") is True, skipped)
s = sig(tactical=[{"ticker": "GNRC", "direction": "BUY"}])
book, skipped, _ = app.desired_book(s, set(), set())
sprawdz("taktyczna bez epic i spoza uniwersum jest pomijana",
        "GNRC" not in book and any("GNRC" in x for x in skipped))

# ------------------------------------------------------------- spójność ------
print("\nKONTROLA SPÓJNOŚCI signals.json")


def bledny(s, opis):
    try:
        app._sanity(s)
        sprawdz(opis, False, "przeszło, a nie powinno")
    except ValueError:
        sprawdz(opis, True)


app._sanity(sig())
sprawdz("poprawny plik przechodzi", True)
bledny(sig(long=["MU"]), "koszyk niepełny jest odrzucany")
bledny(sig(exclude=[{"ticker": "MU", "action": "SPRZEDAJ"}]),
       "nieznane action jest odrzucane")
bledny(sig(exclude=[{"ticker": "MU", "action": "REDUCE", "basis": "wrozba"}]),
       "nieznane basis jest odrzucane")
bledny(sig(fills={"MU": {"cena": -1}}), "ujemna cena wejścia jest odrzucana")
bledny(sig(fills={"MU": {"cena": "abc"}}), "nieliczbowa cena wejścia jest odrzucana")
app._sanity(sig(fills={"MU": {"cena": 913.35, "data": "2026-08-27"}}))
sprawdz("poprawne fills przechodzą", True)
app._sanity(sig(exclude=[{"ticker": "MU", "action": "REDUCE", "basis": "news"}]))
sprawdz("poprawne basis przechodzi", True)
app._sanity(sig(tactical=[{"ticker": "GNRC", "direction": "BUY", "epic": "GNRC"}]))
sprawdz("taktyczna spoza uniwersum z epic przechodzi", True)
bledny(sig(tactical=[{"ticker": "GNRC", "direction": "BUY"}]),
       "taktyczna spoza uniwersum bez epic jest odrzucana")

# --------------------------------------------------------------- cache -------
print("\nCACHE MIGAWEK RYNKU")
c = FakeCap({"MU": 977.5})
real = app.Capital.__new__(app.Capital)
real._rynki = {}
real._get = lambda path, params=None: {
    "snapshot": {"bid": 977.0, "offer": 978.0, "marketStatus": "TRADEABLE"},
    "dealingRules": {"minDealSize": {"value": 0.1}},
    "instrument": {"name": "Micron", "currency": "USD"}}
a = real.market("MU")
b = real.market("MU")
sprawdz("drugie wywołanie market() idzie z cache", a is b)
sprawdz("cena mid liczona ze środka widełek", abs(a["mid"] - 977.5) < 1e-9)

# ------------------------------------------------- ogranicznik tempa --------
print("\nOGRANICZNIK TEMPA WZROSTU EKSPOZYCJI")


def symuluj_alloc(pozycje_brutto, cel_brutto, alloc=0.13,
                  krok=None):
    """Powtarza arytmetykę ogranicznika z sync() na gołych liczbach."""
    krok = app.MAX_EXPOSURE_STEP if krok is None else krok
    if krok <= 0 or pozycje_brutto <= 0:
        return alloc
    limit = pozycje_brutto * (1 + krok)
    if cel_brutto > limit:
        return alloc * (limit / cel_brutto)
    return alloc


sprawdz("wzrost w granicach limitu nie rusza alloc",
        abs(symuluj_alloc(709, 800) - 0.13) < 1e-12)
a = symuluj_alloc(709, 1440)
sprawdz("podwojenie książki jest przycinane do +25%",
        abs(a - 0.13 * (709 * 1.25 / 1440)) < 1e-12, a)
sprawdz("przycięty alloc daje ekspozycję równą limitowi",
        abs((a / 0.13) * 1440 - 709 * 1.25) < 1e-9)
sprawdz("pusty portfel nie jest ograniczany (pierwsze wejście)",
        abs(symuluj_alloc(0, 1440) - 0.13) < 1e-12)
sprawdz("MAX_EXPOSURE_STEP=0 wyłącza ogranicznik",
        abs(symuluj_alloc(709, 1440, krok=0) - 0.13) < 1e-12)
sprawdz("zmniejszanie książki nie jest ograniczane",
        abs(symuluj_alloc(1440, 709) - 0.13) < 1e-12)


# ------------------------------------------------ liczenie kapitalu ---------
print("\nLICZENIE KAPITALU (balance vs balance + profitLoss)")


def konto(balance, profit_loss, deposit=None, ccy="USD"):
    b = {"balance": balance, "profitLoss": profit_loss, "available": 900.0}
    if deposit is not None:
        b["deposit"] = deposit
    cap = app.Capital.__new__(app.Capital)
    cap._rynki = {}
    cap.accounts = lambda: [{"accountId": "X", "currency": ccy,
                             "preferred": True, "balance": b}]
    return cap.account_snapshot()


# Stan rachunku z 18.09.2026: gotowka 986,14 + wycena 55,18 = kapital 1041,32.
# Stary kod zwracal 1041,32 + 55,18 = 1096,50, czyli liczyl wycene dwa razy.
s1 = konto(balance=1041.32, profit_loss=55.18, deposit=986.14)
sprawdz("kapitalem jest samo pole balance",
        abs(s1["equity"] - 1041.32) < 1e-9, s1["equity"])
sprawdz("wycena nie jest doliczana drugi raz",
        abs(s1["equity"] - (1041.32 + 55.18)) > 1e-9)
sprawdz("gotowka liczona z definicji: balance - profitLoss",
        abs(s1["gotowka"] - 986.14) < 1e-9, s1["gotowka"])

# Panel Capital.com 18.09.2026: equity 1041,61, depozyt 177,45 (margin!),
# wydajnosc 58,10, dostepne 864,15. Pole "deposit" to DEPOZYT
# ZABEZPIECZAJACY, nie gotowka — nie wolno na nim opierac zadnej kontroli.
s_real = konto(balance=1041.61, profit_loss=58.10, deposit=177.45)
sprawdz("prawdziwy rachunek: kapital = 1041,61",
        abs(s_real["equity"] - 1041.61) < 1e-9)
sprawdz("depozyt zabezpieczajacy przechowany osobno",
        abs(s_real["depozyt"] - 177.45) < 1e-9)
poz_real = [{"epic": "MU", "direction": "BUY", "size": 0.1, "upl": 20.0},
            {"epic": "AMD", "direction": "BUY", "size": 0.2, "upl": 38.10}]
rep_t = pusty_rep()
k_real = app.kontrola_kapitalu(s_real, poz_real, {"MU", "AMD"}, rep_t)
sprawdz("depozyt rozny od gotowki NIE zapala falszywie kontroli",
        k_real["zgodne"], k_real)
# Kontrola nadal ma dzialac tam, gdzie powinna: wycena bez pokrycia w upl.
rep_t = pusty_rep()
k_pusty = app.kontrola_kapitalu(s_real, [], set(), rep_t)
sprawdz("wycena 58,10 bez ani jednej pozycji zapala kontrole",
        not k_pusty["zgodne"])

# Gdy API nie poda deposit, nic sie nie psuje.
s2 = konto(balance=1041.32, profit_loss=55.18)
sprawdz("brak pola deposit nie wywala migawki", s2["depozyt"] is None)
sprawdz("gotowka nadal liczona poprawnie",
        abs(s2["gotowka"] - 986.14) < 1e-9)

# Rachunek bez otwartych pozycji.
s4 = konto(balance=1000.0, profit_loss=0.0, deposit=0.0)
sprawdz("pusty portfel: kapital = gotowka", abs(s4["equity"] - 1000.0) < 1e-9)

# equity() musi zwracac to samo co account_snapshot()["equity"].
cap = app.Capital.__new__(app.Capital)
cap._rynki = {}
cap.accounts = lambda: [{"accountId": "X", "currency": "USD", "preferred": True,
                         "balance": {"balance": 1041.32, "profitLoss": 55.18,
                                     "deposit": 986.14, "available": 900.0}}]
eq, ccy_, acc_ = cap.equity()
sprawdz("equity() zgodne z account_snapshot()", abs(eq - 1041.32) < 1e-9, eq)
sprawdz("equity() zwraca walute i numer rachunku",
        ccy_ == "USD" and acc_ == "X")


# ---------------------------------------------- limit depozytowy ------------
print("\nLIMIT DEPOZYTOWY")


def limit_depozytowy(equity, stopa, alloc, n=10, budzet=None):
    """Powtarza arytmetyke limitu z sync() na golych liczbach."""
    budzet = app.MARGIN_BUDGET if budzet is None else budzet
    max_brutto = equity * budzet / stopa
    cel = equity * alloc * n
    return (alloc * (max_brutto / cel)) if cel > max_brutto > 0 else alloc


# Stan z 18.09.2026: kapital 1041,61, stopa depozytu 20%, cel 26% x 10.
sprawdz("cel 26% x 10 miesci sie w budzecie depozytu",
        abs(limit_depozytowy(1041.61, 0.20, 0.26) - 0.26) < 1e-12,
        limit_depozytowy(1041.61, 0.20, 0.26))
depozyt_po = 1041.61 * 0.26 * 10 * 0.20
sprawdz("depozyt po podwojeniu to ok. 542 USD", abs(depozyt_po - 541.6) < 1.0,
        round(depozyt_po, 2))
sprawdz("zostaje ponad 45% kapitalu wolnego",
        (1041.61 - depozyt_po) / 1041.61 > 0.45)

# Za duzy cel musi zostac przyciety.
a = limit_depozytowy(1041.61, 0.20, 0.50)
sprawdz("cel 50% x 10 jest przycinany przez budzet depozytu", a < 0.50, a)
sprawdz("po przycieciu depozyt rowna sie budzetowi",
        abs(1041.61 * a * 10 * 0.20 - 1041.61 * app.MARGIN_BUDGET) < 1e-6)

# Wyzsza stopa depozytu (mniejsza dzwignia) tnie mocniej.
sprawdz("stopa 50% ogranicza cel bardziej niz stopa 20%",
        limit_depozytowy(1041.61, 0.50, 0.26)
        < limit_depozytowy(1041.61, 0.20, 0.26))

# Wartosci domyslne po podwojeniu.
sprawdz("ALLOC_PCT podwojony do 0.26", abs(app.ALLOC_PCT - 0.26) < 1e-12,
        app.ALLOC_PCT)
sprawdz("TACTICAL_ALLOC_PCT podwojony do 0.10",
        abs(app.TACTICAL_ALLOC_PCT - 0.10) < 1e-12, app.TACTICAL_ALLOC_PCT)
sprawdz("ALLOC_PCT_SAFE zostaje zachowawczy",
        app.ALLOC_PCT_SAFE < app.ALLOC_PCT)


print(f"\n{'=' * 52}")
print(f"przeszło: {_wynik['ok']}   nie przeszło: {_wynik['zle']}")
print("=" * 52)
sys.exit(1 if _wynik["zle"] else 0)
