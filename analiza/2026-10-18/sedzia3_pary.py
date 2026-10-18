#!/usr/bin/env python3
"""sedzia3_pary.py — próg miękki WYKONALNY lotami dla E: zamiast ×0,5 na locie zamknięcie 2 z 5 par
(o najwyższej σ60 pary ex ante) przy DD < −10 % od kroczącego szczytu, powrót do 5 par przy DD > −5 %.
Porównanie z ×0,5 i z brakiem progu; E, PIT, 209 okien, dzienny bootstrap blokowy jak sedzia3_harness."""
import sys, json, math, numpy as np, pandas as pd
sys.path.insert(0, '.')
import sedzia3_harness as H
import projektC_bt as C
IND = C.IND
d = H.SER[(H.SER.sklad == 'PIT') & (H.SER.wariant == 'B_cap05')].sort_values('d0')
rng = np.random.default_rng(31019)
weeks, prev, unmatched = [], None, 0
for _, r in d.iterrows():
    labels = r.grupy.split(' | '); L = r.L.split(); S = r.S.split()
    def grp(t):
        ind, sec = IND.get(t, ('', ''))
        return ind if ind in labels else (sec if sec in labels else None)
    pairs = []
    for lab in labels:
        l = [t for t in L if grp(t) == lab]; s = [t for t in S if grp(t) == lab]
        if len(l) == 1 and len(s) == 1: pairs.append((H.col[l[0]], H.col[s[0]]))
    if len(pairs) != 5:
        unmatched += 1
        # awaryjnie: pary wg kolejności alfabetycznej
        pairs = list(zip([H.col[t] for t in L], [H.col[t] for t in S]))
    a, b = H.didx[r.d0], H.didx[r.d5]
    PU = np.array([[H.R[t, l] - H.R[t, s] for (l, s) in pairs] for t in range(a + 1, b + 1)])  # dni × 5 par
    hist = np.array([[H.R[t, l] - H.R[t, s] for (l, s) in pairs] for t in range(a - 59, a + 1)])
    s60p = np.nanstd(hist, axis=0)
    order = np.argsort(-s60p)                      # najwyższa σ pierwsza
    keep3 = np.ones(5, bool); keep3[order[:2]] = False
    Lc = [p[0] for p in pairs]; Sc = [p[1] for p in pairs]
    ch = 10 if prev is None else len(set(Lc) - set(prev[0])) + len(set(Sc) - set(prev[1]))
    weeks.append(dict(u=np.nanmean(PU, axis=1) * 0 + np.nansum(PU, axis=1) / 5, u3=np.nansum(PU[:, keep3], axis=1) / 5, ch=ch, s60=float(r.sigma_unit)))
    prev = (Lc, Sc)
print(f'tygodni {len(weeks)}, niedopasowane pary (fallback alfabetyczny): {unmatched}')
mean_pp = float(np.concatenate([w['u'] for w in weeks]).mean() * 5 * 100)
NP, BLOCK = 3000, 4


