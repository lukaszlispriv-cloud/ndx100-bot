#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
waliduj_signals.py — ostatnia bramka PRZED commitem signals.json przez rutynę.

Użycie (w katalogu repo):
  python3 -I scripts/waliduj_signals.py --diff HEAD --rutyna puls
  python3 -I scripts/waliduj_signals.py --diff HEAD --rutyna sobota
  python3 -I scripts/waliduj_signals.py --base <plik_poprzedni.json> --rutyna puls [--plik signals.json]

Kod wyjścia 0 = wolno commitować; 1 = NIE commituj (uruchom FALLBACK).

Dlaczego ten skrypt istnieje: app.py::_sanity sprawdza koszyki, epics,
status, exclude, tactical i fills, ale NIE odrzuca obcych kluczy
top-level ani zmian w polach pisanych przez bota. Obce pole (np.
data_quality) albo nadpisane fills / equity_peak / wykonanie przechodzą
do bota po cichu. Ten walidator jest jedyną ochroną przed tym.

Reguły (per rutyna):
  puls   — wobec bazy zmienione tylko: status, exclude, tactical, last_daily
  sobota — wobec bazy zmienione tylko: version, status, long, short, d0,
           generated, exclude (=[]), tactical (=[]), history (dopisany
           DOKŁADNIE jeden wpis; pole "dane_b1": "tv" dozwolone od 12.10.2026);
           epics — wyłącznie dopisanie nowych kluczy
  obie   — zestaw kluczy top-level DOKŁADNIE taki jak KLUCZE; fills,
           equity_peak, wykonanie identyczne z bazą; podstawowa spójność
           (5/5, rozłączność, tickery w epics, pola wpisów exclude/tactical)
