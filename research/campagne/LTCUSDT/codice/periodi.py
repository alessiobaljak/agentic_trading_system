"""Date di costruzione e validazione della campagna LTCUSDT (Fase 0, punto 1).

Stampa il risultato di ``periodi_campagna`` sul primo mese di dati della scheda.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src.dati import periodi_campagna  # noqa: E402

PRIMO_GIORNO = date(2020, 1, 1)  # scheda_moneta.md: primo mese di dati 2020-01

if __name__ == "__main__":
    p = periodi_campagna(PRIMO_GIORNO)
    for chiave, valore in p.items():
        print(chiave, valore)
