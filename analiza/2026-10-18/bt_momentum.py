#!/usr/bin/env python3
"""
bt_momentum.py — backtest koszyków momentum 5 LONG / 5 SHORT w uniwersum Nasdaq-100
(wspólny harness: okna tygodniowe D0 = ostatnia sesja tygodnia -> D5 = ostatnia sesja
następnego tygodnia; zwrot nogi = zwrot spółki - zwrot ^NDX (long) albo -(...) (short);
spread_pp = średnia 5 long + średnia 5 short).

Warianty:
 (a) 6M (126 sesji) TOP5/BOTTOM5 relatywnie do ^NDX
 (b) 12M-1M (252 sesje, pominięte ostatnie 21)
 (c) 3M (63 sesje)
 (d) 1M (21 sesji)
 (e) 6M z winsoryzacją dziennych zwrotów (cross-sectional 2.5/97.5 pct) i wykluczeniem
     spółek o sigma 20d > 2 x mediany
 (f) 6M z zabezpieczeniem beta: wagi nóg w_i = k / beta_i (beta 250 sesji vs ^NDX,
     przycięta do [0.25, 3]), k tak, że gross = 2 -> każda noga ma równą betę, long beta
     = short beta (beta-neutral). Spread = sum_long w r - sum_short w r (bez odejmowania
     ^NDX, bo strony nie są równe nominalnie; wersja "excess" podana obok).

Baseline: 2000 losowych koszyków 5/5 na każdym oknie (ta sama lista uprawnionych
spółek co w (a)).
Koszty: 0,10% na nogę na rotację (liczone od obrotu nazw: zmieniona noga = 0,10% x 0,2
nominalu strony = 0,02 pp) + finansowanie 6%/rok na gross (= 2 x nominal strony).
Dodatkowo: wrażliwość strategii (a) na ^SOX-^NDX (tygodnie, gdy SOX przegrał z NDX
o > 3 pp) i ekspozycja koszyka na ^SOX-^NDX w czasie (beta nóg z 126 sesji + liczba
półprzewodników w koszyku).
"""
import json
import math
import sys

import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
TV = '/home/user/ndx100-bot/data/tv-screen-2026-W8.json'
HIST = f'{BASE}/analiza/koszyki_historia.json'
OUT_SERIE = f'{BASE}/analiza/bt_momentum_serie.csv'
OUT_MD = f'{BASE}/analiza/bt_momentum.md'

NON_CAND = ['^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV']
COST_LEG = 0.0010      # 0,10% na nogę na rotację
FIN_RATE = 0.06        # 6%/rok na gross
N_RAND = 2000
SEED = 20261018
NL = NS = 5

# ----------------------------------------------------------------------------- dane
df = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
df = df[df['^NDX'].notna()]
df = df.ffill(limit=3)              # pojedyncze luki (święta w jednym źródle)
cands = [c for c in df.columns if c not in NON_CAND]
dates = df.index
P = df[cands].to_numpy(dtype=float)           # ceny spółek
NDX = df['^NDX'].to_numpy(dtype=float)
SOX = df['^SOX'].to_numpy(dtype=float)
VIX = df['^VIX'].to_numpy(dtype=float)
nT, nS = P.shape

R = P[1:] / P[:-1] - 1                        # dzienne zwroty (wiersz t = zwrot z t-1 na t)
R = np.vstack([np.full((1, nS), np.nan), R])
RN = np.concatenate([[np.nan], NDX[1:] / NDX[:-1] - 1])
RSOX = np.concatenate([[np.nan], SOX[1:] / SOX[:-1] - 1])
MA200 = pd.Series(NDX).rolling(200).mean().to_numpy()

# branże
tv = json.load(open(TV))
industry = {r['name']: r['industry'] for r in tv['data']['rows']}
SEMI_IND = {'Semiconductors', 'Electronic Production Equipment'}
SEMI_EXTRA = {'AMAT', 'LRCX', 'KLAC', 'TER', 'ASML', 'SNDK', 'WDC', 'STX', 'LITE', 'ALAB', 'ARM'}
is_semi = {c: (industry.get(c) in SEMI_IND or c in SEMI_EXTRA) for c in cands}

# okna tygodniowe
iso = dates.isocalendar()
keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
last_idx = {}
for i, k in enumerate(keys):
    last_idx[k] = i
weeks = sorted(last_idx)
D0 = np.array([last_idx[w] for w in weeks[:-1]])
D5 = np.array([last_idx[w] for w in weeks[1:]])
nW = len(D0)
WR = P[D5] / P[D0] - 1                        # zwroty tygodniowe spółek
WN = NDX[D5] / NDX[D0] - 1
WSOX = SOX[D5] / SOX[D0] - 1
EX = WR - WN[:, None]                         # excess vs NDX
DAYS = np.array([(dates[b] - dates[a]).days for a, b in zip(D0, D5)])
YEAR = np.array([dates[i].year for i in D0])
VIX0 = VIX[D0]
ABOVE_MA = np.where(np.isnan(MA200[D0]), np.nan, (NDX[D0] > MA200[D0]).astype(float))


# ----------------------------------------------------------------------------- sygnały
def mom_score(L, skip=0):
    """Momentum relatywne: P[d0-skip]/P[d0-L] - 1 - (NDX analogicznie). NaN gdy brak okna."""
    S = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - L < 0:
            continue
        a, b = d0 - L, d0 - skip
        s = P[b] / P[a] - 1 - (NDX[b] / NDX[a] - 1)
        S[w] = s
    return S


