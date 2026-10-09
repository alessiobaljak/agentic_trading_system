"""Mostra le metriche principali di una voce 'risultato' del log. Uso: python mostra.py BNBUSDT-045"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402

for v in registro.leggi():
    if v["id"] == sys.argv[1] and v["tipo"] == "risultato":
        m = v.get("metriche", {})
        for k in ("trade", "trade_per_anno", "r_medio_per_anno", "profit_factor", "drawdown_max", "rendimento_totale",
                  "violazioni_liquidazione", "trade_ridotti", "esiti", "costi_medi_r", "funding_medio_r", "win_rate",
                  "r_mediano"):
            print(k, m.get(k))
        for k in ("blocco", "durata_media_barre", "btc_stessa_finestra", "buy_and_hold_per_anno", "percentile_caso"):
            print(k, v.get(k))
        for k in ("baseline_a", "baseline_b"):
            print(k, v.get(k))
