#!/usr/bin/env python3 -I
"""Risk manager: sigma koszyka, drawdown/kill switch, stopy, korelacja, sizing.

Wejscie: ../dane/closes_5y.csv, mp_koszyki.json (W1-W8).
Wyjscie: ryzyko_sizing_out.md (tabele), ryzyko_sizing_wyniki.json.
Zwroty: proste close/close. Koszyk na "jednostke" = srednia... NIE: suma
zwrotow nog long minus suma nog short (po 1,0 na noge), kapital = ALLOC x suma.
"""
import json, math, sys, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "dane", "closes_5y.csv")
OUT_MD = os.path.join(HERE, "ryzyko_sizing_out.md")
OUT_JSON = os.path.join(HERE, "ryzyko_sizing_wyniki.json")
rng = np.random.default_rng(20261018)

px = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()]  # wiersze swiat (2026-05-25, 2026-09-07) sa cale puste
INDEKSY = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
UNIV = [c for c in px.columns if c not in INDEKSY]
ret = px.pct_change()  # proste zwroty dzienne
dates = px.index

kosz = json.load(open(os.path.join(HERE, "mp_koszyki.json")))
W8 = {"long": ["GOOGL", "GILD", "MSFT", "QCOM", "ADP"],
      "short": ["AXON", "DASH", "ALNY", "APP", "FER"], "d0": "2026-10-16"}
kosz["2026-W8"] = W8
WEEKS = ["2026-W1", "2026-W2", "2026-W3", "2026-W4", "2026-W5", "2026-W6", "2026-W7", "2026-W8"]

out = []
res = {}
def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s); print(s)

def idx_d0(d0):
    d = pd.Timestamp(d0)
    pos = dates.searchsorted(d, side="right") - 1  # ostatnia sesja <= d0
    return pos

def basket_series(long, short, i_end, win):
    """Zwroty dzienne koszyka (1,0 na noge) w oknie [i_end-win+1, i_end]."""
    sl = ret.iloc[i_end - win + 1:i_end + 1]
    L = sl[long]; S = sl[short]
    ok = L.notna().all(axis=1) & S.notna().all(axis=1)
    unit = L.sum(axis=1) - S.sum(axis=1)
    return unit[ok], sl[ok]

def cov_sigma(long, short, i_end, win, w_long=None, w_short=None):
    sl = ret.iloc[i_end - win + 1:i_end + 1][long + short].dropna()
    wl = np.ones(len(long)) if w_long is None else np.asarray(w_long)
    ws = np.ones(len(short)) if w_short is None else np.asarray(w_short)
    w = np.concatenate([wl, -ws])
    C = sl.cov().values
    return math.sqrt(w @ C @ w), sl, C

# ----------------------------------------------------------------------------
P("# Wyniki skryptu ryzyko_sizing.py")
P(f"dane: {CSV}  sesje {dates[0].date()}..{dates[-1].date()} n={len(dates)}; uniwersum {len(UNIV)} tickerow")
P()
P("## (1) sigma koszyka 5L/5S, 24% na noge (gross 240%)")
P()
P("| W | D0 | okno | sigma_d nogi long sr | sigma_d nogi short sr | sigma_d kapital | sigma_tyg (x sqrt5) | sigma_tyg empir. 5-ses. | rho par LONG | rho par SHORT | rho L-S | sigma gdyby nogi niezalezne |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|")
ALLOC = 0.24
res["sigma_koszyki"] = {}
for w in WEEKS:
    k = kosz[w]; i0 = idx_d0(k["d0"])
    for win in (60, 250):
        sig, sl, C = cov_sigma(k["long"], k["short"], i0, win)
        n = len(sl)
        sd = np.sqrt(np.diag(C))
        nl = len(k["long"])
        corr = sl.corr().values
        rl = corr[:nl, :nl][np.triu_indices(nl, 1)].mean()
        rs = corr[nl:, nl:][np.triu_indices(len(k["short"]), 1)].mean()
        rls = corr[:nl, nl:].mean()
        indep = math.sqrt((sd ** 2).sum())
        unit, _ = basket_series(k["long"], k["short"], i0, win)
        # empiryczna tygodniowa: nienakladajace sie okna 5 sesji
        u = unit.values
        m = len(u) // 5 * 5
        wk = (1 + u[:m].reshape(-1, 5) / 1.0)  # suma zwrotow prostych w tyg (przyblizenie liniowe)
        wk5 = u[:m].reshape(-1, 5).sum(axis=1)
        row = dict(week=w, d0=k["d0"], win=win, n=n,
                   sig_long=float(sd[:nl].mean() * 100), sig_short=float(sd[nl:].mean() * 100),
                   sig_cap_d=float(sig * ALLOC * 100), sig_cap_w=float(sig * ALLOC * 100 * math.sqrt(5)),
                   sig_cap_w_emp=float(wk5.std(ddof=1) * ALLOC * 100),
                   rho_L=float(rl), rho_S=float(rs), rho_LS=float(rls), sig_indep=float(indep * ALLOC * 100))
        res["sigma_koszyki"][f"{w}_{win}"] = row
        P(f"| {w[5:]} | {k['d0']} | {win} (n={n}) | {row['sig_long']:.2f}% | {row['sig_short']:.2f}% | **{row['sig_cap_d']:.2f}%** | {row['sig_cap_w']:.1f}% | {row['sig_cap_w_emp']:.1f}% | {rl:.2f} | {rs:.2f} | {rls:.2f} | {row['sig_indep']:.2f}% |")
