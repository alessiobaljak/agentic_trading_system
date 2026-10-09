"""Lancia in serie i gruppi di verifica di verifiche_025.py (ognuno scrive il suo file in esiti/)."""
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
for g in ("ritardo", "costi_doppi", "intrabarra", "timeframe", "robustezza"):
    subprocess.run([sys.executable, str(QUI / "verifiche_025.py"), g], capture_output=True, text=True)
print("fatto")
