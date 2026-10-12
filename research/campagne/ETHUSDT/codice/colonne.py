"""Mostra quante colonne hanno le righe delle candele giornaliere (controllo del formato).

Serve a sapere se la colonna del volume degli acquisti a mercato (taker_buy_volume,
la decima) c'e' in tutti i mesi. Stampa solo il numero di colonne per mese e la prima
riga di un mese, nessun calcolo.
"""

import sys
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402


def main() -> None:
    conteggi = {}
    for anno in range(2020, 2024):
        for mese in range(1, 13):
            righe = dati.righe_csv_da_zip(dati.percorso_mese("ETHUSDT", "klines", "1d", anno, mese))
            conteggi[f"{anno}-{mese:02d}"] = sorted({len(r) for r in righe})
    print(conteggi)
    print(dati.righe_csv_da_zip(dati.percorso_mese("ETHUSDT", "klines", "1d", 2020, 1))[0])


if __name__ == "__main__":
    main()
