#!/usr/bin/env python3
"""Il pannello giornaliero rifatto con il codice del commit della prova 168 (`c6caf1b`, 22 nov 2026) sui dati di oggi, scritto in una
cartella temporanea (mai in research/data: `PANNELLO` del modulo viene spostato prima della chiamata).

Uso: python3 -I audits/repro/prova168_pannello_commit_2026-11-27.py <cartella del codice del commit> <file .pkl di uscita>
"""
import sys
from pathlib import Path

codice, uscita = Path(sys.argv[1]), Path(sys.argv[2])
assert "research/data" not in str(uscita.resolve()), "mai in research/data"
sys.path.insert(0, str(codice))
from research.programma6 import seconda as sc  # noqa: E402

sc.PANNELLO = uscita
pan = sc.costruisci_pannello(log=lambda x: None)
print("fatto", sc.data(pan["t0"]), sc.data(pan["t0"] + pan["close"].shape[0] - 1), len(pan["simboli"]))
