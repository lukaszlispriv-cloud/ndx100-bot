#!/usr/bin/env python3 -I
"""Weryfikacja C7 — bramka reakcji Pulsu (REDUCE 4 %/CLOSE 8 % od ceny wejścia, potwierdzenie
drugą sesją) jako redukcja OGONA, nie średniej; stabilność sygnału „dzień ≤ −3 p.p.”; wariant
od D0 vs od D+1 (fills); reżim VIX; interakcja ze stopem 10 % bota.

Dane: closes_5y.csv (skład dzisiejszy — survivorship bias). Koszyk-proxy systemu: momentum 6M
(126 sesji, bez ostatnich 5) TOP5/BOTTOM5 rel. do ^NDX, równe wagi, okna D0 = ostatnia sesja
tygodnia ISO → następne D0 (jak pq_quant.py / bt_momentum.py). Zwrot nogi = r_spółki − r_NDX
(long) albo −(r − r_NDX) (short), w p.p.; spread = śr. L + śr. S (gross 2).
Kapitał przy ALLOC 0,24: dzienny zwrot kapitału = 1,2 × spread_dzienny/100.
"""
import json, math, sys
import numpy as np, pandas as pd

BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
OUTMD = f"{BASE}/analiza/weryfikacja_C7_out.md"
OUTJ = f"{BASE}/analiza/weryfikacja_C7_wyniki.json"
L = []; OUT = {}
def P(s=""): L.append(s); print(s)

px = pd.read_csv(f"{BASE}/dane/closes_5y.csv", parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()]
px = px.ffill(limit=2)
NONSTOCK = ["^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"]
stocks = [c for c in px.columns if c not in NONSTOCK and c != "GOOG"]
ndx = px["^NDX"]; vix = px["^VIX"].ffill()
dates = px.index
P(f"Dane: {dates[0].date()}…{dates[-1].date()}, sesji {len(px)}, spółek {len(stocks)}")

# tygodnie ISO — D0 = ostatnia sesja tygodnia
wk = px.index.to_series().groupby([px.index.isocalendar().year, px.index.isocalendar().week]).max()
wk = pd.DatetimeIndex(sorted(wk.values))
pos = {d: i for i, d in enumerate(dates)}

def mom_signal(d0):
    i = pos[d0]
    if i < 131: return None
    s = (px[stocks].iloc[i-5] / px[stocks].iloc[i-131] - 1) - (ndx.iloc[i-5] / ndx.iloc[i-131] - 1)
    return s.dropna()

RED, CLO = 4.0, 8.0

def protocol_weights(rel, ab, second=True, red=RED, clo=CLO, lag=0, strict_close=True):
    """rel, ab: macierze (K+1, N) skumulowanych zwrotów od kotwicy (wiersz 0 = kotwica, zera),
    znak już po stronie (dodatni = zgodnie z tezą). Zwraca macierz wag W (K, N): W[k-1] = waga
    segmentu (k-1 → k). lag=0: cięcie na zamknięciu sesji sygnału (≈ bieg 13:45 UTC dnia
    następnego bez luki); lag=1: cięcie na zamknięciu sesji następnej (pesymistycznie)."""
    K1, N = rel.shape; K = K1 - 1
    badR = rel <= -red; badC = rel <= -clo
    if second:
        sigR = badR[1:] & np.vstack([np.zeros((1, N), bool), badR[1:-1]]) & (ab[1:] <= -red)   # k=1..K
        if strict_close:
            sigC = badC[1:] & np.vstack([np.zeros((1, N), bool), badC[1:-1]]) & (ab[1:] <= -clo)
        else:
            sigC = badR[1:] & np.vstack([np.zeros((1, N), bool), badR[1:-1]]) & badC[1:] & (ab[1:] <= -clo)
    else:
        sigR = badR[1:] & (ab[1:] <= -red); sigC = badC[1:] & (ab[1:] <= -clo)
    # pierwsze wystąpienie (indeks k w 1..K; brak → K+1)
    def first(sig):
        f = np.where(sig.any(axis=0), sig.argmax(axis=0) + 1, K + 1)
        return f
    fR, fC = first(sigR), first(sigC)
    ks = np.arange(1, K + 1)[:, None]          # segment k-1→k ma wagę ustaloną na zamknięciu k-1
    eff_k = ks - 1 - lag                        # waga segmentu k zależy od sygnałów do sesji (k-1-lag)
    W = np.ones((K, N))
    W[(eff_k >= fR[None, :])] = 0.5
    W[(eff_k >= fC[None, :])] = 0.0
    nR = (fR <= K).sum(); nC = (fC <= K).sum()
    return W, fR, fC

