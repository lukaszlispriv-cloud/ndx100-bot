#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kursy.py — zamknięcia NASDAQ/NYSE dla systemu NDX100 (Yahoo chart/spark API).

Użycie (w katalogu repo):  python3 scripts/kursy.py [--json]

Co robi:
1. Pobiera dzienne świece dla wszystkich spółek z mapy epics w signals.json
   (tickery amerykańskie, bez sufiksu) oraz ^NDX i ^VIX.
   ODPORNOŚĆ NA LIMIT ZAPYTAŃ (HTTP 429):
   * endpoint batchowy v7/finance/spark — do 20 tickerów NA JEDNO zapytanie
     (cały bieg to ~7 zapytań zamiast ~104, co wcześniej wyzwalało blokadę
     Yahoo na 30-60 min);
   * pauza między zapytaniami (KURSY_PAUZA, domyślnie 2 s), rotacja hostów
     query1/query2 i wykładniczy backoff przy 429 (45/90/180 s);
   * cache odpowiedzi na dysku (TTL KURSY_CACHE_TTL, domyślnie 20 min) —
     ponowny bieg w krótkim odstępie nie zużywa limitu;
   * fallback: pojedyncze v8/finance/chart, gdy spark zawiedzie.
   Uwaga na środowisko z proxy egress: z serwisów notowań przepuszczane jest
   wyłącznie *.finance.yahoo.com — Stooq/FRED/CBOE/StockAnalysis są tam
   zablokowane, więc jedyną realną rezerwą pozostają depesze agencyjne
   (oznacz źródło w raporcie).
2. Do tabel podaje zamknięcie OSTATNIEJ ZAKOŃCZONEJ sesji: jeśli dziś
   jest dzień sesyjny, a zegar (America/New_York) nie minął 16:10, ostatnia
   świeca (dzisiejsza, niedokończona) jest odrzucana.
3. WALIDACJA D0: jeżeli w katalogu bieżącym lub nadrzędnym jest
   signals.json, porównuje zamknięcia z dnia d0.date z d0.prices
   (tolerancja 0,5%) i raportuje OK / RÓŻNICA / BRAK. d0 == null (koszyki
   nieaktywowane) jest obsługiwane i pomija walidację.

