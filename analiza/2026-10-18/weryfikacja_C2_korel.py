import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weryfikacja_C2 as V
def pair_corr(rows):
    out = []; nn = 0
    for r in rows:
        w = V.WIN[r["i"]]; u, C = V.resid_matrix(w["d0"], list(w["sig"]))
        ix = {t: k for k, t in enumerate(u)}
        for l, s in zip(r["lo"], r["sh"]):
            if l in ix and s in ix:
                c = C[ix[l], ix[s]]
                if np.isnan(c): nn += 1
                else: out.append(c)
    return round(float(np.mean(out)), 3), round(float(np.median(out)), 3), len(out), nn
print("korelacja residuów (252 sesje ≤ D0) L–S w parze: b_pary", pair_corr(V.PAIRS), "| none (long_k, short_k)", pair_corr(V.NONE), "| a_branza", pair_corr(V.NEUT), "| PIT K=15", pair_corr(V.PAIRS_PIT))
# korelacja ex post (w oknie D0→D5) zwrotów nóg: wariancja spreadu = suma wariancji nóg − 2cov; policz śr. iloczyn odchyleń
def cov_term(rows):
    L=[];S=[]
    for r in rows:
        w=V.WIN[r["i"]]
        L.append(100*np.mean([w["fwd"][t]-w["r_ndx"] for t in r["lo"]])); S.append(100*np.mean([w["fwd"][t]-w["r_ndx"] for t in r["sh"]]))
    L=np.array(L);S=np.array(S)
    return dict(sd_L=round(L.std(ddof=1),2), sd_S=round(S.std(ddof=1),2), corr_LS=round(float(np.corrcoef(L,S)[0,1]),3), sd_spread=round((L-S).std(ddof=1),2))
print("dekompozycja σ spreadu (σ_L, σ_S, corr(L,S)): none", cov_term(V.NONE), "| b_pary", cov_term(V.PAIRS), "| a_branza", cov_term(V.NEUT), "| PIT K=15", cov_term(V.PAIRS_PIT))
