"""Impronte SHA-256 dei file in-sample della moneta e di BTCUSDT (sezione 5).

Uso: python impronte.py registra   -> scrive campagne/1000SHIBUSDT/impronte.json e ne stampa lo sha256
     python impronte.py verifica   -> confronta i file su disco con impronte.json (sessioni successive)
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
from research.src import dati  # noqa: E402

FILE = q.CARTELLA_CAMPAGNA / "impronte.json"
RADICE = q.RADICE_REPO / "research"


def main():
    if sys.argv[1] == "registra":
        tutto = {"1000SHIBUSDT": dati.calcola_impronte("1000SHIBUSDT", RADICE),
                 "BTCUSDT": dati.calcola_impronte("BTCUSDT", RADICE)}
        testo = json.dumps(tutto, indent=1, sort_keys=True) + "\n"
        FILE.write_text(testo)
        print({k: len(v) for k, v in tutto.items()}, hashlib.sha256(testo.encode()).hexdigest())
    else:
        attese = json.loads(FILE.read_text())
        for simbolo, imp in attese.items():
            diff = dati.verifica_impronte(simbolo, RADICE, imp)
            print(simbolo, "differenze:", len(diff), diff[:5])


if __name__ == "__main__":
    main()
