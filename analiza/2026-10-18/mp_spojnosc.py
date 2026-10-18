"""Spójność wyniku Modelu 3.0 tydzień do tygodnia (W1–W8): korelacja rang wyniku dla nazw obecnych w dwóch kolejnych tabelach,
rotacja składu TOP15/BOTTOM15, zmiany wyniku tej samej spółki vs ruch kursu, format wyniku.
Uruchom: python3 -I mp_spojnosc.py > mp_spojnosc_out.md"""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza")
import pandas as pd, numpy as np
from mp_lib import *
R=ranking(); c=closes()
print('# Spójność wyniku tydzień do tygodnia (tabele TOP15+BOTTOM15, 30 nazw/tydz.)\n')
rows=[]
for a,b in zip(WEEKS[:-1],WEEKS[1:]):
    ra=R[R.week==a].set_index('ticker'); rb=R[R.week==b].set_index('ticker'); com=ra.index.intersection(rb.index)
    # zmiana kursu rel. ^NDX między D0 a D0
    i=c.index.get_loc(pd.Timestamp(D0[a])); j=c.index.get_loc(pd.Timestamp(D0[b])); rel=((c.iloc[j]/c.iloc[i]-1)-(c['^NDX'].iloc[j]/c['^NDX'].iloc[i]-1))*100
    dw=(rb.wynik.reindex(com)-ra.wynik.reindex(com))
    rows.append(dict(para=f'{a[-2:]}→{b[-2:]}',wspolne=len(com),nowe_w_tabeli=30-len(com),spearman_wynik=spearman(ra.wynik.reindex(com),rb.wynik.reindex(com)),
                     sr_abs_zmiana_wyniku=dw.abs().mean(),max_abs_zmiana=dw.abs().max(),corr_zmiana_wyniku_vs_rel_kursu=dw.corr(rel.reindex(com)),
                     zmiana_strony=int((ra.side.reindex(com)!=rb.side.reindex(com)).sum())))
S=pd.DataFrame(rows); print(S.to_markdown(index=False))
print('\nInterpretacja: spearman_wynik ~1 = ranking stabilny; corr(zmiana wyniku, zwrot rel. kursu) > 0 = wynik „goni” kurs (momentum wbudowane w ocenę).')
# obecność w tabelach
cnt=R.groupby('ticker').agg(n=('week','size'),strony=('side',lambda s:'/'.join(sorted(set(s)))),wynik_min=('wynik','min'),wynik_max=('wynik','max'),wynik_sd=('wynik','std'))
print(f"\nUnikalnych spółek w tabelach W1–W8: {len(cnt)} (z ~101); w ≥6 z 8 tygodni: {int((cnt.n>=6).sum())}; tylko raz: {int((cnt.n==1).sum())}")
print('\nSpółki obecne ≥5 razy — rozstęp wyniku:'); print(cnt[cnt.n>=5].sort_values('n',ascending=False).to_markdown())
# zmiana formatu wyniku i p
print('\nFormat wyniku: W1–W7 liczby całkowite; W8 jedno miejsce po przecinku (78,4) — zmiana generatora/metody (dane_b1=tv od 12.10).')
print('Liczba wierszy z gwiazdką/statusem wykluczenia (reguła/filtr poza modelem) w W8:', int((R[R.week=="2026-W8"].status.fillna("").str.contains(r"\*|reguła|filtr|sito|veto",regex=True)).sum()), 'z 30')
# ile nóg koszyka było poza TOP5/BOTTOM5 rankingu (nadpisanie regułą)
K=koszyki()
print('\nNogi koszyka spoza pierwszej piątki rankingu (nadpisania regułami/filtrami):')
for wk in WEEKS:
    r=R[R.week==wk]
    for side,key in (('LONG','long'),('SHORT','short')):
        top5=list(r[(r.side==side)].sort_values('rank').ticker[:5]); kz=K[wk][key]
        poza=[t for t in kz if t not in top5]; pomin=[t for t in top5 if t not in kz]
        if poza or pomin: print(f'  {wk} {side}: w koszyku spoza TOP5: {poza}; z TOP5 pominięte: {pomin}')
