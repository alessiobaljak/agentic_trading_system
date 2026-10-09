"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge DI PROPOSITO la
barra successiva deve battere nettamente il caso e crollare col ritardo di una barra.
Non e' una variante: si registra come nota, prima e dopo. Controlla anche che la baseline (b) a
pezzi paralleli dia per ogni seme gli stessi valori di simula_baseline_casuale in un colpo solo.
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import registro  # noqa: E402
from research.src import motore  # noqa: E402
from research.src.motore import Segnale  # noqa: E402


class Sbirciata(C.Variante):
    tf = "1h"
    direzione = "long"

    def prepara(self, D):
        A = C.arrays(D["candele"])
        su = np.zeros(len(A["c"]), dtype=bool)
        su[:-1] = A["c"][1:] > A["o"][1:]  # LOOKAHEAD VOLUTO: la barra dopo
        return {"c": A["c"], "atr": C.atr(A["h"], A["l"], A["c"], 14), "su": su}

    def segnale(self, i, P):
        if np.isnan(P["atr"][i]):
            return None
        return Segnale("long", P["c"][i] - 2 * P["atr"][i])

    def condizione(self, i, P):
        return bool(P["su"][i])

    def uscita(self, i, P, barre):
        return barre >= 1


def riassunto(v):
    return {"trade": v["metriche"]["trade"], "r_medio": v["metriche"]["r_medio"],
            "t_b": v["baseline_b"].get("t"), "netta_b": v["baseline_b"].get("netta"),
            "t_a": v["baseline_a"].get("t"), "netta_a": v["baseline_a"].get("netta"),
            "media_b": v["baseline_b"].get("media"), "percentile": v.get("percentile_caso")}


if __name__ == "__main__":
    var = Sbirciata()
    # 1) equivalenza della (b) a pezzi su 8 semi
    D = C.carica("1h")
    F = C.Fabbriche(var, D)
    vietate, _ = F.barre_vietate(C.PARAM)
    uno = motore.simula_baseline_casuale(D["candele"], F.crea_casuale, 300, 2, C.PARAM, None, D["mark"],
                                         D["funding"], vietate, n_simulazioni=8, primo_seme=0)
    pezzi = C.baseline_b(D["candele"], D["mark"], D["funding"], F.crea_casuale, 300, 2, C.PARAM, vietate,
                         n_sim=8, processi=4)
    uguali = list(map(float, uno["valori"])) == list(map(float, pezzi["valori"]))
    # 2) controllo positivo, senza e con ritardo
    v0 = C.valuta(var, extra=False)
    v1 = C.valuta(var, replace(C.PARAM, ritardo_barre=1), extra=False)
    esito = {"equivalenza_b_a_pezzi_8_semi": uguali, "senza_ritardo": riassunto(v0), "ritardo_1": riassunto(v1)}
    print(json.dumps(esito, indent=1))
    ok = uguali and v0["baseline_b"]["netta"] and (v1["baseline_b"]["t"] < 0.5 * v0["baseline_b"]["t"])
    registro.aggiungi({"id": "ADAUSDT-N008", "tipo": "nota",
                       "testo": "Controllo positivo degli strumenti: esito (strategia Sbirciata, 1h long, legge la barra dopo; uscita dopo una barra; stop 2 ATR(14)). Deve battere nettamente la (b) e crollare col ritardo di una barra.",
                       "esito": esito, "superato": bool(ok)})
