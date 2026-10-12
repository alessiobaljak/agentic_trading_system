"""Costo di un giro (andata e ritorno) in R per stop tipici, per le previsioni al netto dei costi.

Usa solo l'ATR mediano in costruzione (una misura di volatilita', non un risultato di strategia).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import indicatori as I  # noqa: E402

GIRO = 2 * (0.0005 + 0.0002)
for tf in ["15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d"]:
    c = C.fino_a_costruzione(C.serie(tf)["candele"])
    a = I.atr(c, 14) / I.arr(c, "close")
    med = float(np.nanmedian(a))
    print(tf, "ATR mediano %", round(100 * med, 2), "| costo giro in R con stop 2 ATR:", round(GIRO / (2 * med), 3),
          "| con stop 3 ATR:", round(GIRO / (3 * med), 3))
