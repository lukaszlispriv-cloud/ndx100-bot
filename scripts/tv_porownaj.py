#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tv_porownaj.py — deterministyczne porównanie kursów z TradingView MCP
z kursami ze scripts/kursy.py (Yahoo) i opcjonalnie z FMP; mediana zmian
po branży TV ze screenera; wiersz do data/tv-log.jsonl.

Rutyna NIE liczy setek liczb w głowie: surowe odpowiedzi narzędzi TV
zapisuje do plików w scratchpadzie sesji (NIE do repo) i podaje je tu.

Użycie (w katalogu repo):
  python3 scripts/kursy.py --json > /tmp/kursy.json
  python3 -I scripts/tv_porownaj.py --tv batch1.json [batch2.json ...] \
      --kursy /tmp/kursy.json [--fmp fmp.json] [--ohlcv ndx.json ...] \
      [--screener spx.json ndx.json] --d0 signals.json \
      [--tylko-koszyk] [--log data/tv-log.jsonl --rutyna puls-ndx \
       --wywolania 14 --czas-s 210 --stan OK --faza 1]

Formaty wejścia (dosłownie to, co zwracają narzędzia):
  --tv        get_symbol_data_batch: {"data": {"NASDAQ:MU": {"close":..,"change":..}}, "missing":[...]}
              albo run_screener: {"data": {"rows": [{"symbol":"NASDAQ:MU","close":..}], "totalCount": N}}
  --ohlcv     get_ohlcv: {"symbol": "NASDAQ:NDX", "bars": [{"t":..,"c":..}, ...]}
              (data sesji = data UTC znacznika t; świeca bieżącej sesji
              jest odrzucana, gdy --teraz-utc nie minął 20:10 UTC dla NASDAQ)
  --kursy     wynik `kursy.py --json`: {"kursy": {"MU": {"data": "...", "close": ..}}, "d0": "..."}
  --fmp       lista FMP historical-price-eod-light: [{"symbol":"MU","date":"2026-10-09","price":..}]
  --screener  run_screener z kolumnami name/industry/sector/change (dowolna liczba plików,
              unia po symbolu — np. SYML:SP;SPX + SYML:NASDAQ;NDX)

