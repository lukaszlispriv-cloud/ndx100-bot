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
# PROCES v2 (18.10.2026): stop LONG 15% — -13% już NIE wystarcza; przy dawnym
# progu 10% (zmienna STOP_LOSS_PCT_LONG) nadal przebija.
sprawdz("STX -13% od wejścia NIE przebija stopu LONG 15% (v2)", "STX" not in trafione, trafione)
sprawdz("MU na plusie nie przebija stopu", "MU" not in trafione)
_sl = app.STOP_LOSS_PCT_LONG
app.STOP_LOSS_PCT_LONG = 0.10
trafione = app.stopy_bezpieczenstwa(poz, {}, {"STX": "STX", "MU": "MU"},
                                    cap, pusty_rep())
sprawdz("przy progu 10% (dawne ustawienie) STX -13% przebija stop", "STX" in trafione, trafione)
app.STOP_LOSS_PCT_LONG = _sl

_sl, _ss = app.STOP_LOSS_PCT_LONG, app.STOP_LOSS_PCT_SHORT
app.STOP_LOSS_PCT_LONG = app.STOP_LOSS_PCT_SHORT = 0
sprawdz("STOP_LOSS_PCT_LONG = STOP_LOSS_PCT_SHORT = 0 wyłącza stopy",
        app.stopy_bezpieczenstwa(poz, {}, {"STX": "STX"}, cap, pusty_rep()) == {})
app.STOP_LOSS_PCT_LONG, app.STOP_LOSS_PCT_SHORT = _sl, _ss

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

# PROCES v2 (18.10.2026): moduł taktyczny jest domyślnie WYŁĄCZONY — testy
# jego mechaniki włączają go jawnie, a osobny test pilnuje domyślnego stanu.
s = sig(tactical=[{"ticker": "GNRC", "direction": "BUY", "epic": "GNRC"}])
book, skipped, _ = app.desired_book(s, set(), set())
sprawdz("TACTICAL_ENABLED=false (v2): taktyczna nie wchodzi do książki",
        "GNRC" not in book and len(book) == 10, sorted(book))
_te = app.TACTICAL_ENABLED
app.TACTICAL_ENABLED = True
book, skipped, _ = app.desired_book(s, set(), set())
sprawdz("taktyczna z własnym epic wchodzi do książki spoza uniwersum (moduł włączony)",
        "GNRC" in book and book["GNRC"].get("tactical") is True, skipped)
s = sig(tactical=[{"ticker": "GNRC", "direction": "BUY"}])
book, skipped, _ = app.desired_book(s, set(), set())
sprawdz("taktyczna bez epic i spoza uniwersum jest pomijana",
        "GNRC" not in book and any("GNRC" in x for x in skipped))
app.TACTICAL_ENABLED = _te

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

# Wartosci domyslne: 3.10.2026 podwojenie do 0,24; 18.10.2026 (proces v2)
# zejscie do 0,08 — analiza W1-W7: P(kill) przy 0,24 i alfie 0 to 98-100%/rok.
sprawdz("ALLOC_PCT domyslnie 0.08 (proces v2)", abs(app.ALLOC_PCT - 0.08) < 1e-12,
        app.ALLOC_PCT)
sprawdz("TACTICAL_ALLOC_PCT domyslnie 0.20",
        abs(app.TACTICAL_ALLOC_PCT - 0.20) < 1e-12, app.TACTICAL_ALLOC_PCT)
sprawdz("ALLOC_PCT_SAFE zostaje zachowawczy",
        app.ALLOC_PCT_SAFE < app.ALLOC_PCT)


# -------------------------------- koniunkcja: analityk wzglednie, bot bezwzglednie
print("\nKONIUNKCJA PROGOW (decyzja projektowa, 18.09.2026)")
# Puls liczy ruch WZGLEDEM ^NDX, bot liczy BEZWZGLEDNIE od ceny wejscia.
# Wpis wykonuje sie tylko wtedy, gdy OBA testy wypadna na tak. Ustawienie
# jest swiadomie konserwatywne: czesciej NIE tnie pozycji. Rozliczenie
# okresu 27.08-18.09.2026 pokazalo, ze ciecia kosztowaly 17,43 USD, wiec
# blad w strone "nie tnij" jest tanszy niz blad w strone "tnij".
s = sig(exclude=[{"ticker": "MU", "action": "REDUCE",
                  "reason": "-5 p.p. wzglednie vs ^NDX", "basis": "cena"}])
# Spolka -2% od wejscia, indeks +3% -> wzglednie -5 p.p. (puls widzi sygnal),
# ale bezwzglednie tylko -2% (bot ponizej progu 4%).
cap = FakeCap({"MU": 913.35 * 0.98})
closed, reduced, slad = app.bramka_reakcji(s, cap, {"MU": {"cena": 913.35}},
                                           pusty_rep())
sprawdz("sygnal wylacznie wzgledny NIE jest wykonywany przez bota",
        "MU" not in reduced and "MU" not in closed, f"r={reduced}")
sprawdz("powod odrzucenia jest zapisany w sladzie decyzji",
        slad[0]["wykonane"] == "BRAK" and "uwaga" in slad[0])

# Ten sam sygnal, ale pozycja realnie 5% pod woda -> oba testy na tak.
cap = FakeCap({"MU": 913.35 * 0.95})
closed, reduced, _ = app.bramka_reakcji(s, cap, {"MU": {"cena": 913.35}},
                                        pusty_rep())
sprawdz("sygnal wzgledny POPARTY realna strata jest wykonywany",
        "MU" in reduced)

# Bramka nie dziala w druga strone: nie tworzy wpisu tam, gdzie puls go nie dal.
s_pusty = sig(exclude=[])
closed, reduced, slad = app.bramka_reakcji(s_pusty, FakeCap({"MU": 500.0}),
                                           {"MU": {"cena": 913.35}},
                                           pusty_rep())
sprawdz("bramka nigdy nie dokłada reakcji z wlasnej inicjatywy",
        not closed and not reduced and not slad)


# ------------------------- cena odniesienia tezy (audyt 28.09.2026) ---------
# Wyrównanie wielkości musi zamknąć i otworzyć pozycję na nowo, więc poziom
# otwarcia u brokera bywa sprzed kilku godzin. Bramka i stop-loss liczą od
# ceny wejścia, więc nadpisywanie jej tym poziomem unieruchamiało oba
# zabezpieczenia: "bramka x4" w dwudziestu biegach z rzędu i ani jedna
# z pięciu reakcji z 15-17.09 nie została wykonana.
print("\nCENA ODNIESIENIA TEZY — przeżywa wyrównanie wielkości")

E2T = {t: t for t in BAZA["epics"]}


