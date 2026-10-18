#!/usr/bin/env python3
"""
bt_symulacja-wykonania.py — symulacja WARSTWY WYKONAWCZEJ bota (app.py) na dziennych zamknięciach.

Pytanie: ile kosztuje każdy element wykonania (opóźnienie wejścia, twardy stop od ceny wejścia,
ponowne otwarcie po stopie, sizing, kill switch) — niezależnie od jakości sygnału.

(A) faktyczne koszyki 2026-W4…W7 (koszyki_historia.json; W4 okno 11 sesji, W5 4 sesje),
(B) strategia momentum 6M tygodniowa (126 sesji, TOP5/BOTTOM5 relatywnie do ^NDX — identyczna
    z wariantem a_6M w bt_momentum.py) na oknach 2022-04…2026-10.

Warianty wykonania (sizing bazowy 24% kapitału na nogę, gross 240%, kapitał 100,
kill switch 25% od kroczącego szczytu, szczyt nie niżej niż kapitał startowy — jak app.py):
 (1) bez stopów, wejście D0 (zamknięcie piątku) → wyjście D5 (zamknięcie kolejnego piątku);
 (2) wejście D0+1 (zamknięcie poniedziałku) → wyjście D5+1 (następna rotacja), bez stopów;
 (3) jak (2) + stop 10% od wejścia na zamknięciu, pozycja zamknięta i NIE otwierana ponownie;
 (4) jak (3), ale ponowne otwarcie na zamknięciu następnej sesji (app.py bez wpisu exclude:
     book.pop tylko w tym biegu, w następnym biegu desired_book znów ją otwiera);
 (5) stop 15% bez reopen; (5b) stop 15% z reopen;
 (6) stop 2,5σ dziennej nogi (σ 60 sesji przed wejściem) bez reopen; (6b) z reopen;
 (7) REDUCE 50% po przekroczeniu 2σ od wejścia (zamiast stopu), bez reopen;
 (8) bez stopów, wagi ∝ 1/σ nogi, cel σ dziennej kapitału 1,5% (kowariancja 60 sesji),
     gross ograniczony do 300% (MARGIN_BUDGET 0,60 / depozyt 20%);
 (9) (8) + stop 10% z reopen (obecna logika stopu na innym sizingu).

Konwencje wspólnego harnessu: okna tygodniowe = ostatnia sesja tygodnia → ostatnia sesja
następnego tygodnia; spread_pp = śr. 5 long (zwrot − ^NDX) + śr. 5 short (−(zwrot − ^NDX));
przy równych wagach 24% zwrot kapitału = 1,2 × spread_pp (udział ^NDX znosi się).
Koszty: 0,10% nominału nogi za każde otwarcie (rotacja z turnoverem + reopen) + finansowanie
6%/rok od gross za dni kalendarzowe okna. Baseline: 2000 losowych koszyków 5/5 na okno.
Sygnał liczony wyłącznie z danych do D0 (bez look-ahead).
"""
import json, math, sys
import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
KOSZ = f'{BASE}/analiza/koszyki_historia.json'
NAME = 'symulacja-wykonania'
OUT_SERIE = f'{BASE}/analiza/bt_{NAME}_serie.csv'
OUT_MD = f'{BASE}/analiza/bt_{NAME}.md'
OUT_JSON = f'{BASE}/analiza/bt_{NAME}_summary.json'

NON_CAND = {'^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV'}
NL = NS = 5
ALLOC = 0.24
KILL = 0.75
START = 100.0
COST_LEG = 0.001
FIN_RATE = 0.06
SIGMA_TARGET = 0.015
GROSS_CAP = 3.0
MIN_RANDOM = 2000
RANDOM_EXEC = 200
SEED = 20261018

# ----------------------------------------------------------------------------- dane
df = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
df = df[df['^NDX'].notna()]
df3 = df.ffill(limit=3)                       # pojedyncze luki (święta w jednym źródle)
cands = [c for c in df.columns if c not in NON_CAND]
dates = df.index
P = df3[cands].to_numpy(dtype=float)          # ceny do selekcji (NaN = brak notowania)
PF = df3[cands].ffill().to_numpy(dtype=float)  # ceny do symulacji ścieżki (bez dziur w środku okna)
NDX = df3['^NDX'].to_numpy(dtype=float)
VIX = df3['^VIX'].to_numpy(dtype=float)
MA200 = pd.Series(NDX).rolling(200).mean().to_numpy()
nT, nS = P.shape
COL = {c: i for i, c in enumerate(cands)}

R = np.vstack([np.full((1, nS), np.nan), P[1:] / P[:-1] - 1])      # zwrot z t-1 na t
SIG60 = pd.DataFrame(R).rolling(60, min_periods=40).std(ddof=1).to_numpy()  # σ dzienna do dnia t (włącznie)

# okna tygodniowe
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
WN = NDX[D5] / NDX[D0] - 1
EX = WR - WN[:, None]
YEAR = np.array([dates[i].year for i in D0])
VIX0 = VIX[D0]
ABOVE = np.where(np.isnan(MA200[D0]), np.nan, (NDX[D0] > MA200[D0]).astype(float))


# ----------------------------------------------------------------------------- silnik wykonania
class Cfg:
    def __init__(self, name, delay=1, stop=None, reopen=False, sigma_stop=None, reduce_sigma=None,
                 sizing='equal', alloc=ALLOC, note=''):
        self.name, self.delay, self.stop, self.reopen = name, delay, stop, reopen
        self.sigma_stop, self.reduce_sigma, self.sizing, self.note = sigma_stop, reduce_sigma, sizing, note
        self.alloc = alloc


VARIANTS = [
    Cfg('v1_D0_bez_stopow', delay=0, note='wejście D0 (piątek), wyjście D5; = 1,2 × spread_pp harnessu'),
    Cfg('v2_Pon_bez_stopow', note='wejście D0+1 (poniedziałek), wyjście D5+1 (następna rotacja)'),
    Cfg('v3_stop10_bez_reopen', stop=0.10, note='stop 10% od wejścia na zamknięciu, bez ponownego otwarcia'),
    Cfg('v4_stop10_reopen', stop=0.10, reopen=True, note='stop 10% + reopen następnej sesji (app.py bez exclude)'),
    Cfg('v5_stop15_bez_reopen', stop=0.15, note='stop 15% bez reopen'),
    Cfg('v5b_stop15_reopen', stop=0.15, reopen=True, note='stop 15% z reopen'),
    Cfg('v6_stop2.5sig_bez_reopen', sigma_stop=2.5, note='stop 2,5σ60 dziennej nogi od wejścia, bez reopen'),
    Cfg('v6b_stop2.5sig_reopen', sigma_stop=2.5, reopen=True, note='stop 2,5σ60 z reopen'),
    Cfg('v7_reduce50_2sig', reduce_sigma=2.0, note='REDUCE 50% po 2σ60 przeciw tezie, bez stopu'),
    Cfg('v8_inv_sigma_1.5pct', sizing='invsigma', note='bez stopów, wagi ∝ 1/σ, cel σ dz. kapitału 1,5%, gross ≤ 300%'),
    Cfg('v9_inv_sigma_stop10_reopen', sizing='invsigma', stop=0.10, reopen=True, note='(8) + stop 10% z reopen'),
    Cfg('v10_alloc12_bez_stopow', alloc=0.12, note='jak (2), ale ALLOC_PCT=0,12 (gross 120%) — dodatkowy wariant sizingowy'),
    Cfg('v11_alloc16_bez_stopow', alloc=0.16, note='jak (2), ale ALLOC_PCT=0,16 (gross 160%)'),
    Cfg('v12_alloc12_stop10_reopen', alloc=0.12, stop=0.10, reopen=True, note='ALLOC_PCT=0,12 + obecny stop 10% z reopen'),
]
VBY = {v.name: v for v in VARIANTS}


