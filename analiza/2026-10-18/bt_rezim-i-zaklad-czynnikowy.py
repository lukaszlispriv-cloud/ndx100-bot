#!/usr/bin/env python3
"""Agent: rezim-i-zaklad-czynnikowy.

(1) proxy zakładu czynnikowego „AI-hardware long vs defensywy short" (5/5 wg momentum 6M
    w zamkniętych listach) — tygodniowy spread 2022–2026, korelacja z ^SOX−^NDX i SMH−XLP;
(2) koszyki W4–W7 jako ETF-y (SMH long / XLP short) i dekompozycja spreadu na betę czynnikową;
(3) reżimy warunkowe dla momentum 6M i odwrócenia 1T (VIX>20, ^NDX<MA50, ^NDX<MA200,
    ^SOX 10 sesji < −8%, tydzień po dużym tygodniu |^NDX|>4%, tygodnie „jak W7");
(4) bramka P0/P1/P2 systemu (progi z rutyny/tygodniowa.md, z histerezą i bez) —
    częstość 2022–2026 i wpływ gross 50%/0% na momentum/odwrócenie.

Wspólny harness (jak bt_momentum.py): D0 = ostatnia sesja tygodnia ISO → D5 = ostatnia sesja
następnego tygodnia; noga long = r_spółki − r_NDX, short = −(r_spółki − r_NDX);
spread_pp = śr. 5 long + śr. 5 short (p.p. nominału jednej strony; gross = 2).
Koszty: 0,10% × nominał nogi (0,2 strony) za każdą zmienioną nazwę + 6%/rok × gross × dni/365.
Sygnały wyłącznie z cen ≤ D0.
"""
import json, math, sys
import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
KOSZ = f'{BASE}/analiza/koszyki_historia.json'
NAME = 'rezim-i-zaklad-czynnikowy'
OUT_CSV = f'{BASE}/analiza/bt_{NAME}_serie.csv'
OUT_MD = f'{BASE}/analiza/bt_{NAME}.md'
OUT_JSON = f'{BASE}/analiza/bt_{NAME}_summary.json'

NON_CAND = ['^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV']
COST_LEG = 0.0010
FIN_RATE = 0.06
N_RAND = 2000
SEED = 20261018
NL = NS = 5
L_MOM = 126

HARD = ['MU', 'AMD', 'AVGO', 'MRVL', 'LITE', 'SNDK', 'STX', 'WDC', 'AMAT', 'LRCX', 'KLAC', 'TER', 'ALAB', 'NVDA']
DEFN = ['PEP', 'CMCSA', 'SBUX', 'TMUS', 'KHC', 'MDLZ', 'KDP', 'CCEP', 'MNST', 'XEL', 'AEP', 'EXC', 'PAYX', 'ADP']

# ----------------------------------------------------------------------------- dane
df = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
df = df[df['^NDX'].notna()]
df = df.ffill(limit=3)
cands = [c for c in df.columns if c not in NON_CAND]
cidx = {c: i for i, c in enumerate(cands)}
dates = df.index
P = df[cands].to_numpy(dtype=float)
NDX = df['^NDX'].to_numpy(dtype=float)
SOX = df['^SOX'].to_numpy(dtype=float)
VIX = df['^VIX'].to_numpy(dtype=float)
SMH = df['SMH'].to_numpy(dtype=float)
XLP = df['XLP'].to_numpy(dtype=float)
nT, nS = P.shape

RN = np.concatenate([[np.nan], NDX[1:] / NDX[:-1] - 1])
MA200 = pd.Series(NDX).rolling(200).mean().to_numpy()
MA50 = pd.Series(NDX).rolling(50).mean().to_numpy()
MAX252 = pd.Series(NDX).rolling(252, min_periods=120).max().to_numpy()
DD = NDX / MAX252 - 1

# okna tygodniowe (ISO)
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
WSOX = SOX[D5] / SOX[D0] - 1
WSMH = SMH[D5] / SMH[D0] - 1
WXLP = XLP[D5] / XLP[D0] - 1
EX = WR - WN[:, None]
DAYS = np.array([(dates[b] - dates[a]).days for a, b in zip(D0, D5)])
YEAR = np.array([dates[i].year for i in D0])
VIX0 = VIX[D0]
F_SOX = WSOX - WN            # czynnik: SOX − NDX w oknie
F_ETF = WSMH - WXLP          # czynnik: SMH − XLP w oknie (= spread harnessu dla ETF 5L SMH/5S XLP)

# poprzedni tydzień (zakończony na D0) — do odwrócenia 1T i warunku „po dużym tygodniu"
PREV_WN = np.full(nW, np.nan); PREV_WSOX = np.full(nW, np.nan); PREV_WR = np.full((nW, nS), np.nan)
for w in range(1, nW):
    PREV_WN[w] = WN[w - 1]; PREV_WSOX[w] = WSOX[w - 1]; PREV_WR[w] = WR[w - 1]
SOX10 = np.full(nW, np.nan)
for w in range(nW):
    i = D0[w]
    if i >= 10:
        SOX10[w] = SOX[i] / SOX[i - 10] - 1

# momentum 6M na D0 (tylko dane ≤ D0)
MOM6 = np.full((nW, nS), np.nan)
for w in range(nW):
    i = D0[w]
    if i >= L_MOM:
        MOM6[w] = P[i] / P[i - L_MOM] - 1
VALID = ~np.isnan(MOM6) & ~np.isnan(WR)      # pełne okno sygnału + cena na D5 (dostępność danych)


# ----------------------------------------------------------------------------- narzędzia
def pick(score_row, valid_row, pool=None, n=5, top=True):
    idx = np.arange(nS) if pool is None else np.array(pool)
    idx = idx[valid_row[idx]]
    if len(idx) < n:
        return None
    s = score_row[idx]
    order = np.argsort(-s if top else s)
    return list(idx[order[:n]])


def run_equal(longs, shorts):
    out = dict(spread=np.full(nW, np.nan), long=np.full(nW, np.nan), short=np.full(nW, np.nan),
               hits=np.zeros(nW), legs=np.zeros(nW), turn=np.zeros(nW))
    prevL = prevS = None
    for w in range(nW):
        if longs[w] is None or shorts[w] is None:
            prevL = prevS = None
            continue
        el = EX[w, longs[w]]; es = -EX[w, shorts[w]]
        out['long'][w] = el.mean() * 100
        out['short'][w] = es.mean() * 100
        out['spread'][w] = out['long'][w] + out['short'][w]
        out['hits'][w] = (el > 0).sum() + (es > 0).sum(); out['legs'][w] = NL + NS
        out['turn'][w] = (NL + NS) if prevL is None else \
            len(set(longs[w]) - set(prevL)) + len(set(shorts[w]) - set(prevS))
        prevL, prevS = longs[w], shorts[w]
    return out


def costs(out, gross=None):
    g = np.ones(nW) if gross is None else gross
    rot = out['turn'] * COST_LEG * (1.0 / NL) * 100 * g
    if gross is not None:
        dg = np.abs(np.diff(g)); dg = np.concatenate([[0.0], dg])   # pierwsze zbudowanie liczy już `turn`
        rot = rot + dg * 2 * COST_LEG * 100       # zmiana gross: 0,10% × |Δgross| na obu stronach
    fin = FIN_RATE * 2.0 * g * DAYS / 365 * 100
    return rot, fin


