"""Verifica di causalita' degli indicatori delle varianti (nessun trade, nessun risultato).

Per ogni variante ricalcola gli indicatori su serie troncate e li confronta con quelli della
serie intera: stampa solo le differenze. Il controllo positivo DEVE risultare non causale.
Uso: python verifica_causale.py [timeframe ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import CONTROLLO, VARIANTI  # noqa: E402

tf_scelti = set(sys.argv[1:])
for nome, var in list(VARIANTI.items()) + [("CONTROLLO", CONTROLLO)]:
    if tf_scelti and var.tf not in tf_scelti:
        continue
    ctx = comune.contesto(var.tf, "costruzione")
    diff = comune.verifica_causalita(var, ctx)
    print(nome, var.tf, "causale" if not diff else "NON CAUSALE: " + "; ".join(diff[:4]), flush=True)
