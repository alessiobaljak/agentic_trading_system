"""Aspetta che un file contenga una delle parole date, poi ne stampa la coda.

Uso: aspetta.py <percorso dalla radice del repository> PAROLA [PAROLA ...]
"""
import sys
import time
from pathlib import Path

F = Path(__file__).resolve().parents[4] / sys.argv[1]
parole = sys.argv[2:]
while True:
    t = F.read_text() if F.exists() else ""
    if any(p in t for p in parole):
        print(t[-3000:])
        break
    time.sleep(15)
