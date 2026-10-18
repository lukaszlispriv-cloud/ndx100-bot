#!/usr/bin/env python3
"""Weryfikacja C8: bramka reżimu P0/P1/P2 a momentum 6M — w jednostkach KAPITAŁU (ALLOC 0,24, gross 240%),
z kill switchem 0,75 × kroczący szczyt (jak app.py), kosztami finansowania ∝ gross, wariantami progów
i oceną jako ubezpieczenie (P(kill)) — także przy zerowej alfie (losowe koszyki 5/5).

Wejście: bt_rezim-i-zaklad-czynnikowy_serie.csv (wariant mom6M: longs/shorts na D0) + closes_5y.csv.
Dzienny zwrot kapitału = ALLOC × g_t × (Σ r_long − Σ r_short) − koszty; g_t = mnożnik bramki (1 / 0,5 / 0).
Bez liczb z rachunku — kapitał startowy 100 (umowny).
"""
import json, math, sys
import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
SER = f'{BASE}/analiza/bt_rezim-i-zaklad-czynnikowy_serie.csv'
OUT_MD = f'{BASE}/analiza/weryfikacja_C8_out.md'
OUT_JSON = f'{BASE}/analiza/weryfikacja_C8_wyniki.json'
OUT_CSV = f'{BASE}/analiza/weryfikacja_C8_serie.csv'

ALLOC = 0.24
KILL = 0.75
FIN = 0.06           # rocznie od gross
COST_LEG = 0.0010    # 0,10% nominału nogi za zmianę nazwy / zmianę gross
N_RAND = 500
SEED = 20261018
NON_CAND = ['^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV']

df = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
df = df[df['^NDX'].notna()].ffill(limit=3)
cands = [c for c in df.columns if c not in NON_CAND]
cidx = {c: i for i, c in enumerate(cands)}
dates = df.index
P = df[cands].to_numpy(float)
NDX = df['^NDX'].to_numpy(float); VIX = df['^VIX'].to_numpy(float)
nT, nS = P.shape
R = np.full_like(P, np.nan); R[1:] = P[1:] / P[:-1] - 1
RN = np.concatenate([[np.nan], NDX[1:] / NDX[:-1] - 1])
MA200 = pd.Series(NDX).rolling(200).mean().to_numpy()
MA50 = pd.Series(NDX).rolling(50).mean().to_numpy()
MAX252 = pd.Series(NDX).rolling(252, min_periods=120).max().to_numpy()
DD = NDX / MAX252 - 1
didx = {d: i for i, d in enumerate(dates)}

ser = pd.read_csv(SER, parse_dates=['date_d0', 'date_d5'])
mom = ser[ser.variant == 'mom6M'].reset_index(drop=True)
nW = len(mom)
D0 = np.array([didx[d] for d in mom.date_d0]); D5 = np.array([didx[d] for d in mom.date_d5])
LONGS = [[cidx[t] for t in s.split()] for s in mom.longs]
SHORTS = [[cidx[t] for t in s.split()] for s in mom.shorts]
SPREAD = mom.spread_pp.to_numpy()
YEAR = np.array([dates[i].year for i in D0])
VIX0 = VIX[D0]
DAYS = np.array([(dates[b] - dates[a]).days for a, b in zip(D0, D5)])

# ------------------------------------------------------------------ bramka (dziennie), parametryzowana
def gate_states(p1_ma200=True, p1_dd=0.10, p1_vix=28.0, p2_dd=0.20, p2_vix=40.0, p2_ses=-0.05,
                hyst=True, h2_vix=25.0, h2_n=5, h1_vix=22.0, h1_n=3):
    raw = np.zeros(nT, int)
    for i in range(nT):
        p2 = (DD[i] < -p2_dd) or (VIX[i] > p2_vix) or (not np.isnan(RN[i]) and RN[i] <= p2_ses)
        p1 = (p1_ma200 and not np.isnan(MA200[i]) and NDX[i] < MA200[i]) or (DD[i] < -p1_dd) or (VIX[i] > p1_vix)
        raw[i] = 2 if p2 else (1 if p1 else 0)
    if not hyst:
        return raw
    st = np.zeros(nT, int); s = 0; c2 = c1 = 0
    for i in range(nT):
        r_ = raw[i]
        if r_ == 2:
            s = 2; c2 = c1 = 0
        elif s == 2:
            ok = (VIX[i] < h2_vix) and (not np.isnan(MA50[i]) and NDX[i] > MA50[i])
            c2 = c2 + 1 if ok else 0
            if c2 >= h2_n:
                s = 1; c2 = c1 = 0
        elif s == 1:
            if r_ == 1:
                c1 = 0
            else:
                ok = (VIX[i] < h1_vix) and (not np.isnan(MA200[i]) and NDX[i] > MA200[i])
                c1 = c1 + 1 if ok else 0
                if c1 >= h1_n:
                    s = 0; c1 = 0
        else:
            if r_ == 1:
                s = 1; c1 = 0
        st[i] = s
    return st

