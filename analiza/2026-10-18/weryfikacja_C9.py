"""Weryfikacja C9: P(przebicia kill switcha) z kapitalem ~1,7% nad progiem, koszyk W8.

Sekcje:
 1. Replikacja ryzyko_extra.py (bootstrap blokowy, 250 sesji, demean, blok 5) + wrazliwosc
    na okno (60/125/250/500/1250), blok (1/5/10/20), demean vs surowe, Gauss.
 2. Poniedzialkowa luka: ksiazka W7 (stan /status 18.10, bez ERIC) jest na rachunku do
    biegu 13:45 UTC -> kill sprawdzany NAJPIERW na W7, nie na W8.
 3. Koszt rotacji (zamkniecie 9 + otwarcie 10 nog przy gross ~240%) jako ubytek poduszki.
 4. Dwa sprawdzenia dziennie (13:45 i 17:05 UTC) vs jedno na zamknieciu (Gauss, mnoznik).
 5. Mechanika restartu: poduszka po (a) reset equity_peak przy START_EQUITY=1000,
    (b) tylko START_EQUITY, (c) oba / usuniecie equity_peak + START_EQUITY=kapital,
    (d) KILL_LEVEL; P(kill) dla kazdej poduszki.
 6. Koszt czekania: E[przestrzal pod progiem | kill], rozklad kapitalu po 20 sesjach.
Zrodlo danych: closes_5y.csv (zamkniecia, survivorship bias). Bez liczb z rachunku:
tylko stosunki zaokraglone do 2 cyfr znaczacych (kapital/szczyt ~0,76 z /status 18.10; equity_peak/START_EQUITY ~1,09) — celowo, zeby z pliku nie dalo sie odtworzyc kwot.
"""
import os, math, json
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
px = pd.read_csv(os.path.join(HERE, "..", "dane", "closes_5y.csv"), parse_dates=["date"]).set_index("date").sort_index()
ret = px.pct_change()
rng = np.random.default_rng(7)
NP = 20000
OUT = []
def P(s=""):
    print(s); OUT.append(s)
WYN = {}

W8L = ["GOOGL", "GILD", "MSFT", "QCOM", "ADP"]; W8S = ["AXON", "DASH", "ALNY", "APP", "FER"]
# ksiazka W7 wg /status 18.10 (ekspozycja/kapital po poziomach wejscia, zaokraglone do 0,25; PANW 0,12 po REDUCE 50%)
W7_BOOK = {"CSCO": +0.25, "MU": +0.225, "MRVL": +0.255, "PANW": +0.123,
           "APP": -0.266, "SBUX": -0.254, "PEP": -0.274, "TMUS": -0.275, "CMCSA": -0.258}
# ERIC (taktyczna, ~0,20 kapitalu) nie ma w closes_5y -> pominiety (zanizenie sigma ksiazki W7 o kilka %)

START = 0.76             # kapital / equity_peak (/status 18.10), ZAOKRAGLONE celowo (CLAUDE.md; oryginalny bieg uzyl wartosci o 3 cyfrach) — poduszka ok. 1,7 %
KILL = 0.75
CUSH = START / KILL - 1  # = ~1,7%
PEAK_OVER_START_EQ = 1.09   # equity_peak / START_EQUITY(1000), ZAOKRAGLONE celowo (CLAUDE.md: bez liczb z rachunku w repo)
KAP_OVER_START_EQ = round(START * PEAK_OVER_START_EQ, 2)  # kapital / START_EQUITY ~0,83 (zaokraglone)

def unit_series(L, S, n, demean=True):
    sl = ret.iloc[-n:][L + S].dropna()
    u = (sl[L].sum(axis=1) - sl[S].sum(axis=1)).values
    return u - u.mean() if demean else u

def book_series(book, n, demean=True):
    sl = ret.iloc[-n:][list(book)].dropna()
    u = sum(w * sl[t].values for t, w in book.items())
    return u - u.mean() if demean else u