def mom_winsor(L=126, q=(2.5, 97.5)):
    """6M z dziennymi zwrotami przyciętymi cross-sectionally (percentyle dnia)."""
    lo = np.nanpercentile(R, q[0], axis=1)
    hi = np.nanpercentile(R, q[1], axis=1)
    RW = np.clip(R, lo[:, None], hi[:, None])
    LRW = np.log1p(RW)
    LRN = np.log1p(RN)
    S = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - L < 0:
            continue
        seg = LRW[d0 - L + 1:d0 + 1]
        s = seg.sum(axis=0) - LRN[d0 - L + 1:d0 + 1].sum()
        s[np.isnan(seg).any(axis=0)] = np.nan
        S[w] = s
    return S


def sigma20():
    S = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - 20 < 0:
            continue
        seg = R[d0 - 19:d0 + 1]
        s = np.nanstd(seg, axis=0, ddof=1)
        s[np.isnan(seg).any(axis=0)] = np.nan
        S[w] = s
    return S


def beta250():
    B = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - 250 < 0:
            continue
        seg = R[d0 - 249:d0 + 1]
        rn = RN[d0 - 249:d0 + 1]
        ok = ~np.isnan(seg).any(axis=0)
        x = rn - rn.mean()
        y = seg[:, ok] - seg[:, ok].mean(axis=0)
        B[w, ok] = (x[:, None] * y).sum(axis=0) / (x ** 2).sum()
    return B


def beta_sox(L=126):
    """Beta (r_i - r_ndx) na (r_sox - r_ndx) z L sesji — ekspozycja nogi na półprzewodniki."""
    B = np.full((nW, nS), np.nan)
    xs = RSOX - RN
    for w, d0 in enumerate(D0):
        if d0 - L < 0:
            continue
        seg = R[d0 - L + 1:d0 + 1] - RN[d0 - L + 1:d0 + 1, None]
        x = xs[d0 - L + 1:d0 + 1]
        ok = ~np.isnan(seg).any(axis=0)
        xc = x - x.mean()
        yc = seg[:, ok] - seg[:, ok].mean(axis=0)
        B[w, ok] = (xc[:, None] * yc).sum(axis=0) / (xc ** 2).sum()
    return B


# ----------------------------------------------------------------------------- selekcja
def select(S, extra_mask=None):
    """Zwraca listy indeksów long/short na każde okno (None gdy brak sygnału)."""
    longs, shorts = [], []
    for w in range(nW):
        s = S[w].copy()
        s[np.isnan(WR[w])] = np.nan                   # musi być cena na D0 i D5
        if extra_mask is not None:
            s[~extra_mask[w]] = np.nan
        ok = np.where(~np.isnan(s))[0]
        if len(ok) < 30:
            longs.append(None); shorts.append(None); continue
        order = ok[np.argsort(-s[ok], kind='stable')]
        longs.append(order[:NL]); shorts.append(order[-NS:])
    return longs, shorts


def select_cap_semi(S, max_semi=2):
    """Jak select, ale na każdej stronie najwyżej max_semi półprzewodników (reszta kolejne w rankingu)."""
    longs, shorts = [], []
    for w in range(nW):
        s = S[w].copy(); s[np.isnan(WR[w])] = np.nan
        ok = np.where(~np.isnan(s))[0]
        if len(ok) < 30:
            longs.append(None); shorts.append(None); continue
        order = ok[np.argsort(-s[ok], kind='stable')]
        def take(seq):
            out, ns = [], 0
            for i in seq:
                if is_semi[cands[i]]:
                    if ns >= max_semi:
                        continue
                    ns += 1
                out.append(i)
                if len(out) == NL:
                    break
            return np.array(out)
        longs.append(take(order)); shorts.append(take(order[::-1]))
    return longs, shorts


IND_ARR = np.array([industry.get(c, 'other') for c in cands])


def industry_neutral(S, min_n=3):
    """Score minus mediana branży (branże z >= min_n uprawnionych nazw), inaczej minus mediana całości."""
    out = np.full_like(S, np.nan)
    for w in range(nW):
        s = S[w].copy(); s[np.isnan(WR[w])] = np.nan
        ok = ~np.isnan(s)
        if ok.sum() < 30:
            continue
        med_all = np.median(s[ok])
        adj = s - med_all
        for ind in set(IND_ARR[ok]):
            m = ok & (IND_ARR == ind)
            if m.sum() >= min_n:
                adj[m] = s[m] - np.median(s[m])
        out[w] = adj
    return out


def run_equal(longs, shorts):
    out = dict(spread=np.full(nW, np.nan), long=np.full(nW, np.nan), short=np.full(nW, np.nan),
               hits=np.zeros(nW), legs=np.zeros(nW), turn=np.zeros(nW))
    prevL = prevS = None
    for w in range(nW):
        if longs[w] is None:
            prevL = prevS = None
            continue
        el = EX[w, longs[w]]; es = -EX[w, shorts[w]]
        out['long'][w] = el.mean() * 100
        out['short'][w] = es.mean() * 100
        out['spread'][w] = out['long'][w] + out['short'][w]
        out['hits'][w] = (el > 0).sum() + (es > 0).sum(); out['legs'][w] = NL + NS
        if prevL is None:
            out['turn'][w] = NL + NS
        else:
            out['turn'][w] = len(set(longs[w]) - set(prevL)) + len(set(shorts[w]) - set(prevS))
        prevL, prevS = longs[w], shorts[w]
    return out


