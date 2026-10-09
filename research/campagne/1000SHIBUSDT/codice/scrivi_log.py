"""Aggiunge voci al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Uso: python scrivi_log.py <file.json>
Il file contiene una voce (oggetto JSON) o una lista di voci. Il campo ``data`` di
ogni voce si prende dall'orologio della macchina in UTC al momento della scrittura
(come ``date -u``), mai a memoria. Il log non si riscrive: si apre in aggiunta.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def aggiungi(voci):
    if isinstance(voci, dict):
        voci = [voci]
    with open(LOG, "a", encoding="utf-8") as f:
        for v in voci:
            v = dict(v)
            v["data"] = adesso()
            # «data» subito dopo id e tipo, per leggibilita'
            ordinata = {k: v[k] for k in ("id", "tipo", "tipo_test") if k in v}
            ordinata["data"] = v["data"]
            ordinata.update({k: x for k, x in v.items() if k not in ordinata})
            f.write(json.dumps(ordinata, ensure_ascii=False) + "\n")
    return len(voci)


if __name__ == "__main__":
    voci = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print("voci aggiunte:", aggiungi(voci))
