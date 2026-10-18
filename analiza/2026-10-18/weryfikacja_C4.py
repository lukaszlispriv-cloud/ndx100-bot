#!/usr/bin/env python3 -I
"""Weryfikacja twierdzenia C4 (sizing / P(kill) / vol-target).

Testy:
 A. Dzienna seria jednostkowa koszyka momentum 6M 5/5 (jak v2 w bt_symulacja-wykonania.py):
    autokorelacja |u|, u^2, sigma tygodniowej -> czy tygodnie sa niezalezne.
 B. P(kill 25% od kroczacego szczytu) na sciezce historycznej (okna kroczace 12/52 tyg.),
    z alfa in-sample i po wysrodkowaniu (alfa 0).
 C. Bootstrap: iid dzienny, blok 5/10/20/60, tygodniowy iid; GARCH(1,1) z resztami bootstrapowymi.
 D. Estymator sigma: sigma20 vs sigma60 vs EWMA jako prognoza sigma koszyka w nastepnym tygodniu
    (panel koszykow momentum) + koszyki W4-W8 (w tym W7 dzien po dniu).
 E. Polityki na sciezce historycznej 2022-2026: staly 0,24/0,12/0,10/0,08; vol-target sigma60/sigma20/EWMA
    (cel 1,5%/d, clip 0,04-0,12); alfa in-sample / 0 / +1 p.p. tyg.
 F. Polityki na bootstrapie mieszanki W1-W8 (jak ryzyko_sizing.py §2d) z blokiem 5/10/20, sigma20 vs sigma60.
 G. Wykonalnosc inverse-vol per noga przy kroku 0,1 akcji (logika calc_size z app.py).
Wyjscie: weryfikacja_C4_out.md, weryfikacja_C4_wyniki.json.
"""
import json, math, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "dane", "closes_5y.csv")
OUT_MD = os.path.join(HERE, "weryfikacja_C4_out.md")
OUT_JSON = os.path.join(HERE, "weryfikacja_C4_wyniki.json")
rng = np.random.default_rng(20261018)
NPATH = 20000
KILL = 0.75

out = []; res = {}
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s, flush=True)

# ----------------------------------------------------------------------------- dane
df = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
df = df[df["^NDX"].notna()]
df3 = df.ffill(limit=3)
NON = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
cands = [c for c in df.columns if c not in NON]
dates = df.index
Pm = df3[cands].to_numpy(float)
PF = df3[cands].ffill().to_numpy(float)
NDX = df3["^NDX"].to_numpy(float)
nT, nS = Pm.shape
COL = {c: i for i, c in enumerate(cands)}
R = np.vstack([np.full((1, nS), np.nan), PF[1:] / PF[:-1] - 1])
Rn = np.vstack([np.full((1, nS), np.nan), Pm[1:] / Pm[:-1] - 1])  # z NaN, do sigma ex ante

iso = dates.isocalendar()
keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
last_idx = {}
for i, k in enumerate(keys):
    last_idx[k] = i
weeks = sorted(last_idx)
D0 = np.array([last_idx[w] for w in weeks[:-1]]); D5 = np.array([last_idx[w] for w in weeks[1:]])
nW = len(D0)
WR = Pm[D5] / Pm[D0] - 1

def mom_score(L=126):
    S = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - L < 0: continue
        S[w] = Pm[d0] / Pm[d0 - L] - 1 - (NDX[d0] / NDX[d0 - L] - 1)
    return S
S6 = mom_score(126)
LONGS, SHORTS = [], []
for w in range(nW):
    s = S6[w].copy(); s[np.isnan(WR[w])] = np.nan
    E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1)
    s[np.isnan(Pm[E]) | np.isnan(Pm[X])] = np.nan
    ok = np.where(~np.isnan(s))[0]
    if len(ok) < 30: LONGS.append(None); SHORTS.append(None); continue
    order = ok[np.argsort(-s[ok], kind="stable")]
    LONGS.append(order[:5]); SHORTS.append(order[-5:])
widx = np.array([w for w in range(nW) if LONGS[w] is not None])

# dzienna seria jednostkowa (suma 5 long - suma 5 short), wejscie D0+1 close, wyjscie D5+1 close
u_days = []; u_vals = []; week_of_day = []
sig60_w = {}; sig20_w = {}; ewma_w = {}; real_w = {}
for w in widx:
    E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1)
    L = LONGS[w]; S = SHORTS[w]
    for t in range(E + 1, X + 1):
        u = R[t, L].sum() - R[t, S].sum()
        u_days.append(t); u_vals.append(u); week_of_day.append(w)
    # sigma ex ante (znane w sobote: dane do D0)
    hist = Rn[D0[w] - 59:D0[w] + 1][:, np.concatenate([L, S])]
    ok = ~np.isnan(hist).any(axis=1)
    uh = hist[ok][:, :5].sum(axis=1) - hist[ok][:, 5:].sum(axis=1)
    sig60_w[w] = uh.std(ddof=1) if len(uh) >= 40 else np.nan
    sig20_w[w] = uh[-20:].std(ddof=1) if len(uh) >= 20 else np.nan
    lam = 0.94; wgt = lam ** np.arange(len(uh))[::-1]
    ewma_w[w] = math.sqrt(np.sum(wgt * uh ** 2) / wgt.sum()) if len(uh) >= 20 else np.nan
    uu = np.array(u_vals[-(X - E):])
    real_w[w] = math.sqrt(np.mean(uu ** 2)) if len(uu) else np.nan
