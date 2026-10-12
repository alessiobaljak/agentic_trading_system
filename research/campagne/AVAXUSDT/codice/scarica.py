"""Fase 0 punto 2: scarico dei dati in-sample di AVAXUSDT e delle candele last di BTCUSDT.

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Nessun elenco remoto: un file
per mese, costruito dall'URL. Il controllo del CHECKSUM remoto e' acceso (scarico di rete).
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2020, 9, 1)
FINE = date(2023, 12, 31)


def main():
    dati.azzera_checksum_mancanti()
    conteggi = {}
    for tf in TIMEFRAME:
        for tipo in ("klines", "markPriceKlines"):
            p = dati.scarica_periodo("AVAXUSDT", tipo, tf, INIZIO, FINE)
            conteggi[f"AVAXUSDT {tipo} {tf}"] = len(p)
            print("AVAXUSDT", tipo, tf, len(p), flush=True)
    p = dati.scarica_periodo("AVAXUSDT", "fundingRate", None, INIZIO, FINE)
    conteggi["AVAXUSDT fundingRate"] = len(p)
    print("AVAXUSDT fundingRate", len(p), flush=True)
    for tf in TIMEFRAME:
        p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
        conteggi[f"BTCUSDT klines {tf}"] = len(p)
        print("BTCUSDT klines", tf, len(p), flush=True)
    print("CHECKSUM mancanti:", len(dati.CHECKSUM_MANCANTI))
    for u in dati.CHECKSUM_MANCANTI:
        print("  senza checksum:", u)


if __name__ == "__main__":
    main()
