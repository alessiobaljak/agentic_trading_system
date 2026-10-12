"""Aggiunge voci al log della campagna (solo in aggiunta), con la data presa da `date -u`.

Uso da riga di comando: python registro.py <file.json>
Il file contiene una voce (oggetto JSON) o una lista di voci; il campo `data` si
aggiunge qui, dall'orologio della macchina, mai a memoria.
"""
import json
import subprocess
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True).stdout.strip()


def voci_presenti():
    if not LOG.is_file():
        return []
    return [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    data = adesso()
    nuova = {"id": voce.pop("id"), "tipo": voce.pop("tipo")}
    if "tipo_test" in voce:
        nuova["tipo_test"] = voce.pop("tipo_test")
    nuova["data"] = data
    nuova.update(voce)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(nuova, ensure_ascii=False, default=_serializza) + "\n")
    return nuova


def _serializza(x):
    try:
        import numpy as np
        if isinstance(x, np.generic):
            return x.item()
        if isinstance(x, np.ndarray):
            return x.tolist()
    except ImportError:
        pass
    if isinstance(x, float):
        return x
    return str(x)


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in contenuto if isinstance(contenuto, list) else [contenuto]:
        print(json.dumps(aggiungi(v), ensure_ascii=False)[:300])
