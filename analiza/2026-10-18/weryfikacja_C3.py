#!/usr/bin/env python3
"""
weryfikacja_C3.py — sceptyczna recenzja TWIERDZENIA C3 (koszt twardego stopu 10%).

Harness identyczny z bt_symulacja-wykonania.py (momentum 6M, TOP5/BOTTOM5 vs ^NDX, okna tygodniowe,
wejście = zamknięcie D0+1, wyjście = zamknięcie D5+1, 24% kapitału/noga, brutto bez kosztów).
Nowe elementy (próby obalenia):
 T1  stop na proxy intraday: low/high ≈ close × (1 ∓ k·σ60), k = 0,5 (i 1,0); realizacja na progu (bot: mid o 13:45/17:05)
     albo na zamknięciu (pesymistycznie); z reopen i bez.
 T2  koszt stopu osobno dla nóg LONG i SHORT (stop tylko na jednej stronie) i osobno w reżimie VIX>20 / ≤20 na D0.
 T3  kotwica stopu: cena D0 (teza) vs poziom D+1 (broker, jak app.py); oraz wejście D0 ze stopem.
 T4  ogon: p1/p5/p10 tygodniowego wyniku, CVaR5, najgorsze 4 tyg., maxDD, częstość kill switcha w oknach 12-tyg.,
     5. percentyl min. kapitału — czy stop poprawia ogon mimo gorszej średniej.
 T5  istotność: bootstrap różnic sparowanych (10 000), test znaku, obcięcie 5 najwiekszych |Δ|, podokresy (lata).
 T6  co stop ucina: zwrot od sesji przebicia −10% do wyjścia dla nóg momentum vs nóg losowych (long/short, VIX).
 T7  koszyki faktyczne W1–W7 (wyk_common.KOSZYKI) przez te same warianty (zamknięcia i proxy intraday).
"""
import json, math, sys
import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
OUT_MD = f'{BASE}/analiza/weryfikacja_C3_out.md'
OUT_JSON = f'{BASE}/analiza/weryfikacja_C3_wyniki.json'
OUT_CSV = f'{BASE}/analiza/weryfikacja_C3_serie.csv'

NON_CAND = {'^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV'}
NL = NS = 5
ALLOC = 0.24
KILL = 0.75
SEED = 20261018
RANDOM_EXEC = 200
BOOT = 10000

df = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
df = df[df['^NDX'].notna()]
df3 = df.ffill(limit=3)
cands = [c for c in df.columns if c not in NON_CAND]
dates = df.index
P = df3[cands].to_numpy(dtype=float)
PF = df3[cands].ffill().to_numpy(dtype=float)
NDX = df3['^NDX'].to_numpy(dtype=float)
VIX = df3['^VIX'].to_numpy(dtype=float)
nT, nS = P.shape
COL = {c: i for i, c in enumerate(cands)}
R = np.vstack([np.full((1, nS), np.nan), P[1:] / P[:-1] - 1])
SIG60 = pd.DataFrame(R).rolling(60, min_periods=40).std(ddof=1).to_numpy()
SIG60F = pd.DataFrame(SIG60).ffill().bfill().to_numpy()

iso = dates.isocalendar()
keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
last_idx = {}
for i, k in enumerate(keys):
    last_idx[k] = i
weeks = sorted(last_idx)
D0 = np.array([last_idx[w] for w in weeks[:-1]])
D5 = np.array([last_idx[w] for w in weeks[1:]])
nW = len(D0)
WR = P[D5] / P[D0] - 1
YEAR = np.array([dates[i].year for i in D0])
VIX0 = VIX[D0]


def mom_score(L=126):
    S = np.full((nW, nS), np.nan)
    for w, d0 in enumerate(D0):
        if d0 - L < 0:
            continue
        S[w] = P[d0] / P[d0 - L] - 1 - (NDX[d0] / NDX[d0 - L] - 1)
    return S


def select(S):
    longs, shorts = [], []
    for w in range(nW):
        s = S[w].copy()
        s[np.isnan(WR[w])] = np.nan
        E = min(D0[w] + 1, nT - 1); X = min(D5[w] + 1, nT - 1)
        s[np.isnan(P[E]) | np.isnan(P[X])] = np.nan
        ok = np.where(~np.isnan(s))[0]
        if len(ok) < 30:
            longs.append(None); shorts.append(None); continue
        order = ok[np.argsort(-s[ok], kind='stable')]
        longs.append(order[:NL]); shorts.append(order[-NS:])
    return longs, shorts


