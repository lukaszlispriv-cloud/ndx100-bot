#!/usr/bin/env python3
"""
weryfikacja_C2.py — próba obalenia twierdzenia C2 (b_pary / a_branza na mom6 obniża σ o ~24%
przy Δśr.≈0). Korzysta z harnessu bt_neutralnosc.py (te same dane, sygnał, okna, koszty).

Testy:
 T1 reprodukcja + statystyka odporna (bootstrap σ-ratio, CI Δ, MAD, σ bez ogonów, F-test)
 T2 kontrola: losowa taksonomia (permutacja etykiet branż między spółkami) — czy sama
    struktura parowa / limit 1L+1S obniża σ niezależnie od branży
 T3 taksonomia point-in-time: klastry korelacyjne z 252 sesji ≤ D0 (bez look-ahead)
 T4 wrażliwość: sector-only, industry-only, MIN_IND, MIN_GROUP
 T5 stabilność: połówki, lata
 T6 udział semis/software w parach, wariant bez pary semis, para GOOG/GOOGL
"""
import json, math, os, random, sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_neutralnosc as B

OUT_JSON = os.path.join(B.OUT_DIR, "weryfikacja_C2_wyniki.json")
OUT_TXT = os.path.join(B.OUT_DIR, "weryfikacja_C2_out.txt")
_log = open(OUT_TXT, "w")
def P_(*a):
    s = " ".join(str(x) for x in a); print(s); _log.write(s + "\n"); _log.flush()

RES = {}

# ------------------------------------------------------------------ dane / cache okien
df, tickers = B.load()
ind, missing = B.load_industry(tickers)
Pm = df[tickers].to_numpy(dtype=float)
ndx = df["^NDX"].to_numpy(dtype=float)
vix = df["^VIX"].to_numpy(dtype=float)
we = B.week_ends(df.index)
cfg = B.SIGNALS["mom6"]
hist = max(cfg["win"] + cfg["skip"], B.BETA_WIN + 1)
windows = [(we[k], we[k + 1]) for k in range(len(we) - 1) if we[k] >= hist]
dates = df.index

WIN = []
for d0, d5 in windows:
    sig = B.signals_at(Pm, ndx, d0, tickers, cfg["win"], cfg["skip"])
    r_ndx = ndx[d5] / ndx[d0] - 1
    fwd = {}
    for t in sig:
        j = tickers.index(t)
        if not np.isnan(Pm[d5, j]):
            fwd[t] = Pm[d5, j] / Pm[d0, j] - 1
    sig = {t: sig[t] for t in fwd}
    WIN.append(dict(d0=d0, d5=d5, date=dates[d0].date().isoformat(), year=dates[d0].year,
                    sig=sig, fwd=fwd, r_ndx=r_ndx, vix=float(vix[d0])))
P_(f"okien: {len(WIN)}, uniwersum/okno: {min(len(w['sig']) for w in WIN)}–{max(len(w['sig']) for w in WIN)}, brak w TV: {missing}")

# ------------------------------------------------------------------ harness
def grouping_with(universe, indmap, min_ind=B.MIN_IND, min_group=B.MIN_GROUP, mode="base"):
    if mode == "sector":
        g = {t: indmap[t][1] for t in universe}
    elif mode == "industry":
        g = {t: indmap[t][0] for t in universe}
    else:
        ic = Counter(indmap[t][0] for t in universe)
        g = {t: (indmap[t][0] if ic[indmap[t][0]] >= min_ind else indmap[t][1]) for t in universe}
    gc = Counter(g.values())
    return {t: (g[t] if gc[g[t]] >= min_group else "Pozostałe") for t in universe}

def pick_pairs(sig, grp, min_group=B.MIN_GROUP, exclude_groups=(), only_groups=None):
    gm = defaultdict(list)
    for t in sig:
        if grp[t] != "Pozostałe": gm[grp[t]].append(t)
    pairs = []
    for g, ts in gm.items():
        if len(ts) < min_group or g in exclude_groups: continue
        if only_groups is not None and g not in only_groups: continue
        ts = sorted(ts, key=lambda t: -sig[t]["mom"])
        pairs.append((sig[ts[0]]["mom"] - sig[ts[-1]]["mom"], ts[0], ts[-1], g))
    pairs.sort(reverse=True)
    pairs = pairs[:B.N_LEG]
    return [p[1] for p in pairs], [p[2] for p in pairs], [p[3] for p in pairs]

