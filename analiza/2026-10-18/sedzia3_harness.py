#!/usr/bin/env python3
"""
sedzia3_harness.py — wspólny DZIENNY harness dla polityk trzech projektów (A: vt+soft na konstrukcji A;
B: stałe 0,06 + schodek FLAT −12 % od szczytu cyklu; C: E=B_cap05 stałe 0,08 + próg miękki), te same
209 okien PIT 2022-10…2026-10 (nogi z projektC_bt_serie.csv), bootstrap blokowy 4 tyg., 3000 ścieżek,
alfa 0 / +0,5 / +1,0 p.p./tydz. (dodana do wyśrodkowanej serii dziennej), koszty jak projektA_bt.simulate
(0,10 % na zmienioną nogę i zmianę skali, 6 %/rok × gross). Kill = kapitał < 0,75 × kroczący szczyt, potem płasko.
Wyjście: sedzia3_harness_out.md, sedzia3_harness_wyniki.json. Bez liczb z rachunku.
"""
import json, sys, math
import numpy as np, pandas as pd
sys.path.insert(0, '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza')
import projektA_bt as B

BASE = B.BASE + '/analiza'
SER = pd.read_csv(f'{BASE}/projektC_bt_serie.csv')
NPATH, BLOCK = 3000, 4
rng = np.random.default_rng(31018)
COST_LEG, FIN = B.COST_LEG, B.FIN_RATE
KILL = 0.75

P, names, _, _ = B.build(True)
R = P[1:] / P[:-1] - 1
R = np.vstack([np.full((1, P.shape[1]), np.nan), R])
col = {n: i for i, n in enumerate(names)}
didx = {str(d.date()): i for i, d in enumerate(B.dates)}


def weeks_for(variant):
    df = SER[(SER.sklad == 'PIT') & (SER.wariant == variant)].sort_values('d0')
    out, prev = [], None
    for _, r in df.iterrows():
        L = [col[t] for t in r.L.split()]; S = [col[t] for t in r.S.split()]
        a, b = didx[r.d0], didx[r.d5]
        u = np.array([np.nanmean(R[t, L]) - np.nanmean(R[t, S]) for t in range(a + 1, b + 1)])
        ch = 10 if prev is None else len(set(L) - set(prev[0])) + len(set(S) - set(prev[1]))
        out.append(dict(u=u, s60=float(r.sigma_unit), ch=ch, sp=float(r.spread)))
        prev = (L, S)
    return out