def run_beta(longs, shorts, B):
    out = dict(spread=np.full(nW, np.nan), long=np.full(nW, np.nan), short=np.full(nW, np.nan),
               hits=np.zeros(nW), legs=np.zeros(nW), turn=np.zeros(nW),
               spread_excess=np.full(nW, np.nan), wl=np.full(nW, np.nan), ws=np.full(nW, np.nan),
               beta_l=np.full(nW, np.nan), beta_s=np.full(nW, np.nan))
    prevL = prevS = None
    for w in range(nW):
        if longs[w] is None:
            prevL = prevS = None
            continue
        bl = np.clip(B[w, longs[w]], 0.25, 3.0); bs = np.clip(B[w, shorts[w]], 0.25, 3.0)
        if np.isnan(bl).any() or np.isnan(bs).any():
            out['spread'][w] = np.nan; prevL = prevS = None; continue
        inv = np.concatenate([1 / bl, 1 / bs])
        k = 2.0 / inv.sum()
        wl = k / bl; ws = k / bs
        rl = WR[w, longs[w]]; rs = WR[w, shorts[w]]
        out['long'][w] = (wl * (rl - WN[w])).sum() * 100
        out['short'][w] = -(ws * (rs - WN[w])).sum() * 100
        out['spread_excess'][w] = out['long'][w] + out['short'][w]
        out['spread'][w] = ((wl * rl).sum() - (ws * rs).sum()) * 100       # beta-neutral, bez NDX
        out['wl'][w] = wl.sum(); out['ws'][w] = ws.sum()
        out['beta_l'][w] = (wl * bl).sum(); out['beta_s'][w] = (ws * bs).sum()
        out['hits'][w] = ((rl - WN[w]) > 0).sum() + ((rs - WN[w]) < 0).sum(); out['legs'][w] = NL + NS
        if prevL is None:
            out['turn'][w] = NL + NS
        else:
            out['turn'][w] = len(set(longs[w]) - set(prevL)) + len(set(shorts[w]) - set(prevS))
        prevL, prevS = longs[w], shorts[w]
    return out


def costs(out):
    rot = out['turn'] * COST_LEG * (1.0 / NL) * 100           # pp (noga = 0,2 nominału strony)
    fin = FIN_RATE * 2.0 * DAYS / 365 * 100
    return rot, fin


# ----------------------------------------------------------------------------- metryki
def metrics(sp, mask=None, hits=None, legs=None):
    m = ~np.isnan(sp)
    if mask is not None:
        m &= mask
    x = sp[m]
    n = len(x)
    if n < 2:
        return dict(n=n, mean=np.nan, median=np.nan, sigma=np.nan, t=np.nan, sharpe=np.nan,
                    hit=np.nan, hit_legs=np.nan, maxdd=np.nan, worst=np.nan, best=np.nan)
    mu, sd = x.mean(), x.std(ddof=1)
    cum = np.cumsum(x); dd = (np.maximum.accumulate(cum) - cum).max()
    hl = np.nan
    if hits is not None:
        hl = hits[m].sum() / legs[m].sum()
    return dict(n=n, mean=mu, median=np.median(x), sigma=sd, t=mu / sd * math.sqrt(n),
                sharpe=mu / sd * math.sqrt(52), hit=(x > 0).mean(), hit_legs=hl,
                maxdd=dd, worst=x.min(), best=x.max())


def fmt(v, d=2):
    return '—' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.{d}f}'


def row_metrics(name, m, extra=''):
    return (f"| {name} | {m['n']} | {fmt(m['mean'])} | {fmt(m['median'])} | {fmt(m['sigma'])} | "
            f"{fmt(m['t'])} | {fmt(m['sharpe'])} | {fmt(m['hit'] * 100 if m['hit'] == m['hit'] else np.nan, 0)}% | "
            f"{fmt(m['hit_legs'] * 100 if m['hit_legs'] == m['hit_legs'] else np.nan, 0)}% | "
            f"{fmt(m['maxdd'], 1)} | {fmt(m['worst'], 1)} | {fmt(m['best'], 1)} |{extra}")


HDR = ('| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |\n'
       '|---|---|---|---|---|---|---|---|---|---|---|---|')


def breakdown(sp, hits, legs, mask_base):
    """Rozbicie na lata i reżimy; zwraca wiersze markdown."""
    rows = []
    for y in sorted(set(YEAR)):
        m = metrics(sp, mask_base & (YEAR == y), hits, legs)
        if m['n'] >= 2:
            rows.append(row_metrics(str(y), m))
    for lbl, msk in [('VIX>20 na D0', VIX0 > 20), ('VIX≤20 na D0', VIX0 <= 20),
                     ('NDX < MA200', ABOVE_MA == 0), ('NDX > MA200', ABOVE_MA == 1)]:
        m = metrics(sp, mask_base & msk, hits, legs)
        rows.append(row_metrics(lbl, m))
    return rows


# ----------------------------------------------------------------------------- uruchomienie
S6 = mom_score(126)
S12_1 = mom_score(252, skip=21)
S3 = mom_score(63)
S1 = mom_score(21)
S6W = mom_winsor(126)
SIG20 = sigma20()
BETA = beta250()
BSOX = beta_sox(126)

# maska (e): sigma20 <= 2 x mediana wśród spółek z sygnałem
mask_e = np.zeros((nW, nS), dtype=bool)
for w in range(nW):
    s = S6W[w]; sg = SIG20[w]
    ok = ~np.isnan(s) & ~np.isnan(sg)
    if ok.sum() == 0:
        continue
    med = np.median(sg[ok])
    mask_e[w] = ok & (sg <= 2 * med)

