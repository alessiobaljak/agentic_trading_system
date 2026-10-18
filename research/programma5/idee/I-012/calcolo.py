"""I-012 — il rimbalzo dopo un'ora di volume enorme in discesa (scheda.md). Uso: PYTHONPATH=. python3 research/programma5/idee/I-012/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.idee_ore import per_moneta_i012
from research.programma5.strumenti.rapporto import scrivi

VARIANTI = {"I-012a": {"k": 5, "h": 4}, "I-012b": {"k": 10, "h": 4}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-012", VARIANTI, periodo, Path(__file__).parent, per_moneta_i012)
    print(scrivi("I-012", periodo))
