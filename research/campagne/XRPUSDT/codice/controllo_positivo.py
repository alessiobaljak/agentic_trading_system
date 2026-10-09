"""Controllo positivo degli strumenti: lookahead dichiarato, deve battere il caso e crollare col ritardo."""
import json
import time

import numpy as np

from research.campagne.XRPUSDT.codice import quadro as q


def prepara(s):
    o, c = s["open"], s["close"]
    fut = np.zeros(len(c), dtype=bool)
    fut[:-1] = c[1:] > o[1:] * 1.003  # LOOKAHEAD voluto: la barra dopo
    a = q.atr(s, 14)
    return {"cond": fut, "stop": c - 1.5 * a, "target": None, "warmup": 14}


v = q.Variante("controllo", "1h", "long", prepara, tenuta=1)
s = q.serie("1h")
out = {}
for rit in (0, 1):
    t0 = time.time()
    r = q.valuta(v, s, q.parametri(ritardo_barre=rit))
    out[f"ritardo_{rit}"] = {
        "trade": r["metriche"]["trade"], "r_medio": r["metriche"]["r_medio"],
        "a_t": r["baseline_a"]["t"], "a_netta": r["baseline_a"]["netta"],
        "b_media": r["baseline_b"].get("media"), "b_t": r["baseline_b"]["t"], "b_netta": r["baseline_b"]["netta"],
        "percentile": r.get("percentile_caso"), "secondi": round(time.time() - t0, 1),
    }
    print(rit, out[f"ritardo_{rit}"], flush=True)
q.scrivi_log({"id": "XRPUSDT-N006", "tipo": "nota", "testo": "Esito del controllo positivo (voce XRPUSDT-N005).",
              "controllo_positivo_esito": q._pulisci(out),
              "superato": bool(out["ritardo_0"]["b_netta"] and out["ritardo_0"]["a_netta"]
                               and out["ritardo_1"]["b_t"] < 0.5 * out["ritardo_0"]["b_t"])})
