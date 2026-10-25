import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
from research.programma7 import quarantacinquesima as q
from research.programma6 import seconda as sc
pan = sc.pannello()
ev = q.eventi(set(pan['simboli']))
cb = es.ore_di('BTCUSDT')
for s, a, c, i in ev:
    v = orev(s)
    if v.empty: continue
    h_e, h_u = a//3_600_000+1, c//3_600_000-1
    dopo = v[v.index >= h_e]
    z = dopo[dopo['volume']==0]
    if not len(z): continue
    pz = int(z.index.min())
    if pz <= h_u:
        vera_u = pz - 1   # una ora prima della prima candela morta
        # real "one hour before closure" = pz-2? closure hour = pz (first dead) ; if last active candle is the closure hour (diff 0) ...
        print(f"{s:14s} entra {f(h_e)} p0={v.loc[h_e,'open']:.6g} | ultima viva {f(pz-1)} open={v.loc[pz-1,'open']:.6g} close={v.loc[pz-1,'close']:.6g} | uscita usata {f(h_u)} open={v.loc[h_u,'open']:.6g} vol={v.loc[h_u,'volume']} | r_coin_usata={v.loc[h_u,'open']/v.loc[h_e,'open']-1:+.3f} r_coin_vera={v.loc[pz-2,'open']/v.loc[h_e,'open']-1:+.3f} btc_extra={cb.loc[h_u,'open']/cb.loc[pz-2,'open']-1:+.3f}")
