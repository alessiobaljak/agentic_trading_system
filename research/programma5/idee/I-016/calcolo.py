"""I-016 — reti d'acquisto sotto il prezzo (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-016/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i016
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-016a": {"k": 6, "H": 240}, "I-016b": {"k": 4, "H": 240}, "I-016c": {"k": 3, "H": 15}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-016", VARIANTI, periodo, Path(__file__).parent, per_moneta_i016)
    print(scrivi("I-016", periodo))