LONGS, SHORTS = select(mom_score(126))
widx = np.array([w for w in range(nW) if LONGS[w] is not None])
print(f'okna: {len(widx)} {dates[D0[widx[0]]].date()} → {dates[D5[widx[-1]]].date()}', file=sys.stderr)


# ----------------------------------------------------------------------------- silnik
class Cfg:
    def __init__(self, name, entry='pon', anchor='entry', stop=None, reopen=False, intraday=None, fill='close',
                 side='both', alloc=ALLOC, note=''):
        self.name, self.entry, self.anchor, self.stop, self.reopen = name, entry, anchor, stop, reopen
        self.intraday, self.fill, self.side, self.alloc, self.note = intraday, fill, side, alloc, note


def sim_window(w, cfg, C0=100.0, peak=None, kill=False):
    """Zwraca dict: gross (% C0), long_pp, short_pp (wkład nóg long / short w % C0), stops, reopens, daily (kapitał)."""
    legs = [(int(i), +1) for i in LONGS[w]] + [(int(i), -1) for i in SHORTS[w]]
    d0 = D0[w]
    if cfg.entry == 'd0':
        E, X = d0, D5[w]
    else:
        E, X = min(d0 + 1, nT - 1), min(D5[w] + 1, nT - 1)
    n = len(legs)
    idx = np.array([i for i, _ in legs]); d = np.array([dd for _, dd in legs], dtype=float)
    N = np.full(n, cfg.alloc * C0)
    pe = PF[E, idx].copy()                      # cena wejścia (poziom brokera)
    anchor = PF[d0, idx].copy() if cfg.anchor == 'd0' else pe.copy()
    thr = np.full(n, np.inf)
    if cfg.stop is not None:
        thr = np.full(n, cfg.stop)
        if cfg.side == 'long':
            thr[d < 0] = np.inf
        elif cfg.side == 'short':
            thr[d > 0] = np.inf
    k_intra = cfg.intraday
    is_open = np.ones(n, dtype=bool); pending = np.zeros(n, dtype=bool)
    realized = np.zeros(n); stops = reopens = 0
    daily = []; killed = False
    if peak is None:
        peak = C0
    for t in range(E + 1, X + 1):
        px = PF[t, idx]
        for j in range(n):
            if pending[j]:
                pending[j] = False
                if t < X:
                    is_open[j] = True; pe[j] = px[j]; anchor[j] = px[j]; reopens += 1
        # ruch od ceny wejścia (wynik) i od kotwicy (wyzwalacz)
        move = px / pe - 1
        adv_close = -d * (px / anchor - 1)
        if k_intra is not None:
            sig = SIG60F[t - 1, idx]                       # σ znana przed sesją
            ext = px * (1 - d * k_intra * sig)             # long: proxy low; short: proxy high
            adv_trig = -d * (ext / anchor - 1)
        else:
            adv_trig = adv_close
        for j in range(n):
            if not is_open[j] or thr[j] == np.inf:
                continue
            if adv_trig[j] >= thr[j]:
                if cfg.fill == 'thr' and k_intra is not None:
                    # realizacja na poziomie progu od kotwicy (nie gorzej niż zamknięcie, jeśli zamknięcie już poniżej)
                    # realizacja na poziomie progu od kotwicy (optymistycznie: bot łapie mid przy progu o 13:45/17:05; luki pomijane)
                    fill_px = anchor[j] * (1 - d[j] * thr[j])
                    mv = fill_px / pe[j] - 1
                else:
                    mv = move[j]
                realized[j] += N[j] * d[j] * mv; is_open[j] = False; stops += 1
                if cfg.reopen:
                    pending[j] = True
        unreal = np.where(is_open, N * d * move, 0.0)
        Ct = C0 + realized.sum() + unreal.sum()
        peak = max(peak, Ct)
        daily.append(Ct)
        if kill and Ct < KILL * peak:
            realized += unreal; is_open[:] = False; pending[:] = False; killed = True
            break
    if not killed:
        px = PF[X, idx]; move = px / pe - 1
        realized += np.where(is_open, N * d * move, 0.0)
    return dict(gross=100 * realized.sum() / C0, long_pp=100 * realized[d > 0].sum() / C0,
                short_pp=100 * realized[d < 0].sum() / C0, stops=stops, reopens=reopens, daily=daily,
                killed=killed, peak=peak, per_leg=100 * realized / C0)


