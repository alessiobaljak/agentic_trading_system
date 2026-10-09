"""Fase 0, punto 2: scarica i dati in-sample della moneta e di BTCUSDT (riferimento).

Solo mesi fino al 2023-12 (il caricatore rifiuta il resto). Mai elenchi di file:
gli URL si costruiscono mese per mese.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

SIMBOLO = "1000SHIBUSDT"
TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2021, 5, 1)
FINE = date(2023, 12, 31)


def main():
    for tf in TF:
        for tipo in ("klines", "markPriceKlines"):
            p = dati.scarica_periodo(SIMBOLO, tipo, tf, INIZIO, FINE)
            print(SIMBOLO, tipo, tf, len(p), "file", flush=True)
    p = dati.scarica_periodo(SIMBOLO, "fundingRate", None, INIZIO, FINE)
    print(SIMBOLO, "fundingRate", len(p), "file", flush=True)
    for tf in TF:
        p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
        print("BTCUSDT klines", tf, len(p), "file", flush=True)
    print("checksum mancanti:", sorted(dati.CHECKSUM_MANCANTI), flush=True)


if __name__ == "__main__":
    main()
