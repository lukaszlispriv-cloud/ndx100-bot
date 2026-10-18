#!/usr/bin/env python3 -I
"""Weryfikacja C6: reguła „przegrana noga bez odzyskanej siły relatywnej = poza koszykiem".

Próba OBALENIA twierdzenia z audyt-regul.md: szukamy definicji/warunków, w których
wykluczane nogi mają istotnie GORSZY zwrot przyszły niż reszta kandydatów.

Dane: closes_5y.csv (zamknięcia; survivorship bias — skład dzisiejszy; brak korekty o dywidendy).
Okna: tygodnie kalendarzowe (ostatnia sesja tygodnia = D0, jak sobotnia rutyna), forward = następna ostatnia sesja.
Zwrot relatywny = zwrot spółki − zwrot ^NDX, w p.p.; dla SHORT ze znakiem minus (zysk shortu).
"""
import json, math, sys
import numpy as np, pandas as pd

BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
px = pd.read_csv(f"{BASE}/dane/closes_5y.csv", parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()].ffill(limit=1)
NDX = px["^NDX"]; SOX = px["^SOX"]
UNIV = [c for c in px.columns if not c.startswith("^") and c not in ("QQQ","XLP","XLU","XLV","SMH","IGV")]
P = px[UNIV]
dates = px.index
OUT = {}
md = []
def p(*a):
    s = " ".join(str(x) for x in a); print(s); md.append(s)

# ------------------------------------------------------------------ przekrój
def build_cs(week_ends, mom_len=126):
    """Dla każdego D0 (indeks pozycyjny) i spółki: cechy + zwroty przyszłe 1/2/4 tyg."""
    rec = []
    for k in range(len(week_ends) - 4):
        i0 = week_ends[k]; i1 = week_ends[k+1]; i2 = week_ends[k+2]; i4 = week_ends[k+4]
        if k == 0 or i0 < mom_len + 6: continue
        ip = week_ends[k-1]           # koniec poprzedniego tygodnia
        ipp = week_ends[k-2] if k >= 2 else None
        n0, n1, n2, n4, npv = NDX.iloc[i0], NDX.iloc[i1], NDX.iloc[i2], NDX.iloc[i4], NDX.iloc[ip]
        ndx_w = (n0/npv - 1)*100                      # tydzień indeksu (przed D0)
        ndx_prev2 = (NDX.iloc[ip]/NDX.iloc[ipp]-1)*100 if ipp is not None else np.nan
        sox_w = (SOX.iloc[i0]/SOX.iloc[ip]-1)*100 - ndx_w
        nd = NDX.iloc[i0-3:i0+1].values; ndd = nd[1:]/nd[:-1]-1  # 3 ostatnie sesje dzienne indeksu
        n10 = NDX.iloc[i0]/NDX.iloc[i0-10]-1
        nm = NDX.iloc[i0]/NDX.iloc[i0-mom_len]-1
        nm1 = NDX.iloc[i0-21]/NDX.iloc[i0-mom_len]-1
        for t in UNIV:
            s = P[t].values
            if np.isnan(s[i0]) or np.isnan(s[i1]) or np.isnan(s[i0-mom_len]) or np.isnan(s[ip]): continue
            fwd1 = (s[i1]/s[i0]-1)*100 - (n1/n0-1)*100
            fwd2 = (s[i2]/s[i0]-1)*100 - (n2/n0-1)*100 if not np.isnan(s[i2]) else np.nan
            fwd4 = (s[i4]/s[i0]-1)*100 - (n4/n0-1)*100 if not np.isnan(s[i4]) else np.nan
            prev = (s[i0]/s[ip]-1)*100 - ndx_w                 # tydzień relatywny (przegrana?)
            prev_abs = (s[i0]/s[ip]-1)*100                     # Perf.W absolutny
            prev2 = (s[ip]/s[ipp]-1)*100 - ndx_prev2 if ipp is not None and not np.isnan(s[ipp]) else np.nan
            w = s[i0-3:i0+1]; dd = w[1:]/w[:-1]-1
            rel_d = (dd - ndd)*100                             # 3 ostatnie sesje relatywnie
            last = rel_d[-1]; n_pos3 = int((rel_d > 0).sum()); rel3 = (s[i0]/s[i0-3]-1)*100 - (NDX.iloc[i0]/NDX.iloc[i0-3]-1)*100
            r10 = (s[i0]/s[i0-10]-1)*100
            mom6 = (s[i0]/s[i0-mom_len]-1)*100 - nm*100
            mom6s = (s[i0-21]/s[i0-mom_len]-1)*100 - nm1*100 if not np.isnan(s[i0-21]) else np.nan
            rec.append((dates[i0], t, fwd1, fwd2, fwd4, prev, prev_abs, prev2, last, n_pos3, rel3, r10, mom6, mom6s, ndx_w, sox_w))
    cs = pd.DataFrame(rec, columns=["d0","t","fwd1","fwd2","fwd4","prev","prev_abs","prev2","last","n_pos3","rel3","r10","mom6","mom6s","ndx_w","sox_w"])
    cs["rank"] = cs.groupby("d0").mom6.rank(ascending=False, method="first")
    cs["n_univ"] = cs.groupby("d0").mom6.transform("size")
    cs["q"] = cs.groupby("d0").mom6.transform(lambda x: pd.qcut(x.rank(method="first"), 5, labels=False))
    cs["rank_s"] = cs.groupby("d0").mom6.rank(ascending=True, method="first")
    return cs

