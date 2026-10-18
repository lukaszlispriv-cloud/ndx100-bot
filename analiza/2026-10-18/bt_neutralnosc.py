#!/usr/bin/env python3
"""
bt_neutralnosc.py — konstrukcje neutralizujące ryzyko czynnikowe na sygnale momentum
(6M z pominięciem ostatniego tygodnia; osobno 12M−1M) w uniwersum Nasdaq-100
(dzisiejszy skład → survivorship bias), okna tygodniowe.

Wspólny harness (jak bt_odwrocenie.py):
  * okno = ostatnia sesja tygodnia (D0) → ostatnia sesja następnego tygodnia (D5)
  * koszyk 5 LONG + 5 SHORT; wariant bazowy równych wag (0,2 na nogę, gross 200%)
  * zwrot pozycji = r_spółki − r_^NDX (long), −(r_spółki − r_^NDX) (short)
  * spread_pp = Σ w_i·r_i (wagi ze znakiem) = long_pp + short_pp + (W_L − W_S)·r_NDX
    — dla wariantów dolarowo neutralnych (W_L = W_S) identyczne z „śr. long + śr. short”
  * sygnały tylko z danych ≤ D0; uniwersum = spółki z pełną historią sygnału na D0
  * koszty: 0,10% × (Σ|Δw|/2) na rotację (pełna rotacja 10 slotów równych wag = 0,20 pp)
    + 6%/rok finansowania na gross (gross 200% → 0,231 pp/tydz.; 240% → 0,277 pp/tydz.)
  * baseline: 2000 losowych koszyków 5/5 na każdym oknie + 2000 losowych strategii

Warianty (dla każdego sygnału):
  none    – TOP5/BOTTOM5 wg momentum relatywnego (= ref_mom6 z bt_odwrocenie.py)
  a_branza – ranking WEWNĄTRZ grupy branżowej TV (momentum − średnia grupy);
             maks. 1 long i 1 short z grupy
  b_pary  – 5 par z tej samej grupy: grupy (≥3 spółki) o największym (najlepsza − najgorsza),
             long = najlepsza, short = najgorsza w grupie
  c_blok  – TOP5/BOTTOM5 z limitem: ≤2 long z bloku SEMI (Semiconductors + Computer
             Peripherals + Electronic Production Equipment), ≤2 short z bloku DEF
             (sector Consumer Non-Durables, Utilities, Communications)
  c2_blok_roz – jak c, blok SEMI rozszerzony o AMAT, LRCX (Industrial Machinery) i LITE
  d_rp    – skład none, wagi 10 nóg ∝ 1/σ60d, gross = 240% (wg zadania; strony
             nierówne dolarowo → składnik (W_L − W_S)·r_NDX w spreadzie)
  d2_rp_strony – jak d, ale każda strona osobno ∝ 1/σ i suma strony = 120%
  e_beta  – skład none, równe wagi w stronie, strony przeskalowane tak, by
             Σβ_L = Σβ_S (β 120 sesji vs ^NDX), gross 200%
  cd      – skład c, wagi d
  cde     – skład c, wagi ∝ 1/σ, strony przeskalowane do równości Σwβ, gross 240%
  ade     – skład a, wagi ∝ 1/σ, Σwβ równe, gross 240%
"""
import csv, json, math, os, random, statistics
from collections import Counter, defaultdict
from datetime import date

import numpy as np
import pandas as pd

BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
CSV_IN = os.path.join(BASE, "dane", "closes_5y.csv")
OUT_DIR = os.path.join(BASE, "analiza")
TV_JSON = "/home/user/ndx100-bot/data/tv-screen-2026-W8.json"
OUT_SERIES = os.path.join(OUT_DIR, "bt_neutralnosc_serie.csv")
OUT_MD = os.path.join(OUT_DIR, "bt_neutralnosc.md")
OUT_JSON = os.path.join(OUT_DIR, "bt_neutralnosc_wyniki.json")

NON_CANDIDATES = {"^NDX", "^SOX", "^VIX", "^GSPC", "QQQ", "XLP", "XLU", "XLV", "SMH", "IGV"}
N_LEG = 5
N_RANDOM = 2000
SEED = 42
COST_LEG = 0.10          # % na nogę (slot) na rotację
FIN_YEAR = 6.0           # %/rok na gross
SIGMA_WIN = 60
BETA_WIN = 120
MIN_GROUP = 3            # minimalna liczebność grupy branżowej do rankingu wewnątrz grupy
MIN_IND = 4              # branża TV o ≥4 spółkach w uniwersum zostaje branżą; mniejsze → sector

SIGNALS = {
    "mom6": dict(win=126, skip=5, label="momentum 6M (126 sesji, bez ostatnich 5)"),
    "mom12_1": dict(win=252, skip=21, label="momentum 12M−1M (252 sesje, bez ostatnich 21)"),
}
VARIANTS = ["none", "a_branza", "b_pary", "c_blok", "c2_blok_roz", "d_rp", "d2_rp_strony",
            "e_beta", "cd", "cde", "ade"]

BLOK_SEMI_IND = {"Semiconductors", "Computer Peripherals", "Electronic Production Equipment"}
BLOK_SEMI_EXT_TK = {"AMAT", "LRCX", "LITE"}
BLOK_DEF_SEC = {"Consumer Non-Durables", "Utilities", "Communications"}
MAX_BLOK = 2

# ręczne uzupełnienie taksonomii TV dla spółek, których nie ma w screenie W8
MANUAL_IND = {"KHC": ("Food: Major Diversified", "Consumer Non-Durables"),
              "WBD": ("Movies/Entertainment", "Consumer Services")}

# faktyczne koszyki W4–W7 + listy TOP15/BOTTOM15 z raportów (kolejność rankingu; * = poza
# koszykiem wg prerejestrowanej reguły — pominięte przy zamianie)
FAKT = {
 "2026-W4": dict(d0="2026-09-11", d5="2026-09-28",
    long=["MU", "AMD", "AVGO", "MRVL", "LITE"], short=["INTU", "SBUX", "CMCSA", "APP", "ADSK"],
    top15=["MU", "AMD", "AVGO", "MRVL", "LITE", "TER", "SNDK", "STX", "NVDA", "PANW", "AMAT", "CRWD", "META", "ARM", "FTNT"],
    bottom15=["TSLA*", "INTU", "ADSK", "APP", "SBUX", "CMCSA", "TRI", "NFLX", "WMT", "COST", "AXON", "DASH", "PEP", "ISRG", "ADBE"]),
 "2026-W5": dict(d0="2026-09-28", d5="2026-10-02",
    long=["MU", "AMD", "ALAB", "STX", "TER"], short=["SBUX", "NFLX", "PEP", "CMCSA", "APP"],
    top15=["MU", "NVDA", "ALAB", "STX", "AMD", "LRCX", "AMAT", "TER", "MRVL", "AVGO", "SNDK", "LITE", "KLAC", "WDC", "PANW"],
    bottom15=["TSLA*", "SBUX", "INTU*", "NFLX", "PEP", "CMCSA", "APP", "ADSK", "PAYX", "WMT", "TMUS", "EXC", "XEL", "DASH", "COST"]),
 "2026-W6": dict(d0="2026-10-02", d5="2026-10-09",
    long=["MU", "LITE", "TER", "AMAT", "AMD"], short=["APP", "NFLX", "PAYX", "CMCSA", "SBUX"],
    top15=["MU", "LITE", "TER", "AMAT", "AMD", "PANW", "MRVL", "LRCX", "ALAB", "NVDA*", "CRWD", "KLAC", "SNPS", "SNDK", "TXN"],
    bottom15=["TSLA*", "APP", "NFLX", "INTU*", "PAYX", "CMCSA", "SBUX", "ALNY", "ADSK", "WMT", "COST", "TMUS", "MDLZ", "PEP", "DASH"]),
 "2026-W7": dict(d0="2026-10-09", d5="2026-10-16",
    long=["MU", "LITE", "MRVL", "PANW", "CSCO"], short=["CMCSA", "SBUX", "PEP", "TMUS", "APP"],
    top15=["MU", "LITE", "MRVL", "PANW", "CSCO", "FTNT", "AMAT", "AMD", "DDOG", "CRWD", "MSFT", "NVDA*", "SNPS", "LRCX", "TER"],
    bottom15=["TSLA*", "APP", "CMCSA", "TMUS", "SBUX", "PEP", "NFLX", "PAYX", "CRWV", "KHC", "FER", "AXON", "CPRT", "INTU*", "ADBE"]),
}

