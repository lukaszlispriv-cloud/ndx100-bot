#!/usr/bin/env python3
"""projektC_dod.py — dodatki: P(kill) B_cap05 przy 0,10 i vt 1,0%; moc testu F; wrażliwość na definicję grupy."""
import json, math, numpy as np, pandas as pd, importlib, sys
sys.argv = ['x']
import projektC_bt as C
rng = np.random.default_rng(7)
ser = pd.read_csv(C.OUT_SER)
out = {}; L = []
P = L.append
def boot(df, pol, a0, weeks, soft=False, vt_target=0.015, npath=4000):
    sp = df.spread.values.copy()
    if a0: sp = sp - sp.mean()
    su = df.sigma_unit.values; tl = df.turn_legs.values; n = len(sp); kills = 0
    for p in range(npath):
        idx = []
        while len(idx) < weeks:
            s = rng.integers(0, n - 4); idx.extend(range(s, s + 4))
        cap = peak = 1.0; son = False
        for i in idx[:weeks]:
            a = min(0.12, max(0.04, vt_target / (5 * su[i]))) if pol == 'vt' else float(pol.split(':')[1])
            if soft:
                dd = cap / peak - 1
                if dd < -0.10: son = True
                elif dd > -0.05: son = False
                if son: a *= 0.5
            cap *= 1 + 5 * a * sp[i] / 100 - 10 * a * C.FIN / 52 - tl[i] * a * C.COST_LEG
            peak = max(peak, cap)
            if cap < 0.75 * peak: kills += 1; break
    return kills / npath
P('## A. P(kill) dla B_cap05 i B — dodatkowe polityki (bootstrap blokowy, 4000 ścieżek, koszty wliczone)\n')
P('| konstrukcja | skład | polityka | alfa | P(kill 12) | P(kill 26) | P(kill 52) |'); P('|---|---|---|---|---|---|---|')
for v in ('B_cap05', 'B'):
    for tag in ('PIT', 'dzis'):
        df = ser[(ser.wariant == v) & (ser.sklad == tag)]
        for pol, soft, tgt in (('fix:0.10', False, None), ('fix:0.10', True, None), ('fix:0.08', True, None), ('vt', False, 0.010), ('vt', True, 0.010)):
            for a0 in (True, False):
                r = [boot(df, pol, a0, w, soft, tgt or 0.015) for w in (12, 26, 52)]
                lab = pol + (f' (cel {tgt*100:.1f}%/d)' if tgt else '') + (' + soft −10%' if soft else '')
                out[f'{v}|{tag}|{lab}|{"alfa0" if a0 else "in"}'] = r
                P(f"| {v} | {tag} | {lab} | {'0' if a0 else 'in-sample'} | {r[0]*100:.1f}% | {r[1]*100:.1f}% | {r[2]*100:.1f}% |")
P('\n## B. Moc testu F (σ_B/σ_A) na koszykach cieniach — bootstrap par tygodni (A, B_cap05) PIT\n')
a = ser[(ser.wariant == 'A') & (ser.sklad == 'PIT')].set_index('w').spread
b = ser[(ser.wariant == 'B_cap05') & (ser.sklad == 'PIT')].set_index('w').spread
j = pd.concat([a, b], axis=1, keys=['a', 'b']).dropna()
P('| tygodni | P(F-test p<0,05) | P(σ-ratio < 0,85) | mediana σ-ratio | p5–p95 σ-ratio | P(sparowany t(Δ) < −2) |'); P('|---|---|---|---|---|---|')
from math import erf
powr = {}
for n in (12, 26, 52):
    sig = 0; r85 = 0; rs = []; tneg = 0
    for _ in range(4000):
        idx = []
        while len(idx) < n:
            s = rng.integers(0, len(j) - 4); idx.extend(range(s, s + 4))
        x = j.iloc[idx[:n]]
        ratio = x.b.std(ddof=1) / x.a.std(ddof=1); rs.append(ratio)
        z = math.log(ratio ** 2) / math.sqrt(4 / (n - 1)); p = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))
        sig += p < 0.05 and ratio < 1; r85 += ratio < 0.85
        d = x.b - x.a; tneg += (d.mean() / d.std(ddof=1) * math.sqrt(n)) < -2
    powr[n] = dict(power_F=sig / 4000, p_ratio_lt_085=r85 / 4000, med=float(np.median(rs)), p5=float(np.percentile(rs, 5)), p95=float(np.percentile(rs, 95)), p_tneg=tneg / 4000)
    P(f"| {n} | {sig/4000*100:.0f}% | {r85/4000*100:.0f}% | {np.median(rs):.2f} | {np.percentile(rs,5):.2f}–{np.percentile(rs,95):.2f} | {tneg/4000*100:.1f}% |")
