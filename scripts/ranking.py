#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ranking.py — deterministyczny ranking ilościowy i konstrukcja koszyka 5L/5S
dla systemu NDX100 (sobota, KROK B rutyny tygodniowej od 2026-W9).

Dlaczego ten skrypt istnieje (analiza 18.10.2026, rutyny/ANALIZA-2026-10-18-*.md):
  * wynik Modelu 3.0 (scoring uznaniowy) nie miał mocy predykcyjnej na 5 sesji
    (IC ≈ −0,10, n = 7) i w ~75% był po prostu momentum 6–12M + beta;
  * jedyny sygnał cenowy z dodatnim znakiem w 5-letnim przekroju to momentum
    relatywne 6M: +1,1 p.p./tydz. brutto, t 2,1 (bt_momentum, skład dzisiejszy,
    bez skipu); wariant produkcyjny skip 5 na uniwersum point-in-time: +0,7 brutto
    (t 1,55), +0,44 netto (t 0,95) — najlepszy z siatki skip 0/5/10 (C1), czyli
    in-sample; dowód przewagi jest słaby i tak go opisuj;
  * ryzykiem koszyka rządzi koncentracja czynnikowa (półprzewodniki vs
    defensywy, b_SOX ≈ 1,1–2,1) i sizing, nie dobór nazw — dlatego skrypt
    liczy ekspozycje czynnikowe, σ koszyka i proponowaną alokację.

Użycie (w katalogu repo):
  python3 scripts/ranking.py --closes <plik.csv> --tv data/tv-screen-<version>.json \
      [--d0 RRRR-MM-DD] [--earnings kalendarz.json] [--exclude T1 T2 ...] \
      [--out data/ranking-<version>.json] [--md <plik.md>]
  python3 scripts/ranking.py --fetch --tv data/tv-screen-<version>.json ...   # pobiera 1y z Yahoo

Wejścia:
  --closes   CSV z kolumną `date` i kolumnami tickerów (zamknięcia dzienne);
             musi zawierać ^NDX; do ekspozycji czynnikowych także ^SOX, XLP,
             XLU, XLV, QQQ (gdy brak — ekspozycje = b.d.). Bez --closes i bez
             --fetch skrypt szuka ostatniego pliku ranking-cache.
  --fetch    pobierz serie 1y (spark Yahoo przez scripts/kursy.py) dla kluczy
             epics z signals.json + indeksów/ETF-ów czynnikowych i zapisz do
             --cache (domyślnie data/ranking-cache.csv — bez liczb z rachunku).
  --tv       snapshot run-screener (rows[].name/industry/sector) — grupy branżowe.
  --earnings JSON {ticker: "RRRR-MM-DD"} dat raportów (FMP/TradingView) —
             veto EVENT dla raportu w oknie D0+1…D0+EVENT_WINDOW_DAYS dni
             kalendarzowych (7 ≈ sesje D+1…D+5; chroni okno pomiaru, nie
             poniedziałkową rotację D0+10).
  --earnings-from-tv  daty raportów z kolumny earnings_release_next_date snapshotu
             --tv (0 wywołań); plik --earnings nadpisuje te daty per ticker.
  --exclude  tickery wyłączone z obu stron, każdy jako TICKER albo TICKER=POWÓD
             (np. MSTR=R8 WDAY=K6 KHC=indeks); powód trafia do tekstu veta
             i do `exclude_powody`; przy niepustej liście skrypt liczy też cień
             E_bez_exclude (koszt listy = spread(E_bez_exclude) − spread(E)).
  --faktyczny-long/--faktyczny-short  koszyk faktycznie zapisany w signals.json →
             konstrukcja FAKTYCZNY z polem ryzyko (dla W8 ≠ E; od W9 = E).
  --version  wersja koszyka (np. 2026-W9) zapisywana w JSON — czyta ją koszyki_cienie.py.