def run(variant, grp_fn, **kw):
    """variant: none | pairs | neutral ; grp_fn(window_idx, sig) -> grp dict. Zwraca listę wierszy."""
    rows = []; prev = {}
    for i, w in enumerate(WIN):
        sig = w["sig"]
        if variant == "none":
            lo, sh = B.pick_plain(sig); groups = []
        else:
            grp = grp_fn(i, sig)
            if variant == "pairs":
                lo, sh, groups = pick_pairs(sig, grp, **kw)
                if len(lo) < 3: continue
            elif variant == "neutral":
                lo, sh = B.pick_industry_neutral(sig, grp); groups = [grp[t] for t in lo] + [grp[t] for t in sh]
        wts = B.w_equal(lo, sh)
        ev = B.evaluate(wts, w["fwd"], w["r_ndx"])
        cost_rot, dw = B.turnover_cost(wts, prev); prev = wts
        fin = B.FIN_YEAR / 52.0 * ev["gross"]
        ranks = sorted(sig, key=lambda t: -sig[t]["mom"]); rk = {t: k for k, t in enumerate(ranks)}
        rows.append(dict(date=w["date"], year=w["year"], i=i, spread=ev["spread"], long=ev["long"], short=ev["short"],
                         cost=cost_rot + fin, lo=lo, sh=sh, groups=groups, n_legs=len(lo) + len(sh),
                         ext=float(np.mean([sig[t]["mom"] for t in lo]) - np.mean([sig[t]["mom"] for t in sh])),
                         rank_lo=float(np.mean([rk[t] for t in lo])), rank_sh=float(np.mean([len(ranks) - 1 - rk[t] for t in sh])),
                         vix=w["vix"]))
    return rows

def stats(rows, label=""):
    sp = np.array([r["spread"] for r in rows]); n = len(sp)
    m = sp.mean(); s = sp.std(ddof=1)
    net = np.array([r["spread"] - r["cost"] for r in rows])
    srt = np.sort(sp)
    return dict(label=label, n=n, mean=float(m), sd=float(s), t=float(m / s * math.sqrt(n)), sharpe=float(m / s * math.sqrt(52)),
                worst=float(sp.min()), worst5=[float(x) for x in srt[:5]], mdd=float(B.max_drawdown(list(sp))),
                net_mean=float(net.mean()), net_t=float(net.mean() / net.std(ddof=1) * math.sqrt(n)),
                mad=float(np.median(np.abs(sp - np.median(sp)))), hit=float((sp > 0).mean()),
                ext=float(np.mean([r["ext"] for r in rows])), rank_lo=float(np.mean([r["rank_lo"] for r in rows])),
                rank_sh=float(np.mean([r["rank_sh"] for r in rows])), cost=float(np.mean([r["cost"] for r in rows])))

