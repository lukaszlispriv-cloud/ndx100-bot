#!/usr/bin/env python3 -I
"""perspektywa-quant: liczby odniesienia dla oceny projektu NDX100.
Wejście: closes_5y.csv. Wyjście: pq_quant_out.md + pq_quant_summary.json.
Konwencje jak w siostrzanych backtestach: D0 = ostatnia sesja tygodnia ISO, D5 = ostatnia sesja
następnego tygodnia; zwrot pozycji = r_spółki − r_NDX (long) / −(r − r_NDX) (short);
spread_pp = śr. long + śr. short (P&L w % nominału jednej strony, gross = 2).
"""
import sys, json, math
import numpy as np, pandas as pd

SRC = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv"
OUT = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/pq_quant_out.md"
OUTJ = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/pq_quant_summary.json"
rng = np.random.default_rng(20261018)
lines = []
summary = {}
def P(s=""):
    lines.append(s); print(s)

px = pd.read_csv(SRC, parse_dates=["date"]).set_index("date").sort_index()
px = px[px.notna().sum(axis=1) >= 50]
px = px.ffill(limit=2)  # pojedyncze braki odczytu (<=2 sesje) = poprzednie zamkniecie
NONSTOCK = ["^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"]
stocks = [c for c in px.columns if c not in NONSTOCK]
# GOOG/GOOGL = jedna spółka -> zostaw GOOGL
stocks = [s for s in stocks if s != "GOOG"]
ndx = px["^NDX"]
P(f"Dane: {px.index[0].date()}…{px.index[-1].date()}, sesji {len(px)}, spółek {len(stocks)}")

# --- tygodnie ISO: D0 = ostatnia sesja tygodnia
wk = px.index.to_series().groupby([px.index.isocalendar().year, px.index.isocalendar().week]).max()
wk = pd.DatetimeIndex(sorted(wk.values))
# zwroty tygodniowe (D0 -> następne D0), relatywne vs NDX
pw = px.loc[wk]
rw = pw[stocks].pct_change().shift(-1)  # zwrot od tego D0 do następnego D0
rw_ndx = pw["^NDX"].pct_change().shift(-1)
rel_w = (rw.sub(rw_ndx, axis=0)) * 100  # p.p.

# ---------- A. BASELINE losowe koszyki: N nóg, horyzont h tygodni ----------
P("\n## A. Baseline: losowe koszyki, σ tygodniowego spreadu (p.p., gross = 2)")
P("| nogi na stronę | horyzont | okien | σ pooled | p5 | p95 | σ/σ(5,1w) |")
P("|---|---|---|---|---|---|---|")
def rel_h(h):
    r = pw[stocks].pct_change(h).shift(-h)
    rn = pw["^NDX"].pct_change(h).shift(-h)
    return r.sub(rn, axis=0) * 100
base = {}
for h in (1, 2, 4):
    relh = rel_h(h)
    # okna nienakładające się
    idx = relh.index[::h]
    relh = relh.loc[idx].dropna(how="all")
    for N in (5, 10, 15):
        vals = []
        for d, row in relh.iterrows():
            avail = row.dropna()
            if len(avail) < 2 * N + 10:
                continue
            a = avail.values
            for _ in range(400):
                pick = rng.choice(len(a), 2 * N, replace=False)
                vals.append(a[pick[:N]].mean() - a[pick[N:]].mean())
        vals = np.array(vals)
        base[(N, h)] = vals.std()
        P(f"| {N} | {h} tyg. | {len(relh)} | {vals.std():.2f} | {np.percentile(vals,5):.1f} | {np.percentile(vals,95):.1f} | {vals.std()/base[(5,1)]:.2f} |")
summary["baseline_sigma"] = {f"N{N}_h{h}": round(v, 3) for (N, h), v in base.items()}

# σ pojedynczej nogi (rel vs NDX, 1 tydz.)
leg_sd = rel_w.stack().std()
P(f"\nσ pojedynczej nogi (zwrot rel. vs ^NDX, 1 tydz., pooled): {leg_sd:.2f} p.p.; "
  f"teoretyczna σ spreadu 5/5 przy niezależności = σ_nogi·√(2/5) = {leg_sd*math.sqrt(2/5):.2f} p.p.")