u = np.array(u_vals); u_days = np.array(u_days); week_of_day = np.array(week_of_day)
nD = len(u)
P("# Weryfikacja C4 — skrypt weryfikacja_C4.py")
P()
P(f"Dane: {CSV}; sesje {dates[0].date()}..{dates[-1].date()}; uniwersum {nS} spolek (sklad dzisiejszy, survivorship bias).")
P(f"Sciezka momentum 6M 5/5 (jak v2 w bt_symulacja-wykonania.py): {len(widx)} tygodni, {nD} sesji, {dates[u_days[0]].date()}..{dates[u_days[-1]].date()}.")
P(f"Zwrot jednostkowy u = suma 5 long - suma 5 short; zwrot kapitalu = ALLOC x u. Srednia u {u.mean()*100:+.3f}%/d (= {u.mean()*100*5/5:+.2f} p.p. spread/tydz.), sigma u {u.std()*100:.2f}%/d (x0,24 = {u.std()*24:.2f}%/d kapitalu).")
res["sciezka"] = dict(n_tyg=int(len(widx)), n_ses=int(nD), mean_u=float(u.mean()), sd_u=float(u.std()))

# ----------------------------------------------------------------------------- A. autokorelacja
P()
P("## A. Czy tygodnie sa niezalezne? Autokorelacja zmiennosci sciezki momentum")
P()
def acf(x, lags):
    x = x - x.mean(); v = (x * x).mean()
    return [float((x[:-k] * x[k:]).mean() / v) for k in lags]
lags = [1, 2, 3, 5, 10, 20]
a_u = acf(u, lags); a_abs = acf(np.abs(u), lags); a_sq = acf(u ** 2, lags)
P("| lag | ACF u | ACF |u| | ACF u^2 |"); P("|---|---|---|---|")
for k, a1, a2, a3 in zip(lags, a_u, a_abs, a_sq):
    P(f"| {k} | {a1:+.3f} | {a2:+.3f} | {a3:+.3f} |")
# tygodniowa sigma zrealizowana i jej autokorelacja
wk_ids = sorted(set(week_of_day))
wk_sig = np.array([math.sqrt(np.mean(u[week_of_day == w] ** 2)) for w in wk_ids])
wk_ret = np.array([u[week_of_day == w].sum() for w in wk_ids])
a_ws = acf(wk_sig, [1, 2, 4, 8]); a_wr = acf(wk_ret, [1, 2, 4])
P()
P(f"Sigma tygodniowa zrealizowana (RMS u w tygodniu, n={len(wk_sig)}): ACF lag1 {a_ws[0]:+.3f}, lag2 {a_ws[1]:+.3f}, lag4 {a_ws[2]:+.3f}, lag8 {a_ws[3]:+.3f}. Zwrot tygodniowy: ACF lag1 {a_wr[0]:+.3f}, lag2 {a_wr[1]:+.3f}, lag4 {a_wr[2]:+.3f}.")
P(f"Blad std ACF ~ 1/sqrt(n): dzienny {1/math.sqrt(nD):.3f}, tygodniowy {1/math.sqrt(len(wk_sig)):.3f}. Ljung-Box-podobna suma kwadratow ACF(u^2) lag 1-20 x n = {nD*sum(a*a for a in acf(u**2, range(1,21))):.0f} (chi2(20) krytyczne 31,4).")
res["acf"] = dict(u=a_u, abs=a_abs, sq=a_sq, wk_sigma=a_ws, wk_ret=a_wr)

# ----------------------------------------------------------------------------- silnik
def sim(unit, alloc, alpha_d=0.0, start_dd=0.0, kill=KILL):
    """unit (npath, n). alloc skalar albo (npath,n). Zwraca eq, maxdd, killed, kill_day."""
    npath, n = unit.shape
    eq = np.full(npath, 1.0 - start_dd); peak = np.ones(npath)
    killed = np.zeros(npath, bool); kday = np.full(npath, -1); maxdd = np.zeros(npath)
    for t in range(n):
        a = alloc if np.isscalar(alloc) else alloc[:, t]
        r = a * (unit[:, t] + alpha_d)
        eq = np.where(killed, eq, eq * (1 + r))
        peak = np.maximum(peak, eq); dd = eq / peak - 1; maxdd = np.minimum(maxdd, dd)
        nk = (~killed) & (eq < kill * peak); kday = np.where(nk, t, kday); killed |= nk
    return eq, maxdd, killed, kday

