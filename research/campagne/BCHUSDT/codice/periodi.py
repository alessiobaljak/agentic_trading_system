"""Stampa le date di costruzione e validazione di BCHUSDT (Fase 0, punto 1)."""
import json
from datetime import date

from research.src.dati import periodi_campagna

p = periodi_campagna(date(2020, 1, 1))
print(json.dumps({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in p.items()}))