Wyjście: JSON (pełny ranking: czynniki, percentyle, veta, daty raportów,
5 konstrukcji A–E z ekspozycjami i σ koszyka — E jest koszykiem bota od
2026-W9 — oraz opcjonalnie E_bez_exclude i FAKTYCZNY; percentyl σ liczony
wobec 1000 losowych koszyków 5/5 z uniwersum PO vetach) + tabela markdown.
Skrypt NIE dotyka signals.json — rutyna przepisuje wybór do pól long/short.
Wszystkie parametry mają wartości domyślne prerejestrowane 18.10.2026;
zmiana = commit z datą w nagłówku tego pliku.
"""
import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------- parametry
MOM_WIN, MOM_SKIP = 126, 5          # momentum 6M relatywne z pominięciem 5 sesji
MOM12_WIN, MOM12_SKIP = 252, 21     # momentum 12M−1M (informacyjnie)
SIGMA_WIN = 60                      # σ dzienna nóg i koszyka
BETA_WIN = 250                      # bety czynnikowe
MIN_HISTORY = MOM_WIN + MOM_SKIP + 1
SHORT_VETO_R10 = -0.20              # nie shortuj po spadku ≤ −20% w 10 sesjach (K13)
SIGMA_VETO_MULT = 3.0               # noga o σ60 > 3× mediany uniwersum poza koszykiem (ryzyko, nie prognoza)
FACTOR_BUDGET = 0.5                 # konstrukcje D/E: |b_SOX net| ≤ 0,5 (D także |b_DEF net| ≤ 0,5)
PAIR_POOL = 8                       # konstrukcja E: pula par o największym rozstępie momentum
MAX_PRICE_USD = 1280.0              # veto cenowe (wykonalność lotu 0,1 akcji przy ALLOC 0,08 i kapitale odniesienia START_EQUITY;
                                    # decyzja 18.10.2026, projekt C) — 0 = wyłączone; nadpisanie --max-price; NIE liczyć z kapitału rachunku w rutynie
MAX_SWAPS = 6                       # maks. wymian przy domykaniu budżetu czynnikowego
EVENT_WINDOW_DAYS = 7               # raport w D+1…D+5 (dni kalendarzowe od D0)
MIN_IND, MIN_GROUP = 4, 3           # grupa = industry o ≥4 spółkach, inaczej sector; grupa <3 → Pozostałe
VOL_TARGET_DAILY = 0.015            # cel σ dziennej kapitału
ALLOC_MIN, ALLOC_MAX = 0.04, 0.12   # granice alokacji na nogę (udział kapitału)
N_RANDOM = 1000                     # koszyki losowe do percentyla σ
FACTOR_ETFS = {"SOX": "^SOX", "QQQ": "QQQ", "XLP": "XLP", "XLU": "XLU", "XLV": "XLV", "SMH": "SMH"}  # SMH tylko do cienia ETF (koszyki_cienie.py)
INDEX = "^NDX"

# ręczne uzupełnienie taksonomii dla spółek spoza screenera (poza indeksem)
IND_FALLBACK = {"KHC": ("Food: Major Diversified", "Consumer Non-Durables"),
                "WBD": ("Broadcasting", "Consumer Services")}


# ---------------------------------------------------------------- dane
def wczytaj_closes(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        r = csv.reader(f)
        naglowek = next(r)
        kol = naglowek[1:]
        dane = {k: {} for k in kol}
        daty = []
        for row in r:
            if not row or not row[0]:
                continue
            d = row[0]
            niepuste = False
            for k, v in zip(kol, row[1:]):
                if v not in ("", None):
                    try:
                        dane[k][d] = float(v)
                        niepuste = True
                    except ValueError:
                        pass
            if niepuste:
                daty.append(d)
    return sorted(set(daty)), dane


def zapisz_closes(sciezka, daty, dane):
    kol = sorted(dane)
    with open(sciezka, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date"] + kol)
        for d in daty:
            w.writerow([d] + [dane[k].get(d, "") for k in kol])


def pobierz_1y(tickery):
    """Serie 1y przez scripts/kursy.py (spark, paczki po 20, UA jak w kursy.py)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import kursy  # noqa: E402
    symbole = list(tickery) + [INDEX] + list(FACTOR_ETFS.values())
    mapa, problemy = kursy.pobierz_batch(symbole, zakres="1y")
    dane, daty = {}, set()
    for sym, bary in mapa.items():
        dane[sym] = {d: c for d, c in bary}
        daty.update(dane[sym])
    return sorted(daty), dane, problemy


def seria(dane, t, daty_do):
    """Lista zamknięć tickera w kolejności dat (tylko sesje z notowaniem)."""
    s = dane.get(t, {})
    return [(d, s[d]) for d in daty_do if d in s]


def zwroty(dane, t, daty):
    s = dane.get(t, {})
    out = {}
    prev = None
    for d in daty:
        c = s.get(d)
        if c is None:
            continue
        if prev is not None and prev > 0:
            out[d] = c / prev - 1.0
        prev = c
    return out


# ---------------------------------------------------------------- czynniki
def mom_rel(dane, t, idx_t, daty_do, win, skip):
    s = seria(dane, t, daty_do)
    i = seria(dane, idx_t, daty_do)
    if len(s) < win + skip + 1 or len(i) < win + skip + 1:
        return None
    r_t = s[-1 - skip][1] / s[-1 - skip - win][1] - 1.0
    r_i = i[-1 - skip][1] / i[-1 - skip - win][1] - 1.0
    return r_t - r_i


def ret_n(dane, t, daty_do, n):
    s = seria(dane, t, daty_do)
    if len(s) < n + 1:
        return None
    return s[-1][1] / s[-1 - n][1] - 1.0


def sigma_dzienna(zw, daty_do, win):
    xs = [zw[d] for d in daty_do[-win:] if d in zw]
    return statistics.pstdev(xs) if len(xs) >= win // 2 else None


def beta(zw_t, zw_f, daty_do, win):
    pary = [(zw_t[d], zw_f[d]) for d in daty_do[-win:] if d in zw_t and d in zw_f]
    if len(pary) < win // 2:
        return None
    mx = statistics.fmean(p[0] for p in pary)
    my = statistics.fmean(p[1] for p in pary)
    vy = sum((p[1] - my) ** 2 for p in pary)
    if vy <= 0:
        return None
    return sum((p[0] - mx) * (p[1] - my) for p in pary) / vy


def percentyle(mapa):
    """{ticker: wartość} → {ticker: percentyl 0–100} (rosnąco; None pominięte)."""
    el = sorted((v, t) for t, v in mapa.items() if v is not None)
    n = len(el)
    return {t: (100.0 * i / (n - 1) if n > 1 else 50.0) for i, (v, t) in enumerate(el)}


