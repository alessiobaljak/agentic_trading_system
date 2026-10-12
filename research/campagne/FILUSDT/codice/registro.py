"""Aggiunta di voci al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` si prende dall'orologio della macchina (UTC), come ``date -u``.
Uso da riga di comando: ``python registro.py voce.json`` aggiunge le voci del file
(una voce JSON per riga, senza il campo data) in fondo al log.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
        return round(x, 6)
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if hasattr(x, "item"):
        return _pulisci(x.item())
    return x


def ids_presenti() -> set:
    if not LOG.is_file():
        return set()
    return {(json.loads(r)["id"], json.loads(r)["tipo"]) for r in LOG.read_text().splitlines() if r.strip()}


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    voce["data"] = adesso()
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo"), "data": voce.pop("data")}
    ordinata.update(voce)
    ordinata = _pulisci(ordinata)
    if (ordinata["id"], ordinata["tipo"]) in ids_presenti() and ordinata["tipo"] != "nota":
        raise ValueError(f"voce gia' presente: {ordinata['id']} {ordinata['tipo']}")
    with LOG.open("a") as f:
        f.write(json.dumps(ordinata, ensure_ascii=False) + "\n")
    return ordinata


def voci() -> list:
    return [json.loads(r) for r in LOG.read_text().splitlines() if r.strip()]


if __name__ == "__main__":
    for riga in Path(sys.argv[1]).read_text().splitlines():
        if riga.strip():
            print(aggiungi(json.loads(riga))["data"])
