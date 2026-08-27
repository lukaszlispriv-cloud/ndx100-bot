#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kursy.py — zamknięcia NASDAQ/NYSE dla systemu NDX100 (Yahoo chart API).

Użycie (w katalogu repo):  python3 scripts/kursy.py [--json]

Co robi:
1. Pobiera dzienne świece z query2.finance.yahoo.com (v8/finance/chart)
   dla wszystkich spółek z mapy epics w signals.json (tickery amerykańskie,
   bez sufiksu) oraz indeksu Nasdaq-100 (^NDX).
2. Do tabel podaje zamknięcie OSTATNIEJ ZAKOŃCZONEJ sesji: jeśli dziś
   jest dzień sesyjny, a zegar (Europe/Warsaw) nie minął 17:10, ostatnia
   świeca (dzisiejsza, niedokończona) jest odrzucana.
3. WALIDACJA D0: jeżeli w katalogu bieżącym lub nadrzędnym jest
   signals.json, porównuje zamknięcia z dnia d0.date z d0.prices
   (tolerancja 0,5%) i raportuje OK / RÓŻNICA / BRAK.
4. Symbole-kandydaci: dla spółek o niepewnym kodzie próbuje kolejno
   kilku symboli; braki wypisuje jawnie — wtedy użyj rezerwy (Stooq/PAP)
   i oznacz źródło w raporcie.

Wyjście: czytelna tabela; z flagą --json — struktura maszynowa.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
WAW = NY  # zgodność nazw w dalszym kodzie: „zegar rynku"
KONIEC_SESJI = (16, 10)          # 16:10 czasu Nowego Jorku = sesja zakończona
TOLERANCJA_D0 = 0.005            # 0,5%

# Uniwersum czytane z signals.json (epics) — tu tylko indeks i ewentualne wyjątki
SYMBOLE = {"NDX100": ["^NDX"], "VIX": ["^VIX"]}
URL = ("https://{host}/v8/finance/chart/{sym}"
       "?range=15d&interval=1d")
HOSTY = ("query1.finance.yahoo.com", "query2.finance.yahoo.com")
PAUZA = 0.7                      # throttling — Yahoo zwraca 429 przy salwie zapytań
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def pobierz(sym):
    """Zwraca listę (data 'YYYY-MM-DD', close) albo [] przy braku danych."""
    dane, blad = None, None
    for proba in range(4):
        host = HOSTY[proba % len(HOSTY)]
        req = urllib.request.Request(URL.format(host=host, sym=sym),
                                     headers={"User-Agent": UA})
        try:
            time.sleep(PAUZA)
            with urllib.request.urlopen(req, timeout=20) as r:
                dane = json.load(r)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                json.JSONDecodeError, OSError) as e:
            blad = f"błąd sieci/odpowiedzi: {e}"
            if proba < 3:
                time.sleep(2 * (proba + 1))
    if dane is None:
        return [], blad
    try:
        res = dane["chart"]["result"][0]
        ts = res["timestamp"]
        closes = res["indicators"]["quote"][0]["close"]
    except (KeyError, IndexError, TypeError):
        return [], "brak danych w odpowiedzi"
    bary = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(WAW)
        bary.append((d.strftime("%Y-%m-%d"), round(float(c), 4)))
    return bary, None


def ostatnia_zakonczona(bary, teraz=None):
    """(data, close, poprz_data, poprz_close) ostatniej ZAKOŃCZONEJ sesji."""
    if not bary:
        return None
    teraz = teraz or datetime.now(WAW)
    dzis = teraz.strftime("%Y-%m-%d")
    po_sesji = (teraz.hour, teraz.minute) >= KONIEC_SESJI
    if bary[-1][0] == dzis and not po_sesji:
        bary = bary[:-1]
    if not bary:
        return None
    d, c = bary[-1]
    pd, pc = bary[-2] if len(bary) >= 2 else (None, None)
    return d, c, pd, pc


def znajdz_signals():
    for p in ("signals.json", os.path.join("..", "signals.json")):
        if os.path.exists(p):
            try:
                return json.load(open(p, encoding="utf-8")), p
            except json.JSONDecodeError:
                pass
    return None, None