def run(cfg, ws=None):
    ws = widx if ws is None else ws
    rows = [sim_window(w, cfg) for w in ws]
    return dict(cfg=cfg, gross=np.array([r['gross'] for r in rows]), long=np.array([r['long_pp'] for r in rows]),
                short=np.array([r['short_pp'] for r in rows]), stops=sum(r['stops'] for r in rows),
                reopens=sum(r['reopens'] for r in rows), stops_w=np.array([r['stops'] for r in rows]))


def kill12(cfg, H=12):
    hits = 0; total = 0; minC = []
    for s in range(0, len(widx) - H + 1):
        C = 100.0; peak = 100.0; killed = False; mn = 100.0
        for w in widx[s:s + H]:
            r = sim_window(w, cfg, C0=C, peak=peak, kill=True)
            peak = r['peak']; C = C * (1 + r['gross'] / 100)
            if r['daily']:
                mn = min(mn, min(r['daily']))
            if r['killed']:
                killed = True; break
        total += 1; hits += killed; minC.append(mn)
    return hits, total, np.array(minC)


def tstat(x):
    x = np.asarray(x, float)
    return x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 1 and x.std(ddof=1) > 0 else float('nan')


def tail(x):
    x = np.asarray(x, float)
    cap = np.concatenate([[100], 100 * np.cumprod(1 + x / 100)])
    dd = (1 - cap / np.maximum.accumulate(cap)).max() * 100
    k = max(1, int(round(0.05 * len(x))))
    srt = np.sort(x)
    roll4 = pd.Series(x).rolling(4).sum().min()
    return dict(mean=x.mean(), sigma=x.std(ddof=1), t=tstat(x), p1=np.percentile(x, 1), p5=np.percentile(x, 5),
                p10=np.percentile(x, 10), min=x.min(), cvar5=srt[:k].mean(), worst4=roll4, maxdd=dd,
                skew=float(pd.Series(x).skew()), kurt=float(pd.Series(x).kurt()), cum=cap[-1])


def boot_ci(d, B=BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float); n = len(d)
    means = np.array([d[rng.integers(0, n, n)].mean() for _ in range(B)])
    return np.percentile(means, 2.5), np.percentile(means, 97.5), (means > 0).mean()


def sign_test(d):
    d = np.asarray(d, float); d = d[d != 0]
    n = len(d); k = int((d > 0).sum())
    # dwustronny dokładny test dwumianowy
    lo = min(k, n - k)
    p = sum(math.comb(n, i) for i in range(0, lo + 1)) / 2 ** n * 2
    return n, k, min(1.0, p)


