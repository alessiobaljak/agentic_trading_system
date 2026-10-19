"""Programma 6, quarta prova: le candele da 1 ora dei perpetui mai usati (QUARTA.md, sezione 2), con il CHECKSUM.

Scrive in ``research/data/p6h/<SIMBOLO>/ore/`` (fuori da git) e un'impronta per simbolo (numero di file, primo, ultimo,
SHA-256 dell'elenco «nome impronta») in ``scarico_ore.json`` (o nella cartella di ``P6_IMPRONTE`` mentre gira).

Uso: python3 -m research.programma6.scarico_ore SIMBOLO ...   (o un file .json con l'elenco)
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research.programma5.strumenti.scarico import elenca
from research.programma6.scarico_giorni import MESE_IN_CORSO, _scarica, impronta

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6h"
QUI = Path(__file__).parent


def chiavi(s: str) -> list:
    mensili = elenca(f"data/futures/um/monthly/klines/{s}/1h/")
    out = list(mensili)
    if any("-1h-2026-09.zip" in k for k in mensili):
        out += elenca(f"data/futures/um/daily/klines/{s}/1h/{s}-1h-{MESE_IN_CORSO}-")
    return sorted(out)


def uno(s: str) -> dict:
    with ThreadPoolExecutor(max_workers=8) as ex:
        esiti = list(ex.map(lambda k: _scarica(k, DATI / s / "ore"), chiavi(s)))
    return impronta(esiti)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tutti = json.loads(Path(argv[0]).read_text()) if argv and argv[0].endswith(".json") else argv
    cartella = Path(os.environ["P6_IMPRONTE"]) if os.environ.get("P6_IMPRONTE") else QUI
    dest = cartella / "scarico_ore.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "8"))) as ex:
        for s, r in zip(tutti, ex.map(uno, tutti)):
            imp[s] = r
            print(f"[ore] {s}: {r['file']} file", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
