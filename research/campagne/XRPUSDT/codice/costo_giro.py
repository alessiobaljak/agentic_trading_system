"""Costo di un giro (commissioni + slippage, andata e ritorno) in R, con la distanza tipica dello stop.

Solo costruzione. Distanza dello stop = k x ATR(14) / close, mediana sulle barre. Nessun risultato di strategie.
"""
import numpy as np

from research.campagne.XRPUSDT.codice import quadro as q

GIRO = 2 * (0.0005 + 0.0002)  # 0,14% del nozionale
for tf in ["15m", "30m", "1h", "2h", "4h", "8h", "1d"]:
    s = q.serie(tf)
    a = q.atr(s, 14) / s["close"]
    med = float(np.nanmedian(a))
    righe = [f"{k}ATR: stop {k * med * 100:.2f}% -> costo {GIRO / (k * med):.3f} R" for k in (1.5, 2.0, 2.5)]
    print(tf, f"ATR14 mediana {med * 100:.2f}% |", " | ".join(righe))
