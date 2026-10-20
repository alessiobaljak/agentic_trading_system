"""Programma 6: le candele giornaliere a pronti (spot, coppia contro USDT) delle monete passate almeno una volta dall'universo
delle 100 piu' scambiate, file mensili dell'archivio pubblico di Binance con il CHECKSUM (idea 10 della coda di
`research/REGISTRO.md`).

Il nome a pronti e' quello del perpetuo, o senza il prefisso dei multipli (1000PEPEUSDT → PEPEUSDT); il primo che esiste
nell'archivio. Scrive in ``research/data/p6g/<PERPETUO>/spot/`` (fuori da git) e in ``scarico_spot.json`` l'impronta e il
nome usato. Riprende da dove si e' fermato.

Uso: python3 -m research.programma6.scarico_spot [PERPETUO ...]
"""
from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research.programma5.strumenti.scarico import elenca
from research.programma6 import scarico_giorni as sg
from research.programma6 import scarico_premio as sp

QUI = Path(__file__).parent


def nomi_a_pronti(perpetuo: str) -> list:
    out = [perpetuo]
    m = re.fullmatch(r"(1000000|10000|1000|1M)([A-Z0-9]+USDT)", perpetuo)
    if m:
        out.append(m.group(2))
    return out


def uno(perpetuo: str) -> dict:
    for nome in nomi_a_pronti(perpetuo):
        ch = sorted(k for k in elenca(f"data/spot/monthly/klines/{nome}/1d/") if k.endswith(".zip"))
        if ch:
            with ThreadPoolExecutor(max_workers=8) as ex:
                esiti = list(ex.map(lambda k: sg._scarica(k, sg.DATI / perpetuo / "spot"), ch))
            return {"nome": nome, **sg.impronta(esiti)}
    return {"nome": "", "file": 0}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tutti = argv or sp.monete_dell_universo()
    dest = QUI / "scarico_spot.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "4"))) as ex:
        for s, r in zip(tutti, ex.map(uno, tutti)):
            imp[s] = r
            print(f"[spot] {s}: {r['nome'] or 'nessuna coppia a pronti'} {r['file']} mesi", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    print(f"[spot] FINITO: {len(tutti)} monete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