# ----------------------------------------------------------------------------- warianty
V = [
    Cfg('v2_bez_stopu', note='baza: wejście D0+1, bez stopu'),
    Cfg('v3_stop10_close', stop=0.10, note='stop 10% na zamknięciu, bez reopen (= v3 z fazy 2)'),
    Cfg('v4_stop10_close_reopen', stop=0.10, reopen=True, note='stop 10% na zamknięciu + reopen (= v4, app.py)'),
    # T1 intraday proxy
    Cfg('t1_intra05_thr', stop=0.10, intraday=0.5, fill='thr', note='proxy low/high = close·(1∓0,5σ60); realizacja NA PROGU'),
    Cfg('t1_intra05_thr_reopen', stop=0.10, intraday=0.5, fill='thr', reopen=True, note='j.w. + reopen'),
    Cfg('t1_intra05_close', stop=0.10, intraday=0.5, fill='close', note='proxy 0,5σ, realizacja na zamknięciu (pesymistycznie)'),
    Cfg('t1_intra05_close_reopen', stop=0.10, intraday=0.5, fill='close', reopen=True, note='j.w. + reopen'),
    Cfg('t1_intra10_thr', stop=0.10, intraday=1.0, fill='thr', note='proxy 1,0σ (szerszy zakres dnia), realizacja na progu'),
    Cfg('t1_intra10_thr_reopen', stop=0.10, intraday=1.0, fill='thr', reopen=True, note='j.w. + reopen'),
    # T2 strony
    Cfg('t2_stop10_long_only', stop=0.10, note='stop 10% tylko na nogach LONG (zamknięcia)'),
    Cfg('t2_stop10_short_only', stop=0.10, note='stop 10% tylko na nogach SHORT (zamknięcia)'),
    Cfg('t2_intra05_thr_long_only', stop=0.10, intraday=0.5, fill='thr', side='long', note='proxy intraday, tylko LONG'),
    Cfg('t2_intra05_thr_short_only', stop=0.10, intraday=0.5, fill='thr', side='short', note='proxy intraday, tylko SHORT'),
    # T3 kotwica / wejście
    Cfg('t3_stop10_anchor_d0', stop=0.10, anchor='d0', note='wejście D0+1, stop liczony od ceny D0 (teza), zamknięcia'),
    Cfg('t3_stop10_anchor_d0_reopen', stop=0.10, anchor='d0', reopen=True, note='j.w. + reopen'),
    Cfg('t3_intra05_thr_anchor_d0', stop=0.10, anchor='d0', intraday=0.5, fill='thr', note='kotwica D0, proxy intraday, próg'),
    Cfg('v1_d0_bez_stopu', entry='d0', note='wejście D0 (piątek), bez stopu'),
    Cfg('t3_d0_stop10_close', entry='d0', stop=0.10, note='wejście D0, stop 10% zamknięcia'),
    Cfg('t3_d0_intra05_thr', entry='d0', stop=0.10, intraday=0.5, fill='thr', note='wejście D0, proxy intraday, próg'),
    # progi
    Cfg('t_stop15_intra05_thr', stop=0.15, intraday=0.5, fill='thr', note='stop 15%, proxy intraday, próg'),
    Cfg('t_stop07_intra05_thr', stop=0.07, intraday=0.5, fill='thr', note='stop 7%, proxy intraday, próg'),
    Cfg('t_stop20_close', stop=0.20, note='stop 20% zamknięcia'),
]
V[1].side = 'both'
V[9].side = 'long'; V[10].side = 'short'
VB = {v.name: v for v in V}

RES = {v.name: run(v) for v in V}
for nm, r in RES.items():
    print(f"  {nm:32} śr {r['gross'].mean():+.3f}  t {tstat(r['gross']):+.2f}  stopy {r['stops']:4d} reopen {r['reopens']:4d}", file=sys.stderr)

base = RES['v2_bez_stopu']['gross']
L = []
L.append('# weryfikacja_C3 — wyniki skryptu\n')
L.append(f'Okna momentum 6M: n={len(widx)} ({dates[D0[widx[0]]].date()} → {dates[D5[widx[-1]]].date()}); jednostki: % kapitału na okno (brutto, 24%/noga).\n')

