"""Esegue in serie (mai in parallelo: gli id del log sono progressivi) le varianti passate come argomenti."""
import sys

import comune as C
import varianti as V
from esegui import esegui_variante

for nome in sys.argv[1:]:
    try:
        var, meta = V.CATALOGO[nome]()
        esegui_variante(var, meta)
    except Exception as e:  # registrato e riportato: un errore non deve passare in silenzio
        C.stampa("ERRORE", nome, repr(e))
        raise
C.stampa("FINE LOTTO", " ".join(sys.argv[1:]))