"""
import argparse
import json
import re
import subprocess
import sys

KLUCZE = {"_instrukcja", "d0", "epics", "equity_peak", "exclude", "fills",
          "generated", "history", "last_daily", "long", "short", "status",
          "tactical", "version", "wykonanie"}
POLA_BOTA = ("fills", "equity_peak", "wykonanie")
DOZWOLONE = {
    "puls": {"status", "exclude", "tactical", "last_daily"},
    "sobota": {"version", "status", "long", "short", "d0", "generated",
               "exclude", "tactical", "history", "epics"},
}
BASIS = {"cena", "price", "news", "rekom", "short", "rezim", "reżim"}
HISTORY_POLA = {"week", "spread_pp", "spread_fills_pp", "hit_top", "hit_bottom",
                "tactical_pp", "managed_pp", "reaction_pp", "rezim"}
DATA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WERSJA_RE = re.compile(r"^\d{4}-W\d{1,2}$")


def wczytaj_baze(args):
    if args.base:
        with open(args.base, encoding="utf-8") as f:
            return json.load(f)
    out = subprocess.run(["git", "show", f"{args.diff}:{args.plik}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"nie mogę odczytać {args.diff}:{args.plik}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def spojnosc(sig, problemy):
    L, S = list(sig.get("long") or []), list(sig.get("short") or [])
    if len(L) != 5 or len(S) != 5:
        problemy.append("koszyki muszą mieć po 5 spółek")
    if set(L) & set(S):
        problemy.append("long i short się pokrywają")
    epics = sig.get("epics")
    if not isinstance(epics, dict):
        problemy.append("brak mapy epics")
        epics = {}
    for t in L + S:
        if t not in epics:
            problemy.append(f"ticker spoza mapy epics: {t}")
    if str(sig.get("status", "")).upper()[:6] not in ("AKTUAL", "NIEAKT"):
        problemy.append(f"nieznany status: {sig.get('status')}")
    for e in sig.get("exclude") or []:
        for pole in ("ticker", "action", "basis", "reason", "date"):
            if pole not in e:
                problemy.append(f"wpis exclude bez pola {pole}: {e}")
        if e.get("action") not in ("CLOSE", "REDUCE"):
            problemy.append(f"złe action w exclude: {e}")
        if str(e.get("basis", "cena")).lower() not in BASIS:
            problemy.append(f"nieznane basis w exclude: {e}")
        if e.get("ticker") not in L + S:
            problemy.append(f"exclude dla spółki spoza koszyków: {e.get('ticker')}")
    for t in sig.get("tactical") or []:
        if t.get("direction") not in ("BUY", "SELL"):
            problemy.append(f"zły kierunek taktycznej: {t}")
        if not (t.get("epic") or "").strip() and t.get("ticker") not in epics:
            problemy.append(f"taktyczna spoza uniwersum bez epic: {t}")
        if not DATA_RE.match(str(t.get("entry_date", ""))):
            problemy.append(f"taktyczna bez entry_date RRRR-MM-DD: {t}")
    if len(sig.get("tactical") or []) > 2:
        problemy.append("więcej niż 2 pozycje taktyczne")
    d0 = sig.get("d0")
    if d0:
        if not DATA_RE.match(str(d0.get("date", ""))):
            problemy.append("d0.date nie jest datą RRRR-MM-DD")
        if set((d0.get("prices") or {}).keys()) != set(L + S):
            problemy.append("d0.prices nie ma dokładnie 10 nazw koszyków")
        try:
            if float(d0.get("ndx")) <= 0:
                raise ValueError
            for t, c in (d0.get("prices") or {}).items():
                if float(c) <= 0:
                    raise ValueError
        except (TypeError, ValueError):
            problemy.append("d0.ndx / d0.prices muszą być dodatnimi liczbami")
    if not WERSJA_RE.match(str(sig.get("version", ""))):
        problemy.append(f"version nie ma formatu RRRR-Wn: {sig.get('version')}")
    for pole in ("last_daily", "generated"):
        if sig.get(pole) and not DATA_RE.match(str(sig[pole])):
            problemy.append(f"{pole} nie jest datą RRRR-MM-DD")
    for t, f in (sig.get("fills") or {}).items():
        try:
            if float((f or {}).get("cena")) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            problemy.append(f"zła cena wejścia w fills: {t}")


def porownaj(baza, sig, rutyna, problemy):
    zmienione = {k for k in KLUCZE if baza.get(k) != sig.get(k)}
    for k in POLA_BOTA:
        if k in zmienione:
            problemy.append(f"zmienione pole pisane przez bota: {k} — PRZERWIJ i FALLBACK")
    obce = zmienione - DOZWOLONE[rutyna] - set(POLA_BOTA)
    for k in sorted(obce):
        problemy.append(f"pole {k} zmienione, a rutyna {rutyna} nie ma do niego prawa")
    if rutyna == "sobota":
        if "epics" in zmienione:
            stare, nowe = baza.get("epics") or {}, sig.get("epics") or {}
            if any(k not in nowe or nowe[k] != stare[k] for k in stare):
                problemy.append("epics: wolno tylko DOPISAĆ nową spółkę, nie zmieniać ani usuwać")
        if sig.get("exclude") != [] or sig.get("tactical") != []:
            problemy.append("sobota zapisuje exclude=[] i tactical=[]")
        h0, h1 = baza.get("history") or [], sig.get("history") or []
        if "history" in zmienione:
            if len(h1) != len(h0) + 1 or h1[:-1] != h0:
                problemy.append("history: wolno DOPISAĆ dokładnie jeden wpis na końcu")
            else:
                brak = HISTORY_POLA - set(h1[-1].keys())
                if brak:
                    problemy.append(f"nowy wpis history bez pól: {sorted(brak)}")
                if h1[-1].get("week") != baza.get("version"):
                    problemy.append("nowy wpis history.week ≠ rozliczana version")
            if len(h1) > 26:
                problemy.append("history dłuższe niż 26 wpisów")
        if "version" not in zmienione and sig.get("d0") != baza.get("d0"):
            problemy.append("d0 zmienione bez zmiany version")
        if "version" in zmienione and sig.get("d0") == baza.get("d0"):
            problemy.append("nowa version bez nowego d0")
    return zmienione


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rutyna", choices=("puls", "sobota"), required=True)
    ap.add_argument("--diff", default="HEAD", help="rewizja gita z wersją bazową (domyślnie HEAD)")
    ap.add_argument("--base", help="plik JSON z wersją bazową zamiast rewizji gita")
    ap.add_argument("--plik", default="signals.json")
    args = ap.parse_args()

    with open(args.plik, encoding="utf-8") as f:
        try:
            sig = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ŹLE: {args.plik} nie jest poprawnym JSON: {e}")
            return 1
    problemy = []
    klucze = set(sig.keys())
    if klucze != KLUCZE:
        if klucze - KLUCZE:
            problemy.append(f"OBCE klucze top-level: {sorted(klucze - KLUCZE)} (bot ich nie odrzuca — usuń)")
        if KLUCZE - klucze:
            problemy.append(f"BRAK kluczy top-level: {sorted(KLUCZE - klucze)}")
    spojnosc(sig, problemy)
    baza = wczytaj_baze(args)
    zmienione = porownaj(baza, sig, args.rutyna, problemy)

    print(f"waliduj_signals: rutyna={args.rutyna}, baza={args.base or args.diff}, "
          f"zmienione pola: {sorted(zmienione) or 'brak'}")
    if problemy:
        print("NIE COMMITUJ — problemy:")
        for p in problemy:
            print(" -", p)
        return 1
    print("OK — wolno commitować signals.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
