import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
from research.programma7 import quarantacinquesima as q
from research.programma6 import seconda as sc
pan = sc.pannello()
ev = q.eventi(set(pan['simboli']))
rows=[]
for s, a, c, i in ev:
    v = orev(s)
    h_e, h_u = a//3_600_000+1, c//3_600_000-1
    hc = c//3_600_000
    if v.empty:
        print(s, 'NO DATA'); continue
    dopo = v[v.index >= h_e]
    attivi = dopo[dopo['volume'] > 0]
    ultima_vol = int(attivi.index.max()) if len(attivi) else None
    ultima = int(dopo.index.max()) if len(dopo) else None
    # first zero-volume hour after h_e
    zeri = dopo[dopo['volume'] == 0]
    primo_zero = int(zeri.index.min()) if len(zeri) else None
    b6 = d6.barre(s, '1h')
    has6 = not b6.empty
    # volume (quote) in h_u hour vs median daily-hour before announcement
    qv_u = v.loc[h_u,'quote_volume'] if h_u in v.index else np.nan
    qv_pre = v[(v.index < h_e-1) & (v.index >= h_e-24*7)]['quote_volume'].median()
    rows.append((i, s, f(a//3600000), f(hc), f(ultima_vol) if ultima_vol else None, f(ultima) if ultima else None, f(primo_zero) if primo_zero else None, (ultima_vol - hc) if ultima_vol else None, has6, round(qv_u/qv_pre,2) if qv_pre else None))
for r in rows: print(*r)
