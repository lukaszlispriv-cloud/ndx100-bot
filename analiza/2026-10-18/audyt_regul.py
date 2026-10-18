#!/usr/bin/env python3 -I
"""Audyt reguł rutyn NDX100 — liczby do notatki audyt-regul.md.

Dane: closes_5y.csv (zamknięcia dzienne, bez korekty o dywidendy — adnotacja),
składy koszyków z raportów W1–W8, tv-screen W8 (market_cap jako statyczne proxy).
Zwrot relatywny nogi = [P1/P0−1] − [NDX1/NDX0−1] w p.p.; dla SHORT ze znakiem minus.
"""
import json, sys, math
import numpy as np, pandas as pd

BASE = "/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad"
px = pd.read_csv(f"{BASE}/dane/closes_5y.csv", parse_dates=["date"]).set_index("date").sort_index()
px = px[px["^NDX"].notna()]  # wiersze bez sesji (święta) usunięte
px = px.ffill(limit=1)          # pojedyncze braki kursu (np. CMCSA 3.09) uzupełnione poprzednim zamknięciem — adnotacja
NDX = px["^NDX"]
OUT = {}

def rel(t, d0, d1, side="L"):
    p = px[t]; r = (p.loc[d1] / p.loc[d0] - 1) * 100 - (NDX.loc[d1] / NDX.loc[d0] - 1) * 100
    return -r if side == "S" else r

def absret(t, d0, d1):
    return (px[t].loc[d1] / px[t].loc[d0] - 1) * 100

# ---------------------------------------------------------------- okna
W = {  # version: (D0, koniec rozliczenia, koniec 5-sesyjny)
 "W1": ("2026-08-26", "2026-08-28", "2026-09-03"),
 "W2": ("2026-08-28", "2026-09-04", "2026-09-04"),
 "W3": ("2026-09-04", "2026-09-11", "2026-09-11"),
 "W4": ("2026-09-11", "2026-09-28", "2026-09-18"),
 "W5": ("2026-09-28", "2026-10-02", "2026-10-02"),
 "W6": ("2026-10-02", "2026-10-09", "2026-10-09"),
 "W7": ("2026-10-09", "2026-10-16", "2026-10-16"),
}
BASKETS = {
 "W1": (["MU","LITE","CEG","AMD","MSFT"], ["INTU","WDAY","APP","TSLA","CMCSA"]),
 "W2": (["MU","NVDA","MSFT","AMD","CEG"], ["INTU","APP","TSLA","CMCSA","PEP"]),
 "W3": (["MU","NVDA","AMD","AVGO","STX"], ["TSLA","INTU","SBUX","APP","CMCSA"]),
 "W4": (["MU","AMD","AVGO","MRVL","LITE"], ["INTU","SBUX","CMCSA","APP","ADSK"]),
 "W5": (["MU","AMD","ALAB","STX","TER"], ["SBUX","NFLX","PEP","CMCSA","APP"]),
 "W6": (["MU","LITE","TER","AMAT","AMD"], ["APP","NFLX","PAYX","CMCSA","SBUX"]),
 "W7": (["MU","LITE","MRVL","PANW","CSCO"], ["CMCSA","SBUX","PEP","TMUS","APP"]),
}
# p z raportów (TOP5/BOTTOM5)
P = {
 "W1": {"MU":62,"LITE":62,"CEG":62,"AMD":61,"MSFT":61,"INTU":62,"WDAY":62,"APP":61,"TSLA":61,"CMCSA":60},
 "W2": {"MU":62,"NVDA":62,"MSFT":61,"AMD":61,"CEG":60,"INTU":62,"APP":61,"TSLA":60,"CMCSA":60,"PEP":58},
 "W3": {"MU":62,"NVDA":62,"AMD":62,"AVGO":62,"STX":62,"TSLA":62,"INTU":59,"SBUX":56,"APP":55,"CMCSA":54},
 "W4": {"MU":62,"AMD":62,"AVGO":62,"MRVL":62,"LITE":61,"INTU":60,"SBUX":56,"CMCSA":56,"APP":57,"ADSK":57},
 "W5": {"MU":62,"AMD":60,"ALAB":61,"STX":60,"TER":58,"SBUX":58,"NFLX":57,"PEP":56,"CMCSA":56,"APP":56},
 "W6": {"MU":62,"LITE":61,"TER":60,"AMAT":60,"AMD":60,"APP":58,"NFLX":58,"PAYX":57,"CMCSA":56,"SBUX":56},
 "W7": {"MU":62,"LITE":61,"MRVL":60,"PANW":59,"CSCO":58,"CMCSA":58,"SBUX":57,"PEP":57,"TMUS":57,"APP":58},
}

