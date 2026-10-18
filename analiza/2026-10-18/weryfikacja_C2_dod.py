#!/usr/bin/env python3
"""weryfikacja_C2_dod.py — dopełnienie: klastry complete-linkage (zbalansowane), więcej K;
udział par z grup sektorowych (zlepki) vs industry; korelacja wewnątrz pary; Δ dla a_branza wg definicji."""
import json, math, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weryfikacja_C2 as V   # uruchamia T1–T7 ponownie (cache) — akceptowalne, ~2 min
B = V.B
OUT = os.path.join(B.OUT_DIR, "weryfikacja_C2_dod_out.txt")
f = open(OUT, "w")
def P_(*a):
    s = " ".join(str(x) for x in a); print(s); f.write(s + "\n"); f.flush()

# --- udział par z grup sektorowych vs industry (w taksonomii bazowej)
ind_names = {v[0] for v in V.ind.values()}; sec_names = {v[1] for v in V.ind.values()}
kind = Counter()
same_ind = []
for r in V.PAIRS:
    for l, s, g in zip(r["lo"], r["sh"], r["groups"]):
        kind["industry" if g in ind_names else "sector"] += 1
        same_ind.append(V.ind[l][0] == V.ind[s][0])
tot = sum(kind.values())
P_(f"b_pary: pary z grupy=industry {kind['industry']/tot:.2f}, z grupy=sector (zlepek) {kind['sector']/tot:.2f}; oba końce o tej samej industry TV: {np.mean(same_ind):.2f}")
sec_pairs = Counter((V.ind[l][0], V.ind[s][0]) for r in V.PAIRS for l, s, g in zip(r["lo"], r["sh"], r["groups"]) if g in sec_names)
P_("najczęstsze pary industry wewnątrz grup sektorowych:", sec_pairs.most_common(8))

# --- korelacja residuów dziennych (252 sesje ≤ D0) wewnątrz pary vs między losowymi long/short none
def pair_corr(rows):
    out = []
    for r in rows:
        w = V.WIN[r["i"]]; u, C = V.resid_matrix(w["d0"], list(w["sig"]))
        ix = {t: k for k, t in enumerate(u)}
        for l, s in zip(r["lo"], r["sh"]):
            if l in ix and s in ix: out.append(C[ix[l], ix[s]])
    return float(np.mean(out)), float(np.median(out))
P_(f"śr. korelacja residuów L–S wewnątrz pary: b_pary {pair_corr(V.PAIRS)} | none (long_k vs short_k) {pair_corr(V.NONE)} | pit K=15 {pair_corr(V.PAIRS_PIT)}")

# --- complete linkage
def complete_linkage(C, K):
    n = C.shape[0]; D = 1.0 - C; np.fill_diagonal(D, np.inf)
    clusters = {i: [i] for i in range(n)}; Dm = D.copy()
    while len(clusters) > K:
        keys = list(clusters); sub = Dm[np.ix_(keys, keys)]
        a, b = np.unravel_index(np.argmin(sub), sub.shape); ka, kb = keys[a], keys[b]
        new = clusters[ka] + clusters[kb]
        for kc in keys:
            if kc in (ka, kb): continue
            Dm[ka, kc] = Dm[kc, ka] = max(D[i, j] for i in new for j in clusters[kc])
        clusters[ka] = new; del clusters[kb]; Dm[kb, :] = np.inf; Dm[:, kb] = np.inf
    lab = {}
    for c, mem in enumerate(clusters.values()):
        for i in mem: lab[i] = f"C{c}"
    return lab

CACHE = {}
def grp_cl(i, sig, K, link):
    key = (i, K, link)
    if key not in CACHE:
        w = V.WIN[i]; u, C = V.resid_matrix(w["d0"], list(sig))
        lab = (complete_linkage if link == "complete" else V.avg_linkage)(C, K)
        g = {t: lab[k] for k, t in enumerate(u)}
        for t in sig: g.setdefault(t, "Pozostałe")
        gc = Counter(g.values())
        CACHE[key] = {t: (g[t] if gc[g[t]] >= 3 else "Pozostałe") for t in sig}
    return CACHE[key]

