"""Aggiunge al log una voce letta da un file JSON (uso: python nota.py <file.json>)."""
import json
import sys

from comune import aggiungi_log

with open(sys.argv[1], encoding="utf-8") as f:
    voce = json.load(f)
print(aggiungi_log(voce))