# tygodnie kalendarzowe: ostatnia sesja każdego tygodnia ISO
wk = pd.Series(np.arange(len(dates)), index=dates)
week_ends = wk.groupby([dates.isocalendar().year.values, dates.isocalendar().week.values]).max().sort_values().values
CS = build_cs(week_ends)
OUT["n_tygodni"] = int(CS.d0.nunique()); OUT["zakres"] = [str(CS.d0.min().date()), str(CS.d0.max().date())]
p(f"# Weryfikacja C6 — wyniki skryptu\n\nPrzekrój: {OUT['n_tygodni']} tygodni kalendarzowych {OUT['zakres'][0]}…{OUT['zakres'][1]}, {len(CS)} obserwacji spółka-tydzień.")

def tstat(series):
    s = pd.Series(series).dropna()
    if len(s) < 3: return float("nan")
    return s.mean()/(s.std(ddof=1)/math.sqrt(len(s)))

def grp(sub, col="fwd1"):
    if len(sub) == 0: return dict(n=0)
    g = sub.groupby("d0")[col].mean()
    return dict(n=int(sub[col].notna().sum()), n_tyg=int(len(g)), srednia=round(float(sub[col].mean()),2), t=round(tstat(g),2), hit=round(float((sub[col]>0).mean()),3))

def diff_vs_rest(cand, mask, col="fwd1"):
    """Różnica (wykluczone − reszta kandydatów) policzona tydzień po tygodniu; t klastrowany po tygodniu.
    Dodatnia różnica = reguła wyrzuca nogi LEPSZE od tych, które zostają (reguła kosztuje)."""
    a = cand[mask].groupby("d0")[col].mean(); b = cand[~mask].groupby("d0")[col].mean()
    d = (a - b).dropna()
    if len(d) < 3: return dict(n_tyg=int(len(d)))
    # bootstrap po tygodniach
    rng = np.random.default_rng(7); bs = [rng.choice(d.values, len(d), replace=True).mean() for _ in range(4000)]
    return dict(n_wykl=int(mask.sum()), n_tyg=int(len(d)), roznica=round(float(d.mean()),2), t=round(tstat(d),2),
                ci90=[round(float(np.percentile(bs,5)),2), round(float(np.percentile(bs,95)),2)], hit_tyg=round(float((d>0).mean()),3))

# definicje odzyskania (LONG): A ostatnia sesja rel>0; B >=2 z 3 sesji rel>0; C 3-sesyjny rel>0
REC = {"A_ostatnia_sesja>0": lambda c: c["last"] > 0,
       "B_2z3_sesji>0":      lambda c: c.n_pos3 >= 2,
       "C_3sesje_lacznie>0": lambda c: c.rel3 > 0}
