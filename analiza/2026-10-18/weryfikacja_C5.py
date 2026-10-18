"""Weryfikacja C5: moc predykcyjna Wyniku Modelu 3.0 (TOP15/BOTTOM15, W1-W7) — próba OBALENIA.
T1 okna „jak rachunek" (D+1 -> rotacja), T2 IC na 10 nogach, T3 kalibracja p bez W7 / leave-one-week-out,
T4 IC na resztach (ranking w kwintylach bety / momentum, rangowa OLS, model vs proxy czynnikowe),
T5 moc testu i IC, którego nie można wykluczyć, T6 „~75% wyjaśnione" — pomiar R².
Uruchom: python3 -I weryfikacja_C5.py > weryfikacja_C5_out.md"""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza")
import pandas as pd, numpy as np, json
from mp_lib import *
class _T:  # kwantyle t dla 6 df (brak scipy): 0.975→2.4469, 0.95→1.9432, 0.80→0.9057
    _q={(0.975,6):2.4469,(0.95,6):1.9432,(0.80,6):0.9057}
    def ppf(self,q,df): return self._q[(q,df)]
class _ST:
    t=_T()
    @staticmethod
    def binomtest(k,n):
        class _R:
            def proportion_ci(self,method='wilson'):
                z=1.96; ph=k/n; den=1+z*z/n; cen=(ph+z*z/(2*n))/den; half=z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/den
                return max(0,cen-half),min(1,cen+half)
        return _R()
st=_ST()
OUT='/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza/weryfikacja_C5'
c=closes(); U=universe(c); P=c[U]; ndx=c['^NDX']; lr=np.log(P).diff(); lndx=np.log(ndx).diff()
R=ranking(); K=koszyki(); WK=WEEKS[:-1]
res={}
def factors_at(i):
    p=P.iloc[:i+1]; out={}
    def mom(n,skip=0): return (p.iloc[-1-skip]/p.iloc[-1-skip-n]-1)-(ndx.iloc[i-skip]/ndx.iloc[i-skip-n]-1)
    out['mom_6M']=mom(126); out['mom_12M-1M']=mom(231,21); out['mom_1M']=mom(21)
    out['vol_20d']=lr.iloc[i-19:i+1].std(ddof=1)
    x=lndx.iloc[i-125:i+1]; y=lr.iloc[i-125:i+1]
    out['beta_126d']=y.sub(y.mean()).mul(x-x.mean(),axis=0).sum()/((x-x.mean())**2).sum()
    F=pd.DataFrame(out); return F[p.iloc[-253:].notna().all()]
def rel(d_in,d_out,div=False):
    i=c.index.get_loc(pd.Timestamp(d_in)); j=c.index.get_loc(pd.Timestamp(d_out))
    p0=c.iloc[i]; p1=c.iloc[j].copy()
    if div:
        for (t,dt),amt in DIV.items():
            if t in p1.index and c.index[i]<pd.Timestamp(dt)<=c.index[j]: p1[t]+=amt
    r=p1/p0-1; return (r-r['^NDX'])*100
def nxt(d,k=1):
    i=c.index.get_loc(pd.Timestamp(d)); return str(c.index[min(i+k,len(c)-1)].date())
# kalendarz „jak rachunek": wejście = pierwsza sesja po D0 (bieg 13:45 UTC ≈ zamknięcie tej sesji), wyjście = sesja wejścia następnego koszyka
# (W5 wg fills 2026-09-29, W6 wg fills 2026-10-06, W7 wg fills 2026-10-12; W7 kończy się na ostatnich danych 2026-10-16 — okno otwarte)
ENTRY={'2026-W1':'2026-08-27','2026-W2':'2026-08-31','2026-W3':'2026-09-08','2026-W4':'2026-09-14','2026-W5':'2026-09-29','2026-W6':'2026-10-06','2026-W7':'2026-10-12'}
EXIT ={'2026-W1':'2026-08-31','2026-W2':'2026-09-08','2026-W3':'2026-09-14','2026-W4':'2026-09-29','2026-W5':'2026-10-06','2026-W6':'2026-10-12','2026-W7':'2026-10-16'}
WINDOWS={'D0→D+5 (faza 1)':lambda w:(D0[w],nxt(D0[w],5)),
         'D+1→D+6 (5 sesji od wejścia)':lambda w:(nxt(D0[w],1),nxt(D0[w],6)),
         'rachunek: wejście→rotacja':lambda w:(ENTRY[w],EXIT[w]),
         'history: D0→DEND':lambda w:(D0[w],DEND[w])}
