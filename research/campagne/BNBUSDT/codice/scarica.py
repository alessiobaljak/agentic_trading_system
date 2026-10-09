"""Fase 0, punto 2: scarico dei dati in-sample di BNBUSDT e delle candele last di BTCUSDT.

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Nessun elenco di file remoti.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2020, 2, 1)
FINE = date(2023, 12, 31)

for tf in TIMEFRAME:
    for tipo in ("klines", "markPriceKlines"):
        p = dati.scarica_periodo("BNBUSDT", tipo, tf, INIZIO, FINE)
        print("BNBUSDT", tipo, tf, len(p), "file", flush=True)
p = dati.scarica_periodo("BNBUSDT", "fundingRate", None, INIZIO, FINE)
print("BNBUSDT fundingRate", len(p), "file", flush=True)
for tf in TIMEFRAME:
    p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
    print("BTCUSDT klines", tf, len(p), "file", flush=True)
print("checksum mancanti:", len(dati.CHECKSUM_MANCANTI), dati.CHECKSUM_MANCANTI[:5])
imp = dati.registra_impronte("BNBUSDT")
print("impronte BNBUSDT:", len(imp))
imp = dati.registra_impronte("BTCUSDT")
print("impronte BTCUSDT:", len(imp))
print("FINE")