def sim(sels, a0, mech, alfa_day, nd):
    npath = len(sels)
    U = np.zeros((npath, nd)); U3 = np.zeros((npath, nd)); CH = np.zeros((npath, nd))
    for p, ws in enumerate(sels):
        k = 0
        for j, w in enumerate(ws):
            n = min(len(w['u']), nd - k)
            U[p, k:k + n] = w['u'][:n] + alfa_day; U3[p, k:k + n] = w['u3'][:n] + alfa_day * 0.6
            CH[p, k] = 10 if j == 0 else w['ch']; k += n
            if k >= nd: break
    eq = np.ones(npath); peak = np.ones(npath); soft = np.zeros(npath, bool); killed = np.zeros(npath, bool)
    prev_soft = np.zeros(npath, bool); ret = np.zeros((npath, nd)); softdays = np.zeros(npath)
    for t in range(nd):
        dd = eq / peak - 1
        if mech:
            soft = np.where(soft, dd <= -0.05, dd < -0.10)
        a = np.where(killed, 0.0, a0)
        if mech == 'half':
            u = U[:, t]; a_eff = np.where(soft, a * 0.5, a); nlegs = 10
            r = 5 * a_eff * u - (CH[:, t] * a_eff * H.COST_LEG + np.abs(soft ^ prev_soft) * 10 * a * 0.5 * H.COST_LEG + H.FIN * 10 * a_eff / 252)
        elif mech == 'pairs':
            u = np.where(soft, U3[:, t], U[:, t]); gross = np.where(soft, 6, 10)
            r = 5 * a * u - (CH[:, t] * a * H.COST_LEG * gross / 10 + np.abs(soft ^ prev_soft) * 4 * a * H.COST_LEG + H.FIN * gross * a / 252)
        else:
            r = 5 * a * U[:, t] - (CH[:, t] * a * H.COST_LEG + H.FIN * 10 * a / 252)
        softdays += soft & ~killed
        ret[:, t] = r; eq = eq * (1 + r); peak = np.maximum(peak, eq)
        killed |= eq / peak < H.KILL; prev_soft = soft.copy()
    return ret, killed, softdays.mean() / nd


def run(a0, mech, alfa, hw):
    n = len(weeks); sels = []
    for _ in range(NP):
        sel = []
        while len(sel) < hw:
            s = rng.integers(0, n - BLOCK); sel.extend(weeks[s:s + BLOCK])
        sels.append(sel[:hw])
    nd = min(sum(len(w['u']) for w in s) for s in sels)
    ret, killed, sf = sim(sels, a0, mech, (alfa - mean_pp) / 100 / 5, nd)
    eq = np.cumprod(1 + ret, axis=1); peak = np.maximum.accumulate(np.hstack([np.ones((NP, 1)), eq]), axis=1)[:, 1:]
    mdd = (eq / peak - 1).min(axis=1); end = eq[:, -1]
    nw = nd // 5; wk = eq[:, 4:nw * 5:5] / np.hstack([np.ones((NP, 1)), eq[:, 4:nw * 5 - 5:5]]) - 1
    return dict(pkill=killed.mean(), end_mean=end.mean(), end_med=np.median(end), p5=np.percentile(end, 5), mdd_p95=np.percentile(mdd, 5),
                mu=wk.mean() * 100, sd=wk.std() * 100, sharpe=wk.mean() / wk.std() * math.sqrt(52), soft=sf)


out = ['| E, ALLOC | mechanizm | alfa | P(kill 12) | P(kill 52) | E[kap.] | med | p5 | maxDD p95 | μ tyg. | σ tyg. | Sharpe | dni z progiem |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
res = {}
for a0 in (0.08, 0.10):
    for mech, lab in ((None, 'bez progu'), ('half', '×0,5 na locie (A/C)'), ('pairs', 'zamknij 2 pary o najwyższej σ (gross ×0,6)')):
        for alfa in (0.0, 0.5, 1.0):
            r12 = run(a0, mech, alfa, 12); r = run(a0, mech, alfa, 52)
            res[f'{a0}|{lab}|{alfa}'] = dict(r, pkill12=r12['pkill'])
            out.append(f'| {a0:.2f} | {lab} | {alfa:+.1f} | {r12["pkill"]*100:.1f}% | {r["pkill"]*100:.1f}% | {r["end_mean"]:.3f} | {r["end_med"]:.3f} | {r["p5"]:.3f} | {r["mdd_p95"]*100:.0f}% | {r["mu"]:+.3f} | {r["sd"]:.2f} | {r["sharpe"]:+.2f} | {r["soft"]*100:.0f}% |')
txt = '\n'.join(out); print(txt)
open('sedzia3_pary_out.md', 'w').write(f'# sedzia3_pary — próg miękki ×0,5 vs zamknięcie 2 par (E, PIT, {len(weeks)} tyg., {NP} ścieżek; niedopasowane tygodnie: {unmatched})\n\n' + txt)
json.dump({k: {kk: float(vv) for kk, vv in v.items()} for k, v in res.items()}, open('sedzia3_pary_wyniki.json', 'w'), indent=1)
