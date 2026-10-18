#!/usr/bin/env python3 -I
"""Dodatek do weryfikacji C6: najmocniejsze punkty NA RZECZ reguły — holdout wg zbioru kandydatów,
inny ranking (12M−1M), bootstrap Δ portfela, kontrola wielokrotnych testów, przypadek W8 (Perf.W ≤ −15%)."""
import sys, json, math
import numpy as np, pandas as pd
DIR = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza"
sys.path.insert(0, DIR)
import weryfikacja_C6 as W
CS = W.CS; md = []; R = {}
def p(*a):
    s = " ".join(str(x) for x in a); print(s); md.append(s)

p("# Weryfikacja C6 — dodatek\n")
# ---------------------------------------------------------------- A. holdout od 2025-07 wg zbioru kandydatów
p("## A. Holdout od 2025-07 (64 tyg.) vs in-sample do 2025-06 — Δ (wykluczone − reszta kandydatów), def. A, horyzont 1 tyg.\n")
p("| kandydaci | próg przegranej | okres | n wykl. | śr. wykluczonych | śr. reszty | Δ / t / CI90 / hit tyg. |")
p("|---|---|---|---|---|---|---|")
R["holdout"] = {}
sets = {"top kwintyl": CS[CS.q == 4], "TOP10": CS[CS["rank"] <= 10], "TOP5": CS[CS["rank"] <= 5], "TOP15": CS[CS["rank"] <= 15]}
for lab, cand in sets.items():
    for thr in (0, -4):
        for per, pm in (("holdout ≥2025-07", cand.d0 >= "2025-07-01"), ("in-sample <2025-07", cand.d0 < "2025-07-01"), ("2026", cand.d0.dt.year == 2026)):
            sub = cand[pm]; m = (sub.prev < thr) & ~(sub["last"] > 0)
            ex = W.grp(sub[m]); rest = W.grp(sub[~m]); d = W.diff_vs_rest(sub, m)
            R["holdout"][f"{lab}|{thr}|{per}"] = dict(wykluczone=ex, reszta=rest, roznica=d)
            p(f"| {lab} | {thr} | {per} | {ex['n']} | {ex.get('srednia')} | {rest.get('srednia')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} |")

# ---------------------------------------------------------------- B. symulacja z rankingiem 12M−1M (proxy: 126 sesji z pominięciem ostatnich 21)
p("\n## B. Symulacja portfela z innym rankingiem: momentum 6M z pominięciem ostatniego miesiąca (mom6s), def. A\n")
RL = {"A": lambda r: r["last"] > 0}; RS = {"A": lambda r: r["last"] < 0}
R["sim_mom6s"] = {}
for thr in (0.0, -4.0):
    df = W.simulate(RL["A"], RS["A"], thr=thr, rank_col="mom6s")
    W.md.clear(); s = W.sim_summary(df, f"ranking mom6s, przegrana < {thr}"); md.extend(W.md); R["sim_mom6s"][str(thr)] = s

# ---------------------------------------------------------------- C. bootstrap Δ portfela (def. A, próg 0) i rozkład po tygodniach
p("\n## C. Bootstrap tygodniowy Δ spread (reguła − bez), def. A, próg 0, obie strony\n")
sim = pd.read_csv(f"{DIR}/weryfikacja_C6_sim_A.csv", parse_dates=["d0"]).set_index("d0")
rng = np.random.default_rng(11)
for col in ("d_spread", "d_long", "d_short"):
    x = sim[col].values; bs = np.array([rng.choice(x, len(x), replace=True).mean() for _ in range(10000)])
    R[f"boot_{col}"] = dict(srednia=round(float(x.mean()),3), ci90=[round(float(np.percentile(bs,5)),2), round(float(np.percentile(bs,95)),2)], ci95=[round(float(np.percentile(bs,2.5)),2), round(float(np.percentile(bs,97.5)),2)], P_delta_dodatnia=round(float((bs>0).mean()),3))
    p(f"- {col}: średnia {R[f'boot_{col}']['srednia']} p.p./tydz., CI90 {R[f'boot_{col}']['ci90']}, CI95 {R[f'boot_{col}']['ci95']}, P(Δ>0 — reguła pomaga) = {R[f'boot_{col}']['P_delta_dodatnia']}")