def poz(epic, wejscie, kier="BUY", otwarta="2026-09-25T13:45:00", size=0.1):
    return {"epic": epic, "direction": kier, "wejscie": wejscie,
            "otwarta": otwarta, "size": size, "dealId": "d-" + epic}


# 1. Pozycja zamknięta i otwarta na nowo w ramach wyrównania: broker podaje
#    nowy poziom 1082,28, ale tezę zakładaliśmy po 913,35.
s = sig(fills={"MU": {"cena": 913.35, "kierunek": "BUY", "data": "2026-08-27",
                      "wersja": "2026-W4"}})
f = app.ceny_wejscia(s, [poz("MU", 1082.28)], E2T)
sprawdz("wyrownanie NIE kasuje ceny odniesienia",
        f["MU"]["cena"] == 913.35, f["MU"])
sprawdz("biezacy poziom brokera zachowany osobno",
        f["MU"]["cena_brokera"] == 1082.28)
sprawdz("data wejscia w teze tez przezywa",
        f["MU"]["data"] == "2026-08-27")

# 2. Bramka liczy od odniesienia, nie od poziomu z ostatniego wyrownania.
#    MU 913,35 -> 822,00 to -10% przeciw tezie dlugiej: CLOSE ma przejsc.
s2 = sig(exclude=[{"ticker": "MU", "action": "CLOSE", "basis": "cena"}],
         fills={"MU": {"cena": 913.35, "kierunek": "BUY",
                       "wersja": "2026-W4"}})
closed, reduced, slad = app.bramka_reakcji(
    s2, FakeCap({"MU": 822.0}), app.ceny_wejscia(s2, [poz("MU", 830.0)], E2T),
    pusty_rep())
sprawdz("bramka widzi strate liczona od odniesienia, nie od wyrownania",
        "MU" in closed, f"c={closed} r={reduced}")

# 3. Rotacja koszyka (zmiana version) kasuje odniesienie spolki, ktora
#    WYPADLA z koszyka — nowy tydzien to nowa teza i nowa cena wejscia.
s3 = sig(version="2026-W5", long=["AMD", "AVGO", "MRVL", "LITE", "NVDA"],
         epics=dict(BAZA["epics"], NVDA="NVDA"),
         fills={"MU": {"cena": 913.35, "kierunek": "BUY",
                       "wersja": "2026-W4"}})
f3 = app.ceny_wejscia(s3, [poz("MU", 1082.28)], E2T)
sprawdz("rotacja koszyka resetuje cene odniesienia spolki spoza koszyka",
        f3["MU"]["cena"] == 1082.28 and f3["MU"]["wersja"] == "2026-W5", f3)

# 3a. Przypadek z 10.10.2026: rutyna tygodniowa zmienila version w sobote,
#     a MU zostal w koszyku LONG na W7. Bieg bota przed poniedzialkowa
#     rotacja NIE moze skasowac ceny tezy — noga jest kontynuowana.
s3a = sig(version="2026-W5",
          fills={"MU": {"cena": 913.35, "kierunek": "BUY", "data": "2026-08-27",
                        "wersja": "2026-W4"}})
f3a = app.ceny_wejscia(s3a, [poz("MU", 1082.28)], E2T)
sprawdz("noga kontynuowana po rotacji zachowuje cene i date tezy",
        f3a["MU"]["cena"] == 913.35 and f3a["MU"]["data"] == "2026-08-27", f3a)
sprawdz("noga kontynuowana dostaje nowa wersje i poziom brokera",
        f3a["MU"]["wersja"] == "2026-W5" and f3a["MU"]["cena_brokera"] == 1082.28,
        f3a)
sprawdz("zrodlo opisuje kontynuacje",
        "kontynuowana" in f3a["MU"]["zrodlo"], f3a["MU"]["zrodlo"])

# 3b. Ta sama spolka, ale po rotacji w PRZECIWNYM koszyku (long -> short):
#     to nowa teza, odniesienie musi sie zresetowac.
s3b = sig(version="2026-W5", long=["AMD", "AVGO", "MRVL", "LITE", "INTU"],
          short=["MU", "SBUX", "CMCSA", "APP", "ADSK"],
          fills={"MU": {"cena": 913.35, "kierunek": "BUY",
                        "wersja": "2026-W4"}})
f3b = app.ceny_wejscia(s3b, [poz("MU", 1082.28, kier="SELL")], E2T)
sprawdz("zmiana koszyka long->short resetuje odniesienie",
        f3b["MU"]["cena"] == 1082.28, f3b)

# 3c. Pozycja short, ktora po rotacji nadal jest w koszyku SHORT.
s3c = sig(version="2026-W5",
          fills={"APP": {"cena": 308.51, "kierunek": "SELL",
                         "wersja": "2026-W4"}})
f3c = app.ceny_wejscia(s3c, [poz("APP", 277.22, kier="SELL")], E2T)
sprawdz("short kontynuowany po rotacji zachowuje cene tezy",
        f3c["APP"]["cena"] == 308.51 and f3c["APP"]["wersja"] == "2026-W5", f3c)

# 3d. Taktyczna z wlasnym epic kontynuowana w tactical po zmianie wersji.
s3d = sig(version="2026-W5",
          tactical=[{"ticker": "APOG", "direction": "BUY", "epic": "APOG"}],
          fills={"APOG": {"cena": 42.64, "kierunek": "BUY",
                          "wersja": "2026-W4"}})
f3d = app.ceny_wejscia(s3d, [poz("APOG", 40.59)], dict(E2T, APOG="APOG"))
sprawdz("taktyczna kontynuowana w tactical zachowuje cene tezy",
        f3d["APOG"]["cena"] == 42.64, f3d)

# 3e. Wywolanie bez long/short (stary styl) zachowuje dawne zachowanie.
f3e = app.ceny_wejscia({"version": "2026-W5",
                        "fills": {"MU": {"cena": 913.35, "kierunek": "BUY",
                                         "wersja": "2026-W4"}}},
                       [poz("MU", 1082.28)], E2T)
sprawdz("bez listy koszykow zmiana wersji nadal resetuje",
        f3e["MU"]["cena"] == 1082.28, f3e)

# 4. Odwrocenie kierunku tez kasuje odniesienie.
s4 = sig(fills={"MU": {"cena": 913.35, "kierunek": "SELL",
                       "wersja": "2026-W4"}})
f4 = app.ceny_wejscia(s4, [poz("MU", 1082.28, kier="BUY")], E2T)
sprawdz("zmiana kierunku resetuje cene odniesienia",
        f4["MU"]["cena"] == 1082.28, f4)

