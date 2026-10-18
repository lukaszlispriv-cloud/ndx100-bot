"""IC i kalibracja wyniku Modelu 3.0 (TOP15/BOTTOM15 z raportów W1-W7) wobec zwrotu relatywnego vs ^NDX w 5 sesjach po D0.
Uruchom: python3 -I mp_ic_model.py > mp_ic_model_out.md"""
import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/analiza")
import pandas as pd, numpy as np, json
from mp_lib import *
c=closes(); U=universe(c); R=ranking(); K=koszyki()
rows=[]; wk_stats=[]
for wk in WEEKS[:-1]:
    rel5,dend5=fwd_rel(c,D0[wk],5); relF,dendF=fwd_rel(c,D0[wk],end=DEND[wk]); relFd,_=fwd_rel(c,D0[wk],end=DEND[wk],div=True)
    r=R[R.week==wk].copy()
    r['rel5']=r.ticker.map(rel5); r['relF']=r.ticker.map(relF); r['relFd']=r.ticker.map(relFd)
    r['basket']=[(t in K[wk]['long']) if s=='LONG' else (t in K[wk]['short']) for t,s in zip(r.ticker,r.side)]
    r['sgn']=np.where(r.side=='LONG',1,-1)
    r['pos5']=r.sgn*r.rel5; r['posF']=r.sgn*r.relF
    rows.append(r)
    # IC 30 nazw: wynik vs rel5 ; w obrębie strony
    ic30=spearman(r.wynik,r.rel5); icL=spearman(r[r.side=='LONG'].wynik,r[r.side=='LONG'].rel5); icS=spearman(r[r.side=='SHORT'].wynik,r[r.side=='SHORT'].rel5)
    ic30F=spearman(r.wynik,r.relF)
    # uniwersum: TOP15/BOTTOM15 vs reszta
    rest=[t for t in U if t not in set(r.ticker)]
    restrel=rel5.reindex(rest).dropna()
    # kontrola: spread koszyka od D0 (okno faktyczne, z dywidendami) vs history
    b=r[r.basket]; spreadF=b[b.side=='LONG'].relFd.mean()-b[b.side=='SHORT'].relFd.mean()
    spread5=b[b.side=='LONG'].rel5.mean()-b[b.side=='SHORT'].rel5.mean()
    wk_stats.append(dict(week=wk,d0=D0[wk],d5=str(dend5.date()),dF=str(dendF.date()),ic30=ic30,ic30_okno_fakt=ic30F,ic_long15=icL,ic_short15=icS,
        spread5_pp=spread5,spreadF_div_pp=spreadF,
        hit_top5=int((b[b.side=='LONG'].pos5>0).sum()),hit_bot5=int((b[b.side=='SHORT'].pos5>0).sum()),
        hit_top5_fakt=int((b[b.side=='LONG'].posF>0).sum()),hit_bot5_fakt=int((b[b.side=='SHORT'].posF>0).sum()),
        mean_rel_rest=restrel.mean(),share_rest_pos=(restrel>0).mean()*100,n_rest=len(restrel)))
A=pd.concat(rows); W=pd.DataFrame(wk_stats)
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.float_format',lambda x:f'{x:.2f}')
print('# IC Modelu 3.0 per tydzień (Spearman wynik vs zwrot rel. 5 sesji od D0; strona SHORT ma niski wynik, więc IC30 dodatni = model trafia kierunek)\n')
print(W.to_markdown(index=False))
for col in ['ic30','ic30_okno_fakt','ic_long15','ic_short15','spread5_pp','spreadF_div_pp']:
    m,t,n=tstat(W[col]); print(f'\n{col}: średnia {m:.3f}, t={t:.2f}, n={n}, dodatnich {int((W[col]>0).sum())}/{n}')
print('\nkontrola spread okna faktycznego z dywidendami vs history spread_pp: W1 -4.06, W2 6.19, W3 1.44, W4 13.85, W5 5.95, W6 -5.89, W7 -21.15')
# pooled IC z demeaningiem po tygodniu
A['rel5_dm']=A.rel5-A.groupby('week').rel5.transform('mean')
print(f"\nPooled Spearman (210 nazwo-tygodni, rel5 demeaned per tydzień): {spearman(A.wynik,A.rel5_dm):.3f}")
# permutacja: rozkład średniego IC przy losowym przetasowaniu wyników w obrębie tygodnia
rng=np.random.default_rng(0); perm=[]
for _ in range(5000):
    ics=[]
    for wk,g in A.groupby('week'):
        ics.append(spearman(pd.Series(rng.permutation(g.wynik.values),index=g.index),g.rel5))
    perm.append(np.mean(ics))