# ---------------------------------------------------------------- grupy branżowe
def grupy(uniwersum, tv_rows):
    ind = {}
    for r in tv_rows or []:
        ind[r.get("name")] = (r.get("industry") or "", r.get("sector") or "")
    for t, v in IND_FALLBACK.items():
        ind.setdefault(t, v)
    licz_ind = {}
    for t in uniwersum:
        i, s = ind.get(t, ("", ""))
        licz_ind[i] = licz_ind.get(i, 0) + 1
    g = {}
    for t in uniwersum:
        i, s = ind.get(t, ("", ""))
        if not i and not s:
            g[t] = "Pozostałe"
        elif licz_ind.get(i, 0) >= MIN_IND:
            g[t] = i
        else:
            g[t] = s or i
    licz_g = {}
    for t, gg in g.items():
        licz_g[gg] = licz_g.get(gg, 0) + 1
    for t, gg in list(g.items()):
        if licz_g[gg] < MIN_GROUP:
            g[t] = "Pozostałe"
    return g, ind


# ---------------------------------------------------------------- konstrukcje
def konstrukcja_plain(rank, kandyd_l, kandyd_s, n=5):
    lo = [t for t in rank if t in kandyd_l][-n:][::-1]
    sh = [t for t in rank if t in kandyd_s][:n]
    return lo, sh


def konstrukcja_pary(score, grupa, kandyd_l, kandyd_s, n=5):
    """5 par z tej samej grupy: grupy o największej różnicy najlepsza−najgorsza;
    long = najlepsza (dopuszczona do long), short = najgorsza (dopuszczona do short)."""
    po_grupie = {}
    for t, s in score.items():
        if s is None or grupa.get(t, "Pozostałe") == "Pozostałe":
            continue
        po_grupie.setdefault(grupa[t], []).append((s, t))
    kand = []
    for gname, el in po_grupie.items():
        el.sort()
        longs = [t for s, t in el if t in kandyd_l]
        shorts = [t for s, t in el if t in kandyd_s]
        if len(el) < MIN_GROUP or not longs or not shorts:
            continue
        best, worst = longs[-1], shorts[0]
        if best == worst:
            continue
        kand.append((score[best] - score[worst], gname, best, worst))
    kand.sort(reverse=True)
    lo, sh, pary = [], [], []
    for d, gname, b, w in kand[:n]:
        lo.append(b)
        sh.append(w)
        pary.append({"grupa": gname, "long": b, "short": w, "roznica_mom": round(d, 4)})
    return lo, sh, pary


def konstrukcja_neutralna(rank, grupa, kandyd_l, kandyd_s, n=5):
    """Ranking z limitem: maks. 1 long i 1 short z grupy (grupa Pozostałe bez limitu)."""
    lo, sh, uz_l, uz_s = [], [], set(), set()
    for t in reversed(rank):
        if t in kandyd_l and len(lo) < n:
            g = grupa.get(t, "Pozostałe")
            if g == "Pozostałe" or g not in uz_l:
                lo.append(t)
                uz_l.add(g)
    for t in rank:
        if t in kandyd_s and len(sh) < n:
            g = grupa.get(t, "Pozostałe")
            if g == "Pozostałe" or g not in uz_s:
                sh.append(t)
                uz_s.add(g)
    return lo, sh


def konstrukcja_budzet(rank, kandyd_l, kandyd_s, bety, n=5, glebia=15):
    """Start z A (TOP5/BOTTOM5); dopóki |b_SOX net| lub |b_DEF net| > FACTOR_BUDGET, wymieniaj nogę
    o największym wkładzie do przekroczenia na kolejnego kandydata z TOP15/BOTTOM15, który najbardziej
    zmniejsza przekroczenie (maks. MAX_SWAPS wymian). Zwraca (long, short, lista wymian)."""
    top = [t for t in reversed(rank) if t in kandyd_l][:glebia]
    bot = [t for t in rank if t in kandyd_s][:glebia]
    lo, sh = top[:n], bot[:n]
    if not lo or not sh:
        return lo, sh, []

    def b(t, k):
        v = bety.get(t, {}).get(k)
        return 0.0 if v is None else v

    def net(l, s, k):
        return statistics.fmean(b(t, k) for t in l) - statistics.fmean(b(t, k) for t in s)

    def przekr(l, s):
        return max(0.0, abs(net(l, s, "b_sox")) - FACTOR_BUDGET) + max(0.0, abs(net(l, s, "b_def")) - FACTOR_BUDGET)

    wymiany = []
    for _ in range(MAX_SWAPS):
        p0 = przekr(lo, sh)
        if p0 <= 1e-9:
            break
        best = None
        for strona, lst, pula in (("long", lo, top), ("short", sh, bot)):
            for i, t in enumerate(lst):
                for c in pula:
                    if c in lo or c in sh:
                        continue
                    nl, ns = list(lo), list(sh)
                    (nl if strona == "long" else ns)[i] = c
                    p1 = przekr(nl, ns)
                    if best is None or p1 < best[0]:
                        best = (p1, strona, t, c, nl, ns)
        if best is None or best[0] >= p0 - 1e-9:
            break
        _, strona, t, c, lo, sh = best
        wymiany.append({"strona": strona, "z": t, "na": c})
    return lo, sh, wymiany