# 5. Wpis sprzed tej zmiany (bez pola "wersja") jest uznawany za wazny —
#    migracja nie moze zgubic historycznych cen wejscia.
s5 = sig(fills={"MU": {"cena": 913.35, "kierunek": "BUY"}})
f5 = app.ceny_wejscia(s5, [poz("MU", 1082.28)], E2T)
sprawdz("wpis sprzed migracji (bez pola wersja) zostaje zachowany",
        f5["MU"]["cena"] == 913.35, f5)

# 6. Pozycja bez wczesniejszego wpisu bierze poziom brokera.
f6 = app.ceny_wejscia(sig(fills={}), [poz("AMD", 630.37)], E2T)
sprawdz("pierwsze wejscie bierze poziom brokera",
        f6["AMD"]["cena"] == 630.37 and "nowe" in f6["AMD"]["zrodlo"], f6)

# 7. Stop-loss tez liczy od odniesienia: MU -12% od 913,35 przebija 10%,
#    mimo ze od ostatniego wyrownania po 1000,00 spadek to tylko -3,7%.
s7 = sig(fills={"MU": {"cena": 913.35, "kierunek": "BUY",
                       "wersja": "2026-W4"}})
f7 = app.ceny_wejscia(s7, [poz("MU", 1000.0)], E2T)
traf = app.stopy_bezpieczenstwa([poz("MU", 1000.0)], f7, E2T,
                                FakeCap({"MU": 803.75}), pusty_rep())
sprawdz("stop-loss liczy od odniesienia, nie od ostatniego wyrownania",
        "MU" in traf, traf)


# ----------------------- prog oplacalnosci wyrownania -----------------------
# Kazde wyrownanie kosztuje pelny spread pozycji (zmierzone: 0,33% na SBUX,
# 0,31% na CMCSA, 11,82 USD w miesiac). Domyslne progi maja te drobne
# korekty odciac.
print("\nPROGI ANTY-CHURNOWE")
sprawdz("prog minimalnej wartosci wyrownania jest ustawiony",
        app.MIN_REBALANCE_ACC >= 25, app.MIN_REBALANCE_ACC)
sprawdz("dolne pasmo tolerancji podniesione z 0,12",
        app.REBALANCE_TOL_MIN >= 0.30, app.REBALANCE_TOL_MIN)
sprawdz("pasmo dolne nie przekracza gornego",
        app.REBALANCE_TOL_MIN <= app.REBALANCE_TOL)
sprawdz("wyrownywanie domyslnie tylko w jednym oknie doby",
        len([g for g in app.REBALANCE_HOURS.split(",") if g.strip()]) == 1,
        app.REBALANCE_HOURS)

# Straznik stopy depozytu: domyslnie nic nie zmienia (1.0 = zachowanie
# sprzed audytu), ale nizsza wartosc odrzuca niewiarygodny odczyt.
sprawdz("straznik stopy depozytu domyslnie nie zmienia zachowania",
        app.MARGIN_RATE_MAX == 1.0, app.MARGIN_RATE_MAX)
sprawdz("ostrzezenie o wieku koszyka wlaczone",
        app.ROTATION_MAX_DNI > 0, app.ROTATION_MAX_DNI)


# ---------------------- zrodlo uzytego depozytu (odczyt /run 29.09.2026) ----
# Pole "deposit" z API Capital.com nie zawsze znaczy depozyt zabezpieczajacy.
# Sprawdzamy obie metody na dwoch realnych odczytach z rachunku.
print("\nSTOPA DEPOZYTU — dwa zrodla, dwa realne odczyty")


def stopa(kapital, dostepne, deposit, ekspozycja, z_dostepnych):
    uzyty = (kapital - dostepne) if z_dostepnych else deposit
    return uzyty / ekspozycja


# Odczyt 29.09.2026: deposit == gotowka (kapital - wycena), wiec stopa z pola
# wychodzi absurdalne 89%; z dostepnych wychodzi 20%.
sprawdz("29.09: pole deposit daje bzdurne ~89%",
        abs(stopa(1057.73, 820.42, 1053.62, 1184.43, False) - 0.89) < 0.01)
sprawdz("29.09: kapital-dostepne daje 20%",
        abs(stopa(1057.73, 820.42, 1053.62, 1184.43, True) - 0.20) < 0.005)
# Odczyt 18.09.2026: oba zrodla sa zgodne — to wlasnie dlatego blad dlugo
# pozostawal niewidoczny.
sprawdz("18.09: oba zrodla zgodne co do 20%",
        abs(stopa(1041.61, 864.15, 177.45, 888.0, False)
            - stopa(1041.61, 864.15, 177.45, 888.0, True)) < 0.001)
sprawdz("18.09: kapital-dostepne tez daje 20%",
        abs(stopa(1041.61, 864.15, 177.45, 888.0, True) - 0.20) < 0.005)
# Domyslnie nic sie nie zmienia — wlaczenie ma byc swiadoma decyzja.
sprawdz("nowe zrodlo depozytu domyslnie WYLACZONE",
        app.MARGIN_FROM_AVAILABLE is False, app.MARGIN_FROM_AVAILABLE)


# ------------------ pozycje osierocone przez rotacje (odczyt /run 29.09) -----
# Rotacja czysci tactical; pozycja taktyczna spoza NDX-100 (wlasny epic)
# znikala botowi z oczu: nie byla zamykana, a kontrola kapitalu widziala ja
# jako obca i scinala ALLOC_PCT do ALLOC_PCT_SAFE. Ledger fills jest zapisem
# wlasnych pozycji bota - wszystko, co w nim jest, bot zna i moze zamknac.
print("\nOSIEROCONE POZYCJE — ledger fills wchodzi do managed")


def managed_z(sig):
    m = {e for e in sig["epics"].values() if e and not e.upper().startswith("UZUP")}
    for t in sig.get("tactical", []):
        e = (t.get("epic") or "").strip()
        if e: m.add(e)
    for t, f in (sig.get("fills") or {}).items():
        e = ((f or {}).get("epic") or sig["epics"].get(t) or t or "").strip()
        if e: m.add(e)
    return m


s_rot = sig(tactical=[], fills={"AKAM": {"cena": 116.41, "kierunek": "BUY",
                                          "wersja": "2026-W4", "epic": "AKAM"}})
sprawdz("AKAM po rotacji (tactical=[]) nadal w managed dzieki fills",
        "AKAM" in managed_z(s_rot))
s_stary = sig(tactical=[], fills={"AKAM": {"cena": 116.41, "kierunek": "BUY"}})
sprawdz("wpis fills bez pola epic mapuje sie przez ticker",
        "AKAM" in managed_z(s_stary))
s_brak = sig(tactical=[], fills={})
sprawdz("bez wpisu w fills obca pozycja NIE jest dotykana",
        "AKAM" not in managed_z(s_brak))
sprawdz("pozycje z NDX-100 nadal w managed niezaleznie od fills",
        "MU" in managed_z(s_brak))

