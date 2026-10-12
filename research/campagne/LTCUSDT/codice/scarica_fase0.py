"""Fase 0, punto 2: scarica i dati in-sample di LTCUSDT e il riferimento BTCUSDT.

LTCUSDT: candele last (klines) e mark (markPriceKlines) su tutti i timeframe
ammessi, funding; BTCUSDT: solo candele last su tutti i timeframe ammessi.
Periodo: dal primo mese di dati della scheda (2020-01) al 2023-12. Nessun elenco
remoto: un file per mese, URL costruito (src/dati.py). Il controllo del CHECKSUM
remoto e' acceso (scarico di rete).
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)


def lavoro(arg):
    simbolo, tipo, intervallo = arg
    percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, INIZIO, FINE)
    return simbolo, tipo, intervallo, len(percorsi)


if __name__ == "__main__":
    compiti = [("LTCUSDT", "klines", tf) for tf in TIMEFRAME]
    compiti += [("LTCUSDT", "markPriceKlines", tf) for tf in TIMEFRAME]
    compiti += [("LTCUSDT", "fundingRate", None)]
    compiti += [("BTCUSDT", "klines", tf) for tf in TIMEFRAME]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for simbolo, tipo, intervallo, n in pool.map(lavoro, compiti):
            print(simbolo, tipo, intervallo, "mesi:", n, flush=True)
    print("checksum mancanti:", len(dati.CHECKSUM_MANCANTI))
    for url in dati.CHECKSUM_MANCANTI:
        print("  senza checksum:", url)
    print("fatto")