def sim(weeks_sel, policy, alfa_day):
    """Wektorowo po ścieżkach: weeks_sel = lista (npath) list tygodni. Zwraca macierz dziennych zwrotów (npath × ndays)."""
    npath = len(weeks_sel); nd = sum(len(w['u']) for w in weeks_sel[0])
    # ułóż tablice dzienne: u, s60, ch, week-start flag
    U = np.zeros((npath, nd)); S60 = np.zeros((npath, nd)); CH = np.zeros((npath, nd)); WS = np.zeros((npath, nd), bool)
    for p, ws in enumerate(weeks_sel):
        k = 0
        for j, w in enumerate(ws):
            n = len(w['u'])
            if k + n > nd: n = nd - k
            U[p, k:k + n] = w['u'][:n] + alfa_day; S60[p, k:k + n] = w['s60']
            CH[p, k] = 10 if j == 0 else w['ch']; WS[p, k] = True
            k += n
            if k >= nd: break
    kind, base, mech = policy
    if kind == 'vt':
        a_base = np.clip(0.015 / (5 * S60), 0.04, 0.12)
    else:
        a_base = np.full((npath, nd), base)
    eq = np.ones(npath); peak = np.ones(npath); cyc = np.ones(npath)
    soft = np.zeros(npath, bool); killed = np.zeros(npath, bool)
    flat_until = np.full(npath, -1)      # indeks dnia, od którego wznowienie
    week_no = np.cumsum(WS[0]) - 1       # numer tygodnia dla dnia (identyczny dla wszystkich ścieżek)
    wstart = np.where(WS[0])[0]
    prev_a = np.zeros(npath); ret = np.zeros((npath, nd)); nflat = np.zeros(npath); softdays = np.zeros(npath)
    for t in range(nd):
        a = a_base[:, t].copy()
        if mech == 'soft':
            dd = eq / peak - 1
            soft = np.where(soft, dd <= -0.05, dd < -0.10)
            a = np.where(soft, a * 0.5, a); softdays += soft & (~killed)
        elif mech == 'flat':
            # wznowienie na początku tygodnia
            resume = WS[0, t] & (flat_until >= 0) & (t >= flat_until)
            cyc = np.where(resume, eq, cyc)
            flat_until = np.where(resume, -1, flat_until)
            inflat = flat_until >= 0
            a = np.where(inflat, 0.0, a)
        a = np.where(killed, 0.0, a)
        cost = np.where(CH[:, t] > 0, CH[:, t] * a * COST_LEG, 0.0) + np.abs(a - prev_a) * 10 * COST_LEG + FIN * 10 * a / 252
        r = 5 * a * U[:, t] - cost
        ret[:, t] = r
        eq = eq * (1 + r)
        peak = np.maximum(peak, eq)
        newkill = (~killed) & (eq / peak < KILL)
        killed |= newkill
        if mech == 'flat':
            cyc = np.maximum(cyc, eq)
            trig = (~killed) & (flat_until < 0) & (eq / cyc - 1 < -0.12)
            # płasko do końca tego tygodnia i przez cały następny → wznowienie na starcie tygodnia week_no+2
            wn = week_no[t]
            nxt = wstart[wn + 2] if wn + 2 < len(wstart) else nd + 1
            flat_until = np.where(trig, nxt, flat_until)
            nflat += trig
        prev_a = a
    sim.softfrac = float(softdays.mean() / nd)
    return ret, killed, nflat


def run(weeks, policy, alfa_pp, horizon_w):
    n = len(weeks); alfa_day = alfa_pp / 100 / 5
    sels = []
    for _ in range(NPATH):
        sel = []
        while len(sel) < horizon_w:
            s = rng.integers(0, n - BLOCK); sel.extend(weeks[s:s + BLOCK])
        sels.append(sel[:horizon_w])
    # wyrównaj liczbę dni: użyj minimalnej długości
    nd = min(sum(len(w['u']) for w in s) for s in sels)
    for s in sels:
        pass
    ret, killed, nflat = sim_trim(sels, policy, alfa_day, nd)
    eq = np.cumprod(1 + ret, axis=1)
    peak = np.maximum.accumulate(np.hstack([np.ones((NPATH, 1)), eq]), axis=1)[:, 1:]
    maxdd = (eq / peak - 1).min(axis=1)
    end = eq[:, -1]
    # tygodniowe zwroty kapitału (5-dniowe bloki) do Sharpe'a
    nw = nd // 5
    wk = eq[:, 4:nw * 5:5] / np.hstack([np.ones((NPATH, 1)), eq[:, 4:nw * 5 - 5:5]]) - 1
    mu_w = wk.mean(); sd_w = wk.std()
    return dict(pkill=float(killed.mean()), end_med=float(np.median(end)), end_p5=float(np.percentile(end, 5)),
                end_p95=float(np.percentile(end, 95)), end_mean=float(end.mean()), p_loss=float((end < 1).mean()),
                maxdd_med=float(np.median(maxdd)), maxdd_p95=float(np.percentile(maxdd, 5)),
                mu_week=float(mu_w * 100), sd_week=float(sd_w * 100), sharpe=float(mu_w / sd_w * math.sqrt(52)) if sd_w > 0 else 0.0,
                flat_per_path=float(nflat.mean()), soft_frac=float(getattr(sim, 'softfrac', 0.0)))


def sim_trim(sels, policy, alfa_day, nd):
    # obcięcie tygodni tak, by każda ścieżka miała nd dni: sim() bierze nd z pierwszej ścieżki — przytnij pierwszą
    ret, killed, nflat = sim(sels, policy, alfa_day) if sum(len(w['u']) for w in sels[0]) == nd else sim([_trim(s, nd) for s in sels], policy, alfa_day)
    return ret[:, :nd], killed, nflat


