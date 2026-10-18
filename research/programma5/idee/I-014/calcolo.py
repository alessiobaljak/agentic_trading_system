"""I-014 — le altre monete dopo uno strappo in su di BTC (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-014/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i014
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-014a": {"w": 1, "k": 4, "h": 72}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-014", VARIANTI, periodo, Path(__file__).parent, per_moneta_i014)
    print(scrivi("I-014", periodo))