res = {}
P_("\n=== klastry point-in-time, complete linkage / average linkage z większym K ===")
for link, Ks in (("complete", (8, 12, 15, 20, 25)), ("average", (25, 30, 40))):
    for K in Ks:
        gf = lambda i, sig, K=K, link=link: grp_cl(i, sig, K, link)
        rp = V.run("pairs", gf); rn = V.run("neutral", gf)
        sp = V.stats(rp); sn = V.stats(rn); cp = V.compare(rp, V.NONE, nboot=1000); cn = V.compare(rn, V.NONE, nboot=1000)
        ng = np.mean([len(set(gf(i, V.WIN[i]["sig"]).values()) - {"Pozostałe"}) for i in range(len(V.WIN))])
        P_(f"{link:8s} K={K:2d} grup≥3 {ng:4.1f} | pairs śr {sp['mean']:.2f} σ {sp['sd']:.2f} t {sp['t']:.2f} Sh {sp['sharpe']:.2f} worst {sp['worst']:.1f} Δ {cp['d_mean']:+.2f} (t {cp['d_t']:.2f}) σ-ratio {cp['sigma_ratio']:.3f} | "
           f"neutral śr {sn['mean']:.2f} σ {sn['sd']:.2f} Sh {sn['sharpe']:.2f} Δ {cn['d_mean']:+.2f} (t {cn['d_t']:.2f}) σ-ratio {cn['sigma_ratio']:.3f}")
        res[f"{link}_{K}"] = dict(n_groups=float(ng), pairs=sp, neutral=sn, cmp_pairs=cp, cmp_neutral=cn)
json.dump(res, open(os.path.join(B.OUT_DIR, "weryfikacja_C2_dod_wyniki.json"), "w"), indent=1, default=float)

# --- zbiorczo: Δ i σ-ratio dla wszystkich taksonomii bez look-ahead (T3 + powyżej)
ds = [v["cmp_pairs"]["d_mean"] for v in res.values()] + [V.RES["T3"][k]["cmp_pairs"]["d_mean"] for k in V.RES["T3"]]
sr = [v["cmp_pairs"]["sigma_ratio"] for v in res.values()] + [V.RES["T3"][k]["cmp_pairs"]["sigma_ratio"] for k in V.RES["T3"]]
P_(f"\nPIT pairs, {len(ds)} warianty klastrowania: Δśr mediana {np.median(ds):+.2f} [min {min(ds):+.2f}, max {max(ds):+.2f}], σ-ratio mediana {np.median(sr):.3f} [{min(sr):.3f}, {max(sr):.3f}]")
ds2 = [v["cmp_neutral"]["d_mean"] for v in res.values()] + [V.RES["T3"][k]["cmp_neutral"]["d_mean"] for k in V.RES["T3"]]
sr2 = [v["cmp_neutral"]["sigma_ratio"] for v in res.values()] + [V.RES["T3"][k]["cmp_neutral"]["sigma_ratio"] for k in V.RES["T3"]]
P_(f"PIT neutral: Δśr mediana {np.median(ds2):+.2f} [{min(ds2):+.2f}, {max(ds2):+.2f}], σ-ratio mediana {np.median(sr2):.3f} [{min(sr2):.3f}, {max(sr2):.3f}]")
# TV definicje (T4) zbiorczo
t4p = [v["c"]["d_mean"] for k, v in V.RES["T4"].items() if k.endswith("|pairs")]
t4n = [v["c"]["d_mean"] for k, v in V.RES["T4"].items() if k.endswith("|neutral")]
P_(f"TV definicje grupy (6): pairs Δ {sorted(round(x,2) for x in t4p)} ; neutral Δ {sorted(round(x,2) for x in t4n)}")
P_(f"zapisano {OUT}")