variants = {}
La, Sa = select(S6); variants['a_6M'] = (La, Sa, run_equal(La, Sa))
Lb, Sb = select(S12_1); variants['b_12M-1M'] = (Lb, Sb, run_equal(Lb, Sb))
Lc, Sc = select(S3); variants['c_3M'] = (Lc, Sc, run_equal(Lc, Sc))
Ld, Sd = select(S1); variants['d_1M'] = (Ld, Sd, run_equal(Ld, Sd))
Le, Se = select(S6W, mask_e); variants['e_6M_winsor_sigma'] = (Le, Se, run_equal(Le, Se))
# (f): te same nazwy co (a), ale wymagamy bety 250 sesji dla wszystkich nóg
mask_f = ~np.isnan(BETA)
Lf, Sf = select(S6, mask_f); variants['f_6M_beta_neutral'] = (Lf, Sf, run_beta(Lf, Sf, BETA))
# diagnostyka półprzewodników: limit 2 semis/strona i ranking neutralny branżowo
Lg, Sg = select_cap_semi(S6, 2); variants['g_6M_max2semi'] = (Lg, Sg, run_equal(Lg, Sg))
Lh, Sh = select(industry_neutral(S6)); variants['h_6M_industry_neutral'] = (Lh, Sh, run_equal(Lh, Sh))
# kontrola: odwrócone momentum 1M (kontrarian) — czy 1M to odwrócenie?
Ld_r, Sd_r = select(-S1); variants['d_rev_1M_contrarian'] = (Ld_r, Sd_r, run_equal(Ld_r, Sd_r))
Lb_r, Sb_r = select(-S6); variants['a_rev_6M_contrarian'] = (Lb_r, Sb_r, run_equal(Lb_r, Sb_r))

# wspólny zbiór okien: wszystkie warianty mają sygnał (d0 >= 273 sesje)
common = np.ones(nW, dtype=bool)
for k, (L_, S_, o) in variants.items():
    common &= ~np.isnan(o['spread'])
first_common = int(np.argmax(common))

# ----------------------------------------------------------------------------- baseline
rng = np.random.default_rng(SEED)
RAND = np.full((nW, N_RAND), np.nan)
RAND_LEGHIT = np.full((nW, N_RAND), np.nan)
elig_a = ~np.isnan(S6) & ~np.isnan(WR)
for w in range(nW):
    idx = np.where(elig_a[w])[0]
    if len(idx) < 30:
        continue
    pick = np.array([rng.choice(idx, NL + NS, replace=False) for _ in range(N_RAND)])
    el = EX[w][pick[:, :NL]]; es = -EX[w][pick[:, NL:]]
    RAND[w] = (el.mean(axis=1) + es.mean(axis=1)) * 100
    RAND_LEGHIT[w] = ((el > 0).sum(axis=1) + (es > 0).sum(axis=1)) / (NL + NS)


def baseline_stats(mask):
    X = RAND[mask]
    pooled = X.ravel()
    means = X.mean(axis=0); sds = X.std(axis=0, ddof=1); n = X.shape[0]
    ts = means / sds * math.sqrt(n)
    return dict(n=n, sigma_pooled=pooled.std(ddof=1), p5=np.percentile(pooled, 5),
                p95=np.percentile(pooled, 95), mean_of_means=means.mean(),
                mean_p5=np.percentile(means, 5), mean_p95=np.percentile(means, 95),
                t_p5=np.percentile(ts, 5), t_p95=np.percentile(ts, 95), t_p975=np.percentile(ts, 97.5),
                sigma_of_strat_p5=np.percentile(sds, 5), sigma_of_strat_p95=np.percentile(sds, 95),
                sharpe_p95=np.percentile(means / sds * math.sqrt(52), 95),
                leghit=np.nanmean(RAND_LEGHIT[mask]), means=means, ts=ts)


# ----------------------------------------------------------------------------- SOX / półprzewodniki (wariant a)
oa = variants['a_6M'][2]
sox_rel = WSOX - WN                                     # tygodniowy SOX - NDX
semi_long = np.array([np.nan if La[w] is None else sum(is_semi[cands[i]] for i in La[w]) for w in range(nW)])
semi_short = np.array([np.nan if Sa[w] is None else sum(is_semi[cands[i]] for i in Sa[w]) for w in range(nW)])
expo_sox = np.array([np.nan if La[w] is None else
                     np.nanmean(BSOX[w, La[w]]) - np.nanmean(BSOX[w, Sa[w]]) for w in range(nW)])


def ols(y, x):
    m = ~np.isnan(y) & ~np.isnan(x)
    y, x = y[m], x[m]
    xc = x - x.mean(); yc = y - y.mean()
    b = (xc * yc).sum() / (xc ** 2).sum(); a = y.mean() - b * x.mean()
    r = np.corrcoef(x, y)[0, 1]
    resid = y - a - b * x
    return a, b, r, resid.std(ddof=2), m.sum()


# ----------------------------------------------------------------------------- faktyczne koszyki W4–W8
hist = json.load(open(HIST))
actual_rows = []
cidx = {c: i for i, c in enumerate(cands)}
def mom_at(pos, L=126):
    if pos - L < 0:
        return np.full(nS, np.nan)
    return P[pos] / P[pos - L] - 1 - (NDX[pos] / NDX[pos - L] - 1)


