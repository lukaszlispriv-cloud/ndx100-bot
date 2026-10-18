"""(a) Koszt opóźnienia wejścia: D0 (zamknięcie piątkowe) vs pierwsza sesja po D0 (bieg bota 13:45/17:05 UTC).
Trzy serie na każdy tydzień:
  model      : D0 close -> settle close (jak history.spread_pp)
  wejscie_D1 : entry close -> settle close (ten sam koniec, inne wejście)  => koszt opóźnienia = wejscie_D1 - model
  konto      : entry close -> rot close (okno tak, jak rachunek naprawdę trzyma pozycje: od rotacji do rotacji)
Aproksymacja: cena wejścia = zamknięcie sesji wejścia (bot wchodzi 13:45/17:05 UTC, czyli 9:45/13:05 ET; bez danych intraday).
Dodatkowo tam, gdzie znane są ceny fills (W6, W7) – wariant od faktycznych cen wejścia.
"""
import json, statistics as st
from wyk_common import *

FILLS = {  # faktyczne ceny z ledgera fills (git signals.json) dla nóg NOWYCH w danej rotacji
 "W6": {"LITE": 1088.08, "AMAT": 535.82, "PAYX": 98.87},            # 5.10, bieg 17:05 UTC
 "W7": {"PANW": 411.82, "CSCO": 116.47, "MRVL": 273.80,            # 12.10, bieg 13:45 UTC
        "PEP": 126.91, "TMUS": 152.79},                               # 12.10, bieg 17:05 UTC
 "W5": {"ALAB": 362.18, "STX": 915.81, "TER": 406.82, "PEP": 127.84, "NFLX": 69.87},  # 29.09
}

rows = []
for w, k in KOSZYKI.items():
    if not k["settle"]: continue
    m, _, _ = spread(k["long"], k["short"], k["d0"], k["settle"])
    e, _, _ = spread(k["long"], k["short"], k["entry"], k["settle"])
    kon = spread(k["long"], k["short"], k["entry"], k["rot"])[0] if k["rot"] else None
    # wariant z fills: dla nóg w FILLS cena wejścia = fill, dla pozostałych zamknięcie entry
    f = None
    if w in FILLS:
        rb = ret("^NDX", k["entry"], k["settle"])
        L = []; S = []
        for t in k["long"]:
            p0 = FILLS[w].get(t, close(t, k["entry"]))
            L.append(close(t, k["settle"]) / p0 - 1 - rb)
        for t in k["short"]:
            p0 = FILLS[w].get(t, close(t, k["entry"]))
            S.append(-(close(t, k["settle"]) / p0 - 1 - rb))
        f = 100 * (st.mean(L) + st.mean(S))
    # ruch D0->entry per noga (ile "uciekło")
    luka = {t: round(100 * ret(t, k["d0"], k["entry"]), 2) for t in k["long"] + k["short"]}
    rows.append(dict(week=w, d0=k["d0"], entry=k["entry"], settle=k["settle"], rot=k["rot"],
                     model=round(m, 2), wejscie_D1=round(e, 2), koszt_opoznienia=round(e - m, 2),
                     konto=round(kon, 2) if kon is not None else None,
                     z_fills=round(f, 2) if f is not None else None, luka_D0_entry=luka))

print(f"{'W':4}{'D0':12}{'entry':12}{'settle':12}{'model':>8}{'od D1':>8}{'koszt':>8}{'konto':>8}{'fills':>8}")
for r in rows:
    print(f"{r['week']:4}{r['d0']:12}{r['entry']:12}{r['settle']:12}{r['model']:8.2f}{r['wejscie_D1']:8.2f}"
          f"{r['koszt_opoznienia']:8.2f}{(r['konto'] if r['konto'] is not None else float('nan')):8.2f}"
          f"{(r['z_fills'] if r['z_fills'] is not None else float('nan')):8.2f}")
k47 = [r for r in rows if r["week"] in ("W4", "W5", "W6", "W7")]
print("\nW4–W7: suma model %.2f, suma od D1 %.2f, suma koszt opóźnienia %.2f p.p." % (
    sum(r["model"] for r in k47), sum(r["wejscie_D1"] for r in k47), sum(r["koszt_opoznienia"] for r in k47)))
print("W1–W7: suma model %.2f, od D1 %.2f, koszt %.2f; konto (rotacja->rotacja, W1–W6) %.2f" % (
    sum(r["model"] for r in rows), sum(r["wejscie_D1"] for r in rows), sum(r["koszt_opoznienia"] for r in rows),
    sum(r["konto"] for r in rows if r["konto"] is not None)))
ko = [r["koszt_opoznienia"] for r in rows]
print("koszt opóźnienia: śr %.2f, sd %.2f, n=%d, t=%.2f" % (st.mean(ko), st.stdev(ko), len(ko), st.mean(ko) / (st.stdev(ko) / len(ko) ** 0.5)))
print("\nluka D0->entry per noga (%):")
for r in rows:
    print(r["week"], r["luka_D0_entry"])
json.dump(rows, open("/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/wyk_a_wynik.json", "w"), indent=1)