# ------------------------------------------------------------------ 1. symulacja tygodniowa
d0s = [d for d in wk if d >= pd.Timestamp("2022-04-22")]
rows = []; daily_rows = []; cs_rows = []
rand = np.random.default_rng(20261018)
NRAND = 200
rand_rows = {v: [] for v in ("base", "gate0", "gate1")}
for k in range(len(d0s) - 1):
    d0, d5 = d0s[k], d0s[k + 1]
    i0, i5 = pos[d0], pos[d5]
    if i5 + 1 >= len(dates): break
    s = mom_signal(d0)
    if s is None or len(s) < 20: continue
    s = s.sort_values(); Lg, Sh = list(s.index[-5:]), list(s.index[:5])
    out = dict(d0=d0, year=d0.year, vix0=vix.loc[d0], ndx_w=(ndx.iloc[i5] / ndx.iloc[i0] - 1) * 100)
    for anchor, (ia, ib) in (("D0", (i0, i5)), ("D1", (i0 + 1, i5 + 1))):
        sub = px[stocks].iloc[ia:ib + 1]; nd = ndx.iloc[ia:ib + 1]
        ok = sub.notna().all(axis=0)
        cols = sub.columns[ok]; sub = sub[cols]
        lr = (sub / sub.iloc[0] - 1).values * 100; ln = ((nd / nd.iloc[0] - 1).values * 100)[:, None]
        relc = lr - ln                                   # (K+1, N) rel od kotwicy, long
        absc = lr
        segr = np.diff(sub.values, axis=0) / sub.values[:-1] * 100 - (np.diff(nd.values) / nd.values[:-1] * 100)[:, None]
        res = {}
        for side, sgn in (("L", 1), ("S", -1)):
            rel_s, ab_s, seg_s = sgn * relc, sgn * absc, sgn * segr
            W0, fR0, fC0 = protocol_weights(rel_s, ab_s, lag=0)
            W1, _, _ = protocol_weights(rel_s, ab_s, lag=1)
            Wn, _, _ = protocol_weights(rel_s, ab_s, second=False, lag=0)
            Wa, _, _ = protocol_weights(rel_s, ab_s, lag=0, strict_close=False)  # jak audyt_regul
            res[side] = dict(base=seg_s.sum(axis=0), gate0=(W0 * seg_s).sum(axis=0), gate1=(W1 * seg_s).sum(axis=0),
                             nosec=(Wn * seg_s).sum(axis=0), audyt=(Wa * seg_s).sum(axis=0),
                             fR=fR0, fC=fC0, seg=seg_s, W0=W0, rel=rel_s, ab=ab_s)
        cidx = {c: j for j, c in enumerate(cols)}
        Lj = [cidx[t] for t in Lg if t in cidx]; Sj = [cidx[t] for t in Sh if t in cidx]
        if len(Lj) < 5 or len(Sj) < 5: continue
        K = segr.shape[0]
        for v in ("base", "gate0", "gate1", "nosec", "audyt"):
            out[f"{anchor}_{v}"] = res["L"][v][Lj].mean() + res["S"][v][Sj].mean()
        out[f"{anchor}_nR"] = int((res["L"]["fR"][Lj] <= K).sum() + (res["S"]["fR"][Sj] <= K).sum())
        out[f"{anchor}_nC"] = int((res["L"]["fC"][Lj] <= K).sum() + (res["S"]["fC"][Sj] <= K).sum())
        # serie dzienne spreadu (base i gate0) — do ścieżki kapitału i testu „dzień ≤ −3”
        if anchor == "D1":
            dsb = res["L"]["seg"][:, Lj].mean(axis=1) + res["S"]["seg"][:, Sj].mean(axis=1)
            dsg = (res["L"]["W0"] * res["L"]["seg"])[:, Lj].mean(axis=1) + (res["S"]["W0"] * res["S"]["seg"])[:, Sj].mean(axis=1)
            ndd = np.diff(nd.values) / nd.values[:-1] * 100
            for kk in range(K):
                daily_rows.append(dict(date=dates[ia + 1 + kk], d0=d0, spread=dsb[kk], spread_gate=dsg[kk], ndx=ndd[kk],
                                       vix=vix.iloc[ia + 1 + kk], year=dates[ia + 1 + kk].year))
            # losowe koszyki (szum): ten sam tydzień, 200 losowań 5/5
            N = len(cols)
            for r in range(NRAND):
                pick = rand.choice(N, 10, replace=False)
                for v in ("base", "gate0", "gate1"):
                    rand_rows[v].append(res["L"][v][pick[:5]].mean() + res["S"][v][pick[5:]].mean())
        # przekrój: sygnał REDUCE (pierwszy) w sesjach 2..K-1 — reszta okna; od D0 jak audyt
        if anchor == "D0":
            q = pd.qcut(s.rank(method="first"), 5, labels=False)
            for side, sgn in (("L", 1), ("S", -1)):
                fR = res[side]["fR"]; rel_s = res[side]["rel"]
                for j, c in enumerate(cols):
                    f = fR[j]
                    if 2 <= f <= K - 1:
                        rest = rel_s[K, j] - rel_s[f, j]
                        cs_rows.append(dict(d0=d0, year=d0.year, t=c, side=side, j=int(f), rel_at=rel_s[f, j],
                                            rest=rest, vix_sig=vix.iloc[i0 + f], ndx_sig=(ndx.iloc[i0 + f] / ndx.iloc[i0] - 1) * 100,
                                            q=int(q.get(c, -1)) if c in q.index else -1,
                                            close_lvl=bool(res[side]["fC"][j] <= f)))
    # stop 10 % + reopen (bot) od D1 oraz stop + protokół — pętla po nogach
    ia, ib = i0 + 1, i5 + 1
    def leg_path(t, sgn, gate, lag=0):
        p = px[t].iloc[ia:ib + 1].values; n = ndx.iloc[ia:ib + 1].values
        if np.isnan(p).any(): return np.nan, 0, 0
        anchor_i = 0; w = 1.0; tot = 0.0; stops = 0; reacts = 0; closed = False
        bad_prev = False; badc_prev = False; pend = None
        for kk in range(1, len(p)):
            seg = sgn * ((p[kk] / p[kk - 1] - 1) * 100 - (n[kk] / n[kk - 1] - 1) * 100)
            if pend is not None and lag == 1:
                w = pend; pend = None
            tot += w * seg
            if closed: continue
            if anchor_i is None:  # reopen na zamknięciu tej sesji
                anchor_i = kk; w = 1.0; bad_prev = badc_prev = False; continue
            ab = sgn * (p[kk] / p[anchor_i] - 1) * 100
            rel = ab - sgn * (n[kk] / n[anchor_i] - 1) * 100
            if ab <= -10.0:
                stops += 1; w = 0.0; anchor_i = None; continue   # płasko jedną sesję, reopen następnej
            if gate:
                badR = rel <= -RED; badC = rel <= -CLO
                neww = w
                if badC and badc_prev and ab <= -CLO: neww = 0.0; closed = True; reacts += 1
                elif badR and bad_prev and ab <= -RED and w == 1.0: neww = 0.5; reacts += 1
                if neww != w:
                    if lag == 0: w = neww
                    else: pend = neww
                bad_prev, badc_prev = badR, badC
        return tot, stops, reacts
    for gate in (False, True):
        vals = []; st = 0; rc = 0
        for t in Lg: v, a, b = leg_path(t, 1, gate); vals.append(v); st += a; rc += b
        for t in Sh: v, a, b = leg_path(t, -1, gate); vals.append(v); st += a; rc += b
        key = "D1_stop" if not gate else "D1_stop_gate0"
        out[key] = np.nanmean(vals[:5]) + np.nanmean(vals[5:]); out[key + "_n"] = st if not gate else rc
    rows.append(out)