def compare(rows, base, nboot=4000, seed=7):
    """porównanie parami na wspólnych oknach: Δśr. + CI, stosunek σ + bootstrap CI, F-test (log-F normalny), MAD ratio, σ bez ogonów."""
    bm = {r["date"]: r["spread"] for r in base}
    pr = [(r["spread"], bm[r["date"]]) for r in rows if r["date"] in bm]
    a = np.array([p[0] for p in pr]); b = np.array([p[1] for p in pr]); n = len(a)
    d = a - b
    rng = np.random.default_rng(seed)
    ratios = []; dms = []
    for _ in range(nboot):
        idx = rng.integers(0, n, n)
        ratios.append(a[idx].std(ddof=1) / b[idx].std(ddof=1)); dms.append(d[idx].mean())
    ratios = np.sort(ratios); dms = np.sort(dms)
    vr = b.var(ddof=1) / a.var(ddof=1)
    z = math.log(vr) / math.sqrt(4.0 / (n - 1)); p_f = 0.5 * math.erfc(z / math.sqrt(2))
    # permutacyjny test σ: losowo zamieniaj a_i <-> b_i (parami) — H0: rozkłady spreadów identyczne w oknie
    perm = []
    for _ in range(nboot):
        sw = rng.random(n) < 0.5
        aa = np.where(sw, b, a); bb = np.where(sw, a, b)
        perm.append(aa.std(ddof=1) / bb.std(ddof=1))
    p_perm = float(np.mean(np.array(perm) <= a.std(ddof=1) / b.std(ddof=1)))
    def trim(x, k):
        s = np.sort(x); return s[k:n - k].std(ddof=1)
    return dict(n=n, d_mean=float(d.mean()), d_se=float(d.std(ddof=1) / math.sqrt(n)), d_t=float(d.mean() / d.std(ddof=1) * math.sqrt(n)),
                d_ci95=[float(dms[int(0.025 * nboot)]), float(dms[int(0.975 * nboot)])],
                sigma_ratio=float(a.std(ddof=1) / b.std(ddof=1)),
                sigma_ratio_ci95=[float(ratios[int(0.025 * nboot)]), float(ratios[int(0.975 * nboot)])],
                p_F=p_f, p_perm_sigma=p_perm,
                mad_ratio=float(np.median(np.abs(a - np.median(a))) / np.median(np.abs(b - np.median(b)))),
                sigma_ratio_trim2=float(trim(a, 2) / trim(b, 2)), sigma_ratio_trim6=float(trim(a, 6) / trim(b, 6)),
                sigma_ratio_trim12=float(trim(a, 12) / trim(b, 12)),
                corr=float(np.corrcoef(a, b)[0, 1]),
                worst_a=float(a.min()), worst_b=float(b.min()),
                sd_a=float(a.std(ddof=1)), sd_b=float(b.std(ddof=1)), mean_a=float(a.mean()), mean_b=float(b.mean()))

def fmt(x, d=2): return f"{x:.{d}f}"

# ------------------------------------------------------------------ T1 reprodukcja
P_("\n=== T1 REPRODUKCJA (mom6, 233 okna) + statystyka odporna ===")
grp_base = lambda i, sig: grouping_with(list(sig), ind)
NONE = run("none", None)
PAIRS = run("pairs", grp_base)
NEUT = run("neutral", grp_base)
S_none, S_pairs, S_neut = stats(NONE, "none"), stats(PAIRS, "b_pary"), stats(NEUT, "a_branza")
for s in (S_none, S_pairs, S_neut):
    P_(f"{s['label']:10s} n={s['n']} śr {fmt(s['mean'])} σ {fmt(s['sd'])} t {fmt(s['t'])} Sh {fmt(s['sharpe'])} worst {fmt(s['worst'],1)} "
       f"worst5 {[round(x,1) for x in s['worst5']]} mdd {fmt(s['mdd'],1)} MAD {fmt(s['mad'])} netto {fmt(s['net_mean'])} (t {fmt(s['net_t'])}) "
       f"ekstremalność mom L−S {fmt(s['ext'],1)} pp; śr. ranga L {fmt(s['rank_lo'],1)} / S {fmt(s['rank_sh'],1)}; koszt {fmt(s['cost'],3)}")
C_pairs = compare(PAIRS, NONE); C_neut = compare(NEUT, NONE)
for lab, c in (("b_pary", C_pairs), ("a_branza", C_neut)):
    P_(f"{lab} vs none: Δśr {fmt(c['d_mean'])} ± SE {fmt(c['d_se'])} (t {fmt(c['d_t'])}, CI95 {[round(x,2) for x in c['d_ci95']]}) | "
       f"σ-ratio {fmt(c['sigma_ratio'],3)} CI95 {[round(x,3) for x in c['sigma_ratio_ci95']]} | F p={c['p_F']:.2g} perm p={c['p_perm_sigma']:.3f} | "
       f"MAD-ratio {fmt(c['mad_ratio'],3)} | σ-ratio bez 2/6/12 ogonów {fmt(c['sigma_ratio_trim2'],3)}/{fmt(c['sigma_ratio_trim6'],3)}/{fmt(c['sigma_ratio_trim12'],3)} | corr {fmt(c['corr'],2)}")
