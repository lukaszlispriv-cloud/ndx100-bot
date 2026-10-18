#!/usr/bin/env python3
"""weryfikacja_C3_dod.py — dodatek: korekta o artefakt szumu, ciaśniejsze stopy (ogon/kill), kill12 na losowych,
tercyle zmienności koszyka, okna niosące koszt, porównanie wejście-D0 ze stopem wobec v1."""
import json, math, sys
import numpy as np, pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
src = open(f'{BASE}/analiza/weryfikacja_C3.py').read()
head = src.split('# ----------------------------------------------------------------------------- warianty')[0]
exec(compile(head, 'weryfikacja_C3_head', 'exec'))
OUT_MD = f'{BASE}/analiza/weryfikacja_C3_dod_out.md'
OUT_JSON = f'{BASE}/analiza/weryfikacja_C3_dod_wyniki.json'
L = []; J = {}

V = {
    'v2_bez_stopu': Cfg('v2_bez_stopu'),
    'v3_stop10_close': Cfg('v3_stop10_close', stop=0.10),
    'v4_stop10_close_reopen': Cfg('v4_stop10_close_reopen', stop=0.10, reopen=True),
    't1_intra05_thr': Cfg('t1_intra05_thr', stop=0.10, intraday=0.5, fill='thr'),
    't1_intra05_thr_reopen': Cfg('t1_intra05_thr_reopen', stop=0.10, intraday=0.5, fill='thr', reopen=True),
    't1_intra05_close': Cfg('t1_intra05_close', stop=0.10, intraday=0.5, fill='close'),
    't1_intra05_close_reopen': Cfg('t1_intra05_close_reopen', stop=0.10, intraday=0.5, fill='close', reopen=True),
    't3_stop10_anchor_d0': Cfg('t3_stop10_anchor_d0', stop=0.10, anchor='d0'),
    't_stop15_close': Cfg('t_stop15_close', stop=0.15),
    't_stop15_intra05_thr': Cfg('t_stop15_intra05_thr', stop=0.15, intraday=0.5, fill='thr'),
    't_stop20_close': Cfg('t_stop20_close', stop=0.20),
    't_stop07_close': Cfg('t_stop07_close', stop=0.07),
    't_stop07_close_reopen': Cfg('t_stop07_close_reopen', stop=0.07, reopen=True),
    't_stop05_close': Cfg('t_stop05_close', stop=0.05),
    't_stop07_intra05_thr': Cfg('t_stop07_intra05_thr', stop=0.07, intraday=0.5, fill='thr'),
    't2_stop10_long_only': Cfg('t2_stop10_long_only', stop=0.10, side='long'),
    't2_stop10_short_only': Cfg('t2_stop10_short_only', stop=0.10, side='short'),
    't2_stop07_long_only': Cfg('t2_stop07_long_only', stop=0.07, side='long'),
    't2_stop07_short_only': Cfg('t2_stop07_short_only', stop=0.07, side='short'),
}
RES = {k: run(v) for k, v in V.items()}
base = RES['v2_bez_stopu']['gross']

# --- 1. losowe strategie przez wszystkie warianty (ten sam zestaw losowań) → korekta o artefakt szumu
rng2 = np.random.default_rng(SEED + 1)
saveL, saveS = LONGS, SHORTS
RB = {k: [] for k in V}
RAND_SETS = []
for b in range(100):
    LONGS = list(saveL); SHORTS = list(saveS)
    for w in widx:
        E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
        ok = np.where(~np.isnan(WR[w]) & ~np.isnan(P[E]) & ~np.isnan(P[X]))[0]
        pick = rng2.choice(ok, NL + NS, replace=False)
        LONGS[w] = pick[:NL]; SHORTS[w] = pick[NL:]
    RAND_SETS.append((list(LONGS), list(SHORTS)))
    for k, cfg in V.items():
        r = run(cfg)
        g = r['gross']
        RB[k].append(dict(mean=g.mean(), p5=np.percentile(g, 5), p1=np.percentile(g, 1), mn=g.min(), sigma=g.std(ddof=1),
                          cvar5=np.sort(g)[:12].mean(), stops=r['stops'], maxdd=tail(g)['maxdd']))
    print(f'  random {b + 1}/{RANDOM_EXEC}', file=sys.stderr, end='\r')