P()

# losowe koszyki
P("## (1b) losowe koszyki 5/5 z uniwersum (1000 losowan, okno 250 sesji, 24% na noge)")
P()
P("| data D0 | mediana sigma_d kapital | p10 | p90 | p99 | sr rho par LONG (losowe) | sigma faktycznego koszyka | percentyl faktycznego |")
P("|---|---|---|---|---|---|---|---|")
res["losowe"] = {}
for w in ["2026-W4", "2026-W5", "2026-W6", "2026-W7", "2026-W8"]:
    k = kosz[w]; i0 = idx_d0(k["d0"]); win = 250
    sl_all = ret.iloc[i0 - win + 1:i0 + 1][UNIV]
    dostepne = [c for c in UNIV if sl_all[c].notna().all()]
    R = sl_all[dostepne].values
    C = np.cov(R.T)
    corr = np.corrcoef(R.T)
    sig_l = []; rho_l = []
    for _ in range(1000):
        pick = rng.choice(len(dostepne), 10, replace=False)
        wv = np.zeros(len(dostepne)); wv[pick[:5]] = 1; wv[pick[5:]] = -1
        sig_l.append(math.sqrt(wv @ C @ wv) * ALLOC * 100)
        sub = corr[np.ix_(pick[:5], pick[:5])]
        rho_l.append(sub[np.triu_indices(5, 1)].mean())
    sig_l = np.array(sig_l)
    fakt = res["sigma_koszyki"][f"{w}_250"]["sig_cap_d"]
    pct = (sig_l < fakt).mean() * 100
    res["losowe"][w] = dict(med=float(np.median(sig_l)), p10=float(np.percentile(sig_l, 10)),
                            p90=float(np.percentile(sig_l, 90)), p99=float(np.percentile(sig_l, 99)),
                            rho=float(np.mean(rho_l)), fakt=fakt, pct=float(pct), n_univ=len(dostepne))
    P(f"| {k['d0']} ({w[5:]}, n_univ={len(dostepne)}) | {np.median(sig_l):.2f}% | {np.percentile(sig_l,10):.2f}% | {np.percentile(sig_l,90):.2f}% | {np.percentile(sig_l,99):.2f}% | {np.mean(rho_l):.2f} | {fakt:.2f}% | {pct:.0f} |")
P()

# ----------------------------------------------------------------------------
# (2) Monte Carlo drawdown / kill switch
P("## (2) Rozklad drawdownu i P(kill switch 25% od szczytu)")
P()
# pula: zwroty jednostkowe koszykow W1..W8 z 250 sesji do D0, wysrodkowane (zerowa alfa)
pool_rows = []
for w in WEEKS:
    k = kosz[w]; i0 = idx_d0(k["d0"])
    unit, _ = basket_series(k["long"], k["short"], i0, 250)
    pool_rows.append(unit.values - unit.values.mean())
pool = np.concatenate(pool_rows)
P(f"pula bootstrapu: koszyki W1-W8 x 250 sesji do D0, wysrodkowane; n={len(pool)}, sigma jednostkowa {pool.std()*100:.2f}%/d  (x0,24 = {pool.std()*0.24*100:.2f}%/d kapitalu)")
# pula tylko W4-W7
pool47 = np.concatenate(pool_rows[3:7])
P(f"pula W4-W7: n={len(pool47)}, sigma jednostkowa {pool47.std()*100:.2f}%/d (x0,24 = {pool47.std()*0.24*100:.2f}%/d)")