# ------------------ REDUCE na pozycji z jednym lotem (STX, 2.10.2026) --------
print("\nREDUKCJA — reakcja nie znika w paśmie tolerancji")

cap = FakeCap({"STX": 849.10}, minimum=0.1)
stx = {"epic": "STX", "size": 0.1, "direction": "BUY"}
# cel po redukcji przy kapitale 1088 i ALLOC 0,12: ok. 65 USD
dec, size, opis = app.plan_redukcji(cap, stx, 1088 * 0.12 * 0.5, "USD")
sprawdz("STX 0,1 przy celu 65 USD: redukcja NIEWYKONALNA, nie cicha",
        dec == "niewykonalna" and size is None, (dec, size, opis))
stx2 = {"epic": "STX", "size": 0.2, "direction": "BUY"}
dec, size, _ = app.plan_redukcji(cap, stx2, 1092 * 0.24 * 0.5, "USD")
sprawdz("STX 0,2 po podwojeniu wolumenu: redukcja do 0,1",
        dec == "zmniejsz" and abs(size - 0.1) < 1e-9, (dec, size))
dec, size, _ = app.plan_redukcji(cap, {"epic": "STX", "size": 0.1,
                                       "direction": "BUY"},
                                 1092 * 0.24 * 0.5, "USD")
sprawdz("po redukcji kolejny bieg nie redukuje ponownie",
        dec == "zredukowana", dec)
cap = FakeCap({"ALAB": 350.0}, minimum=0.1)
dec, size, _ = app.plan_redukcji(cap, {"epic": "ALAB", "size": 0.4,
                                       "direction": "BUY"}, 65.0, "USD")
sprawdz("ALAB 0,4 przy celu 65 USD: redukcja do 0,2",
        dec == "zmniejsz" and abs(size - 0.2) < 1e-9, (dec, size))

# ------------------ zapis wykonania sygnałów do signals.json ----------------
print("\nWYKONANIE SYGNAŁÓW — rutyny wiedzą, co naprawdę się stało")
s_w = sig(exclude=[{"ticker": "MU", "action": "REDUCE", "basis": "news"}],
          tactical=[{"ticker": "VICR", "direction": "BUY", "epic": "VICR"}])
w = app.scal_wykonanie({}, {"reakcje": {"MU": "REDUCE wykonany"},
                            "taktyczne": {"VICR": "nieotwarta — min. wielkość"}},
                       s_w)
sprawdz("status reakcji i taktycznej zapisany",
        w["reakcje"].get("MU") == "REDUCE wykonany"
        and w["taktyczne"]["VICR"].startswith("nieotwarta"), w)
w2 = app.scal_wykonanie(w, {"reakcje": {}, "taktyczne": {
    "VICR": "nieotwarta — VICR: rynek zamknięty"}}, s_w)
sprawdz("weekendowy 'rynek zamknięty' nie nadpisuje statusu",
        w2["taktyczne"]["VICR"] == w["taktyczne"]["VICR"], w2)
w4 = app.scal_wykonanie(w, {"reakcje": {"MU": "REDUCE: pozycja na poziomie celu po redukcji (x)"},
                            "taktyczne": {}}, s_w)
sprawdz("raz wykonany REDUCE nie zmienia się w 'na poziomie celu'",
        w4["reakcje"]["MU"] == "REDUCE wykonany", w4)
w3 = app.scal_wykonanie(w, {"reakcje": {}, "taktyczne": {}}, sig())
sprawdz("po rotacji (puste exclude/tactical) wpisy znikają",
        w3["reakcje"] == {} and w3["taktyczne"] == {}, w3)

# ------------------ token biegu: nagłówek i maskowanie w logach -------------
print("\nTOKEN — nagłówek zamiast adresu, maskowanie w logach")
with app.app.test_request_context("/run", headers={"X-Run-Token": "test"}):
    sprawdz("token z nagłówka X-Run-Token akceptowany", app.auth_ok())
with app.app.test_request_context("/run?token=test"):
    sprawdz("token w adresie nadal działa (zgodność z cronem)", app.auth_ok())
with app.app.test_request_context("/run?token=zly"):
    sprawdz("zły token odrzucony", not app.auth_ok())
import logging  # noqa: E402
rec = logging.LogRecord("gunicorn.access", logging.INFO, "", 0,
                        '%s "%s"', ("10.0.0.1", "GET /run?token=tajny&x=1 HTTP/1.1"),
                        None)
app._MaskujToken().filter(rec)
sprawdz("token zamaskowany w logu dostępu",
        "tajny" not in rec.getMessage() and "token=***" in rec.getMessage(),
        rec.getMessage())


# ------------------ /status: pokrycie koszyka (tylko odczyt) ----------------
print("\nPOKRYCIE KOSZYKA — pole /status dla rutyn (12.10.2026)")
s_pk = sig(version="2026-W7", exclude=[{"ticker": "AVGO", "action": "CLOSE"},
                                        {"ticker": "MRVL", "action": "REDUCE"}],
           tactical=[{"ticker": "APOG", "direction": "BUY", "epic": "APOG"}])
poz_pk = [{"epic": "MU", "direction": "BUY", "size": 0.2},
          {"epic": "AMD", "direction": "BUY", "size": 0.3},
          {"epic": "MRVL", "direction": "BUY", "size": 0.5},
          {"epic": "SBUX", "direction": "SELL", "size": 2.2},
          {"epic": "APP", "direction": "SELL", "size": 0.8},
          {"epic": "APOG", "direction": "BUY", "size": 5.0},
          {"epic": "TER", "direction": "BUY", "size": 0.5},
          {"epic": "LITE", "direction": "SELL", "size": 0.2}]
pk = app.pokrycie_koszyka(s_pk, poz_pk)
sprawdz("nogi LONG: AVGO wykluczony nie liczy się, LITE SELL to nie noga BUY",
        pk["nogi_koszyka"] == 4 and pk["nogi_na_rachunku"] == 3
        and pk["brakujace"] == ["LITE"], pk)
sprawdz("wykluczone i zredukowane raportowane osobno",
        pk["wykluczone_przez_puls"] == ["AVGO"]
        and pk["zredukowane_przez_puls"] == ["MRVL"], pk)
sprawdz("koszyk SHORT w trybie classic: 2 z 5 nóg na rachunku",
        (pk["short"] or {}).get("nogi_koszyka") == 5
        and pk["short"]["nogi_na_rachunku"] == 2
        and set(pk["short"]["brakujace"]) == {"INTU", "CMCSA", "ADSK"}, pk)
sprawdz("taktyczna osobno, pozycja po rotacji jako spoza koszyka",
        pk["pozycje_taktyczne"] == ["APOG BUY 5.0"]
        and pk["pozycje_spoza_koszyka"] == ["TER BUY 0.5"], pk)