# skumulowany koszt
cum = sim.d_spread.cumsum(); R["koszt_skumulowany_pp"] = round(float(cum.iloc[-1]),1)
R["koszt_2026_pp"] = round(float(sim.loc["2026", "d_spread"].sum()),1)
R["koszt_od_W1_pp"] = round(float(sim.loc["2026-08-21":, "d_spread"].sum()),1)
p(f"- skumulowany Δ spread 2022-04…2026-09: {R['koszt_skumulowany_pp']} p.p. (suma tygodni); 2026 YTD: {R['koszt_2026_pp']} p.p.; od W1 (21.08.2026): {R['koszt_od_W1_pp']} p.p. w {len(sim.loc['2026-08-21':])} tyg.")
p("- tygodnie od W1 (ranking momentum TOP5/BOTTOM5, nie koszyki Modelu 3.0): " + "; ".join(f"{d.date()}: Δ {v:+.2f}" for d, v in sim.loc["2026-08-21":, "d_spread"].items()))

# ---------------------------------------------------------------- D. kontrola wielokrotnych testów
p("\n## D. Ile wariantów przekrojowych wskazuje, że reguła POMAGA (Δ wykl.−reszta < 0, t ≤ −1,65) vs KOSZTUJE (Δ > 0, t ≥ 1,65)?\n")
OUT = json.load(open(f"{DIR}/weryfikacja_C6_wyniki.json"))
rows = []
def walk(d, path):
    if isinstance(d, dict):
        if "roznica" in d and isinstance(d["roznica"], dict) and "t" in d["roznica"]:
            rows.append((path, d["roznica"]["roznica"], d["roznica"]["t"], d["roznica"].get("n_wykl")))
        else:
            for k, v in d.items(): walk(v, f"{path}/{k}")
walk({k: OUT[k] for k in OUT if k not in ("symulacja", "in_sample")}, "")
T = pd.DataFrame(rows, columns=["wariant", "delta", "t", "n"]).dropna(subset=["t"])
long_rows = T[~T.wariant.str.contains("short", case=False)]
R["wielokrotne"] = dict(n_wariantow=int(len(T)), pomaga_t165=int((T.t <= -1.65).sum()), kosztuje_t165=int((T.t >= 1.65).sum()), delta_ujemna=int((T.delta < 0).sum()), delta_dodatnia=int((T.delta > 0).sum()),
                       long_n=int(len(long_rows)), long_pomaga=int((long_rows.t <= -1.65).sum()), long_kosztuje=int((long_rows.t >= 1.65).sum()))
p(f"- wszystkich wariantów z t: {R['wielokrotne']['n_wariantow']}; Δ<0 (reguła pomaga kierunkowo): {R['wielokrotne']['delta_ujemna']}, Δ>0 (kosztuje): {R['wielokrotne']['delta_dodatnia']}; |t|≥1,65: pomaga {R['wielokrotne']['pomaga_t165']}, kosztuje {R['wielokrotne']['kosztuje_t165']}")
p(f"- tylko LONG: {R['wielokrotne']['long_n']} wariantów, pomaga istotnie {R['wielokrotne']['long_pomaga']}, kosztuje istotnie {R['wielokrotne']['long_kosztuje']}")
p("- warianty, gdzie reguła pomaga z t ≤ −1,3: " + "; ".join(f"{r.wariant} Δ {r.delta} t {r.t} n {r.n}" for r in T[T.t <= -1.3].itertuples()))
p("- warianty, gdzie reguła kosztuje z t ≥ 2,0: " + "; ".join(f"{r.wariant} Δ {r.delta} t {r.t} n {r.n}" for r in T[T.t >= 2.0].itertuples()))

# ---------------------------------------------------------------- E. przypadek W8: Perf.W ≤ −15% i ostatnia sesja ≤ 0 wśród TOP15 — wszystkie obserwacje
p("\n## E. Filtr W8 w wersji skrajnej (TOP15, Perf.W ≤ −15%, ostatnia sesja rel ≤ 0): wszystkie obserwacje\n")
c = sets["TOP15"]; m = (c.prev_abs <= -15) & ~(c["last"] > 0)
sub = c[m].sort_values("d0")
R["W8_skrajny"] = dict(n=int(len(sub)), n_tyg=int(sub.d0.nunique()), fwd1_sr=round(float(sub.fwd1.mean()),2), fwd1_med=round(float(sub.fwd1.median()),2), hit=round(float((sub.fwd1>0).mean()),3),
                      fwd2_sr=round(float(sub.fwd2.mean()),2), fwd4_sr=round(float(sub.fwd4.mean()),2), po_latach={str(y): int(n) for y, n in sub.groupby(sub.d0.dt.year).size().items()},
                      lista=[dict(d0=str(r.d0.date()), t=r.t, perfW=round(r.prev_abs,1), last=round(r["last"],2), fwd1=round(r.fwd1,2), fwd2=round(r.fwd2,2) if not np.isnan(r.fwd2) else None) for _, r in sub.iterrows()])