NPATH = 20000
def block_boot(pool, nses, npath, block=5):
    nb = math.ceil(nses / block)
    starts = rng.integers(0, len(pool) - block, size=(npath, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(npath, -1)[:, :nses]
    return pool[idx]

def sim_paths(unit_ret, alloc, alpha_d=0.0, start_dd=0.0, kill=0.75, staged=None):
    """unit_ret: (npath, nses) zwroty jednostkowe koszyka. alloc moze byc skalarem
    albo (npath,nses) macierza. staged: dict(prog_dd, mnoznik) - polowienie alokacji
    gdy dd < -prog."""
    npath, nses = unit_ret.shape
    eq = np.full(npath, 1.0 - start_dd)
    peak = np.ones(npath)
    killed = np.zeros(npath, bool)
    kill_day = np.full(npath, -1)
    maxdd = np.zeros(npath)
    for t in range(nses):
        a = alloc if np.isscalar(alloc) else alloc[:, t]
        if staged is not None:
            dd_now = eq / peak - 1
            a = np.where(dd_now < -staged["prog_dd"], a * staged["mnoznik"], a)
        r = a * (unit_ret[:, t] + alpha_d)
        eq = np.where(killed, eq, eq * (1 + r))
        peak = np.maximum(peak, eq)
        dd = eq / peak - 1
        maxdd = np.minimum(maxdd, dd)
        newkill = (~killed) & (eq < kill * peak)
        kill_day = np.where(newkill, t, kill_day)
        killed |= newkill
    return eq, maxdd, killed, kill_day

def summarize(eq, maxdd, killed):
    return dict(p_kill=float(killed.mean() * 100),
                dd_med=float(np.median(maxdd) * 100), dd_p90=float(np.percentile(maxdd, 10) * 100),
                dd_p95=float(np.percentile(maxdd, 5) * 100), dd_p99=float(np.percentile(maxdd, 1) * 100),
                eq_med=float((np.median(eq) - 1) * 100), eq_mean=float((eq.mean() - 1) * 100),
                p_strata=float((eq < 1).mean() * 100))

res["mc"] = {}
P()
P("### (2a) stala alokacja na noge, zerowa alfa, bootstrap blokowy (blok 5) z puli W1-W8; start od szczytu")
P()
P("| ALLOC/noge | gross | sigma_d kap. | 4 tyg: DD mediana | DD p90 | DD p95 | DD p99 | P(kill) 4 tyg | P(kill) 12 tyg | P(kill) 12 tyg, start -21% | P(kill) 12 tyg, start -23,7% |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
U20 = block_boot(pool, 20, NPATH); U60 = block_boot(pool, 60, NPATH)
for a in (0.24, 0.20, 0.16, 0.12, 0.10, 0.08, 0.06, 0.04):
    eq, dd, kl, _ = sim_paths(U20, a)
    s20 = summarize(eq, dd, kl)
    eq, dd, kl, _ = sim_paths(U60, a)
    s60 = summarize(eq, dd, kl)
    _, _, kl21, _ = sim_paths(U60, a, start_dd=0.21)
    _, _, kl237, _ = sim_paths(U60, a, start_dd=0.237)
    res["mc"][f"const_{a}"] = dict(s20=s20, s60=s60, p_kill_start21=float(kl21.mean() * 100), p_kill_start237=float(kl237.mean() * 100))
    P(f"| {a:.2f} | {a*10*100:.0f}% | {pool.std()*a*100:.2f}% | {s20['dd_med']:.1f}% | {s20['dd_p90']:.1f}% | {s20['dd_p95']:.1f}% | {s20['dd_p99']:.1f}% | {s20['p_kill']:.1f}% | **{s60['p_kill']:.1f}%** | {kl21.mean()*100:.0f}% | {kl237.mean()*100:.0f}% |")
P()
P("### (2b) to samo, pula tylko W4-W7 (koszyki o najwyzszej zmiennosci)")
P()
P("| ALLOC | sigma_d kap. | P(kill) 4 tyg | P(kill) 12 tyg | DD p95 4 tyg |")
P("|---|---|---|---|---|")
U60b = block_boot(pool47, 60, NPATH); U20b = block_boot(pool47, 20, NPATH)
for a in (0.24, 0.12, 0.08, 0.06):
    eq, dd, kl, _ = sim_paths(U60b, a); s60 = summarize(eq, dd, kl)
    eq, dd, kl, _ = sim_paths(U20b, a); s20 = summarize(eq, dd, kl)
    res["mc"][f"const47_{a}"] = dict(s20=s20, s60=s60)
    P(f"| {a:.2f} | {pool47.std()*a*100:.2f}% | {s20['p_kill']:.1f}% | {s60['p_kill']:.1f}% | {s20['dd_p95']:.1f}% |")
P()

# (2c) losowe koszyki tygodniowo z uniwersum: co tydzien nowy koszyk 5/5, zwroty z losowego 5-sesyjnego bloku historii, demeaned per koszyk
P("### (2c) proces 'co tydzien nowy losowy koszyk 5/5 z uniwersum' (losowy blok 5 sesji z 5 lat, zwroty wysrodkowane), 12 tygodni")
P()
R_all = ret[UNIV].values
def random_basket_weeks(npath, nweeks):
    outm = np.empty((npath, nweeks * 5))
    nd = len(dates)
    for p in range(npath):
        for wk in range(nweeks):
            while True:
                pick = rng.choice(len(UNIV), 10, replace=False)
                st = rng.integers(1, nd - 5)
                blk = R_all[st:st + 5][:, pick]
                if not np.isnan(blk).any():
                    break
            u = blk[:, :5].sum(axis=1) - blk[:, 5:].sum(axis=1)
            outm[p, wk * 5:(wk + 1) * 5] = u
    return outm
RB = random_basket_weeks(5000, 12)
RB_dm = RB - RB.mean()  # globalne wysrodkowanie (zerowa alfa)
P(f"sigma jednostkowa losowych koszykow: {RB.std()*100:.2f}%/d")
P("| ALLOC | sigma_d kap. | P(kill) 12 tyg | DD p95 12 tyg |")
P("|---|---|---|---|")
for a in (0.24, 0.12, 0.08, 0.06):
    eq, dd, kl, _ = sim_paths(RB_dm, a); s = summarize(eq, dd, kl)
    res["mc"][f"random_{a}"] = s
    P(f"| {a:.2f} | {RB.std()*a*100:.2f}% | {s['p_kill']:.1f}% | {s['dd_p95']:.1f}% |")
P()

# (2d) vol-targeting na MIESZANCE koszykow: co tydzien losowy koszyk z W1-W8 (jego wlasna pula 250 sesji,
# wysrodkowana) i jego wlasna sigma60 ex ante (z 60 sesji do D0); alloc = cel / sigma60_unit (cap).
P("### (2d) skalowanie do celu sigma_d kapitalu: co tydzien losowy koszyk z W1-W8 z wlasna historia i wlasna sigma60 ex ante")
P()
P("Metoda: tydzien = losowy koszyk b z {W1..W8}; zwroty = losowy blok 5 sesji z jego 250-sesyjnej, wysrodkowanej historii do D0; ALLOC_b = min(cap, cel / sigma60_unit(b)), sigma60 z 60 sesji do D0 (znane w sobote).")
P()
SIG60 = {w: res["sigma_koszyki"][f"{w}_60"]["sig_cap_d"] / 100 / 0.24 for w in WEEKS}  # jednostkowa sigma dzienna
P("sigma60 jednostkowa (suma 10 nog) per koszyk: " + ", ".join(f"{w[5:]} {SIG60[w]*100:.1f}%" for w in WEEKS))
def mixture_paths(npath, nweeks):
    U = np.empty((npath, nweeks * 5)); B = np.empty((npath, nweeks), int)
    for wk in range(nweeks):
        b = rng.integers(0, len(WEEKS), size=npath); B[:, wk] = b
        for bi in range(len(WEEKS)):
            m = b == bi; nm = m.sum()
            if nm == 0: continue
            pr = pool_rows[bi]
            st = rng.integers(0, len(pr) - 5, size=nm)
            U[m, wk * 5:(wk + 1) * 5] = pr[st[:, None] + np.arange(5)[None, :]]
    return U, B
UM, BM = mixture_paths(NPATH, 12)
P(f"sigma jednostkowa mieszanki: {UM.std()*100:.2f}%/d")
def alloc_from_B(B, fn):
    a = np.vectorize(fn)(B)
    return np.repeat(a, 5, axis=1)
def vt_fn(target, cap=0.24, floor=0.0):
    return lambda bi: float(np.clip(target / SIG60[WEEKS[bi]], floor, cap))
P()
P("| cel sigma_d | sr. ALLOC/noge | min-max ALLOC (W1..W8) | P(kill) 4 tyg | P(kill) 12 tyg | DD p95 4 tyg | DD p95 12 tyg | dla porownania: staly ALLOC o tej samej sredniej -> P(kill 12t) |")
P("|---|---|---|---|---|---|---|---|")
res["voltarget"] = {}
for tgt in (0.010, 0.015, 0.020):
    al = alloc_from_B(BM, vt_fn(tgt))
    eq, dd, kl, _ = sim_paths(UM, al); s = summarize(eq, dd, kl)
    eq4, dd4, kl4, _ = sim_paths(UM[:, :20], al[:, :20])
    eqc, ddc, klc, _ = sim_paths(UM, float(al.mean()))
    vals = [vt_fn(tgt)(i) for i in range(len(WEEKS))]
    res["voltarget"][tgt] = dict(s60=s, p_kill4=float(kl4.mean()*100), alloc_mean=float(al.mean()), alloc_min=min(vals), alloc_max=max(vals), dd_p95_4w=float(np.percentile(dd4, 5) * 100), p_kill_const_same_mean=float(klc.mean()*100), alloc_per_week={w: v for w, v in zip(WEEKS, vals)})
    P(f"| {tgt*100:.1f}% | {al.mean():.3f} | {min(vals):.3f}-{max(vals):.3f} | {kl4.mean()*100:.1f}% | **{s['p_kill']:.1f}%** | {np.percentile(dd4,5)*100:.1f}% | {s['dd_p95']:.1f}% | {klc.mean()*100:.1f}% |")
P()
P("ALLOC na noge z vol-targetu per koszyk (cel 1,5%/d): " + ", ".join(f"{w[5:]} {vt_fn(0.015)(i)*100:.1f}%" for i, w in enumerate(WEEKS)))
P()

# (2e) wagi odwrotnie proporcjonalne do sigma60 nogi, znormalizowane do celu sigma_d kapitalu (kowariancja 60 sesji) - koszyki W4-W8")
P()
res["invvol"] = {}
for w in ["2026-W4", "2026-W5", "2026-W6", "2026-W7", "2026-W8"]:
    k = kosz[w]; i0 = idx_d0(k["d0"])
    sl = ret.iloc[i0 - 59:i0 + 1][k["long"] + k["short"]].dropna()
    C = sl.cov().values; sd = np.sqrt(np.diag(C))
    nl = len(k["long"])
    sgn = np.concatenate([np.ones(nl), -np.ones(len(k["short"]))])
    w_inv = 1 / sd
    for tgt in (0.010, 0.015, 0.020):
        wv = w_inv * sgn
        s = math.sqrt(wv @ C @ wv)
        scale = tgt / s
        wagi = w_inv * scale
        # porownanie: rowne wagi do tego samego celu
        we = sgn.copy(); se = math.sqrt(we @ C @ we); a_eq = tgt / se
        res["invvol"][f"{w}_{tgt}"] = dict(wagi={t: round(float(x), 3) for t, x in zip(k["long"] + k["short"], wagi)},
                                           gross=float(wagi.sum()), alloc_rowne=float(a_eq), gross_rowne=float(a_eq * 10),
                                           sigma_nogi={t: round(float(x) * 100, 2) for t, x in zip(k["long"] + k["short"], sd)})
        if tgt == 0.015:
            P(f"- **{w[5:]}** (sigma60 nog %: " + ", ".join(f"{t} {x*100:.1f}" for t, x in zip(k['long'] + k['short'], sd)) + ")")
            P(f"  - cel 1,5%/d: wagi inv-vol = " + ", ".join(f"{t} {x*100:.1f}%" for t, x in zip(k['long'] + k['short'], wagi)) + f"; gross {wagi.sum()*100:.0f}%")
            P(f"  - cel 1,5%/d przy rownych wagach: {a_eq*100:.1f}% na noge, gross {a_eq*1000:.0f}%; (cel 1,0%: {a_eq/1.5*100:.1f}%/noge; cel 2,0%: {a_eq/1.5*2*100:.1f}%/noge)")
P()

# (2f) zrealizowane zwroty kapitalu W4-W8 (0,24, bez stopow/kosztow) od D0+1 close
P("### (2f) kontrola modelu: zrealizowane dzienne zwroty kapitalu (0,24, rowne wagi, bez stopow/kosztow, wejscie close D0, do kolejnego D0)")
P()
eq_path = [1.0]; dts = []
for w, wn in zip(WEEKS[:-1], WEEKS[1:]):
    k = kosz[w]; i0 = idx_d0(k["d0"]); i1 = idx_d0(kosz[wn]["d0"])
    sl = ret.iloc[i0 + 1:i1 + 1]
    u = sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)
    for d, x in u.items():
        eq_path.append(eq_path[-1] * (1 + 0.24 * x)); dts.append(d)
eqp = np.array(eq_path)
peak = np.maximum.accumulate(eqp)
P(f"sciezka W1..W7 rozliczana do D0 nastepnego tygodnia (D0 W1 = 2026-08-26 -> 2026-10-16), {len(dts)} sesji: wynik {(eqp[-1]-1)*100:+.1f}%, max DD {((eqp/peak).min()-1)*100:.1f}%, szczyt {dts[int(np.argmax(eqp))-1].date() if np.argmax(eqp)>0 else 'start'}; sigma_d zrealizowana {np.diff(np.log(eqp)).std()*100:.2f}%")
res["realized"] = dict(wynik=float((eqp[-1] - 1) * 100), maxdd=float(((eqp / peak).min() - 1) * 100), sigma_d=float(np.diff(np.log(eqp)).std() * 100))
# W7 osobno
k = kosz["2026-W7"]; i0 = idx_d0(k["d0"]); i1 = idx_d0("2026-10-16")
sl = ret.iloc[i0 + 1:i1 + 1]; u = sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)
P(f"W7 (12-16.10): dzienne zwroty kapitalu x0,24: {', '.join(f'{x*24:+.2f}%' for x in u.values)}; suma {u.sum()*24:+.2f}%; sigma_d jednostkowa koszyka W7 ex ante (60 ses.) {res['sigma_koszyki']['2026-W7_60']['sig_cap_d']:.2f}%/d -> tydzien {u.sum()*24/ (res['sigma_koszyki']['2026-W7_60']['sig_cap_d']*math.sqrt(5)):.1f} sigma (ex ante)")
P()

# ----------------------------------------------------------------------------
# (3) stop 10% na nogach o wysokiej sigma
P("## (3) Twardy stop 10% od wejscia na nogach o sigma_d 4-6%: czestosc trafienia w <=5 sesjach (zamkniecia, dolna granica wobec intraday)")
P()
def stop_stats(tk, direction, prog, win_days=5, last=None):
    s = px[tk].dropna()
    if last:
        s = s.iloc[-(last + win_days):]
    v = s.values; n = len(v)
    hits = 0; total = 0; hit_day = []; after = []; whips = 0; end_ret = []; end_ret_stop = []
    for i in range(n - win_days):
        e = v[i]; path = v[i + 1:i + 1 + win_days]
        mv = (path / e - 1) if direction == "BUY" else (1 - path / e)
        total += 1
        fin = mv[-1]
        end_ret.append(fin)
        if (mv <= -prog).any():
            hits += 1
            d = int(np.argmax(mv <= -prog))
            hit_day.append(d + 1)
            # po stopie: ruch od ceny stopu do konca okna (czy dalej spada = kontynuacja)
            rest = mv[-1] - mv[d]
            after.append(rest)
            end_ret_stop.append(fin)
            # whipsaw: na koniec okna strata < prog (czyli stop zamknal gorzej niz 'trzymaj')
            if fin > -prog:
                whips += 1
    return dict(n=total, hits=hits, freq=hits / total * 100 if total else float('nan'),
                hit_day_med=float(np.median(hit_day)) if hit_day else None,
                after_mean=float(np.mean(after) * 100) if after else None,
                whip_share=whips / hits * 100 if hits else None,
                end_mean=float(np.mean(end_ret) * 100), end_sd=float(np.std(end_ret) * 100),
                end_stop_mean=float(np.mean(end_ret_stop) * 100) if end_ret_stop else None)

res["stopy"] = {}
P("| ticker | kierunek | sigma_d 250 | n okien (5 lat) | P(stop 10% w <=5 ses.) 5 lat | ostatnie 250 ses. | ostatnie 60 ses. | mediana dnia trafienia | sr. ruch po stopie do konca okna | udzial 'whipsaw' (na koniec okna strata <10%) | P(stop 15%) 5 lat | P(stop 20%) |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|")
for tk in ["LITE", "SNDK", "MU", "MRVL", "AMD", "TER", "APP", "PANW", "CSCO", "PEP", "CMCSA", "SBUX"]:
    direction = "BUY" if tk in {"LITE", "SNDK", "MU", "MRVL", "AMD", "TER", "PANW", "CSCO"} else "SELL"
    s5 = stop_stats(tk, direction, 0.10); s250 = stop_stats(tk, direction, 0.10, last=250); s60 = stop_stats(tk, direction, 0.10, last=60)
    s15 = stop_stats(tk, direction, 0.15); s20 = stop_stats(tk, direction, 0.20)
    sd250 = ret[tk].dropna().iloc[-250:].std() * 100
    res["stopy"][tk] = dict(dir=direction, sd250=float(sd250), s5=s5, s250=s250, s60=s60, p15=s15["freq"], p20=s20["freq"])
    P(f"| {tk} | {direction} | {sd250:.2f}% | {s5['n']} | **{s5['freq']:.1f}%** | {s250['freq']:.1f}% | {s60['freq']:.1f}% | {s5['hit_day_med']} | {s5['after_mean']:+.2f} p.p. | {s5['whip_share']:.0f}% | {s15['freq']:.1f}% | {s20['freq']:.1f}% |")
P()
# obie strony (stop na long i short tej samej spolki) - symetria
P("Symetria: czestosc ruchu +10% w 5 sesjach (stop na SHORT) dla tych samych nazw, 5 lat:")
for tk in ["LITE", "SNDK", "MU", "MRVL"]:
    s = stop_stats(tk, "SELL", 0.10)
    P(f"- {tk}: {s['freq']:.1f}% (n={s['n']})")
P()
# stop w jednostkach sigma: ile sigma_5 to 10%?
P("Stop 10% w jednostkach sigma 5-sesyjnej (sigma_d60 x sqrt5), stan na 2026-10-16:")
for tk in ["LITE", "SNDK", "MU", "MRVL", "PEP", "CMCSA"]:
    sd = ret[tk].dropna().iloc[-60:].std()
    P(f"- {tk}: sigma_d60 {sd*100:.2f}%, sigma_5 {sd*math.sqrt(5)*100:.1f}%, 10% = {0.10/(sd*math.sqrt(5)):.2f} sigma_5; 2 sigma_5 = {2*sd*math.sqrt(5)*100:.1f}%")
P()
# koszt stop+reopen: symulacja na koszyku nog high-vol: strategia trzymaj vs stop10 (zamkniecie na close dnia przebicia, reopen na close nastepnego dnia) - oczekiwana roznica w 5-ses oknie
P("Stop 10% + ponowne otwarcie nastepnego dnia (jak bot) vs trzymaj, okna 5 sesji, 5 lat, long:")
def stop_reopen(tk, prog=0.10):
    s = px[tk].dropna().values; n = len(s); diff = []; nhit = 0
    for i in range(n - 6):
        e = s[i]; path = s[i + 1:i + 6]
        mv = path / e - 1
        hold = mv[-1]
        if (mv <= -prog).any():
            d = int(np.argmax(mv <= -prog)); nhit += 1
            pnl = mv[d]  # zamknieto na close dnia d
            if d + 1 < 5:
                # reopen na close d+1, trzymaj do konca
                pnl += path[-1] / path[d + 1] - 1
            diff.append(pnl - hold)
    return nhit, n - 6, float(np.mean(diff) * 100) if diff else 0.0, float(np.sum(diff) / (n - 6) * 100 * 50)  # koszt na 50 okien (~rok)
for tk in ["LITE", "SNDK", "MU", "MRVL"]:
    nh, nt, md, cost = stop_reopen(tk)
    P(f"- {tk}: trafien {nh}/{nt} ({nh/nt*100:.1f}%), sr. roznica (stop+reopen - trzymaj) w oknie z trafieniem {md:+.2f} p.p. nogi; oczekiwany koszt na ~50 okien/rok: {cost:+.2f} p.p. nogi")
P()

# ----------------------------------------------------------------------------
# (4) korelacja miedzy nogami long
P("## (4) Korelacja par w LONG a sigma koszyka")
P()
P("| W | rho60 LONG | rho250 LONG | rho60 SHORT | rho60 L-S (cross) | sigma60 strony LONG (5 nog po 24%) | gdyby rho=0 | N_eff LONG |")
P("|---|---|---|---|---|---|---|---|")
res["rho"] = {}
for w in WEEKS:
    k = kosz[w]; i0 = idx_d0(k["d0"])
    r60 = res["sigma_koszyki"][f"{w}_60"]; r250 = res["sigma_koszyki"][f"{w}_250"]
    sl = ret.iloc[i0 - 59:i0 + 1][k["long"]].dropna()
    C = sl.cov().values; sd = np.sqrt(np.diag(C))
    sL = math.sqrt(np.ones(5) @ C @ np.ones(5)) * 0.24 * 100
    s0 = math.sqrt((sd ** 2).sum()) * 0.24 * 100
    neff = (sd.sum() ** 2) / (np.ones(5) @ C @ np.ones(5))
    res["rho"][w] = dict(rho60=r60["rho_L"], rho250=r250["rho_L"], rhoS=r60["rho_S"], rhoLS=r60["rho_LS"], sigL=float(sL), sig0=float(s0), neff=float(neff))
    P(f"| {w[5:]} | {r60['rho_L']:.2f} | {r250['rho_L']:.2f} | {r60['rho_S']:.2f} | {r60['rho_LS']:.2f} | {sL:.2f}% | {s0:.2f}% | {neff:.1f} |")
P()
P("Wrazliwosc teoretyczna: 5 nog long po 24%, sigma_d nogi 4,5% (sr. W4-W7), jednakowa rho par:")
P()
P("| rho | sigma_d strony LONG | mnoznik vs rho=0 | N_eff |")
P("|---|---|---|---|")
for rho in (0.0, 0.2, 0.35, 0.5, 0.6, 0.75, 0.9):
    var = 5 * 0.045 ** 2 + 20 * rho * 0.045 ** 2
    s = math.sqrt(var) * 0.24 * 100
    s0 = math.sqrt(5) * 0.045 * 0.24 * 100
    P(f"| {rho:.2f} | {s:.2f}% | x{s/s0:.2f} | {5/(1+4*rho):.1f} |")
P()

# ----------------------------------------------------------------------------
# (5) polityki: porownanie przy zerowej alfie i przy alfie
P("## (5) Polityki sizingu i kill switcha: P(kill 12 tyg) przy zerowej alfie oraz wynik przy alfie")
P()
P("Alfa: 'spread_pp' tygodniowy koszyka jednostkowego (sr. zwrot 5 long + sr. 5 short, w p.p.) => zwrot jednostkowy sumy 10 nog = 10 x spread/100/... UWAGA: jednostka tu = SUMA 5 long - SUMA 5 short, czyli spread_pp x 5 / 100 na tydzien = spread_pp x 1,0 pp/d.")
P("Alfa_d jednostkowa = spread_tyg(pp) x 5 / 100 / 5 = spread_tyg/100 na dzien. Scenariusze: 0; +1 p.p./tyg; +2 p.p./tyg (sr. W1-W7 = -0,52 p.p.; sr. W1-W6 +2,91 p.p.).")
P()
def pol_const(a):
    return ("ALLOC %.2f staly" % a, lambda B: np.full((B.shape[0], 60), a), None)
def pol_vt(tgt, cap=0.24, floor=0.0):
    nm = "vol-target %.1f%%/d (cap %.2f%s)" % (tgt * 100, cap, (", floor %.2f" % floor) if floor else "")
    return (nm, lambda B: alloc_from_B(B, vt_fn(tgt, cap, floor)), None)
def pol_vt_staged(tgt, prog, mn, cap=0.24):
    return ("vol-target %.1f%%/d + x%.1f przy DD<-%.0f%%" % (tgt * 100, mn, prog * 100), lambda B: alloc_from_B(B, vt_fn(tgt, cap)), dict(prog_dd=prog, mnoznik=mn))
def pol_const_staged(a, prog, mn):
    return ("ALLOC %.2f + x%.1f przy DD<-%.0f%%" % (a, mn, prog * 100), lambda B: np.full((B.shape[0], 60), a), dict(prog_dd=prog, mnoznik=mn))
POLICIES = [pol_const(0.24), pol_const(0.16), pol_const(0.12), pol_const(0.10), pol_const(0.08), pol_const(0.06),
            pol_const_staged(0.12, 0.10, 0.5), pol_const_staged(0.10, 0.10, 0.5), pol_const_staged(0.24, 0.10, 0.5),
            pol_vt(0.010), pol_vt(0.015), pol_vt(0.020), pol_vt(0.015, cap=0.12), pol_vt(0.020, cap=0.12),
            pol_vt(0.015, cap=0.12, floor=0.06),
            pol_vt_staged(0.015, 0.10, 0.5), pol_vt_staged(0.020, 0.10, 0.5), pol_vt_staged(0.010, 0.10, 0.5)]
P("| polityka | sr. ALLOC | sigma_d kap. (sr.) | P(kill 12t) alfa 0 | P(kill 12t) alfa 0, start -21% | DD p95 12t alfa 0 | mediana wyniku 12t alfa +1pp/t | alfa +2pp/t | P(wynik>0) 12t alfa +2 | mediana 12t alfa -1pp/t | sr. 12t alfa +2 |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
res["polityki"] = {}
for name, fa, staged in POLICIES:
    al = fa(BM)
    r0 = sim_paths(UM, al, 0.0, staged=staged)
    r0s = sim_paths(UM, al, 0.0, start_dd=0.21, staged=staged)
    r1 = sim_paths(UM, al, 0.01, staged=staged)
    r2 = sim_paths(UM, al, 0.02, staged=staged)
    rm1 = sim_paths(UM, al, -0.01, staged=staged)
    s0 = summarize(*r0[:3]); s1 = summarize(*r1[:3]); s2 = summarize(*r2[:3]); sm = summarize(*rm1[:3])
    sig = float((al * UM.std()).mean() * 100)
    res["polityki"][name] = dict(alloc=float(al.mean()), sigma=sig, p_kill0=s0["p_kill"], p_kill0_start21=float(r0s[2].mean() * 100), dd95=s0["dd_p95"], med1=s1["eq_med"], med2=s2["eq_med"], pwin2=100 - s2["p_strata"], medm1=sm["eq_med"], mean2=s2["eq_mean"])
    P(f"| {name} | {al.mean():.3f} | {sig:.2f}% | **{s0['p_kill']:.1f}%** | {r0s[2].mean()*100:.0f}% | {s0['dd_p95']:.1f}% | {s1['eq_med']:+.1f}% | {s2['eq_med']:+.1f}% | {100-s2['p_strata']:.0f}% | {sm['eq_med']:+.1f}% | {s2['eq_mean']:+.1f}% |")
P()
P("Uwaga: alfa +2 p.p./tyg to srednia W1-W6 (t=0,97, nieistotna); W1-W7 srednia -0,52 p.p. Mnoznik P&L: tydzien = 5 x ALLOC x spread_pp (0,24 -> 1,2x; 0,08 -> 0,4x).")
P()

# kill fixed vs trailing: P(kill) 52 tygodni dla kilku ALLOC, alfa 0 i +1
P("### (5b) kill switch staly (od startu) vs kroczacy (od szczytu), 52 tyg, bootstrap")
P()
U260 = block_boot(pool, 260, NPATH)
def sim_fixed(U, alloc, alpha_d, kill=0.75):
    eq = np.ones(U.shape[0]); killed = np.zeros(U.shape[0], bool)
    for t in range(U.shape[1]):
        eq = np.where(killed, eq, eq * (1 + alloc * (U[:, t] + alpha_d)))
        killed |= eq < kill
    return eq, killed
P("| ALLOC | alfa/tyg | P(kill 52t) kroczacy | P(kill 52t) staly | mediana wyniku kroczacy | mediana staly |")
P("|---|---|---|---|---|---|")
res["kill_fixed_vs_trailing"] = {}
for a in (0.24, 0.12, 0.08):
    for al_w in (0.0, 0.01, 0.02):
        eqt, _, klt, _ = sim_paths(U260, a, al_w)
        eqf, klf = sim_fixed(U260, a, al_w)
        res["kill_fixed_vs_trailing"][f"{a}_{al_w}"] = dict(trail=float(klt.mean() * 100), fixed=float(klf.mean() * 100), med_t=float((np.median(eqt) - 1) * 100), med_f=float((np.median(eqf) - 1) * 100))
        P(f"| {a:.2f} | {al_w*100:+.0f} p.p. | {klt.mean()*100:.1f}% | {klf.mean()*100:.1f}% | {(np.median(eqt)-1)*100:+.1f}% | {(np.median(eqf)-1)*100:+.1f}% |")
P()

# Czas do kill: z jakiego poziomu? rozklad dnia trafienia kill przy 0,24
eq, dd, kl, kd = sim_paths(U60, 0.24)
kdv = kd[kd >= 0]
P(f"ALLOC 0,24, alfa 0: mediana dnia trafienia kill (sposrod sciezek zabitych w 60 ses.) = {np.median(kdv)+1:.0f}. sesja; 25% zabitych przed {np.percentile(kdv,25)+1:.0f}. sesja")
P()

json.dump(res, open(OUT_JSON, "w"), indent=1, default=float)
open(OUT_MD, "w").write("\n".join(out))
print("zapisano", OUT_MD, OUT_JSON)