def metrics(sp, mask=None, hits=None, legs=None):
    m = ~np.isnan(sp)
    if mask is not None:
        m &= mask
    x = sp[m]
    n = len(x)
    if n < 2:
        return dict(n=n, mean=np.nan, median=np.nan, sigma=np.nan, t=np.nan, sharpe=np.nan,
                    hit=np.nan, hit_legs=np.nan, maxdd=np.nan, worst=np.nan, best=np.nan)
    mu, sd = x.mean(), x.std(ddof=1)
    cum = np.cumsum(x); dd = (np.maximum.accumulate(cum) - cum).max()
    hl = np.nan
    if hits is not None and legs is not None and legs[m].sum() > 0:
        hl = hits[m].sum() / legs[m].sum()
    return dict(n=n, mean=mu, median=float(np.median(x)), sigma=sd,
                t=mu / sd * math.sqrt(n) if sd > 0 else np.nan,
                sharpe=mu / sd * math.sqrt(52) if sd > 0 else np.nan,
                hit=(x > 0).mean(), hit_legs=hl, maxdd=dd, worst=x.min(), best=x.max())


def fmt(v, d=2):
    if v is None or (isinstance(v, float) and (np.isnan(v))):
        return '—'
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    return f'{v:.{d}f}'


def row(name, m, extra=''):
    return (f"| {name} | {m['n']} | {fmt(m['mean'])} | {fmt(m['median'])} | {fmt(m['sigma'])} | {fmt(m['t'])} | "
            f"{fmt(m['sharpe'])} | {fmt(m['hit']*100,0) if not np.isnan(m['hit']) else '—'}% | "
            f"{fmt(m['hit_legs']*100,0) if not (m['hit_legs'] is None or np.isnan(m['hit_legs'])) else '—'}% | "
            f"{fmt(m['maxdd'],1)} | {fmt(m['worst'],1)} | {fmt(m['best'],1)} |{extra}")


HDR = ('| wariant | okna | średnia pp | mediana | σ | t-stat | Sharpe | hit | hit nóg | maxDD | najgorsze | najlepsze |\n'
       '|---|---|---|---|---|---|---|---|---|---|---|---|')


def corr(a, b, mask=None):
    m = ~np.isnan(a) & ~np.isnan(b)
    if mask is not None:
        m &= mask
    if m.sum() < 3:
        return np.nan, int(m.sum())
    return float(np.corrcoef(a[m], b[m])[0, 1]), int(m.sum())


def ols(y, x, mask=None):
    m = ~np.isnan(y) & ~np.isnan(x)
    if mask is not None:
        m &= mask
    X = np.column_stack([np.ones(m.sum()), x[m]])
    b, *_ = np.linalg.lstsq(X, y[m], rcond=None)
    res = y[m] - X @ b
    r2 = 1 - res.var() / y[m].var() if y[m].var() > 0 else np.nan
    return b[0], b[1], r2, int(m.sum()), res.std(ddof=2)


def breakdown(sp, hits, legs, base_mask, lines):
    lines.append(HDR)
    for y in (2022, 2023, 2024, 2025, 2026):
        lines.append(row(str(y), metrics(sp, base_mask & (YEAR == y), hits, legs)))
    lines.append(row('VIX>20 na D0', metrics(sp, base_mask & (VIX0 > 20), hits, legs)))
    lines.append(row('VIX≤20 na D0', metrics(sp, base_mask & (VIX0 <= 20), hits, legs)))
    below = NDX[D0] < MA200[D0]
    lines.append(row('NDX < MA200', metrics(sp, base_mask & below & ~np.isnan(MA200[D0]), hits, legs)))
    lines.append(row('NDX > MA200', metrics(sp, base_mask & ~below & ~np.isnan(MA200[D0]), hits, legs)))


md = []
summary = {}

# ----------------------------------------------------------------------------- BASELINE losowy
rng = np.random.default_rng(SEED)
RAND = np.full((nW, N_RAND), np.nan)
RAND_LEGHIT = np.full((nW, N_RAND), np.nan)
for w in range(nW):
    idx = np.where(VALID[w])[0]
    if len(idx) < NL + NS:
        continue
    for k in range(N_RAND):
        pk = rng.choice(idx, NL + NS, replace=False)
        el = EX[w, pk[:NL]]; es = -EX[w, pk[NL:]]
        RAND[w, k] = (el.mean() + es.mean()) * 100
        RAND_LEGHIT[w, k] = ((el > 0).sum() + (es > 0).sum()) / (NL + NS)
RAND_MASK = ~np.isnan(RAND[:, 0])


def baseline_stats(mask):
    X = RAND[mask]
    pooled = X.ravel()
    means = X.mean(axis=0); sds = X.std(axis=0, ddof=1); n = X.shape[0]
    ts = means / sds * math.sqrt(n)
    return dict(n=n, sigma_pooled=float(pooled.std(ddof=1)), p5=float(np.percentile(pooled, 5)),
                p95=float(np.percentile(pooled, 95)), mean_p5=float(np.percentile(means, 5)),
                mean_p95=float(np.percentile(means, 95)), t_p5=float(np.percentile(ts, 5)),
                t_p95=float(np.percentile(ts, 95)), t_p975=float(np.percentile(ts, 97.5)),
                sharpe_p95=float(np.percentile(means / sds * math.sqrt(52), 95)),
                sigma_strat_p5=float(np.percentile(sds, 5)), sigma_strat_p95=float(np.percentile(sds, 95)))


# ----------------------------------------------------------------------------- strategie bazowe (do (3) i (4))
H_IDX = [cidx[t] for t in HARD]
D_IDX = [cidx[t] for t in DEFN]

Lp = [None] * nW; Sp = [None] * nW         # proxy czynnikowe
Lm = [None] * nW; Sm = [None] * nW         # momentum 6M, całe uniwersum
Lr = [None] * nW; Sr = [None] * nW         # odwrócenie 1T (long = 5 najgorszych poprz. tygodnia)
for w in range(nW):
    Lp[w] = pick(MOM6[w], VALID[w], H_IDX, top=True)
    Sp[w] = pick(MOM6[w], VALID[w], D_IDX, top=False)
    Lm[w] = pick(MOM6[w], VALID[w], top=True)
    Sm[w] = pick(MOM6[w], VALID[w], top=False)
    if w >= 1 and not np.isnan(PREV_WN[w]):
        v = VALID[w] & ~np.isnan(PREV_WR[w])
        Lr[w] = pick(PREV_WR[w], v, top=False)
        Sr[w] = pick(PREV_WR[w], v, top=True)

o_proxy = run_equal(Lp, Sp)
o_mom = run_equal(Lm, Sm)
o_rev = run_equal(Lr, Sr)
COMMON = ~np.isnan(o_proxy['spread']) & ~np.isnan(o_mom['spread']) & ~np.isnan(o_rev['spread']) & RAND_MASK
first_common = dates[D0[np.where(COMMON)[0][0]]].date()