RES["T1"] = dict(none=S_none, pairs=S_pairs, neut=S_neut, cmp_pairs=C_pairs, cmp_neut=C_neut)

# liczba nóg w b_pary (czy zawsze 5 par?)
nl = Counter(r["n_legs"] for r in PAIRS); P_(f"b_pary liczba nóg/okno: {dict(nl)}")
# wspólne nogi
ov = [len(set(p["lo"] + p["sh"]) & set(n["lo"] + n["sh"])) for p, n in zip(PAIRS, NONE)]
P_(f"b_pary wspólne nogi z none: śr. {np.mean(ov):.2f}/10")

# ------------------------------------------------------------------ T2 losowa taksonomia
P_("\n=== T2 KONTROLA: losowa taksonomia (permutacja etykiet industry/sector między spółkami; stała w czasie) ===")
NPERM = 300
rng = random.Random(123)
null = {"pairs": [], "neutral": []}
all_tk = sorted(ind)
for k in range(NPERM):
    vals = [ind[t] for t in all_tk]; rng.shuffle(vals)
    fake = dict(zip(all_tk, vals))
    gf = lambda i, sig, fake=fake: grouping_with(list(sig), fake)
    for v in ("pairs", "neutral"):
        rows = run(v, gf)
        s = stats(rows); c = compare(rows, NONE, nboot=1)
        null[v].append(dict(mean=s["mean"], sd=s["sd"], t=s["t"], worst=s["worst"], ext=s["ext"], mdd=s["mdd"], d_mean=c["d_mean"], sigma_ratio=c["sigma_ratio"]))
def pctile(arr, x, lower=True):
    arr = np.array(arr); return float(np.mean(arr <= x)) if lower else float(np.mean(arr >= x))
for v, real in (("pairs", (S_pairs, C_pairs)), ("neutral", (S_neut, C_neut))):
    N = null[v]
    sds = [x["sd"] for x in N]; ms = [x["mean"] for x in N]; ws = [x["worst"] for x in N]; sr = [x["sigma_ratio"] for x in N]; ts = [x["t"] for x in N]; ex = [x["ext"] for x in N]
    P_(f"{v:8s} losowa taksonomia ({NPERM} perm.): σ med {np.median(sds):.2f} [p5 {np.percentile(sds,5):.2f}, p95 {np.percentile(sds,95):.2f}] | "
       f"σ-ratio med {np.median(sr):.3f} [p5 {np.percentile(sr,5):.3f}, p95 {np.percentile(sr,95):.3f}] | śr med {np.median(ms):.2f} [p5 {np.percentile(ms,5):.2f}, p95 {np.percentile(ms,95):.2f}] | "
       f"t med {np.median(ts):.2f} | worst med {np.median(ws):.1f} | ekstremalność med {np.median(ex):.1f}")
    P_(f"         REAL: σ {real[0]['sd']:.2f} (udział perm. z σ ≤ real: {pctile(sds, real[0]['sd']):.3f}) | śr {real[0]['mean']:.2f} (udział perm. ze śr ≥ real: {pctile(ms, real[0]['mean'], False):.3f}) | "
       f"t {real[0]['t']:.2f} (udział perm. z t ≥ real: {pctile(ts, real[0]['t'], False):.3f}) | worst {real[0]['worst']:.1f} (udział perm. z worst ≤ real: {pctile(ws, real[0]['worst']):.3f})")
