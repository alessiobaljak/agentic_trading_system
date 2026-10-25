"""Controllo con le altre monete del pannello negli stessi giorni (candele giornaliere)."""
import sys; sys.path.insert(0,'/tmp/revisore107'); sys.path.insert(0,'/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
from research.programma6 import ventunesima as vu
pan = sc.pannello(); t0 = pan['t0']
O, C, V, F = pan['open'], pan['close'], np.nan_to_num(pan['quote_volume']), pan['funding']
sim = pan['simboli']; jb = sim.index('BTCUSDT'); je = sim.index('ETHUSDT')
ev = pd.read_csv('/tmp/revisore107/eventi_corretti.csv')
evset = set(ev['simbolo'])
# tutte le monete che chiudono (in qualunque momento) le escludo dai pari per evitare sovrapposizioni dirette
righe = []
for _, r in ev.iterrows():
    j = sim.index(r.simbolo)
    d0 = -(-int(r.h_e) // 24) - t0          # primo giorno che apre dopo l'entrata
    d1 = int(r.h_u) // 24 - t0               # apertura del giorno della chiusura
    if d1 - d0 < 1: continue
    def ret(k):
        if not (np.isfinite(O[d0, k]) and np.isfinite(O[d1, k]) and V[d0-1, k] > 0): return np.nan
        return (O[d1, jb] / O[d0, jb] - 1) - (O[d1, k] / O[d0, k] - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + F[d0:d1, k].sum() - F[d0:d1, jb].sum()
    re_ = ret(j)
    # caratteristiche prima dell'annuncio: volume medio 30 giorni e rendimento 30 giorni (fino al giorno prima dell'entrata)
    a = d0 - 1
    vol30 = V[a-30:a].mean(axis=0)
    r30 = O[a] / O[a-30] - 1
    vivi = [k for k in range(len(sim)) if k not in (jb, je, j) and sim[k] not in evset and np.isfinite(O[d0, k]) and np.isfinite(O[d1, k]) and V[d0-1, k] > 0 and np.isfinite(O[a-30, k])]
    tutti = np.array([ret(k) for k in vivi])
    lv = np.log(np.maximum(vol30[vivi], 1)); lvj = np.log(max(vol30[j], 1))
    vicini_v = np.argsort(np.abs(lv - lvj))[:10]
    rr = r30[vivi]; vicini_r = np.argsort(np.abs(rr - r30[j]))[:10]
    # combinato: rango normalizzato su entrambi
    zv = (lv - lvj) / (lv.std() + 1e-9); zr = (rr - r30[j]) / (np.nanstd(rr) + 1e-9)
    vicini_c = np.argsort(np.hypot(zv, zr))[:10]
    piccoli = np.flatnonzero(lv <= np.quantile(lv, 0.2))
    righe.append(dict(simbolo=r.simbolo, data=r.data, annuncio=r.annuncio, r_ev=re_, r_ev_ore=r.r_senza, tutti=np.nanmean(tutti), n=len(vivi),
                      vicini_volume=np.nanmean(tutti[vicini_v]), vicini_rend30=np.nanmean(tutti[vicini_r]), vicini_entrambi=np.nanmean(tutti[vicini_c]),
                      piccoli_20pct=np.nanmean(tutti[piccoli]), r30_ev=r30[j], vol30_rango=float((vol30[vivi] < vol30[j]).mean())))
df = pd.DataFrame(righe)
pd.set_option('display.width', 250)
print(df.round(3).to_string())
cols = ['r_ev', 'r_ev_ore', 'tutti', 'vicini_volume', 'vicini_rend30', 'vicini_entrambi', 'piccoli_20pct']
print(df[cols].mean().round(4))
# bootstrap per settimana della differenza evento - pari
def boot(x, g, n=10000, seed=2026):
    d = pd.DataFrame({'x': x, 'g': g}).dropna(); gr = [v['x'].to_numpy() for _, v in d.groupby('g')]
    rng = np.random.default_rng(seed); m = np.empty(n)
    for b in range(n):
        s = rng.integers(0, len(gr), len(gr)); m[b] = np.concatenate([gr[i] for i in s]).mean()
    return round(d['x'].mean(), 4), round((np.sum(m <= 0) + 1) / (n + 1), 4)
for c in ['tutti', 'vicini_volume', 'vicini_rend30', 'vicini_entrambi', 'piccoli_20pct']:
    print('evento giornaliero -', c, boot(df['r_ev'] - df[c], df['annuncio']), '| evento orario senza uscita -', c, boot(df['r_ev_ore'] - df[c], df['annuncio']))
print('mediana r30 evento', df['r30_ev'].median(), 'rango volume medio', df['vol30_rango'].mean())
df.to_csv('/tmp/revisore107/pari.csv', index=False)
