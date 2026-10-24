"""Le azioni societarie (dividendi, frazionamenti, scissioni) di tutti i titoli passati per l'S&P 500 dal 2016 al 2024.

    python -m stock.dati.scarica_universo PARTE PARTI     # per esempio 0 3, 1 3, 2 3 in parallelo

Salta i titoli già scaricati con le scissioni. I prezzi al giorno li ha già scaricati `stock.universo.costruisci`.
"""
from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path

from stock.dati import alpaca, archivio
from stock.universo.costruisci import carica_composizione


def main(parte: int, parti: int) -> None:
    comp = carica_composizione(Path.home() / "stock_dati" / "sp500_storico.csv")
    tutti = sorted(set().union(*[m for d, m in comp if date(2015, 9, 1) <= d <= date(2024, 12, 31)]))
    fatti = 0
    for i, t in enumerate(tutti):
        if i % parti != parte:
            continue
        a = archivio.carica(t, "azioni")
        if a is not None and "nuovo" in a.columns:
            continue
        raw = archivio.carica(t, "1Day_raw")
        if raw is None or raw.empty:
            continue
        archivio.salva(alpaca.azioni_societarie(t, datetime(2016, 1, 1, 5, tzinfo=UTC), datetime(2025, 1, 1, 5, tzinfo=UTC)),
                       t, "azioni")
        fatti += 1
        if fatti % 50 == 0:
            print(parte, fatti, flush=True)
    print("FINE", parte, fatti, flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
