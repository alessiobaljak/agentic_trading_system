"""J-007 — La giornata in salita che continua fino a mezzanotte (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/J-007/calcolo.py C2|V2"""
import json
import sys
from pathlib import Path

from research.programma5.strumenti.fase2 import MONETE_F2
from research.programma5.strumenti.idee_fase2 import per_moneta_cella
from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.rapporto import scrivi
from research.programma5.strumenti.scarico import MONETE as FASE1

QUI = Path(__file__).parent
CENTO = json.loads((QUI.parents[1] / "universo_top100.json").read_text())["scelte"]
VARIANTI = {"J-007a": {"cella": "W3 giornata k1 su", "verso": "segue"}, "J-007b": {"cella": "W3 giornata k2 su", "verso": "segue"}}
PARENTE_R = False

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C2"
    if periodo == "C2":
        monete = MONETE_F2
    else:
        monete = tuple(s for s in CENTO if not (PARENTE_R and s in FASE1))
    aggrega("J-007", VARIANTI, periodo, QUI, per_moneta_cella, monete=monete)
    print(scrivi("J-007", periodo))
