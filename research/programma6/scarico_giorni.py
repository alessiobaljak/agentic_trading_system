"""Programma 6, seconda prova: le candele giornaliere e il funding di tutti i perpetui USDT-M dell'archivio pubblico di
Binance, anche quelli tolti dal listino (SECONDA.md, sezione 2), con il CHECKSUM.

Scrive in ``research/data/p6g/<SIMBOLO>/{giorni,funding}/`` (fuori da git) e in ``scarico_giorni.json`` un'impronta per
simbolo e tipo: numero di file, primo e ultimo, e lo SHA-256 dell'elenco ordinato «nome impronta» (si ricalcola dai file).
Riprende da dove si e' fermato.

Uso: python3 -m research.programma6.scarico_giorni [SIMBOLO ...]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research.programma5.strumenti.scarico import BASE, _prendi, elenca
from research.programma5.strumenti.universo import STABILI, simboli
from research.src.dati import leggi_checksum

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6g"
QUI = Path(__file__).parent
MESE_IN_CORSO = "2026-10"


def ammesso(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]+USDT", s)) and not any(s.startswith(x) for x in STABILI)


def chiavi(s: str) -> dict:
    mensili = elenca(f"data/futures/um/monthly/klines/{s}/1d/")
    giorni = list(mensili)
    if any(f"-1d-2026-09.zip" in k for k in mensili):
        giorni += elenca(f"data/futures/um/daily/klines/{s}/1d/{s}-1d-{MESE_IN_CORSO}-")
    return {"giorni": sorted(giorni), "funding": sorted(elenca(f"data/futures/um/monthly/fundingRate/{s}/"))}


def _scarica(chiave: str, dest: Path):
    nome = chiave.rsplit("/", 1)[1]
    f = dest / nome
    ok = f.with_suffix(".zip.ok")
    if f.exists() and ok.exists():
        return nome, ok.read_text().strip()
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return nome, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    dest.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_bytes(contenuto)
    tmp.replace(f)
    ok.write_text(impronta if somma is not None else impronta + " senza-checksum")
    return nome, ok.read_text().strip()


def impronta(esiti: list) -> dict:
    righe = sorted(f"{n} {h}" for n, h in esiti if h)
    return {"file": len(righe), "primo": righe[0].split()[0] if righe else "", "ultimo": righe[-1].split()[0] if righe else "",
            "sha256": hashlib.sha256("\n".join(righe).encode()).hexdigest()}


def uno(s: str) -> dict:
    out = {}
    for tipo, ch in chiavi(s).items():
        with ThreadPoolExecutor(max_workers=8) as ex:
            esiti = list(ex.map(lambda k: _scarica(k, DATI / s / tipo), ch))
        out[tipo] = impronta(esiti)
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tutti = argv or [s for s in simboli() if ammesso(s)]
    dest = QUI / "scarico_giorni.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    import os
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "4"))) as ex:
        for s, r in zip(tutti, ex.map(uno, tutti)):
            imp[s] = r
            print(f"[giorni] {s}: {r['giorni']['file']} giorni/mesi, {r['funding']['file']} funding", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
