"""Aspetta che il log abbia almeno N risultati (python -m ... attendi N), poi esce."""

import sys
import time

from research.campagne.GALAUSDT.codice import registro

if __name__ == "__main__":
    n = int(sys.argv[1])
    while registro.LOG.read_text(encoding="utf-8").count('"tipo": "risultato"') < n:
        time.sleep(5)
    print("pronti", n)
