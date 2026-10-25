import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
import glob
from pathlib import Path
def kl(d, s):
    fs = sorted(glob.glob(f'/tmp/revisore107/{d}/{s}-20*.zip'))
    if not fs: return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(Path(p), m5.KLINE) for p in fs], ignore_index=True)
    df['ora'] = m5._ms(df['open_time']) // 3_600_000
    return df.drop_duplicates('ora', keep='last').set_index('ora').sort_index()[['open','high','low','close']].astype(float)
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
cb = es.ore_di('BTCUSDT')
rows = []
for _, r in ev.iterrows():
    s = r.simbolo; c = es.ore_di(s); ix = kl('idx', s); mk = kl('mark', s)
    he, hu = int(r.h_e), int(r.h_u); usc = he + int(r.ore)
    if ix.empty or he not in ix.index or hu not in ix.index:
        rows.append((s, r.data, None)); continue
    pe, pu = c.loc[he,'open'], c.loc[hu,'open']
    ie, iu = ix.loc[he,'open'], ix.loc[hu,'open']
    # last trading hours range
    ult = c.loc[hu-3:hu+1]
    rows.append(dict(simbolo=s, data=r.data, r=r.r, r_senza=r.r_senza, base_e=pe/ie-1, base_u=pu/iu-1, perp_ret=pu/pe-1, idx_ret=iu/ie-1,
                     idx_ret_ultima=(ix.loc[hu+1,'open']/iu-1) if hu+1 in ix.index else np.nan,
                     perp_ret_ultima=(c.loc[hu+1,'open']/pu-1) if hu+1 in c.index else np.nan))
df = pd.DataFrame([x for x in rows if isinstance(x, dict)])
pd.set_option('display.width', 250)
print(df.round(3).to_string())
print('mancano indice:', [x[0] for x in rows if not isinstance(x, dict)])
print(df[['base_e','base_u','perp_ret','idx_ret','idx_ret_ultima','perp_ret_ultima']].describe().round(3))
# strategy using index price (short index vs BTC) without costs/funding approximation
df.to_csv('/tmp/revisore107/indice_confronto.csv', index=False)
