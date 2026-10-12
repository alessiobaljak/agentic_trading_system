"""Scrive in serie le voci ``risultato`` di un lotto: legge un file JSON [[id, file, corretta, commento], ...].

Uso: python research/campagne/MATICUSDT/codice/chiudi_lotto.py <file.json>
"""
import json
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
for vid, file, corretta, commento in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")):
    p = subprocess.run([sys.executable, str(QUI / "chiudi.py"), vid, file, corretta, commento],
                       capture_output=True, text=True)
    print(p.stdout.strip(), p.stderr.strip()[-300:])