def weights(legs, E, cfg):
    """legs = [(idx, dir)], E = indeks sesji wejścia. Zwraca wagi (ułamek kapitału) i gross."""
    n = len(legs)
    if cfg.sizing == 'equal':
        return np.full(n, cfg.alloc), cfg.alloc * n
    sig = np.array([SIG60[E, i] for i, _ in legs])
    if np.isnan(sig).any():
        sig = np.where(np.isnan(sig), np.nanmedian(sig) if not np.isnan(sig).all() else 0.02, sig)
    sig = np.maximum(sig, 0.004)
    w = 1.0 / sig
    # kowariancja 60 sesji podpisanych zwrotów nóg (long +, short −)
    rows = []
    for (i, d) in legs:
        r = R[E - 59:E + 1, i] * d
        rows.append(r)
    M = np.array(rows)
    M = np.where(np.isnan(M), 0.0, M)
    C = np.cov(M, ddof=1)
    var = float(w @ C @ w)
    if var <= 0:
        var = float(np.sum((w * sig) ** 2))
    k = SIGMA_TARGET / math.sqrt(var)
    w = w * k
    gross = w.sum()
    if gross > GROSS_CAP:
        w = w * GROSS_CAP / gross
        gross = GROSS_CAP
    return w, gross


def sim_window(legs, E, X, C0, cfg, peak, prev_set, kill=True):
    """Symulacja jednego okna na zamknięciach dziennych E..X.
    legs: [(idx, dir)]; C0 kapitał na starcie; peak kroczący szczyt; prev_set zbiór (idx,dir) z poprzedniego
    okna (turnover). Zwraca słownik z wynikiem brutto/netto (% C0), kosztami, zliczeniami i flagą kill."""
    n = len(legs)
    w, gross = weights(legs, E, cfg)
    N = w * C0
    pe = np.array([PF[E, i] for i, _ in legs])
    d = np.array([dd for _, dd in legs], dtype=float)
    thr = np.full(n, np.inf)
    if cfg.stop is not None:
        thr = np.full(n, cfg.stop)
    elif cfg.sigma_stop is not None:
        s = np.array([SIG60[E, i] for i, _ in legs]); s = np.where(np.isnan(s), 0.02, s)
        thr = cfg.sigma_stop * s
    red_thr = None
    if cfg.reduce_sigma is not None:
        s = np.array([SIG60[E, i] for i, _ in legs]); s = np.where(np.isnan(s), 0.02, s)
        red_thr = cfg.reduce_sigma * s
    f = np.ones(n)                      # mnożnik wielkości (REDUCE → 0,5)
    is_open = np.ones(n, dtype=bool)
    pending = np.zeros(n, dtype=bool)
    realized = np.zeros(n)
    cost = sum(COST_LEG * N[j] for j, lg in enumerate(legs) if lg not in prev_set)
    stops = reopens = reduces = 0
    killed = False
    kill_day = None
    daily = []
    for t in range(E + 1, X + 1):
        px = np.array([PF[t, i] for i, _ in legs])
        # reopen z poprzedniej sesji (bot otwiera w następnym biegu, gdy ticker nadal w book)
        for j in range(n):
            if pending[j]:
                pending[j] = False
                if t < X:               # na sesji wyjścia nie ma sensu otwierać — rotacja i tak zamyka
                    is_open[j] = True; pe[j] = px[j]; cost += COST_LEG * N[j] * f[j]; reopens += 1
        move = px / pe - 1
        adverse = -d * move
        for j in range(n):
            if not is_open[j]:
                continue
            if red_thr is not None and f[j] == 1.0 and adverse[j] >= red_thr[j]:
                realized[j] += N[j] * 0.5 * d[j] * move[j]; f[j] = 0.5; reduces += 1
            if adverse[j] >= thr[j]:
                realized[j] += N[j] * f[j] * d[j] * move[j]; is_open[j] = False; stops += 1
                if cfg.reopen:
                    pending[j] = True
        unreal = np.where(is_open, N * f * d * move, 0.0)
        Ct = C0 + realized.sum() + unreal.sum()
        peak = max(peak, Ct)
        if kill and Ct < KILL * peak:
            realized += unreal; is_open[:] = False; pending[:] = False
            killed = True; kill_day = t
            daily.append(Ct)
            break
        daily.append(Ct)
    if not killed:
        px = np.array([PF[X, i] for i, _ in legs])
        move = px / pe - 1
        realized += np.where(is_open, N * f * d * move, 0.0)
    days = (dates[X] - dates[E]).days
    fin = FIN_RATE * N.sum() * days / 365.0
    pnl = realized.sum()
    return dict(gross=100 * pnl / C0, net=100 * (pnl - cost - fin) / C0, cost_spread=100 * cost / C0,
                cost_fin=100 * fin / C0, stops=stops, reopens=reopens, reduces=reduces, killed=killed,
                kill_day=kill_day, peak=peak, exposure=gross, daily=daily,
                set=set(legs) if not killed else set())


def run_path(baskets, cfg, C0=START, kill=True):
    """baskets: lista (E, X, legs). Ścieżka kapitału; po kill switchu płasko do końca.
    Zwraca per-okno zwroty brutto/netto (% kapitału na starcie okna) i krzywe kapitału."""
    C = C0; Cn = C0; peak = C0; prev = set()
    rows = []; killed_at = None; cap = [C0]; capn = [C0]; dcap = []
    for (E, X, legs) in baskets:
        if killed_at is not None or legs is None:
            rows.append(dict(gross=0.0, net=0.0, cost_spread=0.0, cost_fin=0.0, stops=0, reopens=0, reduces=0,
                             killed=False, exposure=0.0, flat=True))
            cap.append(C); capn.append(Cn); prev = set()
            continue
        r = sim_window(legs, E, X, C, cfg, peak, prev, kill=kill)
        peak = r['peak']
        C = C * (1 + r['gross'] / 100)
        Cn = Cn * (1 + r['net'] / 100)
        dcap.extend(r['daily'])
        if r['killed']:
            killed_at = (E, X, r['kill_day'])
        prev = r['set']
        r['flat'] = False
        rows.append(r)
        cap.append(C); capn.append(Cn)
    return rows, np.array(cap), np.array(capn), killed_at, np.array(dcap)


# ----------------------------------------------------------------------------- metryki
def metrics(x, cap=None):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    n = len(x)
    if n < 2:
        return dict(n=n, mean=np.nan, median=np.nan, sigma=np.nan, t=np.nan, sharpe=np.nan, hit=np.nan,
                    maxdd=np.nan, worst=np.nan, best=np.nan, cum=np.nan)
    mu, sd = x.mean(), x.std(ddof=1)
    if cap is None:
        cap = 100 * np.cumprod(1 + x / 100)
        cap = np.concatenate([[100], cap])
    dd = (1 - cap / np.maximum.accumulate(cap)).max() * 100
    return dict(n=n, mean=mu, median=float(np.median(x)), sigma=sd, t=mu / sd * math.sqrt(n),
                sharpe=mu / sd * math.sqrt(52), hit=(x > 0).mean(), maxdd=dd, worst=x.min(), best=x.max(),
                cum=cap[-1] / cap[0] * 100 - 100)


