"""Aspetta che un file di avanzamento finisca con FINE o ERRORE (o che passi il tempo massimo).

Uso: python3 research/campagne/LINK6/codice/aspetta.py <file> [secondi_massimi] [righe_iniziali_da_saltare]

Con righe_iniziali_da_saltare si guarda solo cio' che e' stato scritto dopo quelle righe (un giro nuovo
in un file che ne contiene di vecchi). Stampa solo le righe nuove.
"""
import sys
import time
from pathlib import Path

percorso = Path(sys.argv[1])
massimo = float(sys.argv[2]) if len(sys.argv) > 2 else 540
salta = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def nuove():
    if not percorso.exists():
        return []
    return percorso.read_text(encoding="utf-8").strip().splitlines()[salta:]


inizio = time.time()
while time.time() - inizio < massimo:
    righe = nuove()
    if righe and righe[-1].strip() in ("FINE", "ERRORE"):
        break
    time.sleep(5)
print("\n".join(nuove()) if percorso.exists() else "file non ancora creato")