md.append(f'# Zakład czynnikowy i reżimy (agent: {NAME})\n')
md.append(f'Dane: `{CSV}` — {nT} sesji {dates[0].date()}…{dates[-1].date()}, {nS} kandydatów (skład dzisiejszy → survivorship bias). '
          f'Okna tygodniowe: {nW}; wspólny zbiór okien (proxy, momentum 6M i odwrócenie 1T mają sygnał): {int(COMMON.sum())} od D0 = {first_common}.\n')
md.append('Harness: D0 = ostatnia sesja tygodnia ISO → D5 = ostatnia sesja następnego tygodnia; noga long = r − r_NDX, short = −(r − r_NDX); '
          'spread_pp = śr. 5 long + śr. 5 short. Sygnały tylko z cen ≤ D0; spółki bez pełnego okna 126 sesji wykluczone w danym oknie '
          '(ALAB wchodzi od 2024-09, SNDK od 2025-08 itd.). Koszty: 0,10% × nominał nogi (0,2 strony) za każdą zmienioną nazwę '
          '+ finansowanie 6%/rok × gross (2 strony × udział) × dni/365; przy bramce dodatkowo 0,10% × 2 × |Δgross|.\n')

bs = baseline_stats(COMMON)
summary['baseline'] = bs
md.append(f"**BASELINE** (2000 losowych koszyków 5/5 w każdym z {bs['n']} wspólnych okien): σ pojedynczego tygodnia (pooled) = **{bs['sigma_pooled']:.2f} pp**, "
          f"przedział 5–95% tygodniowego spreadu = **{bs['p5']:.1f} … {bs['p95']:.1f} pp**; rozkład średniej 2000 losowych STRATEGII: "
          f"5–95% = {bs['mean_p5']:.2f} … {bs['mean_p95']:.2f} pp/tydz., t-stat 5–95% = {bs['t_p5']:.2f} … {bs['t_p95']:.2f} (97,5% = {bs['t_p975']:.2f}), "
          f"Sharpe 95% = {bs['sharpe_p95']:.2f}.\n")


def report_variant(key, label, o, mask, note=''):
    rot, fin = costs(o)
    sp = o['spread']
    m = metrics(sp, mask, o['hits'], o['legs'])
    net = sp - rot - fin
    mn = metrics(net, mask)
    pct = float((RAND[mask].mean(axis=0) < m['mean']).mean()) if mask.sum() else np.nan
    summary.setdefault('variants', {})[key] = dict(
        name=label, n=m['n'], mean=round(m['mean'], 3), median=round(m['median'], 3), sigma=round(m['sigma'], 3),
        t=round(m['t'], 3), sharpe=round(m['sharpe'], 3), hit=round(m['hit'], 3), hit_legs=round(m['hit_legs'], 3),
        maxdd=round(m['maxdd'], 2), worst=round(m['worst'], 2), best=round(m['best'], 2),
        net_mean=round(mn['mean'], 3), net_t=round(mn['t'], 3), net_sharpe=round(mn['sharpe'], 3),
        turn=round(float(o['turn'][mask].mean()), 2), pct_random=round(pct, 4), note=note)
    return m, mn, pct


# ============================================================================ (1) PROXY CZYNNIKOWE
md.append('\n## 1. Proxy zakładu czynnikowego: AI-hardware long (top 5 mom 6M z 14) vs defensywy short (5 najgorszych mom 6M z 14)\n')
md.append(f'Listy: LONG z {{{", ".join(HARD)}}}; SHORT z {{{", ".join(DEFN)}}}. Spread liczony w harnessie (excess vs ^NDX po obu stronach).\n')
m_proxy, mn_proxy, pct_proxy = report_variant('proxy_hw_vs_def', 'proxy AI-hardware L / defensywy S (6M)', o_proxy, COMMON,
                                              'zamknięte listy 14/14; selekcja wg momentum 6M wewnątrz list')
m_mom, mn_mom, pct_mom = report_variant('mom6M', 'momentum 6M top5/bottom5 (całe uniwersum)', o_mom, COMMON, 'referencja (agent momentum: a_6M)')
m_rev, mn_rev, pct_rev = report_variant('rev1W', 'odwrócenie 1T: long 5 najgorszych / short 5 najlepszych poprz. tygodnia', o_rev, COMMON,
                                        'kontrariańskie 1T')
md.append(HDR)
md.append(row('proxy HW/DEF 6M', m_proxy))
md.append(row('momentum 6M (uniwersum)', m_mom))
md.append(row('odwrócenie 1T (uniwersum)', m_rev))
md.append(f"| BASELINE losowe 5/5 | {bs['n']} | 0.00 | — | {bs['sigma_pooled']:.2f} (pooled) | 5–95%: {bs['t_p5']:.2f}…{bs['t_p95']:.2f} | 95%: {bs['sharpe_p95']:.2f} | — | 50% | — | p5 {bs['p5']:.1f} | p95 {bs['p95']:.1f} |")
md.append('\nPo kosztach (wspólne okna):\n')
md.append('| wariant | obrót nóg/tydz. | brutto pp | netto pp | t netto | Sharpe netto | pct wśród 2000 losowych strategii (brutto) |\n|---|---|---|---|---|---|---|')
for k in ('proxy_hw_vs_def', 'mom6M', 'rev1W'):
    v = summary['variants'][k]
    md.append(f"| {v['name']} | {v['turn']:.1f} | {v['mean']:.2f} | {v['net_mean']:.2f} | {v['net_t']:.2f} | {v['net_sharpe']:.2f} | {v['pct_random']*100:.1f}% |")

# korelacje
md.append('\n### 1a. Korelacja tygodniowego spreadu proxy z czynnikami\n')
md.append('| para | okna | r Pearsona | beta (OLS spread ~ czynnik) | R² | alfa pp/tydz. |\n|---|---|---|---|---|---|')
corr_tab = {}
for lab, f in (('proxy vs (^SOX−^NDX)', F_SOX * 100), ('proxy vs (SMH−XLP)', F_ETF * 100)):
    r, n = corr(o_proxy['spread'], f, COMMON); a, b, r2, n2, _ = ols(o_proxy['spread'], f, COMMON)
    corr_tab[lab] = dict(r=r, n=n, beta=b, r2=r2, alpha=a)
    md.append(f'| {lab} | {n} | {r:.2f} | {b:.2f} | {r2:.2f} | {a:.2f} |')
for lab, f in (('momentum 6M vs (^SOX−^NDX)', F_SOX * 100), ('momentum 6M vs (SMH−XLP)', F_ETF * 100), ('momentum 6M vs proxy', o_proxy['spread'])):
    r, n = corr(o_mom['spread'], f, COMMON); a, b, r2, n2, _ = ols(o_mom['spread'], f, COMMON)
    corr_tab[lab] = dict(r=r, n=n, beta=b, r2=r2, alpha=a)
    md.append(f'| {lab} | {n} | {r:.2f} | {b:.2f} | {r2:.2f} | {a:.2f} |')