# ------------------------------------------------ 1. rozliczenie koszyków (kontrola vs raporty)
rows = []
for w,(d0,d1,d5) in W.items():
    L,S = BASKETS[w]
    for t in L: rows.append(dict(week=w,ticker=t,side="L",rel=rel(t,d0,d1,"L"),rel5=rel(t,d0,d5,"L"),p=P[w][t]))
    for t in S: rows.append(dict(week=w,ticker=t,side="S",rel=rel(t,d0,d1,"S"),rel5=rel(t,d0,d5,"S"),p=P[w][t]))
legs = pd.DataFrame(rows); legs["hit"] = legs.rel > 0
spread = legs.groupby("week").apply(lambda g: g[g.side=="L"].rel.mean()+g[g.side=="S"].rel.mean())
OUT["spread_kontrola"] = spread.round(2).to_dict()
OUT["hit_kontrola"] = legs.groupby("week").hit.sum().to_dict()

# kalibracja p
cal = legs.groupby("p").agg(n=("hit","size"), hit=("hit","mean"), rel=("rel","mean"))
OUT["kalibracja_p"] = {int(k): dict(n=int(v.n), hit=round(v.hit,3), rel=round(v.rel,2)) for k,v in cal.iterrows()}
hi = legs[legs.p>=61]; lo = legs[legs.p<=58]
OUT["kalibracja_p_grupy"] = {"p>=61": dict(n=len(hi), hit=round(hi.hit.mean(),3), rel=round(hi.rel.mean(),2)),
                             "p<=58": dict(n=len(lo), hit=round(lo.hit.mean(),3), rel=round(lo.rel.mean(),2)),
                             "corr_p_rel": round(np.corrcoef(legs.p, legs.rel)[0,1],3)}

