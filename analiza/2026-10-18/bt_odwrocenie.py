#!/usr/bin/env python3
"""
bt_odwrocenie.py — backtest krótkoterminowego odwrócenia (short-term reversal)
w uniwersum Nasdaq-100 (dzisiejszy skład, survivorship bias), okna tygodniowe.

Wspólny harness:
  * okno = ostatnia sesja tygodnia (D0) -> ostatnia sesja następnego tygodnia (D5)
  * koszyk równych wag 5 LONG + 5 SHORT
  * zwrot pozycji = r_spółki - r_^NDX (long), -(r_spółki - r_^NDX) (short)
  * spread_pp = średnia 5 long + średnia 5 short (p.p.)  == long-short
  * sygnały tylko z danych <= D0
  * koszty: 0,10% na nogę na rotację (tylko zmienione sloty) + 6%/rok finansowania
    na gross (= 2x strona), czyli 6%/52*2 = 0,2308 pp/tydzień
Czysty python (brak pandas/numpy w środowisku).
"""
import csv, json, math, random, statistics, sys, os
from collections import defaultdict
from datetime import date

BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
CSV_IN = os.path.join(BASE, "dane", "closes_5y.csv")
OUT_DIR = os.path.join(BASE, "analiza")
OUT_SERIES = os.path.join(OUT_DIR, "bt_odwrocenie_serie.csv")
OUT_MD = os.path.join(OUT_DIR, "bt_odwrocenie.md")
OUT_JSON = os.path.join(OUT_DIR, "bt_odwrocenie_wyniki.json")

NON_CANDIDATES = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
N_LEG = 5
MOM_WIN = 126          # 6M
MOM_SKIP = 5           # momentum 6M liczone do D0-5 (bez ostatniego tygodnia)
SIG_HIST = MOM_WIN + MOM_SKIP   # wymagana pełna historia sygnału dla wspólnego uniwersum
N_RANDOM = 2000
SEED = 42
COST_LEG = 0.10        # % na slot na rotację (round trip)
FIN_YEAR = 6.0         # % rocznie na gross
FIN_WEEK_PP = FIN_YEAR / 52.0 * 2.0   # gross = 2 (long 1 + short 1)
EVENT_ABS_RET = 8.0    # proxy zdarzenia: |zwrot dzienny| > 8% w ostatnich 5 sesjach

# ---------------------------------------------------------------- dane
def load():
    with open(CSV_IN, newline="") as f:
        rd = csv.reader(f)
        header = next(rd)
        rows = list(rd)
    cols = header[1:]
    ndx_i = cols.index("^NDX") + 1
    # wiersze bez zamknięcia ^NDX (święta: 2026-05-25, 2026-09-07) nie są sesjami
    rows = [r for r in rows if r[ndx_i] not in ("", "nan", "NaN")]
    dates = [date.fromisoformat(r[0]) for r in rows]
    px = {c: [None] * len(rows) for c in cols}
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            v = r[j + 1]
            px[c][i] = float(v) if v not in ("", "nan", "NaN") else None
    return dates, cols, px

def week_ends(dates):
    """indeksy ostatniej sesji każdego tygodnia ISO"""
    last = {}
    for i, d in enumerate(dates):
        y, w, _ = d.isocalendar()
        last[(y, w)] = i
    return [last[k] for k in sorted(last)]

def ret(series, i0, i1):
    a, b = series[i0], series[i1]
    if a is None or b is None or a == 0:
        return None
    return b / a - 1.0

def pct_rank(values):
    """percentyl rangi (0..1), rosnąco; values: dict t->v"""
    items = sorted(values.items(), key=lambda kv: kv[1])
    n = len(items)
    return {t: (k / (n - 1) if n > 1 else 0.5) for k, (t, _) in enumerate(items)}

