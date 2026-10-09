"""Aggiunta di voci al log della campagna (solo in aggiunta, sezione 6).

Il campo ``data`` si prende dall'orologio della macchina (UTC) al momento della
scrittura, mai a memoria. Uso da riga di comando: ``python registro.py voce.json``
dove il file contiene un oggetto JSON (una voce) o una lista di voci.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    """Rende serializzabili numeri numpy, infiniti e chiavi non stringa."""
    import math
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, (str, bytes)):
        try:
            x = x.item()
        except Exception:
            pass
    if isinstance(x, float):
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        if math.isnan(x):
            return "nan"
        return round(x, 6)
    return x


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    voce["data"] = adesso()
    # 'data' subito dopo id e tipo, per leggibilita'
    ordinata = {k: voce[k] for k in ("id", "tipo") if k in voce}
    ordinata["data"] = voce["data"]
    ordinata.update({k: v for k, v in voce.items() if k not in ordinata})
    riga = json.dumps(_pulisci(ordinata), ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return ordinata


def voci() -> list:
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for v in contenuto if isinstance(contenuto, list) else [contenuto]:
        print(aggiungi(v)["id"])