# ------------------------------------------------ 2. kontrfaktyczne wykluczenia (reguły imienne)
# (week, ticker, side, reguła, zastąpiona_przez)
EXCL = [
 # zasada świeżej luki W1
 ("W1","NVDA","L","świeża luka po D0 (W1)",None), ("W1","CRWD","L","świeża luka po D0 (W1)",None),
 # event w oknie — poza koszykiem
 ("W1","AVGO","L","event w oknie (raport 2.09)",None), ("W1","MRVL","L","event w oknie (raport)",None),
 ("W2","AVGO","L","event w oknie (raport 2.09)",None), ("W2","PANW","L","event w oknie (raport 1.09)",None),
 ("W3","ADBE","S","event w oknie (raport 10.09)",None), ("W3","CPRT","S","event w oknie (raport 10.09)",None),
 ("W6","PEP","S","event w oknie (raport 8.10)","PAYX"), ("W6","MRVL","L","event w oknie (Investor Day 6.10, kara 6)",None),
 ("W6","COST","S","event w oknie (sprzedaż mies.)",None),
 # M&A / cel wykupu
 ("W2","WDAY","S","żywy cel wykupu (W2)","PEP"), ("W3","WDAY","S","żywy cel wykupu",None), ("W4","WDAY","S","żywy cel wykupu",None),
 ("W5","WDAY","S","żywy cel wykupu",None), ("W6","WDAY","S","żywy cel wykupu",None), ("W7","WDAY","S","żywy cel wykupu",None),
 ("W2","ADBE","S","fala M&A software (W2)","PEP"),
 # pogoń / jednodniowy skok
 ("W2","CRWD","L","pogoń po +15% (W2)",None), ("W3","SNDK","L","skok +12% w 1 sesję (W3)","AVGO"), ("W4","SNDK","L","koncentracja pamięci / −6% (W4)",None),
 ("W3","ADSK","S","chasing po −8% w 1 sesję (W3)","CMCSA"), ("W4","TRI","S","chasing po −7,9% (W4)",None), ("W3","AXON","S","chasing po −14% (W3)",None),
 ("W6","ALNY","S","pogoń po −6% w 1 dzień (W6)","SBUX"),
 # odbiorca vs płatnik — MSFT poza koszykiem od W3
 ("W3","MSFT","L","płatnik capexu (lekcja W2)",None), ("W4","MSFT","L","płatnik capexu",None), ("W5","MSFT","L","płatnik capexu",None),
 ("W6","MSFT","L","płatnik capexu",None), ("W7","MSFT","L","płatnik capexu",None),
 # NVDA DOJ (od W4)
 ("W4","NVDA","L","reguła DOJ/Groq (W4)","MRVL"), ("W5","NVDA","L","reguła DOJ/Groq","AMD"), ("W6","NVDA","L","reguła DOJ/Groq",None), ("W7","NVDA","L","reguła DOJ/Groq",None),
 # TSLA 3 przegrane (od W4)
 ("W4","TSLA","S","TSLA: 3 przegrane tygodnie (D2-W3)","ADSK"), ("W5","TSLA","S","TSLA poza koszykiem",None), ("W6","TSLA","S","TSLA poza koszykiem",None), ("W7","TSLA","S","TSLA poza koszykiem",None),
 # INTU zakaz >20%/10s (D2-W4, do 16.10)
 ("W5","INTU","S","zakaz >20%/10 sesji (D2-W4)","PEP"), ("W6","INTU","S","zakaz >20%/10 sesji",None), ("W7","INTU","S","zakaz >20%/10 sesji",None),
 ("W5","PAYX","S","short po kolapsie (duch D2-W4)",None),
 # przegrana bez odzyskanej siły relatywnej
 ("W2","LITE","L","wypada po przegranej W1 (prekursor reguły)","CEG"), ("W3","LITE","L","wraca po odzyskaniu siły (W3)",None),
 ("W5","LITE","L","przegrana bez odzyskanej siły (W5)","ALAB"), ("W5","AVGO","L","przegrana W4 + negatyw chiński (W5)","STX"), ("W5","MRVL","L","słabsza relatywnie w W4 (W5)","TER"),
 ("W6","ALAB","L","przegrana bez odzyskanej siły (W6)","LITE"), ("W6","STX","L","filar HDD naruszony — news (W6)","AMAT"),
 ("W7","TER","L","przegrana bez odzyskanej siły (W7)","MRVL"), ("W7","AMAT","L","przegrana bez odzyskanej siły (W7)","PANW"), ("W7","AMD","L","przegrana bez odzyskanej siły (W7)","CSCO"),
 ("W7","NFLX","S","przegrana bez odzyskanej słabości (W7)","PEP"), ("W7","PAYX","S","przegrana + D2-W6 (>12%/10s) (W7)","TMUS"),
 # limit 2 na blok pamięć/WFE
 ("W5","LRCX","L","limit 2/blok pamięć-WFE (W5)","TER"), ("W5","AMAT","L","limit 2/blok pamięć-WFE (W5)","TER"),
 ("W6","LRCX","L","limit 2/blok pamięć-WFE (W6)","AMAT"), ("W6","KLAC","L","limit 2/blok (W6)",None),
 # veto
 ("W1","MSTR","S","veto krypto-beta",None),("W2","MSTR","S","veto krypto-beta",None),("W3","MSTR","S","veto krypto-beta",None),("W4","MSTR","S","veto krypto-beta",None),
 ("W5","MSTR","S","veto krypto-beta",None),("W6","MSTR","S","veto krypto-beta",None),("W7","MSTR","S","veto krypto-beta",None),
 ("W1","PDD","S","veto governance",None),("W2","PDD","S","veto governance",None),("W3","PDD","S","veto governance",None),("W4","PDD","S","veto governance",None),
 ("W5","PDD","S","veto governance",None),("W6","PDD","S","veto governance",None),("W7","PDD","S","veto governance",None),
 # rezerwy nie wybrane (tie-break mniejsza waga / wynik)
 ("W6","PANW","L","AMD (69) nad PANW (67) — wynik (W6)","AMD"), ("W7","FTNT","L","CSCO nad FTNT (wycena/2. cyber) (W7)","CSCO"),
 ("W5","NVDA","L","AMD nad NVDA (DOJ + mniejsza waga) (W5)","AMD"), ("W5","MRVL","L","TER nad MRVL (mniejsza waga) (W5)","TER"),
 ("W6","LRCX","L","AMAT nad LRCX (mnożnik, limit bloku) (W6)","AMAT"), ("W6","MRVL","L","TER nad MRVL (event) (W6)","TER"),
 ("W7","NFLX","S","TMUS nad NFLX (świeży negatyw) (W7)","TMUS"), ("W7","AMD","L","CSCO nad AMD (W7)","CSCO"),
]
ex_rows=[]
for w,t,s,rule,repl in EXCL:
    d0,d1,d5 = W[w]
    if t not in px.columns: continue
    r = rel(t,d0,d1,s); r5 = rel(t,d0,d5,s)
    rr = rel(repl,d0,d1,"L" if s=="L" else "S") if repl else np.nan
    ex_rows.append(dict(week=w,ticker=t,side=s,rule=rule,rel_excl=round(r,2),rel5_excl=round(r5,2),repl=repl,rel_repl=round(rr,2) if repl else None,
                        delta_na_nodze=round((rr - r),2) if repl else None))
EX = pd.DataFrame(ex_rows)
OUT["wykluczenia"] = EX.to_dict("records")

