"""Fase 0, punto 2: scarico dei dati in-sample (solo fino al 2023-12) con il caricatore del protocollo."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

FINE = date(2023, 12, 31)
LAVORI = [
    ("SOLUSDT", "klines", "15m", date(2020, 9, 1)),
    ("SOLUSDT", "markPriceKlines", "15m", date(2020, 9, 1)),
    ("SOLUSDT", "klines", "1d", date(2020, 9, 1)),
    ("SOLUSDT", "fundingRate", None, date(2020, 9, 1)),
    ("BTCUSDT", "klines", "15m", date(2020, 1, 1)),
    ("BTCUSDT", "klines", "1d", date(2020, 1, 1)),
]

if __name__ == "__main__":
    for simbolo, tipo, intervallo, inizio in LAVORI:
        percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, inizio, FINE)
        print(simbolo, tipo, intervallo, "file:", len(percorsi), "primo:", percorsi[0].name if percorsi else None)
    print("senza CHECKSUM remoto:", len(dati.CHECKSUM_MANCANTI))
    for u in dati.CHECKSUM_MANCANTI:
        print("  ", u)
