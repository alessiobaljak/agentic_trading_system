"""Aggiunge voci in coda al log della campagna (solo in aggiunta, sezione 6).

Uso: python aggiungi_log.py <file con una o piu' voci JSON, una per riga>

Il campo ``data`` di ogni voce si prende dall'orologio della macchina (UTC) al
momento dell'aggiunta, come ``date -u``: mai scritto a mano. Una voce che ha
gia' ``data`` viene rifiutata, perche' sarebbe una data scritta a memoria.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aggiungi(voci):
    righe = []
    for voce in voci:
        if "data" in voce:
            raise ValueError(f"la voce {voce.get('id')} ha gia' il campo data")
        nuova = {}
        for k, v in voce.items():
            nuova[k] = v
            if k == "tipo" and "data" not in nuova:
                nuova["data"] = adesso()
        if "data" not in nuova:
            nuova["data"] = adesso()
        righe.append(json.dumps(nuova, ensure_ascii=False))
    with open(LOG, "a", encoding="utf-8") as f:
        for r in righe:
            f.write(r + "\n")
    return len(righe)


if __name__ == "__main__":
    testo = Path(sys.argv[1]).read_text(encoding="utf-8")
    voci = [json.loads(r) for r in testo.splitlines() if r.strip()]
    print("aggiunte", aggiungi(voci))