sprawdz("ticker bez epic liczony jako brakujący, nie wywala funkcji",
        "XYZ (brak epic)" in app.pokrycie_koszyka(
            sig(long=["MU", "XYZ"]), poz_pk)["brakujace"])
sprawdz("pusty rachunek: wszystkie nogi brakujące, bez wyjątku",
        app.pokrycie_koszyka(sig(), [])["nogi_na_rachunku"] == 0)


# ------------- PROCES v2 (18.10.2026): stop 15/10, pamięć stopu, próg miękki, kill ------------
print("\nPROCES v2 — stop asymetryczny, pamięć stopu, próg miękki, ślad kill switcha")
sprawdz("domyślne v2: ALLOC 0,08, SAFE 0,04, stop LONG 0,15 / SHORT 0,10, bez reopen, DD_SOFT 0,10/0,05, "
        "SOFT_PARY 2, KILL_RESUME 14, ALLOC_RESTART 0,04, taktyczne wyłączone, REDUCE_FALLBACK close",
        abs(app.ALLOC_PCT - 0.08) < 1e-12 and abs(app.ALLOC_PCT_SAFE - 0.04) < 1e-12
        and abs(app.STOP_LOSS_PCT_LONG - 0.15) < 1e-12 and abs(app.STOP_LOSS_PCT_SHORT - 0.10) < 1e-12
        and app.STOP_REOPEN is False and abs(app.DD_SOFT - 0.10) < 1e-12
        and abs(app.DD_SOFT_RESET - 0.05) < 1e-12 and app.SOFT_PARY == 2
        and app.KILL_RESUME_DAYS == 14 and abs(app.ALLOC_RESTART - 0.04) < 1e-12
        and app.TACTICAL_ENABLED is False and app.REDUCE_FALLBACK == "close")
poz_v2 = [{"epic": "STX", "direction": "BUY", "size": 0.1, "wejscie": 1000.0},
          {"epic": "AMD", "direction": "BUY", "size": 0.1, "wejscie": 1000.0},
          {"epic": "APP", "direction": "SELL", "size": 1.0, "wejscie": 100.0},
          {"epic": "SBUX", "direction": "SELL", "size": 1.0, "wejscie": 100.0}]
E2T_v2 = {t: t for t in ("STX", "AMD", "APP", "SBUX")}
cap_v2 = FakeCap({"STX": 870.0, "AMD": 840.0, "APP": 112.0, "SBUX": 108.0})
traf = app.stopy_bezpieczenstwa(poz_v2, {}, E2T_v2, cap_v2, pusty_rep())
sprawdz("stop asymetryczny: BUY -13% nie, BUY -16% tak; SELL +12% tak, SELL +8% nie",
        "STX" not in traf and "AMD" in traf and "APP" in traf and "SBUX" not in traf, traf)
sprawdz("opis stopu podaje próg i stronę",
        "STOP 15% (BUY)" in traf["AMD"] and "STOP 10% (SELL)" in traf["APP"], traf)
_sl = app.STOP_LOSS_PCT_LONG
app.STOP_LOSS_PCT_LONG = 0
traf = app.stopy_bezpieczenstwa(poz_v2, {}, E2T_v2, cap_v2, pusty_rep())
sprawdz("STOP_LOSS_PCT_LONG=0 wyłącza stop tylko dla BUY", "AMD" not in traf and "APP" in traf, traf)
app.STOP_LOSS_PCT_LONG = _sl
# pamięć stopu i próg miękki w książce docelowej
book, skipped, _ = app.desired_book(sig(), set(), set(), stopped={"MU"}, soft=False)
sprawdz("desired_book: noga zatrzymana stopem nie wraca (pominięta z opisem)",
        "MU" not in book and any("stop w tej wersji" in x for x in skipped), skipped)
book, skipped, _ = app.desired_book(sig(), set(), set(), soft=True)
sprawdz("desired_book: próg miękki pomija pierwsze 2 nogi long i 2 short, zostaje 6 nóg",
        set(book) == {"AVGO", "MRVL", "LITE", "CMCSA", "APP", "ADSK"}
        and sum("próg miękki" in x for x in skipped) == 4, sorted(book))
_so = app.SOFT_PARY
app.SOFT_PARY = 0
book, _, _ = app.desired_book(sig(), set(), set(), soft=True)
sprawdz("SOFT_PARY=0: próg miękki nic nie zamyka", len(book) == 10)
app.SOFT_PARY = _so
# scal_wykonanie: stopy tylko bieżącej wersji, soft i kill nigdy nie gubione
st = {"stopy": {"MU": {"wersja": "2026-W4", "data": "2026-10-20", "kierunek": "BUY", "opis": "x"},
                "AMD": {"wersja": "2026-W3", "data": "2026-10-13", "kierunek": "BUY", "opis": "y"}},
      "soft": {"aktywny": True, "od": "2026-10-19"},
      "kill": {"data": "2026-10-01", "wersja": "2026-W2"},
      "reakcje": {}, "taktyczne": {}}
w5 = app.scal_wykonanie(st, {"reakcje": {}, "taktyczne": {},
                             "stopy": {"LITE": {"wersja": "2026-W4", "data": "2026-10-21",
                                                "kierunek": "BUY", "opis": "z"}}}, sig())
sprawdz("scal_wykonanie: stopy = bieżąca wersja (MU) + nowy (LITE), stara wersja (AMD) znika; soft i kill przeniesione",
        set(w5["stopy"]) == {"MU", "LITE"} and w5["soft"]["aktywny"] is True
        and w5["kill"]["wersja"] == "2026-W2", w5)
w6 = app.scal_wykonanie(st, {"reakcje": {}, "taktyczne": {}, "stopy": {},
                             "soft": {"aktywny": False, "wylaczono": "2026-10-22"}}, sig(version="2026-W5"))
sprawdz("scal_wykonanie: po rotacji stopy puste, bieżący soft nadpisuje stary",
        w6["stopy"] == {} and w6["soft"]["aktywny"] is False, w6)
w7 = app.scal_wykonanie({"reakcje": {}, "taktyczne": {}}, {"reakcje": {}, "taktyczne": {}, "stopy": {}}, sig())
sprawdz("scal_wykonanie: bez stopów/soft/kill nie dopisuje kluczy (brak zbędnego commitu)",
        "stopy" not in w7 and "soft" not in w7 and "kill" not in w7, w7)
# histereza progu miękkiego
ak, wpis = app.stan_progu_miekkiego(None, 0.09, "2026-10-20", "2026-W9")
sprawdz("próg miękki: dd 9% < 10% → nieaktywny, bez wpisu", ak is False and wpis is None)
ak, wpis = app.stan_progu_miekkiego(None, 0.11, "2026-10-20", "2026-W9")
sprawdz("próg miękki: dd 11% → włączony z wpisem",
        ak is True and wpis["aktywny"] and wpis["dd_start"] == 0.11 and wpis["pary"] == 2, wpis)