pd.set_option('display.width',250)
def week_table(win, div=False):
    rows=[]; A=[]
    for w in WK:
        a,b=WINDOWS[win](w); r=rel(a,b,div); g=R[R.week==w].copy(); g['rel']=g.ticker.map(r)
        g['sgn']=np.where(g.side=='LONG',1,-1); g['pos']=g.sgn*g.rel
        g['basket']=[(t in K[w]['long']) if s=='LONG' else (t in K[w]['short']) for t,s in zip(g.ticker,g.side)]
        g['hit']=(g.pos>0).astype(int)
        u=r.reindex(U).dropna(); g['pos_med']=g.sgn*(g.rel-u.median()); g['hit_med']=(g.pos_med>0).astype(int)
        b10=g[g.basket]
        rows.append(dict(week=w,od=a,do=b,nses=c.index.get_loc(pd.Timestamp(b))-c.index.get_loc(pd.Timestamp(a)),
            ic30=spearman(g.wynik,g.rel),ic10=spearman(b10.wynik,b10.rel),
            icL15=spearman(g[g.side=='LONG'].wynik,g[g.side=='LONG'].rel),icS15=spearman(g[g.side=='SHORT'].wynik,g[g.side=='SHORT'].rel),
            icL5=spearman(b10[b10.side=='LONG'].wynik,b10[b10.side=='LONG'].rel),icS5=spearman(b10[b10.side=='SHORT'].wynik,b10[b10.side=='SHORT'].rel),
            spread10=b10[b10.side=='LONG'].rel.mean()-b10[b10.side=='SHORT'].rel.mean(),
            spread_top5bot5=g[(g.side=='LONG')&(g['rank']<=5)].rel.mean()-g[(g.side=='SHORT')&(g['rank']<=5)].rel.mean(),
            hit10=int(b10.hit.sum()),hit30=int(g.hit.sum()),hit30_med=int(g.hit_med.sum()),udzial_uni_pow_ndx=(u>0).mean()*100))
        g['window']=win; A.append(g)
    return pd.DataFrame(rows), pd.concat(A)
print('# Weryfikacja C5 — wyniki skryptu weryfikacja_C5.py\n')
print('## T1. IC Modelu 3.0 w czterech definicjach okna (Spearman Wynik vs zwrot rel. ^NDX; 30 nazw TOP15+BOTTOM15; 10 nóg koszyka)\n')
ALL={}; T1={}
for win in WINDOWS:
    W,A=week_table(win, div=(win.startswith('rachunek') or win.startswith('history'))); ALL[win]=A
    print(f'### {win}\n'); print(W.round(2).to_markdown(index=False))
    s={}
    for col in ['ic30','ic10','icL15','icS15','icL5','icS5','spread10','spread_top5bot5']:
        m,t,n=tstat(W[col]); s[col]=dict(mean=m,t=t,n=n,pos=int((W[col]>0).sum()))
    print('\n'+', '.join(f"{k}: śr {v['mean']:+.3f} (t {v['t']:.2f}, dodatnich {v['pos']}/{v['n']})" for k,v in s.items()))
    # bootstrap tygodni: P(średni IC30 > 0)
    rng=np.random.default_rng(1); bs=np.array([W.ic30.sample(7,replace=True,random_state=int(rng.integers(1e9))).mean() for _ in range(5000)])
    s['boot_ic30_p_pos']=float((bs>0).mean()); s['boot_ic30_ci']=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]
    print(f"bootstrap tygodni (5000): P(śr. IC30 > 0) = {s['boot_ic30_p_pos']:.2f}; 95% {s['boot_ic30_ci'][0]:+.2f}…{s['boot_ic30_ci'][1]:+.2f}")
    s['hit10']=int(W.hit10.sum()); s['hit30']=int(W.hit30.sum()); s['hit30_med']=int(W.hit30_med.sum())
    print(f"trafienia: 10 nóg {s['hit10']}/70 = {s['hit10']/70*100:.1f}%; 30 nazw vs ^NDX {s['hit30']}/210 = {s['hit30']/210*100:.1f}%; 30 nazw vs mediana uniwersum {s['hit30_med']}/210 = {s['hit30_med']/210*100:.1f}%\n")
    T1[win]=s
    W.to_csv(f"{OUT}_T1_{win.split(' ')[0].replace(':','').replace('→','_')}.csv",index=False)