def boot_paths(u, n_days, blok, npaths=NP, rng=rng):
    nb = math.ceil(n_days / blok)
    st = rng.integers(0, len(u) - blok + 1, size=(npaths, nb))
    idx = (st[:, :, None] + np.arange(blok)[None, None, :]).reshape(npaths, -1)[:, :n_days]
    return u[idx]

def p_kill(R, alloc, start=START, kill=KILL, peak0=1.0, horizons=(5, 10, 20), cost0=0.0, ret_eq=False):
    """R: macierz zwrotow jednostkowych (sciezki x dni); kapital_t = kapital_{t-1}*(1+alloc*R)."""
    eq = np.full(R.shape[0], start * (1 - cost0)); peak = np.full(R.shape[0], peak0)
    killed = np.zeros(R.shape[0], bool); first = np.full(R.shape[0], -1); eq_at_kill = np.full(R.shape[0], np.nan)
    out = {}
    for t in range(R.shape[1]):
        eq_new = np.where(killed, eq, eq * (1 + alloc * R[:, t]))
        peak = np.maximum(peak, eq_new)
        hit = (~killed) & (eq_new < kill * peak)
        eq_at_kill[hit] = eq_new[hit] / (kill * peak[hit]) - 1
        first[hit] = t
        killed |= hit; eq = eq_new
        if t + 1 in horizons:
            out[t + 1] = killed.mean()
    if ret_eq:
        return out, eq, killed, first, eq_at_kill
    return out

# ---------------------------------------------------------------- 1. replikacja + wrazliwosc
P("# Weryfikacja C9 — wyniki skryptu weryfikacja_C9.py")
P()
P(f"Stan: kapital/szczyt = {START}, prog {KILL} -> poduszka {CUSH*100:.2f}% kapitalu; alloc per noga x 10 nog = gross.")
P()
P("## 1. Replikacja (W8, 250 sesji, demean, blok 5, 20 000 sciezek) i wrazliwosc")
P()
u250 = unit_series(W8L, W8S, 250)
P(f"sigma jednostkowa W8: 250 ses. {u250.std()*100:.2f}%/d; 60 ses. {unit_series(W8L,W8S,60).std()*100:.2f}%/d; "
  f"125 ses. {unit_series(W8L,W8S,125).std()*100:.2f}%/d; 500 ses. {unit_series(W8L,W8S,500).std()*100:.2f}%/d; "
  f"1250 ses. {unit_series(W8L,W8S,1250).std()*100:.2f}%/d")
P()
P("| ALLOC | gross | sigma_d kap. | P(kill 5) | P(kill 10) | P(kill 20) | poduszka w sigma_d |")
P("|---|---|---|---|---|---|---|")
WYN["replikacja"] = {}
for a in (0.24, 0.12, 0.08, 0.06, 0.04):
    R = boot_paths(u250, 20, 5)
    pk = p_kill(R, a)
    WYN["replikacja"][a] = pk
    P(f"| {a:.2f} | {a*10*100:.0f}% | {u250.std()*a*100:.2f}% | {pk[5]*100:.0f}% | {pk[10]*100:.0f}% | {pk[20]*100:.0f}% | {CUSH/(u250.std()*a):.1f} |")
P()
P("Wrazliwosc (ALLOC 0,24 / 0,08; P(kill 5) / P(kill 10)):")
P()
P("| wariant | sigma_d (0,24) | 0,24: 5 ses. | 0,24: 10 ses. | 0,08: 5 ses. | 0,08: 10 ses. |")
P("|---|---|---|---|---|---|")
WYN["wrazliwosc"] = {}
for nazwa, u, blok in [("okno 60, blok 5", unit_series(W8L, W8S, 60), 5),
                       ("okno 125, blok 5", unit_series(W8L, W8S, 125), 5),
                       ("okno 250, blok 1", u250, 1),
                       ("okno 250, blok 10", u250, 10),
                       ("okno 250, blok 20", u250, 20),
                       ("okno 250, SUROWE (z dryfem hist.)", unit_series(W8L, W8S, 250, demean=False), 5),
                       ("okno 500, blok 5", unit_series(W8L, W8S, 500), 5),
                       ("okno 1250, blok 5", unit_series(W8L, W8S, 1250), 5)]:
    R = boot_paths(u, 20, blok)
    r24 = p_kill(R, 0.24); r08 = p_kill(R, 0.08)
    WYN["wrazliwosc"][nazwa] = {"0.24": r24, "0.08": r08, "sigma_unit": float(u.std())}
    P(f"| {nazwa} | {u.std()*0.24*100:.2f}% | {r24[5]*100:.0f}% | {r24[10]*100:.0f}% | {r08[5]*100:.0f}% | {r08[10]*100:.0f}% |")
