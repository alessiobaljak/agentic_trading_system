"""Controllo: i09_generale a 30m con i valori predefiniti da' gli stessi trade dei candidati registrati.

Confronta istanti, prezzi e R dei trade (motore.esegui sul periodo di costruzione). Sola lettura.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI, i09_generale  # noqa: E402

GENERALE = {
    "SOLUSDT-015": i09_generale("short"),
    "SOLUSDT-023": i09_generale("short", filtro_sma200=True),
    "SOLUSDT-024": i09_generale("short", filtro_giorno=True),
    "SOLUSDT-026": i09_generale("short", filtro_sma200=True, k_stop=3.0),
    "SOLUSDT-027": i09_generale("short", filtro_giorno=True, k_stop=3.0),
}
s = comune.carica("30m", "costruzione")
for vid, gen in GENERALE.items():
    a = comune.motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(s, VARIANTI[vid][1])(), comune.PARAMETRI).trades
    b = comune.motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(s, gen)(), comune.PARAMETRI).trades
    uguali = len(a) == len(b) and all((x.ts_entrata, x.ts_uscita, x.entrata, x.uscita, x.r) == (y.ts_entrata, y.ts_uscita, y.entrata, y.uscita, y.r) for x, y in zip(a, b))
    print(vid, "trade", len(a), len(b), "identici:", uguali)
