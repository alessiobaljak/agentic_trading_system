import sys
from collections import Counter
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq
from research.programma7 import prima as pr
pan = sc.pannello(); t0 = pan["t0"]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - t0
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
sig = ot.sigma_30(pan, idx)
W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
O = pan["open"][idx]
morti = (W != 0) & ~np.isfinite(O)
print("giorni-moneta con peso e senza candela:", int(morti.sum()))
print("per giorno:", dict(Counter(sc.data(int(giorni[k])) for k, j in np.argwhere(morti)).most_common(8)))
j = pan["simboli"].index("HBARUSDT")
for d in ((2022, 4, 1), (2022, 4, 2)):
    k = int(np.flatnonzero(giorni == sc.giorno(*d))[0]); print("HBAR", sc.data(int(giorni[k])), "peso %.3f" % W[k, j], "candela", np.isfinite(O[k, j]))
lun = int(np.flatnonzero(ps["lunedi"] == sc.giorno(2022, 2, 28))[0]); print("universo del 28 feb 2022:", int(ps["U"][lun].sum()), "monete")
