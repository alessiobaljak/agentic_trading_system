"""Fase 0, punto 2: scarico dei dati in-sample di FILUSDT (e del last di BTCUSDT come riferimento).

Solo fino al 2023-12-31: il caricatore (src/dati.py) rifiuta ogni data oltre. Si costruiscono
gli URL mese per mese, senza elencare file remoti. Alla fine si registrano le impronte.
"""
from __future__ import annotations

import json
import sys
from datetime import date

import comune  # noqa: F401  (mette la radice del repository nel percorso)
from research.src import dati

FINE = date(2023, 12, 31)


def scarica(simbolo: str, tipi, inizio: date) -> dict:
    conteggi = {}
    for tipo in tipi:
        intervalli = [None] if tipo == "fundingRate" else comune.TIMEFRAME
        for intervallo in intervalli:
            percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, inizio, FINE)
            conteggi[f"{tipo}/{intervallo}"] = len(percorsi)
            print(simbolo, tipo, intervallo, len(percorsi), flush=True)
    return conteggi


if __name__ == "__main__":
    dati.azzera_checksum_mancanti()
    esito = {
        "FILUSDT": scarica("FILUSDT", ["klines", "markPriceKlines", "fundingRate"], comune.PRIMO_GIORNO),
        "BTCUSDT": scarica("BTCUSDT", ["klines"], comune.PRIMO_GIORNO),
        "checksum_mancanti": list(dati.CHECKSUM_MANCANTI),
    }
    impronte_fil = dati.registra_impronte("FILUSDT")
    impronte_btc = dati.registra_impronte("BTCUSDT")
    esito["n_impronte"] = {"FILUSDT": len(impronte_fil), "BTCUSDT": len(impronte_btc)}
    (comune.CARTELLA_DATI / "esito_scarico.json").write_text(json.dumps(esito, indent=1))
    print(json.dumps(esito, indent=1))
    sys.exit(0)