ak, wpis2 = app.stan_progu_miekkiego(wpis, 0.07, "2026-10-21", "2026-W9")
sprawdz("próg miękki: dd 7% (między 5 a 10) → zostaje włączony, bez nowego wpisu", ak is True and wpis2 is None)
ak, wpis3 = app.stan_progu_miekkiego(wpis, 0.04, "2026-10-22", "2026-W9")
sprawdz("próg miękki: dd 4% < 5% → wyłączony z wpisem",
        ak is False and wpis3["aktywny"] is False and wpis3["wylaczono"] == "2026-10-22", wpis3)
_dd = app.DD_SOFT
app.DD_SOFT = 0
ak, wpis4 = app.stan_progu_miekkiego(wpis, 0.3, "2026-10-22", "2026-W9")
sprawdz("DD_SOFT=0: aktywny próg zostaje wyłączony, nieaktywny bez wpisu",
        ak is False and wpis4["aktywny"] is False
        and app.stan_progu_miekkiego(None, 0.3, "2026-10-22", "2026-W9") == (False, None))
app.DD_SOFT = _dd
# wznowienie po kill switchu
ki = {"data": "2026-10-20", "wersja": "2026-W9", "szczyt": 1.0, "prog": 0.75, "kapital": 0.74}
sprawdz("wznowienie: za wcześnie (13 dni) → nie", app.decyzja_wznowienia(ki, "2026-W11", "2026-11-02")[0] is False)
sprawdz("wznowienie: 14 dni, ale ta sama wersja → nie", app.decyzja_wznowienia(ki, "2026-W9", "2026-11-03")[0] is False)
wz, ki2 = app.decyzja_wznowienia(ki, "2026-W11", "2026-11-03")
sprawdz("wznowienie: 14 dni i nowa wersja → tak; wpis dostaje wznowiono/wersja_wznowienia/dni_plasko",
        wz is True and ki2["wznowiono"] == "2026-11-03" and ki2["wersja_wznowienia"] == "2026-W11"
        and ki2["dni_plasko"] == 14 and "wznowiono" not in ki, ki2)
sprawdz("wznowienie: wpis już wznowiony nie wznawia ponownie", app.decyzja_wznowienia(ki2, "2026-W12", "2026-12-01")[0] is False)
sprawdz("wznowienie: brak śladu kill → nie", app.decyzja_wznowienia(None, "2026-W12", "2026-12-01") == (False, {}))
_kr = app.KILL_RESUME_DAYS
app.KILL_RESUME_DAYS = 0
sprawdz("KILL_RESUME_DAYS=0 wyłącza wznowienie", app.decyzja_wznowienia(ki, "2026-W11", "2026-12-03")[0] is False)
app.KILL_RESUME_DAYS = _kr
# pokrycie_koszyka: zatrzymane stopem i próg miękki nie są „brakujące"
s_v2 = sig(version="2026-W9",
           wykonanie={"stopy": {"MU": {"wersja": "2026-W9", "data": "2026-10-20", "kierunek": "BUY", "opis": "x"},
                                "AMD": {"wersja": "2026-W8", "data": "2026-10-13", "kierunek": "BUY", "opis": "y"}},
                      "soft": {"aktywny": True}})
pk2 = app.pokrycie_koszyka(s_v2, [{"epic": "AVGO", "direction": "BUY", "size": 0.1},
                                  {"epic": "MRVL", "direction": "BUY", "size": 0.1},
                                  {"epic": "LITE", "direction": "BUY", "size": 0.1},
                                  {"epic": "CMCSA", "direction": "SELL", "size": 1},
                                  {"epic": "APP", "direction": "SELL", "size": 1},
                                  {"epic": "ADSK", "direction": "SELL", "size": 1}])
sprawdz("pokrycie v2: MU zatrzymany (ta wersja), MU/AMD i INTU/SBUX zamknięte progiem miękkim — nie brakujące; AMD ze starej wersji nie jest zatrzymany",
        pk2["zatrzymane_stopem"] == ["MU"] and pk2["zamkniete_progiem_miekkim"] == ["AMD", "MU"]
        and pk2["nogi_koszyka"] == 3 and pk2["brakujace"] == []
        and pk2["short"]["zamkniete_progiem_miekkim"] == ["INTU", "SBUX"] and pk2["short"]["brakujace"] == []
        and pk2["prog_miekki_aktywny"] is True, pk2)
pk_smieci = app.pokrycie_koszyka(sig(version="2026-W9", wykonanie={"stopy": ["MU"], "soft": "tak", "kill": 5}), [])
sprawdz("śmieci w wykonanie (lista/tekst/liczba) nie wywracają pokrycia ani scalania ani decyzji",
        pk_smieci["zatrzymane_stopem"] == [] and pk_smieci["prog_miekki_aktywny"] is False
        and app.scal_wykonanie({"stopy": ["MU"], "soft": "tak", "kill": 5, "reakcje": {}, "taktyczne": {}},
                               {"reakcje": {}, "taktyczne": {}, "stopy": {}}, sig()).get("soft") is None
        and app.decyzja_wznowienia("x", "2026-W9", "2026-11-01") == (False, {})
        and app.stan_progu_miekkiego(["x"], 0.2, "2026-11-01", "2026-W9")[0] is True)
pk3 = app.pokrycie_koszyka(sig(version="2026-W9", wykonanie={"stopy": {"MU": {"wersja": "2026-W9"}}}), [])
sprawdz("pokrycie v2: bez progu miękkiego i z 1 stopem — 4 nogi LONG brakujące, MU osobno",
        pk3["nogi_koszyka"] == 4 and len(pk3["brakujace"]) == 4 and pk3["zatrzymane_stopem"] == ["MU"]
        and pk3["prog_miekki_aktywny"] is False, pk3)

# -------------------------------------------- walidator i tv_porownaj -------
print("\nWALIDATOR signals.json I SKRYPT PORÓWNAWCZY TV (bez sieci)")
import copy
import json
import subprocess
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = [sys.executable, "-I"]


def _pelny(**kw):
    """Pełny plik signals.json (15 kluczy) do testów walidatora."""
    s = sig()
    s.update({"_instrukcja": "test", "d0": {"date": "2026-10-09", "ndx": 30000.0,
                                             "prices": {t: 100.0 for t in s["long"] + s["short"]}},
              "equity_peak": 1000.0, "exclude": [], "fills": {"MU": {"cena": 913.35}},
              "generated": "2026-10-10", "history": [{"week": "2026-W6", "spread_pp": 1.0,
                                                      "spread_fills_pp": 0.5, "hit_top": "3/5",
                                                      "hit_bottom": "2/5", "tactical_pp": None,
                                                      "managed_pp": 1.0, "reaction_pp": 0.0,
                                                      "rezim": "P0"}],
              "last_daily": "2026-10-09", "status": "AKTUALNA", "tactical": [],
              "version": "2026-W7", "wykonanie": {"reakcje": {}, "taktyczne": {}}})
    s.update(kw)
    return s