Wynik: tabela ZGODNOŚĆ (ticker | Yahoo | FMP | TV | Δ% TV/Yahoo | data świecy),
listy |Δ| > 0,1% i > 0,5%, missing, mediana change po industry dla nóg,
oraz JEDEN wiersz JSON logu (bez liczb z rachunku). Kod wyjścia 0 zawsze,
gdy wejście dało się odczytać — rozjazd to adnotacja, nie błąd.
"""
import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timezone

PROG_ADNOTACJA = 0.1
PROG_ROZJAZD = 0.5
KONIEC_SESJI_UTC = (20, 10)   # 16:10 Nowy Jork w czasie letnim; zimą 21:10 — bezpiecznie 21:10
KONIEC_SESJI_UTC_ZIMA = (21, 10)


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def mapa_symboli(sciezka):
    """Odwrotna mapa EXCHANGE:TICKER -> ticker systemowy z data/tv-symbole.json."""
    odwr = {}
    if sciezka and os.path.exists(sciezka):
        m = wczytaj(sciezka)
        for sekcja in ("koszyk", "taktyczne"):
            for t, s in (m.get(sekcja) or {}).items():
                odwr[s] = t
        if m.get("_indeks"):
            odwr[m["_indeks"]] = "NDX100"
        if m.get("_vix"):
            odwr[m["_vix"]] = "VIX"
    return odwr


def ticker_z_symbolu(sym, odwr):
    if sym in odwr:
        return odwr[sym]
    return sym.split(":", 1)[-1]


def wiersze_tv(pliki, odwr):
    """{ticker: {"close":..., "change":..., "industry":..., "sector":...}}, missing[]"""
    out, missing = {}, []
    for p in pliki:
        d = wczytaj(p)
        if d.get("success") is False:
            missing.append(f"{os.path.basename(p)}: success=false ({d.get('error', 'b.d.')})")
            continue
        dane = d.get("data", d)
        if isinstance(dane, dict) and "rows" in dane:
            for r in dane["rows"]:
                sym = r.get("symbol") or f"?:{r.get('name')}"
                out[ticker_z_symbolu(sym, odwr)] = dict(r, symbol=sym)
        elif isinstance(dane, dict):
            for sym, r in dane.items():
                if isinstance(r, dict):
                    out[ticker_z_symbolu(sym, odwr)] = dict(r, symbol=sym)
        for m in d.get("missing") or []:
            missing.append(m.get("symbol", str(m)) if isinstance(m, dict) else str(m))
        if d.get("partial"):
            missing.append(f"{os.path.basename(p)}: partial=true")
    return out, missing


def swiece_ohlcv(pliki, odwr, teraz):
    """{ticker: (data_sesji, close)} — ostatnia ZAKOŃCZONA sesja."""
    out = {}
    dzis = teraz.strftime("%Y-%m-%d")
    po_sesji = (teraz.hour, teraz.minute) >= KONIEC_SESJI_UTC_ZIMA
    for p in pliki:
        d = wczytaj(p)
        sym = d.get("symbol", "?")
        bary = [(datetime.fromtimestamp(b["t"], tz=timezone.utc).strftime("%Y-%m-%d"), b["c"])
                for b in d.get("bars") or []]
        if bary and bary[-1][0] == dzis and not po_sesji:
            bary = bary[:-1]
        if bary:
            out[ticker_z_symbolu(sym, odwr)] = bary[-1]
    return out


def kursy_fmp(plik):
    out = {}
    if not plik:
        return out
    d = wczytaj(plik)
    if isinstance(d, dict):
        d = d.get("historical") or d.get("data") or []
    for r in d:
        t = r.get("symbol")
        cena = r.get("price", r.get("close"))
        if t and cena and (t not in out or r.get("date", "") > out[t][0]):
            out[t] = (r.get("date", ""), float(cena))
    return out


def delta(a, b):
    try:
        return (float(a) / float(b) - 1) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def mediana_branzy(pliki_screener, nogi_tv, odwr):
    """Mediana change po industry w unii uniwersów screenera; dla każdej nogi."""
    uniwersum = {}
    for p in pliki_screener:
        d = wczytaj(p)
        for r in (d.get("data") or {}).get("rows") or []:
            sym = r.get("symbol") or f"?:{r.get('name')}"
            uniwersum[sym] = r
    po_branzy = {}
    for r in uniwersum.values():
        if r.get("industry") and r.get("change") is not None:
            po_branzy.setdefault(r["industry"], []).append(float(r["change"]))
    wynik = {}
    for t, r in nogi_tv.items():
        br = r.get("industry")
        if not br:
            wynik[t] = {"industry": None, "n": 0, "mediana": None, "uwaga": "brak branży w odpowiedzi"}
            continue
        zm = po_branzy.get(br, [])
        if len(zm) < 4:
            wynik[t] = {"industry": br, "n": len(zm), "mediana": None,
                        "uwaga": "branża TV: za mało spółek (n<4) — werdykt tylko z peers"}
        else:
            wynik[t] = {"industry": br, "n": len(zm),
                        "mediana": round(statistics.median(zm), 2),
                        "blokada_tv": statistics.median(zm) < -3.0}
    return wynik


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tv", nargs="*", default=[], help="odpowiedzi get_symbol_data_batch / run_screener")
    ap.add_argument("--ohlcv", nargs="*", default=[], help="odpowiedzi get_ohlcv (po jednej na symbol)")
    ap.add_argument("--kursy", help="wynik kursy.py --json")
    ap.add_argument("--fmp", help="FMP historical-price-eod-light (lista)")
    ap.add_argument("--screener", nargs="*", default=[], help="run_screener do mediany branży")
    ap.add_argument("--d0", default="signals.json")
    ap.add_argument("--symbole", default="data/tv-symbole.json")
    ap.add_argument("--tylko-koszyk", action="store_true", help="tabela tylko dla nóg + taktycznych + indeksu")
    ap.add_argument("--teraz-utc", help="RRRR-MM-DDTHH:MM (domyślnie teraz) — do odrzucenia niedokończonej świecy")
    ap.add_argument("--log", help="ścieżka data/tv-log.jsonl — dopisz wiersz")
    ap.add_argument("--rutyna", default="puls-ndx")
    ap.add_argument("--wywolania", type=int, default=0)
    ap.add_argument("--czas-s", type=int, default=0)
    ap.add_argument("--stan", default="OK", choices=("OK", "brak", "401", "429", "wyłączony", "częściowy"))
    ap.add_argument("--faza", type=int, default=1)
    ap.add_argument("--werdykt-zmieniony", default="nie", choices=("tak", "nie"))
    ap.add_argument("--depesze", default="nie", choices=("tak", "nie"))
    ap.add_argument("--blok-przerwany", action="store_true")
    ap.add_argument("--prefix", default="mcp__TradingView__mcp-tv-")
    args = ap.parse_args()

    teraz = (datetime.strptime(args.teraz_utc, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
             if args.teraz_utc else datetime.now(timezone.utc))
    odwr = mapa_symboli(args.symbole)
    sig = wczytaj(args.d0) if args.d0 and os.path.exists(args.d0) else {}
    nogi = list(sig.get("long") or []) + list(sig.get("short") or [])
    takt = [t.get("ticker") for t in sig.get("tactical") or []]
    koszyk = set(nogi) | set(takt) | {"NDX100"}

    tv, missing = wiersze_tv(args.tv, odwr)
    for t, (data, c) in swiece_ohlcv(args.ohlcv, odwr, teraz).items():
        tv.setdefault(t, {})
        tv[t]["close_ohlcv"], tv[t]["data_ohlcv"] = c, data
    kursy = (wczytaj(args.kursy).get("kursy") if args.kursy else {}) or {}
    fmp = kursy_fmp(args.fmp)

    tickery = sorted(set(tv) | set(kursy) | set(fmp))
    if args.tylko_koszyk:
        tickery = [t for t in tickery if t in koszyk]

    print("ZGODNOŚĆ ŹRÓDEŁ (Δ% = TV / Yahoo − 1; TV = close z batcha, a gdy jest — ostatnia zakończona świeca ohlcv)")
    print(f"{'TICKER':8} {'Yahoo':>11} {'data':11} {'FMP':>11} {'TV':>11} {'Δ% TV':>8}  uwagi")
    delty, adnot, rozjazdy = [], [], []
    for t in tickery:
        y = kursy.get(t) or {}
        r = tv.get(t) or {}
        tvc = r.get("close_ohlcv", r.get("close"))
        f = fmp.get(t)
        d = delta(tvc, y.get("close")) if tvc is not None and y.get("close") else None
        uwagi = []
        if r.get("update_mode") and r["update_mode"] != "streaming" and "close_ohlcv" not in r:
            uwagi.append(f"{r['update_mode']} (kurs opóźniony, nie zamknięcie)")
        if r.get("data_ohlcv") and y.get("data") and r["data_ohlcv"] != y["data"]:
            uwagi.append(f"inna data świecy: TV {r['data_ohlcv']} vs Yahoo {y['data']}")
        if d is not None:
            delty.append(abs(d))
            if abs(d) > PROG_ROZJAZD:
                rozjazdy.append(t); uwagi.append("ROZJAZD ŹRÓDEŁ >0,5%")
            elif abs(d) > PROG_ADNOTACJA:
                adnot.append(t); uwagi.append("odnotuj (>0,1%)")
        oznacz = "*" if t in koszyk else " "
        print(f"{oznacz}{t:7} {str(y.get('close', 'b.d.')):>11} {str(y.get('data', '')):11} "
              f"{(f'{f[1]}' if f else 'b.d.'):>11} {str(tvc if tvc is not None else 'b.d.'):>11} "
              f"{(f'{d:+.2f}' if d is not None else 'b.d.'):>8}  {'; '.join(uwagi)}")
    print(f"\nn = {len(delty)} porównań; max |Δ| = {max(delty):.2f}% ; mediana |Δ| = "
          f"{statistics.median(delty):.2f}%" if delty else "\nn = 0 porównań (brak wspólnych tickerów)")
    print(f"|Δ| > 0,1%: {', '.join(adnot) or 'brak'}")
    print(f"|Δ| > 0,5% (ROZJAZD): {', '.join(rozjazdy) or 'brak'}")
    print(f"missing / błędy TV: {', '.join(missing) or 'brak'}")
    brak_tv = [t for t in nogi + takt if t not in tv]
    if brak_tv:
        print(f"nogi/taktyczne bez odczytu TV: {', '.join(brak_tv)}")

    if args.screener:
        print("\nBLOKADA SEKTOROWA — mediana change po branży TV (unia uniwersów screenera):")
        nogi_tv = {t: tv[t] for t in nogi + takt if t in tv}
        for t, w in mediana_branzy(args.screener, nogi_tv, odwr).items():
            if w.get("mediana") is None:
                print(f"  {t:7} {w.get('industry') or 'b.d.'}: n={w['n']} — {w.get('uwaga')}")
            else:
                print(f"  {t:7} {w['industry']}: n={w['n']}, mediana d/d {w['mediana']:+.2f}% "
                      f"{'→ TV dałby BLOKADĘ (<−3%)' if w['blokada_tv'] else ''}")

    wiersz = {"data": teraz.strftime("%Y-%m-%d"), "rutyna": args.rutyna,
              "narzedzia_prefix": args.prefix, "stan": args.stan,
              "wywolania": args.wywolania, "czas_s": args.czas_s,
              "n_porownan": len(delty),
              "max_delta_pct": round(max(delty), 3) if delty else None,
              "mediana_delta_pct": round(statistics.median(delty), 3) if delty else None,
              "rozjazdy_gt_0_5": rozjazdy, "adnotacje_gt_0_1": adnot,
              "missing": missing, "faza": args.faza,
              "werdykt_zmieniony": args.werdykt_zmieniony,
              "depesze_agencyjne": args.depesze,
              "blok_przerwany_czasem": bool(args.blok_przerwany)}
    print("\nWIERSZ LOGU (data/tv-log.jsonl):")
    print(json.dumps(wiersz, ensure_ascii=False))
    if args.log:
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(wiersz, ensure_ascii=False) + "\n")
        print(f"dopisano do {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
