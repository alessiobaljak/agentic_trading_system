"""Fase 0 punto 1: le date di costruzione e validazione di AVAXUSDT, da periodi_campagna."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src.dati import periodi_campagna  # noqa: E402

p = periodi_campagna(date(2020, 9, 1))
for chiave, valore in p.items():
    print(chiave, valore)
