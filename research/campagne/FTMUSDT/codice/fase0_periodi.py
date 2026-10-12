"""Fase 0 punto 1: stampa le date di costruzione e validazione (prima di caricare i prezzi)."""
import json

from comune import PERIODI

print(json.dumps({k: str(v) for k, v in PERIODI.items()}, indent=1))
