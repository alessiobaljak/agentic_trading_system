# Solo lettura: rifà le spese di G1 della prova 120 con i dati di oggi, senza scrivere nei risultati della prova.
import numpy as np, pandas as pd
from research.programma6 import cinquantaseiesima as cs, ottava as ot, seconda as sc, sesta as se, terza as te, ventiquattresima as vq
from research.programma7 import prima as pr
pan = sc.pannello(); ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - pan["t0"]
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"]); sig = ot.sigma_30(pan, idx)
W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
R = sc.rendimenti(pan)[idx]; costo = sc.costi_moneta(pan["simboli"])
spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
ref = pd.read_csv("research/programma7/risultati_prima/giorni_G1.csv.gz")
d = np.abs(np.asarray(spese) - ref["spese"].to_numpy())
print("oggi: variazioni", n_tot, "limite", n_lim, "senza candele 1h", n_senza, "spese tot", round(float(np.sum(spese)), 4))
print("riferimento spese tot", round(float(ref["spese"].sum()), 4), "giorni diversi", int((d > 1e-12).sum()))
diff = pd.Series(d, index=pd.to_datetime(giorni * 86400, unit="s")); print("giorni diversi per anno", (diff > 1e-12).groupby(diff.index.year).sum().to_dict())
# per moneta: quali monete hanno meno candele a 1 ora oggi
senza = {}
for j, s in enumerate(pan["simboli"]):
    if not (W[:, j] != 0).any(): continue
    b = cs.es.ore_di(s) if hasattr(cs, "es") else None
    senza[s] = 0 if b is None else len(b)
print("monete usate", len(senza))
