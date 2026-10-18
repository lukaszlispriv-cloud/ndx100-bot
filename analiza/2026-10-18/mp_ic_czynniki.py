"""IC prostych czynników ilościowych (liczonych na D0 z closes_5y.csv) do 5-sesyjnego zwrotu relatywnego vs ^NDX.
(a) tygodnie W1-W7 (D0 z raportów, 5 sesji od D0); (b) cała próba: okna piątek→piątek (ostatnia sesja tygodnia ISO) 2022-2026.
Uruchom: python3 -I mp_ic_czynniki.py > mp_ic_czynniki_out.md"""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza")
import pandas as pd, numpy as np, json
from mp_lib import *
c=closes(); U=universe(c); P=c[U]; ndx=c['^NDX']
lr=np.log(P).diff(); lndx=np.log(ndx).diff()
def factors_at(i):
    """czynniki na sesji o indeksie i (tylko dane <= i)"""
    p=P.iloc[:i+1]; out={}
    px=p.iloc[-1]
    def mom(n,skip=0):
        return (p.iloc[-1-skip]/p.iloc[-1-skip-n]-1) - (ndx.iloc[i-skip]/ndx.iloc[i-skip-n]-1)
    out['mom_1T']=mom(5); out['mom_1M']=mom(21); out['mom_3M']=mom(63); out['mom_6M']=mom(126); out['mom_12M-1M']=mom(231,21)
    out['odwr_1T']=-out['mom_1T']
    ma200=p.iloc[-200:].mean(); out['dist_MA200']=px/ma200-1
    out['vol_20d']=lr.iloc[i-19:i+1].std(ddof=1)
    x=lndx.iloc[i-125:i+1]; y=lr.iloc[i-125:i+1]
    cov=y.sub(y.mean()).mul(x-x.mean(),axis=0).sum(); out['beta_126d']=cov/((x-x.mean())**2).sum()
    out['dist_52wH']=px/p.iloc[-252:].max()-1
    out['mom_6M_abs']=p.iloc[-1]/p.iloc[-127]-1   # kontrola: bez odejmowania indeksu (ranki identyczne) 
    # wymagaj pełnej historii 252 sesji
    ok=p.iloc[-253:].notna().all()
    F=pd.DataFrame(out); F=F[ok]
    return F
FACT=['mom_1T','mom_1M','mom_3M','mom_6M','mom_12M-1M','odwr_1T','dist_MA200','vol_20d','beta_126d','dist_52wH']
def ic_block(i, j):
    F=factors_at(i); r=(P.iloc[j]/P.iloc[i]-1)-(ndx.iloc[j]/ndx.iloc[i]-1); r=r.reindex(F.index)*100
    ics={f:spearman(F[f],r) for f in FACT}
    # spread kwintylowy Q5-Q1 (p.p.) dla interpretacji
    qs={}
    for f in FACT:
        q=pd.qcut(F[f].rank(method='first'),5,labels=False)
        qs[f]=r[q==4].mean()-r[q==0].mean()
    return ics,qs,len(F),F,r
# (a) tygodnie W1-W7 (+W8 brak realizacji)
rowsA=[]; expo={}
for wk in WEEKS:
    i=c.index.get_loc(pd.Timestamp(D0[wk])); j=i+5
    if j<len(c):
        ics,qs,n,F,r=ic_block(i,j); rowsA.append(dict(week=wk,n=n,**ics)); 
    else:
        F=factors_at(i); r=None
    expo[wk]=(F,r)
A=pd.DataFrame(rowsA).set_index('week')
pd.set_option('display.width',250)
print('# (a) IC czynników ilościowych w tygodniach W1–W7 (Spearman w przekroju uniwersum ~90 spółek z pełną historią; zwrot 5 sesji od D0 rel. ^NDX)\n')
print(A.to_markdown())
print('\nśrednia / t (7 tyg.):'); print(pd.DataFrame({f:dict(zip(['mean','t','n'],tstat(A[f]))) for f in FACT}).T.to_markdown())
# (b) cała próba: okna ISO-tygodniowe
wk_last=c.groupby([c.index.isocalendar().year,c.index.isocalendar().week]).apply(lambda g:g.index[-1])
ends=list(wk_last.values); ends=[pd.Timestamp(x) for x in ends]
rowsB=[]; qsB=[]
for a,b in zip(ends[:-1],ends[1:]):
    i=c.index.get_loc(a); j=c.index.get_loc(b)
    if i<253: continue
    if not (3<=j-i<=6): continue
    ics,qs,n,F,r=ic_block(i,j); rowsB.append(dict(d0=a.date(),d5=b.date(),n=n,nses=j-i,ndx=(ndx.iloc[j]/ndx.iloc[i]-1)*100,**ics)); qsB.append(dict(d0=a.date(),**qs))
B=pd.DataFrame(rowsB); Q=pd.DataFrame(qsB)
B.to_csv('mp_ic_czynniki_okna.csv',index=False)
print(f'\n# (b) Cała próba: {len(B)} okien tygodniowych {B.d0.min()} → {B.d5.max()} (D0 = ostatnia sesja tygodnia ISO; n spółek {B.n.min()}–{B.n.max()}; uniwersum = dzisiejszy skład → survivorship bias)\n')
summ=[]
for f in FACT:
    m,t,n=tstat(B[f]); summ.append(dict(czynnik=f,IC_sr=m,IC_sd=B[f].std(),t=t,n=n,udzial_IC_dodatni=(B[f]>0).mean()*100,Q5_Q1_pp=Q[f].mean(),Q5_Q1_t=tstat(Q[f])[1]))