RECS = {"A_ostatnia_sesja<0": lambda c: c["last"] < 0,
        "B_2z3_sesji<0":      lambda c: c.n_pos3 <= 1,
        "C_3sesje_lacznie<0": lambda c: c.rel3 < 0}

def simulate(rec_fn_long, rec_fn_short, thr=0.0, w8_filter=False, side_rule=("L","S"), horizon_col="fwd1", stateful=True, topn=5, rank_col="mom6"):
    """Zwraca DataFrame tygodniowy: long_base, long_rule, short_base, short_rule, zmiany nóg."""
    rows = []
    excl_L, excl_S = set(), set()   # nazwy „poza koszykiem do odzyskania”
    prev_L, prev_S = set(), set()
    for d0, g in CS.groupby("d0"):
        g = g.dropna(subset=[horizon_col])
        g = g.dropna(subset=[rank_col]); gl = g.sort_values(rank_col, ascending=False); gs = g.sort_values(rank_col, ascending=True)
        base_L = list(gl.t.iloc[:topn]); base_S = list(gs.t.iloc[:topn])
        # reguła LONG: noga z poprzedniego koszyka, która przegrała i nie odzyskała — poza; wykluczone wracają po odzyskaniu
        byt = g.set_index("t")
        if "L" in side_rule:
            newex = set()
            for t in (prev_L | (excl_L if stateful else set())):
                if t not in byt.index: continue
                r = byt.loc[t]
                if t in prev_L:
                    if r.prev < thr and not rec_fn_long(r): newex.add(t)
                else:  # był wykluczony — wraca tylko po odzyskaniu
                    if not rec_fn_long(r): newex.add(t)
            if w8_filter:
                newex |= set(gl.t[(gl.prev_abs <= -8) & ~(gl["last"] > 0)].iloc[:15])
            rule_L = [t for t in gl.t if t not in newex][:topn]; excl_L = newex
        else:
            rule_L = base_L
        if "S" in side_rule:
            newexS = set()
            for t in (prev_S | (excl_S if stateful else set())):
                if t not in byt.index: continue
                r = byt.loc[t]
                if t in prev_S:
                    if r.prev > -thr and not rec_fn_short(r): newexS.add(t)
                else:
                    if not rec_fn_short(r): newexS.add(t)
            rule_S = [t for t in gs.t if t not in newexS][:topn]; excl_S = newexS
        else:
            rule_S = base_S
        f = byt[horizon_col]
        rows.append(dict(d0=d0, long_base=f[base_L].mean(), long_rule=f[rule_L].mean(), short_base=-f[base_S].mean(), short_rule=-f[rule_S].mean(),
                         zm_base=len(set(base_L)-prev_L)+len(set(base_S)-prev_S), zm_rule=len(set(rule_L)-prev_L)+len(set(rule_S)-prev_S),
                         n_excl=len(set(base_L)-set(rule_L))+len(set(base_S)-set(rule_S)), ndx_w=g.ndx_w.iloc[0], sox_w=g.sox_w.iloc[0]))
        prev_L, prev_S = set(rule_L), set(rule_S)
    df = pd.DataFrame(rows).set_index("d0")
    df["spread_base"] = df.long_base + df.short_base; df["spread_rule"] = df.long_rule + df.short_rule
    df["d_long"] = df.long_rule - df.long_base; df["d_short"] = df.short_rule - df.short_base; df["d_spread"] = df.spread_rule - df.spread_base
    return df

