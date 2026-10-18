#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odtwarza plik closes_5y.csv użyty w analizie 18.10.2026 (Yahoo spark, range=5y).
Użycie: python3 analiza/2026-10-18/pobierz_closes_5y.py [wyjście.csv]
Skrypty analizy czytają ścieżkę ze zmiennej CLOSES lub stałej w nagłówku — dostosuj."""
import csv, datetime, json, sys, time, urllib.parse, urllib.request
sig = json.load(open("signals.json", encoding="utf-8"))
tick = sorted(sig["epics"]) + ["^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"]
out = {}
for i in range(0, len(tick), 20):
    b = tick[i:i + 20]
    url = "https://query1.finance.yahoo.com/v7/finance/spark?symbols=" + ",".join(urllib.parse.quote(t) for t in b) + "&range=5y&interval=1d"
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120))
    for r in d["spark"]["result"]:
        res = r["response"][0]
        out[r["symbol"]] = {datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"): round(c, 4)
                            for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c is not None}
    time.sleep(2)
dates = sorted({d for v in out.values() for d in v}); cols = sorted(out)
with open(sys.argv[1] if len(sys.argv) > 1 else "closes_5y.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date"] + cols)
    for d in dates: w.writerow([d] + [out[c].get(d, "") for c in cols])
print(len(cols), "symboli", len(dates), "sesji")
