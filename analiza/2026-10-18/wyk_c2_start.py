"""(c, uzupełnienie) P(kill) w 1, 5, 10, 20 sesji przy starcie z obsunięcia −23,7% (stan 17.10: ~1,7% nad progiem 0,75×szczyt),
dla ALLOC 0,06…0,24; pula = koszyki W1–W7 (500 sesji), zwroty wyśrodkowane (zerowa przewaga), blok 5.
Uwaga: W8 ma inny profil (long mega-cap/defensywa, short wzrost) — pula W1–W7 jest przybliżeniem „koszyka tego typu”."""
import random, statistics as st
from wyk_common import *
random.seed(7)
pool = []
for w, k in KOSZYKI.items():
    if w == "W8": continue
    i1 = di(k["d0"]); s = []
    for i in range(i1 - 499, i1 + 1):
        if all(PX[t][i] and PX[t][i-1] for t in k["long"] + k["short"]):
            s.append(sum(PX[t][i]/PX[t][i-1]-1 for t in k["long"]) - sum(PX[t][i]/PX[t][i-1]-1 for t in k["short"]))
    pool.append(s)
# W8 koszyk własny profil: 500 sesji
k = KOSZYKI["W8"]; i1 = di(k["d0"]); s8 = []
for i in range(i1 - 499, i1 + 1):
    if all(PX[t][i] and PX[t][i-1] for t in k["long"] + k["short"]):
        s8.append(sum(PX[t][i]/PX[t][i-1]-1 for t in k["long"]) - sum(PX[t][i]/PX[t][i-1]-1 for t in k["short"]))
print(f"W8 (GOOGL GILD MSFT QCOM ADP / AXON DASH ALNY APP FER): σ dzienna jednostkowa {100*st.stdev(s8):.2f}% (×0,24 = {100*0.24*st.stdev(s8):.2f}%/d), śr {100*st.mean(s8):+.3f}%/d, n={len(s8)}")
print(f"W1–W7 pula: σ {100*st.stdev([x for s in pool for x in s]):.2f}%")

def paths(series_list, H, N, block=5):
    out = []
    for _ in range(N):
        s = random.choice(series_list); m = st.mean(s); p = []
        while len(p) < H:
            j = random.randrange(0, len(s) - block); p.extend(x - m for x in s[j:j+block])
        out.append(p[:H])
    return out

def pk(paths_, alloc, start_dd, H):
    hits = 0
    for p in paths_:
        eq = 1 - start_dd; peak = 1.0
        for r in p[:H]:
            eq *= 1 + alloc * r; peak = max(peak, eq)
            if eq <= 0.75 * peak: hits += 1; break
    return hits / len(paths_)

N = 20000
for label, pl in (("pula W1–W7", pool), ("profil W8", [s8])):
    P = paths(pl, 20, N)
    print(f"\n-- start −23,7% od szczytu (~1,7% nad progiem), {label} --")
    print(f"{'ALLOC':>6}" + "".join(f"{'P(kill ≤'+str(h)+' ses.)':>18}" for h in (1, 5, 10, 20)))
    for a in (0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.24):
        print(f"{a:6.2f}" + "".join(f"{100*pk(P, a, 0.237, h):17.1f}%" for h in (1, 5, 10, 20)))
