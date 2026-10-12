"""Scrittura del log della campagna SOLUSDT (solo in aggiunta, sezione 6 del protocollo).

Uso da riga di comando: python registro.py <file.json>
Il file contiene una voce (oggetto JSON) o una lista di voci; ognuna si aggiunge in
fondo a log.jsonl, su una riga, con il campo "data" (UTC) se manca. Nessuna voce
esistente si modifica.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci() -> list:
    return [json.loads(r) for r in LOG.read_text().splitlines() if r.strip()]


def aggiungi(voce: dict) -> dict:
    """Aggiunge una voce in fondo al log. Rifiuta un risultato senza registrazione e id doppi."""
    voce = dict(voce)
    voce.setdefault("data", adesso())
    esistenti = voci()
    if voce["tipo"] in ("registrazione", "scarto"):
        if any(v.get("id") == voce["id"] and v.get("tipo") in ("registrazione", "scarto") for v in esistenti):
            raise ValueError(f"id gia' registrato: {voce['id']}")
    if voce["tipo"] == "risultato":
        if not any(v.get("id") == voce["id"] and v.get("tipo") == "registrazione" for v in esistenti):
            raise ValueError(f"risultato senza registrazione: {voce['id']}")
    with LOG.open("a") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


if __name__ == "__main__":
    dati = json.loads(Path(sys.argv[1]).read_text())
    for v in dati if isinstance(dati, list) else [dati]:
        aggiungi(v)
        print("aggiunta", v.get("id"), v.get("tipo"))
