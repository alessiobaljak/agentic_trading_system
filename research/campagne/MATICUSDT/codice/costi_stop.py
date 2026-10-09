"""Costo di un giro in R con la distanza tipica dello stop (lezioni/metodo.md: previsioni al netto dei costi).

Solo la volatilita' (ATR(14) / close, mediana sulla costruzione): nessuna strategia, nessun rendimento.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402

giro = 2 * (0.0005 + quadro.SLIPPAGE_SCHEDA)
out = {}
for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    s = quadro.carica(tf)
    a = quadro.atr(s, 14) / s.c
    m = float(np.nanmedian(a[~s.vietato]))
    out[tf] = {"atr14_mediano_pct": round(100 * m, 3),
               "costo_giro_in_R_stop_2atr": round(giro / (2 * m), 3)}
testo = json.dumps(out)
(Path(__file__).resolve().parents[1] / "costi_stop.json").write_text(testo)
print(testo)
