"""I-004 — rapporti long/short agli estremi, orizzonte un giorno (scheda.md).
Uso: PYTHONPATH=. python3 research/programma5/idee/I-004/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_giorno import per_moneta_i004
from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-004a": {"regola": "contro_tutti"},
            "I-004b": {"regola": "con_grandi"},
            "I-004c": {"regola": "grandi_non_tutti"}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-004", VARIANTI, periodo, Path(__file__).parent, per_moneta_i004)
    print(scrivi("I-004", periodo))