def konstrukcja_E(score, grupa, kandyd_l, kandyd_s, bety, zw, daty_do, n=5, pool=None):
    """KONSTRUKCJA E (proces v2, decyzja 18.10.2026): z puli PAIR_POOL par o największym
    rozstępie momentum w grupie (jak B) wybierz n par o największej sumie rozstępów,
    dla których |śr. b_SOX(long) − śr. b_SOX(short)| ≤ FACTOR_BUDGET; gdy żadna piątka nie
    spełnia budżetu — piątka o najmniejszym |b_SOX net|. Pole `wybor`: 'budzet' | 'min_b' |
    'bez_czynnika' (brak bety SOX dla którejś nogi — budżet nieliczony, wybór po rozstępie),
    z dopiskiem '+dopelnione', gdy par branżowych było mniej niż n i skrypt dopełnił je
    parami bez grupy (najlepsze momentum long × najgorsze short spośród niewykorzystanych
    kandydatów); 'za_malo_par' = nawet po dopełnieniu < n par (koszyk NIE nadaje się do zapisu).
    Listy long/short uporządkowane od pary o najwyższej σ60 spreadu pary (próg miękki bota
    zamyka pierwsze SOFT_PARY nogi z każdej listy). Zwraca (long, short, pary, b_sox_net,
    wybor, dopelnienia)."""
    import itertools
    pool = pool or PAIR_POOL
    lo_all, sh_all, pary = konstrukcja_pary(score, grupa, kandyd_l, kandyd_s, n=pool)
    dopelnienia = []
    if len(pary) < n:
        uzyte = {p["long"] for p in pary} | {p["short"] for p in pary}
        longs = sorted((t for t in kandyd_l if t not in uzyte and score.get(t) is not None), key=lambda t: -score[t])
        shorts = sorted((t for t in kandyd_s if t not in uzyte and score.get(t) is not None), key=lambda t: score[t])
        while len(pary) < n and longs and shorts:
            b = longs.pop(0)
            w = next((x for x in shorts if x != b), None)
            if w is None:
                break
            shorts.remove(w)
            pary.append({"grupa": "dopełnienie (bez grupy)", "long": b, "short": w, "roznica_mom": round(score[b] - score[w], 4)})
            dopelnienia.append(f"{b}/{w}")

    def sigma_pary(p):
        sp = spread_dzienny(zw, [p["long"]], [p["short"]], daty_do, SIGMA_WIN)
        return statistics.pstdev(sp) if len(sp) >= SIGMA_WIN // 2 else 0.0
    if len(pary) < n:
        for p in pary:
            p["sigma60_pary"] = round(sigma_pary(p), 5)
        pary.sort(key=lambda p: -p["sigma60_pary"])
        return [p["long"] for p in pary], [p["short"] for p in pary], pary, None, "za_malo_par", dopelnienia

    brak_bety = any(bety.get(t, {}).get("b_sox") is None for p in pary for t in (p["long"], p["short"]))

    def b(t):
        return bety[t]["b_sox"]
    best = None
    for comb in itertools.combinations(range(len(pary)), n):
        L = [pary[i]["long"] for i in comb]
        S = [pary[i]["short"] for i in comb]
        suma = sum(pary[i]["roznica_mom"] for i in comb)
        if brak_bety:
            bnet, klucz = None, (0, -suma)
        else:
            bnet = statistics.fmean(b(t) for t in L) - statistics.fmean(b(t) for t in S)
            klucz = (0 if abs(bnet) <= FACTOR_BUDGET else 1, -suma if abs(bnet) <= FACTOR_BUDGET else abs(bnet))
        if best is None or klucz < best[0]:
            best = (klucz, comb, bnet)
    klucz, comb, bnet = best
    wybrane = [pary[i] for i in comb]
    # porządek: para o najwyższej σ60 spreadu pary pierwsza
    for p in wybrane:
        p["sigma60_pary"] = round(sigma_pary(p), 5)
    wybrane.sort(key=lambda p: -p["sigma60_pary"])
    wybor = "bez_czynnika" if brak_bety else ("budzet" if klucz[0] == 0 else "min_b")
    if dopelnienia:
        wybor += "+dopelnione"
    return ([p["long"] for p in wybrane], [p["short"] for p in wybrane], wybrane,
            None if bnet is None else round(bnet, 3), wybor, dopelnienia)


# ---------------------------------------------------------------- ryzyko koszyka
def spread_dzienny(zw, lo, sh, daty_do, win):
    out = []
    for d in daty_do[-win:]:
        rl = [zw[t][d] for t in lo if d in zw.get(t, {})]
        rs = [zw[t][d] for t in sh if d in zw.get(t, {})]
        if len(rl) == len(lo) and len(rs) == len(sh) and lo and sh:
            out.append(statistics.fmean(rl) - statistics.fmean(rs))
    return out