# Gauss o tej samej sigma
for a in (0.24, 0.08):
    G = rng.standard_normal((NP, 20)) * u250.std()
    g = p_kill(G, a)
    WYN["wrazliwosc"][f"gauss_{a}"] = g
    P(f"| Gauss iid, sigma 250 ses., ALLOC {a} | {u250.std()*a*100:.2f}% | {g[5]*100:.0f}% | {g[10]*100:.0f}% | - | - |")
# analityczne: odbicie dla ciaglego monitoringu (gorna granica)
for a in (0.24, 0.08):
    s = u250.std() * a
    from math import erf, sqrt
    Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))
    d = -math.log(1 - CUSH / (1 + CUSH))  # log-odleglosc do progu
    P(f"| odbicie (ciagly monitoring, Gauss), ALLOC {a} | {s*100:.2f}% | {2*Phi(-d/(s*sqrt(5)))*100:.0f}% | {2*Phi(-d/(s*sqrt(10)))*100:.0f}% | - | - |")
P()

# ---------------------------------------------------------------- 2. poniedzialkowa luka na W7
P("## 2. Poniedzialek 13:45 UTC: kill sprawdzany na KSIAZCE W7 (przed rotacja)")
P()
b250 = book_series(W7_BOOK, 250); b500 = book_series(W7_BOOK, 500)
gross7 = sum(abs(w) for w in W7_BOOK.values())
P(f"ksiazka W7 (9 pozycji z /status, wagi = ekspozycja/kapital, gross {gross7*100:.0f}%, bez ERIC): "
  f"sigma dzienna kapitalu 250 ses. {b250.std()*100:.2f}%, 500 ses. {b500.std()*100:.2f}%; ostatnie 5 sesji (13–16.10 + 12.10) zrealizowane: "
  + ", ".join(f"{x*100:+.1f}%" for x in book_series(W7_BOOK, 5, demean=False)))
P()
P("Luka pt. zamkniecie -> pon. 13:45 UTC to ~1 sesja zwrotu (weekend) z udzialem wariancji f (overnight/doba). P(strata > poduszka) z bootstrapu 1-dniowego:")
P()
P("| f (udzial wariancji luki) | P(kill 13:45 pon., 250 ses.) | 500 ses. | Gauss |")
P("|---|---|---|---|")
WYN["pon_luka"] = {}
for f in (0.3, 0.5, 0.7, 1.0):
    s = math.sqrt(f)
    p1 = (b250 * s < -CUSH / (1 + CUSH) * 1.0).mean()  # strata > poduszka (w % kapitalu)
    p2 = (b500 * s < -CUSH / (1 + CUSH)).mean()
    from math import erf, sqrt
    Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))
    pg = Phi(-(CUSH / (1 + CUSH)) / (b250.std() * s))
    WYN["pon_luka"][f] = {"p250": float(p1), "p500": float(p2), "gauss": float(pg)}
    P(f"| {f:.1f} | {p1*100:.0f}% | {p2*100:.0f}% | {pg*100:.0f}% |")
P()
P("Uwaga: poduszka liczona od kapitalu = ~1,7% kapitalu = 1,64% w ujeciu 'strata/kapital' (0,0167/1,0167). W7 na rachunku to realny stan 18.10 (pokrycie_koszyka: 9 pozycji spoza koszyka W8, APP SELL kontynuowany).")
P()

