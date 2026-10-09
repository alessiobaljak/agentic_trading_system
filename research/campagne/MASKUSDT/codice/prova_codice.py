"""Prova che il codice delle varianti gira senza errori (nessun conteggio, nessun risultato: stampa solo 'ok')."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro  # noqa: E402
import registro_idee  # noqa: E402

for vid, (classe, meta) in registro_idee.VARIANTI.items():
    var = classe()
    per = quadro.periodo(var.tf)
    st = var.prepara(per.candele, per)
    for i in range(len(per.candele)):
        if var.segnale(st, i) is not None:
            var.condizione(st, i)
    print(vid, "ok", flush=True)