def waliduj(baza, nowy, rutyna, extra=()):
    with tempfile.TemporaryDirectory() as d:
        pb, pn = os.path.join(d, "baza.json"), os.path.join(d, "nowy.json")
        json.dump(baza, open(pb, "w")); json.dump(nowy, open(pn, "w"))
        out = subprocess.run(PY + [os.path.join(REPO, "scripts", "waliduj_signals.py"),
                                   "--base", pb, "--plik", pn, "--rutyna", rutyna] + list(extra),
                             capture_output=True, text=True)
        return out.returncode, out.stdout


baza = _pelny()
kod, _ = waliduj(baza, baza, "puls")
sprawdz("walidator: plik bez zmian przechodzi", kod == 0)
n = copy.deepcopy(baza); n["status"] = "NIEAKTUALNA"; n["last_daily"] = "2026-10-12"
n["exclude"] = [{"ticker": "MU", "action": "REDUCE", "basis": "news",
                 "reason": "x", "date": "2026-10-12"}]
kod, _ = waliduj(baza, n, "puls")
sprawdz("walidator: puls zmienia status/exclude/last_daily — OK", kod == 0)
n = copy.deepcopy(baza); n["fills"]["MU"]["cena"] = 1.0
kod, out = waliduj(baza, n, "puls")
sprawdz("walidator: zmiana fills jest odrzucana", kod == 1 and "fills" in out)
n = copy.deepcopy(baza); n["data_quality"] = ["X"]
kod, out = waliduj(baza, n, "puls")
sprawdz("walidator: obcy klucz top-level jest odrzucany", kod == 1 and "OBCE" in out)
n = copy.deepcopy(baza); n["long"] = ["AVGO", "LITE", "MRVL", "PANW", "CSCO"]
kod, _ = waliduj(baza, n, "puls")
sprawdz("walidator: puls nie może zmienić koszyka", kod == 1)
n = copy.deepcopy(baza); n["exclude"] = [{"ticker": "MU", "action": "REDUCE", "basis": "news"}]
kod, out = waliduj(baza, n, "puls")
sprawdz("walidator: wpis exclude bez reason/date jest odrzucany", kod == 1 and "reason" in out)
sob = copy.deepcopy(baza)
nowy_long = [t for t in sob["epics"] if t not in sob["short"]][:5]
sob.update({"version": "2026-W8", "status": "AKTUALNA", "generated": "2026-10-17",
            "long": nowy_long, "short": sob["short"],
            "d0": {"date": "2026-10-16", "ndx": 30500.0,
                   "prices": {t: 100.0 for t in nowy_long + sob["short"]}}})
sob["history"] = baza["history"] + [{"week": "2026-W7", "spread_pp": 0.2, "spread_fills_pp": 0.1,
                                     "hit_top": "2/5", "hit_bottom": "3/5", "tactical_pp": None,
                                     "managed_pp": 0.2, "reaction_pp": 0.0, "rezim": "P0"}]
kod, out = waliduj(baza, sob, "sobota")
sprawdz("walidator: rotacja sobotnia z nowym d0 i wpisem history — OK", kod == 0, out)
kod, _ = waliduj(baza, sob, "puls")
sprawdz("walidator: ta sama rotacja jako puls jest odrzucana", kod == 1)
n = copy.deepcopy(sob); n["history"][-1].pop("spread_fills_pp")
kod, out = waliduj(baza, n, "sobota")
sprawdz("walidator: wpis history bez spread_fills_pp jest odrzucany", kod == 1 and "spread_fills_pp" in out)
n = copy.deepcopy(sob); n["history"] = baza["history"]
kod, out = waliduj(baza, n, "sobota")
sprawdz("walidator: rotacja bez wpisu history przechodzi (bieg przy NIEAKTUALNA bez d0)",
        kod == 0, out)
n = copy.deepcopy(sob); n["d0"] = baza["d0"]
kod, out = waliduj(baza, n, "sobota")
sprawdz("walidator: nowa version bez nowego d0 jest odrzucana", kod == 1 and "d0" in out)
n = copy.deepcopy(sob); n["epics"] = {k: v for k, v in sob["epics"].items() if k != "MU"}
kod, out = waliduj(baza, n, "sobota")
sprawdz("walidator: usunięcie spółki z epics jest odrzucane", kod == 1 and "epics" in out)
n = copy.deepcopy(sob); n["equity_peak"] = 1.0
kod, out = waliduj(baza, n, "sobota")
sprawdz("walidator: equity_peak nie wolno ruszać sobocie", kod == 1 and "equity_peak" in out)

# proces v2 (18.10.2026): history przy 26 wpisach, reguły Pulsu
baza26 = copy.deepcopy(baza)
baza26["history"] = [dict(baza["history"][0], week=f"2026-W{i}") for i in range(26)]
sob26 = copy.deepcopy(sob)
sob26["history"] = (baza26["history"] + [dict(sob["history"][-1], week=baza26["version"])])[-26:]
kod, out = waliduj(baza26, sob26, "sobota")
sprawdz("walidator: przy 26 wpisach history dopisanie + obcięcie do 26 OSTATNICH przechodzi", kod == 0, out)
n = copy.deepcopy(sob26); n["history"] = baza26["history"] + [sob26["history"][-1]]
kod, out = waliduj(baza26, n, "sobota")
sprawdz("walidator: 27 wpisów history jest odrzucane", kod == 1 and "history" in out)
n = copy.deepcopy(sob26); n["history"] = baza26["history"][:5] + baza26["history"][6:] + [sob26["history"][-1]]
kod, out = waliduj(baza26, n, "sobota")
sprawdz("walidator: usunięcie wpisu ze środka history jest odrzucane", kod == 1 and "history" in out)
n = copy.deepcopy(baza); n["last_daily"] = "2026-10-12"
n["exclude"] = [{"ticker": "MU", "action": "REDUCE", "basis": "cena", "reason": "x", "date": "2026-10-12"}]
kod, out = waliduj(baza, n, "puls")
sprawdz("walidator v2: nowy wpis exclude o basis=cena jest odrzucany", kod == 1 and "v2" in out)
kod, out = waliduj(baza, n, "puls", ["--v1"])
sprawdz("walidator: ten sam wpis z --v1 (starsza rutyna) przechodzi", kod == 0, out)
n = copy.deepcopy(baza); n["last_daily"] = "2026-10-12"
n["tactical"] = [{"ticker": "GNRC", "direction": "BUY", "epic": "GNRC", "entry_date": "2026-10-12", "reason": "x"}]
kod, out = waliduj(baza, n, "puls")
sprawdz("walidator v2: puls z pozycją taktyczną jest odrzucany", kod == 1 and "tactical" in out)
kod, out = waliduj(baza, n, "puls", ["--v1"])
sprawdz("walidator: taktyczna z --v1 przechodzi", kod == 0, out)

