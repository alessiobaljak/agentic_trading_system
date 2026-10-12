"""Costo di un giro in R per timeframe (lezioni/metodo.md: previsioni al netto dei costi).

ATR(14) mediano in percentuale del prezzo sui dati di costruzione, e costo di un giro
(0,14% del nozionale) diviso per la distanza tipica dello stop. Solo dati, nessun risultato.
"""

import json

import numpy as np

from research.campagne.TRBUSDT.codice import banco
from research.campagne.TRBUSDT.codice import indicatori as ind

if __name__ == "__main__":
    giro = 2 * (0.0005 + banco.SLIPPAGE)
    out = {}
    for tf in ["15m", "30m", "1h", "4h", "8h", "1d"]:
        o, h, l, c, v, ts = ind.colonne(banco.carica(tf)["candele"])
        a = ind.atr(h, l, c, 14) / c
        med = float(np.nanmedian(a))
        out[tf] = {"atr_mediano_pct": round(100 * med, 3),
                   "costo_giro_in_R_stop_1atr": round(giro / med, 3),
                   "costo_giro_in_R_stop_2atr": round(giro / (2 * med), 3)}
    with open(banco.CARTELLA / "costi_in_r.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
