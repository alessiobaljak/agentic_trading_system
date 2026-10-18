"""I-006 (scheda.md). Uso: python3 research/programma5/idee/I-006/calcolo.py C"""
import sys
from pathlib import Path

from research.programma5.strumenti.esplosioni_oi import riassunto
from research.programma5.strumenti.idee_minuti import aggrega, per_moneta_i006

VARIANTI = {'I-006a': {'soglia': 0.0005, 'anticipo': 60}, 'I-006b': {'soglia': 0.0003, 'anticipo': 60}, 'I-006c': {'soglia': 0.0005, 'anticipo': 120}}

if __name__ == "__main__":
    print(riassunto(aggrega("I-006", VARIANTI, sys.argv[1] if len(sys.argv) > 1 else "C", Path(__file__).parent, per_moneta_i006)))