Wyjście: czytelna tabela; z flagą --json — struktura maszynowa.
"""
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
KONIEC_SESJI = (16, 10)          # 16:10 czasu Nowego Jorku = sesja zakończona
TOLERANCJA_D0 = 0.005            # 0,5%

# Uniwersum czytane z signals.json (epics) — tu tylko indeksy
SYMBOLE = {"NDX100": ["^NDX"], "VIX": ["^VIX"]}
HOSTY = ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

PAUZA = float(os.environ.get("KURSY_PAUZA", "2"))          # s między zapytaniami
CACHE_TTL = int(os.environ.get("KURSY_CACHE_TTL", "1200"))  # s ważności cache
BATCH = 20                       # tickerów na jedno zapytanie spark
_ostatnie_zapytanie = [0.0]


def _cache_sciezka(url):
    kat = os.path.join(tempfile.gettempdir(), "kursy-cache")
    os.makedirs(kat, exist_ok=True)
    return os.path.join(kat, hashlib.sha1(url.encode()).hexdigest() + ".json")


def http_json(sciezka_url):
    """GET JSON z Yahoo: cache -> pauza -> rotacja hostów -> backoff na 429.

    Zwraca (dane, None) albo (None, opis_błędu).
    """
    plik = _cache_sciezka(sciezka_url)
    try:
        if os.path.exists(plik) and time.time() - os.path.getmtime(plik) < CACHE_TTL:
            return json.load(open(plik, encoding="utf-8")), None
    except (OSError, json.JSONDecodeError):
        pass
    blad = "nie próbowano"
    for proba in range(3):
        host = HOSTY[proba % len(HOSTY)]
        czekaj = PAUZA - (time.time() - _ostatnie_zapytanie[0])
        if czekaj > 0:
            time.sleep(czekaj)
        req = urllib.request.Request(f"https://{host}{sciezka_url}",
                                     headers={"User-Agent": UA})
        _ostatnie_zapytanie[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                dane = json.load(r)
            try:
                json.dump(dane, open(plik, "w", encoding="utf-8"))
            except OSError:
                pass
            return dane, None
        except urllib.error.HTTPError as e:
            blad = f"HTTP {e.code}"
            if e.code == 429:                      # limit Yahoo — backoff
                time.sleep(45 * (2 ** proba))
                continue
            return None, blad
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                OSError) as e:
            blad = f"błąd sieci/odpowiedzi: {e}"
            time.sleep(5)
    return None, blad


def _bary_z_result(res):
    """Wspólny parser wyniku chart/spark -> [(data 'YYYY-MM-DD', close)]."""
    try:
        ts = res["timestamp"]
        closes = res["indicators"]["quote"][0]["close"]
    except (KeyError, IndexError, TypeError):
        return []
    bary = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(NY)
        bary.append((d.strftime("%Y-%m-%d"), round(float(c), 4)))
    return bary


def pobierz(sym, zakres="15d"):
    """Pojedynczy symbol (v8/finance/chart). Zwraca (bary, błąd|None)."""
    q = urllib.parse.quote(sym)
    dane, blad = http_json(f"/v8/finance/chart/{q}?range={zakres}&interval=1d")
    if dane is None:
        return [], blad
    try:
        res = dane["chart"]["result"][0]
    except (KeyError, IndexError, TypeError):
        return [], "brak danych w odpowiedzi"
    bary = _bary_z_result(res)
    return bary, None if bary else "brak danych w odpowiedzi"


def pobierz_batch(symbole, zakres="15d"):
    """Wiele symboli naraz (v7/finance/spark, paczki po BATCH).

    Zwraca (mapa {symbol: bary}, [problemy]). Symbol bez danych trafia do
    problemów; gdy spark w ogóle zawiedzie, dzwoniący robi fallback na
    pobierz() per symbol.
    """
    mapa, problemy = {}, []
    for i in range(0, len(symbole), BATCH):
        paczka = symbole[i:i + BATCH]
        q = urllib.parse.quote(",".join(paczka), safe=",")
        dane, blad = http_json(f"/v7/finance/spark?symbols={q}"
                               f"&range={zakres}&interval=1d")
        wyniki = (dane or {}).get("spark", {}).get("result") or []
        if not wyniki:
            problemy.append(f"spark: brak odpowiedzi dla paczki "
                            f"{paczka[0]}..{paczka[-1]} ({blad or 'pusto'})")
            continue
        for w in wyniki:
            try:
                sym = w["symbol"]
                bary = _bary_z_result(w["response"][0])
            except (KeyError, IndexError, TypeError):
                continue
            if bary:
                mapa[sym] = bary
        for sym in paczka:
            if sym not in mapa:
                problemy.append(f"spark: brak danych dla {sym}")
    return mapa, problemy


def ostatnia_zakonczona(bary, teraz=None):
    """(data, close, poprz_data, poprz_close) ostatniej ZAKOŃCZONEJ sesji."""
    if not bary:
        return None
    teraz = teraz or datetime.now(NY)
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


def rezim_rynkowy(vix_bary=None):
    """POZIOM 0/1/2 wg prerejestrowanych progów (ochrona przed korektą/bessą).

    Dane: ^NDX 1 rok (MA200, MA50, drawdown od 52-tyg. szczytu) + ^VIX.
    P1: NDX<MA200 LUB drawdown>10% LUB VIX>28  →  gross 50%, taktyczne OFF
    P2: drawdown>20% LUB VIX>40 LUB sesja<=-5%  →  portfel płasko (NIEAKTUALNA)
    Powroty (histereza, decyduje rutyna tygodniowa):
    P2->handel: 5 kolejnych sesji VIX<25 ORAZ NDX>MA50
    P1->P0:     3 kolejne sesje  VIX<22 ORAZ NDX>MA200
    """
    bary_1y, blad = pobierz("^NDX", zakres="1y")
    if not bary_1y:
        return {"blad": f"brak danych ^NDX 1y: {blad}"}
    # dzisiejsza niedokończona świeca nie wchodzi do MA/drawdownu
    oz = ostatnia_zakonczona(bary_1y)
    if not oz:
        return {"blad": "za krótka historia ^NDX"}
    ostatnia_data = oz[0]
    zamk = [c for d, c in bary_1y if d <= ostatnia_data]
    if len(zamk) < 60:
        return {"blad": "za krótka historia ^NDX"}
    if vix_bary is None:
        vix_bary, _ = pobierz("^VIX")
    voz = ostatnia_zakonczona(vix_bary) if vix_bary else None
    v = voz[1] if voz else None
    c = zamk[-1]
    ma200 = sum(zamk[-200:]) / min(200, len(zamk))
    ma50 = sum(zamk[-50:]) / 50
    szczyt = max(zamk)
    dd = (c / szczyt - 1) * 100
    sesja = (c / zamk[-2] - 1) * 100 if len(zamk) >= 2 else 0.0
    poziom = 0
    powody = []
    if c < ma200: poziom = 1; powody.append(f"NDX {c:.0f} < MA200 {ma200:.0f}")
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

    # 1) jedno przejście batchem po całym uniwersum...
    wszystkie = sorted({s for kandydaci in SYMBOLE.values() for s in kandydaci})
    batch, problemy_batch = pobierz_batch(wszystkie)

    wynik, problemy = {}, []
    for ticker, kandydaci in SYMBOLE.items():
        bary, blad, uzyty = [], "nie próbowano", None
        for sym in kandydaci:
            bary = batch.get(sym, [])
            if not bary:                       # 2) ...fallback per symbol
                bary, blad = pobierz(sym)
            if bary:
                uzyty = sym
                break
        if not bary:
            problemy.append(f"{ticker}: brak danych ({', '.join(kandydaci)}; "
                            f"{blad}) — użyj depesz agencyjnych i oznacz źródło")
            continue
        oz = ostatnia_zakonczona(bary)
        if not oz:
            problemy.append(f"{ticker}: brak zakończonej sesji w danych")
            continue
        d, c, pd, pc = oz
        dd = round((c / pc - 1) * 100, 2) if pc else None
        # walidacja D0 (pomijana przy d0 == null — koszyki nieaktywowane)
        d0_close = dict(bary).get(d0_date) if d0_date else None
        ref = d0_prices.get(ticker)
        if ticker == "NDX100" and not ref:
            ref = d0.get("ndx")
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

    rezim = rezim_rynkowy(vix_bary=batch.get("^VIX"))
    problemy = problemy_batch + problemy

    if tryb_json:
        print(json.dumps({"wygenerowano": datetime.now(NY).isoformat(timespec="minutes"),
                          "d0": d0_date, "signals": sig_path,
                          "kursy": wynik, "rezim": rezim, "problemy": problemy},
                         ensure_ascii=False, indent=2))
        return

    print("REŻIM RYNKOWY:", json.dumps(rezim, ensure_ascii=False))
    print(f"KURSY NASDAQ/NYSE — ostatnia zakończona sesja (stan: "
          f"{datetime.now(NY).strftime('%Y-%m-%d %H:%M')} Nowy Jork)")
    if sig_path and d0_date:
        print(f"Walidacja D0 ({d0_date}) względem {sig_path}, tolerancja "
              f"{TOLERANCJA_D0*100:.1f}%")
    elif sig_path:
        print(f"Walidacja D0: pominięta — d0 puste w {sig_path} "
              f"(koszyki nieaktywowane)")
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
