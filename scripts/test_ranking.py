#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy scripts/ranking.py i scripts/koszyki_cienie.py na danych syntetycznych (bez sieci).

Uruchomienie: python3 scripts/test_ranking.py
"""
import json
import tempfile
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ranking  # noqa: E402
import koszyki_cienie  # noqa: E402

WYNIKI = []


def sprawdz(nazwa, warunek, detal=""):
    WYNIKI.append((nazwa, bool(warunek), detal))
    print(("OK   " if warunek else "FAIL ") + nazwa + (f" — {detal}" if detal and not warunek else ""))


def syntetyczne(n_dni=400, seed=7):
    """Uniwersum 30 spółek: 5 'liderów' (dryf +), 5 'maruderów' (dryf −), 2 ekstremalnie
    zmienne, reszta szum; indeks = średnia; ^SOX = indeks + czynnik; ETF-y defensywne."""
    rnd = random.Random(seed)
    tick = [f"T{i:02d}" for i in range(30)]
    dryf = {t: 0.0 for t in tick}
    for t in tick[:5]:
        dryf[t] = 0.004
    for t in tick[5:10]:
        dryf[t] = -0.004
    sig = {t: 0.02 for t in tick}
    sig["T28"] = 0.12  # ekstremalna zmienność → veto σ
    sig["T29"] = 0.11
    daty = []
    d = 20250101
    for i in range(n_dni):
        daty.append(f"{2025 + (i // 250):04d}-{1 + (i % 250) // 21:02d}-{1 + (i % 21):02d}")
    daty = sorted(set(daty))[:n_dni]
    ceny = {t: {} for t in tick}
    idx, sox, xlp, xlu, xlv, qqq = {}, {}, {}, {}, {}, {}
    p = {t: 100.0 for t in tick}
    pi, ps, pp_, pu, pv, pq = 100.0, 100.0, 100.0, 100.0, 100.0, 100.0
    for k, d in enumerate(daty):
        czynnik = rnd.gauss(0, 0.01)
        rynek = rnd.gauss(0, 0.01)
        zw = {}
        for t in tick:
            beta_sox = 1.5 if t in tick[10:15] else 0.0
            zw[t] = dryf[t] + rynek + beta_sox * czynnik + rnd.gauss(0, sig[t])
            p[t] *= 1 + zw[t]
            ceny[t][d] = round(p[t], 4)
        pi *= 1 + rynek
        ps *= 1 + rynek + czynnik
        pq *= 1 + rynek
        pp_ *= 1 + 0.3 * rynek
        pu *= 1 + 0.3 * rynek
        pv *= 1 + 0.5 * rynek
        idx[d], sox[d], qqq[d], xlp[d], xlu[d], xlv[d] = pi, ps, pq, pp_, pu, pv
    dane = dict(ceny)
    dane.update({"^NDX": idx, "^SOX": sox, "QQQ": qqq, "XLP": xlp, "XLU": xlu, "XLV": xlv})
    return daty, dane, tick


def test_ranking():
    daty, dane, tick = syntetyczne()
    tv = [{"name": t, "industry": f"Grupa {int(t[1:]) % 6}", "sector": "Sektor"} for t in tick]
    w = ranking.policz(daty, dane, tick, tv)
    rk = [r["ticker"] for r in w["ranking"]]
    sprawdz("ranking: 30 spółek z historią", w["n_z_historia"] == 30, str(w["n_z_historia"]))
    sprawdz("ranking: liderzy w TOP10 momentum", all(t in rk[:10] for t in tick[:5]), str(rk[:10]))
    sprawdz("ranking: maruderzy w BOTTOM10", all(t in rk[-10:] for t in tick[5:10]), str(rk[-10:]))
    A = w["konstrukcje"]["A_mom6_top5_bottom5"]
    sprawdz("A: 5 long i 5 short, rozłączne", len(A["long"]) == 5 and len(A["short"]) == 5 and not set(A["long"]) & set(A["short"]))
    wier = {r["ticker"]: r for r in w["ranking"]}
    sprawdz("veto σ: T28 i T29 poza koszykami", all(any("σ60" in v for v in wier[t]["veto_long"]) for t in ("T28", "T29"))
            and not ({"T28", "T29"} & (set(A["long"]) | set(A["short"]))))
    sprawdz("czynniki: b_SOX wyższy dla nóg z betą do SOX",
            statistics_mean([wier[t]["b_sox"] for t in tick[10:15]]) > statistics_mean([wier[t]["b_sox"] for t in tick[15:25]]) + 0.5)
    B = w["konstrukcje"]["B_5_par_branzowych"]
    sprawdz("B: każda para z tej samej grupy", all(wier[p["long"]]["grupa"] == wier[p["short"]]["grupa"] == p["grupa"] for p in B["pary"]) and len(B["pary"]) <= 5)
    C = w["konstrukcje"]["C_neutralna_branzowo"]
    sprawdz("C: maks. 1 long z grupy", len({wier[t]["grupa"] for t in C["long"]}) == len(C["long"]))
    D = w["konstrukcje"]["D_budzet_czynnikowy"]
    r = D["ryzyko"]
    sprawdz("D: budżet czynnikowy domknięty lub wyczerpane wymiany",
            (r["b_sox_net"] is not None and abs(r["b_sox_net"]) <= ranking.FACTOR_BUDGET + 1e-9) or len(D["wymiany"]) == ranking.MAX_SWAPS,
            str(r))
    sprawdz("ryzyko: σ60 i ALLOC w granicach", r["sigma60_unit_dzienna"] > 0 and ranking.ALLOC_MIN <= r["alloc_pct_proponowany"] <= ranking.ALLOC_MAX, str(r))
    sprawdz("ryzyko: σ dzienna kapitału = 5×alloc×σ_unit",
            abs(r["sigma_dzienna_kapitalu_przy_alloc"] - 5 * r["alloc_pct_proponowany"] * r["sigma60_unit_dzienna"] * 100) < 0.02)
    # veto K13: sztucznie zwal T20 o 25% w 10 sesji
    dane2 = {k: dict(v) for k, v in dane.items()}
    for d in daty[-10:]:
        dane2["T20"][d] = dane2["T20"][d] * 0.7
    w2 = ranking.policz(daty, dane2, tick, tv)
    wier2 = {x["ticker"]: x for x in w2["ranking"]}
    sprawdz("veto K13: T20 po −30% w 10 sesji ma veto short, nie long",
            any("K13" in v for v in wier2["T20"]["veto_short"]) and not wier2["T20"]["veto_long"], str(wier2["T20"]["veto_short"]))
    # veto event
    w3 = ranking.policz(daty, dane, tick, tv, earnings={"T00": daty[-1][:8] + "%02d" % (int(daty[-1][8:]) + 1) if int(daty[-1][8:]) < 28 else daty[-1]})
    wier3 = {x["ticker"]: x for x in w3["ranking"]}
    sprawdz("veto EVENT: raport w D+1…D+5 wyklucza T00 z long i short", bool(wier3["T00"]["veto_long"]) and bool(wier3["T00"]["veto_short"]), str(wier3["T00"]["veto_long"]))
    # exclude
    w4 = ranking.policz(daty, dane, tick, tv, exclude={"T01"})
    sprawdz("exclude: T01 poza koszykiem A", "T01" not in w4["konstrukcje"]["A_mom6_top5_bottom5"]["long"])
    # konstrukcja E
    E = w["konstrukcje"]["E_pary_budzet_sox"]
    sprawdz("E: 5 par, long/short rozłączne", len(E["long"]) == 5 and len(E["short"]) == 5 and not set(E["long"]) & set(E["short"]), str(E["pary"]))
    sprawdz("E: każda para z tej samej grupy", all(wier[p["long"]]["grupa"] == wier[p["short"]]["grupa"] for p in E["pary"]))
    sprawdz("E: budżet b_SOX albo min_b", (E["wybor"] == "budzet" and abs(E["b_sox_net_ex_ante"]) <= ranking.FACTOR_BUDGET + 1e-9) or E["wybor"] in ("min_b", "za_malo_par"), str(E["wybor"]))
    sprawdz("E: pary uporządkowane od najwyższej σ60 pary", all(E["pary"][i]["sigma60_pary"] >= E["pary"][i + 1]["sigma60_pary"] for i in range(len(E["pary"]) - 1)))
    sprawdz("E: kolejność list = kolejność par", E["long"] == [p["long"] for p in E["pary"]] and E["short"] == [p["short"] for p in E["pary"]])
    # veto cenowe
    stare = ranking.MAX_PRICE_USD
    ranking.MAX_PRICE_USD = 0.01  # każda cena > 0,01 USD → veto (syntetyczny T28 spada poniżej 1 USD)
    w5 = ranking.policz(daty, dane, tick, tv)
    ranking.MAX_PRICE_USD = stare
    sprawdz("veto cenowe: przy MAX_PRICE_USD=0,01 wszystkie spółki mają veto", all(any("MAX_PRICE" in v for v in r["veto_long"]) for r in w5["ranking"]))
    # tabela md
    md = ranking.tabela_md(w)
    sprawdz("tabela md: zawiera nagłówek i 5 konstrukcji", md.count("**") >= 10 and "| # | Ticker" in md and "wybór E" in md)
    # rozliczenie cieni
    d0, d1 = daty[-6], daty[-1]
    wr = koszyki_cienie.rozlicz(dane, daty, d0, d1, A["long"], A["short"])
    sprawdz("cienie: rozliczenie zwraca spread i 10 nóg", wr is not None and len(wr["nogi"]) == 10 and isinstance(wr["spread_pp"], float))
    if wr:
        L = [n["pozycja_pp"] for n in wr["nogi"] if n["strona"] == "long"]
        S = [n["pozycja_pp"] for n in wr["nogi"] if n["strona"] == "short"]
        sprawdz("cienie: spread = śr. long + śr. short", abs(wr["spread_pp"] - (sum(L) / 5 + sum(S) / 5)) < 0.011)


def test_v2_poprawki():
    """Poprawki po przeglądzie 18.10.2026: dopełnianie par, tryb bez czynnika, pula percentyla,
    exclude z powodem + E_bez_exclude, liczniki dat raportów, FAKTYCZNY, ostrzeżenie D0, cienie v2."""
    from datetime import date, timedelta
    daty, dane, tick = syntetyczne()
    tv6 = [{"name": t, "industry": f"Grupa {int(t[1:]) % 6}", "sector": "Sektor"} for t in tick]
    tv3 = [{"name": t, "industry": f"Grupa {int(t[1:]) % 3}", "sector": "Sektor"} for t in tick]
    w3 = ranking.policz(daty, dane, tick, tv3)
    E3 = w3["konstrukcje"]["E_pary_budzet_sox"]
    sprawdz("E: przy 3 grupach dopełnia pary do 5/5 (+dopelnione)",
            len(E3["long"]) == 5 and len(E3["short"]) == 5 and E3["kompletna"] and E3["wybor"].endswith("+dopelnione")
            and len(E3["dopelnienia"]) == 2 and not set(E3["long"]) & set(E3["short"]), str(E3["wybor"]) + str(E3["dopelnienia"]))
    dane_bez = {k: v for k, v in dane.items() if k != "^SOX"}
    wb = ranking.policz(daty, dane_bez, tick, tv6)
    Eb = wb["konstrukcje"]["E_pary_budzet_sox"]
    sprawdz("E: bez ^SOX wybor=bez_czynnika, b_sox_net None, czynniki_dostepne.sox=false",
            Eb["wybor"].startswith("bez_czynnika") and Eb["b_sox_net_ex_ante"] is None and wb["czynniki_dostepne"]["sox"] is False
            and len(Eb["long"]) == 5, str(Eb["wybor"]))
    w = ranking.policz(daty, dane, tick, tv6)
    r = w["konstrukcje"]["E_pary_budzet_sox"]["ryzyko"]
    kand = {x["ticker"] for x in w["ranking"] if not x["veto_long"]} | {x["ticker"] for x in w["ranking"] if not x["veto_short"]}
    E_ = w["konstrukcje"]["E_pary_budzet_sox"]
    sprawdz("ryzyko: pula losowa = kandydaci PO vetach bez 10 nóg koszyka (bez T28/T29), opis w parametrach",
            r["parametry"]["n_pula"] == len(kand - set(E_["long"]) - set(E_["short"])) and "T28" not in kand
            and "po_vetach" in r["parametry"]["uniwersum_losowe"], str(r["parametry"]))
    E_long0 = w["konstrukcje"]["E_pary_budzet_sox"]["long"][0]
    wx = ranking.policz(daty, dane, tick, tv6, exclude={E_long0: "R8"})
    wierx = {x["ticker"]: x for x in wx["ranking"]}
    sprawdz("exclude z powodem: veto 'exclude: R8', konstrukcja E_bez_exclude, exclude_powody",
            "exclude: R8" in wierx[E_long0]["veto_long"] and "exclude: R8" in wierx[E_long0]["veto_short"]
            and "E_bez_exclude" in wx["konstrukcje"] and E_long0 not in wx["konstrukcje"]["E_pary_budzet_sox"]["long"]
            and E_long0 in wx["konstrukcje"]["E_bez_exclude"]["long"] and wx["exclude_powody"] == {E_long0: "R8"})
    sprawdz("bez exclude: brak konstrukcji E_bez_exclude", "E_bez_exclude" not in w["konstrukcje"] and w["exclude_powody"] == {})
    d0 = date.fromisoformat(daty[-1])
    in7, in8 = (d0 + timedelta(days=7)).isoformat(), (d0 + timedelta(days=8)).isoformat()
    we = ranking.policz(daty, dane, tick, tv6, earnings={"T00": in7, "T01": in8, "T02": "zła-data"})
    wiere = {x["ticker"]: x for x in we["ranking"]}
    sprawdz("EVENT: D0+7 wetuje, D0+8 nie; earnings_n_ok=2, earnings_n_blad=[T02], earnings_date w wierszu",
            any(v.startswith("EVENT") for v in wiere["T00"]["veto_long"]) and not any(v.startswith("EVENT") for v in wiere["T01"]["veto_long"])
            and we["earnings_n_ok"] == 2 and we["earnings_n_blad"] == ["T02"] and wiere["T00"]["earnings_date"] == in7
            and wiere["T05"]["earnings_date"] is None, str((we["earnings_n_ok"], we["earnings_n_blad"])))
    wf = ranking.policz(daty, dane, tick, tv6, faktyczny=(tick[:5], tick[5:10]))
    F = wf["konstrukcje"]["FAKTYCZNY"]
    sprawdz("FAKTYCZNY: konstrukcja z ryzykiem (σ, b_SOX, percentyl)",
            F["long"] == tick[:5] and F["short"] == tick[5:10] and F["ryzyko"] and F["ryzyko"]["sigma60_unit_dzienna"] > 0
            and F["ryzyko"]["percentyl_sigma_vs_losowe"] is not None)
    wd = ranking.policz(daty, dane, tick, tv6, d0="2099-01-01")
    sprawdz("D0 spoza danych → ostrzeżenie i d0 = ostatnia sesja", bool(wd["ostrzezenia"]) and wd["d0"] == daty[-1] and w["ostrzezenia"] == [])
    # koszyki_cienie v2
    A = w["konstrukcje"]["A_mom6_top5_bottom5"]
    wr = koszyki_cienie.rozlicz(dane, daty, daty[-6], daty[-1], A["long"], A["short"])
    sprawdz("cienie: sigma_zreal_tyg_pp z 5 dziennych spreadów", wr["sigma_zreal_tyg_pp"] is not None and wr["sigma_zreal_tyg_pp"] > 0)
    sprawdz("betainc: I_x(1,1)=x, symetria I_0.5(a,a)=0.5",
            abs(koszyki_cienie.betainc(1, 1, 0.3) - 0.3) < 1e-9 and abs(koszyki_cienie.betainc(2.5, 2.5, 0.5) - 0.5) < 1e-9)
    sprawdz("F cdf: P(F≤1 | 10,10)=0,5; P(F(5,8)≤3,687)≈0,95",
            abs(koszyki_cienie.f_cdf(1.0, 10, 10) - 0.5) < 1e-9 and abs(koszyki_cienie.f_cdf(3.687, 5, 8) - 0.95) < 2e-3)
    sprawdz("t_kryt: df 10 → 2,228; df 35 → 2,042 (niższy węzeł); df 200 → 1,96",
            koszyki_cienie.t_kryt(10) == 2.228 and koszyki_cienie.t_kryt(35) == 2.042 and koszyki_cienie.t_kryt(200) == 1.96)
    import tempfile
    rnd = random.Random(3)
    rows = []
    for i in range(30):
        rows.append({"version": f"2026-W{i}", "d0": "x", "d1": "y", "sesje": 5, "pokrycie": "10/10" if i % 5 else "9/10",
                     "koszyki": {"E_pary_budzet_sox": {"spread_pp": round(rnd.gauss(0, 4), 2), "sigma_zreal_tyg_pp": 4.0, "sigma_ex_ante_tyg_pp": 4.5},
                                 "A_mom6_top5_bottom5": {"spread_pp": round(rnd.gauss(0, 8), 2)},
                                 "FAKTYCZNY": {"spread_pp": round(rnd.gauss(0, 8), 2)}}, "nogi": {}})
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    out, md = koszyki_cienie.podsumowanie(f.name)
    sprawdz("podsumowanie: n=30, σ-ratio E/A < 0,85, test F p < 0,05, kalibracja w pasmie, pokrycie 24/30, wniosek o wariancji",
            out["okna"] == 30 and out["sigma_ratio_E_A"] < 0.85 and out["test_F_A_vs_E"]["p"] < 0.05
            and out["kalibracja_E"]["w_pasmie_0.7_1.4"] is True and out["pokrycie_10_10"] == {"n_okien_z_pokryciem": 30, "pelne": 24}
            and "WARIANCJA (26+)" in md and "E netto" in md, str((out["sigma_ratio_E_A"], out["test_F_A_vs_E"])))
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f2:
        for row in rows[:5]:
            f2.write(json.dumps(row) + "\n")
    out0, md0 = koszyki_cienie.podsumowanie(os.path.join(tempfile.gettempdir(), "koszyki-cienie-nie-ma.jsonl"))
    sprawdz("podsumowanie: brak pliku logu → n=0 bez wyjątku", out0["okna"] == 0 and isinstance(md0, str))
    out5, md5 = koszyki_cienie.podsumowanie(f2.name)
    sprawdz("podsumowanie: n=5 → „za wcześnie”, bez wniosku o wariancji", out5["okna"] == 5 and "za wcześnie" in md5 and "WARIANCJA (26+)" not in md5)


def statistics_mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


if __name__ == "__main__":
    test_ranking()
    test_v2_poprawki()
    n_ok = sum(1 for _, ok, _ in WYNIKI if ok)
    print(f"\nprzeszło: {n_ok}   nie przeszło: {len(WYNIKI) - n_ok}")
    sys.exit(0 if n_ok == len(WYNIKI) else 1)