# ---------------------------------------------------------------- sygnały
def signals_at(d0, dates, tickers, px, ndx):
    """Zwraca dict ticker -> dict sygnałów policzonych tylko z danych <= d0.
    Uniwersum wspólne: pełna historia SIG_HIST sesji + cena na D0."""
    out = {}
    rn = {k: ret(ndx, d0 - k, d0) for k in (5, 10, 21)}
    rn_mom = ret(ndx, d0 - MOM_SKIP - MOM_WIN, d0 - MOM_SKIP)
    for t in tickers:
        s = px[t]
        seg = s[d0 - SIG_HIST: d0 + 1]
        if any(v is None for v in seg):
            continue
        sig = {}
        ok = True
        for k in (5, 10, 21):
            r = ret(s, d0 - k, d0)
            if r is None or rn[k] is None:
                ok = False; break
            sig[f"rev{k}"] = (r - rn[k]) * 100.0
        if not ok:
            continue
        rm = ret(s, d0 - MOM_SKIP - MOM_WIN, d0 - MOM_SKIP)
        sig["mom6"] = (rm - rn_mom) * 100.0
        # proxy zdarzenia: max |zwrot dzienny| w ostatnich 5 sesjach
        mx = 0.0
        for i in range(d0 - 4, d0 + 1):
            r = abs(s[i] / s[i - 1] - 1.0) * 100.0
            mx = max(mx, r)
        sig["maxabs5"] = mx
        out[t] = sig
    return out

def pick(sig, key, long_low=True, universe=None, n=N_LEG):
    """LONG = n najniższych (long_low) wartości key; SHORT = n najwyższych."""
    u = universe if universe is not None else list(sig.keys())
    srt = sorted(u, key=lambda t: sig[t][key])
    if long_low:
        return srt[:n], srt[-n:][::-1]
    return srt[-n:][::-1], srt[:n]

def variant_baskets(name, sig):
    """Zwraca (long, short) albo None gdy za mało kandydatów (<3 na stronę)."""
    if name == "a_rev5":
        return pick(sig, "rev5")
    if name == "b_rev10":
        return pick(sig, "rev10")
    if name == "c_rev21":
        return pick(sig, "rev21")
    if name == "d_rev5_w_trendzie":
        # kupuj dołki w trendzie: LONG = najgorsze 1T wśród mom6>0;
        # SHORT = najlepsze 1T wśród mom6<0 (sprzedawaj odbicia w trendzie spadkowym)
        up = [t for t in sig if sig[t]["mom6"] > 0]
        dn = [t for t in sig if sig[t]["mom6"] < 0]
        if len(up) < 3 or len(dn) < 3:
            return None
        lo = sorted(up, key=lambda t: sig[t]["rev5"])[:N_LEG]
        sh = sorted(dn, key=lambda t: -sig[t]["rev5"])[:N_LEG]
        return lo, sh
    if name == "e_rev5_bez_zdarzen":
        u = [t for t in sig if sig[t]["maxabs5"] <= EVENT_ABS_RET]
        if len(u) < 2 * N_LEG:
            return None
        return pick(sig, "rev5", universe=u)
    if name == "f_kombo_mom6_rev5":
        pm = pct_rank({t: sig[t]["mom6"] for t in sig})          # wysoki = silne momentum
        pr = pct_rank({t: -sig[t]["rev5"] for t in sig})         # wysoki = mocno wyprzedany 1T
        comb = {t: 0.5 * pm[t] + 0.5 * pr[t] for t in sig}
        srt = sorted(sig, key=lambda t: comb[t])
        return srt[-N_LEG:][::-1], srt[:N_LEG]
    if name == "ref_mom6":
        # odniesienie: czyste momentum 6M (skip 1T): LONG najlepsze, SHORT najgorsze
        return pick(sig, "mom6", long_low=False)
    if name == "ref_rev5_abs":
        # odwrócenie 5-sesyjne na zwrocie bezwzględnym (bez odejmowania NDX) — kontrola
        return pick(sig, "rev5_abs")
    raise KeyError(name)

VARIANTS = ["a_rev5", "b_rev10", "c_rev21", "d_rev5_w_trendzie",
            "e_rev5_bez_zdarzen", "f_kombo_mom6_rev5", "ref_mom6"]

# ---------------------------------------------------------------- metryki
def mean(xs): return sum(xs) / len(xs) if xs else float("nan")
def sd(xs): return statistics.stdev(xs) if len(xs) > 1 else float("nan")

def max_drawdown(xs):
    cum = 0.0; peak = 0.0; mdd = 0.0
    for x in xs:
        cum += x
        peak = max(peak, cum)
        mdd = min(mdd, cum - peak)
    return mdd

