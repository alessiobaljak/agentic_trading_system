"""I-010 — il rimbalzo dopo i crolli di qualche ora (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-010/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i010
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-010a": {"w": 4, "k": 5, "h": 12}, "I-010b": {"w": 4, "k": 4, "h": 12}, "I-010c": {"w": 24, "k": 3, "h": 4}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-010", VARIANTI, periodo, Path(__file__).parent, per_moneta_i010)
    print(scrivi("I-010", periodo))
