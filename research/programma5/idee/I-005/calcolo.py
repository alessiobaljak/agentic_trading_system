"""I-005 (scheda.md). Uso: python3 research/programma5/idee/I-005/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.esplosioni_oi import riassunto
from research.programma5.strumenti.idee_minuti import aggrega, per_moneta_i005

VARIANTI = {'I-005a': {'soglia': 0.70, 'minuti': 15}, 'I-005b': {'soglia': 0.70, 'minuti': 60}, 'I-005c': {'soglia': 0.80, 'minuti': 15}}

if __name__ == "__main__":
    print(riassunto(aggrega("I-005", VARIANTI, sys.argv[1] if len(sys.argv) > 1 else "C", Path(__file__).parent, per_moneta_i005)))
