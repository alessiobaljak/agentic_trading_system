"""Stampa le date di costruzione e validazione di ETHUSDT (Fase 0, punto 1).

Le date vengono da ``periodi_campagna`` di research/src/dati.py, con il primo
mese di dati della scheda (2020-01-01). Non legge prezzi.
"""

import json
import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src.dati import periodi_campagna  # noqa: E402


def main() -> None:
    periodi = periodi_campagna(date(2020, 1, 1))
    print(json.dumps({k: (v.isoformat() if isinstance(v, date) else v) for k, v in periodi.items()}, indent=1))


if __name__ == "__main__":
    main()