# ------------------------------------------------------------------ dane
def load():
    df = pd.read_csv(CSV_IN, index_col=0, parse_dates=True)
    df = df[df["^NDX"].notna()]                       # wiersze bez ^NDX = święta
    df = df.ffill(limit=2)                            # pojedyncze braki (1–2 sesje) = brak odczytu, nie brak spółki
    tickers = [c for c in df.columns if c not in NON_CANDIDATES]
    return df, tickers

def load_industry(tickers):
    rows = json.load(open(TV_JSON))["data"]["rows"]
    m = {r["name"]: (r["industry"], r["sector"]) for r in rows}
    missing = [t for t in tickers if t not in m]
    m.update(MANUAL_IND)
    return m, missing

def week_ends(dates):
    last = {}
    for i, d in enumerate(dates):
        y, w, _ = d.isocalendar()
        last[(y, w)] = i
    return [last[k] for k in sorted(last)]

# ------------------------------------------------------------------ sygnały
def grouping(universe, ind):
    """grupa branżowa: industry (≥MIN_IND w uniwersum) albo sector; grupy < MIN_GROUP → 'Pozostałe'."""
    ic = Counter(ind[t][0] for t in universe)
    g = {t: (ind[t][0] if ic[ind[t][0]] >= MIN_IND else ind[t][1]) for t in universe}
    gc = Counter(g.values())
    return {t: (g[t] if gc[g[t]] >= MIN_GROUP else "Pozostałe") for t in universe}

def in_semi(t, ind, ext=False):
    return ind[t][0] in BLOK_SEMI_IND or (ext and t in BLOK_SEMI_EXT_TK)

def in_def(t, ind):
    return ind[t][1] in BLOK_DEF_SEC

def signals_at(P, ndx, d0, tickers, win, skip):
    """mom (relatywne do NDX, w %), sigma60 (dzienne, %), beta120 — tylko dane ≤ d0."""
    hist = win + skip
    out = {}
    rn_mom = ndx[d0 - skip] / ndx[d0 - hist] - 1
    rn = ndx[d0 - BETA_WIN: d0 + 1]
    rn = rn[1:] / rn[:-1] - 1
    var_n = rn.var(ddof=1)
    for j, t in enumerate(tickers):
        seg = P[d0 - hist: d0 + 1, j]
        if np.isnan(seg).any():
            continue
        r = P[d0 - BETA_WIN: d0 + 1, j]
        r = r[1:] / r[:-1] - 1
        sig = (P[d0 - skip, j] / P[d0 - hist, j] - 1 - rn_mom) * 100.0
        sigma = r[-SIGMA_WIN:].std(ddof=1) * 100.0
        beta = float(np.cov(r, rn, ddof=1)[0, 1] / var_n)
        out[t] = dict(mom=sig, sigma=sigma, beta=min(max(beta, 0.2), 3.0))
    return out

# ------------------------------------------------------------------ dobór składu
def pick_plain(sig):
    srt = sorted(sig, key=lambda t: -sig[t]["mom"])
    return srt[:N_LEG], srt[-N_LEG:][::-1]

def pick_block(sig, ind, ext=False):
    srt = sorted(sig, key=lambda t: -sig[t]["mom"])
    lo, n_b = [], 0
    for t in srt:
        b = in_semi(t, ind, ext)
        if b and n_b >= MAX_BLOK:
            continue
        lo.append(t); n_b += b
        if len(lo) == N_LEG: break
    sh, n_b = [], 0
    for t in srt[::-1]:
        if t in lo: continue
        b = in_def(t, ind)
        if b and n_b >= MAX_BLOK:
            continue
        sh.append(t); n_b += b
        if len(sh) == N_LEG: break
    return lo, sh

def pick_industry_neutral(sig, grp):
    gm = defaultdict(list)
    for t in sig: gm[grp[t]].append(sig[t]["mom"])
    gmean = {g: statistics.mean(v) for g, v in gm.items()}
    score = {t: sig[t]["mom"] - gmean[grp[t]] for t in sig if grp[t] != "Pozostałe"}
    srt = sorted(score, key=lambda t: -score[t])
    lo, used = [], set()
    for t in srt:
        if grp[t] in used: continue
        lo.append(t); used.add(grp[t])
        if len(lo) == N_LEG: break
    sh, used = [], set()
    for t in srt[::-1]:
        if grp[t] in used or t in lo: continue
        sh.append(t); used.add(grp[t])
        if len(sh) == N_LEG: break
    return lo, sh

def pick_pairs(sig, grp):
    gm = defaultdict(list)
    for t in sig:
        if grp[t] != "Pozostałe": gm[grp[t]].append(t)
    pairs = []
    for g, ts in gm.items():
        if len(ts) < MIN_GROUP: continue
        ts = sorted(ts, key=lambda t: -sig[t]["mom"])
        pairs.append((sig[ts[0]]["mom"] - sig[ts[-1]]["mom"], ts[0], ts[-1]))
    pairs.sort(reverse=True)
    pairs = pairs[:N_LEG]
    return [p[1] for p in pairs], [p[2] for p in pairs]

# ------------------------------------------------------------------ wagi
def w_equal(lo, sh, side=1.0):
    w = {t: side / len(lo) for t in lo}
    w.update({t: -side / len(sh) for t in sh})
    return w

def w_riskparity(lo, sh, sig, gross=2.4):
    inv = {t: 1.0 / sig[t]["sigma"] for t in lo + sh}
    s = sum(inv.values())
    w = {t: gross * inv[t] / s for t in lo}
    w.update({t: -gross * inv[t] / s for t in sh})
    return w

def w_riskparity_sides(lo, sh, sig, side=1.2):
    il = {t: 1.0 / sig[t]["sigma"] for t in lo}; sl = sum(il.values())
    ish = {t: 1.0 / sig[t]["sigma"] for t in sh}; ss = sum(ish.values())
    w = {t: side * il[t] / sl for t in lo}
    w.update({t: -side * ish[t] / ss for t in sh})
    return w