def gross_from_state(st, g1=0.5, g2=0.0):
    return np.where(st == 0, 1.0, np.where(st == 1, g1, g2))

# ------------------------------------------------------------------ symulacja kapitału (dziennie)
def simulate(longs, shorts, g_week=None, g_daily=None, alloc=ALLOC, kill=True, costs=True,
             start=100.0, w_from=0, w_to=None, peak0=None):
    """g_week: mnożnik gross odczytany na D0 (stały w oknie); g_daily: mnożnik dzienny (stan z poprzedniej sesji).
    Zwraca krzywą kapitału dzienną, zwroty tygodniowe (% kapitału na starcie okna), flagi kill."""
    w_to = nW if w_to is None else w_to
    cap = start; peak = start if peak0 is None else max(peak0, start)
    curve = [start]; wk = []; killed_at = None; gross_used = []
    prev = set(); fin_cost = 0.0; rot_cost = 0.0
    g_prev = 0.0
    for w in range(w_from, w_to):
        if killed_at is not None:
            wk.append(0.0); gross_used.append(0.0); continue
        c0 = cap
        L = longs[w]; S = shorts[w]
        if L is None:
            wk.append(0.0); gross_used.append(0.0); continue
        g_w = 1.0 if g_week is None else g_week[w]
        cur = set((i, 1) for i in L) | set((i, -1) for i in S)
        # koszt rotacji: zmienione nogi × nominał nogi × 0,10%
        if costs:
            if g_daily is None:
                changed = len(cur - prev) if (prev and g_prev > 0) else len(cur)
                rot = changed * alloc * g_w * COST_LEG * cap
                rot += abs(g_w - g_prev) * 10 * alloc * COST_LEG * cap if (prev and g_prev > 0) else 0.0
                cap -= rot; rot_cost += rot
        gsum = 0.0; nd = 0
        for t in range(D0[w] + 1, D5[w] + 1):
            g = g_w if g_daily is None else g_daily[t - 1]   # stan z zamknięcia poprzedniej sesji
            if g_daily is not None and costs:
                dg = abs(g - g_prev)
                if dg > 0:
                    rot = dg * 10 * alloc * COST_LEG * cap
                    # pierwsze zbudowanie w oknie / zmiana nazw
                    cap -= rot; rot_cost += rot
                if t == D0[w] + 1 and g > 0:
                    changed = len(cur - prev) if prev else len(cur)
                    rot = changed * alloc * g * COST_LEG * cap; cap -= rot; rot_cost += rot
                g_prev = g
            rl = np.nansum(R[t, L]); rs = np.nansum(R[t, S])
            ret = alloc * g * (rl - rs)
            if costs:
                dd_ = (dates[t] - dates[t - 1]).days
                f = FIN * (10 * alloc * g) * dd_ / 365
                ret -= f; fin_cost += f * cap
            cap *= (1 + ret)
            gsum += g; nd += 1
            if cap > peak:
                peak = cap
            if kill and cap < KILL * peak:
                killed_at = (w, t); cap_k = cap
                curve.append(cap)
                break
            curve.append(cap)
        if g_daily is None:
            g_prev = g_w
        prev = cur if (g_w > 0 if g_daily is None else gsum > 0) else prev
        wk.append(100 * (cap / c0 - 1)); gross_used.append(gsum / max(nd, 1))
    return dict(curve=np.array(curve), wk=np.array(wk), killed_at=killed_at, final=cap, peak=peak,
                fin_cost=fin_cost, rot_cost=rot_cost, gross=np.array(gross_used))

