"""Wspólne funkcje: wczytanie closes_5y.csv, rankingów, koszyków; zwroty forward 5-sesyjne relatywne vs ^NDX."""
import pandas as pd, numpy as np, json, re
BASE='/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad'
IDX=['^NDX','^SOX','^VIX','^GSPC','QQQ','XLP','XLU','XLV','SMH','IGV']
WEEKS=['2026-W1','2026-W2','2026-W3','2026-W4','2026-W5','2026-W6','2026-W7','2026-W8']
D0={'2026-W1':'2026-08-26','2026-W2':'2026-08-28','2026-W3':'2026-09-04','2026-W4':'2026-09-11',
    '2026-W5':'2026-09-28','2026-W6':'2026-10-02','2026-W7':'2026-10-09','2026-W8':'2026-10-16'}
# faktyczne końce okien rozliczonych (z history/raportów): W1 2 sesje, W3 4, W4 11, W5 4
DEND={'2026-W1':'2026-08-28','2026-W2':'2026-09-04','2026-W3':'2026-09-11','2026-W4':'2026-09-28',
      '2026-W5':'2026-10-02','2026-W6':'2026-10-09','2026-W7':'2026-10-16'}
DIV={('PEP','2026-09-04'):1.48,('NVDA','2026-09-10'):0.25,('AVGO','2026-09-21'):0.65,('CMCSA','2026-10-07'):0.33,('MU','2026-10-14'):0.15}  # z raportów (dekompozycja-wynikow.md §1)
def closes():
    c=pd.read_csv(f'{BASE}/dane/closes_5y.csv',index_col=0,parse_dates=True).sort_index()
    stocks=[t for t in c.columns if t not in IDX]
    c=c[~c[stocks].isna().all(axis=1)]   # wiersze świąt (2026-05-25, 2026-09-07) mają tylko indeksy
    return c
def universe(c): return [t for t in c.columns if t not in IDX]
def ranking():
    r=pd.read_csv(f'{BASE}/analiza/mp_ranking.csv')
    r['ticker']=r.ticker.str.split().str[0]   # 'EXC / XEL'->EXC, 'MRVL EVENT W OKNIE'->MRVL
    # p_win: prawdopodobieństwo trafienia kierunku (W8 strona SHORT podawała p outperformance)
    r['p_win']=np.where((r.side=='SHORT')&(r.p<50),100-r.p,r.p)
    # p modelowe wg wzoru B4: p = 50+0,5*(wynik-50) obcięte 38-62 (dla short: 100-p)
    pm=(50+0.5*(r.wynik-50)).clip(38,62)
    r['p_formula']=np.where(r.side=='SHORT',100-pm,pm)
    return r
def koszyki():
    k=json.load(open(f'{BASE}/analiza/mp_koszyki.json'))
    k['2026-W8']['long']=['GOOGL','GILD','MSFT','QCOM','ADP']; k['2026-W8']['short']=['AXON','DASH','ALNY','APP','FER']  # z signals.json
    return k
def fwd_rel(c, d0, n=5, end=None, div=False):
    """zwrot spółki od zamknięcia D0 do D0+n sesji (albo do daty end) minus zwrot ^NDX; Series po tickerach uniwersum."""
    i=c.index.get_loc(pd.Timestamp(d0))
    j=c.index.get_loc(pd.Timestamp(end)) if end else i+n
    if j>=len(c): return None
    p0=c.iloc[i]; p1=c.iloc[j].copy()
    if div:
        for (t,dt),amt in DIV.items():
            if t in p1.index and c.index[i]<pd.Timestamp(dt)<=c.index[j]: p1[t]+=amt
    r=p1/p0-1
    return (r-r['^NDX'])*100, c.index[j]
def spearman(a,b):
    d=pd.concat([a,b],axis=1).dropna()
    if len(d)<3: return np.nan
    return d.iloc[:,0].rank().corr(d.iloc[:,1].rank())
def tstat(x):
    x=pd.Series(x).dropna(); n=len(x)
    if n<2: return (x.mean() if n else np.nan, np.nan, n)
    return x.mean(), x.mean()/(x.std(ddof=1)/np.sqrt(n)), n
def md(df, index=True, fmt='{:.2f}'):
    """prosty markdown bez tabulate"""
    d=df.copy()
    if index: d=d.reset_index()
    def f(v):
        if isinstance(v,(float,np.floating)):
            return '' if np.isnan(v) else fmt.format(v)
        return str(v)
    cols=[str(x) for x in d.columns]
    out=['| '+' | '.join(cols)+' |','|'+'---|'*len(cols)]
    for _,row in d.iterrows(): out.append('| '+' | '.join(f(v) for v in row.values)+' |')
    return '\n'.join(out)
pd.DataFrame.to_markdown=lambda self,index=True,**kw: md(self,index=index)
pd.Series.to_markdown=lambda self,index=True,**kw: md(self.to_frame(),index=index)
