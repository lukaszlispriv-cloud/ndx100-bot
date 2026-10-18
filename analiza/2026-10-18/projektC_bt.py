#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projektC_bt.py — Projekt C (konstrukcja koszyka i horyzont).

Pytania liczbowe:
  1. Konstrukcje 5L/5S tygodniowe: A (TOP5/BOTTOM5 mom6 + veta S1/K13), B (5 par w grupie TV),
     oraz warianty 2 transz z 5 nogami na stronę (A_stag, B_stag: każda noga/para trzymana 2 tyg.,
     co sobotę wymiana 2 lub 3), referencyjnie 2×5 nakładające się (10 nazw/stronę, pół wagi),
     D_lo (A + budżet |b_SOX net| ≤ 1,0) i veto cenowe (nazwy > 1280 / > 960 USD poza koszykiem).
  2. Ekspozycja czynnikowa ex ante (b_SOX net z 250 sesji) i zrealizowana (regresja tygodniowa).
  3. Skład dzisiejszy vs point-in-time (tabele JOIN/LEAVE z weryfikacja_C1.py + dropped_closes.csv).
  4. Wykonalność lotów 0,1 akcji przy kapitale odniesienia 1000 USD dla 10 i 20 pozycji.
  5. Kapitał: bootstrap blokowy P(kill −25%) 12/52 tyg. dla polityk sizingu, alfa 0 i in-sample.
