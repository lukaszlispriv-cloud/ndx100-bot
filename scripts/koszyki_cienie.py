#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
koszyki_cienie.py — rozliczenie koszyków „cieni” (konstrukcje z ranking.py,
koszyk faktyczny, ETF SMH−XLP) od D0 do zadanej sesji; wiersz do
data/koszyki-cienie.jsonl; podsumowanie serii z testem F (--podsumowanie).

Po co: analiza 18.10.2026 pokazała, że 7 tygodni nie rozstrzyga o przewadze
(σ spreadu ~7–11 p.p./tydz.), ale JUŻ po 12–26 tygodniach da się rozstrzygać
o WARIANCJI konstrukcji (test F) i o koszcie nadpisań/reguł — pod warunkiem,
że co sobotę rozliczamy te same, prerejestrowane koszyki cienie jednym skryptem.

Użycie (w katalogu repo):
  python3 -I scripts/koszyki_cienie.py --ranking data/ranking-2026-W8.json
      --closes <csv> --do 2026-10-23
      --faktyczny-long GOOGL GILD MSFT QCOM ADP --faktyczny-short AXON DASH ALNY APP FER
      [--pokrycie 10/10] [--log data/koszyki-cienie.jsonl --version 2026-W8]
  python3 -I scripts/koszyki_cienie.py --podsumowanie data/koszyki-cienie.jsonl

Zwrot pozycji = [D+n/D0 − 1] spółki − [D+n/D0 − 1] ^NDX (short ze znakiem ujemnym);
spread_pp = średnia LONG + średnia SHORT. Bez dywidend (adnotacja), bez kosztów.
σ zrealizowana = odchylenie dziennych spreadów (śr. long − śr. short) w oknie × √5.
Konstrukcja bez obu list long/short (np. U_uznaniowy z "pominiety") jest pomijana
z komunikatem — nie przerywa rozliczenia. Gdy w cache nie ma sesji --do, skrypt
ostrzega i NIE dopisuje wiersza do logu.

