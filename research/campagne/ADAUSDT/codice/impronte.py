"""Copia le impronte SHA-256 dei file scaricati in campagne/ADAUSDT/impronte.json e stampa l'impronta di quel file.

Con l'argomento "verifica" ricalcola le impronte dei file su disco e le confronta con quelle registrate.
"""
import hashlib
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

DEST = RADICE / "research" / "campagne" / "ADAUSDT" / "impronte.json"

if len(sys.argv) > 1 and sys.argv[1] == "verifica":
    attese = json.loads(DEST.read_text(encoding="utf-8"))
    for simbolo in ("ADAUSDT", "BTCUSDT"):
        diff = dati.verifica_impronte(simbolo, dati.RADICE_DEFAULT, attese[simbolo])
        print(simbolo, "differenze:", len(diff), diff[:5])
    sys.exit(0)

imp = {"ADAUSDT": dati.calcola_impronte("ADAUSDT"), "BTCUSDT": dati.calcola_impronte("BTCUSDT")}
DEST.write_text(json.dumps(imp, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print("file:", len(imp["ADAUSDT"]), len(imp["BTCUSDT"]))
print("sha256 impronte.json:", hashlib.sha256(DEST.read_bytes()).hexdigest())
