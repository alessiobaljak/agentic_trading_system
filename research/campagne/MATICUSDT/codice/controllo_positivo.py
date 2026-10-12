"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge DI PROPOSITO la barra dopo.

Long su 4h quando la barra SUCCESSIVA chiude sopra la sua apertura (lookahead dichiarato), stop a
2 ATR(14) sotto la chiusura, uscita dopo 1 barra. Deve battere nettamente la (b) e crollare con
il ritardo di una barra. Non e' una variante, non consuma budget: si registra come nota.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402


def regole(s):
    a = quadro.atr(s, 14)
    dopo_su = np.zeros(s.n, dtype=bool)
    dopo_su[:-1] = s.c[1:] > s.o[1:]  # LOOKAHEAD voluto
    return quadro.Regole(s, "long", dopo_su & ~np.isnan(a), s.c - 2 * a, tenuta=1)


uscita = {}
for rit in (0, 1):
    r = quadro.valuta(regole, "4h", ritardo=rit, con_baseline_a=False)
    uscita[f"ritardo_{rit}"] = {"trade": r["metriche"]["trade"], "r_medio": r["metriche"]["r_medio"],
                                "baseline_b": r["baseline_b"], "percentile_caso": r.get("percentile_caso")}
testo = json.dumps(uscita, ensure_ascii=False)
(quadro.RADICE_REPO / "research" / "data" / "insample" / "MATICUSDT" / "controllo_positivo.json").write_text(testo)
print(testo)