def path_stats(curve, wk, n_weeks):
    c = np.asarray(curve)
    peak = np.maximum.accumulate(c); dd = 1 - c / peak
    maxdd = dd.max(); i_tr = int(dd.argmax()); i_pk = int(np.argmax(c[:i_tr + 1]))
    rec = None
    for j in range(i_tr, len(c)):
        if c[j] >= c[i_pk]:
            rec = j - i_pk; break
    x = np.asarray(wk); mu = x.mean(); sd = x.std(ddof=1) if len(x) > 1 else np.nan
    return dict(maxdd_pct=100 * maxdd, peak_to_trough_sessions=i_tr - i_pk,
                recovery_sessions=rec, cagr_pct=100 * ((c[-1] / c[0]) ** (52 / n_weeks) - 1) if c[-1] > 0 else -100,
                final=c[-1], mean_wk=mu, sd_wk=sd, sharpe=mu / sd * math.sqrt(52) if sd > 0 else np.nan,
                t=mu / sd * math.sqrt(len(x)) if sd > 0 else np.nan)

def kill_windows(longs, shorts, g_week=None, g_daily=None, H=12, alloc=ALLOC, step=1):
    hits = tot = 0; mins = []
    for s in range(0, nW - H + 1, step):
        r = simulate(longs, shorts, g_week, g_daily, alloc=alloc, kill=True, w_from=s, w_to=s + H)
        tot += 1; hits += r['killed_at'] is not None; mins.append(r['curve'].min())
    return hits, tot, float(np.percentile(mins, 5)), float(np.median(mins))

# ------------------------------------------------------------------ stany bramki
ST_HYS = gate_states(); ST_RAW = gate_states(hyst=False)
G_HYS_W = gross_from_state(ST_HYS[D0]); G_RAW_W = gross_from_state(ST_RAW[D0])
G_HYS_D = gross_from_state(ST_HYS); G_RAW_D = gross_from_state(ST_RAW)
G_P2ONLY_W = np.where(ST_HYS[D0] == 2, 0.0, 1.0)
assert (ST_HYS[D0] == mom.gate_hys.to_numpy()).all(), 'rozjazd stanów bramki z serią fazy 2'
assert (ST_RAW[D0] == mom.gate_raw.to_numpy()).all()

LONGS_ARR = LONGS; SHORTS_ARR = SHORTS
out = {}; md = []
md.append('# Weryfikacja C8 — bramka reżimu w jednostkach kapitału (ALLOC 0,24, kill 0,75×szczyt)\n')
md.append(f'Okna: {nW} (D0 {dates[D0[0]].date()} → D5 {dates[D5[-1]].date()}), koszyki mom6M z fazy 2 (TOP5/BOTTOM5 6M skip 0, równe wagi). '
          f'Dzienny zwrot kapitału = 0,24 × g × (Σ r_long − Σ r_short) − finansowanie 6%/rok × gross(2,4·g) − 0,10% × nominał za zmienioną nogę/zmianę gross. '
          f'Kill switch: kapitał < 0,75 × kroczący szczyt (sprawdzany na zamknięciach), potem płasko. Kapitał startowy 100 (umowny).\n')

# 1. kontrola: tygodniowy zwrot kapitału ≈ 1,2 × spread_pp
r0 = simulate(LONGS, SHORTS, costs=False, kill=False)
chk = np.corrcoef(r0['wk'], 1.2 * SPREAD)[0, 1]
md.append(f'Kontrola: korelacja tygodniowego zwrotu kapitału (brutto, bez kill) z 1,2×spread_pp = {chk:.4f}; '
          f'śr. {r0["wk"].mean():.3f} vs {1.2 * SPREAD.mean():.3f} pp kapitału.\n')

