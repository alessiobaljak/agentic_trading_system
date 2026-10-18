"""I-020 — scalping a limite: reti d'acquisto a 3σ con uscita a limite (scheda.md).
Uso: PYTHONPATH=. python3 research/programma5/idee/I-020/calcolo.py C|V|R"""
import sys
from pathlib import Path

from research.programma5.strumenti.idee_minuti import aggrega
from research.programma5.strumenti.rapporto import scrivi
from research.programma5.strumenti.scalping import per_moneta_i020

VARIANTI = {"I-020a": {"k": 3, "m": 0.5, "H": 60}, "I-020b": {"k": 3, "m": 0.5, "H": 240},
            "I-020c": {"k": 3, "m": 1, "H": 240}}

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "C"
    aggrega("I-020", VARIANTI, periodo, Path(__file__).parent, per_moneta_i020)
    print(scrivi("I-020", periodo))
