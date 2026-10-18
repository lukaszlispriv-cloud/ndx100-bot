#!/usr/bin/env python3 -I
"""Projekt B (przezywalnosc): symulacja polityk sizingu + schodka FLAT + wznowienia.

Wejscie: ../dane/closes_5y.csv, mp_koszyki.json (W1-W7 + W8 wpisane).
Metoda jak ryzyko_sizing.py (2d/5) i weryfikacja_C4.py (B/E):
  * jednostka u = suma 5 long - suma 5 short dziennych zwrotow (rowne wagi),
    kapital_t = kapital_{t-1} * (1 + ALLOC*u - koszt);
  * mieszanka: co tydzien losowy koszyk z W1-W8, 5-sesyjny blok z jego 250-sesyjnej,
    wysrodkowanej historii do D0 (zerowa alfa); alfa dodawana jawnie (p.p./tydz.);
  * sciezka historyczna momentum 6M 2022-2026 (jak v2 bt_symulacja-wykonania);
  * sciezka W1-W7 faktyczna (D0+1 .. nastepne D0).
Polityki: staly ALLOC; ALLOC + schodek FLAT (DD od szczytu CYKLU < -DD_FLAT -> plasko do
konca tygodnia + COOLDOWN tygodni, potem wznowienie od ALLOC_RESTART na N tygodni,
szczyt cyklu := kapital); kill 0,75 x szczyt WSZECHCZASOWY (jak app.py); wariant
KILL_RESUME (po kill plasko 2 tyg., szczyt := kapital, ALLOC_RESTART).
Koszty (opcjonalnie): finansowanie 6%/rok od gross (10*ALLOC) + rotacja 7 nog/tydz. x
0,2% (zamknij+otworz) x ALLOC  => koszt_d = ALLOC * (0,06*10/252 + 7*0,002/5) = 0,00518*ALLOC.
Bez liczb z rachunku. Wyjscie: projekt_B_sim_out.md, projekt_B_sim_wyniki.json.
"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "dane", "closes_5y.csv")
OUT_MD = os.path.join(HERE, "projekt_B_sim_out.md")
OUT_JSON = os.path.join(HERE, "projekt_B_sim_wyniki.json")
rng = np.random.default_rng(20261019)
NPATH = int(os.environ.get("NPATH", "20000"))
KILL = 0.75
COST_K = 0.06 * 10 / 252 + 7 * 0.002 / 5   # na jednostke ALLOC, dziennie

px = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()]
INDEKSY = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
UNIV = [c for c in px.columns if c not in INDEKSY]
ret = px.pct_change()
dates = px.index

kosz = json.load(open(os.path.join(HERE, "mp_koszyki.json")))
kosz["2026-W8"] = {"d0": "2026-10-16", "long": ["GOOGL", "GILD", "MSFT", "QCOM", "ADP"],
                   "short": ["AXON", "DASH", "ALNY", "APP", "FER"]}
WEEKS = [f"2026-W{i}" for i in range(1, 9)]
HIST = {"2026-W1": -4.06, "2026-W2": 6.19, "2026-W3": 1.44, "2026-W4": 13.85,
        "2026-W5": 5.95, "2026-W6": -5.89, "2026-W7": -21.15}

out, res = [], {}
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

def idx_d0(d0):
    return dates.searchsorted(pd.Timestamp(d0), side="right") - 1

def unit_series(k, i_end, win):
    sl = ret.iloc[i_end - win + 1:i_end + 1][k["long"] + k["short"]].dropna()
    return (sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)).values

# ----------------------------------------------------------------------------- silnik
def simulate(U, alloc, alpha_w=0.0, cost=False, dd_flat=None, cooldown_w=1,
             alloc_restart=None, restart_w=4, kill=KILL, kill_resume=None,
             start_dd=0.0, alloc_vec=None):
    """U: (npath, nses) zwroty jednostkowe. alloc: skalar; alloc_vec: (npath, nses) nadpisuje.
    alpha_w: p.p. spreadu/tydz. -> alfa_d jednostkowa = alpha_w/100 (jednostka = suma 10 nog,
    spread_pp tygodnia = u_tyg*100/5).
    dd_flat: prog schodka od szczytu cyklu (np. 0.12) albo None.
    kill_resume: None (po kill plasko do konca) albo liczba tygodni cooldownu, po ktorych
    szczyt := kapital i start od alloc_restart.
    Zwraca slownik metryk i wektory."""
    npath, nses = U.shape
    nweeks = nses // 5
    alpha_d = alpha_w / 100.0
    eq = np.full(npath, 1.0 - start_dd)
    peak_all = np.ones(npath)
    peak_cyc = eq.copy()
    killed = np.zeros(npath, bool)
    ever_killed = np.zeros(npath, bool)
    n_kill = np.zeros(npath, int)
    kill_day = np.full(npath, -1)
    flat_until = np.full(npath, -1)          # tydzien (wlacznie), do ktorego plasko
    restart_left = np.zeros(npath, int)      # tygodnie na ALLOC_RESTART
    n_flat = np.zeros(npath, int)
    days_in_market = np.zeros(npath, int)
    maxdd = np.zeros(npath)
    kill_resume_until = np.full(npath, -1)
    a_restart = alloc_restart if alloc_restart is not None else alloc
    for t in range(nses):
        w = t // 5
        if t % 5 == 0 and t > 0:
            # granica tygodnia: zejscie z restartu
            restart_left = np.maximum(restart_left - 1, 0)
            # wznowienie po FLAT: szczyt cyklu := kapital
            resume = (flat_until == w - 1)
            if resume.any():
                peak_cyc = np.where(resume, eq, peak_cyc)
                restart_left = np.where(resume, restart_w, restart_left)
            if kill_resume is not None:
                kres = killed & (kill_resume_until == w - 1)
                if kres.any():
                    killed = killed & ~kres
                    peak_all = np.where(kres, eq, peak_all)
                    peak_cyc = np.where(kres, eq, peak_cyc)
                    restart_left = np.where(kres, restart_w, restart_left)
        active = (~killed) & (flat_until < w)
        if alloc_vec is not None:
            a = alloc_vec[:, t]
        else:
            a = np.full(npath, alloc)
        a = np.where(restart_left > 0, np.minimum(a, a_restart), a)
        r = a * (U[:, t] + alpha_d) - (COST_K * a if cost else 0.0)
        eq = np.where(active, eq * (1 + r), eq)
        days_in_market += active
        peak_all = np.maximum(peak_all, eq)
        peak_cyc = np.maximum(peak_cyc, eq)
        dd = eq / peak_all - 1
        maxdd = np.minimum(maxdd, dd)
        newkill = active & (eq < kill * peak_all)
        kill_day = np.where(newkill & (kill_day < 0), t, kill_day)
        n_kill += newkill
        killed |= newkill
        ever_killed |= newkill
        if kill_resume is not None:
            kill_resume_until = np.where(newkill, w + kill_resume, kill_resume_until)
        if dd_flat is not None:
            newflat = active & ~newkill & (eq < (1 - dd_flat) * peak_cyc)
            flat_until = np.where(newflat, w + cooldown_w, flat_until)
            n_flat += newflat
    k12 = None
    return dict(eq=eq, maxdd=maxdd, killed=ever_killed, n_kill=n_kill, kill_day=kill_day,
                n_flat=n_flat, days_in_market=days_in_market)

def metrics(r, nses):
    eq, md, kl = r["eq"], r["maxdd"], r["killed"]
    return dict(p_kill=float(kl.mean() * 100),
                p_flat=float((r["n_flat"] > 0).mean() * 100),
                flat_mean=float(r["n_flat"].mean()),
                in_market=float(r["days_in_market"].mean() / nses * 100),
                dd_med=float(np.median(md) * 100), dd_p95=float(np.percentile(md, 5) * 100),
                eq_med=float((np.median(eq) - 1) * 100), eq_mean=float((eq.mean() - 1) * 100),
                eq_p5=float((np.percentile(eq, 5) - 1) * 100), eq_p95=float((np.percentile(eq, 95) - 1) * 100),
                p_strata=float((eq < 1).mean() * 100), p_ruina60=float((eq < 0.60).mean() * 100),
                kills_mean=float(r["n_kill"].mean()))

# ----------------------------------------------------------------------------- A. mieszanka W1-W8
P("# Projekt B — wyniki skryptu projekt_B_sim.py")
P()
P(f"Dane: closes_5y.csv {dates[0].date()}..{dates[-1].date()}, {len(UNIV)} spolek (sklad dzisiejszy). NPATH={NPATH}.")
P()
pool_rows, SIG60 = [], {}
for w in WEEKS:
    k = kosz[w]; i0 = idx_d0(k["d0"])
    u250 = unit_series(k, i0, 250); pool_rows.append(u250 - u250.mean())
    SIG60[w] = unit_series(k, i0, 60).std(ddof=1)
pool = np.concatenate(pool_rows)
P(f"Pula W1-W8 (250 sesji do D0 kazdego koszyka, wysrodkowane): n={len(pool)}, sigma jednostkowa {pool.std()*100:.2f}%/d.")
P("sigma60 jednostkowa per koszyk: " + ", ".join(f"{w[5:]} {SIG60[w]*100:.1f}%" for w in WEEKS))
P()

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

UM, BM = mixture_paths(NPATH, 52)
P(f"Mieszanka 52 tyg.: sigma jednostkowa {UM.std()*100:.2f}%/d; tygodniowa spreadu (p.p.) = {UM.reshape(NPATH,52,5).sum(axis=2).std()*100/5:.2f} p.p.")
P()
def vt_vec(B, tgt=0.015, lo=0.04, hi=0.12):

    # uwaga: sigma kapitalu = ALLOC * sigma_unit (jednostka = suma 10 nog), wiec ALLOC = tgt/sigma_unit
    a = np.vectorize(lambda bi: float(np.clip(tgt / SIG60[WEEKS[bi]], lo, hi)))(B)
    return np.repeat(a, 5, axis=1)

POLITYKI = [
    ("P0 ALLOC 0,24 (dzis)", dict(alloc=0.24)),
    ("P1 ALLOC 0,10", dict(alloc=0.10)),
    ("P2 ALLOC 0,08", dict(alloc=0.08)),
    ("P3 ALLOC 0,06", dict(alloc=0.06)),
    ("P2a 0,08 + FLAT −10% (cooldown 1 tyg., restart 0,06 x4)", dict(alloc=0.08, dd_flat=0.10, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P2b 0,08 + FLAT −12% (cooldown 1 tyg., restart 0,06 x4)", dict(alloc=0.08, dd_flat=0.12, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P2c 0,08 + FLAT −12% (cooldown 2 tyg., restart 0,06 x4)", dict(alloc=0.08, dd_flat=0.12, cooldown_w=2, alloc_restart=0.06, restart_w=4)),
    ("P2d 0,08 + FLAT −15% (cooldown 1 tyg., restart 0,06 x4)", dict(alloc=0.08, dd_flat=0.15, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P3b 0,06 + FLAT −12% (cooldown 1 tyg., restart 0,05 x4)", dict(alloc=0.06, dd_flat=0.12, cooldown_w=1, alloc_restart=0.05, restart_w=4)),
    ("P3c 0,06 + FLAT −12% (cooldown 1 tyg., restart 0,06 = bez redukcji)", dict(alloc=0.06, dd_flat=0.12, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P3d 0,06 + FLAT −10% (cooldown 1 tyg., restart 0,06)", dict(alloc=0.06, dd_flat=0.10, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P5 ALLOC 0,05 (loty: niewykonalne dla ~9 nazw)", dict(alloc=0.05)),
    ("P1b 0,10 + FLAT −12% (cooldown 1 tyg., restart 0,06 x4)", dict(alloc=0.10, dd_flat=0.12, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
    ("P4 VT sigma60 1,5% [0,04;0,12]", dict(alloc=None, vt=True)),
    ("P4b VT 1,5% + FLAT −12% (restart 0,06 x4)", dict(alloc=None, vt=True, dd_flat=0.12, cooldown_w=1, alloc_restart=0.06, restart_w=4)),
]

def run_policy(U, B, cfg, alpha_w, cost, nses=None, kill_resume=None, start_dd=0.0):
    cfg = dict(cfg); vt = cfg.pop("vt", False)
    av = vt_vec(B)[:, :U.shape[1]] if vt else None
    a = cfg.pop("alloc")
    if a is None: a = float(av.mean())
    return simulate(U, a, alpha_w=alpha_w, cost=cost, alloc_vec=av, kill_resume=kill_resume, start_dd=start_dd, **cfg)

P("## A. Mieszanka koszykow W1-W8 (bootstrap blokowy, 52 tygodnie = 260 sesji, 20 000 sciezek)")
P()
res["A"] = {}
for cost in (False, True):
    for alpha_w in (0.0, 1.0, 2.0, -0.5):
        key = f"alfa {alpha_w:+.1f} p.p./tydz., koszty {'TAK' if cost else 'NIE'}"
        P(f"### {key}")
        P()
        P("| polityka | sr. ALLOC | P(kill 12t) | P(kill 26t) | **P(kill 52t)** | P(>=1 FLAT 52t) | sr. FLAT/rok | % sesji w rynku | DD p95 52t | mediana wyniku 52t | p5 | p95 | P(wynik<0) | P(kapital<0,60) |")
        P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        res["A"][key] = {}
        for nm, cfg in POLITYKI:
            r52 = run_policy(UM, BM, cfg, alpha_w, cost)
            r12 = run_policy(UM[:, :60], BM[:, :12], cfg, alpha_w, cost)
            r26 = run_policy(UM[:, :130], BM[:, :26], cfg, alpha_w, cost)
            m = metrics(r52, 260); m12 = metrics(r12, 60); m26 = metrics(r26, 130)
            av = vt_vec(BM) if cfg.get("vt") else None
            amean = float(av.mean()) if av is not None else cfg["alloc"]
            m.update(p_kill12=m12["p_kill"], p_kill26=m26["p_kill"], alloc=amean)
            res["A"][key][nm] = m
            P(f"| {nm} | {amean:.3f} | {m12['p_kill']:.1f}% | {m26['p_kill']:.1f}% | **{m['p_kill']:.1f}%** | {m['p_flat']:.0f}% | {m['flat_mean']:.2f} | {m['in_market']:.0f}% | {m['dd_p95']:.1f}% | {m['eq_med']:+.1f}% | {m['eq_p5']:+.1f}% | {m['eq_p95']:+.1f}% | {m['p_strata']:.0f}% | {m['p_ruina60']:.1f}% |")
        P()

# A2: wznowienie po kill (KILL_RESUME): rozklad kapitalu po roku, liczba killi
P("### A2. Polityka wznowienia po kill (po trafieniu: plasko 2 tygodnie, szczyt := kapital, ALLOC_RESTART x4), alfa 0 i +1, koszty TAK")
P()
P("| polityka | alfa | P(>=1 kill 52t) | sr. killi/rok | mediana wyniku 52t | p5 | P(kapital<0,60) | P(kapital<0,75) |")
P("|---|---|---|---|---|---|---|---|")
res["A2"] = {}
for nm, cfg in [POLITYKI[0], POLITYKI[2], POLITYKI[3], POLITYKI[5], POLITYKI[8], POLITYKI[9]]:
    for alpha_w in (0.0, 1.0):
        r = run_policy(UM, BM, cfg, alpha_w, True, kill_resume=2)
        m = metrics(r, 260); m["p_lt75"] = float((r["eq"] < 0.75).mean() * 100)
        res["A2"][f"{nm}|{alpha_w}"] = m
        P(f"| {nm} | {alpha_w:+.0f} | {m['p_kill']:.1f}% | {m['kills_mean']:.2f} | {m['eq_med']:+.1f}% | {m['eq_p5']:+.1f}% | {m['p_ruina60']:.1f}% | {m['p_lt75']:.1f}% |")
P()

# A3: start z obsunieciem -23,7% (stan 18.10) bez resetu szczytu vs z resetem
P("### A3. Start z obsunieciem (szczyt wszechczasowy nie zresetowany) — P(kill 12t / 52t), alfa 0, koszty TAK")
P()
P("| polityka | start | P(kill 12t) | P(kill 52t) |")
P("|---|---|---|---|")
res["A3"] = {}
for nm, cfg in [POLITYKI[0], POLITYKI[2], POLITYKI[3], POLITYKI[9]]:
    for sd in (0.0, 0.237):
        r52 = run_policy(UM, BM, cfg, 0.0, True, start_dd=sd); r12 = run_policy(UM[:, :60], BM[:, :12], cfg, 0.0, True, start_dd=sd)
        res["A3"][f"{nm}|{sd}"] = dict(k12=float(r12["killed"].mean() * 100), k52=float(r52["killed"].mean() * 100))
        P(f"| {nm} | {-sd*100:.1f}% | {r12['killed'].mean()*100:.1f}% | {r52['killed'].mean()*100:.1f}% |")
P()

# ----------------------------------------------------------------------------- B. sciezka historyczna momentum 6M
P("## B. Sciezka historyczna momentum 6M TOP5/BOTTOM5 2022-2026 (jak weryfikacja_C4.py: wejscie D0+1, wyjscie D5+1)")
P()
df3 = px.ffill(limit=3)
cands = UNIV
Pm = df3[cands].to_numpy(float); PF = df3[cands].ffill().to_numpy(float); NDX = df3["^NDX"].to_numpy(float)
nT, nS = Pm.shape
R = np.vstack([np.full((1, nS), np.nan), PF[1:] / PF[:-1] - 1])
iso = dates.isocalendar(); keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
last_idx = {}
for i, k in enumerate(keys): last_idx[k] = i
weeks = sorted(last_idx)
D0 = np.array([last_idx[w] for w in weeks[:-1]]); D5 = np.array([last_idx[w] for w in weeks[1:]]); nW = len(D0)
WR = Pm[D5] / Pm[D0] - 1
S6 = np.full((nW, nS), np.nan)
for w, d0 in enumerate(D0):
    if d0 - 126 < 0: continue
    S6[w] = Pm[d0] / Pm[d0 - 126] - 1 - (NDX[d0] / NDX[d0 - 126] - 1)
u_vals, wk_of = [], []
for w in range(nW):
    s = S6[w].copy(); s[np.isnan(WR[w])] = np.nan
    E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1)
    s[np.isnan(Pm[E]) | np.isnan(Pm[X])] = np.nan
    ok = np.where(~np.isnan(s))[0]
    if len(ok) < 30: continue
    order = ok[np.argsort(-s[ok], kind="stable")]
    L, S = order[:5], order[-5:]
    for t in range(E + 1, X + 1):
        u_vals.append(R[t, L].sum() - R[t, S].sum()); wk_of.append(w)
u_hist = np.array(u_vals); nD = len(u_hist)
P(f"Sciezka: {len(set(wk_of))} tygodni, {nD} sesji; srednia u {u_hist.mean()*100:+.3f}%/d (= {u_hist.mean()*100:+.2f} p.p. spread/tydz. in-sample), sigma {u_hist.std()*100:.2f}%/d.")
P()
u_dm = u_hist - u_hist.mean()

def windows(series, nses, step=5):
    starts = list(range(0, len(series) - nses + 1, step))
    return np.stack([series[s:s + nses] for s in starts])

res["B"] = {}
for alpha_nm, ser in (("alfa in-sample (+1,0 p.p.)", u_hist), ("alfa 0", u_dm), ("alfa +1 p.p. (wysrodk. +0,01/d)", u_dm + 0.01)):
    P(f"### {alpha_nm}, koszty TAK (rolling okna co 5 sesji)")
    P()
    P("| polityka | okna 12t: P(kill) | okna 52t: P(kill) | okna 52t: P(>=1 FLAT) | sr. FLAT / 52t | DD p95 (52t) | mediana wyniku 52t | p5 wyniku 52t | pelna sciezka: kapital konc. z kill (100) | maxDD pelnej sciezki | FLAT-ow na pelnej |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    res["B"][alpha_nm] = {}
    W12 = windows(ser, 60); W52 = windows(ser, 260)
    for nm, cfg in POLITYKI:
        if cfg.get("vt"): continue
        c = dict(cfg); a = c.pop("alloc")
        r12 = simulate(W12, a, 0.0, True, **c); r52 = simulate(W52, a, 0.0, True, **c)
        full = simulate(ser[None, :], a, 0.0, True, **c)
        m52 = metrics(r52, 260)
        res["B"][alpha_nm][nm] = dict(k12=float(r12["killed"].mean() * 100), k52=m52["p_kill"], flat52=m52["p_flat"], flatmean=m52["flat_mean"],
                                      dd95=m52["dd_p95"], med=m52["eq_med"], p5=m52["eq_p5"], full_end=float(full["eq"][0] * 100), full_dd=float(full["maxdd"][0] * 100), full_flat=int(full["n_flat"][0]))
        P(f"| {nm} | {r12['killed'].mean()*100:.1f}% | **{m52['p_kill']:.1f}%** | {m52['p_flat']:.0f}% | {m52['flat_mean']:.2f} | {m52['dd_p95']:.1f}% | {m52['eq_med']:+.1f}% | {m52['eq_p5']:+.1f}% | {full['eq'][0]*100:.0f} | {full['maxdd'][0]*100:.1f}% | {int(full['n_flat'][0])} |")
    P()

# ----------------------------------------------------------------------------- C. W1-W7 faktyczne
P("## C. Sciezka W1-W7 faktyczna (koszyki z history, dzienne zwroty D0+1..nastepne D0, bez stopow; W4 11 sesji)")
P()
segs, labels = [], []
for w, wn in zip(WEEKS[:-1], WEEKS[1:]):
    k = kosz[w]; i0 = idx_d0(k["d0"]); i1 = idx_d0(kosz[wn]["d0"])
    sl = ret.iloc[i0 + 1:i1 + 1]
    u = (sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)).values
    segs.append(u); labels += [w] * len(u)
u_w17 = np.concatenate(segs); labels = np.array(labels)
P(f"{len(u_w17)} sesji; suma u {u_w17.sum()*100:+.1f}% jednostkowo (x0,24 = {u_w17.sum()*24:+.1f}% kapitalu liniowo).")
P()
P("| polityka | wynik W1-W7 (zlozony, koszty TAK) | maxDD | FLAT (kiedy) | kill? | W6+W7 |")
P("|---|---|---|---|---|---|")
res["C"] = {}
# wariant dzienny z tygodniami o roznej dlugosci: schodek sprawdzany dziennie, granice tygodni = granice koszykow
def simulate_segments(segs, alloc, dd_flat=None, cooldown_w=1, alloc_restart=None, restart_w=4, cost=True):
    eq = 1.0; peak_all = 1.0; peak_cyc = 1.0; flat_until = -1; restart_left = 0
    killed = False; flats = []; maxdd = 0.0; path = []
    a_restart = alloc_restart or alloc
    for wi, seg in enumerate(segs):
        if wi > 0:
            restart_left = max(restart_left - 1, 0)
            if flat_until == wi - 1:
                peak_cyc = eq; restart_left = restart_w
        for u in seg:
            active = (not killed) and (flat_until < wi)
            a = min(alloc, a_restart) if restart_left > 0 else alloc
            if active:
                eq *= 1 + a * u - (COST_K * a if cost else 0.0)
            peak_all = max(peak_all, eq); peak_cyc = max(peak_cyc, eq)
            maxdd = min(maxdd, eq / peak_all - 1)
            if active and eq < KILL * peak_all:
                killed = True
            elif active and dd_flat is not None and eq < (1 - dd_flat) * peak_cyc:
                flat_until = wi + cooldown_w; flats.append(WEEKS[wi])
        path.append(eq)
    return eq, maxdd, flats, killed, path
for nm, cfg in POLITYKI:
    if cfg.get("vt"): continue
    c = dict(cfg); a = c.pop("alloc")
    eq, md, flats, kl, path = simulate_segments(segs, a, **c)
    w67 = path[-1] / path[-3] - 1
    res["C"][nm] = dict(wynik=float((eq - 1) * 100), maxdd=float(md * 100), flats=flats, kill=kl, w67=float(w67 * 100), path=[float(x) for x in path])
    P(f"| {nm} | {(eq-1)*100:+.1f}% | {md*100:.1f}% | {len(flats)} ({', '.join(f[5:] for f in flats) or '-'}) | {'TAK' if kl else 'nie'} | {w67*100:+.1f}% |")
P()
P("Tygodniowo (zlozone, koszty TAK) dla ALLOC 0,24 vs 0,08: " + " | ".join(
    f"{WEEKS[i][5:]}: {((res['C'][POLITYKI[0][0]]['path'][i] / (res['C'][POLITYKI[0][0]]['path'][i-1] if i else 1)) - 1)*100:+.1f}% / {((res['C'][POLITYKI[2][0]]['path'][i] / (res['C'][POLITYKI[2][0]]['path'][i-1] if i else 1)) - 1)*100:+.1f}%"
    for i in range(7)))
P()

# ----------------------------------------------------------------------------- D. oczekiwane metryki w jednostkach kapitalu
P("## D. Oczekiwane metryki (ALLOC 0,08): przelozenie spreadu na kapital, koszty, prog oplacalnosci")
P()
sig_spread_hist = np.std([HIST[w] for w in WEEKS[:-1]], ddof=1)
sig_spread_mix = UM.reshape(NPATH, 52, 5).sum(axis=2).std() * 100 / 5
for a in (0.24, 0.10, 0.08, 0.06):
    cost_w = COST_K * a * 5 * 100
    P(f"- ALLOC {a:.2f}: 1 p.p. spreadu = {5*a:.2f}% kapitalu; sigma tyg. kapitalu przy sigma spreadu {sig_spread_mix:.1f} p.p. (mieszanka) = {5*a*sig_spread_mix:.2f}%, przy 11,3 p.p. (W1-W7) = {5*a*11.3:.2f}%, przy 7,4 p.p. (momentum 6M) = {5*a*7.4:.2f}%; koszt modelowy {cost_w:.3f}%/tydz. = {cost_w/(5*a):.2f} p.p. spreadu/tydz. (prog oplacalnosci); finansowanie {0.06*10*a*100:.1f}%/rok, rotacja {7*0.002*a*52*100:.1f}%/rok")
P()
res["D"] = dict(sig_spread_mix=float(sig_spread_mix), sig_spread_hist=float(sig_spread_hist), cost_k=COST_K)

# ----------------------------------------------------------------------------- E. wykonalnosc lotow
P("## E. Wykonalnosc lotow (krok 0,1 akcji, calc_size: min. lot otwierany gdy <= 1,6 x cel; kapital odniesienia START_EQUITY 1000 oraz 0,83 x START_EQUITY jak stosunek z C9)")
P()
last = px.iloc[-1]
P("| kapital odn. | ALLOC | cel/noge | nogi POMIJANE (0,1 akcji > 1,6 x cel) | nogi na min. locie z przestrzalem (cel; 1,6 cel] |")
P("|---|---|---|---|---|")
res["E"] = {}
for kap in (1000, 830):
    for a in (0.10, 0.08, 0.06, 0.05, 0.04):
        cel = kap * a
        pom = [t for t in UNIV if pd.notna(last[t]) and last[t] * 0.1 > cel * 1.6]
        prz = [t for t in UNIV if pd.notna(last[t]) and cel < last[t] * 0.1 <= cel * 1.6]
        res["E"][f"{kap}_{a}"] = dict(pomijane=pom, przestrzal=prz)
        P(f"| {kap} | {a:.2f} | {cel:.0f} | {len(pom)}: {', '.join(pom) if pom else '-'} | {len(prz)}: {', '.join(prz)} |")
P()
w8 = kosz["2026-W8"]["long"] + kosz["2026-W8"]["short"]
P("W8 (GOOGL GILD MSFT QCOM ADP / AXON DASH ALNY APP FER), 0,1 akcji w USD: " + ", ".join(f"{t} {last[t]*0.1:.0f}" for t in w8))
P()

json.dump(res, open(OUT_JSON, "w"), indent=1, default=float)
open(OUT_MD, "w").write("\n".join(out) + "\n")
print("zapisano", OUT_MD, OUT_JSON)