# agregaty per reguła
def agg_rule(mask_fn, name):
    sub = EX[EX.rule.apply(mask_fn)]
    OUT.setdefault("reguly_agregat",{})[name] = dict(n=len(sub), srednia_rel_wykluczonej=round(sub.rel_excl.mean(),2),
        suma_rel_wykluczonej=round(sub.rel_excl.sum(),2), ile_wykluczona_wygralaby=int((sub.rel_excl>0).sum()),
        srednia_delta_zastepstwa=(round(sub.delta_na_nodze.dropna().mean(),2) if sub.delta_na_nodze.notna().any() else None),
        n_zastepstw=int(sub.delta_na_nodze.notna().sum()))
agg_rule(lambda r: "odzyskanej" in r or "wypada po przegranej" in r or "wraca po odzyskaniu" in r or "słabsza relatywnie" in r or "przegrana W4" in r, "przegrana_bez_odzyskanej_sily")
agg_rule(lambda r: "DOJ" in r, "NVDA_DOJ")
agg_rule(lambda r: r.startswith("TSLA"), "TSLA_3_przegrane")
agg_rule(lambda r: "zakaz >20%" in r or "kolapsie" in r, "INTU_zakaz_20pct")
agg_rule(lambda r: "event w oknie" in r, "event_w_oknie")
agg_rule(lambda r: "wykupu" in r or "M&A" in r, "cel_wykupu_WDAY_ADBE")
agg_rule(lambda r: "pogoń" in r or "skok" in r or "chasing" in r or "koncentracja pamięci" in r, "pogon_po_skoku")
agg_rule(lambda r: "płatnik" in r, "MSFT_platnik_capexu")
agg_rule(lambda r: "veto krypto" in r, "veto_MSTR")
agg_rule(lambda r: "veto governance" in r, "veto_PDD")
agg_rule(lambda r: "limit 2" in r, "limit_2_na_blok")
agg_rule(lambda r: " nad " in r, "tie_break_i_decyzje_graniczne")

# ------------------------------------------------ 3. deklaracje D1–D3 (z raportów) — rejestr
DEKL = [
 ("W1","D1","MU > NDX","NIE (−1,31, D+2)","brak"),("W1","D2","trio software short ≤ −1 pp","NIE (+3,95 przeciw)","lekcja: rozproszenie shortów, czynnik M&A → W2"),
 ("W1","D3","AVGO cel AI FY27","przeniesiona","—"),
 ("W2","D1","MU > NDX","TAK (+8,60)","—"),("W2","D2","AVGO podtrzyma cel","TAK","—"),("W2","D3","INTU ≤ −1 pp","TAK (+7,46)","—"),
 ("W3","D1","STX > NDX","NIE (−1,66)","STX do rezerwy"),("W3","D2","TSLA ≤ −1 pp","NIE (−3,80)","TSLA poza koszykiem bez względu na model (W4→W8)"),
 ("W3","D3","brak cięć elity / obniżki DRAM","TAK z zastrz.","—"),
 ("W4","D1","MRVL > NDX (5s)","TAK (+2,51)","—"),("W4","D2","ADSK ≤ −1 pp (5s)","NIE (+1,20 przeciw)","ZAKAZ short po >20%/10s przez 4 tyg. (do 16.10) → INTU poza W5–W7"),
 ("W4","D3","MU traci mniej po podwyżce","NIE","brak (teza wyceny-amortyzatora obalona, bez reguły)"),
 ("W5","D1","MU > NDX mimo raportu","TAK (+0,23)","kara event zostaje 8 (nie 15)"),("W5","D2","NFLX ≤ −1 pp","TAK (+4,89)","—"),
 ("W5","D3","read-across MU → blok","TAK (+1,45)","—"),
 ("W6","D1","LITE > NDX (powrót po sile rel.)","TAK (+1,41)","warunek powrotu bez wymogu rewizji"),("W6","D2","PAYX ≤ −1 pp","NIE (−4,85)","SITO >12%/10s wymaga twardego negatywu (od W7); PAYX poza"),
 ("W6","D3","MRVL przegra po Investor Day","NIE (+2,11)","KARA EVENT pozytywny 6 → 3 (od W7)"),
 ("W7","D1","MU > NDX (nadpisanie reguły)","NIE (−9,09)","MU poza W8; reguła „bez odzyskanej siły” bez wyjątku dla wyceny"),
 ("W7","D2","TMUS nie odrobi >50% luki","NIE (+12,57 przeciw)","NOWA REGUŁA: nie shortuj w 1. oknie po luce >10% bez wyników (retest 12 tyg.)"),
 ("W7","D3","WFE dodatnie po ASML","NIE (−1,75)","AMAT nie wraca; (bez nowej reguły)"),
 ("W8","D1","GOOGL > NDX","otwarta (23.10)","kandydat: płatnicy [2] bez premii za wycenę"),("W8","D2","SNDK nie pobije NDX","otwarta","falsyfikacja zdejmuje filtr siły rel. dla kandydatów spoza koszyka"),
 ("W8","D3","read-across NFLX → APP/DASH","otwarta (warunkowa)","read-across skreślony z argumentów"),
]
OUT["deklaracje"] = [dict(week=a,d=b,tresc=c,wynik=d,konsekwencja=e) for a,b,c,d,e in DEKL]
resolved = [d for d in DEKL if d[3].startswith(("TAK","NIE"))]
OUT["deklaracje_bilans"] = dict(rozstrzygnietych=len(resolved), TAK=sum(d[3].startswith("TAK") for d in resolved), NIE=sum(d[3].startswith("NIE") for d in resolved),
                                 konsekwencji_regulowych=sum(1 for d in DEKL if any(k in d[4] for k in ["ZAKAZ","SITO","KARA","NOWA REGUŁA","poza koszykiem","MU poza"])))

