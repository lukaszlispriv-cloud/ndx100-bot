#!/usr/bin/env python3 -I
"""Dodatki: wykonalnosc lotow przy niskim ALLOC, ryzyko kill w biezacym tygodniu (W8),
sigma z 20/60 sesji jako estymator (stabilnosc), proponowana regula w liczbach."""
import json, math, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
px = pd.read_csv(os.path.join(HERE, "..", "dane", "closes_5y.csv"), parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()]
INDEKSY = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
UNIV = [c for c in px.columns if c not in INDEKSY]
ret = px.pct_change()
rng = np.random.default_rng(7)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

P("# Dodatki (ryzyko_extra.py)")
P()
# 1. Wykonalnosc lotow: krok 0,1 akcji (typowy u Capital.com dla akcji USA; app.py calc_size: minimalny lot otwierany,
#    gdy min_acc <= cel x MAX_OVERSHOOT=1,6; inaczej noga pomijana). Kapital odniesienia: START_EQUITY=1000 (domyslna z app.py).
last = px.iloc[-1]
P("## Wykonalnosc lotow (krok 0,1 akcji, kapital odniesienia = START_EQUITY 1 000 USD z app.py)")
P()
P("| ALLOC/noge | cel USD | nazwy, dla ktorych 0,1 akcji > cel x 1,6 (noga POMIJANA) | nazwy z 0,1 akcji w (cel; 1,6 cel] (otwierany min. lot = przestrzal) |")
P("|---|---|---|---|")
for a in (0.24, 0.12, 0.10, 0.08, 0.06):
    cel = 1000 * a
    pom = [f"{t} ({last[t]*0.1:.0f})" for t in UNIV if pd.notna(last[t]) and last[t] * 0.1 > cel * 1.6]
    prz = [f"{t} ({last[t]*0.1:.0f})" for t in UNIV if pd.notna(last[t]) and cel < last[t] * 0.1 <= cel * 1.6]
    P(f"| {a:.2f} | {cel:.0f} | {len(pom)}: {', '.join(pom) if pom else '-'} | {len(prz)}: {', '.join(prz) if prz else '-'} |")
P()
P("Kursy 2026-10-16 (USD): " + ", ".join(f"{t} {last[t]:.0f}" for t in ["MU", "LITE", "NFLX", "AVGO", "MSFT", "META", "COST", "ASML", "MELI", "BKNG", "NVDA", "AMD", "MRVL", "SNDK"] if t in last and pd.notna(last[t])))
P()

# 2. Biezacy tydzien: koszyk W8, kapital ok. 0,76 szczytu (~1,7% nad progiem 0,75), ALLOC 0,24 -> P(kill w 5 / 10 sesjach)
W8L = ["GOOGL", "GILD", "MSFT", "QCOM", "ADP"]; W8S = ["AXON", "DASH", "ALNY", "APP", "FER"]
sl = ret.iloc[-250:][W8L + W8S].dropna()
unit = (sl[W8L].sum(axis=1) - sl[W8S].sum(axis=1)).values
unit_dm = unit - unit.mean()
P("## Biezacy tydzien (W8): P(przebicia kill switcha) przy kapitale ~1,7% nad progiem")
P()
P(f"koszyk W8 sigma jednostkowa 250 ses.: {unit.std()*100:.2f}%/d; 60 ses.: {unit[-60:].std()*100:.2f}%/d")
P("| ALLOC | sigma_d kap. | P(kill w 5 ses.) | P(kill w 10 ses.) | P(kill w 20 ses.) |")
P("|---|---|---|---|---|")
for a in (0.24, 0.12, 0.08, 0.06, 0.04):
    res = []
    for n in (5, 10, 20):
        st = rng.integers(0, len(unit_dm) - 5, size=(20000, math.ceil(n / 5)))
        idx = (st[:, :, None] + np.arange(5)[None, None, :]).reshape(20000, -1)[:, :n]
        U = unit_dm[idx]
        eq = np.full(20000, 0.7627); peak = np.ones(20000); killed = np.zeros(20000, bool)
        for t in range(n):
            eq = np.where(killed, eq, eq * (1 + a * U[:, t])); peak = np.maximum(peak, eq)
            killed |= eq < 0.75 * peak
        res.append(killed.mean() * 100)
    P(f"| {a:.2f} | {unit_dm.std()*a*100:.2f}% | {res[0]:.0f}% | {res[1]:.0f}% | {res[2]:.0f}% |")
P()
P("Odleglosc do progu w sigmach dziennych kapitalu (~1,7%/sigma_d): " + ", ".join(f"ALLOC {a:.2f}: {1.7/(unit_dm.std()*a*100):.1f} sigma" for a in (0.24, 0.12, 0.08, 0.06)))
P()

