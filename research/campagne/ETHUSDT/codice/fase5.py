"""Fase 5: la sfida dello scettico, con numeri presi dal log (nessun nuovo test sui prezzi).

Domanda: le varianti "nette" contro la (b) sono piu' di quelle che il caso darebbe?
Con varianti senza vantaggio la regola «nettamente» esce in circa il 2,275% dei casi
(coda della soglia; sezione 11 dice fra lo 0 e il 2% nelle simulazioni del 7 ottobre).
Si conta quante delle varianti testate sono nette (t oltre la soglia) e quante hanno t
sotto meno la soglia, e si calcola la probabilita' binomiale di vederne almeno tante.
Scrive data/insample/ETHUSDT/lavoro/fase5.json.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import registro  # noqa: E402

P_NULLA = 1 - 0.97725


def coda_binomiale(n, k, p):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def main() -> None:
    voci = registro.voci()
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
    ris = [v for v in voci if v["tipo"] == "risultato" and v["id"] in reg]
    t = [(v["id"], reg[v["id"]]["variante_ipotesi"], float(v["baseline_b"]["t"]), float(v["baseline_b"]["soglia"]),
          bool(v["baseline_b"]["netta"]), float(v["metriche"]["r_medio"])) for v in ris]
    n = len(t)
    nette = [x for x in t if x[4]]
    sotto = [x for x in t if x[2] < -x[3]]
    out = {
        "varianti": n,
        "nette_contro_b": [(x[0], x[1], round(x[2], 3), round(x[5], 4)) for x in nette],
        "t_sotto_meno_soglia": [(x[0], x[1], round(x[2], 3)) for x in sotto],
        "attese_nette_per_caso": n * P_NULLA,
        "prob_almeno_tante_nette_per_caso": coda_binomiale(n, len(nette), P_NULLA),
        "prob_almeno_tante_sotto_per_caso": coda_binomiale(n, len(sotto), P_NULLA),
        "media_t": sum(x[2] for x in t) / n,
        "varianti_t_positivo": sum(1 for x in t if x[2] > 0),
        "nette_con_r_positivo": [x[0] for x in nette if x[5] > 0],
    }
    (comune.LAVORO / "fase5.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