res['T1']=T1
# pooled IC z klastrowym bootstrapem po tygodniach
print('### Pooled Spearman (210 nazwo-tygodni, zwrot demeaned per tydzień) z bootstrapem klastrowym po tygodniach\n')
pool={}
for win,A in ALL.items():
    A=A.copy(); A['rel_dm']=A.rel-A.groupby('week').rel.transform('mean'); obs=spearman(A.wynik,A.rel_dm)
    rng=np.random.default_rng(2); bs=[]
    for _ in range(3000):
        wk=rng.choice(WK,7,replace=True); d=pd.concat([A[A.week==w] for w in wk]); bs.append(spearman(d.wynik,d.rel_dm))
    bs=np.array(bs); pool[win]=dict(pooled=obs,ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],se_naive=1/np.sqrt(210))
    print(f"{win}: pooled IC {obs:+.3f}; 95% klastrowy {pool[win]['ci'][0]:+.3f}…{pool[win]['ci'][1]:+.3f} (naiwne se iid 1/√210 = {1/np.sqrt(210):.3f} → ±{1.96/np.sqrt(210):.3f})")
res['pooled']=pool
# ---------------- T3 kalibracja p
print('\n## T3. Kalibracja p — pełna próba, bez W7, bez W6+W7, leave-one-week-out; dwa okna; dwie bazy (vs ^NDX, vs mediana uniwersum)\n')
def calib(A, hitcol='hit'):
    out={}
    for nm,mask in (('p>55',A.p_win>55),('p≤55',A.p_win<=55),('p≥61',A.p_win>=61),('p≥60',A.p_win>=60),('p≤58',A.p_win<=58)):
        d=A[mask]; k=int(d[hitcol].sum()); n=len(d)
        if n==0: out[nm]=dict(k=0,n=0); continue
        lo,hi=st.binomtest(k,n).proportion_ci(method='wilson'); out[nm]=dict(k=k,n=n,pct=k/n*100,wilson=[lo*100,hi*100],p_decl=d.p_win.mean(),mean_pp=d.pos.mean())
    sp=spearman(A.p_win,A[hitcol]); out['spearman_p_hit']=sp
    out['spearman_p_pos']=spearman(A.p_win,A.pos)
    return out
def fmt(o,nm): v=o[nm]; return f"{v['k']}/{v['n']}={v['pct']:.1f}% [{v['wilson'][0]:.0f}–{v['wilson'][1]:.0f}] dekl. {v['p_decl']:.1f}" if v['n'] else '—'
T3={}
for win in ['D0→D+5 (faza 1)','rachunek: wejście→rotacja']:
    A=ALL[win]
    for hitcol,lab in (('hit','vs ^NDX'),('hit_med','vs mediana uniwersum')):
        print(f'### okno {win}, trafienie {lab}\n'); print('| podzbiór | n | p>55 | p≤55 | p≥61 | p≤58 | Spearman(p, trafienie) | Spearman(p, zwrot pozycji) |'); print('|---|---|---|---|---|---|---|---|')
        subsets={'W1–W7':WK,'bez W7':WK[:-1],'bez W6+W7':WK[:-2],'bez W1 (2 sesje)':WK[1:]}
        for w in WK: subsets[f'bez {w[-2:]}']=[x for x in WK if x!=w]
        for nm,ws in subsets.items():
            d=A[A.week.isin(ws)]; o=calib(d,hitcol); T3[f'{win}|{lab}|{nm}']=o
            print(f"| {nm} | {len(d)} | {fmt(o,'p>55')} | {fmt(o,'p≤55')} | {fmt(o,'p≥61')} | {fmt(o,'p≤58')} | {o['spearman_p_hit']:+.3f} | {o['spearman_p_pos']:+.3f} |")
        print()
# kalibracja per tydzień: Spearman(p, zwrot pozycji) w obrębie tygodnia — czy odwrotna kalibracja to jeden tydzień?
print('### Spearman(p_win, zwrot pozycji) w obrębie tygodnia (30 nazw) — okno D0→D+5 i rachunek\n')
rows=[]
for w in WK:
    d1=ALL['D0→D+5 (faza 1)']; d1=d1[d1.week==w]; d2=ALL['rachunek: wejście→rotacja']; d2=d2[d2.week==w]
    rows.append(dict(week=w,sp_D0D5=spearman(d1.p_win,d1.pos),sp_rachunek=spearman(d2.p_win,d2.pos),hit_p55_D0D5=f"{int(d1[d1.p_win>55].hit.sum())}/{(d1.p_win>55).sum()}",hit_p55_rach=f"{int(d2[d2.p_win>55].hit.sum())}/{(d2.p_win>55).sum()}"))