def beta_balance(w, sig, gross):
    """przeskaluj strony tak, by Σ_L wβ = Σ_S |w|β i Σ|w| = gross."""
    bl = sum(w[t] * sig[t]["beta"] for t in w if w[t] > 0)
    bs = sum(-w[t] * sig[t]["beta"] for t in w if w[t] < 0)
    WL = sum(v for v in w.values() if v > 0); WS = sum(-v for v in w.values() if v < 0)
    # nowe sumy stron: WL' = k_L WL, WS' = k_S WS ; k_L bl = k_S bs ; k_L WL + k_S WS = gross
    k_S = gross / (WS + WL * bs / bl)
    k_L = k_S * bs / bl
    return {t: (v * k_L if v > 0 else v * k_S) for t, v in w.items()}

def build(variant, sig, ind, grp):
    if variant == "none":
        lo, sh = pick_plain(sig); return w_equal(lo, sh)
    if variant == "a_branza":
        lo, sh = pick_industry_neutral(sig, grp); return w_equal(lo, sh)
    if variant == "b_pary":
        lo, sh = pick_pairs(sig, grp)
        return w_equal(lo, sh) if len(lo) >= 3 else None
    if variant == "c_blok":
        lo, sh = pick_block(sig, ind); return w_equal(lo, sh)
    if variant == "c2_blok_roz":
        lo, sh = pick_block(sig, ind, ext=True); return w_equal(lo, sh)
    if variant == "d_rp":
        lo, sh = pick_plain(sig); return w_riskparity(lo, sh, sig)
    if variant == "d2_rp_strony":
        lo, sh = pick_plain(sig); return w_riskparity_sides(lo, sh, sig)
    if variant == "e_beta":
        lo, sh = pick_plain(sig); return beta_balance(w_equal(lo, sh), sig, 2.0)
    if variant == "cd":
        lo, sh = pick_block(sig, ind); return w_riskparity(lo, sh, sig)
    if variant == "cde":
        lo, sh = pick_block(sig, ind); return beta_balance(w_riskparity(lo, sh, sig), sig, 2.4)
    if variant == "ade":
        lo, sh = pick_industry_neutral(sig, grp); return beta_balance(w_riskparity(lo, sh, sig), sig, 2.4)
    raise KeyError(variant)

# ------------------------------------------------------------------ wycena okna
def evaluate(w, fwd, fwd_ndx):
    """fwd: dict t -> zwrot spółki (ułamek); zwraca składniki w pp."""
    WL = sum(v for v in w.values() if v > 0); WS = sum(-v for v in w.values() if v < 0)
    long_pp = 100 * sum(v * (fwd[t] - fwd_ndx) for t, v in w.items() if v > 0)
    short_pp = 100 * sum(v * (fwd[t] - fwd_ndx) for t, v in w.items() if v < 0)
    ndx_pp = 100 * (WL - WS) * fwd_ndx
    spread = long_pp + short_pp + ndx_pp
    legs_hit = sum(1 for t, v in w.items() if v * (fwd[t] - fwd_ndx) > 0)
    return dict(spread=spread, long=long_pp, short=short_pp, ndx=ndx_pp, gross=WL + WS,
                WL=WL, WS=WS, legs_hit=legs_hit, n_legs=len(w))

def turnover_cost(w, prev):
    keys = set(w) | set(prev)
    dw = sum(abs(w.get(t, 0.0) - prev.get(t, 0.0)) for t in keys)
    return COST_LEG * dw / 2.0, dw / 2.0

# ------------------------------------------------------------------ metryki
def mean(xs): return float(np.mean(xs)) if len(xs) else float("nan")
def sd(xs): return float(np.std(xs, ddof=1)) if len(xs) > 1 else float("nan")

def max_drawdown(xs):
    cum = peak = mdd = 0.0
    for x in xs:
        cum += x; peak = max(peak, cum); mdd = min(mdd, cum - peak)
    return mdd

def metrics(rows):
    sp = [r["spread"] for r in rows]; n = len(sp)
    if n == 0: return {"n": 0}
    m = mean(sp); s = sd(sp)
    net = [r["spread"] - r["cost"] for r in rows]
    return {
        "n": n, "mean": m, "median": float(np.median(sp)), "sd": s,
        "t": m / s * math.sqrt(n) if s > 0 else float("nan"),
        "sharpe": m / s * math.sqrt(52) if s > 0 else float("nan"),
        "hit": mean([x > 0 for x in sp]),
        "hit_legs": sum(r["legs_hit"] for r in rows) / sum(r["n_legs"] for r in rows),
        "hit_long": mean([r["long"] > 0 for r in rows]), "hit_short": mean([r["short"] > 0 for r in rows]),
        "mean_long": mean([r["long"] for r in rows]), "mean_short": mean([r["short"] for r in rows]),
        "mean_ndx": mean([r["ndx"] for r in rows]),
        "mdd": max_drawdown(sp), "worst": min(sp), "best": max(sp), "cum": sum(sp),
        "worst_d0": min(rows, key=lambda r: r["spread"])["date_d0"],
        "cost": mean([r["cost"] for r in rows]), "net_mean": mean(net), "net_cum": sum(net),
        "net_t": mean(net) / sd(net) * math.sqrt(n) if sd(net) > 0 else float("nan"),
        "net_mdd": max_drawdown(net),
        "turnover": mean([r["turnover"] for r in rows]), "gross": mean([r["gross"] for r in rows]),
        "net_WL_WS": mean([r["WL"] - r["WS"] for r in rows]),
    }

def fmt(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)): return "–"
    return f"{x:.{d}f}"

def pct(sorted_xs, q):
    i = min(len(sorted_xs) - 1, max(0, int(round(q * (len(sorted_xs) - 1)))))
    return sorted_xs[i]

