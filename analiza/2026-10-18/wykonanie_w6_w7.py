"""Seria „jak rachunek” dla W6 i W7: od D0 vs od faktycznych wejść (fills) vs ze stopami i ponownymi otwarciami.

Źródła wejść/stopów: koszyki_historia.json → zdarzenia_signals (39 stanów fills) oraz reports/puls-2026-10-13..16.html,
reports/raport-2026-W8.html. Poziom stopu = −10 % od poziomu brokera (STOP_LOSS_PCT, app.py::stopy_bezpieczenstwa);
poziom brokera przyjęty = cena z fills (dla MRVL puls 15.10 podaje 267,53 vs fills 273,80 — użyto 267,53).
Egzekucja stopu przyjęta DOKŁADNIE na poziomie −10 % (bot wykonuje po mid w biegu 13:45/17:05 UTC — faktyczna cena
mogła być niższa; to przybliżenie zaznaczone w notatce). Pozycje otwierane 24 % kapitału na nogę (ALLOC_PCT) —
wynik rachunku ≈ 1,2 × spread (5 nóg × 24 % = 120 % na stronę).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_dekomp import *

dates, px = load_closes()
di = {d: i for i, d in enumerate(dates)}
P = lambda t, d: px[t][di[d]]

ALLOC = 0.24

def leg(t, side, segments, d0, dend, div=0.0):
    """segments: lista (cena_wej, cena_wyj) — kolejne odcinki trzymania; zwrot nogi = suma zwrotów odcinków
    (każdy odcinek od nowa na pełną wielkość nogi, jak robi bot). Zwraca dict z trzema seriami."""
    sgn = 1 if side == 'L' else -1
    r_d0 = sgn * ((P(t, dend) + div) / P(t, d0) - 1)
    r_acc = sum(sgn * ((b + (div if j == len(segments) - 1 else 0)) / a - 1) for j, (a, b) in enumerate(segments))
    # hold od pierwszego wejścia bez stopów
    r_hold = sgn * ((P(t, dend) + div) / segments[0][0] - 1)
    return dict(t=t, side=side, r_d0=r_d0, r_hold=r_hold, r_acc=r_acc)

out = {}
# ---------------------------------------------------------------- W6: D0 2.10 → 9.10; rotacja 5.10 13:45 UTC
# Odziedziczone (na rachunku już w D0, trzymane przez rotację): MU, AMD, TER (L), APP, NFLX, CMCSA, SBUX (S) → wejście = D0.
# (6.10 bot zamknął i otworzył je ponownie przy wyrównaniu — ścieżka P&L ciągła, zmiana tylko ceny odniesienia.)
# Nowe 5.10 (fills): LITE 1088,08 BUY; AMAT 535,82 BUY; PAYX 98,87 SELL.
d0, de = '2026-10-02', '2026-10-09'
W6 = [
    leg('MU', 'L', [(P('MU', d0), P('MU', de))], d0, de),
    leg('LITE', 'L', [(1088.08, P('LITE', de))], d0, de),
    leg('TER', 'L', [(P('TER', d0), P('TER', de))], d0, de),
    leg('AMAT', 'L', [(535.82, P('AMAT', de))], d0, de),
    leg('AMD', 'L', [(P('AMD', d0), P('AMD', de))], d0, de),
    leg('APP', 'S', [(P('APP', d0), P('APP', de))], d0, de),
    leg('NFLX', 'S', [(P('NFLX', d0), P('NFLX', de))], d0, de),
    leg('PAYX', 'S', [(98.87, P('PAYX', de))], d0, de),
    leg('CMCSA', 'S', [(P('CMCSA', d0), P('CMCSA', de))], d0, de, div=0.33),
    leg('SBUX', 'S', [(P('SBUX', d0), P('SBUX', de))], d0, de),
]
# ---------------------------------------------------------------- W7: D0 9.10 → 16.10; rotacja 12.10 13:45 UTC
# Odziedziczone: MU (L; poziom brokera 1063,70 z 6.10), LITE (L; 1088,08 z 5.10), CMCSA/SBUX/APP (S) → wejście = D0 dla ścieżki.
# Nowe 12.10: MRVL 273,80 (broker 267,53), PANW 411,82, CSCO 116,47 BUY; PEP 126,91, TMUS 152,79 SELL.
# Stopy: MU 13.10 13:45 UTC (od 1063,70 → 957,33), ponowne otwarcie 17:05 po 935,73;
#        LITE 13.10 17:05 UTC (od 1088,08 → 979,27), CLOSE 14.10 — bez ponownego otwarcia;
#        MRVL 15.10 13:45 UTC (od 267,53 → 240,78), ponowne otwarcie 17:05 po 235,93;
#        PANW 16.10 13:45 UTC (od 411,82 → 370,64), ponowne otwarcie 17:05 po 341,71 (REDUCE 16.10 → połowa wielkości).
d0, de = '2026-10-09', '2026-10-16'
W7 = [
    leg('MU', 'L', [(P('MU', d0), 1063.70 * 0.9), (935.73, P('MU', de))], d0, de, div=0.15),
    leg('LITE', 'L', [(P('LITE', d0), 1088.08 * 0.9)], d0, de),
    leg('MRVL', 'L', [(273.80, 267.53 * 0.9), (235.93, P('MRVL', de))], d0, de),
    leg('PANW', 'L', [(411.82, 411.82 * 0.9), (341.71, P('PANW', de))], d0, de),
    leg('CSCO', 'L', [(116.47, P('CSCO', de))], d0, de),
    leg('CMCSA', 'S', [(P('CMCSA', d0), P('CMCSA', de))], d0, de),
    leg('SBUX', 'S', [(P('SBUX', d0), P('SBUX', de))], d0, de),
    leg('PEP', 'S', [(126.91, P('PEP', de))], d0, de),
    leg('TMUS', 'S', [(152.79, P('TMUS', de))], d0, de),
    leg('APP', 'S', [(P('APP', d0), P('APP', de))], d0, de),
]
# PANW: drugi odcinek na połowie wielkości (REDUCE) — korekta
for l in W7:
    if l['t'] == 'PANW':
        seg2 = (P('PANW', de) / 341.71 - 1)
        l['r_acc'] = (411.82 * 0.9 / 411.82 - 1) + 0.5 * seg2
        l['uwaga'] = 'drugi odcinek na 50 % wielkości (REDUCE 16.10)'

def summary(name, legs):
    L = [l for l in legs if l['side'] == 'L']; S = [l for l in legs if l['side'] == 'S']
    res = {}
    for k, lab in (('r_d0', 'od D0 (prognoza)'), ('r_hold', 'od faktycznych wejść, bez stopów'), ('r_acc', 'jak rachunek (wejścia + stopy + ponowne otwarcia)')):
        sp = mean([l[k] for l in L]) + mean([l[k] for l in S])
        res[k] = sp
        print(f"| {name} | {lab} | LONG śr. {mean([l[k] for l in L])*100:+.2f} | SHORT śr. {mean([l[k] for l in S])*100:+.2f} | spread {sp*100:+.2f} p.p. | ≈ wynik rachunku {sp*100*1.2:+.1f}% kapitału (×1,2) |")
    return res

print('# Seria od D0 vs od wejść vs „jak rachunek” (W6, W7)\n')
print('| tydz. | seria | LONG | SHORT | spread | ≈ rachunek |')
print('|---|---|---|---|---|---|')
r6 = summary('W6', W6); r7 = summary('W7', W7)
print()
print('## Nogi W7 — trzy serie (p.p. na nodze)\n')
print('| noga | kier. | od D0 | od wejścia bez stopu | jak rachunek | efekt stopu+ponownego otwarcia (rachunek − hold) | efekt opóźnienia wejścia (hold − D0) |')
print('|---|---|---|---|---|---|---|')
for l in W7:
    print(f"| {l['t']} | {l['side']} | {l['r_d0']*100:+.2f} | {l['r_hold']*100:+.2f} | {l['r_acc']*100:+.2f} | {(l['r_acc']-l['r_hold'])*100:+.2f} | {(l['r_hold']-l['r_d0'])*100:+.2f} |")
print('\n## Nogi W6 — trzy serie (p.p. na nodze)\n')
print('| noga | kier. | od D0 | od wejścia | efekt opóźnienia wejścia |')
print('|---|---|---|---|---|')
for l in W6:
    print(f"| {l['t']} | {l['side']} | {l['r_d0']*100:+.2f} | {l['r_hold']*100:+.2f} | {(l['r_hold']-l['r_d0'])*100:+.2f} |")

print('\n## Bilans wykonania (p.p. spreadu)')
for name, r in (('W6', r6), ('W7', r7)):
    print(f"- {name}: opóźnienie wejścia {(r['r_hold']-r['r_d0'])*100:+.2f} p.p.; stopy+ponowne otwarcia {(r['r_acc']-r['r_hold'])*100:+.2f} p.p.; razem wykonanie vs prognoza {(r['r_acc']-r['r_d0'])*100:+.2f} p.p. (history spread_fills_pp: W6 +3,88 / W7 −12,36 — te liczby NIE są serią rachunku)")

# Stopy: zrealizowana strata na stopie w % kapitału (ALLOC 0,24 × 10 %)
print(f"\nKażdy stop realizuje −10 % × ALLOC {ALLOC} = {-10*ALLOC:.1f} % kapitału; 4 stopy W7 (MU, LITE, MRVL, PANW) = {-4*10*ALLOC:.1f} % kapitału zrealizowane (bez uwzględnienia, że MU i MRVL/PANW zostały odkupione niżej).")

# Ścieżka rachunku 6.10 → 16.10 (szczyt kapitału wg zadania 6.10): W6 od zamknięcia 6.10 do 9.10 + W7 jak rachunek
d6 = '2026-10-06'; de6 = '2026-10-09'
part6 = []
for l in W6:
    sgn = 1 if l['side'] == 'L' else -1
    div = 0.33 if l['t'] == 'CMCSA' else 0.0
    part6.append((l['side'], sgn * ((P(l['t'], de6) + div) / P(l['t'], d6) - 1)))
sp6b = mean([r for s, r in part6 if s == 'L']) + mean([r for s, r in part6 if s == 'S'])
print(f"\nW6 od zamknięcia 6.10 do 9.10: spread {sp6b*100:+.2f} p.p. (≈ {sp6b*120:+.1f}% kapitału); W7 jak rachunek {r7['r_acc']*100:+.2f} p.p. (≈ {r7['r_acc']*120:+.1f}%); "
      f"złożone ≈ {((1+sp6b*1.2)*(1+r7['r_acc']*1.2)-1)*100:+.1f}% kapitału vs podane w zadaniu −23,7 % od szczytu 6.10→16.10 (różnica: taktyczne APOG/PENG/ERIC, koszty CFD, egzekucja stopów poniżej −10 %, wyrównania).")

json.dump({'W6': W6, 'W7': W7, 'spready': {'W6': r6, 'W7': r7}, 'W6_od_6_10': sp6b}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wykonanie_wyniki.json'), 'w'), indent=1)