def fmt(v, d=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    return f'{v:.{d}f}'


def mrow(name, m, extra=''):
    return (f"| {name} | {m['n']} | {fmt(m['mean'])} | {fmt(m['median'])} | {fmt(m['sigma'])} | {fmt(m['t'])} | "
            f"{fmt(m['sharpe'])} | {fmt(100 * m['hit'], 0)}% | {fmt(m['maxdd'], 1)} | {fmt(m['worst'], 1)} | "
            f"{fmt(m['best'], 1)} | {fmt(m['cum'], 1)} |{extra}")


MHDR = ('| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | maxDD kap. % | najgorsze | najlepsze | kapitał końc. % |\n'
        '|---|---|---|---|---|---|---|---|---|---|---|---|')

# ============================================================================= (B) MOMENTUM 6M
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


S6 = mom_score(126)
LONGS, SHORTS = select(S6)
WIN = np.array([l is not None for l in LONGS])
widx = np.where(WIN)[0]
print(f'(B) okna z sygnałem: {WIN.sum()} od {dates[D0[widx[0]]].date()} do {dates[D5[widx[-1]]].date()}', file=sys.stderr)

# harness: spread_pp wariantu a_6M
spread = np.full(nW, np.nan); long_pp = np.full(nW, np.nan); short_pp = np.full(nW, np.nan)
hits_legs = np.zeros(nW); legs_n = np.zeros(nW)
for w in widx:
    el = EX[w, LONGS[w]]; es = -EX[w, SHORTS[w]]
    long_pp[w] = el.mean() * 100; short_pp[w] = es.mean() * 100; spread[w] = long_pp[w] + short_pp[w]
    hits_legs[w] = (el > 0).sum() + (es > 0).sum(); legs_n[w] = NL + NS


def baskets_for(cfg):
    out = []
    for w in widx:
        if cfg.delay == 0:
            E, X = D0[w], D5[w]
        else:
            E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
        legs = [(int(i), +1) for i in LONGS[w]] + [(int(i), -1) for i in SHORTS[w]]
        out.append((E, X, legs))
    return out


RES_B = {}
for cfg in VARIANTS:
    bk = baskets_for(cfg)
    rows, cap, capn, killed_at, dcap = run_path(bk, cfg)
    rows_nk, cap_nk, capn_nk, _, dcap_nk = run_path(bk, cfg, kill=False)
    g = np.array([r['gross'] for r in rows_nk]); nt = np.array([r['net'] for r in rows_nk])
    RES_B[cfg.name] = dict(cfg=cfg, rows=rows, cap=cap, capn=capn, killed_at=killed_at, dcap=dcap,
                           rows_nk=rows_nk, cap_nk=cap_nk, capn_nk=capn_nk, dcap_nk=dcap_nk,
                           gross=g, net=nt, m_gross=metrics(g, cap_nk), m_net=metrics(nt, capn_nk),
                           m_gross_kill=metrics(np.array([r['gross'] for r in rows]), cap),
                           stops=sum(r['stops'] for r in rows_nk), reopens=sum(r['reopens'] for r in rows_nk),
                           reduces=sum(r['reduces'] for r in rows_nk),
                           exposure=np.mean([r['exposure'] for r in rows_nk]),
                           daily_sigma=float(np.std(np.diff(dcap_nk) / dcap_nk[:-1], ddof=1)) * 100 if len(dcap_nk) > 2 else np.nan)
    print(f"  {cfg.name}: brutto śr {g.mean():.3f} pp/tydz, t {RES_B[cfg.name]['m_gross']['t']:.2f}, "
          f"kapitał końc. (bez kill) {cap_nk[-1]:.1f}, z kill {cap[-1]:.1f}, kill: {killed_at is not None}, "
          f"stopy {RES_B[cfg.name]['stops']} reopen {RES_B[cfg.name]['reopens']}", file=sys.stderr)


# odsetek 12-tygodniowych okien z trafionym kill switchem
def kill_windows(cfg, H=12):
    bk = baskets_for(cfg)
    hits = 0; total = 0; minC = []
    for s in range(0, len(bk) - H + 1):
        rows, cap, _, killed_at, dcap = run_path(bk[s:s + H], cfg)
        total += 1; hits += killed_at is not None
        minC.append(dcap.min() if len(dcap) else 100)
    return hits, total, np.array(minC)


KILL12 = {}
for cfg in VARIANTS:
    h, tot, minC = kill_windows(cfg)
    KILL12[cfg.name] = (h, tot, minC)
    print(f"  kill12 {cfg.name}: {h}/{tot} = {100 * h / tot:.1f}%  (5. pct min kapitału w oknie: {np.percentile(minC, 5):.1f})", file=sys.stderr)

# ----------------------------------------------------------------------------- baseline losowy (harness)
rng = np.random.default_rng(SEED)
pool_sp = []; strat_means = []; strat_t = []
RB = np.full((MIN_RANDOM, len(widx)), np.nan)
for k, w in enumerate(widx):
    ok = np.where(~np.isnan(WR[w]))[0]
    for b in range(MIN_RANDOM):
        pick = rng.choice(ok, NL + NS, replace=False)
        RB[b, k] = (EX[w, pick[:NL]].mean() - EX[w, pick[NL:]].mean()) * 100
pool = RB.ravel()
BASE_RAND = dict(sigma=float(pool.std(ddof=1)), p5=float(np.percentile(pool, 5)), p95=float(np.percentile(pool, 95)),
                 mean_p5=float(np.percentile(RB.mean(1), 5)), mean_p95=float(np.percentile(RB.mean(1), 95)),
                 t_p5=float(np.percentile(RB.mean(1) / RB.std(1, ddof=1) * math.sqrt(RB.shape[1]), 5)),
                 t_p95=float(np.percentile(RB.mean(1) / RB.std(1, ddof=1) * math.sqrt(RB.shape[1]), 95)),
                 t_p975=float(np.percentile(RB.mean(1) / RB.std(1, ddof=1) * math.sqrt(RB.shape[1]), 97.5)),
                 sigma_strat_p5=float(np.percentile(RB.std(1, ddof=1), 5)), sigma_strat_p95=float(np.percentile(RB.std(1, ddof=1), 95)))
# w jednostkach kapitału (×1,2)
print(f"baseline harness: σ {BASE_RAND['sigma']:.2f} pp (kapitał {1.2 * BASE_RAND['sigma']:.2f}), p5/p95 {BASE_RAND['p5']:.2f}/{BASE_RAND['p95']:.2f}", file=sys.stderr)

# ----------------------------------------------------------------------------- baseline losowy przez warstwę wykonania
# 200 losowych strategii (losowy koszyk 5/5 w każdym oknie) przez v2 i v4 (+ v3, v8): koszt wykonania na szumie
rng2 = np.random.default_rng(SEED + 1)
EXEC_BASE = {k: [] for k in ('v2_Pon_bez_stopow', 'v3_stop10_bez_reopen', 'v4_stop10_reopen', 'v8_inv_sigma_1.5pct')}
EXEC_BASE_KILL12 = {k: [] for k in EXEC_BASE}
for b in range(RANDOM_EXEC):
    bk = []
    for w in widx:
        E, X = min(D0[w] + 1, nT - 1), min(D5[w] + 1, nT - 1)
        ok = np.where(~np.isnan(WR[w]) & ~np.isnan(P[E]) & ~np.isnan(P[X]))[0]
        pick = rng2.choice(ok, NL + NS, replace=False)
        bk.append((E, X, [(int(i), +1) for i in pick[:NL]] + [(int(i), -1) for i in pick[NL:]]))
    for k in EXEC_BASE:
        rows, cap, capn, killed_at, _ = run_path(bk, VBY[k], kill=False)
        g = np.array([r['gross'] for r in rows])
        EXEC_BASE[k].append(dict(mean=g.mean(), sigma=g.std(ddof=1), cum=cap[-1], cumn=capn[-1],
                                 stops=sum(r['stops'] for r in rows), maxdd=metrics(g, cap)['maxdd']))
for k in EXEC_BASE:
    m = np.array([x['mean'] for x in EXEC_BASE[k]]); s = np.array([x['sigma'] for x in EXEC_BASE[k]])
    print(f"  exec-baseline {k}: śr {m.mean():.3f} (5–95% {np.percentile(m, 5):.2f}…{np.percentile(m, 95):.2f}), σ śr {s.mean():.2f}", file=sys.stderr)

# ============================================================================= (A) KOSZYKI FAKTYCZNE W4–W7
KH = json.load(open(KOSZ))
DI = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(dates)}
ORDER = ['2026-W4', '2026-W5', '2026-W6', '2026-W7']
HIST = {h['week']: h for h in KH['history']}
A_BASKETS = []
for k, wk in enumerate(ORDER):
    kz = KH['koszyki'][wk]
    d0 = DI[kz['d0']['date']]
    nxt = DI[KH['koszyki'][ORDER[k + 1]]['d0']['date']] if k + 1 < len(ORDER) else nT - 1
    legs = [(COL[t], +1) for t in kz['long']] + [(COL[t], -1) for t in kz['short']]
    A_BASKETS.append(dict(week=wk, d0=d0, d5=nxt, legs=legs, long=kz['long'], short=kz['short']))


