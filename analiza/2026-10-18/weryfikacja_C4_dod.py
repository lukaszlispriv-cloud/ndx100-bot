#!/usr/bin/env python3 -I
"""Dodatek do weryfikacja_C4.py: rozklad ALLOC z vol-targetu, istotnosc roznicy Sharpe'a VT vs staly 0,10
(bootstrap blokowy tygodni), zrealizowana sigma W7 vs prognoza, P(kill 52t) przy rownej sredniej ALLOC."""
import json, math, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "dane", "closes_5y.csv")
rng = np.random.default_rng(7)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s, flush=True)

df = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index(); df = df[df["^NDX"].notna()]
df3 = df.ffill(limit=3)
NON = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
cands = [c for c in df.columns if c not in NON]; dates = df.index
Pm = df3[cands].to_numpy(float); PF = df3[cands].ffill().to_numpy(float); NDX = df3["^NDX"].to_numpy(float)
nT, nS = Pm.shape
R = np.vstack([np.full((1, nS), np.nan), PF[1:] / PF[:-1] - 1]); Rn = np.vstack([np.full((1, nS), np.nan), Pm[1:] / Pm[:-1] - 1])
iso = dates.isocalendar(); keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy())); last_idx = {}
for i, k in enumerate(keys): last_idx[k] = i
weeks = sorted(last_idx); D0 = np.array([last_idx[w] for w in weeks[:-1]]); D5 = np.array([last_idx[w] for w in weeks[1:]]); nW = len(D0)
WR = Pm[D5] / Pm[D0] - 1
S6 = np.full((nW, nS), np.nan)
for w, d0 in enumerate(D0):
    if d0 >= 126: S6[w] = Pm[d0] / Pm[d0 - 126] - 1 - (NDX[d0] / NDX[d0 - 126] - 1)
LONGS, SHORTS = [], []
for w in range(nW):
    s = S6[w].copy(); s[np.isnan(WR[w])] = np.nan
    E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1); s[np.isnan(Pm[E]) | np.isnan(Pm[X])] = np.nan
    ok = np.where(~np.isnan(s))[0]
    if len(ok) < 30: LONGS.append(None); SHORTS.append(None); continue
    order = ok[np.argsort(-s[ok], kind="stable")]; LONGS.append(order[:5]); SHORTS.append(order[-5:])
widx = [w for w in range(nW) if LONGS[w] is not None]
wk_u = []; sig60 = []; sig20 = []
for w in widx:
    E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1); L = LONGS[w]; S = SHORTS[w]
    wk_u.append(np.array([R[t, L].sum() - R[t, S].sum() for t in range(E + 1, X + 1)]))
    hist = Rn[D0[w] - 59:D0[w] + 1][:, np.concatenate([L, S])]; ok = ~np.isnan(hist).any(axis=1)
    uh = hist[ok][:, :5].sum(axis=1) - hist[ok][:, 5:].sum(axis=1)
    sig60.append(uh.std(ddof=1)); sig20.append(uh[-20:].std(ddof=1))
sig60 = np.array(sig60); sig20 = np.array(sig20); nWk = len(wk_u)
allu = np.concatenate(wk_u); mean_u = allu.mean()

P("# Dodatek C4 (weryfikacja_C4_dod.py)")
P()
a60 = np.clip(0.015 / sig60, 0.04, 0.12); a20 = np.clip(0.015 / sig20, 0.04, 0.12)
P(f"## Rozklad ALLOC z vol-targetu sigma60 1,5%/d clip [0,04;0,12] na {nWk} tygodniach momentum 6M")
P(f"- udzial tygodni na capie 0,12: {(a60>=0.12-1e-9).mean()*100:.0f}%; na floorze 0,04: {(a60<=0.04+1e-9).mean()*100:.0f}%; mediana {np.median(a60):.3f}; p10 {np.percentile(a60,10):.3f}; p90 {np.percentile(a60,90):.3f}; srednia {a60.mean():.3f}")
P(f"- to samo z sigma20: cap {(a20>=0.12-1e-9).mean()*100:.0f}%, floor {(a20<=0.04+1e-9).mean()*100:.0f}%, mediana {np.median(a20):.3f}")
P(f"- sigma60 jednostkowa koszykow momentum: mediana {np.median(sig60)*100:.1f}%/d, p10 {np.percentile(sig60,10)*100:.1f}%, p90 {np.percentile(sig60,90)*100:.1f}%; lata: " + ", ".join(f"{y} {np.median([sig60[i] for i,w in enumerate(widx) if dates[D0[w]].year==y])*100:.1f}%" for y in range(2022, 2027)))
P()
# tygodniowe zwroty kapitalu per polityka, 3 scenariusze alfy
def wk_returns(alloc_w, shift):
    return np.array([np.prod(1 + alloc_w[i] * (wk_u[i] + shift)) - 1 for i in range(nWk)])