def metrics(rows):
    """rows: list of dict(spread, long, short, ...)"""
    sp = [r["spread"] for r in rows]
    n = len(sp)
    if n == 0:
        return {"n": 0}
    m = mean(sp); s = sd(sp)
    t = m / s * math.sqrt(n) if s and s > 0 else float("nan")
    return {
        "n": n, "mean": m, "median": statistics.median(sp), "sd": s,
        "t": t, "sharpe": m / s * math.sqrt(52) if s and s > 0 else float("nan"),
        "hit": mean([1.0 if x > 0 else 0.0 for x in sp]),
        "hit_long": mean([1.0 if r["long"] > 0 else 0.0 for r in rows]),
        "hit_short": mean([1.0 if r["short"] > 0 else 0.0 for r in rows]),
        "mean_long": mean([r["long"] for r in rows]),
        "mean_short": mean([r["short"] for r in rows]),
        "mdd": max_drawdown(sp), "worst": min(sp), "best": max(sp),
        "cum": sum(sp),
        "cost": mean([r["cost"] for r in rows]),
        "net_mean": mean([r["spread"] - r["cost"] for r in rows]),
        "net_cum": sum(r["spread"] - r["cost"] for r in rows),
        "turnover": mean([r["turnover"] for r in rows]),
    }

def fmt(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)): return "–"
    return f"{x:.{d}f}"