def a_baskets_for(cfg):
    out = []
    for b in A_BASKETS:
        if cfg.delay == 0:
            E, X = b['d0'], b['d5']
        else:
            E, X = min(b['d0'] + 1, nT - 1), min(b['d5'] + 1, nT - 1)
        out.append((E, X, b['legs']))
    return out


RES_A = {}
for cfg in VARIANTS:
    bk = a_baskets_for(cfg)
    rows, cap, capn, killed_at, dcap = run_path(bk, cfg)
    RES_A[cfg.name] = dict(rows=rows, cap=cap, capn=capn, killed_at=killed_at, bk=bk, dcap=dcap)

# spread harnessu dla koszyków faktycznych (D0 → następne D0)
A_SPREAD = []
for b in A_BASKETS:
    rn = NDX[b['d5']] / NDX[b['d0']] - 1
    el = [P[b['d5'], i] / P[b['d0'], i] - 1 - rn for i, _ in b['legs'][:5]]
    es = [-(P[b['d5'], i] / P[b['d0'], i] - 1 - rn) for i, _ in b['legs'][5:]]
    A_SPREAD.append(dict(long=100 * np.mean(el), short=100 * np.mean(es), spread=100 * (np.mean(el) + np.mean(es)),
                         hits=sum(e > 0 for e in el) + sum(e > 0 for e in es)))

