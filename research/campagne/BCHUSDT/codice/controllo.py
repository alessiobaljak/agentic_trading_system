"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge di proposito
la barra successiva deve battere nettamente il caso e crollare con il ritardo di una barra.

Non e' una variante e non consuma budget: si registra come nota prima e dopo.
Scrive il resoconto in data/insample/BCHUSDT/controllo.json.
"""
import json

import numpy as np

from research.campagne.BCHUSDT.codice import comune, indicatori as ind


class ControlloLookahead(comune.Variante):
    id = "CONTROLLO"
    tf = "1h"
    direzione = "long"
    riscaldamento = 20

    def prepara(self, serie):
        c = serie["close"]
        futuro = np.full(len(c), np.nan)
        futuro[:-1] = c[1:] / c[:-1] - 1  # LOOKAHEAD VOLUTO: rendimento della barra dopo
        return {"atr": ind.atr(serie["high"], serie["low"], c, 14), "futuro": futuro}

    def stop_target(self, x, serie, i):
        a = x["atr"][i]
        if not np.isfinite(a):
            return None
        return serie["close"][i] - 2 * a, None

    def condizione(self, x, serie, i):
        return bool(x["futuro"][i] > 0.004)

    def esci(self, x, serie, i, barre_tenute, pos):
        return barre_tenute >= 2


def ridotto(r):
    return {k: v for k, v in r.items() if k != "_trades"}


def main():
    v = ControlloLookahead()
    serie = comune.carica(v.tf, "costruzione")
    causalita = comune.verifica_causalita(v, serie)
    senza = comune.esamina(v)
    ritardo = comune.esamina(v, ritardo_barre=1, con_a=False)
    out = {"causalita_differenze": causalita[:10], "n_differenze": len(causalita),
           "senza_ritardo": ridotto(senza), "ritardo_1": ridotto(ritardo)}
    (comune.CARTELLA_DATI / "controllo.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("fatto")


if __name__ == "__main__":
    main()
