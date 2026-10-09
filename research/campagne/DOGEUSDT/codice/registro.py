"""Scrittura del log della campagna DOGEUSDT (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` di ogni voce si prende dall'orologio della macchina (``date -u``),
mai a memoria. Uso da riga di comando: ``python registro.py <file.json>`` aggiunge la
voce (o le voci, se il file contiene una lista) lette dal file.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"


def adesso() -> str:
    """Istante UTC dall'orologio della macchina, con ``date -u``."""
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True).stdout.strip()


def _pulisci(x):
    """Rende serializzabili in JSON i numeri di numpy, gli infiniti e le chiavi intere."""
    import math
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items() if k != "valori"}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if np is not None and isinstance(x, np.generic):
        x = x.item()
    if np is not None and isinstance(x, np.ndarray):
        return [_pulisci(v) for v in x.tolist()]
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
        return round(x, 6)
    return x


def aggiungi(voce: dict) -> dict:
    """Aggiunge una voce al log con la data presa ora; ritorna la voce scritta."""
    voce = dict(voce)
    dati = {"id": voce.pop("id", None), "tipo": voce.pop("tipo")}
    if dati["id"] is None:
        dati.pop("id")
    dati["data"] = adesso()
    dati.update(voce)
    riga = json.dumps(_pulisci(dati), ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return dati


def voci() -> list:
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in (contenuto if isinstance(contenuto, list) else [contenuto]):
        print(json.dumps(aggiungi(v), ensure_ascii=False))