p(f"- n={R['W8_skrajny']['n']} obserwacji w {R['W8_skrajny']['n_tyg']} tygodniach; fwd1 śr {R['W8_skrajny']['fwd1_sr']}, mediana {R['W8_skrajny']['fwd1_med']}, hit {R['W8_skrajny']['hit']}; fwd2 śr {R['W8_skrajny']['fwd2_sr']}, fwd4 śr {R['W8_skrajny']['fwd4_sr']}; po latach {R['W8_skrajny']['po_latach']}")
p("- lista: " + "; ".join(f"{x['d0']} {x['t']} W {x['perfW']}% last {x['last']} → fwd1 {x['fwd1']}" for x in R["W8_skrajny"]["lista"]))
# porównanie: reszta TOP15 w tych samych tygodniach
wk = sub.d0.unique(); rest = c[c.d0.isin(wk) & ~m]
R["W8_skrajny"]["reszta_TOP15_te_same_tyg"] = dict(n=int(len(rest)), fwd1_sr=round(float(rest.fwd1.mean()),2), fwd2_sr=round(float(rest.fwd2.mean()),2))
p(f"- reszta TOP15 w tych samych tygodniach: n={len(rest)}, fwd1 śr {R['W8_skrajny']['reszta_TOP15_te_same_tyg']['fwd1_sr']}, fwd2 śr {R['W8_skrajny']['reszta_TOP15_te_same_tyg']['fwd2_sr']}")

# ---------------------------------------------------------------- F. „kontynuacja po krachu”: czy przegrane nogi kontynuują po tygodniu ^NDX < −3%?
p("\n## F. Kontynuacja po krachu? Top kwintyl, tygodnie ^NDX < −3%: przegrane (<0) vs wygrane nogi, forward 1 tyg.\n")
tq = sets["top kwintyl"]; k = tq[tq.ndx_w < -3]
for lab, mm in (("przegrane < 0 bez odzyskania", (k.prev < 0) & ~(k["last"] > 0)), ("przegrane < 0 z odzyskaniem", (k.prev < 0) & (k["last"] > 0)), ("wygrane ≥ 0", k.prev >= 0), ("przegrane < −8 bez odzyskania", (k.prev < -8) & ~(k["last"] > 0))):
    g = W.grp(k[mm]); R[f"krach|{lab}"] = g
    p(f"- {lab}: n={g['n']}, fwd1 śr {g.get('srednia')}, t {g.get('t')}, hit {g.get('hit')}")
ndx_next = CS.groupby("d0").agg(ndx_w=("ndx_w", "first")).reset_index()
# zwrot indeksu w następnym tygodniu
we = W.week_ends; d = W.dates; N = W.NDX
nx = {d[we[i]]: (N.iloc[we[i+1]]/N.iloc[we[i]]-1)*100 for i in range(len(we)-1)}
ndx_next["ndx_next"] = ndx_next.d0.map(nx)
kk = ndx_next[ndx_next.ndx_w < -3]
R["ndx_po_krachu"] = dict(n=int(len(kk)), ndx_next_sr=round(float(kk.ndx_next.mean()),2), hit_dodatni=round(float((kk.ndx_next>0).mean()),3))
p(f"- indeks ^NDX po tygodniu < −3% (n={R['ndx_po_krachu']['n']}): następny tydzień śr {R['ndx_po_krachu']['ndx_next_sr']}%, dodatni w {R['ndx_po_krachu']['hit_dodatni']}")

json.dump(R, open(f"{DIR}/weryfikacja_C6_dod_wyniki.json", "w"), ensure_ascii=False, indent=1, default=str)
open(f"{DIR}/weryfikacja_C6_dod_out.md", "w").write("\n".join(md))