summary["leg_sigma_week_pp"] = round(leg_sd, 3)
# σ nóg wg zmienności: top-20% najzmienniejszych vs reszta
sig60 = px[stocks].pct_change().rolling(60).std() * 100
P("σ dzienna (60 ses., %, przekrój na 2026-10-16): mediana "
  f"{sig60.iloc[-1].median():.2f}, p90 {sig60.iloc[-1].quantile(.9):.2f}, max {sig60.iloc[-1].max():.2f} ({sig60.iloc[-1].idxmax()})")

# ---------- B. Momentum 6M z N nogami i horyzontem ----------
P("\n## B. Momentum 6M (126 sesji, bez ostatnich 5) — liczba nóg i horyzont")
def mom_signal(d0):
    i = px.index.get_loc(d0)
    if i < 131: return None
    p_end = px[stocks].iloc[i - 5]; p_start = px[stocks].iloc[i - 131]
    n_end = ndx.iloc[i - 5]; n_start = ndx.iloc[i - 131]
    s = (p_end / p_start - 1) - (n_end / n_start - 1)
    return s.dropna()

def run_strategy(N, h, overlap=False, cost_rt=0.20, fin=6.0, sig=mom_signal, side_filter=None):
    """Zwraca serię tygodniowych spreadów (p.p.) i obrót.
    h: horyzont trzymania w tygodniach; overlap=True: h transz po 1/h, co tydzień rotuje jedna.
    cost_rt: koszt round-trip w % nominału nogi; fin: %/rok finansowania od gross=2."""
    d0s = [d for d in wk if d >= pd.Timestamp("2022-04-22") and d <= wk[-h - 1]]
    rows = []
    prev_L, prev_S = set(), set()
    tranches = []  # lista (L,S) aktywnych transz
    for k, d0 in enumerate(d0s):
        s = sig(d0)
        if s is None or len(s) < 2 * N + 10: continue
        s = s.sort_values()
        L, S = list(s.index[-N:]), list(s.index[:N])
        if overlap:
            tranches.append((L, S))
            if len(tranches) > h: tranches.pop(0)
            if len(tranches) < h: continue
            # zwrot tygodnia = średnia transz (każda 1/h), każda transza trzyma swoje nazwy
            r = rel_w.loc[d0]
            vals = [np.nanmean(r[tl].values) - np.nanmean(r[ts].values) for tl, ts in tranches]
            spread = float(np.mean(vals))
            # obrót: jedna transza wymienia się na tydzień; koszt w jednostkach nominału strony = (1/h)*(zmienione/N)
            oldL, oldS = tranches[0] if len(tranches) == h else ([], [])
            changed = len(set(L) - set(oldL)) + len(set(S) - set(oldS))
            turn = changed / (2 * N) / h  # ułamek nominału jednej strony wymieniony w tygodniu (obie strony)
            cost = cost_rt * 2 * turn + fin / 52  # round trip na obu stronach + finansowanie gross 2
            rows.append((d0, spread, turn, cost))
        else:
            if k % h != 0: continue
            relh = rel_h(h).loc[d0]
            spread = float(np.nanmean(relh[L].values) - np.nanmean(relh[S].values))
            changed = len(set(L) - prev_L) + len(set(S) - prev_S)
            turn = changed / (2 * N)
            cost = cost_rt * 2 * turn + fin / 52 * h
            rows.append((d0, spread, turn, cost))
            prev_L, prev_S = set(L), set(S)
    df = pd.DataFrame(rows, columns=["d0", "spread", "turn", "cost"]).set_index("d0")
    return df

def stats(df, h=1, label=""):
    n = len(df); m = df.spread.mean(); sd = df.spread.std(ddof=1)
    t = m / sd * math.sqrt(n); sh = m / sd * math.sqrt(52 / h)
    net = (df.spread - df.cost); mn = net.mean(); tn = mn / net.std(ddof=1) * math.sqrt(n)
    shn = mn / net.std(ddof=1) * math.sqrt(52 / h)
    cum = df.spread.cumsum(); dd = (cum - cum.cummax()).min()
    hit = (df.spread > 0).mean()
    # per-week units for comparability
    return dict(label=label, n=n, mean=m, sd=sd, t=t, sharpe=sh, hit=hit, maxdd=dd, worst=df.spread.min(),
                turn=df.turn.mean(), cost=df.cost.mean(), net=mn, t_net=tn, sharpe_net=shn,
                mean_pw=m / h, sd_pw=sd / math.sqrt(h))

