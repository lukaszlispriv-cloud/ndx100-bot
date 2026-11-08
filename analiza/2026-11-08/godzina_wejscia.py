#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""godzina_wejscia.py — pomysł nr 4 z rozmowy 08.11.2026: czy wejścia bota (bieg 13:45 UTC,
kwadrans po otwarciu NYSE) są systematycznie gorsze od kursu zamknięcia tego dnia?
Dane: wszystkie wpisy `fills` z historii gita signals.json (cena wejścia u brokera, data,
kierunek) + zamknięcia z closes_5y.csv (argv[1]). Miara: koszt = znak × (cena wejścia /
zamknięcie dnia − 1); >0 = wejście gorsze niż zamknięcie (BUY drożej / SELL taniej).
Dodatkowo vs poprzednie zamknięcie (koszt opóźnienia D0 → wejście). Bez liczb z rachunku
(ceny instrumentów to nie stan rachunku). Wynik: markdown na stdout."""
import subprocess, json, csv, sys, math, datetime, statistics as st
S = sys.argv[1] if len(sys.argv) > 1 else 'closes_5y.csv'
shas = subprocess.check_output(['git', 'log', '--format=%H', '--', 'signals.json']).decode().split()
fills = {}
for h in shas:
    try: s = json.loads(subprocess.check_output(['git', 'show', f'{h}:signals.json'], stderr=subprocess.DEVNULL))
    except Exception: continue
    for t, v in (s.get('fills') or {}).items():
        if isinstance(v, dict) and 'cena' in v and 'data' in v and v.get('kierunek') in ('BUY', 'SELL'):
            fills.setdefault((t, v['data'], v['kierunek'], round(float(v['cena']), 4)), 1)
rows = list(csv.DictReader(open(S))); idx = {r['date']: i for i, r in enumerate(rows)}
out = []
for (t, d, k, c) in sorted(fills):
    i = idx.get(d)
    if not i or not rows[i].get(t) or not rows[i-1].get(t): continue
    cl, pv = float(rows[i][t]), float(rows[i-1][t]); sgn = 1 if k == 'BUY' else -1
    out.append(dict(d=d, t=t, k=k, c=c, pv=pv, cl=cl, vs_close=sgn*(c/cl-1)*100, vs_prev=sgn*(c/pv-1)*100,
                    mon=datetime.date.fromisoformat(d).weekday() == 0))
def summ(x):
    if len(x) < 3: return f'n = {len(x)}'
    m = st.mean(x); sd = st.stdev(x)
    return f'śr {m:+.2f} % · med {st.median(x):+.2f} % · σ {sd:.2f} · t {m/(sd/math.sqrt(len(x))):.2f} · n = {len(x)} · gorsze niż odniesienie: {sum(v > 0 for v in x)}/{len(x)}'
print('# Godzina wejścia — wpisy fills (historia gita) vs zamknięcia (08.11.2026)\n')
print(f'Wpisy fills z kursami: {len(out)} (unikalne ticker/data/kierunek/cena; wyrównania wielkości tego samego dnia liczone osobno). Zakres: {min(r["d"] for r in out)} … {max(r["d"] for r in out)}.\n')
odd = [r for r in out if abs(r['vs_close']) > 8]
print('Obserwacje odstające (|koszt| > 8 %, prawdopodobnie korekta kursu/split w źródle — wyłączone z wariantu „bez odstających”): ' + (', '.join(f"{r['t']} {r['d']} ({r['vs_close']:+.1f} %)" for r in odd) or 'brak') + '\n')
clean = [r for r in out if abs(r['vs_close']) <= 8]
print('| próba | koszt wejścia vs zamknięcie dnia (>0 = gorzej) | vs poprzednie zamknięcie (opóźnienie D0 → wejście) |\n|---|---|---|')
for name, sel in [('wszystkie', out), ('bez odstających', clean), ('poniedziałki (rotacja), bez odst.', [r for r in clean if r['mon']]), ('pozostałe dni (wyrównania/dopełnienia), bez odst.', [r for r in clean if not r['mon']]), ('BUY, bez odst.', [r for r in clean if r['k'] == 'BUY']), ('SELL, bez odst.', [r for r in clean if r['k'] == 'SELL'])]:
    print(f'| {name} | {summ([r["vs_close"] for r in sel])} | {summ([r["vs_prev"] for r in sel])} |')
m = st.mean([r['vs_close'] for r in clean])
print(f'\nPrzełożenie na koszyk: {m:+.2f} % na nogę × gross 0,8 kapitału ≈ {m*0.8:+.2f} % kapitału na rotację, czyli ok. {m*2:+.2f} pp spreadu (gross 2) — rząd kosztów transakcyjnych przyjętych w analizie 18.10 (0,27 pp/tydz.), nie rząd luki wykonania z W10 (ok. 2 pp kapitału, stopy + wyłącznik P2).')
print('\nUwaga: zamknięcie dnia nie jest ceną osiągalną (bot nie handluje na zamknięciu); test mierzy tylko, czy pierwszy kwadrans sesji jest systematycznie drogi. Kurs otwarcia nie jest dostępny w closes_5y.csv.')
