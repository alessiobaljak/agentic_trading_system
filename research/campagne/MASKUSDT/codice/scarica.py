"""Fase 0, punto 2: scarica i dati in-sample di MASKUSDT (e le candele last di BTCUSDT).

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Mese per mese, URL
costruiti direttamente: nessun elenco dei file remoti. Alla fine registra le
impronte SHA-256 e stampa i CHECKSUM mancanti.
"""
import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2021, 8, 1)
FINE = date(2023, 12, 31)


def main():
    for tf in TF:
        for tipo in ("klines", "markPriceKlines"):
            p = dati.scarica_periodo("MASKUSDT", tipo, tf, INIZIO, FINE)
            print("MASKUSDT", tipo, tf, len(p), "file", flush=True)
    p = dati.scarica_periodo("MASKUSDT", "fundingRate", None, INIZIO, FINE)
    print("MASKUSDT fundingRate", len(p), "file", flush=True)
    for tf in TF:
        p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
        print("BTCUSDT klines", tf, len(p), "file", flush=True)
    imp = dati.registra_impronte("MASKUSDT")
    imp_btc = dati.registra_impronte("BTCUSDT")
    print("impronte MASKUSDT", len(imp), "BTCUSDT", len(imp_btc))
    print("checksum mancanti", len(dati.CHECKSUM_MANCANTI), dati.CHECKSUM_MANCANTI[:20])


if __name__ == "__main__":
    main()
