"""(b) Twardy stop 10% od poziomu brokera + ponowne otwarcie bez wpisu exclude.
Część 1: W7 z FAKTYCZNYMI poziomami brokera i ponownych otwarć (fills z git signals.json, raport W8).
Część 2: symulacja na zamknięciach dziennych W1–W7 (entry = zamknięcie pierwszej sesji po D0,
         wyjście = zamknięcie dnia rozliczenia; stop sprawdzany na ZAMKNIĘCIU każdej sesji —
         bot sprawdza 13:45 i 17:05 UTC intraday, więc to jest DOLNE oszacowanie liczby stopów).
Warianty: bez stopu | stop X% bez ponownego otwarcia | stop X% + ponowne otwarcie tego samego dnia
          (po tym samym zamknięciu, nowy punkt odniesienia; bot: zamknięcie 13:45, otwarcie 17:05) |
          REDUCE 50% przy -X% (zostaje w książce, bez ponownego otwarcia)
Wynik nogi w % wartości pozycji; wkład do kapitału = wynik × ALLOC (0,24).
"""
import statistics as st
from wyk_common import *

ALLOC = 0.24

def path(t, entry_i, exit_i):
    return [PX[t][i] for i in range(entry_i, exit_i + 1)]

def sim_leg(prices, direction, variant, X=0.10, reopen=False, reduce=False):
    """prices[0] = cena wejścia (zamknięcie sesji wejścia), prices[-1] = wyjście.
    Zwraca (pnl w % wartości pełnej pozycji, liczba stopów)."""
    sgn = 1 if direction == "BUY" else -1
    ref = prices[0]; weight = 1.0; pnl = 0.0; stops = 0
    for p in prices[1:]:
        move = sgn * (p / ref - 1)
        if variant != "none" and move <= -X and weight > 0:
            stops += 1
            if reduce:
                # REDUCE: realizuje połowę straty, zostaje połowa z nowym odniesieniem? bot: REDUCE nie zmienia ceny tezy
                pnl += 0.5 * weight * move
                weight *= 0.5
                # dalsza część liczona od tego samego ref (bez re-anchor) – stop nie powtarza się na tej samej cenie tezy
                continue
            pnl += weight * move
            if reopen:
                ref = p          # ponowne otwarcie po tym samym zamknięciu, nowy punkt odniesienia
            else:
                weight = 0.0
    if weight > 0:
        pnl += weight * sgn * (prices[-1] / ref - 1)
    return 100 * pnl, stops

VARIANTS = [
 ("bez stopu",            dict(variant="none")),
 ("stop10 bez reopen",    dict(variant="stop", X=0.10)),
 ("stop10 + reopen",      dict(variant="stop", X=0.10, reopen=True)),
 ("stop15 bez reopen",    dict(variant="stop", X=0.15)),
 ("stop15 + reopen",      dict(variant="stop", X=0.15, reopen=True)),
 ("REDUCE50 przy -10",    dict(variant="stop", X=0.10, reduce=True)),
 ("stop20 bez reopen",    dict(variant="stop", X=0.20)),
]

print("=== CZĘŚĆ 1: W7, faktyczne poziomy (poziom brokera / stop / ponowne otwarcie / zamknięcie 16.10) ===")
# (poziom brokera, cena stopu [optymistycznie = dokładnie próg], ponowne otwarcie, waga po reopen, close 16.10)
W7 = {
 "MU":   dict(broker=1063.70, stop_lvl=957.33, reopen=935.73, w2=1.0, end=878.84, stop_day="2026-10-13", stop_close=953.19),
 "LITE": dict(broker=1088.08, stop_lvl=979.27, reopen=None,   w2=0.0, end=824.13, stop_day="2026-10-13", stop_close=987.99),
 "MRVL": dict(broker=267.53,  stop_lvl=240.78, reopen=235.93, w2=1.0, end=227.83, stop_day="2026-10-15", stop_close=241.24),
 "PANW": dict(broker=400.95,  stop_lvl=360.86, reopen=341.71, w2=0.5, end=342.00, stop_day="2026-10-16", stop_close=342.00),
}
tot = {"faktyczny(stop=próg)": 0, "faktyczny(stop=close dnia)": 0, "bez stopu": 0, "stop bez reopen": 0, "stop15 (od brokera)": 0, "REDUCE50 zamiast stopu": 0}
print(f"{'noga':6}{'bez stopu':>11}{'stop,bez re':>12}{'fakt(próg)':>12}{'fakt(close)':>12}{'REDUCE50':>10}{'stop15?':>9}")
for t, d in W7.items():
    none = 100 * (d["end"] / d["broker"] - 1)
    stop_only = 100 * (d["stop_lvl"] / d["broker"] - 1)
    fact = stop_only + (d["w2"] * 100 * (d["end"] / d["reopen"] - 1) if d["reopen"] else 0)
    fact_c = 100 * (d["stop_close"] / d["broker"] - 1) + (d["w2"] * 100 * (d["end"] / d["reopen"] - 1) if d["reopen"] else 0)
    red = 0.5 * stop_only + 0.5 * none
    # stop 15% od poziomu brokera: czy w ogóle zadziałałby (na zamknięciach)? sprawdź min close w oknie
    i0, i1 = di("2026-10-12"), di("2026-10-16")
    mn = min(PX[t][i] for i in range(i0, i1 + 1))
    s15 = "TAK(close)" if mn / d["broker"] - 1 <= -0.15 else "nie(close)"
    s15v = -15.0 if mn / d["broker"] - 1 <= -0.15 else none
    print(f"{t:6}{none:11.2f}{stop_only:12.2f}{fact:12.2f}{fact_c:12.2f}{red:10.2f}{s15:>9}")
    tot["bez stopu"] += none; tot["stop bez reopen"] += stop_only; tot["faktyczny(stop=próg)"] += fact
    tot["faktyczny(stop=close dnia)"] += fact_c; tot["REDUCE50 zamiast stopu"] += red; tot["stop15 (od brokera)"] += s15v
