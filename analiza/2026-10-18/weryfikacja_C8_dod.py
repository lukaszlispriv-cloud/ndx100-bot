#!/usr/bin/env python3
"""Dodatek C8: (1) kontrola iso-gross — stały ALLOC o tej samej średniej ekspozycji co bramka (0,24×0,74);
(2) epizody drawdownu z datami i czasem odrobienia; (3) tygodnie, które histereza trzyma surowiej niż progi;
(4) tygodnie aktywne w 2022; (5) losowe koszyki: bramka vs stały iso-gross (sparowane)."""
import sys, json, math
import numpy as np, pandas as pd
sys.argv = ['x']
exec(open('/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C8.py').read().split('# ------------------------------------------------------------------ stany bramki')[0])
ST_HYS = gate_states(); ST_RAW = gate_states(hyst=False)
G_HYS_W = gross_from_state(ST_HYS[D0]); G_RAW_W = gross_from_state(ST_RAW[D0]); G_HYS_D = gross_from_state(ST_HYS)
G_P2ONLY_W = np.where(ST_HYS[D0] == 2, 0.0, 1.0)
OUT = f'{BASE}/analiza/weryfikacja_C8_dod_out.md'; OUTJ = f'{BASE}/analiza/weryfikacja_C8_dod_wyniki.json'
md = []; out = {}
md.append('# Dodatek C8\n')

# (4) aktywność 2022
m22 = YEAR == 2022
md.append(f'Tygodnie 2022 (D0 w 2022): {m22.sum()}; z bramką hist. P1 {int((ST_HYS[D0][m22]==1).sum())}, P2 {int((ST_HYS[D0][m22]==2).sum())} → aktywna w {int((ST_HYS[D0][m22]>0).sum())}/{m22.sum()} tyg.; '
          f'cała próba: aktywna {int((ST_HYS[D0]>0).sum())}/{nW} (P1 {int((ST_HYS[D0]==1).sum())}, P2 {int((ST_HYS[D0]==2).sum())}). Śr. gross 2022 = {100*G_HYS_W[m22].mean():.0f}%.\n')
out['active'] = dict(y2022_active=int((ST_HYS[D0][m22]>0).sum()), y2022_n=int(m22.sum()), total_active=int((ST_HYS[D0]>0).sum()))

# (3) histereza vs surowa
hs = ST_HYS[D0]; rw = ST_RAW[D0]
cap_wk = 1.2 * SPREAD
md.append('## Tygodnie, w których histereza trzyma stan SUROWSZY niż progi (odczyt D0) — co robiło momentum\n')
md.append('| przypadek | okna | śr. % kap. (gross 100%) | t | lata |\n|---|---|---|---|---|')
for lab, m in (('hist. P2, surowa P1/P0 (po epizodzie P2, przed histerezą)', (hs == 2) & (rw < 2)),
               ('hist. P1, surowa P0 (po P1, przed 3 sesjami powrotu)', (hs == 1) & (rw == 0)),
               ('hist. łagodniejsza niż surowa (nie powinno być)', hs < rw),
               ('stan zgodny, P1', (hs == 1) & (rw == 1)), ('stan zgodny, P2', (hs == 2) & (rw == 2))):
    x = cap_wk[m]
    yrs = ', '.join(f'{y}:{int(((YEAR==y)&m).sum())}' for y in sorted(set(YEAR[m]))) if m.sum() else '—'
    t = x.mean()/x.std(ddof=1)*math.sqrt(len(x)) if len(x) > 1 else float('nan')
    md.append(f'| {lab} | {m.sum()} | {x.mean():.2f} | {t:.2f} | {yrs} |' if m.sum() else f'| {lab} | 0 | — | — | — |')
    out[f'hyst_{lab[:20]}'] = dict(n=int(m.sum()), mean=float(x.mean()) if m.sum() else None)

# (2) epizody DD z datami
sess = list(range(D0[0], D5[-1] + 1))
def episodes(curve, thr=0.20):
    c = np.asarray(curve); ep = []; pk = 0
    i = 0
    while i < len(c):
        if c[i] >= c[pk]:
            pk = i; i += 1; continue
        # szukamy końca epizodu: powrót do c[pk]
        j = i
        while j < len(c) and c[j] < c[pk]:
            j += 1
        tr = pk + int(np.argmin(c[pk:j])) if j > pk else pk
        depth = 1 - c[tr] / c[pk]
        if depth >= thr:
            ep.append(dict(peak=dates[sess[pk]].date().isoformat(), trough=dates[sess[tr]].date().isoformat(), depth=100*depth,
                           p2t=tr - pk, recovery=(j - pk) if j < len(c) else None,
                           state_at_trough=int(ST_HYS[sess[tr]])))
        if j >= len(c):
            break
        pk = j; i = j
    return ep