df = pd.DataFrame(rows).set_index("d0")
dd = pd.DataFrame(daily_rows).set_index("date")
CS = pd.DataFrame(cs_rows)
OUT["n_tygodni"] = int(len(df))
P(f"Okien tygodniowych: {len(df)} ({df.index[0].date()}…{df.index[-1].date()}); dni w serii dziennej: {len(dd)}; sygnałów przekrojowych: {len(CS)}")

def tail(x):
    x = np.asarray(x, float); cum = np.cumsum(x)
    return dict(n=int(len(x)), mean=x.mean(), sd=x.std(ddof=1), t=x.mean() / x.std(ddof=1) * math.sqrt(len(x)),
                p1=np.percentile(x, 1), p5=np.percentile(x, 5), p10=np.percentile(x, 10), min=x.min(),
                maxDD=(cum - np.maximum.accumulate(cum)).min(), hit=(x > 0).mean(), sum=x.sum())
def diff(a, b):
    d = np.asarray(a) - np.asarray(b); n = len(d)
    return dict(mean=d.mean(), t=d.mean() / d.std(ddof=1) * math.sqrt(n) if d.std() > 0 else float("nan"),
                help=(d > 0).mean(), hurt=(d < 0).mean(), sum=d.sum())
def fmt(d, keys=("n", "mean", "sd", "t", "p5", "p1", "min", "maxDD", "hit")):
    return " | ".join(f"{d[k]:.0f}" if k == "n" else f"{d[k]:.2f}" for k in keys)

# ------------------------------------------------------------------ 2. tabela główna: średnia vs ogon
P("\n## 1. Protokół 4/8 + druga sesja + bramka abs na koszykach momentum 6M (5/5), 2022-04…2026-10\n")
P("Wariant | n | śr. pp/tydz | σ | t | p5 | p1 | min | maxDD (pp skum.) | hit | Δ vs baza (śr.) | t(Δ) | tyg. pomógł | tyg. zaszkodził | ΔmaxDD | Δp5")
P("|".join(["---"] * 16))
VARS = [("D0_base", "od D0, bez reakcji (baza)"), ("D0_gate0", "od D0, protokół, cięcie na close sygnału"),
        ("D0_gate1", "od D0, protokół, cięcie na close dnia następnego"), ("D0_audyt", "od D0, jak audyt_regul (CLOSE luźniej)"),
        ("D0_nosec", "od D0, bez potwierdzenia 2. sesją"),
        ("D1_base", "od D+1 (pon.), bez reakcji (baza)"), ("D1_gate0", "od D+1, protokół, cięcie na close sygnału"),
        ("D1_gate1", "od D+1, protokół, cięcie na close dnia następnego"), ("D1_nosec", "od D+1, bez 2. sesji"),
        ("D1_stop", "od D+1, stop 10 % + reopen (bot), bez protokołu"), ("D1_stop_gate0", "od D+1, stop 10 % + reopen + protokół")]
STATS = {}
for key, name in VARS:
    base = df["D0_base"] if key.startswith("D0") else (df["D1_stop"] if key == "D1_stop_gate0" else df["D1_base"])
    s = tail(df[key]); d = diff(df[key], base); sb = tail(base)
    STATS[key] = dict(stats=s, diff=d, dmaxDD=s["maxDD"] - sb["maxDD"], dp5=s["p5"] - sb["p5"])
    P(f"{name} | {fmt(s)} | {d['mean']:+.3f} | {d['t']:+.2f} | {d['help']:.0%} | {d['hurt']:.0%} | {s['maxDD']-sb['maxDD']:+.1f} | {s['p5']-sb['p5']:+.2f}")