# ---------------------------------------------------------------- 3. laczna sciezka: luka W7 -> koszt rotacji -> W8
P("## 3. Laczna sciezka: pon. 13:45 na W7 (f=0,5) -> rotacja z kosztem c -> W8 od 17:05 (ALLOC a)")
P()
P("Koszt rotacji c = spread polowkowy ~0,05–0,15% x (9 zamkniec + 10 otwarc) x ~24% nominalu = ok. 0,2–0,7% kapitalu (audyt 28.09: AVGO 0,088%, SBUX 0,328%, CMCSA 0,312% na pare; wykonanie-bota.md: podwojny spread w dniu rotacji).")
P()
P("| ALLOC W8 | c | P(kill pon. 13:45) | P(kill w 5 ses.) | P(kill w 10 ses.) | P(kill w 20 ses.) |")
P("|---|---|---|---|---|---|")
WYN["laczna"] = {}
for a in (0.24, 0.12, 0.08, 0.04):
    for c in (0.0, 0.003, 0.006):
        gap = b250[rng.integers(0, len(b250), NP)] * math.sqrt(0.5)
        eq0 = START * (1 + gap)
        killed0 = eq0 < KILL
        # dalej: W8 od 17:05 pon.: sesja pon. (druga polowa, f=0,5) + 19 pelnych sesji
        R = boot_paths(u250, 20, 5)
        R[:, 0] *= math.sqrt(0.5)
        eq = np.where(killed0, eq0, eq0 * (1 - c)); peak = np.ones(NP); killed = killed0.copy()
        res = {}
        for t in range(20):
            eq_new = np.where(killed, eq, eq * (1 + a * R[:, t]))
            peak = np.maximum(peak, eq_new)
            killed |= eq_new < KILL * peak; eq = eq_new
            if t + 1 in (5, 10, 20):
                res[t + 1] = killed.mean()
        WYN["laczna"][f"{a}_{c}"] = {"pon": float(killed0.mean()), **{str(k): float(v) for k, v in res.items()}}
        P(f"| {a:.2f} | {c*100:.1f}% | {killed0.mean()*100:.0f}% | {res[5]*100:.0f}% | {res[10]*100:.0f}% | {res[20]*100:.0f}% |")
P()

# ---------------------------------------------------------------- 4. dwa sprawdzenia dziennie
P("## 4. Dwa sprawdzenia dziennie (13:45 i 17:05 UTC) zamiast jednego na zamknieciu — Gauss, ta sama sigma dzienna")
P()
P("| ALLOC | 1 sprawdzenie/d: 5 ses. | 2 sprawdzenia/d (f=0,5): 5 ses. | 10 ses.: 1 | 10 ses.: 2 |")
P("|---|---|---|---|---|")
WYN["dwa_sprawdzenia"] = {}
for a in (0.24, 0.08):
    s = u250.std()
    G1 = rng.standard_normal((NP, 10)) * s
    g1 = p_kill(G1, a, horizons=(5, 10))
    G2 = rng.standard_normal((NP, 20)) * s * math.sqrt(0.5)
    g2 = p_kill(G2, a, horizons=(10, 20))
    WYN["dwa_sprawdzenia"][a] = {"1x_5": g1[5], "2x_5": g2[10], "1x_10": g1[10], "2x_10": g2[20]}
    P(f"| {a:.2f} | {g1[5]*100:.0f}% | {g2[10]*100:.0f}% | {g1[10]*100:.0f}% | {g2[20]*100:.0f}% |")
P()