md.append('\n## Epizody drawdownu ≥20% kapitału (ścieżka BEZ kill), ALLOC 0,24\n')
for name, gw, gd in (('bez bramki', None, None), ('bramka hist. D0', G_HYS_W, None), ('bramka hist. dzienna', None, G_HYS_D), ('stały ALLOC 0,178 (iso-gross)', None, None)):
    alloc = 0.24 * float(G_HYS_W.mean()) if 'iso' in name else ALLOC
    rn = simulate(LONGS, SHORTS, gw, gd, alloc=alloc, kill=False)
    ep = episodes(rn['curve'])
    out[f'episodes_{name}'] = ep
    md.append(f'**{name}** (ALLOC {alloc:.3f}):\n')
    md.append('| szczyt | dołek | głębokość % | szczyt→dołek ses. | odrobienie ses. (od szczytu) | stan bramki w dołku |\n|---|---|---|---|---|---|')
    for e in ep:
        md.append(f"| {e['peak']} | {e['trough']} | {e['depth']:.1f} | {e['p2t']} | {e['recovery'] if e['recovery'] is not None else 'nie odrobiono do 2026-10-16'} | P{e['state_at_trough']} |")
    md.append('')

# (1) iso-gross: stały ALLOC = 0,24 × śr. gross bramki
md.append('## Kontrola iso-gross: bramka (śr. gross 74%) vs stały ALLOC 0,24×0,74 = 0,178 (gross 178%) vs bramka — momentum 6M\n')
md.append('| wariant | ALLOC | śr. gross (×240%) | kapitał końc. bez kill | maxDD % | Sharpe netto | t | P(kill 12 t.) | P(kill 26 t.) | kill 12 t. 2022 | kill 12 t. 2023–26 | kapitał Z KILL | kill (data) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
iso = {}
g_mean = float(G_HYS_W.mean())
for name, gw, gd, alloc in (('bez bramki', None, None, ALLOC), ('bramka hist. D0', G_HYS_W, None, ALLOC), ('bramka hist. dzienna', None, G_HYS_D, ALLOC),
                            ('stały iso-gross', None, None, ALLOC * g_mean), ('stały ALLOC 0,16', None, None, 0.16), ('stały ALLOC 0,12', None, None, 0.12),
                            ('bramka hist. D0 + ALLOC 0,16 (gross P0 160%)', G_HYS_W, None, 0.16)):
    rn = simulate(LONGS, SHORTS, gw, gd, alloc=alloc, kill=False); rk = simulate(LONGS, SHORTS, gw, gd, alloc=alloc, kill=True)
    s = path_stats(rn['curve'], rn['wk'], nW)
    h12, t12, _, _ = kill_windows(LONGS, SHORTS, gw, gd, H=12, alloc=alloc); h26, t26, _, _ = kill_windows(LONGS, SHORTS, gw, gd, H=26, alloc=alloc)
    k22 = sum(simulate(LONGS, SHORTS, gw, gd, alloc=alloc, w_from=s_, w_to=s_+12)['killed_at'] is not None for s_ in range(0, nW-11) if YEAR[s_] == 2022)
    n22 = sum(1 for s_ in range(0, nW-11) if YEAR[s_] == 2022)
    iso[name] = dict(alloc=alloc, gross=float(rn['gross'].mean()) * alloc / ALLOC, final=s['final'], maxdd=s['maxdd_pct'], sharpe=s['sharpe'], t=s['t'], k12=h12/t12, k26=h26/t26, k22=k22, n22=n22, k_rest=h12-k22, n_rest=t12-n22, final_kill=rk['final'], killed=dates[rk['killed_at'][1]].date().isoformat() if rk['killed_at'] else None)
    md.append(f"| {name} | {alloc:.3f} | {100*rn['gross'].mean()*alloc/ALLOC:.0f}% | {s['final']:.1f} | {s['maxdd_pct']:.1f} | {s['sharpe']:.3f} | {s['t']:.2f} | {100*h12/t12:.1f}% | {100*h26/t26:.1f}% | {k22}/{n22} | {h12-k22}/{t12-n22} | {rk['final']:.1f} | {iso[name]['killed'] or '—'} |")
out['iso'] = iso

# (5) losowe: bramka vs iso-gross, sparowane
md.append('\n## Losowe koszyki 5/5 (zerowa alfa), 200 strategii: bramka hist. D0 vs stały iso-gross ALLOC 0,178 — sparowane\n')
rng = np.random.default_rng(SEED + 7)
L_MOM = 126
MOM_OK = np.zeros((nW, nS), bool)
for w in range(nW):
    i = D0[w]
    if i >= L_MOM:
        MOM_OK[w] = ~np.isnan(P[i]) & ~np.isnan(P[i - L_MOM]) & ~np.isnan(P[D5[w]])
res = {k: dict(k12=[], maxdd=[], sharpe=[], k22=[]) for k in ('bez', 'gate', 'iso')}
NR = 200
for n in range(NR):
    Lr = []; Sr = []
    for w in range(nW):
        ok = np.flatnonzero(MOM_OK[w]); pk = rng.choice(ok, 10, replace=False); Lr.append(list(pk[:5])); Sr.append(list(pk[5:]))
    for k, gw, alloc in (('bez', None, ALLOC), ('gate', G_HYS_W, ALLOC), ('iso', None, ALLOC * g_mean)):
        rn = simulate(Lr, Sr, gw, None, alloc=alloc, kill=False); s = path_stats(rn['curve'], rn['wk'], nW)
        h = 0; t = 0; h22 = 0
        for s_ in range(0, nW - 11, 4):
            kk = simulate(Lr, Sr, gw, None, alloc=alloc, w_from=s_, w_to=s_ + 12)['killed_at'] is not None
            h += kk; t += 1; h22 += kk and YEAR[s_] == 2022
        res[k]['k12'].append(h / t); res[k]['maxdd'].append(s['maxdd_pct']); res[k]['sharpe'].append(s['sharpe']); res[k]['k22'].append(h22)
md.append('| wariant | P(kill 12 t.) śr. | maxDD śr. % | Sharpe netto śr. | śr. liczba okien 12-t. z killem startujących w 2022 (z ~10 badanych) |\n|---|---|---|---|---|')
rr = {}
for k, lab in (('bez', 'bez bramki, ALLOC 0,24'), ('gate', 'bramka hist. D0, ALLOC 0,24'), ('iso', 'stały ALLOC 0,178 (iso-gross)')):
    d = {kk: np.array(v) for kk, v in res[k].items()}; rr[k] = {kk: float(v.mean()) for kk, v in d.items()}
    md.append(f"| {lab} | {100*d['k12'].mean():.1f}% | {d['maxdd'].mean():.1f} | {d['sharpe'].mean():.2f} | {d['k22'].mean():.2f} |")
dk = np.array(res['gate']['k12']) - np.array(res['iso']['k12']); dd_ = np.array(res['gate']['maxdd']) - np.array(res['iso']['maxdd']); ds = np.array(res['gate']['sharpe']) - np.array(res['iso']['sharpe'])
md.append(f'\nSparowane (bramka − iso-gross): ΔP(kill 12 t.) {100*dk.mean():+.1f} pkt (bramka niżej w {100*(dk<0).mean():.0f}%, równe {100*(dk==0).mean():.0f}%); ΔmaxDD {dd_.mean():+.1f} pkt (bramka niżej w {100*(dd_<0).mean():.0f}%); ΔSharpe {ds.mean():+.3f} (bramka wyżej w {100*(ds>0).mean():.0f}%).\n')
out['random_iso'] = dict(res=rr, d_k12=float(dk.mean()), share_lower=float((dk<0).mean()), d_maxdd=float(dd_.mean()), share_dd_lower=float((dd_<0).mean()), d_sharpe=float(ds.mean()), share_sh_higher=float((ds>0).mean()))

# σ kapitału mom6M wg roku i udział w kill: gdzie siedzi ryzyko kill
md.append('\n## σ tygodniowa zwrotu kapitału mom6M (1,2×spread) wg roku i stanu — gdzie jest ryzyko kill\n')
md.append('| rok | okna | śr. % | σ % | najgorszy % | tyg. P0 | σ w P0 | tyg. P1/P2 | σ w P1/P2 |\n|---|---|---|---|---|---|---|---|---|')
for y in sorted(set(YEAR)):
    m = YEAR == y; x = cap_wk[m]; m0 = m & (hs == 0); m12 = m & (hs > 0)
    s0 = cap_wk[m0].std(ddof=1) if m0.sum() > 1 else float('nan'); s12 = cap_wk[m12].std(ddof=1) if m12.sum() > 1 else float('nan')
    md.append(f'| {y} | {m.sum()} | {x.mean():.2f} | {x.std(ddof=1):.2f} | {x.min():.1f} | {m0.sum()} | {s0:.2f} | {m12.sum()} | {s12:.2f} |')

json.dump(out, open(OUTJ, 'w'), indent=1, ensure_ascii=False, default=str)
open(OUT, 'w').write('\n'.join(md) + '\n'); print('\n'.join(md))
