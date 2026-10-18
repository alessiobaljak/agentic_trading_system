"""I-019 — la moneta dopo una salita sua, coperta con BTC (scheda.md).
Uso: PYTHONPATH=. python3 research/programma5/idee/I-019/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore2 import per_moneta_i019
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-019a": {"w": 4, "k": 3, "h": 72}, "I-019b": {"w": 4, "k": 2, "h": 24}, "I-019c": {"w": 4, "k": 2, "h": 72}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-019", VARIANTI, periodo, Path(__file__).parent, per_moneta_i019)
    print(scrivi("I-019", periodo))
