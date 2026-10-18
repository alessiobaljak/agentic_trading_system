"""J-004 — Il rimbalzo dopo i crolli di un giorno (monete fuori dalla fase 1) (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/J-004/calcolo.py C2|V2"""
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
VARIANTI = {"J-004a": {"cella": "F1 w24 k3 giu h24", "verso": "contro"}, "J-004b": {"cella": "F1 w4 k5 giu h24", "verso": "contro"}, "J-004c": {"cella": "F1 w24 k3 giu h72", "verso": "contro"}}
PARENTE_R = True

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C2"
    if periodo == "C2":
        monete = MONETE_F2
    else:
        monete = tuple(s for s in CENTO if not (PARENTE_R and s in FASE1))
    aggrega("J-004", VARIANTI, periodo, QUI, per_moneta_cella, monete=monete)
    print(scrivi("J-004", periodo))
