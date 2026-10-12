"""Fase 0, punto 1: date di costruzione e validazione di TRBUSDT con periodi_campagna."""

import json
from datetime import date

from research.src.dati import periodi_campagna

PRIMO_GIORNO = date(2020, 9, 1)  # scheda_moneta.md: primo mese di dati 2020-09


def periodi():
    return periodi_campagna(PRIMO_GIORNO)


if __name__ == "__main__":
    p = periodi()
    print(json.dumps({k: (v.isoformat() if isinstance(v, date) else v) for k, v in p.items()}, indent=1))