# ------------------------------------------------ 4. testy przekrojowe na 5 latach (okna nienakładające się)
dates = px.index
# uniwersum: spółki (bez indeksów/ETF)
UNIV = [c for c in px.columns if not c.startswith("^") and c not in ("QQQ","XLP","XLU","XLV","SMH","IGV")]
P5 = px[UNIV]; N = NDX
lr = np.log(P5).diff()
# okna co 5 sesji
idx = np.arange(0, len(dates), 5)
rec = []
for k in range(len(idx)-1):
    i0, i1 = idx[k], idx[k+1]
    if i0 < 131: continue
    d0, d1 = dates[i0], dates[i1]
    ndx_f = (N.iloc[i1]/N.iloc[i0]-1)*100
    ndx_p = (N.iloc[i0]/N.iloc[i0-5]-1)*100
    ndx_l = (N.iloc[i0]/N.iloc[i0-1]-1)*100
    ndx_10 = (N.iloc[i0]/N.iloc[i0-10]-1)*100
    ndx_m6 = (N.iloc[i0]/N.iloc[i0-126]-1)*100
    for t in UNIV:
        s = P5[t]
        if pd.isna(s.iloc[i0]) or pd.isna(s.iloc[i1]) or pd.isna(s.iloc[i0-126]) : continue
        fwd = (s.iloc[i1]/s.iloc[i0]-1)*100 - ndx_f
        prev = (s.iloc[i0]/s.iloc[i0-5]-1)*100 - ndx_p
        last = (s.iloc[i0]/s.iloc[i0-1]-1)*100 - ndx_l
        r10 = (s.iloc[i0]/s.iloc[i0-10]-1)*100
        mom6 = (s.iloc[i0]/s.iloc[i0-126]-1)*100 - ndx_m6
        win = s.iloc[i0-3:i0+1].values
        d1max = np.nanmax(win[1:]/win[:-1]-1)*100; d1min = np.nanmin(win[1:]/win[:-1]-1)*100
        rec.append((d0,t,fwd,prev,last,r10,mom6,d1max,d1min))
CS = pd.DataFrame(rec, columns=["d0","t","fwd","prev","last","r10","mom6","d1max","d1min"])
CS["q"] = CS.groupby("d0").mom6.transform(lambda x: pd.qcut(x.rank(method="first"), 5, labels=False))
def stats(sub, col="fwd"):
    if len(sub)==0: return dict(n=0)
    g = sub.groupby("d0")[col].mean()
    tcl = g.mean()/(g.std(ddof=1)/math.sqrt(len(g))) if len(g)>1 else float("nan")
    return dict(n=int(len(sub)), n_okien=int(len(g)), srednia=round(sub[col].mean(),2), sd=round(sub[col].std(),2),
                t_klastrowane=round(tcl,2), hit=round((sub[col]>0).mean(),3))
