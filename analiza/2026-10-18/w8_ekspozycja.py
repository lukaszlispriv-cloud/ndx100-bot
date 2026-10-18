"""Ekspozycja czynnikowa ex ante koszyka W8 (D0 16.10) — bez wyniku (brak danych), tylko ładunki z 250 sesji."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_dekomp import *
dates, px = load_closes(); di = {d: i for i, d in enumerate(dates)}; R = {c: rets(px[c]) for c in px}
d0 = '2026-10-16'; i1 = di[d0]; idx = range(i1 - 249, i1 + 1)
L = ['GOOGL', 'GILD', 'MSFT', 'QCOM', 'ADP']; S = ['AXON', 'DASH', 'ALNY', 'APP', 'FER']
f1 = [R['^NDX'][i] for i in idx]; f2 = [R['^SOX'][i] - R['^NDX'][i] for i in idx]
f3 = [(mean([R['XLP'][i], R['XLU'][i], R['XLV'][i]]) - R['QQQ'][i]) if all(R[c][i] is not None for c in ('XLP','XLU','XLV','QQQ')) else None for i in idx]
print('| noga | kier. | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | σ_d |'); print('|---|---|---|---|---|---|---|---|')
agg = {'L': [], 'S': []}
for side, lst in (('L', L), ('S', S)):
    for t in lst:
        y = [R[t][i] for i in idx]
        m1 = ols(y, [[a] for a in f1]); m3 = ols(y, [[a, b, c] for a, b, c in zip(f1, f2, f3)])
        agg[side].append((m1['beta'][1], m3['beta'][1], m3['beta'][2], m3['beta'][3]))
        print(f"| {t} | {side} | {m1['beta'][1]:.2f} | {m3['beta'][1]:.2f} | {m3['beta'][2]:.2f} | {m3['beta'][3]:.2f} | {m3['r2']:.2f} | {sd(y)*100:.2f}% |")
net = [mean([a[k] for a in agg['L']]) - mean([a[k] for a in agg['S']]) for k in range(4)]
print(f"\nW8 netto (L−S): β1 {net[0]:+.2f}, b_NDX {net[1]:+.2f}, b_SOX−NDX {net[2]:+.2f}, b_DEF {net[3]:+.2f}")
sp = [mean([R[t][i] for t in L]) - mean([R[t][i] for t in S]) for i in idx]
m3 = ols(sp, [[a, b, c] for a, b, c in zip(f1, f2, f3)])
print(f"spread dzienny konstrukcji W8, 250 sesji: σ_d {sd(sp)*100:.2f}% (5-ses. ≈ {sd(sp)*100*math.sqrt(5):.2f} p.p.), R² 3f {m3['r2']:.2f}, β {m3['beta'][1]:+.2f}, b_SOX {m3['beta'][2]:+.2f}, b_DEF {m3['beta'][3]:+.2f}; śr. 5-ses. historyczny {mean(sp)*5*100:+.2f} p.p.")
def pc(lst):
    cs = []
    for a in range(len(lst)):
        for b in range(a + 1, len(lst)):
            cs.append(corr([R[lst[a]][i] for i in range(i1-59,i1+1)], [R[lst[b]][i] for i in range(i1-59,i1+1)]))
    return mean(cs)
print(f"śr. ρ par LONG (60 ses.) {pc(L):.2f}, SHORT {pc(S):.2f}")
