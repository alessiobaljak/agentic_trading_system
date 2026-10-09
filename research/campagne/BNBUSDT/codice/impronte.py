"""Copia le impronte dei file in-sample nella cartella della campagna e stampa l'impronta del file."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

cartella = Path(__file__).resolve().parents[1]
tutte = {"BNBUSDT": dati.calcola_impronte("BNBUSDT"), "BTCUSDT": dati.calcola_impronte("BTCUSDT")}
testo = json.dumps(tutte, indent=1, sort_keys=True) + "\n"
(cartella / "impronte.json").write_text(testo, encoding="utf-8")
print("file:", len(tutte["BNBUSDT"]), len(tutte["BTCUSDT"]))
print("sha256 impronte.json:", hashlib.sha256(testo.encode("utf-8")).hexdigest())