LONGS, SHORTS = saveL, saveS
print(file=sys.stderr)

L.append('# weryfikacja_C3 — dodatek\n')
L.append('## D1. Koszt stopu z korektą o artefakt na szumie (Δ_momentum − Δ_losowe; pp/tydz., brutto)\n')
L.append('Δ_losowe = średnia po 100 losowych strategiach 5/5 (te same okna) różnicy wariant − v2; przy realizacji „na progu” proxy intraday jest dodatni (realizacja lepsza niż zamknięcie, gdy zamknięcie < próg).\n')
L.append('| wariant | Δ momentum (t) | Δ losowe (5–95%) | Δ skorygowane | σ tyg. mom. | σ tyg. los. (v2: {:.2f}) | p5 mom. | p5 los. (v2: {:.2f}) | min mom. | CVaR5 mom. | CVaR5 los. (v2: {:.2f}) | maxDD mom. | maxDD los. śr. (v2: {:.1f}) |'.format(
    np.mean([x['sigma'] for x in RB['v2_bez_stopu']]), np.mean([x['p5'] for x in RB['v2_bez_stopu']]),
    np.mean([x['cvar5'] for x in RB['v2_bez_stopu']]), np.mean([x['maxdd'] for x in RB['v2_bez_stopu']])))
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
m0 = np.array([x['mean'] for x in RB['v2_bez_stopu']])
D1 = {}
for k in V:
    if k == 'v2_bez_stopu':
        continue
    g = RES[k]['gross']; d = g - base
    mr = np.array([x['mean'] for x in RB[k]]) - m0
    tl = tail(g)
    D1[k] = dict(d_mom=float(d.mean()), t=float(tstat(d)), d_rand=float(mr.mean()), d_rand_p5=float(np.percentile(mr, 5)),
                 d_rand_p95=float(np.percentile(mr, 95)), d_corr=float(d.mean() - mr.mean()), sigma=float(tl['sigma']),
                 sigma_rand=float(np.mean([x['sigma'] for x in RB[k]])), p5=float(tl['p5']), p5_rand=float(np.mean([x['p5'] for x in RB[k]])),
                 min=float(tl['min']), cvar5=float(tl['cvar5']), cvar5_rand=float(np.mean([x['cvar5'] for x in RB[k]])),
                 maxdd=float(tl['maxdd']), maxdd_rand=float(np.mean([x['maxdd'] for x in RB[k]])), stops=int(RES[k]['stops']))
    x = D1[k]
    L.append(f"| {k} | {x['d_mom']:+.3f} ({x['t']:+.2f}) | {x['d_rand']:+.3f} ({x['d_rand_p5']:+.2f}…{x['d_rand_p95']:+.2f}) | **{x['d_corr']:+.3f}** | "
             f"{x['sigma']:.2f} | {x['sigma_rand']:.2f} | {x['p5']:+.1f} | {x['p5_rand']:+.2f} | {x['min']:+.1f} | {x['cvar5']:+.1f} | {x['cvar5_rand']:+.2f} | {x['maxdd']:.1f} | {x['maxdd_rand']:.1f} |")
L.append('')

# --- 2. kill12 na losowych strategiach (100 strategii) dla v2, v3, t1_intra05_thr, t_stop07_close
L.append('## D2. Kill switch 25% w oknach 12-tyg. — momentum vs losowe strategie (30 losowań)\n')
L.append('| wariant | kill12 momentum | kill12 losowe śr. (5–95%) | 5. pct min kapitału mom. | 5. pct min kapitału los. śr. |')
L.append('|---|---|---|---|---|')
D2 = {}
for k in ('v2_bez_stopu', 'v3_stop10_close', 't1_intra05_thr', 't_stop07_close'):
    h, tot, minC = kill12(V[k])
    kr = []; mr = []
    for b in range(30):
        LONGS, SHORTS = RAND_SETS[b]
        hh, tt, mc = kill12(V[k])
        kr.append(100 * hh / tt); mr.append(np.percentile(mc, 5))
    LONGS, SHORTS = saveL, saveS
    kr = np.array(kr)
    D2[k] = dict(kill_mom=100 * h / tot, kill_rand=float(kr.mean()), kill_rand_p5=float(np.percentile(kr, 5)), kill_rand_p95=float(np.percentile(kr, 95)),
                 minC_mom=float(np.percentile(minC, 5)), minC_rand=float(np.mean(mr)))
    L.append(f"| {k} | {100 * h / tot:.1f}% | {kr.mean():.1f}% ({np.percentile(kr, 5):.1f}…{np.percentile(kr, 95):.1f}) | {np.percentile(minC, 5):.1f} | {np.mean(mr):.1f} |")
    print(f'  kill12 {k} done', file=sys.stderr)