for wk, k in hist['koszyki'].items():
    d0 = pd.Timestamp(k['d0']['date'])
    pos = int(dates.searchsorted(d0, side='right') - 1)          # ostatnia sesja <= d0
    s = mom_at(pos); s[np.isnan(P[pos])] = np.nan
    ok = ~np.isnan(s)
    ranks = pd.Series(s[ok], index=np.array(cands)[ok]).rank(pct=True)
    order = np.where(ok)[0][np.argsort(-s[ok], kind='stable')]
    pick_l = set(cands[i] for i in order[:NL]); pick_s = set(cands[i] for i in order[-NS:])
    pl = [f"{t}({ranks.get(t, np.nan) * 100:.0f})" for t in k['long']]
    ps = [f"{t}({ranks.get(t, np.nan) * 100:.0f})" for t in k['short']]
    ovl = len(pick_l & set(k['long'])); ovs = len(pick_s & set(k['short']))
    ws_ = np.where(D0 == pos)[0]
    if len(ws_):
        w = int(ws_[0])
        li = [cidx[t] for t in k['long'] if t in cidx]; si = [cidx[t] for t in k['short'] if t in cidx]
        act = (EX[w, li].mean() - EX[w, si].mean()) * 100 if li and si else np.nan
        hd0, hd5, spa, sx = str(dates[D0[w]].date()), str(dates[D5[w]].date()), oa['spread'][w], sox_rel[w] * 100
    else:
        hd0, hd5, spa, sx, act = str(dates[pos].date()), '(brak okna)', np.nan, np.nan, np.nan
    nsem_l = sum(is_semi.get(t, False) for t in k['long'])
    actual_rows.append(dict(week=wk, d0=k['d0']['date'], harness_d0=hd0, harness_d5=hd5, long=' '.join(pl), short=' '.join(ps),
                            overlap_long=ovl, overlap_short=ovs, semis_long=nsem_l,
                            spread_a=spa, spread_actual_harness=act, sox_rel=sx,
                            mom_long=' '.join(sorted(pick_l)), mom_short=' '.join(sorted(pick_s))))

# ----------------------------------------------------------------------------- CSV serii
rows = []
for name, (L_, S_, o) in variants.items():
    for w in range(nW):
        if np.isnan(o['spread'][w]):
            continue
        rot, fin = costs(o)
        rows.append(dict(variant=name, date_d0=str(dates[D0[w]].date()), date_d5=str(dates[D5[w]].date()),
                         spread_pp=round(o['spread'][w], 4), long_pp=round(o['long'][w], 4),
                         short_pp=round(o['short'][w], 4), legs_hit=int(o['hits'][w]), turnover_legs=int(o['turn'][w]),
                         cost_rot_pp=round(rot[w], 4), cost_fin_pp=round(fin[w], 4),
                         net_pp=round(o['spread'][w] - rot[w] - fin[w], 4),
                         ndx_pct=round(WN[w] * 100, 3), sox_minus_ndx_pct=round(sox_rel[w] * 100, 3),
                         vix_d0=round(VIX0[w], 2), ndx_above_ma200=ABOVE_MA[w],
                         common=bool(common[w]),
                         long=' '.join(cands[i] for i in L_[w]), short=' '.join(cands[i] for i in S_[w]),
                         semis_long=(int(semi_long[w]) if name == 'a_6M' and not np.isnan(semi_long[w]) else ''),
                         semis_short=(int(semi_short[w]) if name == 'a_6M' and not np.isnan(semi_short[w]) else ''),
                         expo_sox_beta=(round(expo_sox[w], 3) if name == 'a_6M' and not np.isnan(expo_sox[w]) else ''),
                         rand_p5=round(np.nanpercentile(RAND[w], 5), 3) if not np.isnan(RAND[w]).all() else '',
                         rand_p95=round(np.nanpercentile(RAND[w], 95), 3) if not np.isnan(RAND[w]).all() else ''))
pd.DataFrame(rows).to_csv(OUT_SERIE, index=False)

# ----------------------------------------------------------------------------- raport
md = []
md.append('# Backtest koszyków momentum 5L/5S w uniwersum Nasdaq-100 (agent: momentum)\n')
md.append(f'Dane: `{CSV}` — {nT} sesji {dates[0].date()}…{dates[-1].date()}, {nS} kandydatów '
          f'(skład dzisiejszy → survivorship bias). Okna tygodniowe: {nW}. '
          f'Wspólny zbiór okien (wszystkie warianty mają sygnał, od D0 = {dates[D0[first_common]].date()}): '
          f'{common.sum()} okien.\n')
md.append('Harness: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; noga long = r_spółki − r_NDX, '
          'short = −(r_spółki − r_NDX); spread_pp = średnia 5 long + średnia 5 short (= P&L w % nominału jednej strony, gross = 2). '
          'Sygnały wyłącznie z cen ≤ D0. Spółki bez pełnego okna sygnału wykluczone (ALAB, ARM, CRWV, GEHC, HONA, NBIS, SNDK, SPCX, WBD, CEG do czasu uzupełnienia historii).\n')
md.append('Koszty: rotacja 0,10% × nominał nogi (0,2 strony) za każdą ZMIENIONĄ nazwę (obrót liczony z serii), '
          'finansowanie 6%/rok × gross 2 × dni/365. Pełna rotacja 10 nóg = 0,20 pp/tydz.; finansowanie ≈ 0,23 pp/tydz.\n')

# tabela główna — wspólne okna
md.append('\n## 1. Wyniki na wspólnym zbiorze okien (brutto)\n')
md.append(HDR)
summary = {}
for name, (L_, S_, o) in variants.items():
    m = metrics(o['spread'], common, o['hits'], o['legs'])
    rot, fin = costs(o)
    net = o['spread'] - rot - fin
    mn = metrics(net, common)
    summary[name] = dict(m=m, mn=mn, rot=np.nanmean(rot[common]), fin=np.nanmean(fin[common]),
                         turn=np.nanmean(o['turn'][common]))
    md.append(row_metrics(name, m))
