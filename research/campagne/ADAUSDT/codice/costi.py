"""Costo di un giro (commissioni e slippage, andata e ritorno) in R, con la distanza tipica dello stop
per timeframe (mediana di ATR(14)/close sui dati di costruzione). Nessuna strategia: solo i prezzi.
Controlla anche che le classi delle varianti si preparino senza errori (nessun conteggio di trade)."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402

giro = 2 * (C.PARAM.commissione_per_lato + C.PARAM.slippage_per_lato)
out = {"costo_giro_pct": giro * 100}
for tf in ["15m", "30m", "1h", "4h", "8h", "1d"]:
    D = C.carica(tf)
    A = C.arrays(D["candele"])
    a = C.atr(A["h"], A["l"], A["c"], 14) / A["c"]
    med = float(np.nanmedian(a))
    out[tf] = {"atr14_mediana_pct": round(med * 100, 3),
               "costo_R_stop_1atr": round(giro / med, 3), "costo_R_stop_2atr": round(giro / (2 * med), 3),
               "costo_R_stop_3atr": round(giro / (3 * med), 3)}
if len(sys.argv) > 1 and sys.argv[1] == "prova_classi":
    import varianti as V
    for k, v in V.VARIANTI.items():
        D = C.carica(v.tf)
        P = v.prepara(D)
        v.segnale(len(D["candele"]) - 1, P)
        out.setdefault("classi_ok", []).append(k)
(C.RADICE / "research" / "data" / "insample" / "ADAUSDT" / "costi.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