P("Koszty: round-trip 0,20% nominału nogi na każdą wymienioną nazwę (CFD spread ~0,1% × 2), finansowanie 6%/rok od gross 2 (= 0,115 pp/tydz./stronę → 0,23 pp/tydz.).")
P("| wariant | okien | śr. pp/okno | σ/okno | t | Sharpe | hit | maxDD | najgorsze | obrót/okno | koszt pp/okno | netto pp/okno | t netto | Sharpe netto |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
res_B = {}
for N in (5, 10, 15):
    for h, ov in ((1, False), (2, False), (4, False), (2, True), (4, True)):
        df = run_strategy(N, h, overlap=ov)
        lab = f"mom6M N={N} h={h}w{' nakł.' if ov else ''}"
        st = stats(df, 1 if ov else h, lab); res_B[lab] = st
        P(f"| {lab} | {st['n']} | {st['mean']:.2f} | {st['sd']:.2f} | {st['t']:.2f} | {st['sharpe']:.2f} | {st['hit']:.0%} | {st['maxdd']:.0f} | {st['worst']:.1f} | {st['turn']:.2f} | {st['cost']:.2f} | {st['net']:.2f} | {st['t_net']:.2f} | {st['sharpe_net']:.2f} |")
summary["mom6M_variants"] = {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in res_B.items()}

# ---------- C. Premia za zmienność: long low-vol / short high-vol ----------
P("\n## C. Premia za zmienność (σ60) i zakład systemu (long high-σ semis / short low-σ staples)")
def vol_signal(d0):
    i = px.index.get_loc(d0)
    if i < 61: return None
    s = px[stocks].iloc[i - 60:i + 1].pct_change().std()
    return (-s).dropna()  # wysoki = niska zmienność -> long low vol
def beta_signal(d0):
    i = px.index.get_loc(d0)
    if i < 121: return None
    r = px[stocks].iloc[i - 120:i + 1].pct_change().iloc[1:]
    rn = ndx.iloc[i - 120:i + 1].pct_change().iloc[1:]
    b = r.apply(lambda c: np.cov(c.dropna(), rn.loc[c.dropna().index])[0, 1] / rn.loc[c.dropna().index].var() if c.notna().sum() > 60 else np.nan)
    return (-b).dropna()  # long low beta
for lab, sg in (("long low-σ / short high-σ (5/5)", vol_signal), ("long low-β / short high-β (5/5)", beta_signal)):
    df = run_strategy(5, 1, sig=sg)
    st = stats(df, 1, lab)
    # korelacja z NDX tygodniowym
    c = np.corrcoef(df.spread.values, rw_ndx.loc[df.index].values * 100)[0, 1]
    bNDX = np.polyfit(rw_ndx.loc[df.index].values * 100, df.spread.values, 1)[0]
    P(f"- {lab}: n={st['n']}, śr. {st['mean']:.2f} pp/tydz., σ {st['sd']:.2f}, t {st['t']:.2f}, Sharpe {st['sharpe']:.2f}, hit {st['hit']:.0%}; "
      f"corr z r(^NDX) = {c:.2f}, β na ^NDX = {bNDX:.2f} (pp spreadu na 1 pp indeksu); netto {st['net']:.2f} pp/tydz.")
    summary[lab] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items()}; summary[lab]["corr_ndx"] = round(c, 3); summary[lab]["beta_ndx"] = round(bNDX, 3)
    # po latach
    yr = df.spread.groupby(df.index.year).agg(["count", "mean", "std"])
    P("  lata: " + "; ".join(f"{y}: n={int(r['count'])} śr. {r['mean']:.2f} σ {r['std']:.2f}" for y, r in yr.iterrows()))

