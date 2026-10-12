"""Aggiunge una voce al log della campagna (solo in aggiunta, sezione 6 del protocollo).

Uso: python -m research.campagne.BCHUSDT.codice.registra <file_json_della_voce>

Il campo ``data`` si prende dall'orologio della macchina con ``date -u`` (mai a
memoria) e si inserisce subito dopo ``id`` e ``tipo``. Il file della voce contiene
un oggetto JSON oppure una lista di oggetti (voci aggiunte nell'ordine).
"""
import json
import subprocess
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "log.jsonl"


def adesso() -> str:
    return subprocess.run(
        ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True
    ).stdout.strip()


def _converti(x):
    """Numeri di numpy e insiemi in tipi JSON."""
    if hasattr(x, "item"):
        return x.item()
    if isinstance(x, (set, frozenset, tuple)):
        return list(x)
    raise TypeError(f"non serializzabile: {type(x)}")


def aggiungi(voce: dict) -> dict:
    ordinata = {}
    for chiave in ("id", "tipo", "tipo_test"):
        if chiave in voce:
            ordinata[chiave] = voce[chiave]
    ordinata["data"] = adesso()
    for chiave, valore in voce.items():
        if chiave not in ordinata and chiave != "data":
            ordinata[chiave] = valore
    with open(LOG, "a", encoding="utf-8") as flusso:
        flusso.write(json.dumps(ordinata, ensure_ascii=False, default=_converti) + "\n")
    return ordinata


def main() -> None:
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    voci = contenuto if isinstance(contenuto, list) else [contenuto]
    for voce in voci:
        scritta = aggiungi(voce)
        print(scritta["data"], scritta.get("id", ""), scritta["tipo"])


if __name__ == "__main__":
    main()
