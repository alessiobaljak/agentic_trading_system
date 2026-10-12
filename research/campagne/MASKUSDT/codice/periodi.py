"""Fase 0, punto 1: date di costruzione e validazione di MASKUSDT (periodi_campagna)."""
import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src.dati import periodi_campagna  # noqa: E402

p = periodi_campagna(date(2021, 8, 1))
for k, v in p.items():
    print(k, v)