# ------------------------------------------------------------------ bieg backtestu
def run_signal(sname, df, tickers, ind, P, ndx, vix, we):
    cfg = SIGNALS[sname]
    hist = max(cfg["win"] + cfg["skip"], BETA_WIN + 1)
    dates = df.index
    windows = [(we[k], we[k + 1]) for k in range(len(we) - 1) if we[k] >= hist]
    rng = random.Random(SEED)
    series = {v: [] for v in VARIANTS}
    prev = {v: {} for v in VARIANTS}
    rand_win = []; rand_strats = [[] for _ in range(N_RANDOM)]
    group_sizes = []
    def ma200(i):
        seg = ndx[max(0, i - 199): i + 1]
        return float(np.mean(seg)), len(seg)
    for d0, d5 in windows:
        sig = signals_at(P, ndx, d0, tickers, cfg["win"], cfg["skip"])
        r_ndx = ndx[d5] / ndx[d0] - 1
        fwd = {}
        for t in sig:
            j = tickers.index(t)
            if not np.isnan(P[d5, j]):
                fwd[t] = P[d5, j] / P[d0, j] - 1
        sig = {t: sig[t] for t in fwd}
        grp = grouping(list(sig), ind)
        group_sizes.append(len(set(grp.values())))
        m, nma = ma200(d0)
        ctx = dict(date_d0=dates[d0].date().isoformat(), date_d5=dates[d5].date().isoformat(),
                   year=dates[d0].year, ndx_ret_pp=r_ndx * 100, vix_d0=float(vix[d0]),
                   vix_hi=bool(vix[d0] > 20), ndx_above_ma200=bool(ndx[d0] > m), n_univ=len(sig))
        for v in VARIANTS:
            w = build(v, sig, ind, grp)
            if w is None: continue
            ev = evaluate(w, fwd, r_ndx)
            cost_rot, dw = turnover_cost(w, prev[v])
            fin = FIN_YEAR / 52.0 * ev["gross"]
            prev[v] = w
            lo = sorted([t for t in w if w[t] > 0], key=lambda t: -w[t])
            sh = sorted([t for t in w if w[t] < 0], key=lambda t: w[t])
            row = dict(ctx, variant=v, **ev, cost=cost_rot + fin, turnover=dw / ev["gross"],
                       long_tk=" ".join(f"{t}:{w[t]:.2f}" for t in lo),
                       short_tk=" ".join(f"{t}:{-w[t]:.2f}" for t in sh))
            series[v].append(row)
        u = list(sig); rs = []
        for k in range(N_RANDOM):
            smp = rng.sample(u, 2 * N_LEG)
            s_ = 100 * (mean([fwd[t] for t in smp[:N_LEG]]) - mean([fwd[t] for t in smp[N_LEG:]]))
            rs.append(s_); rand_strats[k].append(s_)
        rand_win.append(rs)
    pooled = np.array([x for rs in rand_win for x in rs])
    ps = np.sort(pooled)
    rs_means = [mean(s) for s in rand_strats]
    rs_t = [mean(s) / sd(s) * math.sqrt(len(s)) for s in rand_strats]
    rs_sh = [mean(s) / sd(s) * math.sqrt(52) for s in rand_strats]
    base = dict(n_windows=len(rand_win), sigma_pp=float(ps.std(ddof=1)), mean_pp=float(ps.mean()),
                p5_pp=float(pct(ps, 0.05)), p95_pp=float(pct(ps, 0.95)),
                sigma_per_window_median=float(np.median([sd(rs) for rs in rand_win])),
                strat_mean_p5=pct(sorted(rs_means), 0.05), strat_mean_p95=pct(sorted(rs_means), 0.95),
                strat_mean_sd=sd(rs_means), strat_t_p5=pct(sorted(rs_t), 0.05), strat_t_p95=pct(sorted(rs_t), 0.95),
                strat_sharpe_sd=sd(rs_sh), rs_means=rs_means)
    return series, base, group_sizes

def paired_vs_none(rows, base_rows):
    """porównanie parami z none na wspólnych oknach: Δśr., t(Δ), stosunek σ, korelacja, F-test (p) dla σ."""
    bm = {r["date_d0"]: r for r in base_rows}
    pairs = [(r["spread"], bm[r["date_d0"]]["spread"]) for r in rows if r["date_d0"] in bm]
    if len(pairs) < 10: return {}
    def legs(r): return {x.split(":")[0] for x in (r["long_tk"] + " " + r["short_tk"]).split()}
    ov = [len(legs(r) & legs(bm[r["date_d0"]])) for r in rows if r["date_d0"] in bm]
    same = sum(1 for r in rows if r["date_d0"] in bm and legs(r) == legs(bm[r["date_d0"]])) / len(ov)
    a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
    d = a - b; n = len(d)
    var_ratio = b.var(ddof=1) / a.var(ddof=1)
    # F-test jednostronny: czy σ(none)² > σ(wariant)²  (df n-1, n-1) — aproksymacja normalna dla log F
    import math as _m
    z = _m.log(var_ratio) / _m.sqrt(2.0 / (n - 1) + 2.0 / (n - 1))
    p_f = 0.5 * _m.erfc(z / _m.sqrt(2))
    # równość wag w stosunku do gross: skaluj oba do gross 2.0 dla porównania σ
    ga = np.mean([r["gross"] for r in rows]); gb = np.mean([bm[r["date_d0"]]["gross"] for r in rows if r["date_d0"] in bm])
    return {"n": n, "d_mean": float(d.mean()), "d_t": float(d.mean() / d.std(ddof=1) * _m.sqrt(n)),
            "sigma_ratio": float(a.std(ddof=1) / b.std(ddof=1)),
            "sigma_ratio_same_gross": float((a.std(ddof=1) / ga) / (b.std(ddof=1) / gb)),
            "corr": float(np.corrcoef(a, b)[0, 1]), "p_F_sigma_lower": p_f,
            "overlap_legs": float(np.mean(ov)), "same_basket": same}

def summarize(series, base, first_d0_common=None):
    res = {}
    for v in VARIANTS:
        rows = series[v]
        if not rows: continue
        r = {"all": metrics(rows), "vs_none": paired_vs_none(rows, series["none"])}
        r["all"]["p_random_strat"] = sum(1 for x in base["rs_means"] if x >= r["all"]["mean"]) / len(base["rs_means"])
        r["years"] = {int(y): metrics([x for x in rows if x["year"] == y]) for y in sorted({x["year"] for x in rows})}
        r["vix_hi"] = metrics([x for x in rows if x["vix_hi"]]); r["vix_lo"] = metrics([x for x in rows if not x["vix_hi"]])
        r["ndx_above_ma200"] = metrics([x for x in rows if x["ndx_above_ma200"]])
        r["ndx_below_ma200"] = metrics([x for x in rows if not x["ndx_above_ma200"]])
        h = len(rows) // 2
        r["half1"] = metrics(rows[:h]); r["half2"] = metrics(rows[h:])
        if first_d0_common:
            r["common"] = metrics([x for x in rows if x["date_d0"] >= first_d0_common])
        res[v] = r
    return res

