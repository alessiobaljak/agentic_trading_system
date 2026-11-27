import numpy as np, pandas as pd, collections, time
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq, esecuzione as es, cinquantunesima as cu
from research.programma7 import prima as pr
from research.programma7.revisione_g1n import nucleo as n
t_ini = time.time()
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
fine = t0 + T - 1
giorni = np.arange(se.INIZIO, fine + 1, dtype=np.int64); idx = giorni - t0
U = n.universo_giorni(pan, idx)
W, _, _ = n.pesi(pan, idx, U)
R = sc.rendimenti(pan)[idx]
D = cu.variazioni(W, R)
mesi = pd.to_datetime(giorni * 86400, unit="s").to_period("M").astype(str)
tot = collections.Counter(); senza = collections.Counter(); per_moneta = collections.Counter()
for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
    b = es.ore_di(pan["simboli"][j])
    ore = set(b.index.tolist()) if not b.empty else set()
    for k in np.flatnonzero(np.abs(D[:, j]) > 1e-9):
        h = int(giorni[k]) * 24
        tot[mesi[k]] += 1
        if h not in ore or h + 1 not in ore:
            senza[mesi[k]] += 1; per_moneta[pan["simboli"][j]] += 1
print("variazioni senza candele a 1 ora (vanno a mercato), per anno:")
anni = sorted({m[:4] for m in tot})
for a in anni:
    t_ = sum(v for m, v in tot.items() if m.startswith(a)); s_ = sum(v for m, v in senza.items() if m.startswith(a))
    print(f"  {a}: {s_} su {t_} ({100*s_/max(1,t_):.1f}%)")
print("ultimi mesi:", {m: f"{senza[m]}/{tot[m]}" for m in sorted(tot)[-4:]})
print("monete con piu' variazioni senza ore:", per_moneta.most_common(12))
print("secondi", round(time.time() - t_ini))