RES["T2"] = {v: dict(sd_med=float(np.median([x["sd"] for x in null[v]])), sd_p5=float(np.percentile([x["sd"] for x in null[v]], 5)), sd_p95=float(np.percentile([x["sd"] for x in null[v]], 95)),
                     mean_med=float(np.median([x["mean"] for x in null[v]])), mean_p5=float(np.percentile([x["mean"] for x in null[v]], 5)), mean_p95=float(np.percentile([x["mean"] for x in null[v]], 95)),
                     t_med=float(np.median([x["t"] for x in null[v]])), worst_med=float(np.median([x["worst"] for x in null[v]])),
                     p_sd_le_real=pctile([x["sd"] for x in null[v]], (S_pairs if v == "pairs" else S_neut)["sd"]),
                     p_mean_ge_real=pctile([x["mean"] for x in null[v]], (S_pairs if v == "pairs" else S_neut)["mean"], False),
                     p_t_ge_real=pctile([x["t"] for x in null[v]], (S_pairs if v == "pairs" else S_neut)["t"], False)) for v in null}

# ------------------------------------------------------------------ T3 taksonomia point-in-time (klastry korelacyjne)
P_("\n=== T3 TAKSONOMIA POINT-IN-TIME: klastry korelacyjne (average linkage) z 252 sesji ≤ D0, residua vs ^NDX ===")
def resid_matrix(d0, universe, win=252):
    idx = [tickers.index(t) for t in universe]
    seg = Pm[d0 - win: d0 + 1][:, idx]
    r = seg[1:] / seg[:-1] - 1
    rn = ndx[d0 - win: d0 + 1]; rn = rn[1:] / rn[:-1] - 1
    ok = ~np.isnan(r).any(axis=0)
    r = r[:, ok]; u = [t for t, o in zip(universe, ok) if o]
    r = r - rn[:, None]
    return u, np.corrcoef(r.T)

def avg_linkage(C, K):
    n = C.shape[0]
    D = 1.0 - C; np.fill_diagonal(D, np.inf)
    clusters = {i: [i] for i in range(n)}
    Dm = D.copy()
    while len(clusters) > K:
        keys = list(clusters)
        sub = Dm[np.ix_(keys, keys)]
        a, b = np.unravel_index(np.argmin(sub), sub.shape); ka, kb = keys[a], keys[b]
        new = clusters[ka] + clusters[kb]
        for kc in keys:
            if kc in (ka, kb): continue
            d = np.mean([D[i, j] for i in new for j in clusters[kc]])
            Dm[ka, kc] = Dm[kc, ka] = d
        clusters[ka] = new; del clusters[kb]
        Dm[kb, :] = np.inf; Dm[:, kb] = np.inf
    lab = {}
    for c, mem in enumerate(clusters.values()):
        for i in mem: lab[i] = f"C{c}"
    return lab

CL_CACHE = {}
def grp_cluster(i, sig, K=15, min_group=3):
    key = (i, K)
    if key not in CL_CACHE:
        w = WIN[i]; u, C = resid_matrix(w["d0"], list(sig))
        lab = avg_linkage(C, K)
        g = {t: lab[k] for k, t in enumerate(u)}
        for t in sig:
            g.setdefault(t, "Pozostałe")
        gc = Counter(g.values())
        CL_CACHE[key] = {t: (g[t] if gc[g[t]] >= min_group else "Pozostałe") for t in sig}
    return CL_CACHE[key]

T3 = {}
for K in (10, 15, 20):
    gf = lambda i, sig, K=K: grp_cluster(i, sig, K)
    rows_p = run("pairs", gf); rows_n = run("neutral", gf)
    sp = stats(rows_p, f"pairs_K{K}"); sn = stats(rows_n, f"neutral_K{K}")
    cp = compare(rows_p, NONE, nboot=2000); cn = compare(rows_n, NONE, nboot=2000)
    ng = np.mean([len(set(grp_cluster(i, WIN[i]["sig"], K).values()) - {"Pozostałe"}) for i in range(len(WIN))])
    P_(f"K={K} (śr. grup ≥3: {ng:.1f}) pairs: śr {sp['mean']:.2f} σ {sp['sd']:.2f} t {sp['t']:.2f} worst {sp['worst']:.1f} | Δ vs none {cp['d_mean']:+.2f} (t {cp['d_t']:.2f}) σ-ratio {cp['sigma_ratio']:.3f} CI {[round(x,3) for x in cp['sigma_ratio_ci95']]} F p={cp['p_F']:.2g}")
    P_(f"       neutral: śr {sn['mean']:.2f} σ {sn['sd']:.2f} t {sn['t']:.2f} worst {sn['worst']:.1f} | Δ vs none {cn['d_mean']:+.2f} (t {cn['d_t']:.2f}) σ-ratio {cn['sigma_ratio']:.3f} CI {[round(x,3) for x in cn['sigma_ratio_ci95']]} F p={cn['p_F']:.2g}")
    T3[K] = dict(pairs=sp, neutral=sn, cmp_pairs=cp, cmp_neutral=cn, n_groups=float(ng))
    if K == 15:
        PAIRS_PIT = rows_p
