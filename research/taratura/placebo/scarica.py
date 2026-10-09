"""Scarica le candele a 1 ora delle monete della prova a placebo (regole in regole.md).

Solo klines 1h, dal primo mese d'archivio di ogni moneta al 2023-12-31: il caricatore
(research/src/dati.py) rifiuta qualunque data oltre il 2023-12-31 prima di toccare la rete.
I file vanno in research/data/placebo/ (fuori da git), separati dai dati delle campagne.
Vive sul branch research/coordinamento (sezione 5 del protocollo): usa l'elenco di universo/.
Uso, dalla radice del repository: python -m research.taratura.placebo.scarica
"""
from __future__ import annotations

import csv
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from research.src import dati

QUI = Path(__file__).resolve().parent
RADICE_DATI = QUI.parent.parent / "data" / "placebo"


#: le monete idonee che non sono di campagna (Passo 1), su questo branch di coordinamento
ELENCO = QUI.parent.parent / "universo" / "monete_idonee_non_campagna.csv"


def monete() -> list:
    """Simbolo, primo mese d'archivio e fascia di slippage delle 80 monete idonee non di campagna."""
    with open(ELENCO, newline="") as f:
        return [{"simbolo": r["simbolo"], "primo_mese_archivio": r["primo_mese_archivio"],
                 "fascia_slippage": r["fascia_slippage"]} for r in csv.DictReader(f)]


def _una(m: dict) -> str:
    inizio = date.fromisoformat(m["primo_mese_archivio"])
    try:
        percorsi = dati.scarica_periodo(m["simbolo"], "klines", "1h", inizio, dati.FINE_IN_SAMPLE,
                                        radice=RADICE_DATI)
        return f"{m['simbolo']}: {len(percorsi)} mesi"
    except Exception as e:  # una moneta che fallisce non ferma le altre: si riporta
        return f"{m['simbolo']}: ERRORE {type(e).__name__}: {e}"


def main() -> int:
    RADICE_DATI.mkdir(parents=True, exist_ok=True)
    elenco = monete()
    # 8 monete alla volta: file diversi, nessun conflitto; un file gia' su disco non si riscarica
    with ThreadPoolExecutor(max_workers=8) as pool:
        for k, riga in enumerate(pool.map(_una, elenco), 1):
            print(f"[{k}/{len(elenco)}] {riga}", flush=True)
    if dati.CHECKSUM_MANCANTI:
        print(f"CHECKSUM mancanti: {len(dati.CHECKSUM_MANCANTI)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
