"""I prezzi al giorno e le azioni societarie del periodo chiuso (novembre 2024 → settembre 2026) di tutti i titoli dell'S&P 500
di quel periodo, nei tipi d'archivio `1Day_raw_chiuso` e `azioni_chiuso` (separati dalla ricerca).

    python -m stock.dati.scarica_chiuso PARTE PARTI
"""
from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from pathlib import Path

from stock.dati import alpaca, archivio
from stock.universo.costruisci import cambi_di_nome, carica_composizione

INIZIO = datetime(2024, 11, 1, 4, tzinfo=UTC)
FINE = datetime(2026, 10, 1, 3, 59, tzinfo=UTC)


def simboli_del_periodo() -> list[str]:
    comp = carica_composizione(Path.home() / "stock_dati" / "sp500_storico.csv")
    cambi = cambi_di_nome()
    tutti = set().union(*[m for d, m in comp if date(2024, 10, 1) <= d <= date(2026, 9, 30)])
    return sorted({cambi.get(t, t) for t in tutti} | {"SPY"})


def main(parte: int, parti: int) -> None:
    for i, s in enumerate(simboli_del_periodo()):
        if i % parti != parte or archivio.carica(s, "1Day_raw_chiuso") is not None:
            continue
        archivio.salva(alpaca.barre(s, "1Day", INIZIO, FINE), s, "1Day_raw_chiuso")
        archivio.salva(alpaca.azioni_societarie(s, INIZIO, FINE), s, "azioni_chiuso")
    print("FINE", parte, flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
