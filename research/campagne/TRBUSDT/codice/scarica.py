"""Fase 0, punto 2: scarica i dati in-sample di TRBUSDT e le candele last di BTCUSDT.

Solo fino al 2023-12-31, file per mese costruiti direttamente (nessun elenco remoto),
con il controllo del CHECKSUM pubblicato accanto a ogni zip (src/dati.py).
"""

import json
from datetime import date

from research.src import dati

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2020, 9, 1)
FINE = date(2023, 12, 31)


def main():
    dati.azzera_checksum_mancanti()
    conteggi = {}
    for tf in TIMEFRAME:
        for tipo in ("klines", "markPriceKlines"):
            p = dati.scarica_periodo("TRBUSDT", tipo, tf, INIZIO, FINE)
            conteggi[f"TRBUSDT {tipo} {tf}"] = len(p)
            print(tipo, tf, len(p), flush=True)
    p = dati.scarica_periodo("TRBUSDT", "fundingRate", None, INIZIO, FINE)
    conteggi["TRBUSDT fundingRate"] = len(p)
    for tf in TIMEFRAME:
        p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
        conteggi[f"BTCUSDT klines {tf}"] = len(p)
        print("BTC", tf, len(p), flush=True)
    print(json.dumps({"conteggi": conteggi, "checksum_mancanti": list(dati.CHECKSUM_MANCANTI)}, indent=1))


if __name__ == "__main__":
    main()