perm=np.array(perm); obs=W.ic30.mean()
print(f"Permutacja (5000): P(średni IC30 >= {obs:.3f}) = {(perm>=obs).mean():.3f}; 5-95% przy zerowej mocy: {np.percentile(perm,5):.3f}…{np.percentile(perm,95):.3f}")
# grupy: TOP5(koszyk) / TOP15 poza koszykiem / reszta uniwersum — zwrot pozycji (long: rel, short: -rel)
print('\n# Hit rate i średni zwrot pozycji wg grupy (5 sesji od D0, równe wagi; "reszta" = uniwersum poza TOP15/BOTTOM15, kierunek long dla strony LONG i short dla SHORT — czyli to samo co losowa nazwa)')
A['grupa']=np.where(A.basket,'koszyk5','ranking6-15/wykl.')
g=A.groupby(['side','grupa']).agg(n=('pos5','size'),hit=('pos5',lambda x:(x>0).mean()*100),mean_pp=('pos5','mean'),sd=('pos5','std'))
g['t']=g.mean_pp/(g.sd/np.sqrt(g.n)); print(g.to_markdown())
# per-week version (klastrowanie po tygodniu)
pw=A.groupby(['side','grupa','week']).pos5.mean().unstack('week')
print('\nŚredni zwrot pozycji grupy per tydzień (p.p.) — do t klastrowanego:'); print(pw.to_markdown())
for (s,gr),row in pw.iterrows():
    m,t,n=tstat(row); print(f'{s} {gr}: śr {m:.2f} p.p./tydz., t(7 tyg.)={t:.2f}')
# reszta uniwersum per tydzień: udział nazw z rel5>0 (baza dla LONG) i rel5<0 (baza SHORT)
print('\nBaza losowa: udział nazw reszty uniwersum z rel5>0 per tydzień: '+', '.join(f"{w}: {s:.0f}%" for w,s in zip(W.week,W.share_rest_pos)))
# kalibracja p
print('\n# Kalibracja p (p_win = deklarowane prawdopodobieństwo trafienia kierunku; w W1-W7 strona SHORT podawała p trafienia, w W8 p outperformance → znormalizowano)')
A['hit']=(A.pos5>0).astype(int)
print(f"p podane vs p ze wzoru B4 (50+0,5·(wynik−50), 38–62): zgodne co do 1 pkt w {(abs(A.p_win-A.p_formula)<=1).mean()*100:.0f}% wierszy (n={A.p_win.notna().sum()}); p jest funkcją wyniku, nie niezależną oceną")
bins=pd.cut(A.p_win,[0,54.5,56.5,58.5,60.5,63],labels=['≤54','55–56','57–58','59–60','61–62'])
cal=A.groupby(bins,observed=True).agg(n=('hit','size'),trafien=('hit','sum'),hit_pct=('hit',lambda x:x.mean()*100),p_sr=('p_win','mean'),mean_pp=('pos5','mean'))
print(cal.to_markdown())
hi=A[A.p_win>55]; lo=A[A.p_win<=55]
for nm,d in (('p>55',hi),('p<=55',lo)):
    k=int(d.hit.sum()); n=len(d); ph=k/n; se=np.sqrt(ph*(1-ph)/n)
    print(f'{nm}: {k}/{n} = {ph*100:.1f}% (±{1.96*se*100:.1f} p.p. 95%), deklarowane śr. {d.p_win.mean():.1f}%; śr. zwrot pozycji {d.pos5.mean():.2f} p.p.')
calw=A[A.p_win>55].groupby('week').hit.agg(['sum','size']); print('p>55 per tydzień:', ', '.join(f"{w}: {int(a)}/{int(b)}" for w,(a,b) in calw.iterrows()))
# wynik jako przedykt: kwartyle |wynik-50|
A['sila']=abs(A.wynik-50)
q=pd.qcut(A.sila,3,labels=['słaby','średni','silny'])
print('\nSiła sygnału |wynik−50| (tercyle) vs trafienie:'); print(A.groupby(q,observed=True).agg(n=('hit','size'),hit_pct=('hit',lambda x:x.mean()*100),mean_pp=('pos5','mean'),sila_min=('sila','min'),sila_max=('sila','max')).to_markdown())
A.to_csv('mp_model_nazwy.csv',index=False); W.to_csv('mp_model_tygodnie.csv',index=False)
