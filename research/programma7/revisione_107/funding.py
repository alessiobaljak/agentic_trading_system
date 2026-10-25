import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
import glob, zipfile, io
from research.src.dati import funding_da_zip
from research.programma6 import seconda as sc
from pathlib import Path
pan = sc.pannello(); t0 = pan['t0']; giorni = np.arange(pan['close'].shape[0]) + t0
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
def vera(s):
    righe = []
    for p in sorted(glob.glob(f'/tmp/revisore107/fr/{s}-20*.zip')):
        righe += funding_da_zip(Path(p))
    return pd.DataFrame(righe, columns=['ts','ore','tasso']).drop_duplicates('ts').sort_values('ts') if righe else pd.DataFrame(columns=['ts','ore','tasso'])
out = []
for _, r in ev.iterrows():
    s = r.simbolo; j = pan['simboli'].index(s)
    f = pd.Series(pan['funding'][:, j], index=giorni)
    usc = int(r.h_e + r.ore)
    g0, g1 = int(r.h_e)//24, usc//24
    pan_sum = f[(f.index >= g0) & (f.index <= g1)].sum()
    v = vera(s)
    # settlements strictly after entry and at or before exit (holder at settlement time)
    m = v[(v.ts > r.h_e*3_600_000) & (v.ts <= usc*3_600_000)]
    vera_sum = m['tasso'].sum()
    ints = sorted(set(m['ore'])) if len(m) else []
    out.append((s, r.data, r.ore, round(100*pan_sum,2), round(100*vera_sum,2), round(100*(vera_sum-pan_sum),2), ints, len(m), round(100*m['tasso'].min(),2) if len(m) else None))
df = pd.DataFrame(out, columns=['simbolo','data','ore','panel_%','vero_%','diff_%','intervalli_h','n','min_%'])
print(df.to_string())
print('media panel', df['panel_%'].mean(), 'media vero', df['vero_%'].mean(), 'media diff', df['diff_%'].mean())
df.to_csv('/tmp/revisore107/funding_confronto.csv', index=False)