def sim_summary(df, label):
    s = dict(n_tyg=int(len(df)), spread_base=round(float(df.spread_base.mean()),2), spread_rule=round(float(df.spread_rule.mean()),2),
             d_spread=round(float(df.d_spread.mean()),2), t_d_spread=round(tstat(df.d_spread),2),
             d_long=round(float(df.d_long.mean()),2), t_d_long=round(tstat(df.d_long),2), d_short=round(float(df.d_short.mean()),2), t_d_short=round(tstat(df.d_short),2),
             hit_tyg_rule_lepsza=round(float((df.d_spread>0).mean()),3), tyg_z_roznica=int((df.d_spread!=0).sum()),
             zmiany_nog_tyg_base=round(float(df.zm_base.mean()),2), zmiany_nog_tyg_rule=round(float(df.zm_rule.mean()),2), wykluczen_tyg=round(float(df.n_excl.mean()),2),
             sharpe_base=round(float(df.spread_base.mean()/df.spread_base.std()*math.sqrt(52)),2), sharpe_rule=round(float(df.spread_rule.mean()/df.spread_rule.std()*math.sqrt(52)),2))
    per_year = {str(y): dict(n=int(len(g)), d_spread=round(float(g.d_spread.mean()),2), t=round(tstat(g.d_spread),2)) for y, g in df.groupby(df.index.year)}
    s["po_latach"] = per_year
    for cn, cm in (("^NDX tydzień < −3%", df.ndx_w < -3), ("^SOX−^NDX < −3 p.p.", df.sox_w < -3), ("holdout od 2025-07", df.index >= "2025-07-01")):
        g = df[cm]; s[cn] = dict(n=int(len(g)), d_spread=round(float(g.d_spread.mean()),2), t=round(tstat(g.d_spread),2), d_long=round(float(g.d_long.mean()),2))
    p(f"\n### {label}\n")
    p(f"- spread bez reguły {s['spread_base']} p.p./tydz. (Sharpe {s['sharpe_base']}), z regułą {s['spread_rule']} (Sharpe {s['sharpe_rule']}); Δ(reguła − bez) = **{s['d_spread']}** p.p./tydz., t {s['t_d_spread']}; LONG Δ {s['d_long']} (t {s['t_d_long']}), SHORT Δ {s['d_short']} (t {s['t_d_short']}); tygodnie z różnicą {s['tyg_z_roznica']}/{s['n_tyg']}, reguła lepsza w {s['hit_tyg_rule_lepsza']} tyg.; zmiany nóg/tydz. {s['zmiany_nog_tyg_base']} → {s['zmiany_nog_tyg_rule']}; wykluczeń/tydz. {s['wykluczen_tyg']}")
    p("- po latach Δ spread: " + ", ".join(f"{y}: {v['d_spread']} (t {v['t']}, n {v['n']})" for y, v in per_year.items()))
    p("- warunkowo: " + "; ".join(f"{cn}: Δ {s[cn]['d_spread']} (t {s[cn]['t']}, n {s[cn]['n']}, LONG Δ {s[cn]['d_long']})" for cn in ("^NDX tydzień < −3%", "^SOX−^NDX < −3 p.p.", "holdout od 2025-07")))
    return s


