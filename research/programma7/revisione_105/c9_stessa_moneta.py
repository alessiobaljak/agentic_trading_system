"""È la stessa moneta? Prezzo di chiusura del primo giorno su Coinbase (quotazioni.json) contro la chiusura del perpetuo Binance lo
stesso giorno; buchi e salti nel perpetuo nei 30 giorni prima di L."""
import json, sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
from research.programma7 import quarantatreesima as q
pan = sc.pannello(); t0 = pan['t0']; sim = pan['simboli']
C = pan['close']; V = np.nan_to_num(pan['quote_volume'])
primi = json.loads(q.PRIMI.read_text())
quot = {x['prodotto']: x for x in json.load(open('/home/user/agentic_trading_system/research/data/coinbase/quotazioni.json'))}
ev = pd.read_csv('/tmp/revisore105/eventi_rifatti.csv')
per_sim = {v['perpetuo']: (b, v) for b, v in primi.items()}
righe = []
for _, x in ev.iterrows():
    s = x['simbolo']; b, v = per_sim[s]; L = int(x['L']); j = sim.index(s); k = L - t0
    molt = 1000 if s.startswith('1000') and not s.startswith('1000000') else (1e6 if s.startswith('1000000') else 1)
    qq = quot.get(v['prodotto'], {})
    pcb = qq.get('prezzo_primo_giorno'); gq = qq.get('primo_giorno'); ora = qq.get('prima_ora')
    pbn = C[k, j] / molt
    finestra = C[k - 30:k, j]
    buchi = int((~np.isfinite(finestra)).sum())
    salto = float(np.nanmax(np.abs(np.diff(np.log(finestra[np.isfinite(finestra)]))))) if np.isfinite(finestra).sum() > 2 else np.nan
    vol_med = float(np.median(V[k - 30:k, j]))
    righe.append({'s': s, 'prodotto': v['prodotto'], 'L': sc.data(L), 'quot_primo_giorno': gq, 'prima_ora_cb': ora,
                  'rapporto_prezzo_cb_su_binance': (pcb / pbn) if pcb and pbn else np.nan, 'buchi_30g': buchi, 'salto_max_log': salto,
                  'vol_med_30g_M$': vol_med / 1e6, 'r': x['r']})
d = pd.DataFrame(righe)
pd.set_option('display.width', 250)
print(d.to_string())
print('rapporto prezzo fuori da [0.8, 1.25]:')
print(d[(d.rapporto_prezzo_cb_su_binance < 0.8) | (d.rapporto_prezzo_cb_su_binance > 1.25) | d.rapporto_prezzo_cb_su_binance.isna()].to_string())
print('date diverse fra quotazioni.json e primi_giorni:', d[d.quot_primo_giorno != d.L][['s', 'L', 'quot_primo_giorno']].to_string())
d.to_csv('/tmp/revisore105/stessa_moneta.csv', index=False)
