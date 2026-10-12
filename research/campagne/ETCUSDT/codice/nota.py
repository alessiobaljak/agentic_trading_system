"""Aggiunge al log una voce `nota` col testo di un file (uso: python nota.py <ID> <file di testo>)."""
import sys
from pathlib import Path

import registro

testo = Path(sys.argv[2]).read_text(encoding="utf-8").strip()
print(registro.scrivi({"id": sys.argv[1], "tipo": "nota", "testo": testo}))
