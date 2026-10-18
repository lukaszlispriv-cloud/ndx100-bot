import sys, json, math, numpy as np
sys.path.insert(0, '.')
import sedzia3_harness as H
W = {v: H.weeks_for(v) for v in ('A', 'B_cap05')}
mean = {v: float(np.concatenate([x['u'] for x in w]).mean() * 5 * 100) for v, w in W.items()}
rows = [('A', ('vt', None, 'soft'), 'A vt+soft', (0.0, 0.3, 0.5)),
        ('A', ('fix', 0.06, 'flat'), 'A 0,06+FLAT', (0.3,)),
        ('A', ('fix', 0.08, 'soft'), 'A 0,08+soft', (0.3,)),
        ('B_cap05', ('fix', 0.08, 'soft'), 'E 0,08+soft', (-0.4, -0.2, 0.0, 0.2, 0.3)),
        ('B_cap05', ('fix', 0.06, 'soft'), 'E 0,06+soft', (0.0,)),
        ('B_cap05', ('fix', 0.10, 'soft'), 'E 0,10+soft', (0.0, 0.2)),
        ('B_cap05', ('fix', 0.08, None), 'E 0,08 bez progu', (-0.2, 0.2))]
out = ['| polityka | alfa | P(kill 52) | E[kap.] | med | p5 | maxDD p95 | μ tyg. | σ tyg. | Sharpe | udział dni z soft |', '|---|---|---|---|---|---|---|---|---|---|---|']
res = {}
for v, pol, lab, alfas in rows:
    for a in alfas:
        r = H.run(W[v], pol, a - mean[v], 52)
        res[f'{lab}|{a}'] = r
        out.append(f'| {lab} | {a:+.1f} | {r["pkill"]*100:.1f}% | {r["end_mean"]:.3f} | {r["end_med"]:.3f} | {r["end_p5"]:.3f} | {r["maxdd_p95"]*100:.0f}% | {r["mu_week"]:+.3f} | {r["sd_week"]:.2f} | {r["sharpe"]:+.2f} | {r["soft_frac"]*100:.0f}% |')
txt = '\n'.join(out); print(txt)
open('sedzia3_dod_out.md', 'w').write('# sedzia3_dod — alfy równoważne i udział dni z progiem miękkim (52 tyg., 3000 ścieżek)\n\n' + txt)
json.dump(res, open('sedzia3_dod_wyniki.json', 'w'), indent=1)
