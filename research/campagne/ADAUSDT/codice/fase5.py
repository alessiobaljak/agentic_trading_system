"""Fase 5, prova dello scettico per il candidato 037: la baseline casuale (b) rifatta entrando a caso SOLO
nelle barre in cui valgono i due filtri (chiusura sopra la media a 20 giorni e BTC in calo nelle 24 ore),
con lo stesso segnale (stop al minimo della prima ora) e la stessa uscita. Se 037 non la batte, il suo
vantaggio viene dallo stato del mercato scelto dai filtri, non dalla rottura dell'intervallo d'apertura.
Solo dati di costruzione. Non e' una variante: si registra come nota prima e dopo."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402
from research.src import motore, statistica  # noqa: E402

var = V.VARIANTI["ADAUSDT-037"]
D = C.carica(var.tf)
F = C.Fabbriche(var, D)
P = F.P
ris = motore.esegui(D["candele"], None, D["mark"], D["funding"], F.crea_strategia(), C.PARAM)
tr = ris.trades
r = [t.r for t in tr]
blocco = statistica.lunghezza_blocco([t.ts_entrata for t in tr], [t.ts_uscita for t in tr])
durata = motore.durata_media_barre(tr, D["passo"])
vietate, _ = F.barre_vietate(C.PARAM)
m = np.zeros(len(D["candele"]), dtype=bool)
for a, b in vietate:
    m[a:b] = True
filtri_ok = np.array([np.isfinite(P["media"][i]) and P["c"][i] > P["media"][i] and np.isfinite(P["btc24"][i]) and P["btc24"][i] < 0
                      for i in range(len(m))])
m |= ~filtri_ok
vietate_f = C.intervalli_da_maschera(m)
base = C.baseline_b(D["candele"], D["mark"], D["funding"], F.crea_casuale, len(tr), durata, C.PARAM, vietate_f)
cmp = statistica.contro_baseline(r, blocco, base)
esito = {"trade": len(tr), "r_medio": float(np.mean(r)), "quota_barre_ammesse": float(1 - m.mean()),
         "b_con_filtri": {"media": base["media"], "t": cmp["t"], "netta": cmp["netta"], "soglia": cmp["soglia"],
                          "trade_per_simulazione_medio": float(np.mean(base["trade_per_simulazione"]))},
         "percentile": statistica.percentile_del_candidato(float(np.mean(r)), base["valori"])}
print(json.dumps(esito, indent=1))
registro.aggiungi({"id": "ADAUSDT-N034", "tipo": "nota", "testo": "Fase 5, prova dello scettico su 037: esito (baseline casuale con i filtri di 037).", "esito": esito})
