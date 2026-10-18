"""Dodatek: (1) tygodniowy IC modelu vs tygodniowy IC czynników; (2) zwrot grup koszyka ponad średnią uniwersum (baza równych wag);
(3) IC modelu na resztach po becie i momentum 6M (czy jest cokolwiek poza czynnikami); (4) ile tygodni trzeba, by wykryć IC.
Uruchom: python3 -I mp_dodatek.py > mp_dodatek_out.md"""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza")
import pandas as pd, numpy as np
from mp_lib import *
exec(open('mp_ic_czynniki.py').read().split('# (a) tygodnie')[0].split('from mp_lib import *')[1])
W=pd.read_csv('mp_model_tygodnie.csv'); A=pd.read_csv('mp_model_nazwy.csv'); R=ranking(); K=koszyki()
print('# (1) Tygodniowy IC Modelu 3.0 (30 nazw) a tygodniowy IC czynników w uniwersum (W1–W7, n=7 — tylko ilustracja)\n')
rows=[]
for wk in WEEKS[:-1]:
    i=c.index.get_loc(pd.Timestamp(D0[wk])); ics,qs,n,F,r=ic_block(i,i+5)
    rows.append(dict(week=wk,ic_model=float(W[W.week==wk].ic30.iloc[0]),**{k:v for k,v in ics.items() if k in ['mom_6M','mom_12M-1M','beta_126d','vol_20d','mom_1T']},ndx5=(ndx.iloc[i+5]/ndx.iloc[i]-1)*100,sox_ndx=((c['^SOX'].iloc[i+5]/c['^SOX'].iloc[i])-(ndx.iloc[i+5]/ndx.iloc[i]))*100))
T=pd.DataFrame(rows).set_index('week'); print(T.to_markdown())
print('\nKorelacja Pearsona ic_model z:', ', '.join(f"{k}: {T.ic_model.corr(T[k]):.2f}" for k in T.columns if k!='ic_model'))
print('\n# (2) Zwrot pozycji grup ponad średnią uniwersum równych wag (baza „losowa nazwa z tego samego uniwersum”), p.p., 5 sesji od D0\n')
rows=[]
for wk in WEEKS[:-1]:
    rel5,_=fwd_rel(c,D0[wk],5); u=rel5.reindex(U).dropna(); a=A[A.week==wk]
    d=dict(week=wk,uni_sr=u.mean(),uni_med=u.median(),udzial_uni_pow_NDX=(u>0).mean()*100)
    for s,sg in (('LONG',1),('SHORT',-1)):
        for gname,mask in (('koszyk5',a.basket),('rank6-15',~a.basket)):
            g=a[(a.side==s)&mask]; d[f'{s[0]}_{gname}']=sg*(g.rel5.mean()-u.mean())
    rows.append(d)
G=pd.DataFrame(rows).set_index('week'); print(G.to_markdown())
for col in ['L_koszyk5','L_rank6-15','S_koszyk5','S_rank6-15']:
    m,t,n=tstat(G[col]); print(f'{col}: śr. nadwyżka nad uniwersum {m:+.2f} p.p./tydz., t={t:.2f} (n=7)')
print(f"\nUwaga: w W1–W5 tylko {G.udzial_uni_pow_NDX.iloc[:5].mean():.0f}% nazw uniwersum biło kapitalizacyjny ^NDX (lider = mega-capy), w W6–W7 {G.udzial_uni_pow_NDX.iloc[5:].mean():.0f}% — hit rate strony LONG liczony vs ^NDX ma bazę daleką od 50%.")
print('\n# (3) IC Modelu 3.0 na resztach: rel5 po usunięciu (OLS w przekroju uniwersum) beta_126d i mom_6M — czy wynik niesie coś poza czynnikami\n')
rows=[]
for wk in WEEKS[:-1]:
    i=c.index.get_loc(pd.Timestamp(D0[wk])); F=factors_at(i); rel5,_=fwd_rel(c,D0[wk],5); y=rel5.reindex(F.index)
    X=np.column_stack([np.ones(len(F)),F.beta_126d.values,F.mom_6M.values]); b,*_=np.linalg.lstsq(X,y.values,rcond=None); res=pd.Series(y.values-X@b,index=F.index)
    r=R[R.week==wk].set_index('ticker'); rows.append(dict(week=wk,ic_surowy=spearman(r.wynik,y.reindex(r.index)),ic_reszty=spearman(r.wynik,res.reindex(r.index)),R2_czynnikow=1-res.var()/y.var(),b_beta=b[1],b_mom6M=b[2]))
Z=pd.DataFrame(rows).set_index('week'); print(Z.to_markdown())
for col in ['ic_surowy','ic_reszty']:
    m,t,n=tstat(Z[col]); print(f'{col}: śr {m:+.3f}, t={t:.2f}')
print('\n# (4) Moc testu: tygodni potrzebnych, by średni IC był istotny (t=2), przy sd IC z próby 2022–2026\n')
B=pd.read_csv('mp_ic_czynniki_okna.csv')
for f in ['mom_6M','mom_12M-1M','vol_20d','beta_126d']:
    sd=B[f].std()
    print(f'{f}: sd IC = {sd:.2f}; dla IC 0,02 → {int(np.ceil((2*sd/0.02)**2))} tyg., 0,03 → {int(np.ceil((2*sd/0.03)**2))}, 0,05 → {int(np.ceil((2*sd/0.05)**2))}, 0,10 → {int(np.ceil((2*sd/0.10)**2))}')
sdm=W.ic30.std(); print(f'Model 3.0: sd tygodniowego IC30 (n=7) = {sdm:.2f}; dla IC 0,05 → {int(np.ceil((2*sdm/0.05)**2))} tyg., 0,10 → {int(np.ceil((2*sdm/0.10)**2))} tyg.')