def rezim_rynkowy():
    """POZIOM 0/1/2 wg prerejestrowanych progów (ochrona przed korektą/bessą).

    Dane: ^NDX 1 rok (MA200, MA50, drawdown od 52-tyg. szczytu) + ^VIX.
    P1: NDX<MA200 LUB drawdown>10% LUB VIX>28  →  gross 50%, taktyczne OFF
    P2: drawdown>20% LUB VIX>40 LUB sesja<=-5%  →  portfel płasko (NIEAKTUALNA)
    Powroty (histereza, decyduje rutyna tygodniowa):
    P2->handel: 5 kolejnych sesji VIX<25 ORAZ NDX>MA50
    P1->P0:     3 kolejne sesje  VIX<22 ORAZ NDX>MA200
    """
    ndx, e1 = pobierz("^NDX?zakres=1y".split("?")[0])  # symbol; zakres niżej
    # osobne pobranie rocznej serii (range=1y)
    import urllib.request as _u
    req = _u.Request(URL.format(host=HOSTY[0], sym="^NDX")
                     .replace("range=15d", "range=1y"),
                     headers={"User-Agent": UA})
    try:
        time.sleep(PAUZA)
        with _u.urlopen(req, timeout=25) as r:
            dane = json.load(r)
        res = dane["chart"]["result"][0]
        pary = [(t, c) for t, c in zip(res["timestamp"],
                res["indicators"]["quote"][0]["close"]) if c is not None]
        zamk = [c for _, c in pary]
    except Exception as e:
        return {"blad": f"brak danych ^NDX 1y: {e}"}
    vix, _ = pobierz("^VIX")
    v = vix[-1][1] if vix else None
    if len(zamk) < 60:
        return {"blad": "za krótka historia ^NDX"}
    c = zamk[-1]
    ma200 = sum(zamk[-200:]) / min(200, len(zamk))
    ma50 = sum(zamk[-50:]) / 50
    szczyt = max(zamk)
    dd = (c / szczyt - 1) * 100
    sesja = (c / zamk[-2] - 1) * 100 if len(zamk) >= 2 else 0.0
    poziom = 0
    powody = []
    if c < ma200: poziom, _p = 1, powody.append(f"NDX {c:.0f} < MA200 {ma200:.0f}")
    if dd < -10:  poziom = max(poziom, 1); powody.append(f"drawdown {dd:.1f}% > 10%")
    if v and v > 28: poziom = max(poziom, 1); powody.append(f"VIX {v:.1f} > 28")
    if dd < -20:  poziom = 2; powody.append(f"drawdown {dd:.1f}% > 20%")
    if v and v > 40: poziom = 2; powody.append(f"VIX {v:.1f} > 40")
    if sesja <= -5: poziom = 2; powody.append(f"sesja {sesja:.1f}% <= -5%")
    return {"poziom": poziom, "ndx": round(c, 1), "ma200": round(ma200, 1),
            "ma50": round(ma50, 1), "drawdown_pct": round(dd, 2),
            "sesja_pct": round(sesja, 2), "vix": v,
            "powody": powody or ["brak przesłanek — POZIOM 0"],
            "vix_lt25_i_ndx_gt_ma50": bool(v and v < 25 and c > ma50),
            "vix_lt22_i_ndx_gt_ma200": bool(v and v < 22 and c > ma200)}


def zbuduj_symbole(sig):
    """Uniwersum = klucze epics; symbol Yahoo = ticker (akcje USA bez sufiksu)."""
    for t in (sig or {}).get("epics", {}):
        SYMBOLE.setdefault(t, [t])


def main():
    tryb_json = "--json" in sys.argv
    sig, sig_path = znajdz_signals()
    zbuduj_symbole(sig)
    d0 = (sig or {}).get("d0") or {}
    d0_date = d0.get("date")
    d0_prices = d0.get("prices") or {}

    wynik, problemy = {}, []
    for ticker, kandydaci in SYMBOLE.items():
        bary, blad, uzyty = [], "nie próbowano", None
        for sym in kandydaci:
            bary, blad = pobierz(sym)
            if bary:
                uzyty = sym
                break
        if not bary:
            problemy.append(f"{ticker}: brak danych ({', '.join(kandydaci)}; "
                            f"{blad}) — użyj rezerwy (Stooq/PAP) i oznacz źródło")
            continue
        oz = ostatnia_zakonczona(bary)
        if not oz:
            problemy.append(f"{ticker}: brak zakończonej sesji w danych")
            continue
        d, c, pd, pc = oz
        dd = round((c / pc - 1) * 100, 2) if pc else None
        # walidacja D0
        d0_close = dict(bary).get(d0_date) if d0_date else None
        ref = d0_prices.get(ticker)
        if ticker == "WIG20" and sig:
            ref = (sig.get("d0") or {}).get("wig20")
        if ref and d0_close:
            odch = abs(d0_close / float(ref) - 1)
            d0_status = ("OK" if odch <= TOLERANCJA_D0
                         else f"RÓŻNICA {odch*100:.2f}% (Yahoo {d0_close} vs D0 {ref})")
        elif ref:
            d0_status = "BRAK świecy z D0 w Yahoo"
        else:
            d0_status = "—"
        wynik[ticker] = {"symbol": uzyty, "data": d, "close": c,
                         "poprzednia": pd, "zmiana_dd_pct": dd,
                         "walidacja_d0": d0_status}

    rezim = rezim_rynkowy()

    if tryb_json:
        print(json.dumps({"wygenerowano": datetime.now(WAW).isoformat(timespec="minutes"),
                          "d0": d0_date, "signals": sig_path,
                          "kursy": wynik, "rezim": rezim, "problemy": problemy},
                         ensure_ascii=False, indent=2))
        return

    print("REŻIM RYNKOWY:", json.dumps(rezim, ensure_ascii=False))
    print(f"KURSY GPW — ostatnia zakończona sesja (stan: "
          f"{datetime.now(WAW).strftime('%Y-%m-%d %H:%M')} CET/CEST)")
    if sig_path:
        print(f"Walidacja D0 ({d0_date}) względem {sig_path}, tolerancja "
              f"{TOLERANCJA_D0*100:.1f}%")
    print(f"{'TICKER':10} {'SYMBOL':9} {'SESJA':11} {'CLOSE':>10} "
          f"{'d/d %':>7}  WALIDACJA D0")
    for t, w in wynik.items():
        dd = f"{w['zmiana_dd_pct']:+.2f}" if w["zmiana_dd_pct"] is not None else "b.d."
        print(f"{t:10} {w['symbol']:9} {w['data']:11} {w['close']:>10} "
              f"{dd:>7}  {w['walidacja_d0']}")
    if problemy:
        print("\nPROBLEMY:")
        for p in problemy:
            print(" -", p)
    rozjazdy = [t for t, w in wynik.items()
                if w["walidacja_d0"].startswith("RÓŻNICA")]
    if rozjazdy:
        print(f"\nUWAGA: rozjazd z d0.prices dla: {', '.join(rozjazdy)} — "
              f"sprawdź symbol/split/dywidendę zanim użyjesz tych kursów.")


if __name__ == "__main__":
    main()