CST = {}
# 4a. "przegrana bez odzyskanej siły" — strona LONG (kandydaci: top kwintyl momentum 6M)
longc = CS[CS.q==4]
CST["long_top_q_wszystkie"] = stats(longc)
CST["long_przegrana_bez_odzyskania(prev<0,last<=0)"] = stats(longc[(longc.prev<0)&(longc["last"]<=0)])
CST["long_przegrana_z_odzyskaniem(prev<0,last>0)"] = stats(longc[(longc.prev<0)&(longc["last"]>0)])
CST["long_wygrana(prev>=0)"] = stats(longc[longc.prev>=0])
CST["long_przegrana_bez_odzyskania_prev<-4"] = stats(longc[(longc.prev<-4)&(longc["last"]<=0)])
# cały przekrój (nie tylko top kwintyl)
CST["univ_przegrana_bez_odzyskania"] = stats(CS[(CS.prev<0)&(CS["last"]<=0)])
CST["univ_przegrana_z_odzyskaniem"] = stats(CS[(CS.prev<0)&(CS["last"]>0)])
CST["univ_wygrana"] = stats(CS[CS.prev>=0])
# strona SHORT (dolny kwintyl); "przegrana" shortu = prev>0 ; brak odzyskanej słabości = last>=0 ; fwd shortu = -fwd
shc = CS[CS.q==0].copy(); shc["fwdS"] = -shc.fwd
CST["short_bot_q_wszystkie"] = stats(shc,"fwdS")
CST["short_przegrana_bez_odzyskania(prev>0,last>=0)"] = stats(shc[(shc.prev>0)&(shc["last"]>=0)],"fwdS")
CST["short_przegrana_z_odzyskaniem(prev>0,last<0)"] = stats(shc[(shc.prev>0)&(shc["last"]<0)],"fwdS")
CST["short_wygrana(prev<=0)"] = stats(shc[shc.prev<=0],"fwdS")
# 4b. sito D2: short po spadku 10-ses. >12% / >20% (dolny kwintyl)
CST["short_r10<=-12"] = stats(shc[shc.r10<=-12],"fwdS"); CST["short_r10<=-20"] = stats(shc[shc.r10<=-20],"fwdS"); CST["short_r10>-12"] = stats(shc[shc.r10>-12],"fwdS")
CST["short_-20<r10<=-12"] = stats(shc[(shc.r10>-20)&(shc.r10<=-12)],"fwdS")
# luka 1-dniowa <= -8% / -10% w 3 sesjach — short
CST["short_luka1d<=-8_w3s"] = stats(shc[shc.d1min<=-8],"fwdS"); CST["short_luka1d<=-10_w3s"] = stats(shc[shc.d1min<=-10],"fwdS")
# cały przekrój (nie tylko dolny kwintyl) — short po spadku
allS = CS.copy(); allS["fwdS"] = -allS.fwd
CST["univ_short_r10<=-12"] = stats(allS[allS.r10<=-12],"fwdS"); CST["univ_short_r10<=-20"] = stats(allS[allS.r10<=-20],"fwdS")
CST["univ_short_luka1d<=-10_w3s"] = stats(allS[allS.d1min<=-10],"fwdS")
# 4c. pogoń: long po skoku 1-dn >= +8% w 3 sesjach (top kwintyl i cały przekrój)
CST["long_skok1d>=8_w3s_topq"] = stats(longc[longc.d1max>=8]); CST["long_skok1d>=12_w3s_topq"] = stats(longc[longc.d1max>=12])
CST["univ_long_skok1d>=8_w3s"] = stats(CS[CS.d1max>=8]); CST["univ_long_r10>=15"] = stats(CS[CS.r10>=15])
# 4d. odwrotna reguła dla short: short po odbiciu? (prev>0 shorty już wyżej)
OUT["testy_przekrojowe"] = CST

# 4e. tie-break "mniejsza waga": statyczne proxy kapitalizacji z tv-screen W8
tv = json.load(open("/home/user/ndx100-bot/data/tv-screen-2026-W8.json"))["data"]["rows"]
mc = {}
for r in tv:
    nm = r.get("name") or r.get("s","").split(":")[-1]
    if r.get("market_cap_basic"): mc[nm] = r["market_cap_basic"]
CS["mc"] = CS.t.map(mc)
CSm = CS.dropna(subset=["mc"]).copy()
CSm["mcq"] = CSm.groupby("d0").mc.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
OUT["tie_break_waga_proxy"] = {f"tercyl_kapitalizacji_{int(q)}": stats(CSm[CSm.mcq==q]) for q in sorted(CSm.mcq.unique())}
OUT["tie_break_waga_proxy"]["uwaga"] = "kapitalizacja statyczna z 16.10.2026 — proxy obciążone (survivorship/look-ahead), tylko orientacyjnie"

