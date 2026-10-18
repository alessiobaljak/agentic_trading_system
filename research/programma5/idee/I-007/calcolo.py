"""I-007 (scheda.md). Uso: python3 research/programma5/idee/I-007/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.esplosioni_oi import riassunto
from research.programma5.strumenti.idee_minuti import aggrega, per_moneta_i007

VARIANTI = {'I-007a': {'minuti': 5, 'indietro': 1/3}, 'I-007b': {'minuti': 15, 'indietro': 1/3}, 'I-007c': {'minuti': 15, 'indietro': 0.5}}

if __name__ == "__main__":
    print(riassunto(aggrega("I-007", VARIANTI, sys.argv[1] if len(sys.argv) > 1 else "C", Path(__file__).parent, per_moneta_i007)))
