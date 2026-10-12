"""Stima dei trade (sezione 8): conta_trade sulle regole esatte della variante, una volta sola.

Stampa SOLO i conteggi. Uso: python conta.py V-01 [V-02 ...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

for chiave in sys.argv[1:]:
    var = VARIANTI[chiave]
    print(chiave, var.tf, var.direzione, json.dumps(comune.conta(var)), flush=True)