def ryzyko_koszyka(zw, lo, sh, daty_do, bety, uniwersum, seed=20261018, opis_puli="po_vetach (kandydaci long ∪ short)"):
    """σ koszyka, korelacje, ekspozycje netto, ALLOC diagnostyczny; percentyl σ wobec N_RANDOM
    losowych koszyków 5/5 z `uniwersum` (w policz(): kandydaci PO vetach, bez nóg koszyka)."""
    sp = spread_dzienny(zw, lo, sh, daty_do, SIGMA_WIN)
    sigma_unit = statistics.pstdev(sp) if len(sp) >= SIGMA_WIN // 2 else None
    # korelacje par w LONG
    rho = []
    for i in range(len(lo)):
        for j in range(i + 1, len(lo)):
            a, b = zw.get(lo[i], {}), zw.get(lo[j], {})
            pary = [(a[d], b[d]) for d in daty_do[-SIGMA_WIN:] if d in a and d in b]
            if len(pary) >= SIGMA_WIN // 2:
                try:
                    rho.append(statistics.correlation([p[0] for p in pary], [p[1] for p in pary]))
                except statistics.StatisticsError:
                    pass
    rho_sr = statistics.fmean(rho) if rho else None
    n_eff = (len(lo) / (1 + (len(lo) - 1) * rho_sr)) if rho_sr is not None and rho_sr > -1.0 / max(1, len(lo) - 1) else None
    # percentyl σ wobec losowych koszyków 5/5
    rnd = random.Random(seed)
    los = []
    pula = [t for t in uniwersum if t not in lo and t not in sh]
    for _ in range(N_RANDOM):
        if len(pula) < 10:
            break
        wyb = rnd.sample(pula, 10)
        s = spread_dzienny(zw, wyb[:5], wyb[5:], daty_do, SIGMA_WIN)
        if len(s) >= SIGMA_WIN // 2:
            los.append(statistics.pstdev(s))
    pct = None
    if los and sigma_unit is not None:
        pct = 100.0 * sum(1 for x in los if x <= sigma_unit) / len(los)

    def net(klucz):
        bl = [bety[t][klucz] for t in lo if bety.get(t, {}).get(klucz) is not None]
        bs = [bety[t][klucz] for t in sh if bety.get(t, {}).get(klucz) is not None]
        if len(bl) != len(lo) or len(bs) != len(sh) or not lo:
            return None
        return statistics.fmean(bl) - statistics.fmean(bs)

    alloc = None
    if sigma_unit:
        alloc = max(ALLOC_MIN, min(ALLOC_MAX, VOL_TARGET_DAILY / (sigma_unit * 5.0)))
        # σ koszyka równych wag = alloc×5×σ_unit (5 nóg na stronę o wadze alloc)
    return {
        "sigma60_unit_dzienna": None if sigma_unit is None else round(sigma_unit, 5),
        "sigma60_tyg_unit_pp": None if sigma_unit is None else round(sigma_unit * math.sqrt(5) * 100, 2),
        "percentyl_sigma_vs_losowe": None if pct is None else round(pct, 1),
        "rho60_par_long": None if rho_sr is None else round(rho_sr, 3),
        "n_eff_long": None if n_eff is None else round(n_eff, 2),
        "beta_ndx_net": None if net("beta_ndx") is None else round(net("beta_ndx"), 3),
        "b_sox_net": None if net("b_sox") is None else round(net("b_sox"), 3),
        "b_def_net": None if net("b_def") is None else round(net("b_def"), 3),
        "alloc_pct_proponowany": None if alloc is None else round(alloc, 4),
        "sigma_dzienna_kapitalu_przy_alloc": None if (alloc is None or sigma_unit is None) else round(alloc * 5 * sigma_unit * 100, 2),
        "parametry": {"VOL_TARGET_DAILY": VOL_TARGET_DAILY, "ALLOC_MIN": ALLOC_MIN, "ALLOC_MAX": ALLOC_MAX,
                      "SIGMA_WIN": SIGMA_WIN, "N_RANDOM": N_RANDOM, "uniwersum_losowe": opis_puli, "n_pula": len(pula)},
    }


