"""Aiutante per il log della campagna BTCUSDT (sezione 6 del protocollo).

Il log e' SOLO IN AGGIUNTA: questo modulo sa solo appendere una riga JSON con
la data e ora di adesso. Non legge, non modifica, non cancella. Si usa da riga
di comando (``python log.py '<json>'``) o importato (``aggiungi(dict)``).
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
    """Appende la voce (con ``data`` = adesso se manca) e la ritorna."""
    voce = dict(voce)
    voce.setdefault("data", adesso())
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False, sort_keys=False) + "\n")
    return voce


if __name__ == "__main__":
    for testo in sys.argv[1:]:
        print(json.dumps(aggiungi(json.loads(testo)), ensure_ascii=False))