bs = baseline_stats(common)
md.append(f"| BASELINE losowe 5/5 (2000 koszyków/okno) | {bs['n']} | {fmt(bs['mean_of_means'])} | — | "
          f"{fmt(bs['sigma_pooled'])} (pooled) | 5–95% t: {fmt(bs['t_p5'])}…{fmt(bs['t_p95'])} | 95% Sharpe: {fmt(bs['sharpe_p95'])} | — | "
          f"{fmt(bs['leghit'] * 100, 0)}% | — | p5 {fmt(bs['p5'], 1)} | p95 {fmt(bs['p95'], 1)} |")
md.append('\nBaseline: σ pojedynczego tygodnia losowego koszyka 5/5 (pooled) = **%.2f pp**, przedział 5–95%% tygodniowego spreadu '
          '= **%.1f … %.1f pp**; rozkład średniej 2000 losowych STRATEGII (losowy koszyk w każdym oknie): 5–95%% = %.2f … %.2f pp/tydz., '
          't-stat 5–95%% = %.2f … %.2f (97,5%% = %.2f); σ tygodniowa losowej strategii 5–95%% = %.2f … %.2f pp.\n'
          % (bs['sigma_pooled'], bs['p5'], bs['p95'], bs['mean_p5'], bs['mean_p95'], bs['t_p5'], bs['t_p95'], bs['t_p975'],
             bs['sigma_of_strat_p5'], bs['sigma_of_strat_p95']))

md.append('\n## 2. Po kosztach (wspólne okna)\n')
md.append('| wariant | obrót nóg/tydz. | koszt rotacji pp/tydz. | finansowanie pp/tydz. | brutto pp | netto pp | t netto | Sharpe netto | hit netto | pct wśród losowych (brutto) |\n|---|---|---|---|---|---|---|---|---|---|')
for name, s in summary.items():
    pct = (bs['means'] < s['m']['mean']).mean() * 100
    md.append(f"| {name} | {fmt(s['turn'], 1)} | {fmt(s['rot'])} | {fmt(s['fin'])} | {fmt(s['m']['mean'])} | "
              f"{fmt(s['mn']['mean'])} | {fmt(s['mn']['t'])} | {fmt(s['mn']['sharpe'])} | {fmt(s['mn']['hit'] * 100, 0)}% | {pct:.1f}% |")

# pełne dostępne okna per wariant
md.append('\n## 3. Każdy wariant na wszystkich swoich oknach (brutto; różne okresy — nieporównywalne wprost)\n')
md.append(HDR)
for name, (L_, S_, o) in variants.items():
    m = metrics(o['spread'], None, o['hits'], o['legs'])
    first = int(np.argmax(~np.isnan(o['spread'])))
    md.append(row_metrics(name, m, f' od {dates[D0[first]].date()}'))
allmask = ~np.isnan(oa['spread'])
bsa = baseline_stats(allmask)
md.append(f"| BASELINE (okna wariantu a) | {bsa['n']} | {fmt(bsa['mean_of_means'])} | — | {fmt(bsa['sigma_pooled'])} | "
          f"t 5–95%: {fmt(bsa['t_p5'])}…{fmt(bsa['t_p95'])} | — | — | {fmt(bsa['leghit'] * 100, 0)}% | — | p5 {fmt(bsa['p5'], 1)} | p95 {fmt(bsa['p95'], 1)} |")

# rozbicia
md.append('\n## 4. Rozbicie na lata i reżimy (brutto; lata wg D0; wariant na swoich wszystkich oknach)\n')
for name, (L_, S_, o) in variants.items():
    if name.endswith('contrarian'):
        continue
    md.append(f'\n### {name}\n')
    md.append(HDR)
    for r in breakdown(o['spread'], o['hits'], o['legs'], ~np.isnan(o['spread'])):
        md.append(r)
# baseline per reżim (średnia losowych w reżimie)
md.append('\n### BASELINE w reżimach (średnia losowego koszyka, σ pooled) — dla porównania z tabelami wyżej\n')
md.append('| reżim | okna | średnia losowych pp | σ pooled | p5 | p95 |\n|---|---|---|---|---|---|')
for lbl, msk in [('wszystkie (okna a)', allmask)] + [(str(y), allmask & (YEAR == y)) for y in sorted(set(YEAR))] + \
        [('VIX>20', allmask & (VIX0 > 20)), ('VIX≤20', allmask & (VIX0 <= 20)),
         ('NDX<MA200', allmask & (ABOVE_MA == 0)), ('NDX>MA200', allmask & (ABOVE_MA == 1))]:
    if msk.sum() < 2:
        continue
    b = baseline_stats(msk)
    md.append(f"| {lbl} | {b['n']} | {fmt(b['mean_of_means'])} | {fmt(b['sigma_pooled'])} | {fmt(b['p5'], 1)} | {fmt(b['p95'], 1)} |")

# (f) szczegóły
of = variants['f_6M_beta_neutral'][2]
mf = ~np.isnan(of['spread'])
md.append('\n## 5. Wariant (f) — szczegóły konstrukcji beta-neutral\n')
md.append(f"Średni nominał strony long = {np.nanmean(of['wl'][mf]):.2f}, short = {np.nanmean(of['ws'][mf]):.2f} (gross 2). "
          f"Średnia beta strony long = short = {np.nanmean(of['beta_l'][mf]):.2f}. "
          f"Spread 'excess vs NDX' (harness literalnie, czyli z dodatkowym shortem NDX o nominał long−short): "
          f"średnia {np.nanmean(of['spread_excess'][common]):.2f} pp, t = {metrics(of['spread_excess'], common)['t']:.2f}; "
          f"spread beta-neutral (bez NDX): średnia {np.nanmean(of['spread'][common]):.2f} pp, t = {metrics(of['spread'], common)['t']:.2f}.\n")
