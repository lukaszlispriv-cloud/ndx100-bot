"""Uzupełnienie: wrażliwość wariantu point-in-time (PIT) na przybliżone daty członkostwa (±90 dni),
kotwice dnia tygodnia na PIT, koncentracja nazw w PIT. Importuje harness z weryfikacja_C1.py (bez ponownego biegu głównego)."""
import importlib.util, sys, json, math
import numpy as np, pandas as pd
spec = importlib.util.spec_from_file_location('w', '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C1.py')
# zamiast importu (długi bieg) wczytujemy definicje przez exec do nagłówka 'results = {}'
src = open(spec.origin).read().split('# ---------------------------------------------------------------------------- bieg')[0]
ns = {}; exec(src, ns)
backtest, metrics, build, windows_anchor, block_bootstrap = ns['backtest'], ns['metrics'], ns['build'], ns['windows_anchor'], ns['block_bootstrap']
cands_all, dropped_df, JOIN_APPROX, JOIN_DROPPED, LEAVE_APPROX, dates = ns['cands_all'], ns['dropped_df'], ns['JOIN_APPROX'], ns['JOIN_DROPPED'], ns['LEAVE_APPROX'], ns['dates']
P_ext, names_ext = build(cands_all, dropped_df)
D0, D5 = windows_anchor(None)
join_all = dict(JOIN_APPROX); join_all.update(JOIN_DROPPED)
def shift(d, days): return {k: str((pd.Timestamp(v) + pd.Timedelta(days=days)).date()) for k, v in d.items()}
out = {}; md = ['# PIT — wrażliwość na daty członkostwa, kotwice, koncentracja\n', '| wariant | n | brutto | σ | t | netto | t netto | L | S |', '|---|---|---|---|---|---|---|---|---|']
def line(lbl, r):
    mg = metrics(r['spread']); mn = metrics(r['net']); ml = metrics(r['long']); ms = metrics(r['short'])
    out[lbl] = dict(n=mg['n'], brutto=round(mg['mean'],3), sigma=round(mg['sigma'],3), t=round(mg['t'],3), netto=round(mn['mean'],3), t_netto=round(mn['t'],3), L=round(ml['mean'],3), S=round(ms['mean'],3))
    md.append(f"| {lbl} | {mg['n']} | {mg['mean']:.2f} | {mg['sigma']:.2f} | {mg['t']:.2f} | {mn['mean']:.2f} | {mn['t']:.2f} | {ml['mean']:.2f} | {ms['mean']:.2f} |")
base = backtest(P_ext, names_ext, D0, D5, join=join_all, leave=LEAVE_APPROX); line('PIT (daty bazowe)', base)
for dj in (-90, 90):
    for dl in (-90, 90):
        r = backtest(P_ext, names_ext, D0, D5, join=shift(join_all, dj), leave=shift(LEAVE_APPROX, dl))
        line(f'PIT join{dj:+d}d leave{dl:+d}d', r)
# tylko usunięcia bez dołączeń (dzisiejsze nazwy od początku) i tylko dołączenia (usunięte do końca)
line('PIT tylko leave (dzisiejsze nazwy bez dat dołączenia)', backtest(P_ext, names_ext, D0, D5, leave=LEAVE_APPROX))
line('PIT tylko join (usunięte zostają do końca danych)', backtest(P_ext, names_ext, D0, D5, join=join_all))
# kotwice dnia tygodnia na PIT
for wd, lbl in [(0,'pon'),(1,'wt'),(2,'śr'),(3,'czw')]:
    d0, d5 = windows_anchor(wd)
    line(f'PIT kotwica {lbl}', backtest(P_ext, names_ext, d0, d5, join=join_all, leave=LEAVE_APPROX))
# koncentracja nazw w PIT
contrib = {}
for w in range(len(D0)):
    if base['longs'][w] is None: continue
    for i in base['longs'][w]:
        c = contrib.setdefault(names_ext[i], [0.0, 0, 0]); c[0] += base['EX'][w, i]*100/5; c[1] += 1
    for i in base['shorts'][w]:
        c = contrib.setdefault(names_ext[i], [0.0, 0, 0]); c[0] += -base['EX'][w, i]*100/5; c[2] += 1
cs = sorted(contrib.items(), key=lambda kv: -kv[1][0])
md.append('\nNajwięksi dawcy PIT (pp skumulowane; okna long/short): ' + ', '.join(f"{k} {v[0]:.1f} ({v[1]}L/{v[2]}S)" for k, v in cs[:12]))
md.append('Najwięksi biorcy PIT: ' + ', '.join(f"{k} {v[0]:.1f} ({v[1]}L/{v[2]}S)" for k, v in cs[-8:]))
out['top'] = [(k, round(v[0],1), v[1], v[2]) for k, v in cs[:12]]; out['bottom'] = [(k, round(v[0],1), v[1], v[2]) for k, v in cs[-8:]]
tot = np.nansum(base['spread'])
md.append(f"Suma spreadu PIT {tot:.1f} pp; udział 5 największych dawców {sum(v[0] for k,v in cs[:5])/tot*100:.0f}%.")
# leave-5-out na PIT vs losowe
names_top5 = [k for k, v in cs[:5]]
mask = np.array([n not in names_top5 for n in names_ext])
line('PIT bez 5 największych dawców', backtest(P_ext, names_ext, D0, D5, join=join_all, leave=LEAVE_APPROX, mask_names=mask))
# najczęstsze shorty z usuniętych
sh = sorted(((k, v[2]) for k, v in contrib.items() if k in dropped_df.columns), key=lambda kv: -kv[1])[:10]
md.append('Najczęstsze shorty spośród usuniętych (okna): ' + ', '.join(f"{k} {n}" for k, n in sh))
out['shorts_dropped_top'] = sh
open('/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C1_pit_robust.md','w').write('\n'.join(md)+'\n')
json.dump(out, open('/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C1_pit_robust.json','w'), indent=1, ensure_ascii=False)
print('\n'.join(md))
