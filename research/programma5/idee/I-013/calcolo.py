"""I-013 — la moneta dopo una scossa sua (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-013/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i013
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-013a": {"w": 4, "k": 3, "lato": "giu", "h": 1}, "I-013b": {"w": 4, "k": 3, "lato": "giu", "h": 4}, "I-013c": {"w": 4, "k": 3, "lato": "su", "h": 24}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-013", VARIANTI, periodo, Path(__file__).parent, per_moneta_i013)
    print(scrivi("I-013", periodo))