def main():
    global OUT
    # ------------------------------------------------------------- 1. LONG, kandydaci = top kwintyl / TOP10 / TOP5
    def blok_long(cand, label, hor="fwd1"):
        res = {}
        p(f"\n## {label} — LONG, horyzont {hor}\n")
        p("| przegrana (próg p.p.) | odzyskanie | wykluczone: n / śr / t | odzyskane: n / śr / t | wygrane: n / śr | wykl. − reszta kandydatów: Δ / t / CI90 / hit tyg. |")
        p("|---|---|---|---|---|---|")
        for thr in (0, -2, -4, -8):
            for rn, rf in REC.items():
                lost = cand.prev < thr; rec = rf(cand)
                ex = grp(cand[lost & ~rec], hor); od = grp(cand[lost & rec], hor); wy = grp(cand[cand.prev >= 0], hor)
                d = diff_vs_rest(cand, lost & ~rec, hor)
                res[f"thr{thr}|{rn}"] = dict(wykluczone=ex, odzyskane=od, wygrane=wy, roznica=d)
                p(f"| {thr} | {rn} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {od['n']} / {od.get('srednia')} / {od.get('t')} | {wy['n']} / {wy.get('srednia')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} |")
        return res

    topq = CS[CS.q == 4]; top10 = CS[CS["rank"] <= 10]; top5 = CS[CS["rank"] <= 5]
    OUT["long_topq"] = blok_long(topq, "Top kwintyl momentum 6M (jak audyt)")
    OUT["long_top10"] = blok_long(top10, "TOP10 momentum 6M (najbliżej koszyka 5 nóg + rezerwy)")
    OUT["long_top5"] = blok_long(top5, "TOP5 momentum 6M (sam koszyk)")
    OUT["long_topq_fwd2"] = blok_long(topq, "Top kwintyl — horyzont 2 tyg.", "fwd2")
    OUT["long_topq_fwd4"] = blok_long(topq, "Top kwintyl — horyzont 4 tyg.", "fwd4")

    # definicja D: dwa tygodnie — przegrana w t−2, odzyskanie = tydzień t−1 relatywnie >0 (praktyka LITE W2→W3)
    p("\n## Definicja D (dwutygodniowa): przegrana w tygodniu t−2, odzyskanie = cały tydzień t−1 rel>0 — LONG top kwintyl\n")
    p("| próg | bez odzyskania (2 przegrane tyg.): n / śr / t | odzyskane (t−1 > 0): n / śr / t | Δ wykl.−reszta / t / CI90 |")
    p("|---|---|---|---|")
    OUT["long_defD"] = {}
    for thr in (0, -2, -4, -8):
        lost2 = topq.prev2 < thr
        ex = grp(topq[lost2 & (topq.prev < 0)]); od = grp(topq[lost2 & (topq.prev > 0)]); d = diff_vs_rest(topq, lost2 & (topq.prev < 0))
        OUT["long_defD"][f"thr{thr}"] = dict(wykluczone=ex, odzyskane=od, roznica=d)
        p(f"| {thr} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {od['n']} / {od.get('srednia')} / {od.get('t')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} |")

    # ------------------------------------------------------------- 2. SHORT symetrycznie (dolny kwintyl; zysk shortu = −fwd)
    def blok_short(cand, label, hor="fwd1"):
        cand = cand.copy(); cand[hor] = -cand[hor]   # zysk shortu
        res = {}
        p(f"\n## {label} — SHORT (zysk shortu = −rel), horyzont {hor}\n")
        p("| przegrana shortu (spółka rel > próg) | odzyskana słabość | wykluczone: n / śr / t | odzyskane: n / śr / t | wygrane: n / śr | wykl. − reszta: Δ / t / CI90 / hit tyg. |")
        p("|---|---|---|---|---|---|")
        for thr in (0, 2, 4, 8):
            for rn, rf in RECS.items():
                lost = cand.prev > thr; rec = rf(cand)
                ex = grp(cand[lost & ~rec], hor); od = grp(cand[lost & rec], hor); wy = grp(cand[cand.prev <= 0], hor)
                d = diff_vs_rest(cand, lost & ~rec, hor)
                res[f"thr{thr}|{rn}"] = dict(wykluczone=ex, odzyskane=od, wygrane=wy, roznica=d)
                p(f"| +{thr} | {rn} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {od['n']} / {od.get('srednia')} / {od.get('t')} | {wy['n']} / {wy.get('srednia')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} |")
        return res
    botq = CS[CS.q == 0]; bot10 = CS[CS.rank_s <= 10]
    OUT["short_botq"] = blok_short(botq, "Dolny kwintyl momentum 6M")
    OUT["short_bot10"] = blok_short(bot10, "BOTTOM10 momentum 6M")

    # ------------------------------------------------------------- 3. warunkowo: tydzień dużej przeceny indeksu / SOX / podokresy
    p("\n## Warunkowo — LONG top kwintyl, przegrana <0 i brak odzyskania (def. A), horyzont 1 tyg.\n")
    p("| warunek | n tyg. | wykluczone: n / śr / t | reszta kandydatów: śr | Δ wykl.−reszta / t / CI90 / hit tyg. |")
    p("|---|---|---|---|---|")
    OUT["warunkowo"] = {}
    mask_base = (topq.prev < 0) & ~(topq["last"] > 0)
    conds = {
     "wszystkie": topq.ndx_w.notna(),
     "^NDX tydzień < −3%": topq.ndx_w < -3, "^NDX tydzień < −2%": topq.ndx_w < -2, "^NDX tydzień > +2%": topq.ndx_w > 2,
     "^NDX tydzień w [−3%, +3%]": topq.ndx_w.abs() <= 3,
     "^SOX−^NDX tydzień < −3 p.p. (jak W6/W7)": topq.sox_w < -3, "^SOX−^NDX > +3 p.p.": topq.sox_w > 3,
     "spółka Perf.W ≤ −8% (absolutnie)": topq.prev_abs <= -8, "spółka Perf.W ≤ −12%": topq.prev_abs <= -12,
     "spółka r10 ≤ −12%": topq.r10 <= -12,
     "rok 2022": topq.d0.dt.year == 2022, "rok 2023": topq.d0.dt.year == 2023, "rok 2024": topq.d0.dt.year == 2024,
     "rok 2025": topq.d0.dt.year == 2025, "rok 2026": topq.d0.dt.year == 2026,
     "holdout od 2025-07": topq.d0 >= "2025-07-01", "do 2025-06 (in-sample)": topq.d0 < "2025-07-01",
    }
    for cn, cm in conds.items():
        sub = topq[cm]; m = mask_base[cm]
        ex = grp(sub[m]); rest = grp(sub[~m]); d = diff_vs_rest(sub, m)
        OUT["warunkowo"][cn] = dict(wykluczone=ex, reszta=rest, roznica=d)
        p(f"| {cn} | {sub.d0.nunique()} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {rest.get('srednia')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} |")

    # dla przegranej dużej (< −4) warunkowo na indeksie
    p("\n### To samo przy przegranej < −4 p.p. i < −8 p.p.\n")
    p("| warunek | próg | wykluczone: n / śr / t | Δ wykl.−reszta / t / CI90 |")
    p("|---|---|---|---|")
    OUT["warunkowo_duza"] = {}
    for thr in (-4, -8):
        mb = (topq.prev < thr) & ~(topq["last"] > 0)
        for cn in ("wszystkie", "^NDX tydzień < −3%", "^NDX tydzień > +2%", "^SOX−^NDX tydzień < −3 p.p. (jak W6/W7)", "rok 2022", "holdout od 2025-07"):
            cm = conds[cn]; sub = topq[cm]; m = mb[cm]
            ex = grp(sub[m]); d = diff_vs_rest(sub, m)
            OUT["warunkowo_duza"][f"{thr}|{cn}"] = dict(wykluczone=ex, roznica=d)
            p(f"| {cn} | {thr} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} |")

    # ------------------------------------------------------------- 4. sito Perf.W ≤ −8% i filtr W8 (kandydaci spoza koszyka)
    p("\n## Sito Perf.W ≤ −8% (B1 pkt 5) i filtr W8 (Perf.W silnie ujemne + ostatnia sesja rel ≤ 0) — LONG\n")
    p("| kandydaci | filtr | n / śr / t wykluczonych | Δ wykl.−reszta / t / CI90 / hit tyg. | horyzont |")
    p("|---|---|---|---|---|")
    OUT["sito"] = {}
    for lab, cand in (("top kwintyl", topq), ("TOP10", top10), ("TOP15", CS[CS["rank"] <= 15])):
        for fn, fm in (("Perf.W ≤ −8%", cand.prev_abs <= -8), ("Perf.W ≤ −8% i ostatnia sesja rel ≤ 0 (filtr W8)", (cand.prev_abs <= -8) & ~(cand["last"] > 0)),
                       ("Perf.W ≤ −15% i ostatnia sesja rel ≤ 0 (jak SNDK/STX/AMAT W8)", (cand.prev_abs <= -15) & ~(cand["last"] > 0)),
                       ("rel tydzień ≤ −8 p.p. i ostatnia sesja rel ≤ 0", (cand.prev <= -8) & ~(cand["last"] > 0))):
            for hor in ("fwd1", "fwd2"):
                ex = grp(cand[fm], hor); d = diff_vs_rest(cand, fm, hor)
                OUT["sito"][f"{lab}|{fn}|{hor}"] = dict(wykluczone=ex, roznica=d)
                p(f"| {lab} | {fn} | {ex['n']} / {ex.get('srednia')} / {ex.get('t')} | {d.get('roznica')} / {d.get('t')} / {d.get('ci90')} / {d.get('hit_tyg')} | {hor} |")

    # sito Perf.W dla SHORT (D2: nie shortuj po kolapsie) — dla porządku
    p("\n### Dla porządku: sito Perf.W ≤ −8% po stronie SHORT (dolny kwintyl; zysk shortu)\n")
    bq = botq.copy(); bq["fwd1"] = -bq["fwd1"]
    for fn, fm in (("Perf.W ≤ −8%", bq.prev_abs <= -8), ("r10 ≤ −12%", bq.r10 <= -12)):
        ex = grp(bq[fm]); d = diff_vs_rest(bq, fm)
        OUT["sito"][f"SHORT|{fn}"] = dict(wykluczone=ex, roznica=d)
        p(f"- {fn}: wykluczone n={ex['n']} śr {ex.get('srednia')} t {ex.get('t')}; Δ wykl.−reszta {d.get('roznica')} (t {d.get('t')}, CI90 {d.get('ci90')}) — ujemna Δ = sito pomaga shortowi")

    # ------------------------------------------------------------- 5. symulacja portfela TOP5/BOTTOM5 z regułą i bez (stan: „poza koszykiem do odzyskania”)
    p("\n## Symulacja portfela: TOP5 LONG / BOTTOM5 SHORT momentum 6M co tydzień, reguła vs bez reguły\n")
    OUT["symulacja"] = {}
    RL = {"A": lambda r: r["last"] > 0, "B": lambda r: r.n_pos3 >= 2, "C": lambda r: r.rel3 > 0}
    RS = {"A": lambda r: r["last"] < 0, "B": lambda r: r.n_pos3 <= 1, "C": lambda r: r.rel3 < 0}
    for key in ("A", "B", "C"):
        df = simulate(RL[key], RS[key], thr=0.0)
        OUT["symulacja"][f"obie_strony_def{key}_thr0"] = sim_summary(df, f"Obie strony, odzyskanie def. {key}, przegrana < 0, z pamięcią wykluczeń")
        if key == "A": df.to_csv(f"{BASE}/analiza/weryfikacja_C6_sim_A.csv")
    for thr in (-2.0, -4.0, -8.0):
        df = simulate(RL["A"], RS["A"], thr=thr)
        OUT["symulacja"][f"obie_strony_defA_thr{thr}"] = sim_summary(df, f"Obie strony, def. A, przegrana < {thr} p.p.")
    df = simulate(RL["A"], RS["A"], thr=0.0, side_rule=("L",)); OUT["symulacja"]["tylko_long_defA"] = sim_summary(df, "Tylko LONG, def. A, przegrana < 0")
    df = simulate(RL["A"], RS["A"], thr=0.0, side_rule=("S",)); OUT["symulacja"]["tylko_short_defA"] = sim_summary(df, "Tylko SHORT, def. A, przegrana shortu > 0")
    df = simulate(RL["A"], RS["A"], thr=0.0, stateful=False); OUT["symulacja"]["bezstanowa_defA"] = sim_summary(df, "Obie strony, def. A, BEZ pamięci (wykluczenie tylko na 1 tydzień)")
    df = simulate(RL["A"], RS["A"], thr=0.0, w8_filter=True); OUT["symulacja"]["defA_plus_filtrW8"] = sim_summary(df, "Obie strony, def. A + filtr W8 dla kandydatów (Perf.W ≤ −8% i ostatnia sesja rel ≤ 0)")
    df = simulate(RL["A"], RS["A"], thr=0.0, horizon_col="fwd2"); OUT["symulacja"]["defA_fwd2"] = sim_summary(df, "Obie strony, def. A, horyzont 2 tyg. (nakładające się)")
    df = simulate(RL["A"], RS["A"], thr=0.0, topn=10); OUT["symulacja"]["defA_top10"] = sim_summary(df, "Obie strony, def. A, koszyk 10/10")

    # wariant: wszystkie 5 przesunięć okien po 5 sesji (sprawdzenie, czy wynik zależy od kotwicy tygodnia)
    p("\n## Zależność od kotwicy okna: 5 przesunięć okien 5-sesyjnych (top kwintyl, def. A, przegrana < 0, Δ wykl.−reszta)\n")
    OUT["kotwice"] = {}
    for off in range(5):
        we = np.arange(off, len(dates), 5)
        cso = build_cs(we); tq = cso[cso.q == 4]
        m = (tq.prev < 0) & ~(tq["last"] > 0)
        ex = grp(tq[m]); od = grp(tq[(tq.prev < 0) & (tq["last"] > 0)]); d = diff_vs_rest(tq, m)
        m4 = (tq.prev < -4) & ~(tq["last"] > 0); d4 = diff_vs_rest(tq, m4); ex4 = grp(tq[m4])
        OUT["kotwice"][off] = dict(wykluczone=ex, odzyskane=od, roznica=d, wykluczone_m4=ex4, roznica_m4=d4)
        p(f"- przesunięcie {off}: wykluczone n={ex['n']} śr {ex.get('srednia')} (t {ex.get('t')}), odzyskane śr {od.get('srednia')}, Δ wykl.−reszta {d.get('roznica')} (t {d.get('t')}, CI90 {d.get('ci90')}); przy przegranej < −4: n={ex4['n']} śr {ex4.get('srednia')}, Δ {d4.get('roznica')} (t {d4.get('t')})")

    # ------------------------------------------------------------- 6. in-sample: rozkład delt zamienników (z audyt_regul_wykluczenia.csv)
    ex = pd.read_csv(f"{BASE}/analiza/audyt_regul_wykluczenia.csv")
    mask = ex.rule.str.contains("odzyskanej|wypada po przegranej|wraca po odzyskaniu|słabsza relatywnie|przegrana W4", regex=True)
    sub = ex[mask]
    dl = sub.delta_na_nodze.dropna()
    OUT["in_sample"] = dict(n=int(len(sub)), n_zamiennikow=int(len(dl)), srednia_delta=round(float(dl.mean()),2), mediana_delta=round(float(dl.median()),2),
                           zamiennik_lepszy=int((dl>0).sum()), bez_LITE_W5_srednia=round(float(dl[~((sub.week=="W5")&(sub.ticker=="LITE"))].mean()),2),
                           wykluczona_dodatnia=int((sub.rel_excl>0).sum()), srednia_rel_wykl=round(float(sub.rel_excl.mean()),2), lista=sub[["week","ticker","side","rel_excl","repl","rel_repl","delta_na_nodze"]].to_dict("records"))
    p(f"\n## In-sample W2–W7 (audyt_regul_wykluczenia.csv): n={len(sub)} wykluczeń, {len(dl)} z zamiennikiem; Δ(zamiennik − wykluczona) średnia {OUT['in_sample']['srednia_delta']}, mediana {OUT['in_sample']['mediana_delta']}, zamiennik lepszy w {OUT['in_sample']['zamiennik_lepszy']}/{len(dl)}; bez LITE W5 średnia {OUT['in_sample']['bez_LITE_W5_srednia']}; wykluczona noga dodatnia w {OUT['in_sample']['wykluczona_dodatnia']}/{len(sub)}")

    json.dump(OUT, open(f"{BASE}/analiza/weryfikacja_C6_wyniki.json", "w"), ensure_ascii=False, indent=1, default=str)
    open(f"{BASE}/analiza/weryfikacja_C6_out.md", "w").write("\n".join(md))

if __name__ == "__main__":
    main()