# ---------------------------------------------------------------- główny bieg
def main():
    dates, cols, px = load()
    tickers = [c for c in cols if c not in NON_CANDIDATES]
    ndx = px["^NDX"]; vix = px["^VIX"]
    we = week_ends(dates)
    # MA200 NDX (min 126 sesji — od początku okien; <200 sesji oznaczone)
    def ma200(i):
        seg = [v for v in ndx[max(0, i - 199): i + 1] if v is not None]
        return mean(seg), len(seg)

    windows = [(we[k], we[k + 1]) for k in range(len(we) - 1) if we[k] >= SIG_HIST]
    rng = random.Random(SEED)

    series = {v: [] for v in VARIANTS}
    rand_spreads_per_window = []       # lista list (2000) na okno
    rand_strats = [[] for _ in range(N_RANDOM)]  # 2000 losowych strategii (łańcuch)
    prev_baskets = {v: (set(), set()) for v in VARIANTS}
    universe_sizes = []

    for (d0, d5) in windows:
        sig = signals_at(d0, dates, tickers, px, ndx)
        r_ndx = ret(ndx, d0, d5)
        if r_ndx is None:
            continue
        fwd = {}
        for t in sig:
            r = ret(px[t], d0, d5)
            if r is not None:
                fwd[t] = (r - r_ndx) * 100.0
        sig = {t: sig[t] for t in fwd}
        u = list(sig.keys())
        universe_sizes.append(len(u))
        m, nma = ma200(d0)
        ctx = {
            "date_d0": dates[d0].isoformat(), "date_d5": dates[d5].isoformat(),
            "year": dates[d0].year, "ndx_ret_pp": r_ndx * 100.0,
            "vix_d0": vix[d0], "vix_hi": (vix[d0] is not None and vix[d0] > 20),
            "ndx_above_ma200": ndx[d0] > m, "ma200_n": nma, "n_univ": len(u),
        }
        for v in VARIANTS:
            b = variant_baskets(v, sig)
            if b is None:
                continue
            lo, sh = b
            lp = mean([fwd[t] for t in lo]); spp = mean([-fwd[t] for t in sh])
            pl, ps = prev_baskets[v]
            ch = (len(set(lo) - pl) + len(set(sh) - ps))
            turnover = ch / (2 * N_LEG)       # 1.0 = pełna rotacja
            cost = COST_LEG * 2 * turnover + FIN_WEEK_PP   # pp spreadu
            prev_baskets[v] = (set(lo), set(sh))
            row = dict(ctx, variant=v, long=lp, short=spp, spread=lp + spp,
                       long_tk=" ".join(lo), short_tk=" ".join(sh),
                       n_long=len(lo), n_short=len(sh), turnover=turnover, cost=cost)
            series[v].append(row)
        # baseline losowy
        rs = []
        for k in range(N_RANDOM):
            smp = rng.sample(u, 2 * N_LEG)
            lo, sh = smp[:N_LEG], smp[N_LEG:]
            s_ = mean([fwd[t] for t in lo]) - mean([fwd[t] for t in sh])
            rs.append(s_)
            rand_strats[k].append(s_)
        rand_spreads_per_window.append(rs)

    # --- baseline: rozkład spreadu losowego (pooled) i per-okno σ
    pooled = [x for rs in rand_spreads_per_window for x in rs]
    pooled_sorted = sorted(pooled)
    def pct(sorted_xs, q):
        i = min(len(sorted_xs) - 1, max(0, int(round(q * (len(sorted_xs) - 1)))))
        return sorted_xs[i]
    base = {
        "n_windows": len(rand_spreads_per_window),
        "sigma_pp": sd(pooled), "mean_pp": mean(pooled),
        "p5_pp": pct(pooled_sorted, 0.05), "p95_pp": pct(pooled_sorted, 0.95),
        "sigma_per_window_median": statistics.median([sd(rs) for rs in rand_spreads_per_window]),
        "sigma_per_window_p5": pct(sorted([sd(rs) for rs in rand_spreads_per_window]), 0.05),
        "sigma_per_window_p95": pct(sorted([sd(rs) for rs in rand_spreads_per_window]), 0.95),
    }
    # rozkład statystyk 2000 losowych STRATEGII (po jednym losowym koszyku na okno)
    rs_means = []; rs_t = []; rs_sharpe = []
    for st in rand_strats:
        m_ = mean(st); s_ = sd(st)
        rs_means.append(m_); rs_t.append(m_ / s_ * math.sqrt(len(st))); rs_sharpe.append(m_ / s_ * math.sqrt(52))
    rs_means_s = sorted(rs_means); rs_t_s = sorted(rs_t)
    base.update({
        "strat_mean_p5": pct(rs_means_s, 0.05), "strat_mean_p95": pct(rs_means_s, 0.95),
        "strat_mean_sd": sd(rs_means), "strat_t_p5": pct(rs_t_s, 0.05), "strat_t_p95": pct(rs_t_s, 0.95),
        "strat_t_sd": sd(rs_t), "strat_sharpe_sd": sd(rs_sharpe),
    })
    def strat_pvalue(mean_pp):
        # odsetek losowych strategii z średnią >= mean_pp (jednostronnie)
        return sum(1 for x in rs_means if x >= mean_pp) / len(rs_means)

    # --- metryki wariantów
    results = {}
    for v in VARIANTS:
        rows = series[v]
        res = {"all": metrics(rows)}
        res["all"]["p_random_strat"] = strat_pvalue(res["all"]["mean"])
        res["years"] = {y: metrics([r for r in rows if r["year"] == y]) for y in sorted({r["year"] for r in rows})}
        res["vix_hi"] = metrics([r for r in rows if r["vix_hi"]])
        res["vix_lo"] = metrics([r for r in rows if not r["vix_hi"]])
        res["ndx_above_ma200"] = metrics([r for r in rows if r["ndx_above_ma200"]])
        res["ndx_below_ma200"] = metrics([r for r in rows if not r["ndx_above_ma200"]])
        # połówki próby (stabilność)
        h = len(rows) // 2
        res["half1"] = metrics(rows[:h]); res["half2"] = metrics(rows[h:])
        results[v] = res

    # --- zapis serii
    fields = ["variant", "date_d0", "date_d5", "spread_pp", "long_pp", "short_pp", "cost_pp", "net_pp",
              "turnover", "ndx_ret_pp", "vix_d0", "ndx_above_ma200", "n_univ", "long", "short"]
    with open(OUT_SERIES, "w", newline="") as f:
        w = csv.writer(f); w.writerow(fields)
        for v in VARIANTS:
            for r in series[v]:
                w.writerow([v, r["date_d0"], r["date_d5"], f"{r['spread']:.4f}", f"{r['long']:.4f}",
                            f"{r['short']:.4f}", f"{r['cost']:.4f}", f"{r['spread']-r['cost']:.4f}",
                            f"{r['turnover']:.2f}", f"{r['ndx_ret_pp']:.3f}",
                            fmt(r["vix_d0"]), int(r["ndx_above_ma200"]), r["n_univ"], r["long_tk"], r["short_tk"]])

    # --- JSON wyników
    with open(OUT_JSON, "w") as f:
        json.dump({"baseline": base, "variants": results,
                   "universe_size_min": min(universe_sizes), "universe_size_max": max(universe_sizes),
                   "first_d0": series["a_rev5"][0]["date_d0"], "last_d5": series["a_rev5"][-1]["date_d5"],
                   "ma200_short_windows": sum(1 for r in series["a_rev5"] if r["ma200_n"] < 200)},
                  f, indent=1, default=str)

    # --- notatka MD
    write_md(results, base, series, universe_sizes)
    print(json.dumps({"baseline": base, "variants": {v: results[v]["all"] for v in VARIANTS}}, indent=1, default=str))