# ============================================================================= rozbicia (B)
def breakdown_table(names):
    masks = {}
    yrs = sorted(set(YEAR[widx]))
    for y in yrs:
        masks[str(y)] = YEAR[widx] == y
    masks['VIX>20'] = VIX0[widx] > 20; masks['VIX≤20'] = VIX0[widx] <= 20
    masks['NDX<MA200'] = ABOVE[widx] == 0; masks['NDX>MA200'] = ABOVE[widx] == 1
    hdr = '| wariant | ' + ' | '.join(f'{k} (n={int(m.sum())})' for k, m in masks.items()) + ' |\n|---|' + '---|' * len(masks)
    lines = [hdr]
    for nm in names:
        g = RES_B[nm]['gross']
        cells = []
        for k, m in masks.items():
            x = g[m]
            if len(x) < 2:
                cells.append('—'); continue
            cells.append(f'{x.mean():.2f} (t {x.mean() / x.std(ddof=1) * math.sqrt(len(x)):.1f})')
        lines.append(f'| {nm} | ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


# ============================================================================= CSV serii
rows_csv = []
for k, w in enumerate(widx):
    row = dict(zbior='B_mom6M', okno=k, date_d0=dates[D0[w]].date(), date_d5=dates[D5[w]].date(),
               date_entry_pon=dates[min(D0[w] + 1, nT - 1)].date(), date_exit_pon=dates[min(D5[w] + 1, nT - 1)].date(),
               spread_pp=round(spread[w], 4), long_pp=round(long_pp[w], 4), short_pp=round(short_pp[w], 4),
               hit_legs=int(hits_legs[w]), vix_d0=round(VIX0[w], 2), ndx_above_ma200=ABOVE[w],
               long=' '.join(cands[i] for i in LONGS[w]), short=' '.join(cands[i] for i in SHORTS[w]))
    for nm, r in RES_B.items():
        rr = r['rows_nk'][k]
        row[f'{nm}_brutto_pp'] = round(rr['gross'], 4); row[f'{nm}_netto_pp'] = round(rr['net'], 4)
        row[f'{nm}_stopy'] = rr['stops']; row[f'{nm}_reopen'] = rr['reopens']
        if nm.startswith('v8'):
            row[f'{nm}_gross_exp'] = round(rr['exposure'], 3)
    rows_csv.append(row)
for k, b in enumerate(A_BASKETS):
    row = dict(zbior='A_koszyk', okno=b['week'], date_d0=dates[b['d0']].date(), date_d5=dates[b['d5']].date(),
               date_entry_pon=dates[min(b['d0'] + 1, nT - 1)].date(), date_exit_pon=dates[min(b['d5'] + 1, nT - 1)].date(),
               spread_pp=round(A_SPREAD[k]['spread'], 4), long_pp=round(A_SPREAD[k]['long'], 4), short_pp=round(A_SPREAD[k]['short'], 4),
               hit_legs=A_SPREAD[k]['hits'], vix_d0=round(VIX[b['d0']], 2), ndx_above_ma200=float(NDX[b['d0']] > MA200[b['d0']]),
               long=' '.join(b['long']), short=' '.join(b['short']))
    for nm, r in RES_A.items():
        rr = r['rows'][k]
        row[f'{nm}_brutto_pp'] = round(rr['gross'], 4); row[f'{nm}_netto_pp'] = round(rr['net'], 4)
        row[f'{nm}_stopy'] = rr['stops']; row[f'{nm}_reopen'] = rr['reopens']
        if nm.startswith('v8'):
            row[f'{nm}_gross_exp'] = round(rr['exposure'], 3)
    rows_csv.append(row)
pd.DataFrame(rows_csv).to_csv(OUT_SERIE, index=False)

# ============================================================================= NOTATKA
L = []
L.append(f'# Symulacja warstwy wykonawczej bota (bt_{NAME})\n')
L.append('Dane: closes_5y.csv (zamknięcia dzienne 2021-10-18…2026-10-16, 103 spółki = DZISIEJSZY skład Nasdaq-100 → '
         'survivorship bias). Stop i kill switch sprawdzane WYŁĄCZNIE na zamknięciach dziennych (bot sprawdza o 13:45 i 17:05 UTC '
         'na mid brokera — w rzeczywistości więcej zadziałań, ale bliżej progu). Wejście = zamknięcie sesji po D0 (bieg 13:45 UTC '
         'w poniedziałek działa po otwarciu NYSE; zamknięcie poniedziałku to przybliżenie), wyjście = zamknięcie sesji po D5 '
         '(następna rotacja). Sizing 24% kapitału na nogę (gross 240%), kapitał 100, kill switch 25% od kroczącego szczytu '
         '(szczyt ≥ 100 jak `max(szczyt, START_EQUITY)` w app.py). Koszty: 0,10% nominału na każde otwarcie nogi '
         '(rotacja z turnoverem i każdy reopen) + 6%/rok finansowania od gross za dni kalendarzowe okna. Bez look-ahead: sygnał z danych do D0.\n')
L.append('## Warianty\n')
for v in VARIANTS:
    L.append(f'- **{v.name}** — {v.note}')
L.append('')

# --- (B)
L.append(f'## (B) Momentum 6M tygodniowe, {len(widx)} okien ({dates[D0[widx[0]]].date()} → {dates[D5[widx[-1]]].date()})\n')
mh = metrics(spread[widx])
L.append('Harness (spread_pp, wejście D0, bez kosztów): ' + f"średnia {mh['mean']:.2f} pp, σ {mh['sigma']:.2f}, t {mh['t']:.2f}, "
         f"Sharpe {mh['sharpe']:.2f}, hit {100 * mh['hit']:.0f}%, hit nóg {100 * hits_legs[widx].sum() / legs_n[widx].sum():.0f}%, "
         f"maxDD skumulowanego spreadu {((np.maximum.accumulate(np.cumsum(spread[widx])) - np.cumsum(spread[widx])).max()):.1f} pp, "
         f"najgorsze {mh['worst']:.1f}, najlepsze {mh['best']:.1f}. (W jednostkach kapitału ×1,2 → wariant v1.)\n")
L.append(f"**BASELINE** 2000 losowych koszyków 5/5 na okno: σ pojedynczego okna {BASE_RAND['sigma']:.2f} pp spreadu "
         f"(= {1.2 * BASE_RAND['sigma']:.2f} pp kapitału), 5–95% spreadu {BASE_RAND['p5']:.2f}…{BASE_RAND['p95']:.2f} pp; "
         f"losowa STRATEGIA (losowy koszyk w każdym oknie): średnia 5–95% {BASE_RAND['mean_p5']:.2f}…{BASE_RAND['mean_p95']:.2f} pp/tydz., "
         f"t-stat 5–95% {BASE_RAND['t_p5']:.2f}…{BASE_RAND['t_p95']:.2f} (97,5%: {BASE_RAND['t_p975']:.2f}), "
         f"σ strategii 5–95% {BASE_RAND['sigma_strat_p5']:.2f}…{BASE_RAND['sigma_strat_p95']:.2f} pp.\n")

L.append('### B1. Warianty wykonania — BRUTTO (% kapitału na okno; bez kill switcha, żeby porównać same reguły)\n')
L.append(MHDR.split('\n')[0] + ' stopy | reopen | REDUCE | śr. gross | σ dz. kapitału % |\n' + MHDR.split('\n')[1] + '---|---|---|---|---|')
for nm, r in RES_B.items():
    L.append(mrow(nm, r['m_gross'], f" {r['stops']} | {r['reopens']} | {r['reduces']} | {r['exposure']:.2f} | {fmt(r['daily_sigma'])} |"))
L.append('')
L.append('### B2. Warianty wykonania — NETTO (po 0,10%/nogę/otwarcie + 6%/rok od gross)\n')
L.append(MHDR)
for nm, r in RES_B.items():
    L.append(mrow(nm, r['m_net']))
L.append('')
L.append('### B3. Kill switch 25% od kroczącego szczytu\n')
L.append('| wariant | kapitał końc. bez kill (brutto) | kapitał końc. z kill (brutto) | kill na pełnej ścieżce | okna 12-tyg. z killem | 5. pct min. kapitału w oknie 12-tyg. | mediana min. |\n|---|---|---|---|---|---|---|')
for nm, r in RES_B.items():
    h, tot, minC = KILL12[nm]
    ka = r['killed_at']
    ks = f"TAK — {dates[ka[2]].date()}" if ka else 'nie'
    L.append(f"| {nm} | {r['cap_nk'][-1]:.1f} | {r['cap'][-1]:.1f} | {ks} | {h}/{tot} = {100 * h / tot:.1f}% | {np.percentile(minC, 5):.1f} | {np.median(minC):.1f} |")
L.append('')
L.append('### B4. Dekompozycja: co kosztuje ile (różnice średnich brutto, pp kapitału/tydzień; t różnicy = sparowany)\n')
pairs = [('opóźnienie wejścia pt→pon (v2 − v1)', 'v2_Pon_bez_stopow', 'v1_D0_bez_stopow'),
         ('stop 10% bez reopen (v3 − v2)', 'v3_stop10_bez_reopen', 'v2_Pon_bez_stopow'),
         ('reopen po stopie (v4 − v3)', 'v4_stop10_reopen', 'v3_stop10_bez_reopen'),
         ('stop 10% + reopen = app.py (v4 − v2)', 'v4_stop10_reopen', 'v2_Pon_bez_stopow'),
         ('stop 15% bez reopen (v5 − v2)', 'v5_stop15_bez_reopen', 'v2_Pon_bez_stopow'),
         ('stop 2,5σ bez reopen (v6 − v2)', 'v6_stop2.5sig_bez_reopen', 'v2_Pon_bez_stopow'),
         ('REDUCE 50% po 2σ (v7 − v2)', 'v7_reduce50_2sig', 'v2_Pon_bez_stopow'),
         ('sizing 1/σ cel 1,5% (v8 − v2)', 'v8_inv_sigma_1.5pct', 'v2_Pon_bez_stopow'),
         ('(8) + stop10 reopen (v9 − v8)', 'v9_inv_sigma_stop10_reopen', 'v8_inv_sigma_1.5pct'),
         ('ALLOC 0,12 zamiast 0,24 (v10 − v2)', 'v10_alloc12_bez_stopow', 'v2_Pon_bez_stopow'),
         ('ALLOC 0,16 zamiast 0,24 (v11 − v2)', 'v11_alloc16_bez_stopow', 'v2_Pon_bez_stopow')]
L.append('| element | Δ średnia pp/tydz | Δ łącznie pp (suma) | t (sparowany) | Δ σ tyg. | Δ Sharpe | Δ kapitał końc. (bez kill) | Δ maxDD |\n|---|---|---|---|---|---|---|---|')
DECOMP = {}
for label, a, b in pairs:
    d = RES_B[a]['gross'] - RES_B[b]['gross']
    t = d.mean() / d.std(ddof=1) * math.sqrt(len(d)) if d.std(ddof=1) > 0 else float('nan')
    DECOMP[label] = dict(d_mean=float(d.mean()), t=float(t))
    L.append(f"| {label} | {d.mean():+.3f} | {d.sum():+.1f} | {t:+.2f} | {RES_B[a]['m_gross']['sigma'] - RES_B[b]['m_gross']['sigma']:+.2f} | "
             f"{RES_B[a]['m_gross']['sharpe'] - RES_B[b]['m_gross']['sharpe']:+.2f} | {RES_B[a]['cap_nk'][-1] - RES_B[b]['cap_nk'][-1]:+.1f} | "
             f"{RES_B[a]['m_gross']['maxdd'] - RES_B[b]['m_gross']['maxdd']:+.1f} |")
L.append('')
# stopy: ile z nich było „słusznych"? — porównanie v3 vs v2 per okno ze stopem
st_w = np.array([r['stops'] > 0 for r in RES_B['v3_stop10_bez_reopen']['rows_nk']])
d34 = RES_B['v4_stop10_reopen']['gross'] - RES_B['v3_stop10_bez_reopen']['gross']
d32 = RES_B['v3_stop10_bez_reopen']['gross'] - RES_B['v2_Pon_bez_stopow']['gross']
L.append(f"Okna z ≥1 stopem 10% (v3): {st_w.sum()}/{len(st_w)} ({100 * st_w.mean():.0f}%). W tych oknach stop bez reopen vs brak stopu: "
         f"śr {d32[st_w].mean():+.2f} pp (udział okien, gdzie stop pomógł: {100 * (d32[st_w] > 0).mean():.0f}%); "
         f"reopen vs bez reopen: śr {d34[st_w].mean():+.2f} pp (udział okien, gdzie reopen pomógł: {100 * (d34[st_w] > 0).mean():.0f}%).\n")

L.append('### B5. Baseline przez warstwę wykonania (200 losowych strategii 5/5, bez kill, brutto) — koszt reguł na SZUMIE\n')
L.append('| wariant | śr. pp/tydz (5–95%) | σ tyg. śr. | kapitał końc. śr. (brutto) | kapitał końc. śr. (netto) | stopy śr. | maxDD śr. |\n|---|---|---|---|---|---|---|')
EXEC_SUM = {}
for k, lst in EXEC_BASE.items():
    m = np.array([x['mean'] for x in lst]); s = np.array([x['sigma'] for x in lst]); c = np.array([x['cum'] for x in lst])
    cn = np.array([x['cumn'] for x in lst]); stp = np.array([x['stops'] for x in lst]); dd = np.array([x['maxdd'] for x in lst])
    EXEC_SUM[k] = dict(mean=float(m.mean()), p5=float(np.percentile(m, 5)), p95=float(np.percentile(m, 95)), sigma=float(s.mean()),
                       cum=float(c.mean()), cumn=float(cn.mean()), stops=float(stp.mean()), maxdd=float(dd.mean()))
    L.append(f"| {k} | {m.mean():+.3f} ({np.percentile(m, 5):+.2f}…{np.percentile(m, 95):+.2f}) | {s.mean():.2f} | {c.mean():.1f} | {cn.mean():.1f} | {stp.mean():.0f} | {dd.mean():.1f} |")
d_exec = np.array([a['mean'] - b['mean'] for a, b in zip(EXEC_BASE['v4_stop10_reopen'], EXEC_BASE['v2_Pon_bez_stopow'])])
d_exec3 = np.array([a['mean'] - b['mean'] for a, b in zip(EXEC_BASE['v3_stop10_bez_reopen'], EXEC_BASE['v2_Pon_bez_stopow'])])
L.append(f"\nNa losowych koszykach stop 10% + reopen zmienia średnią o {d_exec.mean():+.3f} pp/tydz. (5–95% {np.percentile(d_exec, 5):+.2f}…{np.percentile(d_exec, 95):+.2f}; "
         f"udział strategii, gdzie szkodzi: {100 * (d_exec < 0).mean():.0f}%), stop bez reopen o {d_exec3.mean():+.3f} pp/tydz. "
         f"— to koszt wykonania NIEZALEŻNY od sygnału.\n")

L.append('### B6. Rozbicie na lata i reżimy (brutto, pp kapitału/tydz., t w nawiasie; lata i reżim wg D0)\n')
L.append(breakdown_table(['v1_D0_bez_stopow', 'v2_Pon_bez_stopow', 'v3_stop10_bez_reopen', 'v4_stop10_reopen', 'v6_stop2.5sig_bez_reopen', 'v8_inv_sigma_1.5pct', 'v10_alloc12_bez_stopow']))
L.append('')

# --- (A)
L.append('## (A) Faktyczne koszyki 2026-W4…W7 (koszyki_historia.json)\n')
L.append('Okna: D0 → D0 następnego koszyka (W4 11 sesji od 2026-09-14, W5 4, W6 5, W7 4 — W7 kończy się 2026-10-16, ostatnia sesja danych; '
         'wariant „poniedziałek" wychodzi też 2026-10-16). Bez wpisów exclude/tactical z pulsu (czysta warstwa wykonawcza).\n')
L.append('| tydzień | D0 | wyjście | LONG | SHORT | spread_pp (D0→D0+5, vs ^NDX) | hit nóg | history.spread_pp | history.spread_fills_pp |\n|---|---|---|---|---|---|---|---|---|')
for k, b in enumerate(A_BASKETS):
    h = HIST.get(b['week'], {})
    L.append(f"| {b['week']} | {dates[b['d0']].date()} | {dates[b['d5']].date()} | {' '.join(b['long'])} | {' '.join(b['short'])} | "
             f"{A_SPREAD[k]['spread']:+.2f} | {A_SPREAD[k]['hits']}/10 | {h.get('spread_pp', '—')} | {h.get('spread_fills_pp', '—')} |")
L.append('')
L.append('### A1. Zwrot kapitału na okno (brutto, % kapitału na starcie okna; w nawiasie liczba stopów/reopen) i kapitał końcowy\n')
hdr = '| wariant | ' + ' | '.join(ORDER) + ' | suma pp | kapitał końc. brutto | kapitał końc. netto | kill | koszty łącznie pp |\n|---|' + '---|' * (len(ORDER) + 5)
L.append(hdr)
for nm, r in RES_A.items():
    cells = []
    for rr in r['rows']:
        tag = ''
        if rr['stops'] or rr['reopens'] or rr['reduces']:
            tag = f" ({rr['stops']}s/{rr['reopens']}r" + (f"/{rr['reduces']}R" if rr['reduces'] else '') + ')'
        if rr.get('flat'):
            tag = ' (płasko)'
        cells.append(f"{rr['gross']:+.2f}{tag}")
    g = np.array([rr['gross'] for rr in r['rows']])
    cost = sum(rr['cost_spread'] + rr['cost_fin'] for rr in r['rows'])
    ka = r['killed_at']
    ks = f"TAK {dates[ka[2]].date()}" if ka else 'nie'
    L.append(f"| {nm} | " + ' | '.join(cells) + f" | {g.sum():+.2f} | {r['cap'][-1]:.2f} | {r['capn'][-1]:.2f} | {ks} | {cost:.2f} |")
L.append('')
L.append('### A2. Dekompozycja na koszykach faktycznych (Δ kapitału końcowego brutto wobec v2)\n')
for nm, r in RES_A.items():
    if nm == 'v2_Pon_bez_stopow':
        continue
    L.append(f"- {nm}: {r['cap'][-1] - RES_A['v2_Pon_bez_stopow']['cap'][-1]:+.2f} pkt kapitału (v2 = {RES_A['v2_Pon_bez_stopow']['cap'][-1]:.2f})")
L.append('')
# dzienna ścieżka W7 w v2/v3/v4 dla ilustracji
L.append('### A3. Ścieżka dzienna kapitału w W7 (wejście 2026-10-12) — v2 / v3 / v4 / v6\n')
L.append('| sesja | v2 bez stopu | v3 stop10 | v4 stop10+reopen | v6 2,5σ |\n|---|---|---|---|---|')
w7 = 3
E7, X7, _ = RES_A['v2_Pon_bez_stopow']['bk'][w7]
paths = {nm: RES_A[nm]['rows'][w7] for nm in ('v2_Pon_bez_stopow', 'v3_stop10_bez_reopen', 'v4_stop10_reopen', 'v6_stop2.5sig_bez_reopen')}
C7 = {nm: RES_A[nm]['cap'][w7] for nm in paths}
for j, t in enumerate(range(E7 + 1, X7 + 1)):
    cells = []
    for nm, rr in paths.items():
        dl = rr.get('daily', [])
        cells.append(f"{100 * (dl[j] / C7[nm] - 1):+.2f}%" if j < len(dl) else '—')
    L.append(f"| {dates[t].date()} | " + ' | '.join(cells) + ' |')
L.append('')

# --- wnioski
v1, v2, v3, v4 = (RES_B[k] for k in ('v1_D0_bez_stopow', 'v2_Pon_bez_stopow', 'v3_stop10_bez_reopen', 'v4_stop10_reopen'))
v8 = RES_B['v8_inv_sigma_1.5pct']
L.append('## Wnioski\n')
L.append(f"1. Sygnał (v1, D0→D5): {v1['m_gross']['mean']:.2f} pp kapitału/tydz., t {v1['m_gross']['t']:.2f} brutto, netto {v1['m_net']['mean']:.2f} pp (t {v1['m_net']['t']:.2f}); "
         f"baseline t 97,5% = {BASE_RAND['t_p975']:.2f}. {'Przebija' if v1['m_net']['t'] > 2 else 'NIE przebija'} baseline z t>2 po kosztach.")
L.append(f"2. Opóźnienie wejścia pt→pon (v2 − v1): {DECOMP['opóźnienie wejścia pt→pon (v2 − v1)']['d_mean']:+.3f} pp/tydz. (t {DECOMP['opóźnienie wejścia pt→pon (v2 − v1)']['t']:+.2f}).")
L.append(f"3. Stop 10% bez reopen (v3 − v2): {DECOMP['stop 10% bez reopen (v3 − v2)']['d_mean']:+.3f} pp/tydz. (t {DECOMP['stop 10% bez reopen (v3 − v2)']['t']:+.2f}); "
         f"reopen (v4 − v3): {DECOMP['reopen po stopie (v4 − v3)']['d_mean']:+.3f} (t {DECOMP['reopen po stopie (v4 − v3)']['t']:+.2f}); "
         f"razem app.py (v4 − v2): {DECOMP['stop 10% + reopen = app.py (v4 − v2)']['d_mean']:+.3f} pp/tydz. (t {DECOMP['stop 10% + reopen = app.py (v4 − v2)']['t']:+.2f}). "
         f"Na szumie (losowe koszyki) v4 − v2 = {d_exec.mean():+.3f} pp/tydz.")
L.append(f"4. Sizing 1/σ z celem 1,5% σ dziennej (v8): średnia {v8['m_gross']['mean']:.2f} pp, σ {v8['m_gross']['sigma']:.2f}, Sharpe {v8['m_gross']['sharpe']:.2f}, "
         f"maxDD {v8['m_gross']['maxdd']:.1f}% vs v2 Sharpe {v2['m_gross']['sharpe']:.2f}, maxDD {v2['m_gross']['maxdd']:.1f}%; śr. gross {v8['exposure']:.2f}; "
         f"σ dz. kapitału v2 = {v2['daily_sigma']:.2f}% (cel 1,5%).")
L.append(f"5. Kill switch 25%: v2 trafia w {100 * KILL12['v2_Pon_bez_stopow'][0] / KILL12['v2_Pon_bez_stopow'][1]:.1f}% okien 12-tyg., v4 w "
         f"{100 * KILL12['v4_stop10_reopen'][0] / KILL12['v4_stop10_reopen'][1]:.1f}%, v8 w {100 * KILL12['v8_inv_sigma_1.5pct'][0] / KILL12['v8_inv_sigma_1.5pct'][1]:.1f}%.")
v10 = RES_B['v10_alloc12_bez_stopow']; v12 = RES_B['v12_alloc12_stop10_reopen']
L.append(f"6. ALLOC_PCT 0,12 (v10): średnia {v10['m_gross']['mean']:.2f} pp, σ {v10['m_gross']['sigma']:.2f}, maxDD {v10['m_gross']['maxdd']:.1f}%, "
         f"kill w {100 * KILL12['v10_alloc12_bez_stopow'][0] / KILL12['v10_alloc12_bez_stopow'][1]:.1f}% okien 12-tyg.; kapitał końc. z kill {v10['cap'][-1]:.1f} "
         f"vs {v2['cap'][-1]:.1f} dla 0,24; netto {v10['m_net']['mean']:.2f} pp (t {v10['m_net']['t']:.2f}).")
L.append('')
L.append('## Co zmienić w app.py (nazwy zmiennych)\n')
L.append('Ranking kosztu elementów wykonania (B, brutto, pp kapitału/tydz.; ujemne = kosztuje). Warianty sizingu (v8/v10/v11) '
         'obniżają średnią przez samo zmniejszenie gross — to NIE koszt (t-stat i Sharpe bez zmian przy równych wagach), dlatego są wypisane osobno:\n')
rank = sorted(DECOMP.items(), key=lambda kv: kv[1]['d_mean'])
for lab, d in rank:
    if 'sizing' in lab or 'ALLOC' in lab:
        continue
    L.append(f"- {lab}: {d['d_mean']:+.3f} pp/tydz. (t {d['t']:+.2f})")
L.append('')
L.append('Sizing (zmiana skali, nie koszt): ' + '; '.join(f"{lab}: {d['d_mean']:+.3f} pp/tydz., t-stat wariantu {RES_B[a]['m_gross']['t']:.2f} vs {RES_B[b]['m_gross']['t']:.2f}"
         for (lab, a, b), d in zip([x for x in pairs if 'sizing' in x[0] or 'ALLOC' in x[0]], [DECOMP[x[0]] for x in pairs if 'sizing' in x[0] or 'ALLOC' in x[0]])))
L.append('')
L.append('Interpretacja i rekomendacje:\n')
L.append(f"- **Największy koszt to nie reguła per noga, tylko para `ALLOC_PCT=0.24` × `KILL_LEVEL=0.75`**: przy gross 240% tygodniowa σ kapitału "
         f"wynosi ~{v2['m_gross']['sigma']:.0f} pp (dzienna {v2['daily_sigma']:.1f}%), więc obsunięcie 25% od szczytu to ~2,5σ tygodniowej i wypada w "
         f"{100 * KILL12['v2_Pon_bez_stopow'][0] / KILL12['v2_Pon_bez_stopow'][1]:.0f}% okien 12-tygodniowych; po trafieniu strategia z dodatnią "
         f"oczekiwaną (kapitał {v2['cap_nk'][-1]:.0f} bez kill) kończy na {v2['cap'][-1]:.0f}. Żaden stop per noga tego nie zmienia (B3: 37–41% dla v1–v7). "
         f"Działa tylko sizing: `ALLOC_PCT=0.12` daje {100 * KILL12['v10_alloc12_bez_stopow'][0] / KILL12['v10_alloc12_bez_stopow'][1]:.1f}% okien z killem, "
         f"sizing 1/σ z celem 1,5% (gross śr. {v8['exposure']:.2f}) {100 * KILL12['v8_inv_sigma_1.5pct'][0] / KILL12['v8_inv_sigma_1.5pct'][1]:.1f}%. "
         f"Alternatywa, jeśli właściciel chce gross 240%: `KILL_LEVEL` musiałby zejść do ok. 0,50 — co jest sprzeczne z celem kill switcha.")
L.append(f"- **`STOP_LOSS_PCT=0.10` (twardy stop od ceny wejścia) obniża oczekiwaną o {DECOMP['stop 10% bez reopen (v3 − v2)']['d_mean']:+.2f} pp/tydz. (t {DECOMP['stop 10% bez reopen (v3 − v2)']['t']:.1f}) i NIE zmniejsza σ ani maxDD** "
         f"(B1: σ {RES_B['v3_stop10_bez_reopen']['m_gross']['sigma']:.2f} vs {v2['m_gross']['sigma']:.2f}, maxDD {RES_B['v3_stop10_bez_reopen']['m_gross']['maxdd']:.0f}% vs {v2['m_gross']['maxdd']:.0f}%); "
         f"na losowych koszykach jest neutralny ({d_exec3.mean():+.3f}), czyli ścina właśnie noga po spadku, w której sygnał momentum ma dodatni dryf do końca tygodnia. "
         f"Stop 15% (`STOP_LOSS_PCT=0.15`) kosztuje mniej ({DECOMP['stop 15% bez reopen (v5 − v2)']['d_mean']:+.2f}), stop 2,5σ więcej ({DECOMP['stop 2,5σ bez reopen (v6 − v2)']['d_mean']:+.2f}). "
         f"Rekomendacja: `STOP_LOSS_PCT=0` (wyłączyć) albo podnieść do 0,15–0,20 i traktować wyłącznie jako siatkę awaryjną; ryzykiem całości steruje sizing, nie stop per noga.")
L.append(f"- **Reopen po stopie** (brak wpisu `exclude` po STOP → `desired_book` otwiera nogę w następnym biegu) odrabia część kosztu stopu ({DECOMP['reopen po stopie (v4 − v3)']['d_mean']:+.2f} pp/tydz., t {DECOMP['reopen po stopie (v4 − v3)']['t']:.1f}) "
         f"za cenę drugiego spreadu ({RES_B['v4_stop10_reopen']['reopens']} reopenów na {RES_B['v4_stop10_reopen']['stops']} stopów). To nie jest błąd kosztowy, lecz logiczny: stop bez pamięci jest sprzeczny sam ze sobą. "
         f"Jeśli stop zostaje, po STOP bot powinien dopisywać do `signals.json` wpis `exclude` {{ticker, action: CLOSE, basis: 'stop'}} (ścieżka już istnieje dla pulsu; `bramka_reakcji` przepuszcza basis spoza ('cena','price') bez sprawdzania), "
         f"żeby `desired_book` nie otwierał nogi do soboty — wariant v3. Alternatywnie zaakceptować v4 jako świadomy wybór (mniej kosztuje niż v3 brutto, ale netto różnica maleje).")
L.append(f"- **REDUCE 50% po 2σ zamiast stopu** (`REACT_REDUCE_PCT`/`REDUCE_FACTOR` jako siatka automatyczna) kosztuje {DECOMP['REDUCE 50% po 2σ (v7 − v2)']['d_mean']:+.2f} pp/tydz. — mniej niż stop, ale nadal ujemnie; nie rozwiązuje problemu kill switcha.")
L.append(f"- **Opóźnienie wejścia** (rotacja w poniedziałek 13:45 UTC zamiast D0) jest statystycznie nieistotne ({DECOMP['opóźnienie wejścia pt→pon (v2 − v1)']['d_mean']:+.2f} pp/tydz., t {DECOMP['opóźnienie wejścia pt→pon (v2 − v1)']['t']:.1f}); "
         f"W4–W7 akurat sprzyjało (+8 pkt kapitału w (A)). Nie warto zmieniać harmonogramu cron-job.org z tego powodu.")
L.append(f"- **Koszty**: finansowanie 6%/rok od gross 240% = 0,28 pp/tydz., spread z turnoverem ~0,05 pp — razem ~{v2['m_gross']['mean'] - v2['m_net']['mean']:.2f} pp/tydz. z {v2['m_gross']['mean']:.2f} brutto. "
         f"Netto t-stat v2 = {v2['m_net']['t']:.2f} (brutto {v2['m_gross']['t']:.2f}; baseline 97,5% = {BASE_RAND['t_p975']:.2f}): po kosztach żaden wariant nie przebija baseline z t>2. "
         f"Obniżenie gross (ALLOC_PCT 0,12) tnie finansowanie proporcjonalnie, ale nie poprawia t-stat (koszt i zwrot skalują się razem).")
L.append('')
open(OUT_MD, 'w').write('\n'.join(L))

# JSON podsumowanie
summary = dict(
    baseline=BASE_RAND, decomposition=DECOMP, exec_baseline=EXEC_SUM,
    B={nm: dict(gross=r['m_gross'], net=r['m_net'], gross_kill=r['m_gross_kill'], stops=r['stops'], reopens=r['reopens'], reduces=r['reduces'],
                exposure=r['exposure'], daily_sigma=r['daily_sigma'], cap_end_nokill=float(r['cap_nk'][-1]), cap_end_kill=float(r['cap'][-1]),
                killed_at=(str(dates[r['killed_at'][2]].date()) if r['killed_at'] else None),
                kill12=dict(hits=int(KILL12[nm][0]), total=int(KILL12[nm][1]), pct=100 * KILL12[nm][0] / KILL12[nm][1],
                            minC_p5=float(np.percentile(KILL12[nm][2], 5))))
       for nm, r in RES_B.items()},
    A={nm: dict(gross=[rr['gross'] for rr in r['rows']], net=[rr['net'] for rr in r['rows']], stops=[rr['stops'] for rr in r['rows']],
                reopens=[rr['reopens'] for rr in r['rows']], cap_end=float(r['cap'][-1]), cap_end_net=float(r['capn'][-1]),
                killed=(r['killed_at'] is not None)) for nm, r in RES_A.items()},
    A_spread=A_SPREAD,
)


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


json.dump(_clean(summary), open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)
print(f'zapisano: {OUT_MD}\n{OUT_SERIE}\n{OUT_JSON}', file=sys.stderr)
