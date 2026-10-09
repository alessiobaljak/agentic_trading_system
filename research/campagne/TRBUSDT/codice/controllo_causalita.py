"""Controllo che le varianti non guardino avanti: condizione e segnale calcolati sulla serie
troncata alla barra k devono coincidere con quelli calcolati sulla serie intera, per ogni i < k.
Non guarda risultati: solo condizioni e segnali. Scrive l'esito in data/insample/TRBUSDT/causalita.json.
"""

import json
import sys

from research.campagne.TRBUSDT.codice import banco
from research.campagne.TRBUSDT.codice import varianti as V

USCITA = banco.RADICE / "data" / "insample" / "TRBUSDT" / "causalita.json"


def controlla(id_, variante=None):
    v = variante or V.VARIANTI[id_]()
    candele = banco.carica(v.timeframe)["candele"]
    n = len(candele)
    tagli = [n // 3, (2 * n) // 3]
    piena = v.prepara(candele)
    differenze = 0
    controllate = 0
    for k in tagli:
        corta = v.prepara(candele[:k])
        for i in range(max(0, k - 3000), k):
            controllate += 1
            c1, c2 = bool(v.condizione(piena, i)), bool(v.condizione(corta, i))
            s1, s2 = v.segnale(piena, i), v.segnale(corta, i)
            if c1 != c2 or (s1 is None) != (s2 is None) or (s1 is not None and abs(s1.stop - s2.stop) > 1e-9):
                differenze += 1
    return {"id": id_, "controllate": controllate, "differenze": differenze}


if __name__ == "__main__":
    ids = sys.argv[1:] or list(V.VARIANTI)
    esiti = [controlla(i) for i in ids]
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(esiti, f, indent=1)
    print(json.dumps(esiti))