# zgodność klastrów z TV: udział par z klastra K=15, w których oba końce są w tej samej grupie TV
same_tv = [sum(1 for l, s in zip(r["lo"], r["sh"]) if grp_base(0, {l: 0, s: 0}).get(l) == grp_base(0, {l: 0, s: 0}).get(s)) / len(r["lo"]) for r in PAIRS_PIT]
# uwaga: grouping_with na 2 spółkach daje 'Pozostałe' — użyj surowej industry/sector
same_tv = [np.mean([ind[l][0] == ind[s][0] or ind[l][1] == ind[s][1] for l, s in zip(r["lo"], r["sh"])]) for r in PAIRS_PIT]
P_(f"K=15: udział par klastrowych, których oba końce mają tę samą industry lub sector TV: {np.mean(same_tv):.2f}")
RES["T3"] = T3

# ------------------------------------------------------------------ T4 definicja grupy
P_("\n=== T4 WRAŻLIWOŚĆ NA DEFINICJĘ GRUPY ===")
T4 = {}
defs = {"base(ind≥4|sector, grp≥3)": dict(mode="base"), "sector-only": dict(mode="sector"), "industry-only(≥3)": dict(mode="industry"),
        "ind≥6|sector": dict(mode="base", min_ind=6), "ind≥10|sector": dict(mode="base", min_ind=10), "ind≥2|sector": dict(mode="base", min_ind=2)}
for name, kw in defs.items():
    gf = lambda i, sig, kw=kw: grouping_with(list(sig), ind, **kw)
    for v in ("pairs", "neutral"):
        rows = run(v, gf); s = stats(rows); c = compare(rows, NONE, nboot=1000)
        ng = np.mean([len(set(gf(i, WIN[i]["sig"]).values()) - {"Pozostałe"}) for i in range(len(WIN))])
        P_(f"{name:28s} {v:8s} grup {ng:4.1f} n={s['n']} śr {s['mean']:.2f} σ {s['sd']:.2f} t {s['t']:.2f} worst {s['worst']:.1f} | Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f} CI {[round(x,3) for x in c['sigma_ratio_ci95']]} F p={c['p_F']:.2g}")
        T4[f"{name}|{v}"] = dict(s=s, c=c, n_groups=float(ng))
for mg in (2, 4, 5, 6):
    rows = run("pairs", grp_base, min_group=mg); s = stats(rows); c = compare(rows, NONE, nboot=1000)
    P_(f"pairs MIN_GROUP={mg}: n={s['n']} nóg/okno {np.mean([r['n_legs'] for r in rows]):.1f} śr {s['mean']:.2f} σ {s['sd']:.2f} t {s['t']:.2f} worst {s['worst']:.1f} | Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f} F p={c['p_F']:.2g}")
    T4[f"pairs_min_group_{mg}"] = dict(s=s, c=c)
RES["T4"] = T4

