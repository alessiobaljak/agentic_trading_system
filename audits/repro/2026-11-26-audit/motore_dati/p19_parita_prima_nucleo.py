import numpy as np
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq
from research.programma7 import prima as pr
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - t0
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
sig = ot.sigma_30(pan, idx)
W1 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
U2 = n.universo_giorni(pan, idx)
W2, _, _ = n.pesi(pan, idx, U2)
print("universo uguale in", int((Ud == U2).all(axis=1).sum()), "giorni su", len(idx))
d = np.abs(W1 - W2).max(axis=1)
print("pesi: scarto massimo %.2e; giorni con scarto > 1e-9: %d" % (d.max(), int((d > 1e-9).sum())))
if (d > 1e-9).any():
    k = int(np.argmax(d)); print("  il peggiore", sc.data(int(giorni[k])), [(pan["simboli"][j], round(W1[k,j],4), round(W2[k,j],4)) for j in np.flatnonzero(np.abs(W1[k]-W2[k])>1e-9)][:6])
