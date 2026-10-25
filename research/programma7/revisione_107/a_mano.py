import sys; sys.path.insert(0,'/tmp/revisore107')
from rifai import *
from research.programma6 import ventunesima as vu
pub = pd.read_csv('/home/user/agentic_trading_system/research/programma7/risultati_quarantacinquesima/eventi_G13C.csv')
evo = {s: (a, c) for s, a, c, i in q.eventi(set(pan['simboli']))}
for s in ['NEIROETHUSDT', 'KDAUSDT', 'HIPPOUSDT', 'BSWUSDT', 'ANTUSDT']:
    a, c = evo[s]; he, hu = a//3600000 + 1, c//3600000 - 1
    cc = candele(s); p0 = cc.loc[he, 'open']; b0 = cb.loc[he, 'open']
    tratto = cc[(cc.index >= he) & (cc.index < hu)]
    su = tratto.index[tratto['high'] >= p0*1.3]
    if len(su): uh = int(su[0]); pc = p0*1.3*1.01
    else: uh = hu; pc = cc.loc[hu, 'open']
    pb = cb.loc[uh, 'open']
    fcs = fund(s); g0, g1 = he//24, uh//24
    fc = fcs[(fcs.index>=g0)&(fcs.index<=g1)].sum(); fbb = fb[(fb.index>=g0)&(fb.index<=g1)].sum()
    r = (pb/b0-1) - (pc/p0-1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb
    print(f"{s}: entrata {f(he)} p0 {p0:.6g} BTC {b0:.0f} | uscita {f(uh)} {'(stop)' if len(su) else ''} pc {pc:.6g} BTC {pb:.0f} | moneta {pc/p0-1:+.4f} BTC {pb/b0-1:+.4f} costi {-(vu.COSTO_MONETA+vu.COSTO_BTC):+.4f} funding moneta {fc:+.4f} BTC {-fbb:+.4f} => r {r:+.4f} (pubblicato {pub.set_index('simbolo').loc[s,'r']:+.4f})")
print('costi:', vu.COSTO_MONETA, vu.COSTO_BTC)
