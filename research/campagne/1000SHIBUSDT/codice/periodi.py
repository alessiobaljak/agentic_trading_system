"""Stampa le date di costruzione e validazione della campagna (Fase 0, punto 1)."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src.dati import periodi_campagna  # noqa: E402

p = periodi_campagna(date(2021, 5, 1))
print(json.dumps({k: (v.isoformat() if isinstance(v, date) else v) for k, v in p.items()}, ensure_ascii=False))