def _trim(sel, nd):
    out, k = [], 0
    for w in sel:
        n = len(w['u'])
        if k + n >= nd:
            w2 = dict(w); w2['u'] = w['u'][:nd - k]; out.append(w2); break
        out.append(w); k += n
    return out


POLICIES = [
    ('A', ('vt', None, 'soft'), 'PROJEKT A: A, vol-target [0,04;0,12] + próg miękki −10 %'),
    ('A', ('fix', 0.06, 'flat'), 'PROJEKT B (na konstrukcji A): stałe 0,06 + FLAT −12 % (cooldown 1 version)'),
    ('B_cap05', ('fix', 0.08, 'soft'), 'PROJEKT C: E (5 par, budżet SOX), stałe 0,08 + próg miękki −10 %'),
    ('A', ('fix', 0.06, None), 'A, stałe 0,06 bez schodka'),
    ('A', ('fix', 0.08, 'soft'), 'A, stałe 0,08 + próg miękki'),
    ('A', ('vt', None, None), 'A, vol-target bez progu'),
    ('B_cap05', ('fix', 0.08, None), 'E, stałe 0,08 bez progu'),
    ('B_cap05', ('fix', 0.06, 'flat'), 'E, stałe 0,06 + FLAT −12 % (B na E)'),
    ('B_cap05', ('fix', 0.06, 'soft'), 'E, stałe 0,06 + próg miękki'),
    ('B_cap05', ('fix', 0.10, 'soft'), 'E, stałe 0,10 + próg miękki'),
]


def main():
    W = {v: weeks_for(v) for v in ('A', 'B_cap05')}
    res = {}
    md = ['# sedzia3_harness — wspólny dzienny harness (209 okien PIT, blok 4 tyg., 3000 ścieżek, koszty wliczone)', '']
    for v, w in W.items():
        u_all = np.concatenate([x['u'] for x in w])
        md.append(f'- {v}: {len(w)} tygodni, {len(u_all)} sesji; średnia in-sample {u_all.mean()*5*100:+.2f} p.p./tydz., σ dz. jednostkowa {u_all.std()*100:.2f} %/d (σ tyg. ≈ {u_all.std()*math.sqrt(5)*100:.2f} p.p.)')
    md += ['', '| polityka | alfa p.p./tydz. | P(kill 12 t.) | P(kill 52 t.) | E[kapitał 52 t.] | mediana | p5 | p95 | P(strata) | maxDD med / p95 | μ tyg. kap. % | σ tyg. kap. % | Sharpe roczny | FLAT/rok |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for v, pol, label in POLICIES:
        w = W[v]
        mean_pp = float(np.concatenate([x['u'] for x in w]).mean() * 5 * 100)
        for alfa in (0.0, 0.5, 1.0):
            a_rel = alfa - mean_pp
            r12 = run(w, pol, a_rel, 12); r52 = run(w, pol, a_rel, 52)
            key = f'{label}|alfa{alfa}'
            res[key] = dict(k12=r12, k52=r52)
            md.append(f'| {label} | {alfa:+.1f} | {r12["pkill"]*100:.1f}% | {r52["pkill"]*100:.1f}% | {r52["end_mean"]:.3f} | {r52["end_med"]:.3f} | {r52["end_p5"]:.3f} | {r52["end_p95"]:.3f} | {r52["p_loss"]*100:.0f}% | {r52["maxdd_med"]*100:.0f}% / {r52["maxdd_p95"]*100:.0f}% | {r52["mu_week"]:+.3f} | {r52["sd_week"]:.2f} | {r52["sharpe"]:+.2f} | {r52["flat_per_path"]:.2f} |')
    txt = '\n'.join(md)
    open(f'{BASE}/sedzia3_harness_out.md', 'w').write(txt)
    json.dump(res, open(f'{BASE}/sedzia3_harness_wyniki.json', 'w'), indent=1)
    print(txt)


if __name__ == '__main__':
    main()
