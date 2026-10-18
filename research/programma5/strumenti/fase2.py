"""Programma 5, fase 2: le monete (REGOLE.md, sezione 7)."""
import json
from pathlib import Path

from research.programma5.strumenti.scarico import MONETE as VECCHIE

NUOVE = tuple(json.loads((Path(__file__).resolve().parents[1] / "universo_fase2.json").read_text())["scelte"])
MONETE_F2 = tuple(VECCHIE) + NUOVE