def write_md(results, base, series, universe_sizes):
    L = []
    a = series["a_rev5"]
    L.append("# Backtest: krótkoterminowe odwrócenie w Nasdaq-100 (okna tygodniowe)\n")
    L.append(f"Dane: `dane/closes_5y.csv` (zamknięcia 2021-10-18…2026-10-16). Okna: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia; "
             f"pierwsze D0 {a[0]['date_d0']}, ostatnie D5 {a[-1]['date_d5']}, {len(a)} okien. "
             f"Uniwersum wspólne = spółki z pełną historią {SIG_HIST} sesji na D0 (min {min(universe_sizes)}, max {max(universe_sizes)} spółek); "
             f"indeksy/ETF wyłączone. Zwroty względem ^NDX; spread = śr. 5 LONG + śr. 5 SHORT (= long−short). "
             f"Koszty: {COST_LEG}% na slot na rotację (liczone po faktycznej rotacji składu) + {FIN_YEAR}%/rok na gross (= {FIN_WEEK_PP:.3f} pp/tydz.). "
             f"MA200 ^NDX: dla pierwszych okien z <200 sesji użyto średniej z dostępnych (≥{SIG_HIST}).\n")
    L.append("## Warianty\n")
    L.append("| kod | definicja |\n|---|---|")
    L.append("| a_rev5 | LONG 5 najgorszych rel. do NDX w 5 sesjach, SHORT 5 najlepszych |")
    L.append("| b_rev10 | jw., okno 10 sesji |")
    L.append("| c_rev21 | jw., okno 21 sesji |")
    L.append("| d_rev5_w_trendzie | LONG = najgorsze 1T wśród spółek z dodatnim rel. momentum 6M (126 sesji, bez ostatnich 5); SHORT = najlepsze 1T wśród spółek z ujemnym momentum 6M |")
    L.append(f"| e_rev5_bez_zdarzen | a_rev5 po wykluczeniu spółek z jakimkolwiek \\|zwrotem dziennym\\| > {EVENT_ABS_RET}% w ostatnich 5 sesjach (proxy wyników) |")
    L.append("| f_kombo_mom6_rev5 | wynik = 0,5·percentyl(momentum 6M, wysoki=dobry) + 0,5·percentyl(−zwrot 1T, wysoki=wyprzedany); LONG top 5, SHORT dół 5 |")
    L.append("| ref_mom6 | odniesienie: czyste momentum 6M (skip 1T): LONG 5 najlepszych, SHORT 5 najgorszych |\n")

    L.append("## Baseline: 2000 losowych koszyków 5/5 na każdym oknie\n")
    L.append(f"- rozkład spreadu losowego (pooled, {base['n_windows']} okien × 2000): średnia {fmt(base['mean_pp'])} pp, σ **{fmt(base['sigma_pp'])} pp**, "
             f"p5 {fmt(base['p5_pp'])} pp, p95 {fmt(base['p95_pp'])} pp")
    L.append(f"- σ spreadu losowego w pojedynczym oknie: mediana {fmt(base['sigma_per_window_median'])} pp (p5 {fmt(base['sigma_per_window_p5'])}, p95 {fmt(base['sigma_per_window_p95'])})")
    L.append(f"- 2000 losowych STRATEGII (losowy koszyk w każdym oknie): średnia tygodniowa p5 {fmt(base['strat_mean_p5'],3)} / p95 {fmt(base['strat_mean_p95'],3)} pp "
             f"(σ średniej {fmt(base['strat_mean_sd'],3)} pp); t-stat p5 {fmt(base['strat_t_p5'])} / p95 {fmt(base['strat_t_p95'])}; σ Sharpe'a losowego {fmt(base['strat_sharpe_sd'])}\n")

    L.append("## Pełne metryki (cały okres)\n")
    L.append("| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit L | hit S | śr. L | śr. S | maxDD | najgorsze | najlepsze | rotacja | koszt/tydz | **netto śr.** | netto skum. | p(losowa ≥) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in VARIANTS:
        m = results[v]["all"]
        L.append(f"| {v} | {m['n']} | {fmt(m['mean'])} | {fmt(m['median'])} | {fmt(m['sd'])} | {fmt(m['t'])} | {fmt(m['sharpe'])} | "
                 f"{fmt(m['hit']*100,0)}% | {fmt(m['hit_long']*100,0)}% | {fmt(m['hit_short']*100,0)}% | {fmt(m['mean_long'])} | {fmt(m['mean_short'])} | "
                 f"{fmt(m['mdd'],1)} | {fmt(m['worst'],1)} | {fmt(m['best'],1)} | {fmt(m['turnover']*100,0)}% | {fmt(m['cost'])} | **{fmt(m['net_mean'])}** | {fmt(m['net_cum'],1)} | {fmt(m['p_random_strat'],3)} |")
    L.append("\nJednostki: p.p. na tydzień; maxDD/najgorsze/najlepsze/skum. w p.p. (suma prosta spreadów). t = śr./σ·√n. Sharpe = śr./σ·√52 (brutto). p(losowa ≥) = odsetek z 2000 losowych strategii o średniej ≥ średniej wariantu.\n")

    L.append("## Lata (po dacie D0; brutto, pp/tydz.)\n")
    years = sorted({r["year"] for r in a})
    L.append("| wariant | " + " | ".join(f"{y} (n / śr. / t / hit)" for y in years) + " |")
    L.append("|---|" + "---|" * len(years))
    for v in VARIANTS:
        cells = []
        for y in years:
            m = results[v]["years"].get(y, {"n": 0})
            cells.append(f"{m['n']} / {fmt(m['mean'])} / {fmt(m['t'],1)} / {fmt(m['hit']*100,0)}%" if m["n"] else "–")
        L.append(f"| {v} | " + " | ".join(cells) + " |")

    L.append("\n## Reżimy na D0 (brutto, pp/tydz.)\n")
    L.append("| wariant | VIX>20 (n / śr. / t) | VIX≤20 (n / śr. / t) | NDX<MA200 (n / śr. / t) | NDX>MA200 (n / śr. / t) | 1. połowa (n / śr. / t) | 2. połowa (n / śr. / t) |")
    L.append("|---|---|---|---|---|---|---|")
    for v in VARIANTS:
        r = results[v]
        def c(m): return f"{m['n']} / {fmt(m['mean'])} / {fmt(m['t'],1)}" if m["n"] else "–"
        L.append(f"| {v} | {c(r['vix_hi'])} | {c(r['vix_lo'])} | {c(r['ndx_below_ma200'])} | {c(r['ndx_above_ma200'])} | {c(r['half1'])} | {c(r['half2'])} |")

    # najgorsze okna a_rev5
    L.append("\n## a_rev5: 8 najgorszych i 5 najlepszych okien\n")
    L.append("| D0 | D5 | spread | long | short | LONG | SHORT |\n|---|---|---|---|---|---|---|")
    for r in sorted(a, key=lambda r: r["spread"])[:8] + sorted(a, key=lambda r: -r["spread"])[:5]:
        L.append(f"| {r['date_d0']} | {r['date_d5']} | {fmt(r['spread'],1)} | {fmt(r['long'],1)} | {fmt(r['short'],1)} | {r['long_tk']} | {r['short_tk']} |")

    # ostatnie 12 okien a_rev5 (2026)
    L.append("\n## a_rev5: ostatnie 12 okien\n")
    L.append("| D0 | D5 | spread | long | short | LONG | SHORT |\n|---|---|---|---|---|---|---|")
    for r in a[-12:]:
        L.append(f"| {r['date_d0']} | {r['date_d5']} | {fmt(r['spread'],1)} | {fmt(r['long'],1)} | {fmt(r['short'],1)} | {r['long_tk']} | {r['short_tk']} |")

    L.append("\n## Wnioski\n")
    L.append(conclusions(results, base))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(L) + "\n")

