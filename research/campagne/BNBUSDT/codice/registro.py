"""Aggiunta di voci al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` si prende dall'orologio della macchina (UTC) nel momento in cui la voce
si scrive, mai a memoria. Uso da riga di comando: ``python registro.py voce.json``
(il file contiene un oggetto JSON o una lista di oggetti; il campo ``data`` si aggiunge qui).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    """Rende serializzabile in JSON: numpy, inf, chiavi intere."""
    import math
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if np is not None and isinstance(x, np.ndarray):
        return [_pulisci(v) for v in x.tolist()]
    if np is not None and isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
        return round(x, 6)
    return x


def leggi():
    voci = []
    if LOG.exists():
        for riga in LOG.read_text(encoding="utf-8").splitlines():
            if riga.strip():
                voci.append(json.loads(riga))
    return voci


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo")}
    if "tipo_test" in voce:
        ordinata["tipo_test"] = voce.pop("tipo_test")
    ordinata["data"] = adesso()
    voce.pop("data", None)
    ordinata.update(voce)
    ordinata = _pulisci(ordinata)
    ids = [(v["id"], v["tipo"]) for v in leggi()]
    if (ordinata["id"], ordinata["tipo"]) in ids:
        raise ValueError(f"voce gia' presente: {ordinata['id']} {ordinata['tipo']}")
    if ordinata["tipo"] == "risultato" and (ordinata["id"], "registrazione") not in ids:
        raise ValueError(f"risultato senza registrazione: {ordinata['id']}")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ordinata, ensure_ascii=False) + "\n")
    return ordinata


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in contenuto if isinstance(contenuto, list) else [contenuto]:
        print(aggiungi(v)["id"], "scritta")