Cw=pd.DataFrame(rows); print(Cw.round(3).to_markdown(index=False))
for col in ['sp_D0D5','sp_rachunek']:
    m,t,n=tstat(Cw[col]); print(f"{col}: śr {m:+.3f}, t {t:.2f}, dodatnich {(Cw[col]>0).sum()}/7; bez W7: śr {Cw[col][:-1].mean():+.3f}, t {tstat(Cw[col][:-1])[1]:.2f}")
res['T3_perweek']=Cw.to_dict('records'); res['T3']={k:{kk:(vv if not isinstance(vv,dict) else vv) for kk,vv in v.items()} for k,v in T3.items()}
# kalibracja na 70 nogach (jak audyt-regul: p≥61 → 37,5%)
A=ALL['D0→D+5 (faza 1)']; b=A[A.basket]; o=calib(b); print(f"\n70 nóg koszyka, D0→D+5: p≥61 {fmt(o,'p≥61')}; p≤58 {fmt(o,'p≤58')}; Spearman(p, zwrot) {o['spearman_p_pos']:+.3f}")
A=ALL['rachunek: wejście→rotacja']; b=A[A.basket]; o2=calib(b); print(f"70 nóg koszyka, rachunek: p≥61 {fmt(o2,'p≥61')}; p≤58 {fmt(o2,'p≤58')}; Spearman(p, zwrot) {o2['spearman_p_pos']:+.3f}")
b7=A[A.basket&(A.week!='2026-W7')]; o3=calib(b7); print(f"70 nóg, rachunek, bez W7: p≥61 {fmt(o3,'p≥61')}; p≤58 {fmt(o3,'p≤58')}; Spearman(p, zwrot) {o3['spearman_p_pos']:+.3f}")
Ah=ALL['history: D0→DEND']; bh=Ah[Ah.basket]; oh=calib(bh); print(f"70 nóg koszyka, history D0→DEND (jak audyt-regul): p≥61 {fmt(oh,'p≥61')}; p≤58 {fmt(oh,'p≤58')}; Spearman(p, zwrot) {oh['spearman_p_pos']:+.3f}")
res['T3_legs']={'D0D5':o,'rachunek':o2,'rachunek_bezW7':o3,'history':oh}
# klastrowy bootstrap (po tygodniach) dla Spearman(p_win, trafienie) i Spearman(p_win, zwrot pozycji) — pełna próba, 30 nazw
print('\nKlastrowy bootstrap (tygodnie, 3000) Spearman(p_win, trafienie) / (p_win, zwrot pozycji), 210 nazwo-tygodni:')
rng=np.random.default_rng(5); cb={}
for win in ['D0→D+5 (faza 1)','rachunek: wejście→rotacja']:
    A=ALL[win]; b1=[]; b2=[]
    for _ in range(3000):
        wk=rng.choice(WK,7,replace=True); d=pd.concat([A[A.week==w] for w in wk]); b1.append(spearman(d.p_win,d.hit)); b2.append(spearman(d.p_win,d.pos))
    cb[win]=dict(sp_hit=spearman(A.p_win,A.hit),ci_hit=[float(np.percentile(b1,2.5)),float(np.percentile(b1,97.5))],sp_pos=spearman(A.p_win,A.pos),ci_pos=[float(np.percentile(b2,2.5)),float(np.percentile(b2,97.5))],p_pos_lt0=float((np.array(b2)<0).mean()))
    print(f"  {win}: Spearman(p, trafienie) {cb[win]['sp_hit']:+.3f} [{cb[win]['ci_hit'][0]:+.3f}…{cb[win]['ci_hit'][1]:+.3f}]; Spearman(p, zwrot) {cb[win]['sp_pos']:+.3f} [{cb[win]['ci_pos'][0]:+.3f}…{cb[win]['ci_pos'][1]:+.3f}], P(<0) {cb[win]['p_pos_lt0']:.2f}")
