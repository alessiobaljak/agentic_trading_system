"""Scrittura del log della campagna ETCUSDT (solo in aggiunta, sezione 6 del protocollo).

La data di ogni voce viene dall'orologio della macchina (UTC), mai a memoria.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    """Rende serializzabili numpy, inf e chiavi intere."""
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, (list, dict)):
        try:
            x = x.item()
        except Exception:
            pass
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
    return x


def scrivi(voce: dict) -> dict:
    voce = dict(voce)
    voce.setdefault("data", adesso())
    riga = json.dumps(_pulisci(voce), ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return voce


def voci() -> list:
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]