# ------------------------------------------------------------------ T5 stabilność
P_("\n=== T5 STABILNOŚĆ: połówki i lata (b_pary / a_branza vs none) ===")
T5 = {}
h = len(NONE) // 2
for lab, sel in (("połowa 1", lambda r: r["i"] < h), ("połowa 2", lambda r: r["i"] >= h)):
    base = [r for r in NONE if sel(r)]
    for v, rows in (("b_pary", PAIRS), ("a_branza", NEUT)):
        rr = [r for r in rows if sel(r)]; s = stats(rr); sb = stats(base); c = compare(rr, base, nboot=2000)
        P_(f"{lab} {v:9s} n={s['n']} none σ {sb['sd']:.2f} śr {sb['mean']:.2f} | {v} σ {s['sd']:.2f} śr {s['mean']:.2f} t {s['t']:.2f} | Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f} CI {[round(x,3) for x in c['sigma_ratio_ci95']]} F p={c['p_F']:.2g} worst {c['worst_a']:.1f} vs {c['worst_b']:.1f}")
        T5[f"{lab}|{v}"] = dict(s=s, base=sb, c=c)
for y in sorted({r["year"] for r in NONE}):
    base = [r for r in NONE if r["year"] == y]
    line = f"{y} n={len(base)} none σ {stats(base)['sd']:.2f} śr {stats(base)['mean']:+.2f} worst {stats(base)['worst']:.1f}"
    for v, rows in (("b_pary", PAIRS), ("a_branza", NEUT)):
        rr = [r for r in rows if r["year"] == y]; c = compare(rr, base, nboot=500); s = stats(rr)
        line += f" | {v}: σ {s['sd']:.2f} śr {s['mean']:+.2f} Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f} worst {s['worst']:.1f}"
        T5[f"{y}|{v}"] = dict(s=s, c=c)
    P_(line)
# reżim VIX
for lab, sel in (("VIX>20", lambda r: r["vix"] > 20), ("VIX<=20", lambda r: r["vix"] <= 20)):
    base = [r for r in NONE if sel(r)]; rr = [r for r in PAIRS if sel(r)]; c = compare(rr, base, nboot=1000)
    P_(f"{lab}: n={c['n']} none śr {c['mean_b']:.2f} σ {c['sd_b']:.2f} | b_pary śr {c['mean_a']:.2f} σ {c['sd_a']:.2f} Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f}")
    T5[lab] = c
RES["T5"] = T5

# ------------------------------------------------------------------ T6 udział semis / software, GOOG-GOOGL
P_("\n=== T6 SKŁAD PAR: udział grup, wariant bez semis, para GOOG/GOOGL ===")
gcount = Counter(g for r in PAIRS for g in r["groups"])
tot = sum(gcount.values())
P_("udział grup w parach (b_pary):", {g: f"{c/tot:.2f}" for g, c in gcount.most_common(10)})
semi_in = np.mean(["Semiconductors" in r["groups"] for r in PAIRS]); soft_in = np.mean(["Packaged Software" in r["groups"] for r in PAIRS])
P_(f"okna z parą Semiconductors: {semi_in:.2f}; z parą Packaged Software: {soft_in:.2f}")
# wkład pary semis do wariancji: spread pary semi vs reszta
def pair_contrib(rows, gname):
    semi, rest = [], []
    for r in rows:
        w = WIN[r["i"]]
        for l, s, g in zip(r["lo"], r["sh"], r["groups"]):
            v = 100 * ((w["fwd"][l] - w["r_ndx"]) - (w["fwd"][s] - w["r_ndx"])) / len(r["lo"])
            (semi if g == gname else rest).append((r["i"], v))
    return semi, rest
semi, rest = pair_contrib(PAIRS, "Semiconductors")
sv = np.array([v for _, v in semi]); P_(f"para Semiconductors: n={len(sv)} śr. wkład {sv.mean():+.2f} pp/okno, σ wkładu {sv.std(ddof=1):.2f} (udział 1/5 wagi)")
# per-ticker pairs: GOOG/GOOGL
gg = sum(1 for r in PAIRS for l, s in zip(r["lo"], r["sh"]) if {l, s} == {"GOOG", "GOOGL"})
P_(f"par GOOG/GOOGL w b_pary: {gg} na {sum(len(r['lo']) for r in PAIRS)} par")
tkpairs = Counter((l, s) for r in PAIRS for l, s in zip(r["lo"], r["sh"]))
P_("najczęstsze pary (L,S):", tkpairs.most_common(12))
T6 = dict(group_share={g: c / tot for g, c in gcount.most_common()}, semi_windows=float(semi_in), soft_windows=float(soft_in),
          semi_contrib_mean=float(sv.mean()), semi_contrib_sd=float(sv.std(ddof=1)), goog_googl_pairs=gg,
          top_pairs=[[l, s, c] for (l, s), c in tkpairs.most_common(12)])
