"""Fase 3: studio dei trade di una variante testata (solo dati di costruzione, dal file risultati/<id>.json).

    python research/campagne/DYDXUSDT/codice/analisi.py DYDXUSDT-013

Scrive il riepilogo in data/insample/DYDXUSDT/analisi_<id>.json e lo stampa.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

CARTELLA = Path(__file__).resolve().parent.parent
id_ = sys.argv[1]
d = json.loads((CARTELLA / "risultati" / f"{id_}.json").read_text())
tr = d["trades"]
r = np.array([t["r"] for t in tr])
out = {"id": id_, "n": len(tr), "r_medio": float(r.mean()), "mediana": float(np.median(r)),
       "quota_vinti": float((r > 0).mean())}
esiti = {}
for t in tr:
    esiti.setdefault(t["esito"], []).append(t["r"])
out["per_esito"] = {k: {"n": len(v), "r_medio": float(np.mean(v))} for k, v in esiti.items()}
stop_pct = np.array([abs(t["entrata"] - t["stop"]) / t["entrata"] for t in tr])
q = np.quantile(stop_pct, [0, 1 / 3, 2 / 3, 1])
out["per_terzile_stop_pct"] = []
for k in range(3):
    m = (stop_pct >= q[k]) & (stop_pct <= q[k + 1] if k == 2 else stop_pct < q[k + 1])
    out["per_terzile_stop_pct"].append({"da": float(q[k]), "a": float(q[k + 1]), "n": int(m.sum()), "r_medio": float(r[m].mean())})
ore = {}
mesi = {}
giorni = {}
for t in tr:
    g = datetime.fromtimestamp(t["ts_entrata"] / 1000, tz=timezone.utc)
    ore.setdefault(g.hour, []).append(t["r"])
    mesi.setdefault(g.strftime("%Y-%m"), []).append(t["r"])
    giorni.setdefault(g.weekday(), []).append(t["r"])
out["per_ora_ingresso"] = {str(k): [len(v), round(float(np.mean(v)), 3)] for k, v in sorted(ore.items())}
out["per_mese"] = {k: [len(v), round(float(np.mean(v)), 3)] for k, v in sorted(mesi.items())}
out["per_giorno_settimana"] = {str(k): [len(v), round(float(np.mean(v)), 3)] for k, v in sorted(giorni.items())}
ordine = np.argsort(r)
out["peggiori_5"] = [round(float(r[i]), 3) for i in ordine[:5]]
out["migliori_5"] = [round(float(r[i]), 3) for i in ordine[-5:]]
out["funding_totale"] = float(sum(t["funding"] for t in tr))
(CARTELLA.parents[1] / "data" / "insample" / "DYDXUSDT" / f"analisi_{id_}.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