# beta koszyka (a) do NDX
ba_l = np.array([np.nan if La[w] is None else np.nanmean(BETA[w, La[w]]) for w in range(nW)])
ba_s = np.array([np.nan if Sa[w] is None else np.nanmean(BETA[w, Sa[w]]) for w in range(nW)])
md.append(f"Dla porównania koszyk (a) równych wag: średnia beta 250d strony long = {np.nanmean(ba_l):.2f}, short = {np.nanmean(ba_s):.2f} "
          f"→ koszyk (a) ma strukturalnie dodatnią betę netto ≈ {np.nanmean(ba_l - ba_s):.2f} (long wysokiej bety, short niskiej).\n")
# regresja spreadu (a) na NDX tygodniowo
a_, b_, r_, se_, n_ = ols(oa['spread'], WN * 100)
md.append(f"Regresja spreadu (a) na tygodniowym zwrocie ^NDX: alfa = {a_:.2f} pp/tydz., beta = {b_:.2f}, r = {r_:.2f} (n={n_}). "
          f"Czyli {r_**2*100:.0f}% wariancji spreadu (a) to kierunek rynku.\n")

# SOX
md.append('\n## 6. Strategia (a) a półprzewodniki (^SOX − ^NDX)\n')
m_bad = sox_rel < -0.03
m_good = sox_rel > 0.03
m_mid = ~m_bad & ~m_good
md.append('| podzbiór tygodni | okna | średni spread (a) pp | σ | t | hit | najgorsze | średni SOX−NDX pp |\n|---|---|---|---|---|---|---|---|')
for lbl, msk in [('SOX−NDX < −3 pp (jak W6/W7)', m_bad), ('|SOX−NDX| ≤ 3 pp', m_mid), ('SOX−NDX > +3 pp', m_good), ('wszystkie', np.ones(nW, bool))]:
    m = metrics(oa['spread'], msk & allmask)
    md.append(f"| {lbl} | {m['n']} | {fmt(m['mean'])} | {fmt(m['sigma'])} | {fmt(m['t'])} | {fmt(m['hit'] * 100 if m['n'] > 1 else np.nan, 0)}% | "
              f"{fmt(m['worst'], 1)} | {fmt(np.nanmean(sox_rel[msk & allmask]) * 100, 1)} |")
md.append('\nTo samo dla wariantów bez zakładu na półprzewodniki (g: max 2 semis/strona, h: ranking neutralny branżowo), wspólne okna:\n')
md.append('| wariant | SOX−NDX < −3: n / średnia / hit | pozostałe: n / średnia | wszystkie wspólne: średnia / t / σ | beta na SOX−NDX | r |\n|---|---|---|---|---|---|')
for nm in ['a_6M', 'g_6M_max2semi', 'h_6M_industry_neutral', 'e_6M_winsor_sigma', 'f_6M_beta_neutral']:
    o_ = variants[nm][2]
    mb = metrics(o_['spread'], common & m_bad); mo = metrics(o_['spread'], common & ~m_bad); ma = metrics(o_['spread'], common)
    _, bb, rr, _, _ = ols(np.where(common, o_['spread'], np.nan), sox_rel * 100)
    md.append(f"| {nm} | {mb['n']} / {fmt(mb['mean'])} / {fmt(mb['hit'] * 100, 0)}% | {mo['n']} / {fmt(mo['mean'])} | {fmt(ma['mean'])} / {fmt(ma['t'])} / {fmt(ma['sigma'])} | {bb:.2f} | {rr:.2f} |")
a_, b_, r_, se_, n_ = ols(oa['spread'], sox_rel * 100)
md.append(f"\nRegresja tygodniowego spreadu (a) na (SOX−NDX): alfa = {a_:.2f} pp, **beta = {b_:.2f}**, r = {r_:.2f}, R² = {r_**2:.2f} (n={n_}). "
          f"Co 1 pp przegranej SOX z NDX kosztuje koszyk ≈ {b_:.2f} pp.\n")
# ekspozycja w czasie
md.append('\n### Ekspozycja koszyka (a) na SOX−NDX w czasie (beta nóg z 126 sesji; long − short) i liczba półprzewodników\n')
md.append('| okres | okna | śr. ekspozycja beta(SOX−NDX) | min | max | śr. liczba semis LONG | śr. semis SHORT | % tygodni z ≥3 semis w long | % tygodni ekspozycja>0,5 |\n|---|---|---|---|---|---|---|---|---|')
for lbl, msk in [(str(y), allmask & (YEAR == y)) for y in sorted(set(YEAR))] + [('wszystkie', allmask)]:
    if msk.sum() < 2:
        continue
    e = expo_sox[msk]
    md.append(f"| {lbl} | {msk.sum()} | {np.nanmean(e):.2f} | {np.nanmin(e):.2f} | {np.nanmax(e):.2f} | {np.nanmean(semi_long[msk]):.1f} | "
              f"{np.nanmean(semi_short[msk]):.1f} | {(semi_long[msk] >= 3).mean() * 100:.0f}% | {(e > 0.5).mean() * 100:.0f}% |")
# ekspozycja w ostatnich 26 tygodniach
rec = np.where(allmask)[0][-26:]
md.append('\nOstatnie 26 okien (D0, ekspozycja beta SOX−NDX, semis long/short, spread a, SOX−NDX):\n')
md.append('| D0 | ekspozycja | semis L/S | spread (a) pp | SOX−NDX pp | skład long (a) |\n|---|---|---|---|---|---|')
for w in rec:
    md.append(f"| {dates[D0[w]].date()} | {expo_sox[w]:.2f} | {int(semi_long[w])}/{int(semi_short[w])} | {oa['spread'][w]:.1f} | "
              f"{sox_rel[w] * 100:.1f} | {' '.join(cands[i] for i in La[w])} |")
