#!/usr/bin/env python3
"""
projektA_bt.py — liczby dla PROJEKTU A (proces mechaniczny), których fazy 1–2 nie policzyły.

Harness = weryfikacja_C1.py (uniwersum point-in-time: dzisiejszy skład + 28 spółek usuniętych,
daty dołączeń/usunięć), okna piątek→piątek, 5L/5S równych wag, noga = r_i − r_NDX,
spread = śr. LONG + śr. SHORT (p.p., gross 2). Koszty: 0,10% × nominał nogi za zmienioną nazwę,
finansowanie 6%/rok × gross.

Co liczy:
 1. Konstrukcje: A0 (TOP5/BOTTOM5 bez wet), A (A0 + veto σ S1 + veto short K13),
    D (A + budżet czynnikowy |b_SOX net| ≤ 0,5, |b_DEF net| ≤ 0,5, wymiany w TOP15/BOTTOM15, jak
    scripts/ranking.py::konstrukcja_budzet) — na PIT i na składzie dzisiejszym.
 2. Ekspozycja zrealizowanego spreadu na (SOX−NDX) i DEF (regresja tygodniowa) dla A i D.
 3. Sizing: stałe ALLOC 0,24/0,12/0,08 vs vol-target clip(0,015/(5·σ60_unit), 0,04, 0,12)
    oraz vol-target + próg miękki (DD < −10% → ×0,5 do DD > −5%): ścieżka dzienna kapitału,
    P(kill −25% od kroczącego szczytu) w oknach 12 i 52 tyg., alfa in-sample i alfa 0 (demean).
 4. Nakładka ≤1 wymiana nogi na stronę: rozkład Δ spreadu przy losowej wymianie nogi 5. na kandydata
    z rang 6–15 (tej samej strony) — σ Δ i liczba tygodni do wykrycia +0,3 / +0,5 p.p. przy t = 2.
 5. Stop 20% od wejścia bez reopen (na zamknięciach) — koszt vs brak stopu.
Wyjście: projektA_bt_out.md, projektA_bt_wyniki.json, projektA_bt_serie.csv. Bez liczb z rachunku.
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
OUT_MD = f'{BASE}/analiza/projektA_bt_out.md'
OUT_JSON = f'{BASE}/analiza/projektA_bt_wyniki.json'
OUT_SERIE = f'{BASE}/analiza/projektA_bt_serie.csv'

NON_CAND = ['^NDX', '^SOX', '^VIX', '^GSPC', 'QQQ', 'XLP', 'XLU', 'XLV', 'SMH', 'IGV']
COST_LEG = 0.0010
FIN_RATE = 0.06
LOOK, SKIP = 126, 5
SIG_WIN, BETA_WIN, BETA_MIN = 60, 250, 120
SIGMA_VETO_MULT = 3.0
SHORT_VETO_R10 = -0.20
FACTOR_BUDGET, MAX_SWAPS, GLEBIA = 0.5, 6, 15
VOL_TARGET, ALLOC_MIN, ALLOC_MAX = 0.015, 0.04, 0.12
KILL = 0.75
SEED = 20261018
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- dane (jak weryfikacja_C1.py)
raw = pd.read_csv(CSV, parse_dates=['date']).set_index('date').sort_index()
raw = raw[raw['^NDX'].notna()]
raw = raw.ffill(limit=3)
dropped_df = pd.read_csv(DROPPED, parse_dates=['date']).set_index('date').sort_index()
dropped_df = dropped_df.reindex(raw.index).ffill(limit=3)
dates = raw.index
NDX = raw['^NDX'].to_numpy(float)
F_SOX_D = raw['^SOX'].pct_change().to_numpy(float) - raw['^NDX'].pct_change().to_numpy(float)
F_DEF_D = ((raw['XLP'].pct_change() + raw['XLU'].pct_change() + raw['XLV'].pct_change()) / 3
           - raw['QQQ'].pct_change()).to_numpy(float)
cands_all = [c for c in raw.columns if c not in NON_CAND]

JOIN_APPROX = {
    'CEG': '2022-02-02', 'GEHC': '2023-01-04',
    'CCEP': '2023-12-18', 'DASH': '2023-12-18', 'ROP': '2023-12-18', 'TTWO': '2023-12-18',
    'ARM': '2024-06-24', 'LIN': '2024-07-15', 'APP': '2024-11-18',
    'PLTR': '2024-12-23', 'MSTR': '2024-12-23', 'AXON': '2024-12-23',
    'SHOP': '2025-05-19', 'TRI': '2025-07-28',
    'ALNY': '2025-12-22', 'FER': '2025-12-22', 'MPWR': '2025-12-22', 'STX': '2025-12-22', 'WDC': '2025-12-22',
    'WMT': '2026-01-20', 'SNDK': '2026-04-20', 'LITE': '2026-05-18',
    'ALAB': '2026-06-22', 'CRWV': '2026-06-22', 'NBIS': '2026-06-22', 'RKLB': '2026-06-22', 'TER': '2026-06-22',
    'HONA': '2026-06-15', 'SPCX': '2026-06-12',
}
LEAVE_APPROX = {
    'OKTA': '2022-11-21',
    'BIDU': '2022-12-19', 'DOCU': '2022-12-19', 'MTCH': '2022-12-19', 'NTES': '2022-12-19', 'SWKS': '2022-12-19', 'VRSN': '2022-12-19',
    'ALGN': '2023-12-18', 'EBAY': '2023-12-18', 'ENPH': '2023-12-18', 'JD': '2023-12-18', 'LCID': '2023-12-18', 'ZM': '2023-12-18',
    'SIRI': '2024-06-24', 'DLTR': '2024-11-18', 'ILMN': '2024-12-23', 'SMCI': '2024-12-23', 'MRNA': '2024-12-23',
    'MDB': '2025-05-19',
    'BIIB': '2025-12-22', 'CDW': '2025-12-22', 'GFS': '2025-12-22', 'LULU': '2025-12-22', 'ON': '2025-12-22', 'TTD': '2025-12-22',
    'TEAM': '2026-04-20', 'CSGP': '2026-05-18', 'CHTR': '2026-06-22', 'VRSK': '2026-06-22', 'WBD': '2026-10-09',
}
JOIN_DROPPED = {'ENPH': '2022-11-21', 'CSGP': '2022-12-19', 'GFS': '2022-12-19', 'MDB': '2023-12-18', 'CDW': '2023-12-18', 'SMCI': '2024-07-22'}


def build(pit=True):
    P = raw[cands_all].to_numpy(float)
    names = list(cands_all)
    join = dict(JOIN_APPROX)
    leave = dict(LEAVE_APPROX)
    if pit:
        P = np.hstack([P, dropped_df.to_numpy(float)])
        names += list(dropped_df.columns)
        join.update(JOIN_DROPPED)
    else:
        join, leave = {}, {}
    jarr = np.array([pd.Timestamp(join[n]) if n in join else pd.Timestamp('1900-01-01') for n in names])
    larr = np.array([pd.Timestamp(leave[n]) if n in leave else pd.Timestamp('2100-01-01') for n in names])
    return P, names, jarr, larr


def windows():
    iso = dates.isocalendar()
    keys = list(zip(iso.year.to_numpy(), iso.week.to_numpy()))
    last = {}
    for i, k in enumerate(keys):
        last[k] = i
    idx = [last[w] for w in sorted(last)]
    return np.array(idx[:-1]), np.array(idx[1:])


def beta_ols(y, x):
    m = ~np.isnan(y) & ~np.isnan(x)
    if m.sum() < BETA_MIN:
        return np.nan
    x, y = x[m], y[m]
    vx = x.var()
    return np.nan if vx <= 0 else np.cov(x, y, bias=True)[0, 1] / vx


def construct(P, names, jarr, larr, D0, D5, tag):
    """Zwraca listy nóg A0, A, D oraz dane tygodniowe."""
    nW = len(D0)
    R = P[1:] / P[:-1] - 1
    R = np.vstack([np.full((1, P.shape[1]), np.nan), R])  # R[t] = zwrot sesji t
    WR = P[D5] / P[D0] - 1
    WN = NDX[D5] / NDX[D0] - 1
    EX = WR - WN[:, None]
    out = {k: [None] * nW for k in ('A0', 'A_S1', 'A_K13', 'A', 'D')}
    swaps = np.zeros(nW)
    cand_pools = [None] * nW
    stats = []
    hist_need = SKIP + LOOK
    for w, d0 in enumerate(D0):
        if d0 - max(hist_need, SIG_WIN, BETA_MIN) < 0:
            continue
        seg = P[d0 - hist_need:d0 + 1]
        ok = ~np.isnan(seg).any(axis=0) & ~np.isnan(WR[w])
        ok &= (jarr <= dates[d0]) & (larr > dates[d0])
        a, b = d0 - hist_need, d0 - SKIP
        s = P[b] / P[a] - 1 - (NDX[b] / NDX[a] - 1)
        s[~ok] = np.nan
        idx = np.where(ok)[0]
        if len(idx) < 30:
            continue
        sig60 = np.nanstd(R[d0 - SIG_WIN + 1:d0 + 1], axis=0)
        med = np.nanmedian(sig60[idx])
        r10 = P[d0] / P[d0 - 10] - 1
        veto_sigma = sig60 > SIGMA_VETO_MULT * med
        veto_short = r10 <= SHORT_VETO_R10
        order = idx[np.argsort(-s[idx], kind='stable')]
        # A0
        out['A0'][w] = (order[:5], order[-5:])
        okL = [i for i in order if not veto_sigma[i]]
        okS = [i for i in order if not veto_sigma[i] and not veto_short[i]]
        L, S = np.array(okL[:5]), np.array(okS[-5:])
        out['A'][w] = (L, S)
        out['A_S1'][w] = (np.array(okL[:5]), np.array([i for i in order if not veto_sigma[i]][-5:]))
        out['A_K13'][w] = (order[:5], np.array([i for i in order if not veto_short[i]][-5:]))
        top = okL[:GLEBIA]
        bot = okS[-GLEBIA:][::-1]  # od najgorszego momentum
        cand_pools[w] = (top, bot)
        # bety 250 sesji
        lo_b = max(1, d0 - BETA_WIN + 1)
        need = set(top) | set(bot)
        b_sox, b_def = {}, {}
        for i in need:
            b_sox[i] = beta_ols(R[lo_b:d0 + 1, i], F_SOX_D[lo_b:d0 + 1])
            b_def[i] = beta_ols(R[lo_b:d0 + 1, i], F_DEF_D[lo_b:d0 + 1])

        def bb(dct, i):
            v = dct.get(i, np.nan)
            return 0.0 if np.isnan(v) else v

        def net(l, s_, dct):
            return np.mean([bb(dct, i) for i in l]) - np.mean([bb(dct, i) for i in s_])

        def przekr(l, s_):
            return max(0.0, abs(net(l, s_, b_sox)) - FACTOR_BUDGET) + max(0.0, abs(net(l, s_, b_def)) - FACTOR_BUDGET)

        lo, sh = list(L), list(S)
        nsw = 0
        for _ in range(MAX_SWAPS):
            p0 = przekr(lo, sh)
            if p0 <= 1e-9:
                break
            best = None
            for strona, lst, pula in (('long', lo, top), ('short', sh, bot)):
                for i in range(len(lst)):
                    for c in pula:
                        if c in lo or c in sh:
                            continue
                        nl, ns = list(lo), list(sh)
                        (nl if strona == 'long' else ns)[i] = c
                        p1 = przekr(nl, ns)
                        if best is None or p1 < best[0]:
                            best = (p1, nl, ns)
            if best is None or best[0] >= p0 - 1e-9:
                break
            _, lo, sh = best
            nsw += 1
        out['D'][w] = (np.array(lo), np.array(sh))
        swaps[w] = nsw
        stats.append(dict(w=w, d0=str(dates[d0].date()), univ=len(idx), n_veto_sigma=int(veto_sigma[idx].sum()),
                          n_veto_short=int((veto_short & ok).sum()), swaps=nsw,
                          bsox_A=net(L, S, b_sox), bdef_A=net(L, S, b_def),
                          bsox_D=net(lo, sh, b_sox), bdef_D=net(lo, sh, b_def),
                          A_eq_D=int(set(L) == set(lo) and set(S) == set(sh))))
    return dict(legs=out, R=R, EX=EX, WN=WN, D0=D0, D5=D5, swaps=swaps, pools=cand_pools, stats=stats, names=names, tag=tag)


def weekly_series(ctx, key):
    legs = ctx['legs'][key]
    EX, D0, D5 = ctx['EX'], ctx['D0'], ctx['D5']
    nW = len(D0)
    sp = np.full(nW, np.nan); turn = np.zeros(nW)
    prev = None
    for w in range(nW):
        if legs[w] is None:
            prev = None
            continue
        L, S = legs[w]
        sp[w] = (EX[w, L].mean() - EX[w, S].mean()) * 100
        turn[w] = 10 if prev is None else len(set(L) - set(prev[0])) + len(set(S) - set(prev[1]))
        prev = (L, S)
    days = np.array([(dates[b] - dates[a]).days for a, b in zip(D0, D5)])
    net = sp - turn * COST_LEG * (1 / 5) * 100 - FIN_RATE * 2.0 * days / 365 * 100
    return sp, net, turn


def metrics(x):
    m = ~np.isnan(x)
    x = x[m]
    n = len(x)
    mu, sd = x.mean(), x.std(ddof=1)
    t = mu / sd * math.sqrt(n)
    cum = np.cumsum(x)
    dd = (np.maximum.accumulate(cum) - cum).max()
    return dict(n=n, mean=round(mu, 3), sd=round(sd, 3), t=round(t, 2), sharpe=round(mu / sd * math.sqrt(52), 2),
                hit=round((x > 0).mean(), 3), worst=round(x.min(), 2), p5=round(np.percentile(x, 5), 2), maxdd_pp=round(dd, 1))


def factor_load(ctx, sp):
    D0, D5 = ctx['D0'], ctx['D5']
    fs = np.array([np.nansum(F_SOX_D[a + 1:b + 1]) for a, b in zip(D0, D5)]) * 100
    fd = np.array([np.nansum(F_DEF_D[a + 1:b + 1]) for a, b in zip(D0, D5)]) * 100
    m = ~np.isnan(sp)
    X = np.column_stack([np.ones(m.sum()), fs[m], fd[m]])
    coef, *_ = np.linalg.lstsq(X, sp[m], rcond=None)
    pred = X @ coef
    r2 = 1 - ((sp[m] - pred) ** 2).sum() / ((sp[m] - sp[m].mean()) ** 2).sum()
    return dict(alpha=round(coef[0], 3), b_sox=round(coef[1], 3), b_def=round(coef[2], 3), r2=round(r2, 3))


# ---------------------------------------------------------------- ścieżka dzienna kapitału
def daily_unit(ctx, key):
    """Dzienny spread jednostkowy (śr. L − śr. S) dla nóg bieżącego tygodnia; σ60_unit ex ante; zmiany nóg."""
    legs = ctx['legs'][key]; R = ctx['R']; D0, D5 = ctx['D0'], ctx['D5']
    days, unit, week_of, sig60_ex, changed = [], [], [], [], []
    prev = None
    for w in range(len(D0)):
        if legs[w] is None:
            prev = None
            continue
        L, S = legs[w]
        hist = R[D0[w] - SIG_WIN + 1:D0[w] + 1]
        u_hist = np.nanmean(hist[:, L], axis=1) - np.nanmean(hist[:, S], axis=1)
        s60 = np.nanstd(u_hist)
        ch = 10 if prev is None else len(set(L) - set(prev[0])) + len(set(S) - set(prev[1]))
        for t in range(D0[w] + 1, D5[w] + 1):
            days.append(t); week_of.append(w)
            unit.append(np.nanmean(R[t, L]) - np.nanmean(R[t, S]))
            sig60_ex.append(s60); changed.append(ch if t == D0[w] + 1 else 0)
        prev = (L, S)
    return np.array(days), np.array(unit), np.array(week_of), np.array(sig60_ex), np.array(changed)


def alloc_policy(name, sig60):
    if name.startswith('fixed'):
        return np.full_like(sig60, float(name.split('_')[1]))
    a = VOL_TARGET / (5 * sig60)
    return np.clip(a, ALLOC_MIN, ALLOC_MAX)


def simulate(unit, sig60, changed, policy, soft=False, demean=False, stop=None, legR=None):
    """Zwraca dzienne zwroty kapitału (ułamek)."""
    u = unit.copy()
    if demean:
        u = u - np.nanmean(u)
    a_base = alloc_policy(policy, sig60)
    n = len(u)
    ret = np.zeros(n)
    eq, peak = 1.0, 1.0
    factor = 1.0
    prev_a = 0.0
    for t in range(n):
        if soft:
            dd = eq / peak - 1
            if factor == 1.0 and dd < -0.10:
                factor = 0.5
            elif factor == 0.5 and dd > -0.05:
                factor = 1.0
        a = a_base[t] * factor
        cost = 0.0
        if changed[t] > 0:
            cost += changed[t] * a * COST_LEG          # rotacja nóg
            cost += abs(a - prev_a) * 10 * COST_LEG     # zmiana skali koszyka (reszta nóg)
        elif a != prev_a:
            cost += abs(a - prev_a) * 10 * COST_LEG
        cost += FIN_RATE * 10 * a / 252
        r = 5 * a * u[t] - cost
        ret[t] = r
        eq *= 1 + r
        peak = max(peak, eq)
        prev_a = a
    return ret


def pkill(ret, horizon_days):
    """Udział okien (start co 5 sesji) z trafieniem kill −25% od kroczącego szczytu okna."""
    n = len(ret); hits = 0; cnt = 0
    for s in range(0, n - horizon_days, 5):
        eq = np.cumprod(1 + ret[s:s + horizon_days])
        peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
        cnt += 1
        if (eq / peak < KILL).any():
            hits += 1
    return hits / cnt if cnt else np.nan, cnt


def path_stats(ret):
    eq = np.cumprod(1 + ret)
    peak = np.maximum.accumulate(eq)
    maxdd = (eq / peak - 1).min()
    wk = []
    for s in range(0, len(ret) - 5 + 1, 5):
        wk.append(np.prod(1 + ret[s:s + 5]) - 1)
    wk = np.array(wk) * 100
    return dict(end=round(eq[-1], 3), maxdd=round(maxdd * 100, 1), sd_week=round(wk.std(ddof=1), 2),
                mean_week=round(wk.mean(), 3), worst_week=round(wk.min(), 1), sd_day=round(ret.std(ddof=1) * 100, 2))


# ---------------------------------------------------------------- nakładka
def overlay_cost(ctx, key, nrep=50):
    legs = ctx['legs'][key]; EX = ctx['EX']; pools = ctx['pools']
    deltas = []
    per_week_sd = []
    for w in range(len(legs)):
        if legs[w] is None or pools[w] is None:
            continue
        L, S = legs[w]
        top, bot = pools[w]
        altL = [i for i in top if i not in L and i not in S][:10]
        altS = [i for i in bot if i not in L and i not in S][:10]
        if not altL or not altS:
            continue
        base = EX[w, L].mean() - EX[w, S].mean()
        dl = []
        for _ in range(nrep):
            cl = rng.choice(altL); cs = rng.choice(altS)
            nl = list(L[:-1]) + [cl]; ns = list(S[1:]) + [cs]   # wymiana nogi marginalnej (5.) na każdej stronie
            dl.append(((EX[w, nl].mean() - EX[w, ns].mean()) - base) * 100)
        dl = np.array(dl)
        deltas.append(dl.mean()); per_week_sd.append(dl.std())
    deltas = np.array(deltas)
    return dict(n_weeks=len(deltas), mean=round(deltas.mean(), 3), sd=round(deltas.std(ddof=1), 3),
                sd_within_week=round(float(np.mean(per_week_sd)), 3),
                weeks_for_t2_at_0p3=int(round((2 * deltas.std(ddof=1) / 0.3) ** 2)),
                weeks_for_t2_at_0p5=int(round((2 * deltas.std(ddof=1) / 0.5) ** 2)),
                weeks_for_t2_at_1p0=int(round((2 * deltas.std(ddof=1) / 1.0) ** 2)))


# ---------------------------------------------------------------- stop 20% bez reopen
def stop_cost(ctx, key, thr=0.20):
    legs = ctx['legs'][key]; P = None
    R = ctx['R']; D0, D5 = ctx['D0'], ctx['D5']
    sigma_mode = (thr == 'sigma')
    base, stopped = [], []
    nstop = 0
    for w in range(len(D0)):
        if legs[w] is None:
            continue
        L, S = legs[w]
        legsall = list(L) + list(S)
        sgn = np.array([1] * len(L) + [-1] * len(S))
        cum = np.ones(len(legsall))
        alive = np.ones(len(legsall), dtype=bool)
        if sigma_mode:
            s60 = np.nanstd(R[D0[w] - SIG_WIN + 1:D0[w] + 1][:, legsall], axis=0)
            thr_leg = np.clip(2.0 * s60 * math.sqrt(5), 0.08, 0.20)
        else:
            thr_leg = np.full(len(legsall), thr)
        tot_base = np.zeros(len(legsall)); tot_stop = np.zeros(len(legsall))
        for t in range(D0[w] + 1, D5[w] + 1):
            r = R[t, legsall]
            r = np.where(np.isnan(r), 0.0, r)
            tot_base += r * sgn
            tot_stop += np.where(alive, r * sgn, 0.0)
            cum *= 1 + r * sgn
            newly = alive & (cum - 1 <= -thr_leg)
            nstop += newly.sum()
            alive &= ~newly
        base.append((tot_base[:5].mean() - (-tot_base[5:]).mean() * -1) * 100 if False else (tot_base[:5].mean() + tot_base[5:].mean()) * 100)
        stopped.append((tot_stop[:5].mean() + tot_stop[5:].mean()) * 100)
    base, stopped = np.array(base), np.array(stopped)
    d = stopped - base
    return dict(n=len(d), n_stops=int(nstop), delta_mean=round(d.mean(), 3), delta_t=round(d.mean() / d.std(ddof=1) * math.sqrt(len(d)), 2),
                sd_base=round(base.std(ddof=1), 2), sd_stop=round(stopped.std(ddof=1), 2),
                p5_base=round(np.percentile(base, 5), 2), p5_stop=round(np.percentile(stopped, 5), 2),
                worst_base=round(base.min(), 2), worst_stop=round(stopped.min(), 2))


# ---------------------------------------------------------------- main
def main():
    D0, D5 = windows()
    res = {}
    md = ['# projektA_bt — wyniki (harness C1, okna piątek→piątek, 5L/5S, gross 2)', '']
    serie = {}
    for pit in (True, False):
        P, names, jarr, larr = build(pit)
        tag = 'PIT' if pit else 'DZIS'
        ctx = construct(P, names, jarr, larr, D0, D5, tag)
        st = pd.DataFrame(ctx['stats'])
        res[tag] = {'okna': int(len(st)), 'uniwersum_sr': round(float(st['univ'].mean()), 1),
                    'veto_sigma_sr_na_tydz': round(float(st['n_veto_sigma'].mean()), 2),
                    'veto_short_K13_sr_na_tydz': round(float(st['n_veto_short'].mean()), 2),
                    'D_wymiany_sr': round(float(st['swaps'].mean()), 2), 'D_identyczne_z_A_udzial': round(float(st['A_eq_D'].mean()), 3),
                    'bsox_A_sr': round(float(st['bsox_A'].mean()), 3), 'bsox_A_abs_sr': round(float(st['bsox_A'].abs().mean()), 3),
                    'bsox_D_abs_sr': round(float(st['bsox_D'].abs().mean()), 3),
                    'bdef_A_abs_sr': round(float(st['bdef_A'].abs().mean()), 3), 'bdef_D_abs_sr': round(float(st['bdef_D'].abs().mean()), 3),
                    'konstrukcje': {}}
        md += [f'## Uniwersum {tag}: {len(st)} okien, śr. {st["univ"].mean():.1f} spółek; veto σ śr. {st["n_veto_sigma"].mean():.2f}/tydz., '
               f'veto K13 śr. {st["n_veto_short"].mean():.2f}/tydz.; D: śr. {st["swaps"].mean():.2f} wymian, D=A w {st["A_eq_D"].mean()*100:.0f}% okien; '
               f'|b_SOX net| ex ante A {st["bsox_A"].abs().mean():.2f} → D {st["bsox_D"].abs().mean():.2f}, |b_DEF| A {st["bdef_A"].abs().mean():.2f} → D {st["bdef_D"].abs().mean():.2f}', '',
               '| konstrukcja | n | brutto | σ | t | Sharpe | hit | p5 | najgorszy | maxDD pp | netto | t netto | obrót nóg/tydz. | b_SOX zreal. | b_DEF zreal. | R² |',
               '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for key in ('A0', 'A_S1', 'A_K13', 'A', 'D'):
            sp, net, turn = weekly_series(ctx, key)
            m, mn = metrics(sp), metrics(net)
            fl = factor_load(ctx, sp)
            res[tag]['konstrukcje'][key] = dict(brutto=m, netto=mn, obrot=round(float(np.nanmean(turn[~np.isnan(sp)])), 2), czynniki=fl)
            serie[f'{tag}_{key}_brutto'] = sp; serie[f'{tag}_{key}_netto'] = net
            md.append(f'| {key} | {m["n"]} | {m["mean"]:+.2f} | {m["sd"]:.2f} | {m["t"]:.2f} | {m["sharpe"]:.2f} | {m["hit"]*100:.0f}% | {m["p5"]:+.1f} | {m["worst"]:+.1f} | {m["maxdd_pp"]:.0f} | {mn["mean"]:+.2f} | {mn["t"]:.2f} | {np.nanmean(turn[~np.isnan(sp)]):.2f} | {fl["b_sox"]:+.2f} | {fl["b_def"]:+.2f} | {fl["r2"]:.2f} |')
        # różnica D − A sparowana
        spA, _, _ = weekly_series(ctx, 'A'); spD, _, _ = weekly_series(ctx, 'D')
        d = spD - spA; m_ = ~np.isnan(d)
        dm = metrics(d)
        var_ratio = np.nanvar(spD, ddof=1) / np.nanvar(spA, ddof=1)
        res[tag]['D_minus_A'] = dict(delta=dm, var_ratio=round(float(var_ratio), 3))
        # tygodnie SOX−NDX < −3 pp
        fs = np.array([np.nansum(F_SOX_D[a + 1:b + 1]) for a, b in zip(D0, D5)]) * 100
        bad = (fs < -3) & m_
        res[tag]['tyg_SOX_lt_m3'] = dict(n=int(bad.sum()), A=round(float(np.nanmean(spA[bad])), 2), D=round(float(np.nanmean(spD[bad])), 2))
        md += ['', f'D − A (sparowane): Δ śr. {dm["mean"]:+.2f} p.p./tydz. (t {dm["t"]:.2f}), σ_D/σ_A = {math.sqrt(var_ratio):.3f}; '
               f'tygodnie z SOX−NDX < −3 p.p. (n={bad.sum()}): A {np.nanmean(spA[bad]):+.2f}, D {np.nanmean(spD[bad]):+.2f} p.p.', '']
        # lata
        yrs = pd.DatetimeIndex(dates[D0]).year
        md += ['| rok | n | A brutto | D brutto | A netto | D netto |', '|---|---|---|---|---|---|']
        _, netA, _ = weekly_series(ctx, 'A'); _, netD, _ = weekly_series(ctx, 'D')
        res[tag]['lata'] = {}
        for y in sorted(set(yrs)):
            mm = (yrs == y) & m_
            if mm.sum() == 0:
                continue
            res[tag]['lata'][int(y)] = dict(n=int(mm.sum()), A=round(float(np.nanmean(spA[mm])), 2), D=round(float(np.nanmean(spD[mm])), 2),
                                            A_net=round(float(np.nanmean(netA[mm])), 2), D_net=round(float(np.nanmean(netD[mm])), 2))
            md.append(f'| {y} | {mm.sum()} | {np.nanmean(spA[mm]):+.2f} | {np.nanmean(spD[mm]):+.2f} | {np.nanmean(netA[mm]):+.2f} | {np.nanmean(netD[mm]):+.2f} |')
        md.append('')
        if pit:
            # ---- sizing na PIT dla A i D
            res[tag]['sizing'] = {}
            md += ['### Sizing (ścieżka dzienna, koszty: 0,10%/zmieniona noga i zmiana skali, finansowanie 6%/rok × gross)', '',
                   '| konstrukcja | polityka | alfa | ALLOC śr. | σ dz. kap. | σ tyg. kap. | śr. tyg. | najgorszy tyg. | maxDD | kapitał końc. | P(kill 12 tyg.) | P(kill 52 tyg.) |',
                   '|---|---|---|---|---|---|---|---|---|---|---|---|']
            for key in ('A', 'D'):
                days_, unit, wof, s60, ch = daily_unit(ctx, key)
                res[tag]['sizing'][key] = {}
                for pol, soft in (('fixed_0.24', False), ('fixed_0.12', False), ('fixed_0.08', False), ('vt', False), ('vt', True)):
                    for demean in (False, True):
                        ret = simulate(unit, s60, ch, pol, soft=soft, demean=demean)
                        ps = path_stats(ret)
                        pk12, c12 = pkill(ret, 60); pk52, c52 = pkill(ret, 260)
                        a_eff = alloc_policy(pol, s60)
                        label = pol + ('+soft' if soft else '')
                        rec = dict(alloc_sr=round(float(a_eff.mean()), 4), alloc_min=round(float(a_eff.min()), 3), alloc_max=round(float(a_eff.max()), 3),
                                   **ps, pkill12=round(pk12, 3), pkill52=round(pk52, 3), okna12=c12, okna52=c52)
                        res[tag]['sizing'][key][f'{label}|{"alfa0" if demean else "insample"}'] = rec
                        md.append(f'| {key} | {label} | {"0" if demean else "in-sample"} | {a_eff.mean():.3f} | {ps["sd_day"]:.2f}% | {ps["sd_week"]:.2f}% | {ps["mean_week"]:+.2f}% | {ps["worst_week"]:+.1f}% | {ps["maxdd"]:.1f}% | {ps["end"]:.2f} | {pk12*100:.1f}% | {pk52*100:.1f}% |')
                # rozkład ALLOC vol-target
                a_vt = alloc_policy('vt', s60)
                wk_a = pd.Series(a_vt).groupby(wof).first()
                res[tag]['sizing'][key]['vt_alloc_rozklad'] = dict(p5=round(float(wk_a.quantile(0.05)), 3), mediana=round(float(wk_a.median()), 3), p95=round(float(wk_a.quantile(0.95)), 3),
                                                                 udzial_cap_min=round(float((wk_a <= ALLOC_MIN + 1e-9).mean()), 3), udzial_cap_max=round(float((wk_a >= ALLOC_MAX - 1e-9).mean()), 3),
                                                                 sigma60_unit_tyg_pp_mediana=round(float(pd.Series(s60).groupby(wof).first().median() * math.sqrt(5) * 100), 2))
            md.append('')
            # ---- nakładka
            res[tag]['nakladka'] = {k: overlay_cost(ctx, k) for k in ('A', 'D')}
            md += ['### Nakładka: losowa wymiana nogi 5. na kandydata z rang 6–15 (jedna na stronę)', '']
            for k, v in res[tag]['nakladka'].items():
                md.append(f'- {k}: Δ spreadu śr. {v["mean"]:+.2f} p.p./tydz., σ Δ między tygodniami {v["sd"]:.2f} p.p. (σ wewnątrz tygodnia {v["sd_within_week"]:.2f}); '
                          f'tygodni do t=2 przy prawdziwej przewadze nakładki +0,3 / +0,5 / +1,0 p.p.: {v["weeks_for_t2_at_0p3"]} / {v["weeks_for_t2_at_0p5"]} / {v["weeks_for_t2_at_1p0"]}')
            md.append('')
            # ---- stop 20%
            res[tag]['stop20'] = {k: stop_cost(ctx, k, 0.20) for k in ('A', 'D')}
            res[tag]['stop10'] = {k: stop_cost(ctx, k, 0.10) for k in ('A', 'D')}
            res[tag]['stop15'] = {k: stop_cost(ctx, k, 0.15) for k in ('A', 'D')}
            res[tag]['stopsigma'] = {k: stop_cost(ctx, k, 'sigma') for k in ('A', 'D')}
            md += ['### Stop od wejścia (zamknięcie D0), bez reopen, na zamknięciach dziennych — Δ vs brak stopu (p.p./tydz., brutto)', '',
                   '| konstrukcja | próg | stopów | Δ śr. | t | σ bez / ze stopem | p5 bez / ze | najgorszy bez / ze |', '|---|---|---|---|---|---|---|---|']
            for thr in ('stop10', 'stop15', 'stop20', 'stopsigma'):
                for k, v in res[tag][thr].items():
                    md.append(f'| {k} | {thr[4:]} | {v["n_stops"]} | {v["delta_mean"]:+.3f} | {v["delta_t"]:.2f} | {v["sd_base"]:.2f} / {v["sd_stop"]:.2f} | {v["p5_base"]:+.1f} / {v["p5_stop"]:+.1f} | {v["worst_base"]:+.1f} / {v["worst_stop"]:+.1f} |')
            md.append('')
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=float)
    pd.DataFrame({'d0': [str(dates[i].date()) for i in D0], **serie}).to_csv(OUT_SERIE, index=False)
    print('\n'.join(md))


if __name__ == '__main__':
    main()
