#!/usr/bin/env python3
"""
projektA_boot.py — bootstrap blokowy P(kill −25% od kroczącego szczytu) dla polityk sizingu
(konstrukcja A na uniwersum PIT z projektA_bt.py). Blok = 4 kolejne tygodnie (dni + σ60 ex ante +
zmiany nóg razem, żeby zachować związek prognozy σ z realizacją). 2000 ścieżek × 12 i 52 tygodnie.
Alfa: 0 (demean dziennego spreadu jednostkowego), +0,3 p.p./tydz. (realistyczne PIT netto wg C1),
in-sample. Polityki: stałe 0,24/0,12/0,08, vol-target, vol-target + próg miękki −10% (×0,5 do −5%).
Dodatkowo: start z poduszką ~1,7% (stan 18.10) dla W8-podobnej σ — porównanie z C9.
Wyjście: projektA_boot_out.md, projektA_boot_wyniki.json. Bez liczb z rachunku.
"""
import json
import math
import numpy as np
import pandas as pd
import projektA_bt as B

OUT_MD = f'{B.BASE}/analiza/projektA_boot_out.md'
OUT_JSON = f'{B.BASE}/analiza/projektA_boot_wyniki.json'
NPATH = 2000
BLOCK = 4
rng = np.random.default_rng(7)


def weeks_data(ctx, key):
    days, unit, wof, s60, ch = B.daily_unit(ctx, key)
    weeks = []
    for w in sorted(set(wof)):
        m = wof == w
        weeks.append((unit[m], s60[m], ch[m]))
    return weeks


def sim_path(weeks_sel, policy, soft, alfa_day):
    unit = np.concatenate([w[0] for w in weeks_sel]) + alfa_day
    s60 = np.concatenate([w[1] for w in weeks_sel])
    ch = np.concatenate([w[2] for w in weeks_sel])
    ch = ch.copy(); ch[0] = 10
    return B.simulate(unit, s60, ch, policy, soft=soft, demean=False)


def run(weeks, horizon_w, policy, soft, alfa_pp_week, start_dd=0.0):
    """start_dd: startowe obsunięcie od szczytu (np. 0.2375 = kapitał ~76% szczytu)."""
    n = len(weeks)
    alfa_day = alfa_pp_week / 100 / 5
    kills = 0; ends = []; maxdds = []
    for _ in range(NPATH):
        sel = []
        while len(sel) < horizon_w:
            s = rng.integers(0, n - BLOCK)
            sel.extend(weeks[s:s + BLOCK])
        sel = sel[:horizon_w]
        ret = sim_path(sel, policy, soft, alfa_day)
        eq = np.cumprod(1 + ret) * (1 - start_dd)
        peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
        killed = (eq / peak < B.KILL).any()
        kills += killed
        ends.append(eq[-1] / (1 - start_dd))
        maxdds.append((eq / peak - 1).min())
    ends = np.array(ends); maxdds = np.array(maxdds)
    return dict(pkill=round(kills / NPATH, 3), end_med=round(float(np.median(ends)), 3), end_p5=round(float(np.percentile(ends, 5)), 3),
                end_p95=round(float(np.percentile(ends, 95)), 3), maxdd_med=round(float(np.median(maxdds)) * 100, 1), maxdd_p95=round(float(np.percentile(maxdds, 5)) * 100, 1))


def main():
    D0, D5 = B.windows()
    P, names, jarr, larr = B.build(True)
    ctx = B.construct(P, names, jarr, larr, D0, D5, 'PIT')
    weeks = weeks_data(ctx, 'A')
    # demean: odejmujemy średnią dzienną jednostkową (alfa in-sample) → scenariusz alfa 0 = alfa_pp_week = −mean
    unit_all = np.concatenate([w[0] for w in weeks])
    mean_pp_week = float(unit_all.mean() * 5 * 100)
    res = {'n_tygodni': len(weeks), 'srednia_insample_pp_tydz': round(mean_pp_week, 3), 'wyniki': {}}
    md = [f'# projektA_boot — bootstrap blokowy (blok {BLOCK} tyg., {NPATH} ścieżek), konstrukcja A, PIT; średnia in-sample {mean_pp_week:+.2f} p.p./tydz.', '',
          '| polityka | alfa (p.p./tydz.) | horyzont | P(kill) | kapitał końc. mediana | p5 | p95 | maxDD mediana | maxDD p95 |', '|---|---|---|---|---|---|---|---|---|']
    for pol, soft in (('fixed_0.24', False), ('fixed_0.12', False), ('fixed_0.08', False), ('vt', False), ('vt', True)):
        for alfa_label, alfa in (('0', -mean_pp_week), ('+0,3', 0.3 - mean_pp_week), ('in-sample', 0.0)):
            for hw in (12, 52):
                r = run(weeks, hw, pol, soft, alfa)
                key = f'{pol}{"+soft" if soft else ""}|alfa{alfa_label}|{hw}'
                res['wyniki'][key] = r
                md.append(f'| {pol}{"+soft" if soft else ""} | {alfa_label} | {hw} | {r["pkill"]*100:.1f}% | {r["end_med"]:.3f} | {r["end_p5"]:.3f} | {r["end_p95"]:.3f} | {r["maxdd_med"]:.1f}% | {r["maxdd_p95"]:.1f}% |')
    # start z poduszką ~1,7% (stan 18.10): 4 tygodnie
    md += ['', '## Start ~1,7% nad progiem (kapitał = ~76% szczytu), alfa 0, 4 tygodnie', '', '| polityka | P(kill 4 tyg.) |', '|---|---|']
    res['start_167'] = {}
    for pol, soft in (('fixed_0.24', False), ('fixed_0.12', False), ('fixed_0.08', False), ('fixed_0.04', False), ('vt', False), ('vt', True)):
        r = run(weeks, 4, pol, soft, -mean_pp_week, start_dd=0.2375)
        res['start_167'][pol + ('+soft' if soft else '')] = r['pkill']
        md.append(f'| {pol}{"+soft" if soft else ""} | {r["pkill"]*100:.0f}% |')
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('\n'.join(md))


if __name__ == '__main__':
    main()