def block_boot(pool, nses, npath, block):
    if block == 1:
        return pool[rng.integers(0, len(pool), size=(npath, nses))]
    nb = math.ceil(nses / block)
    st = rng.integers(0, len(pool) - block + 1, size=(npath, nb))
    idx = (st[:, :, None] + np.arange(block)[None, None, :]).reshape(npath, -1)[:, :nses]
    return pool[idx]

# ----------------------------------------------------------------------------- B. sciezka historyczna
P()
P("## B. P(kill) na sciezce historycznej momentum 6M (okna kroczace, start od szczytu = kapital startowy)")
P()
u_dm = u - u.mean()
def rolling_kill(series, nses, alloc, step=5):
    starts = range(0, len(series) - nses + 1, step)
    hits = 0; tot = 0; mins = []
    for s in starts:
        eq, dd, k, _ = sim(series[None, s:s + nses], alloc)
        hits += int(k[0]); tot += 1; mins.append(dd[0])
    return hits / tot * 100, tot, float(np.percentile(mins, 5) * 100)
P("| ALLOC | 12 tyg., alfa in-sample (+1,3 p.p./tyg) | 12 tyg., alfa 0 (wysrodkowane) | 52 tyg., alfa in-sample | 52 tyg., alfa 0 | DD p95 12 tyg. alfa 0 |")
P("|---|---|---|---|---|---|")
res["hist"] = {}
for a in (0.24, 0.16, 0.12, 0.10, 0.08):
    k12i, n12, _ = rolling_kill(u, 60, a); k12z, _, dd12 = rolling_kill(u_dm, 60, a)
    k52i, n52, _ = rolling_kill(u, 260, a); k52z, _, _ = rolling_kill(u_dm, 260, a)
    res["hist"][a] = dict(k12_in=k12i, k12_zero=k12z, k52_in=k52i, k52_zero=k52z, n12=n12, n52=n52)
    P(f"| {a:.2f} | {k12i:.1f}% (n={n12}) | **{k12z:.1f}%** | {k52i:.1f}% (n={n52}) | **{k52z:.1f}%** | {dd12:.1f}% |")
P()
P("Uwaga: okna nakladajace sie (krok 5 sesji), wiec n to nie liczba niezaleznych prob. '37-41%' z C4 pochodzi z okien 12-tyg. Z alfa in-sample (sredni spread +1,0 p.p./tydz., kapital +1,3 p.p.); C4 przypisuje te liczbe 'zerowej alfie'.")

# ----------------------------------------------------------------------------- C. bootstrap: iid / bloki / tygodniowy / GARCH
P()
P("## C. Bootstrap z wysrodkowanej sciezki momentum (alfa 0): zaleznosc P(kill) od struktury zaleznosci")
P()
# tygodniowy iid: losuj cale tygodnie
weeks_list = [u_dm[week_of_day == w] for w in wk_ids]
def weekly_boot(nweeks, npath):
    outm = np.empty((npath, nweeks * 5))
    for p in range(npath):
        pick = rng.integers(0, len(weeks_list), size=nweeks)
        row = []
        for q in pick:
            wk = weeks_list[q]
            if len(wk) >= 5: row.extend(wk[:5])
            else: row.extend(list(wk) + [0.0] * (5 - len(wk)))
        outm[p] = row
    return outm

# GARCH(1,1) MLE przez siatke + udoskonalenie (bez scipy)
def garch_nll(params, x):
    om, al, be = params
    if om <= 0 or al < 0 or be < 0 or al + be >= 0.999: return 1e18
    n = len(x); h = np.empty(n); h[0] = x.var()
    for t in range(1, n):
        h[t] = om + al * x[t - 1] ** 2 + be * h[t - 1]
    return 0.5 * np.sum(np.log(h) + x ** 2 / h)
def fit_garch(x):
    v = x.var(); best = (1e18, None)
    for al in np.linspace(0.02, 0.30, 15):
        for be in np.linspace(0.50, 0.97, 24):
            if al + be >= 0.999: continue
            om = v * (1 - al - be)
            nll = garch_nll((om, al, be), x)
            if nll < best[0]: best = (nll, (om, al, be))
    # udoskonalenie lokalne
    om, al, be = best[1]
    for _ in range(3):
        for dal in np.linspace(-0.02, 0.02, 9):
            for dbe in np.linspace(-0.02, 0.02, 9):
                a2, b2 = al + dal, be + dbe
                if a2 < 0 or b2 < 0 or a2 + b2 >= 0.999: continue
                o2 = v * (1 - a2 - b2)
                nll = garch_nll((o2, a2, b2), x)
                if nll < best[0]: best = (nll, (o2, a2, b2))
        om, al, be = best[1]
    return best
