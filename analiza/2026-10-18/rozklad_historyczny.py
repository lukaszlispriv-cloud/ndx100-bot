"""Rozkład historyczny 5-sesyjnych spreadów dla KONSTRUKCJI każdego koszyka (ten sam skład, przesuwane okna)
na 250 i na ~1000 sesjach przed D0 — żeby umiejscowić faktyczny wynik tygodnia (z-score, percentyl).
Plus: udział wariancji 5-sesyjnego spreadu tłumaczony czynnikami (regresja okien nienakładających się).
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_dekomp import *
dates, px = load_closes()
di = {d: i for i, d in enumerate(dates)}
WK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dekompozycja_wyniki.json')))['weeks']

def r5(t, i):
    a, b = px[t][i - 5], px[t][i]
    return b / a - 1 if (a and b) else None

def spread5(W, i):
    L = [r5(t, i) for t in W['long']]; S = [r5(t, i) for t in W['short']]
    if any(v is None for v in L + S): return None
    return mean(L) - mean(S)

print('| koszyk | wynik faktyczny (D+5 na papierze) | 250 sesji przed D0: śr. / sd 5-ses. spreadu | z | percentyl empiryczny (okna nakładające się) | min hist. | ~1000 sesji: sd / z / percentyl / min | R² 3f okien nienakł. (n) |')
print('|---|---|---|---|---|---|---|---|')
for W in WK:
    i1 = di[W['d0']]
    act = W['spread5']
    res = {}
    for span in (250, 1000):
        idx = [i for i in range(max(i1 - span + 1, 5), i1 + 1)]
        xs = [spread5(W, i) for i in idx]; xs = [x for x in xs if x is not None]
        m, s = mean(xs), sd(xs)
        z = (act - m) / s
        pct = sum(1 for x in xs if x <= act) / len(xs) * 100
        res[span] = (m, s, z, pct, min(xs), len(xs))
    # okna nienakładające się co 5 sesji, regresja na czynniki 5-sesyjne
    idx = [i for i in range(i1, max(i1 - 1000, 10), -5)]
    y, X = [], []
    for i in idx:
        sp = spread5(W, i)
        f = [r5('^NDX', i), None, None]
        if sp is None or f[0] is None or r5('^SOX', i) is None or any(r5(c, i) is None for c in ('XLP', 'XLU', 'XLV', 'QQQ')): continue
        f[1] = r5('^SOX', i) - f[0]
        f[2] = mean([r5('XLP', i), r5('XLU', i), r5('XLV', i)]) - r5('QQQ', i)
        y.append(sp); X.append(f)
    m3 = ols(y, X)
    m250, s250, z250, p250, mn250, n250 = res[250]
    m1k, s1k, z1k, p1k, mn1k, n1k = res[1000]
    print(f"| {W['w']} | {act*100:+.2f} | {m250*100:+.2f} / {s250*100:.2f} | {z250:+.2f} | {p250:.1f}% (n={n250}) | {mn250*100:+.2f} | {s1k*100:.2f} / {z1k:+.2f} / {p1k:.1f}% / {mn1k*100:+.2f} | {m3['r2']:.2f} (n={m3['n']}; b_SOX {m3['beta'][2]:.2f}, β {m3['beta'][1]:.2f}) |")

# Pooled: czy historycznie (przed D0) 5-sesyjny spread tych konstrukcji miał dodatnią średnią? (test „czy to po prostu zakład na SOX”)
print('\nŚrednia historyczna 5-ses. spreadu konstrukcji (250 sesji przed D0, okna nakładające się) pokazuje, czy koszyk był „kupnem tego, co rosło”: ')
for W in WK:
    i1 = di[W['d0']]
    xs = [spread5(W, i) for i in range(i1 - 249, i1 + 1)]; xs = [x for x in xs if x is not None]
    # ostatnie 20 sesji przed D0 (momentum 1M konstrukcji)
    xs20 = [spread5(W, i) for i in range(i1 - 19, i1 + 1)]; xs20 = [x for x in xs20 if x is not None]
    def r20(t):
        j = i1 - 20
        while px[t][j] is None: j -= 1
        return px[t][i1] / px[t][j] - 1
    mom20 = sum(r20(t) for t in W['long']) / 5 - sum(r20(t) for t in W['short']) / 5
    W['mom20'] = mom20
    print(f"- {W['w']}: śr. 5-ses. spread rok przed D0 {mean(xs)*100:+.2f} p.p.; ostatnie 20 sesji {mean(xs20)*100:+.2f} p.p.; zwrot konstrukcji L−S w 20 sesjach do D0: {mom20*100:+.2f} p.p.; wynik faktyczny {W['spread']*100:+.2f}")

print(f"\ncorr(momentum 20-ses. konstrukcji, spread faktyczny) = {corr([W['mom20'] for W in WK], [W['spread'] for W in WK]):+.2f} (n=7)")

# średnia korelacja par w LONG i w SHORT (60 sesji przed D0) + korelacja LONG vs SHORT koszyka
print('\n| koszyk | śr. ρ par LONG (60 ses.) | śr. ρ par SHORT | ρ(śr. LONG, śr. SHORT) | efektywna liczba nóg LONG ≈ 5/(1+4ρ) |')
print('|---|---|---|---|---|')
R = {c: rets(px[c]) for c in px}
for W in WK:
    i1 = di[W['d0']]; idx = range(i1 - 59, i1 + 1)
    def pc(lst):
        cs = []
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                c = corr([R[lst[a]][i] for i in idx], [R[lst[b]][i] for i in idx])
                if c is not None: cs.append(c)
        return mean(cs)
    rl, rs = pc(W['long']), pc(W['short'])
    ml = [mean([R[t][i] for t in W['long']]) for i in idx]; ms = [mean([R[t][i] for t in W['short']]) for i in idx]
    print(f"| {W['w']} | {rl:.2f} | {rs:.2f} | {corr(ml, ms):+.2f} | {5/(1+4*rl):.1f} |")

# P(kill switch) przy zerowej przewadze: tygodniowe sd wyniku rachunku = 1,2 × sd 5-ses. spreadu konstrukcji
import random
random.seed(7)
print('\nSymulacja (zero przewagi, rozkład normalny, 20 000 ścieżek): P(obsunięcie od kroczącego szczytu ≥ 25 % w ciągu N tygodni)')
for sdw in (0.07, 0.09, 0.11):
    row = []
    for N in (13, 26, 52):
        hits = 0
        for _ in range(20000):
            eq = 1.0; peak = 1.0; dead = False
            for _ in range(N):
                eq *= 1 + random.gauss(0, sdw * 1.2)
                peak = max(peak, eq)
                if eq <= 0.75 * peak: dead = True; break
            hits += dead
        row.append(f"N={N}: {hits/20000*100:.0f}%")
    print(f"- sd tygodnia spreadu {sdw*100:.0f} p.p. (rachunek {sdw*120:.1f}%): " + ', '.join(row))

