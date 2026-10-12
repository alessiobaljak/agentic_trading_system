"""Fase 0 punto 2: scarico dei dati in-sample di LINKUSDT (e del last di BTCUSDT come riferimento).

Solo mesi fino al 2023-12 (il caricatore rifiuta il resto). Con il controllo del
CHECKSUM remoto acceso (scarico di rete). Scrive un riepilogo su stdout.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)

lavori = []
for tf in TF:
    lavori.append(("LINKUSDT", "klines", tf))
    lavori.append(("LINKUSDT", "markPriceKlines", tf))
lavori.append(("LINKUSDT", "fundingRate", None))
for tf in TF:
    lavori.append(("BTCUSDT", "klines", tf))

for simbolo, tipo, tf in lavori:
    percorsi = dati.scarica_periodo(simbolo, tipo, tf, INIZIO, FINE)
    print(simbolo, tipo, tf, len(percorsi), "file", flush=True)
print("checksum mancanti:", len(dati.CHECKSUM_MANCANTI))
for u in sorted(dati.CHECKSUM_MANCANTI):
    print("  ", u)
print("FINE")