# 3. Jakosc estymatora sigma: sigma20 vs sigma60 nogi jako prognoza sigma realizowanej w kolejnych 5 sesjach (panel uniwersum, 2 lata)
P("## Estymator sigma nogi: korelacja prognozy (sigma20 / sigma60 / EWMA lambda 0,94) z sigma realizowana w nastepnych 5 sesjach")
P()
R = ret[UNIV].iloc[-520:]
rows = []
for col in UNIV:
    s = R[col].dropna()
    if len(s) < 300: continue
    v = s.values
    for i in range(60, len(v) - 5, 5):
        s20 = v[i-20:i].std(); s60 = v[i-60:i].std()
        w = 0.94 ** np.arange(60)[::-1]; ew = math.sqrt(np.sum(w * v[i-60:i] ** 2) / w.sum())
        real = math.sqrt(np.mean(v[i:i+5] ** 2))
        rows.append((s20, s60, ew, real))
A = np.array(rows)
for j, nm in enumerate(["sigma20", "sigma60", "EWMA(0,94)"]):
    r = np.corrcoef(np.log(A[:, j]), np.log(A[:, 3]))[0, 1]
    bias = np.median(A[:, 3] / A[:, j])
    P(f"- {nm}: korelacja log-sigma prognoza vs realizacja {r:.3f}; mediana (realizowana/prognoza) {bias:.2f}; n={len(A)}")
P()

# 4. Ile sesji trzeba, zeby odrobic: po -25% potrzeba +33%; przy alfie +2pp/tyg i ALLOC 0,08 (0,8 pp/tyg) -> ~41 tyg
P("## Arytmetyka odrabiania")
P()
for dd in (0.10, 0.20, 0.237, 0.25):
    P(f"- obsuniecie -{dd*100:.1f}% wymaga +{(1/(1-dd)-1)*100:.1f}% do szczytu; przy alfie +2 p.p./tyg: ALLOC 0,24 -> {math.log(1/(1-dd))/math.log(1+0.024):.0f} tyg (bez szumu), ALLOC 0,08 -> {math.log(1/(1-dd))/math.log(1+0.008):.0f} tyg")
P()

# 5. Regula proponowana - przeliczenie na W1..W8 ex ante: ALLOC_i = clip(VOL_TARGET / sigma60_unit, ALLOC_MIN, ALLOC_MAX) z sigma60 unit = sqrt(w'Cw), w = +-1
kosz = json.load(open(os.path.join(HERE, "mp_koszyki.json")))
kosz["2026-W8"] = {"d0": "2026-10-16", "long": W8L, "short": W8S}
P("## Regula: ALLOC_t = clip(VOL_TARGET / sigma60_unit(koszyk), ALLOC_MIN, ALLOC_MAX); sigma60_unit = odchylenie dzienne sumy 5 long - 5 short z 60 sesji do D0")
P()
P("| W | sigma60_unit | ALLOC przy celu 1,0% | 1,25% | 1,5% | 2,0% | wariant uproszczony: sr. sigma60 nog x sqrt(10) x (1+rho) ... pominiety | P&L tygodnia przy spread_pp faktycznym (cel 1,5%) vs ALLOC 0,24 |")
P("|---|---|---|---|---|---|---|---|")
hist = {"2026-W1": -4.06, "2026-W2": 6.19, "2026-W3": 1.44, "2026-W4": 13.85, "2026-W5": 5.95, "2026-W6": -5.89, "2026-W7": -21.15, "2026-W8": None}
tot15 = 0; tot24 = 0
for w in ["2026-W1", "2026-W2", "2026-W3", "2026-W4", "2026-W5", "2026-W6", "2026-W7", "2026-W8"]:
    k = kosz[w]; i0 = px.index.searchsorted(pd.Timestamp(k["d0"]), side="right") - 1
    sl = ret.iloc[i0 - 59:i0 + 1][k["long"] + k["short"]].dropna()
    u = sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)
    s60 = u.std()
    al = {t: float(np.clip(t / s60, 0.04, 0.16)) for t in (0.010, 0.0125, 0.015, 0.020)}
    sp = hist[w]
    pnl15 = 5 * al[0.015] * sp if sp is not None else None; pnl24 = 5 * 0.24 * sp if sp is not None else None
    if sp is not None: tot15 += pnl15; tot24 += pnl24
    P(f"| {w[5:]} | {s60*100:.1f}% | {al[0.010]*100:.1f}% | {al[0.0125]*100:.1f}% | {al[0.015]*100:.1f}% | {al[0.020]*100:.1f}% | | {('%+.1f%% vs %+.1f%%' % (pnl15, pnl24)) if sp is not None else '-'} |")
P(f"suma W1-W7 (liniowo, bez kosztow): cel 1,5% -> {tot15:+.1f}% kapitalu; ALLOC 0,24 -> {tot24:+.1f}% (spread_pp x 5 x ALLOC; W4 liczony jak 1 tydzien)")
P()
open(os.path.join(HERE, "ryzyko_extra_out.md"), "w").write("\n".join(out))