S=pd.DataFrame(summ).set_index('czynnik'); print(S.to_markdown())
print('\n## IC wg lat (D0): średnia IC / t')
B['rok']=pd.to_datetime(B.d0).dt.year
yr=B.groupby('rok').apply(lambda g:pd.Series({f:f"{g[f].mean():+.3f} (t {tstat(g[f])[1]:.1f}, n {len(g)})" for f in FACT}))
print(yr.T.to_markdown())
print('\n## IC warunkowo na reżim tygodnia realizacji (^NDX w oknie): ^NDX ≤ −2% / −2…+2 / ≥ +2%')
B['rez']=pd.cut(B.ndx,[-100,-2,2,100],labels=['NDX≤−2%','−2…+2%','NDX≥+2%'])
rz=B.groupby('rez',observed=True).apply(lambda g:pd.Series({f:f"{g[f].mean():+.3f} (t {tstat(g[f])[1]:.1f}, n {len(g)})" for f in FACT}))
print(rz.T.to_markdown())
print('\n## Ostatnie 26 okien (2026-04 → 2026-10): średnia IC / t')
last=B.tail(26); print(pd.DataFrame({f:dict(zip(['mean','t','n'],tstat(last[f]))) for f in FACT}).T.to_markdown())
# korelacje między czynnikami (średnia korelacja rang w przekroju, ostatnie 52 okna) — czy to różne sygnały?
print('\n## Średnia korelacja rang między czynnikami w przekroju (ostatnie 52 okna)')
cors=[]
for a in ends[-53:-1]:
    i=c.index.get_loc(a); F=factors_at(i); cors.append(F[FACT].rank().corr())
print(pd.concat(cors).groupby(level=0).mean().loc[FACT,FACT].to_markdown())
# (c) ekspozycja wyniku Modelu 3.0 na czynniki: Spearman(wynik, czynnik) wśród 30 nazw TOP15+BOTTOM15 per tydzień; oraz percentyle koszyka
R=ranking(); K=koszyki()
print('\n# (c) Na co „patrzy” wynik Modelu 3.0: Spearman(wynik, czynnik na D0) wśród 30 nazw TOP15+BOTTOM15, per tydzień (W1–W8)')
rowsC=[]
for wk in WEEKS:
    F,_=expo[wk]; r=R[R.week==wk].set_index('ticker')
    Fw=F.reindex(r.index); rowsC.append(dict(week=wk,n=Fw.mom_6M.notna().sum(),**{f:spearman(r.wynik,Fw[f]) for f in FACT if f!='odwr_1T'}))
C=pd.DataFrame(rowsC).set_index('week'); print(C.to_markdown()); print('\nśrednia / t (8 tyg.):'); print(pd.DataFrame({f:dict(zip(['mean','t','n'],tstat(C[f]))) for f in C.columns if f!='n'}).T.to_markdown())
print('\n## Percentyl (w uniwersum, 0–100) czynników dla nóg koszyka: średnia LONG vs SHORT per tydzień')
rowsD=[]
for wk in WEEKS:
    F,_=expo[wk]; pct=F.rank(pct=True)*100
    L=pct.reindex(K[wk]['long']).mean(); S_=pct.reindex(K[wk]['short']).mean()
    rowsD.append(dict(week=wk,**{f'{f}_L':L[f] for f in ['mom_1T','mom_1M','mom_6M','mom_12M-1M','dist_MA200','vol_20d','beta_126d']},**{f'{f}_S':S_[f] for f in ['mom_1T','mom_1M','mom_6M','mom_12M-1M','dist_MA200','vol_20d','beta_126d']}))
D=pd.DataFrame(rowsD).set_index('week'); print(D.to_markdown())
# (d) „czysty” koszyk mom_6M (TOP5/BOTTOM5 wg percentyla) w oknach W1-W7 vs Model
print('\n# (d) Koszyk 5/5 z samego czynnika (TOP5/BOTTOM5 w uniwersum) w oknach W1–W7, spread p.p. (5 sesji od D0) — kontrola, czy czynnik „wygrałby” te konkretne tygodnie')
rowsE=[]
for wk in WEEKS[:-1]:
    F,r=expo[wk]; d={'week':wk}
    for f in ['mom_1T','mom_1M','mom_3M','mom_6M','mom_12M-1M','dist_MA200','vol_20d','beta_126d']:
        s=F[f].dropna().sort_values(); d[f]=r[s.index[-5:]].mean()-r[s.index[:5]].mean()
    s=F['mom_1T'].dropna().sort_values(); d['odwr_1T']=r[s.index[:5]].mean()-r[s.index[-5:]].mean()
    rowsE.append(d)
E=pd.DataFrame(rowsE).set_index('week'); print(E.to_markdown()); print('\nsuma / średnia / t:'); print(pd.DataFrame({f:dict(suma=E[f].sum(),**dict(zip(['mean','t','n'],tstat(E[f])))) for f in E.columns}).T.to_markdown())
json.dump({'okna':len(B),'summary':S.reset_index().to_dict('records')},open('mp_ic_czynniki_summary.json','w'),indent=1,default=str)