Podsumowanie (--podsumowanie): dla każdej konstrukcji n, średnia, σ (próbkowa),
CI 95 % (t-Studenta), min/max; σ-ratio E/A i E/FAKTYCZNY; test F wariancji A vs E
(dwustronny, p z regularyzowanej funkcji beta — bez scipy); średnia E netto po
prerejestrowanym koszcie KOSZT_PP_TYDZ; kalibracja σ zreal./ex ante dla E;
pokrycie 10/10. Kryteria decyzji (rutyny/tygodniowa.md KROK C) są tu tylko
WYPISYWANE — decyduje właściciel. Plik nie zawiera liczb z rachunku.
"""
import argparse
import json
import math
import os
import statistics
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # działa też pod python3 -I
from ranking import wczytaj_closes, seria, INDEX  # noqa: E402  (ten sam katalog scripts/)

KOSZT_PP_TYDZ = 0.3          # prerejestrowany koszt rotacji+finansowania w p.p. spreadu/tydz. (PROPOZYCJA §6: 0,12 % kapitału / 0,4)
GLOWNA, BAZOWA, FAKT = "E_pary_budzet_sox", "A_mom6_top5_bottom5", "FAKTYCZNY"
ETF_LONG, ETF_SHORT = "SMH", "XLP"


def zwrot(dane, t, d0, d1, daty):
    s = dict(seria(dane, t, [d for d in daty if d <= d1]))
    if d0 not in s or d1 not in s:
        return None
    return s[d1] / s[d0] - 1.0


def sigma_zreal(dane, daty, d0, d1, lo, sh):
    """σ dziennych spreadów (śr. long − śr. short) w oknie (D0, D1] × √5, w p.p.; None gdy < 3 sesji."""
    okno = [d for d in daty if d0 <= d <= d1]
    spready = []
    for prev, d in zip(okno, okno[1:]):
        rl = [dane[t][d] / dane[t][prev] - 1 for t in lo if prev in dane.get(t, {}) and d in dane.get(t, {}) and dane[t][prev]]
        rs = [dane[t][d] / dane[t][prev] - 1 for t in sh if prev in dane.get(t, {}) and d in dane.get(t, {}) and dane[t][prev]]
        if lo and sh and len(rl) == len(lo) and len(rs) == len(sh):
            spready.append(statistics.fmean(rl) - statistics.fmean(rs))
    if len(spready) < 3:
        return None
    return round(statistics.pstdev(spready) * math.sqrt(5) * 100, 2)


def rozlicz(dane, daty, d0, d1, lo, sh):
    r_ndx = zwrot(dane, INDEX, d0, d1, daty)
    if r_ndx is None:
        return None
    nogi = []
    for t in lo:
        r = zwrot(dane, t, d0, d1, daty)
        nogi.append({"ticker": t, "strona": "long", "zwrot": r, "pozycja_pp": None if r is None else (r - r_ndx) * 100})
    for t in sh:
        r = zwrot(dane, t, d0, d1, daty)
        nogi.append({"ticker": t, "strona": "short", "zwrot": r, "pozycja_pp": None if r is None else -(r - r_ndx) * 100})
    L = [n["pozycja_pp"] for n in nogi if n["strona"] == "long" and n["pozycja_pp"] is not None]
    S = [n["pozycja_pp"] for n in nogi if n["strona"] == "short" and n["pozycja_pp"] is not None]
    if not L or not S:
        return None
    return {"d0": d0, "d1": d1, "ndx_pct": round(r_ndx * 100, 2),
            "spread_pp": round(statistics.fmean(L) + statistics.fmean(S), 2),
            "long_sr_pp": round(statistics.fmean(L), 2), "short_sr_pp": round(statistics.fmean(S), 2),
            "hit_long": f"{sum(1 for x in L if x > 0)}/{len(L)}", "hit_short": f"{sum(1 for x in S if x > 0)}/{len(S)}",
            "sigma_zreal_tyg_pp": sigma_zreal(dane, daty, d0, d1, lo, sh),
            "nogi": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in n.items()} for n in nogi]}


# ---------------------------------------------------------------- statystyka bez scipy
_T_KRYT = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
           11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
           21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
           40: 2.021, 50: 2.009, 60: 2.000, 80: 1.990, 100: 1.984}


def t_kryt(df):
    """Kwantyl 97,5 % rozkładu t (tablica; między węzłami bierzemy niższy df = ostrożniej; > 100 → 1,96)."""
    if df <= 0:
        return float("inf")
    if df in _T_KRYT:
        return _T_KRYT[df]
    klucze = sorted(_T_KRYT)
    if df > klucze[-1]:
        return 1.96
    return _T_KRYT[max(k for k in klucze if k < df)]


def _betacf(a, b, x, maxit=300, eps=3e-14):
    """Ułamek łańcuchowy dla niepełnej funkcji beta (Numerical Recipes, betacf)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1e-300 if abs(d) < 1e-300 else d
    d = 1.0 / d
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1e-300 if abs(d) < 1e-300 else d
        c = 1.0 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1e-300 if abs(d) < 1e-300 else d
        c = 1.0 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularyzowana niepełna funkcja beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b


def f_cdf(f, d1, d2):
    """P(F ≤ f) dla rozkładu F(d1, d2)."""
    if f <= 0:
        return 0.0
    x = d1 * f / (d1 * f + d2)
    return betainc(d1 / 2.0, d2 / 2.0, x)


def test_f(xs_a, xs_e):
    """Test F wariancji A vs E (dwustronny): F = s_A²/s_E², p = 2·min(P(F≤f), P(F≥f))."""
    if len(xs_a) < 2 or len(xs_e) < 2:
        return None
    va, ve = statistics.variance(xs_a), statistics.variance(xs_e)
    if ve <= 0 or va <= 0:
        return None
    f = va / ve
    c = f_cdf(f, len(xs_a) - 1, len(xs_e) - 1)
    return {"F": round(f, 3), "df": [len(xs_a) - 1, len(xs_e) - 1], "p": round(min(1.0, 2 * min(c, 1 - c)), 4)}