r, n = corr(o_rev['spread'], o_proxy['spread'], COMMON); corr_tab['odwrócenie 1T vs proxy'] = dict(r=r, n=n)
md.append(f'| odwrócenie 1T vs proxy | {n} | {r:.2f} | — | — | — |')
r, n = corr(F_SOX, F_ETF, COMMON); corr_tab['(^SOX−^NDX) vs (SMH−XLP)'] = dict(r=r, n=n)
md.append(f'| (^SOX−^NDX) vs (SMH−XLP) | {n} | {r:.2f} | — | — | — |')
summary['korelacje'] = corr_tab

md.append('\nKorelacja proxy vs czynniki po latach:\n')
md.append('| rok | okna | r(proxy, SOX−NDX) | r(proxy, SMH−XLP) | r(mom6M, SMH−XLP) | śr. proxy pp | śr. SMH−XLP pp | śr. SOX−NDX pp |\n|---|---|---|---|---|---|---|---|')
for y in (2022, 2023, 2024, 2025, 2026):
    mk = COMMON & (YEAR == y)
    r1, n = corr(o_proxy['spread'], F_SOX, mk); r2_, _ = corr(o_proxy['spread'], F_ETF, mk); r3, _ = corr(o_mom['spread'], F_ETF, mk)
    md.append(f'| {y} | {n} | {r1:.2f} | {r2_:.2f} | {r3:.2f} | {np.nanmean(o_proxy["spread"][mk]):.2f} | {np.nanmean(F_ETF[mk])*100:.2f} | {np.nanmean(F_SOX[mk])*100:.2f} |')

md.append('\nRozbicie proxy na lata i reżimy (brutto):\n')
breakdown(o_proxy['spread'], o_proxy['hits'], o_proxy['legs'], COMMON, md)

# jak bardzo faktyczne koszyki W1–W8 pokrywały się z listami proxy
kh = json.load(open(KOSZ))
KOSZYKI = {
 'W1': dict(d0='2026-08-26', settle='2026-08-28', long=['MU','LITE','CEG','AMD','MSFT'], short=['INTU','WDAY','APP','TSLA','CMCSA']),
 'W2': dict(d0='2026-08-28', settle='2026-09-04', long=['MU','NVDA','MSFT','AMD','CEG'], short=['INTU','APP','TSLA','CMCSA','PEP']),
 'W3': dict(d0='2026-09-04', settle='2026-09-11', long=['MU','NVDA','AMD','AVGO','STX'], short=['TSLA','INTU','SBUX','APP','CMCSA']),
 'W4': dict(d0='2026-09-11', settle='2026-09-28'),
 'W5': dict(d0='2026-09-28', settle='2026-10-02'),
 'W6': dict(d0='2026-10-02', settle='2026-10-09'),
 'W7': dict(d0='2026-10-09', settle='2026-10-16'),
}
for k in ('W4', 'W5', 'W6', 'W7'):
    kk = kh['koszyki'][f'2026-{k}']
    KOSZYKI[k]['long'] = kk['long']; KOSZYKI[k]['short'] = kk['short']
hist_spread = {h['week'].split('-')[1]: h['spread_pp'] for h in kh['history']}

md.append('\n### 1b. Ile zakładu czynnikowego było w faktycznych koszykach W1–W7\n')
md.append('| koszyk | long w liście HW | short w liście DEF | spread wg history pp | spread proxy w tym oknie pp | SMH−XLP pp | SOX−NDX pp |\n|---|---|---|---|---|---|---|')
DI = {d.strftime('%Y-%m-%d'): i for i, d in enumerate(dates)}


def win_ret(arr, d0, d1):
    return arr[DI[d1]] / arr[DI[d0]] - 1


def basket_spread(long, short, d0, d1):
    rn = win_ret(NDX, d0, d1)
    el = [win_ret(P[:, cidx[t]], d0, d1) - rn for t in long]
    es = [-(win_ret(P[:, cidx[t]], d0, d1) - rn) for t in short]
    return 100 * (np.mean(el) + np.mean(es)), el, es


overlap_rows = {}
for k, kz in KOSZYKI.items():
    d0, d1 = kz['d0'], kz['settle']
    i0 = DI[d0]
    mom_row = P[i0] / P[i0 - L_MOM] - 1
    valid_row = ~np.isnan(mom_row)
    lp = pick(mom_row, valid_row, H_IDX, top=True); spx = pick(mom_row, valid_row, D_IDX, top=False)
    sp_proxy, _, _ = basket_spread([cands[i] for i in lp], [cands[i] for i in spx], d0, d1)
    nh = sum(t in HARD for t in kz['long']); nd = sum(t in DEFN for t in kz['short'])
    f_etf = 100 * (win_ret(SMH, d0, d1) - win_ret(XLP, d0, d1)); f_sox = 100 * (win_ret(SOX, d0, d1) - win_ret(NDX, d0, d1))
    overlap_rows[k] = dict(long_hw=nh, short_def=nd, hist=hist_spread.get(k), proxy=sp_proxy, smh_xlp=f_etf, sox_ndx=f_sox,
                           proxy_long=[cands[i] for i in lp], proxy_short=[cands[i] for i in spx])
    md.append(f"| {k} ({d0}→{d1}) | {nh}/5 | {nd}/5 | {fmt(hist_spread.get(k))} | {sp_proxy:.2f} | {f_etf:.2f} | {f_sox:.2f} |")
summary['overlap_W1_W7'] = overlap_rows
md.append('\nUwaga: W4 rozliczano po 11 sesjach (do 2026-09-28); spready „history" liczone przez rutynę z cen d0 i cen rozliczenia (czasem Yahoo/TV, nie te same zamknięcia), więc mogą odbiegać o kilka dziesiątych pp od przeliczenia z closes_5y.csv.\n')

# ============================================================================ (2) KOSZYKI W4–W7 JAKO ETF-Y
md.append('\n## 2. Koszyki W4–W7: faktyczny skład vs ETF-y (SMH long / XLP short) i beta czynnikowa\n')
md.append('Spread ETF w harnessie = (r_SMH − r_NDX) + (−(r_XLP − r_NDX)) = r_SMH − r_XLP. Beta koszyka: OLS tygodniowego spreadu '
          'KOSZYKA O STAŁYM SKŁADZIE (okna ISO sprzed D0, do 104 tygodni wstecz, bez look-ahead) na czynnik SMH−XLP oraz ^SOX−^NDX; '
          '„beta czynnikowa" = beta × zwrot czynnika w oknie koszyka; reszta = spread − beta czynnikowa.\n')
