import numpy as np, pandas as pd
from research.programma6 import seconda as sc, sesta as se, esecuzione as es, cinquantunesima as cu
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
giorni = np.arange(sc.giorno(2026, 9, 1), t0 + T, dtype=np.int64); idx = giorni - t0
U = n.universo_giorni(pan, idx); W, _, _ = n.pesi(pan, idx, U)
R = sc.rendimenti(pan)[idx]; D = cu.variazioni(W, R)
costo = sc.costi_moneta(pan["simboli"])
nov = giorni >= sc.giorno(2026, 11, 1)
extra = 0.0; peso_senza = 0.0; peso_tot = 0.0
for j in np.flatnonzero(np.abs(D[nov]).sum(axis=0) > 0):
    b = es.ore_di(pan["simboli"][j]); ore = set(b.index.tolist()) if not b.empty else set()
    for k in np.flatnonzero(nov & (np.abs(D[:, j]) > 1e-9)):
        h = int(giorni[k]) * 24; peso_tot += abs(D[k, j])
        if h not in ore or h + 1 not in ore:
            peso_senza += abs(D[k, j]); extra += abs(D[k, j]) * (costo[j] - 0.0002)
print("novembre: peso scambiato senza candele orarie %.1f%% del totale; costo in piu' contato dalla ricerca (a mercato invece che a limite, senza il movimento contro) %.2f punti in %d giorni" % (100 * peso_senza / peso_tot, 100 * extra, int(nov.sum())))
