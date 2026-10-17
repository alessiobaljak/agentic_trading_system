"""Aggiunge una voce al log della campagna (solo in aggiunta, regola 4).

Uso: python3 research/campagne/LINK6/codice/log_aggiungi.py <file_json_della_voce>

La voce e' un oggetto JSON con almeno "id" e "tipo". L'orario ("data") lo mette lo script
dall'orologio della macchina. Rifiuta una voce se la stessa coppia (id, tipo) e' gia' nel log.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"
TIPI = {"registrazione", "risultato", "scarto", "nota", "correzione"}


def voci():
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def aggiungi(voce):
    if voce.get("tipo") not in TIPI or not voce.get("id"):
        raise SystemExit(f"voce non valida: serve id e tipo fra {sorted(TIPI)}")
    if any(v.get("id") == voce["id"] and v.get("tipo") == voce["tipo"] for v in voci()):
        raise SystemExit(f"id gia' presente nel log: {voce['id']} ({voce['tipo']})")
    nuova = {"id": voce["id"], "tipo": voce["tipo"],
             "data": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    nuova.update({k: v for k, v in voce.items() if k not in ("id", "tipo", "data")})
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(nuova, ensure_ascii=False) + "\n")
    print(f"aggiunta {nuova['id']} ({nuova['tipo']}) alle {nuova['data']}")


if __name__ == "__main__":
    aggiungi(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
