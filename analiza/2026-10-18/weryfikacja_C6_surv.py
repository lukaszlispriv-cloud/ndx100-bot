#!/usr/bin/env python3 -I
"""C6 — kontrola survivorship bias: uniwersum rozszerzone o 28 spółek usuniętych z NDX (dropped_closes.csv, wciąż notowane).
Powtarza przekrój (def. A, próg 0 / −4) i symulację portfela TOP5/BOTTOM5."""
import sys, json
import numpy as np, pandas as pd
DIR = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza"
sys.path.insert(0, DIR)
import weryfikacja_C6 as W
md = []; R = {}
def p(*a):
    s = " ".join(str(x) for x in a); print(s); md.append(s)
dr = pd.read_csv(f"{DIR}/../dane/dropped_closes.csv", parse_dates=["date"]).set_index("date").sort_index()
dr = dr.reindex(W.dates).ffill(limit=1)
P2 = pd.concat([W.P, dr], axis=1)
W.P = P2; W.UNIV = list(P2.columns)
CS2 = W.build_cs(W.week_ends); W.CS = CS2
R["uniwersum"] = dict(n_spolek=len(W.UNIV), n_dropped=int(dr.shape[1]), dropped=list(dr.columns), n_obs=int(len(CS2)))
p(f"# C6 — uniwersum 131 spółek (103 dzisiejsze + 28 usuniętych z NDX, wciąż notowanych): {len(CS2)} obserwacji\n")
p("| kandydaci | próg | wykluczone (def. A): n / śr / t | odzyskane: śr | wygrane: śr | Δ wykl.−reszta / t / CI90 / hit tyg. |")
p("|---|---|---|---|---|---|")
R["przekroj"] = {}
for lab, cand in (("top kwintyl", CS2[CS2.q == 4]), ("TOP10", CS2[CS2["rank"] <= 10]), ("TOP5", CS2[CS2["rank"] <= 5])):
    for thr in (0, -4, -8):
        m = (cand.prev < thr) & ~(cand["last"] > 0)
        ex = W.grp(cand[m]); od = W.grp(cand[(cand.prev < thr) & (cand["last"] > 0)]); wy = W.grp(cand[cand.prev >= 0]); d = W.diff_vs_rest(cand, m)
        R["przekroj"][f"{lab}|{thr}"] = dict(wykluczone=ex, odzyskane=od, wygrane=wy, roznica=d)
        p(f"| {lab} | {thr} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {od.get('srednia')} | {wy.get('srednia')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} |")
# sito Perf.W ≤ −8% (LONG) na rozszerzonym uniwersum
p("\nSito Perf.W ≤ −8% (LONG) na 131 spółkach:")
for lab, cand in (("top kwintyl", CS2[CS2.q == 4]), ("TOP10", CS2[CS2["rank"] <= 10])):
    m = cand.prev_abs <= -8; ex = W.grp(cand[m]); d = W.diff_vs_rest(cand, m)
    R["przekroj"][f"sito|{lab}"] = dict(wykluczone=ex, roznica=d)
    p(f"- {lab}: wykluczone n={ex['n']} śr {ex.get('srednia')} (t {ex.get('t')}), Δ wykl.−reszta {d.get('roznica')} (t {d.get('t')}, CI90 {d.get('ci90')})")
RL = lambda r: r["last"] > 0; RS = lambda r: r["last"] < 0
R["sim"] = {}
for thr in (0.0, -4.0):
    df = W.simulate(RL, RS, thr=thr)
    W.md.clear(); s = W.sim_summary(df, f"131 spółek, def. A, przegrana < {thr}"); md.extend(W.md); R["sim"][str(thr)] = s
json.dump(R, open(f"{DIR}/weryfikacja_C6_surv_wyniki.json", "w"), ensure_ascii=False, indent=1, default=str)
open(f"{DIR}/weryfikacja_C6_surv_out.md", "w").write("\n".join(md))
