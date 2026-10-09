"""Fase 0, punto 2: scarica i dati in-sample di DOGEUSDT (e le candele last di BTCUSDT come riferimento).

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Mesi dal primo mese di dati della
scheda (2020-07). Il CHECKSUM remoto si controlla a ogni file (scarico di rete).
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 7, 1), date(2023, 12, 31)

dati.azzera_checksum_mancanti()
for tf in TF:
    for tipo in ("klines", "markPriceKlines"):
        p = dati.scarica_periodo("DOGEUSDT", tipo, tf, INIZIO, FINE)
        print("DOGEUSDT", tipo, tf, len(p), "file", flush=True)
p = dati.scarica_periodo("DOGEUSDT", "fundingRate", None, INIZIO, FINE)
print("DOGEUSDT fundingRate", len(p), "file", flush=True)
for tf in TF:
    p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
    print("BTCUSDT klines", tf, len(p), "file", flush=True)
print("CHECKSUM mancanti:", len(dati.CHECKSUM_MANCANTI), dati.CHECKSUM_MANCANTI)
