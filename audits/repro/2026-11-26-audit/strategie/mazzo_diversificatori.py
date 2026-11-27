import sys, math
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import asticella as a
serie, soli = a.mazzo()
nomi = sorted(serie)
g1 = [n for n in nomi if n.startswith('57')]
f5 = [n for n in nomi if n.startswith('24')]
print("nomi G1:", g1, "nomi F5:", f5)
G1 = serie[g1[0]]
righe = []
for n in nomi:
    s = serie[n].dropna()
    if len(s) < 52: continue
    sr = a.sharpe(s); t = sr * math.sqrt(len(s)/52)
    com = s.index.intersection(G1.index)
    rho = float(np.corrcoef(s.loc[com], G1.loc[com])[0,1]) if len(com) > 52 and s.loc[com].std() > 0 else float('nan')
    # miglior miscela a volatilità uguale 50/50 sulle settimane comuni
    x, y = s.loc[com], G1.loc[com]
    if len(com) > 52 and x.std() > 0:
        xs = x / x.std() * y.std()
        mix = 0.5 * xs + 0.5 * y
        srm = a.sharpe(mix); srg = a.sharpe(y)
    else:
        srm = srg = float('nan')
    anni = pd.to_datetime(s.index.to_numpy()*86400, unit='s').year
    per_anno = s.groupby(anni).mean()
    pos = int((per_anno > 0).sum()); tot = len(per_anno)
    righe.append((n, len(s), sr, t, rho, srm, srg, pos, tot))
df = pd.DataFrame(righe, columns=['serie','settimane','sharpe','t','corr_G1','sharpe_mix_50_50_vol_uguale','sharpe_G1_stesse_sett','anni_pos','anni'])
df.to_csv('/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/strategie/mazzo_diversificatori.csv', index=False)
sel = df[(df.sharpe >= 1.0) & (df.corr_G1.abs() < 0.5)].sort_values('sharpe_mix_50_50_vol_uguale', ascending=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 20)
print(sel.head(25).round(2).to_string(index=False))
print("totale serie", len(df), "con Sharpe>=1 e |corr G1|<0,5:", len(sel))
