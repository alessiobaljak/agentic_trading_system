"""Aggiunge voci al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Il campo ``data`` si prende dall'orologio della macchina in UTC al momento della scrittura.
Uso da riga di comando: ``python -m research.campagne.GALAUSDT.codice.registro <file.json>``,
dove il file contiene una voce (dizionario) o una lista di voci.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "log.jsonl"


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(valore):
    """Rende serializzabili numeri numpy, inf e nan (come stringhe)."""
    if isinstance(valore, dict):
        return {str(k): _pulisci(v) for k, v in valore.items()}
    if isinstance(valore, (list, tuple)):
        return [_pulisci(v) for v in valore]
    if hasattr(valore, "item") and not isinstance(valore, (str, bytes)):
        try:
            valore = valore.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(valore, float):
        if valore != valore:
            return "nan"
        if valore in (float("inf"), float("-inf")):
            return "inf" if valore > 0 else "-inf"
        return round(valore, 6)
    return valore


def aggiungi(voce: dict) -> dict:
    voce = dict(voce)
    voce["data"] = adesso()
    # 'data' subito dopo 'id' e 'tipo' per leggibilita'
    ordinata = {k: voce[k] for k in ("id", "tipo") if k in voce}
    ordinata["data"] = voce["data"]
    ordinata.update({k: v for k, v in voce.items() if k not in ordinata})
    riga = json.dumps(_pulisci(ordinata), ensure_ascii=False)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(riga + "\n")
    return ordinata


def ultimo_id_variante() -> int:
    n = 0
    if LOG.exists():
        for riga in LOG.read_text(encoding="utf-8").splitlines():
            v = json.loads(riga)
            if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante":
                n = max(n, int(v.get("variante_n", 0)))
    return n


if __name__ == "__main__":
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    voci = contenuto if isinstance(contenuto, list) else [contenuto]
    for v in voci:
        print(json.dumps(aggiungi(v), ensure_ascii=False)[:300])
