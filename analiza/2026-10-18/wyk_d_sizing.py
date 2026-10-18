"""(d/propozycje) Kontrfaktyczne warianty wielkości pozycji na W1–W7 (wynik „jak rachunek”: wejście = close pierwszej
sesji po D0, wyjście = close rozliczenia; % kapitału; bez kosztów, bez stopów o ile nie zaznaczono).
 A  stałe ALLOC 0,24 (stan obecny)
 B  stałe ALLOC 0,12 (stan sprzed 3.10)
 C  VOL-TARGET GROSS: alloc = 0,24 × min(1, SIGMA_TARGET/σ_port), σ_port z kowariancji 60 sesji do D0 przy ALLOC 0,24;
    SIGMA_TARGET = 1,5%/dzień kapitału (≈ 7% tyg., ≈ 14% / 4 tyg. → kill 25% ≈ 1,8σ 4-tyg.)
 D  DRAWDOWN-SCALE: alloc = 0,24 × max(0,25, 1 − 2·dd), dd = obsunięcie kapitału od szczytu na początku tygodnia
    (ścieżka kapitału liczona kolejno W1→W7 z wyników wariantu D)
 E  PARYTET ZMIENNOŚCI per noga: alloc_i = min(0,24, RISK/(2·σ60_i·√5)), RISK = 2% kapitału na nogę przy ruchu 2σ5
 F  C + twardy stop 10% od ceny tezy bez ponownego otwarcia (sprawdzany na zamknięciu)
"""
import math, statistics as st
from wyk_common import *

SIG_T = 0.015

def cov(a, b):
    ma, mb = st.mean(a), st.mean(b); return sum((x-ma)*(y-mb) for x, y in zip(a, b))/(len(a)-1)

def legs_of(k):
    return [(t, 1) for t in k["long"]] + [(t, -1) for t in k["short"]]

def sigma_port(k, alloc=0.24, n=60):
    i = di(k["d0"]); rets = {t: daily_returns(t, i-n, i) for t, _ in legs_of(k)}
    L = min(len(r) for r in rets.values()); rets = {t: r[-L:] for t, r in rets.items()}
    w = {t: s*alloc for t, s in legs_of(k)}
    return math.sqrt(sum(w[a]*w[b]*cov(rets[a], rets[b]) for a in rets for b in rets)), {t: st.stdev(r) for t, r in rets.items()}

def leg_pnl(t, s, i0, i1, stop=None):
    pr = [PX[t][i] for i in range(i0, i1+1) if PX[t][i]]
    ref = pr[0]
    if stop:
        for p in pr[1:]:
            if s*(p/ref-1) <= -stop: return -stop
    return s*(pr[-1]/ref-1)

res = {v: [] for v in "ABCDEF"}; eqD = 1.0; peakD = 1.0
print(f"{'W':4}{'σ_port60':>9}{'allocC':>8}{'allocD':>8}" + "".join(f"{v:>9}" for v in "ABCDEF"))
for w, k in KOSZYKI.items():
    if not k["settle"]: continue
    i0, i1 = di(k["entry"]), di(k["settle"])
    sp, sig = sigma_port(k)
    aC = 0.24*min(1, SIG_T/sp)
    dd = 1 - eqD/peakD; aD = 0.24*max(0.25, 1-2*dd)
    base = sum(leg_pnl(t, s, i0, i1) for t, s in legs_of(k))         # suma % pozycji (10 nóg)
    A = 0.24*base; B = 0.12*base; C = aC*base; D = aD*base
    E = sum(min(0.24, 0.02/(2*sig[t]*math.sqrt(5)))*leg_pnl(t, s, i0, i1) for t, s in legs_of(k))
    F = aC*sum(leg_pnl(t, s, i0, i1, stop=0.10) for t, s in legs_of(k))
    for v, x in zip("ABCDEF", (A, B, C, D, E, F)): res[v].append(100*x)
    eqD *= 1 + D; peakD = max(peakD, eqD)
    print(f"{w:4}{100*sp:8.2f}%{aC:8.3f}{aD:8.3f}" + "".join(f"{100*x:9.2f}" for x in (A, B, C, D, E, F)))
print(f"{'suma':4}{'':25}" + "".join(f"{sum(res[v]):9.2f}" for v in "ABCDEF"))
print(f"{'sd':4}{'':25}" + "".join(f"{st.stdev(res[v]):9.2f}" for v in "ABCDEF"))
print(f"{'W6+W7':4}{'':25}" + "".join(f"{res[v][-1]+res[v][-2]:9.2f}" for v in "ABCDEF"))
# ścieżka kapitału (iloczyn) i max obsunięcie
for v in "ABCDEF":
    eq = 1.0; pk = 1.0; mdd = 0.0
    for x in res[v]:
        eq *= 1 + x/100; pk = max(pk, eq); mdd = min(mdd, eq/pk-1)
    print(f"wariant {v}: kapitał końcowy {100*(eq-1):+.1f}%, max obsunięcie {100*mdd:.1f}%")
print("\nParytet zmienności (E) — wagi W7:", {t: round(min(0.24, 0.02/(2*s*math.sqrt(5))), 3) for t, s in sigma_port(KOSZYKI['W7'])[1].items()})
print("Uwaga lot: MU 0,1 akcji ≈ 10% kapitału przy ~900 USD/akcję i kapitale ≈ 0,9 × START_EQUITY — alloc < 0,10 dla MU/LITE jest niewykonalny (minimalna transakcja).")