# ------------------------------------------------------------------ faktyczne koszyki W4–W7
def faktyczne(df, tickers, ind, P, ndx):
    dates = [d.date().isoformat() for d in df.index]
    di = {d: i for i, d in enumerate(dates)}
    out = {}
    for wk, k in FAKT.items():
        d0, d5 = di[k["d0"]], di[k["d5"]]
        r_ndx = ndx[d5] / ndx[d0] - 1
        fwd = {}
        for t in set(k["long"] + k["short"] + [x.rstrip("*") for x in k["top15"] + k["bottom15"]]):
            j = tickers.index(t)
            if not (np.isnan(P[d0, j]) or np.isnan(P[d5, j])):
                fwd[t] = P[d5, j] / P[d0, j] - 1
        # sigma60 / beta120 na D0 dla wszystkich kandydatów
        sig = {}
        rn = ndx[d0 - BETA_WIN: d0 + 1]; rn = rn[1:] / rn[:-1] - 1
        for t in fwd:
            j = tickers.index(t)
            r = P[d0 - BETA_WIN: d0 + 1, j]
            if np.isnan(r).any():
                r = P[d0 - SIGMA_WIN: d0 + 1, j]
                if np.isnan(r).any(): continue
                rr = r[1:] / r[:-1] - 1
                sig[t] = dict(sigma=rr.std(ddof=1) * 100, beta=float("nan"))
            else:
                rr = r[1:] / r[:-1] - 1
                sig[t] = dict(sigma=rr[-SIGMA_WIN:].std(ddof=1) * 100,
                              beta=float(np.cov(rr, rn, ddof=1)[0, 1] / rn.var(ddof=1)))
        def apply_block(lo, sh, ext):
            lo2, nb, repl_l = [], 0, []
            for t in lo:
                b = in_semi(t, ind, ext)
                if b and nb >= MAX_BLOK: repl_l.append(t); continue
                lo2.append(t); nb += b
            for c in k["top15"]:
                if len(lo2) == N_LEG: break
                if c.endswith("*") or c in lo2 or c in lo or c in sh: continue
                if in_semi(c, ind, ext) and nb >= MAX_BLOK: continue
                lo2.append(c); nb += in_semi(c, ind, ext)
            sh2, nb, repl_s = [], 0, []
            for t in sh:
                b = in_def(t, ind)
                if b and nb >= MAX_BLOK: repl_s.append(t); continue
                sh2.append(t); nb += b
            for c in k["bottom15"]:
                if len(sh2) == N_LEG: break
                if c.endswith("*") or c in sh2 or c in sh or c in lo2: continue
                if in_def(c, ind) and nb >= MAX_BLOK: continue
                sh2.append(c); nb += in_def(c, ind)
            return lo2, sh2, repl_l, repl_s
        res = {"d0": k["d0"], "d5": k["d5"], "sesje": d5 - d0, "ndx_pp": 100 * r_ndx,
               "long": k["long"], "short": k["short"],
               "blok_long": [t for t in k["long"] if in_semi(t, ind)],
               "blok_long_roz": [t for t in k["long"] if in_semi(t, ind, True)],
               "blok_short": [t for t in k["short"] if in_def(t, ind)],
               "sigma60": {t: round(sig[t]["sigma"], 2) for t in k["long"] + k["short"]},
               "warianty": {}}
        def add(name, lo, sh, w):
            if any(t not in fwd for t in w): return
            ev = evaluate(w, fwd, r_ndx)
            res["warianty"][name] = dict(long=lo, short=sh, spread=ev["spread"], long_pp=ev["long"],
                                         short_pp=ev["short"], ndx_pp=ev["ndx"], gross=ev["gross"],
                                         legs_hit=ev["legs_hit"],
                                         wagi={t: round(v, 3) for t, v in w.items()})
        lo, sh = k["long"], k["short"]
        add("fakt_rowne", lo, sh, w_equal(lo, sh))
        add("fakt_rowne_240", lo, sh, w_equal(lo, sh, side=1.2))
        add("fakt_d_rp", lo, sh, w_riskparity(lo, sh, sig))
        add("fakt_d2_rp_strony", lo, sh, w_riskparity_sides(lo, sh, sig))
        lo2, sh2, rl, rs = apply_block(lo, sh, False)
        res["c_zamiany"] = {"long_out": rl, "long_in": [t for t in lo2 if t not in lo],
                            "short_out": rs, "short_in": [t for t in sh2 if t not in sh]}
        add("c_blok_rowne", lo2, sh2, w_equal(lo2, sh2))
        add("c_blok_d_rp", lo2, sh2, w_riskparity(lo2, sh2, sig))
        lo3, sh3, rl3, rs3 = apply_block(lo, sh, True)
        res["c2_zamiany"] = {"long_out": rl3, "long_in": [t for t in lo3 if t not in lo],
                             "short_out": rs3, "short_in": [t for t in sh3 if t not in sh]}
        add("c2_blok_roz_rowne", lo3, sh3, w_equal(lo3, sh3))
        add("c2_blok_roz_d_rp", lo3, sh3, w_riskparity(lo3, sh3, sig))
        out[wk] = res
    return out