res['T3_cluster']=cb
print('\nWilson 95% dla trafień 10 nóg (70): '+'; '.join(f"{win}: {T1[win]['hit10']}/70 = {T1[win]['hit10']/70*100:.1f}% [{st.binomtest(T1[win]['hit10'],70).proportion_ci()[0]*100:.0f}–{st.binomtest(T1[win]['hit10'],70).proportion_ci()[1]*100:.0f}]" for win in WINDOWS))
# ---------------- T4 IC na resztach
print('\n## T4. IC Modelu po usunięciu czynników — ranking w obrębie kwintyli bety / momentum, rangowa OLS, model vs proxy czynnikowe\n')
def within_q_rank(r,F,fac,q=5):
    qq=pd.qcut(F[fac].rank(method='first'),q,labels=False); rr=r.reindex(F.index)
    return rr.groupby(qq).rank(pct=True)
rows=[]; proxy_rows=[]
for win in ['D0→D+5 (faza 1)','rachunek: wejście→rotacja']:
    for w in WK:
        a,b_=WINDOWS[win](w); r=rel(a,b_,win.startswith('rachunek')); i=c.index.get_loc(pd.Timestamp(D0[w])); F=factors_at(i)
        g=R[R.week==w].set_index('ticker'); idx=[t for t in g.index if t in F.index]
        d=dict(window=win,week=w,n=len(idx),ic_surowy=spearman(g.wynik,r.reindex(g.index)))
        for fac in ['beta_126d','mom_6M','mom_12M-1M','vol_20d']:
            d[f'ic_wQ_{fac}']=spearman(g.wynik.reindex(idx),within_q_rank(r,F,fac).reindex(idx))
        # podwójny sort: tercyle bety × tercyle mom 6M
        qb=pd.qcut(F.beta_126d.rank(method='first'),3,labels=False); qm=pd.qcut(F.mom_6M.rank(method='first'),3,labels=False)
        rr=r.reindex(F.index); d['ic_wQ_beta×mom6M']=spearman(g.wynik.reindex(idx),rr.groupby([qb,qm]).rank(pct=True).reindex(idx))
        # rangowa OLS w uniwersum: rank(rel) ~ rank(beta)+rank(mom6M)+rank(mom12-1)
        ok=rr.notna().values; Fo=F[ok]; rro=rr[ok]
        X=np.column_stack([np.ones(len(Fo))]+[Fo[f].rank().values for f in ['beta_126d','mom_6M','mom_12M-1M']]); y=rro.rank().values
        bb,*_=np.linalg.lstsq(X,y,rcond=None); resid=pd.Series(y-X@bb,index=Fo.index); d['ic_reszty_rangOLS3']=spearman(g.wynik.reindex(idx),resid.reindex(idx))
        d['R2_rangOLS3_uniwersum']=1-resid.var()/np.var(y); d['n_uni_ok']=int(ok.sum())
        # model vs proxy czynnikowe wśród tych samych 30 nazw: proxy = średnia rang (mom6M, mom12-1, beta)
        Fw=F.reindex(idx); proxy=Fw[['mom_6M','mom_12M-1M','beta_126d']].rank().mean(axis=1); proxy2=Fw[['mom_6M','mom_12M-1M']].rank().mean(axis=1)
        d['ic_proxy3']=spearman(proxy,r.reindex(idx)); d['ic_proxy_mom']=spearman(proxy2,r.reindex(idx)); d['ic_model_te_same']=spearman(g.wynik.reindex(idx),r.reindex(idx))
        d['ic_model_minus_proxy3']=d['ic_model_te_same']-d['ic_proxy3']
        # IC modelu na resztach po proxy w obrębie 30 nazw (rangowa regresja rel na proxy)
        rr30=r.reindex(idx); Xp=np.column_stack([np.ones(len(idx)),proxy.values]); bp,*_=np.linalg.lstsq(Xp,rr30.rank().values,rcond=None)
        d['ic_reszty_po_proxy30']=spearman(g.wynik.reindex(idx),pd.Series(rr30.rank().values-Xp@bp,index=idx))
        rows.append(d)
T4=pd.DataFrame(rows)
for win in ['D0→D+5 (faza 1)','rachunek: wejście→rotacja']:
    t=T4[T4.window==win].drop(columns='window').set_index('week'); print(f'### {win}\n'); print(t.round(2).to_markdown())
    summ=pd.DataFrame({col:dict(zip(['mean','t','n'],tstat(t[col]))) for col in t.columns if col!='n'}).T; summ['dodatnich']=[(t[col]>0).sum() for col in summ.index]
    print('\n'+summ.round(3).to_markdown()); print()
