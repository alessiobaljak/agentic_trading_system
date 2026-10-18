"""J-003 — La salita di un'ora con il premio sullo spot (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/J-003/calcolo.py C2|V2"""
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
VARIANTI = {"J-003a": {"cella": "P3 w1 su senza premio h12", "verso": "segue"}, "J-003b": {"cella": "P3 w1 su premio h24", "verso": "segue"}, "J-003c": {"cella": "P3 w4 su senza premio h12", "verso": "segue"}}
PARENTE_R = False

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C2"
    if periodo == "C2":
        monete = MONETE_F2
    else:
        monete = tuple(s for s in CENTO if not (PARENTE_R and s in FASE1))
    aggrega("J-003", VARIANTI, periodo, QUI, per_moneta_cella, monete=monete)
    print(scrivi("J-003", periodo))
