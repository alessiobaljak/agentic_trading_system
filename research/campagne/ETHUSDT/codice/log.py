"""Aiutante del log della campagna ETHUSDT: scrive UNA voce in aggiunta a log.jsonl.

Uso: python3 research/campagne/ETHUSDT/codice/log.py <file json della voce>
oppure da Python: from log import aggiungi; aggiungi({...}).
La data (UTC, al secondo) si aggiunge da sola se manca. Il file si apre solo in
modalita' append: niente in questo aiutante puo' modificare o cancellare una voce.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aggiungi(voce: dict) -> dict:
    if "tipo" not in voce:
        raise ValueError("ogni voce ha un campo 'tipo'")
    voce = {"id": voce.get("id"), "tipo": voce["tipo"], "data": voce.get("data") or adesso(),
            **{k: v for k, v in voce.items() if k not in ("id", "tipo", "data")}}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


def leggi() -> list:
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def prossimo_numero_variante() -> int:
    """variante_n della prossima variante: una in piu' dell'ultima registrata."""
    n = 0
    for voce in leggi():
        if voce.get("tipo") == "registrazione" and voce.get("tipo_test") == "variante":
            n = max(n, int(voce.get("variante_n", 0)))
    return n + 1


def prossimo_id(prefisso: str = "ETHUSDT") -> str:
    """Il prossimo id libero ETHUSDT-NNN, contando gli id gia' nel log."""
    usati = {v.get("id") for v in leggi() if v.get("id")}
    n = 1
    while f"{prefisso}-{n:03d}" in usati:
        n += 1
    return f"{prefisso}-{n:03d}"


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        aggiungi(json.load(f))
