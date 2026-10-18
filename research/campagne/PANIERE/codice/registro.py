"""Aggiunta di voci al log della campagna (solo in aggiunta), con id progressivo e data dall'orologio della macchina.

Le voci del log si scrivono in serie (lezioni/metodo.md): una funzione sola che legge l'ultimo id,
prende la data con l'orologio UTC della macchina e aggiunge una riga JSON in fondo al file.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci():
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(riga) for riga in f if riga.strip()]


def prossimo_id() -> str:
    numeri = [int(v["id"].split("-")[1]) for v in voci()]
    return f"PANIERE-{max(numeri) + 1:03d}"


def aggiungi(campi: dict, id_voce: str = None) -> dict:
    """Aggiunge una voce; ``id_voce`` si passa solo per il risultato di una registrazione già scritta."""
    voce = {"id": id_voce or prossimo_id()}
    voce.update(campi)
    voce.setdefault("data", adesso())
    riga = json.dumps(voce, ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return voce
