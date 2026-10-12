"""Fase 0, punto 1: date di costruzione e validazione, scritte nel log PRIMA di caricare i prezzi."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research.src.dati import periodi_campagna  # noqa: E402
import registro  # noqa: E402

p = periodi_campagna(date(2020, 1, 1))
voce = {
    "id": "ETCUSDT-N003",
    "tipo": "nota",
    "testo": "Fase 0 punto 1: periodi della campagna da periodi_campagna(2020-01-01), primo mese di dati della scheda. Scritti prima di caricare i prezzi.",
    "periodi": {
        "inizio": str(p["inizio"]),
        "giorni": p["giorni"],
        "giorni_costruzione": p["giorni_costruzione"],
        "fine_costruzione": str(p["fine_costruzione"]),
        "inizio_validazione": str(p["inizio_validazione"]),
        "fine_validazione": str(p["fine_validazione"]),
        "inizio_ts": p["inizio_ts"],
        "fine_costruzione_ts": p["fine_costruzione_ts"],
        "inizio_validazione_ts": p["inizio_validazione_ts"],
    },
}
registro.scrivi(voce)
print(voce)