Bez liczb z rachunku (kapitał odniesienia = START_EQUITY 1000 USD z app.py).
"""
import json, math, os, sys
import numpy as np, pandas as pd
from collections import Counter, defaultdict

BASE = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
CSV = f'{BASE}/dane/closes_5y.csv'
DROPPED = f'{BASE}/dane/dropped_closes.csv'
TV = '/home/user/ndx100-bot/data/tv-screen-2026-W8.json'
OUT_MD = f'{BASE}/analiza/projektC_bt_out.md'
OUT_JSON = f'{BASE}/analiza/projektC_bt_wyniki.json'
OUT_SER = f'{BASE}/analiza/projektC_bt_serie.csv'
NON_CAND = {'^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV'}
LOOK, SKIP, NLEG = 126, 5, 5
SIG_WIN, BETA_WIN = 60, 250
COST_LEG = 0.0010           # 0,10% nominału nogi na każdą zmienioną nogę (jak C1/bt_neutralnosc)
FIN = 0.06                  # 6%/rok od gross
MIN_IND, MIN_GROUP = 4, 3
SEED = 20261018
rng = np.random.default_rng(SEED)

# point-in-time (weryfikacja_C1.py)
JOIN = {'CEG': '2022-02-02', 'GEHC': '2023-01-04', 'CCEP': '2023-12-18', 'DASH': '2023-12-18', 'ROP': '2023-12-18',
        'TTWO': '2023-12-18', 'ARM': '2024-06-24', 'LIN': '2024-07-15', 'APP': '2024-11-18', 'PLTR': '2024-12-23',
        'MSTR': '2024-12-23', 'AXON': '2024-12-23', 'SHOP': '2025-05-19', 'TRI': '2025-07-28', 'ALNY': '2025-12-22',
        'FER': '2025-12-22', 'MPWR': '2025-12-22', 'STX': '2025-12-22', 'WDC': '2025-12-22', 'WMT': '2026-01-20',
        'SNDK': '2026-04-20', 'LITE': '2026-05-18', 'ALAB': '2026-06-22', 'CRWV': '2026-06-22', 'NBIS': '2026-06-22',
        'RKLB': '2026-06-22', 'TER': '2026-06-22', 'HONA': '2026-06-15', 'SPCX': '2026-06-12',
        'ENPH': '2022-11-21', 'CSGP': '2022-12-19', 'GFS': '2022-12-19', 'MDB': '2023-12-18', 'CDW': '2023-12-18', 'SMCI': '2024-07-22'}
LEAVE = {'OKTA': '2022-11-21', 'BIDU': '2022-12-19', 'DOCU': '2022-12-19', 'MTCH': '2022-12-19', 'NTES': '2022-12-19',
         'SWKS': '2022-12-19', 'VRSN': '2022-12-19', 'ALGN': '2023-12-18', 'EBAY': '2023-12-18', 'ENPH': '2023-12-18',
         'JD': '2023-12-18', 'LCID': '2023-12-18', 'ZM': '2023-12-18', 'SIRI': '2024-06-24', 'DLTR': '2024-11-18',
         'ILMN': '2024-12-23', 'SMCI': '2024-12-23', 'MRNA': '2024-12-23', 'MDB': '2025-05-19', 'BIIB': '2025-12-22',
         'CDW': '2025-12-22', 'GFS': '2025-12-22', 'LULU': '2025-12-22', 'ON': '2025-12-22', 'TTD': '2025-12-22',
         'TEAM': '2026-04-20', 'CSGP': '2026-05-18', 'CHTR': '2026-06-22', 'VRSK': '2026-06-22', 'WBD': '2026-10-09'}
# taksonomia TV (industry, sector) dla spółek usuniętych — PRZYBLIŻONA (ręcznie, wg klasyfikacji TradingView)
IND_DROPPED = {
    'LCID': ('Motor Vehicles', 'Consumer Durables'), 'NTES': ('Internet Software/Services', 'Technology Services'),
    'OKTA': ('Packaged Software', 'Technology Services'), 'CSGP': ('Internet Software/Services', 'Technology Services'),
    'ENPH': ('Electrical Products', 'Producer Manufacturing'), 'LULU': ('Apparel/Footwear Retail', 'Retail Trade'),
    'TEAM': ('Packaged Software', 'Technology Services'), 'SMCI': ('Computer Processing Hardware', 'Electronic Technology'),
    'ZM': ('Packaged Software', 'Technology Services'), 'ILMN': ('Medical Specialties', 'Health Technology'),
    'BIDU': ('Internet Software/Services', 'Technology Services'), 'DOCU': ('Packaged Software', 'Technology Services'),
    'BIIB': ('Biotechnology', 'Health Technology'), 'CDW': ('Information Technology Services', 'Technology Services'),
    'SIRI': ('Broadcasting', 'Consumer Services'), 'EBAY': ('Internet Retail', 'Retail Trade'),
    'MDB': ('Packaged Software', 'Technology Services'), 'DLTR': ('Discount Stores', 'Retail Trade'),
    'SWKS': ('Semiconductors', 'Electronic Technology'), 'GFS': ('Semiconductors', 'Electronic Technology'),
    'TTD': ('Internet Software/Services', 'Technology Services'), 'CHTR': ('Cable/Satellite TV', 'Consumer Services'),
    'ON': ('Semiconductors', 'Electronic Technology'), 'VRSK': ('Miscellaneous Commercial Services', 'Commercial Services'),
    'VRSN': ('Internet Software/Services', 'Technology Services'), 'MTCH': ('Internet Software/Services', 'Technology Services'),
    'JD': ('Internet Retail', 'Retail Trade'), 'ALGN': ('Medical Specialties', 'Health Technology'),
    'KHC': ('Food: Major Diversified', 'Consumer Non-Durables'), 'WBD': ('Broadcasting', 'Consumer Services')}

# ------------------------------------------------------------------ dane
raw = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
raw = raw[raw['^NDX'].notna()].ffill(limit=3)
drop = pd.read_csv(DROPPED, parse_dates=['date']).set_index('date').sort_index().reindex(raw.index).ffill(limit=3)
dates = raw.index
NDX = raw['^NDX'].to_numpy(float); SOX = raw['^SOX'].to_numpy(float); VIX = raw['^VIX'].to_numpy(float)
QQQ = raw['QQQ'].to_numpy(float)
DEF = (raw[['XLP', 'XLU', 'XLV']].pct_change().mean(axis=1)).to_numpy(float)   # dzienny zwrot „defensyw”
cands_today = [c for c in raw.columns if c not in NON_CAND]
tv_rows = json.load(open(TV))['data']['rows']
IND = {r['name']: (r.get('industry') or '', r.get('sector') or '') for r in tv_rows}
IND.update(IND_DROPPED)
LAST_PX = raw[cands_today].iloc[-1]


def build(pit):
    if pit:
        P = np.hstack([raw[cands_today].to_numpy(float), drop.to_numpy(float)])
        names = cands_today + list(drop.columns)
    else:
        P = raw[cands_today].to_numpy(float); names = list(cands_today)
    return P, names


def windows():
    iso = dates.isocalendar()
    keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
    last = {}
    for i, k in enumerate(keys):
        last[k] = i
    idx = [last[w] for w in sorted(last)]
    return np.array(idx[:-1]), np.array(idx[1:])


D0, D5 = windows()
R = None  # dzienne zwroty (ustawiane per budowa)


def grouping(universe):
    ic = Counter(IND.get(t, ('', ''))[0] for t in universe)
    g = {}
    for t in universe:
        i, s = IND.get(t, ('', ''))
        if not i and not s:
            g[t] = 'Pozostałe'
        else:
            g[t] = i if ic[i] >= MIN_IND else (s or i)
    gc = Counter(g.values())
    return {t: (g[t] if gc[g[t]] >= MIN_GROUP else 'Pozostałe') for t in universe}


def state_at(P, names, w, pit, price_cap=None):
    """Sygnały na D0 okna w: mom (rel. do NDX), sigma60, r10, beta_sox, dostępność."""
    d0 = D0[w]; d5 = D5[w]
    need = LOOK + SKIP
    if d0 - max(need, BETA_WIN) < 0:
        return None
    seg = P[d0 - need:d0 + 1]
    ok = ~np.isnan(seg).any(axis=0) & ~np.isnan(P[d5])
    if pit:
        for j, n in enumerate(names):
            if n in JOIN and pd.Timestamp(JOIN[n]) > dates[d0]: ok[j] = False
            if n in LEAVE and pd.Timestamp(LEAVE[n]) <= dates[d0]: ok[j] = False
    else:
        ok &= np.array([n not in drop.columns for n in names])
    if price_cap is not None:
        ok &= np.nan_to_num(P[d0], nan=0.0) <= price_cap
    a, b = d0 - need, d0 - SKIP
    mom = P[b] / P[a] - 1 - (NDX[b] / NDX[a] - 1)
    r = P[d0 - SIG_WIN:d0 + 1]; r = r[1:] / r[:-1] - 1
    sigma = np.nanstd(r, axis=0, ddof=1)
    r10 = P[d0] / P[d0 - 10] - 1
    # beta na SOX−NDX z 250 sesji
    px = P[d0 - BETA_WIN:d0 + 1]; rr = px[1:] / px[:-1] - 1
    f = (SOX[d0 - BETA_WIN + 1:d0 + 1] / SOX[d0 - BETA_WIN:d0] - 1) - (NDX[d0 - BETA_WIN + 1:d0 + 1] / NDX[d0 - BETA_WIN:d0] - 1)
    fm = f - f.mean(); vf = (fm ** 2).sum()
    rr0 = np.where(np.isnan(rr), 0.0, rr)
    bsox = ((rr0 - rr0.mean(axis=0)) * fm[:, None]).sum(axis=0) / vf
    idx = np.where(ok)[0]
    if len(idx) < 40:
        return None
    med = np.nanmedian(sigma[idx])
    s1 = sigma > 3 * med
    kand_l = {names[j] for j in idx if not s1[j]}
    kand_s = {names[j] for j in idx if not s1[j] and not (r10[j] <= -0.20)}
    uni = [names[j] for j in idx]
    return dict(d0=d0, d5=d5, uni=uni, mom={names[j]: mom[j] for j in idx}, sigma={names[j]: sigma[j] for j in idx},
                bsox={names[j]: bsox[j] for j in idx}, kand_l=kand_l, kand_s=kand_s, grp=grouping(uni),
                j={names[j]: j for j in idx}, s1=sum(1 for j in idx if s1[j]), k13=sum(1 for j in idx if r10[j] <= -0.20))


# ------------------------------------------------------------------ konstrukcje
def pick_plain(st, n=NLEG, excl_l=(), excl_s=()):
    order = sorted(st['uni'], key=lambda t: -st['mom'][t])
    L = [t for t in order if t in st['kand_l'] and t not in excl_l][:n]
    S = [t for t in order[::-1] if t in st['kand_s'] and t not in excl_s][:n]
    return L, S


def pairs_all(st, excl_groups=(), excl_names=()):
    gm = defaultdict(list)
    for t in st['uni']:
        g = st['grp'][t]
        if g != 'Pozostałe' and g not in excl_groups and t not in excl_names:
            gm[g].append(t)
    out = []
    for g, ts in gm.items():
        if len(ts) < MIN_GROUP: continue
        ts = sorted(ts, key=lambda t: -st['mom'][t])
        longs = [t for t in ts if t in st['kand_l']]; shorts = [t for t in ts[::-1] if t in st['kand_s']]
        if not longs or not shorts or longs[0] == shorts[0]: continue
        out.append((st['mom'][longs[0]] - st['mom'][shorts[0]], g, longs[0], shorts[0]))
    out.sort(reverse=True)
    return out


def pick_pairs(st, n=NLEG):
    pr = pairs_all(st)[:n]
    return [p[2] for p in pr], [p[3] for p in pr], [p[1] for p in pr]


def pick_pairs_cap(st, cap=0.5, n=NLEG, top=8):
    from itertools import combinations
    pr = pairs_all(st)[:top]
    if len(pr) < n: return [], [], []
    b = st['bsox']; best = None
    for comb in combinations(pr, n):
        net = np.mean([b[p[2]] for p in comb]) - np.mean([b[p[3]] for p in comb])
        tot = sum(p[0] for p in comb)
        key = (abs(net) <= cap, tot if abs(net) <= cap else -abs(net))
        if best is None or key > best[0]: best = (key, comb)
    comb = best[1]
    return [p[2] for p in comb], [p[3] for p in comb], [p[1] for p in comb]


def budget_sox(st, L, S, cap=1.0, depth=15):
    """Jak ranking.py konstrukcja_budzet, tylko b_SOX, próg cap."""
    order = sorted(st['uni'], key=lambda t: -st['mom'][t])
    candL = [t for t in order if t in st['kand_l']][:depth]
    candS = [t for t in order[::-1] if t in st['kand_s']][:depth]
    L, S = list(L), list(S)
    b = st['bsox']
    for _ in range(6):
        net = np.mean([b[t] for t in L]) - np.mean([b[t] for t in S])
        if abs(net) <= cap: break
        best = None
        for side, legs, cand in (('L', L, candL), ('S', S, candS)):
            for i, t in enumerate(legs):
                for c in cand:
                    if c in L or c in S: continue
                    new = legs.copy(); new[i] = c
                    nn = (np.mean([b[x] for x in new]) - np.mean([b[x] for x in S])) if side == 'L' else \
                         (np.mean([b[x] for x in L]) - np.mean([b[x] for x in new]))
                    if abs(nn) < abs(net) and (best is None or abs(nn) < best[0]):
                        best = (abs(nn), side, i, c)
        if best is None: break
        _, side, i, c = best
        (L if side == 'L' else S)[i] = c
    return L, S


def evaluate(st, w_legs):
    """w_legs: dict ticker -> waga (+ long, − short; suma |w| = 2). Zwraca spread pp, long/short pp, nogi trafione."""
    d0, d5 = st['d0'], st['d5']
    rn = NDX[d5] / NDX[d0] - 1
    lp = sp = 0.0; hit = 0
    for t, wt in w_legs.items():
        j = st['j'][t] if t in st['j'] else None
        if j is None: return None
        r = PP[d5, j] / PP[d0, j] - 1
        ex = (r - rn) * wt * 100
        if wt > 0: lp += ex
        else: sp += ex
        if ex > 0: hit += 1
    return dict(spread=lp + sp, long=lp, short=sp, hit=hit, n=len(w_legs))


def exante(st, L, S):
    """σ60 jednostkowa (śr. L − śr. S dzienne) i b_SOX net ex ante."""
    d0 = st['d0']
    px = PP[d0 - SIG_WIN:d0 + 1]; rr = px[1:] / px[:-1] - 1
    jl = [st['j'][t] for t in L]; js = [st['j'][t] for t in S]
    u = np.nanmean(rr[:, jl], axis=1) - np.nanmean(rr[:, js], axis=1)
    return float(np.nanstd(u, ddof=1)), float(np.mean([st['bsox'][t] for t in L]) - np.mean([st['bsox'][t] for t in S]))


def run(variant, pit, price_cap=None):
    global PP
    PP, names = build(pit)
    rows = []
    prev = {}
    held = []   # dla stag: lista (tag_week, L_list, S_list) albo par
    tranches = []
    for w in range(len(D0)):
        st = state_at(PP, names, w, pit, price_cap)
        if st is None:
            prev = {}; held = []; tranches = []; continue
        pairs_g = None
        if variant in ('A0', 'A', 'D_lo', 'D_05'):
            if variant == 'A0':
                order = sorted(st['uni'], key=lambda t: -st['mom'][t])
                L, S = order[:NLEG], order[-NLEG:][::-1]
            else:
                L, S = pick_plain(st)
                if variant == 'D_lo': L, S = budget_sox(st, L, S, cap=1.0)
                if variant == 'D_05': L, S = budget_sox(st, L, S, cap=0.5)
            wl = {t: 1 / NLEG for t in L}; wl.update({t: -1 / NLEG for t in S})
        elif variant in ('B', 'B_cap05', 'B_cap10'):
            if variant == 'B': L, S, pairs_g = pick_pairs(st)
            else: L, S, pairs_g = pick_pairs_cap(st, cap=0.5 if variant == 'B_cap05' else 1.0)
            if len(L) < NLEG: prev = {}; continue
            wl = {t: 1 / NLEG for t in L}; wl.update({t: -1 / NLEG for t in S})
        elif variant in ('A_stag', 'B_stag'):
            # każda noga/para trzymana 2 tygodnie; wymiana 2/3 na przemian
            held = [(tag, l, s) for (tag, l, s) in held if tag >= w - 1 and w - tag <= 1]
            if held and all(tag == w - 1 for tag, _, _ in held) and len(held) == NLEG:
                # drugi tydzień istnienia: usuń 3 najsłabsze wg bieżącego sygnału (start transzowania)
                key = lambda x: st['mom'].get(x[1], -9) - st['mom'].get(x[2], 9)
                held = sorted(held, key=key, reverse=True)[:2]
            kept_L = [l for _, l, _ in held]; kept_S = [s for _, _, s in held]
            need = NLEG - len(held)
            if variant == 'A_stag':
                nL, nS = pick_plain(st, n=NLEG, excl_l=set(kept_L) | set(kept_S), excl_s=set(kept_S) | set(kept_L))
                nL, nS = nL[:need], nS[:need]
                new = list(zip([w] * need, nL, nS))
            else:
                kept_g = {st['grp'].get(l, '') for l in kept_L}
                pr = pairs_all(st, excl_groups=kept_g, excl_names=set(kept_L) | set(kept_S))[:need]
                new = [(w, p[2], p[3]) for p in pr]
                pairs_g = [st['grp'].get(l) for l in kept_L] + [p[1] for p in pr]
            held = held + new
            if len(held) < NLEG: prev = {}; held = []; continue
            L = [l for _, l, _ in held]; S = [s for _, _, s in held]
            if any(t not in st['j'] for t in L + S):   # kontynuowana noga bez ceny → pomiń okno
                prev = {}; held = []; continue
            wl = {t: 1 / NLEG for t in L}; wl.update({t: -1 / NLEG for t in S})
        elif variant in ('A_2x5', 'B_2x5'):
            if variant == 'A_2x5': L, S = pick_plain(st)
            else:
                L, S, _ = pick_pairs(st)
                if len(L) < NLEG: prev = {}; tranches = []; continue
            tranches.append((L, S)); tranches = tranches[-2:]
            if len(tranches) < 2: continue
            wl = defaultdict(float)
            for tl, ts in tranches:
                if any(t not in st['j'] for t in tl + ts): wl = None; break
                for t in tl: wl[t] += 1 / (2 * NLEG)
                for t in ts: wl[t] -= 1 / (2 * NLEG)
            if wl is None: prev = {}; tranches = []; continue
            wl = {t: v for t, v in wl.items() if abs(v) > 1e-12}
            L = [t for t, v in wl.items() if v > 0]; S = [t for t, v in wl.items() if v < 0]
        else:
            raise ValueError(variant)
        ev = evaluate(st, wl)
        if ev is None: prev = {}; continue
        dw = sum(abs(wl.get(t, 0) - prev.get(t, 0)) for t in set(wl) | set(prev)) / 2   # ułamek nominału strony zmieniony
        legs_changed = dw * NLEG * 2 / 2  # ≈ liczba nóg (przy równych wagach 1/5)
        days = (dates[st['d5']] - dates[st['d0']]).days
        rot = COST_LEG * dw * 2 * 100       # pp spreadu: 0,1% × zmieniony nominał obu stron (gross 2 → ×2)
        fin = FIN * 2.0 * days / 365 * 100
        sig_u, bsox_net = exante(st, [t for t in wl if wl[t] > 0], [t for t in wl if wl[t] < 0])
        rsox = (SOX[st['d5']] / SOX[st['d0']] - 1) - (NDX[st['d5']] / NDX[st['d0']] - 1)
        rdef = (np.prod(1 + DEF[st['d0'] + 1:st['d5'] + 1]) - 1) - (QQQ[st['d5']] / QQQ[st['d0']] - 1)
        rows.append(dict(w=w, d0=str(dates[st['d0']].date()), d5=str(dates[st['d5']].date()), spread=ev['spread'],
                         long=ev['long'], short=ev['short'], hit=ev['hit'], nlegs=ev['n'], net=ev['spread'] - rot - fin,
                         rot_pp=rot, turn_legs=legs_changed, sigma_unit=sig_u, bsox_net=bsox_net,
                         r_sox=rsox * 100, r_def=rdef * 100, vix=VIX[st['d0']], ndx=(NDX[st['d5']] / NDX[st['d0']] - 1) * 100,
                         univ=len(st['uni']), ngroups=len(set(st['grp'].values()) - {'Pozostałe'}),
                         L=' '.join(sorted(wl_t for wl_t in wl if wl[wl_t] > 0)), S=' '.join(sorted(t for t in wl if wl[t] < 0)),
                         grupy=' | '.join(pairs_g) if pairs_g else ''))
        prev = wl
    return pd.DataFrame(rows).set_index('w')


# ------------------------------------------------------------------ metryki
def metr(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    n = len(x); m = x.mean(); sd = x.std(ddof=1)
    cum = np.cumsum(x); dd = (cum - np.maximum.accumulate(cum)).min()
    return dict(n=n, mean=m, sd=sd, t=m / sd * math.sqrt(n), sharpe=m / sd * math.sqrt(52), hit=float((x > 0).mean()),
                p5=float(np.percentile(x, 5)), worst=float(x.min()), maxdd=float(dd))


def factor_fit(df):
    X = np.column_stack([np.ones(len(df)), df.r_sox.values, df.r_def.values, df.ndx.values])
    y = df.spread.values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    r2 = 1 - res.var() / y.var()
    Xs = np.column_stack([np.ones(len(df)), df.r_sox.values])
    bs, *_ = np.linalg.lstsq(Xs, y, rcond=None)
    r2s = 1 - (y - Xs @ bs).var() / y.var()
    return dict(b_sox=b[1], b_def=b[2], b_ndx=b[3], r2=r2, b_sox_alone=bs[1], r2_sox=r2s)


def paired(a, b):
    j = a.join(b, lsuffix='_a', rsuffix='_b', how='inner')
    d = j.spread_b - j.spread_a
    n = len(d); m = d.mean(); se = d.std(ddof=1) / math.sqrt(n)
    # σ-ratio bootstrap
    rs = []
    for _ in range(2000):
        ii = rng.integers(0, n, n)
        rs.append(j.spread_b.values[ii].std(ddof=1) / j.spread_a.values[ii].std(ddof=1))
    ratio = j.spread_b.std(ddof=1) / j.spread_a.std(ddof=1)
    # F-test (log-F approx)
    F = (j.spread_b.var(ddof=1) / j.spread_a.var(ddof=1))
    z = math.log(F) / math.sqrt(2 / (n - 1) + 2 / (n - 1))
    from math import erf
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))
    return dict(n=n, delta=m, t=m / se, ci_lo=m - 1.96 * se, ci_hi=m + 1.96 * se, sigma_ratio=ratio,
                ratio_lo=float(np.percentile(rs, 2.5)), ratio_hi=float(np.percentile(rs, 97.5)), F_p=p,
                corr=float(np.corrcoef(j.spread_a, j.spread_b)[0, 1]),
                legs_common=float(np.mean([len(set(a_.split()) & set(b_.split())) for a_, b_ in zip(j.L_a, j.L_b)]) +
                                  np.mean([len(set(a_.split()) & set(b_.split())) for a_, b_ in zip(j.S_a, j.S_b)])))


def boot_capital(df, policy, alpha0=True, weeks=52, npath=5000, block=4, soft=False, cost=True):
    """Ścieżki kapitału z bootstrapu blokowego tygodni; policy: 'fix:x' lub 'vt'."""
    sp = df.spread.values.copy()
    if alpha0: sp = sp - sp.mean()
    su = df.sigma_unit.values; tl = df.turn_legs.values
    n = len(sp)
    kills = np.zeros(npath, bool); mdd = np.zeros(npath); fin = np.zeros(npath); allocs = []
    for p in range(npath):
        idx = []
        while len(idx) < weeks:
            s = rng.integers(0, n - block); idx.extend(range(s, s + block))
        idx = idx[:weeks]
        cap = 1.0; peak = 1.0; soft_on = False; md = 0.0
        for i in idx:
            if policy == 'vt':
                a = min(0.12, max(0.04, 0.015 / (5 * su[i])))
            else:
                a = float(policy.split(':')[1])
            if soft:
                dd = cap / peak - 1
                if dd < -0.10: soft_on = True
                elif dd > -0.05: soft_on = False
                if soft_on: a *= 0.5
            allocs.append(a)
            r = 5 * a * sp[i] / 100
            if cost: r -= 10 * a * FIN / 52 + tl[i] * a * COST_LEG
            cap *= 1 + r
            peak = max(peak, cap)
            md = min(md, cap / peak - 1)
            if cap < 0.75 * peak: kills[p] = True; break
        mdd[p] = md; fin[p] = cap
    return dict(p_kill=float(kills.mean()), mdd_med=float(np.median(mdd)), mdd_p95=float(np.percentile(mdd, 5)),
                fin_p5=float(np.percentile(fin, 5)), fin_med=float(np.median(fin)), fin_p95=float(np.percentile(fin, 95)),
                alloc_mean=float(np.mean(allocs)))


def lots_table(prices, alloc_list, cap=1000.0, step=0.1, overshoot=1.6):
    out = {}
    for a in alloc_list:
        tgt = a * cap
        lot = prices * step
        skip = sorted(prices.index[lot > tgt * overshoot])
        over = sorted(prices.index[(lot > tgt) & (lot <= tgt * overshoot)])
        out[a] = dict(cel_usd=tgt, pomijane=skip, przestrzal=over)
    return out


# ------------------------------------------------------------------ main
def main():
    out = {}; md = []
    P = md.append
    P('# Projekt C — wyniki projektC_bt.py\n')
    P(f'Dane: closes_5y.csv {dates[0].date()}…{dates[-1].date()} ({len(dates)} sesji), {len(cands_today)} spółek dzisiejszych + {drop.shape[1]} usuniętych (PIT); okna tygodniowe ISO D0→D5.')
    P('Sygnał: momentum 6M relatywne do ^NDX (126 sesji, skip 5). Veta wspólne (poza A0): S1 σ60 > 3× mediany; K13 r10 ≤ −20% (tylko short). Koszty: 0,10% nominału na zmienioną nogę, 6%/rok od gross 2.\n')
    variants = ['A0', 'A', 'B', 'B_cap05', 'B_cap10', 'A_stag', 'B_stag', 'A_2x5', 'B_2x5', 'D_lo', 'D_05']
    series = {}
    for pit in (False, True):
        tag = 'PIT' if pit else 'dzis'
        P(f'\n## 1. Konstrukcje — skład {"point-in-time (JOIN/LEAVE + usunięte)" if pit else "dzisiejszy"}\n')
        P('| konstrukcja | n | śr. pp | σ | t | Sharpe | hit | p5 | najgorszy | maxDD | netto | t netto | obrót nóg/tydz. | σ60_unit śr. %/d | b_SOX net ex ante śr. | b_SOX zreal. | R² (SOX+DEF+NDX) | grup śr. |')
        P('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        res = {}
        for v in variants:
            df = run(v, pit)
            series[(v, tag)] = df
            m = metr(df.spread); mn = metr(df.net); ff = factor_fit(df)
            res[v] = dict(metryki=m, netto=mn, czynniki=ff, obrot=float(df.turn_legs.mean()), sigma_unit=float(df.sigma_unit.mean()),
                          bsox_exante=float(df.bsox_net.mean()), bsox_exante_abs=float(df.bsox_net.abs().mean()), grupy=float(df.ngroups.mean()))
            P(f"| {v} | {m['n']} | {m['mean']:+.2f} | {m['sd']:.2f} | {m['t']:.2f} | {m['sharpe']:.2f} | {m['hit']*100:.0f}% | {m['p5']:.1f} | {m['worst']:.1f} | {m['maxdd']:.0f} | {mn['mean']:+.2f} | {mn['t']:.2f} | {df.turn_legs.mean():.2f} | {df.sigma_unit.mean()*100:.2f} | {df.bsox_net.mean():+.2f} (|·| {df.bsox_net.abs().mean():.2f}) | {ff['b_sox']:+.2f} | {ff['r2']:.2f} | {df.ngroups.mean():.1f} |")
        out[f'konstrukcje_{tag}'] = res
        # sparowane vs A
        P(f'\n### 1b. Różnice sparowane wobec A ({tag})\n')
        P('| wariant | n wspólne | Δ śr. pp/tydz. | t(Δ) | CI95 Δ | σ-ratio | CI95 σ-ratio | F p | corr z A | nóg wspólnych z A (na 10) |')
        P('|---|---|---|---|---|---|---|---|---|---|')
        pr = {}
        for v in variants:
            if v == 'A': continue
            pp_ = paired(series[('A', tag)], series[(v, tag)])
            pr[v] = pp_
            P(f"| {v} | {pp_['n']} | {pp_['delta']:+.2f} | {pp_['t']:+.2f} | [{pp_['ci_lo']:+.2f}; {pp_['ci_hi']:+.2f}] | {pp_['sigma_ratio']:.3f} | [{pp_['ratio_lo']:.2f}; {pp_['ratio_hi']:.2f}] | {pp_['F_p']:.4f} | {pp_['corr']:.2f} | {pp_['legs_common']:.1f} |")
        out[f'sparowane_{tag}'] = pr
        # B_stag vs B
        pb = paired(series[('B', tag)], series[('B_stag', tag)]); pa = paired(series[('A', tag)], series[('A_stag', tag)])
        out[f'stag_vs_base_{tag}'] = dict(B=pb, A=pa)
        P(f"\nB_stag vs B: Δ {pb['delta']:+.2f} (t {pb['t']:+.2f}), σ-ratio {pb['sigma_ratio']:.3f}; A_stag vs A: Δ {pa['delta']:+.2f} (t {pa['t']:+.2f}), σ-ratio {pa['sigma_ratio']:.3f}.")
        # lata i reżimy dla A, B, B_stag
        P(f'\n### 1c. Lata i reżimy ({tag}) — średnia pp/tydz. (σ)\n')
        yrs = sorted({int(d[:4]) for d in series[('A', tag)].d0})
        P('| konstrukcja | ' + ' | '.join(str(y) for y in yrs) + ' | VIX>20 | VIX≤20 | SOX−NDX<−3 | SOX−NDX>+3 | połowa 1 | połowa 2 |')
        P('|---|' + '---|' * (len(yrs) + 6))
        lata = {}
        for v in ('A', 'B', 'B_cap05', 'B_cap10', 'A_stag', 'B_stag', 'D_lo'):
            df = series[(v, tag)]; yr = df.d0.str[:4].astype(int)
            cells = []
            for y in yrs:
                x = df.spread[yr == y]; cells.append(f'{x.mean():+.2f} ({x.std(ddof=1):.1f})' if len(x) > 2 else '—')
            h = len(df) // 2
            segs = [df.spread[df.vix > 20], df.spread[df.vix <= 20], df.spread[df.r_sox < -3], df.spread[df.r_sox > 3], df.spread.iloc[:h], df.spread.iloc[h:]]
            cells += [f'{x.mean():+.2f} ({x.std(ddof=1):.1f}, n{len(x)})' for x in segs]
            lata[v] = {str(y): float(df.spread[yr == y].mean()) for y in yrs}
            lata[v].update(dict(vix_gt20=float(segs[0].mean()), vix_le20=float(segs[1].mean()), sox_lt_m3=float(segs[2].mean()), sox_gt_3=float(segs[3].mean()), n_sox_lt_m3=int(len(segs[2]))))
            P(f'| {v} | ' + ' | '.join(cells) + ' |')
        out[f'lata_{tag}'] = lata

    # ------------------------------------------------ 2. veto cenowe (skład dzisiejszy)
    P('\n## 2. Veto cenowe (kurs > próg na D0 poza koszykiem) — skład dzisiejszy, kursy w CSV (skorygowane o splity, więc historycznie przybliżenie)\n')
    P('| konstrukcja | próg USD | n | śr. | σ | Δ vs bez veta | t(Δ) | udział nóg wyciętych nazw w bazie |')
    P('|---|---|---|---|---|---|---|---|')
    vc = {}
    for v in ('A', 'B', 'B_stag'):
        base = series[(v, 'dzis')]
        for capp in (1280.0, 960.0):
            df = run(v, False, price_cap=capp)
            pp_ = paired(base, df)
            drogie = set(LAST_PX.index[LAST_PX * 0.1 > capp * 0.1])
            udz = float(np.mean([len(set((l + ' ' + s).split()) & drogie) for l, s in zip(base.L, base.S)])) / 10
            vc[f'{v}_{int(capp)}'] = dict(metryki=metr(df.spread), paired=pp_, udzial_nog_drogich=udz, nazwy=sorted(drogie))
            P(f"| {v} | >{capp:.0f} ({', '.join(sorted(drogie))}) | {len(df)} | {df.spread.mean():+.2f} | {df.spread.std(ddof=1):.2f} | {pp_['delta']:+.2f} | {pp_['t']:+.2f} | {udz*100:.1f}% |")
    out['veto_cenowe'] = vc

    # ------------------------------------------------ 3. loty
    P('\n## 3. Wykonalność lotów 0,1 akcji (kapitał odniesienia 1000 USD, MAX_OVERSHOOT 1,6; kursy 2026-10-16 z CSV)\n')
    P('| pozycji | ALLOC/noga (udział kapitału) | cel USD | pomijane (0,1 akcji > 1,6×cel) | przestrzał (lot w (cel; 1,6 cel]) |')
    P('|---|---|---|---|---|')
    lt = {}
    for npos, allocs in ((10, (0.12, 0.10, 0.08, 0.06, 0.04)), (20, (0.06, 0.05, 0.04, 0.03))):
        tab = lots_table(LAST_PX, allocs)
        for a, d in tab.items():
            lt[f'{npos}_{a}'] = d
            P(f"| {npos} | {a:.2f} | {d['cel_usd']:.0f} | {len(d['pomijane'])}: {' '.join(d['pomijane'])} | {len(d['przestrzal'])}: {' '.join(d['przestrzal'])} |")
    out['loty'] = lt
    # udział nazw drogich w nogach B (dzis) dla progu 0,08/10 pozycji
    drogie08 = set(lots_table(LAST_PX, (0.08,))[0.08]['pomijane'])
    P(f"\nNazwy pomijane przy 10 pozycjach i ALLOC 0,08: {sorted(drogie08)}; przy 20 pozycjach i ALLOC 0,04/pozycję: {lots_table(LAST_PX,(0.04,))[0.04]['pomijane']}.")

    # ------------------------------------------------ 4. kapitał
    P('\n## 4. Kapitał — bootstrap blokowy (blok 4 tyg., 5000 ścieżek, koszty wliczone), kill = kapitał < 0,75 × kroczący szczyt\n')
    P('| konstrukcja | skład | polityka | alfa | P(kill 12 tyg.) | P(kill 52 tyg.) | maxDD 52 mediana / p95 | kapitał po 52: p5 / med / p95 | śr. ALLOC |')
    P('|---|---|---|---|---|---|---|---|---|')
    capres = {}
    for v in ('A', 'B', 'B_cap05', 'B_stag'):
        for tag in ('dzis', 'PIT'):
            df = series[(v, tag)]
            for pol, soft in (('fix:0.08', False), ('fix:0.12', False), ('vt', False), ('vt', True)):
                for a0 in (True, False):
                    r12 = boot_capital(df, pol, alpha0=a0, weeks=12, npath=3000, soft=soft)
                    r52 = boot_capital(df, pol, alpha0=a0, weeks=52, npath=3000, soft=soft)
                    key = f'{v}|{tag}|{pol}{"+soft" if soft else ""}|{"alfa0" if a0 else "in-sample"}'
                    capres[key] = dict(k12=r12, k52=r52)
                    P(f"| {v} | {tag} | {pol}{' + soft −10%' if soft else ''} | {'0' if a0 else 'in-sample'} | {r12['p_kill']*100:.1f}% | {r52['p_kill']*100:.1f}% | {r52['mdd_med']*100:.0f}% / {r52['mdd_p95']*100:.0f}% | {r52['fin_p5']:.2f} / {r52['fin_med']:.2f} / {r52['fin_p95']:.2f} | {r52['alloc_mean']:.3f} |")
    out['kapital'] = capres
    # σ tygodniowa kapitału i koszty dla wybranej
    P('\n### 4b. Przekład na kapitał (B_stag, PIT): σ tyg. spreadu × 5 × ALLOC; koszty tygodniowe\n')
    for v in ('A', 'B', 'B_cap05', 'B_stag'):
        df = series[(v, 'PIT')]
        for a in (0.08, 0.10, 0.12):
            fin_w = 10 * a * FIN / 52 * 100; rot_w = df.turn_legs.mean() * a * COST_LEG * 100
            P(f"- {v} ALLOC {a:.2f}: σ tyg. kapitału {5*a*df.spread.std(ddof=1):.2f}%, μ tyg. brutto {5*a*df.spread.mean():+.3f}%, koszt tyg. {fin_w+rot_w:.3f}% (finansowanie {fin_w:.3f} + rotacja {rot_w:.3f}; obrót {df.turn_legs.mean():.2f} nogi), gross {10*a*100:.0f}%")
    # ALLOC z vol-targetu rozkład
    for v in ('A', 'B', 'B_cap05', 'B_stag'):
        df = series[(v, 'PIT')]
        al = np.clip(0.015 / (5 * df.sigma_unit), 0.04, 0.12)
        P(f"- {v}: ALLOC z vol-targetu (PIT) p5 {np.percentile(al,5):.3f}, mediana {np.median(al):.3f}, p95 {np.percentile(al,95):.3f}; udział tygodni na suficie 0,12: {(al>=0.12).mean()*100:.0f}%; w 2026: mediana {np.median(al[df.d0.str.startswith('2026')]):.3f}")
        out.setdefault('alloc_vt', {})[v] = dict(p5=float(np.percentile(al, 5)), med=float(np.median(al)), p95=float(np.percentile(al, 95)), med_2026=float(np.median(al[df.d0.str.startswith('2026')])))

    # ------------------------------------------------ 5. W8 na D0 2026-10-16
    P('\n## 5. Koszyki na ostatnim D0 (2026-10-16, skład dzisiejszy)\n')
    PPl, names = build(False)
    globals()['PP'] = PPl
    global D0, D5
    D0 = np.append(D0, len(dates) - 1); D5 = np.append(D5, len(dates) - 1)
    st = state_at(PPl, names, len(D0) - 1, False)
    L, S = pick_plain(st)
    out['W8'] = {}
    if st:
        Lb, Sb, gb = pick_pairs(st)
        Lc, Sc, gc = pick_pairs_cap(st, cap=0.5)
        for nm, (l, s) in {'A': (L, S), 'B': (Lb, Sb), 'B_cap05': (Lc, Sc)}.items():
            su, bs = exante(st, l, s)
            out['W8'][nm] = dict(long=l, short=s, sigma_unit=su, bsox_net=bs, alloc_vt=min(0.12, max(0.04, 0.015 / (5 * su))))
            P(f"- {nm}: LONG {' '.join(l)} / SHORT {' '.join(s)}; σ60_unit {su*100:.2f}%/d; b_SOX net {bs:+.2f}; ALLOC z vol-targetu {out['W8'][nm]['alloc_vt']:.3f}" + (f"; grupy: {', '.join(gb if nm == 'B' else gc)}" if nm != 'A' else ''))
        fakt_L = ['GOOGL', 'GILD', 'MSFT', 'QCOM', 'ADP']; fakt_S = ['AXON', 'DASH', 'ALNY', 'APP', 'FER']
        if all(t in st['j'] for t in fakt_L + fakt_S):
            su, bs = exante(st, fakt_L, fakt_S)
            out['W8']['FAKT'] = dict(sigma_unit=su, bsox_net=bs)
            P(f"- FAKT W8: σ60_unit {su*100:.2f}%/d; b_SOX net {bs:+.2f}")
        P(f"Uwaga: stan na D0 = {str(dates[st['d0']].date())} (ostatnie okno z D5 w danych), nie 16.10.")

    # zapis
    allser = []
    for (v, tag), df in series.items():
        d = df.copy(); d['wariant'] = v; d['sklad'] = tag; allser.append(d)
    pd.concat(allser).to_csv(OUT_SER)
    def clean(o):
        if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(x) for x in o]
        if isinstance(o, (np.floating, float)): return None if (isinstance(o, float) and math.isnan(o)) else round(float(o), 5)
        if isinstance(o, (np.integer,)): return int(o)
        return o
    json.dump(clean(out), open(OUT_JSON, 'w'), ensure_ascii=False, indent=1)
    open(OUT_MD, 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