# ------------------------------------------------ 5. symulacja bramki 4/8 na koszykach W1–W7 (od D0 jako proxy wejścia)
def simulate_gate(L, S, d0, d1, second=True, abs_gate=True, red=4.0, clo=8.0, stop=None, reopen=False):
    """Zwraca spread zarządzany (równe wagi) i listę reakcji. Reakcje od zamknięcia dnia t (wpis Pulsu rano t+1,
    bieg bota t+1 13:45 → efekt od zamknięcia t+1; tu przyjmujemy efekt od t+1 close, czyli segment t→t+1 jeszcze pełną wagą)."""
    days = px.loc[d0:d1].index
    tot = 0; reacts=[]
    for side, names in (("L",L),("S",S)):
        for t in names:
            sgn = 1 if side=="L" else -1
            w = 1.0; pos_ret = 0.0; prev_rel_bad=False; closed=False; stopped=False
            for k in range(1,len(days)):
                dprev, dcur = days[k-1], days[k]
                seg = sgn*((px[t].loc[dcur]/px[t].loc[dprev]-1)*100 - (N.loc[dcur]/N.loc[dprev]-1)*100)
                pos_ret += w*seg
                if closed: continue
                relD0 = sgn*((px[t].loc[dcur]/px[t].loc[d0]-1)*100 - (N.loc[dcur]/N.loc[d0]-1)*100)
                absD0 = sgn*absret(t,d0,dcur)
                if stop is not None and absD0 <= -stop and not stopped:
                    # stop bota: zamknięcie na close dnia dcur; ponowne otwarcie następnego dnia (pozycja wraca) — strata zrealizowana = już w pos_ret
                    stopped=True; reacts.append((t,str(dcur.date()),"STOP"))
                    if not reopen: closed=True; w=0.0
                    continue
                bad = relD0 <= -red
                cond2 = (prev_rel_bad if second else True)
                if bad and cond2 and (absD0 <= -red or not abs_gate):
                    if relD0 <= -clo and (absD0 <= -clo or not abs_gate) and w>0:
                        reacts.append((t,str(dcur.date()),"CLOSE")); closed=True; w=0.0
                    elif w==1.0:
                        reacts.append((t,str(dcur.date()),"REDUCE")); w=0.5
                prev_rel_bad = bad
            tot += pos_ret/5
    return round(tot,2), reacts

GATE = {}
for w,(d0,d1,d5) in W.items():
    L,S = BASKETS[w]
    base,_ = simulate_gate(L,S,d0,d1,second=True,abs_gate=True,red=999,clo=999)
    g1,r1 = simulate_gate(L,S,d0,d1)                       # protokół 4/8 + 2 sesje + bramka abs
    g2,r2 = simulate_gate(L,S,d0,d1,second=False)          # bez potwierdzenia drugą sesją
    g3,r3 = simulate_gate(L,S,d0,d1,second=False,abs_gate=False)  # tylko względny, bez bramki (stary protokół)
    g4,r4 = simulate_gate(L,S,d0,d1,red=999,clo=999,stop=10.0,reopen=False)  # tylko stop bota 10% bez reopen (od D0, close-based)
    GATE[w] = dict(spread_bez_reakcji=base, protokol_4_8_2s_bramka=g1, reakcje_1=r1, bez_2_sesji=g2, reakcje_2=r2,
                   tylko_wzgledny_stary=g3, reakcje_3=r3, stop10_bez_reopen=g4, reakcje_4=r4)
OUT["symulacja_bramki"] = GATE
sum_ = lambda key: round(sum(v[key] for v in GATE.values()),2)
OUT["symulacja_bramki_suma"] = {k: sum_(k) for k in ["spread_bez_reakcji","protokol_4_8_2s_bramka","bez_2_sesji","tylko_wzgledny_stary","stop10_bez_reopen"]}

# 5b. test przekrojowy bramki: po 2 kolejnych sesjach z rel ≤ −4 pp od D0 (i abs ≤ −4%) w dniach 2–4 okna — co dalej do końca okna?
gate_rec=[]
for k in range(len(idx)-1):
    i0,i1 = idx[k], idx[k+1]
    if i0<131: continue
    for t in UNIV:
        s=P5[t].iloc[i0:i1+1].values; n=N.iloc[i0:i1+1].values
        if np.isnan(s).any(): continue
        relp = (s/s[0]-1)*100-(n/n[0]-1)*100; absp=(s/s[0]-1)*100
        for side,sg in (("L",1),("S",-1)):
            r=sg*relp; a=sg*absp
            for j in range(2,len(s)-1):
                if r[j]<=-4 and r[j-1]<=-4 and a[j]<=-4:
                    rest = sg*((s[-1]/s[j]-1)*100-(n[-1]/n[j]-1)*100)
                    gate_rec.append((dates[i0],t,side,j,r[j],rest, r[j]<=-8 and a[j]<=-8)); break
GR = pd.DataFrame(gate_rec, columns=["d0","t","side","j","rel_at","rest","close_lvl"])
OUT["bramka_przekroj"] = {
 "wszystkie_sygnaly_REDUCE(rel<=-4 2 sesje, abs<=-4)": stats(GR,"rest"),
 "long": stats(GR[GR.side=="L"],"rest"), "short": stats(GR[GR.side=="S"],"rest"),
 "sygnaly_na_poziomie_CLOSE(rel<=-8, abs<=-8)": stats(GR[GR.close_lvl],"rest"),
 "sygnaly_tylko_REDUCE": stats(GR[~GR.close_lvl],"rest"),
 "interpretacja": "rest = zwrot relatywny pozycji od sesji sygnału do końca okna 5-ses.; <0 = cięcie pomaga (kontynuacja), >0 = cięcie szkodzi (odwrócenie)"}
