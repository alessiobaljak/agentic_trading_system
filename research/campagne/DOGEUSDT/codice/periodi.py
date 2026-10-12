"""Fase 0, punto 1: date di costruzione e validazione con periodi_campagna, scritte nel log PRIMA dei prezzi."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src.dati import periodi_campagna  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402

p = periodi_campagna(date(2020, 7, 1))
voce = {
    "tipo": "nota",
    "argomento": "periodi della campagna (Fase 0, punto 1), calcolati con periodi_campagna prima di caricare i prezzi",
    "primo_mese_di_dati": "2020-07 (scheda_moneta.md)",
    "inizio": p["inizio"].isoformat(),
    "giorni": p["giorni"],
    "giorni_costruzione": p["giorni_costruzione"],
    "fine_costruzione": p["fine_costruzione"].isoformat(),
    "fine_costruzione_ts": p["fine_costruzione_ts"],
    "inizio_validazione": p["inizio_validazione"].isoformat(),
    "inizio_validazione_ts": p["inizio_validazione_ts"],
    "fine_validazione": p["fine_validazione"].isoformat(),
    "slippage_per_lato": 0.0002,
}
print(registro.aggiungi(voce))
