"""Aspetta che un file di avanzamento finisca con FINE o ERRORE (o che passi il tempo massimo).

Uso: python3 research/campagne/LINK6/codice/aspetta.py <file> [secondi_massimi]
"""
import sys
import time
from pathlib import Path

percorso = Path(sys.argv[1])
massimo = float(sys.argv[2]) if len(sys.argv) > 2 else 540
inizio = time.time()
while time.time() - inizio < massimo:
    if percorso.exists():
        righe = percorso.read_text(encoding="utf-8").strip().splitlines()
        if righe and righe[-1].strip() in ("FINE", "ERRORE"):
            break
    time.sleep(5)
print(percorso.read_text(encoding="utf-8") if percorso.exists() else "file non ancora creato")
