"""Conta una sola volta i trade di un elenco di varianti (sezione 8), con ``prova.py conta``.

Uso: python research/campagne/MATICUSDT/codice/conta_tutte.py V01 V02 ...
Scrive ogni conteggio in esiti/<ID>_conta.json e un riepilogo in esiti/conteggi.txt.
"""
import json
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
righe = []
for vid in sys.argv[1:]:
    p = subprocess.run([sys.executable, str(QUI / "prova.py"), "conta", vid], capture_output=True, text=True)
    righe.append(f"{vid} {p.stdout.strip()} {p.stderr.strip()[-300:]}")
(QUI.parent / "esiti" / "conteggi.txt").open("a").write("\n".join(righe) + "\n")
print("\n".join(righe))
