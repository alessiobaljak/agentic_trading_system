"""Programma 6, ventisettesima prova: il funding applicato e le candele giornaliere di tutti i contratti USDT perpetui di
Gate.io dall'archivio pubblico (bucket S3 `gateio-public-data`, lo stesso di `download.gatedata.org`), mesi 2023-01 →
2026-09. Scrive in ``research/data/gate/<tipo>/<mese>/`` (fuori da git) e in ``scarico_gate.json`` l'impronta per tipo
(numero di file e SHA-256 dell'elenco ordinato «nome impronta»). Riprende da dove si e' fermato.

Uso: python3 -m research.programma6.scarico_gate
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "gate"
QUI = Path(__file__).parent
BASE = "https://gateio-public-data.s3.amazonaws.com/"
TIPI = ("funding_applies", "candlesticks_1d")


def mesi(da: str = "202301", a: str = "202609") -> list:
    out, y, m = [], int(da[:4]), int(da[4:])
    while f"{y:04d}{m:02d}" <= a:
        out.append(f"{y:04d}{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def elenco(prefisso: str) -> list:
    chiavi, token = [], None
    while True:
        u = BASE + "?list-type=2&prefix=" + urllib.parse.quote(prefisso) + (
            "&continuation-token=" + urllib.parse.quote(token) if token else "")
        x = _prendi(u).decode()
        chiavi += re.findall(r"<Key>([^<]*)</Key>", x)
        m = re.search(r"<NextContinuationToken>([^<]*)</NextContinuationToken>", x)
        if not m:
            return chiavi
        token = m.group(1)


def _prendi(u: str) -> bytes:
    for prova in range(5):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                return r.read()
        except Exception:
            if prova == 4:
                raise
    return b""


def scarica(chiave: str) -> tuple:
    f = DATI / chiave.split("futures_usdt/", 1)[1]
    ok = f.with_name(f.name + ".sha256")
    if f.exists() and ok.exists():
        return f.name, ok.read_text().strip()
    dati = _prendi(BASE + chiave)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(dati)
    h = hashlib.sha256(dati).hexdigest()
    ok.write_text(h)
    return f.name, h


def main() -> int:
    imp = {}
    with ThreadPoolExecutor(max_workers=32) as ex:
        for tipo in TIPI:
            chiavi = []
            for m in mesi():
                chiavi += [k for k in elenco(f"futures_usdt/{tipo}/{m}/") if k.endswith(".csv.gz")]
            esiti = list(ex.map(scarica, chiavi))
            righe = sorted(f"{n} {h}" for n, h in esiti)
            imp[tipo] = {"file": len(righe), "sha256": hashlib.sha256("\n".join(righe).encode()).hexdigest()}
            print(f"[gate] {tipo}: {len(righe)} file", flush=True)
    (QUI / "scarico_gate.json").write_text(json.dumps(imp, indent=1), encoding="utf-8")
    print("[gate] FINITO", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
