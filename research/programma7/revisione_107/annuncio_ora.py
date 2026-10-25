import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
cb = es.ore_di('BTCUSDT')
import json
el = {a['id']: a for a in json.load(open('/home/user/agentic_trading_system/research/data/annunci/chiusure/elenco.json'))}
rows = []
for _, r in ev.iterrows():
    s = r.simbolo; v = orev(s); he = int(r.h_e); ha = he - 1
    ms = el[r.id_annuncio]['ms']; minuto = (ms // 60000) % 60
    def rr(a, b):
        if a in v.index and b in v.index and a in cb.index and b in cb.index:
            return (v.loc[b, 'open'] / v.loc[a, 'open'] - 1) - (cb.loc[b, 'open'] / cb.loc[a, 'open'] - 1)
        return np.nan
    qv = v['quote_volume']
    base = qv.loc[ha-7*24:ha-25].median()
    rows.append(dict(simbolo=s, minuto=minuto, r_m24_m1=rr(ha-24, ha-1), r_ora_prima=rr(ha-1, ha), r_ora_annuncio=rr(ha, he), r_6h_dopo=rr(he, he+6), r_24h_dopo=rr(he, he+24),
                     vol_prima=qv.loc[ha-1]/base, vol_annuncio=qv.loc[ha]/base, vol_dopo=qv.loc[he]/base))
df = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print(df.round(3).to_string())
print(df.drop(columns=['simbolo']).median().round(3))
print(df.drop(columns=['simbolo','minuto']).mean().round(4))
