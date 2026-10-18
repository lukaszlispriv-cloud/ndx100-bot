"""Wspólny loader: closes_5y.csv (czysty csv, bez pandas) + definicje koszyków W1–W8.
Źródła koszyków: W1–W3 tabele rozliczeń w reports/raport-2026-W2..W4.html; W4–W8 koszyki_historia.json.
"""
import csv, math, statistics as st

CSV = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv"

def load():
    r = csv.reader(open(CSV)); hdr = next(r); rows = [row for row in r]
    idx = {h: i for i, h in enumerate(hdr)}
    dates = [row[0] for row in rows]
    px = {}
    for t, i in idx.items():
        if t == "date": continue
        px[t] = [float(row[i]) if row[i] not in ("", None) else None for row in rows]
    return dates, px

DATES, PX = load()
DI = {d: i for i, d in enumerate(DATES)}

def close(t, d):
    return PX[t][DI[d]]

def di(d):
    return DI[d]

def ret(t, d0, d1):
    a, b = close(t, d0), close(t, d1)
    return b / a - 1 if a and b else None

def daily_returns(t, i0, i1):
    """proste zwroty c/c dla indeksów i0..i1 (włącznie i1), z pominięciem braków"""
    out = []
    for i in range(i0 + 1, i1 + 1):
        a, b = PX[t][i - 1], PX[t][i]
        if a and b:
            out.append(b / a - 1)
    return out

# koszyki: D0 (zamknięcie odniesienia), wejście (pierwsza sesja po D0 = bieg bota),
# rozliczenie (D+5 wg raportu), następna rotacja (dzień zamknięcia pozycji na rachunku)
KOSZYKI = {
 "W1": dict(d0="2026-08-26", entry="2026-08-27", settle="2026-08-28", rot="2026-08-31",
            long=["MU","LITE","CEG","AMD","MSFT"], short=["INTU","WDAY","APP","TSLA","CMCSA"]),
 "W2": dict(d0="2026-08-28", entry="2026-08-31", settle="2026-09-04", rot="2026-09-08",
            long=["MU","NVDA","MSFT","AMD","CEG"], short=["INTU","APP","TSLA","CMCSA","PEP"]),
 "W3": dict(d0="2026-09-04", entry="2026-09-08", settle="2026-09-11", rot="2026-09-14",
            long=["MU","NVDA","AMD","AVGO","STX"], short=["TSLA","INTU","SBUX","APP","CMCSA"]),
 "W4": dict(d0="2026-09-11", entry="2026-09-14", settle="2026-09-28", rot="2026-09-29",
            long=["MU","AMD","AVGO","MRVL","LITE"], short=["INTU","SBUX","CMCSA","APP","ADSK"]),
 "W5": dict(d0="2026-09-28", entry="2026-09-29", settle="2026-10-02", rot="2026-10-05",
            long=["MU","AMD","ALAB","STX","TER"], short=["SBUX","NFLX","PEP","CMCSA","APP"]),
 "W6": dict(d0="2026-10-02", entry="2026-10-05", settle="2026-10-09", rot="2026-10-12",
            long=["MU","LITE","TER","AMAT","AMD"], short=["APP","NFLX","PAYX","CMCSA","SBUX"]),
 "W7": dict(d0="2026-10-09", entry="2026-10-12", settle="2026-10-16", rot=None,
            long=["MU","LITE","MRVL","PANW","CSCO"], short=["CMCSA","SBUX","PEP","TMUS","APP"]),
 "W8": dict(d0="2026-10-16", entry=None, settle=None, rot=None,
            long=["GOOGL","GILD","MSFT","QCOM","ADP"], short=["AXON","DASH","ALNY","APP","FER"]),
}

def spread(long, short, d0, d1, bench="^NDX", relative=True):
    """spread_pp wg konwencji history: śr. zwrot pozycji long + śr. zwrot pozycji short, vs ^NDX (p.p.)"""
    rb = ret(bench, d0, d1) if relative else 0.0
    L = [ret(t, d0, d1) - rb for t in long]
    S = [-(ret(t, d0, d1) - rb) for t in short]
    return 100 * (st.mean(L) + st.mean(S)), L, S

def mean_sd(x):
    m = st.mean(x); sd = st.stdev(x) if len(x) > 1 else float("nan")
    return m, sd
