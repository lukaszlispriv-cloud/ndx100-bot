"""(c) Zmienność nóg i prawdopodobieństwo kill switcha.
1. σ60 dzienna nóg W6/W7 (60 zwrotów prostych c/c do D0), korelacje, σ portfela przy wagach ±ALLOC/nogę
   (σ_kapitału = sqrt(w' Σ w), w = +0,24 long / −0,24 short) — z macierzy kowariancji 60 sesji i z 250 sesji.
2. Zrealizowana σ dzienna "koszyka W7 jako rachunek" w oknie 12–16.10.
3. Bootstrap blokowy (blok 5 sesji) dziennych zwrotów KAPITAŁU dla koszyków tego typu:
   seria = dla każdego z 7 koszyków W1–W7 dzienny zwrot 0,24·Σlong − 0,24·Σshort na 500 ostatnich sesjach
   (ta sama konstrukcja: sprzęt AI long vs defensywy short), pula ≈ 3500 dni; usuwamy średnią (zerowa przewaga)
   albo zostawiamy. P(kill) = udział ścieżek 20 sesji (4 tyg.), w których kapitał spada ≥25% od kroczącego szczytu
   (start na szczycie) — dla ALLOC 0,10…0,24. Dodatkowo: start z obsunięciem −21% (stan 16.10 ≈ ~1,7% nad progiem).
"""
import random, statistics as st, math, json
from wyk_common import *

random.seed(20261018)
ALLOCS = [0.10, 0.12, 0.16, 0.20, 0.24]

def sigma60(t, d0, n=60):
    i = di(d0); r = daily_returns(t, i - n, i)
    return st.stdev(r), r

def cov(a, b):
    ma, mb = st.mean(a), st.mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (len(a) - 1)

def port_sigma(legs, d0, n, alloc):
    rets = {}
    for t, _ in legs:
        i = di(d0); r = daily_returns(t, i - n, i)
        rets[t] = r
    L = min(len(r) for r in rets.values())
    rets = {t: r[-L:] for t, r in rets.items()}
    w = {t: (alloc if s == "BUY" else -alloc) for t, s in legs}
    var = 0.0
    for t1 in rets:
        for t2 in rets:
            var += w[t1] * w[t2] * cov(rets[t1], rets[t2])
    # średnia korelacja par w long
    longs = [t for t, s in legs if s == "BUY"]
    cors = []
    for a in range(len(longs)):
        for b in range(a + 1, len(longs)):
            x, y = rets[longs[a]], rets[longs[b]]
            cors.append(cov(x, y) / (st.stdev(x) * st.stdev(y)))
    return math.sqrt(var), st.mean(cors), L

out = {}
for w in ("W6", "W7"):
    k = KOSZYKI[w]
    legs = [(t, "BUY") for t in k["long"]] + [(t, "SELL") for t in k["short"]]
    print(f"=== {w} (D0 {k['d0']}) σ60 dzienna nóg (%), 60 sesji do D0 ===")
    sig = {}
    for t, s in legs:
        sd, _ = sigma60(t, k["d0"]); sig[t] = sd
        print(f"  {t:6}{s:5}{100*sd:6.2f}%   σ5 = {100*sd*math.sqrt(5):5.2f}%   P(5-ses. ruch ≤ −10% | normal) ≈ {100*(0.5*math.erfc(0.10/(sd*math.sqrt(5))/math.sqrt(2))):.1f}%")
    print(f"  śr σ60 long {100*st.mean(sig[t] for t in k['long']):.2f}%, short {100*st.mean(sig[t] for t in k['short']):.2f}%")
    for n in (60, 250):
        ps, rho, L = port_sigma(legs, k["d0"], n, 0.24)
        print(f"  σ dzienna KAPITAŁU (ALLOC 0,24, kowariancja {L} sesji): {100*ps:.2f}%  → tygodniowa {100*ps*math.sqrt(5):.2f}%, 4-tyg. {100*ps*math.sqrt(20):.2f}%; śr. korelacja par LONG {rho:.2f}")
        out[f"{w}_sigma_port_{n}"] = ps
    # σ przy równych wagach sumujących się do tego samego gross, ale z „naiwną” niezależnością (dla porównania)
    naive = 0.24 * math.sqrt(sum(sig[t] ** 2 for t, _ in legs))
    print(f"  σ KAPITAŁU gdyby nogi były niezależne: {100*naive:.2f}% (różnica = koszt koncentracji czynnikowej)")

# 2. zrealizowane w W7
k = KOSZYKI["W7"]; i0, i1 = di("2026-10-09"), di("2026-10-16")
eq = []
for i in range(i0 + 1, i1 + 1):
    r = 0.0
    for t in k["long"]:  r += 0.24 * (PX[t][i] / PX[t][i - 1] - 1)
    for t in k["short"]: r -= 0.24 * (PX[t][i] / PX[t][i - 1] - 1)
    eq.append(r)
