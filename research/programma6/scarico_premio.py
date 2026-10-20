"""Programma 6: l'indice del premio orario (perpetuo contro spot) di tutta la storia, file mensili dell'archivio pubblico di
Binance con il CHECKSUM, per le monete passate almeno una volta dall'universo delle 100 piu' scambiate della terza prova.

Scrive in ``research/data/p6g/<SIMBOLO>/premio_mesi/`` (fuori da git) e in ``scarico_premio.json`` l'impronta per simbolo
(come ``scarico_giorni``). Riprende da dove si e' fermato.

Uso: python3 -m research.programma6.scarico_premio [SIMBOLO ...]
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from research.programma5.strumenti.scarico import elenca
from research.programma6 import scarico_giorni as sg

QUI = Path(__file__).parent


def monete_dell_universo() -> list:
    from research.programma6 import seconda as sc
    from research.programma6 import terza as te
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    return [pan["simboli"][j] for j in np.flatnonzero(ps["U"].any(axis=0))]


def uno(s: str) -> dict:
    ch = sorted(k for k in elenca(f"data/futures/um/monthly/premiumIndexKlines/{s}/1h/") if k.endswith(".zip"))
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = list(ex.map(lambda k: sg._scarica(k, sg.DATI / s / "premio_mesi"), ch))
    return sg.impronta(esiti)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tutti = argv or monete_dell_universo()
    dest = QUI / "scarico_premio.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "4"))) as ex:
        for s, r in zip(tutti, ex.map(uno, tutti)):
            imp[s] = r
            print(f"[premio] {s}: {r['file']} mesi", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    print(f"[premio] FINITO: {len(tutti)} monete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