# ---------- D. Dryf po dużym ruchu dziennym (proxy PEAD / zdarzenie) ----------
P("\n## D. Dryf po dużym ruchu dziennym (proxy wyników): zwrot rel. w kolejnych 5 i 10 sesjach")
rd = px[stocks].pct_change()
rdn = ndx.pct_change()
reld = rd.sub(rdn, axis=0)
fwd5 = (px[stocks].shift(-5) / px[stocks] - 1).sub(ndx.shift(-5) / ndx - 1, axis=0) * 100
fwd10 = (px[stocks].shift(-10) / px[stocks] - 1).sub(ndx.shift(-10) / ndx - 1, axis=0) * 100
fwd1 = (px[stocks].shift(-1) / px[stocks] - 1).sub(ndx.shift(-1) / ndx - 1, axis=0) * 100
P("| zdarzenie (ruch rel. dnia) | n | fwd 1 ses. śr. | fwd 5 ses. śr. | σ5 | t5 (klastr. po dacie) | hit5 (kontynuacja) | fwd 10 ses. śr. |")
P("|---|---|---|---|---|---|---|---|")
def clustered_t(ev_df):
    # średnia po dniach (klaster = data), t z liczby dni
    g = ev_df.groupby(level=0).mean()
    return g.mean() / g.std(ddof=1) * math.sqrt(len(g)), len(g)
ev_res = {}
for lab, mask in (("≥ +8%", reld >= 0.08), ("+5…+8%", (reld >= 0.05) & (reld < 0.08)), ("≤ −8%", reld <= -0.08), ("−8…−5%", (reld <= -0.05) & (reld > -0.08)),
                  ("≥ +12%", reld >= 0.12), ("≤ −12%", reld <= -0.12)):
    m = mask & fwd5.notna()
    e5 = fwd5[m].stack().dropna(); e1 = fwd1[m].stack().dropna(); e10 = fwd10[m].stack().dropna()
    t5, nd = clustered_t(e5)
    sign = -1 if "−" in lab else 1
    hit = (np.sign(e5) == sign).mean()
    P(f"| {lab} | {len(e5)} ({nd} dni) | {e1.mean():.2f} | {e5.mean():.2f} | {e5.std():.1f} | {t5:.2f} | {hit:.0%} | {e10.mean():.2f} |")
    ev_res[lab] = dict(n=len(e5), fwd1=round(e1.mean(), 3), fwd5=round(e5.mean(), 3), sd5=round(e5.std(), 2), t5=round(t5, 2), hit5=round(hit, 3), fwd10=round(e10.mean(), 3))
summary["event_drift"] = ev_res
# po latach dla ≤ −8% (kluczowe dla reguły LUKA-SHORT z propozycji 3.1)
m = (reld <= -0.08) & fwd5.notna()
e5 = fwd5[m].stack().dropna()
yr = e5.groupby(e5.index.get_level_values(0).year).agg(["count", "mean", "std"])
P("Po ≤ −8% (fwd5 rel.) wg lat: " + "; ".join(f"{y}: n={int(r['count'])} śr. {r['mean']:.2f}" for y, r in yr.iterrows()))
m = (reld >= 0.08) & fwd5.notna()
e5 = fwd5[m].stack().dropna()
yr = e5.groupby(e5.index.get_level_values(0).year).agg(["count", "mean", "std"])
P("Po ≥ +8% (fwd5 rel.) wg lat: " + "; ".join(f"{y}: n={int(r['count'])} śr. {r['mean']:.2f}" for y, r in yr.iterrows()))

# dryf po luce ≤ −8% w zależności od momentum 6M spółki (percentyl na dzień zdarzenia, liczony z cen do dnia przed)
mom126 = (px[stocks].shift(1) / px[stocks].shift(127) - 1).sub(ndx.shift(1) / ndx.shift(127) - 1, axis=0)
pct_mom = mom126.rank(axis=1, pct=True)
for lab, mask in (("≤ −8%", reld <= -0.08), ("≥ +8%", reld >= 0.08)):
    m = mask & fwd5.notna() & pct_mom.notna()
    e5 = fwd5[m].stack().dropna(); pm = pct_mom[m].stack().dropna().reindex(e5.index)
    hi = e5[pm >= 0.7]; lo = e5[pm <= 0.3]
    P(f"Po {lab}: spółki z momentum 6M w górnych 30% → fwd5 śr. {hi.mean():.2f} (n={len(hi)}); dolne 30% → {lo.mean():.2f} (n={len(lo)})")

