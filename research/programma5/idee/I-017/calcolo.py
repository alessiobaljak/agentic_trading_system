"""I-017 — il rimbalzo dopo i crolli, provato solo su R (scheda.md).
Uso: PYTHONPATH=. python3 research/programma5/idee/I-017/calcolo.py C|V|scegli|R"""
import json
import sys
from pathlib import Path

import pandas as pd

from research.programma5.strumenti.esplorazione import t_giorni
from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore2 import per_moneta_i017
from research.programma5.strumenti.rapporto import scrivi

QUI = Path(__file__).parent
VARIANTI = {"I-017c1": {"tipo": "limite", "k": 6, "H": 240},
            "I-017c2": {"tipo": "limite", "k": 4, "H": 240},
            "I-017c3": {"tipo": "crollo", "w": 24, "k": 3, "h": 4},
            "I-017c4": {"tipo": "crollo", "w": 4, "k": 5, "h": 12},
            "I-017c5": {"tipo": "sconto", "w": 4, "k": 3, "h": 4},
            "I-017c6": {"tipo": "sconto", "w": 1, "k": 3, "h": 4},
            "I-017c7": {"tipo": "premio_basso", "q": 0.01, "h": 4}}


def scegli() -> list:
    c = json.loads((QUI / "C.json").read_text())
    v = json.loads((QUI / "V.json").read_text())
    righe = []
    for n in VARIANTI:
        if not (c[n].get("trade") and v[n].get("trade")):
            continue
        if not (c[n]["netto"]["media"] > 0 and v[n]["netto"]["media"] > 0):
            continue
        t = pd.concat([pd.read_csv(QUI / f"trade_C_{n}.csv.gz"), pd.read_csv(QUI / f"trade_V_{n}.csv.gz")])
        righe.append((t_giorni(t["netto"].to_numpy(), t["minuto"].to_numpy() // 1440), float(t["netto"].mean()), n))
    righe.sort(reverse=True)
    scelte = [n for _, _, n in righe[:3]]
    (QUI / "scelta.json").write_text(json.dumps({"t_C_V": {n: [t, m] for t, m, n in righe}, "scelte": scelte},
                                                indent=1), encoding="utf-8")
    return scelte


if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    if periodo == "scegli":
        print(scegli())
        sys.exit(0)
    varianti = VARIANTI
    if periodo in ("R", "A"):
        scelte = json.loads((QUI / "scelta.json").read_text())["scelte"]
        varianti = {n: VARIANTI[n] for n in scelte}
    aggrega("I-017", varianti, periodo, QUI, per_moneta_i017)
    print(scrivi("I-017", periodo))
