"""(a) Test panelowy: czy wysoki 20-sesyjny zwrot L−S konstrukcji koszyka zapowiada niższy spread w kolejnych 5 sesjach?
    – na poziomie konstrukcji (7 koszyków × okna nienakładające się z ~1000 sesji),
    – na poziomie uniwersum (103 spółki, zwrot relatywny vs ^NDX; decyle 20-sesyjnego zwrotu relatywnego → 5-ses. forward).
(b) Reszty idiosynkratyczne per strona i per blok (z dekompozycja_wyniki.json)."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_dekomp import *
dates, px = load_closes(); di = {d: i for i, d in enumerate(dates)}
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dekompozycja_wyniki.json')))
WK, LEGS = D['weeks'], D['legs']

def rr(t, i0, i1):
    a, b = px[t][i0], px[t][i1]
    return b / a - 1 if (a and b) else None

print('# (a1) Konstrukcje koszyków: spread 5-ses. forward vs zwrot L−S 20 sesji wstecz (okna nienakładające się co 5 sesji, ~1000 sesji przed D0)\n')
print('| koszyk | n okien | corr(mom20, fwd5) | slope (p.p. fwd na 10 p.p. mom) | t | śr. fwd5 gdy mom20 > +20 p.p. (n) | śr. fwd5 pozostałe |')
print('|---|---|---|---|---|---|---|')
allx, ally = [], []
for W in WK:
    i1 = di[W['d0']]
    xs, ys = [], []
    for i in range(i1 - 5, max(i1 - 1005, 25), -5):
        m = [rr(t, i - 20, i) for t in W['long'] + W['short']]
        f = [rr(t, i, i + 5) for t in W['long'] + W['short']]
        if any(v is None for v in m + f): continue
        mom = mean(m[:5]) - mean(m[5:]); fwd = mean(f[:5]) - mean(f[5:])
        xs.append(mom); ys.append(fwd)
    m1 = ols(ys, [[x] for x in xs])
    hi = [y for x, y in zip(xs, ys) if x > 0.20]; lo = [y for x, y in zip(xs, ys) if x <= 0.20]
    allx += xs; ally += ys
    print(f"| {W['w']} | {len(xs)} | {corr(xs, ys):+.2f} | {m1['beta'][1]*10:+.2f} | {m1['t'][1]:+.2f} | {mean(hi)*100 if hi else float('nan'):+.2f} ({len(hi)}) | {mean(lo)*100:+.2f} |")
m = ols(ally, [[x] for x in allx])
hi = [y for x, y in zip(allx, ally) if x > 0.20]; lo = [y for x, y in zip(allx, ally) if x <= 0.20]
print(f"\nPooled 7 konstrukcji (n={len(allx)}; obserwacje skorelowane między koszykami — t zawyżony): corr {corr(allx, ally):+.2f}, slope {m['beta'][1]*10:+.2f} p.p./10 p.p., t {m['t'][1]:+.2f}; "
      f"fwd5 przy mom20>+20 p.p.: {mean(hi)*100:+.2f} (n={len(hi)}) vs {mean(lo)*100:+.2f} (n={len(lo)})")

print('\n# (a2) Uniwersum 103 spółek: 5-ses. zwrot relatywny vs ^NDX wg decyla 20-ses. zwrotu relatywnego (okna nienakładające się, 2022-10 → 2026-10)\n')
tickers = [c for c in px if not c.startswith('^') and c not in ('QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV')]
i_end = di['2026-10-09']
dec_sum = {d: [] for d in range(10)}
top_bot = []
dates_used = 0
for i in range(i_end, 260, -5):
    rows = []
    rn20 = rr('^NDX', i - 20, i); rn5 = rr('^NDX', i, i + 5)
    if rn20 is None or rn5 is None: continue
    for t in tickers:
        a = rr(t, i - 20, i); b = rr(t, i, i + 5)
        if a is None or b is None: continue
        rows.append((a - rn20, b - rn5))
    if len(rows) < 60: continue
    rows.sort()
    n = len(rows)
    for k, (a, b) in enumerate(rows):
        dec_sum[min(k * 10 // n, 9)].append(b)
    top5 = mean([b for a, b in rows[-5:]]); bot5 = mean([b for a, b in rows[:5]])
    top_bot.append(top5 - bot5)
    dates_used += 1
print(f"okien: {dates_used}; średni 5-ses. zwrot relatywny wg decyla momentum 20-ses. (D1 = najsłabsze, D10 = najmocniejsze):")
for d in range(10):
    xs = dec_sum[d]
    print(f"  D{d+1}: {mean(xs)*100:+.2f} p.p. (n={len(xs)}, sd {sd(xs)*100:.1f})")
print(f"TOP5−BOTTOM5 wg momentum 20-ses. (naiwny „koszyk pogoni”): śr. {mean(top_bot)*100:+.2f} p.p./5 ses., sd {sd(top_bot)*100:.2f}, t {mean(top_bot)/(sd(top_bot)/math.sqrt(len(top_bot))):+.2f} (n={len(top_bot)})")
# ostatni rok osobno
tb_1y = top_bot[:52]
print(f"  ostatnie 52 okna: śr. {mean(tb_1y)*100:+.2f}, t {mean(tb_1y)/(sd(tb_1y)/math.sqrt(len(tb_1y))):+.2f}")

print('\n# (b) Reszty idiosynkratyczne nóg (3f) — per strona i blok\n')
def stat(lab, xs):
    n = len(xs); m = mean(xs); s = sd(xs); t = m / (s / math.sqrt(n)) if s and n > 1 else float('nan')
    hits = sum(1 for x in xs if x > 0)
    print(f"| {lab} | {n} | {m*100:+.2f} | {s*100 if s else float('nan'):.2f} | {t:+.2f} | {hits}/{n} |")
print('| grupa | nóg | śr. reszta p.p. | sd | t (nogi traktowane jako niezależne — zawyżone) | reszta > 0 |')
print('|---|---|---|---|---|---|')
stat('wszystkie nogi', [l['c_res'] for l in LEGS])
stat('LONG', [l['c_res'] for l in LEGS if l['side'] == 'L'])
stat('SHORT', [l['c_res'] for l in LEGS if l['side'] == 'S'])
stat('LONG bez W7', [l['c_res'] for l in LEGS if l['side'] == 'L' and l['w'] != 'W7'])
stat('SHORT bez W7', [l['c_res'] for l in LEGS if l['side'] == 'S' and l['w'] != 'W7'])
for b in ('SEMI', 'SOFT', 'DEF', 'MEDIA', 'CYBER', 'SIECI', 'AUTO', 'UTIL', 'MEGA'):
    xs = [l['c_res'] for l in LEGS if l['blok'] == b]
    if xs: stat(f'blok {b}', xs)
print('\nSurowe pozycje (vs NDX) per strona:')
print('| grupa | nóg | śr. pozycja p.p. | sd | t | trafienia |')
print('|---|---|---|---|---|---|')
stat('LONG pozycja', [l['pos'] for l in LEGS if l['side'] == 'L'])
stat('SHORT pozycja', [l['pos'] for l in LEGS if l['side'] == 'S'])
stat('SHORT DEF+MEDIA pozycja', [l['pos'] for l in LEGS if l['side'] == 'S' and l['blok'] in ('DEF', 'MEDIA')])
stat('SHORT SOFT pozycja', [l['pos'] for l in LEGS if l['side'] == 'S' and l['blok'] == 'SOFT'])
stat('LONG SEMI pozycja', [l['pos'] for l in LEGS if l['side'] == 'L' and l['blok'] == 'SEMI'])
