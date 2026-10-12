"""Scrittura del log della campagna TRBUSDT: solo in aggiunta, una voce per riga.

Il campo ``data`` si prende sempre dall'orologio della macchina con ``date -u``
(messaggio di apertura, punto 5), mai a memoria.

Uso da riga di comando: ``python -m research.campagne.TRBUSDT.codice.registro <voce.json>``
aggiunge al log la voce scritta nel file (un oggetto JSON, senza ``data``).
"""

import json
import subprocess
import sys
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True).stdout.strip()


def voci():
    if not LOG.is_file():
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    if "id" in voce:
        voce = {"id": voce.pop("id"), "tipo": voce.pop("tipo"), "data": adesso(), **voce}
    else:
        voce = {"tipo": voce.pop("tipo"), "data": adesso(), **voce}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


def prossima_variante_n() -> int:
    n = [v.get("variante_n", 0) for v in voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"]
    return (max(n) if n else 0) + 1


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        voce = json.load(f)
    print(json.dumps(aggiungi(voce), ensure_ascii=False))