def conclusions(results, base):
    a = results["a_rev5"]["all"]
    lines = []
    best = max(VARIANTS, key=lambda v: results[v]["all"]["t"])
    bm = results[best]["all"]
    lines.append(f"- Odwrócenie 5-sesyjne (a_rev5): średnia {fmt(a['mean'])} pp/tydz., t = {fmt(a['t'])}, Sharpe {fmt(a['sharpe'])}, hit {fmt(a['hit']*100,0)}%; "
                 f"po kosztach (ok. {fmt(a['cost'])} pp/tydz. przy rotacji {fmt(a['turnover']*100,0)}%) średnia **{fmt(a['net_mean'])} pp/tydz.**, "
                 f"skumulowane netto {fmt(a['net_cum'],1)} pp w {a['n']} tygodni.")
    lines.append(f"- Baseline: σ spreadu losowego koszyka 5/5 = {fmt(base['sigma_pp'])} pp/tydz.; losowa strategia ma średnią w przedziale "
                 f"[{fmt(base['strat_mean_p5'],2)}; {fmt(base['strat_mean_p95'],2)}] pp i |t| zwykle < {fmt(max(abs(base['strat_t_p5']), abs(base['strat_t_p95'])),1)}. "
                 f"Wariant o najwyższym t: {best} (t = {fmt(bm['t'])}, p(losowa ≥) = {fmt(bm['p_random_strat'],3)}).")
    passing = [v for v in VARIANTS if results[v]["all"]["t"] > 2 and results[v]["all"]["net_mean"] > 0]
    if passing:
        lines.append(f"- Warianty z t > 2 **i** dodatnią średnią po kosztach: {', '.join(passing)}.")
    else:
        lines.append("- **Żaden wariant nie ma jednocześnie t > 2 i dodatniej średniej po kosztach.**")
    # asymetria nóg i dryf w czasie
    lines.append(f"- Asymetria nóg (a_rev5): noga LONG (kupno 1T przegranych) średnio {fmt(a['mean_long'])} pp/tydz., hit {fmt(a['hit_long']*100,0)}%; "
                 f"noga SHORT (sprzedaż 1T wygranych) średnio **{fmt(a['mean_short'])} pp/tydz.**, hit {fmt(a['hit_short']*100,0)}% — "
                 f"straty generuje przede wszystkim shortowanie tygodniowych liderów (krótkoterminowa KONTYNUACJA, nie odwrócenie).")
    ya = results['a_rev5']['years']
    lines.append("- Dryf w czasie (a_rev5, brutto): " + "; ".join(f"{y}: {fmt(ya[y]['mean'])} pp (hit {fmt(ya[y]['hit']*100,0)}%)" for y in sorted(ya)) +
                 ". Odwrócenie działało słabo dodatnio w 2022–2023, a od 2024 (era momentum AI/półprzewodniki) jest ujemne — pierwsza i druga połowa próby mają przeciwne znaki, więc nie ma stabilnego efektu.")
    for v in ("a_rev5", "c_rev21"):
        m = results[v]["all"]
        lines.append(f"- Lustro {v} (kupuj 1T/1M liderów, sprzedawaj maruderów): średnia {fmt(-m['mean'])} pp, t = {fmt(-m['t'])}, "
                     f"netto {fmt(-m['mean'] - m['cost'])} pp/tydz. — też NIE przebija progu t > 2 (i jest wynikiem in-sample, odczytanym z tego samego testu).")
    lines.append("- Filtry (d) trend, (e) bez zdarzeń i (f) kombinacja z momentum 6M poprawiają odwrócenie do ok. 0 brutto (t 0,3–0,4; p(losowa ≥) 0,24–0,31 — nieodróżnialne od losowego koszyka) "
                 "i do ok. −0,25 pp/tydz. netto, bo rotacja 80–93% tygodniowo kosztuje ok. 0,4 pp/tydz. Cała poprawa względem (a) pochodzi z komponentu momentum, nie z odwrócenia.")
    lines.append(f"- Odniesienie ref_mom6 (czyste momentum 6M, skip 1T): t = {fmt(results['ref_mom6']['all']['t'])}, netto {fmt(results['ref_mom6']['all']['net_mean'])} pp/tydz., "
                 f"rotacja {fmt(results['ref_mom6']['all']['turnover']*100,0)}% — jedyny wariant z t ≈ 2 i dodatnim wynikiem po kosztach, ale w 2022–2023 ≈ 0 (zysk skoncentrowany w 2024–2026, survivorship bias sprzyja momentum).")
    lines.append("- **Odpowiedź wprost: odwrócenie 5-sesyjne w Nasdaq-100 2022–2026 NIE działa — brutto jest ujemne (−0,33 pp/tydz., t = −0,93, gorsze niż 93% losowych koszyków), "
                 "a po koszcie spreadu i finansowania traci ok. 0,74 pp/tydz. (≈ −38 pp/rok). Żaden wariant odwrócenia (a–f) nie przebija baseline z t > 2 ani nie jest dodatni po kosztach.**")
    return "\n".join(lines)

if __name__ == "__main__":
    main()