def sharpe(x): return x.mean() / x.std(ddof=1) * math.sqrt(52)
P("## Istotnosc roznicy Sharpe'a: VT sigma60 [0,04;0,12] vs staly 0,10 vs staly 0,12 (bootstrap blokowy tygodni, blok 4, 5000 prob)")
P()
P("| scenariusz alfy | Sharpe VT | Sharpe 0,10 | roznica | 90% CI roznicy (bootstrap) | P(roznica>0) | sr. tyg. VT | sr. tyg. 0,10 | stosunek zyskow VT/0,10 |")
P("|---|---|---|---|---|---|---|---|---|")
res = {}
for nm, shift in (("in-sample", 0.0), ("alfa 0", -mean_u), ("alfa +1 p.p.", -mean_u + 0.01), ("alfa +0,5 p.p.", -mean_u + 0.005)):
    rv = wk_returns(a60, shift); rf = wk_returns(np.full(nWk, 0.10), shift)
    d = sharpe(rv) - sharpe(rf); diffs = []
    nb = math.ceil(nWk / 4)
    for _ in range(5000):
        st = rng.integers(0, nWk - 4 + 1, size=nb); idx = (st[:, None] + np.arange(4)[None, :]).ravel()[:nWk]
        diffs.append(sharpe(rv[idx]) - sharpe(rf[idx]))
    diffs = np.array(diffs)
    ratio = rv.mean() / rf.mean() if abs(rf.mean()) > 1e-9 else float("nan")
    res[nm] = dict(sh_vt=sharpe(rv), sh_f=sharpe(rf), d=d, ci=[float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))], p=float((diffs > 0).mean()), ratio=ratio)
    P(f"| {nm} | {sharpe(rv):.2f} | {sharpe(rf):.2f} | {d:+.2f} | [{np.percentile(diffs,5):+.2f}; {np.percentile(diffs,95):+.2f}] | {(diffs>0).mean()*100:.0f}% | {rv.mean()*100:+.3f}% | {rf.mean()*100:+.3f}% | {ratio:.2f} |")
P()
P("Uwaga: Sharpe stalego ALLOC nie zalezy od poziomu ALLOC (0,10 = 0,12 = 0,24 co do Sharpe'a przy zwrotach liniowych), wiec roznica dotyczy KSZTALTU skalowania, nie poziomu.")
P()
# W7 realized sigma
kosz = json.load(open(os.path.join(HERE, "mp_koszyki.json"))); k = kosz["2026-W7"]
ret = df.pct_change(); i0 = dates.searchsorted(pd.Timestamp("2026-10-09"), side="right") - 1
sl = ret.iloc[i0 + 1:i0 + 6][k["long"] + k["short"]]; u7 = (sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)).values
h = ret.iloc[i0 - 59:i0 + 1][k["long"] + k["short"]].dropna(); uh = (h[k["long"]].sum(axis=1) - h[k["short"]].sum(axis=1)).values
P("## W7: zrealizowana zmiennosc vs prognoza")
P(f"- RMS u w W7: {math.sqrt(np.mean(u7**2))*100:.1f}%/d; odchylenie wokol wlasnej sredniej: {u7.std(ddof=1)*100:.1f}%/d; sigma60 ex ante {uh.std(ddof=1)*100:.1f}%, sigma20 {uh[-20:].std(ddof=1)*100:.1f}%; srednia dzienna W7 {u7.mean()*100:+.1f}%/d = {u7.mean()/uh.std(ddof=1):+.2f} sigma60 dziennie, 5 dni z rzedu ujemnych (P przy symetrii = 1/32 = 3,1%).")
P(f"- Wniosek: W7 to nie 'wybuch zmiennosci' (RMS/prognoza {math.sqrt(np.mean(u7**2))/uh.std(ddof=1):.2f}x), lecz seria 5 ujemnych dni o przecietnej skali 1,2 sigma; zaden estymator sigma z danych do D0 (ani sigma20 ani sigma60) nie przewidzialby tego — sigma20 byla NIZSZA od sigma60 i dalaby wyzszy ALLOC.")
P()
# P(kill) at equal mean ALLOC: VT scaled to mean 0.10 vs fixed 0.10 on historical path (rolling windows), 3 alpha scenarios
P("## Rowna srednia ALLOC: VT sigma60 przeskalowany do sredniej 0,10 vs staly 0,10 (sciezka historyczna, okna kroczace co 5 sesji)")
P()
def rolling_kill(alloc_w, shift, nses):
    allr = np.concatenate([alloc_w[i] * (wk_u[i] + shift) for i in range(nWk)])
    hits = 0; tot = 0; mdd = []
    for s in range(0, len(allr) - nses + 1, 5):
        e = np.cumprod(1 + allr[s:s + nses]); pk = np.maximum.accumulate(np.maximum(e, 1.0))
        hits += bool((e < 0.75 * pk).any()); tot += 1; mdd.append((e / pk - 1).min())
    return hits / tot * 100, float(np.percentile(mdd, 5) * 100)
a60s = a60 * (0.10 / a60.mean())
P("| scenariusz | polityka | sr. ALLOC | max ALLOC | okna 12t kill | okna 52t kill | DD p95 12t |")
P("|---|---|---|---|---|---|---|")
for nm, shift in (("alfa 0", -mean_u), ("alfa +1 p.p.", -mean_u + 0.01)):
    for pn, aw in (("staly 0,10", np.full(nWk, 0.10)), ("VT sigma60 x (0,10/sr.)", a60s), ("VT sigma60 [0,04;0,12]", a60)):
        k12, dd = rolling_kill(aw, shift, 60); k52, _ = rolling_kill(aw, shift, 260)
        P(f"| {nm} | {pn} | {aw.mean():.3f} | {aw.max():.3f} | {k12:.1f}% | {k52:.1f}% | {dd:.1f}% |")
P()
open(os.path.join(HERE, "weryfikacja_C4_dod_out.md"), "w").write("\n".join(out))
json.dump(res, open(os.path.join(HERE, "weryfikacja_C4_dod_wyniki.json"), "w"), indent=1, default=float)
