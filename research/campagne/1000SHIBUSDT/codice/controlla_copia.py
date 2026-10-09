"""Controlla che la fabbrica delle verifiche riproduca gli indicatori e le condizioni della variante originale.

Uso: python controlla_copia.py <originale> <copia>
Confronta indicatori e condizione d'ingresso barra per barra (nessun trade, nessun risultato).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

a, b = varianti.VARIANTI[sys.argv[1]], varianti.VARIANTI[sys.argv[2]]
serie = q.carica(a.tf)
n = q.candele_costruzione(serie)
c = serie.candele[:n]
ia, ib = a.prepara(c, serie), b.prepara(c, serie)
for k in ia:
    print(k, "uguale" if np.allclose(ia[k], ib[k], equal_nan=True) else "DIVERSO")
ca = [a.ingresso(i, ia) for i in range(len(c))]
cb = [b.ingresso(i, ib) for i in range(len(c))]
print("condizione", "uguale" if ca == cb else "DIVERSA", sum(ca))
sa = [a.segnale(i, ia, c) for i in range(len(c))]
sb = [b.segnale(i, ib, c) for i in range(len(c))]
print("segnale", "uguale" if sa == sb else "DIVERSO")
