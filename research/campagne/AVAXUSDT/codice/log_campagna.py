"""Aggiunta di voci al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` si prende dall'orologio della macchina (lo stesso di ``date -u``),
mai a memoria. Uso da riga di comando: ``python log_campagna.py <file.json>``, dove il
file contiene una voce (oggetto) o una lista di voci; oppure da codice con ``aggiungi``.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ids_esistenti():
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    if "data" not in voce or voce["data"] in (None, "", "adesso"):
        # la data va subito dopo id e tipo, per leggibilita'
        nuova = {}
        for k in ("id", "tipo", "tipo_test"):
            if k in voce:
                nuova[k] = voce[k]
        nuova["data"] = adesso()
        for k, v in voce.items():
            if k not in nuova:
                nuova[k] = v
        voce = nuova
    voci = ids_esistenti()
    if voce.get("tipo") == "registrazione":
        if any(v.get("id") == voce["id"] and v.get("tipo") == "registrazione" for v in voci):
            raise ValueError(f"registrazione con id gia' presente: {voce['id']}")
    if voce.get("tipo") == "risultato":
        if not any(v.get("id") == voce["id"] and v.get("tipo") == "registrazione" for v in voci):
            raise ValueError(f"risultato senza registrazione precedente: {voce['id']}")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")
    return voce


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in contenuto if isinstance(contenuto, list) else [contenuto]:
        print(aggiungi(v)["data"], v.get("id"))
