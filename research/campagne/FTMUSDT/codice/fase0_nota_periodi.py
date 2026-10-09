"""Fase 0 punto 1: scrive nel log le date di costruzione e validazione, PRIMA di caricare i prezzi."""
from comune import PERIODI, aggiungi_log

aggiungi_log({
    "id": "FTMUSDT-N003",
    "tipo": "nota",
    "testo": "Fase 0 punto 1: date calcolate con periodi_campagna di src/dati.py dal primo mese di dati della scheda (2020-09), prima di caricare qualunque prezzo.",
    "periodi": {k: str(v) for k, v in PERIODI.items()},
    "parametri_motore": "commissione 0,05% per lato, slippage 0,05% per lato (scheda), rischio 1%, leva massima 2, isolated, margine di mantenimento 0,025, capitale 1000, stop prima, serie stop = last (candele_stop=None), liquidazione sul mark",
})
