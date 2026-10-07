"""Fase 0, punto 2: scarica i dati in-sample di BTCUSDT (solo fino al 2023-12-31).

Cosa si scarica (file mensili di data.binance.vision, con controllo del
CHECKSUM remoto, blocco del vault nel caricatore):
* klines 15m (last price): la serie dei segnali e degli stop; gli altri
  timeframe ammessi (30m ... 1d) si costruiscono per aggregazione;
* klines 1d (last price): solo per controllare che l'aggregazione da 15m
  coincida con le candele native di Binance;
* markPriceKlines 15m: la serie delle liquidazioni;
* fundingRate: il funding storico.
Alla fine registra le impronte SHA-256 (impronte.json) e stampa un riepilogo.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research.src import dati  # noqa: E402
from log import aggiungi  # noqa: E402

SIMBOLO = "BTCUSDT"
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
RICHIESTE = [("klines", "15m"), ("klines", "1d"), ("markPriceKlines", "15m"), ("fundingRate", None)]

riepilogo = {}
for tipo, intervallo in RICHIESTE:
    percorsi = dati.scarica_periodo(SIMBOLO, tipo, intervallo, INIZIO, FINE)
    chiave = tipo if intervallo is None else f"{tipo}/{intervallo}"
    riepilogo[chiave] = {"file_scaricati": len(percorsi), "mesi_richiesti": 48}
    print(chiave, len(percorsi), "file")

impronte = dati.registra_impronte(SIMBOLO)
print("impronte registrate:", len(impronte))
print("checksum mancanti:", sorted(dati.CHECKSUM_MANCANTI))
aggiungi({
    "id": "BTCUSDT-F0-02", "tipo": "nota", "fase": "0",
    "oggetto": "scarico dei dati in-sample completato",
    "fonte": "data.binance.vision, file mensili futures/um, 2020-01 .. 2023-12",
    "file": riepilogo,
    "n_impronte": len(impronte),
    "checksum_remoti_mancanti": sorted(dati.CHECKSUM_MANCANTI),
    "nota": "nessun file oltre il 2023-12 e' stato richiesto o elencato",
})