OUT["tabela_glowna"] = {k: {kk: (vv if not isinstance(vv, dict) else {a: float(b) for a, b in vv.items()}) for kk, vv in v.items()} for k, v in STATS.items()}
P(f"\nLiczba reakcji (D+1, lag 0): REDUCE {int(df['D1_nR'].sum())}, CLOSE {int(df['D1_nC'].sum())} na {len(df)*10} nóg; tygodnie z ≥1 reakcją: {int((df['D1_nR']+df['D1_nC']>0).sum())}/{len(df)}; stopy 10 % (D+1): {int(df['D1_stop_n'].sum())}.")
OUT["reakcje"] = dict(REDUCE=int(df['D1_nR'].sum()), CLOSE=int(df['D1_nC'].sum()), tyg_z_reakcja=int((df['D1_nR']+df['D1_nC']>0).sum()), stopy=int(df['D1_stop_n'].sum()))

# tygodnie z reakcją: rozkład Δ
act = df[(df["D1_nR"] + df["D1_nC"]) > 0]
dl = act["D1_gate0"] - act["D1_base"]
P(f"W tygodniach z reakcją (n={len(act)}): Δ śr. {dl.mean():+.2f} pp, mediana {dl.median():+.2f}, p10 {dl.quantile(.1):+.2f}, p90 {dl.quantile(.9):+.2f}; "
  f"spread bazowy w tych tygodniach śr. {act['D1_base'].mean():+.2f} (vs {df['D1_base'].mean():+.2f} ogółem).")
# ogon: w 5 % najgorszych tygodni bazy — ile bramka odjęła straty?
q5 = df["D1_base"].quantile(.05); worst = df[df["D1_base"] <= q5]
P(f"5 % najgorszych tygodni bazy (n={len(worst)}, śr. {worst['D1_base'].mean():.2f} pp): z protokołem śr. {worst['D1_gate0'].mean():.2f} (lag0) / {worst['D1_gate1'].mean():.2f} (lag1) → Δ {(worst['D1_gate0']-worst['D1_base']).mean():+.2f} / {(worst['D1_gate1']-worst['D1_base']).mean():+.2f} pp.")
q95 = df["D1_base"].quantile(.95); best = df[df["D1_base"] >= q95]
P(f"5 % najlepszych tygodni bazy (n={len(best)}, śr. {best['D1_base'].mean():.2f}): z protokołem {best['D1_gate0'].mean():.2f} → Δ {(best['D1_gate0']-best['D1_base']).mean():+.2f} pp.")
OUT["ogon"] = dict(worst5_base=worst['D1_base'].mean(), worst5_gate0=worst['D1_gate0'].mean(), worst5_gate1=worst['D1_gate1'].mean(),
                   best5_base=best['D1_base'].mean(), best5_gate0=best['D1_gate0'].mean())

# ------------------------------------------------------------------ 3. losowe koszyki (szum)
P("\n## 2. Losowe koszyki 5/5 (200 losowań/tydzień, te same okna, od D+1) — co bramka robi na SZUMIE\n")
rb = np.array(rand_rows["base"]).reshape(-1, NRAND); rg0 = np.array(rand_rows["gate0"]).reshape(-1, NRAND); rg1 = np.array(rand_rows["gate1"]).reshape(-1, NRAND)
def strat_stats(M):
    m = M.mean(axis=0); p5 = np.percentile(M, 5, axis=0); sd = M.std(axis=0, ddof=1)
    cum = np.cumsum(M, axis=0); mdd = (cum - np.maximum.accumulate(cum, axis=0)).min(axis=0)
    return m, sd, p5, mdd
mb, sdb, p5b, mddb = strat_stats(rb); mg, sdg, p5g, mddg = strat_stats(rg0); mg1, sdg1, p5g1, mddg1 = strat_stats(rg1)
P("| | baza | protokół lag0 | protokół lag1 |\n|---|---|---|---|")
P(f"| śr. pp/tydz. (śr. po 200 strategiach) | {mb.mean():+.3f} | {mg.mean():+.3f} (Δ {np.mean(mg-mb):+.3f}, szkodzi w {np.mean(mg<mb):.0%}) | {mg1.mean():+.3f} (Δ {np.mean(mg1-mb):+.3f}, szkodzi w {np.mean(mg1<mb):.0%}) |")
P(f"| σ tyg. | {sdb.mean():.2f} | {sdg.mean():.2f} | {sdg1.mean():.2f} |")
P(f"| p5 tyg. | {p5b.mean():.2f} | {p5g.mean():.2f} (Δ {np.mean(p5g-p5b):+.2f}) | {p5g1.mean():.2f} (Δ {np.mean(p5g1-p5b):+.2f}) |")
P(f"| maxDD skum. | {mddb.mean():.1f} | {mddg.mean():.1f} (Δ {np.mean(mddg-mddb):+.1f}) | {mddg1.mean():.1f} (Δ {np.mean(mddg1-mddb):+.1f}) |")
pooled_b = rb.ravel(); pooled_g = rg0.ravel()
P(f"Pooled (n={len(pooled_b)}): p5 {np.percentile(pooled_b,5):.2f} → {np.percentile(pooled_g,5):.2f}; p1 {np.percentile(pooled_b,1):.2f} → {np.percentile(pooled_g,1):.2f}; σ {pooled_b.std():.2f} → {pooled_g.std():.2f}.")
OUT["losowe"] = dict(d_mean_lag0=float(np.mean(mg-mb)), d_mean_lag1=float(np.mean(mg1-mb)), d_p5_lag0=float(np.mean(p5g-p5b)), d_p5_lag1=float(np.mean(p5g1-p5b)),
                     d_maxDD_lag0=float(np.mean(mddg-mddb)), d_maxDD_lag1=float(np.mean(mddg1-mddb)), sd_base=float(sdb.mean()), sd_gate0=float(sdg.mean()),
                     pooled_p5=[float(np.percentile(pooled_b,5)), float(np.percentile(pooled_g,5))], pooled_p1=[float(np.percentile(pooled_b,1)), float(np.percentile(pooled_g,1))])

