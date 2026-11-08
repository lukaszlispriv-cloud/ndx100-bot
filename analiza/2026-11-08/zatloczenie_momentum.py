#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zatloczenie_momentum.py — test dwóch KANDYDATÓW z rozmowy 08.11.2026 (po tygodniu W10).
Czysty Python (bez numpy — środowisko rutyn go nie ma).

 T1. ZATŁOCZENIE MOMENTUM: czy średnia korelacja parowa 20-sesyjnych zwrotów dziennych
     wśród TOP10 momentum (na D0) zapowiada gorszy / bardziej lewoskośny spread momentum
     w następnym tygodniu? Kontrola: korelacja całego uniwersum (czynnik rynkowy).
 T2. MOMENTUM REZYDUALNE: ranking po zwrocie oczyszczonym z bety do ^NDX i ^SOX
     (regresja dzienna w oknie formacji, skip 5; wynik = suma reszt / σ reszt) zamiast
     surowego momentum relatywnego. Czy ma podobną średnią i mniejsze załamania?
 T3 (informacyjnie). Reżim „po korekcie”: obsunięcie ^NDX od maks. 252 sesji > 10 % i VIX > 25
     na D0 — jak wypada surowe momentum (strona long / short osobno).

Harness jak w analiza/2026-10-18/bt_momentum.py: okna tygodniowe D0 = ostatnia sesja
tygodnia → D5 = ostatnia sesja następnego tygodnia; noga long = r_spółki − r_NDX,
short = −(r_spółki − r_NDX); spread_pp = średnia 5 long + średnia 5 short.
Wariant produkcyjny momentum: 126 sesji, skip 5 (ranking.py). Uniwersum = klucze
`epics` z signals.json (skład dzisiejszy → survivorship bias, jak w analizie 18.10).
Dane: closes_5y.csv (analiza/2026-10-18/pobierz_closes_5y.py), ścieżka jako argv[1].
Wynik: markdown na stdout (zapisywany do zatloczenie-momentum.md). Bez liczb z rachunku.
Nic z tego pliku nie zmienia ranking.py, signals.json ani bota — to KANDYDACI na papierze.
"""
import sys, csv, math, datetime
CSV = sys.argv[1] if len(sys.argv) > 1 else 'closes_5y.csv'
NON = {'^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV'}
L, SKIP, NL, NS, CORRW = 126, 5, 5, 5, 20
COST_LEG, FIN = 0.0010, 0.06
NaN = float('nan')
def isn(x): return x != x

rows = list(csv.DictReader(open(CSV)))
cols = [c for c in rows[0].keys() if c != 'date']
rows = [r for r in rows if r['^NDX'] not in ('', None)]
dates = [datetime.date.fromisoformat(r['date']) for r in rows]
nT = len(rows)
def series(c):
    out = [float(r[c]) if r[c] not in ('', None) else NaN for r in rows]
    gap = 0
    for i in range(1, nT):               # ffill limit 3
        if isn(out[i]) and not isn(out[i-1]) and gap < 3: out[i] = out[i-1]; gap += 1
        elif not isn(out[i]): gap = 0
    return out
cands = [c for c in cols if c not in NON]
P = {c: series(c) for c in cands}; NDX = series('^NDX'); SOX = series('^SOX'); VIX = series('^VIX')
def rets(s): return [NaN] + [s[i]/s[i-1]-1 if not isn(s[i]) and not isn(s[i-1]) else NaN for i in range(1, nT)]
R = {c: rets(P[c]) for c in cands}; RN = rets(NDX); RS = rets(SOX)
# okna tygodniowe
wk = {}
for i, d in enumerate(dates):
    y, w, _ = d.isocalendar(); wk[(y, w)] = i
last = [wk[k] for k in sorted(wk)]
D0 = last[:-1]; D5 = last[1:]; nW = len(D0)
WN = [NDX[b]/NDX[a]-1 for a, b in zip(D0, D5)]
EX = [{c: (P[c][b]/P[c][a]-1-WN[w]) if not isn(P[c][a]) and not isn(P[c][b]) else NaN for c in cands} for w, (a, b) in enumerate(zip(D0, D5))]
YEAR = [dates[i].year for i in D0]
def rollmax(s, n):
    out = [NaN]*nT
    for i in range(n-1, nT):
        win = [x for x in s[i-n+1:i+1] if not isn(x)]
        out[i] = max(win) if win else NaN
    return out
MX = rollmax(NDX, 252); DD0 = [NDX[i]/MX[i]-1 if not isn(MX[i]) else NaN for i in D0]; VIX0 = [VIX[i] for i in D0]
DAYS = [(dates[b]-dates[a]).days for a, b in zip(D0, D5)]

def mom_raw():
    S = []
    for d0 in D0:
        a, b = d0-L, d0-SKIP
        if a < 0: S.append(None); continue
        S.append({c: (P[c][b]/P[c][a]-1)-(NDX[b]/NDX[a]-1) if not isn(P[c][a]) and not isn(P[c][b]) else NaN for c in cands})
    return S
def inv3(M):
    a,b,c = M[0]; d,e,f = M[1]; g,h,i = M[2]
    A = e*i-f*h; B = -(d*i-f*g); C = d*h-e*g; det = a*A+b*B+c*C
    if abs(det) < 1e-18: return None
    return [[A/det, -(b*i-c*h)/det, (b*f-c*e)/det], [B/det, (a*i-c*g)/det, -(a*f-c*d)/det], [C/det, -(a*h-b*g)/det, (a*e-b*d)/det]]
def mom_resid():
    S = []
    for d0 in D0:
        a, b = d0-L+1, d0-SKIP
        if a < 1: S.append(None); continue
        xs = [(1.0, RN[t], RS[t]) for t in range(a, b+1)]
        if any(isn(x[1]) or isn(x[2]) for x in xs): S.append(None); continue
        n = len(xs); XtX = [[sum(x[i]*x[j] for x in xs) for j in range(3)] for i in range(3)]; Xi = inv3(XtX)
        if Xi is None: S.append(None); continue
        sc = {}
        for c in cands:
            y = [R[c][t] for t in range(a, b+1)]
            if any(isn(v) for v in y): sc[c] = NaN; continue
            Xty = [sum(x[i]*v for x, v in zip(xs, y)) for i in range(3)]
            beta = [sum(Xi[i][j]*Xty[j] for j in range(3)) for i in range(3)]
            res = [v-(beta[0]+beta[1]*x[1]+beta[2]*x[2]) for x, v in zip(xs, y)]
            m = sum(res)/n; sd = math.sqrt(sum((r-m)**2 for r in res)/(n-3))
            sc[c] = sum(res)/sd if sd > 0 else NaN
        S.append(sc)
    return S
def select(S):
    longs, shorts = [], []
    for w in range(nW):
        if S[w] is None: longs.append(None); shorts.append(None); continue
        v = sorted([(s, c) for c, s in S[w].items() if not isn(s) and not isn(EX[w][c])])
        if len(v) < NL+NS+10: longs.append(None); shorts.append(None); continue
        longs.append([c for _, c in v[-NL:]][::-1]); shorts.append([c for _, c in v[:NS]])
    return longs, shorts
def run(longs, shorts):
    sp, lo, sh, tu = [NaN]*nW, [NaN]*nW, [NaN]*nW, [0.0]*nW
    for w in range(nW):
        if longs[w] is None: continue
        lo[w] = sum(EX[w][c] for c in longs[w])/NL*100; sh[w] = -sum(EX[w][c] for c in shorts[w])/NS*100; sp[w] = lo[w]+sh[w]
        if w > 0 and longs[w-1] is not None:
            tu[w] = (NL-len(set(longs[w]) & set(longs[w-1])))+(NS-len(set(shorts[w]) & set(shorts[w-1])))
    return sp, lo, sh, tu
def clean(x): return [v for v in x if not isn(v)]
def mean(x): x = clean(x); return sum(x)/len(x) if x else NaN
def sd(x): x = clean(x); m = sum(x)/len(x); return math.sqrt(sum((v-m)**2 for v in x)/(len(x)-1)) if len(x) > 1 else NaN
def pct(x, p): x = sorted(clean(x)); k = (len(x)-1)*p/100; f = math.floor(k); c = min(f+1, len(x)-1); return x[f]+(x[c]-x[f])*(k-f)
def stats(x):
    x = clean(x); n = len(x)
    if n < 3: return dict(n=n)
    m = sum(x)/n; s = sd(x); sk = sum((v-m)**3 for v in x)/n/s**3 if s > 0 else NaN
    cum = 0; pk = 0; dd = 0
    for v in x: cum += v; pk = max(pk, cum); dd = max(dd, pk-cum)
    return dict(n=n, mean=m, med=pct(x, 50), sd=s, t=m/(s/math.sqrt(n)), sharpe=m/s*math.sqrt(52), skew=sk, p5=pct(x, 5), mn=min(x), hit=sum(v > 0 for v in x)/n, maxdd=dd)
def row(name, s, extra=''):
    if s.get('n', 0) < 3: return f'| {name} | {s.get("n", 0)} | — | | | | | | | | | |'
    return (f"| {name} | {s['n']} | {s['mean']:.2f} | {s['med']:.2f} | {s['sd']:.2f} | {s['t']:.2f} | {s['sharpe']:.2f} | {s['skew']:.2f} | "
            f"{s['p5']:.1f} | {s['mn']:.1f} | {s['hit']*100:.0f}% | {s['maxdd']:.1f} |{extra}")
HDR = '| wariant / kubełek | okna | średnia pp | mediana | σ | t | Sharpe | skośność | p5 | min | hit | maxDD |\n|---|---|---|---|---|---|---|---|---|---|---|---|'
def welch(a, b):
    a, b = clean(a), clean(b)
    return (mean(a)-mean(b))/math.sqrt(sd(a)**2/len(a)+sd(b)**2/len(b))
def pair_corr(names, d0):
    a = d0-CORRW+1; X = [[R[c][t] for t in range(a, d0+1)] for c in names]
    X = [x for x in X if not any(isn(v) for v in x)]
    if len(X) < 4: return NaN
    def corr(u, v):
        mu, mv = sum(u)/len(u), sum(v)/len(v); su = math.sqrt(sum((a-mu)**2 for a in u)); sv = math.sqrt(sum((b-mv)**2 for b in v))
        return sum((a-mu)*(b-mv) for a, b in zip(u, v))/(su*sv) if su > 0 and sv > 0 else NaN
    cs = [corr(X[i], X[j]) for i in range(len(X)) for j in range(i+1, len(X))]
    return mean(cs)
def ols(y, x):
    pts = [(a, b) for a, b in zip(x, y) if not isn(a) and not isn(b)]; n = len(pts)
    mx = sum(a for a, _ in pts)/n; my = sum(b for _, b in pts)/n
    sxx = sum((a-mx)**2 for a, _ in pts); b1 = sum((a-mx)*(b-my) for a, b in pts)/sxx
    e2 = sum((b-my-b1*(a-mx))**2 for a, b in pts); se = math.sqrt(e2/(n-2)/sxx)
    return b1, b1/se, n
def sub(x, m): return [v for v, k in zip(x, m) if k]

S_raw = mom_raw(); S_res = mom_resid()
Lr, Sr = select(S_raw); Lz, Sz = select(S_res)
sp_r, lo_r, sh_r, tu_r = run(Lr, Sr); sp_z, lo_z, sh_z, tu_z = run(Lz, Sz)
common = [not isn(a) and not isn(b) for a, b in zip(sp_r, sp_z)]
crowd, crowd_all = [NaN]*nW, [NaN]*nW
for w, d0 in enumerate(D0):
    if Lr[w] is None or d0 < CORRW: continue
    v = sorted([(s, c) for c, s in S_raw[w].items() if not isn(s) and not isn(EX[w][c])])
    crowd[w] = pair_corr([c for _, c in v[-10:]], d0); crowd_all[w] = pair_corr([c for _, c in v], d0)
ok1 = [not isn(a) and not isn(b) for a, b in zip(crowd, sp_r)]
cv = sub(crowd, ok1); q1, q2, q80 = pct(cv, 33.3), pct(cv, 66.7), pct(cv, 80)
lowb = [o and c <= q1 for o, c in zip(ok1, crowd)]; midb = [o and q1 < c <= q2 for o, c in zip(ok1, crowd)]
highb = [o and c > q2 for o, c in zip(ok1, crowd)]; topb = [o and c > q80 for o, c in zip(ok1, crowd)]
rel = [c-a if not isn(c) and not isn(a) else NaN for c, a in zip(crowd, crowd_all)]
rv = sub(rel, ok1); r1, r2 = pct(rv, 33.3), pct(rv, 66.7)
rlow = [o and r <= r1 for o, r in zip(ok1, rel)]; rhigh = [o and r > r2 for o, r in zip(ok1, rel)]
b1, t1, n1 = ols(sp_r, crowd); b2, t2, n2 = ols(sp_r, rel); b3, t3, n3 = ols(sp_r, crowd_all)
reg = [o and not isn(d) and d < -0.10 and v > 25 for o, d, v in zip(ok1, DD0, VIX0)]
calm = [o and not r for o, r in zip(ok1, reg)]

out = []
nsig = sum(1 for v in sp_r if not isn(v)); first_common = common.index(True)
out.append('# Zatłoczenie momentum i momentum rezydualne — test KANDYDATÓW (08.11.2026)\n')
out.append(f'Dane: closes_5y.csv — {nT} sesji {dates[0]}…{dates[-1]}, {len(cands)} kandydatów (skład dzisiejszy → survivorship bias). Okna tygodniowe: {nW}; z sygnałem (6M skip 5): {nsig}; wspólne okna surowe/rezydualne: {sum(common)} (od D0 = {dates[D0[first_common]]}).\n')
out.append('Harness: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; noga long = r − r_NDX, short = −(r − r_NDX); spread_pp = śr. 5 long + śr. 5 short (gross 2). Sygnały wyłącznie z cen ≤ D0. Brutto; koszty (rotacja 0,10 % × 0,2 nominału strony za zmienioną nogę + finansowanie 6 %/rok × gross) podane osobno w T2.\n')
out.append('## T1. Zatłoczenie momentum (średnia korelacja parowa 20-sesyjna TOP10 momentum na D0) → spread 6M skip 5 w następnym tygodniu\n')
out.append(f'Rozkład proxy: tercyle {q1:.3f} / {q2:.3f}, p80 {q80:.3f}; korelacja TOP10 vs całe uniwersum kandydatów: średnia {mean(cv):.3f} vs {mean(sub(crowd_all, ok1)):.3f}.\n')
out.append(HDR)
out.append(row('wszystkie okna z proxy', stats(sub(sp_r, ok1))))
out.append(row('korelacja TOP10 — tercyl niski', stats(sub(sp_r, lowb))))
out.append(row('korelacja TOP10 — tercyl środkowy', stats(sub(sp_r, midb))))
out.append(row('korelacja TOP10 — tercyl wysoki', stats(sub(sp_r, highb))))
out.append(row('korelacja TOP10 — górne 20 %', stats(sub(sp_r, topb))))
out.append(row('korelacja TOP10 − uniwersum (relatywna) — tercyl niski', stats(sub(sp_r, rlow))))
out.append(row('korelacja TOP10 − uniwersum (relatywna) — tercyl wysoki', stats(sub(sp_r, rhigh))))
out.append(row('  → strona LONG, tercyl wysoki korelacji', stats(sub(lo_r, highb))))
out.append(row('  → strona SHORT, tercyl wysoki korelacji', stats(sub(sh_r, highb))))
out.append(row('  → strona LONG, tercyl niski korelacji', stats(sub(lo_r, lowb))))
out.append(f'\nRóżnica średnich wysoki − niski tercyl: {mean(sub(sp_r, highb))-mean(sub(sp_r, lowb)):+.2f} pp (Welch t = {welch(sub(sp_r, highb), sub(sp_r, lowb)):.2f}); relatywna: {mean(sub(sp_r, rhigh))-mean(sub(sp_r, rlow)):+.2f} pp (t = {welch(sub(sp_r, rhigh), sub(sp_r, rlow)):.2f}). OLS spread ~ korelacja TOP10: nachylenie {b1:.1f} pp na 1,0 korelacji (t = {t1:.2f}, n = {n1}); ~ relatywna: {b2:.1f} (t = {t2:.2f}); ~ korelacja uniwersum: {b3:.1f} (t = {t3:.2f}).\n')
out.append('Stabilność znaku po latach (średni spread w tercylu wysokim − niskim, lata wg D0):\n\n| rok | okna wys./nis. | wysoki pp | niski pp | różnica |\n|---|---|---|---|---|')
for y in sorted(set(YEAR)):
    h = [a and yy == y for a, yy in zip(highb, YEAR)]; l = [a and yy == y for a, yy in zip(lowb, YEAR)]
    if sum(h) >= 3 and sum(l) >= 3:
        out.append(f'| {y} | {sum(h)}/{sum(l)} | {mean(sub(sp_r, h)):.2f} | {mean(sub(sp_r, l)):.2f} | {mean(sub(sp_r, h))-mean(sub(sp_r, l)):+.2f} |')
worst = sorted([w for w in range(nW) if not isn(sp_r[w])], key=lambda w: sp_r[w])[:10]
ranks = {w: i for i, w in enumerate(sorted([w for w in range(nW) if ok1[w]], key=lambda w: crowd[w]))}
out.append('\n10 najgorszych tygodni surowego momentum i wartość proxy na D0 (percentyl korelacji TOP10 wśród okien):\n\n| D0 | spread pp | kor. TOP10 | percentyl | kor. uniwersum | VIX D0 | dd ^NDX D0 |\n|---|---|---|---|---|---|---|')
for w in worst:
    pr = f'{ranks[w]/max(1, len(ranks)-1)*100:.0f}' if w in ranks else 'b.d.'
    out.append(f'| {dates[D0[w]]} | {sp_r[w]:.1f} | {crowd[w]:.2f} | {pr} | {crowd_all[w]:.2f} | {VIX0[w]:.1f} | {DD0[w]*100:.1f} % |')
out.append('\n## T2. Momentum rezydualne (reszty wobec ^NDX i ^SOX, 126 sesji, skip 5, suma reszt / σ reszt) vs surowe momentum relatywne\n')
out.append(HDR)
out.append(row('a) surowe 6M rel. skip 5 (produkcyjne)', stats(sub(sp_r, common)), f' obrót {mean(sub(tu_r, common)):.1f} nóg/tydz.'))
out.append(row('b) rezydualne NDX+SOX', stats(sub(sp_z, common)), f' obrót {mean(sub(tu_z, common)):.1f} nóg/tydz.'))
out.append(row('  a) strona LONG', stats(sub(lo_r, common)))); out.append(row('  b) strona LONG', stats(sub(lo_z, common))))
out.append(row('  a) strona SHORT', stats(sub(sh_r, common)))); out.append(row('  b) strona SHORT', stats(sub(sh_z, common))))
ov = [len(set(Lr[w]) & set(Lz[w]))+len(set(Sr[w]) & set(Sz[w])) for w in range(nW) if common[w]]
a_, b_ = sub(sp_r, common), sub(sp_z, common); ma, mb = mean(a_), mean(b_)
cr = sum((x-ma)*(y-mb) for x, y in zip(a_, b_))/math.sqrt(sum((x-ma)**2 for x in a_)*sum((y-mb)**2 for y in b_))
dmean = mean(sub(DAYS, common))
costs_r = mean(sub(tu_r, common))*COST_LEG*0.2*100+FIN*2*dmean/365*100; costs_z = mean(sub(tu_z, common))*COST_LEG*0.2*100+FIN*2*dmean/365*100
diff = [y-x for x, y in zip(a_, b_)]
out.append(f'\nPokrycie składów a/b: średnio {mean(ov):.1f} z 10 nóg wspólnych; korelacja tygodniowych spreadów a/b: {cr:.2f}. Koszty (rotacja + finansowanie): a) {costs_r:.2f} pp/tydz., b) {costs_z:.2f} pp/tydz. → netto a) {ma-costs_r:.2f}, b) {mb-costs_z:.2f} pp/tydz. Stosunek wariancji b/a: {sd(b_)**2/sd(a_)**2:.3f} (df {len(a_)-1}); różnica średnich b − a = {mb-ma:+.2f} pp (t par = {mean(diff)/(sd(diff)/math.sqrt(len(diff))):.2f}).\n')
out.append('Po latach (lata wg D0, wspólne okna):\n\n| rok | okna | a) surowe pp | b) rezydualne pp | a) min | b) min | a) σ | b) σ |\n|---|---|---|---|---|---|---|---|')
for y in sorted(set(YEAR)):
    m = [c and yy == y for c, yy in zip(common, YEAR)]
    if sum(m) >= 5:
        out.append(f'| {y} | {sum(m)} | {mean(sub(sp_r, m)):.2f} | {mean(sub(sp_z, m)):.2f} | {min(sub(sp_r, m)):.1f} | {min(sub(sp_z, m)):.1f} | {sd(sub(sp_r, m)):.2f} | {sd(sub(sp_z, m)):.2f} |')
out.append('\nTygodnie, gdy surowe momentum straciło ≥ 10 pp — co zrobiło rezydualne:\n\n| D0 | a) surowe | b) rezydualne | SOX−NDX pp |\n|---|---|---|---|')
for w in range(nW):
    if common[w] and sp_r[w] <= -10:
        out.append(f'| {dates[D0[w]]} | {sp_r[w]:.1f} | {sp_z[w]:.1f} | {(SOX[D5[w]]/SOX[D0[w]]-NDX[D5[w]]/NDX[D0[w]])*100:.1f} |')
wl = max(w for w in range(nW) if common[w])
out.append(f'\nSkład rezydualny na ostatnim D0 harnessu ({dates[D0[wl]]}, informacyjnie, NIE do signals.json): LONG {", ".join(Lz[wl])} · SHORT {", ".join(Sz[wl])}; surowe: LONG {", ".join(Lr[wl])} · SHORT {", ".join(Sr[wl])}.\n')
out.append('## T3 (informacyjnie). Reżim „po korekcie”: obsunięcie ^NDX od maks. 252 sesji > 10 % i VIX > 25 na D0\n')
out.append(HDR)
out.append(row('surowe momentum — reżim po korekcie', stats(sub(sp_r, reg)))); out.append(row('surowe momentum — pozostałe okna', stats(sub(sp_r, calm))))
out.append(row('  strona LONG — po korekcie', stats(sub(lo_r, reg)))); out.append(row('  strona SHORT — po korekcie', stats(sub(sh_r, reg))))
rc = [r and c for r, c in zip(reg, common)]; cc = [k and c for k, c in zip(calm, common)]
out.append(row('rezydualne — po korekcie', stats(sub(sp_z, rc)))); out.append(row('rezydualne — pozostałe okna', stats(sub(sp_z, cc))))
yrs = sorted(set(y for y, r in zip(YEAR, reg) if r))
out.append(f'\nOkna „po korekcie”: {sum(reg)} (lata: {", ".join(f"{y}: {sum(1 for yy, r in zip(YEAR, reg) if r and yy == y)}" for y in yrs)}). Welch t różnicy średnich (po korekcie − pozostałe): {welch(sub(sp_r, reg), sub(sp_r, calm)) if sum(reg) >= 3 else float("nan"):.2f}.\n')
out.append('## Uwagi metodyczne\n- Skład dzisiejszy uniwersum (survivorship bias) — jak w analizie 18.10; spółki bez pełnego okna formacji wypadają z selekcji w danym tygodniu.\n- Proxy zatłoczenia T1 jest liczone z cen (korelacja), nie z pozycji funduszy — mierzy współbieżność ruchów liderów momentum, nie faktyczne zatłoczenie.\n- Kryteria awansu z nagłówka rutyny/reguly.md: ≥ 30 zdarzeń w ≥ 15 tygodniach, |t| ≥ 2 (klastrowane), ten sam znak w ≥ 4 z 5 lat, reguła musi wiązać. Moratorium na nowe reguły koszykowe do końca 26 okien cieni.\n- Nic z tego pliku nie zmienia ranking.py, signals.json ani bota.\n')
print('\n'.join(out))