# ---------- E. Sezonowość dnia tygodnia dla spreadu momentum ----------
P("\n## E. Dzień tygodnia: dzienny spread koszyka momentum 6M (5/5, skład z ostatniego D0) wg dnia tygodnia")
daily_rows = []
d0s = [d for d in wk if d >= pd.Timestamp("2022-04-22")]
for k in range(len(d0s) - 1):
    s = mom_signal(d0s[k])
    if s is None: continue
    s = s.sort_values(); L, S = list(s.index[-5:]), list(s.index[:5])
    seg = reld.loc[(reld.index > d0s[k]) & (reld.index <= d0s[k + 1])]
    sp = (seg[L].mean(axis=1) - seg[S].mean(axis=1)) * 100
    for d, v in sp.items(): daily_rows.append((d, d.dayofweek, v, rdn.loc[d] * 100))
dd = pd.DataFrame(daily_rows, columns=["date", "dow", "spread", "ndx"]).set_index("date")
names = ["pon", "wt", "śr", "czw", "pt"]
P("| dzień | n | śr. spread pp | σ | t | śr. r(^NDX) % |")
P("|---|---|---|---|---|---|")
for d in range(5):
    x = dd[dd.dow == d]
    P(f"| {names[d]} | {len(x)} | {x.spread.mean():.3f} | {x.spread.std():.2f} | {x.spread.mean()/x.spread.std()*math.sqrt(len(x)):.2f} | {x.ndx.mean():.3f} |")
summary["dow"] = {names[d]: round(dd[dd.dow == d].spread.mean(), 4) for d in range(5)}
# autokorelacja dziennego spreadu (sygnał dla bramki reakcji)
ac1 = dd.spread.autocorr(1); ac2 = dd.spread.autocorr(2)
P(f"Autokorelacja dziennego spreadu momentum: lag1 {ac1:.3f}, lag2 {ac2:.3f} (n={len(dd)}); "
  f"wartość |ρ|<0,05 = brak podstaw dla bramki reagującej na dwie sesje w jednym kierunku.")
summary["daily_spread_autocorr"] = [round(ac1, 4), round(ac2, 4)]
# Warunkowo: po dniu spreadu ≤ −3 pp co dalej (kolejne 3 sesje)
nxt = dd.spread.shift(-1) + dd.spread.shift(-2) + dd.spread.shift(-3)
bad = dd.spread <= -3
P(f"Po dniu ze spreadem ≤ −3 pp (n={bad.sum()}): suma kolejnych 3 sesji śr. {nxt[bad].mean():.2f} pp (σ {nxt[bad].std():.2f}, t {nxt[bad].mean()/nxt[bad].std()*math.sqrt(bad.sum()):.2f}); "
  f"po dniu ≥ +3 pp (n={(dd.spread>=3).sum()}): {nxt[dd.spread>=3].mean():.2f} pp.")

# ---------- F. Sharpe -> tygodniowy spread; sizing; prawdopodobieństwo kill switcha ----------
P("\n## F. Przekład Sharpe'a na tygodniowy spread i ryzyko kill switcha (symulacja)")
P("| σ tyg. spreadu | Sharpe 0,5 → μ pp/tydz. | Sharpe 1,0 | Sharpe 1,5 | tygodni do t=2 przy S=1,0 |")
P("|---|---|---|---|---|")
for sd in (3.4, 5.0, 7.0, 10.0):
    P(f"| {sd:.1f} | {0.5*sd/math.sqrt(52):.2f} | {1.0*sd/math.sqrt(52):.2f} | {1.5*sd/math.sqrt(52):.2f} | {int(round((2/(1.0/math.sqrt(52)))**2))} |")