# wariant: top/bottom kwintyl momentum (jak koszyki)
GRq = GR.merge(CS[["d0","t","q"]], on=["d0","t"], how="left")
OUT["bramka_przekroj"]["long_top_q_mom"] = stats(GRq[(GRq.side=="L")&(GRq.q==4)],"rest")
OUT["bramka_przekroj"]["short_bot_q_mom"] = stats(GRq[(GRq.side=="S")&(GRq.q==0)],"rest")

# ------------------------------------------------ 6. shorty defensywne (CMCSA/SBUX/PEP/NFLX) vs software shorty — w koszykach
DEF = {"CMCSA","SBUX","PEP","NFLX","TMUS"}
sl = legs[legs.side=="S"]
OUT["shorty_defensywne_vs_reszta"] = {"defensywne": dict(n=int(sl.ticker.isin(DEF).sum()), hit=int(sl[sl.ticker.isin(DEF)].hit.sum()), srednia=round(sl[sl.ticker.isin(DEF)].rel.mean(),2), suma=round(sl[sl.ticker.isin(DEF)].rel.sum(),2)),
                                      "pozostale": dict(n=int((~sl.ticker.isin(DEF)).sum()), hit=int(sl[~sl.ticker.isin(DEF)].hit.sum()), srednia=round(sl[~sl.ticker.isin(DEF)].rel.mean(),2), suma=round(sl[~sl.ticker.isin(DEF)].rel.sum(),2)),
                                      "defensywne_do_W6": dict(n=int(sl[(sl.ticker.isin(DEF))&(sl.week!="W7")].shape[0]), hit=int(sl[(sl.ticker.isin(DEF))&(sl.week!="W7")].hit.sum())),
                                      "defensywne_W7": dict(n=int(sl[(sl.ticker.isin(DEF))&(sl.week=="W7")].shape[0]), hit=int(sl[(sl.ticker.isin(DEF))&(sl.week=="W7")].hit.sum()), suma=round(sl[(sl.ticker.isin(DEF))&(sl.week=="W7")].rel.sum(),2))}
# przekrój: dolny kwintyl momentum — defensywy (XLP/XLU/XLV proxy) vs reszta? użyj listy sektorowej z tv-screen
sector = {}
for r in tv:
    nm = r.get("name");
    if nm: sector[nm] = r.get("sector")
CS["sector"] = CS.t.map(sector)
defsec = {"Consumer Staples","Utilities","Health Technology","Communications","Consumer Non-Durables","Consumer Services","Health Services","Distribution Services","Retail Trade"}
shc2 = CS[CS.q==0].copy(); shc2["fwdS"]=-shc2.fwd
OUT["shorty_defensywne_przekroj"] = {"bot_q_sektory_defensywne": stats(shc2[shc2.sector.isin(defsec)],"fwdS"), "bot_q_technologia_i_reszta": stats(shc2[~shc2.sector.isin(defsec)],"fwdS"),
                                     "sektory_TV_uzyte": sorted(set(shc2.sector.dropna()))}

# ------------------------------------------------ 7. W8 — stan na papierze (nierozstrzygnięty): tylko skład i D0
OUT["W8_nierozstrzygniety"] = dict(d0="2026-10-16", ostatnia_sesja_w_danych=str(dates[-1].date()),
    filtr_sily_rel_wykluczyl=["SNDK","STX","AVGO","AMAT","KLAC","FTNT"], nogi_W7_wykluczone=["MU","LITE","MRVL","PANW","CSCO","CMCSA","SBUX","PEP","TMUS"],
    uwaga="okno 16.10→23.10 — brak danych po 16.10; nie liczymy")

json.dump(OUT, open(f"{BASE}/analiza/audyt_regul_wyniki.json","w"), indent=1, ensure_ascii=False, default=str)
EX.to_csv(f"{BASE}/analiza/audyt_regul_wykluczenia.csv", index=False)
legs.to_csv(f"{BASE}/analiza/audyt_regul_nogi.csv", index=False)
print(json.dumps({k:v for k,v in OUT.items() if k not in ("wykluczenia","deklaracje","symulacja_bramki")}, indent=1, ensure_ascii=False, default=str))
print("\n=== WYKLUCZENIA ===")
print(EX.to_string())
print("\n=== BRAMKA per tydzień ===")
for w,v in GATE.items():
    print(w, {k:v[k] for k in v if not k.startswith("reakcje")}, "| reakcje protokół:", v["reakcje_1"], "| stary:", v["reakcje_3"], "| stop:", v["reakcje_4"])
