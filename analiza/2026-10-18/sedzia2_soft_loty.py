"""Sędzia 2: wykonalność progu miękkiego ×0,5 (A, C) przy locie 0,1 akcji.
Odtwarza calc_size z app.py (krok 0,1; MAX_OVERSHOOT 1,6; krok w górę do 1,25× celu)
dla kursów z ostatniego wiersza closes_5y.csv. Kapitał odniesienia 1000 USD (START_EQUITY, app.py:164)
i 0,83×1000 (stosunek z C9). Bez liczb z rachunku."""
import csv, math, json, sys
PLIK = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv"
with open(PLIK) as f:
    rows = list(csv.DictReader(f))
last = rows[-1]
tick = [k for k in last if k and not k.startswith("^") and k not in ("Date","date","QQQ","XLP","XLU","XLV","SMH","IGV") and last[k]]
ceny = {t: float(last[t]) for t in tick}
STEP, OVER = 0.1, 1.6
def calc_size(target, mid):
    surowy = target / mid
    dol = math.floor(surowy / STEP) * STEP
    gora = dol + STEP
    size = dol
    if dol >= STEP:
        if abs(gora*mid - target) < abs(dol*mid - target) and gora*mid <= target*1.25:
            size = gora
    size = round(size, 4)
    if size < STEP:
        return STEP if STEP*mid <= target*OVER else None
    return size
def tabela(kap, alloc):
    cel = kap*alloc; cel_soft = cel*0.5
    pom0 = 0; red_ok = 0; red_brak = 0; red_niewyk = 0; red_czesc = 0
    nazwy = {"pom0":[], "niewyk":[], "brak":[]}
    for t, p in ceny.items():
        s0 = calc_size(cel, p)
        if s0 is None:
            pom0 += 1; nazwy["pom0"].append(t); continue
        s1 = calc_size(cel_soft, p)
        if s1 is None:
            red_niewyk += 1; nazwy["niewyk"].append(t)
        elif s1 >= s0:
            red_brak += 1; nazwy["brak"].append(t)
        else:
            r = 1 - s1/s0
            if r >= 0.4: red_ok += 1
            else: red_czesc += 1
    n = len(ceny)
    return {"kapital": kap, "alloc": alloc, "cel_usd": round(cel), "n": n, "pomijane_juz_przy_pelnym": pom0,
            "soft_redukcja>=40%": red_ok, "soft_redukcja<40%": red_czesc, "soft_brak_redukcji(min lot)": red_brak,
            "soft_niewykonalny(close|keep)": red_niewyk, "nazwy": {k: sorted(v) for k, v in nazwy.items()}}
out = []
for kap in (1000.0, 830.0):
    for alloc in (0.12, 0.08, 0.06):
        out.append(tabela(kap, alloc))
# koszyki: E (C) i W8 (FAKT)
E = ["CRWD","AMD","FTNT","TRI","ABNB","APP","AVGO","PAYX","NFLX","CMCSA"]
W8 = ["GOOGL","GILD","MSFT","QCOM","ADP","AXON","DASH","ALNY","APP","FER"]
A_W8 = ["CRWD","DDOG","PANW","FTNT","AMD","NFLX","FER","APP","ALNY","CMCSA"]
def koszyk(nazwa, lst, kap, alloc):
    cel = kap*alloc; w = []
    for t in lst:
        p = ceny.get(t)
        if p is None: w.append((t, "brak kursu")); continue
        s0 = calc_size(cel, p); s1 = calc_size(cel*0.5, p)
        w.append((t, round(p), None if s0 is None else round(s0*p), None if s1 is None else round(s1*p)))
    return {"koszyk": nazwa, "kapital": kap, "alloc": alloc, "cel": round(cel), "nogi(ticker,kurs,USD pełny,USD po soft)": w}
kosz = [koszyk("E", E, 830.0, 0.08), koszyk("A-W8", A_W8, 830.0, 0.08), koszyk("W8 FAKT", W8, 830.0, 0.08), koszyk("W8 FAKT", W8, 830.0, 0.06)]
# limit depozytowy: MARGIN_BUDGET 0.60 (app.py:135), stopa 0.20 normalna, 0.48 przy hipotezie 2,4× z wykonanie-bota.md
limit = {s: round(0.60/s, 2) for s in (0.20, 0.48)}
res = {"uniwersum": out, "koszyki": kosz, "max_brutto_jako_wielokrotnosc_kapitalu": limit,
       "gross": {"A cap 0.12": 1.2, "C/A 0.08": 0.8, "B 0.06": 0.6}}
json.dump(res, open("sedzia2_soft_loty_wyniki.json","w"), indent=1, ensure_ascii=False)
for r in out:
    print({k: v for k, v in r.items() if k != "nazwy"})
    print("   niewykonalne po soft:", " ".join(r["nazwy"]["niewyk"][:30]))
    print("   bez redukcji (min lot):", " ".join(r["nazwy"]["brak"][:30]))
for k in kosz: print(k)
print(limit)