# ------------------------------------------------------------------ 4. reżimy: VIX, rok, ruch indeksu
P("\n## 3. Protokół (od D+1, lag0) wg reżimu — czy w VIX>25 bramka pomaga?\n")
P("reżim | n | baza śr. | protokół śr. | Δ śr. | t(Δ) | baza p5 | protokół p5 | baza min | protokół min | baza maxDD | protokół maxDD")
P("|".join(["---"] * 12))
REG = {}
def reg_row(name, m):
    sub = df[m]
    if len(sub) < 5: return
    sb, sg = tail(sub["D1_base"]), tail(sub["D1_gate0"]); d = diff(sub["D1_gate0"], sub["D1_base"])
    REG[name] = dict(n=len(sub), base=sb["mean"], gate=sg["mean"], d=d["mean"], t=d["t"], p5=[sb["p5"], sg["p5"]], min=[sb["min"], sg["min"]], maxDD=[sb["maxDD"], sg["maxDD"]])
    P(f"{name} | {len(sub)} | {sb['mean']:+.2f} | {sg['mean']:+.2f} | {d['mean']:+.2f} | {d['t']:+.2f} | {sb['p5']:.2f} | {sg['p5']:.2f} | {sb['min']:.1f} | {sg['min']:.1f} | {sb['maxDD']:.1f} | {sg['maxDD']:.1f}")
reg_row("VIX(D0) > 25", df.vix0 > 25); reg_row("VIX(D0) 20–25", (df.vix0 > 20) & (df.vix0 <= 25)); reg_row("VIX(D0) ≤ 20", df.vix0 <= 20)
reg_row("VIX(D0) > 20", df.vix0 > 20)
for y in sorted(df.year.unique()): reg_row(f"rok {y}", df.year == y)
reg_row("^NDX w oknie ≤ −2 %", df.ndx_w <= -2); reg_row("^NDX w oknie > −2 %", df.ndx_w > -2); reg_row("^NDX w oknie ≥ +2 %", df.ndx_w >= 2)
OUT["rezimy"] = REG

# ------------------------------------------------------------------ 5. kapitał przy ALLOC 0,24: P(kill −25 %) z/bez bramki
P("\n## 4. Ścieżka kapitału przy ALLOC 0,24 (1,2 × spread dzienny): P(kill switch −25 % od szczytu okna) z/bez protokołu\n")
dd = dd.sort_index()
def kill_prob(series, weeks, lvl=0.75):
    r = 1 + 1.2 * series.values / 100
    starts = sorted(set(dd.d0)); hits = 0; tot = 0; dds = []
    d0arr = dd.d0.values
    for si, s0 in enumerate(starts):
        if si + weeks > len(starts): break
        s1 = starts[si + weeks - 1]
        m = (d0arr >= s0) & (d0arr <= s1)
        path = np.cumprod(r[m]); peak = np.maximum.accumulate(np.maximum(path, 1.0))
        mdd = (path / peak - 1).min(); dds.append(mdd)
        hits += mdd <= lvl - 1; tot += 1
    return hits / tot, tot, np.percentile(dds, 5), np.median(dds)
KILL = {}
for weeks in (4, 12, 26):
    pb, nb, p5b_, medb = kill_prob(dd.spread, weeks); pg, ng, p5g_, medg = kill_prob(dd.spread_gate, weeks)
    KILL[weeks] = dict(base=pb, gate=pg, n=nb, dd_p5=[p5b_, p5g_], dd_med=[medb, medg])
    P(f"- okna {weeks} tyg. (n={nb}): P(kill) baza {pb:.1%} → protokół {pg:.1%}; DD p5 {p5b_:.1%} → {p5g_:.1%}; mediana DD {medb:.1%} → {medg:.1%}")
OUT["kill"] = KILL
# σ dzienna kapitału
P(f"σ dzienna spreadu: baza {dd.spread.std():.2f} pp → protokół {dd.spread_gate.std():.2f} pp; σ dz. kapitału (×1,2): {1.2*dd.spread.std():.2f} % → {1.2*dd.spread_gate.std():.2f} %; najgorszy dzień {dd.spread.min():.2f} → {dd.spread_gate.min():.2f} pp.")
OUT["sigma_dz"] = dict(base=float(dd.spread.std()), gate=float(dd.spread_gate.std()), worst_day=[float(dd.spread.min()), float(dd.spread_gate.min())])

# ------------------------------------------------------------------ 6. „dzień ≤ −3 pp” — stabilność
P("\n## 5. Sygnał „dzień ze spreadem koszyka ≤ −3 pp” → suma kolejnych 3 sesji (seria dzienna koszyka momentum od D+1)\n")
sp = dd.spread
nxt = sp.shift(-1) + sp.shift(-2) + sp.shift(-3)
valid = nxt.notna()
def hac_t(x, lag=3):
    x = np.asarray(x, float); n = len(x); m = x.mean(); e = x - m
    s = (e @ e) / n
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); s += 2 * w * (e[l:] @ e[:-l]) / n
    return m / math.sqrt(s / n)
