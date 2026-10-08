"""Verifica delle impronte dei dati in-sample rispetto a quelle registrate in Fase 0 (sezione 5)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402

CARTELLA = Path(__file__).resolve().parents[1]
for simbolo, nome in (("SOLUSDT", "impronte.json"), ("BTCUSDT", "impronte_btcusdt.json")):
    attese = json.loads((CARTELLA / nome).read_text())
    diff = comune.dati.verifica_impronte(simbolo, comune.dati.RADICE_DEFAULT, attese)
    print(simbolo, "file attesi", len(attese), "differenze", len(diff), diff[:5])
