"""Impronte SHA-256 dei file scaricati (sezione 5): le scrive o le verifica.

Uso: ``python impronte.py scrivi`` (Fase 0: crea ``impronte.json`` nella cartella della campagna
e stampa la sua impronta da copiare in ``fase0_dati.md``) oppure ``python impronte.py verifica``
(a ogni nuova sessione, dopo il riscaricamento: lista vuota = dati uguali; altrimenti STOP).
"""
from __future__ import annotations

import hashlib
import json
import sys

import comune
from research.src import dati

FILE = comune.CARTELLA_CAMPAGNA / "impronte.json"

if __name__ == "__main__":
    if sys.argv[1] == "scrivi":
        tutte = {"FILUSDT": dati.calcola_impronte("FILUSDT"), "BTCUSDT": dati.calcola_impronte("BTCUSDT")}
        FILE.write_text(json.dumps(tutte, indent=1, sort_keys=True) + "\n")
        print(len(tutte["FILUSDT"]), len(tutte["BTCUSDT"]), hashlib.sha256(FILE.read_bytes()).hexdigest())
    else:
        attese = json.loads(FILE.read_text())
        radice = comune.RADICE_REPO / "research"
        diff = dati.verifica_impronte("FILUSDT", radice, attese["FILUSDT"]) + \
            dati.verifica_impronte("BTCUSDT", radice, attese["BTCUSDT"])
        print("differenze:", diff)
