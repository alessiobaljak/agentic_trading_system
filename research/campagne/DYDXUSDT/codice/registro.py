"""Scrittura del log della campagna DYDXUSDT (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` si prende dall'orologio della macchina in UTC (lo stesso di
``date -u``), mai a memoria. Uso da riga di comando:

    python research/campagne/DYDXUSDT/codice/registro.py <file_json_della_voce>

La voce si scrive prima in un file JSON (senza il campo ``data``), poi si aggiunge.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    """Rende serializzabili numpy, inf e nan (inf -> stringa, come nel log)."""
    import math
    try:
        import numpy as np
        if isinstance(x, np.generic):
            x = x.item()
        if isinstance(x, np.ndarray):
            x = x.tolist()
    except ImportError:
        pass
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
        return x
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    return x


def aggiungi(voce: dict) -> dict:
    """Aggiunge una voce al log con ``data`` dall'orologio; rifiuta id doppi per lo stesso tipo."""
    voce = dict(voce)
    if "data" in voce:
        raise ValueError("il campo data lo mette questa funzione, dall'orologio")
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo")}
    if "tipo_test" in voce:
        ordinata["tipo_test"] = voce.pop("tipo_test")
    ordinata["data"] = adesso()
    ordinata.update(voce)
    ordinata = _pulisci(ordinata)
    if LOG.exists():
        for riga in LOG.read_text(encoding="utf-8").splitlines():
            if not riga.strip():
                continue
            v = json.loads(riga)
            if v.get("id") == ordinata["id"] and v.get("tipo") == ordinata["tipo"] and ordinata["tipo"] in ("registrazione", "risultato"):
                raise ValueError(f"voce {ordinata['tipo']} con id {ordinata['id']} gia' presente")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordinata, ensure_ascii=False) + "\n")
    return ordinata


def voci() -> list:
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


if __name__ == "__main__":
    voce = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    scritta = aggiungi(voce)
    print(json.dumps(scritta, ensure_ascii=False)[:400])
