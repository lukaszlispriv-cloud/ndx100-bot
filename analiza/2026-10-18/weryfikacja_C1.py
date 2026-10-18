#!/usr/bin/env python3
"""
weryfikacja_C1.py — próba OBALENIA twierdzenia C1 (momentum 6M relatywne, skip 5 sesji,
TOP5/BOTTOM5 w NDX-100: ~+1,0 pp/tydz. brutto, t≈2,0–2,1; +0,7–0,85 netto, t≈1,5–1,6;
2022–2023 ≈ 0, alfa 2024–2026; survivorship bias; ex ante +0,4…+0,8 netto przy σ 6–7,5).

Harness identyczny z bt_odwrocenie.py / bt_momentum.py:
 - okno tygodniowe D0 = ostatnia sesja tygodnia ISO -> D5 = ostatnia sesja następnego tygodnia
   (test (b): okna kotwiczone na innym dniu tygodnia);
 - sygnał mom6 = P[d0-skip]/P[d0-skip-126] - 1 - (NDX analogicznie), dane <= D0;
 - uniwersum: pełna historia (skip+126) sesji + cena na D0 i D5; min 30 spółek;
 - noga long = r_i - r_NDX, short = -(r_i - r_NDX); spread = śr. long + śr. short (pp, gross 2);
 - koszty: 0,10% x nominał nogi (1/N strony) za każdą zmienioną nazwę + 6%/rok x gross 2 x dni/365.

Testy: (a) usunięcie spółek krótkiej historii / dodanych po 2023 (listy + quasi point-in-time),
       (b) inne dni tygodnia, (c) bootstrap blokowy, (d) podokresy 2022-04…2024-06 i 2024-07…2026-10,
       (e) skip 0/5/21 x nogi 4/5/7, (f) koncentracja alfy w nazwach (leave-k-out), dekompozycja nóg,
       (g) opcjonalnie: uniwersum rozszerzone o spółki USUNIĘTE z NDX-100 (plik dane/dropped_closes.csv).
Wyjście: weryfikacja_C1_out.md (tabele), weryfikacja_C1_wyniki.json, weryfikacja_C1_serie.csv.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
DROPPED = f'{BASE}/dane/dropped_closes.csv'
OUT_MD = f'{BASE}/analiza/weryfikacja_C1_out.md'
OUT_JSON = f'{BASE}/analiza/weryfikacja_C1_wyniki.json'
OUT_SERIE = f'{BASE}/analiza/weryfikacja_C1_serie.csv'

NON_CAND = ['^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV']
COST_LEG = 0.0010
FIN_RATE = 0.06
LOOK = 126
SEED = 20261018

# ---------------------------------------------------------------------------- dane
raw = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
raw = raw[raw['^NDX'].notna()]
raw = raw.ffill(limit=3)
dropped_df = None
if os.path.exists(DROPPED):
    dropped_df = pd.read_csv(DROPPED, parse_dates=['date']).set_index('date').sort_index()
    dropped_df = dropped_df.reindex(raw.index).ffill(limit=3)

dates = raw.index
NDX = raw['^NDX'].to_numpy(float)
VIX = raw['^VIX'].to_numpy(float)
cands_all = [c for c in raw.columns if c not in NON_CAND]
first_valid = {c: raw[c].first_valid_index() for c in cands_all}

# listy wykluczeń (test a)
SHORT_HIST = sorted(c for c in cands_all if first_valid[c] > dates[0])          # dane: pierwsza cena > 2021-10-18
HINT_LIST = ['ALAB', 'ARM', 'CRWV', 'FER', 'GEHC', 'HONA', 'NBIS', 'SNDK', 'SPCX', 'MRNA', 'PLTR',
             'MSTR', 'AXON', 'SHOP', 'APP', 'DASH', 'TTWO', 'WDAY']
# szerzej: + inne nazwy dodane (wg wiedzy recenzenta, przybliżone) po 2023: rekonstytucje XII 2023,
# 2024 (LIN, APP, PLTR, MSTR, AXON, ARM), 2025 (SHOP, rekonstytucja XII 2025), 2026 (spin-offy)
BROAD_EXTRA = ['CCEP', 'ROP', 'LIN', 'ALNY', 'MPWR', 'RKLB', 'STX', 'WDC', 'LITE', 'TRI', 'WMT', 'CEG', 'WBD']
BROAD_LIST = sorted(set(HINT_LIST) | set(BROAD_EXTRA))
# quasi point-in-time: przybliżona data dołączenia do NDX-100 (przed nią spółka poza uniwersum)
JOIN_APPROX = {
    'CEG': '2022-02-02', 'GEHC': '2023-01-04', 'CCEP': '2023-12-18', 'DASH': '2023-12-18', 'ROP': '2023-12-18',
    'TTWO': '2023-12-18', 'LIN': '2024-07-15', 'ARM': '2024-07-01', 'APP': '2024-11-18', 'PLTR': '2024-12-23',
    'MSTR': '2024-12-23', 'AXON': '2024-12-23', 'SHOP': '2025-05-19', 'ALNY': '2025-12-22', 'CRWV': '2025-12-22',
    'FER': '2025-12-22', 'MPWR': '2025-12-22', 'RKLB': '2025-12-22', 'SNDK': '2025-12-22', 'STX': '2025-12-22',
    'WDC': '2025-12-22', 'LITE': '2025-12-22', 'TRI': '2025-12-22', 'WMT': '2025-12-22', 'NBIS': '2025-12-22',
    'ALAB': '2025-12-22', 'HONA': '2026-06-15', 'SPCX': '2026-06-12', 'WBD': '2026-10-05', 'WDAY': '2022-12-19',
    'MRNA': '2020-07-20',
}


# przybliżone daty USUNIĘCIA z NDX-100 (wg wiedzy recenzenta; przybliżone) i dołączenia spółek usuniętych
LEAVE_APPROX = {
    'BIDU': '2022-12-19', 'DOCU': '2022-12-19', 'MTCH': '2022-12-19', 'NTES': '2022-12-19', 'SWKS': '2022-12-19',
    'VRSN': '2022-12-19', 'OKTA': '2022-12-19',
    'ALGN': '2023-12-18', 'EBAY': '2023-12-18', 'ENPH': '2023-12-18', 'JD': '2023-12-18', 'LCID': '2023-12-18', 'ZM': '2023-12-18',
    'DLTR': '2024-11-18', 'ILMN': '2024-12-23', 'SMCI': '2024-12-23', 'MDB': '2025-05-19',
    'SIRI': '2025-12-22', 'BIIB': '2025-12-22', 'CDW': '2025-12-22', 'CSGP': '2025-12-22', 'GFS': '2025-12-22',
    'LULU': '2025-12-22', 'ON': '2025-12-22', 'TTD': '2025-12-22', 'TEAM': '2025-12-22', 'CHTR': '2025-12-22', 'VRSK': '2025-12-22',
}
JOIN_DROPPED = {'SMCI': '2024-07-22', 'MDB': '2023-12-18', 'CDW': '2023-12-18', 'GFS': '2022-12-19', 'ON': '2022-12-19'}


def build(cands, extra=None):
    """Macierz cen dla listy kandydatów (+ opcjonalnie DataFrame spółek usuniętych)."""
    P = raw[cands].to_numpy(float)
    names = list(cands)
    if extra is not None:
        P = np.hstack([P, extra.to_numpy(float)])
        names += list(extra.columns)
    return P, names


# ---------------------------------------------------------------------------- okna
def windows_anchor(weekday=None):
    """Okna tygodniowe. weekday=None -> ostatnia sesja tygodnia ISO (jak harness).
    weekday=k (0=Pn..4=Pt) -> ostatnia sesja tygodnia o dniu <= k (gdy w tygodniu brak sesji <= k, pomijamy tydzień)."""
    iso = dates.isocalendar()
    keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
    last = {}
    for i, k in enumerate(keys):
        if weekday is None or dates[i].weekday() <= weekday:
            last[k] = i
    wk = sorted(last)
    idx = [last[w] for w in wk]
    D0 = np.array(idx[:-1]); D5 = np.array(idx[1:])
    return D0, D5


def backtest(P, names, D0, D5, skip=5, nleg=5, join=None, mask_names=None, min_univ=30, leave=None):
    """Zwraca dict serii (spread, long, short, net, turnover) + listy nóg.
    join: dict nazwa->Timestamp (quasi point-in-time: wyklucz nazwę przed datą)."""
    nW = len(D0); nS = P.shape[1]
    WR = P[D5] / P[D0] - 1
    WN = NDX[D5] / NDX[D0] - 1
    EX = WR - WN[:, None]
    DAYS = np.array([(dates[b] - dates[a]).days for a, b in zip(D0, D5)])
    sp = np.full(nW, np.nan); lg = np.full(nW, np.nan); sh = np.full(nW, np.nan)
    turn = np.zeros(nW); univ = np.zeros(nW)
    longs, shorts = [None] * nW, [None] * nW
    prevL = prevS = None
    hist_need = skip + LOOK
    jarr = None
    if join:
        jarr = np.array([pd.Timestamp(join[n]) if n in join else pd.Timestamp('1900-01-01') for n in names])
    larr = None
    if leave:
        larr = np.array([pd.Timestamp(leave[n]) if n in leave else pd.Timestamp('2100-01-01') for n in names])
    for w, d0 in enumerate(D0):
        if d0 - hist_need < 0:
            continue
        seg = P[d0 - hist_need:d0 + 1]
        ok = ~np.isnan(seg).any(axis=0) & ~np.isnan(WR[w])
        if mask_names is not None:
            ok &= mask_names
        if jarr is not None:
            ok &= jarr <= dates[d0]
        if larr is not None:
            ok &= larr > dates[d0]
        a, b = d0 - hist_need, d0 - skip
        s = P[b] / P[a] - 1 - (NDX[b] / NDX[a] - 1)
        s[~ok] = np.nan
        idx = np.where(ok)[0]
        univ[w] = len(idx)
        if len(idx) < min_univ:
            prevL = prevS = None
            continue
        order = idx[np.argsort(-s[idx], kind='stable')]
        L, S = order[:nleg], order[-nleg:]
        longs[w], shorts[w] = L, S
        el = EX[w, L]; es = -EX[w, S]
        lg[w] = el.mean() * 100; sh[w] = es.mean() * 100; sp[w] = lg[w] + sh[w]
        if prevL is None:
            turn[w] = 2 * nleg
        else:
            turn[w] = len(set(L) - set(prevL)) + len(set(S) - set(prevS))
        prevL, prevS = L, S
    rot = turn * COST_LEG * (1.0 / nleg) * 100
    fin = FIN_RATE * 2.0 * DAYS / 365 * 100
    net = sp - rot - fin
    return dict(spread=sp, long=lg, short=sh, net=net, turn=turn, univ=univ, longs=longs, shorts=shorts,
                D0=D0, D5=D5, WN=WN, EX=EX, names=names)


def metrics(x, mask=None):
    m = ~np.isnan(x)
    if mask is not None:
        m &= mask
    v = x[m]; n = len(v)
    if n < 3:
        return dict(n=n, mean=np.nan, sigma=np.nan, t=np.nan, hit=np.nan, sharpe=np.nan, maxdd=np.nan, worst=np.nan)
    mu, sd = v.mean(), v.std(ddof=1)
    cum = np.cumsum(v); dd = (np.maximum.accumulate(cum) - cum).max()
    return dict(n=n, mean=mu, sigma=sd, t=mu / sd * math.sqrt(n), hit=(v > 0).mean(), sharpe=mu / sd * math.sqrt(52),
                maxdd=dd, worst=v.min())


def f(v, d=2):
    return '—' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.{d}f}'


def row(label, r, mask=None):
    mg = metrics(r['spread'], mask); mn = metrics(r['net'], mask)
    ml = metrics(r['long'], mask); ms = metrics(r['short'], mask)
    return (f"| {label} | {mg['n']} | {f(mg['mean'])} | {f(mg['sigma'])} | {f(mg['t'])} | {f(mg['hit']*100,0)}% | "
            f"{f(mn['mean'])} | {f(mn['t'])} | {f(ml['mean'])} | {f(ms['mean'])} | {f(mg['maxdd'],1)} | {f(mg['worst'],1)} |"), mg, mn, ml, ms


HDR = ('| wariant | n | brutto pp | σ | t | hit | netto pp | t netto | noga L | noga S | maxDD | najgorsze |\n'
       '|---|---|---|---|---|---|---|---|---|---|---|---|')


def year_of(D0):
    return np.array([dates[i].year for i in D0])


def period_mask(D0, a, b):
    d = dates[D0]
    return (d >= pd.Timestamp(a)) & (d <= pd.Timestamp(b))


# ---------------------------------------------------------------------------- bootstrap
def block_bootstrap(x, B=10000, block=6, seed=SEED):
    """Stacjonarny bootstrap blokowy (Politis-Romano, średnia długość bloku = block) średniej i t.
    Zwraca: CI 95% średniej, p(średnia<=0) z rozkładu bootstrapu wyśrodkowanego (H0: mu=0), rozkład t."""
    x = x[~np.isnan(x)]; n = len(x)
    rng = np.random.default_rng(seed)
    p = 1.0 / block
    means = np.empty(B); ts = np.empty(B)
    for b_ in range(B):
        idx = np.empty(n, dtype=int)
        i = rng.integers(n)
        for k in range(n):
            if k > 0 and rng.random() >= p:
                i = (i + 1) % n
            else:
                i = rng.integers(n)
            idx[k] = i
        v = x[idx]
        means[b_] = v.mean(); ts[b_] = v.mean() / v.std(ddof=1) * math.sqrt(n)
    mu = x.mean()
    ci = np.percentile(means, [2.5, 97.5])
    # H0: mu=0 — wyśrodkuj
    centered = means - mu
    p_one = (centered >= mu).mean()         # P(bootstrap mean - mu >= mu) = p jednostronne
    return dict(ci_lo=ci[0], ci_hi=ci[1], p_one_sided=p_one, t_ci=np.percentile(ts, [2.5, 97.5]).tolist(),
                se=means.std(ddof=1))


# ---------------------------------------------------------------------------- bieg
results = {}
md = []
md.append('# Weryfikacja C1 — wyniki skryptu weryfikacja_C1.py\n')
md.append(f'Dane: `{CSV}` — {len(dates)} sesji {dates[0].date()}…{dates[-1].date()}, {len(cands_all)} kandydatów (skład dzisiejszy).\n')

D0f, D5f = windows_anchor(None)
P_all, names_all = build(cands_all)

# 0. baseline (reprodukcja twierdzenia)
base = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5)
r0, mg0, mn0, ml0, ms0 = row('BAZA: 6M skip5, 5/5, piątek→piątek, pełne uniwersum', base)
md.append('\n## 0. Reprodukcja twierdzenia (harness jak w fazie 2)\n'); md.append(HDR); md.append(r0)
results['baza'] = dict(brutto=mg0, netto=mn0, long=ml0, short=ms0, mean_univ=float(np.nanmean(base['univ'][base['univ'] > 0])),
                       turn=float(np.nanmean(base['turn'][~np.isnan(base['spread'])])))
md.append(f"\nŚrednie uniwersum {results['baza']['mean_univ']:.1f} spółek; obrót {results['baza']['turn']:.2f} nóg/tydz. "
          f"(koszt rotacji {np.nanmean((base['turn']*COST_LEG/5*100)[~np.isnan(base['spread'])]):.3f} pp + finansowanie "
          f"{np.nanmean((base['spread']-base['net']-base['turn']*COST_LEG/5*100)[~np.isnan(base['spread'])]):.3f} pp).\n")
YR = year_of(D0f)
md.append('\nLata (brutto / netto, t):\n'); md.append('| rok | n | brutto | t | netto | t netto |\n|---|---|---|---|---|---|')
results['baza_lata'] = {}
for y in sorted(set(YR)):
    mg = metrics(base['spread'], YR == y); mn = metrics(base['net'], YR == y)
    if mg['n'] >= 3:
        md.append(f"| {y} | {mg['n']} | {f(mg['mean'])} | {f(mg['t'])} | {f(mn['mean'])} | {f(mn['t'])} |")
        results['baza_lata'][int(y)] = dict(n=mg['n'], mean=mg['mean'], t=mg['t'], net=mn['mean'])

# ---------------------------------------------------------------------------- (a) wykluczenia
md.append('\n## (a) Usunięcie spółek krótkiej historii / dodanych po 2023\n')
md.append(f"Lista krótka historia (pierwsza cena w danych > {dates[0].date()}): {' '.join(SHORT_HIST)}\n")
md.append(f"Lista z podpowiedzi (18): {' '.join(HINT_LIST)}\n")
md.append(f"Lista szeroka (podpowiedź + przybliżone dodania 2022–2026): {' '.join(BROAD_LIST)}\n")
md.append(HDR); md.append(r0)
results['a'] = {}
name_idx = {n: i for i, n in enumerate(names_all)}
for lbl, lst in [('bez krótkiej historii (dane)', SHORT_HIST), ('bez listy z podpowiedzi (18)', HINT_LIST),
                 ('bez listy szerokiej (%d)' % len(BROAD_LIST), BROAD_LIST),
                 ('bez podpowiedzi + krótkiej historii', sorted(set(HINT_LIST) | set(SHORT_HIST)))]:
    mask = np.array([n not in lst for n in names_all])
    r = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, mask_names=mask)
    line, mg, mn, ml, ms = row(lbl, r)
    md.append(line)
    results['a'][lbl] = dict(brutto=mg, netto=mn, long=ml, short=ms, excluded=len(lst), mean_univ=float(np.nanmean(r['univ'][r['univ'] > 0])))
    # lata
    yrs = {}
    for y in sorted(set(YR)):
        m_ = metrics(r['spread'], YR == y)
        if m_['n'] >= 3:
            yrs[int(y)] = round(m_['mean'], 2)
    results['a'][lbl]['lata'] = yrs
# quasi point-in-time
r_pit = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, join=JOIN_APPROX)
line, mg, mn, ml, ms = row('quasi point-in-time (przybliżone daty dołączenia)', r_pit)
md.append(line)
results['a']['quasi_pit'] = dict(brutto=mg, netto=mn, long=ml, short=ms)
md.append('\nLata (brutto) dla wariantów (a):\n')
md.append('| wariant | ' + ' | '.join(str(y) for y in sorted(set(YR)) if (YR == y).sum() >= 3) + ' |\n|---|' + '---|' * len([y for y in sorted(set(YR)) if (YR == y).sum() >= 3]))
for lbl, d in results['a'].items():
    if 'lata' in d:
        md.append(f"| {lbl} | " + ' | '.join(f"{d['lata'].get(y, float('nan')):.2f}" for y in sorted(set(YR)) if (YR == y).sum() >= 3) + ' |')
yrs_pit = {int(y): metrics(r_pit['spread'], YR == y)['mean'] for y in sorted(set(YR)) if (YR == y).sum() >= 3}
md.append('| quasi point-in-time | ' + ' | '.join(f"{yrs_pit[y]:.2f}" for y in yrs_pit) + ' |')
results['a']['quasi_pit']['lata'] = {k: round(v, 2) for k, v in yrs_pit.items()}

# (a2) koncentracja: wkład nazw do P&L (noga long i short osobno) i leave-k-out
md.append('\n### (a2) Koncentracja alfy w nazwach (baza)\n')
contrib = {}
for w in range(len(D0f)):
    if base['longs'][w] is None:
        continue
    for i in base['longs'][w]:
        contrib.setdefault(names_all[i], [0.0, 0])
        contrib[names_all[i]][0] += base['EX'][w, i] * 100 / 5; contrib[names_all[i]][1] += 1
    for i in base['shorts'][w]:
        contrib.setdefault(names_all[i], [0.0, 0])
        contrib[names_all[i]][0] += -base['EX'][w, i] * 100 / 5; contrib[names_all[i]][1] += 1
total = np.nansum(base['spread'])
cs = sorted(contrib.items(), key=lambda kv: -kv[1][0])
md.append(f"Suma spreadu brutto = {total:.1f} pp na {mg0['n']} okien. Najwięksi dawcy (pp skumulowane, liczba okien w koszyku):\n")
md.append('| nazwa | wkład pp | okien | | nazwa | wkład pp | okien |\n|---|---|---|---|---|---|---|')
for k in range(10):
    a_ = cs[k]; b_ = cs[-(k + 1)]
    md.append(f"| {a_[0]} | {a_[1][0]:.1f} | {a_[1][1]} | | {b_[0]} | {b_[1][0]:.1f} | {b_[1][1]} |")
results['a2_top'] = [(k, round(v[0], 1), v[1]) for k, v in cs[:12]]
results['a2_bottom'] = [(k, round(v[0], 1), v[1]) for k, v in cs[-8:]]
md.append('\nLeave-k-out: usuń k największych dawców z uniwersum i policz ponownie (test kruchości):\n')
md.append(HDR)
results['a2_leave'] = {}
for k in (1, 3, 5, 10):
    drop = [kv[0] for kv in cs[:k]]
    mask = np.array([n not in drop for n in names_all])
    r = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, mask_names=mask)
    line, mg, mn, _, _ = row(f'bez {k} największych dawców ({" ".join(drop)})', r)
    md.append(line)
    results['a2_leave'][k] = dict(brutto=mg, netto=mn, drop=drop)
# kontrola: usuń k LOSOWYCH nazw (rozkład) — czy spadek po usunięciu top-k jest większy niż losowy?
rng = np.random.default_rng(SEED)
md.append('\nKontrola: usunięcie 5 LOSOWYCH nazw (200 powtórzeń) — rozkład średniej brutto:\n')
rand_means = []
for _ in range(200):
    drop = rng.choice(names_all, 5, replace=False)
    mask = np.array([n not in set(drop) for n in names_all])
    r = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, mask_names=mask)
    rand_means.append(np.nanmean(r['spread']))
rand_means = np.array(rand_means)
md.append(f"średnia {rand_means.mean():.2f}, 5–95% {np.percentile(rand_means,5):.2f}…{np.percentile(rand_means,95):.2f}, min {rand_means.min():.2f}\n")
results['a2_random5'] = dict(mean=float(rand_means.mean()), p5=float(np.percentile(rand_means, 5)), p95=float(np.percentile(rand_means, 95)), min=float(rand_means.min()))

# ---------------------------------------------------------------------------- (b) inne dni tygodnia
md.append('\n## (b) Okna kotwiczone na innym dniu tygodnia (sygnał i wejście tego samego dnia)\n')
md.append(HDR)
results['b'] = {}
for wd, lbl in [(0, 'poniedziałek'), (1, 'wtorek'), (2, 'środa'), (3, 'czwartek'), (4, 'piątek (ostatnia sesja ≤ pt)'), (None, 'ostatnia sesja tygodnia (baza)')]:
    D0, D5 = windows_anchor(wd)
    r = backtest(P_all, names_all, D0, D5, skip=5, nleg=5)
    line, mg, mn, ml, ms = row(lbl, r)
    md.append(line)
    results['b'][lbl] = dict(brutto=mg, netto=mn)
    r['label'] = lbl
    if wd is not None:
        yr = year_of(D0)
        results['b'][lbl]['podokresy'] = dict(
            p1=metrics(r['spread'], period_mask(D0, '2022-04-01', '2024-06-30'))['mean'],
            p2=metrics(r['spread'], period_mask(D0, '2024-07-01', '2026-10-31'))['mean'])
vals = [results['b'][k]['brutto']['mean'] for k in results['b'] if 'baza' not in k]
nets = [results['b'][k]['netto']['mean'] for k in results['b'] if 'baza' not in k]
ts = [results['b'][k]['brutto']['t'] for k in results['b'] if 'baza' not in k]
md.append(f"\nŚrednia po 5 kotwicach: brutto {np.mean(vals):.2f} pp (min {np.min(vals):.2f}, max {np.max(vals):.2f}), "
          f"netto {np.mean(nets):.2f} pp (min {np.min(nets):.2f}), t brutto min {np.min(ts):.2f} max {np.max(ts):.2f}.\n")
results['b_summary'] = dict(mean_gross=float(np.mean(vals)), min_gross=float(np.min(vals)), max_gross=float(np.max(vals)),
                            mean_net=float(np.mean(nets)), min_net=float(np.min(nets)), t_min=float(np.min(ts)), t_max=float(np.max(ts)))

# ---------------------------------------------------------------------------- (c) bootstrap blokowy
md.append('\n## (c) Bootstrap blokowy (stacjonarny, 10 000 prób) — baza, brutto i netto\n')
md.append('| seria | średnia | 95% CI średniej | SE boot | p jednostr. (H0: μ≤0) | 95% CI t |\n|---|---|---|---|---|---|')
results['c'] = {}
for lbl, x in [('brutto', base['spread']), ('netto', base['net'])]:
    for bl in (4, 8):
        bb = block_bootstrap(x, B=10000, block=bl)
        md.append(f"| {lbl}, blok ~{bl} tyg. | {np.nanmean(x):.2f} | {bb['ci_lo']:.2f} … {bb['ci_hi']:.2f} | {bb['se']:.2f} | {bb['p_one_sided']:.3f} | {bb['t_ci'][0]:.2f} … {bb['t_ci'][1]:.2f} |")
        results['c'][f'{lbl}_blok{bl}'] = bb
# bootstrap dla wariantu bez listy z podpowiedzi
mask = np.array([n not in HINT_LIST for n in names_all])
r_h = backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, mask_names=mask)
for lbl, x in [('brutto bez listy 18', r_h['spread']), ('netto bez listy 18', r_h['net'])]:
    bb = block_bootstrap(x, B=10000, block=6)
    md.append(f"| {lbl}, blok ~6 | {np.nanmean(x):.2f} | {bb['ci_lo']:.2f} … {bb['ci_hi']:.2f} | {bb['se']:.2f} | {bb['p_one_sided']:.3f} | {bb['t_ci'][0]:.2f} … {bb['t_ci'][1]:.2f} |")
    results['c'][lbl] = bb

# ---------------------------------------------------------------------------- (d) podokresy
md.append('\n## (d) Podokresy 2022-04…2024-06 i 2024-07…2026-10 (baza i warianty (a))\n')
md.append('| wariant | okres | n | brutto | σ | t | netto | t netto | noga L | noga S |\n|---|---|---|---|---|---|---|---|---|---|')
results['d'] = {}
variants_d = [('baza', base), ('bez listy 18', r_h), ('quasi point-in-time', r_pit)]
mask_b = np.array([n not in BROAD_LIST for n in names_all])
variants_d.append(('bez listy szerokiej', backtest(P_all, names_all, D0f, D5f, skip=5, nleg=5, mask_names=mask_b)))
for vl, r in variants_d:
    results['d'][vl] = {}
    for pl, a, b in [('2022-04…2024-06', '2022-04-01', '2024-06-30'), ('2024-07…2026-10', '2024-07-01', '2026-10-31'),
                     ('2022-04…2023-12', '2022-04-01', '2023-12-31'), ('2024-01…2026-10', '2024-01-01', '2026-10-31')]:
        m = period_mask(r['D0'], a, b)
        mg = metrics(r['spread'], m); mn = metrics(r['net'], m); ml = metrics(r['long'], m); ms = metrics(r['short'], m)
        md.append(f"| {vl} | {pl} | {mg['n']} | {f(mg['mean'])} | {f(mg['sigma'])} | {f(mg['t'])} | {f(mn['mean'])} | {f(mn['t'])} | {f(ml['mean'])} | {f(ms['mean'])} |")
        results['d'][vl][pl] = dict(brutto=mg, netto=mn, long=ml['mean'], short=ms['mean'])
# test różnicy średnich między podokresami (Welch)
m1 = period_mask(D0f, '2022-04-01', '2024-06-30'); m2 = period_mask(D0f, '2024-07-01', '2026-10-31')
x1 = base['spread'][m1 & ~np.isnan(base['spread'])]; x2 = base['spread'][m2 & ~np.isnan(base['spread'])]
tw = (x2.mean() - x1.mean()) / math.sqrt(x1.var(ddof=1) / len(x1) + x2.var(ddof=1) / len(x2))
md.append(f"\nWelch t różnicy (2. okres − 1. okres) dla bazy: {tw:.2f} (różnica {x2.mean()-x1.mean():.2f} pp/tydz.).\n")
results['d_welch'] = dict(t=tw, diff=float(x2.mean() - x1.mean()))

# ---------------------------------------------------------------------------- (e) skip x nogi
md.append('\n## (e) Wrażliwość: skip 0/5/21 sesji × 4/4, 5/5, 7/7 nóg (piątek→piątek, pełne uniwersum)\n')
md.append('| skip | nogi | n | brutto | σ | t | netto | t netto | 2022-04…2024-06 | 2024-07…2026-10 | bez listy 18: brutto / t / netto |\n|---|---|---|---|---|---|---|---|---|---|---|')
results['e'] = {}
for skip in (0, 5, 21):
    for nl in (4, 5, 7):
        r = backtest(P_all, names_all, D0f, D5f, skip=skip, nleg=nl)
        rh = backtest(P_all, names_all, D0f, D5f, skip=skip, nleg=nl, mask_names=mask)
        mg = metrics(r['spread']); mn = metrics(r['net'])
        p1 = metrics(r['spread'], period_mask(D0f, '2022-04-01', '2024-06-30'))['mean']
        p2 = metrics(r['spread'], period_mask(D0f, '2024-07-01', '2026-10-31'))['mean']
        mgh = metrics(rh['spread']); mnh = metrics(rh['net'])
        md.append(f"| {skip} | {nl}/{nl} | {mg['n']} | {f(mg['mean'])} | {f(mg['sigma'])} | {f(mg['t'])} | {f(mn['mean'])} | {f(mn['t'])} | {f(p1)} | {f(p2)} | {f(mgh['mean'])} / {f(mgh['t'])} / {f(mnh['mean'])} |")
        results['e'][f'skip{skip}_n{nl}'] = dict(brutto=mg, netto=mn, p1=p1, p2=p2, bez18=dict(brutto=mgh, netto=mnh))
grid_t = [v['brutto']['t'] for v in results['e'].values()]
grid_net = [v['netto']['mean'] for v in results['e'].values()]
grid_t18 = [v['bez18']['brutto']['t'] for v in results['e'].values()]
md.append(f"\nSiatka 9 wariantów: t brutto {np.min(grid_t):.2f}…{np.max(grid_t):.2f} (mediana {np.median(grid_t):.2f}), "
          f"netto {np.min(grid_net):.2f}…{np.max(grid_net):.2f} pp; bez listy 18: t brutto {np.min(grid_t18):.2f}…{np.max(grid_t18):.2f}.\n")
results['e_summary'] = dict(t_min=float(np.min(grid_t)), t_max=float(np.max(grid_t)), t_med=float(np.median(grid_t)),
                            net_min=float(np.min(grid_net)), net_max=float(np.max(grid_net)),
                            t18_min=float(np.min(grid_t18)), t18_max=float(np.max(grid_t18)))

# ---------------------------------------------------------------------------- (f) reżim VIX i ekspozycja rynkowa
md.append('\n## (f) Dodatkowo: beta spreadu do ^NDX i warunkowo VIX (baza)\n')
m = ~np.isnan(base['spread'])
x = base['WN'][m] * 100; y = base['spread'][m]
b = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); a = y.mean() - b * x.mean(); rr = np.corrcoef(x, y)[0, 1]
md.append(f"Regresja spread ~ ^NDX tyg.: alfa {a:.2f} pp, beta {b:.2f}, r {rr:.2f} (n={m.sum()}).\n")
results['f_beta'] = dict(alfa=a, beta=b, r=rr)
vix0 = VIX[D0f]
for lbl, mk in [('VIX>20', vix0 > 20), ('VIX≤20', vix0 <= 20)]:
    mg = metrics(base['spread'], mk); mn = metrics(base['net'], mk)
    md.append(f"- {lbl}: n={mg['n']}, brutto {f(mg['mean'])} (t {f(mg['t'])}), netto {f(mn['mean'])}.")
    results[f'f_{lbl}'] = dict(brutto=mg, netto=mn)

# ---------------------------------------------------------------------------- (g) uniwersum + spółki usunięte z indeksu
if dropped_df is not None and dropped_df.shape[1] > 0:
    md.append('\n## (g) Uniwersum rozszerzone o spółki USUNIĘTE z NDX-100 (częściowa korekta survivorship)\n')
    md.append(f"Dodane kolumny ({dropped_df.shape[1]}): {' '.join(dropped_df.columns)}\n")
    P_ext, names_ext = build(cands_all, dropped_df)
    r_ext = backtest(P_ext, names_ext, D0f, D5f, skip=5, nleg=5)
    md.append(HDR); md.append(r0)
    line, mg, mn, ml, ms = row('pełne + usunięte', r_ext); md.append(line)
    results['g'] = {'pelne_plus_usuniete': dict(brutto=mg, netto=mn, long=ml, short=ms)}
    # usunięte + bez listy 18
    mask_ext = np.array([n not in HINT_LIST for n in names_ext])
    r_ext2 = backtest(P_ext, names_ext, D0f, D5f, skip=5, nleg=5, mask_names=mask_ext)
    line, mg, mn, ml, ms = row('pełne + usunięte, bez listy 18', r_ext2); md.append(line)
    results['g']['plus_usuniete_bez18'] = dict(brutto=mg, netto=mn, long=ml, short=ms)
    join_all = dict(JOIN_APPROX); join_all.update(JOIN_DROPPED)
    r_pit2 = backtest(P_ext, names_ext, D0f, D5f, skip=5, nleg=5, join=join_all, leave=LEAVE_APPROX)
    line, mg, mn, ml, ms = row('point-in-time: dołączenia + usunięcia (przybliżone daty)', r_pit2); md.append(line)
    results['g']['pit_pelny'] = dict(brutto=mg, netto=mn, long=ml, short=ms, mean_univ=float(np.nanmean(r_pit2['univ'][r_pit2['univ'] > 0])))
    for pl, a_, b_ in [('2022-04…2024-06', '2022-04-01', '2024-06-30'), ('2024-07…2026-10', '2024-07-01', '2026-10-31')]:
        mm = period_mask(D0f, a_, b_)
        mg_ = metrics(r_pit2['spread'], mm); mn_ = metrics(r_pit2['net'], mm)
        md.append(f"- point-in-time pełny, {pl}: n={mg_['n']}, brutto {f(mg_['mean'])} (t {f(mg_['t'])}), netto {f(mn_['mean'])}, noga L {f(metrics(r_pit2['long'], mm)['mean'])}, noga S {f(metrics(r_pit2['short'], mm)['mean'])}")
        results['g'][f'pit_pelny_{pl}'] = dict(brutto=mg_, netto=mn_)
    bbp = block_bootstrap(r_pit2['spread'], B=10000, block=6); bbn = block_bootstrap(r_pit2['net'], B=10000, block=6)
    md.append(f"- bootstrap blokowy PIT pełny: brutto 95% CI {bbp['ci_lo']:.2f}…{bbp['ci_hi']:.2f} (p {bbp['p_one_sided']:.3f}); netto CI {bbn['ci_lo']:.2f}…{bbn['ci_hi']:.2f} (p {bbn['p_one_sided']:.3f})")
    results['g']['pit_boot'] = dict(brutto=bbp, netto=bbn)
    # siatka skip x nogi na PIT pełnym
    md.append('\nSiatka skip × nogi na uniwersum point-in-time (brutto / t / netto):\n')
    md.append('| skip | 4/4 | 5/5 | 7/7 |\n|---|---|---|---|')
    results['g']['pit_grid'] = {}
    for skip in (0, 5, 21):
        cells = []
        for nl in (4, 5, 7):
            rr_ = backtest(P_ext, names_ext, D0f, D5f, skip=skip, nleg=nl, join=join_all, leave=LEAVE_APPROX)
            mg_ = metrics(rr_['spread']); mn_ = metrics(rr_['net'])
            cells.append(f"{f(mg_['mean'])} / {f(mg_['t'])} / {f(mn_['mean'])}")
            results['g']['pit_grid'][f'skip{skip}_n{nl}'] = dict(brutto=mg_, netto=mn_)
        md.append(f"| {skip} | " + ' | '.join(cells) + ' |')
    # koncentracja w PIT: ile nóg to spółki usunięte, lata
    md.append('\nLata (brutto) PIT pełny: ' + ', '.join(f"{y}: {metrics(r_pit2['spread'], YR == y)['mean']:.2f}" for y in sorted(set(YR)) if (YR == y).sum() >= 3))
    results['g']['pit_lata'] = {int(y): metrics(r_pit2['spread'], YR == y)['mean'] for y in sorted(set(YR)) if (YR == y).sum() >= 3}
    cl2 = sum(1 for w in range(len(D0f)) if r_pit2['longs'][w] is not None for i in r_pit2['longs'][w] if names_ext[i] in dropped_df.columns)
    cs2 = sum(1 for w in range(len(D0f)) if r_pit2['shorts'][w] is not None for i in r_pit2['shorts'][w] if names_ext[i] in dropped_df.columns)
    md.append(f"PIT pełny: nogi long ze spółek usuniętych {cl2}, short {cs2}; średnie uniwersum {results['g']['pit_pelny']['mean_univ']:.1f}.")
    results['g']['pit_legs_dropped'] = dict(long=cl2, short=cs2)
    # quasi-PIT: usunięte wchodzą do uniwersum tylko do (przybliżonej) daty usunięcia -> join/leave
    md.append('\nLata (brutto):\n')
    md.append('| wariant | ' + ' | '.join(str(y) for y in sorted(set(YR)) if (YR == y).sum() >= 3) + ' |\n|---|' + '---|' * len([y for y in sorted(set(YR)) if (YR == y).sum() >= 3]))
    for vl, r in [('baza', base), ('pełne + usunięte', r_ext), ('pełne + usunięte, bez listy 18', r_ext2)]:
        md.append(f"| {vl} | " + ' | '.join(f"{metrics(r['spread'], YR == y)['mean']:.2f}" for y in sorted(set(YR)) if (YR == y).sum() >= 3) + ' |')
    for pl, a_, b_ in [('2022-04…2024-06', '2022-04-01', '2024-06-30'), ('2024-07…2026-10', '2024-07-01', '2026-10-31')]:
        mm = period_mask(D0f, a_, b_)
        mg = metrics(r_ext['spread'], mm); mn = metrics(r_ext['net'], mm)
        md.append(f"- pełne + usunięte, {pl}: n={mg['n']}, brutto {f(mg['mean'])} (t {f(mg['t'])}), netto {f(mn['mean'])}")
        results['g'][f'pelne_plus_usuniete_{pl}'] = dict(brutto=mg, netto=mn)
    # ile razy usunięte nazwy trafiają do koszyków
    cnt_l = sum(1 for w in range(len(D0f)) if r_ext['longs'][w] is not None for i in r_ext['longs'][w] if names_ext[i] in dropped_df.columns)
    cnt_s = sum(1 for w in range(len(D0f)) if r_ext['shorts'][w] is not None for i in r_ext['shorts'][w] if names_ext[i] in dropped_df.columns)
    md.append(f"\nSpółki usunięte w koszykach: {cnt_l} nóg long, {cnt_s} nóg short (z {5*metrics(r_ext['spread'])['n']} nóg na stronę).\n")
    results['g']['legs_dropped'] = dict(long=cnt_l, short=cnt_s)

# ---------------------------------------------------------------------------- serie
rows = []
for w in range(len(D0f)):
    if np.isnan(base['spread'][w]):
        continue
    rows.append(dict(d0=str(dates[D0f[w]].date()), d5=str(dates[D5f[w]].date()), spread=round(base['spread'][w], 3),
                     net=round(base['net'][w], 3), long=round(base['long'][w], 3), short=round(base['short'][w], 3),
                     spread_bez18=round(r_h['spread'][w], 3) if not np.isnan(r_h['spread'][w]) else '',
                     spread_pit=round(r_pit['spread'][w], 3) if not np.isnan(r_pit['spread'][w]) else '',
                     long_tk=' '.join(names_all[i] for i in base['longs'][w]), short_tk=' '.join(names_all[i] for i in base['shorts'][w])))
pd.DataFrame(rows).to_csv(OUT_SERIE, index=False)


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o


json.dump(clean(results), open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)
open(OUT_MD, 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))