# ---------------------------------------------------------------- główny bieg
def policz(daty, dane, uniwersum, tv_rows, d0=None, earnings=None, exclude=(), faktyczny=None):
    """exclude: iterable tickerów albo dict {ticker: powód}; faktyczny: (long, short) koszyka z signals.json."""
    excl = dict(exclude) if isinstance(exclude, dict) else {t: "rutyna" for t in (exclude or ())}
    if d0 is None:
        d0 = daty[-1]
    daty_do = [d for d in daty if d <= d0]
    if not daty_do:
        raise SystemExit(f"brak sesji do {d0}")
    ostrzezenia = []
    if daty_do[-1] != d0:
        ostrzezenia.append(f"D0 {d0} nie ma w danych — użyto ostatniej sesji {daty_do[-1]}; sprawdź --fetch")
    d0 = daty_do[-1]
    zw = {t: zwroty(dane, t, daty_do) for t in list(uniwersum) + [INDEX] + list(FACTOR_ETFS.values()) if t in dane}
    # czynniki
    f_sox = {d: zw[FACTOR_ETFS["SOX"]][d] - zw[INDEX][d] for d in daty_do
             if FACTOR_ETFS["SOX"] in zw and d in zw[FACTOR_ETFS["SOX"]] and d in zw[INDEX]}
    f_def = {}
    if all(FACTOR_ETFS[k] in zw for k in ("XLP", "XLU", "XLV", "QQQ")):
        for d in daty_do:
            try:
                f_def[d] = (zw["XLP"][d] + zw["XLU"][d] + zw["XLV"][d]) / 3 - zw["QQQ"][d]
            except KeyError:
                pass
    wiersze, score = {}, {}
    for t in uniwersum:
        if t not in dane or len(seria(dane, t, daty_do)) < MIN_HISTORY:
            wiersze[t] = {"ticker": t, "status": "brak historii (<%d sesji)" % MIN_HISTORY}
            score[t] = None
            continue
        m6 = mom_rel(dane, t, INDEX, daty_do, MOM_WIN, MOM_SKIP)
        m12 = mom_rel(dane, t, INDEX, daty_do, MOM12_WIN, MOM12_SKIP)
        r5, r10 = ret_n(dane, t, daty_do, 5), ret_n(dane, t, daty_do, 10)
        s60 = sigma_dzienna(zw[t], daty_do, SIGMA_WIN)
        b_ndx = beta(zw[t], zw[INDEX], daty_do, BETA_WIN)
        b_sox = beta(zw[t], f_sox, daty_do, BETA_WIN) if f_sox else None
        b_def = beta(zw[t], f_def, daty_do, BETA_WIN) if f_def else None
        ost = seria(dane, t, daty_do)[-1]
        wiersze[t] = {"ticker": t, "status": "ok", "close": ost[1], "close_date": ost[0],
                      "mom6_rel": m6, "mom12_1_rel": m12, "r5": r5, "r10": r10, "sigma60": s60,
                      "beta_ndx": b_ndx, "b_sox": b_sox, "b_def": b_def}
        score[t] = m6
    pct6 = percentyle({t: w.get("mom6_rel") for t, w in wiersze.items() if w.get("status") == "ok"})
    pct12 = percentyle({t: w.get("mom12_1_rel") for t, w in wiersze.items() if w.get("status") == "ok"})
    pcts = percentyle({t: w.get("sigma60") for t, w in wiersze.items() if w.get("status") == "ok"})
    # veta
    sig_list = [w["sigma60"] for w in wiersze.values() if w.get("status") == "ok" and w.get("sigma60") is not None]
    med_sigma = statistics.median(sig_list) if sig_list else None
    d0_date = date.fromisoformat(d0)
    okno_do = d0_date + timedelta(days=EVENT_WINDOW_DAYS)
    earn_ok, earn_blad = 0, []
    for t, w in wiersze.items():
        if w.get("status") != "ok":
            continue
        veta = []
        if t in excl:
            veta.append(f"exclude: {excl[t]}")
        w["earnings_date"] = None
        if earnings and t in earnings:
            try:
                e = date.fromisoformat(str(earnings[t])[:10])
                earn_ok += 1
                w["earnings_date"] = e.isoformat()
                if d0_date < e <= okno_do:
                    veta.append(f"EVENT: raport {e.isoformat()} w oknie D0+1…D0+{EVENT_WINDOW_DAYS} dni (≈ sesje D+1…D+5)")
            except ValueError:
                earn_blad.append(t)
        if w["sigma60"] is not None and med_sigma and w["sigma60"] > SIGMA_VETO_MULT * med_sigma:
            veta.append("σ60 %.1f%% > %.0f× mediany (%.1f%%)" % (w["sigma60"] * 100, SIGMA_VETO_MULT, med_sigma * 100))
        w["veto_long"] = list(veta)
        w["veto_short"] = list(veta)
        if MAX_PRICE_USD > 0 and w.get("close") and w["close"] > MAX_PRICE_USD:
            w["veto_long"].append("cena %.0f > MAX_PRICE_USD %.0f (lot 0,1 akcji)" % (w["close"], MAX_PRICE_USD))
            w["veto_short"].append("cena %.0f > MAX_PRICE_USD %.0f (lot 0,1 akcji)" % (w["close"], MAX_PRICE_USD))
        if w["r10"] is not None and w["r10"] <= SHORT_VETO_R10:
            w["veto_short"].append("K13: spadek 10-sesyjny ≤ −20%% (%.1f%%)" % (w["r10"] * 100))
        w["pct_mom6"] = round(pct6.get(t, 50.0), 1)
        w["pct_mom12_1"] = round(pct12.get(t, 50.0), 1)
        w["pct_sigma60"] = round(pcts.get(t, 50.0), 1)
    ok = [t for t, w in wiersze.items() if w.get("status") == "ok"]
    rank = sorted(ok, key=lambda t: score[t])  # rosnąco: najgorsze momentum pierwsze
    kandyd_l = {t for t in ok if not wiersze[t]["veto_long"]}
    kandyd_s = {t for t in ok if not wiersze[t]["veto_short"]}
    bez_excl = lambda veta: [v for v in veta if not v.startswith("exclude")]  # noqa: E731
    kandyd_l_bx = {t for t in ok if not bez_excl(wiersze[t]["veto_long"])}
    kandyd_s_bx = {t for t in ok if not bez_excl(wiersze[t]["veto_short"])}
    pula_los = sorted(kandyd_l | kandyd_s)  # percentyl σ wobec losowych koszyków z uniwersum PO vetach
    grupa, ind = grupy(ok, tv_rows)
    for t in ok:
        wiersze[t]["grupa"] = grupa.get(t)
        wiersze[t]["industry"] = ind.get(t, ("", ""))[0]
        wiersze[t]["sector"] = ind.get(t, ("", ""))[1]
    bety = {t: {"beta_ndx": wiersze[t]["beta_ndx"], "b_sox": wiersze[t]["b_sox"], "b_def": wiersze[t]["b_def"]} for t in ok}
    kons = {}
    lo, sh = konstrukcja_plain(rank, kandyd_l, kandyd_s)
    kons["A_mom6_top5_bottom5"] = {"long": lo, "short": sh, "ryzyko": ryzyko_koszyka(zw, lo, sh, daty_do, bety, pula_los)}
    lo, sh, pary = konstrukcja_pary(score, grupa, kandyd_l, kandyd_s)
    kons["B_5_par_branzowych"] = {"long": lo, "short": sh, "pary": pary, "ryzyko": ryzyko_koszyka(zw, lo, sh, daty_do, bety, pula_los)}
    lo, sh = konstrukcja_neutralna(rank, grupa, kandyd_l, kandyd_s)
    kons["C_neutralna_branzowo"] = {"long": lo, "short": sh, "ryzyko": ryzyko_koszyka(zw, lo, sh, daty_do, bety, pula_los)}
    lo, sh, wym = konstrukcja_budzet(rank, kandyd_l, kandyd_s, bety)
    kons["D_budzet_czynnikowy"] = {"long": lo, "short": sh, "wymiany": wym, "ryzyko": ryzyko_koszyka(zw, lo, sh, daty_do, bety, pula_los)}
    lo, sh, pary, bnet, wybor, dopeln = konstrukcja_E(score, grupa, kandyd_l, kandyd_s, bety, zw, daty_do)
    kons["E_pary_budzet_sox"] = {"long": lo, "short": sh, "pary": pary, "b_sox_net_ex_ante": bnet, "wybor": wybor,
                                 "dopelnienia": dopeln, "kompletna": len(lo) == 5 and len(sh) == 5,
                                 "pula_par": PAIR_POOL, "ryzyko": ryzyko_koszyka(zw, lo, sh, daty_do, bety, pula_los)}
    if excl:
        lo2, sh2, pary2, bnet2, wybor2, dopeln2 = konstrukcja_E(score, grupa, kandyd_l_bx, kandyd_s_bx, bety, zw, daty_do)
        kons["E_bez_exclude"] = {"long": lo2, "short": sh2, "pary": pary2, "b_sox_net_ex_ante": bnet2, "wybor": wybor2,
                                 "dopelnienia": dopeln2, "ryzyko": ryzyko_koszyka(zw, lo2, sh2, daty_do, bety, pula_los),
                                 "_uwaga": "ten sam algorytm co E bez listy --exclude; koszt listy = spread(E_bez_exclude) − spread(E)"}
    if faktyczny and faktyczny[0] and faktyczny[1]:
        fl, fs = list(faktyczny[0]), list(faktyczny[1])
        brak = [t for t in fl + fs if t not in ok]
        kons["FAKTYCZNY"] = {"long": fl, "short": fs,
                             "ryzyko": ryzyko_koszyka(zw, fl, fs, daty_do, bety, pula_los) if not brak else None,
                             "_uwaga": "koszyk faktycznie zapisany w signals.json (podany przez rutynę/właściciela); od 2026-W9 tożsamy z E"
                                       + (f"; brak historii dla {brak} — ryzyko = null" if brak else "")}
    kons["E_pary_budzet_sox"]["_uwaga"] = ("KOSZYK BOTA od 2026-W9 (proces v2): listy long/short w kolejności od pary o najwyższej "
                                           "σ60 (próg miękki bota zamyka pierwsze SOFT_PARY nogi każdej listy)")
    return {
        "_opis": "ranking.py — ranking ilościowy (momentum 6M relatywne, skip 5) i konstrukcje koszyka; bez liczb z rachunku",
        "d0": d0, "n_uniwersum": len(uniwersum), "n_z_historia": len(ok),
        "ostrzezenia": ostrzezenia, "exclude_powody": excl,
        "earnings_n_ok": earn_ok, "earnings_n_blad": earn_blad,
        "parametry": {"MOM_WIN": MOM_WIN, "MOM_SKIP": MOM_SKIP, "SIGMA_WIN": SIGMA_WIN, "BETA_WIN": BETA_WIN,
                      "SHORT_VETO_R10": SHORT_VETO_R10, "SIGMA_VETO_MULT": SIGMA_VETO_MULT,
                      "FACTOR_BUDGET": FACTOR_BUDGET, "MAX_SWAPS": MAX_SWAPS, "PAIR_POOL": PAIR_POOL,
                      "MAX_PRICE_USD": MAX_PRICE_USD, "EVENT_WINDOW_DAYS": EVENT_WINDOW_DAYS,
                      "MIN_IND": MIN_IND, "MIN_GROUP": MIN_GROUP},
        "czynniki_dostepne": {"sox": bool(f_sox), "def": bool(f_def)},
        "ranking": [wiersze[t] for t in reversed(rank)],  # od najlepszego momentum
        "bez_historii": [t for t, w in wiersze.items() if w.get("status") != "ok"],
        "konstrukcje": kons,
    }