# ------------------------------------------------------------------ MD
def table_all(res, base, title, key="all"):
    L = [f"### {title}\n",
         "| wariant | n | śr. pp | mediana | σ | t | Sharpe | hit | hit nóg | śr. L | śr. S | śr. NDX-skł. | maxDD | najgorsze (D0) | najlepsze | gross | rotacja | koszt/tydz | **netto śr.** | netto t | netto maxDD | p(losowa ≥) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in VARIANTS:
        if v not in res: continue
        m = res[v][key]
        if not m.get("n"): continue
        L.append(f"| {v} | {m['n']} | {fmt(m['mean'])} | {fmt(m['median'])} | {fmt(m['sd'])} | {fmt(m['t'])} | {fmt(m['sharpe'])} | "
                 f"{fmt(m['hit']*100,0)}% | {fmt(m['hit_legs']*100,0)}% | {fmt(m['mean_long'])} | {fmt(m['mean_short'])} | {fmt(m['mean_ndx'])} | "
                 f"{fmt(m['mdd'],1)} | {fmt(m['worst'],1)} ({m['worst_d0']}) | {fmt(m['best'],1)} | {fmt(m['gross']*100,0)}% | {fmt(m['turnover']*100,0)}% | "
                 f"{fmt(m['cost'])} | **{fmt(m['net_mean'])}** | {fmt(m['net_t'])} | {fmt(m['net_mdd'],1)} | {fmt(m.get('p_random_strat'),3) if key=='all' else '–'} |")
    return L

def write_md(results, bases, fakt, group_sizes, missing_ind, common_d0, series_all):
    L = ["# Backtest: neutralizacja ryzyka czynnikowego na momentum (Nasdaq-100, okna tygodniowe)\n"]
    r6 = results["mom6"]["none"]["all"]; r12 = results["mom12_1"]["none"]["all"]
    L.append(f"Dane: `dane/closes_5y.csv` (zamknięcia 2021-10-18…2026-10-16, dzisiejszy skład NDX-100 → survivorship bias). "
             f"Okna: D0 = ostatnia sesja tygodnia → D5 = ostatnia sesja następnego tygodnia. "
             f"Sygnał 6M: {results['mom6']['none']['first_d0']}…, {r6['n']} okien; sygnał 12M−1M: {results['mom12_1']['none']['first_d0']}…, {r12['n']} okien. "
             f"Uniwersum = spółki z pełną historią sygnału (i 121 sesji do β) na D0; indeksy/ETF wyłączone; pojedyncze braki odczytu (≤2 sesje) uzupełnione poprzednim zamknięciem. "
             f"Branże: `data/tv-screen-2026-W8.json` (industry/sector TV; brak w screenie: {', '.join(missing_ind)} → przypisane ręcznie). "
             f"Grupa branżowa = industry o ≥{MIN_IND} spółkach w uniwersum, inaczej sector; grupy <{MIN_GROUP} → „Pozostałe” (nie biorą udziału w rankingu wewnątrz grupy); "
             f"liczba grup na oknie: {min(group_sizes['mom6'])}–{max(group_sizes['mom6'])}.\n")
    L.append(f"Konwencje: spread_pp = Σ wᵢ·rᵢ (wagi ze znakiem, long +, short −) = long_pp + short_pp + (W_L − W_S)·r_NDX; "
             f"dla równych wag 5/5 to dokładnie „śr. 5 long − śr. 5 short” względem ^NDX. Kolumna „śr. NDX-skł.” = średni składnik (W_L − W_S)·r_NDX "
             f"(≠0 tylko przy stronach nierównych dolarowo: d_rp, e_beta, cd, cde, ade). "
             f"Koszty: {COST_LEG}% × Σ|Δw|/2 na rotację (pełna rotacja równych wag = 0,20 pp) + {FIN_YEAR}%/rok na gross "
             f"({FIN_YEAR/52*2:.3f} pp/tydz. przy gross 200%, {FIN_YEAR/52*2.4:.3f} przy 240%). "
             f"σ60 = odchylenie dziennych zwrotów z 60 sesji do D0; β = OLS 120 sesji vs ^NDX (przycięta do [0,2; 3]). "
             f"t = śr./σ·√n; Sharpe = śr./σ·√52 (brutto); „netto t” liczone na serii po kosztach.\n")
    L.append("## Warianty\n")
    L.append("| kod | definicja |\n|---|---|")
    L.append("| none | TOP5/BOTTOM5 wg momentum relatywnego (bez neutralizacji; = ref_mom6 z bt_odwrocenie.py) |")
    L.append("| a_branza | (a) ranking WEWNĄTRZ grupy branżowej (momentum − średnia grupy); maks. 1 long i 1 short z grupy; równe wagi |")
    L.append("| b_pary | (b) 5 par z tej samej grupy (≥3 spółki): grupy o największej różnicy najlepsza−najgorsza; long = najlepsza, short = najgorsza |")
    L.append(f"| c_blok | (c) TOP5/BOTTOM5 z limitem ≤{MAX_BLOK} long z bloku SEMI = industry {{{', '.join(sorted(BLOK_SEMI_IND))}}} i ≤{MAX_BLOK} short z bloku DEF = sector {{{', '.join(sorted(BLOK_DEF_SEC))}}}; nadmiar zastępuje następna spółka z rankingu |")
    L.append(f"| c2_blok_roz | jak c, blok SEMI rozszerzony o {', '.join(sorted(BLOK_SEMI_EXT_TK))} (semicap w TV = Industrial Machinery, LITE = Electrical Products) |")
    L.append("| d_rp | (d) skład none, wagi 10 nóg ∝ 1/σ60, Σ\\|w\\| = 240% (dosłownie wg zadania: strony NIE są równe dolarowo) |")
    L.append("| d2_rp_strony | (d′) wagi ∝ 1/σ60 osobno w każdej stronie, każda strona = 120% (dolarowo neutralny) |")
    L.append("| e_beta | (e) skład none, równe wagi w stronie, strony przeskalowane tak, by Σβ_L = Σβ_S, gross 200% |")
    L.append("| cd | skład c_blok + wagi d_rp |")
    L.append("| cde | skład c_blok, wagi ∝ 1/σ, strony przeskalowane do Σwβ_L = Σwβ_S, gross 240% |")
    L.append("| ade | skład a_branza, wagi ∝ 1/σ, Σwβ równe, gross 240% |\n")

    for sname in SIGNALS:
        base = bases[sname]
        L.append(f"## Sygnał: {SIGNALS[sname]['label']}\n")
        L.append(f"**Baseline (2000 losowych koszyków 5/5 równych wag na każdym z {base['n_windows']} okien):** σ spreadu losowego **{fmt(base['sigma_pp'])} pp**, "
                 f"p5 {fmt(base['p5_pp'])} / p95 {fmt(base['p95_pp'])} pp, średnia {fmt(base['mean_pp'])}; σ w pojedynczym oknie (mediana) {fmt(base['sigma_per_window_median'])} pp. "
                 f"2000 losowych STRATEGII: średnia tygodniowa p5 {fmt(base['strat_mean_p5'],3)} / p95 {fmt(base['strat_mean_p95'],3)} pp, t-stat p5 {fmt(base['strat_t_p5'])} / p95 {fmt(base['strat_t_p95'])}, σ Sharpe'a {fmt(base['strat_sharpe_sd'])}. "
                 f"Dla gross 240% (warianty d/cd/cde/ade) baseline σ skaluje się ×1,2 → {fmt(base['sigma_pp']*1.2)} pp.\n")
        L += table_all(results[sname], base, "Cały okres")
        L.append("")
        L.append("### Porównanie parami z `none` (te same okna)\n")
        L.append("| wariant | n | Δśr. pp (wariant − none) | t(Δ) | σ wariantu / σ none | to samo przy gross 200% | korelacja z none | p (σ wariantu < σ none, F) | wspólne nogi z none (na 10) | okna z identycznym składem |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for v in VARIANTS:
            if v == "none" or v not in results[sname]: continue
            c = results[sname][v].get("vs_none") or {}
            if not c: continue
            L.append(f"| {v} | {c['n']} | {fmt(c['d_mean'])} | {fmt(c['d_t'])} | {fmt(c['sigma_ratio'])} | {fmt(c['sigma_ratio_same_gross'])} | {fmt(c['corr'])} | {fmt(c['p_F_sigma_lower'],4)} | {fmt(c['overlap_legs'],1)} | {fmt(c['same_basket']*100,0)}% |")
        L.append("")
        if sname == "mom6":
            L += table_all(results[sname], base, f"Wspólny okres z sygnałem 12M−1M (D0 ≥ {common_d0})", key="common")
            L.append("")
        res = results[sname]
        years = sorted({y for v in res for y in res[v]["years"]})
        L.append("### Lata (po dacie D0; brutto, pp/tydz.: n / śr. / t / hit)\n")
        L.append("| wariant | " + " | ".join(str(y) for y in years) + " |")
        L.append("|---|" + "---|" * len(years))
        for v in VARIANTS:
            if v not in res: continue
            cells = []
            for y in years:
                m = res[v]["years"].get(y, {"n": 0})
                cells.append(f"{m['n']} / {fmt(m['mean'])} / {fmt(m['t'],1)} / {fmt(m['hit']*100,0)}%" if m["n"] else "–")
            L.append(f"| {v} | " + " | ".join(cells) + " |")
        L.append("\n### Reżimy na D0 (brutto: n / śr. / σ / t)\n")
        L.append("| wariant | VIX>20 | VIX≤20 | NDX<MA200 | NDX>MA200 | 1. połowa | 2. połowa |")
        L.append("|---|---|---|---|---|---|---|")
        for v in VARIANTS:
            if v not in res: continue
            r = res[v]
            def c(m): return f"{m['n']} / {fmt(m['mean'])} / {fmt(m['sd'],1)} / {fmt(m['t'],1)}" if m["n"] else "–"
            L.append(f"| {v} | {c(r['vix_hi'])} | {c(r['vix_lo'])} | {c(r['ndx_below_ma200'])} | {c(r['ndx_above_ma200'])} | {c(r['half1'])} | {c(r['half2'])} |")
        L.append("")

    L.append("## Ostatnie 8 okien: składy none / b_pary (6M) i a_branza (12M−1M)\n")
    L.append("| D0 | D5 | NDX pp | none 6M (spread) | b_pary 6M (spread) | a_branza 12M−1M (spread) |")
    L.append("|---|---|---|---|---|---|")
    s6n = {r["date_d0"]: r for r in series_all["mom6"]["none"]}; s6b = {r["date_d0"]: r for r in series_all["mom6"]["b_pary"]}
    s12a = {r["date_d0"]: r for r in series_all["mom12_1"]["a_branza"]}
    def strip(tk): return " ".join(x.split(":")[0] for x in tk.split())
    for d0 in [r["date_d0"] for r in series_all["mom6"]["none"][-8:]]:
        a = s6n[d0]; b = s6b.get(d0); c = s12a.get(d0)
        L.append(f"| {d0} | {a['date_d5']} | {fmt(a['ndx_ret_pp'],1)} | L {strip(a['long_tk'])} / S {strip(a['short_tk'])} (**{fmt(a['spread'],1)}**) | "
                 + (f"L {strip(b['long_tk'])} / S {strip(b['short_tk'])} (**{fmt(b['spread'],1)}**)" if b else "–") + " | "
                 + (f"L {strip(c['long_tk'])} / S {strip(c['short_tk'])} (**{fmt(c['spread'],1)}**)" if c else "–") + " |")
    L.append("")
    # faktyczne koszyki
    L.append("## Faktyczne koszyki W4–W7 po narzuceniu (c) i (d)\n")
    L.append("Okno = D0 koszyka → sesja rozliczenia z raportu (W4: 11 sesji — rotacja przeterminowana; pozostałe 4–5 sesji). "
             "Zamiana nadmiarowych nóg: kolejne spółki z TOP15/BOTTOM15 danego raportu (w kolejności rankingu), z pominięciem oznaczonych „*” (poza koszykiem wg prerejestrowanej reguły: TSLA, INTU do 16.10, NVDA od W6) "
             "i spółek już w koszyku; limit bloku sprawdzany także dla zamienników. Wagi (d) z σ60 na D0 danego koszyka; gross 240% (dla porównania podano też równe wagi ×1,2 = gross 240%).\n")
    L.append("| tydzień | okno | sesje | NDX pp | nogi w bloku SEMI (spec / rozsz.) | nogi w bloku DEF | zamiany (c) | zamiany (c2) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for wk, f in fakt.items():
        z = f["c_zamiany"]; z2 = f["c2_zamiany"]
        zs = "; ".join(x for x in [
            f"L: {' '.join(z['long_out'])} → {' '.join(z['long_in'])}" if z["long_out"] else "",
            f"S: {' '.join(z['short_out'])} → {' '.join(z['short_in'])}" if z["short_out"] else ""] if x) or "brak"
        zs2 = "; ".join(x for x in [
            f"L: {' '.join(z2['long_out'])} → {' '.join(z2['long_in'])}" if z2["long_out"] else "",
            f"S: {' '.join(z2['short_out'])} → {' '.join(z2['short_in'])}" if z2["short_out"] else ""] if x) or "brak"
        L.append(f"| {wk} | {f['d0']}→{f['d5']} | {f['sesje']} | {fmt(f['ndx_pp'])} | {' '.join(f['blok_long'])} ({len(f['blok_long'])}) / {' '.join(f['blok_long_roz'])} ({len(f['blok_long_roz'])}) | "
                 f"{' '.join(f['blok_short']) or '—'} ({len(f['blok_short'])}) | {zs} | {zs2} |")
    L.append("\nWyniki (pp spreadu w oknie; „nogi+” = liczba nóg z dodatnim wkładem na 10):\n")
    names = ["fakt_rowne", "fakt_rowne_240", "fakt_d_rp", "fakt_d2_rp_strony", "c_blok_rowne", "c_blok_d_rp", "c2_blok_roz_rowne", "c2_blok_roz_d_rp"]
    L.append("| tydzień | " + " | ".join(names) + " |")
    L.append("|---|" + "---|" * len(names))
    sums = {n: 0.0 for n in names}
    for wk, f in fakt.items():
        cells = []
        for n in names:
            w = f["warianty"].get(n)
            if w: cells.append(f"{fmt(w['spread'])} ({w['legs_hit']}/10)"); sums[n] += w["spread"]
            else: cells.append("–")
        L.append(f"| {wk} | " + " | ".join(cells) + " |")
    L.append("| **suma** | " + " | ".join(f"**{fmt(sums[n])}**" for n in names) + " |")
    L.append("\nSkłady po (c) i wagi (d):\n")
    for wk, f in fakt.items():
        c = f["warianty"].get("c_blok_rowne"); d = f["warianty"].get("fakt_d_rp"); cd = f["warianty"].get("c_blok_d_rp")
        L.append(f"- **{wk}**: fakt L {' '.join(f['long'])} / S {' '.join(f['short'])}; σ60: " +
                 ", ".join(f"{t} {v}" for t, v in f["sigma60"].items()) + ".")
        if d: L.append(f"  - wagi d_rp (fakt): " + ", ".join(f"{t} {v:+.2f}" for t, v in d["wagi"].items()) +
                       f" (W_L {sum(v for v in d['wagi'].values() if v>0):.2f}, W_S {-sum(v for v in d['wagi'].values() if v<0):.2f}; składnik NDX {fmt(d['ndx_pp'])} pp)")
        if c: L.append(f"  - po (c): L {' '.join(c['long'])} / S {' '.join(c['short'])} → {fmt(c['spread'])} pp (fakt {fmt(f['warianty']['fakt_rowne']['spread'])} pp)")
        if cd: L.append(f"  - po (c)+(d): {fmt(cd['spread'])} pp; wagi " + ", ".join(f"{t} {v:+.2f}" for t, v in cd["wagi"].items()))
    L.append("")
    L.append("## Wnioski\n")
    L += conclusions(results, bases, fakt)
    with open(OUT_MD, "w") as f:
        f.write("\n".join(L) + "\n")

def conclusions(results, bases, fakt):
    out = []
    for sname in SIGNALS:
        res = results[sname]; base = bases[sname]
        n = res["none"]["all"]
        out.append(f"- **{SIGNALS[sname]['label']}**, bez neutralizacji (none): śr. {fmt(n['mean'])} pp/tydz., σ {fmt(n['sd'])}, t {fmt(n['t'])}, Sharpe {fmt(n['sharpe'])}, maxDD {fmt(n['mdd'],1)} pp, najgorsze okno {fmt(n['worst'],1)} pp ({n['worst_d0']}); netto {fmt(n['net_mean'])} pp/tydz. (netto t {fmt(n['net_t'])}). Baseline σ losowego koszyka {fmt(base['sigma_pp'])} pp — momentum ma σ ok. {fmt(n['sd']/base['sigma_pp'],1)}× wyższą niż losowy koszyk 5/5 (koncentracja czynnikowa).")
        rows = []
        for v in VARIANTS:
            if v == "none" or v not in res: continue
            m = res[v]["all"]
            rows.append((v, m))
        for v, m in rows:
            scale = 1.0
            if m["gross"] > 2.2: scale = 1.2
            out.append(f"  - {v}: σ {fmt(m['sd'])} ({fmt(m['sd']/n['sd']/scale*100,0)}% σ none przy tym samym gross), śr. {fmt(m['mean'])}, t {fmt(m['t'])}, Sharpe {fmt(m['sharpe'])}, maxDD {fmt(m['mdd'],1)}, najgorsze {fmt(m['worst'],1)} ({m['worst_d0']}), hit {fmt(m['hit']*100,0)}%, netto śr. {fmt(m['net_mean'])} (netto t {fmt(m['net_t'])}), p(losowa ≥) {fmt(m['p_random_strat'],3)}.")
        passing = [v for v in VARIANTS if v in res and res[v]["all"]["t"] > 2 and res[v]["all"]["net_mean"] > 0 and res[v]["all"]["net_t"] > 2]
        weak = [v for v in VARIANTS if v in res and res[v]["all"]["t"] > 2 and res[v]["all"]["net_mean"] > 0 and res[v]["all"]["net_t"] <= 2]
        out.append(f"  - Warianty z t > 2 **i** netto > 0 **i** netto t > 2: {', '.join(passing) if passing else '**żaden**'}"
                   + (f"; t > 2 i netto > 0, ale netto t ≤ 2: {', '.join(weak)}" if weak else "") + ".")
    s = {k: sum(f["warianty"][k]["spread"] for f in fakt.values() if k in f["warianty"]) for k in
         ["fakt_rowne", "fakt_rowne_240", "fakt_d_rp", "c_blok_rowne", "c_blok_d_rp", "c2_blok_roz_rowne", "c2_blok_roz_d_rp"]}
    out.append("- **Interpretacja.** (1) Neutralność branżowa (a) i parowanie (b) obniżają σ spreadu o ok. 20–24% przy tym samym gross i tej samej (6M) lub wyższej (12M−1M) średniej — to jedyne konstrukcje, które statystycznie zmniejszają ryzyko (F-test p < 0,001) bez kosztu w średniej; maxDD spada z ok. −50 do −37…−41 pp, najgorsze okno z −26 do −14…−18 pp. Sharpe rośnie z ~1,0 do ~1,3 (6M) i z ~0,6 do ~1,2 (12M−1M). Ale: w obu przypadkach t brutto ≈ 2,2–2,7 i t netto 1,6–2,0 — po kosztach żaden wariant nie przekracza t > 2, a σ Sharpe'a losowej strategii to ~0,5, więc przewaga nad losowym koszykiem o Sharpe 1,3 jest ok. 2,5σ, nie więcej. "
               "(2) Limit bloku (c) w wersji z zadania prawie nie wiąże (skład identyczny z none w większości okien, korelacja 0,98) i nic nie zmienia; rozszerzony blok (c2) obniża σ o 6–8%, ale kosztem średniej (6M: Δ = −0,35 pp/tydz., t(Δ) = −2,2) — momentum w tym uniwersum to w dużej mierze blok sprzętu AI i jego ograniczanie ucina źródło zwrotu. "
               "(3) Równy udział ryzyka (d) w wersji dosłownej (10 nóg ∝ 1/σ) przenosi dolary z longów o wysokiej σ (semis) na shorty o niskiej σ (staples) → W_S ≈ 1,6–1,75 vs W_L ≈ 0,7–0,85, czyli koszyk jest netto short indeksu o 80–100% kapitału; w rynku rosnącym to ujemny składnik (W_L − W_S)·r_NDX i wyższa σ, nie niższa. Wersja po stronach (d2) nie zmienia nic poza skalą (σ/gross 0,97–1,01 σ none). "
               "(4) Neutralność beta (e) jest tym samym zakładem w innej skali: longi momentum mają β > shorty, więc wyrównanie Σβ wymaga przewagi dolarowej shortów — średnia spada o 0,45 (6M) i 0,90 pp/tydz. (12M−1M, t(Δ) = −3,2); maxDD rośnie. Kombinacje cde/ade dziedziczą tę wadę. Wniosek: przy zwrotach liczonych względem ^NDX i równych stronach koszyk jest już „neutralny” w sensie, który ma znaczenie dla tego harnessu; jawna neutralizacja β/σ bez hedgu indeksowego pogarsza wynik.")
    out.append(f"- **Faktyczne koszyki W4–W7** (suma 4 okien): równe wagi {fmt(s['fakt_rowne'])} pp (×1,2 przy gross 240%: {fmt(s['fakt_rowne_240'])}); "
               f"(d) risk parity 240%: {fmt(s['fakt_d_rp'])}; (c) limit bloku (spec): {fmt(s['c_blok_rowne'])}; (c)+(d): {fmt(s['c_blok_d_rp'])}; "
               f"(c) blok rozszerzony: {fmt(s['c2_blok_roz_rowne'])}; (c2)+(d): {fmt(s['c2_blok_roz_d_rp'])}. Poprawa z (c) w W4–W6 pochodzi z zamienników (PANW, AMAT, LRCX, LITE), które akurat pobiły indeks — to cztery okna, anegdota, nie test; w W7 limit nie wiąże (2 nogi SEMI, 2 nogi DEF) i strata −21 pp zostaje. (d) na faktycznych koszykach daje +0,8…+1,8 pp w W4/W6/W7 głównie przez składnik netto-short NDX (W7: +4,35 pp przy NDX −5,5%), a nie przez trafniejsze nogi (nogi+ bez zmian).")
    return out

# ------------------------------------------------------------------ main
def main():
    df, tickers = load()
    ind, missing = load_industry(tickers)
    P = df[tickers].to_numpy(dtype=float)
    ndx = df["^NDX"].to_numpy(dtype=float); vix = df["^VIX"].to_numpy(dtype=float)
    we = week_ends(df.index)
    all_series, bases, gsizes, results = {}, {}, {}, {}
    for sname in SIGNALS:
        series, base, gs = run_signal(sname, df, tickers, ind, P, ndx, vix, we)
        all_series[sname] = series; bases[sname] = base; gsizes[sname] = gs
    common_d0 = all_series["mom12_1"]["none"][0]["date_d0"]
    for sname in SIGNALS:
        results[sname] = summarize(all_series[sname], bases[sname], common_d0)
        for v in results[sname]:
            results[sname][v]["first_d0"] = all_series[sname][v][0]["date_d0"]
            results[sname][v]["last_d5"] = all_series[sname][v][-1]["date_d5"]
    fakt = faktyczne(df, tickers, ind, P, ndx)

    fields = ["signal", "variant", "date_d0", "date_d5", "spread_pp", "long_pp", "short_pp", "ndx_comp_pp", "cost_pp", "net_pp",
              "gross", "WL", "WS", "legs_hit", "turnover", "ndx_ret_pp", "vix_d0", "ndx_above_ma200", "n_univ", "long", "short"]
    with open(OUT_SERIES, "w", newline="") as f:
        w = csv.writer(f); w.writerow(fields)
        for sname in SIGNALS:
            for v in VARIANTS:
                for r in all_series[sname][v]:
                    w.writerow([sname, v, r["date_d0"], r["date_d5"], f"{r['spread']:.4f}", f"{r['long']:.4f}", f"{r['short']:.4f}",
                                f"{r['ndx']:.4f}", f"{r['cost']:.4f}", f"{r['spread']-r['cost']:.4f}", f"{r['gross']:.3f}",
                                f"{r['WL']:.3f}", f"{r['WS']:.3f}", r["legs_hit"], f"{r['turnover']:.3f}", f"{r['ndx_ret_pp']:.3f}",
                                fmt(r["vix_d0"]), int(r["ndx_above_ma200"]), r["n_univ"], r["long_tk"], r["short_tk"]])
    bases_out = {s: {k: v for k, v in b.items() if k != "rs_means"} for s, b in bases.items()}
    with open(OUT_JSON, "w") as f:
        json.dump({"baseline": bases_out, "variants": results, "faktyczne": fakt, "common_d0": common_d0,
                   "missing_industry": missing}, f, indent=1, default=str)
    write_md(results, bases_out, fakt, gsizes, missing, common_d0, all_series)
    # skrót na stdout
    for sname in SIGNALS:
        print(f"== {sname}  baseline σ {bases[sname]['sigma_pp']:.2f} p5 {bases[sname]['p5_pp']:.2f} p95 {bases[sname]['p95_pp']:.2f}  n={bases[sname]['n_windows']}")
        for v in VARIANTS:
            m = results[sname][v]["all"]
            print(f"  {v:14s} n={m['n']} mean={m['mean']:6.2f} sd={m['sd']:5.2f} t={m['t']:5.2f} sh={m['sharpe']:5.2f} hit={m['hit']*100:4.0f}% "
                  f"mdd={m['mdd']:7.1f} worst={m['worst']:6.1f} gross={m['gross']:.2f} net={m['net_mean']:6.2f} net_t={m['net_t']:5.2f} p={m['p_random_strat']:.3f}")
    for wk, f in fakt.items():
        print(wk, {k: round(v["spread"], 2) for k, v in f["warianty"].items()}, f["c_zamiany"], f["c2_zamiany"])

if __name__ == "__main__":
    main()
