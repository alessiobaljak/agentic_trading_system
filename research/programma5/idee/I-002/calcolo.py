"""I-002 — ritorno dopo le salite di short liquidati (scheda.md). Uso: python3 research/programma5/idee/I-002/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.esplosioni_oi import calcola, riassunto

VARIANTI = {"I-002a": {"L": 16, "verso": 1, "oi": "basso", "trade": "contro", "minuti": 60},
            "I-002b": {"L": 8, "verso": 1, "oi": "basso", "trade": "contro", "minuti": 60},
            "I-002c": {"L": 16, "verso": 1, "oi": None, "trade": "contro", "minuti": 60}}

if __name__ == "__main__":
    print(riassunto(calcola("I-002", VARIANTI, sys.argv[1] if len(sys.argv) > 1 else "C", Path(__file__).parent)))
