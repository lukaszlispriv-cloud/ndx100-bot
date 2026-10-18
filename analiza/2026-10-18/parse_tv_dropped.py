import json, sys, glob, datetime
import pandas as pd
files = glob.glob('/root/.claude/projects/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/tool-results/mcp-TradingView-mcp-tv-get-ohlcv-*.txt')
series = {}
for fp in files:
    try:
        d = json.load(open(fp))
    except Exception as e:
        print('skip', fp, e); continue
    if not d.get('success') or 'bars' not in d:
        continue
    sym = d['symbol'].split(':')[-1]
    b = d['bars']
    idx = pd.to_datetime([datetime.datetime.utcfromtimestamp(t).date() for t in b['t']])
    s = pd.Series(b['c'], index=idx, name=sym, dtype=float)
    s = s[~s.index.duplicated(keep='last')]
    series[sym] = s
    print(sym, len(s), s.index[0].date(), s.index[-1].date(), d['count'], d['has_more'])
df = pd.DataFrame(series).sort_index()
df.index.name = 'date'
df.to_csv('/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/dropped_closes.csv')
print(df.shape, sorted(df.columns))