print(f"\nW7 zrealizowane dzienne zwroty kapitału (ALLOC 0,24, bez stopów/kosztów): {[round(100*x,2) for x in eq]}  suma {100*sum(eq):.2f}%, σ {100*st.stdev(eq):.2f}%")
k = KOSZYKI["W6"]; i0, i1 = di("2026-10-02"), di("2026-10-09"); eq6 = []
for i in range(i0 + 1, i1 + 1):
    r = 0.0
    for t in k["long"]:  r += 0.24 * (PX[t][i] / PX[t][i - 1] - 1)
    for t in k["short"]: r -= 0.24 * (PX[t][i] / PX[t][i - 1] - 1)
    eq6.append(r)
print(f"W6 zrealizowane: {[round(100*x,2) for x in eq6]}  suma {100*sum(eq6):.2f}%, σ {100*st.stdev(eq6):.2f}%")

# 3. bootstrap
N_HIST = 500
pool = []       # dzienne zwroty „portfela jednostkowego” (ALLOC=1): Σlong − Σshort
per_basket_sd = {}
for w, k in KOSZYKI.items():
    if w == "W8": continue
    i1 = di(k["d0"]); i0 = i1 - N_HIST
    series = []
    for i in range(i0 + 1, i1 + 1):
        ok = all(PX[t][i] and PX[t][i - 1] for t in k["long"] + k["short"])
        if not ok: continue
        r = sum(PX[t][i] / PX[t][i - 1] - 1 for t in k["long"]) - sum(PX[t][i] / PX[t][i - 1] - 1 for t in k["short"])
        series.append(r)
    per_basket_sd[w] = (st.mean(series), st.stdev(series), len(series))
    pool.append(series)
print("\n=== pula historyczna: koszyki W1–W7 na 500 sesjach do swojego D0 (jednostka = 1,0 na nogę) ===")
for w, (m, sd, n) in per_basket_sd.items():
    print(f"  {w}: śr {100*m:+.3f}%/d, σ {100*sd:.2f}%/d (×0,24 → σ kapitału {100*sd*0.24:.2f}%/d), n={n}")
flat = [x for s in pool for x in s]
mu_all, sd_all = st.mean(flat), st.stdev(flat)
print(f"  razem n={len(flat)}: śr {100*mu_all:+.3f}%/d, σ {100*sd_all:.2f}%/d; przy ALLOC 0,24 σ kapitału {100*0.24*sd_all:.2f}%/d, 4-tyg. {100*0.24*sd_all*math.sqrt(20):.1f}%")

def block_paths(series_list, horizon, n_paths, block=5, demean=True):
    paths = []
    for _ in range(n_paths):
        s = random.choice(series_list)
        m = st.mean(s) if demean else 0.0
        p = []
        while len(p) < horizon:
            j = random.randrange(0, len(s) - block)
            p.extend(x - m for x in s[j:j + block])
        paths.append(p[:horizon])
    return paths

def p_kill(paths, alloc, start_dd=0.0, kill=0.25):
    hits = 0
    for p in paths:
        peak = 1.0; eq = 1.0 - start_dd
        for r in p:
            eq *= (1 + alloc * r)
            peak = max(peak, eq)
            if eq <= peak * (1 - kill):
                hits += 1; break
    return hits / len(paths)

NP = 20000
print(f"\n=== bootstrap blokowy (blok 5), {NP} ścieżek, kill = −25% od kroczącego szczytu ===")
for demean in (True, False):
    paths20 = block_paths(pool, 20, NP, demean=demean)
    paths52 = block_paths(pool, 260, 5000, demean=demean)
    lab = "zerowa przewaga (zwroty wyśrodkowane)" if demean else "zwroty historyczne jak są (śr. z 2 lat)"
    print(f"-- {lab} --")
    print(f"{'ALLOC':>6}{'P(kill) 4 tyg. od szczytu':>28}{'P(kill) 4 tyg. start −21%':>28}{'P(kill) 52 tyg. od szczytu':>28}{'σ kap./d':>10}")
    for a in ALLOCS:
        print(f"{a:6.2f}{100*p_kill(paths20, a):27.1f}%{100*p_kill(paths20, a, start_dd=0.21):27.1f}%{100*p_kill(paths52, a):27.1f}%{100*a*sd_all:9.2f}%")
    out[f"bootstrap_demean_{demean}"] = {str(a): p_kill(paths20, a) for a in ALLOCS}

# wrażliwość: tylko koszyki W6/W7 (najbardziej skoncentrowane)
sub = [pool[5], pool[6]]
paths20 = block_paths(sub, 20, NP, demean=True)
print("\n-- tylko koszyki W6/W7 jako pula (zerowa przewaga) --")
for a in ALLOCS:
    print(f"ALLOC {a:.2f}: P(kill 4 tyg. od szczytu) {100*p_kill(paths20,a):.1f}%, start −21%: {100*p_kill(paths20,a,0.21):.1f}%")
json.dump(out, open("/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/wyk_c_wynik.json", "w"), indent=1)