def tabela_md(wynik, n=15):
    L = [f"# Ranking ilościowy — D0 {wynik['d0']} (momentum 6M rel., skip {MOM_SKIP}; {wynik['n_z_historia']}/{wynik['n_uniwersum']} spółek z historią)", ""]
    for nazwa, k in wynik["konstrukcje"].items():
        r = k["ryzyko"]
        L.append(f"**{nazwa}**: LONG {', '.join(k['long'])} · SHORT {', '.join(k['short'])} · "
                 f"σ60 tyg. {r['sigma60_tyg_unit_pp']} p.p. (percentyl vs losowe {r['percentyl_sigma_vs_losowe']}) · "
                 f"b_SOX net {r['b_sox_net']} · b_DEF net {r['b_def_net']} · β net {r['beta_ndx_net']} · "
                 f"ρ60 par LONG {r['rho60_par_long']} (N_eff {r['n_eff_long']}) · ALLOC prop. {r['alloc_pct_proponowany']} "
                 f"(σ dz. kapitału {r['sigma_dzienna_kapitalu_przy_alloc']}%)")
        if k.get("pary"):
            L.append("  pary: " + "; ".join(f"{p['grupa']}: {p['long']} / {p['short']}" for p in k["pary"]))
        if k.get("wymiany"):
            L.append("  wymiany (budżet czynnikowy): " + "; ".join(f"{w['strona']} {w['z']}→{w['na']}" for w in k["wymiany"]))
        if k.get("wybor"):
            L.append(f"  wybór E: {k['wybor']} (b_SOX net ex ante {k['b_sox_net_ex_ante']}, pula {k['pula_par']} par"
                     + (f"; dopełnienia: {', '.join(k['dopelnienia'])}" if k.get('dopelnienia') else "") + ")")
    L.append("")
    L.append("| # | Ticker | mom6 rel | pct | mom12−1 rel | r10 | σ60 dz. | β NDX | b_SOX | b_DEF | grupa | veto long | veto short |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = wynik["ranking"]
    wyb = rows[:n] + [{"ticker": "…"}] + rows[-n:]

    def f(x, d=1, pct=True):
        if x is None:
            return "b.d."
        return (f"{x * 100:+.{d}f}%" if pct else f"{x:.2f}")
    for i, w in enumerate(wyb):
        if w["ticker"] == "…":
            L.append("| … | … | | | | | | | | | | | |")
            continue
        poz = rows.index(w) + 1
        L.append(f"| {poz} | {w['ticker']} | {f(w['mom6_rel'])} | {w['pct_mom6']} | {f(w['mom12_1_rel'])} | {f(w['r10'])} | "
                 f"{f(w['sigma60'], 2)} | {f(w['beta_ndx'], pct=False)} | {f(w['b_sox'], pct=False)} | {f(w['b_def'], pct=False)} | "
                 f"{w.get('grupa', '')} | {'; '.join(w['veto_long']) or '—'} | {'; '.join(w['veto_short']) or '—'} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--closes", help="CSV zamknięć (date + tickery + ^NDX, ^SOX, XLP, XLU, XLV, QQQ)")
    ap.add_argument("--fetch", action="store_true", help="pobierz serie 1y z Yahoo (scripts/kursy.py)")
    ap.add_argument("--cache", default="data/ranking-cache.csv", help="plik zapisu serii po --fetch")
    ap.add_argument("--signals", default="signals.json")
    ap.add_argument("--tv", help="data/tv-screen-<version>.json (industry/sector)")
    ap.add_argument("--d0", help="data D0 (domyślnie ostatnia sesja w danych)")
    ap.add_argument("--earnings", help="JSON {ticker: 'RRRR-MM-DD'} dat raportów")
    ap.add_argument("--earnings-from-tv", action="store_true", help="daty raportów z kolumny earnings_release_next_date snapshotu --tv")
    ap.add_argument("--version", default="", help="wersja koszyka (np. 2026-W9) zapisywana w JSON")
    ap.add_argument("--exclude", nargs="*", default=[], help="tickery wyłączone: TICKER albo TICKER=POWÓD (np. MSTR=R8 WDAY=K6)")
    ap.add_argument("--faktyczny-long", nargs="*", default=[], help="koszyk faktyczny z signals.json → konstrukcja FAKTYCZNY")
    ap.add_argument("--faktyczny-short", nargs="*", default=[])
    ap.add_argument("--max-price", type=float, default=None, help="veto cenowe w USD (wykonalność lotu 0,1 akcji); 0 = wyłączone")
    ap.add_argument("--out", help="ścieżka JSON wyniku")
    ap.add_argument("--md", help="ścieżka tabeli markdown")
    a = ap.parse_args()
    global MAX_PRICE_USD
    if a.max_price is not None:
        MAX_PRICE_USD = a.max_price
    with open(a.signals, encoding="utf-8") as f:
        sig = json.load(f)
    uniwersum = sorted(sig["epics"])
    problemy = []
    if a.fetch:
        daty, dane, problemy = pobierz_1y(uniwersum)
        zapisz_closes(a.cache, daty, dane)
    elif a.closes:
        daty, dane = wczytaj_closes(a.closes)
    elif os.path.exists(a.cache):
        daty, dane = wczytaj_closes(a.cache)
    else:
        raise SystemExit("podaj --closes albo --fetch")
    tv_rows = None
    if a.tv:
        with open(a.tv, encoding="utf-8") as f:
            tv = json.load(f)
        tv_rows = (tv.get("data") or {}).get("rows") or tv.get("rows") or []
    earnings = None
    if a.earnings_from_tv and tv_rows:
        earnings = {r["name"]: str(r["earnings_release_next_date"])[:10] for r in tv_rows
                    if r.get("name") and r.get("earnings_release_next_date")}
    if a.earnings:
        with open(a.earnings, encoding="utf-8") as f:
            earnings = {**(earnings or {}), **json.load(f)}
    excl = {}
    for x in a.exclude:
        t, _, powod = x.partition("=")
        excl[t.strip().upper()] = (powod.strip() or "rutyna")
    wynik = policz(daty, dane, uniwersum, tv_rows, a.d0, earnings, excl, (a.faktyczny_long, a.faktyczny_short))
    wynik["version"] = a.version
    if not earnings:
        wynik["zrodlo_earnings"] = "brak (bez veta EVENT)"
    else:
        wynik["zrodlo_earnings"] = ("tv-snapshot" if a.earnings_from_tv else "") + ("+plik" if a.earnings else "") + f" ({len(earnings)} dat)"
    if a.tv and not tv_rows:
        wynik["ostrzezenia"].append("--tv: brak wierszy (data.rows/rows) — zły format snapshotu? grupy = Pozostałe, bez dat raportów")
    wynik["problemy_pobierania"] = problemy
    wynik["wygenerowano"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(wynik, f, ensure_ascii=False, indent=1)
    md = tabela_md(wynik)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(md)
    print(md)
    if problemy:
        print("PROBLEMY POBIERANIA:", *problemy, sep="\n  ")


if __name__ == "__main__":
    main()
