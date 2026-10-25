import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
ev = pd.read_csv('/tmp/revisore107/eventi_finale.csv')
ev = ev[ev.data >= '2024-01-01']
rows = []
for _, r in ev.iterrows():
    v = orev(r.simbolo); he, hu = int(r.h_e), int(r.h_u)
    rows.append(dict(simbolo=r.simbolo, qv_entrata=v.loc[he,'quote_volume'], qv_uscita=v.loc[hu,'quote_volume'] if hu in v.index else np.nan,
                     qv_ora_prima_uscita=v.loc[hu-1,'quote_volume'], qv_mediana_tenuta=v.loc[he:hu,'quote_volume'].median(),
                     range_uscita=(v.loc[hu,'high']/v.loc[hu,'low']-1) if hu in v.index else np.nan, range_tipico=(v.loc[he:hu,'high']/v.loc[he:hu,'low']-1).median()))
d = pd.DataFrame(rows)
print(d.describe(percentiles=[.1,.25,.5,.75]).round(3).to_string())
print(d.sort_values('qv_mediana_tenuta').head(8).round(0).to_string())
