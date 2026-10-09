"""Secondo controllo positivo (Fase 5): short su candele 1d e short su 4h, con lookahead dichiarato.

Il primo controllo (controllo.py) copriva solo il long su 1h. Questo verifica che gli strumenti
vedano un vantaggio anche dal lato short e sui timeframe lenti usati dalla campagna, e che il
ritardo di una barra lo faccia crollare. Scrive data/insample/BCHUSDT/controllo2.json.
"""
import json

import numpy as np

from research.campagne.BCHUSDT.codice import comune, indicatori as ind
from research.campagne.BCHUSDT.codice.controllo import ridotto


class ControlloShort(comune.Variante):
    direzione = "short"
    riscaldamento = 20

    def __init__(self, tf, soglia):
        self.id, self.tf, self.soglia = f"CONTROLLO-SHORT-{tf}", tf, soglia

    def prepara(self, serie):
        c = serie["close"]
        futuro = np.full(len(c), np.nan)
        futuro[:-1] = c[1:] / c[:-1] - 1  # LOOKAHEAD VOLUTO
        return {"atr": ind.atr(serie["high"], serie["low"], c, 14), "futuro": futuro}

    def stop_target(self, x, serie, i):
        a = x["atr"][i]
        if not np.isfinite(a):
            return None
        return serie["close"][i] + 2 * a, None

    def condizione(self, x, serie, i):
        return bool(x["futuro"][i] < -self.soglia)

    def esci(self, x, serie, i, barre_tenute, pos):
        return barre_tenute >= 1


def main():
    out = {}
    for tf, soglia in (("1d", 0.01), ("4h", 0.005)):
        v = ControlloShort(tf, soglia)
        out[tf] = {"senza_ritardo": ridotto(comune.esamina(v)),
                   "ritardo_1": ridotto(comune.esamina(v, ritardo_barre=1, con_a=False))}
    (comune.CARTELLA_DATI / "controllo2.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for tf, r in out.items():
        print(tf, "senza ritardo t_b", r["senza_ritardo"]["baseline_b"]["t"], "R", r["senza_ritardo"]["metriche"]["r_medio"],
              "trade", r["senza_ritardo"]["metriche"]["trade"],
              "| ritardo t_b", r["ritardo_1"]["baseline_b"]["t"], "R", r["ritardo_1"]["metriche"]["r_medio"])


if __name__ == "__main__":
    main()