md.append('| koszyk | okno | spread faktyczny pp (przeliczony) | history pp | ETF SMH−XLP pp | ETF ^SOX−XLP pp | beta(SMH−XLP) [R²] | beta czynnikowa pp | reszta pp | udział bety % | beta(SOX−NDX) [R²] | beta czynn. SOX pp | reszta SOX pp |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
etf_rows = {}
for k in ('W4', 'W5', 'W6', 'W7'):
    kz = KOSZYKI[k]; d0, d1 = kz['d0'], kz['settle']
    sp_act, el, es = basket_spread(kz['long'], kz['short'], d0, d1)
    f_etf = 100 * (win_ret(SMH, d0, d1) - win_ret(XLP, d0, d1))
    f_soxxlp = 100 * (win_ret(SOX, d0, d1) - win_ret(XLP, d0, d1))
    f_sox = 100 * (win_ret(SOX, d0, d1) - win_ret(NDX, d0, d1))
    # historyczny spread koszyka o stałym składzie
    li = [cidx[t] for t in kz['long']]; si = [cidx[t] for t in kz['short']]
    hist_sp = np.full(nW, np.nan)
    for w in range(nW):
        if dates[D5[w]] <= pd.Timestamp(d0) and not np.isnan(EX[w, li]).any() and not np.isnan(EX[w, si]).any():
            hist_sp[w] = 100 * (EX[w, li].mean() - EX[w, si].mean())
    valid_w = np.where(~np.isnan(hist_sp))[0][-104:]
    mk = np.zeros(nW, bool); mk[valid_w] = True
    a1, b1, r21, n1, _ = ols(hist_sp, F_ETF * 100, mk)
    a2, b2, r22, n2, _ = ols(hist_sp, F_SOX * 100, mk)
    fac1 = b1 * f_etf; fac2 = b2 * f_sox
    share = fac1 / sp_act * 100 if sp_act != 0 else np.nan
    etf_rows[k] = dict(spread_actual=sp_act, hist=hist_spread.get(k), etf_smh_xlp=f_etf, etf_sox_xlp=f_soxxlp, beta_etf=b1, r2_etf=r21,
                       n_hist=n1, factor_etf=fac1, resid_etf=sp_act - fac1, share_etf_pct=share, beta_sox=b2, r2_sox=r22,
                       factor_sox=fac2, resid_sox=sp_act - fac2, alpha_hist_pp=a1, hist_mean_pp=float(np.nanmean(hist_sp[mk])))
    md.append(f"| {k} | {d0}→{d1} | {sp_act:.2f} | {fmt(hist_spread.get(k))} | {f_etf:.2f} | {f_soxxlp:.2f} | {b1:.2f} [{r21:.2f}] (n={n1}) | {fac1:.2f} | {sp_act-fac1:.2f} | {share:.0f}% | {b2:.2f} [{r22:.2f}] | {fac2:.2f} | {sp_act-fac2:.2f} |")
summary['etf_W4_W7'] = etf_rows
tot_act = sum(etf_rows[k]['spread_actual'] for k in etf_rows); tot_etf = sum(etf_rows[k]['etf_smh_xlp'] for k in etf_rows)
tot_fac = sum(etf_rows[k]['factor_etf'] for k in etf_rows)
md.append(f'\nSuma W4–W7: spread faktyczny {tot_act:.1f} pp; ETF SMH−XLP {tot_etf:.1f} pp; beta czynnikowa (SMH−XLP) {tot_fac:.1f} pp; '
          f'reszta {tot_act - tot_fac:.1f} pp. W6+W7: faktyczny {etf_rows["W6"]["spread_actual"]+etf_rows["W7"]["spread_actual"]:.1f} pp, '
          f'ETF {etf_rows["W6"]["etf_smh_xlp"]+etf_rows["W7"]["etf_smh_xlp"]:.1f} pp, beta czynnikowa {etf_rows["W6"]["factor_etf"]+etf_rows["W7"]["factor_etf"]:.1f} pp.\n')

# długookresowo: ETF-owy spread SMH−XLP w harnessie i proxy
m_etf = metrics(F_ETF * 100, COMMON); m_soxndx = metrics(F_SOX * 100, COMMON)
md.append('Dla skali — czynnik jako „strategia" 2022–2026 (wspólne okna):\n')
md.append(HDR)
md.append(row('ETF: long SMH / short XLP (= SMH−XLP)', m_etf))
md.append(row('^SOX − ^NDX', m_soxndx))
summary['variants']['etf_SMH_XLP'] = dict(name='ETF long SMH / short XLP', n=m_etf['n'], mean=round(m_etf['mean'], 3), sigma=round(m_etf['sigma'], 3),
                                          t=round(m_etf['t'], 3), sharpe=round(m_etf['sharpe'], 3), hit=round(m_etf['hit'], 3), maxdd=round(m_etf['maxdd'], 2),
                                          worst=round(m_etf['worst'], 2), best=round(m_etf['best'], 2),
                                          net_mean=round(m_etf['mean'] - FIN_RATE * 2 * 7 / 365 * 100, 3), note='czynnik czysty; koszt tylko finansowanie (brak rotacji)')

# ============================================================================ (3) REŻIMY WARUNKOWE
md.append('\n## 3. Reżimy warunkowe: momentum 6M vs odwrócenie 1T; kontynuacja czy odwrócenie po dużych tygodniach\n')
md.append('Warunek sprawdzany na D0 (dane ≤ D0). „Poprzedni tydzień" = okno ISO zakończone na D0. Index: zwrot ^NDX i (^SOX−^NDX) w NASTĘPNYM tygodniu (D0→D5). '
          'Przekrój: `rev1W` = long 5 najgorszych / short 5 najlepszych poprzedniego tygodnia (dodatni = przegrani odbijają); `mom6M` = top5/bottom5 6M. '
          'Dodatkowo „przegrani-10": średni excess 10 najgorszych spółek poprzedniego tygodnia w tygodniu następnym (dodatni = odbicie).\n')

below200 = (NDX[D0] < MA200[D0]) & ~np.isnan(MA200[D0])
below50 = (NDX[D0] < MA50[D0]) & ~np.isnan(MA50[D0])
conds = [
    ('wszystkie okna', COMMON),
    ('VIX>20 na D0', COMMON & (VIX0 > 20)),
    ('VIX≤20 na D0', COMMON & (VIX0 <= 20)),
    ('^NDX<MA50', COMMON & below50),
    ('^NDX≥MA50', COMMON & ~below50),
    ('^NDX<MA200', COMMON & below200),
    ('^NDX≥MA200', COMMON & ~below200),
    ('^SOX 10 sesji < −8%', COMMON & (SOX10 < -0.08)),
    ('^SOX 10 sesji ≥ −8%', COMMON & ~(SOX10 < -0.08)),
    ('po dużym tygodniu |^NDX|>4%', COMMON & (np.abs(PREV_WN) > 0.04)),
    ('po dużym spadku ^NDX<−4%', COMMON & (PREV_WN < -0.04)),
    ('po dużym wzroście ^NDX>+4%', COMMON & (PREV_WN > 0.04)),
    ('„jak W7": ^NDX<−4% i ^SOX<−8%', COMMON & (PREV_WN < -0.04) & (PREV_WSOX < -0.08)),
    ('po spokojnym tygodniu |^NDX|≤4%', COMMON & (np.abs(PREV_WN) <= 0.04)),
]

# przegrani-10 / wygrani-10 poprzedniego tygodnia
LOS10 = np.full(nW, np.nan); WIN10 = np.full(nW, np.nan)
for w in range(nW):
    if np.isnan(PREV_WN[w]):
        continue
    v = VALID[w] & ~np.isnan(PREV_WR[w])
    idx = np.where(v)[0]
    if len(idx) < 20:
        continue
    order = idx[np.argsort(PREV_WR[w, idx])]
    LOS10[w] = EX[w, order[:10]].mean() * 100
    WIN10[w] = EX[w, order[-10:]].mean() * 100


def tst(x):
    x = x[~np.isnan(x)]
    return x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan


md.append('| warunek na D0 | okna | ^NDX nast. tydz. śr. % [hit>0] | ^SOX−^NDX nast. tydz. śr. pp | mom6M śr. pp [t] hit | rev1W śr. pp [t] hit | przegrani-10 excess pp [t] | wygrani-10 excess pp [t] | proxy HW/DEF śr. pp [t] |\n|---|---|---|---|---|---|---|---|---|')
regime_rows = {}
for lab, mk in conds:
    n = int(mk.sum())
    if n == 0:
        md.append(f'| {lab} | 0 | — | — | — | — | — | — | — |'); continue
    ndx_next = WN[mk] * 100; sox_next = F_SOX[mk] * 100
    mm = metrics(o_mom['spread'], mk); mr = metrics(o_rev['spread'], mk); mp = metrics(o_proxy['spread'], mk)
    l10 = LOS10[mk]; w10 = WIN10[mk]
    regime_rows[lab] = dict(n=n, ndx_next_mean=float(ndx_next.mean()), ndx_next_hit=float((ndx_next > 0).mean()),
                            sox_ndx_next=float(sox_next.mean()), mom_mean=mm['mean'], mom_t=mm['t'], mom_hit=mm['hit'],
                            rev_mean=mr['mean'], rev_t=mr['t'], rev_hit=mr['hit'], losers10=float(np.nanmean(l10)), losers10_t=tst(l10),
                            winners10=float(np.nanmean(w10)), winners10_t=tst(w10), proxy_mean=mp['mean'], proxy_t=mp['t'])
    md.append(f"| {lab} | {n} | {ndx_next.mean():.2f} [{(ndx_next>0).mean()*100:.0f}%] | {sox_next.mean():.2f} | "
              f"{fmt(mm['mean'])} [{fmt(mm['t'],1)}] {fmt(mm['hit']*100,0) if n>1 else '—'}% | {fmt(mr['mean'])} [{fmt(mr['t'],1)}] {fmt(mr['hit']*100,0) if n>1 else '—'}% | "
              f"{np.nanmean(l10):.2f} [{fmt(tst(l10),1)}] | {np.nanmean(w10):.2f} [{fmt(tst(w10),1)}] | {fmt(mp['mean'])} [{fmt(mp['t'],1)}] |")
summary['rezimy'] = regime_rows

# lista tygodni „jak W7" i po dużych spadkach
md.append('\nTygodnie po dużym spadku ^NDX (<−4% w tygodniu zakończonym na D0) — co było w następnym tygodniu:\n')
md.append('| D0 | ^NDX poprz. % | ^SOX poprz. % | VIX D0 | ^NDX nast. % | ^SOX−^NDX nast. pp | mom6M pp | rev1W pp | przegrani-10 pp | proxy pp |\n|---|---|---|---|---|---|---|---|---|---|')
big_down = []
for w in np.where(COMMON & (PREV_WN < -0.04))[0]:
    tag = ' **(jak W7)**' if PREV_WSOX[w] < -0.08 else ''
    big_down.append(dict(d0=str(dates[D0[w]].date()), ndx_prev=PREV_WN[w]*100, sox_prev=PREV_WSOX[w]*100, vix=VIX0[w], ndx_next=WN[w]*100,
                         sox_ndx_next=F_SOX[w]*100, mom=o_mom['spread'][w], rev=o_rev['spread'][w], los10=LOS10[w], proxy=o_proxy['spread'][w], like_w7=bool(PREV_WSOX[w] < -0.08)))
    md.append(f"| {dates[D0[w]].date()}{tag} | {PREV_WN[w]*100:.1f} | {PREV_WSOX[w]*100:.1f} | {VIX0[w]:.1f} | {WN[w]*100:.1f} | {F_SOX[w]*100:.1f} | {o_mom['spread'][w]:.1f} | {o_rev['spread'][w]:.1f} | {LOS10[w]:.1f} | {o_proxy['spread'][w]:.1f} |")
summary['po_duzym_spadku'] = big_down
# tydzień W7 sam (2026-10-09 → 2026-10-16) z realnych danych
w7 = np.where(dates[D0] == pd.Timestamp('2026-10-09'))[0]
if len(w7):
    w = w7[0]
    md.append(f"\nSam tydzień W7 (D0 2026-10-09→2026-10-16): ^NDX {WN[w]*100:.2f}%, ^SOX {WSOX[w]*100:.2f}%, SMH−XLP {F_ETF[w]*100:.2f} pp, mom6M {o_mom['spread'][w]:.2f} pp, "
              f"rev1W {o_rev['spread'][w]:.2f} pp, proxy {o_proxy['spread'][w]:.2f} pp. Następny tydzień (po W7) jeszcze nie istnieje w danych — "
              f"tabela wyżej to jedyna statystyka ex ante dla tygodnia W8.\n")
    summary['W7_window'] = dict(ndx=WN[w]*100, sox=WSOX[w]*100, smh_xlp=F_ETF[w]*100, mom=o_mom['spread'][w], rev=o_rev['spread'][w], proxy=o_proxy['spread'][w])

md.append('\nPełne rozbicie momentum 6M i odwrócenia 1T (brutto, wspólne okna):\n')
md.append('\n**momentum 6M**\n'); breakdown(o_mom['spread'], o_mom['hits'], o_mom['legs'], COMMON, md)
md.append('\n**odwrócenie 1T**\n'); breakdown(o_rev['spread'], o_rev['hits'], o_rev['legs'], COMMON, md)

# ============================================================================ (4) BRAMKA REŻIMU P0/P1/P2
md.append('\n## 4. Bramka reżimu P0/P1/P2 (progi z rutyny/tygodniowa.md KROK B0)\n')
md.append('Dziennie: P1 = ^NDX<MA200 LUB drawdown od max 252 sesji >10% LUB VIX>28; P2 = drawdown>20% LUB VIX>40 LUB sesja ≤−5%. '
          'Wariant „surowy" = poziom z progów w dniu D0; wariant „z histerezą" = automat jak w rutynie (z P2 do handlu po 5 kolejnych sesjach VIX<25 i ^NDX>MA50 → P1; '
          'z P1 do P0 po 3 kolejnych sesjach VIX<22 i ^NDX>MA200). Gross: P0 = 100%, P1 = 50%, P2 = 0%. Reżim odczytany na D0 obowiązuje w oknie D0→D5.\n')

raw = np.zeros(nT, int)
for i in range(nT):
    p2 = (DD[i] < -0.20) or (VIX[i] > 40) or (not np.isnan(RN[i]) and RN[i] <= -0.05)
    p1 = (not np.isnan(MA200[i]) and NDX[i] < MA200[i]) or (DD[i] < -0.10) or (VIX[i] > 28)
    raw[i] = 2 if p2 else (1 if p1 else 0)
state = np.zeros(nT, int); st_ = 0; c2 = 0; c1 = 0
for i in range(nT):
    r_ = raw[i]
    if r_ == 2:
        st_ = 2; c2 = 0; c1 = 0
    elif st_ == 2:
        ok = (VIX[i] < 25) and (not np.isnan(MA50[i]) and NDX[i] > MA50[i])
        c2 = c2 + 1 if ok else 0
        if c2 >= 5:
            st_ = 1; c2 = 0; c1 = 0
    elif st_ == 1:
        if r_ == 1:
            c1 = 0
        else:
            ok = (VIX[i] < 22) and (not np.isnan(MA200[i]) and NDX[i] > MA200[i])
            c1 = c1 + 1 if ok else 0
            if c1 >= 3:
                st_ = 0; c1 = 0
    else:
        if r_ == 1:
            st_ = 1; c1 = 0
    state[i] = st_
RAW0 = raw[D0]; HYS0 = state[D0]
G_RAW = np.where(RAW0 == 0, 1.0, np.where(RAW0 == 1, 0.5, 0.0))
G_HYS = np.where(HYS0 == 0, 1.0, np.where(HYS0 == 1, 0.5, 0.0))
# które progi strzelały (na D0)
trig = dict(ma200=(NDX[D0] < MA200[D0]) & ~np.isnan(MA200[D0]), dd10=DD[D0] < -0.10, vix28=VIX0 > 28,
            dd20=DD[D0] < -0.20, vix40=VIX0 > 40, ses5=RN[D0] <= -0.05)

md.append('Częstość (wspólne okna, odczyt na D0):\n')
md.append('| rok | okna | P1 surowy | P2 surowy | P1 z histerezą | P2 z histerezą | ^NDX<MA200 | DD>10% | VIX>28 | DD>20% | VIX>40 | sesja D0 ≤−5% | śr. gross hist. |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
freq = {}
for y in ('razem', 2022, 2023, 2024, 2025, 2026):
    mk = COMMON if y == 'razem' else COMMON & (YEAR == y)
    n = int(mk.sum())
    f = dict(n=n, p1_raw=int((RAW0[mk] == 1).sum()), p2_raw=int((RAW0[mk] == 2).sum()), p1_hys=int((HYS0[mk] == 1).sum()), p2_hys=int((HYS0[mk] == 2).sum()),
             **{k: int(v[mk].sum()) for k, v in trig.items()}, gross_hys=float(G_HYS[mk].mean()))
    freq[str(y)] = f
    md.append(f"| {y} | {n} | {f['p1_raw']} | {f['p2_raw']} | {f['p1_hys']} | {f['p2_hys']} | {f['ma200']} | {f['dd10']} | {f['vix28']} | {f['dd20']} | {f['vix40']} | {f['ses5']} | {f['gross_hys']*100:.0f}% |")
summary['bramka_czestosc'] = freq
# sesje dzienne P2 w całej próbie
md.append(f"\nSesje dzienne 2022–2026 w stanie P2 (z histerezą): {int((state[dates.year>=2022]==2).sum())} z {int((dates.year>=2022).sum())}; "
          f"P1: {int((state[dates.year>=2022]==1).sum())}. Epizody P2 (pierwsza sesja): " +
          ', '.join(str(dates[i].date()) for i in range(1, nT) if state[i] == 2 and state[i-1] != 2 and dates[i].year >= 2022) + '.\n')

# wynik strategii w reżimach bramki
md.append('\nCo bramka wycina — spread strategii w tygodniach wg stanu bramki (brutto, gross 100%):\n')
md.append('| stan na D0 | okna | ^NDX nast. % [hit] | mom6M śr. pp [t] | rev1W śr. pp [t] | proxy śr. pp [t] | SMH−XLP pp |\n|---|---|---|---|---|---|---|')
gate_rows = {}
for lab, arr in (('surowy', RAW0), ('z histerezą', HYS0)):
    for lv in (0, 1, 2):
        mk = COMMON & (arr == lv)
        n = int(mk.sum())
        if n == 0:
            md.append(f'| {lab} P{lv} | 0 | — | — | — | — | — |'); continue
        mm = metrics(o_mom['spread'], mk); mr = metrics(o_rev['spread'], mk); mp = metrics(o_proxy['spread'], mk)
        gate_rows[f'{lab} P{lv}'] = dict(n=n, ndx_next=float(WN[mk].mean()*100), mom_mean=mm['mean'], mom_t=mm['t'], rev_mean=mr['mean'], rev_t=mr['t'], proxy_mean=mp['mean'], smh_xlp=float(F_ETF[mk].mean()*100))
        md.append(f"| {lab} P{lv} | {n} | {WN[mk].mean()*100:.2f} [{(WN[mk]>0).mean()*100:.0f}%] | {fmt(mm['mean'])} [{fmt(mm['t'],1)}] | {fmt(mr['mean'])} [{fmt(mr['t'],1)}] | {fmt(mp['mean'])} [{fmt(mp['t'],1)}] | {F_ETF[mk].mean()*100:.2f} |")
summary['bramka_stany'] = gate_rows

md.append('\nStrategie z bramką (gross × spread; tygodnie P2 = 0 pp; koszty: rotacja × gross + 0,10%×2×|Δgross| + finansowanie × gross):\n')
md.append('| wariant | okna | brutto pp | σ | t | Sharpe | hit | maxDD | najgorsze | netto pp | t netto | Sharpe netto | śr. gross |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
gated = {}
for sname, o in (('mom6M', o_mom), ('rev1W', o_rev), ('proxy', o_proxy)):
    for gname, g in (('bez bramki', np.ones(nW)), ('bramka surowa', G_RAW), ('bramka z histerezą', G_HYS), ('tylko P2→0 (P1 pełny gross), hist.', np.where(HYS0 == 2, 0.0, 1.0)),
                     ('odwrotna: P1/P2 → gross 150%/200%', np.where(HYS0 == 0, 1.0, np.where(HYS0 == 1, 1.5, 2.0)))):
        sp = o['spread'] * g
        rot, fin = costs(o, g)
        net = sp - rot - fin
        m = metrics(sp, COMMON); mn = metrics(net, COMMON)
        key = f'{sname} | {gname}'
        gated[key] = dict(n=m['n'], mean=round(m['mean'], 3), sigma=round(m['sigma'], 3), t=round(m['t'], 3), sharpe=round(m['sharpe'], 3), hit=round(m['hit'], 3),
                          maxdd=round(m['maxdd'], 2), worst=round(m['worst'], 2), net_mean=round(mn['mean'], 3), net_t=round(mn['t'], 3), net_sharpe=round(mn['sharpe'], 3),
                          gross_mean=round(float(g[COMMON].mean()), 3))
        md.append(f"| {key} | {m['n']} | {m['mean']:.2f} | {m['sigma']:.2f} | {m['t']:.2f} | {m['sharpe']:.2f} | {m['hit']*100:.0f}% | {m['maxdd']:.1f} | {m['worst']:.1f} | {mn['mean']:.2f} | {mn['t']:.2f} | {mn['sharpe']:.2f} | {g[COMMON].mean()*100:.0f}% |")
summary['bramka_strategie'] = gated
for k in ('mom6M | bramka z histerezą', 'rev1W | bramka z histerezą', 'mom6M | bramka surowa'):
    v = gated[k]
    summary['variants'][k.replace(' | ', '__').replace(' ', '_')] = dict(name=k, n=v['n'], mean=v['mean'], sigma=v['sigma'], t=v['t'], sharpe=v['sharpe'], hit=v['hit'],
                                                                         maxdd=v['maxdd'], worst=v['worst'], net_mean=v['net_mean'], net_t=v['net_t'],
                                                                         note=f"śr. gross {v['gross_mean']*100:.0f}%")

# stan bramki w tygodniach W1–W8 systemu
md.append('\nStan bramki na D0 koszyków systemu (dla porównania z `rezim` w history):\n')
md.append('| koszyk | D0 | surowy | z histerezą | ^NDX vs MA200 % | DD od max 252 % | VIX |\n|---|---|---|---|---|---|---|')
for k, kz in list(KOSZYKI.items()) + [('W8', dict(d0='2026-10-16'))]:
    i = DI[kz['d0']]
    md.append(f"| {k} | {kz['d0']} | P{raw[i]} | P{state[i]} | {(NDX[i]/MA200[i]-1)*100:.1f} | {DD[i]*100:.1f} | {VIX[i]:.1f} |")

# ============================================================================ serie CSV
rows = []
for sname, o, L_, S_ in (('proxy_hw_vs_def', o_proxy, Lp, Sp), ('mom6M', o_mom, Lm, Sm), ('rev1W', o_rev, Lr, Sr)):
    for w in range(nW):
        if np.isnan(o['spread'][w]):
            continue
        rows.append(dict(variant=sname, date_d0=dates[D0[w]].date(), date_d5=dates[D5[w]].date(), spread_pp=round(o['spread'][w], 4),
                         long_pp=round(o['long'][w], 4), short_pp=round(o['short'][w], 4),
                         longs=' '.join(cands[i] for i in L_[w]), shorts=' '.join(cands[i] for i in S_[w]),
                         ndx_pct=round(WN[w]*100, 4), sox_ndx_pp=round(F_SOX[w]*100, 4), smh_xlp_pp=round(F_ETF[w]*100, 4),
                         vix_d0=round(VIX0[w], 2), ndx_below_ma200=int(below200[w]), ndx_below_ma50=int(below50[w]),
                         prev_ndx_pct=round(PREV_WN[w]*100, 4) if not np.isnan(PREV_WN[w]) else '', sox10_pct=round(SOX10[w]*100, 4) if not np.isnan(SOX10[w]) else '',
                         gate_raw=int(RAW0[w]), gate_hys=int(HYS0[w]), turn=int(o['turn'][w]), common=int(COMMON[w])))
pd.DataFrame(rows).to_csv(OUT_CSV, index=False)

# ============================================================================ wnioski
md.append('\n## 5. Wnioski\n')
v = summary['variants']
md.append(f"1. Proxy „AI-hardware long / defensywy short”: średnia {v['proxy_hw_vs_def']['mean']:.2f} pp/tydz., t = {v['proxy_hw_vs_def']['t']:.2f}, "
          f"netto {v['proxy_hw_vs_def']['net_mean']:.2f} pp (t {v['proxy_hw_vs_def']['net_t']:.2f}); σ {v['proxy_hw_vs_def']['sigma']:.1f} pp wobec {bs['sigma_pooled']:.1f} pp losowego koszyka — "
          f"to zakład o {v['proxy_hw_vs_def']['sigma']/bs['sigma_pooled']:.1f}× większej zmienności niż losowy 5/5. Korelacja z SMH−XLP r = {corr_tab['proxy vs (SMH−XLP)']['r']:.2f} "
          f"(R² {corr_tab['proxy vs (SMH−XLP)']['r2']:.2f}), z ^SOX−^NDX r = {corr_tab['proxy vs (^SOX−^NDX)']['r']:.2f}.")
md.append(f"2. Faktyczne koszyki W4–W7: {sum(overlap_rows[k]['long_hw'] for k in ('W4','W5','W6','W7'))}/20 nóg long z listy hardware, "
          f"{sum(overlap_rows[k]['short_def'] for k in ('W4','W5','W6','W7'))}/20 nóg short z listy defensyw. Beta na SMH−XLP koszyków: "
          + ', '.join(f"{k} {etf_rows[k]['beta_etf']:.2f} (R² {etf_rows[k]['r2_etf']:.2f})" for k in ('W4','W5','W6','W7'))
          + f". W6+W7 faktyczne {etf_rows['W6']['spread_actual']+etf_rows['W7']['spread_actual']:.1f} pp, z czego beta czynnikowa {etf_rows['W6']['factor_etf']+etf_rows['W7']['factor_etf']:.1f} pp "
          f"({(etf_rows['W6']['factor_etf']+etf_rows['W7']['factor_etf'])/(etf_rows['W6']['spread_actual']+etf_rows['W7']['spread_actual'])*100:.0f}%).")
rr = regime_rows
BD = 'po dużym spadku ^NDX<−4%'; W7K = '„jak W7": ^NDX<−4% i ^SOX<−8%'
md.append(f"3. Po tygodniach ^NDX<−4% (n={rr[BD]['n']}): ^NDX nast. tydz. {rr[BD]['ndx_next_mean']:.2f}% (hit {rr[BD]['ndx_next_hit']*100:.0f}%), "
          f"^SOX−^NDX {rr[BD]['sox_ndx_next']:.2f} pp, mom6M {rr[BD]['mom_mean']:.2f} pp [t {rr[BD]['mom_t']:.1f}], "
          f"rev1W {rr[BD]['rev_mean']:.2f} pp [t {rr[BD]['rev_t']:.1f}], przegrani-10 {rr[BD]['losers10']:.2f} pp. "
          f"Tygodnie „jak W7” (n={rr[W7K]['n']}): ^NDX {rr[W7K]['ndx_next_mean']:.2f}%, mom6M {rr[W7K]['mom_mean']:.2f} pp, rev1W {rr[W7K]['rev_mean']:.2f} pp.")
g = gated
md.append(f"4. Bramka z histerezą: aktywna (P1 lub P2) w {freq['razem']['p1_hys']+freq['razem']['p2_hys']} z {freq['razem']['n']} tygodni (P2: {freq['razem']['p2_hys']}); śr. gross {freq['razem']['gross_hys']*100:.0f}%. "
          f"Momentum 6M: bez bramki {g['mom6M | bez bramki']['mean']:.2f} pp (t {g['mom6M | bez bramki']['t']:.2f}, Sharpe {g['mom6M | bez bramki']['sharpe']:.2f}, maxDD {g['mom6M | bez bramki']['maxdd']:.0f}) → z bramką {g['mom6M | bramka z histerezą']['mean']:.2f} pp "
          f"(t {g['mom6M | bramka z histerezą']['t']:.2f}, Sharpe {g['mom6M | bramka z histerezą']['sharpe']:.2f}, maxDD {g['mom6M | bramka z histerezą']['maxdd']:.0f}); netto {g['mom6M | bez bramki']['net_mean']:.2f} → {g['mom6M | bramka z histerezą']['net_mean']:.2f} pp. "
          f"Odwrócenie 1T: {g['rev1W | bez bramki']['mean']:.2f} → {g['rev1W | bramka z histerezą']['mean']:.2f} pp.")

open(OUT_MD, 'w').write('\n'.join(md) + '\n')


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


json.dump(clean(summary), open(OUT_JSON, 'w'), ensure_ascii=False, indent=1)
print('\n'.join(md))