res['T4']=T4.to_dict('records')
# ---------------- T6 „~75% wyjaśnione": R² rang Wyniku na czynnikach
print('\n## T6. Ile Wyniku wyjaśniają momentum 6M, 12M−1M i beta: R² regresji rang Wyniku (30 nazw; osobno 15 LONG / 15 SHORT) na rangach czynników, per tydzień\n')
rows=[]
for w in WEEKS:
    i=c.index.get_loc(pd.Timestamp(D0[w])); F=factors_at(i); g=R[R.week==w].set_index('ticker'); idx=[t for t in g.index if t in F.index]; Fw=F.reindex(idx)
    def r2(y,cols,sub=None):
        yy=y.copy(); FF=Fw.copy()
        if sub is not None: yy=yy[sub]; FF=FF[sub]
        yr=yy.rank().values; X=np.column_stack([np.ones(len(yr))]+[FF[cc].rank().values for cc in cols]); bb,*_=np.linalg.lstsq(X,yr,rcond=None)
        return 1-np.var(yr-X@bb)/np.var(yr)
    y=g.wynik.reindex(idx); sideL=(g.side.reindex(idx)=='LONG').values; sideS=~sideL
    rows.append(dict(week=w,n=len(idx),R2_mom6M=r2(y,['mom_6M']),R2_beta=r2(y,['beta_126d']),R2_mom6M_mom12=r2(y,['mom_6M','mom_12M-1M']),R2_3czynniki=r2(y,['mom_6M','mom_12M-1M','beta_126d']),
        R2_3cz_LONG15=r2(y,['mom_6M','mom_12M-1M','beta_126d'],sideL),R2_3cz_SHORT15=r2(y,['mom_6M','mom_12M-1M','beta_126d'],sideS),R2_4cz_z_vol=r2(y,['mom_6M','mom_12M-1M','beta_126d','vol_20d']),
        strona_vs_mom6M=float(abs(spearman(pd.Series(sideL.astype(int),index=idx),Fw.mom_6M)))))
T6=pd.DataFrame(rows).set_index('week'); print(T6.round(2).to_markdown()); print('\nśrednia W1–W7: '+', '.join(f"{col} {T6.loc[WK,col].mean():.2f}" for col in T6.columns if col!='n')+f"; W8: R2_3czynniki {T6.loc['2026-W8','R2_3czynniki']:.2f}")
# R² między tygodniowym IC modelu a IC czynników (jak w dodatku): już policzone corr 0,90–0,95 → tu powtórzone na dwóch oknach
for win in ['D0→D+5 (faza 1)','rachunek: wejście→rotacja']:
    t=T4[T4.window==win]; print(f"{win}: corr(IC modelu, IC proxy3 wśród tych samych 30 nazw) = {t.ic_model_te_same.corr(t.ic_proxy3):.2f} (R² {t.ic_model_te_same.corr(t.ic_proxy3)**2:.2f}); corr z IC proxy mom = {t.ic_model_te_same.corr(t.ic_proxy_mom):.2f}")