def statystyka(xs):
    n = len(xs)
    if n == 0:
        return None
    m = statistics.fmean(xs)
    sd = statistics.stdev(xs) if n >= 2 else None
    ci = None if sd is None else t_kryt(n - 1) * sd / math.sqrt(n)
    return {"n": n, "srednia": round(m, 2), "sd": None if sd is None else round(sd, 2),
            "ci95": None if ci is None else [round(m - ci, 2), round(m + ci, 2)],
            "min": round(min(xs), 2), "max": round(max(xs), 2)}


def podsumowanie(sciezka_logu, koszt=KOSZT_PP_TYDZ):
    """Czyta data/koszyki-cienie.jsonl i zwraca (dict, markdown)."""
    wiersze = []
    # Brak pliku = jeszcze żadnego okna (pierwszy bieg v2 albo bieg powtórny
    # bez --log po nieudanym logowaniu) — podsumowanie n = 0, nie traceback.
    if os.path.exists(sciezka_logu):
        with open(sciezka_logu, encoding="utf-8") as f:
            for linia in f:
                linia = linia.strip()
                if linia:
                    wiersze.append(json.loads(linia))
    serie, kalib, pokrycia = {}, [], []
    for r in wiersze:
        pokrycia.append(r.get("pokrycie"))
        for nazwa, w in (r.get("koszyki") or {}).items():
            if w.get("spread_pp") is None:
                continue
            serie.setdefault(nazwa, []).append(w["spread_pp"])
            if nazwa == GLOWNA and w.get("sigma_zreal_tyg_pp") and w.get("sigma_ex_ante_tyg_pp"):
                kalib.append(w["sigma_zreal_tyg_pp"] / w["sigma_ex_ante_tyg_pp"])
    stat = {n: statystyka(xs) for n, xs in serie.items()}
    out = {"okna": len(wiersze), "wersje": [wiersze[0]["version"], wiersze[-1]["version"]] if wiersze else [],
           "koszyki": stat, "koszt_pp_tydz": koszt}
    sE, sA, sF = stat.get(GLOWNA), stat.get(BAZOWA), stat.get(FAKT)
    out["sigma_ratio_E_A"] = round(sE["sd"] / sA["sd"], 3) if sE and sA and sE.get("sd") and sA.get("sd") else None
    out["sigma_ratio_E_FAKT"] = round(sE["sd"] / sF["sd"], 3) if sE and sF and sE.get("sd") and sF.get("sd") else None
    out["test_F_A_vs_E"] = test_f(serie.get(BAZOWA, []), serie.get(GLOWNA, [])) if sE and sA else None
    if sE:
        netto = sE["srednia"] - koszt
        out["E_netto"] = {"srednia": round(netto, 2),
                          "ci95": None if sE["ci95"] is None else [round(sE["ci95"][0] - koszt, 2), round(sE["ci95"][1] - koszt, 2)]}
    sr_kal = round(statistics.fmean(kalib), 2) if kalib else None
    out["kalibracja_E"] = {"n": len(kalib), "sr_zreal_do_ex_ante": sr_kal,
                           "w_pasmie_0.7_1.4": None if sr_kal is None else (0.7 <= sr_kal <= 1.4)}
    znane = [p for p in pokrycia if p]
    out["pokrycie_10_10"] = {"n_okien_z_pokryciem": len(znane), "pelne": sum(1 for p in znane if str(p).startswith("10/"))}
    # markdown
    n = len(wiersze)
    L = [f"# Podsumowanie koszyków cieni — {n} okien" + (f" ({out['wersje'][0]} … {out['wersje'][1]})" if n else ""), "",
         "| koszyk | n | średnia p.p. | σ p.p. | CI 95 % | min | max |", "|---|---|---|---|---|---|---|"]
    for nazwa in sorted(stat, key=lambda k: (k != GLOWNA, k != BAZOWA, k)):
        s = stat[nazwa]
        ci = "b.d." if s["ci95"] is None else f"[{s['ci95'][0]:+.2f}; {s['ci95'][1]:+.2f}]"
        L.append(f"| {nazwa} | {s['n']} | {s['srednia']:+.2f} | {s['sd'] if s['sd'] is not None else 'b.d.'} | {ci} | {s['min']:+.2f} | {s['max']:+.2f} |")
    L.append("")
    L.append(f"σ-ratio E/A: {out['sigma_ratio_E_A'] if out['sigma_ratio_E_A'] is not None else 'b.d.'}; "
             f"E/FAKTYCZNY: {out['sigma_ratio_E_FAKT'] if out['sigma_ratio_E_FAKT'] is not None else 'b.d.'}; "
             f"test F (A vs E): {out['test_F_A_vs_E'] if out['test_F_A_vs_E'] else 'b.d.'}")
    if "E_netto" in out:
        L.append(f"E netto (koszt {koszt} p.p./tydz.): {out['E_netto']['srednia']:+.2f}, CI 95 % {out['E_netto']['ci95']}")
    L.append(f"kalibracja E (σ zreal./ex ante): n = {out['kalibracja_E']['n']}, średnia {sr_kal}, "
             f"w pasmie [0,7; 1,4]: {out['kalibracja_E']['w_pasmie_0.7_1.4']}; pokrycie 10/10: "
             f"{out['pokrycie_10_10']['pelne']}/{out['pokrycie_10_10']['n_okien_z_pokryciem']} okien")
    L.append("")
    if n < 12:
        L.append(f"WNIOSEK: n = {n} < 12 — za wcześnie na jakikolwiek wniosek (o wariancji od 12 okien, o średniej nie przed 26).")
    else:
        L.append(f"KALIBRACJA (od 12 okien): {'OK' if out['kalibracja_E']['w_pasmie_0.7_1.4'] else 'POZA PASMEM — problem wykonania, nie konstrukcji'}; "
                 f"pokrycie pełne w {out['pokrycie_10_10']['pelne']}/{out['pokrycie_10_10']['n_okien_z_pokryciem']} (próg ≥ 10/12).")
        if n < 26:
            L.append("WARIANCJA: test F informacyjnie; decyzja o konstrukcji dopiero po 26 oknach. O średniej — nic.")
        else:
            sr = out["sigma_ratio_E_A"]
            if sr is not None:
                if sr <= 0.85:
                    L.append(f"WARIANCJA (26+): σ-ratio E/A {sr} ≤ 0,85 → E zostaje (warunek |b_SOX| E < A sprawdź z plików ranking).")
                elif sr > 1.03:
                    L.append(f"WARIANCJA (26+): σ-ratio E/A {sr} > 1,03 → rekomendacja powrotu do A z ALLOC 0,06 (decyzja właściciela).")
                else:
                    L.append(f"WARIANCJA (26+): σ-ratio E/A {sr} w pasmie 0,85–1,03 → bez zmian, pomiar trwa do 52 okien.")
            if n >= 52 and "E_netto" in out and out["E_netto"]["ci95"] is not None:
                gora = out["E_netto"]["ci95"][1]
                L.append(f"ŚREDNIA (52+): górna granica CI E netto {gora:+.2f} → "
                         + ("rekomendacja przejścia na papier / czynnik ETF." if gora < 0 else "brak podstaw do zamknięcia (CI obejmuje zero lub dodatnie)."))
            else:
                L.append("ŚREDNIA: żadnego wniosku przed 52 oknami.")
    return out, "\n".join(L) + "\n"


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ranking", help="data/ranking-<version>.json z ranking.py (d0 + konstrukcje)")
    ap.add_argument("--closes", help="CSV zamknięć (cache z ranking.py --fetch)")
    ap.add_argument("--do", help="sesja rozliczenia RRRR-MM-DD")
    ap.add_argument("--faktyczny-long", nargs="*", default=[])
    ap.add_argument("--faktyczny-short", nargs="*", default=[])
    ap.add_argument("--pokrycie", default=None, help="pokrycie nóg na rachunku w rozliczanym tygodniu, np. 10/10 (z /status, A9)")
    ap.add_argument("--version", default="")
    ap.add_argument("--log", help="data/koszyki-cienie.jsonl — dopisz wiersz")
    ap.add_argument("--podsumowanie", metavar="LOG", help="wypisz statystyki serii z pliku logu i zakończ")
    a = ap.parse_args()
    if a.podsumowanie:
        _, md = podsumowanie(a.podsumowanie)
        print(md)
        return
    if not (a.ranking and a.closes and a.do):
        ap.error("podaj --ranking, --closes i --do (albo --podsumowanie LOG)")
    with open(a.ranking, encoding="utf-8") as f:
        rk = json.load(f)
    daty, dane = wczytaj_closes(a.closes)
    d0 = rk["d0"]
    d1 = max(d for d in daty if d <= a.do)
    ostrzezenia = []
    if d1 != a.do:
        ostrzezenia.append(f"OSTRZEŻENIE: w cache nie ma sesji {a.do} — rozliczono do {d1}; odśwież cache (ranking.py --fetch) i NIE loguj tego biegu")
    sesje = len([d for d in daty if d0 < d <= d1 and d in dane.get(INDEX, {})])
    wyniki = {}
    for nazwa, k in (rk.get("konstrukcje") or {}).items():
        if not isinstance(k, dict) or not k.get("long") or not k.get("short"):
            print(f"{nazwa}: pominięty — brak list long/short" + (f" ({k.get('pominiety')})" if isinstance(k, dict) and k.get("pominiety") else ""))
            continue
        w = rozlicz(dane, daty, d0, d1, k["long"], k["short"])
        if w:
            r = k.get("ryzyko") or {}
            w["sigma_ex_ante_tyg_pp"] = r.get("sigma60_tyg_unit_pp")
            w["b_sox_net_ex_ante"] = r.get("b_sox_net")
            wyniki[nazwa] = w
    if a.faktyczny_long and a.faktyczny_short:
        w = rozlicz(dane, daty, d0, d1, a.faktyczny_long, a.faktyczny_short)
        if w:
            r = ((rk.get("konstrukcje") or {}).get(FAKT) or {}).get("ryzyko") or {}
            w["sigma_ex_ante_tyg_pp"] = r.get("sigma60_tyg_unit_pp")
            w["b_sox_net_ex_ante"] = r.get("b_sox_net")
            wyniki[FAKT] = w
    if ETF_LONG in dane and ETF_SHORT in dane:
        w = rozlicz(dane, daty, d0, d1, [ETF_LONG], [ETF_SHORT])
        if w:
            w["sigma_ex_ante_tyg_pp"], w["b_sox_net_ex_ante"] = None, None
            wyniki[f"ETF_{ETF_LONG}_{ETF_SHORT}"] = w
    print(f"Rozliczenie koszyków cieni: D0 {d0} → {d1} ({sesje} sesji), ^NDX {next(iter(wyniki.values()))['ndx_pct'] if wyniki else 'b.d.'}%"
          + (f", pokrycie {a.pokrycie}" if a.pokrycie else ""))
    print("| koszyk | spread_pp | long śr. | short śr. | hit L | hit S | σ zreal. tyg. | σ ex ante | skład |")
    print("|---|---|---|---|---|---|---|---|---|")
    for nazwa, w in wyniki.items():
        sklad = ", ".join(n["ticker"] for n in w["nogi"] if n["strona"] == "long") + " / " + ", ".join(n["ticker"] for n in w["nogi"] if n["strona"] == "short")
        print(f"| {nazwa} | {w['spread_pp']:+.2f} | {w['long_sr_pp']:+.2f} | {w['short_sr_pp']:+.2f} | {w['hit_long']} | {w['hit_short']} | "
              f"{w['sigma_zreal_tyg_pp'] if w['sigma_zreal_tyg_pp'] is not None else 'b.d.'} | {w['sigma_ex_ante_tyg_pp'] if w['sigma_ex_ante_tyg_pp'] is not None else 'b.d.'} | {sklad} |")
    for o in ostrzezenia:
        print(o)
    if a.log and not ostrzezenia:
        wiersz = {"version": a.version or rk.get("version", ""), "d0": d0, "d1": d1, "sesje": sesje, "pokrycie": a.pokrycie,
                  "zapis": datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
                  "koszyki": {n: {k: v for k, v in w.items() if k != "nogi"} for n, w in wyniki.items()},
                  "nogi": {n: w["nogi"] for n, w in wyniki.items()}}
        with open(a.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(wiersz, ensure_ascii=False) + "\n")
        print(f"dopisano wiersz do {a.log}")
    elif a.log:
        print(f"NIE dopisano wiersza do {a.log} — patrz ostrzeżenie")


if __name__ == "__main__":
    main()
