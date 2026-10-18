"""I-003 — continuazione con posizioni nuove (scheda.md). Uso: python3 research/programma5/idee/I-003/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.esplosioni_oi import calcola, riassunto

VARIANTI = {"I-003a": {"L": 8, "verso": 0, "oi": "alto", "trade": "segue", "minuti": 15},
            "I-003b": {"L": 8, "verso": 0, "oi": "alto", "trade": "segue", "minuti": 60},
            "I-003c": {"L": 16, "verso": 0, "oi": "alto", "trade": "segue", "minuti": 60}}

if __name__ == "__main__":
    print(riassunto(calcola("I-003", VARIANTI, sys.argv[1] if len(sys.argv) > 1 else "C", Path(__file__).parent)))
