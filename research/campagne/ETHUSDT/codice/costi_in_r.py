"""Costo di un giro (andata e ritorno: commissioni e slippage) in R, per timeframe.

Serve a scrivere le previsioni al netto dei costi (lezioni/metodo.md). Usa solo la
volatilita' tipica (ATR(14) in percentuale del prezzo, mediana sulla costruzione):
nessuna strategia, nessun risultato. Costo di un giro = 2 x (commissione + slippage)
del nozionale; con uno stop a k ATR il costo in R e' costo / (k x ATR%).
"""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from indicatori import ATR  # noqa: E402


def main() -> None:
    p = comune.parametri()
    giro = 2 * (p.commissione_per_lato + p.slippage_per_lato)
    out = {"costo_giro_frazione_nozionale": giro, "timeframe": {}}
    for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
        s = comune.carica(tf, "costruzione")
        atr = ATR(14)
        pct = []
        for c in s.last:
            atr.aggiorna(c.high, c.low, c.close)
            if atr.valore is not None:
                pct.append(atr.valore / c.close)
        med = statistics.median(pct)
        out["timeframe"][tf] = {
            "atr14_pct_mediana": med,
            "atr14_pct_quartili": statistics.quantiles(pct, n=4),
            "costo_in_R_stop_1_atr": giro / med,
            "costo_in_R_stop_2_atr": giro / (2 * med),
            "quota_barre_con_2_atr_oltre_6pct": sum(1 for x in pct if 2 * x > 0.06) / len(pct),
        }
    uscita = comune.LAVORO / "costi_in_r.json"
    uscita.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for tf, v in out["timeframe"].items():
        print(tf, f"ATR% {v['atr14_pct_mediana']*100:.2f}", f"costo R a 1 ATR {v['costo_in_R_stop_1_atr']:.3f}",
              f"a 2 ATR {v['costo_in_R_stop_2_atr']:.3f}", f"2ATR>6% {v['quota_barre_con_2_atr_oltre_6pct']:.2f}")


if __name__ == "__main__":
    main()
