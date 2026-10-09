"""Fase 0, punto 2: scarica i dati in-sample di DYDXUSDT (last, mark, funding) e il last di BTCUSDT.

Solo i mesi fino al 2023-12 (il caricatore rifiuta il resto). Nessun elenco di file remoti.
Alla fine registra le impronte (data/insample/<SIMBOLO>/impronte.json) e stampa i conteggi.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2021, 9, 1)
FINE = date(2023, 12, 31)

dati.azzera_checksum_mancanti()
riepilogo = {}
for tf in TIMEFRAME:
    for tipo in ("klines", "markPriceKlines"):
        p = dati.scarica_periodo("DYDXUSDT", tipo, tf, INIZIO, FINE)
        riepilogo[f"DYDXUSDT/{tipo}/{tf}"] = len(p)
        print(tipo, tf, len(p), flush=True)
p = dati.scarica_periodo("DYDXUSDT", "fundingRate", None, INIZIO, FINE)
riepilogo["DYDXUSDT/fundingRate"] = len(p)
for tf in TIMEFRAME:
    p = dati.scarica_periodo("BTCUSDT", "klines", tf, INIZIO, FINE)
    riepilogo[f"BTCUSDT/klines/{tf}"] = len(p)
    print("BTC", tf, len(p), flush=True)

imp_d = dati.registra_impronte("DYDXUSDT")
imp_b = dati.registra_impronte("BTCUSDT")
riepilogo["file_DYDXUSDT"] = len(imp_d)
riepilogo["file_BTCUSDT"] = len(imp_b)
riepilogo["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
print(json.dumps(riepilogo, indent=1))