# tv_porownaj — fixture z kształtami odpowiedzi narzędzi z 12.10.2026
with tempfile.TemporaryDirectory() as d:
    def zapisz(nazwa, obj):
        p = os.path.join(d, nazwa); json.dump(obj, open(p, "w")); return p
    sygn = zapisz("signals.json", _pelny())
    kursy = zapisz("kursy.json", {"kursy": {
        "MU": {"data": "2026-10-09", "close": 1029.0}, "LITE": {"data": "2026-10-09", "close": 200.0},
        "NDX100": {"data": "2026-10-09", "close": 30863.68}, "AAPL": {"data": "2026-10-09", "close": 336.6}}})
    batch = zapisz("batch.json", {"success": True, "count": 3, "data": {
        "NASDAQ:MU": {"name": "MU", "close": 1029.5, "change": 1.2, "industry": "Semiconductors",
                      "sector": "Electronic Technology", "update_mode": "streaming"},
        "NASDAQ:LITE": {"name": "LITE", "close": 202.0, "change": -3.0, "industry": "Telecommunications Equipment",
                        "sector": "Electronic Technology", "update_mode": "streaming"},
        "NASDAQ:AAPL": {"name": "AAPL", "close": 336.6, "change": 0.0, "industry": "Telecommunications Equipment",
                        "sector": "Electronic Technology", "update_mode": "delayed_streaming_900"}},
        "missing": [{"symbol": "NASDAQ:XYZ", "reason": "Quote data not found"}], "missing_count": 1})
    # świece: 9.10 (piątek, 13:30 UTC) i 12.10 (poniedziałek, niedokończona)
    ohlcv = zapisz("ndx.json", {"symbol": "NASDAQ:NDX", "bars": [
        {"t": 1791466200, "c": 30500.0}, {"t": 1791552600, "c": 30863.68}, {"t": 1791811800, "c": 30600.0}]})
    scr = zapisz("spx.json", {"data": {"rows": [
        {"symbol": f"NYSE:S{i}", "name": f"S{i}", "industry": "Telecommunications Equipment", "change": -4.0 - i}
        for i in range(5)] + [{"symbol": "NASDAQ:MU", "name": "MU", "industry": "Semiconductors", "change": 1.2}],
        "totalCount": 6}})
    sym = zapisz("tv-symbole.json", {"koszyk": {"MU": "NASDAQ:MU", "LITE": "NASDAQ:LITE", "AAPL": "NASDAQ:AAPL"},
                                     "taktyczne": {}, "_indeks": "NASDAQ:NDX", "_vix": "CBOE:VIX"})
    log = os.path.join(d, "tv-log.jsonl")
    out = subprocess.run(PY + [os.path.join(REPO, "scripts", "tv_porownaj.py"), "--tv", batch,
                               "--ohlcv", ohlcv, "--kursy", kursy, "--screener", scr, "--d0", sygn,
                               "--symbole", sym, "--teraz-utc", "2026-10-12T12:30", "--log", log,
                               "--rutyna", "puls-ndx", "--wywolania", "5", "--czas-s", "60"],
                         capture_output=True, text=True)
    t = out.stdout
    sprawdz("tv_porownaj: kończy się kodem 0", out.returncode == 0, out.stderr[-300:])
    sprawdz("tv_porownaj: MU zgodne (0,05% = bez adnotacji), LITE rozjazd 1% oznaczony",
            "LITE" in t.split("|Δ| > 0,5% (ROZJAZD): ")[1].splitlines()[0]
            and "MU" not in t.split("|Δ| > 0,1%: ")[1].splitlines()[0], t)
    sprawdz("tv_porownaj: niedokończona świeca 12.10 odrzucona, NDX z 9.10 zgodny co do grosza",
            "NDX100" in t and "+0.00" in t, t)
    sprawdz("tv_porownaj: missing z odpowiedzi trafia do raportu", "NASDAQ:XYZ" in t)
    sprawdz("tv_porownaj: mediana branży LITE n=5 < −3% → TV dałby blokadę; MU n<4",
            "n=5" in t and "BLOKADĘ" in t and "za mało spółek" in t, t)
    wiersz = json.loads(open(log).read().strip().splitlines()[-1])
    sprawdz("tv_porownaj: wiersz logu bez liczb z rachunku, z rozjazdami i stanem",
            wiersz["rozjazdy_gt_0_5"] == ["LITE"] and wiersz["stan"] == "OK"
            and not any(k in wiersz for k in ("kapital", "equity", "upl")), wiersz)

# konfiguracja TV w repo musi być poprawnym JSON i spójna z epics
for plik in ("data/tv-config.json", "data/tv-symbole.json", "data/tv-kolumny.json", "rutyny/tv-zestaw-b1.json"):
    try:
        json.load(open(os.path.join(REPO, plik), encoding="utf-8"))
        sprawdz(f"{plik} to poprawny JSON", True)
    except (OSError, ValueError) as e:
        sprawdz(f"{plik} to poprawny JSON", False, str(e))
try:
    _sym = json.load(open(os.path.join(REPO, "data", "tv-symbole.json"), encoding="utf-8"))
    _sig = json.load(open(os.path.join(REPO, "signals.json"), encoding="utf-8"))
    _kol = json.load(open(os.path.join(REPO, "data", "tv-kolumny.json"), encoding="utf-8"))["kolumny"]
    _b1 = json.load(open(os.path.join(REPO, "rutyny", "tv-zestaw-b1.json"), encoding="utf-8"))["kolumny"]
    sprawdz("tv-symbole.json pokrywa wszystkie klucze epics",
            set(_sig["epics"]) <= set(_sym["koszyk"]), sorted(set(_sig["epics"]) - set(_sym["koszyk"])))
    sprawdz("tv-zestaw-b1.json używa tylko kolumn z tv-kolumny.json",
            set(_b1) <= set(_kol), sorted(set(_b1) - set(_kol)))
except (OSError, ValueError, KeyError) as e:
    sprawdz("pliki TV spójne", False, str(e))


print(f"\n{'=' * 52}")
print(f"przeszło: {_wynik['ok']}   nie przeszło: {_wynik['zle']}")
print("=" * 52)
sys.exit(1 if _wynik["zle"] else 0)
