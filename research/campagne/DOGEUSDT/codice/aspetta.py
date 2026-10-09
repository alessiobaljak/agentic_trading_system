"""Aspetta che un file sotto data/insample/DOGEUSDT contenga una delle parole date, poi lo stampa.

Uso: aspetta.py <nome_file> PAROLA [PAROLA ...]
"""
import sys
import time
from pathlib import Path

F = Path(__file__).resolve().parents[4] / "research" / "data" / "insample" / "DOGEUSDT" / sys.argv[1]
parole = sys.argv[2:]
while True:
    t = F.read_text() if F.exists() else ""
    if any(p in t for p in parole):
        print(t[-6000:])
        break
    time.sleep(15)