L.append('')

# --- 3. tercyle zmienności koszyka ex ante (średnia σ60 nóg na wejściu) — czy koszt stopu zależy od tego, ile σ to 10%
L.append('## D3. Koszt stopu wg tercyli zmienności koszyka ex ante (śr. σ60 dzienna nóg na sesji wejścia; 10% w jednostkach σ5 = 0,10/(σ60·√5))\n')
sig_b = []
for w in widx:
    E = min(D0[w] + 1, nT - 1)
    idx = np.concatenate([LONGS[w], SHORTS[w]])
    sig_b.append(np.nanmean(SIG60F[E, idx]))
sig_b = np.array(sig_b)
ter = np.digitize(sig_b, np.percentile(sig_b, [33.3, 66.7]))
L.append('| tercyl | n | śr. σ60 nogi | 10% w σ5 | śr. v2 | Δ v3 (t) | Δ v4 (t) | Δ intra05_thr (t) | Δ stop07_close (t) | Δ stop15_close (t) | stopy v3 | p5 v2 | p5 v3 | p5 stop07 |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
D3 = {}
for q in range(3):
    m = ter == q
    def cell(k):
        d = (RES[k]['gross'] - base)[m]
        return f"{d.mean():+.3f} ({tstat(d):+.1f})"
    s = sig_b[m].mean()
    D3[q] = dict(n=int(m.sum()), sigma=float(s), v3=float((RES['v3_stop10_close']['gross'] - base)[m].mean()),
                 v4=float((RES['v4_stop10_close_reopen']['gross'] - base)[m].mean()),
                 stop07=float((RES['t_stop07_close']['gross'] - base)[m].mean()))
    L.append(f"| {q + 1} | {m.sum()} | {100 * s:.2f}% | {0.10 / (s * math.sqrt(5)):.2f}σ | {base[m].mean():+.2f} | {cell('v3_stop10_close')} | {cell('v4_stop10_close_reopen')} | "
             f"{cell('t1_intra05_thr')} | {cell('t_stop07_close')} | {cell('t_stop15_close')} | {int(RES['v3_stop10_close']['stops_w'][m].sum())} | "
             f"{np.percentile(base[m], 5):+.1f} | {np.percentile(RES['v3_stop10_close']['gross'][m], 5):+.1f} | {np.percentile(RES['t_stop07_close']['gross'][m], 5):+.1f} |")
# koszyki W4–W7: σ60 nóg dla odniesienia
KZ = {'W4': (['MU', 'AMD', 'AVGO', 'MRVL', 'LITE'], ['INTU', 'SBUX', 'CMCSA', 'APP', 'ADSK'], '2026-09-14'),
      'W7': (['MU', 'LITE', 'MRVL', 'PANW', 'CSCO'], ['CMCSA', 'SBUX', 'PEP', 'TMUS', 'APP'], '2026-10-12'),
      'W8': (['GOOGL', 'GILD', 'MSFT', 'QCOM', 'ADP'], ['AXON', 'DASH', 'ALNY', 'APP', 'FER'], '2026-10-16')}
DIx = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(dates)}
refs = []
for wk, (lg, sh, dt) in KZ.items():
    i = DIx[dt]; s = np.nanmean(SIG60F[i, [COL[t] for t in lg + sh]])
    sl = np.nanmean(SIG60F[i, [COL[t] for t in lg]]); ss = np.nanmean(SIG60F[i, [COL[t] for t in sh]])
    refs.append(f"{wk}: σ60 nóg {100 * s:.2f}% (long {100 * sl:.2f}%, short {100 * ss:.2f}%) = percentyl {100 * (sig_b < s).mean():.0f} rozkładu okien momentum")
L.append('\nOdniesienie koszyków faktycznych: ' + '; '.join(refs) + '.\n')