# ------------------------------------------------------------------ TEST 1+2: pełna ścieżka 2022-04 → 2026-10
md.append('\n## TEST 1–2. Pełna ścieżka: maxDD kapitału, czas odrobienia, Sharpe netto z finansowaniem ∝ gross\n')
md.append('| wariant | śr. gross | kapitał końc. bez kill | maxDD kap. % (bez kill) | szczyt→dołek ses. | odrobienie ses. | CAGR % | Sharpe netto (tyg.) | t netto | śr. tyg. % | σ tyg. % | kapitał końc. Z KILL | kill (data) | koszt fin. łącznie | koszt rot. łącznie |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
VARS = [('bez bramki', None, None),
        ('bramka z histerezą (odczyt D0, jak faza 2)', G_HYS_W, None),
        ('bramka surowa (odczyt D0)', G_RAW_W, None),
        ('tylko P2→0 (P1 pełny gross)', G_P2ONLY_W, None),
        ('bramka z histerezą DZIENNA (jak Puls: stan z poprzedniej sesji)', None, G_HYS_D),
        ('bramka surowa DZIENNA', None, G_RAW_D)]
full = {}
for name, gw, gd in VARS:
    rk = simulate(LONGS, SHORTS, gw, gd, kill=True)
    rn = simulate(LONGS, SHORTS, gw, gd, kill=False)
    s = path_stats(rn['curve'], rn['wk'], nW)
    kd = dates[rk['killed_at'][1]].date().isoformat() if rk['killed_at'] else '—'
    full[name] = dict(stats=s, final_kill=rk['final'], killed=kd, gross=float(rn['gross'].mean()),
                      fin=rn['fin_cost'], rot=rn['rot_cost'])
    md.append(f"| {name} | {100 * rn['gross'].mean():.0f}% | {s['final']:.1f} | {s['maxdd_pct']:.1f} | {s['peak_to_trough_sessions']} | "
              f"{s['recovery_sessions'] if s['recovery_sessions'] is not None else 'nie odrobiono'} | {s['cagr_pct']:.1f} | {s['sharpe']:.2f} | {s['t']:.2f} | "
              f"{s['mean_wk']:.2f} | {s['sd_wk']:.2f} | {rk['final']:.1f} | {kd} | {rn['fin_cost']:.1f} | {rn['rot_cost']:.1f} |")
out['full_path'] = full

# epizody DD > 25% na ścieżce bez kill (żeby policzyć ile razy kill by strzelił, gdyby wznawiano)
def dd_episodes(curve, thr=0.25):
    c = np.asarray(curve); peak = c[0]; ep = []; in_ep = False
    for i, v in enumerate(c):
        if v > peak:
            peak = v; in_ep = False
        elif v < (1 - thr) * peak and not in_ep:
            ep.append(i); in_ep = True
    return ep
md.append('\nEpizody przebicia −25% od kroczącego szczytu na ścieżce BEZ kill (= ile razy kill switch strzeliłby, gdyby po każdym strzale wznawiać od bieżącego kapitału jako nowego szczytu — przybliżenie):\n')
md.append('| wariant | liczba epizodów | daty pierwszej sesji |\n|---|---|---|')
for name, gw, gd in VARS:
    rn = simulate(LONGS, SHORTS, gw, gd, kill=False)
    ep = dd_episodes(rn['curve'])
    # indeks krzywej → data: krzywa ma 1 + liczba sesji od D0[0]+1
    sess = list(range(D0[0], D5[-1] + 1))
    ds = [dates[sess[min(i, len(sess) - 1)]].date().isoformat() for i in ep]
    full[name]['dd25_episodes'] = ds
    md.append(f"| {name} | {len(ep)} | {', '.join(ds)} |")

# ------------------------------------------------------------------ TEST 4: P(kill) na oknach kroczących
md.append('\n## TEST 4. P(kill) — okna kroczące 12 i 26 tygodni (start kapitału 100 = szczyt), ALLOC 0,24\n')
md.append('| wariant | okna 12 tyg. z killem | % | 5. pct min. kapitału (12 t.) | mediana min. | okna 26 tyg. z killem | % |\n|---|---|---|---|---|---|---|')
kw = {}
for name, gw, gd in VARS:
    h12, t12, p5, med = kill_windows(LONGS, SHORTS, gw, gd, H=12)
    h26, t26, _, _ = kill_windows(LONGS, SHORTS, gw, gd, H=26)
    kw[name] = dict(k12=h12, n12=t12, p5=p5, med=med, k26=h26, n26=t26)
    md.append(f'| {name} | {h12}/{t12} | {100 * h12 / t12:.1f} | {p5:.1f} | {med:.1f} | {h26}/{t26} | {100 * h26 / t26:.1f} |')
out['kill_windows'] = kw

# P(kill) per rok (okna 12 tyg. startujące w roku)
md.append('\nOkna 12-tyg. z killem wg roku startu (bez bramki vs bramka z histerezą D0 vs dzienna):\n')
md.append('| rok startu | okna | bez bramki | hist. D0 | hist. dzienna | tylko P2→0 |\n|---|---|---|---|---|---|')
ky = {}
for y in sorted(set(YEAR)):
    idx = [s for s in range(0, nW - 12 + 1) if YEAR[s] == y]
    row = []
    for name, gw, gd in [VARS[0], VARS[1], VARS[4], VARS[3]]:
        h = sum(simulate(LONGS, SHORTS, gw, gd, w_from=s, w_to=s + 12)['killed_at'] is not None for s in idx)
        row.append(h)
    ky[int(y)] = dict(n=len(idx), bez=row[0], hist=row[1], dzienna=row[2], p2only=row[3])
    md.append(f'| {y} | {len(idx)} | {row[0]} | {row[1]} | {row[2]} | {row[3]} |')
out['kill_by_year'] = ky

# ------------------------------------------------------------------ 2022 jako epizod ubezpieczeniowy
md.append('\n## Epizod 2022 (okna z D0 w 2022): kapitał z/bez bramki, start 100 na pierwszym D0 2022\n')
i22 = [w for w in range(nW) if YEAR[w] == 2022]
md.append('| wariant | kapitał końc. 2022 bez kill | maxDD % | z kill: kapitał | kill |\n|---|---|---|---|---|')
e22 = {}
for name, gw, gd in VARS:
    rn = simulate(LONGS, SHORTS, gw, gd, kill=False, w_from=i22[0], w_to=i22[-1] + 1)
    rk = simulate(LONGS, SHORTS, gw, gd, kill=True, w_from=i22[0], w_to=i22[-1] + 1)
    s = path_stats(rn['curve'], rn['wk'], len(i22))
    e22[name] = dict(final=rn['final'], maxdd=s['maxdd_pct'], final_kill=rk['final'], killed=bool(rk['killed_at']))
    md.append(f"| {name} | {rn['final']:.1f} | {s['maxdd_pct']:.1f} | {rk['final']:.1f} | {dates[rk['killed_at'][1]].date() if rk['killed_at'] else '—'} |")
out['y2022'] = e22

# tygodnie wg stanu bramki: σ zwrotu kapitału (nie tylko średnia) — to decyduje o P(kill)
md.append('\nZwrot kapitału (brutto, 1,2×spread) wg stanu bramki z histerezą na D0 — średnia, σ, najgorszy tydzień:\n')
md.append('| stan | okna | śr. % kap. | σ % kap. | najgorszy % | 5. pct % | udział tyg. < −10% kap. |\n|---|---|---|---|---|---|---|')
cap_wk = 1.2 * SPREAD
bs = {}
for s_, lab in ((0, 'P0'), (1, 'P1'), (2, 'P2')):
    m = ST_HYS[D0] == s_; x = cap_wk[m]
    bs[lab] = dict(n=int(m.sum()), mean=float(x.mean()), sd=float(x.std(ddof=1)), worst=float(x.min()), p5=float(np.percentile(x, 5)), lt10=float((x < -10).mean()))
    md.append(f'| {lab} | {m.sum()} | {x.mean():.2f} | {x.std(ddof=1):.2f} | {x.min():.1f} | {np.percentile(x, 5):.1f} | {100 * (x < -10).mean():.0f}% |')
out['by_state'] = bs

# ------------------------------------------------------------------ TEST 3: siatka progów
md.append('\n## TEST 3. Warianty progów (bramka z histerezą, odczyt D0 i DZIENNY) — czy jakiś poprawia Sharpe netto kapitału?\n')
md.append('Siatka: P1 VIX ∈ {25, 28, 30, 35}, P1 DD ∈ {10, 15, 100(=wył.)}, MA200 ∈ {tak, nie}; P2 DD ∈ {20, 25, 100(=wył.)}, P2 VIX ∈ {35, 40}; gross P1 ∈ {0,5; 0,75}. '
          'Metryki na pełnej ścieżce BEZ kill (Sharpe/maxDD) oraz P(kill 12 t.). Wielokrotne porównania — każdy "najlepszy" wariant jest in-sample.\n')
grid = []
for p1v in (25.0, 28.0, 30.0, 35.0):
    for p1d in (0.10, 0.15, 1.0):
        for ma in (True, False):
            for p2d in (0.20, 0.25, 1.0):
                for p2v in (35.0, 40.0):
                    st = gate_states(p1_ma200=ma, p1_dd=p1d, p1_vix=p1v, p2_dd=p2d, p2_vix=p2v)
                    for g1 in (0.5, 0.75):
                        for mode in ('D0', 'dzienna'):
                            gw = gross_from_state(st[D0], g1=g1) if mode == 'D0' else None
                            gd = gross_from_state(st, g1=g1) if mode == 'dzienna' else None
                            rn = simulate(LONGS, SHORTS, gw, gd, kill=False)
                            s = path_stats(rn['curve'], rn['wk'], nW)
                            act = int(((st[D0]) > 0).sum())
                            grid.append(dict(p1_vix=p1v, p1_dd=p1d, ma200=ma, p2_dd=p2d, p2_vix=p2v, g1=g1, mode=mode,
                                             active=act, gross=float(rn['gross'].mean()), sharpe=s['sharpe'], t=s['t'],
                                             mean=s['mean_wk'], sd=s['sd_wk'], maxdd=s['maxdd_pct'], final=s['final']))
G = pd.DataFrame(grid)
base_sh = full['bez bramki']['stats']['sharpe']; base_dd = full['bez bramki']['stats']['maxdd_pct']
G['d_sharpe'] = G.sharpe - base_sh; G['d_maxdd'] = G.maxdd - base_dd
md.append(f'Odniesienie bez bramki: Sharpe netto {base_sh:.3f}, maxDD {base_dd:.1f}%, kapitał końc. {full["bez bramki"]["stats"]["final"]:.1f}.\n')
md.append(f'Wariantów w siatce: {len(G)}; z Sharpe > odniesienia: {(G.d_sharpe > 0).sum()} ({100 * (G.d_sharpe > 0).mean():.0f}%); '
          f'z maxDD niższym o >5 pkt: {(G.d_maxdd < -5).sum()}; z OBYDWOMA (Sharpe wyżej i maxDD niżej o >5 pkt): {((G.d_sharpe > 0) & (G.d_maxdd < -5)).sum()}.\n')
md.append('Top 10 wg Sharpe:\n')
md.append('| P1 VIX | P1 DD | MA200 | P2 DD | P2 VIX | gross P1 | tryb | aktywna tyg. | śr. gross | Sharpe | t | śr. tyg. % | σ | maxDD % | kapitał końc. |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for _, r in G.sort_values('sharpe', ascending=False).head(10).iterrows():
    md.append(f"| {r.p1_vix:.0f} | {'wył.' if r.p1_dd >= 1 else f'{100*r.p1_dd:.0f}%'} | {'tak' if r.ma200 else 'nie'} | {'wył.' if r.p2_dd >= 1 else f'{100*r.p2_dd:.0f}%'} | {r.p2_vix:.0f} | {r.g1} | {r['mode']} | {r.active} | {100*r.gross:.0f}% | {r.sharpe:.3f} | {r.t:.2f} | {r['mean']:.2f} | {r.sd:.2f} | {r.maxdd:.1f} | {r.final:.1f} |")
md.append('\nWarianty z pytania (VIX 25 / VIX 30 / DD 15%), reszta progów jak w rutynie, gross P1 0,5:\n')
md.append('| wariant | tryb | aktywna tyg. | śr. gross | Sharpe | t | maxDD % | kapitał końc. | ΔSharpe | ΔmaxDD |\n|---|---|---|---|---|---|---|---|---|---|')
for lab, q in (('P1 VIX>25', dict(p1_vix=25.0, p1_dd=0.10, ma200=True, p2_dd=0.20, p2_vix=40.0, g1=0.5)),
               ('P1 VIX>30', dict(p1_vix=30.0, p1_dd=0.10, ma200=True, p2_dd=0.20, p2_vix=40.0, g1=0.5)),
               ('P1 DD>15%', dict(p1_vix=28.0, p1_dd=0.15, ma200=True, p2_dd=0.20, p2_vix=40.0, g1=0.5)),
               ('P2 DD>25%', dict(p1_vix=28.0, p1_dd=0.10, ma200=True, p2_dd=0.25, p2_vix=40.0, g1=0.5)),
               ('bez MA200 w P1', dict(p1_vix=28.0, p1_dd=0.10, ma200=False, p2_dd=0.20, p2_vix=40.0, g1=0.5)),
               ('tylko VIX (P1>28, P2>40), bez DD i MA', dict(p1_vix=28.0, p1_dd=1.0, ma200=False, p2_dd=1.0, p2_vix=40.0, g1=0.5))):
    for mode in ('D0', 'dzienna'):
        r = G[(G.p1_vix == q['p1_vix']) & (G.p1_dd == q['p1_dd']) & (G.ma200 == q['ma200']) & (G.p2_dd == q['p2_dd']) & (G.p2_vix == q['p2_vix']) & (G.g1 == q['g1']) & (G['mode'] == mode)].iloc[0]
        md.append(f"| {lab} | {mode} | {r.active} | {100*r.gross:.0f}% | {r.sharpe:.3f} | {r.t:.2f} | {r.maxdd:.1f} | {r.final:.1f} | {r.d_sharpe:+.3f} | {r.d_maxdd:+.1f} |")
G.to_csv(f'{BASE}/analiza/weryfikacja_C8_siatka.csv', index=False)
out['grid_summary'] = dict(n=len(G), better_sharpe=int((G.d_sharpe > 0).sum()), lower_dd5=int((G.d_maxdd < -5).sum()),
                           both=int(((G.d_sharpe > 0) & (G.d_maxdd < -5)).sum()), best=G.sort_values('sharpe', ascending=False).head(5).to_dict('records'))

# ------------------------------------------------------------------ TEST 4b: ubezpieczenie przy ZEROWEJ alfie — losowe koszyki 5/5
md.append('\n## TEST 4b. Bramka jako ubezpieczenie przy zerowej alfie: losowe koszyki 5/5 (te same okna), ALLOC 0,24\n')
md.append(f'{N_RAND} losowych strategii (losowy TOP5/BOTTOM5 z uniwersum ważnego na D0 — spółki z pełnym 126-sesyjnym oknem). '
          'Dla każdej: P(kill 12 t.) bez bramki vs z bramką (hist. D0 i dzienna), maxDD pełnej ścieżki, Sharpe netto. Finansowanie ∝ gross jest tu kosztem netto ujemnym dla obu wariantów.\n')
rng = np.random.default_rng(SEED)
VALID = ~np.isnan(mom.spread_pp.to_numpy())
MOM_OK = np.zeros((nW, nS), bool)
L_MOM = 126
for w in range(nW):
    i = D0[w]
    if i >= L_MOM:
        MOM_OK[w] = ~np.isnan(P[i]) & ~np.isnan(P[i - L_MOM]) & ~np.isnan(P[D5[w]])
rand_res = {k: dict(k12=[], maxdd=[], sharpe=[], final=[], mean=[], sd=[]) for k in ('bez', 'hist_D0', 'hist_dzienna', 'p2only')}
STEP = 4  # okna 12-tyg. co 4 tygodnie dla szybkości
for n in range(N_RAND):
    Lr = []; Sr = []
    for w in range(nW):
        ok = np.flatnonzero(MOM_OK[w])
        pick = rng.choice(ok, 10, replace=False)
        Lr.append(list(pick[:5])); Sr.append(list(pick[5:]))
    for k, gw, gd in (('bez', None, None), ('hist_D0', G_HYS_W, None), ('hist_dzienna', None, G_HYS_D), ('p2only', G_P2ONLY_W, None)):
        rn = simulate(Lr, Sr, gw, gd, kill=False)
        s = path_stats(rn['curve'], rn['wk'], nW)
        h, t, _, _ = kill_windows(Lr, Sr, gw, gd, H=12, step=STEP)
        rand_res[k]['k12'].append(h / t); rand_res[k]['maxdd'].append(s['maxdd_pct']); rand_res[k]['sharpe'].append(s['sharpe'])
        rand_res[k]['final'].append(s['final']); rand_res[k]['mean'].append(s['mean_wk']); rand_res[k]['sd'].append(s['sd_wk'])
md.append('| wariant | P(kill 12 t.) śr. | mediana | maxDD śr. % | mediana | Sharpe netto śr. | śr. tyg. % | σ tyg. % | kapitał końc. mediana | udział strategii z kill w pełnej ścieżce |\n|---|---|---|---|---|---|---|---|---|---|')
rr = {}
for k, lab in (('bez', 'bez bramki'), ('hist_D0', 'bramka hist. D0'), ('hist_dzienna', 'bramka hist. dzienna'), ('p2only', 'tylko P2→0')):
    d = {kk: np.array(v) for kk, v in rand_res[k].items()}
    rr[k] = {kk: float(v.mean()) for kk, v in d.items()}; rr[k]['k12_med'] = float(np.median(d['k12'])); rr[k]['maxdd_med'] = float(np.median(d['maxdd'])); rr[k]['final_med'] = float(np.median(d['final']))
    rr[k]['full_kill_share'] = float((d['maxdd'] >= 25).mean())
    md.append(f"| {lab} | {100 * d['k12'].mean():.1f}% | {100 * np.median(d['k12']):.1f}% | {d['maxdd'].mean():.1f} | {np.median(d['maxdd']):.1f} | {d['sharpe'].mean():.2f} | {d['mean'].mean():.3f} | {d['sd'].mean():.2f} | {np.median(d['final']):.1f} | {100 * (d['maxdd'] >= 25).mean():.0f}% |")
# sparowana różnica
dk = np.array(rand_res['hist_D0']['k12']) - np.array(rand_res['bez']['k12'])
ddd = np.array(rand_res['hist_D0']['maxdd']) - np.array(rand_res['bez']['maxdd'])
dsh = np.array(rand_res['hist_D0']['sharpe']) - np.array(rand_res['bez']['sharpe'])
md.append(f'\nSparowane różnice (hist. D0 − bez bramki) na {N_RAND} losowych strategiach: ΔP(kill 12 t.) = {100 * dk.mean():+.1f} pkt (udział strategii, gdzie bramka obniża P(kill): {100 * (dk < 0).mean():.0f}%); '
          f'ΔmaxDD = {ddd.mean():+.1f} pkt (obniża w {100 * (ddd < 0).mean():.0f}%); ΔSharpe = {dsh.mean():+.3f} (podnosi w {100 * (dsh > 0).mean():.0f}%).\n')
out['random'] = rr; out['random_paired'] = dict(d_k12=float(dk.mean()), share_lower_k12=float((dk < 0).mean()), d_maxdd=float(ddd.mean()), share_lower_dd=float((ddd < 0).mean()), d_sharpe=float(dsh.mean()), share_higher_sh=float((dsh > 0).mean()))

# σ losowego koszyka wg stanu bramki (zmienność szumu w P2 vs P0)
md.append('σ tygodniowego zwrotu kapitału LOSOWEGO koszyka (brutto, 1,2×spread) wg stanu bramki (pooled z 200 losowań):\n')
rng2 = np.random.default_rng(SEED + 1)
pool = {0: [], 1: [], 2: []}
WRET = P[D5] / P[D0] - 1; WN = NDX[D5] / NDX[D0] - 1; EX = WRET - WN[:, None]
for n in range(200):
    for w in range(nW):
        ok = np.flatnonzero(MOM_OK[w]); pk = rng2.choice(ok, 10, replace=False)
        sp = 100 * (EX[w, pk[:5]].mean() - EX[w, pk[5:]].mean())
        pool[ST_HYS[D0[w]]].append(1.2 * sp)
md.append('| stan | σ % kap. | 5. pct | 1. pct |\n|---|---|---|---|')
sig_state = {}
for s_, lab in ((0, 'P0'), (1, 'P1'), (2, 'P2')):
    x = np.array(pool[s_]); sig_state[lab] = dict(sd=float(x.std()), p5=float(np.percentile(x, 5)), p1=float(np.percentile(x, 1)))
    md.append(f'| {lab} | {x.std():.2f} | {np.percentile(x, 5):.1f} | {np.percentile(x, 1):.1f} |')
out['random_sigma_by_state'] = sig_state

# ------------------------------------------------------------------ ALLOC niższy: czy bramka ma sens przy 0,12?
md.append('\n## Dodatek: ta sama bramka przy ALLOC 0,12 (gross 120%) — momentum 6M\n')
md.append('| wariant | kapitał końc. bez kill | maxDD % | Sharpe netto | P(kill 12 t.) | kapitał z kill |\n|---|---|---|---|---|---|')
a12 = {}
for name, gw, gd in [VARS[0], VARS[1], VARS[4], VARS[3]]:
    rn = simulate(LONGS, SHORTS, gw, gd, alloc=0.12, kill=False); rk = simulate(LONGS, SHORTS, gw, gd, alloc=0.12, kill=True)
    s = path_stats(rn['curve'], rn['wk'], nW); h, t, _, _ = kill_windows(LONGS, SHORTS, gw, gd, H=12, alloc=0.12)
    a12[name] = dict(final=s['final'], maxdd=s['maxdd_pct'], sharpe=s['sharpe'], k12=h / t, final_kill=rk['final'])
    md.append(f"| {name} | {s['final']:.1f} | {s['maxdd_pct']:.1f} | {s['sharpe']:.2f} | {100 * h / t:.1f}% | {rk['final']:.1f} |")
out['alloc12'] = a12

# ------------------------------------------------------------------ zapis
pd.DataFrame(dict(date_d0=mom.date_d0, date_d5=mom.date_d5, spread_pp=SPREAD, state_hys_d0=ST_HYS[D0], state_raw_d0=ST_RAW[D0],
                  g_hys_w=G_HYS_W, cap_wk_bez=simulate(LONGS, SHORTS, kill=False)['wk'], cap_wk_hist=simulate(LONGS, SHORTS, G_HYS_W, kill=False)['wk'],
                  cap_wk_hist_dzienna=simulate(LONGS, SHORTS, None, G_HYS_D, kill=False)['wk'])).to_csv(OUT_CSV, index=False)

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)): return None if (isinstance(o, float) and math.isnan(o)) else float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
json.dump(clean(out), open(OUT_JSON, 'w'), indent=1, ensure_ascii=False, default=str)
open(OUT_MD, 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))