# --- tabela główna: koszt vs v2
L.append('## 1. Koszt wariantu stopu wobec braku stopu (Δ = wariant − v2, sparowane po oknach)\n')
L.append('| wariant | śr. pp | t | stopy | reopen | Δ śr. pp/tydz | t Δ | boot 95% CI Δ | P(Δ>0) boot | test znaku n/k/p | Δ bez 5 najw. abs. | okna ze stopem | Δ śr. w oknach ze stopem | udział okien, gdzie stop pomógł |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
SUMM = {}
for nm, r in RES.items():
    g = r['gross']; d = g - base
    lo, hi, pp = boot_ci(d)
    n_s, k_s, p_s = sign_test(d)
    srt = np.argsort(-np.abs(d)); d_trim = np.delete(d, srt[:5])
    sw = r['stops_w'] > 0
    SUMM[nm] = dict(mean=float(g.mean()), t=float(tstat(g)), stops=int(r['stops']), reopens=int(r['reopens']),
                    d_mean=float(d.mean()), d_t=float(tstat(d)) if d.std() > 0 else None, ci=(float(lo), float(hi)),
                    p_pos=float(pp), sign=(int(n_s), int(k_s), float(p_s)), d_trim=float(d_trim.mean()),
                    windows_with_stop=int(sw.sum()), d_in_stop_windows=float(d[sw].mean()) if sw.any() else None,
                    helped_share=float((d[sw] > 0).mean()) if sw.any() else None)
    L.append(f"| {nm} | {g.mean():+.3f} | {tstat(g):+.2f} | {r['stops']} | {r['reopens']} | {d.mean():+.3f} | "
             f"{(tstat(d) if d.std() > 0 else float('nan')):+.2f} | {lo:+.3f}…{hi:+.3f} | {pp:.3f} | {n_s}/{k_s}/{p_s:.3f} | {d_trim.mean():+.3f} | "
             f"{sw.sum()} | {(d[sw].mean() if sw.any() else float('nan')):+.3f} | {(100 * (d[sw] > 0).mean() if sw.any() else float('nan')):.0f}% |")
L.append('')

# --- T2: long/short rozbicie kosztu i reżim VIX
L.append('## 2. Skąd pochodzi koszt: strona nogi i reżim VIX (Δ wobec v2, pp/tydz., t w nawiasie)\n')
L.append('| wariant | Δ nogi LONG | Δ nogi SHORT | Δ VIX>20 (n) | Δ VIX≤20 (n) | Δ 2022 | Δ 2023 | Δ 2024 | Δ 2025 | Δ 2026 |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
vixw = VIX0[widx]; yrw = YEAR[widx]
B2 = {}
for nm in ('v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen', 't1_intra10_thr',
           't2_stop10_long_only', 't2_stop10_short_only', 't3_stop10_anchor_d0', 't_stop15_intra05_thr', 't_stop20_close'):
    r = RES[nm]
    dl = r['long'] - RES['v2_bez_stopu']['long']; ds = r['short'] - RES['v2_bez_stopu']['short']; d = r['gross'] - base
    def cell(x):
        return f"{x.mean():+.3f} ({tstat(x):+.1f})" if len(x) > 2 and x.std() > 0 else f"{x.mean():+.3f}"
    cells = [cell(dl), cell(ds), cell(d[vixw > 20]) + f" ({int((vixw > 20).sum())})", cell(d[vixw <= 20]) + f" ({int((vixw <= 20).sum())})"]
    for y in (2022, 2023, 2024, 2025, 2026):
        cells.append(cell(d[yrw == y]))
    B2[nm] = dict(long=float(dl.mean()), long_t=float(tstat(dl)), short=float(ds.mean()), short_t=float(tstat(ds)),
                  vix_hi=float(d[vixw > 20].mean()), vix_hi_t=float(tstat(d[vixw > 20])), vix_lo=float(d[vixw <= 20].mean()),
                  vix_lo_t=float(tstat(d[vixw <= 20])), years={int(y): float(d[yrw == y].mean()) for y in (2022, 2023, 2024, 2025, 2026)})
    L.append(f"| {nm} | " + ' | '.join(cells) + ' |')
L.append('')
# liczba stopów long vs short
cnt = {'long': 0, 'short': 0}
for w in widx:
    r3 = sim_window(w, VB['t2_stop10_long_only']); cnt['long'] += r3['stops']
    r4 = sim_window(w, VB['t2_stop10_short_only']); cnt['short'] += r4['stops']
L.append(f"Liczba stopów 10% (zamknięcia) na nogach LONG: {cnt['long']}, SHORT: {cnt['short']} (na {5 * len(widx)} nóg każdej strony).\n")

# --- T4: ogon
L.append('## 3. Ogon rozkładu tygodniowego wyniku i kill switch (brutto)\n')
L.append('| wariant | śr. | σ | p1 | p5 | p10 | min | CVaR5 | najgorsze 4 tyg. (suma) | maxDD % | skośność | kurtoza | kapitał końc. | kill w oknach 12-tyg. | 5. pct min kapitału (12 tyg.) | mediana min |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
T4 = {}
for nm in ('v2_bez_stopu', 'v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen',
           't1_intra10_thr', 't2_stop10_long_only', 't2_stop10_short_only', 't3_stop10_anchor_d0', 't_stop15_intra05_thr',
           't_stop07_intra05_thr', 't_stop20_close'):
    tl = tail(RES[nm]['gross'])
    h, tot, minC = kill12(VB[nm])
    tl.update(kill_pct=100 * h / tot, kill_hits=h, kill_total=tot, minC_p5=float(np.percentile(minC, 5)), minC_med=float(np.median(minC)))
    T4[nm] = {k: float(v) for k, v in tl.items()}
    L.append(f"| {nm} | {tl['mean']:+.2f} | {tl['sigma']:.2f} | {tl['p1']:+.1f} | {tl['p5']:+.1f} | {tl['p10']:+.1f} | {tl['min']:+.1f} | {tl['cvar5']:+.1f} | "
             f"{tl['worst4']:+.1f} | {tl['maxdd']:.1f} | {tl['skew']:+.2f} | {tl['kurt']:+.2f} | {tl['cum']:.0f} | {h}/{tot} = {tl['kill_pct']:.1f}% | {tl['minC_p5']:.1f} | {tl['minC_med']:.1f} |")
    print(f"  tail {nm}: p5 {tl['p5']:+.2f} min {tl['min']:+.1f} kill12 {tl['kill_pct']:.1f}%", file=sys.stderr)
L.append('')
# ogon: różnice sparowane w 10% najgorszych oknach v2
worst_mask = base <= np.percentile(base, 10)
L.append('W 10% najgorszych okien bazy (v2) — średnia Δ wariantu wobec v2 (pp): ' + '; '.join(
    f"{nm} {(RES[nm]['gross'] - base)[worst_mask].mean():+.2f}" for nm in ('v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen', 't_stop15_intra05_thr')) + '\n')
best_mask = base >= np.percentile(base, 90)
L.append('W 10% najlepszych okien bazy (v2): ' + '; '.join(
    f"{nm} {(RES[nm]['gross'] - base)[best_mask].mean():+.2f}" for nm in ('v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen', 't_stop15_intra05_thr')) + '\n')

# --- T6: co stop ucina — zwrot po przebiciu do wyjścia, nogi momentum vs losowe
L.append('## 4. Co stop ucina: zwrot nogi od sesji przebicia −10% (zamknięcie) do wyjścia (kierunek tezy, %)\n')
rng = np.random.default_rng(SEED + 7)


def after_hit(legs_fn, label):
    out = {'long': [], 'short': [], 'vix_hi': [], 'vix_lo': [], 'all': [], 'day': []}
    n_legs = 0
    for w in widx:
        E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
        for (i, dd) in legs_fn(w):
            n_legs += 1
            pe = PF[E, i]
            for t in range(E + 1, X + 1):
                if -dd * (PF[t, i] / pe - 1) >= 0.10:
                    rest = dd * (PF[X, i] / PF[t, i] - 1) * 100 if t < X else 0.0
                    out['all'].append(rest); out['day'].append(t - E)
                    out['long' if dd > 0 else 'short'].append(rest)
                    out['vix_hi' if VIX0[w] > 20 else 'vix_lo'].append(rest)
                    break
    rows = []
    for k in ('all', 'long', 'short', 'vix_hi', 'vix_lo'):
        x = np.array(out[k])
        if len(x) == 0:
            rows.append(f"{k}: n=0"); continue
        rows.append(f"{k}: n={len(x)} ({100 * len(x) / max(1, n_legs) if k == 'all' else float('nan'):.1f}% nóg) śr {x.mean():+.2f}% med {np.median(x):+.2f}% sd {x.std(ddof=1):.2f} t {tstat(x):+.2f}; udział dalszych strat {100 * (x < 0).mean():.0f}%")
    return label, rows, out


lab, rows, HIT_M = after_hit(lambda w: [(int(i), +1) for i in LONGS[w]] + [(int(i), -1) for i in SHORTS[w]], 'momentum 6M')
L.append(f'**{lab}**: ' + ' | '.join(rows))
# losowe nogi: 10 losowań na okno
def rand_legs(w):
    E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
    ok = np.where(~np.isnan(WR[w]) & ~np.isnan(P[E]) & ~np.isnan(P[X]))[0]
    pick = rng.choice(ok, NL + NS, replace=False)
    return [(int(i), +1) for i in pick[:NL]] + [(int(i), -1) for i in pick[NL:]]
lab, rows, HIT_R = after_hit(rand_legs, 'losowe nogi 5/5')
L.append(f'**{lab}**: ' + ' | '.join(rows))
# mediana dnia przebicia
dm = np.array(HIT_M['day'])
L.append(f"Dzień przebicia (sesje od wejścia) w nogach momentum: rozkład {np.bincount(dm, minlength=6)[1:].tolist()} dla sesji 1..5+.\n")
T6 = dict(mom={k: dict(n=len(v), mean=float(np.mean(v)) if v else None, t=float(tstat(np.array(v))) if len(v) > 2 else None) for k, v in HIT_M.items() if k != 'day'},
          rand={k: dict(n=len(v), mean=float(np.mean(v)) if v else None, t=float(tstat(np.array(v))) if len(v) > 2 else None) for k, v in HIT_R.items() if k != 'day'})

# --- B5: losowe strategie przez proxy intraday (neutralność na szumie)
L.append('## 5. Losowe strategie 5/5 przez warianty (koszt reguły na szumie)\n')
rng2 = np.random.default_rng(SEED + 1)
RLONGS, RSHORTS = LONGS, SHORTS
EXB = {k: [] for k in ('v2_bez_stopu', 'v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen')}
saveL, saveS = LONGS, SHORTS
for b in range(RANDOM_EXEC):
    LONGS = list(saveL); SHORTS = list(saveS)
    for w in widx:
        E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
        ok = np.where(~np.isnan(WR[w]) & ~np.isnan(P[E]) & ~np.isnan(P[X]))[0]
        pick = rng2.choice(ok, NL + NS, replace=False)
        LONGS[w] = pick[:NL]; SHORTS[w] = pick[NL:]
    for k in EXB:
        r = run(VB[k])
        EXB[k].append(dict(mean=r['gross'].mean(), p5=np.percentile(r['gross'], 5), stops=r['stops'], sigma=r['gross'].std(ddof=1)))
LONGS, SHORTS = saveL, saveS
L.append('| wariant | śr. pp/tydz (5–95%) | Δ vs v2 śr. | udział strategii, gdzie Δ<0 | p5 tyg. śr. | σ śr. | stopy śr. |')
L.append('|---|---|---|---|---|---|---|')
B5 = {}
for k, lst in EXB.items():
    m = np.array([x['mean'] for x in lst]); m0 = np.array([x['mean'] for x in EXB['v2_bez_stopu']])
    p5 = np.array([x['p5'] for x in lst]); s = np.array([x['sigma'] for x in lst]); st_ = np.array([x['stops'] for x in lst])
    B5[k] = dict(mean=float(m.mean()), d=float((m - m0).mean()), neg=float(((m - m0) < 0).mean()), p5=float(p5.mean()), sigma=float(s.mean()), stops=float(st_.mean()))
    L.append(f"| {k} | {m.mean():+.3f} ({np.percentile(m, 5):+.2f}…{np.percentile(m, 95):+.2f}) | {(m - m0).mean():+.4f} | {100 * ((m - m0) < 0).mean():.0f}% | {p5.mean():+.2f} | {s.mean():.2f} | {st_.mean():.0f} |")
L.append('')

# --- T7: koszyki faktyczne W1–W7
L.append('## 6. Koszyki faktyczne W1–W7 (wejście = zamknięcie pierwszej sesji po D0, wyjście = zamknięcie rozliczenia; % kapitału, 24%/noga)\n')
KOSZYKI = {
    'W1': dict(d0='2026-08-26', entry='2026-08-27', settle='2026-08-28', long=['MU', 'LITE', 'CEG', 'AMD', 'MSFT'], short=['INTU', 'WDAY', 'APP', 'TSLA', 'CMCSA']),
    'W2': dict(d0='2026-08-28', entry='2026-08-31', settle='2026-09-04', long=['MU', 'NVDA', 'MSFT', 'AMD', 'CEG'], short=['INTU', 'APP', 'TSLA', 'CMCSA', 'PEP']),
    'W3': dict(d0='2026-09-04', entry='2026-09-08', settle='2026-09-11', long=['MU', 'NVDA', 'AMD', 'AVGO', 'STX'], short=['TSLA', 'INTU', 'SBUX', 'APP', 'CMCSA']),
    'W4': dict(d0='2026-09-11', entry='2026-09-14', settle='2026-09-28', long=['MU', 'AMD', 'AVGO', 'MRVL', 'LITE'], short=['INTU', 'SBUX', 'CMCSA', 'APP', 'ADSK']),
    'W5': dict(d0='2026-09-28', entry='2026-09-29', settle='2026-10-02', long=['MU', 'AMD', 'ALAB', 'STX', 'TER'], short=['SBUX', 'NFLX', 'PEP', 'CMCSA', 'APP']),
    'W6': dict(d0='2026-10-02', entry='2026-10-05', settle='2026-10-09', long=['MU', 'LITE', 'TER', 'AMAT', 'AMD'], short=['APP', 'NFLX', 'PAYX', 'CMCSA', 'SBUX']),
    'W7': dict(d0='2026-10-09', entry='2026-10-12', settle='2026-10-16', long=['MU', 'LITE', 'MRVL', 'PANW', 'CSCO'], short=['CMCSA', 'SBUX', 'PEP', 'TMUS', 'APP']),
}
DI = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(dates)}


def sim_basket(kz, cfg):
    idx = np.array([COL[t] for t in kz['long'] + kz['short']]); d = np.array([1.0] * 5 + [-1.0] * 5)
    E, X, d0 = DI[kz['entry']], DI[kz['settle']], DI[kz['d0']]
    n = 10; N = np.full(n, cfg.alloc * 100)
    pe = PF[E, idx].copy(); anchor = PF[d0, idx].copy() if cfg.anchor == 'd0' else pe.copy()
    thr = np.full(n, cfg.stop if cfg.stop else np.inf)
    if cfg.side == 'long': thr[d < 0] = np.inf
    if cfg.side == 'short': thr[d > 0] = np.inf
    is_open = np.ones(n, bool); pending = np.zeros(n, bool); realized = np.zeros(n); stops = reopens = 0
    for t in range(E + 1, X + 1):
        px = PF[t, idx]
        for j in range(n):
            if pending[j]:
                pending[j] = False
                if t < X:
                    is_open[j] = True; pe[j] = px[j]; anchor[j] = px[j]; reopens += 1
        move = px / pe - 1
        if cfg.intraday is not None:
            ext = px * (1 - d * cfg.intraday * SIG60F[t - 1, idx]); adv = -d * (ext / anchor - 1)
        else:
            adv = -d * (px / anchor - 1)
        for j in range(n):
            if is_open[j] and adv[j] >= thr[j]:
                if cfg.fill == 'thr' and cfg.intraday is not None:
                    mv = anchor[j] * (1 - d[j] * thr[j]) / pe[j] - 1
                else:
                    mv = move[j]
                realized[j] += N[j] * d[j] * mv; is_open[j] = False; stops += 1
                if cfg.reopen: pending[j] = True
    px = PF[X, idx]; move = px / pe - 1
    realized += np.where(is_open, N * d * move, 0.0)
    return realized.sum(), stops, reopens


names7 = ['v2_bez_stopu', 'v3_stop10_close', 'v4_stop10_close_reopen', 't1_intra05_thr', 't1_intra05_thr_reopen', 't1_intra05_close',
          't1_intra10_thr', 't3_stop10_anchor_d0', 't_stop15_intra05_thr', 't_stop20_close']
L.append('| wariant | ' + ' | '.join(KOSZYKI) + ' | suma | stopy | reopen |')
L.append('|---|' + '---|' * (len(KOSZYKI) + 3))
T7 = {}
for nm in names7:
    cells = []; tot = 0; st_ = 0; ro = 0
    for wk, kz in KOSZYKI.items():
        g, s, r = sim_basket(kz, VB[nm]); tot += g; st_ += s; ro += r
        cells.append(f"{g:+.2f}" + (f" ({s}s/{r}r)" if s else ''))
    T7[nm] = dict(sum=float(tot), stops=int(st_), reopens=int(ro))
    L.append(f"| {nm} | " + ' | '.join(cells) + f" | {tot:+.2f} | {st_} | {ro} |")
L.append('')

# --- CSV serii
rows_csv = []
for k, w in enumerate(widx):
    row = dict(okno=k, d0=dates[D0[w]].date(), d5=dates[D5[w]].date(), vix_d0=round(VIX0[w], 2),
               long=' '.join(cands[i] for i in LONGS[w]), short=' '.join(cands[i] for i in SHORTS[w]))
    for nm, r in RES.items():
        row[nm] = round(r['gross'][k], 4); row[nm + '_stopy'] = int(r['stops_w'][k])
    rows_csv.append(row)
pd.DataFrame(rows_csv).to_csv(OUT_CSV, index=False)

open(OUT_MD, 'w').write('\n'.join(L))
json.dump(dict(summary=SUMM, by_side_regime=B2, tail=T4, after_hit=T6, random=B5, baskets_W1_W7=T7, n_windows=int(len(widx))),
          open(OUT_JSON, 'w'), indent=1, ensure_ascii=False, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, np.integer) else str(o))
print('\n'.join(L))
