"""Dekompozycja wyników koszyków W1–W7 (NDX100).

Uruchomienie: python3 -I dekompozycja.py  (z katalogu analiza/)
Wyjście: tabele markdown na stdout + dekompozycja_wyniki.json
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_dekomp import *

dates, px = load_closes()
di = {d: i for i, d in enumerate(dates)}
R = {c: rets(px[c]) for c in px}

# ---------------------------------------------------------------- koszyki
# Źródła: W1–W3 tabele rozliczeń w reports/raport-2026-W2..W4.html; W4–W7 koszyki_historia.json.
# Dywidendy (ex-date w oknie) wg raportów: PEP 1,48 (4.09), NVDA 0,25 (10.09), AVGO 0,65 (21.09),
# CMCSA 0,33 (7.10), MU 0,15 (14.10). Korekta symetryczna: zwrot całkowity spółki = (P_end + div)/P_d0 - 1.
WEEKS = [
    dict(w='W1', d0='2026-08-26', end='2026-08-28', n=2,
         long=['MU', 'LITE', 'CEG', 'AMD', 'MSFT'], short=['INTU', 'WDAY', 'APP', 'TSLA', 'CMCSA'],
         div={}, hist=-4.06),
    dict(w='W2', d0='2026-08-28', end='2026-09-04', n=5,
         long=['MU', 'NVDA', 'MSFT', 'AMD', 'CEG'], short=['INTU', 'APP', 'TSLA', 'CMCSA', 'PEP'],
         div={'PEP': (1.48, '2026-09-04')}, hist=6.19),
    dict(w='W3', d0='2026-09-04', end='2026-09-11', n=4,
         long=['MU', 'NVDA', 'AMD', 'AVGO', 'STX'], short=['TSLA', 'INTU', 'SBUX', 'APP', 'CMCSA'],
         div={'NVDA': (0.25, '2026-09-10')}, hist=1.44),
    dict(w='W4', d0='2026-09-11', end='2026-09-28', n=11,
         long=['MU', 'AMD', 'AVGO', 'MRVL', 'LITE'], short=['INTU', 'SBUX', 'CMCSA', 'APP', 'ADSK'],
         div={'AVGO': (0.65, '2026-09-21')}, hist=13.85),
    dict(w='W5', d0='2026-09-28', end='2026-10-02', n=4,
         long=['MU', 'AMD', 'ALAB', 'STX', 'TER'], short=['SBUX', 'NFLX', 'PEP', 'CMCSA', 'APP'],
         div={}, hist=5.95),
    dict(w='W6', d0='2026-10-02', end='2026-10-09', n=5,
         long=['MU', 'LITE', 'TER', 'AMAT', 'AMD'], short=['APP', 'NFLX', 'PAYX', 'CMCSA', 'SBUX'],
         div={'CMCSA': (0.33, '2026-10-07')}, hist=-5.89),
    dict(w='W7', d0='2026-10-09', end='2026-10-16', n=5,
         long=['MU', 'LITE', 'MRVL', 'PANW', 'CSCO'], short=['CMCSA', 'SBUX', 'PEP', 'TMUS', 'APP'],
         div={'MU': (0.15, '2026-10-14')}, hist=-21.15),
]

# Bloki (taksonomia własna, potwierdzona kolumną industry w data/tv-screen-2026-W8.json)
BLOK = {
    # półprzewodniki / AI-hardware (pamięć, GPU/ASIC, optyka, WFE/test, storage)
    'MU': 'SEMI', 'AMD': 'SEMI', 'NVDA': 'SEMI', 'AVGO': 'SEMI', 'MRVL': 'SEMI', 'LITE': 'SEMI',
    'ALAB': 'SEMI', 'STX': 'SEMI', 'TER': 'SEMI', 'AMAT': 'SEMI',
    # sieci / cyber (AI-adjacent, nie półprzewodniki)
    'CSCO': 'SIECI', 'PANW': 'CYBER',
    # software (ofiary substytucji / drogie)
    'INTU': 'SOFT', 'WDAY': 'SOFT', 'APP': 'SOFT', 'ADSK': 'SOFT', 'MSFT': 'MEGA',
    # defensywy: staples / telekomy / media / usługi
    'PEP': 'DEF', 'CMCSA': 'DEF', 'SBUX': 'DEF', 'TMUS': 'DEF', 'PAYX': 'DEF', 'NFLX': 'MEDIA',
    'TSLA': 'AUTO', 'CEG': 'UTIL',
}


def price(t, d):
    return px[t][di[d]]


def ret(t, d0, d1, div=None):
    p0, p1 = price(t, d0), price(t, d1)
    if div and di[d0] < di[div[1]] <= di[d1]:
        p1 = p1 + div[0]
    return p1 / p0 - 1


def factor_window(d0, d1):
    rn = ret('^NDX', d0, d1)
    rs = ret('^SOX', d0, d1)
    rq = ret('QQQ', d0, d1)
    rdef = mean([ret('XLP', d0, d1), ret('XLU', d0, d1), ret('XLV', d0, d1)])
    return dict(ndx=rn, sox_m_ndx=rs - rn, def_m_qqq=rdef - rq, sox=rs, qqq=rq, defn=rdef)


def loadings(t, d0, nses=250):
    """Ładunki czynnikowe z 250 sesji dziennych zwrotów kończących się na D0 (włącznie)."""
    i1 = di[d0]
    i0 = i1 - nses + 1
    idx = range(i0, i1 + 1)
    y = [R[t][i] for i in idx]
    f1 = [R['^NDX'][i] for i in idx]
    f2 = [R['^SOX'][i] - R['^NDX'][i] if (R['^SOX'][i] is not None and R['^NDX'][i] is not None) else None for i in idx]
    f3 = []
    for i in idx:
        vals = [R['XLP'][i], R['XLU'][i], R['XLV'][i], R['QQQ'][i]]
        f3.append(mean(vals[:3]) - vals[3] if all(v is not None for v in vals) else None)
    m1 = ols(y, [[a] for a in f1])
    m3 = ols(y, [[a, b, c] for a, b, c in zip(f1, f2, f3)])
    return dict(beta1=m1['beta'][1], se_beta1=m1['se'][1], r2_1=m1['r2'],
                b_ndx=m3['beta'][1], b_sox=m3['beta'][2], b_def=m3['beta'][3],
                se_sox=m3['se'][2], se_def=m3['se'][3], r2_3=m3['r2'], n=m3['n'],
                sigma_d=sd(y))


out = {'weeks': []}
legs_all = []
print('# 1. Rozliczenie per noga (od D0, vs ^NDX) — zgodność z history/raportami\n')
for W in WEEKS:
    d0, d1 = W['d0'], W['end']
    F = factor_window(d0, d1)
    rows = []
    for side, lst in (('L', W['long']), ('S', W['short'])):
        for t in lst:
            rr = ret(t, d0, d1, W['div'].get(t))
            pos = (rr - F['ndx']) * (1 if side == 'L' else -1)
            L = loadings(t, d0)
            # składowe pozycji względem ^NDX: (b_ndx-1)*R_ndx + b_sox*F_sox + b_def*F_def + reszta
            sgn = 1 if side == 'L' else -1
            c_beta = sgn * (L['b_ndx'] - 1) * F['ndx']
            c_sox = sgn * L['b_sox'] * F['sox_m_ndx']
            c_def = sgn * L['b_def'] * F['def_m_qqq']
            c_res = pos - c_beta - c_sox - c_def
            rows.append(dict(w=W['w'], t=t, side=side, blok=BLOK[t], ret=rr, pos=pos, hit=pos > 0,
                             beta1=L['beta1'], b_ndx=L['b_ndx'], b_sox=L['b_sox'], b_def=L['b_def'],
                             se_sox=L['se_sox'], r2_3=L['r2_3'], sigma_d=L['sigma_d'],
                             c_beta=c_beta, c_sox=c_sox, c_def=c_def, c_res=c_res))
    legs_all += rows
    longs = [r for r in rows if r['side'] == 'L']
    shorts = [r for r in rows if r['side'] == 'S']
    spread = mean([r['pos'] for r in longs]) + mean([r['pos'] for r in shorts])
    hit = sum(r['hit'] for r in rows)
    dec = {k: sum(r[k] for r in longs) / 5 + sum(r[k] for r in shorts) / 5 for k in ('c_beta', 'c_sox', 'c_def', 'c_res')}
    beta_net = mean([r['b_ndx'] for r in longs]) - mean([r['b_ndx'] for r in shorts])
    beta1_net = mean([r['beta1'] for r in longs]) - mean([r['beta1'] for r in shorts])
    sox_net = mean([r['b_sox'] for r in longs]) - mean([r['b_sox'] for r in shorts])
    def_net = mean([r['b_def'] for r in longs]) - mean([r['b_def'] for r in shorts])
    W.update(spread=spread, hit=hit, F=F, dec=dec, beta_net=beta_net, beta1_net=beta1_net,
             sox_net=sox_net, def_net=def_net, rows=rows,
             n_semi_long=sum(1 for r in longs if r['blok'] == 'SEMI'),
             n_def_short=sum(1 for r in shorts if r['blok'] in ('DEF', 'MEDIA')),
             n_soft_short=sum(1 for r in shorts if r['blok'] == 'SOFT'))
    print(f"## {W['w']}  D0={d0} → {d1} (n={W['n']})  ^NDX {F['ndx']*100:+.2f}%  SOX−NDX {F['sox_m_ndx']*100:+.2f} p.p.  DEF−QQQ {F['def_m_qqq']*100:+.2f} p.p.")
    print('| noga | kier. | blok | zwrot kursu | pozycja vs NDX | β(1f) | b_NDX | b_SOX−NDX | b_DEF | R²(3f) | skł. beta | skł. SOX | skł. DEF | reszta |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        print(f"| {r['t']} | {r['side']} | {r['blok']} | {r['ret']*100:+.2f}% | {r['pos']*100:+.2f} | {r['beta1']:.2f} | {r['b_ndx']:.2f} | {r['b_sox']:.2f} | {r['b_def']:.2f} | {r['r2_3']:.2f} | {r['c_beta']*100:+.2f} | {r['c_sox']*100:+.2f} | {r['c_def']*100:+.2f} | {r['c_res']*100:+.2f} |")
    print(f"\nspread = {spread*100:+.2f} p.p. (history: {W['hist']:+.2f}; Δ {spread*100-W['hist']:+.2f})  hit {hit}/10  "
          f"β_net(3f) {beta_net:+.2f}  b_SOX_net {sox_net:+.2f}  b_DEF_net {def_net:+.2f}")
    c_beta1 = beta1_net * F['ndx']
    W['c_beta1'] = c_beta1
    print(f"dekompozycja 3f: beta {dec['c_beta']*100:+.2f} + SOX {dec['c_sox']*100:+.2f} + DEF {dec['c_def']*100:+.2f} + reszta {dec['c_res']*100:+.2f}")
    print(f"wariant 1f: β1_net {beta1_net:+.2f} × ^NDX {F['ndx']*100:+.2f}% = {c_beta1*100:+.2f} p.p.; reszta po samej becie {(spread - c_beta1)*100:+.2f}\n")

# ---------------------------------------------------------------- 5-sesyjna normalizacja
print('\n# 2. Okna znormalizowane do 5 sesji (na papierze, od D0)\n')
norm = []
for W in WEEKS:
    i0 = di[W['d0']]
    d5 = dates[i0 + 5] if i0 + 5 < len(dates) else None
    if W['w'] == 'W3':   # 4 sesje przez Labor Day — D+4 = 11.09, D+5 wypada 14.09 (po rotacji)
        pass
    d5 = dates[min(i0 + 5, len(dates) - 1)]
    F = factor_window(W['d0'], d5)
    pos = []
    for side, lst in (('L', W['long']), ('S', W['short'])):
        for t in lst:
            dv = W['div'].get(t)
            rr = ret(t, W['d0'], d5, dv)
            pos.append(((rr - F['ndx']) * (1 if side == 'L' else -1), side))
    sp5 = mean([p for p, s in pos if s == 'L']) + mean([p for p, s in pos if s == 'S'])
    hit5 = sum(1 for p, s in pos if p > 0)
    nact = di[d5] - i0
    W['spread5'] = sp5; W['end5'] = d5; W['hit5'] = hit5
    W['spread_per_ses5'] = W['spread'] / W['n'] * 5
    norm.append(W)
    print(f"| {W['w']} | D0 {W['d0']} | koniec faktyczny {W['end']} (n={W['n']}) {W['spread']*100:+.2f} | D+5 {d5} (n={nact}) {sp5*100:+.2f} hit {hit5}/10 | per-sesja×5 {W['spread_per_ses5']*100:+.2f} |")

# ---------------------------------------------------------------- statystyki
print('\n# 3. Statystyki (t, Wilson)\n')
def tstats(label, xs):
    n = len(xs); m = mean(xs); s = sd(xs); t = m / (s / math.sqrt(n)) if s else None
    p = t_pvalue_two_sided(t, n - 1)
    print(f"| {label} | n={n} | śr. {m*100:+.2f} | sd {s*100:.2f} | t = {t:.2f} | p ≈ {p:.2f} | suma {sum(xs)*100:+.2f} |")
    return dict(label=label, n=n, mean=m, sd=s, t=t, p=p, sum=sum(xs))
print('| seria | n | średnia p.p. | sd | t | p (dwustr.) | suma |')
print('|---|---|---|---|---|---|---|')
S = {}
S['raw'] = tstats('surowa (okna 2/5/4/11/4/5/5)', [W['spread'] for W in WEEKS])
S['n5'] = tstats('D0→D+5 na papierze (wszystkie 7)', [W['spread5'] for W in WEEKS])
S['n5_full'] = tstats('tylko pełne 5-ses. okna faktyczne (W2,W6,W7)', [W['spread'] for W in WEEKS if W['n'] == 5])
S['perses'] = tstats('per-sesja ×5 (surowa/n×5)', [W['spread_per_ses5'] for W in WEEKS])
S['n5_exW7'] = tstats('D0→D+5 bez W7', [W['spread5'] for W in WEEKS if W['w'] != 'W7'])
S['long'] = tstats('tylko strona LONG (śr. poz. L, okna faktyczne)', [mean([r['pos'] for r in W['rows'] if r['side'] == 'L']) for W in WEEKS])
S['short'] = tstats('tylko strona SHORT (śr. poz. S, okna faktyczne)', [mean([r['pos'] for r in W['rows'] if r['side'] == 'S']) for W in WEEKS])
S['resid'] = tstats('reszta idiosynkratyczna spreadu (3f)', [W['dec']['c_res'] for W in WEEKS])
S['factor'] = tstats('część czynnikowa spreadu (beta+SOX+DEF)', [W['dec']['c_beta'] + W['dec']['c_sox'] + W['dec']['c_def'] for W in WEEKS])

print('\n## Hit rate (Wilson 95%)')
tot_hit = sum(W['hit'] for W in WEEKS); tot_n = 10 * len(WEEKS)
hl = sum(1 for r in legs_all if r['side'] == 'L' and r['hit']); hs = sum(1 for r in legs_all if r['side'] == 'S' and r['hit'])
for lab, k, n in (('wszystkie nogi', tot_hit, tot_n), ('LONG', hl, 35), ('SHORT', hs, 35),
                  ('bez W7', tot_hit - WEEKS[6]['hit'], 60), ('W1–W6 LONG', hl - sum(1 for r in WEEKS[6]['rows'] if r['side']=='L' and r['hit']), 30),
                  ('W1–W6 SHORT', hs - sum(1 for r in WEEKS[6]['rows'] if r['side']=='S' and r['hit']), 30)):
    lo, hi = wilson(k, n)
    print(f"| {lab} | {k}/{n} = {k/n*100:.1f}% | Wilson [{lo*100:.1f}%, {hi*100:.1f}%] | p dwumianowy vs 50% = {binom_two_sided_p(k, n):.2f} |")
# hit rate po odjęciu części czynnikowej: trafienie reszty
hit_res = sum(1 for r in legs_all if r['c_res'] > 0)
lo, hi = wilson(hit_res, len(legs_all))
print(f"| trafienie RESZTY (po odjęciu beta/SOX/DEF) | {hit_res}/{len(legs_all)} = {hit_res/len(legs_all)*100:.1f}% | Wilson [{lo*100:.1f}%, {hi*100:.1f}%] | p = {binom_two_sided_p(hit_res, len(legs_all)):.2f} |")
# tygodnie z dodatnim spreadem
wk_pos = sum(1 for W in WEEKS if W['spread'] > 0)
print(f"\nTygodnie z dodatnim spreadem: {wk_pos}/7; p(≥{wk_pos} z 7 przy 50%) = {sum(math.comb(7,k) for k in range(wk_pos,8))/128:.2f}")

# ---------------------------------------------------------------- udział wariancji (tygodniowo, n=7)
print('\n# 4. Udział wariancji spreadu: czynniki vs selekcja\n')
sp = [W['spread'] for W in WEEKS]
fac = [W['dec']['c_beta'] + W['dec']['c_sox'] + W['dec']['c_def'] for W in WEEKS]
res = [W['dec']['c_res'] for W in WEEKS]
vs, vf, vr = sd(sp) ** 2, sd(fac) ** 2, sd(res) ** 2
cov_fr = corr(fac, res) * sd(fac) * sd(res)
print(f"n=7 tygodni: var(spread)={vs*1e4:.1f}, var(czynniki)={vf*1e4:.1f} ({vf/vs*100:.0f}%), var(reszta)={vr*1e4:.1f} ({vr/vs*100:.0f}%), 2cov={2*cov_fr*1e4:.1f} ({2*cov_fr/vs*100:.0f}%); corr(czynniki,spread)={corr(fac,sp):.2f}, corr(reszta,spread)={corr(res,sp):.2f}")
for k, lab in (('c_beta', 'beta×NDX'), ('c_sox', 'SOX−NDX'), ('c_def', 'DEF−QQQ')):
    xs = [W['dec'][k] for W in WEEKS]
    print(f"  składnik {lab}: śr. {mean(xs)*100:+.2f} p.p., sd {sd(xs)*100:.2f}, corr ze spreadem {corr(xs, sp):+.2f}")
# regresja tygodniowa spreadu na zrealizowane czynniki (n=7, k=3 → ostrożnie)
y = sp
X1 = [[W['F']['ndx']] for W in WEEKS]
X2 = [[W['F']['ndx'], W['F']['sox_m_ndx']] for W in WEEKS]
X3 = [[W['F']['ndx'], W['F']['sox_m_ndx'], W['F']['def_m_qqq']] for W in WEEKS]
for lab, X in (('NDX', X1), ('NDX+SOX−NDX', X2), ('NDX+SOX−NDX+DEF', X3)):
    # ols wymaga n>=10 — tu n=7, liczymy ręcznie prostszą wersją
    data = list(zip(y, X)); n = len(data); k = len(X[0]) + 1
    Xm = [[1.0] + list(x) for _, x in data]
    XtX = [[sum(Xm[r][i] * Xm[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(Xm[r][i] * y[r] for r in range(n)) for i in range(k)]
    b = solve(XtX, Xty)
    fit = [sum(bb * xx for bb, xx in zip(b, row)) for row in Xm]
    ssr = sum((yy - f) ** 2 for yy, f in zip(y, fit)); sst = sum((yy - mean(y)) ** 2 for yy in y)
    r2 = 1 - ssr / sst; adj = 1 - (1 - r2) * (n - 1) / (n - k)
    print(f"  regresja tygodniowa spread ~ {lab}: R² {r2:.2f} (adj {adj:.2f}), współczynniki {[round(v, 2) for v in b[1:]]} (n=7, k={k} — ilustracja, nie dowód)")

# ---------------------------------------------------------------- udział wariancji — dzienne serie koszyków (pooled w oknie i 250 sesji przed D0)
print('\n## 4b. Dzienna seria spreadu koszyka: w oknie (pooled) i na 250 sesjach PRZED D0 (konstrukcja koszyka)\n')
def daily_spread(W, i):
    L = [R[t][i] for t in W['long']]; Sh = [R[t][i] for t in W['short']]
    if any(v is None for v in L + Sh): return None
    return mean(L) - mean(Sh)
pool_y, pool_X1, pool_X2, pool_X3 = [], [], [], []
pre_r2 = []
print('| koszyk | R² NDX (250 przed D0) | R² NDX+SOX | R² NDX+SOX+DEF | β_spread | b_SOX | b_DEF | σ_d spreadu | sd 5-ses. spreadu (√5) | w oknie: dni, R² 3f |')
print('|---|---|---|---|---|---|---|---|---|---|')
for W in WEEKS:
    i1 = di[W['d0']]; idx = list(range(i1 - 249, i1 + 1))
    y = [daily_spread(W, i) for i in idx]
    f1 = [R['^NDX'][i] for i in idx]
    f2 = [R['^SOX'][i] - R['^NDX'][i] for i in idx]
    f3 = [mean([R['XLP'][i], R['XLU'][i], R['XLV'][i]]) - R['QQQ'][i] if all(R[c][i] is not None for c in ('XLP','XLU','XLV','QQQ')) else None for i in idx]
    m1 = ols(y, [[a] for a in f1]); m2 = ols(y, [[a, b] for a, b in zip(f1, f2)]); m3 = ols(y, [[a, b, c] for a, b, c in zip(f1, f2, f3)])
    sig = sd(y)
    # w oknie
    widx = list(range(di[W['d0']] + 1, di[W['end']] + 1))
    wy = [daily_spread(W, i) for i in widx]
    wX3 = [[R['^NDX'][i], R['^SOX'][i] - R['^NDX'][i], (mean([R['XLP'][i], R['XLU'][i], R['XLV'][i]]) - R['QQQ'][i]) if all(R[c][i] is not None for c in ('XLP','XLU','XLV','QQQ')) else None] for i in widx]
    keep = [j for j in range(len(wy)) if wy[j] is not None and all(v is not None for v in wX3[j])]
    wy = [wy[j] for j in keep]; wX3 = [wX3[j] for j in keep]
    pool_y += wy; pool_X3 += wX3; pool_X1 += [[x[0]] for x in wX3]; pool_X2 += [x[:2] for x in wX3]
    # R² w oknie z własnych ładunków (250 przed D0): 1 - var(resid)/var(y)
    fitw = [m3['beta'][0] + sum(b * x for b, x in zip(m3['beta'][1:], row)) for row in wX3]
    ssr = sum((a - b) ** 2 for a, b in zip(wy, fitw)); sst = sum((a - mean(wy)) ** 2 for a in wy)
    r2w = 1 - ssr / sst if sst > 0 else None
    pre_r2.append(dict(w=W['w'], r2_1=m1['r2'], r2_2=m2['r2'], r2_3=m3['r2'], beta=m3['beta'][1], bsox=m3['beta'][2], bdef=m3['beta'][3], sigma=sig, r2_win=r2w))
    W['pre'] = pre_r2[-1]
    print(f"| {W['w']} | {m1['r2']:.2f} | {m2['r2']:.2f} | {m3['r2']:.2f} | {m3['beta'][1]:.2f} | {m3['beta'][2]:.2f} | {m3['beta'][3]:.2f} | {sig*100:.2f}% | {sig*100*math.sqrt(5):.2f} p.p. | {len(wy)}, {r2w if r2w is None else round(r2w,2)} |")
mp1 = ols(pool_y, pool_X1); mp2 = ols(pool_y, pool_X2); mp3 = ols(pool_y, pool_X3)
print(f"\nPooled dni w oknach W1–W7 (n={mp3['n']}): R² NDX {mp1['r2']:.2f}; NDX+SOX−NDX {mp2['r2']:.2f}; +DEF {mp3['r2']:.2f}; współcz. 3f: β {mp3['beta'][1]:.2f} (SE {mp3['se'][1]:.2f}), b_SOX {mp3['beta'][2]:.2f} (SE {mp3['se'][2]:.2f}), b_DEF {mp3['beta'][3]:.2f} (SE {mp3['se'][3]:.2f}); α dzienna {mp3['beta'][0]*100:+.3f}% (t {mp3['t'][0]:.2f}); σ reszty {mp3['sigma']*100:.2f}%")
print(f"Pooled: średni dzienny spread {mean(pool_y)*100:+.3f}% , sd {sd(pool_y)*100:.2f}%, t = {mean(pool_y)/(sd(pool_y)/math.sqrt(len(pool_y))):.2f} (n={len(pool_y)} dni)")

# ---------------------------------------------------------------- bloki
print('\n# 5. Koncentracja blokowa a wynik\n')
print('| tydz. | longi SEMI | shorty DEF+MEDIA | shorty SOFT | β_net(3f) | b_SOX_net | spread | SOX−NDX w oknie | skł. SOX | skł. beta |')
print('|---|---|---|---|---|---|---|---|---|---|')
for W in WEEKS:
    print(f"| {W['w']} | {W['n_semi_long']}/5 | {W['n_def_short']}/5 | {W['n_soft_short']}/5 | {W['beta_net']:+.2f} | {W['sox_net']:+.2f} | {W['spread']*100:+.2f} | {W['F']['sox_m_ndx']*100:+.2f} | {W['dec']['c_sox']*100:+.2f} | {W['dec']['c_beta']*100:+.2f} |")
n4 = [W for W in WEEKS if W['n_semi_long'] >= 4]
print(f"\nTygodnie z ≥4 longami SEMI: {len(n4)}/7 ({', '.join(W['w'] for W in n4)}); śr. spread {mean([W['spread'] for W in n4])*100:+.2f} vs pozostałe {mean([W['spread'] for W in WEEKS if W['n_semi_long'] < 4])*100:+.2f}")
n4d = [W for W in WEEKS if W['n_def_short'] >= 4]
print(f"Tygodnie z ≥4 shortami DEF/MEDIA: {len(n4d)}/7 ({', '.join(W['w'] for W in n4d)}); śr. spread {mean([W['spread'] for W in n4d])*100:+.2f} vs pozostałe {mean([W['spread'] for W in WEEKS if W['n_def_short'] < 4])*100:+.2f}")
both = [W for W in WEEKS if W['n_semi_long'] >= 4 and W['n_def_short'] >= 4]
print(f"Oba naraz (≥4 SEMI long i ≥4 DEF short): {len(both)}/7 ({', '.join(W['w'] for W in both)}); śr. spread {mean([W['spread'] for W in both])*100:+.2f}")
print(f"corr(b_SOX_net, spread) = {corr([W['sox_net'] for W in WEEKS], sp):+.2f}; corr(SOX−NDX w oknie, spread) = {corr([W['F']['sox_m_ndx'] for W in WEEKS], sp):+.2f}; corr(^NDX w oknie, spread) = {corr([W['F']['ndx'] for W in WEEKS], sp):+.2f}; corr(DEF−QQQ, spread) = {corr([W['F']['def_m_qqq'] for W in WEEKS], sp):+.2f}")

# ---------------------------------------------------------------- per ticker
print('\n# 6. Wkład per ticker (suma pozycji vs NDX, p.p., okna faktyczne) i reszta idiosynkratyczna\n')
agg = {}
for r in legs_all:
    a = agg.setdefault(r['t'], dict(n=0, pos=0, res=0, hit=0, side=r['side'], blok=r['blok']))
    a['n'] += 1; a['pos'] += r['pos']; a['res'] += r['c_res']; a['hit'] += r['hit']
print('| ticker | kier. | blok | tygodni | suma pozycji p.p. | suma reszty p.p. | trafienia |')
print('|---|---|---|---|---|---|---|')
for t, a in sorted(agg.items(), key=lambda kv: -kv[1]['pos']):
    print(f"| {t} | {a['side']} | {a['blok']} | {a['n']} | {a['pos']*100:+.2f} | {a['res']*100:+.2f} | {a['hit']}/{a['n']} |")

json.dump({'weeks': [{k: v for k, v in W.items() if k != 'rows'} for W in WEEKS], 'legs': legs_all, 'stats': S,
           'pooled': dict(r2_1=mp1['r2'], r2_2=mp2['r2'], r2_3=mp3['r2'], n=mp3['n'])},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dekompozycja_wyniki.json'), 'w'), indent=1, default=str)
