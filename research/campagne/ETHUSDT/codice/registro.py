"""Il log della campagna ETHUSDT: solo in aggiunta (regola 3 del protocollo).

``aggiungi(voce)`` scrive una riga JSON in fondo a research/campagne/ETHUSDT/log.jsonl.
Non modifica e non cancella mai righe gia' scritte. Controlla:
* che ogni voce abbia ``id`` e ``tipo`` fra quelli della sezione 6;
* che una ``registrazione`` non riusi un ``id`` gia' registrato;
* che un ``risultato`` rimandi a una ``registrazione`` precedente con lo stesso ``id``.

Uso da riga di comando: ``python registro.py <file.json>`` aggiunge la voce (o la
lista di voci) contenuta nel file, che si scrive prima con lo strumento dei file.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "log.jsonl"
TIPI = ("registrazione", "risultato", "scarto", "nota", "correzione")


def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def voci() -> list:
    if not LOG.is_file():
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def prossimo_variante_n() -> int:
    n = [v.get("variante_n", 0) for v in voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"]
    return (max(n) if n else 0) + 1


def aggiungi(voce: dict) -> dict:
    if "id" not in voce or voce.get("tipo") not in TIPI:
        raise ValueError(f"voce senza id o con tipo non ammesso: {voce.get('tipo')!r}")
    voce = dict(voce)
    voce.setdefault("data", adesso())
    esistenti = voci()
    if voce["tipo"] == "registrazione":
        if any(v["id"] == voce["id"] and v["tipo"] == "registrazione" for v in esistenti):
            raise ValueError(f"id gia' registrato: {voce['id']}")
    if voce["tipo"] == "risultato":
        if not any(v["id"] == voce["id"] and v["tipo"] == "registrazione" for v in esistenti):
            raise ValueError(f"risultato senza registrazione precedente: {voce['id']}")
        if any(v["id"] == voce["id"] and v["tipo"] == "risultato" for v in esistenti):
            raise ValueError(f"risultato gia' scritto per {voce['id']}: una correzione e' una voce nuova")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(pulisci(voce), ensure_ascii=False, default=_serializza, allow_nan=False) + "\n")
    return voce


def pulisci(x):
    """Numeri non finiti come testo ("inf", "-inf", "nan"): il JSON standard non li ammette."""
    import math
    if isinstance(x, dict):
        return {str(k): pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    try:
        import numpy as np
        if isinstance(x, np.generic):
            x = x.item()
        elif isinstance(x, np.ndarray):
            return [pulisci(v) for v in x.tolist()]
    except ImportError:
        pass
    if isinstance(x, float) and not math.isfinite(x):
        return "nan" if math.isnan(x) else ("inf" if x > 0 else "-inf")
    return x


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
        return repr(x)
    return str(x)


def main() -> None:
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    lista = contenuto if isinstance(contenuto, list) else [contenuto]
    for voce in lista:
        scritta = aggiungi(voce)
        print("aggiunta:", scritta["id"], scritta["tipo"])


if __name__ == "__main__":
    main()