print("suma 4 nóg (% pozycji) i wkład do kapitału przy ALLOC 0,24:")
for k, v in tot.items():
    print(f"  {k:28}{v:8.2f} % pozycji  -> {v * ALLOC:7.2f} % kapitału")

print("\n=== CZĘŚĆ 2: symulacja na zamknięciach, W1–W7, wejście = close pierwszej sesji po D0, wyjście = close rozliczenia ===")
agg = {name: [] for name, _ in VARIANTS}
stops_cnt = {name: 0 for name, _ in VARIANTS}
per_week = {}
for w, k in KOSZYKI.items():
    if not k["settle"]: continue
    i0, i1 = di(k["entry"]), di(k["settle"])
    res = {}
    for name, kw in VARIANTS:
        pnl = 0.0; n_st = 0
        for t, dr in [(t, "BUY") for t in k["long"]] + [(t, "SELL") for t in k["short"]]:
            pr = [p for p in path(t, i0, i1) if p]
            v, s = sim_leg(pr, dr, **kw)
            pnl += v * ALLOC
            n_st += s
        res[name] = (round(pnl, 2), n_st)   # pnl: suma (% pozycji) × ALLOC = % kapitału (bez relatywizacji do NDX — rachunek)
        agg[name].append(pnl); stops_cnt[name] += n_st
    per_week[w] = res
hdr = f"{'W':4}" + "".join(f"{n[:18]:>20}" for n, _ in VARIANTS)
print(hdr)
for w, res in per_week.items():
    print(f"{w:4}" + "".join(f"{res[n][0]:14.2f} ({res[n][1]})" for n, _ in VARIANTS))
print(f"{'suma':4}" + "".join(f"{sum(agg[n]):14.2f} ({stops_cnt[n]})" for n, _ in VARIANTS))
print("(wartości = % kapitału przy ALLOC 0,24, suma 10 nóg, bez kosztów; w nawiasie liczba zadziałań stopu/REDUCE)")

# CZĘŚĆ 3: ile razy w 5 latach noga tego typu przebija -10% od wejścia w 5 sesjach (częstość stopu) i co dzieje się po stopie
print("\n=== CZĘŚĆ 3: panel historyczny 2021-10..2026-10 — okna 5-sesyjne nienakładające się, nogi z koszyków W1–W8 ===")
legs = sorted({t for k in KOSZYKI.values() for t in k["long"] + k["short"]})
n_win = n_hit = 0; after = []; after_reopen = []; full = []
for t in legs:
    s = PX[t]
    for i in range(1, len(s) - 6, 5):
        win = s[i:i + 6]
        if any(p is None for p in win): continue
        n_win += 1
        hit = None
        for j in range(1, 6):
            if win[j] / win[0] - 1 <= -0.10:
                hit = j; break
        full.append(win[5] / win[0] - 1)
        if hit is not None:
            n_hit += 1
            after.append(win[5] / win[hit] - 1)   # ruch od dnia stopu do końca okna (to, co "łapie" reopen)
print(f"okna: {n_win}, z przebiciem -10% (na zamknięciu) w ≤5 sesji: {n_hit} ({100*n_hit/n_win:.2f}%)")
if after:
    m, sd = mean_sd(after)
    print(f"po stopie do końca okna (long): śr {100*m:.2f}%, mediana {100*st.median(after):.2f}%, sd {100*sd:.2f}%, n={len(after)}, "
          f"udział dalszych spadków {100*sum(1 for x in after if x<0)/len(after):.0f}%")
print(f"okno 5 sesji, wszystkie: śr {100*st.mean(full):.2f}%, sd {100*st.stdev(full):.2f}%")