def cond(name, mask):
    m = mask & valid
    x = nxt[m]; n = len(x)
    if n < 5: P(f"- {name}: n={n} — za mało"); return None
    u = nxt[valid & (sp > -3) & (sp < 3)] if True else None
    t_naive = x.mean() / x.std(ddof=1) * math.sqrt(n); t_hac = hac_t(x.values)
    # nienakładające się: po zdarzeniu pomiń 3 sesje
    idx = np.where(m.values)[0]; keep = []; last = -10
    for i in idx:
        if i - last > 3: keep.append(i); last = i
    xn = nxt.iloc[keep]
    r = dict(n=n, mean=x.mean(), sd=x.std(ddof=1), t_naive=t_naive, t_hac=t_hac, n_nonov=len(xn), mean_nonov=xn.mean(),
             t_nonov=xn.mean() / xn.std(ddof=1) * math.sqrt(len(xn)), hit=(x > 0).mean(), median=x.median())
    P(f"- {name}: n={n} (nienakł. {len(xn)}), śr. {x.mean():+.2f} pp (mediana {x.median():+.2f}, hit {r['hit']:.0%}), σ {x.std():.2f}, t naiwne {t_naive:.2f}, t HAC(3) {t_hac:.2f}, nienakł. śr. {xn.mean():+.2f} t {r['t_nonov']:.2f}")
    return r
