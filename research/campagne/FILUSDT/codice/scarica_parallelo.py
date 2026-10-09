"""Scarico in parallelo di un solo gruppo di file (per accelerare scarica.py, che poi li trova su disco).

Uso: python scarica_parallelo.py SIMBOLO TIPO   (TIPO: klines, markPriceKlines o fundingRate)
Stesse regole di scarica.py: solo fino al 2023-12-31, URL costruiti mese per mese, CHECKSUM verificato.
"""
from __future__ import annotations

import sys
from datetime import date

import comune
from research.src import dati

if __name__ == "__main__":
    simbolo, tipo = sys.argv[1], sys.argv[2]
    intervalli = [None] if tipo == "fundingRate" else list(reversed(comune.TIMEFRAME))
    for intervallo in intervalli:
        dati.scarica_periodo(simbolo, tipo, intervallo, comune.PRIMO_GIORNO, date(2023, 12, 31))
    (comune.CARTELLA_DATI / f"fatto_{simbolo}_{tipo}.txt").write_text(
        "fatto; checksum mancanti: " + repr(dati.CHECKSUM_MANCANTI) + "\n")
