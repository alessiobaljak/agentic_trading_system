"""Scrittura del log della campagna SOLUSDT (research/PROTOCOLLO.md, sezione 6).

Solo in aggiunta: ogni chiamata aggiunge UNA riga JSON a log.jsonl e non tocca
mai le righe precedenti. La data e' l'istante UTC della scrittura.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scrivi(voce: dict) -> dict:
    """Aggiunge la voce (con la data, se manca) e la restituisce."""
    voce = dict(voce)
    voce.setdefault("data", adesso())
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


def leggi() -> list:
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def prossimo_numero() -> int:
    """Il prossimo numero progressivo di id (SOLUSDT-NNN), contando tutte le voci con id numerico."""
    n = 0
    for v in leggi():
        i = str(v.get("id", ""))
        if i.startswith("SOLUSDT-") and i[8:].isdigit():
            n = max(n, int(i[8:]))
    return n + 1
