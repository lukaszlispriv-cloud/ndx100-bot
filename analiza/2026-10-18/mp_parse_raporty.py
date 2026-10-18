"""Parsuje tabele TOP15 (LONG) i BOTTOM15 (SHORT) z reports/raport-2026-W1..W8.html.
Wyjście: mp_ranking.csv (week, side, rank, ticker, wynik, p, hl, status) + mp_koszyki.json (koszyki W1-W8 i D0).
Uruchom: python3 -I mp_parse_raporty.py
"""
import re, json, html, csv, sys
REPO='/home/user/ndx100-bot'
OUT='/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza'
D0={'2026-W1':'2026-08-26','2026-W2':'2026-08-28','2026-W3':'2026-09-04','2026-W4':'2026-09-11',
    '2026-W5':'2026-09-28','2026-W6':'2026-10-02','2026-W7':'2026-10-09','2026-W8':'2026-10-16'}
def strip(s): return html.unescape(re.sub(r'<[^>]+>','',s)).strip()
def table_after(h, marker):
    i=h.find(marker); assert i>0, marker
    j=h.find('<table',i); k=h.find('</table>',j)
    return h[j:k]
rows=[]; koszyki={}
for w in range(1,9):
    wk=f'2026-W{w}'
    h=open(f'{REPO}/reports/raport-{wk}.html',encoding='utf-8').read()
    for side,marker in (('LONG','TOP15 (strona LONG)'),('SHORT','BOTTOM15 (strona SHORT)')):
        t=table_after(h,marker)
        trs=re.findall(r'<tr([^>]*)>(.*?)</tr>',t,flags=re.S)
        for attrs,body in trs:
            tds=re.findall(r'<td[^>]*>(.*?)</td>',body,flags=re.S)
            if len(tds)<4: continue
            rank=strip(tds[0]); tick=strip(tds[1]); wyn=strip(tds[2]); p=strip(tds[3])
            if not rank.isdigit(): continue
            w2=wyn.replace(',','.').replace('−','-')
            if '–' in w2 or ('-' in w2[1:]):
                a,b=re.split(r'[–-]',w2.strip(),maxsplit=1); wyn_f=(float(a)+float(b))/2; print('ZAKRES',wk,side,tick,wyn,file=sys.stderr)
            else: wyn_f=float(w2)
            pm=re.match(r'(\d+)\s*%',p); p_f=int(pm.group(1)) if pm else None
            status=strip(tds[7]) if len(tds)>=8 else ''
            rows.append(dict(week=wk,side=side,rank=int(rank),ticker=tick,wynik=wyn_f,p=p_f,p_raw=p,
                             hl=int('hl' in attrs),status=status[:80]))
    # koszyk: TOP5 — LONG / BOTTOM5 — SHORT tables, first column ticker-ish
    kz={}
    for side,marker in (('long','TOP5 — LONG'),('short','BOTTOM5 — SHORT')):
        t=table_after(h,marker)
        trs=re.findall(r'<tr[^>]*>(.*?)</tr>',t,flags=re.S)
        ticks=[]
        for body in trs:
            tds=re.findall(r'<td[^>]*>(.*?)</td>',body,flags=re.S)
            if not tds: continue
            c=[strip(x) for x in tds[:3]]
            cand=[x for x in c if re.fullmatch(r'[A-Z]{1,5}',x)]
            if cand: ticks.append(cand[0])
        kz[side]=ticks[:5]
    koszyki[wk]=dict(d0=D0[wk],**kz)
with open(f'{OUT}/mp_ranking.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
json.dump(koszyki,open(f'{OUT}/mp_koszyki.json','w'),indent=1)
from collections import Counter
print(Counter((r['week'],r['side']) for r in rows))
for wk,k in koszyki.items(): print(wk,k)
print('p values:',sorted(Counter(r['p'] for r in rows).items(), key=lambda x:(x[0] is None, x[0])))
