"""Aspetta che il log abbia almeno N voci 'risultato' o 'scarto' (o che passino M secondi), poi
stampa il riassunto dell'ultimo lotto. Uso: python -m ...attendi N [secondi_massimi]"""

import json
import sys
import time

from research.campagne.TRBUSDT.codice import registro
from research.campagne.TRBUSDT.codice.esegui_variante import USCITA

if __name__ == "__main__":
    n = int(sys.argv[1])
    massimo = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
    t0 = time.time()
    while time.time() - t0 < massimo:
        k = sum(1 for v in registro.voci() if v.get("tipo") in ("risultato", "scarto"))
        if k >= n:
            break
        time.sleep(10)
    if USCITA.is_file():
        print(USCITA.read_text(encoding="utf-8"))
