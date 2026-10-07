"""Fase 0, punto 1: le date di costruzione e validazione di BTCUSDT.

Si calcolano dalla scheda (primo mese di dati 2020-01, fine in-sample
2023-12-31) con ``divisione_costruzione_validazione`` 70/30 sui GIORNI di
calendario, e si scrivono nel log PRIMA di caricare qualunque prezzo.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log import aggiungi  # noqa: E402

INIZIO = date(2020, 1, 1)      # primo mese di dati nell'archivio (scheda_moneta.md)
FINE = date(2023, 12, 31)      # fine dell'in-sample (parametri.yaml)
QUOTA_COSTRUZIONE = 0.70

giorni = (FINE - INIZIO).days + 1
giorni_costruzione = round(giorni * QUOTA_COSTRUZIONE)
fine_costruzione = INIZIO + timedelta(days=giorni_costruzione - 1)
inizio_validazione = fine_costruzione + timedelta(days=1)

voce = {
    "id": "BTCUSDT-F0-01",
    "tipo": "nota",
    "fase": "0",
    "oggetto": "date di costruzione e validazione, scritte prima di caricare i prezzi",
    "in_sample": {"inizio": INIZIO.isoformat(), "fine": FINE.isoformat(), "giorni": giorni},
    "costruzione": {"inizio": INIZIO.isoformat(), "fine": fine_costruzione.isoformat(), "giorni": giorni_costruzione},
    "validazione": {"inizio": inizio_validazione.isoformat(), "fine": FINE.isoformat(), "giorni": giorni - giorni_costruzione},
    "regola": "70% dei giorni di calendario dell'in-sample alla costruzione (arrotondato), il resto alla validazione",
    "fonte_date": "research/campagne/BTCUSDT/scheda_moneta.md (listing 2019-09-08, primo mese di dati 2020-01); research/config/parametri.yaml",
    "nota": "i mesi settembre-dicembre 2019 restano fuori perche' l'archivio mensile parte da gennaio 2020 (decisione 5 del Passo 0)",
}
print(aggiungi(voce))
