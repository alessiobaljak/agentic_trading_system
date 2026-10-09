"""Scrittura del log della campagna (sezione 6): solo in aggiunta.

Il campo ``data`` si prende dall'orologio della macchina (UTC), mai a memoria:
equivale a ``date -u``. Ogni voce sta su una riga. Un ``id`` gia' usato da una
voce dello stesso tipo alza un errore (le registrazioni e i risultati hanno lo
stesso id per costruzione: si controlla la coppia id, tipo).
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    """Numeri non finiti in stringa (JSON non li ammette), numpy in python."""
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, (str, bytes)):
        try:
            x = x.item()
        except Exception:
            pass
    if isinstance(x, float) and not math.isfinite(x):
        return str(x)
    return x


def voci():
    if not LOG.exists():
        return []
    return [json.loads(r) for r in LOG.read_text().splitlines() if r.strip()]


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    gia = {(v.get("id"), v.get("tipo")) for v in voci()}
    if (voce.get("id"), voce.get("tipo")) in gia:
        raise ValueError(f"voce gia' presente: {voce.get('id')} {voce.get('tipo')}")
    ordinata = {"id": voce.pop("id"), "tipo": voce.pop("tipo"), "data": adesso()}
    voce.pop("data", None)
    ordinata.update(voce)
    riga = json.dumps(_pulisci(ordinata), ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return ordinata


if __name__ == "__main__":
    # uso: python registro.py file_voce.json  (aggiunge la voce contenuta nel file)
    aggiungi(json.loads(Path(sys.argv[1]).read_text()))
