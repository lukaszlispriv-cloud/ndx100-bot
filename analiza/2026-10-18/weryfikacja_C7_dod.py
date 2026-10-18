#!/usr/bin/env python3 -I
"""C7 dodatek: czy bramka obcina ogon mocniej w koszykach o wysokiej σ ex ante (jak koszyki systemu,
σ 11 pp/tydz. vs 7 w proxy)? Podział tygodni momentum 6M wg σ60 ex ante dziennego spreadu koszyka
(60 sesji przed D0) na kwartyle; Δ protokołu (od D+1, lag0 i lag1) w każdym kwartylu, p5, min, maxDD."""
import json, math, sys
import numpy as np, pandas as pd
sys.argv = ["x"]
exec(open("/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C7.py").read().split("# ------------------------------------------------------------------ 1. symulacja tygodniowa")[0])
BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
df = pd.read_csv(f"{BASE}/analiza/weryfikacja_C7_serie.csv", parse_dates=["d0"]).set_index("d0")
rets = px[stocks].pct_change() * 100; rn = ndx.pct_change() * 100
sig = {}
for d0 in df.index:
    s = mom_signal(d0); s = s.sort_values(); Lg, Sh = list(s.index[-5:]), list(s.index[:5])
    i = pos[d0]; win = slice(i - 60, i)
    rl = rets[Lg].iloc[win].sub(rn.iloc[win], axis=0).mean(axis=1); rs = -rets[Sh].iloc[win].sub(rn.iloc[win], axis=0).mean(axis=1)
    sig[d0] = (rl + rs).std()
df["sig60"] = pd.Series(sig); df["q"] = pd.qcut(df.sig60, 4, labels=False)
L = []
def P(s=""): L.append(s); print(s)
def tail(x):
    x = np.asarray(x, float); cum = np.cumsum(x)
    return dict(n=len(x), mean=x.mean(), sd=x.std(ddof=1), p5=np.percentile(x, 5), min=x.min(), maxDD=(cum - np.maximum.accumulate(cum)).min())
P("## Dodatek: Δ protokołu wg kwartyla σ60 ex ante koszyka (od D+1)\n")
P("kwartyl σ60 (zakres pp/dz) | n | σ tyg. zreal. bazy | baza śr. | Δ lag0 | t(Δ) | Δ lag1 | t(Δ) | p5 baza→lag0→lag1 | min baza→lag0→lag1 | maxDD baza→lag0→lag1 | reakcje/tydz.")
P("|".join(["---"] * 12))
OUT = {}
for q in range(4):
    sub = df[df.q == q]
    d0_ = sub.D1_gate0 - sub.D1_base; d1_ = sub.D1_gate1 - sub.D1_base
    tb, t0, t1 = tail(sub.D1_base), tail(sub.D1_gate0), tail(sub.D1_gate1)
    OUT[q] = dict(n=len(sub), sig_lo=sub.sig60.min(), sig_hi=sub.sig60.max(), base=tb, lag0=t0, lag1=t1, d0=d0_.mean(), t0=d0_.mean()/d0_.std()*math.sqrt(len(sub)), d1=d1_.mean(), t1=d1_.mean()/d1_.std()*math.sqrt(len(sub)))
    P(f"Q{q+1} ({sub.sig60.min():.2f}–{sub.sig60.max():.2f}) | {len(sub)} | {tb['sd']:.2f} | {tb['mean']:+.2f} | {d0_.mean():+.3f} | {OUT[q]['t0']:+.2f} | {d1_.mean():+.3f} | {OUT[q]['t1']:+.2f} | {tb['p5']:.1f}→{t0['p5']:.1f}→{t1['p5']:.1f} | {tb['min']:.1f}→{t0['min']:.1f}→{t1['min']:.1f} | {tb['maxDD']:.1f}→{t0['maxDD']:.1f}→{t1['maxDD']:.1f} | {(sub.D1_nR+sub.D1_nC).mean():.2f}")
# σ60 koszyków systemu dla odniesienia (W4–W7 wg ryzyko-i-sizing: σ_d jednostkowa 4,4–6,3 %/d przy 0,24 → spread dz. ≈ σ_d/1,2)
P(f"\nOdniesienie: σ60 ex ante tygodni proxy mediana {df.sig60.median():.2f} pp/dz., p90 {df.sig60.quantile(.9):.2f}, max {df.sig60.max():.2f}; koszyki systemu W4–W7 wg ryzyko-i-sizing.md: σ_d kapitału 4,4–6,3 % przy ALLOC 0,24 ≈ {4.4/1.2:.1f}–{6.3/1.2:.1f} pp/dz. spreadu, czyli Q4 i powyżej.")
# tygodnie z zrealizowaną stratą bazy ≤ −10 pp (ogon „typu W6/W7”)
sub = df[df.D1_base <= -10]
P(f"\nTygodnie z bazą ≤ −10 pp (n={len(sub)}, śr. {sub.D1_base.mean():.2f}): Δ lag0 {(sub.D1_gate0-sub.D1_base).mean():+.2f} pp (pomógł w {((sub.D1_gate0-sub.D1_base)>0).mean():.0%}), Δ lag1 {(sub.D1_gate1-sub.D1_base).mean():+.2f}; najgorszy tydzień bazy {df.D1_base.min():.2f} → lag0 {df.loc[df.D1_base.idxmin(),'D1_gate0']:.2f} / lag1 {df.loc[df.D1_base.idxmin(),'D1_gate1']:.2f}.")
OUT["ogon_le_-10"] = dict(n=len(sub), base=sub.D1_base.mean(), d0=(sub.D1_gate0-sub.D1_base).mean(), d1=(sub.D1_gate1-sub.D1_base).mean(), help0=((sub.D1_gate0-sub.D1_base)>0).mean())
# ile razy protokół ZWIĘKSZYŁ stratę o >2 pp (odbicie po cięciu) vs zmniejszył o >2 pp
d = df.D1_gate0 - df.D1_base
P(f"Rozkład Δ lag0 (wszystkie tygodnie): Δ > +2 pp w {(d>2).sum()} tyg., Δ < −2 pp w {(d<-2).sum()} tyg.; max Δ {d.max():+.2f} ({d.idxmax().date()}), min Δ {d.min():+.2f} ({d.idxmin().date()}).")
OUT["delta_rozklad"] = dict(gt2=int((d>2).sum()), lt_m2=int((d<-2).sum()), max=d.max(), min=d.min())
json.dump(OUT, open(f"{BASE}/analiza/weryfikacja_C7_dod_wyniki.json", "w"), indent=1, default=float)
open(f"{BASE}/analiza/weryfikacja_C7_dod_out.md", "w").write("\n".join(L))
