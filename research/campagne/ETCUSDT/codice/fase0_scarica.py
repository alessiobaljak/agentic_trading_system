"""Fase 0, punto 2: scarico dei dati in-sample (fino al 2023-12-31) di ETCUSDT e del riferimento BTCUSDT."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)

for tf in TF:
    for tipo in ("klines", "markPriceKlines"):
        p = dati.scarica_periodo("ETCUSDT", tipo, tf, INIZIO, FINE)
        print("ETCUSDT", tipo, tf, len(p), flush=True)
p = dati.scarica_periodo("ETCUSDT", "fundingRate", None, INIZIO, FINE)
print("ETCUSDT fundingRate", len(p), flush=True)
for tf in TF:
    p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
    print("BTCUSDT klines", tf, len(p), flush=True)
print("checksum mancanti:", dati.CHECKSUM_MANCANTI, flush=True)
