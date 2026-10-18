"""I-015 — la moneta dopo una discesa sua, coperta con BTC (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-015/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i015
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-015a": {"w": 1, "k": 3, "h": 4}, "I-015b": {"w": 4, "k": 2, "h": 24}, "I-015c": {"w": 1, "k": 2, "h": 24}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-015", VARIANTI, periodo, Path(__file__).parent, per_moneta_i015)
    print(scrivi("I-015", periodo))