# symulacja: kapitał, tygodnie, kill 25% od szczytu; zwroty t-Studenta df=4 skalowane
def p_kill(mu_pp, sd_pp, gross_mult, weeks, nsim=20000, df=4):
    scale = sd_pp * gross_mult / 100 * math.sqrt((df - 2) / df)
    r = rng.standard_t(df, size=(nsim, weeks)) * scale + mu_pp * gross_mult / 100
    eq = np.cumprod(1 + r, axis=1); eq = np.concatenate([np.ones((nsim, 1)), eq], axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    return ((eq / peak) <= 0.75).any(axis=1).mean()
P("\nP(kill switch −25% od szczytu) — zwroty t(4), tygodniowe; mnożnik kapitał/spread = gross/2 (ALLOC 0,24 → 1,2; 0,12 → 0,6):")
P("| μ pp/tydz. | σ pp/tydz. | ALLOC | 26 tyg. | 52 tyg. |")
P("|---|---|---|---|---|")
pk = {}
for mu, sd in ((0.0, 7.0), (0.75, 7.0), (0.75, 5.0), (1.0, 7.0), (0.0, 3.4), (0.5, 3.4)):
    for alloc, gm in ((0.24, 1.2), (0.12, 0.6), (0.08, 0.4)):
        a, b = p_kill(mu, sd, gm, 26), p_kill(mu, sd, gm, 52)
        pk[f"mu{mu}_sd{sd}_alloc{alloc}"] = [round(a, 3), round(b, 3)]
        P(f"| {mu:.2f} | {sd:.1f} | {alloc:.2f} | {a:.0%} | {b:.0%} |")
summary["p_kill"] = pk
# Kelly: f* = μ/σ² na jednostkę nominału strony (spread w ułamkach)
P("\nUłamek Kelly'ego (f* = μ/σ², w jednostkach nominału jednej strony/kapitał; 1,0 = ALLOC 0,20 przy 5 nogach):")
for mu, sd in ((0.5, 3.4), (0.75, 7.0), (1.0, 7.0), (1.0, 5.0)):
    f = (mu / 100) / (sd / 100) ** 2
    P(f"- μ {mu} pp, σ {sd} pp → f* = {f:.2f} × strona (pełny Kelly = ALLOC {f*0.2:.2f}; pół-Kelly = ALLOC {f*0.1:.2f})")

# ---------- G. Faktyczne W1–W7 vs baseline ----------
P("\n## G. Faktyczne wyniki W1–W7 vs baseline")
hist = [-4.06, 6.19, 1.44, 13.85, 5.95, -5.89, -21.15]
h = np.array(hist);
P(f"W1–W7: śr. {h.mean():.2f}, σ {h.std(ddof=1):.2f}, t {h.mean()/h.std(ddof=1)*math.sqrt(7):.2f}; "
  f"σ faktyczna / σ losowego 5-5 (3,4) = {h.std(ddof=1)/3.4:.1f}×; W7 jako z wobec losowego koszyka: {-21.15/3.4:.1f}σ, "
  f"wobec σ koszyków momentum 6M w 2026 (~12 pp wg bt_momentum): {-21.15/12.2:.1f}σ.")
# test wariancji: czy σ W1-W7 (11,3) jest zgodna z σ losowego 3,4? chi2 (6 df) = 6*11.3²/3.4²
chi = 6 * h.var(ddof=1) / 3.4 ** 2
P(f"χ²(6) = {chi:.0f} dla H0: σ = 3,4 pp → p ≈ 0 (wartość krytyczna 12,6): koszyki są istotnie bardziej ryzykowne niż losowe o równych wagach.")
# ile tygodni na wykrycie
for mu in (0.5, 1.0, 2.0):
    for sd in (3.4, 7.0, 11.3):
        P(f"- μ={mu} pp, σ={sd} pp: n tygodni do t=2: {int(round((2*sd/mu)**2))}")
summary["W1W7"] = dict(mean=round(h.mean(), 3), sd=round(h.std(ddof=1), 3), t=round(h.mean()/h.std(ddof=1)*math.sqrt(7), 3), chi2=round(chi, 1))

with open(OUT, "w") as f: f.write("\n".join(lines) + "\n")
with open(OUTJ, "w") as f: json.dump(summary, f, ensure_ascii=False, indent=1, default=float)
print("\nzapisano", OUT, OUTJ)
