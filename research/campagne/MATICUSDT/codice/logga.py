"""Aggiunge voci al log della campagna (solo in aggiunta, sezione 6).

Uso: python research/campagne/MATICUSDT/codice/logga.py <file.json>
Il file contiene una voce (oggetto JSON) o una lista di voci. Il campo ``data`` si
prende dall'orologio della macchina in UTC (come ``date -u``) al momento della
scrittura, mai a memoria.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    voce["data"] = adesso()
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo"), "data": voce.pop("data")}
    ordinata.update(voce)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordinata, ensure_ascii=False) + "\n")
    return ordinata


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in contenuto if isinstance(contenuto, list) else [contenuto]:
        print(aggiungi(v)["id"])
