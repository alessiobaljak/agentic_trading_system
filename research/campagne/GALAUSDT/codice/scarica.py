"""Fase 0, punto 2: scarica i dati in-sample di GALAUSDT e le candele last di BTCUSDT.

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Nessun elenco di file remoti:
gli URL si costruiscono mese per mese dal primo mese di dati della scheda.
"""

from datetime import date

from research.src import dati

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2021, 9, 1)
FINE = date(2023, 12, 31)


def main() -> None:
    for tf in TIMEFRAME:
        for tipo in ("klines", "markPriceKlines"):
            p = dati.scarica_periodo("GALAUSDT", tipo, tf, INIZIO, FINE)
            print("GALAUSDT", tipo, tf, len(p), flush=True)
        p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
        print("BTCUSDT klines", tf, len(p), flush=True)
    p = dati.scarica_periodo("GALAUSDT", "fundingRate", None, INIZIO, FINE)
    print("GALAUSDT fundingRate", len(p), flush=True)
    print("checksum mancanti", len(dati.CHECKSUM_MANCANTI), dati.CHECKSUM_MANCANTI, flush=True)
    imp = dati.registra_impronte("GALAUSDT")
    print("impronte GALAUSDT", len(imp), flush=True)
    imp_btc = dati.registra_impronte("BTCUSDT")
    print("impronte BTCUSDT", len(imp_btc), flush=True)


if __name__ == "__main__":
    main()