M3 = {}
uncond = nxt[valid]; M3["bezwarunkowo"] = dict(n=int(len(uncond)), mean=float(uncond.mean()), t=float(uncond.mean()/uncond.std()*math.sqrt(len(uncond))))
P(f"- bezwarunkowo (wszystkie dni): n={len(uncond)}, śr. sumy 3 sesji {uncond.mean():+.2f} pp (σ {uncond.std():.2f}, t {M3['bezwarunkowo']['t']:.2f}) — to jest właściwy punkt odniesienia, nie 0")
M3["<=-3"] = cond("po dniu ≤ −3 pp", sp <= -3)
M3[">=+3"] = cond("po dniu ≥ +3 pp", sp >= 3)
M3["<=-3_bez2022"] = cond("po dniu ≤ −3 pp, bez 2022", (sp <= -3) & (dd.year != 2022))
for y in sorted(dd.year.unique()): M3[f"<=-3_{y}"] = cond(f"po dniu ≤ −3 pp, rok {y}", (sp <= -3) & (dd.year == y))
M3["<=-3_ndx<=-2"] = cond("po dniu ≤ −3 pp, gdy ^NDX tego dnia ≤ −2 %", (sp <= -3) & (dd.ndx <= -2))
M3["<=-3_ndx>-2"] = cond("po dniu ≤ −3 pp, gdy ^NDX tego dnia > −2 %", (sp <= -3) & (dd.ndx > -2))
M3["<=-3_|ndx|<1"] = cond("po dniu ≤ −3 pp, gdy |^NDX| tego dnia < 1 % (spread własny, nie indeks)", (sp <= -3) & (dd.ndx.abs() < 1))
M3["<=-3_vix>25"] = cond("po dniu ≤ −3 pp, VIX > 25", (sp <= -3) & (dd.vix > 25))
M3["<=-3_vix<=25"] = cond("po dniu ≤ −3 pp, VIX ≤ 25", (sp <= -3) & (dd.vix <= 25))
M3["<=-5"] = cond("po dniu ≤ −5 pp", sp <= -5)
M3["2dni<=-4"] = cond("po DWÓCH sesjach o sumie ≤ −4 pp (analog potwierdzenia 2. sesją)", (sp + sp.shift(1)) <= -4)
M3["2dni<=-4_obie<0"] = cond("po dwóch sesjach ≤ −2 pp każda", (sp <= -2) & (sp.shift(1) <= -2))
# czy odbicie to indeks czy spread własny? regresja nxt na przyszły ^NDX
nx_ndx = dd.ndx.shift(-1) + dd.ndx.shift(-2) + dd.ndx.shift(-3)
mm = (sp <= -3) & valid & nx_ndx.notna()
b = np.polyfit(nx_ndx[mm], nxt[mm], 1)
P(f"- po dniu ≤ −3 pp: ^NDX w kolejnych 3 sesjach śr. {nx_ndx[mm].mean():+.2f} % (bezwar. {nx_ndx[valid & nx_ndx.notna()].mean():+.2f} %); β spreadu(3 ses.) na ^NDX(3 ses.) = {b[0]:.2f}, stała {b[1]:+.2f} pp — część odbicia niezależna od indeksu")
M3["ndx_po"] = dict(mean=float(nx_ndx[mm].mean()), uncond=float(nx_ndx[valid & nx_ndx.notna()].mean()), beta=float(b[0]), const=float(b[1]))
# spread liczony z bramką: czy po dniu ≤ −3 protokół obcina odbicie?
g = dd.spread_gate; nxt_g = g.shift(-1) + g.shift(-2) + g.shift(-3)
mm2 = (sp <= -3) & valid
P(f"- po dniu ≤ −3 pp: kolejne 3 sesje bez reakcji {nxt[mm2].mean():+.2f} pp vs z protokołem (wagi po reakcjach) {nxt_g[mm2].mean():+.2f} pp → koszt protokołu po złym dniu {(nxt_g[mm2]-nxt[mm2]).mean():+.2f} pp (t sparowane {((nxt_g[mm2]-nxt[mm2]).mean()/(nxt_g[mm2]-nxt[mm2]).std()*math.sqrt(mm2.sum())):.2f})")
M3["koszt_po_-3"] = dict(mean=float((nxt_g[mm2]-nxt[mm2]).mean()), t=float((nxt_g[mm2]-nxt[mm2]).mean()/(nxt_g[mm2]-nxt[mm2]).std()*math.sqrt(mm2.sum())))
OUT["dzien_minus3"] = {k: ({kk: (float(vv) if isinstance(vv, (int, float, np.floating, np.integer)) else vv) for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in M3.items()}

# ------------------------------------------------------------------ 7. przekrój REDUCE: reżimy, lata, strony
P("\n## 6. Przekrój: pierwszy sygnał REDUCE (rel ≤ −4 dwie sesje, abs ≤ −4) w sesjach 2..K−1 od D0 → reszta okna (pp rel.)\n")
def cstats(sub, col="rest"):
    if len(sub) == 0: return dict(n=0)
    g = sub.groupby("d0")[col].mean()
    tcl = g.mean() / (g.std(ddof=1) / math.sqrt(len(g))) if len(g) > 1 else float("nan")
    return dict(n=int(len(sub)), n_okien=int(len(g)), mean=float(sub[col].mean()), sd=float(sub[col].std()), t_cl=float(tcl), hit=float((sub[col] > 0).mean()))
P("podzbiór | n | okien | śr. reszta pp | σ | t (klastr. po d0) | hit>0")
P("|".join(["---"] * 7))
CSR = {}
def crow(name, sub):
    s = cstats(sub); CSR[name] = s
    if s["n"] == 0: P(f"{name} | 0"); return
    P(f"{name} | {s['n']} | {s['n_okien']} | {s['mean']:+.2f} | {s['sd']:.2f} | {s['t_cl']:+.2f} | {s['hit']:.1%}")
crow("wszystkie", CS); crow("long", CS[CS.side == "L"]); crow("short", CS[CS.side == "S"])
crow("poziom CLOSE (rel/abs ≤ −8 dwie sesje)", CS[CS.close_lvl]); crow("tylko REDUCE", CS[~CS.close_lvl])
crow("long top-kwintyl mom6M (jak koszyk)", CS[(CS.side == "L") & (CS.q == 4)]); crow("short dolny kwintyl mom6M", CS[(CS.side == "S") & (CS.q == 0)])
crow("koszykowe (top-L + bot-S)", CS[((CS.side == "L") & (CS.q == 4)) | ((CS.side == "S") & (CS.q == 0))])
crow("VIX(sygnał) > 25", CS[CS.vix_sig > 25]); crow("VIX(sygnał) 20–25", CS[(CS.vix_sig > 20) & (CS.vix_sig <= 25)]); crow("VIX(sygnał) ≤ 20", CS[CS.vix_sig <= 20])
crow("VIX > 25, koszykowe", CS[(CS.vix_sig > 25) & (((CS.side == "L") & (CS.q == 4)) | ((CS.side == "S") & (CS.q == 0)))])
for y in sorted(CS.year.unique()): crow(f"rok {y}", CS[CS.year == y])
crow("sygnał w sesji 2", CS[CS.j == 2]); crow("sygnał w sesji 3", CS[CS.j == 3]); crow("sygnał w sesji 4", CS[CS.j == 4])
crow("^NDX od D0 do sygnału ≤ −3 %", CS[CS.ndx_sig <= -3]); crow("^NDX od D0 do sygnału > −3 %", CS[CS.ndx_sig > -3])
OUT["przekroj"] = CSR
# ogon reszty: czy po sygnale ogon „reszty” jest grubszy niż bezwarunkowo? (p5 reszty)
P(f"\nRozkład reszty po sygnale REDUCE: p5 {CS.rest.quantile(.05):.2f}, p95 {CS.rest.quantile(.95):.2f}, σ {CS.rest.std():.2f} pp (asymetria {CS.rest.skew():.2f}); poziom CLOSE: p5 {CS[CS.close_lvl].rest.quantile(.05):.2f}, p95 {CS[CS.close_lvl].rest.quantile(.95):.2f}.")
OUT["przekroj_ogon"] = dict(p5=float(CS.rest.quantile(.05)), p95=float(CS.rest.quantile(.95)), sd=float(CS.rest.std()), skew=float(CS.rest.skew()))

# ------------------------------------------------------------------ 8. W1–W7 in-sample: od D0 vs od D+1, lag 0/1
P("\n## 7. In-sample W1–W7: protokół od D0 (jak audyt) vs od D+1 (pon., proxy fills), cięcie lag 0/1\n")
W = {"W1": ("2026-08-26", "2026-08-28"), "W2": ("2026-08-28", "2026-09-04"), "W3": ("2026-09-04", "2026-09-11"),
     "W4": ("2026-09-11", "2026-09-28"), "W5": ("2026-09-28", "2026-10-02"), "W6": ("2026-10-02", "2026-10-09"), "W7": ("2026-10-09", "2026-10-16")}
BASKETS = {"W1": (["MU","LITE","CEG","AMD","MSFT"], ["INTU","WDAY","APP","TSLA","CMCSA"]), "W2": (["MU","NVDA","MSFT","AMD","CEG"], ["INTU","APP","TSLA","CMCSA","PEP"]),
           "W3": (["MU","NVDA","AMD","AVGO","STX"], ["TSLA","INTU","SBUX","APP","CMCSA"]), "W4": (["MU","AMD","AVGO","MRVL","LITE"], ["INTU","SBUX","CMCSA","APP","ADSK"]),
           "W5": (["MU","AMD","ALAB","STX","TER"], ["SBUX","NFLX","PEP","CMCSA","APP"]), "W6": (["MU","LITE","TER","AMAT","AMD"], ["APP","NFLX","PAYX","CMCSA","SBUX"]),
           "W7": (["MU","LITE","MRVL","PANW","CSCO"], ["CMCSA","SBUX","PEP","TMUS","APP"])}
def sim_week(Lg, Sh, ia, ib, lag, strict=True, second=True, stop=False):
    tot = {}
    sub = px[Lg + Sh].iloc[ia:ib + 1]; nd = ndx.iloc[ia:ib + 1]
    lr = (sub / sub.iloc[0] - 1).values * 100; ln = ((nd / nd.iloc[0] - 1).values * 100)[:, None]
    segr = np.diff(sub.values, axis=0) / sub.values[:-1] * 100 - (np.diff(nd.values) / nd.values[:-1] * 100)[:, None]
    vals = []; nre = 0
    for j, t in enumerate(Lg + Sh):
        sgn = 1 if j < 5 else -1
        rel = sgn * (lr[:, [j]] - ln); ab = sgn * lr[:, [j]]; seg = sgn * segr[:, [j]]
        Wm, fR, fC = protocol_weights(rel, ab, lag=lag, strict_close=strict, second=second)
        vals.append(((Wm * seg).sum(), seg.sum())); nre += int(fR[0] <= len(seg)) + int(fC[0] <= len(seg))
    g = np.mean([v[0] for v in vals[:5]]) + np.mean([v[0] for v in vals[5:]]); b = np.mean([v[1] for v in vals[:5]]) + np.mean([v[1] for v in vals[5:]])
    return b, g, nre
WK = {}
P("tydzień | baza D0 | protokół D0 lag0 (audyt-CLOSE) | protokół D0 lag0 (ścisły CLOSE) | protokół D0 lag1 | baza D+1 | protokół D+1 lag0 | protokół D+1 lag1 | D+1 bez 2. sesji")
P("|".join(["---"] * 9))
tot = dict(b0=0, a0=0, s0=0, l1=0, b1=0, g1=0, g11=0, n1=0)
for w, (d0, d1) in W.items():
    Lg, Sh = BASKETS[w]; i0, i1 = pos[pd.Timestamp(d0)], pos[pd.Timestamp(d1)]
    b0, a0, _ = sim_week(Lg, Sh, i0, i1, 0, strict=False); _, s0, _ = sim_week(Lg, Sh, i0, i1, 0, strict=True); _, l1, _ = sim_week(Lg, Sh, i0, i1, 1, strict=False)
    ib = min(i1 + 1, len(dates) - 1)
    b1, g1, nr = sim_week(Lg, Sh, i0 + 1, ib, 0, strict=False); _, g11, _ = sim_week(Lg, Sh, i0 + 1, ib, 1, strict=False); _, n1, _ = sim_week(Lg, Sh, i0 + 1, ib, 0, strict=False, second=False)
    WK[w] = dict(b0=b0, a0=a0, s0=s0, l1=l1, b1=b1, g1=g1, g11=g11, n1=n1)
    for kk, vv in WK[w].items(): tot[kk] += vv
    P(f"{w} | {b0:+.2f} | {a0:+.2f} | {s0:+.2f} | {l1:+.2f} | {b1:+.2f} | {g1:+.2f} | {g11:+.2f} | {n1:+.2f}")
P(f"SUMA | {tot['b0']:+.2f} | {tot['a0']:+.2f} (Δ {tot['a0']-tot['b0']:+.2f}) | {tot['s0']:+.2f} (Δ {tot['s0']-tot['b0']:+.2f}) | {tot['l1']:+.2f} (Δ {tot['l1']-tot['b0']:+.2f}) | {tot['b1']:+.2f} | {tot['g1']:+.2f} (Δ {tot['g1']-tot['b1']:+.2f}) | {tot['g11']:+.2f} (Δ {tot['g11']-tot['b1']:+.2f}) | {tot['n1']:+.2f} (Δ {tot['n1']-tot['b1']:+.2f})")
P("Uwaga: okno D+1 dla W7 kończy się 16.10 (brak sesji D5+1 w danych) — W7 od D+1 to 12.10→16.10.")
OUT["W1_W7"] = dict(tyg=WK, suma=tot)

json.dump(OUT, open(OUTJ, "w"), indent=1, ensure_ascii=False, default=float)
df.to_csv(f"{BASE}/analiza/weryfikacja_C7_serie.csv"); dd.to_csv(f"{BASE}/analiza/weryfikacja_C7_dzienne.csv"); CS.to_csv(f"{BASE}/analiza/weryfikacja_C7_przekroj.csv", index=False)
open(OUTMD, "w").write("\n".join(L))