# ---------------------------------------------------------------- 5. mechanika restartu
P("## 5. Mechanika restartu wg app.py:1488-1492: odniesienie = max(equity_peak or START_EQUITY, START_EQUITY); prog = odniesienie x KILL_LEVEL")
P()
P(f"kapital/START_EQUITY(1000) ~ {KAP_OVER_START_EQ:.2f} (equity_peak/1000 ~ {PEAK_OVER_START_EQ:.2f}; wartosci zaokraglone celowo; START_EQUITY na Renderze NIE jest w /status.ustawienia — zalozono domyslne 1000 z app.py:164).")
P()
opcje = {
    "(0) nic nie robic": CUSH,
    "(a) equity_peak := kapital, START_EQUITY 1000 bez zmian -> odniesienie = START_EQUITY": KAP_OVER_START_EQ / 0.75 - 1,
    "(b) tylko START_EQUITY := kapital (equity_peak w pliku bez zmian) -> odniesienie = equity_peak": CUSH,
    "(c) equity_peak := kapital ORAZ START_EQUITY <= kapital (albo usunac equity_peak + START_EQUITY := kapital)": 1 / 0.75 - 1,
    "(d) KILL_LEVEL 0,70, szczyt bez zmian": START / 0.70 - 1,
    "(e) KILL_LEVEL 0,65, szczyt bez zmian": START / 0.65 - 1,
}
P("| opcja | poduszka nad progiem | 0,24: P(kill 5/10/20/60 ses.) | 0,08: P(kill 5/10/20/60) |")
P("|---|---|---|---|")
WYN["restart"] = {}
for nazwa, cush in opcje.items():
    row = {}
    for a in (0.24, 0.08):
        R = boot_paths(u250, 60, 5)
        pk = p_kill(R, a, start=KILL * (1 + cush), kill=KILL, peak0=1.0, horizons=(5, 10, 20, 60))
        row[a] = pk
    WYN["restart"][nazwa] = {str(a): {str(k): float(v) for k, v in r.items()} for a, r in row.items()}
    P(f"| {nazwa} | {cush*100:.1f}% | " + "/".join(f"{row[0.24][h]*100:.0f}%" for h in (5, 10, 20, 60)) + " | "
      + "/".join(f"{row[0.08][h]*100:.0f}%" for h in (5, 10, 20, 60)) + " |")
P()
P("Uwaga do (c): po restarcie bot przy pierwszym zapisie fills nadpisze equity_peak = max(zapisany, kapital) (app.py:1960-1961), wiec reset trzyma sie tylko, gdy START_EQUITY <= nowy equity_peak; przy START_EQUITY > kapital odniesienie i tak = START_EQUITY (opcja a).")
P()

# ---------------------------------------------------------------- 6. koszt czekania
P("## 6. Koszt czekania na automatyczny kill vs restart teraz (W8, 20 sesji, zero alfy)")
P()
P("| ALLOC | P(kill 20) | E[przestrzal pod progiem | kill] | mediana sesji do kill | kapital/szczyt po 20 ses.: p5 / mediana / p95 | E[kapital/szczyt] |")
P("|---|---|---|---|---|---|")
WYN["czekanie"] = {}
for a in (0.24, 0.12, 0.08, 0.04):
    R = boot_paths(u250, 20, 5)
    pk, eq, killed, first, over = p_kill(R, a, horizons=(20,), ret_eq=True)
    ov = -np.nanmean(over[killed]) * 100
    med = np.median(first[killed]) + 1 if killed.any() else float("nan")
    WYN["czekanie"][a] = {"p20": float(pk[20]), "przestrzal_pct": float(ov), "med_sesji": float(med),
                          "p5": float(np.percentile(eq, 5)), "med": float(np.median(eq)), "p95": float(np.percentile(eq, 95)), "mean": float(eq.mean())}
    P(f"| {a:.2f} | {pk[20]*100:.0f}% | {ov:.2f}% | {med:.0f} | {np.percentile(eq,5):.3f} / {np.median(eq):.3f} / {np.percentile(eq,95):.3f} | {eq.mean():.4f} |")
P()
P(f"Restart teraz (zamkniecie W7 na poziomie {START} szczytu, koszt zamkniecia ~0,2–0,3%) = kapital/szczyt ~{START*(1-0.0025):.3f} pewny; czekanie: ten sam E[kapital] minus koszty, ale rozklad dwumodalny (kill ~0,74 albo W8 w grze).")
P()

json.dump(WYN, open(os.path.join(HERE, "weryfikacja_C9_wyniki.json"), "w"), indent=1, default=float)
open(os.path.join(HERE, "weryfikacja_C9_out.md"), "w").write("\n".join(OUT) + "\n")