# wariant bez semis (pary z innych grup), tylko semis+software, bez semis i software
for name, kw in (("bez Semiconductors", dict(exclude_groups=("Semiconductors",))),
                 ("bez Semi i Software", dict(exclude_groups=("Semiconductors", "Packaged Software"))),
                 ("bez Electronic Technology (sector)", dict(exclude_groups=("Semiconductors", "Electronic Technology"))),
                 ("tylko Semi+Software (≤2 pary)", dict(only_groups={"Semiconductors", "Packaged Software"}))):
    rows = run("pairs", grp_base, **kw)
    if not rows: P_(name, "— brak okien"); continue
    s = stats(rows); c = compare(rows, NONE, nboot=1000)
    P_(f"pairs {name:36s} n={s['n']} nóg/okno {np.mean([r['n_legs'] for r in rows]):.1f} śr {s['mean']:.2f} σ {s['sd']:.2f} t {s['t']:.2f} Sh {s['sharpe']:.2f} worst {s['worst']:.1f} | Δ {c['d_mean']:+.2f} (t {c['d_t']:.2f}) σ-ratio {c['sigma_ratio']:.3f} F p={c['p_F']:.2g}")
    T6[name] = dict(s=s, c=c)
# none bez GOOG (dla symetrii) i pairs bez GOOG
RES["T6"] = T6

# ------------------------------------------------------------------ T7 struktura: 'none' z mniej ekstremalnymi rangami (kontrola ekstremalności)
P_("\n=== T7 KONTROLA EKSTREMALNOŚCI: none z rang k..k+4 (bez taksonomii) ===")
T7 = {}
for k in (0, 3, 6, 10, 15):
    rows = []; prev = {}
    for i, w in enumerate(WIN):
        srt = sorted(w["sig"], key=lambda t: -w["sig"][t]["mom"])
        lo, sh = srt[k:k + 5], srt[::-1][k:k + 5]
        wts = B.w_equal(lo, sh); ev = B.evaluate(wts, w["fwd"], w["r_ndx"]); cr, dw = B.turnover_cost(wts, prev); prev = wts
        rows.append(dict(date=w["date"], year=w["year"], i=i, spread=ev["spread"], long=ev["long"], short=ev["short"], cost=cr + B.FIN_YEAR / 52 * 2, lo=lo, sh=sh, groups=[], n_legs=10,
                         ext=float(np.mean([w["sig"][t]["mom"] for t in lo]) - np.mean([w["sig"][t]["mom"] for t in sh])), rank_lo=k + 2, rank_sh=k + 2, vix=w["vix"]))
    s = stats(rows); c = compare(rows, NONE, nboot=1000)
    P_(f"rangi {k+1}–{k+5}: śr {s['mean']:.2f} σ {s['sd']:.2f} t {s['t']:.2f} worst {s['worst']:.1f} ekstremalność {s['ext']:.1f} | σ-ratio vs none {c['sigma_ratio']:.3f} Δ {c['d_mean']:+.2f}")
    T7[k] = dict(s=s, c=c)
RES["T7"] = T7
# σ a ekstremalność: w b_pary średnia ranga nóg
P_(f"b_pary: śr. ranga long {S_pairs['rank_lo']:.1f}, short {S_pairs['rank_sh']:.1f} (0 = skrajna); ekstremalność mom L−S {S_pairs['ext']:.1f} pp vs none {S_none['ext']:.1f} pp")

json.dump(RES, open(OUT_JSON, "w"), indent=1, default=float)
P_(f"\nzapisano {OUT_JSON}, {OUT_TXT}")
