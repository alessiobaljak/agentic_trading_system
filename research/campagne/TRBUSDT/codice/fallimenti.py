"""Fase 3: studio dei fallimenti di una variante gia' testata, SOLO sui dati di costruzione.

Ripete il test (stesse regole, stessi dati) e divide i trade per: distanza dello stop in
percentuale (quintili), esito dell'uscita, ora di ingresso, anno. Scrive in
data/insample/TRBUSDT/fallimenti_<id>.json. Nessun nuovo test di variante.
"""

import json
import sys
from datetime import datetime, timezone

import numpy as np

from research.src import motore
from research.campagne.TRBUSDT.codice import banco
from research.campagne.TRBUSDT.codice import varianti as V


def gruppi(trades, chiave):
    out = {}
    for t in trades:
        out.setdefault(chiave(t), []).append(t)
    return {str(k): {"n": len(v), "r_medio": round(float(np.mean([x.r for x in v])), 3),
                     "r_lordo_medio": round(float(np.mean([x.pnl_lordo / x.rischio_iniziale for x in v])), 3)}
            for k, v in sorted(out.items())}


if __name__ == "__main__":
    id_ = sys.argv[1]
    v = V.VARIANTI[id_]()
    d = banco.carica(v.timeframe)
    ris = motore.esegui(d["candele"], None, d["mark"], d["funding"], banco.crea(v, d)(), banco.parametri())
    tr = ris.trades
    dist = np.array([abs(t.entrata - t.stop) / t.entrata for t in tr])
    q = np.quantile(dist, [0.2, 0.4, 0.6, 0.8])
    out = {
        "n": len(tr),
        "quintili_distanza_stop_pct": [round(100 * x, 2) for x in q],
        "per_quintile_distanza": gruppi(tr, lambda t: int(np.searchsorted(q, abs(t.entrata - t.stop) / t.entrata))),
        "per_esito": gruppi(tr, lambda t: t.esito),
        "per_ora_ingresso": gruppi(tr, lambda t: datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour // 4 * 4),
        "per_anno": gruppi(tr, lambda t: datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year),
        "costo_medio_in_R": round(float(np.mean([(t.commissioni + t.slippage_costo) / t.rischio_iniziale for t in tr])), 3),
    }
    with open(banco.RADICE / "data" / "insample" / "TRBUSDT" / f"fallimenti_{id_}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
