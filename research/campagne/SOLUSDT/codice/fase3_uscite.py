"""Fase 3, uscite: cosa fa il prezzo dopo l'uscita a tempo e dopo lo stop (solo dati di costruzione, sola lettura).

  python fase3_uscite.py <ID> <barre_dopo>

Per ogni trade della variante: movimento a favore (nella direzione del trade) del close a
<barre_dopo> barre dall'uscita rispetto al prezzo d'uscita, in unita' di rischio iniziale
(|entrata - stop|), senza costi. Per i trade usciti per stop: dove sarebbe stato il close
alla barra dell'uscita a tempo (6 barre dall'ingresso per le varianti a 6 barre), in R lordo.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

vid, dopo = sys.argv[1], int(sys.argv[2])
tf, costr = VARIANTI[vid][0], VARIANTI[vid][1]
s = comune.carica(tf, "costruzione")
ris = comune.motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(s, costr)(), comune.PARAMETRI)
indice = {c.ts: k for k, c in enumerate(s.last)}
close = comune.arr(s.last, "close")
passo = comune.ms_tf(tf)
dopo_tempo, stop_alla_scadenza = [], []
for t in ris.trades:
    lato = 1 if t.direzione == "long" else -1
    rischio = abs(t.entrata - t.stop)
    i_ing = indice[t.ts_entrata]
    if t.esito == "segnale":
        i_usc = indice.get(t.ts_uscita)
        if i_usc is not None and i_usc + dopo < len(close):
            dopo_tempo.append(lato * (close[i_usc + dopo] - t.uscita) / rischio)
    elif t.esito == "stop":
        j = i_ing + 5  # ultima barra tenuta con l'uscita a tempo dopo 6 barre
        if j < len(close):
            stop_alla_scadenza.append(lato * (close[j] - t.entrata) / rischio)
out = {"id": vid, "trade": len(ris.trades),
       "uscite_a_tempo": len(dopo_tempo),
       "movimento_a_favore_dopo_uscita_R_medio": round(float(np.mean(dopo_tempo)), 4) if dopo_tempo else None,
       "quota_a_favore_dopo_uscita": round(float(np.mean(np.array(dopo_tempo) > 0)), 3) if dopo_tempo else None,
       "stop": len(stop_alla_scadenza),
       "stop_close_alla_scadenza_R_medio": round(float(np.mean(stop_alla_scadenza)), 4) if stop_alla_scadenza else None,
       "stop_che_sarebbero_in_guadagno": int(np.sum(np.array(stop_alla_scadenza) > 0)) if stop_alla_scadenza else None,
       "stop_sotto_meno_2R": int(np.sum(np.array(stop_alla_scadenza) < -2)) if stop_alla_scadenza else None}
print(json.dumps(out))