nll, (om, al, be) = fit_garch(u_dm)
n = len(u_dm); h = np.empty(n); h[0] = u_dm.var()
for t in range(1, n): h[t] = om + al * u_dm[t - 1] ** 2 + be * h[t - 1]
z = u_dm / np.sqrt(h)
P(f"GARCH(1,1) na u (wysrodkowane): omega {om:.2e}, alpha {al:.3f}, beta {be:.3f}, alpha+beta {al+be:.3f} (polowiczny czas zaniku szoku {math.log(0.5)/math.log(al+be):.1f} sesji); sigma bezwarunkowa {math.sqrt(om/(1-al-be))*100:.2f}%/d; kurtoza reszt z {float(((z-z.mean())**4).mean()/z.var()**2):.2f} (u surowe {float(((u_dm)**4).mean()/u_dm.var()**2):.2f}).")
res["garch"] = dict(omega=om, alpha=al, beta=be, nll=float(nll))
def garch_sim(nses, npath, h0=None):
    zz = z[rng.integers(0, len(z), size=(npath, nses))]
    outm = np.empty((npath, nses)); hh = np.full(npath, om / (1 - al - be) if h0 is None else h0)
    for t in range(nses):
        x = np.sqrt(hh) * zz[:, t]; outm[:, t] = x
        hh = om + al * x ** 2 + be * hh
    return outm