# warunkowa: ekspozycja wysoka vs niska
hi = expo_sox > np.nanmedian(expo_sox)
m_hi = metrics(oa['spread'], allmask & hi); m_lo = metrics(oa['spread'], allmask & ~hi)
md.append(f"\nSpread (a) gdy ekspozycja SOX powyżej mediany ({np.nanmedian(expo_sox):.2f}): średnia {m_hi['mean']:.2f} pp, σ {m_hi['sigma']:.2f}, t {m_hi['t']:.2f} (n={m_hi['n']}); "
          f"poniżej mediany: średnia {m_lo['mean']:.2f} pp, σ {m_lo['sigma']:.2f}, t {m_lo['t']:.2f} (n={m_lo['n']}).\n")
# korelacja spreadu z SOX-NDX w podokresach
md.append('\nKorelacja spreadu (a) z (SOX−NDX) wg lat: ' + ', '.join(
    f"{y}: r={ols(oa['spread'][allmask & (YEAR == y)], sox_rel[allmask & (YEAR == y)] * 100)[2]:.2f}" for y in sorted(set(YEAR)) if (allmask & (YEAR == y)).sum() > 5) + '\n')

# faktyczne koszyki
md.append('\n## 7. Faktyczne koszyki W4–W8 a momentum 6M\n')
md.append('Percentyl momentum 6M relatywnego (100 = najsilniejsza spółka) przy D0 koszyka; overlap = ile nazw pokrywa się z TOP5/BOTTOM5 (a).\n')
md.append('| tydzień | D0 koszyka | okno harnessu | long (pct mom) | short (pct mom) | overlap L/S | semis w long | spread (a) w oknie | spread faktyczny w oknie | SOX−NDX pp | TOP5 (a) | BOTTOM5 (a) |\n|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in actual_rows:
    md.append(f"| {r['week']} | {r['d0']} | {r['harness_d0']}→{r['harness_d5']} | {r['long']} | {r['short']} | {r['overlap_long']}/{r['overlap_short']} | "
              f"{r['semis_long']} | {fmt(r['spread_a'], 1)} | {fmt(r['spread_actual_harness'], 1)} | {fmt(r['sox_rel'], 1)} | {r['mom_long']} | {r['mom_short']} |")
md.append('\nHistory (zapisane w signals): ' + ', '.join(f"{h['week']}: {h['spread_pp']} pp" for h in hist['history']) + '\n')

md.append('\n## 7b. Stabilność: pierwsza vs druga połowa wspólnych okien (brutto)\n')
ci = np.where(common)[0]; half = ci[len(ci) // 2]
md.append('| wariant | 1. połowa: n / średnia / t | 2. połowa: n / średnia / t |\n|---|---|---|')
for name, (L_, S_, o) in variants.items():
    if name.endswith('contrarian'):
        continue
    m1 = metrics(o['spread'], common & (np.arange(nW) < half)); m2 = metrics(o['spread'], common & (np.arange(nW) >= half))
    md.append(f"| {name} | {m1['n']} / {fmt(m1['mean'])} / {fmt(m1['t'])} | {m2['n']} / {fmt(m2['mean'])} / {fmt(m2['t'])} |")

# wnioski — generowane z liczb
md.append('\n## 8. Wnioski (automatyczne z liczb — interpretacja w odpowiedzi agenta)\n')
best = max((k for k in summary if not k.endswith('contrarian')), key=lambda k: summary[k]['mn']['t'])
for name, s in summary.items():
    flag = []
    if s['m']['t'] > 2: flag.append('t>2 brutto')
    if s['mn']['t'] > 2: flag.append('t>2 netto')
    if s['m']['mean'] > bs['mean_p95']: flag.append('średnia > p95 losowych')
    if s['m']['sigma'] > bs['sigma_of_strat_p95']: flag.append('σ > p95 losowych strategii (koncentracja ryzyka)')
    md.append(f"- {name}: brutto {s['m']['mean']:.2f} pp/tydz. (t {s['m']['t']:.2f}), netto {s['mn']['mean']:.2f} pp (t {s['mn']['t']:.2f}); "
              + ('; '.join(flag) if flag else 'nie odróżnia się od szumu') + '.')
md.append(f"- Najlepszy t netto wśród wariantów a–f: {best} (t = {summary[best]['mn']['t']:.2f}).")

open(OUT_MD, 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))

# JSON do odpowiedzi
res = dict(baseline=dict(sigma_pp=round(bs['sigma_pooled'], 3), p5_pp=round(bs['p5'], 3), p95_pp=round(bs['p95'], 3),
                         mean_p5=round(bs['mean_p5'], 3), mean_p95=round(bs['mean_p95'], 3), t_p95=round(bs['t_p95'], 3)),
           variants={k: dict(n=int(s['m']['n']), mean=round(s['m']['mean'], 3), sigma=round(s['m']['sigma'], 3), t=round(s['m']['t'], 3),
                             sharpe=round(s['m']['sharpe'], 3), hit=round(s['m']['hit'], 3), hit_legs=round(s['m']['hit_legs'], 3),
                             maxdd=round(s['m']['maxdd'], 2), worst=round(s['m']['worst'], 2), best=round(s['m']['best'], 2),
                             net_mean=round(s['mn']['mean'], 3), net_t=round(s['mn']['t'], 3)) for k, s in summary.items()})
json.dump(res, open(f'{BASE}/analiza/bt_momentum_summary.json', 'w'), indent=1)
