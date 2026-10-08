"""Fase 0, punto 2: scarica i dati in-sample di ETHUSDT e di BTCUSDT (riferimento).

Solo fino al 2023-12-31, con il caricatore del protocollo (research/src/dati.py),
che rifiuta ogni data oltre e confronta ogni zip con il CHECKSUM pubblicato.
Non elenca file remoti: costruisce gli URL mese per mese dal 2020-01.

Uso: python research/campagne/ETHUSDT/codice/scarica.py
Stampa un riepilogo per tipo e intervallo e gli URL senza CHECKSUM.
"""

import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)
TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]


def scarica(simbolo: str, tipo: str, intervallo) -> None:
    percorsi = dati.scarica_periodo(simbolo, tipo, intervallo, INIZIO, FINE)
    print(f"{simbolo} {tipo} {intervallo}: {len(percorsi)} mesi", flush=True)


def main() -> None:
    for tf in TIMEFRAME:
        scarica("ETHUSDT", "klines", tf)
        scarica("ETHUSDT", "markPriceKlines", tf)
    scarica("ETHUSDT", "fundingRate", None)
    for tf in TIMEFRAME:
        scarica("BTCUSDT", "klines", tf)
    print("CHECKSUM mancanti:", len(dati.CHECKSUM_MANCANTI))
    for url in dati.CHECKSUM_MANCANTI:
        print("  ", url)


if __name__ == "__main__":
    main()