P()
P("| ALLOC | horyzont | iid dzienny | blok 5 | blok 10 | blok 20 | blok 60 | tygodniowy iid | GARCH(1,1) | GARCH start h=sigma60 W7 |")
P("|---|---|---|---|---|---|---|---|---|---|")
# h0 dla scenariusza: start z sigma jednostkowa jak koszyk W7 (18,3%/d) -> jako wariancja
H0_W7 = (0.183) ** 2
res["boot"] = {}
for nses, hor in ((60, "12 tyg."), (260, "52 tyg.")):
    U = {}
    U["iid"] = block_boot(u_dm, nses, NPATH, 1)
    for b in (5, 10, 20, 60): U[f"blok{b}"] = block_boot(u_dm, nses, NPATH, b)
    U["tyg"] = weekly_boot(nses // 5, 5000)
    U["garch"] = garch_sim(nses, NPATH)
    U["garch_w7"] = garch_sim(nses, NPATH, h0=H0_W7)
    for a in (0.24, 0.12, 0.10, 0.08):
        row = {}
        for k2, M in U.items():
            _, _, kl, _ = sim(M, a); row[k2] = float(kl.mean() * 100)
        res["boot"][f"{a}_{nses}"] = row
        P(f"| {a:.2f} | {hor} | {row['iid']:.1f}% | {row['blok5']:.1f}% | {row['blok10']:.1f}% | {row['blok20']:.1f}% | {row['blok60']:.1f}% | {row['tyg']:.1f}% | {row['garch']:.1f}% | {row['garch_w7']:.1f}% |")
P()
P("Pula: sciezka momentum 6M (sigma u 18%/d, jak koszyki W1-W8: 17,5%). 'tygodniowy iid' = losowanie calych tygodni (zalozenie niezaleznych tygodni z C4). GARCH start h=sigma W7 = scenariusz 'zaczynamy w tygodniu o podwyzszonej zmiennosci'.")

# ----------------------------------------------------------------------------- D. estymator sigma
P()
P("## D. Estymator sigma koszyka: sigma20 vs sigma60 vs EWMA(0,94) jako prognoza sigma w nastepnym tygodniu")
P()
ok = np.array([w for w in widx if not (np.isnan(sig60_w[w]) or np.isnan(sig20_w[w]) or np.isnan(real_w[w]))])
s60 = np.array([sig60_w[w] for w in ok]); s20 = np.array([sig20_w[w] for w in ok]); sew = np.array([ewma_w[w] for w in ok]); rl = np.array([real_w[w] for w in ok])
P(f"Panel: {len(ok)} tygodni koszykow momentum (sigma koszyka wybranego w sobote liczona z jego wlasnej historii do D0; realizacja = RMS u w tygodniu po wejsciu).")
P("| estymator | corr(log prognoza, log realizacja) | mediana realiz./prognoza | udzial tygodni realiz. > 1,5x prognoza | udzial > 2x | MAE log |")
P("|---|---|---|---|---|---|")
res["estymator"] = {}
for nm, est in (("sigma60", s60), ("sigma20", s20), ("EWMA 0,94", sew), ("max(sigma20,sigma60)", np.maximum(s20, s60))):
    c = float(np.corrcoef(np.log(est), np.log(rl))[0, 1]); ratio = rl / est
    res["estymator"][nm] = dict(corr=c, med=float(np.median(ratio)), p15=float((ratio > 1.5).mean()*100), p2=float((ratio > 2).mean()*100), mae=float(np.mean(np.abs(np.log(ratio)))))
    P(f"| {nm} | {c:.3f} | {np.median(ratio):.2f} | {(ratio>1.5).mean()*100:.1f}% | {(ratio>2).mean()*100:.1f}% | {np.mean(np.abs(np.log(ratio))):.3f} |")
P()
# vol-target: sigma kapitalu zrealizowana per tydzien przy ALLOC = cel/sigma_est, clip
def vt_alloc(est, tgt=0.015, lo=0.04, hi=0.12):
    return np.clip(tgt / est, lo, hi)
for nm, est in (("sigma60", s60), ("sigma20", s20), ("EWMA", sew)):
    a_w = vt_alloc(est); sig_cap = a_w * rl
    P(f"- vol-target 1,5%/d z {nm}: sr. ALLOC {a_w.mean():.3f}; zrealizowana sigma_d kapitalu: mediana {np.median(sig_cap)*100:.2f}%, p90 {np.percentile(sig_cap,90)*100:.2f}%, p99 {np.percentile(sig_cap,99)*100:.2f}%, max {sig_cap.max()*100:.2f}%; udzial tygodni z sigma_d kapitalu > 3% (2x cel): {(sig_cap>0.03).mean()*100:.1f}%")
a_fix = 0.10; sig_cap = a_fix * rl
P(f"- staly ALLOC 0,10: zrealizowana sigma_d kapitalu: mediana {np.median(sig_cap)*100:.2f}%, p90 {np.percentile(sig_cap,90)*100:.2f}%, p99 {np.percentile(sig_cap,99)*100:.2f}%, max {sig_cap.max()*100:.2f}%; udzial > 3%: {(sig_cap>0.03).mean()*100:.1f}%")
P()

# koszyki W4-W8: sigma20/60 na D0 i dzien po dniu w tygodniu W7
kosz = json.load(open(os.path.join(HERE, "mp_koszyki.json")))
kosz["2026-W8"] = {"long": ["GOOGL", "GILD", "MSFT", "QCOM", "ADP"], "short": ["AXON", "DASH", "ALNY", "APP", "FER"], "d0": "2026-10-16"}
WEEKS = ["2026-W1", "2026-W2", "2026-W3", "2026-W4", "2026-W5", "2026-W6", "2026-W7", "2026-W8"]
hist_spread = {"2026-W1": -4.06, "2026-W2": 6.19, "2026-W3": 1.44, "2026-W4": 13.85, "2026-W5": 5.95, "2026-W6": -5.89, "2026-W7": -21.15}
ret_df = df.pct_change()
def unit_series(k, i_end, win):
    sl = ret_df.iloc[i_end - win + 1:i_end + 1][k["long"] + k["short"]].dropna()
    return (sl[k["long"]].sum(axis=1) - sl[k["short"]].sum(axis=1)).values
P("Koszyki faktyczne W1-W8 na D0 (sobota): sigma jednostkowa z 60 vs 20 sesji i wynikajacy ALLOC (cel 1,5%/d, clip 0,04-0,12) oraz P&L tygodnia:")
P()
P("| W | sigma60 | sigma20 | sigma20/sigma60 | ALLOC(sigma60) | ALLOC(sigma20) | ALLOC(max) | spread_pp | P&L kap. 0,24 | P&L sigma60 | P&L sigma20 | P&L staly 0,10 |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|")
res["koszyki"] = {}; tot = dict(a24=0, s60=0, s20=0, f10=0, mx=0)
for w in WEEKS:
    k = kosz[w]; i0 = dates.searchsorted(pd.Timestamp(k["d0"]), side="right") - 1
    uu = unit_series(k, i0, 60); sg60 = uu.std(ddof=1); sg20 = uu[-20:].std(ddof=1)
    a60 = float(np.clip(0.015 / sg60, 0.04, 0.12)); a20 = float(np.clip(0.015 / sg20, 0.04, 0.12)); amx = min(a60, a20)
    sp = hist_spread.get(w)
    pl = lambda a: 5 * a * sp if sp is not None else None
    if sp is not None:
        tot["a24"] += pl(0.24); tot["s60"] += pl(a60); tot["s20"] += pl(a20); tot["f10"] += pl(0.10); tot["mx"] += pl(amx)
    res["koszyki"][w] = dict(sig60=float(sg60), sig20=float(sg20), a60=a60, a20=a20)
    f = lambda x: f"{x:+.1f}%" if x is not None else "-"
    P(f"| {w[5:]} | {sg60*100:.1f}% | {sg20*100:.1f}% | {sg20/sg60:.2f} | {a60*100:.1f}% | {a20*100:.1f}% | {amx*100:.1f}% | {sp if sp is not None else '-'} | {f(pl(0.24))} | {f(pl(a60))} | {f(pl(a20))} | {f(pl(0.10))} |")
P(f"Suma W1-W7 (liniowo, bez kosztow): ALLOC 0,24 {tot['a24']:+.1f}%, vol-target sigma60 {tot['s60']:+.1f}%, sigma20 {tot['s20']:+.1f}%, min(ALLOC60, ALLOC20) {tot['mx']:+.1f}%, staly 0,10 {tot['f10']:+.1f}%.")
res["koszyki_suma"] = tot
P()
# W7 dzien po dniu
k = kosz["2026-W7"]; i0 = dates.searchsorted(pd.Timestamp("2026-10-09"), side="right") - 1
P("W7 (koszyk z 9.10, sesje 12-16.10): sigma20/sigma60 jednostkowa liczona na kazde zamkniecie, zwrot jednostkowy dnia i skumulowany:")
P()
P("| sesja | u dnia | sigma20 do tej sesji | sigma60 | |u|/sigma60 ex ante | skumulowany u |")
P("|---|---|---|---|---|---|")
sg60_0 = unit_series(k, i0, 60).std(ddof=1); cum = 0.0
for j in range(0, 6):
    i = i0 + j
    if i >= len(dates): break
    uu = unit_series(k, i, 60); d_u = uu[-1] if j > 0 else 0.0; cum += d_u if j > 0 else 0.0
    P(f"| {dates[i].date()} | {d_u*100:+.2f}% | {uu[-20:].std(ddof=1)*100:.1f}% | {uu.std(ddof=1)*100:.1f}% | {abs(d_u)/sg60_0:.1f} | {cum*100:+.1f}% |")
P(f"Interpretacja: zwrot W7 jednostkowy {cum*100:+.1f}% (x0,24 = {cum*24:+.1f}% kapitalu, zgodne z -21,15 p.p. x 1,2 = -25,4%) przy sigma60 ex ante {sg60_0*100:.1f}%/d -> {cum/(sg60_0*math.sqrt(5)):+.1f} sigma tygodniowej.")
res["w7_dni"] = dict(cum=float(cum), sig60_d0=float(sg60_0))

# ----------------------------------------------------------------------------- E. polityki na sciezce historycznej
P()
P("## E. Polityki sizingu na sciezce historycznej momentum 6M 2022-2026 (tygodniowe przeskalowanie)")
P()
# alloc dzienny z polityki (per tydzien)
def alloc_series(policy):
    a = np.empty(nD)
    for w in wk_ids:
        m = week_of_day == w
        if policy[0] == "fix": a[m] = policy[1]
        else:
            est = {"s60": sig60_w, "s20": sig20_w, "ewma": ewma_w}[policy[1]][w]
            if np.isnan(est): est = np.nanmedian(list(sig60_w.values()))
            val = float(np.clip(policy[2] / est, policy[3], policy[4]))
            if policy[1] == "s60" and len(policy) > 5 and policy[5] == "min20":
                e20 = sig20_w[w]
                if not np.isnan(e20): val = min(val, float(np.clip(policy[2] / e20, policy[3], policy[4])))
            a[m] = val
    return a
POL = [("ALLOC 0,24 staly", ("fix", 0.24)), ("ALLOC 0,12 staly", ("fix", 0.12)), ("ALLOC 0,10 staly", ("fix", 0.10)), ("ALLOC 0,08 staly", ("fix", 0.08)),
       ("VT sigma60 1,5% [0,04;0,12]", ("vt", "s60", 0.015, 0.04, 0.12)), ("VT sigma20 1,5% [0,04;0,12]", ("vt", "s20", 0.015, 0.04, 0.12)),
       ("VT EWMA 1,5% [0,04;0,12]", ("vt", "ewma", 0.015, 0.04, 0.12)), ("VT min(s60,s20) 1,5% [0,04;0,12]", ("vt", "s60", 0.015, 0.04, 0.12, "min20")),
       ("VT sigma60 1,5% [0,04;0,24]", ("vt", "s60", 0.015, 0.04, 0.24)), ("VT sigma60 2,0% [0,04;0,16]", ("vt", "s60", 0.020, 0.04, 0.16)),
       ("VT sigma60 1,0% [0,03;0,10]", ("vt", "s60", 0.010, 0.03, 0.10))]
def path_metrics(a, unit):
    r = a * unit
    eq = np.cumprod(1 + r); peak = np.maximum.accumulate(np.maximum(eq, 1.0)); dd = eq / peak - 1
    # tygodniowe zwroty kapitalu
    wr = np.array([np.prod(1 + r[week_of_day == w]) - 1 for w in wk_ids])
    sharpe = wr.mean() / wr.std(ddof=1) * math.sqrt(52) if wr.std() > 0 else float("nan")
    # kill okna 12/52 tyg. kroczace (krok 5 sesji)
    def rk(nses):
        hits = 0; tot = 0
        for s in range(0, nD - nses + 1, 5):
            e = np.cumprod(1 + r[s:s + nses]); pk = np.maximum.accumulate(np.maximum(e, 1.0))
            hits += bool((e < KILL * pk).any()); tot += 1
        return hits / tot * 100
    # pelna sciezka z kill: po trafieniu plasko
    e = eq.copy(); pk = np.maximum.accumulate(np.maximum(eq, 1.0)); kidx = np.where(eq < KILL * pk)[0]
    end_kill = eq[kidx[0]] if len(kidx) else eq[-1]
    return dict(mean_w=float(wr.mean() * 100), sd_w=float(wr.std(ddof=1) * 100), sharpe=float(sharpe), end=float(eq[-1] * 100), end_kill=float(end_kill * 100),
                maxdd=float(dd.min() * 100), sig_d=float(r.std() * 100), k12=rk(60), k52=rk(260), alloc=float(a.mean()),
                worst_w=float(wr.min() * 100), kill_date=(str(dates[u_days[kidx[0]]].date()) if len(kidx) else "-"))
res["polityki_hist"] = {}
for alpha_nm, unit_sc in (("alfa in-sample (+1,0 p.p. spread/tydz.)", u), ("alfa 0 (wysrodkowane)", u_dm), ("alfa +1 p.p./tydz. (wysrodkowane + 0,01/d)", u_dm + 0.01), ("alfa +0,5 p.p./tydz.", u_dm + 0.005)):
    P(f"### {alpha_nm}")
    P()
    P("| polityka | sr. ALLOC | sigma_d kap. | sr. tyg. | sigma tyg. | Sharpe (52) | najgorszy tydz. | maxDD | kapital konc. bez kill (100=start) | z kill | data kill | okna 12 tyg. z kill | okna 52 tyg. z kill |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    res["polityki_hist"][alpha_nm] = {}
    for nm, pol in POL:
        a = alloc_series(pol); m = path_metrics(a, unit_sc); res["polityki_hist"][alpha_nm][nm] = m
        P(f"| {nm} | {m['alloc']:.3f} | {m['sig_d']:.2f}% | {m['mean_w']:+.2f}% | {m['sd_w']:.2f}% | {m['sharpe']:.2f} | {m['worst_w']:+.1f}% | {m['maxdd']:.1f}% | {m['end']:.0f} | {m['end_kill']:.0f} | {m['kill_date']} | {m['k12']:.1f}% | {m['k52']:.1f}% |")
    P()

# ----------------------------------------------------------------------------- F. bootstrap mieszanki W1-W8 z blokami i sigma20
P("## F. Bootstrap mieszanki koszykow W1-W8 (jak ryzyko_sizing.py §2d) — blok 5/10/20, sigma60 vs sigma20, staly 0,10 vs vol-target")
P()
pool_rows = []; SIG60 = {}; SIG20 = {}
for w in WEEKS:
    k = kosz[w]; i0 = dates.searchsorted(pd.Timestamp(k["d0"]), side="right") - 1
    uu = unit_series(k, i0, 250); pool_rows.append(uu - uu.mean())
    u60 = unit_series(k, i0, 60); SIG60[w] = u60.std(ddof=1); SIG20[w] = u60[-20:].std(ddof=1)
def mixture(npath, nweeks, block):
    """co 'block' sesji losowy koszyk b i blok jego historii; ALLOC ustalany co tydzien wg koszyka tygodnia."""
    nses = nweeks * 5; U = np.empty((npath, nses)); B = np.empty((npath, nweeks), int)
    nblk = math.ceil(nses / block)
    for j in range(nblk):
        b = rng.integers(0, len(WEEKS), size=npath)
        for bi in range(len(WEEKS)):
            m = b == bi; nm = m.sum()
            if nm == 0: continue
            pr = pool_rows[bi]; st = rng.integers(0, len(pr) - block, size=nm)
            seg = pr[st[:, None] + np.arange(block)[None, :]]
            lo = j * block; hi = min(nses, lo + block)
            U[m, lo:hi] = seg[:, :hi - lo]
        for wk in range(j * block // 5, min(nweeks, math.ceil((j + 1) * block / 5))):
            B[:, wk] = b
    return U, B
def alloc_from_B(B, fn): return np.repeat(np.vectorize(fn)(B), 5, axis=1)
def vt_fn(tgt, SIG, lo=0.04, hi=0.12): return lambda bi: float(np.clip(tgt / SIG[WEEKS[bi]], lo, hi))
P("| blok | polityka | sr. ALLOC | P(kill 12t) alfa 0 | P(kill 52t) alfa 0 | DD p95 12t | mediana 12t alfa +1 | srednia 12t alfa +1 | mediana 52t alfa +1 | P(kill 52t) alfa +1 | Sharpe tyg. (52) alfa +1 |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
res["mix"] = {}
for block in (5, 10, 20):
    U12, B12 = mixture(NPATH, 12, block); U52, B52 = mixture(8000, 52, block)
    pols = [("ALLOC 0,24", lambda B: np.full((B.shape[0], B.shape[1] * 5), 0.24)), ("ALLOC 0,12", lambda B: np.full((B.shape[0], B.shape[1] * 5), 0.12)),
            ("ALLOC 0,10", lambda B: np.full((B.shape[0], B.shape[1] * 5), 0.10)), ("ALLOC 0,08", lambda B: np.full((B.shape[0], B.shape[1] * 5), 0.08)),
            ("VT sigma60 1,5% [0,04;0,12]", lambda B: alloc_from_B(B, vt_fn(0.015, SIG60))), ("VT sigma20 1,5% [0,04;0,12]", lambda B: alloc_from_B(B, vt_fn(0.015, SIG20))),
            ("VT sigma60 1,5% [0,04;0,24]", lambda B: alloc_from_B(B, vt_fn(0.015, SIG60, 0.04, 0.24)))]
    for nm, fa in pols:
        a12 = fa(B12); a52 = fa(B52)
        _, dd0, k0, _ = sim(U12, a12); _, _, k0_52, _ = sim(U52, a52)
        eq1, _, _, _ = sim(U12, a12, 0.01); eq1_52, _, k1_52, _ = sim(U52, a52, 0.01)
        # Sharpe tygodniowy przy alfie +1 na 52 tyg (bez kill, z log zwrotow tygodniowych)
        r = a52 * (U52 + 0.01); wk = (1 + r).reshape(r.shape[0], 52, 5).prod(axis=2) - 1
        sh = float((wk.mean(axis=1) / wk.std(axis=1, ddof=1)).mean() * math.sqrt(52))
        row = dict(alloc=float(a12.mean()), k12=float(k0.mean()*100), k52=float(k0_52.mean()*100), dd95=float(np.percentile(dd0, 5)*100), med1=float((np.median(eq1)-1)*100), mean1=float((eq1.mean()-1)*100), med1_52=float((np.median(eq1_52)-1)*100), k1_52=float(k1_52.mean()*100), sharpe1=sh)
        res["mix"][f"{block}_{nm}"] = row
        P(f"| {block} | {nm} | {row['alloc']:.3f} | **{row['k12']:.1f}%** | {row['k52']:.1f}% | {row['dd95']:.1f}% | {row['med1']:+.1f}% | {row['mean1']:+.1f}% | {row['med1_52']:+.1f}% | {row['k1_52']:.1f}% | {row['sharpe1']:.2f} |")
P()
P("sigma60 / sigma20 jednostkowa koszykow na D0: " + "; ".join(f"{w[5:]} {SIG60[w]*100:.1f}/{SIG20[w]*100:.1f}%" for w in WEEKS))

# ----------------------------------------------------------------------------- G. inverse-vol per noga wykonalnosc
P()
P("## G. Inverse-vol per noga przy kroku 0,1 akcji (logika calc_size z app.py: krok otwierany, gdy min_acc <= cel x MAX_OVERSHOOT=1,6)")
P()
last = df.iloc[-1]
P("| kapital odniesienia (USD) | koszyk | cel sigma_d | wagi inv-vol (min / max, % kapitalu) | nogi POMIJANE (0,1 akcji > 1,6 x cel) | nogi jako min. lot (przestrzal >1x) | faktyczny gross po lotach vs zamierzony |")
P("|---|---|---|---|---|---|---|")
res["invvol"] = {}
for capital in (1000, 2500, 5000, 10000):
    for w in ("2026-W7", "2026-W8"):
        k = kosz[w]; i0 = dates.searchsorted(pd.Timestamp(k["d0"]), side="right") - 1
        sl = ret_df.iloc[i0 - 59:i0 + 1][k["long"] + k["short"]].dropna(); C = sl.cov().values; sd = np.sqrt(np.diag(C))
        sgn = np.concatenate([np.ones(5), -np.ones(5)]); winv = 1 / sd; wv = winv * sgn
        scale = 0.015 / math.sqrt(wv @ C @ wv); wagi = winv * scale
        pom = []; minlot = []; gross_real = 0.0
        for t, wg in zip(k["long"] + k["short"], wagi):
            cel = capital * wg; price = last[t] if w == "2026-W8" else df.loc[dates[i0], t]
            step = 0.1; raw = cel / price; dol = math.floor(raw / step) * step; size = dol
            if dol >= step:
                gora = dol + step
                if abs(gora * price - cel) < abs(dol * price - cel) and gora * price <= cel * 1.25: size = gora
            if size < step:
                if step * price <= cel * 1.6: size = step; minlot.append(f"{t} ({step*price/cel:.1f}x)")
                else: pom.append(t); size = 0
            gross_real += size * price / capital
        res["invvol"][f"{capital}_{w}"] = dict(pom=pom, minlot=minlot, gross_real=gross_real, gross_target=float(wagi.sum()))
        P(f"| {capital} | {w[5:]} | 1,5%/d | {wagi.min()*100:.1f}% / {wagi.max()*100:.1f}% | {len(pom)}: {', '.join(pom) if pom else '-'} | {len(minlot)}: {', '.join(minlot) if minlot else '-'} | {gross_real*100:.0f}% vs {wagi.sum()*100:.0f}% |")
P()
P("Kursy z D0 koszyka (W7: 9.10.2026, W8: 16.10.2026). Krok 0,1 akcji = zalozenie z ryzyko_extra.py (Capital.com, akcje USA); app.py bierze krok z minDealSize brokera.")

json.dump(res, open(OUT_JSON, "w"), indent=1, default=float)
open(OUT_MD, "w").write("\n".join(out))
print("zapisano", OUT_MD, OUT_JSON, file=sys.stderr)
