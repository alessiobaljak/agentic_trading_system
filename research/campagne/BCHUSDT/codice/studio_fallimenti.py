"""Fase 3: studio dei fallimenti di una variante sui trade di costruzione.

Uso: python -m research.campagne.BCHUSDT.codice.studio_fallimenti <id>

Per ogni trade calcola, alla barra del segnale (quella prima dell'ingresso), alcune
caratteristiche e stampa l'R medio per terzili di ciascuna: rendimento a 7 e 30
barre, distanza dalla media a 50 barre, volatilita' (ATR / prezzo), funding.
Scrive il resoconto in data/insample/BCHUSDT/fallimenti_<id>.json.
"""
import json
import sys

import numpy as np

from research.campagne.BCHUSDT.codice import comune, indicatori as ind, varianti


def main():
    vid = sys.argv[1]
    v = varianti.VARIANTI[vid]()
    s = comune.carica(v.tf, "costruzione")
    trades = json.loads((comune.CARTELLA_DATI / "trade" / f"{vid}.json").read_text(encoding="utf-8"))
    c = s["close"]
    car = {
        "rend_7": ind.rendimento(c, 7),
        "rend_30": ind.rendimento(c, 30),
        "dist_media_50": c / ind.sma(c, 50) - 1,
        "atr_su_prezzo": ind.atr(s["high"], s["low"], c, 14) / c,
    }
    idx = np.searchsorted(s["ts"], [t["ts_entrata"] for t in trades]) - 1
    r = np.array([t["r"] for t in trades])
    out = {"trade": len(trades), "r_medio": float(r.mean()), "per_caratteristica": {}}
    for nome, arr in car.items():
        x = arr[idx]
        ok = np.isfinite(x)
        q = np.quantile(x[ok], [1 / 3, 2 / 3])
        gruppi = [ok & (x <= q[0]), ok & (x > q[0]) & (x <= q[1]), ok & (x > q[1])]
        out["per_caratteristica"][nome] = {
            "confini": [round(float(z), 4) for z in q],
            "r_medio_terzili": [round(float(r[g].mean()), 4) for g in gruppi],
            "trade_terzili": [int(g.sum()) for g in gruppi],
        }
    esiti = {}
    for t in trades:
        esiti.setdefault(t["esito"], []).append(t["r"])
    out["per_esito"] = {k: {"n": len(x), "r_medio": round(float(np.mean(x)), 4)} for k, x in esiti.items()}
    (comune.CARTELLA_DATI / f"fallimenti_{vid}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