out['moc_F'] = powr
# ile tygodni, by wykryć Δ średniej: σ(Δ) sparowanej
d = j.b - j.a
P(f"\nσ sparowanej różnicy B_cap05 − A (PIT): {d.std(ddof=1):.2f} p.p./tydz.; tygodni do t=2 przy prawdziwej Δ 0,3 / 0,5 / 1,0 p.p.: {int((2*d.std(ddof=1)/0.3)**2)} / {int((2*d.std(ddof=1)/0.5)**2)} / {int((2*d.std(ddof=1)/1.0)**2)}")
out['sd_delta'] = float(d.std(ddof=1))
P('\n## C. Wrażliwość B_cap05 na definicję grupy (skład PIT i dzisiejszy)\n')
P('| definicja | skład | n | śr. | σ | Sharpe | Δ vs A | t(Δ) | σ-ratio | b_SOX zreal. | najgorszy |'); P('|---|---|---|---|---|---|---|---|---|---|---|')
defs = {'base industry≥4|sector, grupa≥3': (4, 3), 'industry≥2|sector': (2, 3), 'industry≥6|sector': (6, 3), 'grupa≥5': (4, 5)}
sens = {}
for name, (mi, mg) in defs.items():
    C.MIN_IND, C.MIN_GROUP = mi, mg
    for pit in (True, False):
        tag = 'PIT' if pit else 'dzis'
        df = C.run('B_cap05', pit)
        base = ser[(ser.wariant == 'A') & (ser.sklad == tag)].set_index('w')
        pp = C.paired(base, df); m = C.metr(df.spread); ff = C.factor_fit(df)
        sens[f'{name}|{tag}'] = dict(m=m, paired=pp, bsox=ff['b_sox'])
        P(f"| {name} | {tag} | {m['n']} | {m['mean']:+.2f} | {m['sd']:.2f} | {m['sharpe']:.2f} | {pp['delta']:+.2f} | {pp['t']:+.2f} | {pp['sigma_ratio']:.3f} | {ff['b_sox']:+.2f} | {m['worst']:.1f} |")
# sector-only
C.MIN_IND, C.MIN_GROUP = 10**6, 3
for pit in (True, False):
    tag = 'PIT' if pit else 'dzis'
    df = C.run('B_cap05', pit); base = ser[(ser.wariant == 'A') & (ser.sklad == tag)].set_index('w')
    pp = C.paired(base, df); m = C.metr(df.spread); ff = C.factor_fit(df)
    sens[f'sector-only|{tag}'] = dict(m=m, paired=pp, bsox=ff['b_sox'])
    P(f"| sector-only | {tag} | {m['n']} | {m['mean']:+.2f} | {m['sd']:.2f} | {m['sharpe']:.2f} | {pp['delta']:+.2f} | {pp['t']:+.2f} | {pp['sigma_ratio']:.3f} | {ff['b_sox']:+.2f} | {m['worst']:.1f} |")
out['wrazliwosc'] = sens
def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    if isinstance(o, (np.floating, float)): return round(float(o), 5)
    if isinstance(o, np.integer): return int(o)
    return o
json.dump(clean(out), open('projektC_dod_wyniki.json', 'w'), ensure_ascii=False, indent=1)
open('projektC_dod_out.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
