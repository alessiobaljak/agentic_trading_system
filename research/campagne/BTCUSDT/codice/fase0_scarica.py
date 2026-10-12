"""Fase 0, punto 2: scarica i dati in-sample di BTCUSDT (fino al 2023-12-31) e registra le impronte."""
import json
from datetime import date

from comune import SIMBOLO, TIMEFRAME, dati

INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
dati.azzera_checksum_mancanti()
conteggi = {}
for tipo in ("klines", "markPriceKlines"):
    for tf in TIMEFRAME:
        p = dati.scarica_periodo(SIMBOLO, tipo, tf, INIZIO, FINE)
        conteggi[f"{tipo}/{tf}"] = len(p)
        print(tipo, tf, len(p), flush=True)
p = dati.scarica_periodo(SIMBOLO, "fundingRate", None, INIZIO, FINE)
conteggi["fundingRate"] = len(p)
impronte = dati.registra_impronte(SIMBOLO)
print(json.dumps({"conteggi": conteggi, "file": len(impronte),
                  "checksum_mancanti": list(dati.CHECKSUM_MANCANTI)}, indent=1))