# --- 4. okna niosące koszt v3 i v4
L.append('## D4. Okna z największym |Δ| (v3 − v2) — co stop uciął\n')
d3 = RES['v3_stop10_close']['gross'] - base
order = np.argsort(d3)
L.append('| okno D0 | Δ v3 | Δ v4 | v2 | stopy v3 | nogi ze stopem (kierunek, zwrot od stopu do wyjścia %) |')
L.append('|---|---|---|---|---|---|')
D4 = []
for k in list(order[:8]) + list(order[-4:]):
    w = widx[k]
    E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
    legs = [(int(i), +1) for i in LONGS[w]] + [(int(i), -1) for i in SHORTS[w]]
    desc = []
    for i, dd in legs:
        pe = PF[E, i]
        for t in range(E + 1, X + 1):
            if -dd * (PF[t, i] / pe - 1) >= 0.10:
                rest = dd * (PF[X, i] / PF[t, i] - 1) * 100
                desc.append(f"{cands[i]} {'L' if dd > 0 else 'S'} d{t - E} close {100 * (PF[t, i] / pe - 1):+.1f}% → {rest:+.1f}%")
                break
    D4.append(dict(d0=str(dates[D0[w]].date()), d_v3=float(d3[k]), d_v4=float((RES['v4_stop10_close_reopen']['gross'] - base)[k]), legs=desc))
    L.append(f"| {dates[D0[w]].date()} | {d3[k]:+.2f} | {(RES['v4_stop10_close_reopen']['gross'] - base)[k]:+.2f} | {base[k]:+.2f} | {int(RES['v3_stop10_close']['stops_w'][k])} | {'; '.join(desc)} |")
srt = np.argsort(d3)
L.append(f"\nSuma Δ v3: {d3.sum():+.1f} pp; udział 5 najgorszych okien: {d3[srt[:5]].sum():+.1f} pp; 10 najgorszych: {d3[srt[:10]].sum():+.1f} pp; "
         f"suma dodatnich Δ: {d3[d3 > 0].sum():+.1f} pp (n={int((d3 > 0).sum())}), suma ujemnych: {d3[d3 < 0].sum():+.1f} pp (n={int((d3 < 0).sum())}); mediana Δ w oknach ze stopem: {np.median(d3[d3 != 0]):+.2f}.\n")

# --- 5. wejście D0 ze stopem vs v1 (sparowane)
v1 = run(Cfg('v1', entry='d0'))['gross']
for nm, cfg in (('d0_stop10_close', Cfg('x', entry='d0', stop=0.10)), ('d0_stop10_close_reopen', Cfg('x', entry='d0', stop=0.10, reopen=True)),
                ('d0_intra05_thr', Cfg('x', entry='d0', stop=0.10, intraday=0.5, fill='thr'))):
    g = run(cfg)['gross']; d = g - v1
    lo, hi, pp = boot_ci(d)
    L.append(f"Wejście D0: {nm} − v1 = {d.mean():+.3f} pp/tydz. (t {tstat(d):+.2f}; boot 95% {lo:+.3f}…{hi:+.3f}); stopy {run(cfg)['stops']}.")
    J[f'd0_{nm}'] = dict(d=float(d.mean()), t=float(tstat(d)))
L.append('')

# --- 6. rozkład Δ: ile okien stop pomógł o > 2 pp vs zaszkodził o > 2 pp
L.append('## D5. Rozkład Δ (v3 − v2) i (stop07 − v2)\n')
for k in ('v3_stop10_close', 'v4_stop10_close_reopen', 't_stop07_close', 't1_intra05_close'):
    d = RES[k]['gross'] - base
    L.append(f"- {k}: Δ>+2 pp w {int((d > 2).sum())} oknach (suma {d[d > 2].sum():+.1f}), Δ<−2 pp w {int((d < -2).sum())} (suma {d[d < -2].sum():+.1f}); |Δ|≤2: {int((np.abs(d) <= 2).sum())} (suma {d[np.abs(d) <= 2].sum():+.1f}); p99 Δ {np.percentile(d, 99):+.1f}, p1 Δ {np.percentile(d, 1):+.1f}")
L.append('')

open(OUT_MD, 'w').write('\n'.join(L))
J.update(D1=D1, D2=D2, D3=D3, D4=D4)
json.dump(J, open(OUT_JSON, 'w'), indent=1, ensure_ascii=False, default=lambda o: float(o))
print('\n'.join(L))
