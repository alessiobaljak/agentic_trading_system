"""I-011 — la rottura del massimo di 60 giorni (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-011/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i011
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-011a": {"N": 60, "h": 72}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-011", VARIANTI, periodo, Path(__file__).parent, per_moneta_i011)
    print(scrivi("I-011", periodo))