res['T6']=T6.reset_index().to_dict('records')
# ---------------- T5 moc testu
print('\n## T5. Moc testu i IC, którego nie można wykluczyć\n')
T5={}
for win in ['D0→D+5 (faza 1)','D+1→D+6 (5 sesji od wejścia)','rachunek: wejście→rotacja']:
    W=pd.read_csv(f"{OUT}_T1_{win.split(' ')[0].replace(':','').replace('→','_')}.csv"); ic=W.ic30; m=ic.mean(); sd=ic.std(ddof=1); se=sd/np.sqrt(7); tcrit=st.t.ppf(0.975,6)
    ci=(m-tcrit*se,m+tcrit*se)
    # MDE (80% mocy, alfa 5% dwustronnie, n=7, t-test): IC_min = (t_{0.975,6}+t_{0.80,6})·sd/√7
    mde=(st.t.ppf(0.975,6)+st.t.ppf(0.80,6))*se
    # moc symulowana dla IC_true przy sd obserwowanym
    rng=np.random.default_rng(3); power={}
    for ict in [0.03,0.05,0.10,0.20,0.30,0.50]:
        sims=rng.normal(ict,sd,(20000,7)); tt=sims.mean(1)/(sims.std(1,ddof=1)/np.sqrt(7)); power[ict]=float((tt>st.t.ppf(0.95,6)).mean())  # jednostronnie: IC>0
    # sd IC tygodniowego pod H0 niezależnych nazw: 1/sqrt(n-1) dla n=30
    sd0=1/np.sqrt(29)
    # ile tygodni dla t=2 przy IC 0,05 i 0,03 przy sd obserwowanym
    nweeks={ict:int(np.ceil((2*sd/ict)**2)) for ict in [0.03,0.05,0.10]}
    T5[win]=dict(mean=m,sd=sd,se=se,ci95=list(ci),mde80=mde,power=power,sd_H0_iid=sd0,nweeks_t2=nweeks)
    print(f"### {win}\nśr. IC30 {m:+.3f}, sd tygodniowego IC {sd:.3f} (pod H0 niezależnych 30 nazw sd ≈ 1/√29 = {sd0:.3f} — obserwowane {sd/sd0:.1f}× większe, bo Wynik ładuje czynniki), se {se:.3f}")
    print(f"95% CI średniego IC (t, 6 df): {ci[0]:+.3f} … {ci[1]:+.3f}  → nie można wykluczyć IC aż do {ci[1]:+.2f} (ani ujemnego do {ci[0]:+.2f})")
    print(f"MDE (80% mocy, α 5% dwustr., n=7): |IC| ≥ {mde:.2f}; moc wykrycia (jednostr. α 5%) IC_true: "+', '.join(f"{k}: {v*100:.0f}%" for k,v in power.items()))
    print(f"tygodni do t=2 przy tym sd: IC 0,03 → {nweeks[0.03]}, 0,05 → {nweeks[0.05]}, 0,10 → {nweeks[0.10]}\n")
# permutacja: pasmo zerowej mocy vs IC 0,05 — czy IC 0,05 mieści się w paśmie (tj. test permutacyjny nie ma mocy)
A=ALL['D0→D+5 (faza 1)']; rng=np.random.default_rng(0); perm=[]
for _ in range(5000):
    perm.append(np.mean([spearman(pd.Series(rng.permutation(g.wynik.values),index=g.index),g.rel) for _,g in A.groupby('week')]))
perm=np.array(perm); T5['perm']=dict(sd=float(perm.std()),p5=float(np.percentile(perm,5)),p95=float(np.percentile(perm,95)),p_obs=float((perm>=A.groupby('week').apply(lambda g:spearman(g.wynik,g.rel)).mean()).mean()))
print(f"Permutacja (Wynik tasowany w obrębie tygodnia, 5000): sd śr. IC {perm.std():.3f}, 5–95% {np.percentile(perm,5):+.3f}…{np.percentile(perm,95):+.3f}; P(≥ obs) = {T5['perm']['p_obs']:.3f}. IC 0,05 leży W paśmie zerowej mocy → test permutacyjny z n=7×30 nie odróżnia IC 0,05 od zera; poza tym H0 permutacji (brak JAKIEJKOLWIEK struktury) nie jest H0 interesującą — Wynik ma strukturę czynnikową, więc realna sd IC jest {T5[list(T5)[0]]['sd']/perm.std()/np.sqrt(7):.1f}× większa niż permutacyjna.")
res['T5']=T5
# ---------------- dodatkowo: horyzont 10 sesji (czy model działa na dłuższym oknie)
print('\n## Dodatek. IC Wyniku na 10 i 15 sesjach od D0 (tam, gdzie dane sięgają) — czy brak mocy to kwestia horyzontu\n')
rows=[]
for w in WK:
    i=c.index.get_loc(pd.Timestamp(D0[w])); g=R[R.week==w]
    d=dict(week=w)
    for h in [5,10,15]:
        if i+h<len(c): r=rel(D0[w],str(c.index[i+h].date())); d[f'ic_{h}s']=spearman(g.wynik,g.ticker.map(r))
        else: d[f'ic_{h}s']=np.nan
    rows.append(d)
H=pd.DataFrame(rows).set_index('week'); print(H.round(2).to_markdown())
for col in H.columns: m,t,n=tstat(H[col]); print(f"{col}: śr {m:+.3f}, t {t:.2f}, n {n}")
res['horyzont']=H.reset_index().to_dict('records')
json.dump(res,open(OUT+'_wyniki.json','w'),indent=1,default=lambda o: float(o) if isinstance(o,(np.floating,np.integer)) else str(o))
pd.concat(ALL.values()).to_csv(OUT+'_nazwy.csv',index=False)
