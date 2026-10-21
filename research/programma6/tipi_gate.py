"""Programma 6: il tipo di ogni contratto USDT perpetuo di Gate.io (campo ``contract_type`` dell'interfaccia pubblica
``/api/v4/futures/usdt/contracts/<nome>``: per esempio «stocks» per le azioni), per togliere dalle prove i contratti che non
sono una moneta. Scrive ``research/data/gate/tipi.json`` (fuori da git) e ``tipi_gate.json`` (quanti per tipo e l'impronta).

Uso: python3 -m research.programma6.tipi_gate
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research.programma6 import ventisettesima as vt

QUI = Path(__file__).parent
FILE = vt.DATI / "tipi.json"
URL = "https://api.gateio.ws/api/v4/futures/usdt/contracts/"


def uno(nome: str) -> tuple:
    for prova in range(5):
        try:
            with urllib.request.urlopen(URL + urllib.parse.quote(nome), timeout=30) as r:
                d = json.loads(r.read())
                return nome, d.get("contract_type", "") or ""
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return nome, "sconosciuto"
            time.sleep(2 ** prova)
        except Exception:
            time.sleep(2 ** prova)
    return nome, "errore"


def carica() -> dict:
    return json.loads(FILE.read_text()) if FILE.exists() else {}


def moneta(nome: str, tipi: dict) -> bool:
    """Vero se il contratto e' una moneta: tipo vuoto o «crypto» (non azioni, indici, materie prime, valute)."""
    return tipi.get(nome, "sconosciuto") in ("", "crypto")


def main() -> int:
    nomi = sorted({f.name.rsplit("-", 1)[0] for f in (vt.DATI / "candlesticks_1d").glob("*/*.csv.gz")})
    tipi = carica()
    mancano = [n for n in nomi if n not in tipi or tipi[n] == "errore"]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for n, t in ex.map(uno, mancano):
            tipi[n] = t
    FILE.write_text(json.dumps(tipi, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    righe = "\n".join(f"{k} {v}" for k, v in sorted(tipi.items()))
    riassunto = {"contratti": len(tipi), "per_tipo": dict(Counter(tipi.values())),
                 "sha256": hashlib.sha256(righe.encode()).hexdigest()}
    (QUI / "tipi_gate.json").write_text(json.dumps(riassunto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(riassunto, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
